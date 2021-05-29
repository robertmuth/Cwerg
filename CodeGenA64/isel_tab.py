#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  ARMv6T2 and above

See `ARM32.md` for more details.
"""

import collections
from typing import List, Dict, Any, Set, Optional
import enum

from Base import ir
from Base import opcode_tab as o
from CodeGenA64 import regs
import CpuA64.opcode_tab as a64
from Elf import enum_tab
from Util import cgen


class SYMOP(enum.IntEnum):
    pass


@enum.unique
class IMM_KIND(enum.IntEnum):
    """Immediate Kind

    Helps determine if a pattern is a suitable match
    """
    INVALID = 0
    ZERO = 1
    SHIFTED_10_21_22 = 2
    IMM_10_15_16_22_W = 3
    IMM_10_15_16_22_X = 4
    IMM_SHIFTED_5_20_21_22 = 5
    ANY = 6


_NUM_MATCHERS: Dict[IMM_KIND, Any] = {
    IMM_KIND.ZERO: lambda x: x == 0,
    IMM_KIND.ANY: lambda x: True,
    IMM_KIND.IMM_SHIFTED_5_20_21_22: lambda x: a64.EncodeShifted_5_20_21_22(x) is not None,
    IMM_KIND.SHIFTED_10_21_22: lambda x: a64.EncodeShifted_10_21_22(x) is not None,
}

_IMM_KIND_STK: Set[IMM_KIND] = {}


def _InsAddNop1ForCodeSel(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    if opc is o.SWITCH:
        # needs scratch to compute the jmp address into
        scratch = fun.GetScratchReg(o.DK.C64, "switch", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    return [ins]


def FunAddNop1ForCodeSel(fun: ir.Fun):
    return ir.FunGenericRewrite(fun, _InsAddNop1ForCodeSel)


@enum.unique
class PARAM(enum.Enum):
    """Placeholder in A64 instruction template for stuff that needs to be derived
    for the Cwerg instructions"""
    invalid = 0
    reg0 = 1
    reg1 = 2
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
    num0_neg = 11
    num1_neg = 12
    num2_neg = 13
    num3_neg = 14
    num4_neg = 15
    #
    num0_not = 16
    num1_not = 17
    num2_not = 18
    #
    bbl0 = 19
    bbl2 = 20
    fun0 = 21
    scratch_gpr = 22
    scratch_flt = 23
    num2_rsb_width = 24
    num2_rsb_width_minus1 = 25
    mem1_num2_prel_hi21 = 26
    mem1_num2_lo12 = 27
    any = 28


_RELOC_ARGS: Set[PARAM] = {PARAM.bbl0, PARAM.bbl2, PARAM.fun0,
                           PARAM.mem1_num2_prel_hi21,
                           PARAM.mem1_num2_lo12,
                           }


def GetStackOffset(stk: ir.Stk, num: ir.Const) -> int:
    assert isinstance(num, ir.Const)
    assert isinstance(stk, ir.Stk)
    assert stk.slot is not None
    return stk.slot + num.value


def _ExtractTmplArgOp(ins: ir.Ins, arg: PARAM, ctx: regs.EmitContext) -> int:
    if isinstance(arg, a64.SHIFT):
        return arg.value
    elif arg in {PARAM.reg0, PARAM.reg1, PARAM.reg2, PARAM.reg3, PARAM.reg4}:
        n = arg.value - PARAM.reg0.value
        reg = ins.operands[n]
        assert isinstance(reg,
                          ir.Reg) and reg.HasCpuReg(), f"unexpected op {ins} {ins.operands} [{reg}]"
        return reg.cpu_reg.no
    elif arg in {PARAM.num0, PARAM.num1, PARAM.num2, PARAM.num3, PARAM.num4}:
        n = arg.value - PARAM.num0.value
        num = ins.operands[n]
        assert isinstance(num, ir.Const), f"expected {arg} got {num} in {ins} {ins.operands}"
        return num.value
    elif arg in {PARAM.num0_neg, PARAM.num1_neg, PARAM.num2_neg, PARAM.num3_neg, PARAM.num4_neg}:
        n = arg.value - PARAM.num0_neg.value
        num = ins.operands[n]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        return -num.value & ((1 << num.kind.bitwidth()) - 1)
    elif arg in {PARAM.num0_not, PARAM.num1_not, PARAM.num2_not}:
        n = arg.value - PARAM.num0_not.value
        num = ins.operands[n]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        return ~num.value & ((1 << num.kind.bitwidth()) - 1)
    elif arg in _RELOC_ARGS:
        return 0
    elif arg is PARAM.scratch_flt:
        assert False
        # assert ctx.scratch_cpu_reg.kind is not regs.A32RegKind.GPR
        # return ctx.scratch_cpu_reg.no
    elif arg is PARAM.scratch_gpr:
        assert False
        # assert ctx.scratch_cpu_reg.kind is regs.A32RegKind.GPR
        # return ctx.scratch_cpu_reg.no
    else:
        assert False, f"unknown ARG {repr(arg)}"


def _TranslateTmplOpInt(ins: ir.Ins, op: Any, ctx: regs.EmitContext) -> int:
    if type(op) == int:
        return op
    elif isinstance(op, PARAM):
        return _ExtractTmplArgOp(ins, op, ctx)
    elif isinstance(op, FIXARG):
        return op.value
    else:
        assert False, f"unknown param {repr(op)}"


def _HandleReloc(armins: a64.Ins, pos: int, ins: ir.Ins, op: PARAM):
    assert armins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.NONE, f"{armins.reloc_kind}"
    armins.reloc_pos = pos

    if op is PARAM.bbl0:
        armins.reloc_kind = enum_tab.RELOC_TYPE_AARCH64.CONDBR19
        armins.is_local_sym = True
        bbl = ins.operands[0]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        armins.reloc_symbol = bbl.name
    elif op is PARAM.bbl2:
        armins.reloc_kind = enum_tab.RELOC_TYPE_AARCH64.JUMP26
        armins.is_local_sym = True
        bbl = ins.operands[2]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        armins.reloc_symbol = bbl.name
    elif op is PARAM.fun0:
        armins.reloc_kind = enum_tab.RELOC_TYPE_AARCH64.CALL26
        fun = ins.operands[0]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        armins.reloc_symbol = fun.name
    elif op in {PARAM.mem1_num2_prel_hi21, PARAM.mem1_num2_lo12}:
        armins.reloc_kind = (enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC if op is PARAM.mem1_num2_lo12
                             else enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21)
        mem = ins.operands[1]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        armins.reloc_symbol = mem.name
        num = ins.operands[2]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert armins.operands[pos] == 0
        armins.operands[pos] = num.value
    else:
        assert False


class InsTmpl:
    """Represents a template for an A32 instructions

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.

    args: a list of registers/constants/placeholders
    """

    def __init__(self, opcode_name: str, args: List[Any]):
        opcode = a64.Opcode.name_to_opcode[opcode_name]
        for op in args:
            assert isinstance(op, (int, PARAM, FIXARG)), (
                f"unknown op {op} for {opcode.name} {args}")
        self.opcode = opcode
        self.args: List[Any] = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> a64.Ins:
        out = a64.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            val = _TranslateTmplOpInt(ins, arg, ctx)
            val = a64.EncodeOperand(self.opcode.fields[n], val)
            assert val is not None
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


def _HighByte(x):
    """This reflects what can be expressed as immediates by add_imm  and sub_imm"""
    shift = 0
    while x > 255:
        x >>= 2
        shift += 2
    return x << shift


# not this must have more bits set than MAX_OPERANDS
MATCH_IMPOSSIBLE = 255


class Pattern:
    """
    A pattern translates an IR instructions into zero or target instructions

    Whether a pattern matches the IR instructions is decides as follows:
    * the opcode must match
    * the operand types must match
    * operands that are constants must satisfy a "range constraint"
    """
    # groups all the patterns for a given opcode number together
    Table: Dict[int, List["Pattern"]] = collections.defaultdict(list)

    def __init__(self, opcode: o.Opcode, type_constraints: List[o.DK],
                 emit: List[InsTmpl],
                 imm_kind0=IMM_KIND.INVALID,
                 imm_kind1=IMM_KIND.INVALID,
                 imm_kind2=IMM_KIND.INVALID,
                 imm_kind3=IMM_KIND.INVALID,
                 imm_kind4=IMM_KIND.INVALID):
        # the template, usually contains ArmIns except for the nop1 pattern
        self.emit = emit
        # how to fill the template params
        assert len(type_constraints) == len(
            opcode.operand_kinds), f"{opcode.name} {type_constraints} {opcode.operand_kinds}"
        imm_constraints = [imm_kind0, imm_kind1, imm_kind2, imm_kind3, imm_kind4]
        imm_constraints = imm_constraints[:len(type_constraints)]
        self.type_constraints = type_constraints
        self.imm_constraints = imm_constraints
        for type_constr, imm_constr, kind in zip(type_constraints, imm_constraints,
                                                 opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr is IMM_KIND.INVALID
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr != IMM_KIND.INVALID
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert imm_constr is IMM_KIND.INVALID, f"bad pattern for {opcode}"

        # we put all the patterns for given IR opcode into the same bucket
        Pattern.Table[opcode.no].append(self)

    def MatchesTypeConstraints(self, ins: ir.Ins) -> bool:
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

    def MatchesImmConstraints(self, ins: ir.Ins) -> int:
        """Returns bit positions that have a mismatch

        assumes that MatchesTypeConstraints return true
        Possible return values:
        * 0: perfect match, pattern can be used directly for code generation
        * MATCH_IMPOSSBILE: pattern is not suitable
        * other: partial match, pattern can be used if the operands at the bit positions which are set
                would live in a register instead of being an immediate
        """
        out = 0
        for pos, (imm_constr, op) in enumerate(zip(self.imm_constraints, ins.operands)):
            if isinstance(op, ir.Const):
                if imm_constr is IMM_KIND.INVALID:
                    # have constant but need a reg (we know the op must be a reg because ow there would
                    #  not be a match at all
                    out |= 1 << pos
                    continue
                val = op.value
                if imm_constr in _IMM_KIND_STK:
                    stk = ins.operands[pos - 1]
                    if not isinstance(stk, ir.Stk):
                        return MATCH_IMPOSSIBLE
                    assert stk.slot is not None, f"unfinalized stack slot for {stk} in {ins}"
                    val += stk.slot
                if not _NUM_MATCHERS[imm_constr](val):
                    # have constant that does not fit
                    return MATCH_IMPOSSIBLE
            elif isinstance(op, ir.Reg):
                if imm_constr is not IMM_KIND.INVALID:
                    # have a reg but need a const
                    return MATCH_IMPOSSIBLE
        return out

    def __str__(self):
        return f"[PATTERN {self.type_constraints} {self.imm_constraints}]"

    def __repr__(self):
        return f"[PATTERN {self.type_constraints} {self.imm_constraints}]"


def EmitFunEpilog(ctx: regs.EmitContext) -> List[InsTmpl]:
    out = []
    stk_size = ctx.stk_size
    assert (stk_size >> 24) == 0
    if stk_size & 0xfff != 0:
        out.append(InsTmpl("sub_x_imm", [31, 31, a64.EncodeShifted_10_21_22(stk_size & 0xfff)]))
    if stk_size & 0xfff000 != 0:
        out.append(InsTmpl("sub_x_imm", [31, 31, a64.EncodeShifted_10_21_22(stk_size & 0xfff000)]))

    restores = []
    gpr_regs = regs.MaskToGpr64Regs(ctx.gpr64_reg_mask)
    while gpr_regs:
        r1 = gpr_regs.pop(-1)
        if not gpr_regs:
            restores.append(InsTmpl("ldr_x_imm_post", [r1.no, 31, 16]))
            break
        else:
            r2 = gpr_regs.pop(-1)
            restores.append(InsTmpl("ldp_x_imm_post", [r2.no, r1, 31, 16]))
    flt_regs = regs.MaskToFlt64Regs(ctx.flt64_reg_mask)
    while flt_regs:
        r1 = flt_regs.pop(-1)
        if not flt_regs:
            restores.append(InsTmpl("fldr_d_imm_post", [r1.no, 31, 16]))
            break
        else:
            r2 = flt_regs.pop(-1)
            restores.append(InsTmpl("fldp_d_imm_post", [r2.no, r1.no, 31, 16]))
    out += reversed(restores)

    # a9bf7bfd 	stp	x29, x30, [sp, #-16]!

    out.append(InsTmpl("ret", [30]))
    return out


def HandlePseudoNop1(ins: ir.Ins, ctx: regs.EmitContext):
    """This does not emit any code but copies the register assigned to the nop into the ctx

The idea is that the next instruction can use this register as a scratch. But this
only works if the next instruction was not assigned the register itself.
"""
    # assert ctx.scratch_reg is ir.REG_INVALID
    ctx.scratch_cpu_reg = ins.operands[0].cpu_reg
    return []


def EmitFunProlog(ctx: regs.EmitContext) -> List[InsTmpl]:
    out = []
    gpr_regs = regs.MaskToGpr64Regs(ctx.gpr64_reg_mask)
    while gpr_regs:
        r1 = gpr_regs.pop(-1)
        if not gpr_regs:
            out.append(InsTmpl("str_x_imm_pre", [31, -16, r1.no]))
            break
        else:
            r2 = gpr_regs.pop(-1)
            out.append(InsTmpl("stp_x_imm_pre", [31, -16, r2.no, r1.no]))
    flt_regs = regs.MaskToFlt64Regs(ctx.flt64_reg_mask)
    while flt_regs:
        r1 = flt_regs.pop(-1)
        if not flt_regs:
            out.append(InsTmpl("fstr_d_imm_pre", [31, -16, r1.no]))
            break
        else:
            r2 = flt_regs.pop(-1)
            out.append(InsTmpl("fstp_d_imm_pre", [31, -16, r2.no, r1.no]))

    stk_size = ctx.stk_size
    assert (stk_size >> 24) == 0
    if stk_size & 0xfff000 != 0:
        out.append(InsTmpl("add_x_imm", [31, 31, a64.EncodeShifted_10_21_22(stk_size & 0xfff000)]))
    if stk_size & 0xfff != 0:
        out.append(InsTmpl("add_x_imm", [31, 31, a64.EncodeShifted_10_21_22(stk_size & 0xfff)]))

    return out


OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.NOP1,  # pseudo instruction
    o.RET,  # handled via special epilog code
}

_CMP_SIGNED = {o.BLT: "b_lt", o.BLE: "b_le"}
_CMP_UNSIGNED = {o.BLT: "b_cc", o.BLE: "b_ls"}
_CMP_SIGNED_INV = {o.BLT: "b_gt", o.BLE: "b_ge"}
_CMP_UNSIGNED_INV = {o.BLT: "b_hi", o.BLE: "b_cs"}


class FIXARG(enum.Enum):
    WZR = 31
    XZR = 31
    X8 = 8
    SP = 31
    LSL = 0
    UXTW = 0
    SXTW = 1


def InitCondBra():
    # TODO: cover the floating points ones
    for kind in [o.DK.U32, o.DK.S32]:
        for opc, a64_opc in [(o.BEQ, "b_eq"), (o.BNE, "b_ne")]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_w_reg", [FIXARG.WZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(a64_opc, [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(a64_opc, [PARAM.bbl2])],
                    imm_kind1=IMM_KIND.SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for opc, a64_opc in [(o.BEQ, "b_eq"), (o.BNE, "b_ne")]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(a64_opc, [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(a64_opc, [PARAM.bbl2])],
                    imm_kind1=IMM_KIND.SHIFTED_10_21_22)

    for kind in [o.DK.U32, o.DK.S32]:
        xlate = _CMP_SIGNED if kind == o.DK.S32 else _CMP_UNSIGNED
        xlate_inv = _CMP_SIGNED_INV if kind == o.DK.S32 else _CMP_UNSIGNED_INV

        for opc in [o.BLT, o.BLE]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_w_reg", [FIXARG.WZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])],
                    imm_kind1=IMM_KIND.SHIFTED_10_21_22)
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.reg1, PARAM.num0]),
                     InsTmpl(xlate_inv[opc], [PARAM.bbl2])],
                    imm_kind0=IMM_KIND.SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.A64, o.DK.C64, o.DK.S64]:
        xlate = _CMP_SIGNED if kind == o.DK.S32 else _CMP_UNSIGNED
        xlate_inv = _CMP_SIGNED_INV if kind == o.DK.S32 else _CMP_UNSIGNED_INV

        for opc in [o.BLT, o.BLE]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_x_reg", [FIXARG.XZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])],
                    imm_kind1=IMM_KIND.SHIFTED_10_21_22)
            Pattern(opc, type_constraints,
                    [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.reg1, PARAM.num0]),
                     InsTmpl(xlate_inv[opc], [PARAM.bbl2])],
                    imm_kind0=IMM_KIND.SHIFTED_10_21_22)

    # * we do not have a story for the unordered case
    # * comparison against zero should be special cased
    for kind, a64_cmp in [(o.DK.F32, "fcmpe_s"), (o.DK.F64, "fcmpe_d")]:
        for opc, a64_bxx in [(o.BEQ, "b_eq"), (o.BNE, "b_ne"),
                             (o.BLT, "b_mi"), (o.BLE, "b_ls")]:
            Pattern(opc, [kind, kind, o.DK.INVALID],
                    [InsTmpl(a64_cmp, [PARAM.reg0, PARAM.reg1]),
                     InsTmpl(a64_bxx, [PARAM.bbl2])])


def InitCmp():
    # TODO: cover the floating points ones
    for kind in [o.DK.U32, o.DK.S32]:
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_w_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                 InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                 InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind4=IMM_KIND.SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_x_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                 InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                 InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind4=IMM_KIND.SHIFTED_10_21_22)

    for kind, csel, inv_csel in [
        (o.DK.U32, "csel_w_cc", "csel_w_cs"),
        (o.DK.S32, "csel_w_lt", "csel_w_ge")]:
        Pattern(o.CMPLT, [kind] * 5,
                [InsTmpl("sub_w_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                 InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                 InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind4=IMM_KIND.SHIFTED_10_21_22)
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_w_imm", [FIXARG.WZR, PARAM.num3, PARAM.reg4]),
                 InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind3=IMM_KIND.SHIFTED_10_21_22)

    for kind, csel, inv_csel in [
        (o.DK.U64, "csel_x_cc", "csel_x_cs"),
        (o.DK.A64, "csel_x_cc", "csel_x_cs"),  # should this be signed?
        (o.DK.S64, "csel_x_lt", "csel_x_ge")]:
        Pattern(o.CMPLT, [kind] * 5,
                [InsTmpl("sub_x_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                 InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                 InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind4=IMM_KIND.SHIFTED_10_21_22)
        Pattern(o.CMPEQ, [kind] * 5,
                [InsTmpl("sub_x_imm", [FIXARG.XZR, PARAM.num3, PARAM.reg4]),
                 InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                imm_kind3=IMM_KIND.SHIFTED_10_21_22)


def InitAlu():
    for kind1 in [o.DK.U32, o.DK.S32]:
        for opc, a64_opc in [(o.AND, "and_w_reg"),
                             (o.XOR, "eor_w_reg"),
                             (o.ADD, "add_w_reg"),
                             (o.OR, "orr_w_reg"),
                             (o.SUB, "sub_w_reg")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc,
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, a64.SHIFT.lsl, 0])])

        for opc, a64_opc in [(o.AND, "and_w_imm"), (o.XOR, "eor_w_imm"),
                             (o.OR, "orr_w_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_kind2=IMM_KIND.IMM_10_15_16_22_W)
        for opc, a64_opc in [(o.SUB, "sub_w_imm"), (o.ADD, "add_w_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_kind2=IMM_KIND.SHIFTED_10_21_22)
        Pattern(o.SUB, [kind1] * 3,
                [InsTmpl("sub_w_reg", [PARAM.reg0, FIXARG.WZR, PARAM.reg2])],
                imm_kind1=IMM_KIND.ZERO)

    for kind1 in [o.DK.U64, o.DK.S64]:
        for opc, a64_opc in [(o.AND, "and_x_reg"),
                             (o.XOR, "eor_x_reg"),
                             (o.ADD, "add_x_reg"),
                             (o.OR, "orr_x_reg"),
                             (o.SUB, "sub_x_reg")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc,
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, a64.SHIFT.lsl, 0])])

        for opc, a64_opc in [(o.AND, "and_x_imm"), (o.XOR, "eor_x_imm"),
                             (o.OR, "orr_x_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_kind2=IMM_KIND.IMM_10_15_16_22_W)
        for opc, a64_opc in [(o.SUB, "sub_x_imm"), (o.ADD, "add_x_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_kind2=IMM_KIND.SHIFTED_10_21_22)
        Pattern(o.SUB, [kind1] * 3,
                [InsTmpl("sub_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg2])],
                imm_kind1=IMM_KIND.ZERO)

    for kind1 in [o.DK.U32, o.DK.S32]:
        Pattern(o.MUL, [kind1] * 3,
                [InsTmpl("madd_w", [PARAM.reg0, PARAM.reg1, PARAM.reg2, FIXARG.WZR])])
    for kind1 in [o.DK.U64, o.DK.S64]:
        Pattern(o.MUL, [kind1] * 3,
                [InsTmpl("madd_x", [PARAM.reg0, PARAM.reg1, PARAM.reg2, FIXARG.WZR])])

    for kind1, a64_opc in [(o.DK.U32, "udiv_w"), (o.DK.S32, "sdiv_w"),
                           (o.DK.U64, "udiv_x"), (o.DK.S64, "sdiv_x")]:
        Pattern(o.DIV, [kind1] * 3,
                [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for opc, kind1, a64_opc in [(o.SHL, o.DK.U32, "lslv_w"),
                                (o.SHL, o.DK.S32, "lslv_w"),
                                (o.SHR, o.DK.U32, "lsrv_w"),
                                (o.SHR, o.DK.S32, "asrv_w"),
                                (o.SHL, o.DK.U64, "lslv_x"),
                                (o.SHL, o.DK.S64, "lslv_x"),
                                (o.SHR, o.DK.U64, "lsrv_x"),
                                (o.SHR, o.DK.S64, "asrv_x")]:
        Pattern(opc, [kind1] * 3,
                [InsTmpl(a64_opc,
                         [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for opc, kind1, a64_opc, n in [(o.SHR, o.DK.U32, "ubfm_w", 31),
                                   (o.SHR, o.DK.S32, "sbfm_w", 31),
                                   (o.SHR, o.DK.U64, "ubfm_x", 63),
                                   (o.SHR, o.DK.S64, "sbfm_x", 63)]:
        Pattern(opc, [kind1] * 3,
                [InsTmpl(a64_opc,
                         [PARAM.reg0, PARAM.reg1, PARAM.num2, n])],
                imm_kind2=IMM_KIND.ANY)  # pick better constraint

    for kind1, a64_opc in [(o.DK.U32, "ubfm_w"),
                           (o.DK.S32, "ubfm_w"),
                           (o.DK.U64, "ubfm_x"),
                           (o.DK.S64, "ubfm_x")]:
        Pattern(o.SHL, [kind1] * 3,
                [InsTmpl(a64_opc,
                         [PARAM.reg0, PARAM.reg1, PARAM.num2_rsb_width,
                          PARAM.num2_rsb_width_minus1])],
                imm_kind2=IMM_KIND.ANY)  # pick better constraint


def InitLoad():
    for kind1, opc in [(o.DK.U64, "ldr_x"), (o.DK.S64, "ldr_x"),
                       (o.DK.A64, "ldr_x"), (o.DK.C64, "ldr_x"),
                       (o.DK.U32, "ldr_w"), (o.DK.S32, "ldrsw"),
                       (o.DK.U16, "ldr_h"), (o.DK.S16, "ldrsh_x"),
                       (o.DK.U8, "ldr_b"), (o.DK.S8, "ldrsb_x")]:
        for kind2 in [o.DK.S64, o.DK.U64]:
            Pattern(o.LD, [kind1, o.DK.A64, kind2],
                    [InsTmpl(opc + "_reg_x",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, FIXARG.LSL,
                              0])])
        for shift, kind2 in [(FIXARG.SXTW, o.DK.S32), (FIXARG.UXTW, o.DK.U32)]:
            Pattern(o.LD, [kind1, o.DK.A64, kind2],
                    [InsTmpl(opc + "_reg_w",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, shift, 0])])

        # TODO: add immediate flavors


def InitStore():
    for kind1, opc in [(o.DK.U64, "str_x"), (o.DK.S64, "str_x"),
                       (o.DK.A64, "str_x"), (o.DK.C64, "str_x"),
                       (o.DK.U32, "str_w"), (o.DK.S32, "str_w"),
                       (o.DK.U16, "str_h"), (o.DK.S16, "str_h"),
                       (o.DK.U8, "str_b"), (o.DK.S8, "str_b")]:
        for offset_kind in [o.DK.S64, o.DK.U64]:
            Pattern(o.ST, [o.DK.A64, offset_kind, kind1],
                    [InsTmpl(opc + "_reg_x",
                             [PARAM.reg0, PARAM.reg1, FIXARG.LSL,
                              0, PARAM.reg2])])
        for shift, offset_kind in [(FIXARG.SXTW, o.DK.S32), (FIXARG.UXTW, o.DK.U32)]:
            Pattern(o.ST, [o.DK.A64, offset_kind, kind1],
                    [InsTmpl(opc + "_reg_w",
                             [PARAM.reg0, PARAM.reg1, shift, 0, PARAM.reg2])])

        # TODO: add immediate flavors


def InitLea():
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        Pattern(o.LEA_MEM, [o.DK.A64, o.DK.INVALID, kind1],
                [InsTmpl("adrp", [PARAM.reg0, PARAM.mem1_num2_prel_hi21]),
                 InsTmpl("add_x_imm", [PARAM.reg0, PARAM.reg0, PARAM.mem1_num2_lo12])],
                imm_kind2=IMM_KIND.ANY)

    for kind1 in [o.DK.U64, o.DK.S64]:
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [InsTmpl("add_x_reg",
                         [PARAM.reg0, PARAM.reg1, PARAM.reg2, FIXARG.LSL, 0])])
    for offset_kind, opc in [(o.DK.U32, "add_x_reg_uxtw"), (o.DK.S32, "add_x_reg_sxtw")]:
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, offset_kind],
                [InsTmpl(opc, [PARAM.reg0, PARAM.reg1, PARAM.reg2, 0])])

    return
    Pattern(o.LEA_FUN, [o.DK.C64, o.DK.INVALID], _NO_IMM2,
            [InsTmpl("movw", [PARAM.reg0, PARAM.fun1_lo16]),
             InsTmpl("movt", [PARAM.reg0, PARAM.fun1_hi16])])

    for kind1 in [o.DK.U32, o.DK.S32]:
        Pattern(o.LEA, [o.DK.A32, o.DK.A64, kind1], _NO_IMM3,
                [InsTmpl("add_regimm",
                         [PARAM.reg0, PARAM.reg1, PARAM.reg2, a64.SHIFT.lsl, 0])])
        Pattern(o.LEA, [o.DK.A32, o.DK.A32, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted],
                [InsTmpl("add_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2])])

        Pattern(o.LEA, [o.DK.A32, o.DK.A32, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.neg_8_bits_shifted],
                [InsTmpl("sub_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2_neg])])

        # note: the second and third op are combined in the generated code
        Pattern(o.LEA_MEM, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.any_32_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.mem1_num2_lo16]),
                 InsTmpl("movt", [PARAM.reg0, PARAM.mem1_num2_hi16])])

        # Note, lea_stks are our last resort and MUST support ALL possible immediates
        # note: the second and third op are combined in the generated code
        Pattern(o.LEA_STK, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_8_bits_shifted],
                [InsTmpl("add_imm", [PARAM.reg0, a64.REG.sp, PARAM.stk1_offset2])])
        Pattern(o.LEA_STK, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_16_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.stk1_offset2]),
                 InsTmpl("add_regimm", [PARAM.reg0, a64.REG.sp, PARAM.reg0, a64.SHIFT.lsl, 0])])
        Pattern(o.LEA_STK, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.any_32_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.stk1_offset2_lo]),
                 InsTmpl("movt", [PARAM.reg0, PARAM.stk1_offset2_hi]),
                 InsTmpl("add_regimm", [PARAM.reg0, a64.REG.sp, PARAM.reg0, a64.SHIFT.lsl, 0])])


def InsTmplMove(dst, src, kind):
    return
    assert dst is PARAM.reg0
    if src in {PARAM.reg1, PARAM.reg2, PARAM.reg3, PARAM.reg4}:
        return InsTmpl("mov_regimm", [dst, src, a64.SHIFT.lsl, 0], pred)

    assert src in {PARAM.num1, PARAM.num2, PARAM.num3, PARAM.num4, PARAM.num1_not}
    if kind is IMM_KIND.pos_16_bits:
        return InsTmpl("movw", [dst, src], pred)
    elif kind is IMM_KIND.pos_8_bits_shifted:
        return InsTmpl("mov_imm", [dst, src], pred)
    elif kind is IMM_KIND.not_8_bits_shifted:
        return InsTmpl("mvn_imm", [dst, src], pred)
    else:
        assert False, f"unsupported mov combination {kind.name}"


# Note, moves are our last resort and MUST support ALL possible immediates
def InitMove():
    for kind1 in [o.DK.A64, o.DK.C64, o.DK.U64,  #
                  o.DK.S64, o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.num1])],
                imm_kind1=IMM_KIND.IMM_SHIFTED_5_20_21_22)
    return
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for num, src_kind in [(PARAM.num1, IMM_KIND.pos_8_bits_shifted),
                              (PARAM.num1_not, IMM_KIND.not_8_bits_shifted),
                              (PARAM.num1, IMM_KIND.pos_16_bits)]:
            Pattern(o.MOV, [kind1] * 2, [IMM_KIND.invalid, src_kind],
                    [InsTmplMove(PARAM.reg0, num, src_kind)])
        Pattern(o.MOV, [kind1] * 2, _NO_IMM2,
                [InsTmplMove(PARAM.reg0, PARAM.reg1, kind1)])
        Pattern(o.MOV, [kind1] * 2, [IMM_KIND.invalid, IMM_KIND.any_32_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.num1_lo16]),
                 InsTmpl("movt", [PARAM.reg0, PARAM.num1_hi16])])


def InitConv():
    # truncation to operand of smaller bit width: nothing to be done here
    for kind1 in [o.DK.U64, o.DK.S64, o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U64, o.DK.S64]:
            Pattern(o.CONV, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.CONV, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])
    for kind1 in [o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U16, o.DK.S16]:
            Pattern(o.CONV, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])

    # bitcast between equal bit  width ops: nothing to be done here
    for kind1 in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for kind2 in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
            Pattern(o.BITCAST, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])
    for kind1 in [o.DK.U32, o.DK.S32]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.BITCAST, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])

    # sign change from 8it: nothing to be done here
    # TODO: explain when this happens - why only got 8bit?
    for kind1 in [o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U8, o.DK.S8]:
            Pattern(o.CONV, [kind1, kind2],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])

    for kind in [o.DK.U64, o.DK.U32]:
        Pattern(o.CONV, [kind, o.DK.U8],
                [InsTmpl("and_x_imm", [PARAM.reg0, PARAM.reg1, 0xff])])
        Pattern(o.CONV, [kind, o.DK.U16],
                [InsTmpl("and_x_imm", [PARAM.reg0, PARAM.reg1, 0xffff])])

    for kind in [o.DK.S64, o.DK.S32]:
        Pattern(o.CONV, [kind, o.DK.S8],
                [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 7])])

        Pattern(o.CONV, [kind, o.DK.S16],
                [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 15])])


    Pattern(o.CONV, [o.DK.U64, o.DK.U32],
            [InsTmpl("orr_w_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, FIXARG.LSL, 0])])

    Pattern(o.CONV, [o.DK.S64, o.DK.S32],
            [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 31])])


def InitMiscBra():
    Pattern(o.BRA, [o.DK.INVALID],
            [InsTmpl("b", [PARAM.bbl0])])

    Pattern(o.BSR, [o.DK.INVALID],
            [InsTmpl("bl", [PARAM.fun0])])

    Pattern(o.JSR, [o.DK.C64, o.DK.INVALID],
            [InsTmpl("blr", [PARAM.reg0])])

    Pattern(o.TRAP, [], [InsTmpl("brk", [0])])

    Pattern(o.SYSCALL, [o.DK.INVALID, o.DK.U32],
            [InsTmpl("movz_x_imm", [FIXARG.X8, PARAM.num1]),
             InsTmpl("svc", [0])],
            imm_kind1=IMM_KIND.IMM_SHIFTED_5_20_21_22)

    # Note: a dummy "nop1 %scratch_gpr" either immediately before
    # or after will ensure that %scratch_gpr is available
    # Pattern(o.SWITCH, [o.DK.U32, o.DK.INVALID],
    #         [InsTmpl("movw", [PARAM.scratch_gpr, PARAM.jtb1_lo16]),
    #          InsTmpl("movt", [PARAM.scratch_gpr, PARAM.jtb1_hi16]),
    #          InsTmpl("ldr_reg_add",
    #                  [a64.REG.pc, PARAM.scratch_gpr, PARAM.reg0, a64.SHIFT.lsl,
    #                   2]),
    #          ])


def InitVFP():
    for kind, suffix in [(o.DK.F32, "_s"), (o.DK.F64, "_d")]:
        Pattern(o.MOV, [kind] * 2,
                [InsTmpl("fmov" + suffix + "_reg", [PARAM.reg0, PARAM.reg1])])
        Pattern(o.ADD, [kind] * 3,
                [InsTmpl("fadd" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.SUB, [kind] * 3,
                [InsTmpl("fsub" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.MUL, [kind] * 3,
                [InsTmpl("fmul" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.DIV, [kind] * 3,
                [InsTmpl("fdiv" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for kind_dst, kind_src, a64_opc in [(o.DK.F64, o.DK.S32, "scvtf_d_from_w"),
                                        (o.DK.F64, o.DK.U32, "ucvtf_d_from_w"),
                                        (o.DK.F32, o.DK.S32, "scvtf_s_from_w"),
                                        (o.DK.F32, o.DK.U32, "ucvtf_s_from_w"),
                                        (o.DK.F64, o.DK.S64, "scvtf_d_from_x"),
                                        (o.DK.F64, o.DK.U64, "ucvtf_d_from_x"),
                                        (o.DK.F32, o.DK.S64, "scvtf_s_from_x"),
                                        (o.DK.F32, o.DK.U64, "ucvtf_s_from_x"),
                                        (o.DK.S32, o.DK.F32, "fcvtzs_w_s"),
                                        (o.DK.S32, o.DK.F64, "fcvtzs_w_d"),
                                        (o.DK.U32, o.DK.F32, "fcvtzu_w_s"),
                                        (o.DK.U32, o.DK.F64, "fcvtzu_w_d"),
                                        (o.DK.S64, o.DK.F32, "fcvtzs_x_s"),
                                        (o.DK.S64, o.DK.F64, "fcvtzs_x_d"),
                                        (o.DK.U64, o.DK.F32, "fcvtzu_x_s"),
                                        (o.DK.U64, o.DK.F64, "fcvtzu_x_d"),
                                        ]:
        Pattern(o.CONV, [kind_dst, kind_src],
                [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1])])


InitLoad()
InitStore()
InitAlu()
InitLea()
InitMove()
InitCondBra()
InitCmp()
InitMiscBra()
InitConv()
InitVFP()


def FindMatchingPattern(ins: ir.Ins) -> Optional[Pattern]:
    """Returns the best pattern matching `ins` or None"""
    patterns = Pattern.Table[ins.opcode.no]
    # print(f"@ {ins} {ins.operands}")
    for p in patterns:
        # print(f"@trying pattern {p}")
        if p.MatchesTypeConstraints(ins) and 0 == p.MatchesImmConstraints(ins):
            return p
    else:
        # assert False, f"Could not find a matching patterns for {ins}. tried:\n{patterns}"
        return None


def FindtImmediateMismatchesInBestMatchPattern(ins: ir.Ins) -> int:
    """Returns a list of operand positions that need to be rewritten

    None means there was an error
    """
    best = MATCH_IMPOSSIBLE
    best_num_bits = bin(best).count('1')
    patterns = Pattern.Table[ins.opcode.no]
    for p in patterns:
        if not p.MatchesTypeConstraints(ins):
            continue
        mismatches = p.MatchesImmConstraints(ins)
        num_bits = bin(mismatches).count('1')
        if num_bits < best_num_bits:
            best, best_num_bits = mismatches, num_bits
    return best


def _EmitCodeH(fout):
    for cls in [IMM_KIND, PARAM]:
        cgen.RenderEnum(cgen.NameValues(cls), f"class {cls.__name__} : uint8_t", fout)


def _RenderOperands(operands: List[Any]):
    out = []
    mask = 0
    for n, op in enumerate(operands):
        if isinstance(op, PARAM):
            mask |= 1 << n
            s = f"+PARAM::{op.name}"
        elif isinstance(op, a64.REG):
            s = f"+REG::{op.name}"
        elif isinstance(op, a64.SHIFT):
            s = f"+SHIFT::{op.name}"
        elif isinstance(op, int):
            s = f"{op}"
        else:
            assert False, f"bad op {op}"
        out.append(s)
    return mask, out


def _EmitCodeC(fout):
    print(f"\nconst InsTmpl kInsTemplates[] = {{", file=fout)
    print("  { /*used first entry*/ },", file=fout)
    num_ins = 1
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        opcode = o.Opcode.TableByNo.get(i)
        for pat in patterns:
            for tmpl in pat.emit:
                mask, ops = _RenderOperands(tmpl.args)
                num_ins += 1
                print(f"  {{ {{{', '.join(ops)}}},", file=fout)
                print(
                    f"    a32::OPC::{tmpl.opcode.name}, 0x{mask:x} }},  // {opcode.name} [{num_ins}]",
                    file=fout)
    print(f"}};", file=fout)

    print(f"\nconst uint16_t kPatternJumper[256] = {{")
    n = 0
    for i in range(256):
        opcode = o.Opcode.TableByNo.get(i)
        name = opcode.name if opcode else "---"
        print(f" {n} /* {name} */, ", end="", file=fout)
        n += len(Pattern.Table.get(i, []))
        if i % 4 == 3:
            print("", file=fout)
    print(f"}};", file=fout)

    print(f"\nconst Pattern kPatterns[] = {{", file=fout)
    num_ins = 1  # we want the first entry in the  kInsTemplate to be unused
    num_pattern = 0
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        opcode = o.Opcode.TableByNo.get(i)
        for pat in patterns:
            reg_constraints = [f"DK::{c.name}" for c in pat.type_constraints]
            imm_constraints = [f"IK::{c.name}" for c in pat.imm_constraints]
            print(f"  {{ {{{', '.join(reg_constraints)}}},")
            print(f"    {{{', '.join(imm_constraints)}}},")
            print(
                f"    &kInsTemplates[{num_ins}], {len(pat.emit)} }},  // {opcode.name} [{num_pattern}]")
            num_ins += len(pat.emit)
            num_pattern += 1
    print(f"}};", file=fout)

    print("}  // namespace", file=fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(IMM_KIND), "IMM_KIND", fout)
    cgen.RenderEnumToStringFun("IMM_KIND", fout)


def _DumpCodeSelTable():
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        opcode = o.Opcode.TableByNo[i]
        print(f"{opcode.name} [{' '.join([k.name for k in opcode.operand_kinds])}]")
        for pat in patterns:
            type_constraints = [x.name if x != o.DK.INVALID else '*' for x in pat.type_constraints]
            imm_constraints = [x.name if x else '*' for x in pat.imm_constraints]

            print(f"  [{' '.join(type_constraints)}]  [{' '.join(imm_constraints)}]")
            for tmpl in pat.emit:
                ops = [str(x) if isinstance(x, int) else x.name for x in tmpl.args]
                print(f"    {tmpl.opcode.name} [{' '.join(ops)}]")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "documentation":
            pass
        elif sys.argv[1] == "gen_h":
            cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_c":
            cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)

    else:
        _DumpCodeSelTable()
