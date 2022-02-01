#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "Base/reg_stats.h"
#include "CpuX64/opcode_gen.h"

#include <array>

namespace cwerg::code_gen_x64 {
using namespace cwerg;

enum class CPU_REG_KIND : uint8_t {
  INVALID,
  GPR,
  FLT,
};


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
};

#if 0
const constexpr uint32_t GPR_REGS_MASK = 0x7fffffff;
const constexpr uint32_t GPR_LAC_REGS_MASK = 0x3fff0000;
const constexpr uint32_t GPR_LAC_REGS_MASK_WITH_LR = 0x7fff0000;
const constexpr uint32_t FLT_REGS_MASK = 0xffffffff;
const constexpr uint32_t FLT_LAC_REGS_MASK = 0x0000ff00;

// maps the DK of Cwerg reg to the CPU_REG_KIND needed for a cpu reg
extern base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

inline uint32_t CpuRegToAllocMask(base::CpuReg cpu_reg) { return 1U << CpuRegNo(cpu_reg); }

#endif

extern std::vector<base::CpuReg> GetCpuRegsForInSignature(unsigned count,
                                                        const base::DK* kinds);

extern std::vector<base::CpuReg> GetCpuRegsForOutSignature(unsigned count,
                                                        const base::DK* kinds);

// Note: regs must match the class of  cpu_reg_mask, e.g. be all
// floating point or all GPR
// This will use up the "first_choice" regs first.  "second_choice"
// may incur additional cost, e.g. due to the registers being "callee save".
extern void AssignCpuRegOrMarkForSpilling(
    const std::vector<base::Reg>& assign_to,
    uint32_t cpu_reg_mask_first_choice,
    uint32_t cpu_reg_mask_second_choice,
    std::vector<base::Reg>* to_be_spilled);



// must be called early in main()
extern void InitCodeGenX64();

extern void FunLocalRegAlloc(base::Fun fun, std::vector<base::Ins>* inss);




extern EmitContext FunComputeEmitContext(base::Fun fun);


extern void FunPushargConversion(base::Fun fun);
extern void FunPopargConversion(base::Fun fun);

}  // namespace cwerg::code_gen_a64
