// (c) Robert Muth - see LICENSE for more info

#include <algorithm>
#include <iomanip>

#include "Base/canonicalize.h"
#include "Base/cfg.h"
#include "Base/liveness.h"
#include "Base/lowering.h"
#include "Base/optimize.h"
#include "Base/reg_alloc.h"
#include "Base/sanity.h"
#include "Base/serialize.h"
#include "CodeGenA64/isel_gen.h"
#include "CodeGenA64/regs.h"

namespace cwerg::code_gen_a64 {
namespace {

using namespace cwerg;
using namespace cwerg::base;

// +-prefix converts an enum the underlying integer type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

bool InsRequiresSpecialHandling(Ins ins) {
  const OPC opc = InsOPC(ins);
  return opc == OPC::LINE ||  // handled via special epilog code
         opc == OPC::RET ||   // handled via special epilog code
         opc == OPC::NOP1;    // pseudo instruction
}

void FunAddNop1ForCodeSel(Fun fun, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    Reg tmp;
    for (Ins ins : BblInsIter(bbl)) {
      switch (InsOPC(ins)) {
        case OPC::SWITCH:
          tmp = FunGetScratchReg(fun, DK::C64, "switch", false);
          inss->push_back(InsNew(OPC::NOP1, tmp));
          inss->push_back(ins);
          dirty = true;
          break;
        case OPC::CAS:
          tmp = FunGetScratchReg(fun, DK::U64, "cas", false);
          inss->push_back(InsNew(OPC::NOP1, tmp));
          inss->push_back(ins);
          dirty = true;
          break;
        case OPC::COPYSIGN:
          tmp = FunGetScratchReg(fun, DK::U64, "copysign", false);
          inss->push_back(InsNew(OPC::NOP1, tmp));
          inss->push_back(ins);
          dirty = true;
          break;
        case OPC::CNTPOP:
          tmp = FunGetScratchReg(fun, DK::F64, "cntpop", false);
          inss->push_back(InsNew(OPC::NOP1, tmp));
          inss->push_back(ins);
          dirty = true;
          break;
        default:
          inss->push_back(ins);
          break;
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

void FunRewriteOutOfBoundsImmediates(Fun fun, Unit unit,
                                     std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      if (!InsRequiresSpecialHandling(ins)) {
        const uint8_t mismatches =
            code_gen_a64::FindtImmediateMismatchesInBestMatchPattern(ins, true);
        if (mismatches != 0) {
          ASSERT(mismatches != code_gen_a64::MATCH_IMPOSSIBLE,
                 "cannot match: " << ins);
          for (unsigned pos = 0; pos < a64::MAX_OPERANDS; ++pos) {
            if (mismatches & (1U << pos)) {
              const DK kind = ConstKind(Const(InsOperand(ins, pos)));
              if (kind == DK::F64 || kind == DK::F32) {
                InsEliminateImmediateViaMem(ins, pos, fun, unit, DK::A64,
                                            DK::U32, inss);
              } else {
                InsEliminateImmediateViaMov(ins, pos, fun, inss);
              }
              dirty = true;
            }
          }
        }
      }
      inss->push_back(ins);
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

int FunMoveEliminationCpu(Fun fun, std::vector<Ins>* to_delete) {
  to_delete->clear();

  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      OPC opc = InsOPC(ins);
      if (opc == OPC::MOV) {
        Reg dst(InsOperand(ins, 0));
        Reg src(InsOperand(ins, 1));
        if (src.kind() == RefKind::REG && RegCpuReg(src) == RegCpuReg(dst)) {
          to_delete->push_back(ins);
        }
      }
    }
  }

  for (Ins ins : *to_delete) {
    BblInsUnlink(ins);
    InsDel(ins);
  }
  return to_delete->size();
}

// Return all global regs in `fun` that map to `rk` after applying `rk_map`
// and whose `lac-ness` matches `is_lac`
void FunFilterGlobalRegs(Fun fun, CPU_REG_KIND rk, bool is_lac,
                         const DK_MAP& rk_map, std::vector<Reg>* out) {
  for (Reg reg : FunRegIter(fun)) {
    if (RegHasFlag(reg, REG_FLAG::GLOBAL) && RegCpuReg(reg).isnull() &&
        RegHasFlag(reg, REG_FLAG::LAC) == is_lac &&
        rk_map[+RegKind(reg)] == +rk) {
      out->push_back(reg);
    }
  }
}

bool SpillingNeeded(const FunRegStats& needed, unsigned num_regs_lac,
                    unsigned num_regs_not_lac) {
  return needed.global_lac + needed.local_lac > num_regs_lac ||
         needed.global_lac + needed.local_lac + needed.global_not_lac +
                 needed.local_not_lac >
             num_regs_lac + num_regs_not_lac;
}

// This assumes that at least count bits are set.
uint32_t FindMaskCoveringTheLowOrderSetBits(uint32_t bits, unsigned count) {
  if (count == 0) return 0;
  uint32_t mask = 1;
  unsigned n = 0;
  while (n < count) {
    if ((mask & bits) != 0) ++n;
    mask <<= 1U;
  }
  return mask - 1;
}

struct PoolMasks {
  uint32_t mask_lac;
  uint32_t mask_not_lac;
};

PoolMasks GetRegPoolsForGlobals(const FunRegStats& needed, uint32_t regs_lac,
                                uint32_t regs_not_lac,
                                uint32_t regs_preallocated) {
  unsigned num_regs_lac = __builtin_popcount(regs_lac);
  unsigned num_regs_not_lac = __builtin_popcount(regs_not_lac);
  bool spilling_needed = SpillingNeeded(needed, num_regs_lac, num_regs_not_lac);

  uint32_t global_lac = regs_lac;
  uint32_t local_lac = 0;
  if (num_regs_lac > needed.global_lac) {
    const uint32_t mask =
        FindMaskCoveringTheLowOrderSetBits(global_lac, needed.global_lac);
    local_lac = global_lac & ~mask;
    global_lac = global_lac & mask;
  }

  uint32_t global_not_lac = 0;
  if (num_regs_not_lac > needed.local_not_lac + spilling_needed) {
    const uint32_t mask = FindMaskCoveringTheLowOrderSetBits(
        regs_not_lac, needed.local_not_lac + spilling_needed);
    global_not_lac = regs_not_lac & ~(mask | regs_preallocated);
  }

  if (__builtin_popcount(local_lac) > needed.local_lac) {
    const uint32_t mask =
        FindMaskCoveringTheLowOrderSetBits(local_lac, needed.local_lac);
    global_not_lac |= local_lac & ~mask;
  }
  return PoolMasks{global_lac, global_not_lac};
}

}  // namespace

void PhaseLegalizationStep1(Fun fun, Unit unit, std::ostream* fout) {
  std::vector<Ins> inss;
  FunRegWidthWidening(fun, DK::U8, DK::U32, &inss);
  FunRegWidthWidening(fun, DK::S8, DK::S32, &inss);
  FunRegWidthWidening(fun, DK::U16, DK::U32, &inss);
  FunRegWidthWidening(fun, DK::S16, DK::S32, &inss);
}

void PhaseLegalizationStep2(Fun fun, Unit unit, std::ostream* fout) {
  std::vector<Ins> inss;
  FunSetInOutCpuRegs(fun, *PushPopInterfaceA64);

  if (FunKind(fun) != FUN_KIND::NORMAL) return;
  FunPushargConversion(fun, *PushPopInterfaceA64);
  FunPopargConversion(fun, *PushPopInterfaceA64);
  FunEliminateRem(fun, &inss);

  FunEliminateStkLoadStoreWithRegOffset(fun, DK::A64, DK::S32, &inss);
  FunEliminateMemLoadStore(fun, DK::A64, DK::S32, &inss);

  FunCanonicalize(fun);
  // We need to run this before massaging immediates because it changes
  // COND_RRA instruction possibly with immediates.
  FunCfgExit(fun);

  FunRewriteOutOfBoundsImmediates(fun, unit, &inss);
}

void DumpRegStats(Fun fun, const DK_LAC_COUNTS& stats, std::ostream* output) {
  unsigned local_lac = 0;
  unsigned local_not_lac = 0;
  for (size_t i = 0; i < stats.lac.size(); ++i) {
    local_lac += stats.lac[i];
    local_not_lac += stats.not_lac[i];
  }
  std::vector<Reg> global_lac;
  std::vector<Reg> global_not_lac;
  std::vector<Reg> allocated_lac;
  std::vector<Reg> allocated_not_lac;
  for (Reg reg : FunRegIter(fun)) {
    if (!RegHasFlag(reg, REG_FLAG::GLOBAL)) continue;
    if (RegCpuReg(reg).isnull()) {
      if (RegHasFlag(reg, REG_FLAG::LAC))
        global_lac.push_back(reg);
      else
        global_not_lac.push_back(reg);
    } else {
      if (RegHasFlag(reg, REG_FLAG::LAC))
        allocated_lac.push_back(reg);
      else
        allocated_not_lac.push_back(reg);
    }
  }
  if (output != nullptr) {
    *output << "# REGSTATS " << std::left << std::setw(20) << Name(fun)
            << std::right
            << "   "
            //
            << "all: " << std::setw(2) << allocated_lac.size() << " "
            << std::setw(2) << allocated_not_lac.size()
            << "  "
            //
            << "glo: " << std::setw(2) << global_lac.size() << " "
            << std::setw(2) << global_not_lac.size()
            << "  "
            //
            << "loc: " << std::setw(2) << local_lac << " " << std::setw(2)
            << local_not_lac << "\n";
  }
}

void GlobalRegAllocOneKind(Fun fun, CPU_REG_KIND kind,
                           const FunRegStats& needed, uint32_t regs_lac,
                           uint32_t regs_not_lac, uint32_t regs_lac_mask,
                           std::vector<Reg>* regs,
                           std::vector<Reg>* to_be_spilled,
                           std::ostream* debug) {
  uint32_t pre_alloced = 0;
  for (Reg reg : FunRegIter(fun)) {
    CpuReg cpu_reg(RegCpuReg(reg));
    if (cpu_reg.kind() != RefKind::CPU_REG) continue;
    if (CPU_REG_KIND(CpuRegKind(cpu_reg)) == kind) {
      pre_alloced |= CpuRegToAllocMask(cpu_reg);
    }
  }

  auto reg_cmp = [](Reg a, Reg b) -> bool {
    return StrCmpLt(Name(a), Name(b));
  };

  if (debug)
    *debug << "@@  " << EnumToString(kind) << " " << needed.global_lac << " "
           << needed.global_not_lac << " " << needed.local_lac << " "
           << needed.local_not_lac << "\n";

  const auto [global_lac, global_not_lac] =
      GetRegPoolsForGlobals(needed, regs_lac, regs_not_lac, pre_alloced);

  if (debug)
    *debug << "@@ " << EnumToString(kind) << " POOL " << std::hex << global_lac
           << " " << global_not_lac << std::dec << "\n";

  // handle is_lac global regs
  regs->clear();
  FunFilterGlobalRegs(fun, kind, true, DK_TO_CPU_REG_KIND_MAP, regs);
  std::sort(regs->begin(), regs->end(), reg_cmp);  // make things deterministic
  AssignCpuRegOrMarkForSpilling(*regs, global_lac, 0, to_be_spilled);
  // handle not is_lac global regs
  regs->clear();
  FunFilterGlobalRegs(fun, kind, false, DK_TO_CPU_REG_KIND_MAP, regs);
  std::sort(regs->begin(), regs->end(), reg_cmp);  // make things deterministic
  AssignCpuRegOrMarkForSpilling(*regs, global_not_lac & ~regs_lac_mask,
                                global_not_lac & regs_lac_mask, to_be_spilled);
}

void PhaseGlobalRegAlloc(Fun fun, Unit unit, std::ostream* fout) {
  if (fout != nullptr) {
    *fout << "############################################################\n"
          << "# GlobalRegAlloc " << Name(fun) << "\n"
          << "############################################################\n";
  }

  //
  FunComputeRegStatsExceptLAC(fun);
  FunDropUnreferencedRegs(fun);
  FunNumberReg(fun);
  FunComputeLivenessInfo(fun);
  FunComputeRegStatsLAC(fun);
  const DK_LAC_COUNTS local_reg_stats =
      FunComputeBblRegUsageStats(fun, DK_TO_CPU_REG_KIND_MAP);
  const DK_LAC_COUNTS global_reg_stats =
      FunGlobalRegStats(fun, DK_TO_CPU_REG_KIND_MAP);
  if (fout != nullptr) {
    DumpRegStats(fun, local_reg_stats, fout);
  }

  std::vector<Reg> to_be_spilled;
  std::vector<Reg> regs;
  std::ostream* debug = nullptr;

  {
    const FunRegStats needed{global_reg_stats.lac[+CPU_REG_KIND::GPR],      //
                             global_reg_stats.not_lac[+CPU_REG_KIND::GPR],  //
                             local_reg_stats.lac[+CPU_REG_KIND::GPR],       //
                             local_reg_stats.not_lac[+CPU_REG_KIND::GPR]};
    GlobalRegAllocOneKind(fun, CPU_REG_KIND::GPR, needed,
                          GPR_REGS_MASK & GPR_LAC_REGS_MASK,
                          GPR_REGS_MASK & ~GPR_LAC_REGS_MASK, GPR_LAC_REGS_MASK,
                          &regs, &to_be_spilled, debug);
  }
  {
    const FunRegStats needed{global_reg_stats.lac[+CPU_REG_KIND::FLT],
                             global_reg_stats.not_lac[+CPU_REG_KIND::FLT],
                             local_reg_stats.lac[+CPU_REG_KIND::FLT],
                             local_reg_stats.not_lac[+CPU_REG_KIND::FLT]};
    GlobalRegAllocOneKind(fun, CPU_REG_KIND::FLT, needed,
                          FLT_REGS_MASK & FLT_LAC_REGS_MASK,
                          FLT_REGS_MASK & ~FLT_LAC_REGS_MASK, FLT_LAC_REGS_MASK,
                          &regs, &to_be_spilled, debug);
  }

  std::vector<Ins> inss;
  FunSpillRegs(fun, DK::U32, to_be_spilled, &inss, "$gspill");
}

void PhaseFinalizeStackAndLocalRegAlloc(Fun fun, Unit unit,
                                        std::ostream* fout) {
  std::vector<Ins> inss;
  FunComputeRegStatsExceptLAC(fun);
  FunDropUnreferencedRegs(fun);
  FunNumberReg(fun);
  FunComputeLivenessInfo(fun);
  FunComputeRegStatsLAC(fun);
  FunAddNop1ForCodeSel(fun, &inss);
  FunLocalRegAlloc(fun, &inss);
  FunFinalizeStackSlots(fun);
  FunMoveEliminationCpu(fun, &inss);
}

void LegalizeAll(Unit unit, bool verbose, std::ostream* fout) {
  std::vector<Fun> seeds;
  Fun fun = UnitFunFind(unit, StrNew("main"));
  if (!fun.isnull()) seeds.push_back(fun);
  fun = UnitFunFind(unit, StrNew("_start"));
  if (!fun.isnull()) seeds.push_back(fun);
  if (!seeds.empty()) UnitRemoveUnreachableCode(unit, seeds);
  for (Fun fun : UnitFunIter(unit)) {
    FunCheck(fun);
    if (FunKind(fun) == FUN_KIND::NORMAL) {
      FunCfgInit(fun);
      FunOptBasic(fun, true);
    }

    FunCheck(fun);
    PhaseLegalizationStep1(fun, unit, fout);
    PhaseLegalizationStep2(fun, unit, fout);
  }
}

void RegAllocGlobal(Unit unit, bool verbose, std::ostream* fout) {
  for (Fun fun : UnitFunIter(unit)) {
    FunCheck(fun);
    PhaseGlobalRegAlloc(fun, unit, fout);
  }
}

void RegAllocLocal(Unit unit, bool verbose, std::ostream* fout) {
  for (Fun fun : UnitFunIter(unit)) {
    PhaseFinalizeStackAndLocalRegAlloc(fun, unit, fout);
  }
}

}  // namespace  cwerg::code_gen_a64
