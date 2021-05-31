"""This file contains code for Register Allocation/Assignment """
from typing import List, Dict, Optional

from Base import ir
from Base import liveness
from Base import opcode_tab as o
from Base.liveness import LiveRange


class PreAllocation:
    """Pre-allocation manages a collection of LiveRanges

    We want to query this set for overlap with a given lr.
    Also the queries are against monotonically increasing lrs.
    """

    def __init__(self):
        self.ranges: List[LiveRange] = []  # must be sorted ow. has_conflict wont work
        self.current = 0

    def add(self, lr: LiveRange):
        if self.ranges:
            assert self.ranges[-1] < lr
        self.ranges.append(lr)

    def has_conflict(self, lr: LiveRange) -> bool:
        while self.current < len(self.ranges):
            top = self.ranges[self.current]
            # consider two ranges:
            # lr:  [def:11 - last_use:12]
            # top: [def:10 - last_use:11]
            # there is no overlap and since subsequent lrs will have bigger last_use
            # components we can drop

            if top.last_use_pos <= lr.def_pos:
                self.current += 1
                continue
            # we know top.last_use_pos > lr.def_pos
            return top.def_pos < lr.last_use_pos
        return False

    def __str__(self):
        return f"PRE-ALLOCATED: {self.ranges}"


class RegPool:
    """RegPool interface manages register available for allocation
     while running a linear scan allocator.

     Supports the use case where certain ranges are reserved meaning, the
     register assigned to that region cannot be changed.
     This is the reason why the pop() member takes a live_range parameter.
     """

    def get_available_reg(self, lr: LiveRange) -> ir.CpuReg:
        assert False, "must be implemented by subclass"
        return ir.CPU_REG_INVALID

    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        assert False, "must be implemented by subclass"

    def get_cpu_reg_family(self, kind: o.DK) -> int:
        assert False, "must be implemented by subclass"

    def backtrack_reset(self, cpu_reg: ir.CpuReg):
        assert False, "must be implemented by subclass"


PRE_ALLOC = liveness.LiveRangeFlag.PRE_ALLOC
IGNORE = liveness.LiveRangeFlag.IGNORE


def _HandleUseLiveRange(lr_use: LiveRange, pool, debug):
    for lr in lr_use.uses:
        assert lr_use.reg is ir.REG_INVALID
        if lr.last_use_pos != lr_use.def_pos:  # we only care about end of use
            continue
        if IGNORE in lr.flags:
            continue
        c = lr.cpu_reg
        if PRE_ALLOC in lr.flags:
            assert c is not ir.CPU_REG_INVALID
            assert c is not ir.CPU_REG_SPILL
            assert c == lr.reg.cpu_reg
        if c is not ir.CPU_REG_SPILL:
            pool.give_back_available_reg(c)
        if debug:
            debug(lr, f"end {c.name}")


def _HandleDefLiveRange(lr: LiveRange, pool, debug):
    assert lr.cpu_reg is ir.CPU_REG_INVALID, f"{lr} was already assigned"
    lr.cpu_reg = pool.get_available_reg(lr)
    assert lr.cpu_reg is not ir.CPU_REG_INVALID
    if debug:
        debug(lr, f"start {lr.cpu_reg.name}")
    if lr.last_use_pos is liveness.NO_USE and lr.cpu_reg is not ir.CPU_REG_SPILL:
        pool.give_back_available_reg(lr.cpu_reg)
        if debug:
            debug(lr, f"no use {lr.cpu_reg.name}")


def RegisterAssignerLinearScan(live_ranges: List[LiveRange], pool: RegPool, debug=None):
    """
    Standard Linear Scan Interval Coloring algorithm.
    The allocator:
     * will only allocate registers for regions not marked `IGNORE`
     * pre-allocated regs are made available for those ranges where they are not used

    Updates the live_range.cpu_reg field with the  allocated cpu_reg
    or CPU_REG_UNASSIGNED when no reg was available
    """
    live_ranges.sort()
    for lr in live_ranges:
        if lr.uses:
            _HandleUseLiveRange(lr, pool, debug)
        else:
            if PRE_ALLOC in lr.flags or IGNORE in lr.flags:
                continue
            _HandleDefLiveRange(lr, pool, debug)


def _SpillEarlierLiveRange(reg: ir.Reg, pos: int, i: int, live_ranges: List[LiveRange],
                           pool: RegPool, do_not_spill: List[LiveRange], debug) -> int:

    kind_wanted = pool.get_cpu_reg_family(reg.kind)
    for i in range(i, -1, -1):  # count down to zero!
        lr = live_ranges[i]
        if (lr in do_not_spill or
                lr.is_use_lr() or
                IGNORE in lr.flags or
                PRE_ALLOC in lr.flags or
                lr.cpu_reg is ir.CPU_REG_SPILL or
                lr.last_use_pos <= pos or
                pool.get_cpu_reg_family(lr.reg.kind) != kind_wanted):
            continue
        if debug:
            debug(lr, f"spilling previously assigned {lr.cpu_reg.name}")

        pool.give_back_available_reg(lr.cpu_reg)
        lr.cpu_reg = ir.CPU_REG_SPILL
        return
    assert False, f"failed to free up reg for {reg}"


# def _BackTrack(reg: ir.Reg, pos: int, i: int, live_ranges: List[LiveRange], pool: RegPool, debug) -> int:
#     kind_wanted = pool.get_cpu_reg_family(reg.kind)
#     for i in range(i, -1, -1):  # count down to zero!
#         lr = live_ranges[i]
#         if lr.uses or IGNORE in lr.flags or PRE_ALLOC in lr.flags:
#             continue
#         if debug:
#             print(f"## UNDO {lr}")
#
#         if lr.cpu_reg is ir.CPU_REG_SPILL:
#             continue
#         pool.backtrack_reset(lr.cpu_reg)
#         lr.cpu_reg = ir.CPU_REG_SPILL
#         if lr.last_use_pos <= pos or pool.get_cpu_reg_family(lr.reg.kind) != kind_wanted:
#             continue
#         # This range may free up a reg that could help us make progress later on - spill it
#         return i + 1


def _HandleDefLiveRangeFancy(i: int, lr: LiveRange, live_ranges: List[LiveRange], pool,
                             debug):
    _HandleDefLiveRange(lr, pool, debug)
    if lr.cpu_reg is ir.CPU_REG_SPILL:
        # we need to spill but we still need a tmp reg
        tmp_lr = LiveRange(lr.def_pos, liveness.NO_USE, lr.reg, 0)
        tmp_reg = pool.get_available_reg(tmp_lr)
        if tmp_reg is ir.CPU_REG_SPILL:
            if debug:
                debug(lr, "no spill scratch reg for def")
            # backtracking provides better allocation but is slow (potentially exponentially so)
            _SpillEarlierLiveRange(lr.reg, lr.def_pos, i - 1, live_ranges, pool, [], debug)
            tmp_reg = pool.get_available_reg(tmp_lr)
            assert tmp_reg is not ir.CPU_REG_SPILL
        if debug:
            debug(lr, f"spill scratch reg for def: {tmp_reg.name}")
        pool.give_back_available_reg(tmp_reg)
    return i + 1


def _HandleUseLiveRangeFancy(i: int, lr_use: LiveRange, live_ranges: List[LiveRange], pool,
                             debug):
    """return are reg """
    spill_tmp_regs: List[ir.CpuReg] = []
    do_not_spill = []
    for x, lr in enumerate(lr_use.uses):
        if IGNORE in lr.flags or PRE_ALLOC in lr.flags or lr.cpu_reg is not ir.CPU_REG_SPILL:
            do_not_spill.append(lr)
            continue
        # The reg in question was spilled and we have a use here.
        # we need a tmp reg to load the spilled reg - make sure we can get one
        # Note: we backtrack one register at a time which simplifies the code but
        # may not be the most efficient.
        tmp_lr = LiveRange(lr_use.def_pos, liveness.NO_USE, lr.reg, 0)
        tmp_reg = pool.get_available_reg(tmp_lr)
        if tmp_reg is ir.CPU_REG_SPILL:
            if debug:
                debug(lr, f"[{x}, def:{lr_use.def_pos}] no spill scratch reg for use")
            # backtracking provides better allocation but is slow (potentially exponentially so)
            # TODO: make a second pass to maybe undo some spilling
            # TODO: the earlier spilled reg may be a "lac" but we may request a non_lac
            _SpillEarlierLiveRange(lr.reg, lr.def_pos, i - 1, live_ranges, pool, do_not_spill, debug)
            tmp_reg = pool.get_available_reg(tmp_lr)
            assert tmp_reg is not ir.CPU_REG_SPILL

        spill_tmp_regs.append(tmp_reg)
        if debug:
            debug(lr, f"[{x}, def:{lr_use.def_pos} {lr.reg}] spill scratch reg for use: {tmp_reg.name}")
    _HandleUseLiveRange(lr_use, pool, debug)

    for tmp_reg in spill_tmp_regs:
        pool.give_back_available_reg(tmp_reg)
    return i + 1


def RegisterAssignerLinearScanFancy(live_ranges: List[LiveRange], pool: RegPool, debug=None):
    """
    Standard Linear Scan Interval Coloring algorithm with special spill handling

    When a LiveRange is spilled we still need tmp regs (with very small live-ranges)
    at each use and def of the original regs.
    This version of linear scan takes this into account. So that we so not have to reserve
    regs upfront to play the role of tmp regs.
    If not tmp regs can be found the algorithm will back track and convert an earlier
    allocation into a spill.

    As long as there are at least 4 register available per register class this should
    always work as the worst case for spilling are the cmp opcodes which have 4 inputs.

    After this function has run all liveranges which are not PRE_ALLOCATED or IGNORE should
    have lr.cpu_reg is ir.CPU_REG_INVALID
    """
    live_ranges.sort()
    i = 0
    while i < len(live_ranges):
        lr = live_ranges[i]
        if lr.uses:
            i = _HandleUseLiveRangeFancy(i, lr, live_ranges, pool, debug)
        else:
            if PRE_ALLOC in lr.flags or IGNORE in lr.flags:
                i += 1
                continue
            i = _HandleDefLiveRangeFancy(i, lr, live_ranges, pool, debug)


def InsSpillRegs(ins: ir.Ins, fun: ir.Fun, zero_const, reg_to_stk) -> Optional[List[ir.Ins]]:
    before: List[ir.Ins] = []
    after: List[ir.Ins] = []
    num_defs = ins.opcode.def_ops_count()
    for n, reg in reversed(list(enumerate(ins.operands))):
        if not isinstance(reg, ir.Reg):
            continue
        stk = reg_to_stk.get(reg)
        if stk is None:
            continue
        if n < num_defs:
            scratch = fun.GetScratchReg(reg.kind, "stspill", False)
            ins.operands[n] = scratch
            after.append(ir.Ins(o.ST_STK, [stk, zero_const, scratch]))
        else:
            scratch = fun.GetScratchReg(reg.kind, "ldspill", False)
            ins.operands[n] = scratch
            before.append(ir.Ins(o.LD_STK, [scratch, stk, zero_const]))
    if before or after:
        return before + [ins] + after
    else:
        return None


def BblSpillRegs(bbl: ir.Bbl, fun: ir.Fun, regs: List[ir.Reg], offset_kind: o.DK, prefix) -> int:
    reg_to_stk: Dict[ir.Reg, ir.Stk] = {}
    for reg in regs:
        size = ir.OffsetConst(reg.kind.bitwidth() // 8)
        stk = ir.Stk(f"{prefix}_{reg.name}", size, size)
        reg_to_stk[reg] = stk
        fun.AddStk(stk)
    ir.BblGenericRewrite(bbl, fun, InsSpillRegs, zero_const=ir.Const(offset_kind, 0),
                         reg_to_stk=reg_to_stk)


def FunSpillRegs(fun: ir.Fun, offset_kind: o.DK, regs: List[ir.Reg], prefix) -> int:
    reg_to_stk: Dict[ir.Reg, ir.Stk] = {}
    for reg in regs:
        size = ir.OffsetConst(reg.kind.bitwidth() // 8)
        stk = ir.Stk(f"{prefix}_{reg.name}", size, size)
        reg_to_stk[reg] = stk
        fun.AddStk(stk)
    return ir.FunGenericRewrite(fun, InsSpillRegs, zero_const=ir.Const(offset_kind, 0),
                                reg_to_stk=reg_to_stk)

