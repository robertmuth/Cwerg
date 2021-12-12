#!/usr/bin/python3
"""Testing helper for table driven code selection"""

from CpuX64 import symbolic
from Base import serialize
from Base import ir
from CodeGenX64 import isel_tab
from CodeGenX64 import regs

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

    pattern = isel_tab.FindMatchingPattern(ins)
    print(
        f"PAT: reg:[{' '.join(a.name for a in pattern.type_constraints)}]  "
        f"imm:[{' '.join(a.name for a in pattern.op_curbs)}]")
    for tmpl in pattern.emit:
        x64ins = tmpl.MakeInsFromTmpl(ins, ctx)
        name, ops = symbolic.InsSymbolize(x64ins)
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
                    ctx.scratch_cpu_reg = regs.CPU_REGS_MAP["rax"]
                print()
                HandleIns(ins, ctx)


if __name__ == "__main__":
    Translate(sys.stdin)
