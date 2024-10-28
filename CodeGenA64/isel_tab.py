#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  ARMv6T2 and above

See `ARM32.md` for more details.
"""

import collections
import enum
from typing import List, Dict, Any, Set, Optional

from Base import ir
from Base import opcode_tab as o
from CodeGenA64 import regs
from CpuA64 import opcode_tab as a64
from BE.Elf import enum_tab
from Util import cgen


@enum.unique
class IMM_CURB(enum.IntEnum):
    """Immediate Curbs - describes constraints on the immediate values involved in patterns

    Used to determine if a pattern is a suitable match for a Cwerg IR instruction
    """
    INVALID = 0
    ZERO = 1
    ANY = 2
    IMM_SHIFTED_10_21_22 = 3
    IMM_10_15_16_22_W = 4
    IMM_10_15_16_22_X = 5
    IMM_SHIFTED_5_20_21_22 = 6
    IMM_SHIFTED_5_20_21_22_NOT = 7
    # also update _IMM_KIND_STK if new stk immediates are added
    pos_stk_combo_shifted_10_21_22 = 8
    pos_stk_combo_16_bits = 9
    pos_stk_combo_32_bits = 10
    pos_stk_combo_10_21 = 11
    pos_stk_combo_10_21_times_2 = 12
    pos_stk_combo_10_21_times_4 = 13
    pos_stk_combo_10_21_times_8 = 14
    IMM_POS_32 = 15


_NUM_MATCHERS: Dict[IMM_CURB, Any] = {
    # return False on non-match
    IMM_CURB.ZERO: lambda x: x == 0,
    IMM_CURB.ANY: lambda x: True,
    IMM_CURB.pos_stk_combo_16_bits: lambda x: 0 <= x < (1 << 16),
    IMM_CURB.pos_stk_combo_32_bits: lambda x: 0 <= x < (1 << 32),
    IMM_CURB.IMM_SHIFTED_5_20_21_22_NOT: lambda x: a64.EncodeShifted_5_20_21_22(~x) is not None,
    # The curbs below map directly to an a64.OK. return None on non-match
    IMM_CURB.IMM_SHIFTED_5_20_21_22: a64.OK.IMM_SHIFTED_5_20_21_22,
    IMM_CURB.IMM_SHIFTED_10_21_22: a64.OK.IMM_SHIFTED_10_21_22,
    IMM_CURB.pos_stk_combo_shifted_10_21_22: a64.OK.IMM_SHIFTED_10_21_22,
    IMM_CURB.pos_stk_combo_10_21: a64.OK.IMM_10_21,
    IMM_CURB.pos_stk_combo_10_21_times_2: a64.OK.IMM_10_21_TIMES_2,
    IMM_CURB.pos_stk_combo_10_21_times_4: a64.OK.IMM_10_21_TIMES_4,
    IMM_CURB.pos_stk_combo_10_21_times_8: a64.OK.IMM_10_21_TIMES_8,
    IMM_CURB.IMM_10_15_16_22_W: a64.OK.IMM_10_15_16_22_W,
    IMM_CURB.IMM_10_15_16_22_X: a64.OK.IMM_10_15_16_22_X,
    IMM_CURB.IMM_POS_32: lambda x: 0 <= x < (1 << 32),
}


def ValueMatchesCurbs(constraint: IMM_CURB, val: int) -> bool:
    m = _NUM_MATCHERS[constraint]
    if isinstance(m, a64.OK):
        return a64.TryEncodeOperand(m, val) is not None
    else:
        assert callable(m)
        return m(val)


_IMM_KIND_STK: Set[IMM_CURB] = {
    IMM_CURB.pos_stk_combo_shifted_10_21_22,
    IMM_CURB.pos_stk_combo_16_bits,
    IMM_CURB.pos_stk_combo_32_bits,
    IMM_CURB.pos_stk_combo_32_bits,
    IMM_CURB.pos_stk_combo_10_21,
    IMM_CURB.pos_stk_combo_10_21_times_2,
    IMM_CURB.pos_stk_combo_10_21_times_4,
    IMM_CURB.pos_stk_combo_10_21_times_8,
}


def _InsAddNop1ForCodeSel(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    if opc is o.CNTPOP:
        scratch = fun.GetScratchReg(o.DK.F64, "popcnt", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    return [ins]


def FunAddNop1ForCodeSel(fun: ir.Fun):
    """Add dummy instruction to ensure we have a scratch register for the next instruction
    """
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
    # The value is computed by combining the Mem operand with the constant offset operand
    mem1_num2_prel_hi21 = 26
    mem1_num2_lo12 = 27
    # The value is computed by combining the STK operand with the constant offset operand
    stk1_offset2 = 28
    stk1_offset2_lo = 29
    stk1_offset2_hi = 30
    stk0_offset1 = 31
    stk0_offset1_lo = 32
    stk0_offset1_hi = 33
    #
    fun1_prel_hi21 = 34
    fun1_lo12 = 35
    #
    jtb1_prel_hi21 = 36
    jtb1_lo12 = 37
    num1_0_16 = 38
    num1_16_32 = 39
    num1_32_48 = 40
    num1_48_64 = 41
    frame_size = 42


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
        assert isinstance(
            reg, ir.Reg), f"expected reg: {reg} in {ins} {ins.operands}"
        assert reg.HasCpuReg(
        ), f"expected cpu reg: {reg} in {ins} {ins.operands}"
        return reg.cpu_reg.no
    elif arg in {PARAM.num0, PARAM.num1, PARAM.num2, PARAM.num3, PARAM.num4}:
        n = arg.value - PARAM.num0.value
        num = ins.operands[n]
        assert isinstance(
            num, ir.Const), f"expected {arg} got {num} in {ins} {ins.operands}"
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
    elif arg in {PARAM.num1_0_16, PARAM.num1_16_32, PARAM.num1_32_48, PARAM.num1_48_64}:
        shift = ((arg.value - PARAM.num1_0_16.value) * 16)
        return (ins.operands[1].value >> shift) & 0xffff
    elif arg is PARAM.scratch_flt:
        assert ctx.scratch_cpu_reg.kind == regs.CpuRegKind.FLT, f"{ctx.scratch_cpu_reg}"
        return ctx.scratch_cpu_reg.no
    elif arg is PARAM.scratch_gpr:
        # This is a reserved reg and hence always available
        return regs.GPR_HELPER_REG.no
    elif arg in {PARAM.stk1_offset2, PARAM.stk1_offset2_hi, PARAM.stk1_offset2_lo}:
        return GetStackOffset(ins.operands[1], ins.operands[2])
    elif arg in {PARAM.stk0_offset1, PARAM.stk0_offset1_hi, PARAM.stk0_offset1_lo}:
        return GetStackOffset(ins.operands[0], ins.operands[1])
    elif arg is PARAM.num2_rsb_width:
        num = ins.operands[2]
        width = num.kind.bitwidth()
        assert 1 <= num.value <= width
        return width - num.value
    elif arg is PARAM.num2_rsb_width_minus1:
        num = ins.operands[2]
        width = num.kind.bitwidth()
        assert 1 <= num.value <= width
        return width - num.value - 1
    elif arg in _OP_TO_RELOC_KIND:
        return 0
    elif arg is PARAM.frame_size:
        return ctx.FrameSize()
    else:
        assert False, f"unknown ARG {repr(arg)}"


_OP_TO_RELOC_KIND = {
    PARAM.bbl0: enum_tab.RELOC_TYPE_AARCH64.JUMP26,
    PARAM.bbl2: enum_tab.RELOC_TYPE_AARCH64.CONDBR19,
    PARAM.fun0: enum_tab.RELOC_TYPE_AARCH64.CALL26,
    PARAM.mem1_num2_prel_hi21: enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21,
    PARAM.mem1_num2_lo12: enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC,
    PARAM.fun1_prel_hi21: enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21,
    PARAM.fun1_lo12: enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC,
    PARAM.jtb1_prel_hi21: enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21,
    PARAM.jtb1_lo12: enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC,
}


def _HandleReloc(cpuins: a64.Ins, pos: int, ins: ir.Ins, op: PARAM):
    assert not cpuins.has_reloc(), f"{cpuins.reloc_kind}"

    if op is PARAM.bbl0:
        bbl = ins.operands[0]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is PARAM.bbl2:
        bbl = ins.operands[2]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op is PARAM.fun0:
        fun = ins.operands[0]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        assert fun.kind is not o.FUN_KIND.EXTERN, f"undefined fun: {fun.name}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op in {PARAM.mem1_num2_prel_hi21, PARAM.mem1_num2_lo12}:
        mem = ins.operands[1]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        assert mem.kind is not o.MEM_KIND.EXTERN, f"undefined fun: {mem.name}"
        num = ins.operands[2]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert cpuins.operands[pos] == 0
        cpuins.operands[pos] = num.value
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, mem.name)
    elif op in {PARAM.fun1_prel_hi21, PARAM.fun1_lo12}:
        fun = ins.operands[1]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        assert fun.kind is not o.FUN_KIND.EXTERN, f"undefined fun: {fun.name}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op in {PARAM.jtb1_prel_hi21, PARAM.jtb1_lo12}:
        jtb = ins.operands[1]
        assert isinstance(jtb, ir.Jtb), f"{ins} {jtb}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, jtb.name)
    else:
        assert False


class InsTmpl:
    """Represents a template for an A32 instruction

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.

    args: a list of registers/constants/placeholders all values must be run through EncodeOperand
    """

    def __init__(self, opcode_name: str, args: List[Any]):
        opcode: a64.Opcode = a64.Opcode.name_to_opcode[opcode_name]
        assert len(args) == len(
            opcode.fields), f"num arg mismatch for {opcode_name} {args} vs {opcode.fields}"
        for op in args:
            assert isinstance(op, (int, PARAM, FIXARG)), (
                f"unknown op {op} for {opcode.name} {args}")
        self.opcode = opcode
        self.args: List[Any] = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> a64.Ins:
        out = a64.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            if type(arg) == int:
                val = arg
            elif isinstance(arg, PARAM):
                val = _ExtractTmplArgOp(ins, arg, ctx)
            elif isinstance(arg, FIXARG):
                val = arg.value
            elif isinstance(arg, a64.SHIFT):
                val = arg.value
            else:
                assert False, f"unknown param {repr(arg)}"

            assert val is not None
            out.operands.append(a64.EncodeOperand(self.opcode.fields[n], val))
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
    See ../Docs/instruction_selection.md
    """
    # groups all the patterns for a given opcode number together
    Table: Dict[int, List["Pattern"]] = collections.defaultdict(list)

    def __init__(self, opcode: o.Opcode, type_constraints: List[o.DK],
                 emit: List[InsTmpl],
                 imm_curb0=IMM_CURB.INVALID,
                 imm_curb1=IMM_CURB.INVALID,
                 imm_curb2=IMM_CURB.INVALID,
                 imm_curb3=IMM_CURB.INVALID,
                 imm_curb4=IMM_CURB.INVALID):
        # the template, usually contains ArmIns except for the nop1 pattern
        self.emit = emit
        # how to fill the template params
        assert len(type_constraints) == len(
            opcode.operand_kinds), f"{opcode.name} {type_constraints} {opcode.operand_kinds}"
        imm_curbs = [imm_curb0, imm_curb1, imm_curb2, imm_curb3, imm_curb4]
        imm_curbs = imm_curbs[:len(type_constraints)]
        self.type_constraints = type_constraints
        self.opcode = opcode
        self.imm_curbs = imm_curbs
        for type_constr, imm_constr, kind in zip(type_constraints, imm_curbs,
                                                 opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr is IMM_CURB.INVALID
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr != IMM_CURB.INVALID
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert imm_constr is IMM_CURB.INVALID, f"bad pattern for {opcode}"

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

    def MatchesImmCurbs(self, ins: ir.Ins, assume_stk_op_matches: bool) -> int:
        """Returns bit positions that have a mismatch

        assumes that MatchesTypeConstraints return true
        Possible return values:
        * 0: perfect match, pattern can be used directly for code generation
        * MATCH_IMPOSSBILE: pattern is not suitable
        * other: partial match, pattern can be used if the operands at the bit positions which are set
                would live in a register instead of being an immediate
        """
        out = 0
        for pos, (imm_curb, op) in enumerate(zip(self.imm_curbs, ins.operands)):
            if isinstance(op, ir.Const):
                if imm_curb is IMM_CURB.INVALID:
                    # have constant but need a reg (we know the op must be a reg because ow there would
                    #  not be a match at all
                    out |= 1 << pos
                    continue
                val = op.value
                if imm_curb in _IMM_KIND_STK:
                    stk = ins.operands[pos - 1]
                    if not isinstance(stk, ir.Stk):
                        return MATCH_IMPOSSIBLE
                    if assume_stk_op_matches:
                        # we have not finalized the stack yet but by design we know that
                        # all stack operands can be matched
                        continue
                    assert stk.slot is not None, f"unfinalized stack slot for {stk} in {ins}"
                    val += stk.slot
                if not ValueMatchesCurbs(imm_curb, val):

                    # have constant that does not fit
                    return MATCH_IMPOSSIBLE
            elif isinstance(op, ir.Reg):
                if imm_curb is not IMM_CURB.INVALID:
                    # have a reg but need a const
                    return MATCH_IMPOSSIBLE
        return out

    def __str__(self):
        types = [x.name for x in self.type_constraints]
        curbs = [x.name for x in self.imm_curbs]
        return f"PATTERN {self.opcode.name} [{' '.join(types)}] [{' '.join(curbs)}]"


def EmitFunEpilog(ctx: regs.EmitContext) -> List[InsTmpl]:
    out = []
    # we reverse everything at the end
    out.append(InsTmpl("ret", [FIXARG.LR]))

    gpr_regs = regs.MaskToGpr64Regs(ctx.gpr_reg_mask)
    while gpr_regs:
        r1 = gpr_regs.pop(-1)
        if not gpr_regs:
            out.append(InsTmpl("ldr_x_imm_post", [r1.no, FIXARG.SP, 16]))
            break
        else:
            r2 = gpr_regs.pop(-1)
            out.append(InsTmpl("ldp_x_imm_post", [
                       r2.no, r1.no, FIXARG.SP, 16]))
    flt_regs = regs.MaskToFlt64Regs(ctx.flt_reg_mask)
    while flt_regs:
        r1 = flt_regs.pop(-1)
        if not flt_regs:
            out.append(InsTmpl("fldr_d_imm_post", [r1.no, FIXARG.SP, 16]))
            break
        else:
            r2 = flt_regs.pop(-1)
            out.append(InsTmpl("fldp_d_imm_post", [
                       r2.no, r1.no, FIXARG.SP, 16]))
    # a9bf7bfd 	stp	x29, x30, [sp, #-16]!

    stk_size = ctx.stk_size
    assert (stk_size >> 24) == 0
    if stk_size & 0xfff000 != 0:
        out.append(
            InsTmpl("add_x_imm", [FIXARG.SP, FIXARG.SP, stk_size & 0xfff000]))
    if stk_size & 0xfff != 0:
        out.append(
            InsTmpl("add_x_imm", [FIXARG.SP, FIXARG.SP, stk_size & 0xfff]))
    # Note: we need to reverse these
    out.reverse()
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
    gpr_regs = regs.MaskToGpr64Regs(ctx.gpr_reg_mask)
    while gpr_regs:
        r1 = gpr_regs.pop(-1)
        if not gpr_regs:
            # rethink this if we want a predictable stack location of the return address
            out.append(InsTmpl("str_x_imm_pre", [FIXARG.SP, -16, r1.no]))
            break
        r2 = gpr_regs.pop(-1)
        out.append(InsTmpl("stp_x_imm_pre", [FIXARG.SP, -16, r2.no, r1.no]))
    flt_regs = regs.MaskToFlt64Regs(ctx.flt_reg_mask)
    while flt_regs:
        r1 = flt_regs.pop(-1)
        if not flt_regs:
            out.append(InsTmpl("fstr_d_imm_pre", [FIXARG.SP, -16, r1.no]))
            break
        else:
            r2 = flt_regs.pop(-1)
            out.append(InsTmpl("fstp_d_imm_pre", [
                       FIXARG.SP, -16, r2.no, r1.no]))

    stk_size = ctx.stk_size
    assert (stk_size >> 24) == 0, f"stack is too large {stk_size}"
    if stk_size & 0xfff000 != 0:
        out.append(
            InsTmpl("sub_x_imm", [FIXARG.SP, FIXARG.SP, stk_size & 0xfff000]))
    if stk_size & 0xfff != 0:
        out.append(
            InsTmpl("sub_x_imm", [FIXARG.SP, FIXARG.SP, stk_size & 0xfff]))

    return out


OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.LINE,  # debug line number
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
    LR = 30
    SP = 31
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
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(a64_opc, [PARAM.bbl2])],
                    imm_curb1=IMM_CURB.IMM_SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for opc, a64_opc in [(o.BEQ, "b_eq"), (o.BNE, "b_ne")]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(a64_opc, [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(a64_opc, [PARAM.bbl2])],
                    imm_curb1=IMM_CURB.IMM_SHIFTED_10_21_22)

    for kind in [o.DK.U32, o.DK.S32]:
        xlate = _CMP_SIGNED if kind == o.DK.S32 else _CMP_UNSIGNED
        xlate_inv = _CMP_SIGNED_INV if kind == o.DK.S32 else _CMP_UNSIGNED_INV

        for opc in [o.BLT, o.BLE]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_w_reg", [FIXARG.WZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])],
                    imm_curb1=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg1, PARAM.num0]),
                     InsTmpl(xlate_inv[opc], [PARAM.bbl2])],
                    imm_curb0=IMM_CURB.IMM_SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.A64, o.DK.C64, o.DK.S64]:
        xlate = _CMP_SIGNED if kind == o.DK.S64 else _CMP_UNSIGNED
        xlate_inv = _CMP_SIGNED_INV if kind == o.DK.S64 else _CMP_UNSIGNED_INV

        for opc in [o.BLT, o.BLE]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])])
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg0, PARAM.num1]),
                     InsTmpl(xlate[opc], [PARAM.bbl2])],
                    imm_curb1=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(opc, type_constraints,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg1, PARAM.num0]),
                     InsTmpl(xlate_inv[opc], [PARAM.bbl2])],
                    imm_curb0=IMM_CURB.IMM_SHIFTED_10_21_22)

    # * we do not have a story for the unordered case
    for kind, a64_cmp in [(o.DK.F32, "fcmpe_s"), (o.DK.F64, "fcmpe_d")]:
        for opc, a64_bxx in [(o.BEQ, "b_eq"), (o.BNE, "b_ne"),
                             (o.BLT, "b_mi"), (o.BLE, "b_ls")]:
            Pattern(opc, [kind, kind, o.DK.INVALID],
                    [InsTmpl(a64_cmp, [PARAM.reg0, PARAM.reg1]),
                     InsTmpl(a64_bxx, [PARAM.bbl2])])
            Pattern(opc, [kind, kind, o.DK.INVALID],
                    [InsTmpl(a64_cmp + "_zero", [PARAM.reg0, 0]),
                     InsTmpl(a64_bxx, [PARAM.bbl2])],
                    imm_curb1=IMM_CURB.ZERO)


def InitCmp():
    # TODO: cover the floating points ones
    for kind in [o.DK.U32, o.DK.S32]:
        for cmp_kind in [o.DK.U32, o.DK.S32]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 5,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
        for cmp_kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for cmp_kind in [o.DK.U32, o.DK.S32]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
        for cmp_kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for cmp_kind, csel, inv_csel in [
            (o.DK.U32, "csel_x_cc", "csel_x_cs"),
                (o.DK.S32, "csel_x_lt", "csel_x_ge")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.num3, PARAM.reg4]),
                     InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb3=IMM_CURB.IMM_SHIFTED_10_21_22)
    for kind in [o.DK.U32, o.DK.S32]:
        for cmp_kind, csel, inv_csel in [
            (o.DK.U32, "csel_w_cc", "csel_w_cs"),
                (o.DK.S32, "csel_w_lt", "csel_w_ge")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_reg", [FIXARG.WZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_w_imm", [FIXARG.WZR, PARAM.num3, PARAM.reg4]),
                     InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb3=IMM_CURB.IMM_SHIFTED_10_21_22)
    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for cmp_kind, csel, inv_csel in [
            (o.DK.U64, "csel_x_cc", "csel_x_cs"),
            (o.DK.A64, "csel_x_cc", "csel_x_cs"),  # should this be signed?
                (o.DK.S64, "csel_x_lt", "csel_x_ge")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.num3, PARAM.reg4]),
                     InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb3=IMM_CURB.IMM_SHIFTED_10_21_22)
    for kind in [o.DK.U32, o.DK.S32]:
        for cmp_kind, csel, inv_csel in [
            (o.DK.U64, "csel_w_cc", "csel_w_cs"),
            (o.DK.A64, "csel_w_cc", "csel_w_cs"),  # should this be signed?
                (o.DK.S64, "csel_w_lt", "csel_w_ge")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_reg", [FIXARG.XZR, PARAM.reg3, PARAM.reg4, a64.SHIFT.lsl, 0]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.reg3, PARAM.num4]),
                     InsTmpl(csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb4=IMM_CURB.IMM_SHIFTED_10_21_22)
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl("subs_x_imm", [FIXARG.XZR, PARAM.num3, PARAM.reg4]),
                     InsTmpl(inv_csel, [PARAM.reg0, PARAM.reg1, PARAM.reg2])],
                    imm_curb3=IMM_CURB.IMM_SHIFTED_10_21_22)
    for kind in [o.DK.U32, o.DK.S32]:
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl("csel_w_mi", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl("csel_w_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl("csel_x_mi", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl("csel_x_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for kind, sel in [(o.DK.F64, "fcsel_d"), (o.DK.F32, "fcsel_s")]:
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPLT, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl(sel + "_mi", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        for cmp_kind, cmp in [(o.DK.F32, "fcmp_s"), (o.DK.F64, "fcmp_d")]:
            Pattern(o.CMPEQ, [kind] * 3 + [cmp_kind] * 2,
                    [InsTmpl(cmp, [PARAM.reg3, PARAM.reg4]),
                     InsTmpl(sel + "_eq", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])


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
                    imm_curb2=IMM_CURB.IMM_10_15_16_22_W)
        for opc, a64_opc in [(o.SUB, "sub_w_imm"), (o.ADD, "add_w_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_curb2=IMM_CURB.IMM_SHIFTED_10_21_22)
        Pattern(o.SUB, [kind1] * 3,
                [InsTmpl("sub_w_reg", [PARAM.reg0, FIXARG.WZR,
                         PARAM.reg2, a64.SHIFT.lsl, 0])],
                imm_curb1=IMM_CURB.ZERO)
        Pattern(o.CNTLZ, [kind1] * 2,
                [InsTmpl("clz_w", [PARAM.reg0, PARAM.reg1])])
        Pattern(o.CNTTZ, [kind1] * 2,
                [InsTmpl("rbit_w", [PARAM.reg0, PARAM.reg1]),
                 InsTmpl("clz_w", [PARAM.reg0, PARAM.reg0])])
        Pattern(o.CNTPOP, [kind1] * 2,
                [InsTmpl("orr_w_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0]),
                 InsTmpl("fmov_d_from_x", [PARAM.scratch_flt, PARAM.reg0]),
                 InsTmpl("cnt_8b", [PARAM.scratch_flt, PARAM.scratch_flt]),
                 InsTmpl("uaddlv_8b", [PARAM.scratch_flt, PARAM.scratch_flt]),
                 InsTmpl("fmov_w_from_s", [PARAM.reg0, PARAM.scratch_flt])])

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
                    imm_curb2=IMM_CURB.IMM_10_15_16_22_X)
        for opc, a64_opc in [(o.SUB, "sub_x_imm"), (o.ADD, "add_x_imm")]:
            Pattern(opc, [kind1] * 3,
                    [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_curb2=IMM_CURB.IMM_SHIFTED_10_21_22)
        Pattern(o.SUB, [kind1] * 3,
                [InsTmpl("sub_x_reg", [PARAM.reg0, FIXARG.XZR,
                         PARAM.reg2, a64.SHIFT.lsl, 0])],
                imm_curb1=IMM_CURB.ZERO)
        Pattern(o.CNTLZ, [kind1] * 2,
                [InsTmpl("clz_x", [PARAM.reg0, PARAM.reg1])])
        Pattern(o.CNTTZ, [kind1] * 2,
                [InsTmpl("rbit_x", [PARAM.reg0, PARAM.reg1]),
                 InsTmpl("clz_x", [PARAM.reg0, PARAM.reg0])])
        Pattern(o.CNTPOP, [kind1] * 2,
                [InsTmpl("fmov_d_from_x", [PARAM.scratch_flt, PARAM.reg1]),
                 InsTmpl("cnt_8b", [PARAM.scratch_flt, PARAM.scratch_flt]),
                 InsTmpl("uaddlv_8b", [PARAM.scratch_flt, PARAM.scratch_flt]),
                 InsTmpl("fmov_w_from_s", [PARAM.reg0, PARAM.scratch_flt])])

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
                imm_curb2=IMM_CURB.ANY)  # pick better constraint

    for kind1, a64_opc in [(o.DK.U32, "ubfm_w"),
                           (o.DK.S32, "ubfm_w"),
                           (o.DK.U64, "ubfm_x"),
                           (o.DK.S64, "ubfm_x")]:
        Pattern(o.SHL, [kind1] * 3,
                [InsTmpl(a64_opc,
                         [PARAM.reg0, PARAM.reg1, PARAM.num2_rsb_width,
                          PARAM.num2_rsb_width_minus1])],
                imm_curb2=IMM_CURB.ANY)  # pick better constraint


def InitLoad():
    for dst_kind, opc in [(o.DK.U64, "ldr_x"), (o.DK.S64, "ldr_x"),
                          (o.DK.A64, "ldr_x"), (o.DK.C64, "ldr_x"),
                          (o.DK.U32, "ldr_w"), (o.DK.S32, "ldrsw"),
                          (o.DK.U16, "ldr_h"), (o.DK.S16, "ldrsh_x"),
                          (o.DK.U8, "ldr_b"), (o.DK.S8, "ldrsb_x"),
                          (o.DK.F32, "fldr_s"), (o.DK.F64, "fldr_d")]:
        for offset_kind in [o.DK.S64, o.DK.U64]:
            Pattern(o.LD, [dst_kind, o.DK.A64, offset_kind],
                    [InsTmpl(opc + "_reg_x",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, a64.SHIFT.lsl, 0])])
        for shift, offset_kind in [(FIXARG.SXTW, o.DK.S32), (FIXARG.UXTW, o.DK.U32)]:
            Pattern(o.LD, [dst_kind, o.DK.A64, offset_kind],
                    [InsTmpl(opc + "_reg_w",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, shift, 0])])
        # support zero offset for now - this could be improved a lot
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            Pattern(o.LD, [dst_kind, o.DK.A64, offset_kind],
                    [InsTmpl(opc + "_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                    imm_curb2=IMM_CURB.ZERO)
        # TODO: add immediate flavors


def InitStackLoad():
    # support for smaller stack offsets
    for dst_kind, opc, curb in [
        (o.DK.U64, "ldr_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.S64, "ldr_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.A64, "ldr_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.C64, "ldr_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.U32, "ldr_w_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
        (o.DK.S32, "ldrsw_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
        (o.DK.U16, "ldrsh_x_imm", IMM_CURB.pos_stk_combo_10_21_times_2),
        (o.DK.S16, "ldr_h_imm", IMM_CURB.pos_stk_combo_10_21_times_2),
        (o.DK.U8, "ldr_b_imm", IMM_CURB.pos_stk_combo_10_21),
        (o.DK.S8, "ldrsb_x_imm", IMM_CURB.pos_stk_combo_10_21),
        (o.DK.F32, "fldr_s_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
            (o.DK.F64, "fldr_d_imm", IMM_CURB.pos_stk_combo_10_21_times_8)]:
        # note: the first and second op are combined in the generated code
        # The offset_kind does not really matter, what matters is actual values
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            Pattern(o.LD_STK, [dst_kind, o.DK.INVALID, offset_kind],
                    [InsTmpl(opc, [PARAM.reg0, FIXARG.SP, PARAM.stk1_offset2])],
                    imm_curb2=curb)

    # support stack offsets up to 64k
    for dst_kind, opc in [
        (o.DK.U64, "ldr_x_reg_w"),
        (o.DK.S64, "ldr_x_reg_w"),
        (o.DK.A64, "ldr_x_reg_w"),
        (o.DK.C64, "ldr_x_reg_w"),
        (o.DK.U32, "ldr_w_reg_w"),
        (o.DK.S32, "ldrsw_reg_w"),
        (o.DK.U16, "ldrsh_x_reg_w"),
        (o.DK.S16, "ldr_h_reg_w"),
        (o.DK.U8, "ldr_b_reg_w"),
        (o.DK.S8, "ldrsb_x_reg_w"),
        (o.DK.F32, "fldr_s_reg_w"),
            (o.DK.F64, "fldr_d_reg_w")]:
        # The offset_kind does not really matter, what matters is actual values
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            Pattern(o.LD_STK, [dst_kind, o.DK.INVALID, offset_kind],
                    [InsTmpl("movz_x_imm", [PARAM.scratch_gpr, PARAM.stk1_offset2]),
                    InsTmpl(opc, [PARAM.reg0, FIXARG.SP, PARAM.scratch_gpr, FIXARG.UXTW, 0])],
                    imm_curb2=IMM_CURB.pos_stk_combo_16_bits)


def InitStore():
    for src_kind, opc in [(o.DK.U64, "str_x"), (o.DK.S64, "str_x"),
                          (o.DK.A64, "str_x"), (o.DK.C64, "str_x"),
                          (o.DK.U32, "str_w"), (o.DK.S32, "str_w"),
                          (o.DK.U16, "str_h"), (o.DK.S16, "str_h"),
                          (o.DK.U8, "str_b"), (o.DK.S8, "str_b"),
                          (o.DK.F64, "fstr_d"), (o.DK.F32, "fstr_s")]:
        for offset_kind in [o.DK.S64, o.DK.U64]:
            Pattern(o.ST, [o.DK.A64, offset_kind, src_kind],
                    [InsTmpl(opc + "_reg_x",
                             [PARAM.reg0, PARAM.reg1, a64.SHIFT.lsl,
                              0, PARAM.reg2])])
        for shift, offset_kind in [(FIXARG.SXTW, o.DK.S32), (FIXARG.UXTW, o.DK.U32)]:
            Pattern(o.ST, [o.DK.A64, offset_kind, src_kind],
                    [InsTmpl(opc + "_reg_w",
                             [PARAM.reg0, PARAM.reg1, shift, 0, PARAM.reg2])])
    # TODO: add immediate flavors


def _UnsignedExtension(reg, bw: int, set_cc:  bool) -> List[InsTmpl]:
    cc = "s" if set_cc else ""
    if bw == 8:
        return InsTmpl(f"and{cc}_x_imm", [reg, reg, 0xff])
    elif bw == 16:
        return InsTmpl(f"and{cc}_x_imm", [reg, reg, 0xffff])
    elif bw == 32:
        return InsTmpl(f"add{cc}_w_imm", [reg, reg, 0])
    else:
        return InsTmpl(f"add{cc}_x_imm", [reg, reg, 0])


def InitCAS():
    """
    4009e8:       2a0003f0        <zero-ext>     scratch, reg1
    4009ec:       885ffc40        ldaxr   reg0, [reg3]
    4009f0:       6b10001f        cmp     rego, scratch
*   4009f4:       54000061        b.ne    3
    4009f8:       8811fc41        stlxr   scratch, reg2, [x2]
*   4009fc:       35ffff91        cbnz    scratch, -4
    cas   dst expected src  base
loop:
    tmp = ldl base
    tmp = xor tmp expected
    tmp = ext tmp [set cc]
    tmp = xor tmp expected
    tmp = ext tmp
    b.ne  done
    tmp  = stc src
    cbnz loop
    mov tmp expected
    done:
         mov dst tmp


    """
    for kind, suffix in [(o.DK.U64, "x"), (o.DK.S64, "x"),
                         (o.DK.A64, "x"), (o.DK.C64, "x"),
                         (o.DK.U32, "w"), (o.DK.S32, "w"),
                         (o.DK.U16, "h"), (o.DK.S16, "h"),
                         (o.DK.U8, "b"), (o.DK.S8, "b")]:
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            # Note: this will break with peephole optimizations
            # unless we fixup the branch targets
            Pattern(o.CAS, [kind, kind, kind, o.DK.A64, offset_kind],
                    [InsTmpl(f"ldaxr_{suffix}", [PARAM.scratch_gpr, PARAM.reg3]),
                    InsTmpl(f"eor_x_reg",
                            [PARAM.scratch_gpr, PARAM.scratch_gpr, PARAM.reg1, a64.SHIFT.lsl, 0]),
                    _UnsignedExtension(PARAM.scratch_gpr,
                                       kind.bitwidth(), True),
                    InsTmpl(f"eor_x_reg", [
                        PARAM.scratch_gpr, PARAM.scratch_gpr, PARAM.reg1, a64.SHIFT.lsl, 0]),
                    _UnsignedExtension(PARAM.scratch_gpr,
                                       kind.bitwidth(), False),
                    InsTmpl("b_ne", [4]),
                    InsTmpl(f"stlxr_{suffix}", [
                        PARAM.scratch_gpr, PARAM.reg3, PARAM.reg2]),
                    InsTmpl("cbnz_w", [PARAM.scratch_gpr, -7]),
                    InsTmpl(f"orr_x_reg", [
                            PARAM.scratch_gpr,  FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0]),
                     InsTmpl(f"orr_x_reg", [
                         PARAM.reg0,  FIXARG.XZR, PARAM.scratch_gpr, a64.SHIFT.lsl, 0]),
                     ], imm_curb4=IMM_CURB.ZERO)


def InitStackStore():
    for src_kind, opc, imm in [
        (o.DK.U64, "str_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.S64, "str_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.A64, "str_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.C64, "str_x_imm", IMM_CURB.pos_stk_combo_10_21_times_8),
        (o.DK.U32, "str_w_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
        (o.DK.S32, "str_w_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
        (o.DK.U16, "str_h_imm", IMM_CURB.pos_stk_combo_10_21_times_2),
        (o.DK.S16, "str_h_imm", IMM_CURB.pos_stk_combo_10_21_times_2),
        (o.DK.U8, "str_b_imm", IMM_CURB.pos_stk_combo_10_21),
        (o.DK.S8, "str_b_imm", IMM_CURB.pos_stk_combo_10_21),
        (o.DK.F32, "fstr_s_imm", IMM_CURB.pos_stk_combo_10_21_times_4),
            (o.DK.F64, "fstr_d_imm", IMM_CURB.pos_stk_combo_10_21_times_8)]:
        # STACK VARIANTS: note we cover all reasonable offsets
        # note: the first and second op are combined in the generated code
        # The offset_kind does not really matter, what matters is actual values
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            Pattern(o.ST_STK, [o.DK.INVALID, offset_kind, src_kind],
                    [InsTmpl(opc, [FIXARG.SP, PARAM.stk0_offset1, PARAM.reg2])],
                    imm_curb1=imm)

    # support stack offsets up to 64k
    for src_kind, opc in [
        (o.DK.U64, "str_x_reg_w"),
        (o.DK.S64, "str_x_reg_w"),
        (o.DK.A64, "str_x_reg_w"),
        (o.DK.C64, "str_x_reg_w"),
        (o.DK.U32, "str_w_reg_w"),
        (o.DK.S32, "str_w_reg_w"),
        (o.DK.U16, "str_h_reg_w"),
        (o.DK.S16, "str_h_reg_w"),
        (o.DK.U8, "str_b_reg_w"),
        (o.DK.S8, "str_b_reg_w"),
        (o.DK.F32, "fstr_s_reg_w"),
            (o.DK.F64, "fstr_d_reg_w")]:
        # The offset_kind does not really matter, what matters is actual values
        for offset_kind in [o.DK.S64, o.DK.U64, o.DK.S32, o.DK.U32]:
            Pattern(o.ST_STK, [o.DK.INVALID, offset_kind, src_kind],
                    [InsTmpl("movz_x_imm", [PARAM.scratch_gpr, PARAM.stk0_offset1]),
                    InsTmpl(opc, [FIXARG.SP, PARAM.scratch_gpr, FIXARG.UXTW, 0, PARAM.reg2])],
                    imm_curb1=IMM_CURB.pos_stk_combo_16_bits)


def InitLea():
    Pattern(o.LEA_FUN, [o.DK.C64, o.DK.INVALID],
            [InsTmpl("adrp", [PARAM.reg0, PARAM.fun1_prel_hi21]),
             InsTmpl("add_x_imm", [PARAM.reg0, PARAM.reg0, PARAM.fun1_lo12])])
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        Pattern(o.LEA_MEM, [o.DK.A64, o.DK.INVALID, kind1],
                [InsTmpl("adrp", [PARAM.reg0, PARAM.mem1_num2_prel_hi21]),
                 InsTmpl("add_x_imm", [PARAM.reg0, PARAM.reg0, PARAM.mem1_num2_lo12])],
                imm_curb2=IMM_CURB.ANY)

    for kind1 in [o.DK.U64, o.DK.S64]:
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [InsTmpl("add_x_reg",
                         [PARAM.reg0, PARAM.reg1, PARAM.reg2, a64.SHIFT.lsl, 0])])
    for offset_kind, opc in [(o.DK.U32, "add_x_reg_uxtw"), (o.DK.S32, "add_x_reg_sxtw")]:
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, offset_kind],
                [InsTmpl(opc, [PARAM.reg0, PARAM.reg1, PARAM.reg2, 0])])

    for offset_kind in [o.DK.U64, o.DK.S64, o.DK.U32, o.DK.S32]:
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, offset_kind],
                [InsTmpl("add_x_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2])],
                imm_curb2=IMM_CURB.IMM_SHIFTED_10_21_22)

    for offset_kind in [o.DK.U64, o.DK.S64, o.DK.U32, o.DK.S32]:
        # Note, lea_stks are our last resort and MUST support ALL possible immediates
        #        that occur in practice
        # note: the second and third op are combined in the generated code
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, offset_kind],
                [InsTmpl("add_x_imm", [PARAM.reg0, FIXARG.SP, PARAM.stk1_offset2])],
                imm_curb2=IMM_CURB.pos_stk_combo_shifted_10_21_22)
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, offset_kind],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.stk1_offset2]),
                 InsTmpl("add_x_reg_uxtx", [PARAM.reg0, FIXARG.SP, PARAM.reg0, 0])],
                imm_curb2=IMM_CURB.pos_stk_combo_16_bits)
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, offset_kind],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.stk1_offset2_lo]),
                 InsTmpl("movk_x_imm", [PARAM.reg0,
                         PARAM.stk1_offset2_hi, 16]),
                 InsTmpl("add_x_reg_uxtx", [PARAM.reg0, FIXARG.SP, PARAM.reg0, 0])],
                imm_curb2=IMM_CURB.pos_stk_combo_32_bits)
        # TODO: we we really need to support stack offsets > 32 bits?


# Note, moves are our last resort and MUST support 64bit immediates
def InitMove():
    for kind1 in [o.DK.A64, o.DK.C64, o.DK.U64,  #
                  o.DK.S64, o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.num1])],
                imm_curb1=IMM_CURB.IMM_SHIFTED_5_20_21_22)
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("movn_x_imm", [PARAM.reg0, PARAM.num1_not])],
                imm_curb1=IMM_CURB.IMM_SHIFTED_5_20_21_22_NOT)
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.num1_0_16]),
                 InsTmpl("movk_x_imm", [PARAM.reg0, PARAM.num1_16_32, 16])],
                imm_curb1=IMM_CURB.IMM_POS_32)
        Pattern(o.MOV, [kind1, kind1],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.num1_0_16]),
                 InsTmpl("movk_x_imm", [PARAM.reg0, PARAM.num1_16_32, 16]),
                 InsTmpl("movk_x_imm", [PARAM.reg0, PARAM.num1_32_48, 32]),
                 InsTmpl("movk_x_imm", [PARAM.reg0, PARAM.num1_48_64, 48])],
                imm_curb1=IMM_CURB.ANY)
        Pattern(o.GETFP, [o.DK.A64],
                [InsTmpl("movz_x_imm", [PARAM.reg0, PARAM.frame_size]),
                InsTmpl("add_x_reg_uxtx", [PARAM.reg0, FIXARG.SP, PARAM.reg0, 0])])
        Pattern(o.GETSP, [o.DK.A64],
                [InsTmpl("add_x_imm", [PARAM.reg0, FIXARG.SP, 0])])


def InitConv():
    # truncation to operand of smaller bit width: nothing to be done here
    for dst_kind in [o.DK.U64, o.DK.S64, o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for src_kind in [o.DK.U64, o.DK.S64]:
            Pattern(o.CONV, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])
    for dst_kind in [o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for src_kind in [o.DK.U32, o.DK.S32]:
            Pattern(o.CONV, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])
    for dst_kind in [o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for src_kind in [o.DK.U16, o.DK.S16]:
            Pattern(o.CONV, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])

    # bitcast between equal bit  width ops: nothing to be done here
    for dst_kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        for src_kind in [o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
            Pattern(o.BITCAST, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])
    for dst_kind in [o.DK.U32, o.DK.S32]:
        for src_kind in [o.DK.U32, o.DK.S32]:
            Pattern(o.BITCAST, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])

    # sign change from 8it: nothing to be done here
    # TODO: explain when this happens - why only got 8bit?
    for dst_kind in [o.DK.U8, o.DK.S8]:
        for src_kind in [o.DK.U8, o.DK.S8]:
            Pattern(o.CONV, [dst_kind, src_kind],
                    [InsTmpl("orr_x_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])

    # TODO: this is iffy, should we go S32 -> U32 -> U64 or S32 -> S64 -> U64?
    Pattern(o.CONV, [o.DK.U64, o.DK.S32],
            [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 31])])

    for dst_kind in [o.DK.S64, o.DK.S32, o.DK.U64, o.DK.U32]:
        Pattern(o.CONV, [dst_kind, o.DK.S16],
                [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 15])])
        Pattern(o.CONV, [dst_kind, o.DK.U16],
                [InsTmpl("and_x_imm", [PARAM.reg0, PARAM.reg1, 0xffff])])

    for dst_kind in [o.DK.S64, o.DK.S32, o.DK.U64, o.DK.U32, o.DK.S16, o.DK.U16]:
        Pattern(o.CONV, [dst_kind, o.DK.S8],
                [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 7])])
        Pattern(o.CONV, [dst_kind, o.DK.U8],
                [InsTmpl("and_x_imm", [PARAM.reg0, PARAM.reg1, 0xff])])

    for dst_kind in [o.DK.U64, o.DK.S64]:
        Pattern(o.CONV, [dst_kind, o.DK.U32],
                [InsTmpl("orr_w_reg", [PARAM.reg0, FIXARG.XZR, PARAM.reg1, a64.SHIFT.lsl, 0])])

    Pattern(o.CONV, [o.DK.S64, o.DK.S32],
            [InsTmpl("sbfm_x", [PARAM.reg0, PARAM.reg1, 0, 31])])

    Pattern(o.CONV, [o.DK.F64, o.DK.F32],
            [InsTmpl("fcvt_d_s", [PARAM.reg0, PARAM.reg1])])

    Pattern(o.CONV, [o.DK.F32, o.DK.F64],
            [InsTmpl("fcvt_s_d", [PARAM.reg0, PARAM.reg1])])


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
            imm_curb1=IMM_CURB.IMM_SHIFTED_5_20_21_22)

    # Note: a dummy "nop1 %scratch_gpr" either immediately before
    # or after will ensure that %scratch_gpr is available
    # We currently use very inefficient jmp tables (8 byte entries)
    Pattern(o.SWITCH, [o.DK.U32, o.DK.INVALID],
            [InsTmpl("adrp", [PARAM.scratch_gpr, PARAM.jtb1_prel_hi21]),
             InsTmpl("add_x_imm", [PARAM.scratch_gpr,
                     PARAM.scratch_gpr, PARAM.jtb1_lo12]),
             InsTmpl("ldr_x_reg_w",
                     [PARAM.scratch_gpr, PARAM.scratch_gpr, PARAM.reg0, FIXARG.UXTW, 3]),
             InsTmpl("br", [PARAM.scratch_gpr])])


def InitVFP():
    for kind, suffix in [(o.DK.F32, "_s"), (o.DK.F64, "_d")]:
        Pattern(o.MOV, [kind] * 2,
                [InsTmpl("fmov" + suffix + "_reg", [PARAM.reg0, PARAM.reg1])])
        Pattern(o.FLOOR, [kind] * 2,
                [InsTmpl("frintm" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.CEIL, [kind] * 2,
                [InsTmpl("frintp" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.ROUND, [kind] * 2,
                [InsTmpl("frinta" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.TRUNC, [kind] * 2,
                [InsTmpl("frintz" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.ADD, [kind] * 3,
                [InsTmpl("fadd" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.SUB, [kind] * 3,
                [InsTmpl("fsub" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.MUL, [kind] * 3,
                [InsTmpl("fmul" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.DIV, [kind] * 3,
                [InsTmpl("fdiv" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        # implies fastmath
        Pattern(o.SQRT, [kind] * 2,
                [InsTmpl("fsqrt" + suffix, [PARAM.reg0, PARAM.reg1])])

        Pattern(o.COPYSIGN, [kind] * 3,
                [InsTmpl("fabs" + suffix, [PARAM.reg0, PARAM.reg1])],
                imm_curb2=IMM_CURB.ZERO)

    Pattern(o.COPYSIGN, [o.DK.F32] * 3,
            [InsTmpl("fmov_w_from_s", [PARAM.scratch_gpr, PARAM.reg2]),
             InsTmpl("fabs_s", [PARAM.reg0, PARAM.reg1]),
             InsTmpl("tbz", [PARAM.scratch_gpr, 31, 2]),
             InsTmpl("fneg_s", [PARAM.reg0, PARAM.reg0])])

    Pattern(o.COPYSIGN, [o.DK.F64] * 3,
            [InsTmpl("fmov_x_from_d", [PARAM.scratch_gpr, PARAM.reg2]),
             InsTmpl("fabs_d", [PARAM.reg0, PARAM.reg1]),
             InsTmpl("tbz", [PARAM.scratch_gpr, 63, 0]),
             InsTmpl("fneg_d", [PARAM.reg0, PARAM.reg0])])

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

    for kind_dst, kind_src, a64_opc in [(o.DK.F64, o.DK.U64, "fmov_d_from_x"),
                                        (o.DK.F64, o.DK.S64, "fmov_d_from_x"),
                                        (o.DK.F32, o.DK.S32, "fmov_s_from_w"),
                                        (o.DK.F32, o.DK.U32, "fmov_s_from_w"),
                                        (o.DK.U64, o.DK.F64, "fmov_x_from_d"),
                                        (o.DK.S64, o.DK.F64, "fmov_x_from_d"),
                                        (o.DK.U32, o.DK.F32, "fmov_w_from_s"),
                                        (o.DK.S32, o.DK.F32, "fmov_w_from_s")]:
        Pattern(o.BITCAST, [kind_dst, kind_src],
                [InsTmpl(a64_opc, [PARAM.reg0, PARAM.reg1])])


InitLoad()
InitStackLoad()
InitStore()
InitCAS()
InitStackStore()
InitAlu()
InitLea()
InitMove()
InitCondBra()
InitCmp()
InitMiscBra()
InitConv()
InitVFP()


def FindMatchingPattern(ins: ir.Ins, diagnostic: bool = False) -> Optional[Pattern]:
    """Returns the best pattern matching `ins` or None

    This can only be called AFTER the stack has been finalized
    """
    patterns = Pattern.Table[ins.opcode.no]

    for p in patterns:
        if diagnostic:
            print(f"@@ trying pattern {p}", end=" ")
        if not p.MatchesTypeCurbs(ins):
            if diagnostic:
                print(f"TYPE_MISMATCH")
        elif 0 != p.MatchesImmCurbs(ins, False):
            if diagnostic:
                print(f"IMM_MISMATCH")
        else:
            return p
    else:
        # assert False, f"Could not find a matching patterns for {ins}. tried:\n{patterns}"
        return None


def FindtImmediateMismatchesInBestMatchPattern(ins: ir.Ins, assume_stk_op_matches: bool) -> int:
    """Returns a list of operand positions that need to be rewritten

    None means there was an error
    """
    best = MATCH_IMPOSSIBLE
    best_num_bits = bin(best).count('1')
    patterns = Pattern.Table[ins.opcode.no]
    for p in patterns:
        if not p.MatchesTypeCurbs(ins):
            continue
        mismatches = p.MatchesImmCurbs(ins, assume_stk_op_matches)
        if mismatches == 0:
            return 0
        num_bits = bin(mismatches).count('1')
        if num_bits < best_num_bits:
            best, best_num_bits = mismatches, num_bits
    return best


def _EmitCodeH(fout):
    for cls in [IMM_CURB, PARAM]:
        cgen.RenderEnum(cgen.NameValues(
            cls), f"class {cls.__name__} : uint8_t", fout)


def _RenderOperands(operands: List[Any]):
    out = []
    mask = 0
    for n, op in enumerate(operands):
        if isinstance(op, PARAM):
            mask |= 1 << n
            s = f"+PARAM::{op.name}"
        elif isinstance(op, FIXARG):
            s = f"+FIXARG::{op.name}"
        elif isinstance(op, a64.SHIFT):
            s = f"+SHIFT::{op.name}"
        elif isinstance(op, int):
            s = f"{op}"
        else:
            assert False, f"bad op {op}"
        out.append(s)
    return mask, out


def _EmitCodeC(fout):
    for cls in [FIXARG, a64.SHIFT]:
        cgen.RenderEnum(cgen.NameValues(
            cls), f"class {cls.__name__} : uint8_t", fout)

    print(f"\nconst InsTmpl kInsTemplates[] = {{", file=fout)
    print("  { /*used first entry*/ },", file=fout)
    num_ins = 1
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None:
            continue
        opcode = o.Opcode.TableByNo.get(i)
        for pat in patterns:
            for tmpl in pat.emit:
                mask, ops = _RenderOperands(tmpl.args)
                num_ins += 1
                print(f"  {{ {{{', '.join(ops)}}},", file=fout)
                print(
                    f"    a64::OPC::{tmpl.opcode.NameForEnum()}, 0x{mask:x} }},  // {opcode.name} [{num_ins}]",
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
        if patterns is None:
            continue
        opcode = o.Opcode.TableByNo.get(i)
        for pat in patterns:
            reg_constraints = [f"DK::{c.name}" for c in pat.type_constraints]
            imm_constraints = [f"IC::{c.name}" for c in pat.imm_curbs]
            print(f"  {{ {{{', '.join(reg_constraints)}}},")
            print(f"    {{{', '.join(imm_constraints)}}},")
            print(
                f"    &kInsTemplates[{num_ins}], {len(pat.emit)} }},  // {opcode.name} [{num_pattern}]")
            num_ins += len(pat.emit)
            num_pattern += 1
    print(f"}};", file=fout)

    print("}  // namespace", file=fout)
    # TODO: without the ZZZ hack we get an  "array subscript XX is above array bounds" error but
    # only for these two instances - no idea why
    cgen.RenderEnumToStringMap(cgen.NameValues(
        IMM_CURB) + [("ZZZ", len(IMM_CURB))], "IMM_CURB", fout)
    cgen.RenderEnumToStringFun("IMM_CURB", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(
        PARAM) + [("ZZZ", len(PARAM))], "PARAM", fout)
    cgen.RenderEnumToStringFun("PARAM", fout)


def _DumpCodeSelTable():
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None:
            continue
        opcode = o.Opcode.TableByNo[i]
        print(
            f"{opcode.name} [{' '.join([k.name for k in opcode.operand_kinds])}]")
        for pat in patterns:
            type_constraints = [
                x.name if x != o.DK.INVALID else '*' for x in pat.type_constraints]
            imm_constraints = [x.name if x else '*' for x in pat.imm_curbs]

            print(
                f"  [{' '.join(type_constraints)}]  [{' '.join(imm_constraints)}]")
            for tmpl in pat.emit:
                ops = [str(x) if isinstance(x, int)
                       else x.name for x in tmpl.args]
                print(f"    {tmpl.opcode.name} [{' '.join(ops)}]")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "gen_h":
            cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_c":
            cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)

    else:
        _DumpCodeSelTable()
