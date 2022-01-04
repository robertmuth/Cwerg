# (c) Robert Muth - see LICENSE for more info
from typing import List, Optional

from Base import ir
from Base import opcode_tab as o


def _InsCanonicalize(ins: ir.Ins, _fun: ir.Fun) -> Optional[List[ir.Ins]]:
    """
    * moves immediate into the the last operand slot if possible (ALU, CMP, COND_BRA)
    """
    opcode = ins.opcode
    if o.OA.COMMUTATIVE not in opcode.attributes:
        return None
    ops = ins.operands
    if opcode.kind is o.OPC_KIND.ALU:
        if isinstance(ops[1], ir.Const) and not isinstance(ops[2], ir.Const):
            ir.InsSwapOps(ins, 1, 2)
            return [ins]
    elif opcode is o.CMPEQ:
        if isinstance(ops[3], ir.Const) and not isinstance(ops[4], ir.Const):
            ir.InsSwapOps(ins, 3, 4)
            return [ins]
    elif opcode.kind is o.OPC_KIND.COND_BRA:
        if isinstance(ops[0], ir.Const) and not isinstance(ops[1], ir.Const):
            if opcode is o.BEQ or opcode is o.BNE:
                ir.InsSwapOps(ins, 0, 1)
                return [ins]
    else:
        assert False
    return None


def FunCanonicalize(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsCanonicalize)
