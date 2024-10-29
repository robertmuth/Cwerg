#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <array>

#include "BE/Base/ir.h"
#include "BE/Base/lowering.h"
#include "BE/Base/reg_stats.h"
#include "BE/CpuX64/opcode_gen.h"

namespace cwerg::code_gen_x64 {
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

// Note, these arrays will be UNINITIALIZED unless InitCodeGenX32 is called
extern std::array<base::CpuReg, 16> GPR_REGS;
extern std::array<base::CpuReg, 16> FLT_REGS;

// must be called early in main()
extern void InitCodeGenX64();

// Return a list of all cpu regs - this is primarily used by tests that
// parse IR fragments with pre-allocated regs.
extern std::vector<base::CpuReg> GetAllRegs();

struct EmitContext {
  uint32_t gpr_reg_mask = 0;
  uint32_t flt_reg_mask = 0;
  uint32_t stk_size = 0;
  bool is_leaf = false;
  base::CpuReg scratch_cpu_reg = base::CpuReg(base::HandleInvalid);

  uint32_t FrameSize() const {
    // we assume that stk_size is 16B aligned. To that we add:
    // the saved flt regs, the saved gpr regs, the return address
    uint32_t out = stk_size + 8 * __builtin_popcount(flt_reg_mask) +
                   8 * __builtin_popcount(gpr_reg_mask) + 8;
    // if we have to make an adjustment make sure we end up being
    // 16B aligned. Not for a lead function it is ok for the stack
    // to be only 8B aligned
    if (!is_leaf || stk_size != 0 || flt_reg_mask != 0) {
      out = (out + 15) / 16 * 16;
    }
    return out;
  }

  uint32_t StackAdjustment() const {
    // the saved gpr regs and the return address will be pushed
    // onto the stack and hence need no adjustment
    return FrameSize() - 8 * __builtin_popcount(gpr_reg_mask) - 8;
  }
};

constexpr const uint32_t GPR_RESERVED_MASK = 0x0011;
constexpr const uint32_t GPR_REGS_MASK = 0xffee;
constexpr const uint32_t GPR_LAC_REGS_MASK = 0xf028;

constexpr const uint32_t GPR_REG_IMPLICIT_MASK = 0x0007;
constexpr const uint32_t FLT_RESERVED_MASK = 0x0001;
constexpr const uint32_t FLT_REGS_MASK = 0xfffe;
constexpr const uint32_t FLT_LAC_REGS_MASK = 0xff00;

// maps the DK of Cwerg reg to the CPU_REG_KIND needed for a cpu reg
extern base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

inline uint32_t CpuRegToAllocMask(base::CpuReg cpu_reg) {
  return 1U << CpuRegNo(cpu_reg);
}

extern std::vector<base::CpuReg> GetCpuRegsForInSignature(
    unsigned count, const base::DK* kinds);

extern std::vector<base::CpuReg> GetCpuRegsForOutSignature(
    unsigned count, const base::DK* kinds);

// Note: regs must match the class of  cpu_reg_mask, e.g. be all
// floating point or all GPR
// This will use up the "first_choice" regs first.  "second_choice"
// may incur additional cost, e.g. due to the registers being "callee save".
extern void AssignCpuRegOrMarkForSpilling(
    const std::vector<base::Reg>& assign_to, uint32_t cpu_reg_mask_first_choice,
    uint32_t cpu_reg_mask_second_choice);

// must be called early in main()
extern void InitCodeGenX64();

extern const base::PushPopInterface* const PushPopInterfaceX64;

extern void FunLocalRegAlloc(base::Fun fun, std::vector<base::Ins>* inss);

extern EmitContext FunComputeEmitContext(base::Fun fun);

extern void FunPushargConversion(base::Fun fun);
extern void FunPopargConversion(base::Fun fun);

}  // namespace cwerg::code_gen_x64
