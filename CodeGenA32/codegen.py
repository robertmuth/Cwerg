#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  ARMv6T2 and above

See `README.md` for more details.
"""

import os
import stat
import collections
from typing import List, Dict

from Base import cfg
from Base import ir
from Base import opcode_tab as o
from Base import sanity
from Base import serialize

from CpuA32 import opcode_tab as a32
from CpuA32 import symbolic
from CpuA32 import assembler

from CodeGenA32 import isel_tab
from CodeGenA32 import regs
from CodeGenA32 import legalize

from Elf import enum_tab
from Elf import elf_unit


def LegalizeAll(unit: ir.Unit, opt_stats, fout, verbose=False):
    seeds = [f for f in [unit.fun_syms.get("_start"),
                         unit.fun_syms.get("main")] if f]
    if seeds:
        cfg.UnitRemoveUnreachableCode(unit, seeds)
    for fun in unit.funs:
        sanity.FunCheck(fun, unit, check_cfg=False, check_push_pop=True)

        if fun.kind is o.FUN_KIND.NORMAL:
            legalize.PhaseOptimize(fun, unit, opt_stats, fout)

    for fun in unit.funs:
        legalize.PhaseLegalization(fun, unit, opt_stats, fout)


def RegAllocGlobal(unit: ir.Unit, opt_stats, fout, verbose=False):
    for fun in unit.funs:
        sanity.FunCheck(fun, unit, check_cfg=False, check_push_pop=False)
        legalize.PhaseGlobalRegAlloc(fun, opt_stats, fout)
        if verbose:
            legalize.DumpFun("after global_reg_alloc", fun)


def RegAllocLocal(unit: ir.Unit, opt_stats, fout, verbose=False):
    for fun in unit.funs:
        legalize.PhaseFinalizeStackAndLocalRegAlloc(fun, opt_stats, fout)
        if verbose:
            legalize.DumpFun("after stack finalization", fun)


############################################################
# textual emitter
############################################################

_MEMKIND_TO_SECTION = {
    o.MEM_KIND.RO: "rodata",
    o.MEM_KIND.RW: "data",
    # bss missing
}


def _MemCodeGenText(mem: ir.Mem, _mod: ir.Unit) -> List[str]:
    out = [f"# size {mem.Size()}",
           f".mem {mem.name} {mem.alignment} {_MEMKIND_TO_SECTION[mem.kind]}"]
    for d in mem.datas:
        if isinstance(d, ir.DataBytes):
            out += [f"    .data {d.count} {serialize.EscapeCStyle(d.data)}"]
        elif isinstance(d, ir.DataAddrFun):
            out += [f"    .addr.fun {d.size} {d.fun.name}"]
        elif isinstance(d, ir.DataAddrMem):
            out += [f"    .addr.mem {d.size} {d.mem.name} 0x{d.offset:x}"]
        else:
            assert False

    out += [f".endmem"]
    return out


def _JtbCodeGen(jtb: ir.Jtb):
    out = [f".localmem {jtb.name} 4 rodata"]
    for i in range(jtb.size):
        bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
        out.append(f"    .addr.bbl 4 {bbl.name}")
    out.append(".endmem")
    return out


def _RenderIns(ins: a32.Ins):
    name, ops = symbolic.InsSymbolize(ins)
    return f"    {name} {' '.join(ops)}"


def _FunCodeGenArm32(fun: ir.Fun, _mod: ir.Unit) -> List[str]:
    assert fun.kind is not o.FUN_KIND.EXTERN
    assert ir.FUN_FLAG.STACK_FINALIZED in fun.flags
    assert fun.stk_size >= 0, f"did you call FinalizeStk?"
    # DumpFun("codegen", fun)
    out: List[str] = [
        f"# sig: {fun.render_signature()}  stk_size:{fun.stk_size}",
        f".fun {fun.name} 16",
    ]

    for jtb in fun.jtbs:
        out += _JtbCodeGen(jtb)

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
    out.append(f".endfun")
    return out


def EmitUnitAsText(unit: ir.Unit, fout):
    # we emit the memory stuff AFTER the code since the code generation may add new
    # memory for Consts
    for mem in unit.mems:
        assert mem.kind is not o.MEM_KIND.EXTERN
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        for s in _MemCodeGenText(mem, unit):
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
        arm_mem = _MemCodeGenText(mem, unit)
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
        elfunit.MemStart(mem.name, mem.alignment,
                         _MEMKIND_TO_SECTION[mem.kind], False)
        for d in mem.datas:
            if isinstance(d, ir.DataBytes):
                elfunit.AddData(d.count, d.data)
            elif isinstance(d, ir.DataAddrFun):
                elfunit.AddFunAddr(
                    enum_tab.RELOC_TYPE_ARM.ABS32, d.size, d.fun.name)
            elif isinstance(d, ir.DataAddrMem):
                elfunit.AddMemAddr(enum_tab.RELOC_TYPE_ARM.ABS32,
                                   d.size, d.mem.name, d.offset)
            else:
                assert False
        elfunit.MemEnd()

    sec_text = elfunit.sec_text
    for fun in unit.funs:
        elfunit.FunStart(fun.name, 16, assembler.NOP_BYTES)
        for jtb in fun.jtbs:
            elfunit.MemStart(jtb.name, 4, "rodata", True)
            for i in range(jtb.size):
                bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
                elfunit.AddBblAddr(enum_tab.RELOC_TYPE_ARM.ABS32, 4, bbl.name)
            elfunit.MemEnd()

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
        parser = argparse.ArgumentParser(description='CodeGenA32')
        parser.add_argument('-mode', type=str, help='mode')
        parser.add_argument('input', type=str, help='input file')
        parser.add_argument('output', type=str, help='output file')
        args = parser.parse_args()

        assert args.mode in _ALLOWED_MODES
        fin = sys.stdin if args.input == "-" else open(args.input)

        unit = serialize.UnitParseFromAsm(fin)
        opt_stats: Dict[str, int] = collections.defaultdict(int)

        if args.mode == "binary":
            # we need to legalize all functions first as this may change the signature
            # and fills in cpu reg usage which is used by subsequent interprocedural opts.
            LegalizeAll(unit, opt_stats, None)
            RegAllocGlobal(unit, opt_stats, None)
            RegAllocLocal(unit, opt_stats, None)
            armunit = EmitUnitAsBinary(unit)
            exe = assembler.Assemble(armunit, True)
            exe.save(open(args.output, "wb"))
            os.chmod(args.output, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE)
            return

        fout = sys.stdout if args.output == "-" else open(args.output, "w")

        # we need to legalize all functions first as this may change the signature
        # and fills in cpu reg usage which is used by subsequent interprocedural opts.
        LegalizeAll(unit, opt_stats, fout)
        if args.mode == "legalize":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        RegAllocGlobal(unit, opt_stats, fout)
        if args.mode == "reg_alloc_global":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        RegAllocLocal(unit, opt_stats, fout)
        if args.mode == "reg_alloc_local":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        assert args.mode == "normal"
        EmitUnitAsText(unit, fout)
        if False:
            print(f"# STATS:")
            for key, val in sorted(opt_stats.items()):
                print(f"#  {key}: {val}", file=fout)

    main()
