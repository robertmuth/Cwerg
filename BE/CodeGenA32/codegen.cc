// (c) Robert Muth - see LICENSE for more info

#include "BE/CodeGenA32/codegen.h"

#include "BE/Base/ir.h"
#include "BE/Base/optimize.h"
#include "BE/Base/serialize.h"
#include "BE/CodeGenA32/isel_gen.h"
#include "BE/CodeGenA32/legalize.h"
#include "BE/CodeGenA32/regs.h"
#include "BE/CodeGenCommon/cpu_neutral.h"
#include "BE/CpuA32/opcode_gen.h"
#include "BE/CpuA32/symbolic.h"
#include "Util/parse.h"

namespace cwerg::code_gen_a32 {

using namespace cwerg;
using namespace cwerg::base;
using namespace cwerg::code_gen_common;

namespace {

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

std::string_view padding_nop("\x00\xf0\x20\xe3", 4);

void FunCodeGenArm32(Fun fun, std::ostream* output) {
  ASSERT(FunKind(fun) != FUN_KIND::EXTERN, "");
  *output << "# sig: IN: ";
  EmitParamList(FunNumInputTypes(fun), FunInputTypes(fun), output);
  *output << " -> OUT: ";
  EmitParamList(FunNumOutputTypes(fun), FunOutputTypes(fun), output);
  *output << "  stk_size:" << FunStackSize(fun) << "\n";
  *output << ".fun " << Name(fun) << " 16\n";
  for (Jtb jtb : FunJtbIter(fun)) {
    JtbCodeGenSimpleText(jtb, output, 4);
  }

  std::vector<a32::Ins> inss;
  std::vector<std::string> ops;
  auto drain = [&]() {
    for (const auto& ins : inss) {
      ops.clear();
      std::string_view name = a32::InsSymbolize(ins, &ops);
      *output << "    " << name;
      for (const std::string& op : ops) *output << " " << op;
      *output << "\n";
    }
    inss.clear();
  };

  EmitContext ctx = FunComputeEmitContext(fun);
  EmitFunProlog(ctx, &inss);
  drain();
  for (Bbl bbl : FunBblIter(fun)) {
    *output << ".bbl " << Name(bbl) << " 4\n";
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::NOP1) {
        ctx.scratch_cpu_reg = CpuReg(RegCpuReg(Reg(InsOperand(ins, 0))));
      } else if (InsOPC(ins) == OPC::RET) {
        EmitFunEpilog(ctx, &inss);
      } else {
        const Pattern* pat = FindMatchingPattern(ins);
        ASSERT(pat != nullptr, "");
        for (unsigned i = 0; i < pat->length; ++i) {
          inss.push_back(MakeInsFromTmpl(pat->start[i], ins, ctx));
        }
      }
    }
    drain();
  }
  *output << ".endfun\n";
}

}  // namespace

void EmitUnitAsText(Unit unit, std::ostream* output) {
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGenText(mem, output);
  }
  for (Fun fun : UnitFunIter(unit)) {
    if (FunKind(fun) == FUN_KIND::SIGNATURE) continue;
    FunCodeGenArm32(fun, output);
  }
}

a32::A32Unit EmitUnitAsBinary(base::Unit unit) {
  a32::A32Unit out;
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGenBinary(mem, +elf::RELOC_TYPE_ARM::ABS32, &out);
  }

  std::vector<a32::Ins> inss;
  auto drain = [&]() {
    for (auto& ins : inss) {
      AddIns(&out, &ins);
    }
    inss.clear();
  };

  for (Fun fun : UnitFunIter(unit)) {
    ASSERT(FunKind(fun) != FUN_KIND::EXTERN, "");
    out.FunStart(StrData(Name(fun)), 16, padding_nop);
    for (Jtb jtb : FunJtbIter(fun)) {
      JtbCodeGenSimpleBinary(jtb, 4, +elf::RELOC_TYPE_ARM::ABS32, &out);
    }
    EmitContext ctx = FunComputeEmitContext(fun);
    EmitFunProlog(ctx, &inss);
    drain();
    for (Bbl bbl : FunBblIter(fun)) {
      out.AddLabel(StrData(Name(bbl)), 4, padding_nop);
      for (Ins ins : BblInsIter(bbl)) {
        if (InsOPC(ins) == OPC::NOP1) {
          ctx.scratch_cpu_reg = CpuReg(RegCpuReg(Reg(InsOperand(ins, 0))));
        } else if (InsOPC(ins) == OPC::RET) {
          EmitFunEpilog(ctx, &inss);
        } else if (InsOPC(ins) == OPC::LINE) {
          // TODO
        } else {
          const Pattern* pat = FindMatchingPattern(ins);
          ASSERT(pat != nullptr, "cannot find match for " << ins);
          for (unsigned i = 0; i < pat->length; ++i) {
            inss.push_back(MakeInsFromTmpl(pat->start[i], ins, ctx));
          }
        }
      }
      drain();
    }
    out.FunEnd();
  }
  out.AddLinkerDefs();
  return out;
}

}  // namespace  cwerg::code_gen_a32
