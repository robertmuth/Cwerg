#include "CodeGenX64/regs.h"
#include "Base/cfg.h"
#include "Base/reg_alloc.h"
#include "Base/serialize.h"
#include "Util/parse.h"

namespace cwerg::code_gen_x64 {

using namespace cwerg;
using namespace cwerg::base;

// The std:arrays below will be initialized by  InitCodeGenA64();
std::array<CpuReg, 16> GPR_REGS;

std::array<CpuReg, 16> FLT_REGS;

base::DK_MAP DK_TO_CPU_REG_KIND_MAP;

constexpr const uint32_t GPR_RESERVED_MASK = 0x0011;
constexpr const uint32_t GPR_REGS_MASK = 0xffee;
constexpr const uint32_t GPR_LAC_REGS_MASK = 0xf028;

constexpr const uint32_t GPR_REG_IMPLICIT_MASK = 0x0007;
constexpr const uint32_t FLT_RESERVED_MASK = 0x0001;
constexpr const uint32_t FLT_REGS_MASK = 0xfffe;
constexpr const uint32_t FLT_LAC_REGS_MASK = 0xff00;

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
        if (cpu_reg.kind() == RefKind::STACK_SLOT) continue;
        ;
        if (cpu_reg.kind() != RefKind::CPU_REG) {
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

}  // namespace

EmitContext FunComputeEmitContext(Fun fun) {
  CpuRegMasks masks = FunCpuRegStats(fun);
  masks.gpr_mask &= GPR_LAC_REGS_MASK;
  masks.flt_mask &= FLT_LAC_REGS_MASK;

  const uint32_t stk_size = (FunStackSize(fun) + 15) / 16 * 16;
  return EmitContext{masks.gpr_mask, masks.flt_mask, stk_size, FunIsLeaf(fun)};
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

  // FLT
  for (unsigned i = 0; i < FLT_REGS.size(); ++i) {
    char buffer[8] = "xmm";
    ToDecString(i, buffer + 3);
    FLT_REGS[i] = CpuRegNew(i, +CPU_REG_KIND::FLT, StrNew(buffer));
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
std::vector<base::CpuReg> GetCpuRegsForSignature(unsigned count,
                                                 const base::DK* kinds) {
  std::vector<base::CpuReg> out;
  // TODO
  return out;
}

void FunPushargConversion(base::Fun fun) {
  // TODO
}

void FunPopargConversion(base::Fun fun) {
  // TODO
}

}  // namespace cwerg::code_gen_x64
