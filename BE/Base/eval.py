"""The file contains helpers for evaluating instructions where all the operands
are known/constant.

"""

from typing import Optional
from BE.Base import ir
from IR import opcode_tab as o

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


def MakeAllOnesMask(n_ones: int) -> int:
    return (1 << n_ones) - 1


def SignedIntFromBits(data: int, n_bits: int) -> int:
    """Takes the lower n_bits bit from data and converts them into an n_bits signed int"""
    mask = (1 << n_bits) - 1
    data &= mask
    if data & (1 << (n_bits - 1)):
        return data - (1 << n_bits)
    else:
        return data


def _truncate(dk: o.DK, val):
    if dk.flavor() == o.DK_FLAVOR_R:
        return val
    elif dk.flavor() == o.DK_FLAVOR_U:
        return val & ((1 << dk.bitwidth()) - 1)
    else:
        return SignedIntFromBits(val, dk.bitwidth())


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
    return ir.Const(op1.kind, _truncate(op1.kind, evaluator(op1.value, op2.value)))


def EvaluatateALU1(opcode: o.Opcode, op: ir.Const) -> Optional[ir.Const]:
    evaluator = _EVALUATORS_ALU1.get(opcode)
    assert evaluator, f"Evaluator NYI for: {opcode}"
    return ir.Const(op.kind, _truncate(op.kind, evaluator(op.kind, op.value)))


def EvaluatateCondBra(opcode: o.Opcode, op1: ir.Const, op2: ir.Const) -> bool:
    evaluator = _EVALUATORS_COND_BRA.get(opcode)
    assert evaluator, f"Evaluator NYI for: {opcode}"
    return evaluator(op1.value, op2.value)


def AddOffsets(a: ir.Const, b: ir.Const) -> ir.Const:
    return ir.OffsetConst(a.value + b.value)


def ConvertIntValue(kind_dst: o.DK, val: ir.Const) -> ir.Const:
    kind_src = val.kind
    width_dst = kind_dst.bitwidth()
    width_src = kind_src.bitwidth()
    masked = val.value & ((1 << width_dst) - 1)
    if kind_dst.flavor() == o.DK_FLAVOR_U:
        return ir.Const(kind_dst, val.value & masked)
    # print ("@@@", kind_dst.name, width_dst, kind_src, width_src, num_kind, x)
    elif width_dst > width_src:
        return ir.Const(kind_dst, val.value)
    else:
        # dst is ACS and width_dst <= width_src
        will_be_negative = val.value & (1 << (width_dst - 1))
        if will_be_negative:
            return ir.Const(kind_dst, masked - (1 << width_dst))
        return ir.Const(kind_dst, masked)
