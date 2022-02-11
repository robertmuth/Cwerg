#include "CodeGenA32/regs.h"
#include "Base/reg_alloc.h"
#include "Base/serialize.h"
#include "CodeGenA32/isel_gen.h"
#include "Util/parse.h"

namespace cwerg::code_gen_a32 {

using namespace cwerg;
using namespace cwerg::base;

std::array<CpuReg, 16> GPR_REGS;
std::array<CpuReg, 32> FLT_REGS;
std::array<CpuReg, 16> DBL_REGS;

std::array<CpuReg, 6> GPR_PARAM_REGS;
std::array<CpuReg, 16> FLT_PARAM_REGS;
std::array<CpuReg, 8> DBL_PARAM_REGS;

base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

namespace {

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

const uint32_t LINK_REG_MASK = 0x4000;

std::array<const char*, 16> GPR_NAMES = {
    "r0", "r1", "r2",  "r3",  "r4",  "r5", "r6", "r7",  //
    "r8", "r9", "r10", "r11", "r12", "sp", "lr", "pc"};

class RegPoolArm : public RegPool {
 public:
  explicit RegPoolArm(Fun fun,
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
    return (dk == DK::F64 or dk == DK::F32) ? 2 : 1;
  }

  CpuReg get_available_reg(const LiveRange& lr) override {
    const bool lac = lr.HasFlag(LR_FLAG::LAC);
    const DK kind = RegKind(lr.reg);
    const bool is_gpr = DKFlavor(kind) != DK_FLAVOR_F;
    const uint32_t available = get_available(lac, is_gpr);
    if (kind == DK::F64) {
      for (unsigned n = 0; n < 32; n += 2) {
        const uint32_t mask = 3U << n;
        if ((mask & available) == mask) {
          if (!flt_reserved_[n].has_conflict(lr) &&
              !flt_reserved_[n + 1].has_conflict(lr)) {
            set_available(lac, is_gpr, available & ~mask);
            return DBL_REGS[n / 2];
          }
        }
      }
    } else if (kind == DK::F32) {
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
      for (unsigned n = 0; n <= 14; ++n) {
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
    bool is_gpr = CpuRegKind(cpu_reg) == +CPU_REG_KIND::GPR;
    uint32_t mask = A32RegToAllocMask(cpu_reg);
    bool lac = 0 != (mask & (is_gpr ? GPR_LAC_REGS_MASK : FLT_LAC_REGS_MASK));

    uint32_t available = get_available(lac, is_gpr);
    set_available(lac, is_gpr, available | mask);
  }

  void add_reserved_range(const LiveRange& lr) {
    const Reg reg = lr.reg;
    const CpuReg cpu_reg(RegCpuReg(reg));
    ASSERT(cpu_reg.kind() == RefKind::CPU_REG, "");
    if (RegKind(reg) == DK::F32) {
      flt_reserved_[CpuRegNo(cpu_reg)].add(&lr);
    } else if (RegKind(reg) == DK::F64) {
      flt_reserved_[CpuRegNo(cpu_reg) * 2 + 0].add(&lr);
      flt_reserved_[CpuRegNo(cpu_reg) * 2 + 1].add(&lr);
    } else {
      gpr_reserved_[CpuRegNo(cpu_reg)].add(&lr);
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
  std::array<PreAllocation, 16> gpr_reserved_;
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
  RegPoolArm pool(fun, bbl, allow_spilling, mask_gpr_regs_lac,
                  mask_gpr_regs_not_lac, mask_flt_regs_lac,
                  mask_flt_regs_not_lac);

  std::vector<LiveRange*> ordered;
  for (unsigned i = 1; i < ranges->size(); ++i)
    ordered.push_back(&(*ranges)[i]);
  std::sort(begin(ordered), end(ordered),
            [](LiveRange* lhs, LiveRange* rhs) { return *lhs < *rhs; });

  for (LiveRange* lr : ordered) {
    if (!lr->cpu_reg.isnull()) {
      pool.add_reserved_range(*lr);
    }
  }
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
        const uint32_t mask = A32RegToAllocMask(cpu_reg);
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

struct ArmFltRegRange {
  uint32_t start;
  uint32_t count;
};

ArmFltRegRange ArmGetFltRegRanges(uint32_t flt_mask) {
  uint32_t start = 0;
  while ((flt_mask & 1U) == 0) {
    flt_mask >>= 1U;
    ++start;
  }
  uint32_t count = 0;
  while (flt_mask > 0) {
    flt_mask >>= 1U;
    ++count;
  }
  return {start, count};
}

void GetCpuRegsForSignature(unsigned count,
                            const DK* kinds,
                            std::vector<CpuReg>* out) {
  out->clear();
  unsigned next_gpr = 0;
  unsigned next_flt = 0;
  for (unsigned i = 0; i < count; ++i) {
    switch (kinds[i]) {
      case DK::A32:
      case DK::C32:
      case DK::S32:
      case DK::U32:
        ASSERT(next_gpr < GPR_PARAM_REGS.size(), "too many gpr regs "
                                                     << next_gpr << " vs "
                                                     << GPR_PARAM_REGS.size());
        out->push_back(GPR_PARAM_REGS[next_gpr]);
        ++next_gpr;
        break;
      case DK::F32:
        ASSERT(next_flt < FLT_PARAM_REGS.size(), "");
        out->push_back(FLT_PARAM_REGS[next_flt]);
        ++next_flt;
        break;
      case DK::F64:
        if ((next_flt & 1U) == 1) ++next_flt;
        ASSERT(next_flt / 2 < DBL_PARAM_REGS.size(), "");
        out->push_back(DBL_PARAM_REGS[next_flt / 2]);
        next_flt += 2;
        break;
      default:
        break;
    }
  }
}

struct PushPopInterfaceA64 : base::PushPopInterface {
  void GetCpuRegsForInSignature(unsigned count,
                                const base::DK* kinds,
                                std::vector<base::CpuReg>* out) const override {
    return GetCpuRegsForSignature(count, kinds, out);
  }

  void GetCpuRegsForOutSignature(
      unsigned count,
      const base::DK* kinds,
      std::vector<base::CpuReg>* out) const override {
    return GetCpuRegsForSignature(count, kinds, out);
  }
} PushPopInterfaceA32Impl;

}  // namespace

const base::PushPopInterface* const PushPopInterfaceA32 =
    &PushPopInterfaceA32Impl;

uint32_t A32RegToAllocMask(CpuReg cpu_reg) {
  if (CpuRegKind(cpu_reg) == +CPU_REG_KIND::DBL) {
    return 3U << (CpuRegNo(cpu_reg) * 2U);
  } else {
    return 1U << CpuRegNo(cpu_reg);
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

std::vector<CpuReg> GetAllRegs() {
  std::vector<CpuReg> out;
  for (CpuReg cpu_reg : GPR_REGS) out.push_back(cpu_reg);
  for (CpuReg cpu_reg : FLT_REGS) out.push_back(cpu_reg);
  for (CpuReg cpu_reg : DBL_REGS) out.push_back(cpu_reg);
  return out;
}

void AssignCpuRegOrMarkForSpilling(const std::vector<Reg>& regs,
                                   uint32_t cpu_reg_mask_first_choice,
                                   uint32_t cpu_reg_mask_second_choice,
                                   std::vector<Reg>* to_be_spilled) {
  uint32_t cpu_reg_mask = cpu_reg_mask_first_choice;
  unsigned pos = 0;
  for (Reg reg : regs) {
    ASSERT(RegCpuReg(reg).isnull(), "");
    // This ugly hack is necessary because we prefer to use reg lr and XX
    // over r6-r11 despite them being "numerically higher".
    if (cpu_reg_mask == 0 && cpu_reg_mask_second_choice != 0) {
      cpu_reg_mask = cpu_reg_mask_second_choice;
      cpu_reg_mask_second_choice = 0;
      pos = 0;
    }
    if (cpu_reg_mask == 0) {
      to_be_spilled->push_back(reg);
      continue;
    }
    if (RegKind(reg) != DK::F64) {
      while (((1U << pos) & cpu_reg_mask) == 0) ++pos;
      if (RegKind(reg) == DK::F32) {
        RegCpuReg(reg) = FLT_REGS[pos];
      } else {
        RegCpuReg(reg) = GPR_REGS[pos];
      }
      cpu_reg_mask &= ~(1U << pos);
      ++pos;
      continue;
    }

    for (unsigned pos_dbl = pos / 2; pos_dbl < 32; pos_dbl += 2) {
      unsigned mask = 3U << pos_dbl;
      if ((mask & cpu_reg_mask) == mask) {
        RegCpuReg(reg) = DBL_REGS[pos_dbl / 2];
        cpu_reg_mask &= ~mask;
        break;
      } else if ((mask & cpu_reg_mask) == 0) {
        // advance pos if we did not skip any set bits
        if (pos_dbl == pos) {
          pos += 2;
        }
      }
    }
    to_be_spilled->push_back(reg);
  }
}

EmitContext FunComputeEmitContext(Fun fun) {
  CpuRegMasks masks = FunCpuRegStats(fun);
  const bool must_save_link_reg =
      !FunIsLeaf(fun) || (masks.gpr_mask & LINK_REG_MASK) != 0;
  masks.gpr_mask &= GPR_LAC_REGS_MASK;
  masks.flt_mask &= FLT_LAC_REGS_MASK;
  EmitContext out{masks.gpr_mask, masks.flt_mask, masks.gpr_mask,
                  masks.flt_mask};
  if (must_save_link_reg) {
    out.stm_regs |= A32RegToAllocMask(GPR_REGS[14]);
    out.ldm_regs |= A32RegToAllocMask(GPR_REGS[15]);
  }
  uint32_t num_saved_regs =
      __builtin_popcount(out.ldm_regs) + __builtin_popcount(out.vldm_regs);
  uint32_t stk_size = FunStackSize(fun) + 4 * num_saved_regs;
  stk_size = (stk_size + 15) / 16 * 16;
  stk_size -= 4 * num_saved_regs;
  out.stk_size = stk_size;
  return out;
}

uint32_t HighByte(uint32_t x) {
  unsigned shift = 0;
  while (x > 255) {
    x >>= 2U;
    shift += 2;
  }
  return x << shift;
}

void EmitFunProlog(const EmitContext& ctx, std::vector<a32::Ins>* output) {
  if (ctx.stm_regs > 0) {
    output->emplace_back(MakeIns(a32::OPC::stmdb_update, +a32::PRED::al,
                                 +a32::REG::sp, ctx.stm_regs));
  }

  if (ctx.vstm_regs > 0) {
    const ArmFltRegRange range = ArmGetFltRegRanges(ctx.vstm_regs);
    output->emplace_back(MakeIns(a32::OPC::vstmdb_s_update, +a32::PRED::al,
                                 +a32::REG::sp, range.start, range.count));
  }

  uint32_t stk_size = ctx.stk_size;
  while (stk_size > 0) {
    uint32_t high_byte = HighByte(stk_size);
    output->emplace_back(MakeIns(a32::OPC::sub_imm, +a32::PRED::al,
                                 +a32::REG::sp, +a32::REG::sp, high_byte));
    stk_size -= high_byte;
  }
}

void EmitFunEpilog(const EmitContext& ctx, std::vector<a32::Ins>* output) {
  uint32_t stk_size = ctx.stk_size;
  while (stk_size > 0) {
    uint32_t high_byte = HighByte(stk_size);
    output->emplace_back(MakeIns(a32::OPC::add_imm, +a32::PRED::al,
                                 +a32::REG::sp, +a32::REG::sp, high_byte));
    stk_size -= high_byte;
  }

  if (ctx.vldm_regs > 0) {
    const ArmFltRegRange range = ArmGetFltRegRanges(ctx.vldm_regs);
    output->emplace_back(MakeIns(a32::OPC::vldmia_s_update, +a32::PRED::al,
                                 range.start, range.count, +a32::REG::sp));
  }

  if (ctx.ldm_regs > 0) {
    output->emplace_back(MakeIns(a32::OPC::ldmia_update, +a32::PRED::al,
                                 +ctx.ldm_regs, +a32::REG::sp));
  }

  if ((A32RegToAllocMask(GPR_REGS[15]) & ctx.ldm_regs) == 0) {
    output->emplace_back(MakeIns(a32::OPC::bx, +a32::PRED::al, +a32::REG::lr));
  }
}

void InitCodeGenA32() {
  // GPR
  for (size_t i = 0; i < 16; ++i) {
    GPR_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::GPR, StrNew(GPR_NAMES[i]));
    const uint32_t mask = A32RegToAllocMask(GPR_REGS[i]);
    if (i < GPR_PARAM_REGS.size()) {
      ASSERT((GPR_LAC_REGS_MASK & mask) == 0,
             "" << i << " " << GPR_LAC_REGS_MASK);
      GPR_PARAM_REGS[i] = GPR_REGS[i];
    }
  }

  // FLT
  for (unsigned i = 0; i < 32; ++i) {
    char buffer[8];
    buffer[0] = 's';
    ToDecString(i, buffer + 1);
    FLT_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::FLT, StrNew(buffer));
    uint32_t mask = A32RegToAllocMask(FLT_REGS[i]);
    if (i < FLT_PARAM_REGS.size()) {
      ASSERT((FLT_LAC_REGS_MASK & mask) == 0, "");
      FLT_PARAM_REGS[i] = FLT_REGS[i];
    }
  }

  // DBL
  for (unsigned i = 0; i < 16; ++i) {
    char buffer[8];
    buffer[0] = 'd';
    ToDecString(i, buffer + 1);
    DBL_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::DBL, StrNew(buffer));
    if (i < DBL_PARAM_REGS.size()) {
      DBL_PARAM_REGS[i] = DBL_REGS[i];
    }
  }

  for (unsigned i = 0; i < DK_TO_CPU_REG_KIND_MAP.size(); ++i) {
    DK_TO_CPU_REG_KIND_MAP[i] = +CPU_REG_KIND::INVALID;
  }
  DK_TO_CPU_REG_KIND_MAP[+DK::S8] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U8] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::S16] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U16] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::S32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::U32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::A32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::C32] = +CPU_REG_KIND::GPR;
  DK_TO_CPU_REG_KIND_MAP[+DK::F32] = +CPU_REG_KIND::FLT;
  DK_TO_CPU_REG_KIND_MAP[+DK::F64] = +CPU_REG_KIND::DBL;
}

}  // namespace cwerg::code_gen_a32
