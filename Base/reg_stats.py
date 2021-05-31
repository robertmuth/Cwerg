"""Register Allocation Statistics Helper

* FunRegStats needs to be accurate because it is used to make spilling decisions
* The terms global and local register are WRT to the function
* A registers is NOT global just because it is referenced in multiple Bbls
  it actually has to be live across Bbls (appear in a live-out set)
* A Bbl may contain mutliple calls
* "lac" stands for "live across calls", both local and global registers may be "lac"

"""

import collections
import dataclasses
from typing import List, Dict, Tuple, Set

from Base import ir
from Base import liveness
from Base import reg_alloc
import Base.opcode_tab as o

REG_KIND_LAC = Tuple[o.DK, bool]


class BblRegUsageStatsRegPool(reg_alloc.RegPool):
    """Regpool for determining register pressure at the Bbl level

    Can be used repeatedly in which case it will  compute the maximum
    register pressure over a set of Bbls
    """

    def __init__(self, reg_kind_map: Dict[o.DK, o.DK]):
        super(BblRegUsageStatsRegPool, self).__init__()
        self.counter = 0
        self.reg_kind_map = reg_kind_map
        self._available: Dict[REG_KIND_LAC,
                              List[ir.CpuReg]] = collections.defaultdict(list)

    def _get_reg_class(self, lr: reg_alloc.LiveRange) -> REG_KIND_LAC:
        return self.reg_kind_map[lr.reg.kind], liveness.LiveRangeFlag.LAC in lr.flags

    # @override
    def get_available_reg(self, lr: liveness.LiveRange) -> ir.CpuReg:
        key: REG_KIND_LAC = self._get_reg_class(lr)
        available = self._available.get(key)
        if available:
            return available.pop(-1)
        else:
            # manufacture a new register
            self.counter += 1
            return ir.CpuReg(f"z{self.counter}", key[1], key[0].value)

    def usage(self) -> Dict[REG_KIND_LAC, int]:
        assert sum(len(val)
                   for val in self._available.values()) == self.counter
        return {key: len(val) for (key, val) in self._available.items()}

    # @override
    def give_back_available_reg(self, cpu_reg: ir.CpuReg):
        key: REG_KIND_LAC = (o.DK(cpu_reg.kind), bool(cpu_reg.no))
        self._available[key].append(cpu_reg)


def LiveRangeShouldBeIgnored(lr: liveness.LiveRange, reg_kind_map) -> bool:
    if lr.is_cross_bbl(): return True
    if lr.is_use_lr(): return False  # this is an entry for "uses"
    if lr.reg.kind not in reg_kind_map: return True
    return lr.reg.HasCpuReg()


def FunComputeBblRegUsageStats(fun: ir.Fun,
                               reg_kind_map: Dict[o.DK, o.DK]) -> Dict[REG_KIND_LAC, int]:
    """
    Computes maximum number of register needed for locals across all Bbls

    Requires liveness
    """
    pool = BblRegUsageStatsRegPool(reg_kind_map)
    for bbl in fun.bbls:
        live_ranges = liveness.BblGetLiveRanges(bbl, fun, bbl.live_out, True)
        # we do not want re-use of regs that are not coming from the pool
        for lr in live_ranges:
            if LiveRangeShouldBeIgnored(lr, reg_kind_map):
                lr.flags |= liveness.LiveRangeFlag.IGNORE
        reg_alloc.RegisterAssignerLinearScan(live_ranges, pool)
    return pool.usage()


def FunComputeRegStatsExceptLAC(fun: ir.Fun):
    """Updates Reg info: Sets def_ins, def_bbl and the flags:

    GLOBAL, MULTIDEF, IS_READ. MULTI_READ

    Note, the computation of GLOBAL is conservative in that locally used
    regs may appear global if they occur in multiple bbls.

    Once we have renamed those registers via FunSeparateLocalRegUsage the issue goes away
    """
    for reg in fun.regs:
        reg.def_ins = ir.INS_INVALID
        reg.def_bbl = ir.BBL_INVALID
        reg.flags = ir.REG_FLAG(0)
    for bbl in fun.bbls:
        for ins in bbl.inss:
            num_defs = ins.opcode.def_ops_count()
            for n, reg in enumerate(ins.operands):
                if not isinstance(reg, ir.Reg):
                    continue
                if n < num_defs:
                    if reg.def_ins is ir.INS_INVALID:
                        reg.def_ins = ins
                        reg.def_bbl = bbl
                    else:
                        reg.flags |= ir.REG_FLAG.MULTI_DEF
                        if bbl != reg.def_bbl:
                            reg.flags |= ir.REG_FLAG.GLOBAL
                else:
                    if reg.flags & ir.REG_FLAG.IS_READ:
                        reg.flags |= ir.REG_FLAG.MULTI_READ
                    else:
                        reg.flags |= ir.REG_FLAG.IS_READ
                    if bbl != reg.def_bbl:
                        reg.flags |= ir.REG_FLAG.GLOBAL


def FunComputeRegStatsLAC(fun: ir.Fun):
    """Updates Reg info: Sets flags: GLOBAL, LAC

    Note the GLOBAL flags computation is more accurate than FunComputeRegStatsExceptLAC.
    """
    for reg in fun.regs:
        reg.flags &= ~(ir.REG_FLAG.GLOBAL | ir.REG_FLAG.LAC)
    for bbl in fun.bbls:
        live_out = bbl.live_out.copy()
        for ins in reversed(bbl.inss):
            if ins.opcode.is_call():
                for reg in live_out:
                    reg.flags |= ir.REG_FLAG.LAC
            num_defs = ins.opcode.def_ops_count()
            for n, reg in enumerate(ins.operands):
                if not isinstance(reg, ir.Reg): continue
                if n < num_defs:
                    live_out.discard(reg)
                else:
                    live_out.add(reg)
        for reg in live_out:
            reg.flags |= ir.REG_FLAG.GLOBAL


def FunDropUnreferencedRegs(fun: ir.Fun) -> int:
    """Remove all regs which are no longer referenced"""
    to_be_removed: List[ir.Reg] = []
    for reg in fun.regs:
        if reg.def_ins == ir.INS_INVALID and ir.REG_FLAG.IS_READ not in reg.flags:
            to_be_removed.append(reg)
    for reg in to_be_removed:
        fun.regs.remove(reg)
        del fun.reg_syms[reg.name]
    return len(to_be_removed)


@dataclasses.dataclass(init=True)
class FunRegStats:
    global_lac = 0
    global_not_lac = 0
    local_lac = 0
    local_not_lac = 0

    def __str__(self):
        return (
            f"{self.global_lac:2}/{self.global_not_lac:2}  "
            f"{self.local_lac:2}/{self.local_not_lac:2}")


def FunCalculateRegStats(fun: ir.Fun) -> FunRegStats:
    rs = FunRegStats()
    for reg in fun.regs:
        if ir.REG_FLAG.GLOBAL in reg.flags:
            if ir.REG_FLAG.LAC in reg.flags:
                rs.global_lac += 1
            else:
                rs.global_not_lac += 1
        else:
            if ir.REG_FLAG.LAC in reg.flags:
                rs.local_lac += 1
            else:
                rs.local_not_lac += 1
    return rs


def _BblRenameReg(bbl, pos, reg_src, reg_dst):
    done = False
    for ins in bbl.inss[pos:]:
        num_defs = ins.opcode.def_ops_count()
        for n, reg in enumerate(ins.operands):
            if reg != reg_src:
                continue
            if n < num_defs:
                done = True
            else:
                ins.operands[n] = reg_dst
        if done:
            return


def FunSeparateLocalRegUsage(fun: ir.Fun) -> int:
    count = 0
    for bbl in fun.bbls:
        for pos, ins in enumerate(bbl.inss):
            num_defs = ins.opcode.def_ops_count()
            for n, reg in enumerate(ins.operands[:num_defs]):
                assert isinstance(reg, ir.Reg)
                if reg.def_ins is ins or ir.REG_FLAG.GLOBAL in reg.flags or reg.cpu_reg is not None:
                    continue
                purpose = reg.name
                if purpose.startswith("$"):
                    underscore_pos = purpose.find("_")
                    purpose = purpose[underscore_pos + 1:]
                new_reg = fun.GetScratchReg(reg.kind, purpose, False)
                ins.operands[n] = new_reg
                _BblRenameReg(bbl, pos + 1, reg, new_reg)
                count += 1
    return count


def FunPreallocatedRegs(fun: ir.Fun) -> Set[ir.CpuReg]:
    out: Set[ir.CpuReg] = set()
    for reg in fun.regs:
        if reg.cpu_reg:
            out.add(reg.cpu_reg)
    return out
