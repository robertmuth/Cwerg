import collections
import dataclasses
from typing import List, Dict, Optional, Tuple, Set

from Base import canonicalize
from Base import reg_alloc
from Base import ir
from Base import liveness
from Base import lowering
from Base import opcode_tab as o
from Base import reg_stats
from Base import sanity
from Base import optimize
from Base import serialize
from CodeGenA32 import isel_tab
from CodeGenA32 import regs

_DUMMY_A32 = ir.Reg("dummy", o.DK.A32)
_ZERO_OFFSET = ir.Const(o.DK.U32, 0)


def _InsRewriteOutOfBoundsImmediates(
        ins: ir.Ins, fun: ir.Fun, unit: ir.Unit) -> Optional[List[ir.Ins]]:
    if ins.opcode in isel_tab.OPCODES_REQUIRING_SPECIAL_HANDLING:
        return None
    inss = []
    mismatches = isel_tab.FindtImmediateMismatchesInBestMatchPattern(ins, True)
    assert mismatches != isel_tab.MATCH_IMPOSSIBLE, f"could not match opcode {ins} {ins.operands}"

    if mismatches == 0:
        return None
    for pos in range(o.MAX_OPERANDS):
        if mismatches & (1 << pos) != 0:

            const_kind = ins.operands[pos].kind
            if const_kind is o.DK.F32 or const_kind is o.DK.F64:
                inss += lowering.InsEliminateImmediateViaMem(
                    ins, pos, fun, unit, o.DK.A32, o.DK.U32)
            else:
                inss.append(
                    lowering.InsEliminateImmediateViaMov(ins, pos, fun))
    if not inss:
        return None
    # assert len(inss) == 1, f"unexpected rewrites for {ins.opcode} {ins.operands} {len(inss)}"
    inss.append(ins)
    return inss


def _FunRewriteOutOfBoundsImmediates(fun: ir.Fun, unit: ir.Unit) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteOutOfBoundsImmediates, unit=unit)


def _InsMoveEliminationCpu(ins: ir.Ins, _fun: ir.Fun) -> Optional[List[ir.Ins]]:
    # TODO: handle conv
    if ins.opcode not in {o.MOV}:
        return None
    dst, src = ins.operands[0], ins.operands[1]
    if not isinstance(src, ir.Reg):
        return None
    assert dst.cpu_reg and src.cpu_reg
    if src.cpu_reg != dst.cpu_reg:
        return None
    return []


def FunMoveEliminationCpu(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsMoveEliminationCpu)


def DumpBbl(bbl: ir.Bbl):
    print("\n".join(serialize.BblRenderToAsm(bbl)))


def DumpFun(reason: str, fun: ir.Fun):
    print("#" * 60)
    print(f"# {reason}", fun.name)
    print("#" * 60)
    print("\n".join(serialize.FunRenderToAsm(fun)))


REG_KIND_TO_CPU_KIND: Dict[o.DK, int] = {
    o.DK.S8: regs.CpuRegKind.GPR.value,
    o.DK.S16: regs.CpuRegKind.GPR.value,
    o.DK.S32: regs.CpuRegKind.GPR.value,
    o.DK.U8: regs.CpuRegKind.GPR.value,
    o.DK.U16: regs.CpuRegKind.GPR.value,
    o.DK.U32: regs.CpuRegKind.GPR.value,
    #
    o.DK.A32: regs.CpuRegKind.GPR.value,
    o.DK.C32: regs.CpuRegKind.GPR.value,
    #
    o.DK.F32: regs.CpuRegKind.FLT.value,
    o.DK.F64: regs.CpuRegKind.DBL.value,
}


def DumpRegStats(fun: ir.Fun, stats: Dict[reg_stats.REG_KIND_LAC, int], fout):
    local_lac = 0
    local_not_lac = 0
    for (kind, lac), count in stats.items():
        if lac:
            local_lac += count
        else:
            local_not_lac += count

    allocated_lac = []
    allocated_not_lac = []
    global_lac = []
    global_not_lac = []

    for reg in fun.regs:
        if ir.REG_FLAG.GLOBAL not in reg.flags:
            continue
        if reg.HasCpuReg():
            if ir.REG_FLAG.LAC in reg.flags:
                allocated_lac.append(reg)
            else:
                allocated_not_lac.append(reg)
        else:
            if ir.REG_FLAG.LAC in reg.flags:
                global_lac.append(reg)
            else:
                global_not_lac.append(reg)

    if fout:
        print(f"# REGSTATS {fun.name:20s}   "
              f"all: {len(allocated_lac):2} {len(allocated_not_lac):2}  "
              f"glo: {len(global_lac):2} {len(global_not_lac):2}  "
              f"loc: {local_lac:2} {local_not_lac:2}", file=fout)


@dataclasses.dataclass()
class RegsNeeded:
    """estimate for how many regs are needed"""
    global_lac: int = 0
    global_not_lac: int = 0
    local_lac: int = 0
    local_not_lac: int = 0

    def __dir__(self):
        return f"RegNeeded: {self.global_lac} {self.global_not_lac} {self.local_lac} {self.local_not_lac}"


def _spilling_needed(needed: RegsNeeded, num_global_lac: int,
                     num_local_not_lac: int) -> bool:
    """ Note: this assumes the early condition of the pools with only two lists populated"""
    return (needed.global_lac + needed.local_lac > num_global_lac or
            needed.global_lac + needed.local_lac + needed.global_not_lac + needed.local_not_lac >
            num_global_lac + num_local_not_lac)


def _maybe_move_excess(src, dst, n):
    if n < len(src):
        if dst is not None:
            dst += src[n:]
        del src[n:]


def _popcount(x):
    return bin(x).count('1')


def _FindMaskCoveringTheLowOrderSetBits(bits: int, count: int) -> int:
    if count == 0:
        return 0
    mask = 1
    n = 0
    while n < count:
        if (mask & bits) != 0:
            n += 1
        mask <<= 1
    return mask - 1


def _GetRegPoolsForGlobals(needed: RegsNeeded, regs_lac: int,
                           regs_not_lac: int, regs_preallocated: int) -> Tuple[int, int]:
    """
    Partitions all the CPU registers into 4 categories

    Initially all allocatable regs are either in pools.global_lac and pools.local_not_local

    We want the low numbers regs to stay in pools.local_not_lac as much as possible
    to avoid moves as this is where the parameters arrive and results get returned

    We also want to use as few callee saved registers as possible

    If we need to spill, earmark one more local_not_lac reg to handle the spilling
    TODO: this needs some more thinking - the worst case could require more regs
    """
    num_regs_lac = _popcount(regs_lac)
    num_regs_not_lac = _popcount(regs_not_lac)
    spilling_needed = _spilling_needed(needed, num_regs_lac, num_regs_not_lac)
    global_lac = regs_lac
    local_lac = 0
    # excess lac globals can be used for lac locals
    if num_regs_lac > needed.global_lac:
        mask = _FindMaskCoveringTheLowOrderSetBits(
            global_lac, needed.global_lac)
        local_lac = global_lac & ~mask
        global_lac = global_lac & mask
    # we can use local_not_lac as global_not lac but only if they are not pre-allocated
    # because the global allocator does not check for live range conflicts
    global_not_lac = 0
    if num_regs_not_lac > needed.local_not_lac + spilling_needed:
        mask = _FindMaskCoveringTheLowOrderSetBits(
            regs_not_lac, needed.local_not_lac + spilling_needed)
        global_not_lac = regs_not_lac & ~(mask | regs_preallocated)

    if _popcount(local_lac) > needed.local_lac:
        mask = _FindMaskCoveringTheLowOrderSetBits(local_lac, needed.local_lac)
        global_not_lac |= local_lac & ~mask
    return global_lac, global_not_lac


def PhaseOptimize(fun: ir.Fun, unit: ir.Unit, opt_stats: Dict[str, int], fout):
    optimize.FunCfgInit(fun, unit)
    optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=True)


def PhaseLegalization(fun: ir.Fun, unit: ir.Unit, _opt_stats: Dict[str, int], fout):
    """
    Does a lot of the heavily lifting so that the instruction selector can remain
    simple and table driven.
    * lift almost all regs to 32bit width
    * rewrite Ins that cannot be expanded
    * rewrite immediates that cannot be expanded (stack offsets which are not known yet
      are ignored and we rely on being able to select all (reasonable) stack offsets)

    TODO: missing is a function to change calling signature so that
    """
    # shifts on A32 are saturating but Cwerg requires (mod <bitwidth>)
    lowering.FunLimitShiftAmounts(fun, 32)
    # lift everything to 32 bit
    lowering.FunRegWidthWidening(fun, o.DK.U8, o.DK.U32)
    lowering.FunRegWidthWidening(fun, o.DK.S8, o.DK.S32)
    lowering.FunRegWidthWidening(fun, o.DK.S16, o.DK.S32)
    lowering.FunRegWidthWidening(fun, o.DK.U16, o.DK.U32)

    fun.cpu_live_in = regs.PushPopInterface.GetCpuRegsForInSignature(
        fun.input_types)
    fun.cpu_live_out = regs.PushPopInterface.GetCpuRegsForOutSignature(
        fun.output_types)
    if fun.kind is not o.FUN_KIND.NORMAL:
        return
    # replaces pusharg and poparg instructions and replace them with moves
    # The moves will use pre-allocated regs (the once use for argument/result passing)
    # We eliminate pusharg/poparg early because out immediate elimination code may
    # introduce addtional instructions which make it difficult to perserve the invariant
    # that all poparg/pusharg related to a call be adjecent.
    lowering.FunPushargConversion(fun, regs.PushPopInterface)
    lowering.FunPopargConversion(fun, regs.PushPopInterface)

    # ARM is missing instructions for: mod, cntpop
    lowering.FunEliminateRem(fun)
    lowering.FunEliminateCntPop(fun)

    # A32 has not support for base + reg + offset but a stack access implicitly
    # requires base (=sp) + offset, so we have to rewrite
    # ld.stk/st.stk/lea.stk -> lea.stk + ld/st/lea
    lowering.FunEliminateStkLoadStoreWithRegOffset(fun, base_kind=o.DK.A32,
                                                   offset_kind=o.DK.S32)

    # The address of a global is somewhat costly to materialize and we may want to re-use
    # that computation so we rewrite:
    # ld.mem/st.mem -> lea.mem +ld/st
    lowering.FunEliminateMemLoadStore(fun, base_kind=o.DK.A32,
                                      offset_kind=o.DK.S32)

    canonicalize.FunCanonicalize(fun)
    # TODO: add a cfg linearization pass to improve control flow
    # not this may affect immediates as it flips branches
    optimize.FunCfgExit(fun, unit)

    # Handle most overflowing immediates.
    _FunRewriteOutOfBoundsImmediates(fun, unit)
    sanity.FunCheck(fun, None)
    # optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=False)


def GlobalRegAllocOneKind(fun: ir.Fun, kinds: Set[regs.CpuRegKind], needed: RegsNeeded, cpu_regs_lac,
                          cpu_regs_not_lac, cpu_regs_lac_mask, global_regs_lac, global_regs_not_lac,
                          debug) -> List[ir.Reg]:
    pre_allocated = 0
    for reg in fun.regs:
        if reg.HasCpuReg() and reg.cpu_reg.kind in kinds:
            pre_allocated |= 1 << reg.cpu_reg.no

    kind_name = next(iter(kinds))
    if debug:
        print(f"@@ {kind_name} NEEDED {needed.global_lac} {needed.global_not_lac} "
              f"{needed.local_lac} {needed.local_not_lac}", file=debug)

    global_lac_pool, global_not_lac_pool = _GetRegPoolsForGlobals(
        needed, cpu_regs_lac, cpu_regs_not_lac, pre_allocated)
    if debug:
        print(
            f"@@ {kind_name} POOL {global_lac_pool:x} {global_not_lac_pool:x}", file=debug)

    return (regs.AssignCpuRegOrMarkForSpilling(global_regs_lac, global_lac_pool, 0) +
            regs.AssignCpuRegOrMarkForSpilling(
                global_regs_not_lac,
                global_not_lac_pool & ~cpu_regs_lac_mask,
                global_not_lac_pool & cpu_regs_lac_mask))


def PhaseGlobalRegAlloc(fun: ir.Fun, _opt_stats: Dict[str, int], fout):
    """
    These phase introduces CpuReg for globals and situations where we have no choice
    which register to use, e.g. function parameters and results ("pre-allocated" regs).

    After this function has been run all globals will have a valid cpu_reg and
    we have to be careful to not introduce new globals subsequently.
    If not enough cpu_regs are available for all globals, some of them will be spilled.
    We err on the site of spilling more, the biggest danger is to over-allocate and then
    lack registers for intra-bbl register allocation.

    The whole global allocator is terrible and so is the the decision which globals
    to spill is extremely simplistic at this time.

    We separate global from local register allocation so that we can use a straight
    forward linear scan allocator for the locals. This allocator assumes that
    each register is defined exactly once and hence does not work for globals.
    """

    if fout:
        print("#" * 60, file=fout)
        print(f"# GlobalRegAlloc {fun.name}", file=fout)
        print("#" * 60, file=fout)

    # replaces pusharg and poparg instructions and replace them with moves
    # The moves will use pre-allocated regs (the once use for argument/result paassing)
    # regs.FunPushargConversion(fun)
    # regs.FunPopargConversion(fun)

    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)

    # Note: REG_KIND_MAP_ARM maps all non-float to registers to S32
    local_reg_stats = reg_stats.FunComputeBblRegUsageStats(
        fun, REG_KIND_TO_CPU_KIND)
    #
    global_reg_stats = reg_stats.FunGlobalRegStats(fun, REG_KIND_TO_CPU_KIND)
    DumpRegStats(fun, local_reg_stats, fout)

    debug = None
    # compute the number of regs needed if had indeed unlimited regs
    needed_gpr = RegsNeeded(len(global_reg_stats[(regs.CpuRegKind.GPR, True)]),
                            len(global_reg_stats[(
                                regs.CpuRegKind.GPR, False)]),
                            local_reg_stats.get(
                                (regs.CpuRegKind.GPR, True), 0),
                            local_reg_stats.get((regs.CpuRegKind.GPR, False), 0))
    to_be_spilled: List[ir.Reg] = GlobalRegAllocOneKind(fun, {regs.CpuRegKind.GPR}, needed_gpr,
                                                        regs.GPR_REGS_MASK & regs.GPR_LAC_REGS_MASK,
                                                        regs.GPR_REGS_MASK & ~regs.GPR_LAC_REGS_MASK,
                                                        regs.GPR_LAC_REGS_MASK,
                                                        global_reg_stats[(
                                                            regs.CpuRegKind.GPR, True)],
                                                        global_reg_stats[(
                                                            regs.CpuRegKind.GPR, False)],
                                                        debug)

    needed_flt = RegsNeeded(len(global_reg_stats[(regs.CpuRegKind.FLT, True)]) + 2 *
                            len(global_reg_stats[(regs.CpuRegKind.DBL, True)]),
                            len(global_reg_stats[(regs.CpuRegKind.FLT, False)]) + 2 *
                            len(global_reg_stats[(
                                regs.CpuRegKind.DBL, False)]),
                            local_reg_stats.get((regs.CpuRegKind.FLT, True), 0) + 2 *
                            local_reg_stats.get(
                                (regs.CpuRegKind.DBL, True), 0),
                            local_reg_stats.get((regs.CpuRegKind.FLT, False), 0) + 2 *
                            local_reg_stats.get((regs.CpuRegKind.DBL, False), 0))
    to_be_spilled += GlobalRegAllocOneKind(fun, {regs.CpuRegKind.FLT, regs.CpuRegKind.DBL}, needed_flt,
                                           regs.FLT_REGS_MASK & regs.FLT_LAC_REGS_MASK,
                                           regs.FLT_REGS_MASK & ~regs.FLT_LAC_REGS_MASK,
                                           regs.FLT_LAC_REGS_MASK,
                                           global_reg_stats[(regs.CpuRegKind.FLT, True)] +
                                           global_reg_stats[(
                                               regs.CpuRegKind.DBL, True)],
                                           global_reg_stats[(regs.CpuRegKind.FLT, False)] +
                                           global_reg_stats[(
                                               regs.CpuRegKind.DBL, False)],
                                           debug)

    reg_alloc.FunSpillRegs(fun, o.DK.U32, to_be_spilled, prefix="$gspill")


def PhaseFinalizeStackAndLocalRegAlloc(fun: ir.Fun,
                                       _opt_stats: Dict[str, int], fout):
    """Finalizing the stack implies performing all transformations that
    could increase register usage.

    """
    # Recompute Everything (TODO: make this more selective)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    # establish per bbl SSA form by splitting liveranges
    # TODO:
    reg_stats.FunSeparateLocalRegUsage(fun)
    # DumpRegStats(fun, local_reg_stats)
    # hack: some of the code expansion templates need a scratch reg
    # we do not want to reserve registers for this globally, so instead
    # we inject some nop instructions that reserve a register that we
    # use as a scratch for the instruction immediately following the nop
    isel_tab.FunAddNop1ForCodeSel(fun)
    
    regs.FunLocalRegAlloc(fun)
    fun.FinalizeStackSlots()
    # cleanup
    FunMoveEliminationCpu(fun)
