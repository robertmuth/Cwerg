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
from CodeGenA64 import isel_tab
from CodeGenA64 import regs

_DUMMY_A32 = ir.Reg("dummy", o.DK.A32)
_ZERO_OFFSET = ir.Const(o.DK.U32, 0)

_OPCODES_IGNORED_BY_IMMEDIATE_REWRITER = isel_tab.OPCODES_REQUIRING_SPECIAL_HANDLING | {
    o.POPARG, o.PUSHARG,  # will be rewritten later
}


def _InsRewriteOutOfBoundsImmediates(
        ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    if ins.opcode in _OPCODES_IGNORED_BY_IMMEDIATE_REWRITER:
        return None
    inss = []
    mismatches = isel_tab.FindtImmediateMismatchesInBestMatchPattern(ins, True)
    assert mismatches != isel_tab.MATCH_IMPOSSIBLE, f"could not match opcode {ins} {ins.operands}"

    if mismatches == 0:
        return None
    for pos in range(o.MAX_OPERANDS):
        if mismatches & (1 << pos) != 0:
            inss.append(lowering.InsEliminateImmediate(ins, pos, fun))
    if not inss:
        return None
    # assert len(inss) == 1, f"unexpected rewrites for {ins.opcode} {ins.operands} {len(inss)}"
    inss.append(ins)
    return inss


def _FunRewriteOutOfBoundsImmediates(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteOutOfBoundsImmediates)


def _InsRewriteFltImmediates(
        ins: ir.Ins, fun: ir.Fun, unit: ir.Unit) -> Optional[List[ir.Ins]]:
    inss = []
    for n, op in enumerate(ins.operands):
        if isinstance(op, ir.Const) and op.kind.flavor() is o.DK_FLAVOR_F:
            mem = unit.FindOrAddConstMem(op)
            tmp = fun.GetScratchReg(op.kind, "flt_const", True)
            inss.append(ir.Ins(o.LD_MEM, [tmp, mem, _ZERO_OFFSET]))
            ins.operands[n] = tmp
    if inss:
        return inss + [ins]
    return None


def _FunRewriteFltImmediates(fun: ir.Fun, unit: ir.Unit) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteFltImmediates, unit=unit)


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


# map all int regs to S32 which will then be allocated to gpr A32 regs
REG_KIND_MAP_ARM = {
    o.DK.S8: o.DK.S64,
    o.DK.S16: o.DK.S64,
    o.DK.S32: o.DK.S64,
    o.DK.S64: o.DK.S64,
    #
    o.DK.U8: o.DK.S64,
    o.DK.U16: o.DK.S64,
    o.DK.U32: o.DK.S64,
    o.DK.U64: o.DK.S64,
    #
    o.DK.A64: o.DK.S64,
    o.DK.C64: o.DK.S64,
    #
    o.DK.F32: o.DK.F64,
    o.DK.F64: o.DK.F64,
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
        if ir.REG_FLAG.GLOBAL not in reg.flags: continue
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


def _spilling_needed(needed: RegsNeeded, global_lac: List[ir.CpuReg],
                     local_not_lac: List[ir.CpuReg]) -> bool:
    """ Note: this assumes the early condition of the pools with only two lists populated"""
    return (needed.global_lac + needed.local_lac > len(global_lac) or
            needed.global_lac + needed.local_lac + needed.global_not_lac + needed.local_not_lac >
            len(global_lac) + len(local_not_lac))


def _maybe_move_excess(src, dst, n):
    if n < len(src):
        if dst is not None:
            dst += src[n:]
        del src[n:]


def _GetRegPoolsForGlobals(needed: RegsNeeded, regs_lac: List[ir.CpuReg],
                           regs_not_lac: List[ir.CpuReg],
                           pre_allocated: Set[ir.CpuReg]) -> Tuple[
    List[ir.CpuReg], List[ir.CpuReg]]:
    """
    Partitions all the CPU registers into 4 categories

    Initially all allocatable regs are either in pools.global_lac and pools.local_not_local

    We want the low numbers regs to stay in pools.local_not_lac as much as possible
    to avoid moves as this is where the paramters arrive and results get returned

    We also want to use as few callee saved registers as possible

    If we need to spill, earmark one more local_not_lac reg to handle the spilling
    TODO: this needs some more thinking - the worst case could require more regs
    """
    spill_reg_needed = _spilling_needed(needed, regs_lac, regs_not_lac)
    global_lac = regs_lac
    local_lac = []
    # excess lac globals can be used for lac locals
    _maybe_move_excess(regs_lac, local_lac, needed.global_lac)
    # we can use local_not_lac as global_not lac but only if they are not pre-allocated
    # because the global allocator does not check for live range conflicts
    local_not_lac = []
    global_not_lac = []
    for n, cpu_reg in enumerate(regs_not_lac):
        if n < needed.local_not_lac + spill_reg_needed or cpu_reg in pre_allocated:
            local_not_lac.append(cpu_reg)
        else:
            global_not_lac.append(cpu_reg)
    # xxx_lac can also be  used in place of  xxx_not_lac
    _maybe_move_excess(local_lac, global_not_lac, needed.local_lac)
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
    * rewrite immediates that cannot be expanded except stack offsets which are dealt with in
      another pass

    TODO: missing is a function to change calling signature so that
    """

    lowering.FunRegWidthWidening(fun, o.DK.U8, o.DK.U32)
    lowering.FunRegWidthWidening(fun, o.DK.S8, o.DK.S32)
    lowering.FunRegWidthWidening(fun, o.DK.S16, o.DK.S32)
    lowering.FunRegWidthWidening(fun, o.DK.U16, o.DK.U32)

    fun.cpu_live_in = regs.GetCpuRegsForSignature(fun.input_types)
    fun.cpu_live_out = regs.GetCpuRegsForSignature(fun.output_types)
    if fun.kind is not o.FUN_KIND.NORMAL:
        return

    # ARM has no mod instruction
    lowering.FunEliminateRem(fun)

    # A64 has not support for these addressing modes
    lowering.FunEliminateStkLoadStoreWithRegOffset(fun, base_kind=o.DK.A64,
                                                   offset_kind=o.DK.S32)
    # No floating point immediates
    lowering.FunMoveImmediatesToMemory(fun, unit, o.DK.F32)
    lowering.FunMoveImmediatesToMemory(fun, unit, o.DK.F64)
    # also handles ld_mem from two transformations above
    lowering.FunEliminateMemLoadStore(fun, base_kind=o.DK.A64,
                                      offset_kind=o.DK.S32)

    canonicalize.FunCanonicalize(fun)
    # TODO: add a cfg linearization pass to improve control flow
    optimize.FunCfgExit(fun, unit)  # not this may affect immediates as it flips branches

    # Handle most overflowing immediates.
    # This excludes immediates related to stack offsets which have not been determined yet
    _FunRewriteOutOfBoundsImmediates(fun)
    # hack: some of the code expansion templates need a scratch reg
    # we do not want to reserve registers for this globally, so instead
    # we inject some nop instructions that reserve a register that we
    # use as a scratch for the instruction immediately following the nop
    isel_tab.FunAddNop1ForCodeSel(fun)
    sanity.FunCheck(fun, None)
    # optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=False)


KIND_AND_LAC = Tuple[o.DK, bool]


def _FunGlobalRegStats(fun: ir.Fun, reg_kind_map: Dict[o.DK, o.DK]) -> Dict[
    KIND_AND_LAC, List[ir.Reg]]:
    out: Dict[KIND_AND_LAC, List[ir.Reg]] = collections.defaultdict(list)
    for reg in fun.regs:
        if not reg.HasCpuReg() and ir.REG_FLAG.GLOBAL in reg.flags:
            out[(reg_kind_map[reg.kind], ir.REG_FLAG.LAC in reg.flags)].append(
                reg)
    for v in out.values():
        v.sort()
    return out


def _AssignCpuRegOrMarkForSpilling(assign_to: List[ir.Reg],
                                   cpu_regs: List[ir.CpuReg]) -> List[ir.Reg]:
    """This is pretty simplistic and has lots of assumptions

    E.g. for the floating points regs F64 should precedw F32"""
    # print (f"@@@@@@@ assign {global_regs} {cpu_regs}")
    out: List[ir.Reg] = []
    n = 0
    for reg in assign_to:
        if n < len(cpu_regs):
            assert reg.cpu_reg is None
            reg.cpu_reg = cpu_regs[n]
            n += 1
        else:
            out.append(reg)
    return out


def PhaseGlobalRegAlloc(fun: ir.Fun, _opt_stats: Dict[str, int], fout):
    """
    These phase introduces CpuReg for globals and situations where we have no choice
    which register to use, e.g. function parameters and results ("pre-allocated" regs).

    After this function has been run all globals will have a valid cpu_reg and
    we have to be careful to not introduce new globals subsequently.
    IF not enough cpu_regs are available for all globals, some of them will be spilled.

    The whole global allocator is terrible and so is the the decision which globals
    to spill is extremely simplistic at this time.

    We sepatate global from local register allocation so that we can use a straight
    forward linear scan allocator for the locals. This allocator assumes that
    each register is defined exactly once and hence does not work for globals.
    """

    if fout:
        print("#" * 60, file=fout)
        print(f"# GlobalRegAlloc {fun.name}", file=fout)
        print("#" * 60, file=fout)

    regs.FunPushargConversion(fun)
    regs.FunPopargConversion(fun)

    # print ("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))


    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)

    # Note: REG_KIND_MAP_ARM maps all non-float to registers to S64
    local_reg_stats = reg_stats.FunComputeBblRegUsageStats(fun,
                                                           REG_KIND_MAP_ARM)
    # we  have introduced some cpu regs in previous phases - do not treat them as globals
    global_reg_stats = _FunGlobalRegStats(fun, REG_KIND_MAP_ARM)
    DumpRegStats(fun, local_reg_stats, fout)

    pre_allocated: Set[ir.CpuReg] = {reg.cpu_reg for reg in fun.regs if reg.HasCpuReg()}

    # Handle GPR regs
    needed_gpr = RegsNeeded(len(global_reg_stats[(o.DK.S64, True)]),
                            len(global_reg_stats[(o.DK.S64, False)]),
                            local_reg_stats.get((o.DK.S64, True), 0),
                            local_reg_stats.get((o.DK.S64, False), 0))
    gpr_global_lac, gpr_global_not_lac = _GetRegPoolsForGlobals(
        needed_gpr, regs.GPR64_CALLEE_SAVE_REGS.copy(),
        regs.GPR64_PARAMETER_REGS.copy(), pre_allocated)

    to_be_spilled: List[ir.Reg] = []
    to_be_spilled += _AssignCpuRegOrMarkForSpilling(global_reg_stats[(o.DK.S64, True)],
                                                    gpr_global_lac)
    to_be_spilled += _AssignCpuRegOrMarkForSpilling(global_reg_stats[(o.DK.S64, False)],
                                                    gpr_global_not_lac)

    # Handle Float regs
    needed_flt = RegsNeeded(len(global_reg_stats[(o.DK.F64, True)]),
                            len(global_reg_stats[(o.DK.F64, True)]),
                            local_reg_stats.get((o.DK.F64, True), 0),
                            local_reg_stats.get((o.DK.F64, False), 0))

    flt_global_lac, flt_global_not_lac = _GetRegPoolsForGlobals(
        needed_flt, regs.FLT64_CALLEE_SAVE_REGS.copy(),
        regs.FLT64_PARAMETER_REGS.copy(), pre_allocated)

    to_be_spilled += _AssignCpuRegOrMarkForSpilling(global_reg_stats[(o.DK.F64, True)],
                                                    flt_global_lac)
    to_be_spilled += _AssignCpuRegOrMarkForSpilling(global_reg_stats[(o.DK.F64, False)],
                                                    flt_global_not_lac)

    reg_alloc.FunSpillRegs(fun, o.DK.U32, to_be_spilled, prefix="$gspill")

    # Recompute Everything (TODO: make this more selective to reduce work)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    reg_stats.FunSeparateLocalRegUsage(fun)
    # DumpRegStats(fun, local_reg_stats)


def PhaseFinalizeStackAndLocalRegAlloc(fun: ir.Fun,
                                       _opt_stats: Dict[str, int], fout):
    """Finalizing the stack implies performing all transformations that
    could increase register usage.

    """
    regs.FunLocalRegAlloc(fun)
    fun.FinalizeStackSlots()
    # cleanup
    FunMoveEliminationCpu(fun)
    # print ("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
