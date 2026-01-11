#!/bin/env python3

import collections
import sys
from typing import List, Dict

from BE.Base import cfg
from BE.Base import ir
from BE.Base import liveness
from BE.Base import lowering
from IR import opcode_tab as o
from BE.Base import reaching_defs
from BE.Base import reg_alloc
from BE.Base import reg_stats
from BE.Base import sanity
from BE.Base import serialize
from BE.Base import canonicalize

# This is just to get an idea of how much registers we need
# it is only used for informational purposes
REG_KIND_MAP_TYPICAL: Dict[o.DK, int] = {
    o.DK.S8: o.DK.S32.value,
    o.DK.S16: o.DK.S32.value,
    o.DK.S32: o.DK.S32.value,
    o.DK.S64: o.DK.S64.value,

    o.DK.U8: o.DK.S32.value,
    o.DK.U16: o.DK.S32.value,
    o.DK.U32: o.DK.S32.value,
    o.DK.U64: o.DK.S64.value,

    o.DK.A32: o.DK.S32.value,
    o.DK.A64: o.DK.S64.value,

    o.DK.C32: o.DK.S32.value,
    o.DK.C64: o.DK.S64.value,

    o.DK.R32: o.DK.R32.value,
    o.DK.R64: o.DK.R64.value,
}


class RegPoolSimple(reg_alloc.RegPool):
    """Simplified version of CodeGenA32/regs.py
    A simple register re-allocator to exercise the allocation framework for testing.
    The allocator may reduce the number of registers used. However thia makes reaching def
    based optimization less effective and hence should be run toward the end of the
    optimization phase.

    Note
     * this is ignore live across call issues as it does not deal with machine regs
     * add_reserved_range and add_available_reg must be called before
           get_available_reg and give_back_available_reg
    """

    def __init__(self):
        super(reg_alloc.RegPool, self).__init__()
        self._available: Dict[o.DK, List[ir.Reg]] = collections.defaultdict(
            list)
        self.reserved: Dict[
            ir.Reg, reg_alloc.PreAllocation] = collections.defaultdict(
            reg_alloc.PreAllocation)

    def add_reserved_range(self, lr: reg_alloc.LiveRange):
        """mark a live range as reserved meaning we cannot make a register assignment
        in conflict with this range"""
        self.reserved[lr.reg].add(lr)

    def add_available_reg(self, reg):
        """add to the pool of available regs"""
        available = self._available[reg.kind]
        assert reg not in available
        available.append(reg)

    def get_available_reg(self, lr: reg_alloc.LiveRange) -> ir.Reg:
        available = self._available[lr.reg.kind]
        # try to re-use the most recently given back regs
        for n, reg in enumerate(reversed(available)):
            reserved = self.reserved.get(reg)
            if reserved is None or not reserved.has_conflict(lr):
                return available.pop(-n - 1)
        assert False
        return ir.CPU_REG_INVALID

    def give_back_available_reg(self, reg: ir.Reg, lr: reg_alloc.LiveRange):
        available = self._available[reg.kind]
        # it seems a bit odd to re-add a reg which is already in the pool
        # but this can happen due to reserved regions
        # we need to make sure only one copy of the reg is in the pool
        if reg in available:
            available.remove(reg)
        available.append(reg)


def FunCfgInit(fun: ir.Fun, unit: ir.Unit):
    cfg.FunSplitBblsAtTerminators(fun)
    cfg.FunInitCFG(fun)
    cfg.FunRemoveUnconditionalBranches(fun)
    cfg.FunRemoveEmptyBbls(fun)
    sanity.FunCheck(fun, unit, check_cfg=True,
                    check_push_pop=True,
                    check_fallthroughs=False)


def UnitCfgInit(unit: ir.Unit):
    for fun in unit.funs:
        if fun.kind is o.FUN_KIND.NORMAL:
            FunCfgInit(fun, unit)


def FunCfgExit(fun: ir.Fun, unit: ir.Unit):
    cfg.FunAddUnconditionalBranches(fun)
    sanity.FunCheck(fun, unit, check_fallthroughs=True)


def UnitCfgExit(unit: ir.Unit):
    for fun in unit.funs:
        if fun.kind is o.FUN_KIND.NORMAL:
            FunCfgExit(fun, unit)


def FunOptBasic(fun: ir.Fun, opt_stats: Dict[str, int],
                allow_conv_conversion: bool):
    opt_stats["merge_move"] += reaching_defs.FunMergeMoveWithSrcDef(fun)

    opt_stats["canonicalized"] += canonicalize.FunCanonicalize(fun)
    opt_stats["strength_red"] += lowering.FunStrengthReduction(fun)

    opt_stats["empty_bbls"] = cfg.FunRemoveEmptyBbls(fun)
    opt_stats["unreachable_bbls"] = cfg.FunRemoveUnreachableBbls(fun)
    reaching_defs.FunComputeReachingDefs(fun)
    reaching_defs.FunCheckReachingDefs(fun)
    opt_stats["reg_prop"] = reaching_defs.FunPropagateRegs(fun)
    opt_stats["const_prop"] += reaching_defs.FunPropagateConsts(fun)

    opt_stats["const_fold"] += reaching_defs.FunConstantFold(
        fun, allow_conv_conversion)

    opt_stats["canonicalized"] += canonicalize.FunCanonicalize(fun)
    opt_stats["strength_red"] += lowering.FunStrengthReduction(fun)

    opt_stats["ls_st_simplify"] += reaching_defs.FunLoadStoreSimplify(fun)

    opt_stats["move_elim"] += lowering.FunMoveElimination(fun)

    liveness.FunComputeLivenessInfo(fun)

    opt_stats["useless"] = liveness.FunRemoveUselessInstructions(fun)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunComputeRegStatsLAC(fun)

    opt_stats["dropped_regs"] += reg_stats.FunDropUnreferencedRegs(fun)
    opt_stats["separated_regs"] += reg_stats.FunSeparateLocalRegUsage(fun)


def UnitOptBasic(unit: ir.Unit, dump_reg_stats) -> Dict[str, int]:
    cfg.UnitRemoveUnreachableCode(unit, [unit.fun_syms["main"]])
    opt_stats: Dict[str, int] = collections.defaultdict(int)
    for fun in unit.funs:
        if fun.kind is not o.FUN_KIND.NORMAL:
            continue
        FunOptBasic(fun, opt_stats, allow_conv_conversion=True)
        if dump_reg_stats:
            reg_stats.FunComputeRegStatsExceptLAC(fun)
            liveness.FunComputeLivenessInfo(fun)
            reg_stats.FunComputeRegStatsLAC(fun)
            rs = reg_stats.FunCalculateRegStats(fun)
            print(f"# {fun.name:30} RegStats: {rs}")
    return opt_stats


def FunOpt(fun: ir.Fun, opt_stats: Dict[str, int]):
    FunOptBasic(fun, opt_stats, allow_conv_conversion=True)
    lowering.FunRegWidthWidening(fun, o.DK.U8, o.DK.U32)
    lowering.FunRegWidthWidening(fun, o.DK.S8, o.DK.S32)
    lowering.FunRegWidthWidening(fun, o.DK.U16, o.DK.U32)
    lowering.FunRegWidthWidening(fun, o.DK.S16, o.DK.S32)

    FunOptBasic(fun, opt_stats, allow_conv_conversion=False)

    # non_scratch = set()
    # for reg in fun.regs:
    #     if reg.name.startswith("%scratch"):
    #         continue
    #     non_scratch.add(reg.name)
    # liveness.FunSpillRegs(fun, non_scratch, unit)


def UnitOpt(unit: ir.Unit, dump_reg_stats) -> Dict[str, int]:
    cfg.UnitRemoveUnreachableCode(unit, [unit.fun_syms["main"]])
    opt_stats: Dict[str, int] = collections.defaultdict(int)
    for fun in unit.funs:
        if fun.kind is not o.FUN_KIND.NORMAL:
            continue
        FunOpt(fun, opt_stats)
        if dump_reg_stats:
            local_stats = reg_stats.FunComputeBblRegUsageStats(
                fun, REG_KIND_MAP_TYPICAL)
            loc_lac = sum(
                count for (kind, lac), count in local_stats.items() if lac)
            loc_not_lac = sum(
                count for (kind, lac), count in local_stats.items() if not lac)

            # computes max number of
            reg_stats.FunComputeRegStatsExceptLAC(fun)
            reg_stats.FunComputeRegStatsLAC(fun)
            rs = reg_stats.FunCalculateRegStats(fun)
            print(
                f"# {fun.name:30} RegStats: {rs}  {loc_lac:2}/{loc_not_lac:2}")
    return opt_stats


def main(argv):
    mode = "optimize"
    if argv:
        mode = argv.pop(0)

    unit = serialize.UnitParseFromAsm(sys.stdin)
    if mode == "optimize":
        UnitCfgInit(unit)
        unit_stats = UnitOpt(unit, True)
        UnitCfgExit(unit)
        print("\n".join(serialize.UnitRenderToASM(unit)))
    elif mode == "optlite":
        UnitCfgInit(unit)
        unit_stats = UnitOptBasic(unit, True)
        UnitCfgExit(unit)
        print("\n".join(serialize.UnitRenderToASM(unit)))
    elif mode == "optimize_stats":
        UnitCfgInit(unit)
        unit_stats = UnitOpt(unit, True)
        UnitCfgExit(unit)
        print("\n".join(serialize.UnitRenderToASM(unit)))
        print(f"# STATS:")
        for key, val in unit_stats.items():
            print(f"#  {key}: {val}")
    elif mode == "serialize":
        print("\n".join(serialize.UnitRenderToASM(unit)))
    elif mode == "cfg":
        UnitCfgInit(unit)
        print("\n".join(serialize.UnitRenderToASM(unit)))
    elif mode == "cfg2":
        UnitCfgInit(unit)
        UnitCfgExit(unit)
        print("\n".join(serialize.UnitRenderToASM(unit)))
    else:
        assert False, f"unknown mode: [{mode}]"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
