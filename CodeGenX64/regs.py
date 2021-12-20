from Base import ir
from Base import opcode_tab as o
from Base import cfg

import enum
import dataclasses

from typing import List, Optional, Tuple


# This must mimic the DK enum (0: invalid, no more than 255 entries)
@enum.unique
class X64RegKind(enum.IntEnum):
    INVALID = 0
    GPR = 1
    FLT = 2


# We use the 64 bit reg names regardless of the operand width
_REG_NAMES = ["rax", "rcx", "rdx", "rbx", "sp", "rbp", "rsi", "rdi",
              "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]

_GPR_REGS = [ir.CpuReg(name, i, X64RegKind.GPR) for i, name in enumerate(_REG_NAMES)]

_FLT_REGS = [ir.CpuReg(f"xmm{i}", i, X64RegKind.FLT) for i in range(16)]

CPU_REGS_MAP = {**{r.name: r for r in _GPR_REGS},
                **{r.name: r for r in _FLT_REGS}}

_FLT_IN_OUT_REGS = _FLT_REGS[1:8]

# mimics linux calling convention
_GPR_IN_REGS = [
    _GPR_REGS[7],  # rdi
    _GPR_REGS[6],  # rsi
    _GPR_REGS[2],  # rdx
    _GPR_REGS[1],  # rcx
    _GPR_REGS[8],   # r8
    _GPR_REGS[9],  # r9
    _GPR_REGS[0],  # rax
]

_GPR_OUT_REGS = [
    _GPR_REGS[0],  # rax
    _GPR_REGS[2],  # rdx
    _GPR_REGS[7],  # rdi
    _GPR_REGS[6],  # rsi
    _GPR_REGS[1],  # rcx
    _GPR_REGS[8],  # r8
    _GPR_REGS[9],  # r9
]


def _GetCpuRegsForSignatureCommon(kinds: List[o.DK], gpr_regs: List[ir.CpuReg],
                                  flt_regs: List[ir.CpuReg]) -> List[ir.CpuReg]:
    out = []
    next_gpr = 0
    next_flt = 0
    for k in kinds:
        if k in {o.DK.F32, o.DK.F64}:
            cpu_reg = flt_regs[next_flt]
            next_flt += 1
        else:
            cpu_reg = gpr_regs[next_gpr]
            next_gpr += 1
        out.append(cpu_reg)
    return out


def GetCpuRegsForInSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    return _GetCpuRegsForSignatureCommon(kinds, _GPR_IN_REGS, _FLT_IN_OUT_REGS)


def GetCpuRegsForOutSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    return _GetCpuRegsForSignatureCommon(kinds, _GPR_OUT_REGS, _FLT_IN_OUT_REGS)


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    gpr_reg_mask: int = 0  # bitmask for saved gpr
    flt_reg_mask: int = 0  # bitmask for saved flt (dbl, etc.) only lower 64bits are saved
    stk_size: int = 0

    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID


def _InsPopargConversion(ins: ir.Ins, fun: ir.Fun,
                         params: List[ir.CpuReg]) -> Optional[List[ir.Ins]]:
    """
    This pass converts `poparg reg` -> `mov reg = arg_reg`

    it must used in a forward pass over the Bbl and will update `param`
    for use with the next Ins in the BBl. The initial value of `param`
    reflects the Fun's arguments.

    """
    if ins.opcode is o.POPARG:
        cpu_reg = params.pop(0)
        dst = ins.operands[0]
        # assert dst.kind == cpu_reg.kind
        reg = fun.FindOrAddCpuReg(cpu_reg, dst.kind)
        return [ir.Ins(o.MOV, [dst, reg])]

    assert not params, f"params {params} should be empty at ins {ins}"

    if ins.opcode.is_call():
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        params += GetCpuRegsForOutSignature(callee.output_types)
    return None


def FunPopargConversion(fun: ir.Fun):
    return ir.FunGenericRewrite(fun, _InsPopargConversion,
                                params=GetCpuRegsForInSignature(fun.input_types))


def _InsPushargConversionReverse(ins: ir.Ins, fun: ir.Fun,
                                 params: List[ir.CpuReg]) -> Optional[
    List[ir.Ins]]:
    """
    This pass converts pusharg reg -> mov arg_reg = reg

    Note:
         * params is passed around between calls to this function
         * pusharg's always precede calls or returns
    """
    if ins.opcode is o.PUSHARG:
        cpu_reg = params.pop(0)
        src = ins.operands[0]
        reg = fun.FindOrAddCpuReg(cpu_reg, src.kind)
        return [ir.Ins(o.MOV, [reg, src])]
    assert not params, f"params {params} should be empty at ins {ins} {ins.operands}"
    if ins.opcode.is_call():
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        params += GetCpuRegsForInSignature(callee.input_types)
    elif ins.opcode is o.RET:
        params += GetCpuRegsForOutSignature(fun.output_types)
    return None


def FunPushargConversion(fun: ir.Fun):
    return ir.FunGenericRewriteReverse(fun, _InsPushargConversionReverse,
                                       params=[])


