import dataclasses
import enum
from typing import List, Tuple

from BE.Base import ir
from BE.Base import liveness
from BE.Base import lowering
from IR import opcode_tab as o
from BE.Base import reg_alloc
from BE.Base import serialize


# This must mimic the DK enum (0: invalid, no more than 255 entries)
@enum.unique
class CpuRegKind(enum.Enum):
    INVALID = 0
    GPR = 1
    FLT = 2


REG_KIND_TO_CPU_REG_FAMILY = {
    o.DK.S8: CpuRegKind.GPR,
    o.DK.S16: CpuRegKind.GPR,
    o.DK.S32: CpuRegKind.GPR,
    o.DK.S64: CpuRegKind.GPR,
    #
    o.DK.U8: CpuRegKind.GPR,
    o.DK.U16: CpuRegKind.GPR,
    o.DK.U32: CpuRegKind.GPR,
    o.DK.U64: CpuRegKind.GPR,
    #
    o.DK.A64: CpuRegKind.GPR,
    o.DK.C64: CpuRegKind.GPR,
    #
    o.DK.R32: CpuRegKind.FLT,
    o.DK.R64: CpuRegKind.FLT,
}

# We use the 64 bit reg names regardless of the operand width
_REG_NAMES = ["rax", "rcx", "rdx", "rbx", "sp", "rbp", "rsi", "rdi",
              "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]

_GPR_REGS = [ir.CpuReg(name, i, CpuRegKind.GPR) for i, name in enumerate(_REG_NAMES)]

_FLT_REGS = [ir.CpuReg(f"xmm{i}", i, CpuRegKind.FLT) for i in range(16)]

CPU_REGS_MAP = {**{r.name: r for r in _GPR_REGS},
                **{r.name: r for r in _FLT_REGS}}

GPR_RESERVED_MASK = 0x0011  # rax/sp is not available for allocation
GPR_REGS_MASK = 0xffee
GPR_LAC_REGS_MASK = 0xf028  # rbx, rbp, r12-r15

GPR_REG_IMPLICIT_MASK = 0x0007  # rax/rcx/rdx must not be used for globals
FLT_RESERVED_MASK = 0x0001  # xmm0 is not available for allocation
FLT_REGS_MASK = 0xfffe
FLT_LAC_REGS_MASK = 0xff00  # xmm8 - xmm15

REGS_RESERVED = {_GPR_REGS[0], _FLT_REGS[0]}  # we use these in the code generator

_KIND_TO_CPU_REG_LIST = {
    o.DK.S8: _GPR_REGS,
    o.DK.S16: _GPR_REGS,
    o.DK.S32: _GPR_REGS,
    o.DK.U8: _GPR_REGS,
    o.DK.U16: _GPR_REGS,
    o.DK.U32: _GPR_REGS,
    #
    o.DK.U64: _GPR_REGS,
    o.DK.S64: _GPR_REGS,
    o.DK.A64: _GPR_REGS,
    o.DK.C64: _GPR_REGS,
    #
    o.DK.R32: _FLT_REGS,
    o.DK.R64: _FLT_REGS,
}

# mimics linux calling convention
_GPR_IN_REGS = [
    _GPR_REGS[7],  # rdi
    _GPR_REGS[6],  # rsi
    _GPR_REGS[2],  # rdx
    _GPR_REGS[1],  # rcx
    _GPR_REGS[8],  # r8
    _GPR_REGS[9],  # r9
    _GPR_REGS[10],  # r10
    _GPR_REGS[11],  # r11
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
    _GPR_REGS[10],  # r10
    _GPR_REGS[11],  # r11

]

_FLT_IN_OUT_REGS = _FLT_REGS[1:8]


def MaskToGprRegs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _GPR_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


def MaskToFltRegs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _FLT_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


def _GetCpuRegsForSignature(kinds: List[o.DK], gpr_regs: List[ir.CpuReg],
                            flt_regs: List[ir.CpuReg]) -> List[ir.CpuReg]:
    out = []
    next_gpr = 0
    next_flt = 0
    for k in kinds:
        if k in {o.DK.R32, o.DK.R64}:
            assert next_flt < len(flt_regs), f"too many float args: {next_flt}"
            cpu_reg = flt_regs[next_flt]
            next_flt += 1
        else:
            assert next_gpr < len(gpr_regs), f"too many gpr args: {next_gpr}"
            cpu_reg = gpr_regs[next_gpr]
            next_gpr += 1
        out.append(cpu_reg)
    return out


class PushPopInterface(lowering.PushPopInterface):
    """Used with FunPopargConversion and FunPushargConversion"""

    @classmethod
    def GetCpuRegsForInSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        return _GetCpuRegsForSignature(kinds, _GPR_IN_REGS, _FLT_IN_OUT_REGS)

    @classmethod
    def GetCpuRegsForOutSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        return _GetCpuRegsForSignature(kinds, _GPR_OUT_REGS, _FLT_IN_OUT_REGS)


class CpuRegPool(reg_alloc.RegPool):
    """
    We also distinguish if the register is  lac (live across calls)
    """

    def __init__(self, fun: ir.Fun, bbl: ir.Bbl, allow_spilling,
                 gpr_available_lac: int, gpr_available_not_lac: int, flt_available_lac: int,
                 flt_available_not_lac: int):
        super(CpuRegPool, self).__init__()
        self._fun = fun
        self._bbl = bbl
        self._allow_spilling = allow_spilling

        # set of registers that are ready to be allocated subject to the
        # reserved regions below. Should use an ordered set here?
        # Note, the int is a bit-mask
        self._gpr_available_lac: int = gpr_available_lac
        self._gpr_available_not_lac: int = gpr_available_not_lac
        # for FLT and DBL since the register are overlapping
        self._flt_available_lac: int = flt_available_lac
        self._flt_available_not_lac: int = flt_available_not_lac

        self._gpr_reserved: List[reg_alloc.PreAllocation] = [
            reg_alloc.PreAllocation() for _ in range(len(_GPR_REGS))]
        self._flt_reserved: List[reg_alloc.PreAllocation] = [
            reg_alloc.PreAllocation() for _ in range(len(_FLT_REGS))]

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return CpuRegKind.FLT if kind in {o.DK.R64, o.DK.R32} else CpuRegKind.GPR

    def get_available(self, lac, is_gpr) -> int:
        # TODO: use lac as fallback if no not_lac is available
        if is_gpr:
            return self._gpr_available_lac if lac else self._gpr_available_not_lac
        else:
            return self._flt_available_lac if lac else self._flt_available_not_lac

    def render_available(self, lac, is_gpr) -> str:
        """used by debugging tools"""
        l = " lac" if lac else ""
        return f"{self.get_available(True, is_gpr):08x} {self.get_available(False, is_gpr):08x}"

    def set_available(self, lac, is_gpr, available):
        if is_gpr:
            if lac:
                self._gpr_available_lac = available
            else:
                self._gpr_available_not_lac = available
        else:
            if lac:
                self._flt_available_lac = available
            else:
                self._flt_available_not_lac = available

    def add_reserved_range(self, lr: reg_alloc.LiveRange):
        """Add a reserved region to the pool (part of pool set up)"""
        reg = lr.reg
        assert reg.HasCpuReg()
        cpu_reg = reg.cpu_reg
        if cpu_reg in REGS_RESERVED:
            return
        if cpu_reg.kind == CpuRegKind.GPR:
            self._gpr_reserved[cpu_reg.no].add(lr)
        else:
            assert cpu_reg.kind == CpuRegKind.FLT
            self._flt_reserved[cpu_reg.no].add(lr)

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.CpuReg:
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_R
        available = self.get_available(lac, is_gpr)

        # print(f"GET {lr} {self}  avail:{available:x}")
        if not is_gpr:
            for n in range(len(_FLT_REGS)):
                mask = 1 << n
                if available & mask == mask:
                    if not self._flt_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return _KIND_TO_CPU_REG_LIST[lr.reg.kind][n]
        else:
            for n in range(len(_GPR_REGS)):
                mask = 1 << n
                if mask & available == mask:
                    if not self._gpr_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return _KIND_TO_CPU_REG_LIST[lr.reg.kind][n]
        if self._allow_spilling:
            return ir.CPU_REG_SPILL
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        lines = [f"{n - 1:2} {x}" for n, x in enumerate(serialize.BblRenderToAsm(self._bbl))]
        print("\n".join(lines))
        print(f"# ALLOCATION IMPOSSIBLE - no spilling allowed in {self._fun.name}:{self._bbl.name}")
        print(f"# {lr}")
        print(f"# ALLOCATOR status: {self}")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        assert False, f"in {self._fun.name}:{self._bbl.name} no reg available for {lr} in {self}"

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        if cpu_reg in REGS_RESERVED:
            return
        reg_mask = 1 << cpu_reg.no
        if cpu_reg.kind == CpuRegKind.FLT:
            is_gpr = False
            is_lac = (reg_mask & FLT_LAC_REGS_MASK) != 0
        else:
            is_gpr = True
            is_lac = (reg_mask & GPR_LAC_REGS_MASK) != 0
        available = self.get_available(is_lac, is_gpr)
        self.set_available(is_lac, is_gpr, available | reg_mask)
        # print (f"@@@@ adding {lac} {cpu_reg} {available | mask:x}")

    def __str__(self):
        gpr_lac, gpr_not_lac = self._gpr_available_lac, self._gpr_available_not_lac
        flt_lac, flt_not_lac = self._flt_available_lac, self._flt_available_not_lac
        out = [f"POOL gpr:{gpr_lac:x}/{gpr_not_lac:x}  flt:{flt_lac:x}/{flt_not_lac:x}"]
        for n, pa in enumerate(self._gpr_reserved):
            if pa.ranges:
                out.append(f"gpr{n} {len(pa.ranges)}")
        for n, pa in enumerate(self._flt_reserved):
            if pa.ranges:
                out.append(f"flt{n} {len(pa.ranges)}")
        return "\n".join(out)


def _RunLinearScan(bbl: ir.Bbl, fun: ir.Fun, live_ranges: List[liveness.LiveRange], allow_spilling,
                   gpr_regs_lac: int, gpr_regs_not_lac: int,
                   flt_regs_lac: int,
                   flt_regs_not_lac: int):
    pool = CpuRegPool(fun, bbl, allow_spilling,
                      gpr_regs_lac, gpr_regs_not_lac, flt_regs_lac, flt_regs_not_lac)
    for lr in live_ranges:
        # since we are operating on a BBL we cannot change LiveRanges
        # extending beyond the BBL.
        # reg_kinds_fixed (e.g. Machine) regs are assumed to be
        # pre-allocated and will not change

        if liveness.LiveRangeFlag.PRE_ALLOC in lr.flags:
            assert lr.cpu_reg is not ir.CPU_REG_INVALID and lr.cpu_reg is not ir.CPU_REG_SPILL

            pool.add_reserved_range(lr)
        else:
            lr.cpu_reg = ir.CPU_REG_INVALID

    # print (f"{pool}")
    # print(f"\nPY {bbl.name}")
    # for lr in live_ranges:
    #    print(f"{lr}")

    # print ("\n".join(serialize.BblRenderToAsm(bbl)))
    n = [0]

    def logger(lr, message):
        m = f"{n[0]} {lr} {message}"
        n[0] += 1
        print(m)

    reg_alloc.RegisterAssignerLinearScan(live_ranges, pool, None)


def _AssignAllocatedRegsAndMarkSpilledRegs(live_ranges) -> int:
    spill_count = 0
    for lr in live_ranges:
        if liveness.LiveRangeFlag.PRE_ALLOC in lr.flags:
            continue
        if lr.is_use_lr():
            continue
        assert lr.cpu_reg != ir.CPU_REG_INVALID
        if lr.cpu_reg is ir.CPU_REG_SPILL:
            lr.reg.cpu_reg = ir.StackSlot(0)
            spill_count += 1
        else:
            lr.reg.cpu_reg = lr.cpu_reg
    return spill_count


def _DumpBblWithLineNumbers(bbl):
    lines = serialize.BblRenderToAsm(bbl)
    print(lines.pop(0))
    for n, l in enumerate(lines):
        print(f"{n:2d}", l)


def _BblRegAllocOrSpill(bbl: ir.Bbl, fun: ir.Fun) -> int:
    """Allocates regs to the intra bbl live ranges

    Note, this runs after global register allocation has occurred
    """
    VERBOSE = False
    if VERBOSE:
        _DumpBblWithLineNumbers(bbl)

    live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out)
    live_ranges.sort()
    for lr in live_ranges:
        assert liveness.LiveRangeFlag.IGNORE not in lr.flags
        # since we are operating on a BBL we cannot change LiveRanges
        # extending beyond the BBL.
        # reg_kinds_fixed (e.g. Machine) regs are assumed to be
        # pre-allocated and will not change
        assert not lr.reg.IsSpilled()
        if lr.reg.HasCpuReg():
            lr.flags |= liveness.LiveRangeFlag.PRE_ALLOC
            lr.cpu_reg = lr.reg.cpu_reg
        if VERBOSE:
            print(repr(lr))

    # First reg-alloc path to determine if spilling is needed.
    # Note, global and fixed registers have already been assigned and will
    # be respected by the allocator.
    _RunLinearScan(bbl, fun, live_ranges, True,
                   GPR_REGS_MASK & GPR_LAC_REGS_MASK, GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                   FLT_REGS_MASK & FLT_LAC_REGS_MASK, FLT_REGS_MASK & ~FLT_LAC_REGS_MASK)

    if VERBOSE:
        print("@@@ AFTER")
        for lr in live_ranges:
            print(repr(lr))
    # for reg
    #     print(f"SPILL: {spilled_regs}")
    #     count += len(spilled_regs)
    #     reg_alloc.BblSpillRegs(bbl, fun, spilled_regs, o.DK.U32)
    #     continue
    #
    # # print ("\n".join(serialize.BblRenderToAsm(bbl)))
    # return count
    return _AssignAllocatedRegsAndMarkSpilledRegs(live_ranges)


def FunLocalRegAlloc(fun):
    return ir.FunGenericRewriteBbl(fun, _BblRegAllocOrSpill)


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    gpr_reg_mask: int = 0  # bitmask for saved gpr
    flt_reg_mask: int = 0  # bitmask for saved flt (dbl, etc.) only lower 64bits are saved
    stk_size: int = 0
    is_leaf: bool = False
    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID

    def FrameSize(self):
        # includes the return address
        gpr_regs = MaskToGprRegs(self.gpr_reg_mask)
        flt_regs = MaskToFltRegs(self.flt_reg_mask)
        stk_size = self.stk_size + 8 * len(flt_regs) + 8 * len(gpr_regs) + 8
        if not self.is_leaf or self.stk_size or flt_regs:
            stk_size = ((stk_size + 15) >> 4) << 4  # align to 16
        return stk_size

def _FunCpuRegStats(fun: ir.Fun) -> Tuple[int, int]:
    gpr = 0
    flt = 0
    for bbl in fun.bbls:
        for ins in bbl.inss:
            for reg in ins.operands:
                if isinstance(reg, ir.Reg):
                    if reg.IsSpilled():
                        continue
                    assert reg.HasCpuReg(), f"missing cpu reg for {reg} in {ins} {ins.operands}"
                    if reg.cpu_reg.kind == CpuRegKind.GPR:
                        gpr |= 1 << reg.cpu_reg.no
                    else:
                        flt |= 1 << reg.cpu_reg.no
    return gpr, flt


def FunComputeEmitContext(fun: ir.Fun) -> EmitContext:
    gpr_mask, flt_mask = _FunCpuRegStats(fun)
    gpr_mask &= GPR_LAC_REGS_MASK
    flt_mask &= FLT_LAC_REGS_MASK
    stk_size = (fun.stk_size + 15) // 16 * 16
    return EmitContext(gpr_mask, flt_mask, stk_size, ir.FunIsLeaf(fun))


def AssignCpuRegOrMarkForSpilling(assign_to: List[ir.Reg],
                                  cpu_reg_mask_first_choice: int,
                                  cpu_reg_mask_second_choice: int):
    """
    Returns the regs that could not be assigned.
    """
    # print (f"@@ AssignCpuRegOrMarkForSpilling {len(assign_to)} {cpu_reg_mask_first_choice:x} {cpu_reg_mask_second_choice:x}")
    mask = cpu_reg_mask_first_choice
    pos = 0
    for reg in assign_to:
        if mask == 0 and cpu_reg_mask_second_choice != 0:
            mask = cpu_reg_mask_second_choice
            cpu_reg_mask_second_choice = 0
            pos = 0
        if mask == 0:
            reg.cpu_reg = ir.StackSlot()
            continue
        while ((1 << pos) & mask) == 0: pos += 1
        assert reg.cpu_reg is None
        reg.cpu_reg = _KIND_TO_CPU_REG_LIST[reg.kind][pos]
        mask &= ~(1 << pos)
        pos += 1
