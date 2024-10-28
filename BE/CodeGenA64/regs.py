from Base import cfg
from Base import ir
from Base import liveness
from Base import opcode_tab as o
from Base import reg_alloc
from Base import serialize

import dataclasses
from typing import List, Optional, Tuple
import enum


# This must mimic the DK enum (0: invalid, no more than 255 entries)
@enum.unique
class CpuRegKind(enum.Enum):
    INVALID = 0
    GPR = 1
    FLT = 2


_GPR_REGS = [ir.CpuReg(f"x{i}" if i != 31 else "sp", i, CpuRegKind.GPR)
             for i in range(32)]

_FLT_REGS = [ir.CpuReg(f"d{i}", i, CpuRegKind.FLT) for i in range(32)]

# used to map function parameters to CpuRegs and for non-lac regs
# note: our calling convention does not completely match the official one
_GPR_PARAMETER_REGS = _GPR_REGS[0:16]
_FLT_PARAMETER_REGS = _FLT_REGS[0:8] + _FLT_REGS[16:32]

# Note: this is excluded from GPR_LAC_REGS_MASK
GPR_HELPER_REG = _GPR_REGS[16]

CPU_REGS_MAP = {**{r.name: r for r in _GPR_REGS},
                **{r.name: r for r in _FLT_REGS}}

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
    o.DK.F32: CpuRegKind.FLT,
    o.DK.F64: CpuRegKind.FLT,
}


def MaskToGpr64Regs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _GPR_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


def MaskToFlt64Regs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _FLT_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


# We do not really care about the 32 vs 64 bit for these
_LINK_REG_MASK = 1 << 30

# excludes x16 which we have reserved
GPR_REGS_MASK = 0x7ffeffff
GPR_LAC_REGS_MASK = 0x3ffe0000
GPR_LAC_REGS_MASK_WITH_LR = 0x7ffe0000
GPR_SPECIAL_MASK = 0x00010000

FLT_REGS_MASK = 0xffffffff
FLT_LAC_REGS_MASK = 0x0000ff00

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
    o.DK.F32: _FLT_REGS,
    o.DK.F64: _FLT_REGS,
}


# Same for input and output refs
def _GetCpuRegsForSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    next_gpr = 0
    next_flt = 0
    out = []
    for k in kinds:
        if k in {o.DK.F32, o.DK.F64}:
            assert next_flt < len(
                _FLT_PARAMETER_REGS), "too many flt arguments"
            cpu_reg = _FLT_PARAMETER_REGS[next_flt]
            next_flt += 1
        else:
            assert k in {o.DK.S32, o.DK.U32, o.DK.C64,
                         o.DK.S64, o.DK.A64, o.DK.U64}, f"unexpected reg type {k}"
            assert next_gpr <= len(
                _GPR_PARAMETER_REGS), "too many gpr arguments"
            cpu_reg = _GPR_PARAMETER_REGS[next_gpr]
            next_gpr += 1
        out.append(cpu_reg)
    return out


class PushPopInterface:
    """Used with FunPopargConversion and FunPushargConversion

    Has all the calling-convention logic
    """

    @classmethod
    def GetCpuRegsForInSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        return _GetCpuRegsForSignature(kinds)

    @classmethod
    def GetCpuRegsForOutSignature(cls, kinds: List[o.DK]) -> List[ir.CpuReg]:
        return _GetCpuRegsForSignature(kinds)


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
        return CpuRegKind.FLT if kind in {o.DK.F64, o.DK.F32} else CpuRegKind.GPR

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
        if cpu_reg.kind == CpuRegKind.GPR:
            self._gpr_reserved[cpu_reg.no].add(lr)
        else:
            assert cpu_reg.kind == CpuRegKind.FLT
            self._flt_reserved[cpu_reg.no].add(lr)

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        self.give_back_available_reg(cpu_reg)
        if cpu_reg.kind == CpuRegKind.GPR:
            self._gpr_reserved[cpu_reg.no].current = 0
        else:
            assert cpu_reg.kind == CpuRegKind.FLT
            self._flt_reserved[cpu_reg.no].current = 0

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.CpuReg:
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_F
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
        lines = [f"{n - 1:2} {x}" for n,
                 x in enumerate(serialize.BblRenderToAsm(self._bbl))]
        print("\n".join(lines))
        print(
            f"# ALLOCATION IMPOSSIBLE - no spilling allowed in {self._fun.name}:{self._bbl.name}")
        print(f"# {lr}")
        print(f"# ALLOCATOR status: {self}")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        assert False, f"in {self._fun.name}:{self._bbl.name} no reg available for {lr} in {self}"

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
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
        out = [
            f"POOL gpr:{gpr_lac:x}/{gpr_not_lac:x}  flt:{flt_lac:x}/{flt_not_lac:x}"]
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

    reg_alloc.RegisterAssignerLinearScanFancy(live_ranges, pool, None)


def _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges) -> List[ir.Reg]:
    out: List[ir.Reg] = []
    for lr in live_ranges:
        if liveness.LiveRangeFlag.PRE_ALLOC in lr.flags:
            continue
        if lr.is_use_lr():
            continue
        assert lr.cpu_reg != ir.CPU_REG_INVALID
        if lr.cpu_reg is ir.CPU_REG_SPILL:
            out.append(lr.reg)
        else:
            lr.reg.cpu_reg = lr.cpu_reg
    return out


def _BblRegAllocOrSpill(bbl: ir.Bbl, fun: ir.Fun) -> int:
    """Allocates regs to the intra bbl live ranges

    Note, this runs after global register allocation has occurred
    """
    # print ("\n".join(serialize.BblRenderToAsm(bbl)))

    live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out)
    live_ranges.sort()
    for lr in live_ranges:
        assert liveness.LiveRangeFlag.IGNORE not in lr.flags
        # since we are operating on a BBL we cannot change LiveRanges
        # extending beyond the BBL.
        # reg_kinds_fixed (e.g. Machine) regs are assumed to be
        # pre-allocated and will not change
        if lr.reg.HasCpuReg():
            lr.flags |= liveness.LiveRangeFlag.PRE_ALLOC
            lr.cpu_reg = lr.reg.cpu_reg
        # print (repr(lr))

    # First reg-alloc pass to determine if spilling is needed.
    # Note, global and fixed registers have already been assigned and will
    # be respected by the allocator.
    _RunLinearScan(bbl, fun, live_ranges, True,
                   GPR_REGS_MASK & GPR_LAC_REGS_MASK, GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                   FLT_REGS_MASK & FLT_LAC_REGS_MASK, FLT_REGS_MASK & ~FLT_LAC_REGS_MASK)
    spilled_regs = _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges)
    if spilled_regs:
        # print (f"@@ adjusted spill count: {len(spilled_regs)} {spilled_regs}")
        # convert all register spills to loads/stores from/to the stack
        # this introduces new temporaries so we run another register allocation pass
        # afterwards
        reg_alloc.BblSpillRegs(bbl, fun, spilled_regs, o.DK.U32, "$spill")

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out)
        live_ranges.sort()
        for lr in live_ranges:
            # since we are operating on a BBL we cannot change LiveRanges
            # extending beyond the BBL.
            # reg_kinds_fixed (e.g. Machine) regs are assumed to be
            # pre-allocated and will not change
            if lr.reg.HasCpuReg():
                lr.flags |= liveness.LiveRangeFlag.PRE_ALLOC
                lr.cpu_reg = lr.reg.cpu_reg
        _RunLinearScan(bbl, fun, live_ranges, False,
                       GPR_REGS_MASK & GPR_LAC_REGS_MASK, GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                       FLT_REGS_MASK & FLT_LAC_REGS_MASK, FLT_REGS_MASK & ~FLT_LAC_REGS_MASK)
        spilled_regs = _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges)
        assert not spilled_regs
    return 0
    # assert False

    # for reg
    #     print(f"SPILL: {spilled_regs}")
    #     count += len(spilled_regs)
    #     reg_alloc.BblSpillRegs(bbl, fun, spilled_regs, o.DK.U32)
    #     continue
    #
    # # print ("\n".join(serialize.BblRenderToAsm(bbl)))
    # return count


def FunLocalRegAlloc(fun):
    return ir.FunGenericRewriteBbl(fun, _BblRegAllocOrSpill)


def _FunCpuRegStats(fun: ir.Fun) -> Tuple[int, int]:
    gpr = 0
    flt = 0
    for bbl in fun.bbls:
        for ins in bbl.inss:
            for reg in ins.operands:
                if isinstance(reg, ir.Reg):
                    assert reg.HasCpuReg(
                    ), f"missing cpu reg for {reg} in {ins} {ins.operands}"
                    if reg.cpu_reg.kind == CpuRegKind.GPR:
                        gpr |= 1 << reg.cpu_reg.no
                    else:
                        flt |= 1 << reg.cpu_reg.no
    return gpr, flt


def AssignCpuRegOrMarkForSpilling(assign_to: List[ir.Reg],
                                  cpu_reg_mask_first_choice: int,
                                  cpu_reg_mask_second_choice: int) -> List[ir.Reg]:
    """
    Returns the regs that could not be assigned.
    """
    # print (f"@@ AssignCpuRegOrMarkForSpilling {len(assign_to)} {cpu_reg_mask_first_choice:x} {cpu_reg_mask_second_choice:x}")
    out: List[ir.Reg] = []
    mask = cpu_reg_mask_first_choice
    pos = 0
    for reg in assign_to:
        if mask == 0 and cpu_reg_mask_second_choice != 0:
            mask = cpu_reg_mask_second_choice
            cpu_reg_mask_second_choice = 0
            pos = 0
        if mask == 0:
            out.append(reg)
            continue
        while ((1 << pos) & mask) == 0:
            pos += 1
        assert reg.cpu_reg is None
        reg.cpu_reg = _KIND_TO_CPU_REG_LIST[reg.kind][pos]
        mask &= ~(1 << pos)
        pos += 1
    return out


def popcount(x):
    return bin(x).count('1')


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    gpr_reg_mask: int = 0  # bitmask for saved gpr
    # bitmask for saved flt (dbl, etc.) only lower 64bits are saved
    flt_reg_mask: int = 0
    stk_size: int = 0

    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID

    def FrameSize(self):
        num_gpr_regs = popcount(self.gpr_reg_mask)
        num_gpr_regs += 1
        num_gpr_regs &= ~1
        num_flt_regs = popcount(self.flt_reg_mask)
        num_flt_regs += 1
        num_flt_regs &= ~1
        return 8 * (num_flt_regs + num_gpr_regs) + self.stk_size


def FunComputeEmitContext(fun: ir.Fun) -> EmitContext:
    gpr_mask, flt_mask = _FunCpuRegStats(fun)
    gpr_mask &= GPR_LAC_REGS_MASK_WITH_LR
    flt_mask &= FLT_LAC_REGS_MASK
    if not ir.FunIsLeaf(fun):
        gpr_mask |= _LINK_REG_MASK
    stk_size = (fun.stk_size + 15) // 16 * 16
    return EmitContext(gpr_mask, flt_mask, stk_size)
