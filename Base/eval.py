"""The file contains helpers for evaluating instructions where all the operands
are known/constant.

"""

from typing import List, Dict, Optional
from Base import ir
from Base import opcode_tab as o

# TODO: naive implementation -> needs a lot more scrutiny
_EVALUATORS_ALU = {
    o.ADD: lambda x, y: x + y,
    o.SUB: lambda x, y: x - y,
    o.MUL: lambda x, y: x * y,
    o.DIV: lambda x, y: x // y,
    o.SHL: lambda x, y: x << y,
    o.OR: lambda x, y: x | y,
    o.AND: lambda x, y: x & y,
    o.XOR: lambda x, y: x ^ y,
}

_EVALUATORS_COND_BRA = {
    o.BEQ: lambda x, y: x == y,
    o.BNE: lambda x, y: x != y,
    o.BLT: lambda x, y: x < y,
    o.BLE: lambda x, y: x <= y,
}


def Cnttz(kind: o.DK, val: int):
    if val == 0:
        return kind.bitwidth()
    n = 0
    while val & 1 == 0:
        val >>= 1
        n += 1
    return n


def Cntlz(kind: o.DK, val: int):
    if val == 0:
        return kind.bitwidth()
    mask = 1 << (kind.bitwidth() - 1)
    n = 0
    while val & mask:
        mask >>= 1
        n += 1
    return n


_EVALUATORS_ALU1 = {
    o.CNTLZ: Cntlz,
    o.CNTTZ: Cnttz,
}


def EvaluatateALU(opcode: o.Opcode, op1: ir.Const, op2: ir.Const) -> ir.Const:
    evaluator = _EVALUATORS_ALU.get(opcode)
    assert evaluator, f"Evaluator NYI for: {opcode}"
    return ir.Const(op1.kind, evaluator(op1.value, op2.value))


def EvaluatateALU1(opcode: o.Opcode, op: ir.Const) -> Optional[ir.Const]:
    evaluator = _EVALUATORS_ALU1.get(opcode)
    assert evaluator, f"Evaluator NYI for: {opcode}"
    return ir.Const(op.kind, evaluator(op.kind, op.value))


def EvaluatateCondBra(opcode: o.Opcode, op1: ir.Const, op2: ir.Const) -> bool:
    evaluator = _EVALUATORS_COND_BRA.get(opcode)
    assert evaluator, f"Evaluator NYI for: {opcode}"
    return evaluator(op1.value, op2.value)


def ConvertIntValue(kind_dst: o.DK, val: ir.Const) -> ir.Const:
    kind_src = val.kind
    width_dst = kind_dst.bitwidth()
    width_src = kind_src.bitwidth()
    # print ("@@@", kind_dst.name, width_dst, kind_src, width_src, num_kind, x)
    masked = val.value & ((1 << width_dst) - 1)
    if width_dst > width_src:
        if kind_dst.flavor() == kind_src.flavor() or kind_src.flavor() == o.DK_FLAVOR_U:
            return ir.Const(kind_dst, val.value)
        # kind_dst == RK_U, kind_src == RK_S
        return ir.Const(kind_dst, masked)
    elif kind_dst.flavor() == o.DK_FLAVOR_U:
        return ir.Const(kind_dst, masked)
    else:
        # kind_dst[0] == RK_S
        sign = val.value & (1 << (width_dst - 1))
        if sign == 0:
            return ir.Const(kind_dst, masked)
        return ir.Const(kind_dst, masked - (1 << width_dst))
