#!/usr/bin/python3

"""Code Generation (Instruction Selection) for x86-64
"""

import collections
from typing import List, Dict, Any, Set, Optional
import enum

from Base import ir
from Base import opcode_tab as o
from CodeGenA64 import regs
import CpuX64.opcode_tab as x64
from Elf import enum_tab
from Util import cgen


@enum.unique
class OP_CURB(enum.IntEnum):
    """Immediate Curbs - describes constraints on the immediate values involved in patterns

    Used to determine if a pattern is a suitable match for a Cwerg IR instruction
    """
    INVALID = 0
    ZERO = 1
    ANY = 2
    REG = 3
    SP_REG = 4
    SIMM8 = 5
    SIMM16 = 6
    SIMM32 = 7
    SIMM64 = 8
    UIMM8 = 9
    UIMM16 = 10
    UIMM32 = 11
    UIMM64 = 12


class FIXARG(enum.Enum):
    NO_INDEX = 4
    SP = 4


@enum.unique
class PARAM(enum.Enum):
    """Placeholder in X64 instruction template for stuff that needs to be derived
    for the Cwerg instructions"""
    invalid = 0
    reg01 = 1
    reg2 = 3
    reg3 = 4
    reg4 = 5
    #
    num0 = 6
    num1 = 7
    num2 = 8
    num3 = 9
    num4 = 10
    #
    stk01 = 11
    stk2 = 12

    #


_RELOC_ARGS: Set[PARAM] = {
}


def _HandleReloc(cpuins: x64.Ins, pos: int, ins: ir.Ins, op: PARAM):
    assert not cpuins.has_reloc(), f"{cpuins.reloc_kind}"


def _ExtractTmplArgOp(ins: ir.Ins, arg: PARAM, ctx: regs.EmitContext) -> int:
    ops = ins.operands
    if arg is PARAM.reg01:
        assert ops[0] == ops[1]
        reg = ops[0]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    if arg is PARAM.reg2:
        reg = ops[2]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    elif arg is PARAM.num2:
        assert isinstance(ops[2], ir.Const)
        return ops[2].value
    else:
        assert False, f"could not extract op for {ins} {ins.operands} {arg}"


class InsTmpl:
    """Represents a template for an A32 instructions

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.

    args: a list of registers/constants/placeholders all values must be run through EncodeOperand
    """

    def __init__(self, opcode_name: str, args: List[Any]):
        opcode: x64.Opcode = x64.Opcode.OpcodesByName[opcode_name]
        assert args is not None
        assert len(args) == len(opcode.fields), f"num arg mismatch for {opcode_name}"
        for op in args:
            assert isinstance(op, (int, PARAM, FIXARG)), (
                f"unknown op {op} for {opcode.name} {args}")
        self.opcode = opcode
        self.args: List[Any] = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> x64.Ins:
        out = x64.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            if type(arg) == int:
                val = arg
            elif isinstance(arg, FIXARG):
                val = arg.value
            elif isinstance(arg, PARAM):
                val = _ExtractTmplArgOp(ins, arg, ctx)
            else:
                assert False, f"unknown param {repr(arg)}"

            assert isinstance(val, int), f"expected int {val}"
            out.operands.append(val)
            # note: this may alter the value we just appended
            if arg in _RELOC_ARGS:
                _HandleReloc(out, n, ins, arg)
        return out


_ALLOWED_OPERAND_TYPES_REG = {
    o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64,
    o.DK.U32, o.DK.S32,
    o.DK.U8, o.DK.S8,
    o.DK.U16, o.DK.S16,
    o.DK.F32, o.DK.F64,
}


class Pattern:
    """
    See ../Docs/instruction_selection.md
    """
    # groups all the patterns for a given opcode number together
    Table: Dict[int, List["Pattern"]] = collections.defaultdict(list)

    def __init__(self, opcode: o.Opcode, type_constraints: List[o.DK],
                 op_curbs: List[OP_CURB], emit: List[InsTmpl]):
        # the template, usually contains ArmIns except for the nop1 pattern
        self.emit = emit
        # how to fill the template params
        assert len(type_constraints) == len(
            opcode.operand_kinds), f"{opcode.name} {type_constraints} {opcode.operand_kinds}"
        assert len(type_constraints) == len(op_curbs)
        self.type_constraints = type_constraints
        self.opcode = opcode
        self.op_curbs = op_curbs
        for type_constr, op_constr, kind in zip(type_constraints, op_curbs,
                                                opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert op_constr in {OP_CURB.REG, OP_CURB.SP_REG}
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert op_constr in {}
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert op_constr is OP_CURB.INVALID, f"bad pattern for {opcode}"

        # we put all the patterns for given IR opcode into the same bucket
        Pattern.Table[opcode.no].append(self)

    def MatchesTypeCurbs(self, ins: ir.Ins) -> bool:
        for type_constr, op in zip(self.type_constraints, ins.operands):
            if type_constr is o.DK.INVALID:
                continue
            if isinstance(op, ir.Reg):
                if op.kind != type_constr:
                    return False
            elif isinstance(op, ir.Const):
                if op.kind != type_constr:
                    return False
            else:
                assert False
        return True

    def MatchesOpCurbs(self, ins: ir.Ins) -> bool:
        """
        """
        for pos, (op_curb, op) in enumerate(zip(self.op_curbs, ins.operands)):
            if op_curb is OP_CURB.INVALID:
                assert not isinstance(ir.Const, ir.Reg)
            elif op_curb is OP_CURB.REG:
                if not isinstance(op, ir.Reg):
                    return False
                if isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb is OP_CURB.SP_REG:
                if not isinstance(op, ir.Reg):
                    return False
                if not isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb in {OP_CURB.SIMM8, OP_CURB.SIMM16,
                             OP_CURB.SIMM32, OP_CURB.SIMM64}:
                assert isinstance(op, ir.Const)
                if op_curb is OP_CURB.SIMM8:
                    if (1 << 7) <= op.value or op.value < -(1 << 7):
                        return False
                elif op_curb is OP_CURB.SIMM16:
                    if (1 << 15) <= op.value or op.value < -(1 << 15):
                        return False
                elif op_curb is OP_CURB.SIMM32:
                    if (1 << 31) <= op.value or op.value < -(1 << 31):
                        return False
                elif op_curb is OP_CURB.SIMM64:
                    if (1 << 63) <= op.value or op.value < -(1 << 63):
                        return False
        return True

    def __str__(self):
        types = [x.name for x in self.type_constraints]
        curbs = [x.name for x in self.op_curbs]
        return f"PATTERN {self.opcode.name} [{' '.join(types)}] [{' '.join(curbs)}]"


_KIND_TO_IMM = {
    o.DK.U8: OP_CURB.UIMM8,
    o.DK.S8: OP_CURB.SIMM8,
    o.DK.U16: OP_CURB.UIMM16,
    o.DK.S16: OP_CURB.SIMM16,
    o.DK.U32: OP_CURB.UIMM32,
    o.DK.S32: OP_CURB.SIMM32,
    o.DK.U64: OP_CURB.SIMM32,  # not a typo
    o.DK.S64: OP_CURB.SIMM32,  # not a typo
}


OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.RET
}


def InitAlu():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for opc, x64_opc in [(o.AND, "and"),
                             (o.XOR, "xor"),
                             (o.ADD, "add"),
                             (o.OR, "or"),
                             (o.SUB, "sub")]:
            bw = kind1.bitwidth()
            iw = 32 if bw == 64 else bw
            Pattern(opc, [kind1] * 3,
                    [OP_CURB.REG, OP_CURB.REG, OP_CURB.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr",
                             [PARAM.reg01, PARAM.reg2])])
            Pattern(opc, [kind1] * 3,
                    [OP_CURB.SP_REG, OP_CURB.SP_REG, OP_CURB.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_r",
                             [FIXARG.SP, FIXARG.NO_INDEX,
                              PARAM.stk01, 0, PARAM.reg2])])
            Pattern(opc, [kind1] * 3,
                    [OP_CURB.REG, OP_CURB.REG, OP_CURB.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32",
                             [PARAM.reg01, FIXARG.SP, FIXARG.NO_INDEX,
                              PARAM.stk2, 0])])
            Pattern(opc, [kind1] * 3,
                    [OP_CURB.REG, OP_CURB.REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_imm{iw}", [PARAM.reg01, PARAM.num2])])
            Pattern(opc, [kind1] * 3,
                    [OP_CURB.SP_REG, OP_CURB.SP_REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_imm{iw}",
                             [FIXARG.SP, FIXARG.NO_INDEX,
                              PARAM.stk01, 0, PARAM.num2])])


def InitCondBra():
    pass


def FindMatchingPattern(ins: ir.Ins) -> Optional[Pattern]:
    """Returns the best pattern matching `ins` or None

    This can only be called AFTER the stack has been finalized
    """
    patterns = Pattern.Table[ins.opcode.no]
    # print(f"@@ {ins} {ins.operands}")
    for p in patterns:
        # print(f"@@ trying pattern {p}")
        if p.MatchesTypeCurbs(ins) and p.MatchesOpCurbs(ins):
            return p
    # assert False, f"Could not find a matching patterns for {ins}. tried:\n{patterns}"
    return None

InitAlu()
