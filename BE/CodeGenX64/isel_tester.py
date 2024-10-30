#!/bin/env python3
"""Testing helper for table driven code selection"""

from BE.CpuX64 import symbolic
from BE.Base import serialize
from BE.Base import ir
from BE.CodeGenX64 import isel_tab
from BE.CodeGenX64 import regs

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

    pattern = isel_tab.FindMatchingPattern(ins)
    assert pattern
    print(
        f"PAT: reg:[{' '.join(a.name for a in pattern.type_constraints)}]  "
        f"op:[{' '.join(a.name for a in pattern.op_curbs)}]")
    for tmpl in pattern.emit:
        x64ins = tmpl.MakeInsFromTmpl(ins, ctx)
        name, ops = symbolic.InsSymbolize(x64ins, True)
        print(f"    {name} {' '.join(ops)}")


def Translate(fin):
    unit = serialize.UnitParseFromAsm(fin, cpu_regs=regs.CPU_REGS_MAP)
    for fun in unit.funs:
        ctx = regs.EmitContext(0, 0, 0)
        ctx.scratch_cpu_reg = regs.CPU_REGS_MAP["rax"]
        fun.FinalizeStackSlots()
        for bbl in fun.bbls:
            for ins in bbl.inss:
                print()
                HandleIns(ins, ctx)


if __name__ == "__main__":
    Translate(sys.stdin)
