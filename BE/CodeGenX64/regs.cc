#include "BE/CodeGenX64/regs.h"

#include <algorithm>

#include "BE/Base/cfg.h"
#include "BE/Base/reg_alloc.h"
#include "BE/Base/serialize.h"
#include "Util/parse.h"

namespace cwerg::code_gen_x64 {

using namespace cwerg;
using namespace cwerg::base;

// The std:arrays below will be initialized by  InitCodeGenA64();
std::array<CpuReg, 16> GPR_REGS;

std::array<CpuReg, 16> FLT_REGS;
std::array<CpuReg, 9> GPR_IN_REGS;
std::array<CpuReg, 9> GPR_OUT_REGS;
std::array<CpuReg, 8> FLT_IN_OUT_REGS;

base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

namespace {
struct CpuRegMasks {
  uint32_t gpr_mask;
  uint32_t flt_mask;
};

bool IsReserved(CpuReg cpu_reg) {
  return cpu_reg == GPR_REGS[0] || cpu_reg == FLT_REGS[0];
}

CpuRegMasks FunCpuRegStats(Fun fun) {
  uint32_t gpr_mask = 0;
  uint32_t flt_mask = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      const uint32_t num_ops = InsOpcode(ins).num_operands;
      for (unsigned i = 0; i < num_ops; ++i) {
        const Reg reg(InsOperand(ins, i));
        if (Kind(reg) != RefKind::REG) continue;
        const CpuReg cpu_reg(RegCpuReg(reg));
        if (Kind(cpu_reg) == RefKind::STACK_SLOT) continue;
        ;
        if (Kind(cpu_reg) != RefKind::CPU_REG) {
          BblRenderToAsm(bbl, fun, &std::cout);
          ASSERT(false,
                 "found unallocated reg " << Name(reg) << " in " << Name(fun));
        }
        const uint32_t mask = 1 << CpuRegNo(cpu_reg);
        if (CpuRegKind(cpu_reg) == +CPU_REG_KIND::GPR) {
          gpr_mask |= mask;
        } else {
          flt_mask |= mask;
        }
      }
    }
  }
  return {gpr_mask, flt_mask};
}

void GetCpuRegsForSignature(unsigned count,
                            const DK* kinds,
                            const std::array<CpuReg, 9>& gpr_regs,
                            const std::array<CpuReg, 8>& flt_regs,
                            std::vector<CpuReg>* out) {
  out->clear();
  unsigned next_gpr = 0;
  unsigned next_flt = 0;
  for (unsigned i = 0; i < count; ++i) {
    switch (kinds[i]) {
      case DK::S64:
      case DK::U64:
      case DK::A64:
      case DK::C64:
      case DK::S32:
      case DK::U32:
      case DK::S16:
      case DK::U16:
      case DK::S8:
      case DK::U8:
        ASSERT(next_gpr < gpr_regs.size(),
               "too many gpr64 regs " << next_gpr << " vs " << gpr_regs.size());
        out->push_back(gpr_regs[next_gpr]);
        ++next_gpr;
        break;
      case DK::R32:
      case DK::R64:
        ASSERT(next_flt < flt_regs.size(), "");
        out->push_back(flt_regs[next_flt]);
        ++next_flt;
        break;
      default:
        ASSERT(false, "invalid DK " << EnumToString(kinds[i]));
        break;
    }
  }
}

struct PushPopInterfaceX64 : base::PushPopInterface {
  void GetCpuRegsForInSignature(unsigned count,
                                const base::DK* kinds,
                                std::vector<base::CpuReg>* out) const override {
    return GetCpuRegsForSignature(count, kinds, GPR_IN_REGS, FLT_IN_OUT_REGS,
                                  out);
  }

  void GetCpuRegsForOutSignature(
      unsigned count,
      const base::DK* kinds,
      std::vector<base::CpuReg>* out) const override {
    return GetCpuRegsForSignature(count, kinds, GPR_OUT_REGS, FLT_IN_OUT_REGS,
                                  out);
  }
} PushPopInterfaceX64Impl;

}  // namespace

const base::PushPopInterface* const PushPopInterfaceX64 =
    &PushPopInterfaceX64Impl;

void AssignCpuRegOrMarkForSpilling(const std::vector<Reg>& assign_to,
                                   uint32_t cpu_reg_mask_first_choice,
                                   uint32_t cpu_reg_mask_second_choice) {
  // std::cout << "@@ AssignCpuRegOrMarkForSpilling " << assign_to.size() << " "
  //         << std::hex
  //    << cpu_reg_mask_first_choice << " " << cpu_reg_mask_second_choice <<
  //    "\n";
  uint32_t cpu_reg_mask = cpu_reg_mask_first_choice;
  unsigned pos = 0;
  for (Reg reg : assign_to) {
    ASSERT(RegCpuReg(reg).isnull(), "");
    if (cpu_reg_mask == 0 && cpu_reg_mask_second_choice != 0) {
      cpu_reg_mask = cpu_reg_mask_second_choice;
      cpu_reg_mask_second_choice = 0;
      pos = 0;
    }
    if (cpu_reg_mask == 0) {
      RegCpuReg(reg) = StackSlotNew(0);
      continue;
    }
    while (((1U << pos) & cpu_reg_mask) == 0) ++pos;
    const DK dk = RegKind(reg);
    if (DKFlavor(dk) == DK_FLAVOR_F) {
      RegCpuReg(reg) = FLT_REGS[pos];
    } else {
      RegCpuReg(reg) = GPR_REGS[pos];
    }
    // std::cout << "@@@@ ASSIGN " << Name(reg) << " " <<
    //    EnumToString(dk) << " " << Name(RegCpuReg(reg)) << "\n";
    cpu_reg_mask &= ~(1U << pos);
    ++pos;
  }
}

EmitContext FunComputeEmitContext(Fun fun) {
  CpuRegMasks masks = FunCpuRegStats(fun);
  masks.gpr_mask &= GPR_LAC_REGS_MASK;
  masks.flt_mask &= FLT_LAC_REGS_MASK;

  const uint32_t stk_size = (FunStackSize(fun) + 15) / 16 * 16;
  return EmitContext{masks.gpr_mask, masks.flt_mask, stk_size, FunIsLeaf(fun)};
}

void AssignAllocatedRegsAndReturnSpilledRegs(
    const std::vector<LiveRange>& ranges) {
  for (const LiveRange& lr : ranges) {
    if (lr.HasFlag(LR_FLAG::PRE_ALLOC) || lr.is_use_lr()) continue;
    if (lr.cpu_reg == CPU_REG_SPILL) {
      RegCpuReg(lr.reg) = StackSlotNew(0);
    } else {
      ASSERT(lr.cpu_reg != CPU_REG_INVALID, "");
      ASSERT(lr.cpu_reg.value != ~0U, "");
      RegCpuReg(lr.reg) = lr.cpu_reg;
    }
  }
}

class CpuRegPool : public RegPool {
 public:
  explicit CpuRegPool(Fun fun,
                      Bbl bbl,
                      bool allow_spilling,
                      uint32_t gpr_available_lac,
                      uint32_t gpr_available_not_lac,
                      uint32_t flt_available_lac,
                      uint32_t flt_available_not_lac)
      : fun_(fun),
        bbl_(bbl),
        allow_spilling_(allow_spilling),
        gpr_available_lac_(gpr_available_lac),
        gpr_available_not_lac_(gpr_available_not_lac),
        flt_available_lac_(flt_available_lac),
        flt_available_not_lac_(flt_available_not_lac) {}

  uint8_t get_cpu_reg_family(DK dk) override {
    return DKFlavor(dk) == DK_FLAVOR_F ? +CPU_REG_KIND::FLT
                                       : +CPU_REG_KIND::GPR;
  }

  CpuReg get_available_reg(const LiveRange& lr) override {
    const bool lac = lr.HasFlag(LR_FLAG::LAC);
    const DK kind = RegKind(lr.reg);
    const bool is_gpr = DKFlavor(kind) != DK_FLAVOR_F;
    const uint32_t available = get_available(lac, is_gpr);
    if (!is_gpr) {
      for (unsigned n = 0; n < 16; ++n) {
        const uint32_t mask = 1U << n;
        if ((mask & available) == mask) {
          if (!flt_reserved_[n].has_conflict(lr)) {
            set_available(lac, is_gpr, available & ~mask);
            return FLT_REGS[n];
          }
        }
      }
    } else {
      for (unsigned n = 0; n <= 16; ++n) {
        const uint32_t mask = 1U << n;
        if ((mask & available) == mask) {
          if (!gpr_reserved_[n].has_conflict(lr)) {
            set_available(lac, is_gpr, available & ~mask);
            return GPR_REGS[n];
          }
        }
      }
    }
    ASSERT(allow_spilling_, "could not find reg for LiveRange " << lr);
    return CPU_REG_SPILL;
  }

  void give_back_available_reg(CpuReg cpu_reg) override {
    if (IsReserved(cpu_reg)) return;
    const uint32_t mask = 1U << CpuRegNo(cpu_reg);
    bool is_gpr;
    bool is_lac;
    if (CpuRegKind(cpu_reg) == +CPU_REG_KIND::FLT) {
      is_gpr = false;
      is_lac = (mask & FLT_LAC_REGS_MASK) != 0;
    } else {
      is_gpr = true;
      is_lac = (mask & GPR_LAC_REGS_MASK) != 0;
    }

    uint32_t available = get_available(is_lac, is_gpr);
    set_available(is_lac, is_gpr, available | mask);
  }

  void add_reserved_range(const LiveRange& lr) {
    const Reg reg = lr.reg;
    const CpuReg cpu_reg(RegCpuReg(reg));
    ASSERT(Kind(cpu_reg) == RefKind::CPU_REG, "");
    if (RegKind(reg) == DK::R32 || RegKind(reg) == DK::R64) {
      flt_reserved_[CpuRegNo(cpu_reg)].add(&lr);
    } else {
      gpr_reserved_[CpuRegNo(cpu_reg)].add(&lr);
    }
  }

  void Render(std::ostream* out) {
    *out << "POOL gpr:" << std::hex << gpr_available_lac_ << "/"
         << gpr_available_not_lac_ << " flt:" << flt_available_lac_ << "/"
         << flt_available_not_lac_ << std::dec << "\n";

    for (unsigned i = 0; i < gpr_reserved_.size(); ++i) {
      if (gpr_reserved_[i].size() > 0)
        *out << "gpr" << i << " " << gpr_reserved_[i].size() << "\n";
    }
    for (unsigned i = 0; i < flt_reserved_.size(); ++i) {
      if (flt_reserved_[i].size() > 0)
        *out << "flt" << i << " " << gpr_reserved_[i].size() << "\n";
    }
  }

 private:
  uint32_t get_available(bool lac, bool is_gpr) const {
    if (is_gpr) {
      return lac ? gpr_available_lac_ : gpr_available_not_lac_;
    } else {
      return lac ? flt_available_lac_ : flt_available_not_lac_;
    }
  }

  void set_available(bool lac, bool is_gpr, uint32_t available) {
    if (is_gpr) {
      if (lac) {
        gpr_available_lac_ = available;
      } else {
        gpr_available_not_lac_ = available;
      }
    } else {
      if (lac) {
        flt_available_lac_ = available;
      } else {
        flt_available_not_lac_ = available;
      }
    }
  }

  const Fun fun_;  // for debugging
  const Bbl bbl_;  // for debugging
  const bool allow_spilling_;
  // bit masks:
  uint32_t gpr_available_lac_ = 0;
  uint32_t gpr_available_not_lac_ = 0;
  uint32_t flt_available_lac_ = 0;
  uint32_t flt_available_not_lac_ = 0;
  std::array<PreAllocation, 31> gpr_reserved_;  // r32 is stack/zero
  std::array<PreAllocation, 32> flt_reserved_;
};

void RunLinearScan(Bbl bbl,
                   Fun fun,
                   bool allow_spilling,
                   std::vector<LiveRange>* ranges,
                   uint32_t mask_gpr_regs_lac,
                   uint32_t mask_gpr_regs_not_lac,
                   uint32_t mask_flt_regs_lac,
                   uint32_t mask_flt_regs_not_lac) {
  CpuRegPool pool(fun, bbl, allow_spilling, mask_gpr_regs_lac,
                  mask_gpr_regs_not_lac, mask_flt_regs_lac,
                  mask_flt_regs_not_lac);
  std::vector<LiveRange*> ordered;
  for (unsigned i = 1; i < ranges->size(); ++i)
    ordered.push_back(&(*ranges)[i]);
  std::sort(begin(ordered), end(ordered),
            [](LiveRange* lhs, LiveRange* rhs) { return *lhs < *rhs; });

  for (LiveRange* lr : ordered) {
    if (lr->HasFlag(LR_FLAG::PRE_ALLOC)) {
      pool.add_reserved_range(*lr);
    } else {
      lr->cpu_reg = CPU_REG_INVALID;
    }
  }
  // pool.Render(&std::cout);
  // std::cout << "\nCC" << Name(bbl) << "\n";
  // for (const LiveRange* lr : ordered) {
  //  std::cout << *lr << "\n";
  // }
#if 0
  unsigned n = 0;
  auto logger = [&](const LiveRange& lr, std::string_view msg) {
    std::cout << n++ << " " << lr << " " << msg << "\n";
  };

  RegisterAssignerLinearScan(ordered, ranges, &pool, logger);
#else
  RegisterAssignerLinearScan(ordered, ranges, &pool, nullptr);
#endif
}

void BblRegAllocOrSpill(Bbl bbl, Fun fun, const std::vector<Reg>& live_out) {
  std::vector<LiveRange> ranges = BblGetLiveRanges(bbl, fun, live_out);
  for (LiveRange& lr : ranges) {
    CpuReg cpu_reg(RegCpuReg(lr.reg));
    if (Kind(cpu_reg) ==
        RefKind::CPU_REG) {  // covers both CPU_REG_SPILL/-INVALID
      lr.SetFlag(LR_FLAG::PRE_ALLOC);
      lr.cpu_reg = cpu_reg;
    }
  }

  RunLinearScan(bbl, fun, true, &ranges, GPR_REGS_MASK & GPR_LAC_REGS_MASK,
                GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                FLT_REGS_MASK & FLT_LAC_REGS_MASK,
                FLT_REGS_MASK & ~FLT_LAC_REGS_MASK);

  AssignAllocatedRegsAndReturnSpilledRegs(ranges);
}

void FunLocalRegAlloc(base::Fun fun, std::vector<base::Ins>* inss) {
  const unsigned num_regs = FunNumRegs(fun);
  const Reg* const reg_map = (Reg*)FunRegMap(fun).BackingStorage();
  std::vector<Reg> live_out;

  for (Reg reg : FunRegIter(fun)) {
    RegSpillSlot(reg) = Stk(0);
  }
  for (Bbl bbl : FunBblIter(fun)) {
    live_out.clear();
    const BitVec& live_out_vec = BblLiveOut(bbl);
    for (int i = 1; i < num_regs; ++i) {
      if (live_out_vec.BitGet(i)) live_out.push_back(reg_map[i]);
    }
    BblRegAllocOrSpill(bbl, fun, live_out);
  }
}

std::vector<CpuReg> GetAllRegs() {
  std::vector<CpuReg> out;
  out.reserve(GPR_REGS.size() + FLT_REGS.size());
  for (CpuReg cpu_reg : GPR_REGS) out.push_back(cpu_reg);
  for (CpuReg cpu_reg : FLT_REGS) out.push_back(cpu_reg);
  return out;
}

void InitCodeGenX64() {
  // GPR
  GPR_REGS[0] = CpuRegNew(0, +CPU_REG_KIND::GPR, StrNew("rax"));
  GPR_REGS[1] = CpuRegNew(1, +CPU_REG_KIND::GPR, StrNew("rcx"));
  GPR_REGS[2] = CpuRegNew(2, +CPU_REG_KIND::GPR, StrNew("rdx"));
  GPR_REGS[3] = CpuRegNew(3, +CPU_REG_KIND::GPR, StrNew("rbx"));
  GPR_REGS[4] = CpuRegNew(4, +CPU_REG_KIND::GPR, StrNew("sp"));
  GPR_REGS[5] = CpuRegNew(5, +CPU_REG_KIND::GPR, StrNew("rbp"));
  GPR_REGS[6] = CpuRegNew(6, +CPU_REG_KIND::GPR, StrNew("rsi"));
  GPR_REGS[7] = CpuRegNew(7, +CPU_REG_KIND::GPR, StrNew("rdi"));
  GPR_REGS[8] = CpuRegNew(8, +CPU_REG_KIND::GPR, StrNew("r8"));
  GPR_REGS[9] = CpuRegNew(9, +CPU_REG_KIND::GPR, StrNew("r9"));
  GPR_REGS[10] = CpuRegNew(10, +CPU_REG_KIND::GPR, StrNew("r10"));
  GPR_REGS[11] = CpuRegNew(11, +CPU_REG_KIND::GPR, StrNew("r11"));
  GPR_REGS[12] = CpuRegNew(12, +CPU_REG_KIND::GPR, StrNew("r12"));
  GPR_REGS[13] = CpuRegNew(13, +CPU_REG_KIND::GPR, StrNew("r13"));
  GPR_REGS[14] = CpuRegNew(14, +CPU_REG_KIND::GPR, StrNew("r14"));
  GPR_REGS[15] = CpuRegNew(15, +CPU_REG_KIND::GPR, StrNew("r15"));

  GPR_IN_REGS[0] = GPR_REGS[7];
  GPR_IN_REGS[1] = GPR_REGS[6];
  GPR_IN_REGS[2] = GPR_REGS[2];
  GPR_IN_REGS[3] = GPR_REGS[1];
  GPR_IN_REGS[4] = GPR_REGS[8];
  GPR_IN_REGS[5] = GPR_REGS[9];
  GPR_IN_REGS[6] = GPR_REGS[10];
  GPR_IN_REGS[7] = GPR_REGS[11];
  GPR_IN_REGS[8] = GPR_REGS[0];

  GPR_OUT_REGS[0] = GPR_REGS[0];
  GPR_OUT_REGS[1] = GPR_REGS[2];
  GPR_OUT_REGS[2] = GPR_REGS[7];
  GPR_OUT_REGS[3] = GPR_REGS[6];
  GPR_OUT_REGS[4] = GPR_REGS[1];
  GPR_OUT_REGS[5] = GPR_REGS[8];
  GPR_OUT_REGS[6] = GPR_REGS[9];
  GPR_OUT_REGS[7] = GPR_REGS[10];
  GPR_OUT_REGS[8] = GPR_REGS[11];

  // FLT
  for (unsigned i = 0; i < FLT_REGS.size(); ++i) {
    char buffer[8] = "xmm";
    ToDecString(i, buffer + 3);
    FLT_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::FLT, StrNew(buffer));
  }

  FLT_IN_OUT_REGS[0] = FLT_REGS[1];
  FLT_IN_OUT_REGS[1] = FLT_REGS[2];
  FLT_IN_OUT_REGS[2] = FLT_REGS[3];
  FLT_IN_OUT_REGS[3] = FLT_REGS[4];
  FLT_IN_OUT_REGS[4] = FLT_REGS[5];
  FLT_IN_OUT_REGS[5] = FLT_REGS[6];
  FLT_IN_OUT_REGS[6] = FLT_REGS[7];
  FLT_IN_OUT_REGS[7] = FLT_REGS[8];

  // ==================================================
  for (unsigned i = 0; i < DK_TO_CPU_REG_KIND_MAP.size(); ++i) {
    DK_TO_CPU_REG_KIND_MAP[i] = +CPU_REG_KIND::INVALID;
  }
  DK_TO_CPU_REG_KIND_MAP[+DK::S8] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U8] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::S16] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U16] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::S32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::S64] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U64] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::A64] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::C64] = +CPU_REG_KIND::GPR;
  //
  DK_TO_CPU_REG_KIND_MAP[+DK::R32] = +CPU_REG_KIND::FLT;
  DK_TO_CPU_REG_KIND_MAP[+DK::R64] = +CPU_REG_KIND::FLT;
}

}  // namespace cwerg::code_gen_x64
