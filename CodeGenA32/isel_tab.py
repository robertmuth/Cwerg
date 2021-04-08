#!/usr/bin/python3

"""Code Generation (Instruction Selection) for  ARMv6T2 and above

See `ARM32.md` for more details.
"""

import collections
from typing import List, Dict, Any, Set, Optional
import enum

from Base import ir
from Base import opcode_tab as o
from CodeGenA32 import regs
import CpuA32.opcode_tab as arm
from Elf import enum_tab
from Util import cgen


@enum.unique
class IMM_KIND(enum.IntEnum):
    """Immediate Kind

    Helps determine if a pattern is a suitable match
    """
    invalid = 0
    pos_8_bits_shifted = 1
    neg_8_bits_shifted = 2
    not_8_bits_shifted = 3
    pos_5_bits = 4
    pos_12_bits = 5
    neg_12_bits = 6
    pos_8_bits = 7
    neg_8_bits = 8
    pos_8_bits_times_4 = 9
    neg_8_bits_times_4 = 10
    pos_16_bits = 11
    any_32_bits = 12
    pos_stk_combo_8_bits_shifted = 13
    pos_stk_combo_8_bits = 14
    pos_stk_combo_8_bits_times_4 = 15
    pos_stk_combo_12_bits = 16
    pos_stk_combo_16_bits = 17


_NUM_MATCHERS: Dict[IMM_KIND, Any] = {
    IMM_KIND.pos_8_bits_shifted: lambda x: arm.EncodeRotateImm(x) is not None,
    IMM_KIND.neg_8_bits_shifted: lambda x: arm.EncodeRotateImm(-x & 0xffffffff) is not None,
    IMM_KIND.not_8_bits_shifted: lambda x: arm.EncodeRotateImm(~x & 0xffffffff) is not None,

    IMM_KIND.pos_5_bits: lambda x: 0 <= x < (1 << 5),

    IMM_KIND.pos_12_bits: lambda x: 0 <= x < (1 << 12),
    IMM_KIND.neg_12_bits: lambda x: -(1 << 12) < x <= 0,

    IMM_KIND.pos_8_bits: lambda x: 0 <= x < (1 << 8),
    IMM_KIND.neg_8_bits: lambda x: -(1 << 8) < x <= 0,
    IMM_KIND.pos_8_bits_times_4: lambda x: 0 <= (x // 4) < (1 << 8) and (x & 3) == 0,
    IMM_KIND.neg_8_bits_times_4: lambda x: -(1 << 8) < (x // 4) <= 0 and (x & 3) == 0,

    IMM_KIND.pos_16_bits: lambda x: 0 <= x < (1 << 16),
    IMM_KIND.any_32_bits: lambda x: True,

    IMM_KIND.pos_stk_combo_8_bits_shifted: lambda x: arm.EncodeRotateImm(x) is not None,
    IMM_KIND.pos_stk_combo_8_bits: lambda x: 0 <= x < (1 << 8),
    IMM_KIND.pos_stk_combo_8_bits_times_4: lambda x: 0 <= (x // 4) < (1 << 8),
    IMM_KIND.pos_stk_combo_12_bits: lambda x: 0 <= x < (1 << 12),
    IMM_KIND.pos_stk_combo_16_bits: lambda x: 0 <= x < (1 << 16),
}

_IMM_KIND_STK: Set[IMM_KIND] = {
    IMM_KIND.pos_stk_combo_8_bits_shifted,
    IMM_KIND.pos_stk_combo_8_bits,
    IMM_KIND.pos_stk_combo_8_bits_times_4,
    IMM_KIND.pos_stk_combo_12_bits,
    IMM_KIND.pos_stk_combo_16_bits,
}


def _InsAddNop1ForCodeSel(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    if opc is o.SWITCH:
        # needs scratch to compute the jmp address into
        scratch = fun.GetScratchReg(o.DK.C32, "switch", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    elif (opc is o.CONV and o.RegIsInt(ins.operands[0].kind) and
          ins.operands[1].kind.flavor() == o.DK_FLAVOR_F):
        # need scratch for intermediate ftl result
        # we know the result cannot be wider than 32bit for this CPU
        scratch = fun.GetScratchReg(o.DK.F32, "ftoi", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    elif (opc is o.CONV and o.RegIsInt(ins.operands[1].kind) and
          ins.operands[0].kind is o.DK.F64):
        # need scratch for intermediate ftl result
        # we know the result cannot be wider than 32bit for this CPU
        scratch = fun.GetScratchReg(o.DK.F32, "itof", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    return [ins]


def FunAddNop1ForCodeSel(fun: ir.Fun):
    return ir.FunGenericRewrite(fun, _InsAddNop1ForCodeSel)


@enum.unique
class PARAM(enum.Enum):
    """Placeholder in A32 instruction template for stuff that needs to be derived"""
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
    num1_lo16 = 19
    num1_hi16 = 20
    mem1_num2_lo16 = 21
    mem1_num2_hi16 = 22
    fun1_lo16 = 23
    fun1_hi16 = 24
    bbl0 = 25
    bbl2 = 26
    fun0 = 27
    jtb1_lo16 = 28
    jtb1_hi16 = 29
    scratch_flt = 30
    scratch_gpr = 31
    ldm_regmask = 32
    stm_regmask = 33
    vldm_start = 34
    vldm_count = 35
    vstm_start = 36
    vstm_count = 37
    stk0_offset1 = 38
    stk1_offset2 = 39
    stk1_offset2_lo = 40
    stk1_offset2_hi = 41


_RELOC_ARGS = {PARAM.bbl0, PARAM.bbl2, PARAM.fun0,
               PARAM.mem1_num2_lo16, PARAM.mem1_num2_hi16,
               PARAM.fun1_lo16, PARAM.fun1_hi16,
               PARAM.jtb1_lo16, PARAM.jtb1_hi16}


def GetStackOffset(stk: ir.Stk, num: ir.Const) -> int:
    assert isinstance(num, ir.Const)
    assert isinstance(stk, ir.Stk)
    assert stk.slot is not None
    return stk.slot + num.value


def _ExtractTmplArgOp(ins: ir.Ins, arg: PARAM, ctx: regs.EmitContext) -> int:
    if isinstance(arg, arm.SHIFT):
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
        return -num.value & 0xffffffff
    elif arg in {PARAM.num0_not, PARAM.num1_not, PARAM.num2_not}:
        n = arg.value - PARAM.num0_not.value
        num = ins.operands[n]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        return ~num.value & 0xffffffff
    elif arg in _RELOC_ARGS:
        return 0
    elif arg is PARAM.num1_lo16:
        num = ins.operands[1]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        return num.value & 0xffff
    elif arg is PARAM.num1_hi16:
        num = ins.operands[1]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        return (num.value >> 16) & 0xffff
    elif arg is PARAM.scratch_flt:
        assert ctx.scratch_cpu_reg.kind is not regs.A32RegKind.GPR
        return ctx.scratch_cpu_reg.no
    elif arg is PARAM.scratch_gpr:
        assert ctx.scratch_cpu_reg.kind is regs.A32RegKind.GPR
        return ctx.scratch_cpu_reg.no
    elif arg is PARAM.stm_regmask:
        return ctx.stm_regs
    elif arg is PARAM.ldm_regmask:
        return ctx.ldm_regs
    elif arg is PARAM.vldm_start:
        start, _ = regs.ArmGetFltRegRanges(ctx.vldm_regs)
        return start.no
    elif arg is PARAM.vldm_count:
        _, count = regs.ArmGetFltRegRanges(ctx.vldm_regs)
        return count
    elif arg is PARAM.vstm_start:
        start, _ = regs.ArmGetFltRegRanges(ctx.vstm_regs)
        return start.no
    elif arg is PARAM.vstm_count:
        _, count = regs.ArmGetFltRegRanges(ctx.vstm_regs)
        return count
    elif arg is PARAM.stk0_offset1:
        return GetStackOffset(ins.operands[0], ins.operands[1])
    elif arg is PARAM.stk1_offset2:
        return GetStackOffset(ins.operands[1], ins.operands[2])
    elif arg is PARAM.stk1_offset2_lo:
        return GetStackOffset(ins.operands[1], ins.operands[2]) & 0xffff
    elif arg is PARAM.stk1_offset2_hi:
        return (GetStackOffset(ins.operands[1], ins.operands[2]) >> 16) & 0xffff
    else:
        assert False, f"unknown ARG {repr(arg)}"


def _TranslateTmplOpInt(ins: ir.Ins, op: Any, ctx: regs.EmitContext) -> int:
    if type(op) == int:
        return op
    elif isinstance(op, arm.PRED):
        return op.value
    elif isinstance(op, arm.REG):
        return op.value
    elif isinstance(op, arm.SHIFT):
        return op.value
    elif isinstance(op, PARAM):
        return _ExtractTmplArgOp(ins, op, ctx)
    else:
        assert False, f"unknown param {repr(op)}"


_RAW_ENOCDER : Dict [arm.OK, Any] = {
    arm.OK.IMM_0_7_8_11: arm.EncodeRotateImm,
    arm.OK.SIMM_0_23: lambda x: x & 0xffffff,
    arm.OK.IMM_10_11_TIMES_8: lambda x: x // 8,
    arm.OK.IMM_0_7_TIMES_4: lambda x: x // 4,
}


def _HandleReloc(armins: arm.Ins, pos: int, ins: ir.Ins, op: PARAM):
    assert armins.reloc_kind == 0
    armins.reloc_pos = pos

    def movt_or_movw_rel(is_low):
        return enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC if is_low else enum_tab.RELOC_TYPE_ARM.MOVT_ABS

    if op in {PARAM.mem1_num2_lo16, PARAM.mem1_num2_hi16}:
        armins.reloc_kind = movt_or_movw_rel(op is PARAM.mem1_num2_lo16)
        mem = ins.operands[1]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        armins.reloc_symbol = mem.name
        num = ins.operands[2]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert armins.operands[pos] == 0
        armins.operands[pos] = num.value
    elif op in {PARAM.jtb1_lo16, PARAM.jtb1_hi16}:
        armins.reloc_kind = movt_or_movw_rel(op is PARAM.jtb1_lo16)
        armins.is_local_sym = True
        jtb = ins.operands[1]
        assert isinstance(jtb, ir.Jtb), f"{ins} {jtb}"
        armins.reloc_symbol = jtb.name
    elif op in {PARAM.fun1_lo16, PARAM.fun1_hi16}:
        armins.reloc_kind = movt_or_movw_rel(op is PARAM.fun1_lo16)
        fun = ins.operands[1]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        armins.reloc_symbol = fun.name
    elif op is PARAM.bbl0:
        armins.reloc_kind = enum_tab.RELOC_TYPE_ARM.JUMP24
        armins.is_local_sym = True
        bbl = ins.operands[0]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        armins.reloc_symbol = bbl.name
    elif op is PARAM.bbl2:
        armins.reloc_kind = enum_tab.RELOC_TYPE_ARM.JUMP24
        armins.is_local_sym = True
        bbl = ins.operands[2]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        armins.reloc_symbol = bbl.name
    elif op is PARAM.fun0:
        armins.reloc_kind = enum_tab.RELOC_TYPE_ARM.CALL
        fun = ins.operands[0]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        armins.reloc_symbol = fun.name
    else:
        assert False


class InsTmpl:
    """Represents a template for an A32 instructions

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.
    """

    def __init__(self, opcode_name: str, args: List[Any], pred=arm.PRED.al):
        opcode = arm.Opcode.name_to_opcode[opcode_name]
        assert len(args) + opcode.HasPred() == len(
            opcode.fields), f"{opcode_name} operand len mismatch {args} {opcode.fields}"
        if pred is not None:
            args = [pred] + args
        for op in args:
            assert isinstance(op, (int, PARAM, arm.PRED, arm.REG, arm.SHIFT)), (
                f"unknown op {op} for {opcode.name} {args}")
        self.opcode = opcode
        self.args = args

    def MakeInsFromTmpl(self, ins: Optional[ir.Ins], ctx: regs.EmitContext) -> arm.Ins:
        out = arm.Ins(self.opcode)
        for n, arg in enumerate(self.args):
            val = _TranslateTmplOpInt(ins, arg, ctx)
            enc = _RAW_ENOCDER.get(self.opcode.fields[n])
            if enc:
                val = enc(val)
            assert val is not None
            out.operands.append(val)
            # note: this may alter the value we just appended
            if arg in _RELOC_ARGS:
                _HandleReloc(out, n, ins, arg)
        return out


_ALLOWED_OPERAND_TYPES_REG = {
    o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32,
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


def EmitFunEpilog(ctx: regs.EmitContext) -> List[InsTmpl]:
    out = []
    stk_size = ctx.stk_size
    while stk_size > 0:
        high_byte = _HighByte(stk_size)
        out.append(InsTmpl("add_imm", [arm.REG.sp, arm.REG.sp, high_byte]))
        stk_size -= high_byte
    if ctx.vldm_regs > 0:
        out.append(
            InsTmpl("vldmia_s_update", [PARAM.vldm_start, PARAM.vldm_count, arm.REG.sp]))
    if ctx.ldm_regs > 0:
        out.append(InsTmpl("ldmia_update", [PARAM.ldm_regmask, arm.REG.sp]))
    if (regs.A32RegToAllocMask(regs.PC_REG) & ctx.ldm_regs) == 0:
        out.append(InsTmpl("bx", [arm.REG.lr]))
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
    # TODO: make sure stack is 8 byte aligned
    if ctx.stm_regs:
        out.append(InsTmpl("stmdb_update", [arm.REG.sp, PARAM.stm_regmask]))
    if ctx.vstm_regs > 0:
        out.append(InsTmpl(
            "vstmdb_s_update",
            [arm.REG.sp, PARAM.vstm_start, PARAM.vstm_count]))
    stk_size = ctx.stk_size
    while stk_size > 0:
        high_byte = _HighByte(stk_size)
        out.append(InsTmpl("sub_imm", [arm.REG.sp, arm.REG.sp, high_byte]))
        stk_size -= high_byte
    return out


# not this must have more bits set than MAX_OPERANDS
MATCH_IMPOSSIBLE = 255


class Pattern:
    Table: Dict[o.Opcode, List["Pattern"]] = collections.defaultdict(list)

    def __init__(self, opcode: o.Opcode, type_constraints: List[o.DK],
                 imm_constraints: List[IMM_KIND],
                 emit: List[InsTmpl]):
        # the template, usually contains ArmIns except for the nop1 pattern
        self.emit = emit
        # how to fill the template params
        assert len(type_constraints) == len(
            opcode.operand_kinds), f"{opcode.name} {type_constraints} {opcode.operand_kinds}"
        for type_constr, imm_constr, kind in zip(type_constraints, imm_constraints,
                                                 opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr is IMM_KIND.invalid
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert imm_constr != IMM_KIND.invalid
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
            else:
                assert type_constr is o.DK.INVALID
                assert imm_constr is IMM_KIND.invalid, f"bad pattern for {opcode}"

        self.type_constraints = type_constraints
        self.imm_constraints = imm_constraints
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
        """Returns bit positions that hsve a mismatch

        assumes that MatchesTypeConstraints return true"""
        out = 0
        for pos, (imm_constr, op) in enumerate(zip(self.imm_constraints, ins.operands)):
            if isinstance(op, ir.Const):
                if imm_constr is IMM_KIND.invalid:
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
                    out |= 1 << pos
            elif isinstance(op, ir.Reg):
                if imm_constr is not IMM_KIND.invalid:
                    return MATCH_IMPOSSIBLE
        return out

    def __str__(self):
        return f"[PATTERN {self.type_constraints} {self.imm_constraints}]"

    def __repr__(self):
        return f"[PATTERN {self.type_constraints} {self.imm_constraints}]"


OPCODES_REQUIRING_SPECIAL_HANDLING = {
    o.NOP1,  # pseudo instruction
    o.RET,  # handled via special epilog code
}

_CMP_SIGNED = {o.BLT: arm.PRED.lt, o.BLE: arm.PRED.le}
_CMP_UNSIGNED = {o.BLT: arm.PRED.cc, o.BLE: arm.PRED.ls}
_CMP_SIGNED_INV = {o.BLT: arm.PRED.gt, o.BLE: arm.PRED.ge}
_CMP_UNSIGNED_INV = {o.BLT: arm.PRED.hi, o.BLE: arm.PRED.cs}

_NO_IMM0 = []
_NO_IMM1 = [IMM_KIND.invalid]
_NO_IMM2 = [IMM_KIND.invalid] * 2
_NO_IMM3 = [IMM_KIND.invalid] * 3
_NO_IMM4 = [IMM_KIND.invalid] * 4


def InitCondBra():
    # TODO: cover the floating points ones
    for kind in [o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32]:
        for opc, cond in [(o.BEQ, arm.PRED.eq), (o.BNE, arm.PRED.ne)]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints, _NO_IMM3,
                    [InsTmpl("cmp_regimm", [PARAM.reg0,PARAM.reg1, arm.SHIFT.lsl, 0]),
            InsTmpl("b", [PARAM.bbl2], pred=cond)])
            imm_constraints = [IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted,
                               IMM_KIND.invalid]
            Pattern(opc, type_constraints, imm_constraints,
                    [InsTmpl("cmp_imm", [PARAM.reg0, PARAM.num1]),
                     InsTmpl("b", [PARAM.bbl2], pred=cond)])

    for kind in [o.DK.U32, o.DK.A32, o.DK.C32, o.DK.S32]:
        xlate = _CMP_SIGNED if kind == o.DK.S32 else _CMP_UNSIGNED
        xlate_inv = _CMP_SIGNED_INV if kind == o.DK.S32 else _CMP_UNSIGNED_INV

        for opc in [o.BLT, o.BLE]:
            type_constraints = [kind, kind, o.DK.INVALID]
            Pattern(opc, type_constraints, _NO_IMM3,
                    [InsTmpl("cmp_regimm", [PARAM.reg0, PARAM.reg1, arm.SHIFT.lsl, 0]),
                     InsTmpl("b", [PARAM.bbl2], pred=xlate[opc])])
            imm_constraints = [IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted,
                               IMM_KIND.invalid]
            Pattern(opc, type_constraints, imm_constraints,
                    [InsTmpl("cmp_imm", [PARAM.reg0, PARAM.num1]),
                     InsTmpl("b", [PARAM.bbl2], pred=xlate[opc])])
            imm_constraints = [IMM_KIND.pos_8_bits_shifted, IMM_KIND.invalid,
                               IMM_KIND.invalid]
            Pattern(opc, type_constraints, imm_constraints,
                    [InsTmpl("cmp_imm", [PARAM.reg1, PARAM.num0]),
                     InsTmpl("b", [PARAM.bbl2], pred=xlate_inv[opc])])

    # * we do not have a story for the unordered case
    # * comparison against zero should be special cased
    for kind, cmp in [(o.DK.F32, "vcmp_f32"), (o.DK.F64, "vcmp_f64")]:
        for opc, pred in [(o.BEQ, arm.PRED.eq), (o.BNE, arm.PRED.ne),
                          (o.BLT, arm.PRED.mi), (o.BLE, arm.PRED.ls)]:
            Pattern(opc, [kind, kind, o.DK.INVALID], _NO_IMM3,
                    [InsTmpl(cmp, [PARAM.reg0, PARAM.reg1]),
                     InsTmpl("vmrs_APSR_nzcv_fpscr", []),
                     InsTmpl("b", [PARAM.bbl2], pred=pred)])


def InsTmplMove(dst, src, kind, pred=arm.PRED.al):
    assert dst is PARAM.reg0
    if src in {PARAM.reg1, PARAM.reg2, PARAM.reg3, PARAM.reg4}:
        return InsTmpl("mov_regimm", [dst, src, arm.SHIFT.lsl, 0], pred)

    assert src in {PARAM.num1, PARAM.num2, PARAM.num3, PARAM.num4, PARAM.num1_not}
    if kind is IMM_KIND.pos_16_bits:
        return InsTmpl("movw", [dst, src], pred)
    elif kind is IMM_KIND.pos_8_bits_shifted:
        return InsTmpl("mov_imm", [dst, src], pred)
    elif kind is IMM_KIND.not_8_bits_shifted:
        return InsTmpl("mvn_imm", [dst, src], pred)
    else:
        assert False, f"unsupported mov combination {kind.name}"


def InitCmp():
    IMM_1_2 = [(IMM_KIND.invalid, IMM_KIND.invalid), (IMM_KIND.invalid, IMM_KIND.pos_16_bits),
               (IMM_KIND.pos_16_bits, IMM_KIND.invalid),
               (IMM_KIND.pos_16_bits, IMM_KIND.pos_16_bits)]
    # TODO: cover the floating points ones
    for kind in [o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32]:
        cond, inv_cond = arm.PRED.eq, arm.PRED.ne
        for imm1, imm2 in IMM_1_2:
            Pattern(o.CMPEQ, [kind] * 5,
                    [IMM_KIND.invalid, imm1, imm2, IMM_KIND.invalid, IMM_KIND.invalid],
                    [InsTmpl("cmp_regimm", [PARAM.reg3, PARAM.reg4, arm.SHIFT.lsl, 0]),
                     InsTmplMove(PARAM.reg0, PARAM.reg1 if imm1 == IMM_KIND.invalid else PARAM.num1,
                                 imm1, cond),
                     InsTmplMove(PARAM.reg0, PARAM.reg2 if imm2 == IMM_KIND.invalid else PARAM.num2,
                                 imm2, inv_cond)])
            Pattern(o.CMPEQ, [kind] * 5,
                    [IMM_KIND.invalid, imm1, imm2, IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted],
                    [InsTmpl("cmp_imm", [PARAM.reg3, PARAM.num4]),
                     InsTmplMove(PARAM.reg0, PARAM.reg1 if imm1 == IMM_KIND.invalid else PARAM.num1,
                                 imm1, cond),
                     InsTmplMove(PARAM.reg0, PARAM.reg2 if imm2 == IMM_KIND.invalid else PARAM.num2,
                                 imm2, inv_cond)])

    for kind in [o.DK.U32, o.DK.A32, o.DK.S32]:
        cond, inv_cond = (arm.PRED.lt, arm.PRED.ge) if kind == o.DK.S32 else (
            arm.PRED.cc, arm.PRED.cs)
        for imm1, imm2 in IMM_1_2:
            Pattern(o.CMPLT, [kind] * 5,
                    [IMM_KIND.invalid, imm1, imm2, IMM_KIND.invalid, IMM_KIND.invalid],
                    [InsTmpl("cmp_regimm", [PARAM.reg3, PARAM.reg4, arm.SHIFT.lsl, 0]),
                     InsTmplMove(PARAM.reg0, PARAM.reg1 if imm1 == IMM_KIND.invalid else PARAM.num1,
                                 imm1, cond),
                     InsTmplMove(PARAM.reg0, PARAM.reg2 if imm2 == IMM_KIND.invalid else PARAM.num2,
                                 imm2, inv_cond)])
            Pattern(o.CMPLT, [kind] * 5,
                    [IMM_KIND.invalid, imm1, imm2, IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted],
                    [InsTmpl("cmp_imm", [PARAM.reg3, PARAM.num4]),
                     InsTmplMove(PARAM.reg0, PARAM.reg1 if imm1 == IMM_KIND.invalid else PARAM.num1,
                                 imm1, cond),
                     InsTmplMove(PARAM.reg0, PARAM.reg2 if imm2 == IMM_KIND.invalid else PARAM.num2,
                                 imm2, inv_cond)])

    for kind in [o.DK.U32, o.DK.A32, o.DK.S32]:
        cond, inv_cond = (arm.PRED.gt, arm.PRED.le) if kind == o.DK.S32 else (
            arm.PRED.hi, arm.PRED.ls)
        for imm1, imm2 in IMM_1_2:
            Pattern(o.CMPLT, [kind] * 5,
                    [IMM_KIND.invalid, imm1, imm2, IMM_KIND.pos_8_bits_shifted, IMM_KIND.invalid],
                    [InsTmpl("cmp_imm", [PARAM.reg4, PARAM.num3]),
                     InsTmplMove(PARAM.reg0, PARAM.reg1 if imm1 == IMM_KIND.invalid else PARAM.num1,
                                 imm1, cond),
                     InsTmplMove(PARAM.reg0, PARAM.reg2 if imm2 == IMM_KIND.invalid else PARAM.num2,
                                 imm2, inv_cond)])


def InitAlu():
    for kind1 in [o.DK.U32, o.DK.S32]:
        for node, opc in [(o.AND, "and"), (o.XOR, "eor"),
                          (o.ADD, "add"), (o.OR, "orr"), (o.SUB, "sub")]:
            Pattern(node, [kind1] * 3, _NO_IMM3,
                    [InsTmpl(opc + "_regimm",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, arm.SHIFT.lsl, 0])])

        imm_constraints = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted]
        for node, opc in [(o.AND, "and"), (o.XOR, "eor"),
                          (o.ADD, "add"), (o.OR, "orr"), (o.SUB, "sub")]:
            Pattern(node, [kind1] * 3, imm_constraints,
                    [InsTmpl(opc + "_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2])])

        imm_constraints = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.not_8_bits_shifted]
        for node, opc in [(o.AND, "bic")]:
            Pattern(node, [kind1] * 3, imm_constraints,
                    [InsTmpl(opc + "_imm", [PARAM.reg0, PARAM.reg1, PARAM.num2_not])])

        imm_constraints = [IMM_KIND.invalid, IMM_KIND.pos_8_bits_shifted, IMM_KIND.invalid]
        for node, opc in [(o.SUB, "rsb")]:
            Pattern(node, [kind1] * 3, imm_constraints,
                    [InsTmpl(opc + "_imm", [PARAM.reg0, PARAM.reg2, PARAM.num1])])

    for kind1 in [o.DK.U32, o.DK.S32]:
        Pattern(o.MUL, [kind1] * 3, _NO_IMM3,
                [InsTmpl("mul", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

    for opc, kind1, shift_dir in [(o.SHL, o.DK.U32, arm.SHIFT.lsl),
                                  (o.SHL, o.DK.S32, arm.SHIFT.lsl),
                                  (o.SHR, o.DK.U32, arm.SHIFT.lsr),
                                  (o.SHR, o.DK.S32, arm.SHIFT.asr)]:
        imm_constraints = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_5_bits]
        Pattern(opc, [kind1] * 3, _NO_IMM3,
                [InsTmpl("mov_regreg",
                         [PARAM.reg0, PARAM.reg1, shift_dir, PARAM.reg2])])
        Pattern(opc, [kind1] * 3, imm_constraints,
                [InsTmpl("mov_regimm",
                         [PARAM.reg0, PARAM.reg1, shift_dir, PARAM.num2])])

    Pattern(o.DIV, [o.DK.U32] * 3, _NO_IMM3,
            [InsTmpl("udiv", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
    Pattern(o.DIV, [o.DK.S32] * 3, _NO_IMM3,
            [InsTmpl("sdiv", [PARAM.reg0, PARAM.reg1, PARAM.reg2])])


def InitLoad():
    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_12_bits]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.neg_12_bits]
    for kind1, opc in [(o.DK.U32, "ldr"), (o.DK.S32, "ldr"), (o.DK.A32, "ldr"),
                       (o.DK.C32, "ldr"), (o.DK.U8, "ldrb")]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.LD, [kind1, o.DK.A32, kind2], _NO_IMM3,
                    [InsTmpl(opc + "_reg_add",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2, arm.SHIFT.lsl,
                              0])])
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_pos,
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, PARAM.reg1, PARAM.num2])])
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_neg,
                    [InsTmpl(opc + "_imm_sub",
                             [PARAM.reg0, PARAM.reg1, PARAM.num2_neg])])
            # note: the second and third op are combined in the generated code
            Pattern(o.LD_STK, [kind1, o.DK.INVALID, kind2],
                    [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_12_bits],
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, arm.REG.sp, PARAM.stk1_offset2])])

    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_8_bits_times_4]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.neg_8_bits_times_4]
    for kind1, opc in [(o.DK.F32, "vldr_f32_"), (o.DK.F64, "vldr_f64_")]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_pos,
                    [InsTmpl(opc + "add", [PARAM.reg0, PARAM.reg1, PARAM.num2])])
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_neg,
                    [InsTmpl(opc + "sub", [PARAM.reg0, PARAM.reg1, PARAM.num2_neg])])
            # note: the second and third op are combined in the generated code
            Pattern(o.LD_STK, [kind1, o.DK.INVALID, kind2],
                    [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_8_bits_times_4],
                    [InsTmpl(opc + "add", [PARAM.reg0, arm.REG.sp, PARAM.stk1_offset2])])

    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_8_bits]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.neg_8_bits]
    for kind1, opc in [(o.DK.S8, "ldrsb"), (o.DK.U16, "ldrh"), (o.DK.S16, "ldrsh")]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.LD, [kind1, o.DK.A32, kind2], _NO_IMM3,
                    [InsTmpl(opc + "_reg_add",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_neg,
                    [InsTmpl(opc + "_imm_sub",
                             [PARAM.reg0, PARAM.reg1, PARAM.num2_neg])])
            Pattern(o.LD, [kind1, o.DK.A32, kind2], imm_constraints_pos,
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, PARAM.reg1, PARAM.num2])])
            # note: the second and third op are combined in the generated code
            Pattern(o.LD_STK, [kind1, o.DK.INVALID, kind2],
                    [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_8_bits],
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, arm.REG.sp, PARAM.stk1_offset2])])


def InitStore():
    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.pos_12_bits, IMM_KIND.invalid]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.neg_12_bits, IMM_KIND.invalid]
    for kind2, opc in [(o.DK.U32, "str"), (o.DK.S32, "str"), (o.DK.A32, "str"),
                       (o.DK.C32, "str"), (o.DK.U8, "strb"), (o.DK.S8, "strb")]:
        for kind1 in [o.DK.U32, o.DK.S32]:
            Pattern(o.ST, [o.DK.A32, kind1, kind2], _NO_IMM3,
                    [InsTmpl(opc + "_reg_add",
                             [PARAM.reg0, PARAM.reg1, arm.SHIFT.lsl, 0,
                              PARAM.reg2])])
            Pattern(o.ST, [o.DK.A32, kind1, kind2], imm_constraints_pos,
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, PARAM.num1, PARAM.reg2])])
            Pattern(o.ST, [o.DK.A32, kind1, kind2], imm_constraints_neg,
                    [InsTmpl(opc + "_imm_sub",
                             [PARAM.reg0, PARAM.num1_neg, PARAM.reg2])])
            # note: the second and third op are combined in the generated code
            Pattern(o.ST_STK, [o.DK.INVALID, kind1, kind2],
                    [IMM_KIND.invalid, IMM_KIND.pos_stk_combo_12_bits, IMM_KIND.invalid],
                    [InsTmpl(opc + "_imm_add",
                             [arm.REG.sp, PARAM.stk0_offset1, PARAM.reg2])])

    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.pos_8_bits_times_4, IMM_KIND.invalid]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.neg_8_bits_times_4, IMM_KIND.invalid]
    for kind1, opc in [(o.DK.F32, "vstr_f32_"), (o.DK.F64, "vstr_f64_")]:
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.ST, [o.DK.A32, kind2, kind1], imm_constraints_pos,
                    [InsTmpl(opc + "add", [PARAM.reg0, PARAM.num1, PARAM.reg2])])
            Pattern(o.ST, [o.DK.A32, kind2, kind1], imm_constraints_neg,
                    [InsTmpl(opc + "sub", [PARAM.reg0, PARAM.num1_neg, PARAM.reg2])])
            # note: the second and third op are combined in the generated code
            Pattern(o.ST_STK, [o.DK.INVALID, kind2, kind1],
                    [IMM_KIND.invalid, IMM_KIND.pos_stk_combo_8_bits_times_4, IMM_KIND.invalid],
                    [InsTmpl(opc + "add", [arm.REG.sp, PARAM.stk0_offset1, PARAM.reg2])])

    imm_constraints_pos = [IMM_KIND.invalid, IMM_KIND.pos_8_bits, IMM_KIND.invalid]
    imm_constraints_neg = [IMM_KIND.invalid, IMM_KIND.neg_8_bits, IMM_KIND.invalid]
    for kind2, opc in [(o.DK.U16, "strh"), (o.DK.S16, "strh")]:
        for kind1 in [o.DK.U32, o.DK.S32]:
            Pattern(o.ST, [o.DK.A32, kind1, kind2], _NO_IMM3,
                    [InsTmpl(opc + "_reg_add",
                             [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
            Pattern(o.ST, [o.DK.A32, kind1, kind2], imm_constraints_pos,
                    [InsTmpl(opc + "_imm_add",
                             [PARAM.reg0, PARAM.num1, PARAM.reg2])])
            Pattern(o.ST, [o.DK.A32, kind1, kind2], imm_constraints_neg,
                    [InsTmpl(opc + "_imm_sub",
                             [PARAM.reg0, PARAM.num1_neg, PARAM.reg2])])
            # note: the second and third op are combined in the generated code
            Pattern(o.ST_STK, [o.DK.INVALID, kind1, kind2],
                    [IMM_KIND.invalid, IMM_KIND.pos_stk_combo_8_bits, IMM_KIND.invalid],
                    [InsTmpl(opc + "_imm_add",
                             [arm.REG.sp, PARAM.stk0_offset1, PARAM.reg2])])


def InitLea():
    Pattern(o.LEA_FUN, [o.DK.C32, o.DK.INVALID], _NO_IMM2,
            [InsTmpl("movw", [PARAM.reg0, PARAM.fun1_lo16]),
             InsTmpl("movt", [PARAM.reg0, PARAM.fun1_hi16])])

    for kind1 in [o.DK.U32, o.DK.S32]:
        Pattern(o.LEA, [o.DK.A32, o.DK.A32, kind1], _NO_IMM3,
                [InsTmpl("add_regimm",
                         [PARAM.reg0, PARAM.reg1, PARAM.reg2, arm.SHIFT.lsl, 0])])
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
                [InsTmpl("add_imm", [PARAM.reg0, arm.REG.sp, PARAM.stk1_offset2])])
        Pattern(o.LEA_STK, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.pos_stk_combo_16_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.stk1_offset2]),
                 InsTmpl("add_regimm", [PARAM.reg0, arm.REG.sp, PARAM.reg0, arm.SHIFT.lsl, 0])])
        Pattern(o.LEA_STK, [o.DK.A32, o.DK.INVALID, kind1],
                [IMM_KIND.invalid, IMM_KIND.invalid, IMM_KIND.any_32_bits],
                [InsTmpl("movw", [PARAM.reg0, PARAM.stk1_offset2_lo]),
                 InsTmpl("movt", [PARAM.reg0, PARAM.stk1_offset2_hi]),
                 InsTmpl("add_regimm", [PARAM.reg0, arm.REG.sp, PARAM.reg0, arm.SHIFT.lsl, 0])])


# Note, moves are our last resort and MUST support ALL possible immediates
def InitMove():
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
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        # truncation or sign change from 32bit: nothing to be done here
        for kind2 in [o.DK.U32, o.DK.S32]:
            Pattern(o.CONV, [kind1, kind2], _NO_IMM2,
                    [InsTmplMove(PARAM.reg0, PARAM.reg1, kind2)])
    # truncation or sign change from 16bit: nothing to be done here
    for kind1 in [o.DK.U16, o.DK.S16, o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U16, o.DK.S16]:
            Pattern(o.CONV, [kind1, kind2], _NO_IMM2,
                    [InsTmplMove(PARAM.reg0, PARAM.reg1, kind2)])
    # sign change from 8it: nothing to be done here
    for kind1 in [o.DK.U8, o.DK.S8]:
        for kind2 in [o.DK.U8, o.DK.S8]:
            Pattern(o.CONV, [kind1, kind2], _NO_IMM2,
                    [InsTmplMove(PARAM.reg0, PARAM.reg1, kind2)])

    Pattern(o.CONV, [o.DK.U32, o.DK.U8], _NO_IMM2,
            [InsTmpl("uxtb", [PARAM.reg0, PARAM.reg1, 0])])

    Pattern(o.CONV, [o.DK.S32, o.DK.S8], _NO_IMM2,
            [InsTmpl("sxtb", [PARAM.reg0, PARAM.reg1, 0])])

    Pattern(o.CONV, [o.DK.U32, o.DK.U16], _NO_IMM2,
            [InsTmpl("uxth", [PARAM.reg0, PARAM.reg1, 0])])

    Pattern(o.CONV, [o.DK.S32, o.DK.S16], _NO_IMM2,
            [InsTmpl("sxth", [PARAM.reg0, PARAM.reg1, 0])])

    # bitcast between 32bit regs: nothing to be done here
    for kind1 in [o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32]:
        for kind2 in [o.DK.U32, o.DK.S32, o.DK.A32, o.DK.C32]:
            Pattern(o.BITCAST, [kind1, kind2], _NO_IMM2,
                    [InsTmplMove(PARAM.reg0, PARAM.reg1, kind2)])


def InitMiscBra():
    Pattern(o.BRA, [o.DK.INVALID], _NO_IMM1,
            [InsTmpl("b", [PARAM.bbl0])])

    Pattern(o.BSR, [o.DK.INVALID], _NO_IMM1,
            [InsTmpl("bl", [PARAM.fun0])])

    Pattern(o.JSR, [o.DK.C32, o.DK.INVALID], _NO_IMM2,
            [InsTmpl("blx_reg", [PARAM.reg0])])

    Pattern(o.TRAP, [], [], [InsTmpl("ud2", [])])

    Pattern(o.SYSCALL, [o.DK.INVALID, o.DK.U32], [IMM_KIND.invalid, IMM_KIND.pos_16_bits],
            [InsTmpl("str_imm_sub_pre", [arm.REG.sp, 4, arm.REG.r7]),  # push r7 on stack
             InsTmpl("movw", [arm.REG.r7, PARAM.num1]),
             InsTmpl("svc", [0]),
             InsTmpl("ldr_imm_add_post",
                     [arm.REG.r7, arm.REG.sp, 4])])  # pop r7 from stack

    # Note: a dummy "nop1 %scratch_gpr" either immediately before
    # or after will ensure that %scratch_gpr is available
    Pattern(o.SWITCH, [o.DK.U32, o.DK.INVALID], _NO_IMM2,
            [InsTmpl("movw", [PARAM.scratch_gpr, PARAM.jtb1_lo16]),
             InsTmpl("movt", [PARAM.scratch_gpr, PARAM.jtb1_hi16]),
             InsTmpl("ldr_reg_add",
                     [arm.REG.pc, PARAM.scratch_gpr, PARAM.reg0, arm.SHIFT.lsl,
                      2]),
             ])


def InitVFP():
    for kind, suffix in [(o.DK.F32, "_f32"), (o.DK.F64, "_f64")]:
        Pattern(o.MOV, [kind] * 2, _NO_IMM2,
                [InsTmpl("vmov" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.TRUNC, [kind] * 2, _NO_IMM2,
                [InsTmpl("vmov" + suffix, [PARAM.reg0, PARAM.reg1])])
        Pattern(o.ADD, [kind] * 3, _NO_IMM3,
                [InsTmpl("vadd" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.SUB, [kind] * 3, _NO_IMM3,
                [InsTmpl("vsub" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.MUL, [kind] * 3, _NO_IMM3,
                [InsTmpl("vmul" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])
        Pattern(o.DIV, [kind] * 3, _NO_IMM3,
                [InsTmpl("vdiv" + suffix, [PARAM.reg0, PARAM.reg1, PARAM.reg2])])

        # Note: a dummy "nop1 %scratch_flt" either immediately before
        # or after will ensure that %scratch_flt is available
        # not even for a F64 we want a F32 scratch
        Pattern(o.CONV, [o.DK.S32, kind], _NO_IMM2,
                [InsTmpl("vcvt_s32" + suffix, [PARAM.scratch_flt, PARAM.reg1]),
                 InsTmpl("vmov_stoa", [PARAM.reg0, PARAM.scratch_flt])])
        # Note: a dummy "nop1 %scratch_flt" either immediately before
        # or after will ensure that %scratch_flt is available
        Pattern(o.CONV, [o.DK.U32, kind], _NO_IMM2,
                [InsTmpl("vcvt_u32" + suffix, [PARAM.scratch_flt, PARAM.reg1]),
                 InsTmpl("vmov_stoa", [PARAM.reg0, PARAM.scratch_flt])])

    Pattern(o.CONV, [o.DK.F32, o.DK.S32], _NO_IMM2,
            [InsTmpl("vmov_atos", [PARAM.reg0, PARAM.reg1]),
             InsTmpl(f"vcvt_f32_s32", [PARAM.reg0, PARAM.reg0])])

    Pattern(o.CONV, [o.DK.F32, o.DK.U32], _NO_IMM2,
            [InsTmpl("vmov_atos", [PARAM.reg0, PARAM.reg1]),
             InsTmpl(f"vcvt_f32_u32", [PARAM.reg0, PARAM.reg0])])

    # note, we could use a hack where d[x] is mapped to s[x*2] for scratch
    # but this would not work for d16-d31 should want to support them
    Pattern(o.CONV, [o.DK.F64, o.DK.S32], _NO_IMM2,
            [InsTmpl("vmov_atos", [PARAM.scratch_flt, PARAM.reg1]),
             InsTmpl(f"vcvt_f64_s32", [PARAM.reg0, PARAM.scratch_flt])])

    Pattern(o.CONV, [o.DK.F64, o.DK.U32], _NO_IMM2,
            [InsTmpl("vmov_atos", [PARAM.scratch_flt, PARAM.reg1]),
             InsTmpl(f"vcvt_f64_u32", [PARAM.reg0, PARAM.scratch_flt])])


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
        elif isinstance(op, arm.PRED):
            s = f"+PRED::{op.name}"
        elif isinstance(op, arm.REG):
            s = f"+REG::{op.name}"
        elif isinstance(op, arm.SHIFT):
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
                    f"    a32::OPC::{tmpl.opcode.NameForEnum()}, 0x{mask:x} }},  // {opcode.name} [{num_ins}]",
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

    print("}  // namspace", file=fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(IMM_KIND), "IMM_KIND", fout)
    cgen.RenderEnumToStringFun("IMM_KIND", fout)


def _DumpCodeSelTable():
    for i in range(256):
        patterns = Pattern.Table.get(i)
        if patterns is None: continue
        opcode = o.Opcode.TableByNo[i]
        print(f"{opcode.name} [{' '.join([k.name for k in opcode.operand_kinds])}]")
        for pat in patterns:
            print(f"  [{' '.join([o.name if o else '*' for o in pat.constraints])}]")
            for opcode, operands in pat.emit:
                ops = [str(x) if isinstance(x, int) else x.name for x in operands]
                print(f"    {opcode.name} [{' '.join(ops)}]")


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
