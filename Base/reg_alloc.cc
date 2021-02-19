// (c) Robert Muth - see LICENSE for more info

#include "Base/reg_alloc.h"
#include "Base/liveness.h"
#include "Base/lowering.h"
#include "Util/parse.h"

#include <algorithm>

namespace cwerg::base {
namespace {

void HandleUseLiveRange(LiveRange* lr_use,
                        std::vector<LiveRange>* ranges,
                        RegPool* pool,
                        RegAllocLoggerFun debug) {
  for (unsigned i = 0; i < MAX_USES_PER_OPCODE && lr_use->use_def[i] != 0;
       ++i) {
    LiveRange& lr = (*ranges)[lr_use->use_def[i]];
    if (lr.last_use_pos != lr_use->def_pos) continue;
    if (lr.HasFlag(LR_FLAG::IGNORE)) continue;
    if (lr.HasFlag(LR_FLAG::PRE_ALLOC)) {
      if (debug) debug(lr, "end pre-alloc");
      pool->give_back_available_reg(lr.cpu_reg);
    } else {
      if (debug) debug(lr, "end");
      if (lr.cpu_reg != CPU_REG_SPILL) {
        pool->give_back_available_reg(lr.cpu_reg);
      }
    }
  }
}

void HandleDefLiveRange(LiveRange* lr,
                        std::vector<LiveRange>* ranges,
                        RegPool* pool,
                        RegAllocLoggerFun debug) {
  ASSERT(lr->cpu_reg == CPU_REG_INVALID, "");
  lr->cpu_reg = pool->get_available_reg(*lr);
  if (debug) debug(*lr, "start");
  if (lr->last_use_pos == NO_USE && lr->cpu_reg != CPU_REG_SPILL) {
    if (debug) debug(*lr, "no use");
    pool->give_back_available_reg(lr->cpu_reg);
  }
}

void SpillEarlierLiveRange(Reg reg,
                           unsigned def_pos,
                           int i,
                           const std::vector<LiveRange*>& ordered,
                           std::vector<LiveRange>* ranges,
                           RegPool* pool,
                           RegAllocLoggerFun debug) {
  const int kind_wanted = pool->get_cpu_reg_family(RegKind(reg));
  for (; i >= 0; --i) {
    LiveRange& lr = *ordered[i];
    if (lr.is_use_lr() || lr.HasFlag(LR_FLAG::IGNORE) ||
        lr.HasFlag(LR_FLAG::PRE_ALLOC) || lr.cpu_reg == CPU_REG_SPILL ||
        lr.last_use_pos <= def_pos ||
        pool->get_cpu_reg_family(RegKind(lr.reg)) != kind_wanted) {
      continue;
    }
    if (debug) debug(lr, "spilling this to free up reg");
    pool->give_back_available_reg(lr.cpu_reg);
    lr.cpu_reg = CPU_REG_SPILL;
    return;
  }
  ASSERT(false, "failed to free up reg for " << Name(reg));
}

int HandleDefLiveRangeFancy(int i,
                            const std::vector<LiveRange*>& ordered,
                            LiveRange* lr,
                            std::vector<LiveRange>* ranges,
                            RegPool* pool,
                            RegAllocLoggerFun debug) {
  HandleDefLiveRange(lr, ranges, pool, debug);
  if (lr->cpu_reg == CPU_REG_SPILL) {
    const LiveRange tmp_lr = LiveRange{lr->def_pos, NO_USE, lr->reg, 0};
    CpuReg tmp_reg = pool->get_available_reg(tmp_lr);
    if (tmp_reg == CPU_REG_SPILL) {
      if (debug) debug(*lr, "no scratch reg for spilled def");
      SpillEarlierLiveRange(lr->reg, lr->def_pos, i - 1, ordered, ranges, pool,
                            debug);
      tmp_reg = pool->get_available_reg(tmp_lr);
      ASSERT(tmp_reg != CPU_REG_SPILL, "cannot find tmp_reg");
    } else {
      if (debug) {
        debug(*lr, "scratch for spilled reg: " +
                       std::string(StrData(Name(tmp_reg))));
      }
    }
    pool->give_back_available_reg(tmp_reg);
  }
  return i + 1;
}

int HandleUseLiveRangeFancy(int i,
                            const std::vector<LiveRange*>& ordered,
                            LiveRange* lr_use,
                            std::vector<LiveRange>* ranges,
                            RegPool* pool,
                            RegAllocLoggerFun debug) {
  CpuReg spill_tmp_regs[MAX_USES_PER_OPCODE];
  unsigned num_spilled_tmp_regs = 0;

  for (unsigned x = 0; x < MAX_USES_PER_OPCODE && lr_use->use_def[x] != 0;
       ++x) {
    LiveRange& lr = (*ranges)[lr_use->use_def[x]];
    if (lr.HasFlag(LR_FLAG::IGNORE) or lr.HasFlag(LR_FLAG::PRE_ALLOC) ||
        lr.cpu_reg != CPU_REG_SPILL) {
      continue;
    }
    const LiveRange tmp_lr = LiveRange{lr_use->def_pos, NO_USE, lr.reg, 0};
    CpuReg tmp_reg = pool->get_available_reg(tmp_lr);
    if (tmp_reg == CPU_REG_SPILL) {
      if (debug) {
        std::ostringstream os;
        os << "[" << x << "] no scratch reg for spilled use at "
           << lr_use->def_pos;
        debug(lr, os.str());
      }
      SpillEarlierLiveRange(lr.reg, lr.def_pos, i - 1, ordered, ranges, pool,
                            debug);
      tmp_reg = pool->get_available_reg(tmp_lr);
      ASSERT(tmp_reg != CPU_REG_SPILL, "cannot find tmp_reg");
    }
    spill_tmp_regs[num_spilled_tmp_regs++] = tmp_reg;
    if (debug) {
      std::ostringstream os;
      os << "[" << x << "] scratch reg for spilled use at " << lr_use->def_pos
         << ": " << Name(tmp_reg);
      debug(lr, os.str());
    }
  }

  HandleUseLiveRange(lr_use, ranges, pool, debug);
  for (unsigned x = 0; x < num_spilled_tmp_regs; x++) {
    pool->give_back_available_reg(spill_tmp_regs[x]);
  }
  return i + 1;
}

}  // namespace

void RegisterAssignerLinearScan(const std::vector<LiveRange*>& ordered,
                                std::vector<LiveRange>* ranges,
                                RegPool* pool,
                                RegAllocLoggerFun debug) {
  for (int i = 0; i < ordered.size(); ++i) {
    LiveRange& lr = *ordered[i];
    ASSERT(i == 0 || *ordered[i - 1] < lr,
           *ordered[i - 1] << " not smaller than " << lr);
    if (lr.is_use_lr()) {
      HandleUseLiveRange(&lr, ranges, pool, debug);
    } else {
      if (lr.HasFlag(LR_FLAG::PRE_ALLOC) || lr.HasFlag(LR_FLAG::IGNORE)) {
        continue;
      }
      HandleDefLiveRange(&lr, ranges, pool, debug);
    }
  }
}

void RegisterAssignerLinearScanFancy(const std::vector<LiveRange*>& ordered,
                                     std::vector<LiveRange>* ranges,
                                     RegPool* pool,
                                     RegAllocLoggerFun debug) {
  for (int i = 0; i < ordered.size(); ++i) {
    LiveRange& lr = *ordered[i];
    ASSERT(i == 0 || *ordered[i - 1] < lr,
           *ordered[i - 1] << " not smaller than " << lr);
    if (lr.is_use_lr()) {
      HandleUseLiveRangeFancy(i, ordered, &lr, ranges, pool, debug);
    } else {
      if (lr.HasFlag(LR_FLAG::PRE_ALLOC) || lr.HasFlag(LR_FLAG::IGNORE)) {
        continue;
      }
      HandleDefLiveRangeFancy(i, ordered, &lr, ranges, pool, debug);
    }
  }
}

void PreAllocation::add(const LiveRange* lr) {
  if (!ranges_.empty()) {
    ASSERT(*ranges_.back() < *lr, ranges_.back() << " not smaller than " << lr);
  }
  ranges_.push_back(lr);
}

bool PreAllocation::has_conflict(const LiveRange& lr) {
  if (ranges_.empty()) return false;
  while (current_ < ranges_.size()) {
    const LiveRange* top = ranges_[current_];
    if (top->last_use_pos <= lr.def_pos) {
      ++current_;
      continue;
    }
    return top->def_pos < lr.last_use_pos;
  }
  return false;
}

void BblSpillRegs(Bbl bbl, Fun fun, DK offset, std::vector<Ins>* inss) {
  inss->clear();
  bool dirty = false;
  for (Ins ins : BblInsIter(bbl)) {
    const unsigned num_defs = InsOpcode(ins).num_defs;
    unsigned num_ld = 0;
    unsigned num_st = 0;
    // Note: backwards iteration (uses before defs)
    for (int i = InsOpcode(ins).num_operands - 1; i >= 0; --i) {
      const Reg reg = Reg(InsOperand(ins, i));
      if (reg.kind() != RefKind::REG) continue;
      const Stk stk = RegSpillSlot(reg);
      if (stk.isnull()) continue;
      dirty = true;
      if (i >= num_defs) {
        ++num_ld;
        Reg tmp = FunGetScratchReg(fun, RegKind(reg), "ldspill", false);
        inss->push_back(InsNew(OPC::LD_STK, tmp, stk, ConstNewU(offset, 0)));
        InsOperand(ins, i) = tmp;
      } else {
        if (num_st == 0) {
          inss->push_back(ins);
        }
        ++num_st;
        Reg tmp = FunGetScratchReg(fun, RegKind(reg), "stspill", false);
        inss->push_back(InsNew(OPC::ST_STK, stk, ConstNewU(offset, 0), tmp));
        InsOperand(ins, i) = tmp;
      }
    }
    if (num_st == 0) {
      inss->push_back(ins);
    }
  }

  if (dirty) {
    BblReplaceInss(bbl, *inss);
  }
}

Stk RegCreateSpillSlot(Reg reg, Fun fun) {
  uint32_t size = DKBitWidth(RegKind(reg)) / 8;
  char buf[kMaxIdLength];
  Str name =
      StrNew(StrCat(buf, sizeof(buf), "$spill", "_", StrData(Name(reg))));
  Stk stk = StkNew(name, size, size);
  FunStkAdd(fun, stk);
  return stk;
}

void FunCreateStackSlotsForMarkedRegs(Fun fun) {
  for (Reg reg : FunRegIter(fun)) {
    if (RegHasFlag(reg, REG_FLAG::MARKED)) {
      RegClearFlag(reg, REG_FLAG::MARKED);
      RegSpillSlot(reg) = RegCreateSpillSlot(reg, fun);
    } else {
      RegSpillSlot(reg) = Stk(0);
    }
  }
}

void FunSpillRegs(Fun fun,
                  DK offset_kind,
                  const std::vector<Reg>& regs,
                  std::vector<Ins>* inss) {
  for (Reg reg : FunRegIter(fun)) RegSpillSlot(reg) = Stk(0);

  for (Reg reg : regs) RegSpillSlot(reg) = RegCreateSpillSlot(reg, fun);

  for (Bbl bbl : FunBblIter(fun)) {
    BblSpillRegs(bbl, fun, offset_kind, inss);
  }
  for (Reg reg : FunRegIter(fun)) RegSpillSlot(reg) = Stk(0);
}

}  // namespace cwerg::base
