from Base import cfg
from Base import ir
from Base import liveness
from Base import opcode_tab as o
from Base import reg_alloc
from Base import serialize

import dataclasses
from typing import List, Optional, Tuple
import enum
import functools
import operator


@enum.unique
class A64RegKind(enum.IntEnum):
    INVALID = 0
    GPR32 = 1
    GPR64 = 2
    FLT32 = 3
    FLT64 = 4


_GPR32_REGS = [ir.CpuReg(f"w{i}", i, A64RegKind.GPR32) for i in range(31)]
_GPR64_REGS = [ir.CpuReg(f"x{i}" if i != 31 else "sp", i, A64RegKind.GPR64)
               for i in range(32)]

_FLT32_REGS = [ir.CpuReg(f"s{i}", i, A64RegKind.GPR32) for i in range(32)]
_FLT64_REGS = [ir.CpuReg(f"d{i}", i, A64RegKind.GPR64) for i in range(32)]

# note: our calling convention does not completely match the official one
GPR32_PARAMETER_REGS = _GPR32_REGS[0:16]
GPR64_PARAMETER_REGS = _GPR64_REGS[0:16]

FLT32_PARAMETER_REGS = _FLT32_REGS[0:8] + _FLT32_REGS[16:32]
FLT64_PARAMETER_REGS = _FLT64_REGS[0:8] + _FLT64_REGS[16:32]

GPR64_CALLEE_SAVE_REGS = _GPR64_REGS[16:30]
FLT64_CALLEE_SAVE_REGS = _FLT64_REGS[8:16]


def RegsToMask(regs: List[ir.CpuReg]) -> int:
    return functools.reduce(operator.or_, (1 << r.no for r in regs), 0)


def MaskToGpr64Regs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _GPR64_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


def MaskToFlt64Regs(mask: int) -> List[ir.CpuReg]:
    out = []
    for reg in _FLT64_REGS:
        if ((1 << reg.no) & mask) != 0:
            out.append(reg)
    return out


_LINK_REG_MASK = 1 << 30
_GPR64_PARAMETER_REGS_MASK = RegsToMask(GPR64_PARAMETER_REGS)
_FLT64_PARAMETER_REGS_MASK = RegsToMask(FLT64_PARAMETER_REGS)

_GPR64_CALLEE_SAVE_REGS_MASK = RegsToMask(GPR64_CALLEE_SAVE_REGS)
_FLT64_CALLEE_SAVE_REGS_MASK = RegsToMask(FLT64_CALLEE_SAVE_REGS)

_KIND_TO_CPU_KIND = {
    o.DK.S8: A64RegKind.GPR32,
    o.DK.S16: A64RegKind.GPR32,
    o.DK.S32: A64RegKind.GPR32,
    o.DK.U8: A64RegKind.GPR32,
    o.DK.U16: A64RegKind.GPR32,
    o.DK.U32: A64RegKind.GPR32,
    #
    o.DK.U64: A64RegKind.GPR64,
    o.DK.S64: A64RegKind.GPR64,
    o.DK.A64: A64RegKind.GPR64,
    o.DK.C64: A64RegKind.GPR64,
    #
    o.DK.F32: A64RegKind.FLT32,
    o.DK.F64: A64RegKind.FLT64,
}

_KIND_TO_CPU_REG_LIST = {
    o.DK.S8: _GPR32_REGS,
    o.DK.S16: _GPR32_REGS,
    o.DK.S32: _GPR32_REGS,
    o.DK.U8: _GPR32_REGS,
    o.DK.U16: _GPR32_REGS,
    o.DK.U32: _GPR32_REGS,
    #
    o.DK.U64: _GPR64_REGS,
    o.DK.S64: _GPR64_REGS,
    o.DK.A64: _GPR64_REGS,
    o.DK.C64: _GPR64_REGS,
    #
    o.DK.F32: _FLT32_REGS,
    o.DK.F64: _FLT32_REGS,
}


def CpuRegForType(reg_kind: o.DK, cpu_reg_no: int) -> ir.CpuReg:
    pass


# Same for input and output refs
def GetCpuRegsForSignature(kinds: List[o.DK]) -> List[ir.CpuReg]:
    next_gpr = 0
    next_flt = 0
    out = []
    for k in kinds:
        if k == o.DK.F32:
            assert next_flt < len(FLT32_PARAMETER_REGS)
            cpu_reg = FLT32_PARAMETER_REGS[next_flt]
            next_flt += 1
        elif k == o.DK.F64:
            assert next_flt < len(FLT64_PARAMETER_REGS)
            cpu_reg = FLT64_PARAMETER_REGS[next_flt]
            next_flt += 1
        elif k == o.DK.S32 or k == o.DK.U32:
            assert next_gpr < len(GPR32_PARAMETER_REGS)
            cpu_reg = GPR32_PARAMETER_REGS[next_gpr]
            next_gpr += 1
        else:
            assert k in {o.DK.C64, o.DK.S64, o.DK.A64, o.DK.U64}
            assert next_gpr <= len(GPR64_PARAMETER_REGS)
            cpu_reg = GPR64_PARAMETER_REGS[next_gpr]
            next_gpr += 1
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
            reg_alloc.PreAllocation() for _ in range(len(_GPR64_REGS))]
        self._flt_reserved: List[reg_alloc.PreAllocation] = [
            reg_alloc.PreAllocation() for _ in range(len(_FLT64_REGS))]

    def get_available(self, lac, is_gpr) -> int:
        # TODO: use lac as fallback if no not_lac is available
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
        if cpu_reg.kind is A64RegKind.GPR32 or cpu_reg.kind is A64RegKind.GPR64:
            self._gpr_reserved[cpu_reg.no].add(lr)
        else:
            assert cpu_reg.kind is A64RegKind.FLT32 or cpu_reg.kind is A64RegKind.FLT64
            self._flt_reserved[cpu_reg.no].add(lr)

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        return 2 if kind == o.DK.F64 or kind == o.DK.F32 else 1

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        self.give_back_available_reg(cpu_reg)
        if cpu_reg.kind is A64RegKind.GPR32 or cpu_reg.kind is A64RegKind.GPR64:
            self._gpr_reserved[cpu_reg.no].current = 0
        else:
            assert cpu_reg.kind is A64RegKind.FLT32 or cpu_reg.kind is A64RegKind.FLT64
            self._flt_reserved[cpu_reg.no].current = 0

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.CpuReg:
        lac = liveness.LiveRangeFlag.LAC in lr.flags
        is_gpr = lr.reg.kind.flavor() != o.DK_FLAVOR_F
        available = self.get_available(lac, is_gpr)
        # print(f"GET {lr} {self}  avail:{available:x}")
        if lr.reg.kind == o.DK.F32 or lr.reg.kind == o.DK.F64:
            for n in range(len(_FLT64_REGS)):
                mask = 1 << n
                if available & mask == mask:
                    if not self._flt_reserved[n].has_conflict(lr):
                        self.set_available(lac, is_gpr, available & ~mask)
                        return _KIND_TO_CPU_REG_LIST[lr.reg.kind][n]
        else:
            for n in range(len(_GPR64_REGS)):
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
        reg_mask = 1 << cpu_reg.no
        if cpu_reg.kind is A64RegKind.FLT32 or cpu_reg.kind is A64RegKind.FLT64:
            is_gpr = False
            is_lac = (reg_mask & _GPR64_CALLEE_SAVE_REGS_MASK) != 0
        else:
            is_gpr = True
            is_lac = (reg_mask & _FLT64_CALLEE_SAVE_REGS_MASK) != 0
        available = self.get_available(is_lac, is_gpr)
        self.set_available(is_lac, is_gpr, available | reg_mask)
        # print (f"@@@@ adding {lac} {cpu_reg} {available | mask:x}")

    def __str__(self):
        gpr_lac, gpr_not_lac = self._gpr_available_lac, self._gpr_available_not_lac
        flt_lac, flt_not_lac = self._flt_available_lac, self._flt_available_not_lac
        return f"POOL gpr:{gpr_lac:x}/{gpr_not_lac:x}  flt:{flt_lac:x}/{flt_not_lac:x}"


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


def _BblRegAllocOrSpill(bbl: ir.Bbl, fun: ir.Fun) -> int:
    """Allocates regs to the intra bbl live ranges

    Note, this runs after global register allocation has occurred
    """
    # print ("\n".join(serialize.BblRenderToAsm(bbl)))

    live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out, True)
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

    # First reg-alloc path to determine if spilling is needed.
    # Note, global and fixed registers have already been assigned and will
    # be respected by the allocator.
    _RunLinearScan(bbl, fun, live_ranges, True,
                   _GPR64_CALLEE_SAVE_REGS_MASK, _GPR64_PARAMETER_REGS_MASK,
                   _FLT64_CALLEE_SAVE_REGS_MASK, _FLT64_PARAMETER_REGS_MASK)
    spilled_regs = _AssignAllocatedRegsAndReturnSpilledRegs(live_ranges)
    if spilled_regs:
        assert False
        # print (f"@@ adjusted spill count: {len(spilled_regs)} {spilled_regs}")
        reg_alloc.BblSpillRegs(bbl, fun, spilled_regs, o.DK.U32, "$spill")

        live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out, True)
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


def _FunCpuRegStats(fun: ir.Fun) -> Tuple[int, int]:
    gpr = 0
    flt = 0
    for bbl in fun.bbls:
        for ins in bbl.inss:
            for reg in ins.operands:
                if isinstance(reg, ir.Reg):
                    assert reg.HasCpuReg(), f"missing cpu reg for {reg} in {ins} {ins.operands}"
                    if reg.cpu_reg.kind in {A64RegKind.GPR32, A64RegKind.GPR64}:
                        gpr |= 1 << reg.cpu_reg.no
                    else:
                        flt |= 1 << reg.cpu_reg.no
    return gpr, flt


def _FunMustSaveLinkReg(fun) -> bool:
    for bbl in fun.bbls:
        for ins in bbl.inss:
            # Note, syscalls do not clobber lr
            if ins.opcode is o.BSR or ins.opcode is o.JSR:
                return True
    return False


@dataclasses.dataclass()
class EmitContext:
    """Grab bag of data needed for emitting instructions"""
    gpr64_reg_mask: int = 0  # bitmask for saved gpr
    flt64_reg_mask: int = 0  # bitmask for saved flt (dbl, etc.) only lower 64bits are saved
    stk_size: int = 0

    scratch_cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID


def FunComputeEmitContext(fun: ir.Fun) -> EmitContext:
    gpr_mask, flt_mask = _FunCpuRegStats(fun)

    gpr_mask &= _GPR64_CALLEE_SAVE_REGS_MASK
    flt_mask &= _FLT64_CALLEE_SAVE_REGS_MASK
    if not ir.FunIsLeaf(fun):
        gpr_mask |= _LINK_REG_MASK
    stk_size = (fun.stk_size + 15) // 16 * 16
    return EmitContext(gpr_mask, flt_mask, stk_size)
