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
class C(enum.IntEnum):
    """Curbs/Constraints - describes constraints on the immediate values involved in patterns

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


class F(enum.Enum):
    """Fixed params"""
    NO_INDEX = 1
    NO_BASE = 2
    SP = 3
    RIP = 4
    SCALE1 =5


_F_TO_INT = {
    F.NO_INDEX: 4,
    F.NO_BASE: 5,
    F.SP: 4,
    F.RIP: 0,
    F.SCALE1: 0,
}


@enum.unique
class P(enum.Enum):
    """Placeholder/Parameter in X64 instruction template for stuff that needs to be derived
    for the Cwerg instructions"""
    invalid = 0
    reg01 = 1
    reg0 = 2
    reg1 = 3
    reg2 = 4
    reg3 = 5
    reg4 = 6
    tmp_gpr = 7
    tmp_flt = 8
    scratch_gpr = 9
    #
    num0 = 10
    num1 = 11
    num2 = 12
    num3 = 13
    num4 = 14
    #
    spill01 = 20
    spill0 = 21
    spill1 = 22
    spill2 = 23
    stk1_offset2 = 24
    stk1 = 25
    #
    bbl0 = 30
    bbl2 = 31
    #
    mem1_num2_prel = 40
    mem0_num1_prel = 41

    fun1_prel = 45
    jtb1_prel = 46


_OP_TO_RELOC_KIND = {
    P.bbl0: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.bbl2: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.fun1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.mem1_num2_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.jtb1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
}


def _HandleReloc(cpuins: x64.Ins, pos: int, ins: ir.Ins, op: P):
    assert not cpuins.has_reloc(), f"{cpuins.reloc_kind}"
    if op is P.bbl2:
        bbl = ins.operands[2]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is P.bbl0:
        bbl = ins.operands[0]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is P.fun1_prel:
        fun = ins.operands[1]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        assert fun.kind is not o.FUN_KIND.EXTERN, f"undefined fun: {fun.name}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op is P.mem1_num2_prel:
        mem = ins.operands[1]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        assert mem.kind is not o.MEM_KIND.EXTERN, f"undefined fun: {mem.name}"
        num = ins.operands[2]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert cpuins.operands[pos] == 0
        cpuins.operands[pos] = num.value
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, mem.name)
    elif op is P.jtb1_prel:
        jtb = ins.operands[1]
        assert isinstance(jtb, ir.Jtb), f"{ins} {jtb}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, jtb.name)
    else:
        assert False


def _ExtractTmplArgOp(ins: ir.Ins, arg: P, ctx: regs.EmitContext) -> int:
    ops = ins.operands
    if arg is P.reg01:
        assert ops[0] == ops[1]
        reg = ops[0]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    elif arg in {P.reg0, P.reg1, P.reg2}:
        pos = arg.value - P.reg0.value
        reg = ops[pos]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    elif arg is P.num2:
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
        # Note, the sanity checks below need to be adjusted as needed
        for op, field in zip(args, opcode.fields):
            assert isinstance(op, (int, P, F)), (
                f"unknown op {op} for {opcode.name} {args}")
            if field is x64.OK.SIB_SCALE:
                assert op in {F.SCALE1}, f"{op}"
            elif field in {x64.OK.MODRM_REG8, x64.OK.MODRM_REG16, x64.OK.MODRM_REG32, x64.OK.MODRM_REG64,
                           x64.OK.MODRM_RM_REG8, x64.OK.MODRM_RM_REG16, x64.OK.MODRM_RM_REG32,
                           x64.OK.MODRM_RM_REG64}:
                assert op in {P.reg0, P.reg1, P.reg2, P.reg01, P.tmp_gpr, P.scratch_gpr}, f"{op}"
            elif field in {x64.OK.MODRM_XREG32, x64.OK.MODRM_XREG64,
                           x64.OK.MODRM_RM_XREG32, x64.OK.MODRM_RM_XREG64}:
                assert op in {P.reg0, P.reg1, P.reg2, P.reg01, P.tmp_flt}, f"{op}"
            elif field is x64.OK.SIB_INDEX:
                assert op in {F.NO_INDEX, P.reg1, P.reg2, P.tmp_gpr, P.scratch_gpr}, f"{op}"
            elif field is x64.OK.SIB_BASE:
                assert op in {F.SP, P.reg01, P.reg0, P.reg1, P.tmp_gpr, P.scratch_gpr}, f"{op}"
            elif field is x64.OK.RIP_BASE:
                assert op in {F.RIP}, f"{op}"
            elif field is x64.OK.OFFABS32:
                assert op in {P.spill0, P.spill1, P.spill2, P.spill01, P.num1, P.num2,
                              P.fun1_prel, P.mem0_num1_prel, P.mem1_num2_prel,
                              P.stk1_offset2, P.stk1}, f"{op}"
            elif field is x64.OK.OFFABS8:
                assert op in {0}, f"{op}"
            elif field in {x64.OK.IMM8, x64.OK.IMM16, x64.OK.IMM32, x64.OK.IMM32_64}:
                assert op in {P.num0, P.num1, P.num2}, f"{op}"
            elif field is x64.OK.OFFPCREL32:
                assert op in {P.bbl0, P.bbl2}, f"{op}"
            else:
                assert False, f"{opcode_name}  {opcode.fields} {args}  -  {op}, {field}"

        self.opcode = opcode
        self.args: List[Any] = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> x64.Ins:
        out = x64.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            if type(arg) == int:
                val = arg
            elif isinstance(arg, F):
                val = _F_TO_INT[arg]
            elif isinstance(arg, P):
                val = _ExtractTmplArgOp(ins, arg, ctx)
            else:
                assert False, f"unknown param {repr(arg)}"

            assert isinstance(val, int), f"expected int {val}"
            out.operands.append(val)
            # note: this may alter the value we just appended
            if arg in _OP_TO_RELOC_KIND:
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
                 op_curbs: List[C], emit: List[InsTmpl]):
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
                assert op_constr in {C.REG, C.SP_REG}
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert op_constr in {}
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert op_constr is C.INVALID, f"bad pattern for {opcode}"

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
            if op_curb is C.INVALID:
                assert not isinstance(ir.Const, ir.Reg)
            elif op_curb is C.REG:
                if not isinstance(op, ir.Reg):
                    return False
                if isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb is C.SP_REG:
                if not isinstance(op, ir.Reg):
                    return False
                if not isinstance(op.cpu_reg, ir.StackSlot):
                    return False
            elif op_curb in {C.SIMM8, C.SIMM16,
                             C.SIMM32, C.SIMM64}:
                if not isinstance(op, ir.Const):
                    return False
                if op_curb is C.SIMM8:
                    if (1 << 7) <= op.value or op.value < -(1 << 7):
                        return False
                elif op_curb is C.SIMM16:
                    if (1 << 15) <= op.value or op.value < -(1 << 15):
                        return False
                elif op_curb is C.SIMM32:
                    if (1 << 31) <= op.value or op.value < -(1 << 31):
                        return False
                elif op_curb is C.SIMM64:
                    if (1 << 63) <= op.value or op.value < -(1 << 63):
                        return False
        return True

    def __str__(self):
        types = [x.name for x in self.type_constraints]
        curbs = [x.name for x in self.op_curbs]
        return f"PATTERN {self.opcode.name} [{' '.join(types)}] [{' '.join(curbs)}]"


def InsTmplStkSt(dk: o.DK, spill: P, src):
    return InsTmpl(f"mov_{dk.bitwidth()}_mbis32_r", [F.SP, F.NO_INDEX, F.SCALE1, spill, src])


def InsTmplStkLd(dk: o.DK, dst, spill: P):
    return InsTmpl(f"mov_{dk.bitwidth()}_r_mbis32", [dst, F.SP, F.NO_INDEX, F.SCALE1, spill])


_KIND_TO_IMM = {
    o.DK.U8: C.UIMM8,
    o.DK.S8: C.SIMM8,
    o.DK.U16: C.UIMM16,
    o.DK.S16: C.SIMM16,
    o.DK.U32: C.UIMM32,
    o.DK.S32: C.SIMM32,
    o.DK.U64: C.SIMM32,  # not a typo
    o.DK.S64: C.SIMM32,  # not a typo
}

OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.RET
}


def InitAluInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        for opc, x64_opc in [(o.AND, "and"),
                             (o.XOR, "xor"),
                             (o.ADD, "add"),
                             (o.OR, "or"),
                             (o.SUB, "sub")]:
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr",
                             [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_r",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32",
                             [P.reg01, F.SP, F.NO_INDEX, F.SCALE1, P.spill2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    [InsTmpl(f"mov_{bw}_r_mbis32",
                             [P.tmp_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.spill2]),
                     InsTmpl(f"{x64_opc}_{bw}_mbis32_r",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.tmp_gpr])])
            #
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_imm{iw}", [P.reg01, P.num2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.num2])])


def InitAluFlt():
    for kind1, suffix in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        for opc, x64_opc in [(o.ADD, "adds"),
                             (o.SUB, "subs"),
                             (o.MUL, "muls"),
                             (o.DIV, "divs")]:
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx",
                             [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.reg01, F.SP, F.NO_INDEX, F.SCALE1, P.spill2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.REG],
                    [InsTmpl(f"movs{suffix}_x_mbis32",
                             [P.tmp_flt, F.SP, F.NO_INDEX, F.SCALE1, P.spill01]),
                     InsTmpl(f"{x64_opc}{suffix}_x_mx",
                             [P.tmp_flt, P.reg2]),
                     InsTmpl(f"movs{suffix}_mbis32_x",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.tmp_flt])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    [InsTmpl(f"movs{suffix}_x_mbis32",
                             [P.tmp_flt, F.SP, F.NO_INDEX, F.SCALE1, P.spill01]),
                     InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.tmp_flt, F.SP, F.NO_INDEX, F.SCALE1, P.spill2]),
                     InsTmpl(f"movs{suffix}_mbis32_x",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.tmp_flt])])

        for opc, x64_opc in [(o.SQRT, "sqrts")]:
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.reg0, P.reg1])])
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.reg0, F.SP, F.NO_INDEX, F.SCALE1, P.spill1])])
            Pattern(opc, [kind1] * 2,
                    [C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx",
                             [P.tmp_flt, P.reg1]),
                     InsTmpl(f"movs{suffix}_mbis32_x",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill0, P.tmp_flt])])
            Pattern(opc, [kind1] * 2,
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32",
                             [P.tmp_flt, F.SP, F.NO_INDEX, F.SCALE1, P.spill1]),
                     InsTmpl(f"movs{suffix}_mbis32_x",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill0, P.tmp_flt])])


# http://unixwiz.net/techtips/x86-jumps.html
def _GetJmp(dk: o.DK, opc):
    if opc is o.BEQ:
        return "je"
    elif opc is o.BNE:
        return "jne"
    elif opc is o.BLT:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jl"
        else:
            return "jb"
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jle"
        else:
            return "jbe"


def _GetJmpSwp(dk: o.DK, opc):
    if opc is o.BEQ:
        return "je"
    elif opc is o.BNE:
        return "jne"
    elif opc is o.BLT:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jg"
        else:
            return "ja"
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jge"
        else:
            return "jae"


def InitCondBraInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        for opc in [o.BEQ, o.BNE, o.BLT, o.BLE]:
            x64_jmp = _GetJmp(kind1, opc)
            x64_jmp_swp = _GetJmpSwp(kind1, opc)
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mr", [P.reg0, P.reg1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_r",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill0, P.reg2]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mbis32",
                             [P.reg0, F.SP, F.NO_INDEX, F.SCALE1, P.spill1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.SP_REG, C.INVALID],
                    [InsTmplStkLd(kind1, P.tmp_gpr, P.spill0),
                     InsTmpl(f"cmp_{bw}_r_mbis32",
                             [P.tmp_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.spill1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg0, P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill0, P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg1, P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}",
                             [F.SP, F.NO_INDEX, F.SCALE1, P.spill1, P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])


_EXTEND_TO_64bit = {
    o.DK.U8: "movzx_64_8_",
    o.DK.S8: "movsx_64_8_",
    o.DK.U16: "movzx_64_16_",
    o.DK.S16: "movsx_64_16_",
    o.DK.U32: "mov_32_",
    o.DK.S32: "movsxd_64_",
}


def ExtendRegTo64Bit(reg, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_TO_64bit.get(dk)
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc + "r_mr", [reg, reg])]


def ExtendRegTo64BitFromSP(reg, spill, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_TO_64bit.get(dk)
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc + "r_mbis32", [reg, F.SP, F.NO_INDEX, F.SCALE1, spill])]


def InitLea():
    # LEA_FUN dst_reg fun
    Pattern(o.LEA_FUN, [o.DK.C64, o.DK.INVALID],
            [C.REG, C.INVALID],
            [InsTmpl("lea_64_r_mpc32", [P.reg0, F.RIP, P.fun1_prel])])
    Pattern(o.LEA_FUN, [o.DK.C64, o.DK.INVALID],
            [C.SP_REG, C.INVALID],
            [InsTmpl("lea_64_r_mpc32", [P.tmp_gpr, F.RIP, P.fun1_prel]),
             InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])

    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        # LEA_MEM  dst_reg mem offset_reg will be rewritten so do not handle it here
        # LEA_MEM dst_reg mem const
        Pattern(o.LEA_MEM, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mpc32", [P.reg0, F.RIP, P.mem1_num2_prel])])
        Pattern(o.LEA_MEM, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mpc32", [P.tmp_gpr, F.RIP, P.mem1_num2_prel]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])
        # LEA dstsrc_reg dstsrc_reg const  [note we assume the first two regs are the same]
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32",
                         [P.reg01, P.reg01, F.NO_INDEX, F.SCALE1, P.num2])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.SP_REG, C.SP_REG, C.SIMM32],
                [InsTmpl(f"add_64_mbis32_imm32",
                         [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.num2])])
        # LEA dstsrc_reg dstsrc_reg offset_reg
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis8", [P.reg01, P.reg01, P.reg2, F.SCALE1, 0])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.SP_REG, C.SP_REG, C.REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl(f"add_64_mbis32_r", [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.reg2])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("add_64_r_mr", [P.reg01, P.reg2])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.SP_REG, C.SP_REG, C.SP_REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl(f"add_64_mbis32_r",
                         [F.SP, F.NO_INDEX, F.SCALE1, P.spill01, P.reg2])])
        # LEA_STK dst_reg stk const
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32",
                         [P.reg0, F.SP, F.NO_INDEX, F.SCALE1, P.stk1_offset2])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32",
                         [P.tmp_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.stk1_offset2]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])
        # LEA_STK dst_reg stk offset_reg
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis32", [P.reg0, F.SP, P.reg2, F.SCALE1, P.stk1])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.REG],
                ExtendRegTo64Bit(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis32",
                         [P.tmp_gpr, F.SP, P.reg2, F.SCALE1, P.stk1]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("lea_64_r_mbis32",
                         [P.reg0, F.SP, P.tmp_gpr, F.SCALE1, P.stk1])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("lea_64_r_mbis32",
                         [P.tmp_gpr, F.SP, P.tmp_gpr, F.SCALE1, P.stk1]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])


def InitLoad():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for kind2 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                      o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
            bw = kind2.bitwidth()
            # LD_MEM dst_reg mem reg_offset will be rewritten so do not handle it here
            # LD_MEM dst_reg mem const
            Pattern(o.LD_MEM, [kind2, o.DK.INVALID, kind1],
                    [C.REG, C.INVALID, C.SIMM32],
                    [InsTmpl(f"mov_{bw}_r_mpc32",
                             [P.reg0, F.RIP, P.mem1_num2_prel])])
            Pattern(o.LD_MEM, [kind2, o.DK.INVALID, kind1],
                    [C.SP_REG, C.INVALID, C.SIMM32],
                    [InsTmpl(f"mov_{bw}_r_mpc32",
                             [P.tmp_gpr, F.RIP, P.mem1_num2_prel]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            # LD dst_reg base_reg const
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.SIMM32],
                    [InsTmpl(f"mov_{bw}_r_mbis32",
                             [P.reg0, P.reg1, F.NO_INDEX, F.SCALE1, P.num2])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.SIMM32],
                    [InsTmpl(f"mov_{bw}_r_mbis32",
                             [P.tmp_gpr, P.reg1, F.NO_INDEX, F.SCALE1, P.num2]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.SIMM32],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(f"mov_{bw}_r_mbis32",
                             [P.reg0, P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num2])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.SIMM32],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(f"mov_{bw}_r_mbis32",
                             [P.tmp_gpr, P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num2]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            # LD dst_reg base_reg offset_reg
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.REG],
                    ExtendRegTo64Bit(P.reg2, kind1) +
                    [InsTmpl(f"mov_{bw}_r_mbis8", [P.reg0, P.reg1, P.reg2, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.REG],
                    ExtendRegTo64Bit(P.reg2, kind1) +
                    [InsTmpl(f"mov_{bw}_r_mbis8",
                             [P.tmp_gpr, P.reg1, P.reg2, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.REG],
                    ExtendRegTo64Bit(P.reg2, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(f"mov_{bw}_r_mbis8",
                             [P.reg0, P.tmp_gpr, P.reg2, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"mov_{bw}_r_mbis8", [P.reg0, P.reg1, P.tmp_gpr, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.REG],
                    ExtendRegTo64Bit(P.reg2, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(f"mov_{bw}_r_mbis8", [P.tmp_gpr, P.tmp_gpr, P.reg2, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"mov_{bw}_r_mbis8", [P.tmp_gpr, P.reg1, P.tmp_gpr, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"add_64_r_mbis32", [P.tmp_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.spill1]),
                     InsTmpl(f"mov_{bw}_r_mbis8", [P.reg0, P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"add_64_r_mbis32", [P.tmp_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.spill1]),
                     InsTmpl(f"mov_{bw}_r_mbis8", [P.tmp_gpr, P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, P.tmp_gpr)])


def InitStore():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for kind2 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                      o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
            bw = kind2.bitwidth()
            # ST_MEM mem reg_offset src_reg will be rewritten so do not handle it here
            # ST_MEM mem const src_reg
            Pattern(o.ST_MEM, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.REG],
                    [InsTmpl(f"mov_{bw}_mpc32_r",
                             [F.RIP, P.mem0_num1_prel, P.reg2])])
            Pattern(o.ST_MEM, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(kind2, P.tmp_gpr, P.spill2),
                     InsTmpl(f"mov_{bw}_mpc32_r",
                             [F.RIP, P.mem0_num1_prel, P.tmp_gpr])])
            # ST base_reg const src_reg
            Pattern(o.ST, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SIMM32, C.REG],
                    [InsTmpl(f"mov_{bw}_mbis32_r",
                             [P.reg0, F.NO_INDEX, F.SCALE1, P.num1, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(kind2, P.tmp_gpr, P.spill2),
                     InsTmpl(f"mov_{bw}_mbis32_r",
                             [P.reg0, F.NO_INDEX, F.SCALE1, P.num1, P.tmp_gpr])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SIMM32, C.REG],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(f"mov_{bw}_mbis32_r",
                             [P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num1, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmplStkLd(o.DK.A64, P.scratch_gpr, P.spill2),
                     InsTmpl(f"mov_{bw}_mbis8_r",
                             [P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0, P.scratch_gpr])])
            # ST base_reg offset_reg src_reg
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.REG, C.REG],
                    ExtendRegTo64Bit(P.reg1, kind1) +
                    [InsTmpl(f"mov_{bw}_mbis8_r", [P.reg0, P.reg1, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.REG, C.REG],
                    ExtendRegTo64Bit(P.reg1, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(f"mov_{bw}_mbis8_r", [P.tmp_gpr, P.reg1, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill1, kind1) +
                    [InsTmpl(f"mov_{bw}_mbis8_r", [P.reg0, P.tmp_gpr, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind2) +
                    [InsTmpl(f"mov_{bw}_mbis8_r", [P.reg0, P.reg1, F.SCALE1, 0, P.tmp_gpr])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill1, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(f"mov_{bw}_mbis8_r", [P.tmp_gpr, P.scratch_gpr, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill2, kind2) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(f"mov_{bw}_r_mbis8", [P.tmp_gpr, P.reg1, P.tmp_gpr, F.SCALE1, 0])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill1, kind1) +
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind2) +
                    [InsTmpl(f"mov_64_mbis8_r", [P.reg0, P.scratch_gpr, F.SCALE1, 0, P.tmp_gpr])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill1, kind1) +
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind2) +
                    [InsTmpl(f"add_64_r_mbis32", [P.scratch_gpr, F.SP, F.NO_INDEX, F.SCALE1, P.spill0]),
                     InsTmpl(f"mov_{bw}_mbis8_r", [P.scratch_gpr, F.NO_INDEX, F.SCALE1, 0, P.tmp_gpr])])


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


InitAluInt()
InitAluFlt()
InitCondBraInt()
InitLea()
InitLoad()
InitStore()


def _DumpCodeSelTable():
    count = 0
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        count += len(patterns)
        opcode = o.Opcode.TableByNo[i]
        print(f"{opcode.name} [{' '.join([k.name for k in opcode.operand_kinds])}] patters={len(patterns)}")
        for pat in patterns:
            type_constraints = [x.name if x != o.DK.INVALID else '*' for x in pat.type_constraints]
            op_constraints = [x.name if x else '*' for x in pat.op_curbs]

            print(f"  [{' '.join(type_constraints)}]  [{' '.join(op_constraints)}]")
            for tmpl in pat.emit:
                ops = [str(x) if isinstance(x, int) else x.name for x in tmpl.args]
                print(f"    {tmpl.opcode.name} [{' '.join(ops)}]")
        print()
    print(f"Total patterns {count}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        assert False
        if sys.argv[1] == "documentation":
            pass
        elif sys.argv[1] == "gen_h":
            cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_c":
            cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)

    else:
        _DumpCodeSelTable()
