#!/bin/env python3

"""Code Generation (Instruction Selection) for  ARMv6T2 and above

See `README.md` for more details.
"""

import os
import stat
import collections

from BE.Base import ir
from IR import opcode_tab as o
from BE.Base import serialize

from BE.CpuA32 import opcode_tab as a32
from BE.CpuA32 import symbolic
from BE.CpuA32 import assembler

from BE.CodeGenA32 import isel_tab
from BE.CodeGenA32 import regs
from BE.CodeGenA32 import legalize
from BE.CodeGenCommon import cpu_neutral

from BE.Elf import enum_tab
from BE.Elf import elf_unit


############################################################
# textual emitter
############################################################


def _RenderIns(ins: a32.Ins):
    name, ops = symbolic.InsSymbolize(ins)
    return f"    {name} {' '.join(ops)}"


def _FunCodeGenArm32(fun: ir.Fun, _mod: ir.Unit) -> list[str]:
    assert fun.kind is not o.FUN_KIND.EXTERN
    assert ir.FUN_FLAG.STACK_FINALIZED in fun.flags
    assert fun.stk_size >= 0, "did you call FinalizeStk?"
    # DumpFun("codegen", fun)
    out: list[str] = [
        f"# sig: {fun.render_signature()}  stk_size:{fun.stk_size}",
        f".fun {fun.name} 16",
    ]

    for jtb in fun.jtbs:
        out += cpu_neutral.JtbCodeGenSimpleText(jtb, 4)

    ctx = regs.FunComputeEmitContext(fun)

    out += [_RenderIns(tmpl.MakeInsFromTmpl(None, ctx))
            for tmpl in isel_tab.EmitFunProlog(ctx)]
    for bbl in fun.bbls:
        live_out = sorted([r.name for r in bbl.live_out])
        out.append(f".bbl {bbl.name} 4")
        for ins in bbl.inss:
            if ins.opcode is o.NOP1:
                isel_tab.HandlePseudoNop1(ins, ctx)
            elif ins.opcode is o.RET:
                out += [_RenderIns(tmpl.MakeInsFromTmpl(None, ctx))
                        for tmpl in isel_tab.EmitFunEpilog(ctx)]
            else:
                pattern = isel_tab.FindMatchingPattern(ins)
                assert pattern, (f"could not find pattern for\n{ins} {ins.operands} "
                                 f"in {fun.name}:{bbl.name}")

                out += [_RenderIns(tmpl.MakeInsFromTmpl(ins, ctx))
                        for tmpl in pattern.emit]
    out.append(".endfun")
    return out


def EmitUnitAsText(unit: ir.Unit, fout):
    # we emit the memory stuff AFTER the code since the code generation may add new
    # memory for Consts
    for mem in unit.mems:
        assert mem.kind is not o.MEM_KIND.EXTERN
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        for s in cpu_neutral.MemCodeGenText(mem, unit):
            print(s, file=fout)
    for fun in unit.funs:
        if fun.kind in {o.FUN_KIND.SIGNATURE}:
            continue
        for s in _FunCodeGenArm32(fun, unit):
            print(s, file=fout)


class Unit:
    """Arm specific version of a Unit"""

    def __init__(self):
        self.mems = []
        self.mem_syms = {}
        self.funs = []
        self.fun_syms = {}


def codegen(unit: ir.Unit) -> Unit:
    out = Unit()
    for mem in unit.mems:
        assert mem.kind != o.MEM_KIND.EXTERN
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        arm_mem = cpu_neutral.MemCodeGenText(mem, unit)
        out.mems.append((mem.name, arm_mem))
        out.mem_syms[mem.name] = arm_mem
    for fun in unit.funs:
        if fun.kind is not o.FUN_KIND.NORMAL:
            continue
        arm_fun = _FunCodeGenArm32(fun, unit)
        out.funs.append((fun.name, arm_fun))
        out.fun_syms[fun.name] = arm_fun
    return out


############################################################
# binary emitter
############################################################

def EmitUnitAsBinary(unit: ir.Unit) -> elf_unit.Unit:
    elfunit = elf_unit.Unit()
    for mem in unit.mems:
        assert mem.kind is not o.MEM_KIND.EXTERN
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        cpu_neutral.MemCodeGenBinary(
            elfunit, mem, enum_tab.RELOC_TYPE_ARM.ABS32)

    sec_text = elfunit.sec_text
    for fun in unit.funs:
        elfunit.FunStart(fun.name, 16, assembler.NOP_BYTES)
        for jtb in fun.jtbs:
            cpu_neutral.JtbCodeGenSimpleBinary(
                elfunit, jtb, 4, enum_tab.RELOC_TYPE_ARM.ABS32)

        ctx = regs.FunComputeEmitContext(fun)

        for tmpl in isel_tab.EmitFunProlog(ctx):
            assembler.AddIns(elfunit, tmpl.MakeInsFromTmpl(None, ctx))

        for bbl in fun.bbls:
            elfunit.AddLabel(bbl.name, 4, assembler.NOP_BYTES)
            for ins in bbl.inss:
                if ins.opcode is o.NOP1:
                    isel_tab.HandlePseudoNop1(ins, ctx)
                elif ins.opcode is o.LINE:
                    pass
                    # TODO: add line number support
                elif ins.opcode is o.RET:
                    for tmpl in isel_tab.EmitFunEpilog(ctx):
                        assembler.AddIns(elfunit,
                                         tmpl.MakeInsFromTmpl(None, ctx))

                else:
                    pattern = isel_tab.FindMatchingPattern(ins)
                    assert pattern, f"could not find pattern for\n{ins} {ins.operands}"
                    for tmpl in pattern.emit:
                        assembler.AddIns(elfunit,
                                         tmpl.MakeInsFromTmpl(ins, ctx))
        elfunit.FunEnd()
    elfunit.AddLinkerDefs()
    return elfunit


if __name__ == "__main__":
    import sys
    import argparse

    _ALLOWED_MODES = {"normal", "binary", "legalize", "reg_alloc_global",
                      "reg_alloc_local"}

    def main():
        parser = argparse.ArgumentParser(description='CodeGenA32',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-mode', type=str, help='mode', default="binary",
                            choices=_ALLOWED_MODES)
        parser.add_argument('input', type=str,  nargs='+', help='input file')
        parser.add_argument('output', type=str, help='output file')
        args = parser.parse_args()

        unit = ir.Unit("module")
        for input in args.input:
            fin = sys.stdin if input == "-" else open(input)
            serialize.UnitAddParseFromAsm(unit, fin)
        serialize.UnitSanityCheckAfterParse(unit)
        opt_stats: dict[str, int] = collections.defaultdict(int)

        if args.mode == "binary":
            # we need to legalize all functions first as this may change the signature
            # and fills in cpu reg usage which is used by subsequent interprocedural opts.
            legalize.LegalizeAll(unit, opt_stats, None)
            legalize.RegAllocGlobal(unit, opt_stats, None)
            legalize.RegAllocLocal(unit, opt_stats, None)
            armunit = EmitUnitAsBinary(unit)
            exe = assembler.Assemble(armunit, True)
            exe.save(open(args.output, "wb"))
            os.chmod(args.output, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE)
            return

        fout = sys.stdout if args.output == "-" else open(args.output, "w")

        # we need to legalize all functions first as this may change the signature
        # and fills in cpu reg usage which is used by subsequent interprocedural opts.
        legalize.LegalizeAll(unit, opt_stats)
        if args.mode == "legalize":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        legalize.RegAllocGlobal(unit, opt_stats, fout)
        if args.mode == "reg_alloc_global":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        legalize.RegAllocLocal(unit, opt_stats)
        if args.mode == "reg_alloc_local":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        assert args.mode == "normal"
        EmitUnitAsText(unit, fout)
        if False:
            print("# STATS:")
            for key, val in sorted(opt_stats.items()):
                print(f"#  {key}: {val}", file=fout)

    main()
