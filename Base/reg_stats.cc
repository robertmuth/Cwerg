// (c) Robert Muth - see LICENSE for more info

#include "Base/reg_stats.h"
#include "Base/liveness.h"
#include "Base/opcode_gen.h"
#include "Base/reg_alloc.h"
#include "Base/serialize.h"

#include <iomanip>
#include <map>

// #define TRACE_REG_ALLOC

namespace cwerg::base {
namespace {

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

class BblRegUsageStatsRegPool : public RegPool {
 public:
  explicit BblRegUsageStatsRegPool(const DK_MAP& rk_map) : rk_map_(rk_map) {}

  CpuReg get_available_reg(const LiveRange& lr) override {
    const DK dk = get_rk(lr.reg);
    const bool lac = lr.HasFlag(LR_FLAG::LAC);
    std::vector<CpuReg>& pool = (lac ? available_lac_ : available_not_lac_)[dk];
    // Note: the cpu_reg is a fake handle
    CpuReg cpu_reg;
    if (pool.empty()) {
      ++counter_;
      cpu_reg = CpuReg(counter_ | (+dk << 16U) | (lac << 15U));
    } else {
      cpu_reg = pool.back();
      pool.pop_back();
    }
#ifdef TRACE_REG_ALLOC
    std::cout << (cpu_reg.index() & 0xffff) << " " << int(dk) << " <- " << lr
              << "\n";
#endif
    return cpu_reg;
  }

  uint8_t get_cpu_reg_family(DK dk) override { return rk_map_[+dk]; }

  void give_back_available_reg(CpuReg cpu_reg) override {
#ifdef TRACE_REG_ALLOC
    std::cout << "FREE: " << (cpu_reg.index() & 0xffff) << "\n";
#endif
    const DK dk = static_cast<DK>((cpu_reg.index() >> 16U) & 0xff);
    const bool lac = (cpu_reg.index() >> 15U) & 1U;
    std::vector<CpuReg>& pool = (lac ? available_lac_ : available_not_lac_)[dk];
    pool.push_back(cpu_reg);
  }

  DK_LAC_COUNTS usage() const {
    DK_LAC_COUNTS out;
    for (auto& [k, v] : available_lac_) {
      out.lac[+k] += v.size();
    }
    for (auto& [k, v] : available_not_lac_) {
      out.not_lac[+k] += v.size();
    }
    unsigned count = 0;
    for (size_t i = 0; i < out.lac.size(); ++i) {
      count += out.lac[i] + out.not_lac[i];
    }
    ASSERT(count == counter_, "expected reg_num: " << counter_ << " actual "
                                                   << count << "\n"
                                                   << out);
    return out;
  }

  unsigned counter() const { return counter_; }

 private:
  DK get_rk(Reg reg) {
    const DK out = DK(rk_map_[+RegKind(reg)]);
    ASSERT(out != DK::INVALID, "reg has untracked type: " << Name(reg));
    return out;
  }

  const DK_MAP& rk_map_;

  std::map<DK, std::vector<CpuReg>> available_lac_;
  std::map<DK, std::vector<CpuReg>> available_not_lac_;
  unsigned counter_ = 0;
};

bool LiveRangeShouldBeIgnored(const LiveRange& lr, const DK_MAP& rk_map) {
  if (lr.is_cross_bbl()) return true;
  if (lr.is_use_lr()) return false;
  if (rk_map[+RegKind(lr.reg)] == +DK::INVALID) return true;
  return !RegCpuReg(lr.reg).isnull();
}

}  // namespace

DK_LAC_COUNTS FunComputeBblRegUsageStats(Fun fun, const DK_MAP& rk_map) {
  const unsigned num_regs = FunNumRegs(fun);
  const Reg* const reg_map = (Reg*)FunRegMap(fun).BackingStorage();
  std::vector<Reg> live_out;

  BblRegUsageStatsRegPool pool(rk_map);
  for (Bbl bbl : FunBblIter(fun)) {
    live_out.clear();
    const BitVec& live_out_vec = BblLiveOut(bbl);
    for (int i = 1; i < num_regs; ++i) {
      if (live_out_vec.BitGet(i)) live_out.push_back(reg_map[i]);
    }

    std::vector<LiveRange> ranges = BblGetLiveRanges(bbl, fun, live_out, true);
    std::vector<LiveRange*> ordered;
    // Skip the first range which is a dummy
    for (unsigned i = 1; i < ranges.size(); ++i) ordered.push_back(&ranges[i]);
    std::sort(begin(ordered), end(ordered),
              [](LiveRange* lhs, LiveRange* rhs) { return *lhs < *rhs; });
#ifdef TRACE_REG_ALLOC
    std::cout
        << "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n";
    BblRenderToAsm(bbl, fun, &std::cout);
    for (const auto& lr : ordered) {
      std::cout << *lr << "\n";
    }
#endif
    for (LiveRange& lr : ranges) {
      if (LiveRangeShouldBeIgnored(lr, rk_map)) {
        lr.SetFlag(LR_FLAG::IGNORE);
      }
    }
    RegisterAssignerLinearScan(ordered, &ranges, &pool);
  }

  return pool.usage();
}

std::ostream& operator<<(std::ostream& os, const DK_LAC_COUNTS& usage) {
  unsigned lac = 0;
  unsigned not_lac = 0;
  for (size_t i = 0; i < usage.lac.size(); ++i) {
    lac += usage.lac[i];
    not_lac += usage.not_lac[i];
  }
  os << std::setw(2) << lac << "/" << std::setw(2) << not_lac;
  return os;
}

void FunComputeRegStatsExceptLAC(Fun fun) {
  for (Reg reg : FunRegIter(fun)) {
    RegFlags(reg) &=
        ~(+REG_FLAG::MULTI_DEF | +REG_FLAG::GLOBAL | +REG_FLAG::IS_READ);
    RegDefIns(reg) = Ins(0);
    RegDefBbl(reg) = Bbl(0);
  }
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      const unsigned num_defs = InsOpcode(ins).num_defs;
      const unsigned num_ops = InsOpcode(ins).num_operands;
      for (unsigned i = 0; i < num_defs; ++i) {
        Reg reg = Reg(InsOperand(ins, i));  // must be a reg
        if (RegDefIns(reg).isnull()) {      // first definition
          RegDefIns(reg) = ins;
          RegDefBbl(reg) = bbl;
        } else {  // not the first definition
          RegFlags(reg) |= +REG_FLAG::MULTI_DEF;
          if (RegDefBbl(reg) != bbl) {
            RegFlags(reg) |= +REG_FLAG::GLOBAL;
          }
        }
      }
      for (unsigned i = num_defs; i < num_ops; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        if (reg.kind() != RefKind::REG) continue;
        if (RegHasFlag(reg, REG_FLAG::IS_READ)) {
          RegFlags(reg) |= +REG_FLAG::MULTI_READ;
        } else {
          RegFlags(reg) |= +REG_FLAG::IS_READ;
        }
        if (RegDefBbl(reg) != bbl) {
          RegFlags(reg) |= +REG_FLAG::GLOBAL;
        }
      }
    }
  }
}

void FunComputeRegStatsLAC(Fun fun) {
  for (Reg reg : FunRegIter(fun)) {
    // we will (re)compute these
    RegFlags(reg) &= ~(+REG_FLAG::GLOBAL | +REG_FLAG::LAC);
  }
  const unsigned num_regs = FunNumRegs(fun);
  BitVec live = BitVec::New(num_regs);
  const Reg* const reg_map = (Reg*)FunRegMap(fun).BackingStorage();
  for (Bbl bbl : FunBblIter(fun)) {
    live.CopyFrom(BblLiveOut(bbl));
    for (Ins ins : BblInsIterReverse(bbl)) {
      if (InsOpcode(ins).IsCall()) {
        for (unsigned i = 1; i < num_regs; ++i) {
          if (live.BitGet(i)) {
            RegFlags(reg_map[i]) |= +REG_FLAG::LAC;
          }
        }
      }
      const unsigned num_defs = InsOpcode(ins).num_defs;
      const unsigned num_ops = InsOpcode(ins).num_operands;
      for (unsigned i = 0; i < num_defs; ++i) {
        const Reg reg = Reg(InsOperand(ins, i));
        live.BitClear(RegNo(reg));
      }

      for (unsigned i = num_defs; i < num_ops; ++i) {
        const Reg reg = Reg(InsOperand(ins, i));
        if (reg.kind() != RefKind::REG) continue;
        live.BitSet(RegNo(reg));
      }
    }
    for (unsigned i = 1; i < num_regs; ++i) {
      if (live.BitGet(i)) {
        RegFlags(reg_map[i]) |= +REG_FLAG::GLOBAL;
      }
    }
  }
  BitVec::Del(live);
}

int FunDropUnreferencedRegs(Fun fun) {
  std::vector<Reg> to_be_deleted;
  for (Reg reg : FunRegIter(fun)) {
    if (!RegHasFlag(reg, REG_FLAG::IS_READ) && RegDefIns(reg).isnull()) {
      to_be_deleted.push_back(reg);
    }
  }
  for (Reg reg : to_be_deleted) {
    FunRegDel(fun, reg);
    RegDel(reg);
  }

  return to_be_deleted.size();
}

FunRegStats FunCalculateRegStats(Fun fun) {
  FunRegStats rs;
  for (Reg reg : FunRegIter(fun)) {
    if (RegHasFlag(reg, REG_FLAG::GLOBAL)) {
      if (RegHasFlag(reg, REG_FLAG::LAC)) {
        ++rs.global_lac;
      } else {
        ++rs.global_not_lac;
      }
    } else {
      if (RegHasFlag(reg, REG_FLAG::LAC)) {
        ++rs.local_lac;
      } else {
        ++rs.local_not_lac;
      }
    }
  }
  return rs;
}

std::ostream& operator<<(std::ostream& os, const FunRegStats& stats) {
  os << std::right << std::setw(2) << stats.global_lac << "/" << std::setw(2)
     << stats.global_not_lac << "  " << std::setw(2) << stats.local_lac << "/"
     << std::setw(2) << stats.local_not_lac;

  return os;
}

namespace {
void RenameRegRange(Ins ins, Reg reg_src, Reg reg_dst) {
  while (!BblInsList::IsSentinel(ins)) {
    const unsigned num_defs = InsOpcode(ins).num_defs;
    const unsigned num_ops = InsOpcode(ins).num_operands;
    for (unsigned i = num_defs; i < num_ops; ++i) {
      if (InsOperand(ins, i) == reg_src) InsOperand(ins, i) = reg_dst;
    }
    for (unsigned i = 0; i < num_defs; ++i) {
      if (InsOperand(ins, i) == reg_src) return;
    }
    ins = BblInsList::Next(ins);
  }
}

}  // namespace

int FunSeparateLocalRegUsage(Fun fun) {
  int count = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      const unsigned num_defs = InsOpcode(ins).num_defs;
      for (unsigned i = 0; i < num_defs; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        if (RegDefIns(reg) == ins || RegHasFlag(reg, REG_FLAG::GLOBAL) ||
            (RegHasFlag(reg, REG_FLAG::TWO_ADDRESS) &&
             InsOpcode(ins).num_operands >= 2 &&
             InsOperand(ins, 0) == InsOperand(ins, 1)) ||
            RegCpuReg(reg) != HandleInvalid) {
          continue;
        }
        auto purpose = MaybeSkipCountPrefix(StrData(Name(reg)));
        const Reg new_reg = FunGetScratchReg(fun, RegKind(reg), purpose, false);
        if (RegHasFlag(reg, REG_FLAG::TWO_ADDRESS)) {
          RegFlags(new_reg) |= +REG_FLAG::TWO_ADDRESS;
        }
        InsOperand(ins, i) = new_reg;
        RenameRegRange(BblInsList::Next(ins), reg, new_reg);
        count += 1;
      }
    }
  }
  return count;
}

DK_LAC_COUNTS FunGlobalRegStats(Fun fun, const DK_MAP& rk_map) {
  DK_LAC_COUNTS out;
  for (Reg reg : FunRegIter(fun)) {
    if (!RegCpuReg(reg).isnull() || !RegHasFlag(reg, REG_FLAG::GLOBAL)) {
      continue;
    }
    const unsigned kind = rk_map[+RegKind(reg)];
    ASSERT(kind != 0, "");
    if (RegHasFlag(reg, REG_FLAG::LAC))
      ++out.lac[kind];
    else
      ++out.not_lac[kind];
  }
  return out;
}

}  // namespace cwerg::base
