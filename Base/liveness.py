"""This file contains code for Register Liveness analysis and
optimization depending on it, e.g. useless code removal"""

import dataclasses
from typing import List, Tuple, Set, Dict
import enum

from Base import ir
from Base import cfg
from Base import opcode_tab as o


@dataclasses.dataclass()
class Liveness:
    """Liveness summary for Bbl

    Only live_out is used for optimizations. live_in, live_def, live_use
    are used  only during the analysis phase.
    """

    live_in: Set[ir.Reg] = dataclasses.field(default_factory=set)
    live_out: Set[ir.Reg] = dataclasses.field(default_factory=set)
    # defined
    live_def: Set[ir.Reg] = dataclasses.field(default_factory=set)
    # used before defined
    live_use: Set[ir.Reg] = dataclasses.field(default_factory=set)


def InsMaybeReplaceDefReg(ins: ir.Ins, reg_old: ir.Reg, reg_new: ir.Reg) -> int:
    """If the ins writes reg_old, replace it with reg_new """
    if ins.opcode.def_ops_count() == 0:
        return 0
    assert ins.opcode.def_ops_count() == 1
    op = ins.operands[0]
    if op == reg_old:
        ins.operands[0] = reg_new
    return 1


def InsMaybeReplaceUseReg(ins: ir.Ins, reg_old: ir.Reg, reg_new: ir.Reg) -> int:
    """If the ins reads reg_old, replace it with reg_new """
    it = enumerate(ins.operands)
    # skip register writing operands
    for _ in range(ins.opcode.def_ops_count()):
        next(it)
    count = 0
    for n, op in it:
        if op == reg_old:
            ins.operands[n] = reg_new
            count += 1
    return count


def _InsUpdateDefUse(ins: ir.Ins, fun: ir.Fun, defs: Set[ir.Reg], uses: Set[ir.Reg]):
    """Compute the set of defined and used registers for each instruction"""
    if ins.opcode.is_call():
        # note: a call instruction may have at most one used reg if opcode is JSR
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        for cpu_reg in callee.cpu_live_out:
            # we intentionally iterate overall regs here
            for reg in fun.regs:
                if reg.cpu_reg is cpu_reg:
                    defs.add(reg)
                    uses.discard(reg)
        # for cpu_reg in callee.cpu_live_clobber:
        #     defs.add(cpu_reg)
        #     uses.discard(cpu_reg)
        # for cpu_reg in callee.cpu_live_in:
        #     uses.add(cpu_reg)

    num_defs = ins.opcode.def_ops_count()
    for n, reg in enumerate(ins.operands):
        if not isinstance(reg, ir.Reg): continue
        if n < num_defs:
            defs.add(reg)
            uses.discard(reg)
        else:
            uses.add(reg)


def _BblDefUse(bbl: ir.Bbl, fun: ir.Fun) -> Tuple[Set[ir.Reg], Set[ir.Reg]]:
    bbl_def: Set[ir.Reg] = set()
    bbl_use: Set[ir.Reg] = set()
    for ins in reversed(bbl.inss):
        _InsUpdateDefUse(ins, fun, bbl_def, bbl_use)
    return bbl_def, bbl_use


def _InsUpdateLiveness(ins: ir.Ins, fun: ir.Fun, live_out: Set[ir.Reg]) -> bool:
    """Similar to _InsUpdateDefUse but also checks if the instruction is useless"""
    if ins.opcode.is_call():
        # note: a call instruction may have at most one used reg if opcode is JSR
        callee: ir.Fun = cfg.InsCallee(ins)
        assert isinstance(callee, ir.Fun)
        for cpu_reg in callee.cpu_live_out:
            for reg in fun.regs:
                if reg.cpu_reg is cpu_reg:
                    live_out.discard(reg)

    # TODO: take cpu_live_in into account, otherwise we cannot eliminate useless code
    #       after pusharg and poparg convdersions
    #         live_out.discard(cpu_reg)
    #     for cpu_reg in callee.cpu_live_clobber:
    #         live_out.discard(cpu_reg)
    #     for cpu_reg in callee.cpu_live_in:
    #         live_out.add(cpu_reg)

    is_live = ins.opcode.has_side_effect()
    num_defs = ins.opcode.def_ops_count()
    for n, reg in enumerate(ins.operands):
        if not isinstance(reg, ir.Reg): continue

        if n < num_defs:
            if reg in live_out:
                is_live = True
            live_out.discard(reg)
        else:
            # all defs precede the uses, so if the ins is not live at this point,
            # we can skip the
            if not is_live:
                break
            live_out.add(reg)
    return is_live


def _BblRemoveUselessInstructions(bbl: ir.Bbl, fun: ir.Fun) -> int:
    live_out = bbl.live_out.copy()
    old_count = len(bbl.inss)
    keep = []
    for ins in reversed(bbl.inss):
        if _InsUpdateLiveness(ins, fun, live_out):
            keep.append(ins)
    bbl.inss = list(reversed(keep))
    return old_count - len(keep)


def FunRemoveUselessInstructions(fun: ir.Fun) -> int:
    assert ir.FUN_FLAG.LIVENESS_VALID in fun.flags
    return ir.FunGenericRewriteBbl(fun, _BblRemoveUselessInstructions)


def _FunLivenessFixpoint(fun: ir.Fun,
                         all_liveness: Dict[str, Liveness]) -> int:
    """ Standard backward flow liveness computation"""
    count = 0
    active = fun.bbls[:]
    while active:
        count += 1
        bbl = active.pop(-1)
        # print(f"@@ processing {bbl.name}")
        liveness = all_liveness[bbl.name]
        live_in = liveness.live_out.copy()
        live_in.difference_update(liveness.live_def)
        live_in.update(liveness.live_use)
        if len(live_in) <= len(liveness.live_in):
            continue
        liveness.live_in = live_in

        for pred in bbl.edge_in:
            pred_liveness = all_liveness[pred.name]
            old_len = len(pred_liveness.live_out)
            pred_liveness.live_out.update(liveness.live_in)
            if len(pred_liveness.live_out) > old_len:
                if pred not in active:
                    active.append(pred)

    return count


def FunComputeLivenessInfo(fun: ir.Fun) -> int:
    """Assumes that cfg.funInitCFG has been called"""
    if len(fun.bbls) > 1:
        assert len(fun.bbls[0].edge_out) > 0, f"you must run cfg.FunInitCFG"
    all_liveness: Dict[str, Liveness] = {}
    for bbl in fun.bbls:
        liveness = Liveness()
        liveness.live_def, liveness.live_use = _BblDefUse(bbl, fun)
        # if bbl.IsReturn():
        #     liveness.live_out = set(fun.cpu_live_out)
        all_liveness[bbl.name] = liveness
    rounds = _FunLivenessFixpoint(fun, all_liveness)
    for bbl in fun.bbls:
        bbl.live_out = all_liveness[bbl.name].live_out
    fun.flags |= ir.FUN_FLAG.LIVENESS_VALID
    return rounds


def _HandleSpillForIns(ins: ir.Ins, regs_to_be_spilled: Set[str],
                       spill_slots, ld_spill, st_spill, zero):
    out_ld = []
    out_st = []

    def_count = ins.opcode.def_ops_count()

    def maybe_add_spill(pos, reg: ir.Reg):
        if reg.name not in regs_to_be_spilled:
            return
        if pos < def_count:
            out_st.append(ir.Ins(
                st_spill, [spill_slots[reg.name], zero, reg]))
        else:
            out_ld.append(ir.Ins(
                ld_spill, [reg, spill_slots[reg.name], zero]))

    for n, op in enumerate(ins.operands):
        if isinstance(op, ir.Reg):
            maybe_add_spill(n, op)

    return out_ld + [ins] + out_st


BEFORE_BBL = -32000
AFTER_BBL = 32000
NO_USE = AFTER_BBL + 1


@enum.unique
class LiveRangeFlag(enum.Flag):
    LAC = 1  # live across call
    PRE_ALLOC = 2  # already allocated - re-use reg after last_use
    IGNORE = 4  # ignore completely


@dataclasses.dataclass()
class LiveRange:
    """Represents and intra Bbl live-range

    if reg == REG_INVALID - this is a fake liverange
    """
    def_pos: int
    last_use_pos: int
    reg: ir.Reg  # contains a proper register
    num_uses: int
    uses: List["LiveRange"] = dataclasses.field(default_factory=list)
    flags: LiveRangeFlag = LiveRangeFlag(0)
    cpu_reg: ir.CpuReg = ir.CPU_REG_INVALID

    def is_cross_bbl(self):
        return self.last_use_pos is AFTER_BBL or self.def_pos is BEFORE_BBL

    def is_use_lr(self):
        return self.reg is ir.REG_INVALID

    def __lt__(self, other: "LiveRange"):
        """This will order uses before defs

        because def_pos and last_use_pos are the same for "use lr's" but different for def lr's
        """
        return ((self.def_pos, self.last_use_pos) <
                (other.def_pos, other.last_use_pos))

    def __repr__(self):
        def render_pos(pos):
            if pos == BEFORE_BBL: return "BB"
            if pos == AFTER_BBL: return "AB"
            if pos == NO_USE: return "NU"
            return f"{pos:2d}"

        flags_str = ""
        if self.flags:
            flags_str = f" {' '.join(f.name for f in LiveRangeFlag if f in self.flags)}"

        if self.is_use_lr():
            # commented to make output compatible with c++ implementation
            starts = ",".join([f"{lr.reg.name}:{lr.def_pos}" for lr in self.uses])
            extra_str = f" uses:{starts}"
            # extra_str = f" uses:{len(self.uses)}"
        else:
            extra_str = f" def:{self.reg.name}:{self.reg.kind.name}"
            if self.cpu_reg is ir.CPU_REG_SPILL:
                flags_str += " SPILLED"
            elif self.cpu_reg != ir.CPU_REG_INVALID:
                extra_str += "@" + self.cpu_reg.name
        return f"LR {render_pos(self.def_pos)} - {render_pos(self.last_use_pos)}{flags_str}{extra_str}"


def BblGetLiveRanges(bbl: ir.Bbl, fun: ir.Fun, live_out: Set[ir.Reg], emit_uses: bool) -> List[LiveRange]:
    """ LiveRanges are use to do register allocation

    Note: function call handling is quite adhoc and likely has bugs.
    The output contains the following special LiveRanges
    * LRs without a last_use if the register is used outside the Bbl (based on live_out)
    * LRs without a def of the register is defined outside the Bbl
    * [if emit_uses] use-def LRs contain the LRs of all the used regs in the instruction at point p.
                     (def=p last_use=p,  reg=REG_INVALID)
    """
    out = []
    bbl_size = len(bbl.inss)

    last_use: Dict[ir.Reg, LiveRange] = {}
    last_call_pos = -1
    last_call_cpu_live_in = []

    def initialize_lr(pos: int, reg: ir.Reg) -> LiveRange:
        lr = LiveRange(-1, pos, reg, 1)
        last_use[reg] = lr
        out.append(lr)
        return lr

    def finalize_lr(lr: LiveRange, def_pos: int):
        lr.def_pos = def_pos
        if (last_call_pos != -1 and last_call_pos != AFTER_BBL and
                last_call_pos < lr.last_use_pos):
            lr.flags |= LiveRangeFlag.LAC
        del last_use[lr.reg]

    # handle live ranges that extend passed the bbl
    for reg in live_out:
        initialize_lr(AFTER_BBL, reg)

    for pos, ins in enumerate(reversed(bbl.inss)):
        pos = bbl_size - 1 - pos
        if ins.opcode is o.RET:
            if fun.cpu_live_out:
                last_call_cpu_live_in = fun.cpu_live_out
                last_call_pos = AFTER_BBL
        elif ins.opcode.is_call():
            callee: ir.Fun = cfg.InsCallee(ins)
            assert isinstance(callee, ir.Fun)
            # This complication only applies after we have (partial) reg allocation
            # Finalize live ranges using the results of the call
            if callee.cpu_live_out:
                # Note, destructive list iteration -> `list(...)` is necessary
                for reg, lr in list(last_use.items()):
                    if reg.HasCpuReg() and reg.cpu_reg in callee.cpu_live_out:
                        finalize_lr(lr, pos)
            last_call_cpu_live_in = callee.cpu_live_in
            last_call_pos = pos  # setting this after dealing with cpu_live_out seems right

        num_defs = ins.opcode.def_ops_count()
        uses = []
        for n, reg in enumerate(ins.operands):
            if not isinstance(reg, ir.Reg): continue
            if n < num_defs:  # define reg
                lr = last_use.get(reg)
                if lr:
                    finalize_lr(lr, pos)
                else:
                    last_use_pos = NO_USE
                    # Note: likely this makes some assumptions about the adjacency
                    # of these instruction and the call: We assume this cannot be LAC!
                    if reg.HasCpuReg() and reg.cpu_reg in last_call_cpu_live_in:
                        last_use_pos = last_call_pos
                    out.append(LiveRange(pos, last_use_pos, reg, 0))
            else:  # used reg
                lr = last_use.get(reg)
                if lr:
                    lr.num_uses += 1
                else:
                    lr = initialize_lr(pos, reg)
                if lr not in uses:
                    uses.append(lr)
        if emit_uses and uses:
            # Note "pos, pos" ensure that this record will come before
            #       a regular record after sorting
            out.append(LiveRange(pos, pos, ir.REG_INVALID, 0, uses))

    for lr in list(last_use.values()):
        finalize_lr(lr, BEFORE_BBL)
    return out
