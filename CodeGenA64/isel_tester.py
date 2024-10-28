#!/usr/bin/python3
"""Testing helper for table driven code selection"""

from BE.CpuA64 import symbolic
from Base import serialize
from Base import ir
from CodeGenA64 import isel_tab
from CodeGenA64 import regs

from typing import Any
import sys


def OpToStr(op: Any) -> str:
    return str(op)


def OpTypeStr(op: Any) -> str:
    if isinstance(op, ir.Reg):
        return op.kind.name
    elif isinstance(op, ir.Const):
        return op.kind.name
    else:
        return "_"


def HandleIns(ins: ir.Ins, ctx: regs.EmitContext):
    print("INS: " + serialize.InsRenderToAsm(
        ins).strip() + f"  [{' '.join(OpTypeStr(o) for o in ins.operands)}]")
    if ins.opcode in isel_tab.OPCODES_REQUIRING_SPECIAL_HANDLING:
        print(f"    SPECIAL")
        return
    mismatches = isel_tab.FindtImmediateMismatchesInBestMatchPattern(ins, False)
    if mismatches == isel_tab.MATCH_IMPOSSIBLE:
        print(f"    MATCH_IMPOSSIBLE")
    elif mismatches != 0:
        pattern = isel_tab.FindMatchingPattern(ins)
        assert pattern is None
        print(f"    mismatches: {mismatches:x}")
    else:
        pattern = isel_tab.FindMatchingPattern(ins)
        print(
            f"PAT: reg:[{' '.join(a.name for a in pattern.type_constraints)}]  "
            f"imm:[{' '.join(a.name for a in pattern.imm_curbs)}]")
        for tmpl in pattern.emit:
            armins = tmpl.MakeInsFromTmpl(ins, ctx)
            name, ops = symbolic.InsSymbolize(armins)
            print(f"    {name} {' '.join(ops)}")


def Translate(fin):
    unit = serialize.UnitParseFromAsm(fin, cpu_regs=regs.CPU_REGS_MAP)
    for fun in unit.funs:
        ctx = regs.EmitContext(0, 0, 0)
        ctx.scratch_cpu_reg = ir.CPU_REG_INVALID

        ctx.scratch_cpu_reg = ir.CPU_REG_INVALID
        fun.FinalizeStackSlots()
        for bbl in fun.bbls:
            for ins in bbl.inss:
                if "gpr_scratch" in fun.name:
                    ctx.scratch_cpu_reg = regs.CPU_REGS_MAP["x8"]
                print()
                HandleIns(ins, ctx)


if __name__ == "__main__":
    Translate(sys.stdin)
