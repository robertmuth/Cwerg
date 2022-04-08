#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <array>

#include "Base/ir.h"
#include "Base/lowering.h"
#include "Base/reg_stats.h"
#include "CpuA32/opcode_gen.h"

namespace cwerg::code_gen_a32 {
using namespace cwerg;

enum class CPU_REG_KIND : uint8_t {
  INVALID,
  GPR = 1 << 0,
  FLT = 1 << 1,
  DBL = 1 << 2,
};

// Note, these arrays will be UNINITIALIZED unless InitCodeGenA32 is called
extern std::array<base::CpuReg, 16> GPR_REGS;
extern std::array<base::CpuReg, 32> FLT_REGS;
extern std::array<base::CpuReg, 16> DBL_REGS;

extern std::array<base::CpuReg, 6> GPR_PARAM_REGS;
extern std::array<base::CpuReg, 16> FLT_PARAM_REGS;

const constexpr uint32_t GPR_REGS_MASK = 0x5fff;
const constexpr uint32_t GPR_LAC_REGS_MASK = 0x0fc0;

const constexpr uint32_t FLT_REGS_MASK = 0xffffffff;
const constexpr uint32_t FLT_LAC_REGS_MASK = 0xffff0000;

// maps the DK of Cwerg reg to the CPU_REG_KIND needed for a cpu reg
extern base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

// must be called early in main()
extern void InitCodeGenA32();

extern const base::PushPopInterface* const PushPopInterfaceA32;

// Note: regs must match the class of cpu_reg_mask, e.g. be all
// floating point or all GPR
extern void AssignCpuRegOrMarkForSpilling(
    const std::vector<base::Reg>& regs, uint32_t cpu_reg_mask_first_choice,
    uint32_t cpu_reg_mask_second_choice, std::vector<base::Reg>* to_be_spilled);

extern std::vector<base::CpuReg> GetAllRegs();

extern void FunLocalRegAlloc(base::Fun fun, std::vector<base::Ins>* inss);

extern bool FunMustSaveLinkReg(base::Fun fun);

struct EmitContext {
  uint32_t ldm_regs;
  uint32_t vldm_regs;
  uint32_t stm_regs;
  uint32_t vstm_regs;
  uint32_t stk_size = 0;
  base::CpuReg scratch_cpu_reg = base::CpuReg(0);

  uint32_t FrameSize() const {
    return __builtin_popcount(ldm_regs) * 4 +
           __builtin_popcount(vldm_regs) * 8 + stk_size;
  }
};

extern EmitContext FunComputeEmitContext(base::Fun fun);

extern void EmitFunProlog(const EmitContext& ctx,
                          std::vector<a32::Ins>* output);
extern void EmitFunEpilog(const EmitContext& ctx,
                          std::vector<a32::Ins>* output);

extern uint32_t A32RegToAllocMask(base::CpuReg cpu_reg);

// Regs must be either all FLT/DBL or GPR
extern uint32_t A32RegsToAllocMask(const std::vector<base::CpuReg>& regs);

}  // namespace cwerg::code_gen_a32
