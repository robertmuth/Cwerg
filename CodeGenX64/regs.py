from Base import ir

import enum
import dataclasses

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


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    gpr_reg_mask: int = 0  # bitmask for saved gpr
    flt_reg_mask: int = 0  # bitmask for saved flt (dbl, etc.) only lower 64bits are saved
    stk_size: int = 0

    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID
