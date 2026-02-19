import dataclasses
from typing import List, Dict, Optional, Tuple

from BE.Base import canonicalize
from BE.Base import ir
from BE.Base import cfg
from BE.Base import liveness
from BE.Base import lowering
from IR import opcode_tab as o
from BE.Base import optimize
from BE.Base import reg_stats
from BE.Base import sanity
from BE.Base import serialize
from BE.CodeGenX64 import isel_tab
from BE.CodeGenX64 import regs


def DumpBbl(bbl: ir.Bbl):
    print("\n".join(serialize.BblRenderToAsm(bbl)))


def DumpFun(reason: str, fun: ir.Fun):
    print("#" * 60)
    print(f"# {reason}", fun.name)
    print("#" * 60)
    print("\n".join(serialize.FunRenderToAsm(fun)))


_SUPPORTED_IN_ALL_WIDTHS = {
    o.ADD, o.SUB, o.XOR, o.AND, o.OR,
}


def IsOutOfBoundImmediate(opcode, op, pos) -> bool:
    if not isinstance(op, ir.Const):
        return False
    if op.kind in {o.DK.R64, o.DK.R32}:
        return True
    if opcode is o.MOV:
        return False
    if opcode in {o.DIV, o.REM, o.MUL, o.CNTTZ, o.CNTLZ, o.CONV}:
        return True
    if pos == 2 and opcode in {o.ST, o.ST_STK, o.ST_MEM}:
        return True
    if op.kind in {o.DK.S8, o.DK.S16, o.DK.S32, o.DK.S64, o.DK.A64, o.DK.C64}:
        return op.value < -(1 << 31) or (1 << 31) <= op.value
    if op.kind in {o.DK.U8, o.DK.U16, o.DK.U32, o.DK.U64}:
        return (1 << 31) <= op.value
    else:
        assert False, f"unknown op: {op}"


def _InsRewriteOutOfBoundsImmediates(
        ins: ir.Ins, fun: ir.Fun, cache: lowering.RegConstCache) -> Optional[List[ir.Ins]]:
    inss = []
    if ins.opcode.kind in {o.OPC_KIND.ALU, o.OPC_KIND.COND_BRA, o.OPC_KIND.ALU1, o.OPC_KIND.ST,
                           o.OPC_KIND.CONV, o.OPC_KIND.MOV}:
        for pos, op in enumerate(ins.operands):
            if IsOutOfBoundImmediate(ins.opcode, op, pos):
                # support of PUSHARG would require additional work because they need to stay consecutive
                assert ins.opcode is not o.PUSHARG
                from_mem = op.kind in (o.DK.R32, o.DK.R64)
                reg = cache.Materialize(fun, op, from_mem, inss)
                ins.operands[pos] = reg
    if not inss:
        return None
    inss.append(ins)
    return inss


def _FunRewriteOutOfBoundsImmediates(fun: ir.Fun, unit: ir.Unit) -> int:
    """Rewrite instruction with an immediate as mov of the immediate

    mul z = a 666
    becomes
    mov scratch = 666
    mul z = a scratch

    This is useful if the target architecture does not support immediate
    for that instruction, or the immediate is too large.

    This optimization is run rather late and may already see machine registers.
    Ideally, the generated mov instruction hould be iselectable by the target architecture or
    else another pass may be necessary.
    """
    count = 0
    # since X64 has very regs and caching consts can increase register pressure we only use
    # a small chache size
    cache = lowering.RegConstCache(unit, o.DK.A64, o.DK.U32, 2)
    for bbl in fun.bbls:
        cache.Reset()
        count += ir.BblGenericRewrite(bbl, fun,
                                      _InsRewriteOutOfBoundsImmediates, cache=cache)
    return count

# These require implicit regs
# Note, that rax is a scratch register. Using it here is a little iffy but
# we are only using it with simple mov instructions which do not require
# the scratch register


def _InsRewriteDivRemShiftsCAS(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    ops = ins.operands
    if opc is o.DIV and ops[0].kind.flavor() != o.DK_FLAVOR_R:
        # note: we could leave it to the register allocator to pick a CpuReg for ops[2]
        # but then we would somehow have to  ensure that the reg is NOT rdx.
        # By forcing rcx for ops[2] we sidestep the issue
        rax = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rax"], ops[0].kind)
        rcx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rcx"], ops[0].kind)
        rdx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rdx"], ops[0].kind)
        return [ir.Ins(o.MOV, [rax, ops[1]], False),
                ir.Ins(o.MOV, [rcx, ops[2]], False),
                # note the notion of src/dst regs is murky here
                ir.Ins(o.DIV, [rdx, rax, rcx], False),
                ir.Ins(o.MOV, [ops[0], rax], False)]
    elif opc is o.REM and ops[0].kind.flavor() != o.DK_FLAVOR_R:
        rax = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rax"], ops[0].kind)
        rcx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rcx"], ops[0].kind)
        rdx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rdx"], ops[0].kind)
        return [ir.Ins(o.MOV, [rax, ops[1]], False),
                ir.Ins(o.MOV, [rcx, ops[2]], False),
                # note the notion of src/dst regs is murky here
                ir.Ins(o.DIV, [rdx, rax, rcx],  False),
                ir.Ins(o.MOV, [ops[0], rdx], False)]
    elif opc in (o.SHR, o.SHL):
        dk: o.DK = ops[0].kind
        mask = dk.bitwidth() - 1

        if isinstance(ops[2], ir.Reg):
            rcx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rcx"], ops[0].kind)
            mov = ir.Ins(o.MOV, [rcx, ops[2]], False)
            ops[2] = rcx
            return [mov, ir.Ins(o.AND, [rcx, rcx, ir.Const(dk, mask)], False), ins]
        else:
            assert isinstance(ops[2], ir.Const)
            ops[2].value = ops[2].value & mask
    elif opc in {o.CAS, o.CAS_MEM, o.CAS_STK}:
        rax = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rax"], ops[0].kind)
        mov_src = ir.Ins(o.MOV, [rax, ops[1]], False)
        mov_dst = ir.Ins(o.MOV, [ops[0], rax], False)
        ops[1] = rax
        ops[0] = rax
        return [mov_src, ins, mov_dst]
    else:
        return None


def _FunRewriteDivRemShiftsCAS(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteDivRemShiftsCAS)


def InsNeedsAABFormRewrite(ins: ir.Ins):
    opc = ins.opcode
    ops = ins.operands
    if opc.kind not in {o.OPC_KIND.ALU, o.OPC_KIND.LEA}:
        return False
    if opc in {o.DIV, o.REM} and ops[0].kind.flavor() != o.DK_FLAVOR_R:
        return False
    if opc in {o.LEA_MEM, o.LEA_STK}:
        return False
    return True


def _InsRewriteIntoAABForm(
        ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    ops = ins.operands
    if not InsNeedsAABFormRewrite(ins):
        return None
    if ops[0] == ops[1]:
        ops[0].flags |= ir.REG_FLAG.TWO_ADDRESS
        return None
    elif ops[0] == ops[2] and o.OA.COMMUTATIVE in ins.opcode.attributes:
        ir.InsSwapOps(ins, 1, 2)
        ops[0].flags |= ir.REG_FLAG.TWO_ADDRESS
        return [ins]
    else:
        reg = fun.GetScratchReg(ins.operands[0].kind, "aab", False)
        reg.flags |= ir.REG_FLAG.TWO_ADDRESS
        return [ir.Ins(o.MOV, [reg, ops[1]], False),
                ir.Ins(ins.opcode, [reg, reg, ops[2]], False),
                ir.Ins(o.MOV, [ops[0], reg], False)]


def _FunRewriteIntoAABForm(fun: ir.Fun, unit: ir.Unit) -> int:
    """Bring instructions into A A B form (dst == src1). See README.md"""
    return ir.FunGenericRewrite(fun, _InsRewriteIntoAABForm)


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


def _FunMoveEliminationCpu(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsMoveEliminationCpu)


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
    if fout:
        print("#" * 60, file=fout)
        print(f"# Legalize {fun.name}", file=fout)
        print("#" * 60, file=fout)

    fun.cpu_live_in = regs.PushPopInterface.GetCpuRegsForInSignature(
        fun.input_types)
    fun.cpu_live_out = regs.PushPopInterface.GetCpuRegsForOutSignature(
        fun.output_types)
    if fun.kind is not o.FUN_KIND.NORMAL:
        return

    # Getting rid of the pusharg/poparg now relieves us form having to pay to attention to  the
    # invariant that pushargs/popargs must be adjacent.
    lowering.FunPushargConversion(fun, regs.PushPopInterface)
    lowering.FunPopargConversion(fun, regs.PushPopInterface)

    # We did not bother with this addressing mode
    # TODO: we like can avoid this by adding more cases to isel_tab.py
    lowering.FunEliminateStkLoadStoreWithRegOffset(fun, base_kind=o.DK.A64,
                                                   offset_kind=o.DK.S32)

    # TODO: switch this to a WithRegOffset flavor
    lowering.FunEliminateMemLoadStore(fun, base_kind=o.DK.A64,
                                      offset_kind=o.DK.S32)

    lowering.FunEliminateCopySign(fun)
    # TODO: support a few special cases in the isel, e.g. cmpXX a 0, 1, x, y
    lowering.FunEliminateCmp(fun)

    canonicalize.FunCanonicalize(fun)
    # TODO: add a cfg linearization pass to improve control flow
    # not this may affect immediates as it flips branches
    optimize.FunCfgExit(fun, unit)

    # Handle most overflowing immediates.
    # This excludes immediates related to stack offsets which have not been determined yet
    _FunRewriteOutOfBoundsImmediates(fun, unit)

    # mul/div/rem need special treatment
    _FunRewriteDivRemShiftsCAS(fun)

    _FunRewriteIntoAABForm(fun, unit)

    # Recompute Everything (TODO: make this more selective to reduce work)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    # this has special hacks to avoid undoing _FunRewriteIntoAABForm()
    reg_stats.FunSeparateLocalRegUsage(fun)
    # DumpRegStats(fun, local_reg_stats)

    sanity.FunCheck(fun, None)
    # optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=False)


def LegalizeAll(unit, opt_stats, fout, verbose=False):
    seeds = [f for f in [unit.fun_syms.get("_start"),
                         unit.fun_syms.get("main")] if f]
    if seeds:
        cfg.UnitRemoveUnreachableCode(unit, seeds)
    for fun in unit.funs:
        sanity.FunCheck(fun, unit, check_cfg=False, check_push_pop=True)

        if fun.kind is o.FUN_KIND.NORMAL:
            optimize.FunCfgInit(fun, unit)
            optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=True)

    for fun in unit.funs:
        # pass
        PhaseLegalization(fun, unit, opt_stats, fout)


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
    Allocate global registers

    Initially all allocatable regs are either in pools.global_lac and pools.local_not_lac
    We want to assign a subset of these to global_lac and global_not_lac

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


def GlobalRegAllocOneKind(fun: ir.Fun, kind: regs.CpuRegKind, needed: RegsNeeded, regs_lac,
                          regs_not_lac, regs_lac_mask, global_reg_stats, debug):
    pre_allocated = 0
    for reg in fun.regs:
        if reg.HasCpuReg() and reg.cpu_reg.kind == kind:
            pre_allocated |= 1 << reg.cpu_reg.no

    if debug:
        print(f"@@ {kind.name} NEEDED {needed.global_lac} {needed.global_not_lac} "
              f"{needed.local_lac} {needed.local_not_lac}", file=debug)

    global_lac, global_not_lac = _GetRegPoolsForGlobals(
        needed, regs_lac, regs_not_lac, pre_allocated)
    if debug:
        print(f"@@ {kind.name} POOL {global_lac:x} {global_not_lac:x}", file=debug)

    if True:
        regs.AssignCpuRegOrMarkForSpilling(
            global_reg_stats[(kind, True)], global_lac, 0)
        regs.AssignCpuRegOrMarkForSpilling(
            global_reg_stats[(kind, False)],
            global_not_lac & ~regs_lac_mask,
            global_not_lac & regs_lac_mask)
    else:
        regs.AssignCpuRegOrMarkForSpilling(
            global_reg_stats[(kind, True)], 0, 0)
        regs.AssignCpuRegOrMarkForSpilling(
            global_reg_stats[(kind, False)], 0, 0)


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
    debug = None
    if fout:
        print("#" * 60, file=fout)
        print(f"# GlobalRegAlloc {fun.name}", file=fout)
        print("#" * 60, file=fout)

    # print ("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))

    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)

    local_reg_stats = reg_stats.FunComputeBblRegUsageStats(fun,
                                                           regs.REG_KIND_TO_CPU_REG_FAMILY)
    # we  have introduced some cpu regs in previous phases - do not treat them as globals
    global_reg_stats = reg_stats.FunGlobalRegStats(
        fun, regs.REG_KIND_TO_CPU_REG_FAMILY)
    if fout:
        DumpRegStats(fun, local_reg_stats, fout)

    # Handle GPR regs
    needed_gpr = RegsNeeded(len(global_reg_stats[(regs.CpuRegKind.GPR, True)]),
                            len(global_reg_stats[(
                                regs.CpuRegKind.GPR, False)]),
                            local_reg_stats.get(
                                (regs.CpuRegKind.GPR, True), 0),
                            local_reg_stats.get((regs.CpuRegKind.GPR, False), 0))
    GlobalRegAllocOneKind(fun, regs.CpuRegKind.GPR, needed_gpr,
                          regs.GPR_REGS_MASK & regs.GPR_LAC_REGS_MASK & ~regs.GPR_REG_IMPLICIT_MASK,
                          regs.GPR_REGS_MASK & ~regs.GPR_LAC_REGS_MASK & ~regs.GPR_REG_IMPLICIT_MASK,
                          regs.GPR_LAC_REGS_MASK, global_reg_stats, debug)

    needed_flt = RegsNeeded(len(global_reg_stats[(regs.CpuRegKind.FLT, True)]),
                            len(global_reg_stats[(
                                regs.CpuRegKind.FLT, False)]),
                            local_reg_stats.get(
                                (regs.CpuRegKind.FLT, True), 0),
                            local_reg_stats.get((regs.CpuRegKind.FLT, False), 0))
    GlobalRegAllocOneKind(fun, regs.CpuRegKind.FLT, needed_flt,
                          regs.FLT_REGS_MASK & regs.FLT_LAC_REGS_MASK,
                          regs.FLT_REGS_MASK & ~regs.FLT_LAC_REGS_MASK,
                          regs.FLT_LAC_REGS_MASK, global_reg_stats, debug)


def PhaseFinalizeStackAndLocalRegAlloc(fun: ir.Fun,
                                       _opt_stats: Dict[str, int], fout):
    """Finalizing the stack implies performing all transformations that
    could increase register usage.

    """
    # print("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)), file=fout)

    # hack: some of the code expansion templates need a scratch reg
    # we do not want to reserve registers for this globally, so instead
    # we inject some nop instructions that reserve a register that we
    # use as a scratch for the instruction immediately following the nop
    #
    # This still has a potential bug: if the next instruction has one of its
    # inputs spilled, it will like use the scratch reg provided by the nop1
    # which will cause incorrect code.
    # TODO: add a checker so we at least detect this
    # Alternatives: reserve reg (maybe only for functions that need it)
    # TODO: make sure that nop1 regs never get spilled
    # Recompute Everything (TODO: make this more selective to reduce work)

    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    # DumpRegStats(fun, local_reg_stats)
    # DumpFun("after global alloc", fun)

    isel_tab.FunAddNop1ForCodeSel(fun)
    if True:
        regs.FunLocalRegAlloc(fun)
    else:
        for reg in fun.regs:
            if reg.IsSpilled() or reg.HasCpuReg():
                continue
            elif "nop1" in reg.name:
                reg.cpu_reg = regs.CPU_REGS_MAP["xmm1"] if reg.kind.flavor() == o.DK_FLAVOR_R else regs.CPU_REGS_MAP[
                    "rsi"]
            else:
                reg.cpu_reg = ir.StackSlot(0)
    fun.FinalizeStackSlots()
    # if fun.name == "fibonacci": DumpFun("after local alloc", fun)
    # DumpFun("after local alloc", fun)
    # cleanup
    _FunMoveEliminationCpu(fun)
    # print ("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
