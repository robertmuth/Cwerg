#include "CodeGenA64/regs.h"
#include "Base/cfg.h"
#include "Base/reg_alloc.h"
#include "Base/serialize.h"
#include "Util/parse.h"

namespace cwerg::code_gen_a64 {

using namespace cwerg;
using namespace cwerg::base;

// The std:arrays below will be initialized by  InitCodeGenA64();
std::array<CpuReg, 31> GPR_REGS;

std::array<CpuReg, 32> FLT_REGS;

base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

namespace {

// For push/pop conversion
std::array<CpuReg, 16> GPR_PARAM_REGS;
std::array<CpuReg, 24> FLT_PARAM_REGS;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
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
    return DKFlavor(dk) == DK_FLAVOR_F ? +CPU_REG_KIND::FLT : +CPU_REG_KIND::GPR;
  }

  CpuReg get_available_reg(const LiveRange& lr) override {
    const bool lac = lr.HasFlag(LR_FLAG::LAC);
    const DK kind = RegKind(lr.reg);
    const bool is_gpr = DKFlavor(kind) != DK_FLAVOR_F;
    const uint32_t available = get_available(lac, is_gpr);
    if (!is_gpr) {
      for (unsigned n = 0; n < 32; ++n) {
        const uint32_t mask = 1U << n;
        if ((mask & available) == mask) {
          if (!flt_reserved_[n].has_conflict(lr)) {
            set_available(lac, is_gpr, available & ~mask);
            return FLT_REGS[n];
          }
        }
      }
    } else {
      for (unsigned n = 0; n <= 30; ++n) {
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
    ASSERT(cpu_reg.kind() == RefKind::CPU_REG, "");
    if (RegKind(reg) == DK::F32 || RegKind(reg) == DK::F64) {
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

  const Fun fun_;
  const Bbl bbl_;
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

  RegisterAssignerLinearScanFancy(ordered, ranges, &pool, logger);
#else
  RegisterAssignerLinearScanFancy(ordered, ranges, &pool, nullptr);
#endif
}

std::vector<Reg> AssignAllocatedRegsAndReturnSpilledRegs(
    const std::vector<LiveRange>& ranges) {
  std::vector<Reg> out;
  for (const LiveRange& lr : ranges) {
    if (lr.HasFlag(LR_FLAG::PRE_ALLOC) || lr.is_use_lr()) continue;
    if (lr.cpu_reg == CPU_REG_SPILL) {
      out.push_back(lr.reg);
    } else {
      ASSERT(lr.cpu_reg != CPU_REG_INVALID, "");
      ASSERT(lr.cpu_reg.value != ~0U, "");
      RegCpuReg(lr.reg) = lr.cpu_reg;
    }
  }
  return out;
}

void BblRegAllocOrSpill(Bbl bbl,
                        Fun fun,
                        const std::vector<Reg>& live_out,
                        std::vector<Ins>* inss) {
  std::vector<LiveRange> ranges = BblGetLiveRanges(bbl, fun, live_out, true);
  for (LiveRange& lr : ranges) {
    CpuReg cpu_reg(RegCpuReg(lr.reg));
    if (!cpu_reg.isnull()) {  // covers both CPU_REG_SPILL/-INVALID
      lr.SetFlag(LR_FLAG::PRE_ALLOC);
      lr.cpu_reg = cpu_reg;
    }
  }

  RunLinearScan(bbl, fun, true, &ranges, GPR_REGS_MASK & GPR_LAC_REGS_MASK,
                GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                FLT_REGS_MASK & FLT_LAC_REGS_MASK,
                FLT_REGS_MASK & ~FLT_LAC_REGS_MASK);

  std::vector<Reg> spilled_regs =
      AssignAllocatedRegsAndReturnSpilledRegs(ranges);
  if (!spilled_regs.empty()) {
    for (Reg reg : spilled_regs) {
      RegSpillSlot(reg) = RegCreateSpillSlot(reg, fun, "$spill");
    }
    BblSpillRegs(bbl, fun, DK::U32, inss);
    // This cleanup should not be strictly necessary since we only deal
    // with locals which do not overlap Bbls
    for (Reg reg : spilled_regs) {
      RegSpillSlot(reg) = Stk(0);
    }
    std::vector<LiveRange> ranges = BblGetLiveRanges(bbl, fun, live_out, true);
    for (LiveRange& lr : ranges) {
      if (!RegCpuReg(lr.reg).isnull()) {  // covers both CPU_REG_SPILL/-INVALID
        lr.SetFlag(LR_FLAG::PRE_ALLOC);
        lr.cpu_reg = CpuReg(RegCpuReg(lr.reg));
      }
    }
    RunLinearScan(bbl, fun, true, &ranges, GPR_REGS_MASK & GPR_LAC_REGS_MASK,
                  GPR_REGS_MASK & ~GPR_LAC_REGS_MASK,
                  FLT_REGS_MASK & FLT_LAC_REGS_MASK,
                  FLT_REGS_MASK & ~FLT_LAC_REGS_MASK);
    spilled_regs = AssignAllocatedRegsAndReturnSpilledRegs(ranges);
    ASSERT(spilled_regs.empty(), "");
  }
}

struct CpuRegMasks {
  uint32_t gpr_mask;
  uint32_t flt_mask;
};

CpuRegMasks FunCpuRegStats(Fun fun) {
  uint32_t gpr_mask = 0;
  uint32_t flt_mask = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      const uint32_t num_ops = InsOpcode(ins).num_operands;
      for (unsigned i = 0; i < num_ops; ++i) {
        const Reg reg(InsOperand(ins, i));
        if (reg.kind() != RefKind::REG) continue;
        const CpuReg cpu_reg(RegCpuReg(reg));
        if (cpu_reg.kind() != RefKind::CPU_REG) {
          BblRenderToAsm(bbl, fun, &std::cout);
          ASSERT(false,
                 "found unallocated reg " << Name(reg) << " in " << Name(fun));
        }
        const uint32_t mask = CpuRegToAllocMask(cpu_reg);
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

}  // namespace

std::vector<CpuReg> GetCpuRegsForSignature(unsigned count, const DK* kinds) {
  unsigned next_gpr = 0;
  unsigned next_flt = 0;
  std::vector<CpuReg> out;
  for (unsigned i = 0; i < count; ++i) {
    switch (kinds[i]) {
      case DK::S64:
      case DK::U64:
      case DK::A64:
      case DK::C64:
        ASSERT(next_gpr < GPR_PARAM_REGS.size(), "too many gpr32 regs "
                                                     << next_gpr << " vs "
                                                     << GPR_PARAM_REGS.size());
        out.push_back(GPR_PARAM_REGS[next_gpr]);
        ++next_gpr;
        break;
      case DK::S32:
      case DK::U32:
        ASSERT(next_gpr < GPR_PARAM_REGS.size(), "too many gpr64 regs "
                                                     << next_gpr << " vs "
                                                     << GPR_PARAM_REGS.size());
        out.push_back(GPR_PARAM_REGS[next_gpr]);
        ++next_gpr;
        break;
      case DK::F32:
        ASSERT(next_flt < FLT_PARAM_REGS.size(), "");
        out.push_back(FLT_PARAM_REGS[next_flt]);
        ++next_flt;
        break;
      case DK::F64:
        ASSERT(next_flt < FLT_PARAM_REGS.size(), "");
        out.push_back(FLT_PARAM_REGS[next_flt]);
        ++next_flt;
        break;
      default:
        break;
    }
  }

  return out;
}

void FunPushargConversion(Fun fun) {
  std::vector<CpuReg> parameter;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      if (InsOPC(ins) == OPC::PUSHARG) {
        ASSERT(!parameter.empty(),
               "possible undefined fun call in " << Name(fun));
        Handle src = InsOperand(ins, 0);
        CpuReg cpu_reg = parameter.back();
        parameter.pop_back();
        Reg reg = FunFindOrAddCpuReg(fun, cpu_reg, RegOrConstKind(src));
        InsInit(ins, OPC::MOV, reg, src);
        continue;
      }

      if (InsOpcode(ins).IsCall()) {
        Fun callee = InsCallee(ins);
        parameter = GetCpuRegsForSignature(FunNumInputTypes(callee),
                                           FunInputTypes(callee));
        std::reverse(parameter.begin(), parameter.end());
      } else if (InsOPC(ins) == OPC::RET) {
        parameter =
            GetCpuRegsForSignature(FunNumOutputTypes(fun), FunOutputTypes(fun));
        std::reverse(parameter.begin(), parameter.end());
      }
    }
  }
}

void FunPopargConversion(Fun fun) {
  std::vector<CpuReg> parameter =
      GetCpuRegsForSignature(FunNumInputTypes(fun), FunInputTypes(fun));
  std::reverse(parameter.begin(), parameter.end());
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::POPARG) {
        ASSERT(!parameter.empty(), "");
        Reg dst = Reg(InsOperand(ins, 0));
        CpuReg cpu_reg = parameter.back();
        parameter.pop_back();
        Reg reg = FunFindOrAddCpuReg(fun, cpu_reg, RegKind(dst));
        InsInit(ins, OPC::MOV, dst, reg);
        continue;
      }

      if (InsOpcode(ins).IsCall()) {
        Fun callee = InsCallee(ins);
        parameter = GetCpuRegsForSignature(FunNumOutputTypes(callee),
                                           FunOutputTypes(callee));
        std::reverse(parameter.begin(), parameter.end());
      }
    }
  }
}

void FunLocalRegAlloc(Fun fun, std::vector<Ins>* inss) {
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
    BblRegAllocOrSpill(bbl, fun, live_out, inss);
  }
}

void AssignCpuRegOrMarkForSpilling(const std::vector<Reg>& assign_to,
                                   uint32_t cpu_reg_mask_first_choice,
                                   uint32_t cpu_reg_mask_second_choice,
                                   std::vector<Reg>* to_be_spilled) {
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
      to_be_spilled->push_back(reg);
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
  masks.gpr_mask &= GPR_LAC_REGS_MASK_WITH_LR;
  masks.flt_mask &= FLT_LAC_REGS_MASK;
  if (!FunIsLeaf(fun)) {
    // add link regs if it is not already included
    masks.gpr_mask |= 1U << 30U;
  }

  const uint32_t stk_size = (FunStackSize(fun) + 15) / 16 * 16;
  return EmitContext{masks.gpr_mask, masks.flt_mask, stk_size};
}

std::vector<CpuReg> GetAllRegs() {
  std::vector<CpuReg> out;
  for (CpuReg cpu_reg : GPR_REGS) out.push_back(cpu_reg);
  for (CpuReg cpu_reg : FLT_REGS) out.push_back(cpu_reg);
  return out;
}

void InitCodeGenA64() {
  // GPR
  for (unsigned i = 0; i < GPR_REGS.size(); ++i) {
    char buffer[8];
    buffer[0] = 'x';
    ToDecString(i, buffer + 1);
    GPR_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::GPR, StrNew(buffer));
  }
  // FLT
  for (unsigned i = 0; i < FLT_REGS.size(); ++i) {
    char buffer[8];
    buffer[0] = 'd';
    ToDecString(i, buffer + 1);
    FLT_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::FLT, StrNew(buffer));
  }
  // ==================================================
  // GPR_PARAM_REGS
  for (unsigned i = 0; i < GPR_PARAM_REGS.size(); ++i) {
    GPR_PARAM_REGS[i] = GPR_REGS[i];
  }

  // FLT_PARAM_REGS
  for (unsigned i = 0; i < FLT_PARAM_REGS.size(); ++i) {
    FLT_PARAM_REGS[i] = FLT_REGS[i < 8 ? i : 8 + i];
  }

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
  DK_TO_CPU_REG_KIND_MAP[+DK::F32] = +CPU_REG_KIND::FLT;
  DK_TO_CPU_REG_KIND_MAP[+DK::F64] = +CPU_REG_KIND::FLT;
}

}  // namespace cwerg::code_gen_a64
