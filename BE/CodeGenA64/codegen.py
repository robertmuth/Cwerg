#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  A64 (Aarch64)

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

from BE.CpuA64 import opcode_tab as a64
from BE.CpuA64 import symbolic
from BE.CpuA64 import assembler

from BE.CodeGenA64 import isel_tab
from BE.CodeGenA64 import regs
from BE.CodeGenA64 import legalize

from BE.Elf import enum_tab
from BE.Elf import elf_unit


def LegalizeAll(unit, opt_stats, fout, verbose=False):
    seeds = [f for f in [unit.fun_syms.get("_start"),
                         unit.fun_syms.get("main")] if f]
    if seeds:
        cfg.UnitRemoveUnreachableCode(unit, seeds)
    for fun in unit.funs:
        sanity.FunCheck(fun, unit, check_cfg=False, check_push_pop=True)

        if fun.kind is o.FUN_KIND.NORMAL:
            legalize.PhaseOptimize(fun, unit, opt_stats, fout)

    for fun in unit.funs:
        legalize.PhaseLegalizationStep1(fun, unit, opt_stats, fout)

    for fun in unit.funs:
        legalize.PhaseLegalizationStep2(fun, unit, opt_stats, fout)


def RegAllocGlobal(unit, opt_stats, fout, verbose=False):
    for fun in unit.funs:
        sanity.FunCheck(fun, unit, check_cfg=False, check_push_pop=False)
        legalize.PhaseGlobalRegAlloc(fun, opt_stats, fout)
        if verbose:
            legalize.DumpFun("after global_reg_alloc", fun)


def RegAllocLocal(unit, opt_stats, fout, verbose=False):
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


def _MemCodeGenText(mem: ir.Mem, _mod: ir.Unit):
    yield f"# size {mem.Size()}"
    yield f".mem {mem.name} {mem.alignment} {_MEMKIND_TO_SECTION[mem.kind]}"
    for d in mem.datas:
        if isinstance(d, ir.DataBytes):
            yield f"    .data {d.count} {serialize.EscapeCStyle(d.data)}"
        elif isinstance(d, ir.DataAddrFun):
            yield f"    .addr.fun {d.size} {d.fun.name}"
        elif isinstance(d, ir.DataAddrMem):
            yield f"    .addr.mem {d.size} {d.mem.name} 0x{d.offset:x}"
        else:
            assert False

    yield ".endmem"


def _JtbCodeGen(jtb: ir.Jtb):
    yield f".localmem {jtb.name} 8 rodata"
    for i in range(jtb.size):
        bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
        yield f"    .addr.bbl 8 {bbl.name}"
    yield".endmem"


def _RenderIns(ins: a64.Ins) -> str:
    name, ops = symbolic.InsSymbolize(ins)
    return f"    {name} {' '.join(ops)}"


def _SimplifyCpuIns(cpu_ins: a64.Ins) -> bool:
    # NOTE: seems to be ineffective and has not been implemented in the C++ version
    # ops = cpu_ins.operands
    # if (cpu_ins.opcode.NameForEnum() == "orr_x_reg" and
    #    ops[1] == isel_tab.FIXARG.XZR and
    #        ops[0] == ops[2] and
    #        ops[3] == a64.SHIFT.lsl and ops[4] == 0):
    #    return False
    return True


def _FunCodeGenText(fun: ir.Fun, _mod: ir.Unit):
    assert ir.FUN_FLAG.STACK_FINALIZED in fun.flags
    assert fun.stk_size >= 0, f"did you call FinalizeStk?"
    # DumpFun("codegen", fun)

    yield f"# sig: {fun.render_signature()}  stk_size:{fun.stk_size}"
    yield f".fun {fun.name} 16"

    for jtb in fun.jtbs:
        yield from _JtbCodeGen(jtb)

    ctx = regs.FunComputeEmitContext(fun)
    for tmpl in isel_tab.EmitFunProlog(ctx):
        yield _RenderIns(tmpl.MakeInsFromTmpl(None, ctx))

    for bbl in fun.bbls:
        live_out = sorted([r.name for r in bbl.live_out])
        yield f".bbl {bbl.name} 4"
        for ins in bbl.inss:
            if ins.opcode is o.NOP1:
                isel_tab.HandlePseudoNop1(ins, ctx)
            elif ins.opcode is o.RET:
                for tmpl in isel_tab.EmitFunEpilog(ctx):
                    yield _RenderIns(tmpl.MakeInsFromTmpl(None, ctx))

            else:
                pattern = isel_tab.FindMatchingPattern(ins)
                assert pattern, (f"could not find pattern for\n{ins} {ins.operands} "
                                 f"in {fun.name}:{bbl.name}")
                for tmpl in pattern.emit:
                    cpu_ins = tmpl.MakeInsFromTmpl(ins, ctx)
                    if _SimplifyCpuIns(cpu_ins):
                        yield _RenderIns(cpu_ins)
    yield f".endfun"


def EmitUnitAsText(unit: ir.Unit, fout):
    # we emit the memory stuff AFTER the code since the code generation may add new
    # memory for Consts
    for mem in unit.mems:
        assert mem.kind != o.MEM_KIND.EXTERN
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        for s in _MemCodeGenText(mem, unit):
            print(s, file=fout)
    for fun in unit.funs:
        if fun.kind in {o.FUN_KIND.SIGNATURE}:
            continue
        for s in _FunCodeGenText(fun, unit):
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
        out.mems.append((mem.name, [x for x in arm_mem]))
        out.mem_syms[mem.name] = arm_mem
    for fun in unit.funs:
        if fun.kind is not o.FUN_KIND.NORMAL:
            continue
        arm_fun = _FunCodeGenText(fun, unit)
        out.funs.append((fun.name, [x for x in arm_fun]))
        out.fun_syms[fun.name] = arm_fun
    return out


############################################################
# binary emitter
############################################################

def EmitUnitAsBinary(unit: ir.Unit) -> elf_unit.Unit:
    elfunit = elf_unit.Unit()
    for mem in unit.mems:
        assert mem.kind != o.MEM_KIND.EXTERN, f"undefined symbol: {mem}"
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        elfunit.MemStart(mem.name, mem.alignment,
                         _MEMKIND_TO_SECTION[mem.kind], False)
        for d in mem.datas:
            if isinstance(d, ir.DataBytes):
                elfunit.AddData(d.count, d.data)
            elif isinstance(d, ir.DataAddrFun):
                elfunit.AddFunAddr(
                    enum_tab.RELOC_TYPE_AARCH64.ABS64, d.size, d.fun.name)
            elif isinstance(d, ir.DataAddrMem):
                elfunit.AddMemAddr(
                    enum_tab.RELOC_TYPE_AARCH64.ABS64, d.size, d.mem.name, d.offset)
            else:
                assert False
        elfunit.MemEnd()

    sec_text = elfunit.sec_text
    for fun in unit.funs:
        elfunit.FunStart(fun.name, 16, assembler.NOP_BYTES)
        for jtb in fun.jtbs:
            elfunit.MemStart(jtb.name, 8, "rodata", True)
            for i in range(jtb.size):
                bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
                elfunit.AddBblAddr(
                    enum_tab.RELOC_TYPE_AARCH64.ABS64, 8, bbl.name)
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
                    # TODO
                    pass
                elif ins.opcode is o.RET:
                    for tmpl in isel_tab.EmitFunEpilog(ctx):
                        assembler.AddIns(elfunit,
                                         tmpl.MakeInsFromTmpl(None, ctx))

                else:
                    pattern = isel_tab.FindMatchingPattern(ins)
                    if not pattern:
                        print(f"@@ {ins} {ins.operands}")
                        for n, op in enumerate(ins.operands):
                            if isinstance(op, ir.Const):
                                print(f"op {n}: {op.value} [{op}]")
                            elif isinstance(op, ir.Stk):
                                print(f"op {n}: {op.slot} [{op}]")
                            else:
                                print(f"op {n}: {op}")
                        isel_tab.FindMatchingPattern(ins, diagnostic=True)
                    assert pattern, f"could not find pattern for\n{ins} {ins.operands}"
                    for tmpl in pattern.emit:
                        cpu_ins = tmpl.MakeInsFromTmpl(ins, ctx)
                        if _SimplifyCpuIns(cpu_ins):
                            assembler.AddIns(elfunit, cpu_ins)
        elfunit.FunEnd()
    elfunit.AddLinkerDefs()
    return elfunit


if __name__ == "__main__":
    import sys
    import argparse

    _ALLOWED_MODES = {"normal", "binary", "legalize", "reg_alloc_global",
                      "reg_alloc_local"}

    def main():
        parser = argparse.ArgumentParser(description='CodeGenA64')
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
