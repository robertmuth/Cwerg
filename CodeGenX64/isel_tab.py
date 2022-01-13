#!/usr/bin/python3

"""Code Generation (Instruction Selection) for x86-64
"""

import collections
import enum
from typing import List, Dict, Any, Optional

from Base import ir
from Base import opcode_tab as o
from CodeGenX64 import regs
from CpuX64 import opcode_tab as x64
from Elf import enum_tab


@enum.unique
class C(enum.Enum):
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
    # order important
    REG_RAX = 13
    REG_RCX = 14
    REG_RDX = 15


class F(enum.Enum):
    """Fixed params"""
    NO_INDEX = 1
    NO_BASE = 2
    RIP = 3
    SCALE1 = 4
    SCALE2 = 5
    SCALE4 = 6
    SCALE8 = 7
    RAX = 10
    RCX = 11
    RDX = 12
    RBX = 13
    RSP = 14
    RBP = 15
    RSI = 16
    RDI = 17
    R8 = 18
    R9 = 19
    R10 = 20
    R11 = 21
    R12 = 22
    R13 = 23
    R14 = 24
    R15 = 25
    XMM0 = 26
    XMM1 = 27
    XMM2 = 28
    XMM3 = 29
    XMM4 = 30
    XMM5 = 31
    XMM6 = 32
    XMM7 = 33
    XMM8 = 34
    XMM9 = 35
    XMM10 = 36
    XMM11 = 37
    XMM12 = 38
    XMM13 = 39
    XMM14 = 40
    XMM15 = 41


_F_TO_INT = {
    F.NO_INDEX: 4,
    F.NO_BASE: 5,
    F.RIP: 0,
    #
    F.SCALE1: 0,
    F.SCALE2: 1,
    F.SCALE4: 2,
    F.SCALE8: 3,
    #
    F.RAX: 0,
    F.RCX: 1,
    F.RDX: 2,
    F.RBX: 3,
    F.RSP: 4,
    F.RBP: 5,
    F.RSI: 6,
    F.RDI: 7,
    F.R8: 8,
    F.R9: 9,
    F.R10: 10,
    F.R11: 11,
    F.R12: 12,
    F.R13: 13,
    F.R14: 14,
    F.R15: 15,
    #
    F.XMM0: 0,
    F.XMM1: 1,
    F.XMM2: 2,
    F.XMM3: 3,
    F.XMM4: 4,
    F.XMM5: 5,
    F.XMM6: 6,
    F.XMM7: 7,
    F.XMM8: 8,
    F.XMM9: 9,
    F.XMM10: 10,
    F.XMM11: 11,
    F.XMM12: 12,
    F.XMM13: 13,
    F.XMM14: 14,
    F.XMM15: 15,
}

F_REGS = {F.RAX, F.RCX, F.RDX, F.RBX, F.RSP, F.RBP, F.RSI, F.RDI,
          F.R8, F.R9, F.R10, F.R11, F.R12, F.R13, F.R14, F.R15}
F_XREGS = {F.XMM0, F.XMM1, F.XMM2, F.XMM3, F.XMM4, F.XMM5, F.XMM6, F.XMM7,
           F.XMM8, F.XMM9, F.XMM10, F.XMM11, F.XMM12, F.XMM13, F.XMM14, F.XMM15}
F_SCALE = {F.SCALE1, F.SCALE2, F.SCALE4, F.SCALE8}


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
    stk0_offset1 = 25
    stk1 = 26
    #
    bbl0 = 30
    bbl1 = 31
    bbl2 = 32
    fun0 = 35
    #
    mem0_num1_prel = 40
    mem1_num2_prel = 41

    fun1_prel = 45
    jtb1_prel = 46


_OP_TO_RELOC_KIND = {
    P.bbl0: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.bbl2: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.fun0: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.fun1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.mem1_num2_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.mem0_num1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
    P.jtb1_prel: enum_tab.RELOC_TYPE_X86_64.PC32,
}


def _HandleReloc(cpuins: x64.Ins, pos: int, ins: ir.Ins, op: P):
    assert not cpuins.has_reloc(), f"{cpuins.reloc_kind}"
    if op in {P.bbl0, P.bbl1, P.bbl2}:
        bbl = ins.operands[op.value - P.bbl0.value]
        assert isinstance(bbl, ir.Bbl), f"{ins} {bbl}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, bbl.name)
    elif op in {P.fun0}:
        fun = ins.operands[op.value - P.fun0.value]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op is P.fun1_prel:
        fun = ins.operands[1]
        assert isinstance(fun, ir.Fun), f"{ins} {fun}"
        assert fun.kind is not o.FUN_KIND.EXTERN, f"undefined fun: {fun.name}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, fun.name)
    elif op in {P.mem1_num2_prel, P.mem0_num1_prel}:
        slot = op.value - P.mem0_num1_prel.value
        mem = ins.operands[slot]
        assert isinstance(mem, ir.Mem), f"{ins} {mem}"
        assert mem.kind is not o.MEM_KIND.EXTERN, f"undefined fun: {mem.name}"
        num = ins.operands[slot + 1]
        assert isinstance(num, ir.Const), f"{ins} {num}"
        assert cpuins.operands[pos] == 0
        cpuins.operands[pos] = num.value
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], False, pos, mem.name)
    elif op is P.jtb1_prel:
        jtb = ins.operands[1]
        assert isinstance(jtb, ir.Jtb), f"{ins} {jtb}"
        cpuins.set_reloc(_OP_TO_RELOC_KIND[op], True, pos, jtb.name)
    else:
        assert False, f"unsupported reloc {op}"


def GetStackOffset(stk: ir.Stk, num: ir.Const) -> int:
    assert isinstance(num, ir.Const)
    assert isinstance(stk, ir.Stk)
    assert stk.slot is not None
    return stk.slot + num.value


def _ExtractTmplArgOp(ins: ir.Ins, arg: P, ctx: regs.EmitContext) -> int:
    ops = ins.operands
    if arg is P.reg01:
        assert ops[0] == ops[1], f"ins not in aab for {ins} {ins.operands}"
        reg = ops[0]
        assert isinstance(reg, ir.Reg)
        assert reg.HasCpuReg()
        return reg.cpu_reg.no
    elif arg in {P.reg0, P.reg1, P.reg2}:
        pos = arg.value - P.reg0.value
        reg = ops[pos]
        assert isinstance(reg, ir.Reg), f"in {ins} expect reg for {arg} but got {reg}"
        assert reg.HasCpuReg(), f"in {ins} expect reg with cpureg for {arg} but got {reg}"
        return reg.cpu_reg.no
    elif arg in {P.num0, P.num1, P.num2, P.num3, P.num4}:
        pos = arg.value - P.num0.value
        assert isinstance(ops[pos], ir.Const)
        return ops[pos].value
    elif arg is P.stk1_offset2:
        return GetStackOffset(ops[1], ops[2])
    elif arg is P.stk0_offset1:
        return GetStackOffset(ops[0], ops[1])
    elif arg is P.tmp_gpr:
        return _F_TO_INT[F.RAX]
    elif arg is P.tmp_flt:
        return _F_TO_INT[F.XMM0]
    elif arg is P.scratch_gpr:
        assert ctx.scratch_cpu_reg.kind == regs.CpuRegKind.GPR, f"{ctx.scratch_cpu_reg}"
        return ctx.scratch_cpu_reg.no
    elif arg in {P.spill0, P.spill1, P.spill2}:
        pos = arg.value - P.spill0.value
        reg = ops[pos]
        assert isinstance(reg, ir.Reg)
        assert isinstance(reg.cpu_reg, ir.StackSlot)
        return reg.cpu_reg.offset
    elif arg is P.spill01:
        assert ops[0] == ops[1]
        reg = ops[0]
        assert isinstance(reg, ir.Reg)
        assert isinstance(reg.cpu_reg, ir.StackSlot)
        return reg.cpu_reg.offset
    elif arg in _OP_TO_RELOC_KIND:
        return 0
    else:
        assert False, f"could not extract op for {ins} {ins.operands}  unsupported: {arg}"


class InsTmpl:
    """Represents a template for an A32 instructions

    The idea is to "explode" each IR instruction into a list of these.

    The template args will be converted into A32 instruction operands by
    substituting data derived from the IR instruction operands as needed.

    args: a list of registers/constants/placeholders all values must be run through EncodeOperand
    """

    def __init__(self, opcode_name: str, args: List[Any]):
        opcode: x64.Opcode = x64.Opcode.name_to_opcode[opcode_name]
        assert args is not None
        assert len(args) == len(opcode.fields), f"num arg mismatch for {opcode_name} {args} {opcode.fields}"
        # Note, the sanity checks below need to be adjusted as needed
        for op, field in zip(args, opcode.fields):
            assert isinstance(op, (int, P, F)), (
                f"unknown op {op} for {opcode.name} {args}")
            if field is x64.OK.SIB_SCALE:
                assert op in F_SCALE, f"{op}"
            elif field in {x64.OK.MODRM_REG8, x64.OK.MODRM_REG16, x64.OK.MODRM_REG32, x64.OK.MODRM_REG64,
                           x64.OK.MODRM_RM_REG8, x64.OK.MODRM_RM_REG16, x64.OK.MODRM_RM_REG32,
                           x64.OK.MODRM_RM_REG64}:
                assert op in {P.reg0, P.reg1, P.reg2, P.reg01, P.tmp_gpr, P.scratch_gpr} or op in F_REGS, f"{op}"
            elif field in {x64.OK.MODRM_XREG32, x64.OK.MODRM_XREG64,
                           x64.OK.MODRM_RM_XREG32, x64.OK.MODRM_RM_XREG64}:
                assert op in {P.reg0, P.reg1, P.reg2, P.reg01, P.tmp_flt} or op in F_XREGS, f"{op}"
            elif field is x64.OK.SIB_INDEX:
                assert op in {F.NO_INDEX, P.reg1, P.reg2, P.tmp_gpr, P.scratch_gpr}, f"{op}"
            elif field is x64.OK.SIB_BASE:
                assert op in {P.reg01, P.reg0, P.reg1, P.tmp_gpr, P.scratch_gpr} or op in F_REGS, f"{op}"
            elif field is x64.OK.RIP_BASE:
                assert op in {F.RIP}, f"{op}"
            elif field is x64.OK.OFFABS32:
                assert isinstance(op, int) or op in {P.spill0, P.spill1, P.spill2, P.spill01, P.num1, P.num2,
                                                     P.fun1_prel, P.mem0_num1_prel, P.mem1_num2_prel, P.jtb1_prel,
                                                     P.stk1_offset2, P.stk0_offset1, P.stk1}, f"{op}"
            elif field is x64.OK.OFFABS8:
                assert op in {0}, f"{op}"
            elif field in {x64.OK.IMM8, x64.OK.IMM16, x64.OK.IMM32, x64.OK.IMM32_64, x64.OK.IMM64}:
                assert op in {P.num0, P.num1, P.num2} or isinstance(op, int), f"{op}"
            elif field is x64.OK.OFFPCREL32:
                assert op in {P.bbl0, P.bbl2, P.fun0}, f"{op}"
            elif field in {x64.OK.BYTE_WITH_REG8, x64.OK.BYTE_WITH_REG16, x64.OK.BYTE_WITH_REG32,
                           x64.OK.BYTE_WITH_REG64}:
                assert op in {P.reg0, P.tmp_gpr} or op in F_REGS, f"{op}"
            elif field in {x64.OK.IMPLICIT_AX, x64.OK.IMPLICIT_EAX, x64.OK.IMPLICIT_RAX}:
                assert op is F.RAX
            elif field in {x64.OK.IMPLICIT_DX, x64.OK.IMPLICIT_EDX, x64.OK.IMPLICIT_RDX}:
                assert op is F.RDX
            elif field in {x64.OK.IMPLICIT_CL}:
                assert op is F.RCX
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

_ALLOWED_CURBS_REG = {C.REG, C.SP_REG, C.REG_RAX, C.REG_RCX, C.REG_RDX}
_ALLOWED_CURBS_CONST = {C.UIMM8, C.SIMM8, C.UIMM16, C.SIMM16, C.UIMM32, C.SIMM32, C.UIMM64, C.SIMM64}
_ALLOWED_CURBS_REG_OR_CONST = _ALLOWED_CURBS_REG | _ALLOWED_CURBS_CONST


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
        for type_constr, curb, kind in zip(type_constraints, op_curbs,
                                           opcode.operand_kinds):
            if kind is o.OP_KIND.REG:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert curb in _ALLOWED_CURBS_REG, f"{kind} {curb}"
            elif kind is o.OP_KIND.CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert curb in _ALLOWED_CURBS_CONST, f"{opcode} {type_constr} {curb} {kind}"
            elif kind is o.OP_KIND.REG_OR_CONST:
                assert type_constr in _ALLOWED_OPERAND_TYPES_REG, f"bad {kind} {type_constr} {opcode}"
                assert curb in _ALLOWED_CURBS_REG_OR_CONST, f"{opcode} {type_constr} {curb} {kind}"
            else:
                assert type_constr is o.DK.INVALID
                assert curb is C.INVALID, f"bad pattern for {opcode}"

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
            elif op_curb in {C.SIMM8, C.SIMM16, C.SIMM32, C.SIMM64,
                             C.UIMM8, C.UIMM16, C.UIMM32, C.UIMM64}:
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
                elif op_curb is C.UIMM8:
                    if (1 << 8) <= op.value or op.value < 0:
                        return False
                elif op_curb is C.UIMM16:
                    if (1 << 16) <= op.value or op.value < 0:
                        return False
                elif op_curb is C.UIMM32:
                    if (1 << 32) <= op.value or op.value < 0:
                        return False
                elif op_curb is C.UIMM64:
                    if (1 << 64) <= op.value or op.value < 0:
                        return False
            elif op_curb in {C.REG_RAX, C.REG_RCX, C.REG_RDX}:
                if not isinstance(op, ir.Reg):
                    return False
                if op.cpu_reg.no != op_curb.value - C.REG_RAX.value:
                    return False
            else:
                assert False, f"{op_curb}"
        return True

    def __str__(self):
        types = [x.name for x in self.type_constraints]
        curbs = [x.name for x in self.op_curbs]
        return f"PATTERN {self.opcode.name} [{' '.join(types)}] [{' '.join(curbs)}]"


def HandlePseudoNop1(ins: ir.Ins, ctx: regs.EmitContext):
    """This does not emit any code but copies the register assigned to the nop into the ctx

    The idea is that the next instruction can use this register as a scratch. But this
    only works if the next instruction was not assigned the register itself.
    """
    # assert ctx.scratch_reg is ir.REG_INVALID
    ctx.scratch_cpu_reg = ins.operands[0].cpu_reg
    return []


def EmitFunProlog(ctx: regs.EmitContext) -> List[InsTmpl]:
    """
    Stack organisation:
    * return address
    * gpr
    * flt
    * stack data
    """
    out = []
    gpr_regs = regs.MaskToGprRegs(ctx.gpr_reg_mask)
    flt_regs = regs.MaskToFltRegs(ctx.flt_reg_mask)
    stk_size = ctx.stk_size + 8 * len(flt_regs) + 8 * len(gpr_regs) + 8
    if not ctx.is_leaf or ctx.stk_size or flt_regs:
        stk_size = ((stk_size + 15) >> 4) << 4  # align to 16
    stk_size -= 8 * len(gpr_regs) + 8  # already accounted for
    while gpr_regs:
        out.append(InsTmpl("push_64_r", [F(F.RAX.value + gpr_regs.pop(-1).no)]))
    if stk_size > 0:
        out.append(InsTmpl("sub_64_mr_imm32", [F.RSP, stk_size]))
    offset = ctx.stk_size
    while flt_regs:
        out.append(InsTmpl("movsd_mbis32_x", Spilled(offset) +
                           [F(F.XMM0.value + flt_regs.pop(-1).no)]))
        offset += 8
    return out


def EmitFunEpilog(ctx: regs.EmitContext) -> List[InsTmpl]:
    out = []
    # we reverse everything at the end, which allows us to mimic the Prolog more closely
    out.append(InsTmpl("ret", []))
    gpr_regs = regs.MaskToGprRegs(ctx.gpr_reg_mask)
    flt_regs = regs.MaskToFltRegs(ctx.flt_reg_mask)
    stk_size = ctx.stk_size + 8 * len(flt_regs) + 8 * len(gpr_regs) + 8
    if not ctx.is_leaf or ctx.stk_size or flt_regs:
        stk_size = ((stk_size + 15) >> 4) << 4  # align to 16
    stk_size -= 8 * len(gpr_regs) + 8  # already accounted for
    while gpr_regs:
        out.append(InsTmpl("pop_64_r", [F(F.RAX.value + gpr_regs.pop(-1).no)]))
    if stk_size > 0:
        out.append(InsTmpl("add_64_mr_imm32", [F.RSP, stk_size]))
    offset = ctx.stk_size
    while flt_regs:
        out.append(
            InsTmpl("movsd_x_mbis32", [F(F.XMM0.value + flt_regs.pop(-1).no)] + Spilled(offset)))
        offset += 8

    out.reverse()
    return out


def _InsAddNop1ForCodeSel(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    if opc in {o.ST, o.SWITCH}:
        # needs scratch reg for some opcodes
        scratch = fun.GetScratchReg(o.DK.S64, "nop1", False)
        return [ir.Ins(o.NOP1, [scratch]), ins]
    return [ins]


def FunAddNop1ForCodeSel(fun: ir.Fun):
    """Add dummy instruction to ensure we have a scratch register for the next instruction

    Currently, SWITCH needs a scratch register
    """
    return ir.FunGenericRewrite(fun, _InsAddNop1ForCodeSel)


def Spilled(spill):
    return [F.RSP, F.NO_INDEX, F.SCALE1, spill]


def InsTmplStkSt(dk: o.DK, spill: P, src):
    if dk.flavor() == o.DK_FLAVOR_F:
        suffix = "s" if dk is o.DK.F32 else "d"
        return InsTmpl(f"movs{suffix}_mbis32_x", Spilled(spill) + [src])
    return InsTmpl(f"mov_{dk.bitwidth()}_mbis32_r", Spilled(spill) + [src])


def InsTmplStkLd(dk: o.DK, dst, spill: P):
    if dk.flavor() == o.DK_FLAVOR_F:
        suffix = "s" if dk is o.DK.F32 else "d"
        return InsTmpl(f"movs{suffix}_x_mbis32", [dst] + Spilled(spill))
    return InsTmpl(f"mov_{dk.bitwidth()}_r_mbis32", [dst] + Spilled(spill))


_KIND_TO_IMM = {
    o.DK.U8: C.UIMM8,
    o.DK.S8: C.SIMM8,
    o.DK.U16: C.UIMM16,
    o.DK.S16: C.SIMM16,
    o.DK.U32: C.UIMM32,
    o.DK.S32: C.SIMM32,
    o.DK.U64: C.SIMM32,  # not a typo
    o.DK.S64: C.SIMM32,  # not a typo
    o.DK.A64: C.SIMM32,  # not a typo
    o.DK.C64: C.SIMM32,  # not a typo
}

_KIND_TO_IMM_WITH_64 = {
    o.DK.U8: C.UIMM8,
    o.DK.S8: C.SIMM8,
    o.DK.U16: C.UIMM16,
    o.DK.S16: C.SIMM16,
    o.DK.U32: C.UIMM32,
    o.DK.S32: C.SIMM32,
    o.DK.U64: C.UIMM64,
    o.DK.S64: C.SIMM64,
    o.DK.A64: C.SIMM64,
    o.DK.C64: C.SIMM64,
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
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr", [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_r", Spilled(P.spill01) + [P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32", [P.reg01] + Spilled(P.spill2))])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    [InsTmpl(f"mov_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill2)),
                     InsTmpl(f"{x64_opc}_{bw}_mbis32_r", Spilled(P.spill01) + [P.tmp_gpr])])
            #
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_imm{iw}", [P.reg01, P.num2])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, _KIND_TO_IMM[kind1]],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_imm{iw}", Spilled(P.spill01) + [P.num2])])

    # TODO: handle 8 bit multiply, maybe support some immediate variants
    for kind1 in [o.DK.U16, o.DK.S16, o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind1.bitwidth()
        Pattern(o.MUL, [kind1] * 3,
                [C.REG, C.REG, C.REG],
                [InsTmpl(f"imul_{bw}_r_mr", [P.reg01, P.reg2])])
        Pattern(o.MUL, [kind1] * 3,
                [C.SP_REG, C.SP_REG, C.REG],
                [InsTmpl(f"mov_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill01)),
                 InsTmpl(f"imul_{bw}_r_mr", [P.tmp_gpr, P.reg2]),
                 InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill01) + [P.tmp_gpr])])
        Pattern(o.MUL, [kind1] * 3,
                [C.REG, C.REG, C.SP_REG],
                [InsTmpl(f"imul_{bw}_r_mbis32", [P.reg01] + Spilled(P.spill2))])
        Pattern(o.MUL, [kind1] * 3,
                [C.SP_REG, C.SP_REG, C.SP_REG],
                [InsTmpl(f"mov_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill01)),
                 InsTmpl(f"imul_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill2)),
                 InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill01) + [P.tmp_gpr])])

    # TODO: handle 8 bit divide
    for rdx, rax, kind1 in [("dx", "ax", o.DK.U16), ("edx", "eax", o.DK.U32), ("rdx", "rax", o.DK.U64)]:
        bw = kind1.bitwidth()
        Pattern(o.DIV, [kind1] * 3,
                [C.REG_RDX, C.REG_RAX, C.REG],
                [InsTmpl(f"xor_{bw}_mr_r", [F.RDX, F.RDX]),
                 InsTmpl(f"div_{bw}_{rdx}_{rax}_mr", [F.RDX, F.RAX, P.reg2])])

    # TODO: handle 8 bit divide
    for rdx, rax, kind1, prep in [("dx", "ax", o.DK.S16, "cwd_16_dx_ax"),
                                  ("edx", "eax", o.DK.S32, "cdq_32_edx_eax"),
                                  ("rdx", "rax", o.DK.S64, "cqo_64_rdx_rax")]:
        bw = kind1.bitwidth()
        Pattern(o.DIV, [kind1] * 3,
                [C.REG_RDX, C.REG_RAX, C.REG],
                [InsTmpl(prep, [F.RDX, F.RAX]),
                 InsTmpl(f"idiv_{bw}_{rdx}_{rax}_mr", [F.RDX, F.RAX, P.reg2])])


def InitBitFiddle():
    for kind in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                 o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind.bitwidth()
        for opc, x64_opc_s, x64_opc_u in [(o.SHL, "shl", "shl"), (o.SHR, "sar", "shr")]:
            x64_opc = x64_opc_u if kind in {o.DK.U8, o.DK.U16, o.DK.U32, o.DK.U64} else x64_opc_s
            Pattern(opc, [kind] * 3, [C.REG, C.REG, C.UIMM8],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_imm8", [P.reg01, P.num2])])
            Pattern(opc, [kind] * 3, [C.SP_REG, C.SP_REG, C.UIMM8],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_imm8", Spilled(P.spill01) + [P.num2])])
            Pattern(opc, [kind] * 3, [C.REG, C.REG, C.REG_RCX],
                    [InsTmpl(f"{x64_opc}_{bw}_mr_cl", [P.reg01, F.RCX])])
            Pattern(opc, [kind] * 3, [C.SP_REG, C.SP_REG, C.REG_RCX],
                    [InsTmpl(f"{x64_opc}_{bw}_mbis32_cl", Spilled(P.spill01) + [F.RCX])])

    for kind in [o.DK.U16, o.DK.S16, o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        bw = kind.bitwidth()
        for opc, x64_opc in [(o.CNTTZ, "tzcnt"), (o.CNTLZ, "lzcnt")]:
            Pattern(opc, [kind] * 2,
                    [C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr", [P.reg0, P.reg1])])
            Pattern(opc, [kind] * 2,
                    [C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mr", [P.tmp_gpr, P.reg1]),
                     InsTmplStkSt(kind, P.spill0, P.tmp_gpr)])
            Pattern(opc, [kind] * 2,
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32", [P.reg0] + Spilled(P.spill1))])
            Pattern(opc, [kind] * 2,
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmplStkSt(kind, P.spill0, P.tmp_gpr)])

    for kind in [o.DK.U8, o.DK.S8]:
        Pattern(o.CNTTZ, [kind] * 2,
                [C.REG, C.REG],
                [InsTmpl(f"or_16_mr_imm16", [P.reg1, 0xff00]),
                 InsTmpl(f"tzcnt_16_r_mr", [P.reg0, P.reg1])])
        Pattern(o.CNTTZ, [kind] * 2,
                [C.REG, C.SP_REG],
                [InsTmplStkLd(kind, P.tmp_gpr, P.spill1),
                 InsTmpl(f"or_16_mr_imm16", [P.tmp_gpr, 0xff00]),
                 InsTmpl(f"tzcnt_16_r_mr", [P.reg0, P.tmp_gpr])])
        # TODO SP_REG, REG  + SP_REG, SP_REG

    for kind in [o.DK.U8, o.DK.S8]:
        Pattern(o.CNTLZ, [kind] * 2,
                [C.REG, C.REG],
                [InsTmpl(f"and_16_mr_imm16", [P.reg1, 0xff]),
                 InsTmpl(f"lzcnt_16_r_mr", [P.reg0, P.reg1]),
                 InsTmpl(f"sub_8_mr_imm8", [P.reg0, 8])])
        Pattern(o.CNTLZ, [kind] * 2,
                [C.REG, C.SP_REG],
                [InsTmplStkLd(kind, P.tmp_gpr, P.spill1),
                 InsTmpl(f"and_16_mr_imm16", [P.tmp_gpr, 0xff]),
                 InsTmpl(f"lzcnt_16_r_mr", [P.reg0, P.tmp_gpr]),
                 InsTmpl(f"sub_8_mr_imm8", [P.reg0, 8])])
        # TODO SP_REG, REG  + SP_REG, SP_REG


def InitMovInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        # mov dst_reg src_reg
        Pattern(o.MOV, [kind1] * 2, [C.REG, C.REG],
                [InsTmpl(f"mov_{bw}_r_mr", [P.reg0, P.reg1])])
        Pattern(o.MOV, [kind1] * 2, [C.SP_REG, C.REG],
                [InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill0) + [P.reg1])])
        Pattern(o.MOV, [kind1] * 2, [C.REG, C.SP_REG],
                [InsTmpl(f"mov_{bw}_r_mbis32", [P.reg0] + Spilled(P.spill1))])
        Pattern(o.MOV, [kind1] * 2, [C.SP_REG, C.SP_REG],
                [InsTmpl(f"mov_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                 InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])
        # mov dst_reg const
        Pattern(o.MOV, [kind1] * 2, [C.REG, _KIND_TO_IMM_WITH_64[kind1]],
                [InsTmpl(f"mov_{bw}_r_imm{bw}", [P.reg0, P.num1])])
        Pattern(o.MOV, [kind1] * 2,
                [C.SP_REG, _KIND_TO_IMM[kind1]],
                [InsTmpl(f"mov_{bw}_mbis32_imm{iw}", Spilled(P.spill0) + [P.num1])])
        if bw == 64:
            Pattern(o.MOV, [kind1] * 2,
                    [C.SP_REG, _KIND_TO_IMM_WITH_64[kind1]],
                    [InsTmpl(f"mov_{bw}_r_imm{bw}", [P.tmp_gpr, P.num1]),
                     InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])


def InitAluFlt():
    for kind1, suffix in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        for opc, x64_opc in [(o.ADD, "adds"),
                             (o.SUB, "subs"),
                             (o.MUL, "muls"),
                             (o.DIV, "divs")]:
            Pattern(opc, [kind1] * 3, [C.REG, C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.reg01, P.reg2])])
            Pattern(opc, [kind1] * 3,
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32", [P.reg01] + Spilled(P.spill2))])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.REG],
                    [InsTmpl(f"movs{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill01)),
                     InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.tmp_flt, P.reg2]),
                     InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill01) + [P.tmp_flt])])
            Pattern(opc, [kind1] * 3,
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    [InsTmpl(f"movs{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill01)),
                     InsTmpl(f"{x64_opc}{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill2)),
                     InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill01) + [P.tmp_flt])])

        for opc, x64_opc in [(o.SQRT, "sqrts")]:
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.reg0, P.reg1])])
            Pattern(opc, [kind1] * 2,
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32", [P.reg0] + Spilled(P.spill1))])
            Pattern(opc, [kind1] * 2,
                    [C.SP_REG, C.REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mx", [P.tmp_flt, P.reg1]),
                     InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill0) + [P.tmp_flt])])
            Pattern(opc, [kind1] * 2,
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(f"{x64_opc}{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill1)),
                     InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill0) + [P.tmp_flt])])


def InitMovFlt():
    for kind1, suffix in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        # mov dst_reg const does not need to be handled as we are rewriting those to loads from memory
        # mov dst_reg src_reg
        Pattern(o.MOV, [kind1] * 2,
                [C.REG, C.REG],
                [InsTmpl(f"movs{suffix}_x_mx", [P.reg0, P.reg1])])
        Pattern(o.MOV, [kind1] * 2,
                [C.SP_REG, C.REG],
                [InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill0) + [P.reg1])])
        Pattern(o.MOV, [kind1] * 2,
                [C.REG, C.SP_REG],
                [InsTmpl(f"movs{suffix}_x_mbis32", [P.reg0] + Spilled(P.spill1))])
        # Note: this is just memory copy so we could use GPRs
        Pattern(o.MOV, [kind1] * 2,
                [C.SP_REG, C.SP_REG],
                [InsTmpl(f"movs{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill1)),
                 InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill0) + [P.tmp_flt])])


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
            return "jb"  # below
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jle"
        else:
            return "jbe"  # below or equal


def _GetJmpSwp(dk: o.DK, opc):
    if opc is o.BEQ:
        return "je"
    elif opc is o.BNE:
        return "jne"
    elif opc is o.BLT:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jg"
        else:
            return "ja"  # above
    elif opc is o.BLE:
        if dk in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64}:
            return "jge"
        else:
            return "jae"  # above or equal


def InitCondBraInt():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64]:
        bw = kind1.bitwidth()
        iw = 32 if bw == 64 else bw
        for opc in [o.BEQ, o.BNE, o.BLT, o.BLE]:
            if kind1 in {o.DK.C64} and opc not in {o.BEQ, o.BNE}:
                continue
            x64_jmp = _GetJmp(kind1, opc)
            x64_jmp_swp = _GetJmpSwp(kind1, opc)
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mr", [P.reg0, P.reg1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_r", Spilled(P.spill0) + [P.reg1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_r_mbis32", [P.reg0] + Spilled(P.spill1)),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.SP_REG, C.INVALID],
                    [InsTmplStkLd(kind1, P.tmp_gpr, P.spill0),
                     InsTmpl(f"cmp_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg0, P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, _KIND_TO_IMM[kind1], C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}", Spilled(P.spill0) + [P.num1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            #
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mr_imm{iw}", [P.reg1, P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [_KIND_TO_IMM[kind1], C.SP_REG, C.INVALID],
                    [InsTmpl(f"cmp_{bw}_mbis32_imm{iw}", Spilled(P.spill1) + [P.num0]),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])


def InitCondBraFlt():
    for kind1, suffix in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        for opc, x64_jmp, x64_jmp_swp in [(o.BEQ, "je", "je"),
                                          (o.BNE, "jne", "jne"),
                                          (o.BLT, "jb", "ja"),
                                          (o.BLE, "jbe", "jae")]:
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.REG, C.INVALID],
                    [InsTmpl(f"comis{suffix}_x_mx", [P.reg0, P.reg1]),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.REG, C.SP_REG, C.INVALID],
                    [InsTmpl(f"comis{suffix}_x_mbis32", [P.reg0] + Spilled(P.spill1)),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.REG, C.INVALID],
                    [InsTmpl(f"comis{suffix}_x_mbis32", [P.reg1] + Spilled(P.spill0)),
                     InsTmpl(f"{x64_jmp_swp}_32", [P.bbl2])])
            Pattern(opc, [kind1] * 2 + [o.DK.INVALID],
                    [C.SP_REG, C.SP_REG, C.INVALID],
                    [InsTmplStkLd(kind1, P.tmp_flt, P.spill0),
                     InsTmpl(f"comis{suffix}_x_mbis32", [P.tmp_flt] + Spilled(P.spill1)),
                     InsTmpl(f"{x64_jmp}_32", [P.bbl2])])


# (dst-width, source-kind)
_EXTEND_OPCODE = {
    (64, o.DK.U8): "movzx_64_8_",
    (64, o.DK.S8): "movsx_64_8_",
    (64, o.DK.U16): "movzx_64_16_",
    (64, o.DK.S16): "movsx_64_16_",
    (64, o.DK.U32): "mov_32_",
    (64, o.DK.S32): "movsxd_64_",
    #
    (32, o.DK.U8): "movzx_32_8_",
    (32, o.DK.S8): "movsx_32_8_",
    (32, o.DK.U16): "movzx_32_16_",
    (32, o.DK.S16): "movsx_32_16_",
    #
    (16, o.DK.U8): "movzx_16_8_",
    (16, o.DK.S8): "movsx_16_8_",
}


def ExtendRegTo64BitInPlace(reg, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_OPCODE.get((64, dk))
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc + "r_mr", [reg, reg])]


def ExtendRegTo64Bit(reg_dst, reg_src, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_OPCODE.get((64, dk))
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc + "r_mr", [reg_dst, reg_src])]


def ExtendRegTo64BitFromSP(reg_dst, spill, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_OPCODE.get((64, dk))
    if not x64_opc:
        x64_opc = "mov_64_"
    return [InsTmpl(x64_opc + "r_mbis32", [reg_dst] + Spilled(spill))]


def ExtendRegTo32BitInPlace(reg, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_OPCODE.get((32, dk))
    if not x64_opc:
        return []
    return [InsTmpl(x64_opc + "r_mr", [reg, reg])]


def ExtendRegTo32BitFromSP(reg_dst, spill, dk: o.DK) -> List[InsTmpl]:
    x64_opc = _EXTEND_OPCODE.get((32, dk))
    if not x64_opc:
        x64_opc = "mov_32_"
    return [InsTmpl(x64_opc + "r_mbis32", [reg_dst] + Spilled(spill))]


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
                [InsTmpl(f"add_64_mbis32_imm32", Spilled(P.spill01) + [P.num2])])
        # LEA dstsrc_reg dstsrc_reg offset_reg
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.REG],
                ExtendRegTo64BitInPlace(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis8", [P.reg01, P.reg01, P.reg2, F.SCALE1, 0])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.SP_REG, C.SP_REG, C.REG],
                ExtendRegTo64BitInPlace(P.reg2, kind1) +
                [InsTmpl(f"add_64_mbis32_r", Spilled(P.spill01) + [P.reg2])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.REG, C.REG, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("add_64_r_mr", [P.reg01, P.tmp_gpr])])
        Pattern(o.LEA, [o.DK.A64, o.DK.A64, kind1],
                [C.SP_REG, C.SP_REG, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl(f"add_64_mbis32_r", Spilled(P.spill01) + [P.tmp_gpr])])
        # LEA_STK dst_reg stk const
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32", [P.reg0] + Spilled(P.stk1_offset2))])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.SIMM32],
                [InsTmpl("lea_64_r_mbis32", [P.tmp_gpr] + Spilled(P.stk1_offset2)),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])
        # LEA_STK dst_reg stk offset_reg
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.REG],
                ExtendRegTo64BitInPlace(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis32", [P.reg0, F.RSP, P.reg2, F.SCALE1, P.stk1])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.REG],
                ExtendRegTo64BitInPlace(P.reg2, kind1) +
                [InsTmpl("lea_64_r_mbis32", [P.tmp_gpr, F.RSP, P.reg2, F.SCALE1, P.stk1]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.REG, C.INVALID, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("lea_64_r_mbis32",
                         [P.reg0, F.RSP, P.tmp_gpr, F.SCALE1, P.stk1])])
        Pattern(o.LEA_STK, [o.DK.A64, o.DK.INVALID, kind1],
                [C.SP_REG, C.INVALID, C.SP_REG],
                ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                [InsTmpl("lea_64_r_mbis32",
                         [P.tmp_gpr, F.RSP, P.tmp_gpr, F.SCALE1, P.stk1]),
                 InsTmplStkSt(o.DK.A64, P.spill0, P.tmp_gpr)])


def InitLoad():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for kind2 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                      o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64, o.DK.F32, o.DK.F64]:
            bw = kind2.bitwidth()
            if kind2 is o.DK.F32:
                x64_ld = lambda addr: f"movss_x_{addr}"
                tmp_reg = P.tmp_flt
            elif kind2 is o.DK.F64:
                x64_ld = lambda addr: f"movsd_x_{addr}"
                tmp_reg = P.tmp_flt
            else:
                x64_ld = lambda addr: f"mov_{bw}_r_{addr}"
                tmp_reg = P.tmp_gpr
            # LD_MEM dst_reg mem reg_offset will be rewritten so do not handle it here (TODO: reconsider this)
            # LD_MEM dst_reg mem const
            Pattern(o.LD_MEM, [kind2, o.DK.INVALID, kind1],
                    [C.REG, C.INVALID, C.SIMM32],
                    [InsTmpl(x64_ld("mpc32"), [P.reg0, F.RIP, P.mem1_num2_prel])])
            Pattern(o.LD_MEM, [kind2, o.DK.INVALID, kind1],
                    [C.SP_REG, C.INVALID, C.SIMM32],
                    [InsTmpl(x64_ld("mpc32"), [tmp_reg, F.RIP, P.mem1_num2_prel]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            # LD_STK dst_reg stk reg_offset will be rewritten so do not handle it here
            # LD_STK dst_reg stk const
            Pattern(o.LD_STK, [kind2, o.DK.INVALID, kind1],
                    [C.REG, C.INVALID, C.SIMM32],
                    [InsTmpl(x64_ld("mbis32"), [P.reg0] + Spilled(P.stk1_offset2))])
            Pattern(o.LD_STK, [kind2, o.DK.INVALID, kind1],
                    [C.SP_REG, C.INVALID, C.SIMM32],
                    [InsTmpl(x64_ld("mbis32"), [tmp_reg] + Spilled(P.stk1_offset2)),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            # LD dst_reg base_reg const
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.SIMM32],
                    [InsTmpl(x64_ld("mbis32"), [P.reg0, P.reg1, F.NO_INDEX, F.SCALE1, P.num2])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.SIMM32],
                    [InsTmpl(x64_ld("mbis32"), [tmp_reg, P.reg1, F.NO_INDEX, F.SCALE1, P.num2]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.SIMM32],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(x64_ld("mbis32"), [P.reg0, P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num2])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.SIMM32],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(x64_ld("mbis32"), [tmp_reg, P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num2]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            # LD dst_reg base_reg offset_reg
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg2, kind1) +
                    [InsTmpl(x64_ld("mbis8"), [P.reg0, P.reg1, P.reg2, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg2, kind1) +
                    [InsTmpl(x64_ld("mbis8"), [tmp_reg, P.reg1, P.reg2, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg2, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(x64_ld("mbis8"), [P.reg0, P.tmp_gpr, P.reg2, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(x64_ld("mbis8"), [P.reg0, P.reg1, P.tmp_gpr, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg2, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill1),
                     InsTmpl(x64_ld("mbis8"), [tmp_reg, P.tmp_gpr, P.reg2, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(x64_ld("mbis8"), [tmp_reg, P.reg1, P.tmp_gpr, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"add_64_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(x64_ld("mbis8"), [P.reg0, P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0])])
            Pattern(o.LD, [kind2, o.DK.A64, kind1],
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill2, kind1) +
                    [InsTmpl(f"add_64_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(x64_ld("mbis8"), [tmp_reg, P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0]),
                     InsTmplStkSt(kind2, P.spill0, tmp_reg)])


def InitStore():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for kind2 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                      o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64, o.DK.A64, o.DK.C64, o.DK.F32, o.DK.F64]:
            bw = kind2.bitwidth()
            if kind2 is o.DK.F32:
                x64_st = lambda addr: f"movss_{addr}_x"
                tmp_reg = P.tmp_flt
            elif kind2 is o.DK.F64:
                x64_st = lambda addr: f"movsd_{addr}_x"
                tmp_reg = P.tmp_flt
            else:
                x64_st = lambda addr: f"mov_{bw}_{addr}_r"
                tmp_reg = P.tmp_gpr
            # ST_MEM mem reg_offset src_reg will be rewritten so do not handle it here
            # ST_MEM mem const src_reg
            Pattern(o.ST_MEM, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.REG],
                    [InsTmpl(x64_st("mpc32"), [F.RIP, P.mem0_num1_prel, P.reg2])])
            Pattern(o.ST_MEM, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mpc32"), [F.RIP, P.mem0_num1_prel, tmp_reg])])
            # ST_STK stk reg_offset src_reg will be rewritten so do not handle it here (TODO: reconsider this)
            # ST_STK stk const src_reg
            Pattern(o.ST_STK, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.REG],
                    [InsTmpl(x64_st("mbis32"), Spilled(P.stk0_offset1) + [P.reg2])])
            Pattern(o.ST_STK, [o.DK.INVALID, kind1, kind2],
                    [C.INVALID, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis32"), Spilled(P.stk0_offset1) + [tmp_reg])])
            # ST base_reg const src_reg
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SIMM32, C.REG],
                    [InsTmpl(x64_st("mbis32"), [P.reg0, F.NO_INDEX, F.SCALE1, P.num1, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis32"), [P.reg0, F.NO_INDEX, F.SCALE1, P.num1, tmp_reg])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SIMM32, C.REG],
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(x64_st("mbis32"), [P.tmp_gpr, F.NO_INDEX, F.SCALE1, P.num1, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SIMM32, C.SP_REG],
                    [InsTmplStkLd(o.DK.A64, P.scratch_gpr, P.spill0),
                     InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis32"), [P.scratch_gpr, F.NO_INDEX, F.SCALE1, P.num1, tmp_reg])])
            # ST base_reg offset_reg src_reg
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg1, kind1) +
                    [InsTmpl(x64_st("mbis8"), [P.reg0, P.reg1, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg1, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.tmp_gpr, P.spill0),
                     InsTmpl(x64_st("mbis8"), [P.tmp_gpr, P.reg1, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill1, kind1) +
                    [InsTmpl(x64_st("mbis8"), [P.reg0, P.tmp_gpr, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.REG, C.SP_REG],
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis8"), [P.reg0, P.reg1, F.SCALE1, 0, tmp_reg])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SP_REG, C.REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill1, kind1) +
                    [InsTmpl(f"add_64_r_mbis32", [P.tmp_gpr] + Spilled(P.spill0)),
                     InsTmpl(x64_st("mbis8"), [P.tmp_gpr, F.NO_INDEX, F.SCALE1, 0, P.reg2])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.REG, C.SP_REG],
                    ExtendRegTo64BitInPlace(P.reg1, kind1) +
                    [InsTmplStkLd(o.DK.A64, P.scratch_gpr, P.spill0),
                     InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis8"), [P.scratch_gpr, P.reg1, F.SCALE1, 0, tmp_reg])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill1, kind1) +
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(x64_st("mbis8"), [P.reg0, P.scratch_gpr, F.SCALE1, 0, tmp_reg])])
            Pattern(o.ST, [o.DK.A64, kind1, kind2],
                    [C.SP_REG, C.SP_REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill1, kind1) +
                    [InsTmplStkLd(kind2, tmp_reg, P.spill2),
                     InsTmpl(f"add_64_r_mbis32", [P.scratch_gpr] + Spilled(P.spill0)),
                     InsTmpl(x64_st("mbis8"), [P.scratch_gpr, F.NO_INDEX, F.SCALE1, 0, tmp_reg])])


def InitCFG():
    for kind in [o.DK.U8, o.DK.U16, o.DK.U32]:
        Pattern(o.SYSCALL, [o.DK.INVALID, kind],
                [C.INVALID, C.SIMM32],
                [InsTmpl("push_64_mr", [F.RCX]),
                 InsTmpl("push_64_mr", [F.R11]),
                 InsTmpl("mov_64_mr_imm32", [F.RAX, P.num1]),
                 InsTmpl("mov_64_mr_r", [F.R10, F.RCX]),
                 InsTmpl("syscall", []),
                 InsTmpl("pop_64_mr", [F.R11]),
                 InsTmpl("pop_64_mr", [F.RCX])])

    Pattern(o.TRAP, [], [],
            [InsTmpl("int3", [])])

    Pattern(o.BRA, [o.DK.INVALID], [C.INVALID],
            [InsTmpl("jmp_32", [P.bbl0])])

    Pattern(o.BSR, [o.DK.INVALID], [C.INVALID],
            [InsTmpl("call_32", [P.fun0])])

    Pattern(o.JSR, [o.DK.C64, o.DK.INVALID], [C.REG, C.INVALID],
            [InsTmpl("call_64_mr", [P.reg0])])

    Pattern(o.JSR, [o.DK.C64, o.DK.INVALID], [C.SP_REG, C.INVALID],
            [InsTmpl("call_64_mbis32", Spilled(P.spill0))])

    # Note: we currently use very inefficient jmp tables (8 byte entries)
    for kind in [o.DK.U8, o.DK.U16, o.DK.U32]:
        Pattern(o.SWITCH, [kind, o.DK.INVALID], [C.REG, C.INVALID],
                ExtendRegTo64Bit(P.scratch_gpr, P.reg0, kind) +
                [InsTmpl("lea_64_r_mpc32", [P.tmp_gpr, F.RIP, P.jtb1_prel]),
                 InsTmpl("jmp_64_mbis8", [P.tmp_gpr, P.scratch_gpr, F.SCALE8, 0])])

        Pattern(o.SWITCH, [kind, o.DK.INVALID], [C.SP_REG, C.INVALID],
                ExtendRegTo64BitFromSP(P.scratch_gpr, P.spill0, kind) +
                [InsTmpl("lea_64_r_mpc32", [P.tmp_gpr, F.RIP, P.jtb1_prel]),
                 InsTmpl("jmp_64_mbis8", [P.tmp_gpr, P.scratch_gpr, F.SCALE8, 0])])


# Break this up in Truncating, Extending, Flt <-> Int
def InitCONV():
    for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                  o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
        for kind2 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16,
                      o.DK.U32, o.DK.S32, o.DK.U64, o.DK.S64]:
            bw_src = kind1.bitwidth()
            bw_dst = kind2.bitwidth()
            if bw_dst <= bw_src:
                conv_opc = f"mov_{bw_dst}_"
            else:
                conv_opc = _EXTEND_OPCODE[(bw_dst, kind1)]
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.REG],
                    [InsTmpl(conv_opc + "r_mr", [P.reg0, P.reg1])])
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.SP_REG],
                    [InsTmpl(conv_opc + "r_mbis32", [P.reg0] + Spilled(P.spill1))])
            Pattern(o.CONV, [kind2, kind1],
                    [C.SP_REG, C.REG],
                    ExtendRegTo32BitInPlace(P.reg1, kind1) +
                    [InsTmpl(f"mov_{bw_dst}_mbis32_r", Spilled(P.spill0) + [P.reg1])])
            Pattern(o.CONV, [kind2, kind1],
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(conv_opc + "r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(f"mov_{bw_dst}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])

    for kind2, suffix2 in [(o.DK.F32, "s"), (o.DK.F64, "d")]:
        for kind1 in [o.DK.U8, o.DK.S8, o.DK.U16, o.DK.S16, o.DK.S32]:
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.REG],
                    ExtendRegTo32BitInPlace(P.reg1, kind1) +
                    [InsTmpl(f"cvtsi2s{suffix2}_32_x_mr", [P.reg0, P.reg1])])
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.SP_REG],
                    ExtendRegTo32BitFromSP(P.tmp_gpr, P.spill1, kind1) +
                    [InsTmpl(f"cvtsi2s{suffix2}_32_x_mr", [P.reg0, P.tmp_gpr])])
            # TODO SP_REG <- SP_REG, SP_REG <- REG
            #
            Pattern(o.CONV, [kind1, kind2],
                    [C.REG, C.REG],
                    [InsTmpl(f"cvts{suffix2}2si_32_r_mx", [P.reg0, P.reg1])])
            Pattern(o.CONV, [kind1, kind2],
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"cvts{suffix2}2si_32_r_mbis32", [P.reg0] + Spilled(P.spill1))])
            Pattern(o.CONV, [kind1, kind2],
                    [C.SP_REG, C.REG],
                    [InsTmpl(f"cvts{suffix2}2si_32_r_mx", [P.tmp_gpr, P.reg1]),
                     InsTmpl(f"mov_32_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])
            Pattern(o.CONV, [kind1, kind2],
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(f"cvts{suffix2}2si_32_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(f"mov_32_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])

        for kind1 in [o.DK.U32, o.DK.S64]:
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.REG],
                    ExtendRegTo64BitInPlace(P.reg1, kind1) +
                    [InsTmpl(f"cvtsi2s{suffix2}_64_x_mr", [P.reg0, P.reg1])])
            Pattern(o.CONV, [kind2, kind1],
                    [C.REG, C.SP_REG],
                    ExtendRegTo64BitFromSP(P.tmp_gpr, P.spill1, kind1) +
                    [InsTmpl(f"cvtsi2s{suffix2}_32_x_mr", [P.reg0, P.tmp_gpr])])
            # TODO SP_REG <- SP_REG, SP_REG <- REG
            Pattern(o.CONV, [kind1, kind2],
                    [C.REG, C.REG],
                    [InsTmpl(f"cvts{suffix2}2si_64_r_mx", [P.reg0, P.reg1])])
            Pattern(o.CONV, [kind1, kind2],
                    [C.REG, C.SP_REG],
                    [InsTmpl(f"cvts{suffix2}2si_64_r_mbis32", [P.reg0] + Spilled(P.spill1))])
            # TODO SP_REG <- SP_REG, SP_REG <- REG


def InitBITCAST():
    for k1, k2 in [(o.DK.U8, o.DK.S8), (o.DK.U16, o.DK.S16),
                   (o.DK.U32, o.DK.S32), (o.DK.U64, o.DK.S64),
                   (o.DK.A64, o.DK.S64), (o.DK.A64, o.DK.U64),
                   (o.DK.C64, o.DK.S64), (o.DK.C64, o.DK.U64)]:
        assert k1.bitwidth() == k2.bitwidth()
        bw = k1.bitwidth()
        for kind1, kind2 in [(k1, k2), (k2, k1)]:
            Pattern(o.BITCAST, [kind1, kind2], [C.REG, C.REG], [InsTmpl(f"mov_{bw}_r_mr", [P.reg0, P.reg1])])
            Pattern(o.BITCAST, [kind1, kind2], [C.SP_REG, C.REG],
                    [InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill0) + [P.reg1])])
            Pattern(o.BITCAST, [kind1, kind2], [C.REG, C.SP_REG],
                    [InsTmpl(f"mov_{bw}_r_mbis32", [P.reg0] + Spilled(P.spill1))])
            Pattern(o.BITCAST, [kind1, kind2],
                    [C.SP_REG, C.SP_REG],
                    [InsTmpl(f"mov_{bw}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                     InsTmpl(f"mov_{bw}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])

    for kind_flt, kind_int, suffix, x64_opc in [(o.DK.F32, o.DK.S32, "s", "movd"),
                                                (o.DK.F32, o.DK.U32, "s", "movd"),
                                                (o.DK.F64, o.DK.S64, "d", "movq"),
                                                (o.DK.F64, o.DK.U64, "d", "movq")]:
        bw_int = kind_int.bitwidth()
        Pattern(o.BITCAST, [kind_flt, kind_int], [C.REG, C.REG],
                [InsTmpl(f"{x64_opc}_x_mr", [P.reg0, P.reg1])])
        Pattern(o.BITCAST, [kind_int, kind_flt], [C.REG, C.REG],
                [InsTmpl(f"{x64_opc}_{bw_int}_mr_x", [P.reg0, P.reg1])])
        #
        Pattern(o.BITCAST, [kind_flt, kind_int], [C.SP_REG, C.REG],
                [InsTmpl(f"mov_{bw_int}_mbis32_r", Spilled(P.spill0) + [P.reg1])])
        Pattern(o.BITCAST, [kind_int, kind_flt], [C.SP_REG, C.REG],
                [InsTmpl(f"movs{suffix}_mbis32_x", Spilled(P.spill0) + [P.reg1])])
        #
        Pattern(o.BITCAST, [kind_flt, kind_int], [C.REG, C.SP_REG],
                [InsTmpl(f"movs{suffix}_x_mbis32", [P.reg0] + Spilled(P.spill1))])
        Pattern(o.BITCAST, [kind_int, kind_flt], [C.REG, C.SP_REG],
                [InsTmpl(f"mov_{bw_int}_r_mbis32", [P.reg0] + Spilled(P.spill1))])
        #
        Pattern(o.BITCAST, [kind_flt, kind_int], [C.SP_REG, C.SP_REG],
                [InsTmpl(f"mov_{bw_int}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                 InsTmpl(f"mov_{bw_int}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])
        Pattern(o.BITCAST, [kind_flt, kind_int], [C.SP_REG, C.SP_REG],
                [InsTmpl(f"mov_{bw_int}_r_mbis32", [P.tmp_gpr] + Spilled(P.spill1)),
                 InsTmpl(f"mov_{bw_int}_mbis32_r", Spilled(P.spill0) + [P.tmp_gpr])])


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
InitBitFiddle()
InitAluFlt()
InitMovInt()
InitMovFlt()
InitCondBraInt()
InitCondBraFlt()
InitLea()
InitLoad()
InitStore()
InitCFG()
InitCONV()
InitBITCAST()


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
