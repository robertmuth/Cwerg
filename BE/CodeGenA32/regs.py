"""Helpers for A32 Register management"""

import operator
import dataclasses
import functools
from typing import List, Optional, Tuple
import enum

from BE.Base import ir
from BE.Base import liveness
from BE.Base import lowering
from IR import opcode_tab as o
from BE.Base import reg_alloc
from BE.Base import serialize

_GPR_REG_NAMES = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
                  "r8", "r9", "r10", "r11", "r12", "sp", "lr", "pc"]


# This must mimic the DK enum (0: invalid, no more than 255 entries)
@enum.unique
class CpuRegKind(enum.IntEnum):
    INVALID = 0
    GPR = 1
    FLT = 2
    DBL = 4


GPR_REGS = [ir.CpuReg(name, i, CpuRegKind.GPR) for i, name in
            enumerate(_GPR_REG_NAMES)]
FLT_REGS = [ir.CpuReg(f"s{i}", i, CpuRegKind.FLT) for i in range(32)]
DBL_REGS = [ir.CpuReg(f"d{i}", i, CpuRegKind.DBL) for i in range(16)]

CPU_REGS_MAP = {**{r.name: r for r in GPR_REGS},
                **{r.name: r for r in FLT_REGS},
                **{r.name: r for r in DBL_REGS}}


def A32RegToAllocMask(reg: ir.CpuReg) -> int:
    """ Note that for DBL and FLT this matches the architectural overlap

    For GPR this produces the right mask for ldm/stm
    """
    if reg.kind is CpuRegKind.DBL:
        return 3 << (reg.no * 2)
    else:
        return 1 << reg.no


def A32RegsToAllocMask(regs: List[ir.CpuReg]) -> int:
    return functools.reduce(operator.or_,
                            (A32RegToAllocMask(r) for r in regs), 0)


def RenderMaskGPR(mask: int) -> str:
    out = []
    for i, name in enumerate(_GPR_REG_NAMES):
        if (mask & (1 << i)) != 0:
            out.append(name)
    return " ".join(out)


def RenderMaskFLT(mask: int) -> str:
    out = []
    for i in range(32):
        if (mask & (1 << i)) != 0:
            out.append(f"s{i}")
    return " ".join(out)


PC_REG = GPR_REGS[15]
LINK_REG = GPR_REGS[14]
STACK_REG = GPR_REGS[13]
GPR_SCRATCH_REG = GPR_REGS[12]

GPR_REGS_MASK = 0x5fff  # excludes pc and sp
GPR_LAC_REGS_MASK = 0x0fc0
GPR_LAC_REGS_MASK_WITH_LR = 0x4fc0

_LINK_REG_MASK = A32RegToAllocMask(LINK_REG)
_PC_REG_MASK = A32RegToAllocMask(PC_REG)

FLT_REGS_MASK = 0xffffffff
FLT_LAC_REGS_MASK = 0xffff0000

GPR_PARAMETER_REGS = GPR_REGS[0:6]
FLT_PARAMETER_REGS = FLT_REGS[0:16]
DBL_PARAMETER_REGS = DBL_REGS[0:8]


def ArmGetFltRegRanges(x: int) -> Tuple[ir.CpuReg, int]:
    start = 0
    while x & 1 == 0:
        x >>= 1
        start += 1
    # there should not be any gaps
    count = 0
    while x != 0:
        x >>= 1
        count += 1
    return FLT_REGS[start], count


def _GetCpuRegsForSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    gpr = 0
    flt = 0
    out = []
    for k in kinds:
        if k == o.DK.R32:
            assert flt < len(FLT_PARAMETER_REGS)
            cpu_reg = FLT_PARAMETER_REGS[flt]
            flt += 1
        elif k == o.DK.R64:
            # we are wasting a reg here. Can be avoided by moving f64 before all f32 params
            if flt & 1 == 1:
                flt += 1
            assert flt // 2 < len(DBL_PARAMETER_REGS)
            cpu_reg = DBL_PARAMETER_REGS[flt // 2]
            flt += 2
        else:
            assert k in {o.DK.C32, o.DK.S32, o.DK.A32, o.DK.U32}, f"unexpected reg type: {k}"
            assert gpr <= len(GPR_PARAMETER_REGS)
            cpu_reg = GPR_PARAMETER_REGS[gpr]
            gpr += 1
        out.append(cpu_reg)
    return out


class PushPopInterface(lowering.PushPopInterface):
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
            reg_alloc.PreAllocation() for _ in range(len(GPR_REGS))]
        self._flt_reserved: List[reg_alloc.PreAllocation] = [
            reg_alloc.PreAllocation() for _ in range(len(FLT_REGS))]

    def get_available(self, lac, is_gpr) -> int:
        # TODO: use lac as fallback if no not_lac is available
        if is_gpr:
            return self._gpr_available_lac if lac else self._gpr_available_not_lac
        else:
            return self._flt_available_lac if lac else self._flt_available_not_lac

    def render_available(self, lac, is_gpr) -> str:
        """used by debugging tools"""
        return f"{self.get_available(True, is_gpr):x} {self.get_available(False, is_gpr):x}"

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
        if cpu_reg.kind is CpuRegKind.GPR:
            self._gpr_reserved[cpu_reg.no].add(lr)
        elif cpu_reg.kind is CpuRegKind.FLT:
            self._flt_reserved[cpu_reg.no].add(lr)
        else:
            assert cpu_reg.kind is CpuRegKind.DBL
            self._flt_reserved[cpu_reg.no * 2].add(lr)
            self._flt_reserved[cpu_reg.no * 2 + 1].add(lr)

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return 2 if kind == o.DK.R64 or kind == o.DK.R32 else 1

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        self.give_back_available_reg(cpu_reg)
        if cpu_reg.kind is CpuRegKind.GPR:
            self._gpr_reserved[cpu_reg.no].current = 0
        elif cpu_reg.kind is CpuRegKind.FLT:
            self._flt_reserved[cpu_reg.no].current = 0
        else:
            self._flt_reserved[cpu_reg.no * 2].current = 0
            self._flt_reserved[cpu_reg.no * 2 + 1].current = 0

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.CpuReg:
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_R
        available = self.get_available(lac, is_gpr)
        # print(f"GET {lr} {self}  avail:{available:x}")
        if lr.reg.kind == o.DK.R64:
            for n in range(len(DBL_REGS)):
                mask = 3 << (n * 2)  # two adjacent bit at an even bit pos
                if available & mask == mask:
                    if (not self._flt_reserved[n * 2 + 0].has_conflict(lr) and
                            not self._flt_reserved[n * 2 + 1].has_conflict(lr)):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return DBL_REGS[n]
        elif lr.reg.kind == o.DK.R32:
            for n in range(len(FLT_REGS)):
                mask = 1 << n
                if available & mask == mask:
                    if not self._flt_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return FLT_REGS[n]
        else:
            for n in range(len(GPR_REGS)):
                mask = 1 << n
                if mask & available == mask:
                    if not self._gpr_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return GPR_REGS[n]
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
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        assert False

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        mask = A32RegToAllocMask(cpu_reg)
        if cpu_reg.kind == CpuRegKind.GPR:
            is_gpr = True
            is_lac = (mask & GPR_LAC_REGS_MASK) != 0
        else:
            is_gpr = False
            is_lac = (mask & FLT_LAC_REGS_MASK) != 0
        available = self.get_available(is_lac, is_gpr)
        self.set_available(is_lac, is_gpr, available | mask)
        # print (f"@@@@ adding {lac} {cpu_reg} {available | mask:x}")

    def __str__(self):
        gpr_lac, gpr_not_lac = self._gpr_available_lac, self._gpr_available_not_lac
        flt_lac, flt_not_lac = self._flt_available_lac, self._flt_available_not_lac
        return f"POOL  (lac/not_lac)  gpr:{gpr_lac:x}/{gpr_not_lac:x}  flt:{flt_lac:x}/{flt_not_lac:x}"


def _RunLinearScan(bbl: ir.Bbl, fun: ir.Fun, live_ranges: List[liveness.LiveRange], allow_spilling,
                   gpr_regs_lac: int, gpr_regs_not_lac: int,
                   flt_regs_lac: int,
                   flt_regs_not_lac: int):
    # print("\n".join(serialize.BblRenderToAsm(bbl)))
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


def _ComputeRegReserve(spilled_regs: List[ir.Reg], gpr_regs_not_lac, flt_regs_not_lac):
    """we need to spill regs. In theory we need to hold back as many regs that largest
    number of source regs in any opcode. For now we assume one reg is good enough
    """
    # print (f"@@ spill count: {len(spilled_regs)} {spilled_regs}")
    gpr_not_lac_reserve = 0
    flt_not_lac_reserve = 0
    for reg in spilled_regs:
        if reg.kind is o.DK.R64:
            flt_not_lac_reserve = 2
        elif reg.kind is o.DK.R32:
            if flt_not_lac_reserve == 0:
                flt_not_lac_reserve = 1
        else:
            gpr_not_lac_reserve = 1

    # TODO: fix this hack
    gpr_not_lac_reserve = 2
    new_gpr_regs_not_lac = gpr_regs_not_lac
    if gpr_not_lac_reserve:
        new_gpr_regs_not_lac &= new_gpr_regs_not_lac - 1
    if gpr_not_lac_reserve > 1:
        new_gpr_regs_not_lac &= new_gpr_regs_not_lac - 1
    new_flt_regs_not_lac = flt_regs_not_lac
    if flt_not_lac_reserve > 0:
        new_flt_regs_not_lac &= new_flt_regs_not_lac - 1
    if flt_not_lac_reserve > 1:
        new_flt_regs_not_lac &= new_flt_regs_not_lac - 1
    # print (f"@@@ reserve {gpr_not_lac_reserve} {flt_not_lac_reserve}")

    return new_gpr_regs_not_lac, new_flt_regs_not_lac


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

    if False:
        print("@@@@@@@@@@@@@@@@@@@")
        for lr in live_ranges:
            ins = ""
            if lr.def_pos >= 0 and not lr.is_use_lr():
                ins = "\t# " + serialize.InsRenderToAsm(bbl.inss[lr.def_pos])
            print(str(lr) + ins)

    _RunLinearScan(bbl, fun, live_ranges, True,
                   GPR_REGS_MASK & GPR_LAC_REGS_MASK, GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                   FLT_REGS_MASK & FLT_LAC_REGS_MASK, FLT_REGS_MASK & ~FLT_LAC_REGS_MASK)
    spilled_regs = _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges)
    if spilled_regs:
        # print (f"@@ adjusted spill count: {len(spilled_regs)} {spilled_regs}")
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


def AssignCpuRegOrMarkForSpilling(assign_to: List[ir.Reg],
                                  cpu_reg_mask_first_choice: int,
                                  cpu_reg_mask_second_choice: int) -> List[ir.Reg]:
    """
    Returns the regs that could not be assigned.
    Each invocation is for one register family (GPR or FLT)
    If used with family FLT, make sure the F64 regs precede the F32 regs

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
        if reg.kind is not o.DK.R64:
            while ((1 << pos) & mask) == 0:
                pos += 1
            assert reg.cpu_reg is None
            reg.cpu_reg = FLT_REGS[pos] if reg.kind is o.DK.R32 else GPR_REGS[pos]
            mask &= ~(1 << pos)
            pos += 1
        else:
            for pos_dbl in range(pos // 2, 32, 2):
                mask_dbl = 3 << pos_dbl
                if (mask & mask_dbl) == mask_dbl:
                    reg.cpu_reg = DBL_REGS[pos_dbl // 2]
                    mask &= ~mask_dbl
                    break
                elif (mask & mask_dbl) == 0 and pos == pos_dbl:
                    # advance pos if we did not skip any set bits
                    pos += 2
    return out


def popcount(x):
    return bin(x).count('1')


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    ldm_regs: int = 0  # bitmask for gpr
    vldm_regs: int = 0  # bitmask for flt (dbl use two bits)
    stm_regs: int = 0
    vstm_regs: int = 0
    stk_size: int = 0
    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID

    def FrameSize(self):
        # TODO: make sure stack is 8 byte aligned.
        num_gpr_regs = popcount(self.ldm_regs)
        num_flt_regs = popcount(self.vldm_regs)
        return 8 * num_flt_regs + 4 * num_gpr_regs + self.stk_size


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
                        gpr |= A32RegToAllocMask(reg.cpu_reg)
                    else:
                        flt |= A32RegToAllocMask(reg.cpu_reg)
    return gpr, flt


def FunComputeEmitContext(fun: ir.Fun) -> EmitContext:
    gpr_mask, flt_mask = _FunCpuRegStats(fun)
    must_save_link = not ir.FunIsLeaf(fun) or (
        (gpr_mask & _LINK_REG_MASK) != 0)
    gpr_mask &= GPR_LAC_REGS_MASK
    flt_mask &= FLT_LAC_REGS_MASK

    ctx = EmitContext()
    ctx.stm_regs = gpr_mask
    ctx.ldm_regs = gpr_mask

    ctx.vstm_regs = flt_mask
    ctx.vldm_regs = flt_mask
    if must_save_link:
        ctx.stm_regs |= _LINK_REG_MASK
        ctx.ldm_regs |= _PC_REG_MASK
    # Python 3.10 has int.bit_count():
    num_saved_regs = bin(ctx.ldm_regs).count(
        '1') + bin(ctx.vldm_regs).count('1')
    stk_size = fun.stk_size + 4 * num_saved_regs
    stk_size = (stk_size + 15) // 16 * 16
    stk_size -= 4 * num_saved_regs
    ctx.stk_size = stk_size
    return ctx
