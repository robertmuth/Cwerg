"""Helpers for A32 Register management"""

from Base import cfg
from Base import ir
from Base import liveness
from Base import opcode_tab as o
from Base import reg_alloc
from Base import serialize

import operator
import dataclasses
import functools
from typing import List, Optional, Tuple
import enum

_GPR_REG_NAMES = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
                  "r8", "r9", "r10", "r11", "r12", "sp", "lr", "pc"]


@enum.unique
class A32RegKind(enum.IntEnum):
    INVALID = 0
    GPR = 1
    FLT = 2
    DBL = 2 + 16


_GPR_REGS = [ir.CpuReg(name, i, A32RegKind.GPR) for i, name in
             enumerate(_GPR_REG_NAMES)]
_FLT_REGS = [ir.CpuReg(f"s{i}", i, A32RegKind.FLT) for i in range(32)]
DBL_REGS = [ir.CpuReg(f"d{i}", i, A32RegKind.DBL) for i in range(16)]

CPU_REGS = {**{r.name: r for r in _GPR_REGS},
            **{r.name: r for r in _FLT_REGS},
            **{r.name: r for r in DBL_REGS}}


def A32RegToAllocMask(reg: ir.CpuReg) -> int:
    """ Note that for DBL and FLT this matches the architectural overlap

    For GPR this produces the right mask for ldm/stm
    """
    if reg.kind is A32RegKind.DBL:
        return 3 << (reg.no * 2)
    else:
        return 1 << reg.no


def A32RegsToAllocMask(regs: List[ir.CpuReg]) -> int:
    return functools.reduce(operator.or_,
                            (A32RegToAllocMask(r) for r in regs), 0)


PC_REG = _GPR_REGS[15]
LINK_REG = _GPR_REGS[14]
STACK_REG = _GPR_REGS[13]
GPR_SCRATCH_REG = _GPR_REGS[12]

# this not compatible with any ABI
GPR_CALLEE_SAVE_REGS = _GPR_REGS[6:12]
FLT_CALLEE_SAVE_REGS = _FLT_REGS[16:]
DBL_CALLEE_SAVE_REGS = DBL_REGS[8:]

GPR_PARAMETER_REGS = _GPR_REGS[0:6]
GPR_NOT_LAC_REGS = GPR_PARAMETER_REGS + [GPR_SCRATCH_REG, LINK_REG]

FLT_PARAMETER_REGS = _FLT_REGS[0:16]
DBL_PARAMETER_REGS = DBL_REGS[0:8]

_LINK_REG_MASK = A32RegToAllocMask(LINK_REG)
_FLT_CALLEE_SAVE_REGS_MASK = A32RegsToAllocMask(FLT_CALLEE_SAVE_REGS)
_GPR_CALLEE_SAVE_REGS_MASK = A32RegsToAllocMask(GPR_CALLEE_SAVE_REGS)

_GPR_NOT_LAC_REGS_MASK = A32RegsToAllocMask(GPR_NOT_LAC_REGS)
_FLT_PARAMETER_REGS_MASK = A32RegsToAllocMask(FLT_PARAMETER_REGS)


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
    return _FLT_REGS[start], count


# Same for input and output refs
def GetCpuRegsForSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    gpr = 0
    flt = 0
    out = []
    for k in kinds:
        if k == o.DK.F32:
            assert flt < len(FLT_PARAMETER_REGS)
            cpu_reg = FLT_PARAMETER_REGS[flt]
            flt += 1
        elif k == o.DK.F64:
            # we are wasting a reg here. Can be avoided by moving f64 before all f32 params
            if flt & 1 == 1:
                flt += 1
            assert flt // 2 < len(DBL_PARAMETER_REGS)
            cpu_reg = DBL_PARAMETER_REGS[flt // 2]
            flt += 2
        else:
            assert k in {o.DK.C32, o.DK.S32, o.DK.A32, o.DK.U32}
            assert gpr <= len(GPR_PARAMETER_REGS)
            cpu_reg = GPR_PARAMETER_REGS[gpr]
            gpr += 1
        out.append(cpu_reg)
    return out


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
        params += GetCpuRegsForSignature(callee.output_types)
    return None


def FunPopargConversion(fun: ir.Fun):
    return ir.FunGenericRewrite(fun, _InsPopargConversion,
                                params=GetCpuRegsForSignature(fun.input_types))


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
        params += GetCpuRegsForSignature(callee.input_types)
    elif ins.opcode is o.RET:
        params += GetCpuRegsForSignature(fun.output_types)
    return None


def FunPushargConversion(fun: ir.Fun):
    return ir.FunGenericRewriteReverse(fun, _InsPushargConversionReverse,
                                       params=[])


class RegPoolArm(reg_alloc.RegPool):
    """
    We also distinguish if the register is  lac (live across calls)
    """

    def __init__(self, fun: ir.Fun, bbl: ir.Bbl, allow_spilling,
                 gpr_available_lac: int, gpr_available_not_lac: int, flt_available_lac: int,
                 flt_available_not_lac: int):
        super(RegPoolArm, self).__init__()
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

    def get_available(self, lac, is_gpr) -> int:
        # TODO: use lac as fallabck if no not_lac is available
        if is_gpr:
            return self._gpr_available_lac if lac else self._gpr_available_not_lac
        else:
            return self._flt_available_lac if lac else self._flt_available_not_lac

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
        if cpu_reg.kind is A32RegKind.GPR:
            self._gpr_reserved[cpu_reg.no].add(lr)
        elif cpu_reg.kind is A32RegKind.FLT:
            self._flt_reserved[cpu_reg.no].add(lr)
        else:
            assert cpu_reg.kind is A32RegKind.DBL
            self._flt_reserved[cpu_reg.no * 2].add(lr)
            self._flt_reserved[cpu_reg.no * 2 + 1].add(lr)

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return 2 if kind == o.DK.F64 or kind == o.DK.F32 else 1

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        self.give_back_available_reg(cpu_reg)
        if cpu_reg.kind is A32RegKind.GPR:
            self._gpr_reserved[cpu_reg.no].current = 0
        elif cpu_reg.kind is A32RegKind.FLT:
            self._flt_reserved[cpu_reg.no].current = 0
        else:
            self._flt_reserved[cpu_reg.no * 2].current = 0
            self._flt_reserved[cpu_reg.no * 2 + 1].current = 0

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.CpuReg:
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_F
        available = self.get_available(lac, is_gpr)
        # print(f"GET {lr} {self}  avail:{available:x}")
        if lr.reg.kind == o.DK.F64:
            for n in range(len(DBL_REGS)):
                mask = 3 << (n * 2)  # two adjacent bit at an even bit pos
                if available & mask == mask:
                    if (not self._flt_reserved[n * 2 + 0].has_conflict(lr) and
                            not self._flt_reserved[n * 2 + 1].has_conflict(lr)):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return DBL_REGS[n]
        elif lr.reg.kind == o.DK.F32:
            for n in range(len(_FLT_REGS)):
                mask = 1 << n
                if available & mask == mask:
                    if not self._flt_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return _FLT_REGS[n]
        else:
            for n in range(len(_GPR_REGS)):
                mask = 1 << n
                if mask & available == mask:
                    if not self._gpr_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return _GPR_REGS[n]
        if self._allow_spilling:
            return ir.CPU_REG_SPILL
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("\n".join(serialize.BblRenderToAsm(self._bbl)))
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        assert False, f"in {self._fun.name}:{self._bbl.name} no reg available for {lr} in {self}"

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        mask = A32RegToAllocMask(cpu_reg)
        if cpu_reg.kind == A32RegKind.GPR:
            is_gpr = True
            is_lac = (mask & _GPR_CALLEE_SAVE_REGS_MASK) != 0
        else:
            is_gpr = False
            is_lac = (mask & _FLT_CALLEE_SAVE_REGS_MASK) != 0
        available = self.get_available(is_lac, is_gpr)
        self.set_available(is_lac, is_gpr, available | mask)
        # print (f"@@@@ adding {lac} {cpu_reg} {available | mask:x}")

    def __str__(self):
        gpr_lac, gpr_not_lac = self._gpr_available_lac, self._gpr_available_not_lac
        flt_lac, flt_not_lac = self._flt_available_lac, self._flt_available_not_lac
        return f"POOL gpr:{gpr_lac:x}/{gpr_not_lac:x}  flt:{flt_lac:x}/{flt_not_lac:x}"


_SUPPORTED_FLT_REGS = {o.DK.F64, o.DK.F32}

_SUPPORTED_GPR_REGS = {o.DK.A32, o.DK.C32,
                       o.DK.S8, o.DK.S16, o.DK.S32,
                       o.DK.U8, o.DK.U16, o.DK.U32}

_SUPPORTED_REGS = _SUPPORTED_FLT_REGS | _SUPPORTED_GPR_REGS


def _RunLinearScan(bbl: ir.Bbl, fun: ir.Fun, live_ranges, allow_spilling,
                   gpr_regs_lac: int, gpr_regs_not_lac: int,
                   flt_regs_lac: int,
                   flt_regs_not_lac: int):
    # print("\n".join(serialize.BblRenderToAsm(bbl)))
    pool = RegPoolArm(fun, bbl, allow_spilling,
                      gpr_regs_lac, gpr_regs_not_lac, flt_regs_lac, flt_regs_not_lac)
    for lr in live_ranges:
        # since we are operating on a BBL we cannot change LifeRanges
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
        if reg.kind is o.DK.F64:
            flt_not_lac_reserve = 2
        elif reg.kind is o.DK.F32:
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

    live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out, True)
    live_ranges.sort()
    for lr in live_ranges:
        # since we are operating on a BBL we cannot change LifeRanges
        # extending beyond the BBL.
        # reg_kinds_fixed (e.g. Machine) regs are assumed to be
        # pre-allocated and will not change
        if lr.reg.HasCpuReg():
            lr.flags |= liveness.LiveRangeFlag.PRE_ALLOC
            lr.cpu_reg = lr.reg.cpu_reg
        # print (repr(lr))
    _RunLinearScan(bbl, fun, live_ranges, True,
                   _GPR_CALLEE_SAVE_REGS_MASK, _GPR_NOT_LAC_REGS_MASK,
                   _FLT_CALLEE_SAVE_REGS_MASK, _FLT_PARAMETER_REGS_MASK)
    spilled_regs = _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges)
    if spilled_regs:
        # print (f"@@ adjusted spill count: {len(spilled_regs)} {spilled_regs}")
        reg_alloc.BblSpillRegs(bbl, fun, spilled_regs, o.DK.U32)

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out, True)
        live_ranges.sort()
        for lr in live_ranges:
            # since we are operating on a BBL we cannot change LifeRanges
            # extending beyond the BBL.
            # reg_kinds_fixed (e.g. Machine) regs are assumed to be
            # pre-allocated and will not change
            if lr.reg.HasCpuReg():
                lr.flags |= liveness.LiveRangeFlag.PRE_ALLOC
                lr.cpu_reg = lr.reg.cpu_reg
        _RunLinearScan(bbl, fun, live_ranges, False,
                       _GPR_CALLEE_SAVE_REGS_MASK, _GPR_NOT_LAC_REGS_MASK,
                       _FLT_CALLEE_SAVE_REGS_MASK, _FLT_PARAMETER_REGS_MASK)
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


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    ldm_regs: int = 0  # bitmask for gpr
    vldm_regs: int = 0  # bitmask for flt (dbl use two bits)
    stm_regs: int = 0
    vstm_regs: int = 0
    stk_size: int = 0
    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID


def _FunCpuRegStats(fun: ir.Fun) -> Tuple[int, int]:
    gpr = 0
    flt = 0
    for bbl in fun.bbls:
        for ins in bbl.inss:
            for reg in ins.operands:
                if isinstance(reg, ir.Reg):
                    assert reg.HasCpuReg(), f"missing cpu reg for {reg} in {ins} {ins.operands}"
                    if reg.cpu_reg.kind == A32RegKind.GPR:
                        gpr |= A32RegToAllocMask(reg.cpu_reg)
                    else:
                        flt |= A32RegToAllocMask(reg.cpu_reg)
    return gpr, flt


def _FunMustSaveLinkReg(fun) -> bool:
    for bbl in fun.bbls:
        for ins in bbl.inss:
            # Note, syscalls do not clobber lr
            if ins.opcode is o.BSR or ins.opcode is o.JSR:
                return True
    return False


def FunComputeEmitContext(fun: ir.Fun):
    gpr_mask, flt_mask = _FunCpuRegStats(fun)
    must_save_link = _FunMustSaveLinkReg(fun) or ((gpr_mask & _LINK_REG_MASK) != 0)
    gpr_mask &= _GPR_CALLEE_SAVE_REGS_MASK
    flt_mask &= _FLT_CALLEE_SAVE_REGS_MASK
    ctx = EmitContext()
    ctx.stm_regs = gpr_mask
    ctx.ldm_regs = gpr_mask
    ctx.vstm_regs = flt_mask
    ctx.vldm_regs = flt_mask
    if must_save_link:
        ctx.stm_regs |= A32RegToAllocMask(LINK_REG)
        ctx.ldm_regs |= A32RegToAllocMask(PC_REG)
    # Python 3.10 has int.bit_count():
    num_saved_regs = bin(ctx.ldm_regs).count('1') + bin(ctx.vldm_regs).count('1')
    stk_size = fun.stk_size + 4 * num_saved_regs
    stk_size = (stk_size + 15) // 16 * 16
    stk_size -= 4 * num_saved_regs
    ctx.stk_size = stk_size
    return ctx
