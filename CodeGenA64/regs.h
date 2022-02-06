#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "Base/lowering.h"
#include "Base/reg_stats.h"
#include "CpuA64/opcode_gen.h"

#include <array>

namespace cwerg::code_gen_a64 {
using namespace cwerg;

enum class CPU_REG_KIND : uint8_t {
  INVALID,
  GPR,
  FLT,
};

inline const char* EnumToString(CPU_REG_KIND kind) {
  switch (kind) {
    case CPU_REG_KIND::INVALID:
      return "INVALID";
    case CPU_REG_KIND::GPR:
      return "GPR";
    case CPU_REG_KIND::FLT:
      return "FLT";
    default:
      return "@@UNKNOWN@@";
  }
}

// Note, these arrays will be UNINITIALIZED unless InitCodeGenA32 is called
extern std::array<base::CpuReg, 31> GPR_REGS;

extern std::array<base::CpuReg, 32> FLT_REGS;

const constexpr uint32_t GPR_REGS_MASK = 0x7fffffff;
const constexpr uint32_t GPR_LAC_REGS_MASK = 0x3fff0000;
const constexpr uint32_t GPR_LAC_REGS_MASK_WITH_LR = 0x7fff0000;
const constexpr uint32_t FLT_REGS_MASK = 0xffffffff;
const constexpr uint32_t FLT_LAC_REGS_MASK = 0x0000ff00;

// maps the DK of Cwerg reg to the CPU_REG_KIND needed for a cpu reg
extern base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

inline uint32_t CpuRegToAllocMask(base::CpuReg cpu_reg) {
  return 1U << CpuRegNo(cpu_reg);
}

// must be called early in main()
extern void InitCodeGenA64();

extern const base::PushPopInterface* const PushPopInterfaceA64;

// Note: regs must match the class of  cpu_reg_mask, e.g. be all
// floating point or all GPR
// This will use up the "first_choice" regs first.  "second_choice"
// may incur additional cost, e.g. due to the registers being "callee save".
extern void AssignCpuRegOrMarkForSpilling(
    const std::vector<base::Reg>& assign_to,
    uint32_t cpu_reg_mask_first_choice,
    uint32_t cpu_reg_mask_second_choice,
    std::vector<base::Reg>* to_be_spilled);

// Return a list of all cpu regs - this is primarily used by tests that
// parse IR fragments with pre-allocated regs.
extern std::vector<base::CpuReg> GetAllRegs();

extern void FunLocalRegAlloc(base::Fun fun, std::vector<base::Ins>* inss);

struct EmitContext {
  uint32_t gpr_reg_mask = 0;
  uint32_t flt_reg_mask = 0;
  uint32_t stk_size = 0;
  base::CpuReg scratch_cpu_reg = base::CpuReg(0);
};

extern EmitContext FunComputeEmitContext(base::Fun fun);

}  // namespace cwerg::code_gen_a64
