#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "Base/reg_stats.h"
#include "CpuA32/opcode_gen.h"

namespace cwerg::code_gen_a32 {
using namespace cwerg;

// must be called early in main()
extern void InitCodeGenA32();

extern std::vector<base::CpuReg> GetCpuRegsForSignature(unsigned count,
                                                        const base::DK* kinds);

// Note: regs must match the class of  cpu_reg_mask, e.g. be all
// floating point or all GPR
extern void AssignCpuRegOrMarkForSpilling(
    const std::vector<base::Reg>& regs,
    uint32_t cpu_reg_mask_first_choice, uint32_t cpu_reg_mask_second_choice,
    std::vector<base::Reg>* to_be_spilled);

extern std::vector<base::CpuReg> GetAllRegs();

extern void FunLocalRegAlloc(base::Fun fun,
                             std::vector<base::Ins>* inss);

extern bool FunMustSaveLinkReg(base::Fun fun);

struct EmitContext {
  uint32_t ldm_regs;
  uint32_t vldm_regs;
  uint32_t stm_regs;
  uint32_t vstm_regs;
  uint32_t stk_size = 0;
  base::CpuReg scratch_cpu_reg = base::CpuReg(0);
};

extern EmitContext FunComputeEmitContext(base::Fun fun);

extern void EmitFunProlog(const EmitContext& ctx, std::vector<a32::Ins>* output);
extern void EmitFunEpilog(const EmitContext& ctx, std::vector<a32::Ins>* output);

const constexpr  uint32_t GPR_CALLEE_SAVE_REGS_MASK = 0x0fc0;
const constexpr  uint32_t GPR_NOT_LAC_REGS_MASK = 0x503f;

const constexpr uint32_t FLT_CALLEE_SAVE_REGS_MASK = 0xffff0000;
const constexpr uint32_t FLT_PARAM_REGS_REGS_MASK = 0x0000ffff;

extern uint32_t A32RegToAllocMask(base::CpuReg cpu_reg);

// Regs must be either all FLT/DBL or GPR
extern uint32_t A32RegsToAllocMask(const std::vector<base::CpuReg>& regs);

}  // namespace cwerg::code_gen_a32
