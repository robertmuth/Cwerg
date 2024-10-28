#!/usr/bin/python3
"""Testing helper for table driven code selection"""

from typing import Any
import sys

from Base import serialize
from Base import ir

from BE.CpuA32 import opcode_tab as a32
from BE.CpuA32 import symbolic

from CodeGenA32 import isel_tab
from CodeGenA32 import regs


def OpToStr(op: Any) -> str:
    if isinstance(op, (isel_tab.PARAM, a32.PRED, a32.REG, a32.SHIFT)):
        return op.name
    assert isinstance(op, int)
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
            f"PAT: reg:[{' '.join(a.name for a in pattern.type_curbs)}]  "
            f"imm:[{' '.join(a.name for a in pattern.imm_curbs)}]")
        for tmpl in pattern.emit:
            armins = tmpl.MakeInsFromTmpl(ins, ctx)
            name, ops = symbolic.InsSymbolize(armins)
            print(f"    {name} {' '.join(ops)}")


def Translate(fin):
    unit = serialize.UnitParseFromAsm(fin, cpu_regs=regs.CPU_REGS_MAP)
    for fun in unit.funs:
        ctx = regs.EmitContext(0xfc0, 0xfc0, 0xffff0000, 0xffff0000, 66)
        if "gpr_scratch" in fun.name:
            ctx.scratch_cpu_reg = regs.GPR_REGS[6]
        fun.FinalizeStackSlots()
        for bbl in fun.bbls:
            for ins in bbl.inss:
                print()
                HandleIns(ins, ctx)


if __name__ == "__main__":
    Translate(sys.stdin)
