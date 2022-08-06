#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  X64 (x86-64)

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

from CpuX64 import opcode_tab as x64
from CpuX64 import symbolic
from CpuX64 import assembler

from CodeGenX64 import isel_tab
from CodeGenX64 import regs
from CodeGenX64 import legalize

from Elf import enum_tab
from Elf import elf_unit


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
        legalize.PhaseLegalization(fun, unit, opt_stats, fout)


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
    out = [f".localmem {jtb.name} 8 rodata"]
    for i in range(jtb.size):
        bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
        out.append(f"    .addr.bbl 8 {bbl.name}")
    out.append(".endmem")
    return out


def _RenderIns(ins: x64.Ins) -> str:
    name, ops = symbolic.InsSymbolize(ins, True)
    ops_str = " " + " ".join(ops) if ops else ""
    return f"    {name}{ops_str}"


# Note: mv_32_r_mr is NOT a nop. It clears the upper bits.
_REG_MOV_OPCODES = {
    x64.Opcode.name_to_opcode[f"mov_{bw}_r_mr"] for bw in [8, 16, 64]}


def _SimplifyCpuIns(cpu_ins: x64.Ins) -> bool:
    # TODO: rewrite instruction to a simpler variant
    if cpu_ins.opcode in _REG_MOV_OPCODES and cpu_ins.operands[0] == cpu_ins.operands[1]:
        return False
    return True


def _FunCodeGenText(fun: ir.Fun, _mod: ir.Unit) -> List[str]:
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
            elif ins.opcode is o.INLINE:
                out.append("    " + str(ins.operands[0], "ascii"))
            else:
                pattern = isel_tab.FindMatchingPattern(ins)
                assert pattern, (f"could not find pattern for\n{ins} {ins.operands} "
                                 f"in {fun.name}:{bbl.name}")
                for tmpl in pattern.emit:
                    cpu_ins = tmpl.MakeInsFromTmpl(ins, ctx)
                    if _SimplifyCpuIns(cpu_ins):
                        out.append(_RenderIns(cpu_ins))
    out.append(f".endfun")
    return out


def EmitUnitAsText(unit: ir.Unit, fout):
    # we emit the memory stuff AFTER the code since the code generation may add new
    # memory for Consts
    for mem in unit.mems:
        assert mem.kind != o.MEM_KIND.EXTERN, f"bad MEM {mem}"
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
        assert mem.kind != o.MEM_KIND.EXTERN, f"bad MEM {mem}"
        if mem.kind == o.MEM_KIND.BUILTIN:
            continue
        cpu_mem = _MemCodeGenText(mem, unit)
        out.mems.append((mem.name, cpu_mem))
        out.mem_syms[mem.name] = cpu_mem
    for fun in unit.funs:
        if fun.kind is not o.FUN_KIND.NORMAL:
            continue
        cpu_fun = _FunCodeGenText(fun, unit)
        out.funs.append((fun.name, cpu_fun))
        out.fun_syms[fun.name] = cpu_fun
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
                    enum_tab.RELOC_TYPE_X86_64.X_64, d.size, d.fun.name)
            elif isinstance(d, ir.DataAddrMem):
                elfunit.AddMemAddr(
                    enum_tab.RELOC_TYPE_X86_64.X_64, d.size, d.mem.name, d.offset)
            else:
                assert False
        elfunit.MemEnd()

    sec_text = elfunit.sec_text
    for fun in unit.funs:
        # print (f"Processing {fun.name}")
        elfunit.FunStart(fun.name, 16, assembler.TextPadder)
        for jtb in fun.jtbs:
            elfunit.MemStart(jtb.name, 8, "rodata", True)
            for i in range(jtb.size):
                bbl = jtb.bbl_tab.get(i, jtb.def_bbl)
                elfunit.AddBblAddr(
                    enum_tab.RELOC_TYPE_X86_64.X_64, 8, bbl.name)
            elfunit.MemEnd()
        ctx = regs.FunComputeEmitContext(fun)

        for tmpl in isel_tab.EmitFunProlog(ctx):
            assembler.AddIns(elfunit, tmpl.MakeInsFromTmpl(None, ctx))

        for bbl in fun.bbls:
            elfunit.AddLabel(bbl.name, 1, assembler.TextPadder)
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
                elif ins.opcode is o.INLINE:
                    tokens = str(ins.operands[0], "ascii").split()
                    cpu_ins = symbolic.InsFromSymbolized(tokens[0], tokens[1:])
                    # intentionally no simplification for now
                    assembler.AddIns(elfunit, cpu_ins)
                else:
                    pattern = isel_tab.FindMatchingPattern(ins)
                    assert pattern, f"could not find pattern in fun {fun.name}\n{ins} {ins.operands}"
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

        log = None
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
            x64unit = EmitUnitAsBinary(unit)
            exe = assembler.Assemble(x64unit, True)
            exe.save(open(args.output, "wb"))
            os.chmod(args.output, stat.S_IREAD | stat.S_IEXEC | stat.S_IWRITE)
            return

        fout = sys.stdout if args.output == "-" else open(args.output, "w")

        # we need to legalize all functions first as this may change the signature
        # and fills in cpu reg usage which is used by subsequent interprocedural opts.
        LegalizeAll(unit, opt_stats, log)
        if args.mode == "legalize":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        RegAllocGlobal(unit, opt_stats, log)
        if args.mode == "reg_alloc_global":
            print("\n".join(serialize.UnitRenderToASM(unit)), file=fout)
            return

        RegAllocLocal(unit, opt_stats, log)
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
