import collections
import dataclasses
from typing import List, Dict, Optional, Tuple

from Base import canonicalize
from Base import ir
from Base import liveness
from Base import lowering
from Base import opcode_tab as o
from Base import optimize
from Base import reg_stats
from Base import sanity
from Base import serialize
from CodeGenX64 import isel_tab
from CodeGenX64 import regs


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
    if op.kind in {o.DK.F64, o.DK.F32}:
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
        ins: ir.Ins, fun: ir.Fun, unit: ir.Unit) -> Optional[List[ir.Ins]]:
    inss = []
    if ins.opcode.kind in {o.OPC_KIND.ALU, o.OPC_KIND.COND_BRA, o.OPC_KIND.ALU1, o.OPC_KIND.ST,
                           o.OPC_KIND.CONV, o.OPC_KIND.MOV}:
        for pos, op in enumerate(ins.operands):
            if IsOutOfBoundImmediate(ins.opcode, op, pos):
                if op.kind in {o.DK.F32, o.DK.F64}:
                    inss += lowering.InsEliminateImmediateViaMem(ins, pos, fun, unit,
                                                                 o.DK.A64, o.DK.U32)
                else:
                    inss.append(lowering.InsEliminateImmediateViaMov(ins, pos, fun))

    inss.append(ins)
    return inss


def _FunRewriteOutOfBoundsImmediates(fun: ir.Fun, unit: ir.Unit) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteOutOfBoundsImmediates, unit=unit)


_SHIFT_MASK = {
    o.DK.S8: ir.Const(o.DK.S8, 7),
    o.DK.U8: ir.Const(o.DK.U8, 7),
    o.DK.S16: ir.Const(o.DK.S16, 15),
    o.DK.U16: ir.Const(o.DK.U16, 15),
    o.DK.S32: ir.Const(o.DK.S32, 31),
    o.DK.U32: ir.Const(o.DK.U32, 31),
}


def _InsRewriteDivRemShifts(ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    opc = ins.opcode
    ops = ins.operands
    if opc is o.DIV and ops[0].kind.flavor() != o.DK_FLAVOR_F:
        rax = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rax"], ops[0].kind)
        rdx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rdx"], ops[0].kind)
        return [ir.Ins(o.MOV, [rax, ops[1]]),
                ir.Ins(o.DIV, [rdx, rax, ops[2]]),  # note the notion of src/dst regs is murky here
                ir.Ins(o.MOV, [ops[0], rax])]
    elif opc is o.REM and ops[0].kind.flavor() != o.DK_FLAVOR_F:
        rax = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rax"], ops[0].kind)
        rdx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rdx"], ops[0].kind)
        return [ir.Ins(o.MOV, [rax, ops[1]]),
                ir.Ins(o.DIV, [rdx, rax, ops[2]]),  # note the notion of src/dst regs is murky here
                ir.Ins(o.MOV, [ops[0], rdx])]
    elif opc in {o.SHR, o.SHL} and isinstance(ops[2], ir.Reg):
        rcx = fun.FindOrAddCpuReg(regs.CPU_REGS_MAP["rcx"], ops[0].kind)
        mov = ir.Ins(o.MOV, [rcx, ops[2]])
        ops[2] = rcx
        mask = _SHIFT_MASK.get(ops[0].kind)
        if mask:
            return [mov, ir.Ins(o.AND, [rcx, rcx, mask]), ins]
        else:
            return [mov, ins]
    else:
        return None


def _FunRewriteDivRem(fun: ir.Fun) -> int:
    return ir.FunGenericRewrite(fun, _InsRewriteDivRemShifts)


def NeedsAABFromRewrite(ins: ir.Ins):
    opc = ins.opcode
    ops = ins.operands
    if opc.kind not in {o.OPC_KIND.ALU, o.OPC_KIND.LEA}:
        return False
    if opc in {o.DIV, o.REM} and ops[0].kind.flavor() != o.DK_FLAVOR_F:
        return False
    if opc in {o.LEA_MEM, o.LEA_STK}:
        return False
    return True


def _InsRewriteIntoAABForm(
        ins: ir.Ins, fun: ir.Fun) -> Optional[List[ir.Ins]]:
    ops = ins.operands
    if not NeedsAABFromRewrite(ins):
        return None
    if ops[0] == ops[1]:
        ops[0].flags |= ir.REG_FLAG.TWO_ADDRESS
        return None
    if ops[0] == ops[2] and o.OA.COMMUTATIVE in ins.opcode.attributes:
        ir.InsSwapOps(ins, 1, 2)
        ops[0].flags |= ir.REG_FLAG.TWO_ADDRESS
        return [ins]
    else:
        reg = fun.GetScratchReg(ins.operands[0].kind, "aab", False)
        reg.flags |= ir.REG_FLAG.TWO_ADDRESS
        return [ir.Ins(o.MOV, [reg, ops[1]]),
                ir.Ins(ins.opcode, [reg, reg, ops[2]]),
                ir.Ins(o.MOV, [ops[0], reg])]


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
    fun.cpu_live_in = regs.PushPopInterface.GetCpuRegsForInSignature(fun.input_types)
    fun.cpu_live_out = regs.PushPopInterface.GetCpuRegsForOutSignature(fun.output_types)
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
    optimize.FunCfgExit(fun, unit)  # not this may affect immediates as it flips branches

    # Handle most overflowing immediates.
    # This excludes immediates related to stack offsets which have not been determined yet
    _FunRewriteOutOfBoundsImmediates(fun, unit)

    # mul/div/rem need special treatment
    _FunRewriteDivRem(fun)

    _FunRewriteIntoAABForm(fun, unit)

    # Recompute Everything (TODO: make this more selective to reduce work)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    reg_stats.FunSeparateLocalRegUsage(fun)  # this has special hacks to avoid undoing _FunRewriteIntoAABForm()
    # DumpRegStats(fun, local_reg_stats)

    # if fun.name == "fibonacci": DumpFun("end of legal", fun)
    # if fun.name == "write_s": exit(1)
    sanity.FunCheck(fun, None)
    # optimize.FunOptBasic(fun, opt_stats, allow_conv_conversion=False)


KIND_AND_LAC = Tuple[o.DK, bool]


def _FunGlobalRegStats(fun: ir.Fun, reg_kind_map: Dict[o.DK, o.DK]) -> Dict[KIND_AND_LAC, List[ir.Reg]]:
    out: Dict[KIND_AND_LAC, List[ir.Reg]] = collections.defaultdict(list)
    for reg in fun.regs:
        if not reg.HasCpuReg() and ir.REG_FLAG.GLOBAL in reg.flags:
            out[(reg_kind_map[reg.kind], ir.REG_FLAG.LAC in reg.flags)].append(reg)
    for v in out.values():
        v.sort()
    return out


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
    if count == 0: return 0
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
        mask = _FindMaskCoveringTheLowOrderSetBits(global_lac, needed.global_lac)
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
    global_reg_stats = _FunGlobalRegStats(fun, regs.REG_KIND_TO_CPU_REG_FAMILY)
    DumpRegStats(fun, local_reg_stats, fout)

    pre_allocated_mask_gpr = 0
    for reg in fun.regs:
        if reg.HasCpuReg() and reg.cpu_reg.kind == regs.CpuRegKind.GPR:
            pre_allocated_mask_gpr |= 1 << reg.cpu_reg.no

    # Handle GPR regs
    needed_gpr = RegsNeeded(len(global_reg_stats[(regs.GPR_FAMILY, True)]),
                            len(global_reg_stats[(regs.GPR_FAMILY, False)]),
                            local_reg_stats.get((regs.GPR_FAMILY, True), 0),
                            local_reg_stats.get((regs.GPR_FAMILY, False), 0))
    if debug:
        print(f"@@ GPR NEEDED global lac={needed_gpr.global_lac} !lac={needed_gpr.global_not_lac}", file=debug)
        print(f"@@ GPR NEEDED local  lac={needed_gpr.local_lac} !lac={needed_gpr.local_not_lac}", file=debug)
        print(f"@@ GPR prealloc={pre_allocated_mask_gpr:x}", file=debug)
    gpr_global_lac, gpr_global_not_lac = _GetRegPoolsForGlobals(
        needed_gpr, regs.GPR_REGS_MASK & regs.GPR_LAC_REGS_MASK & ~regs.GPR_REG_IMPLICIT_MASK,
                    regs.GPR_REGS_MASK & ~regs.GPR_LAC_REGS_MASK & ~regs.GPR_REG_IMPLICIT_MASK, pre_allocated_mask_gpr)
    if debug:
        print(f"@@ GPR POOL global lac={gpr_global_lac:x} !lac={gpr_global_not_lac:x}", file=debug)

    # assign global lac
    regs.AssignCpuRegOrMarkForSpilling(
        global_reg_stats[(regs.GPR_FAMILY, True)], gpr_global_lac, 0)

    # assigned global not-lac
    regs.AssignCpuRegOrMarkForSpilling(
        global_reg_stats[(regs.GPR_FAMILY, False)],
        gpr_global_not_lac & ~regs.GPR_LAC_REGS_MASK,
        gpr_global_not_lac & regs.GPR_LAC_REGS_MASK)

    # Handle Float regs
    pre_allocated_mask_flt = 0
    for reg in fun.regs:
        if reg.HasCpuReg() and reg.cpu_reg.kind is regs.CpuRegKind.FLT:
            pre_allocated_mask_flt |= 1 << reg.cpu_reg.no

    needed_flt = RegsNeeded(len(global_reg_stats[(regs.FLT_FAMILY, True)]),
                            len(global_reg_stats[(regs.FLT_FAMILY, False)]),
                            local_reg_stats.get((regs.FLT_FAMILY, True), 0),
                            local_reg_stats.get((regs.FLT_FAMILY, False), 0))
    if debug:
        print(f"@@ FLT NEEDED {needed_flt.global_lac} {needed_flt.global_not_lac} "
              f"{needed_flt.local_lac} {needed_flt.local_not_lac}", file=debug)

    flt_global_lac, flt_global_not_lac = _GetRegPoolsForGlobals(
        needed_flt, regs.FLT_REGS_MASK & regs.FLT_LAC_REGS_MASK,
                    regs.FLT_REGS_MASK & ~regs.FLT_LAC_REGS_MASK, pre_allocated_mask_flt)
    if debug:
        print(f"@@ FLT POOL {flt_global_lac:x} {flt_global_not_lac:x}", file=debug)

    regs.AssignCpuRegOrMarkForSpilling(
        global_reg_stats[(regs.FLT_FAMILY, True)], flt_global_lac, 0)
    regs.AssignCpuRegOrMarkForSpilling(
        global_reg_stats[(regs.FLT_FAMILY, False)],
        flt_global_not_lac & ~regs.FLT_LAC_REGS_MASK,
        flt_global_not_lac & regs.FLT_LAC_REGS_MASK)

    # Recompute Everything (TODO: make this more selective to reduce work)
    reg_stats.FunComputeRegStatsExceptLAC(fun)
    reg_stats.FunDropUnreferencedRegs(fun)
    liveness.FunComputeLivenessInfo(fun)
    reg_stats.FunComputeRegStatsLAC(fun)
    # DumpRegStats(fun, local_reg_stats)
    # DumpFun("after global alloc", fun)


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
    isel_tab.FunAddNop1ForCodeSel(fun)
    regs.FunLocalRegAlloc(fun)
    fun.FinalizeStackSlots()
    # if fun.name == "fibonacci": DumpFun("after local alloc", fun)
    # DumpFun("after local alloc", fun)
    # cleanup
    _FunMoveEliminationCpu(fun)
    # print ("@@@@@@\n", "\n".join(serialize.FunRenderToAsm(fun)))
