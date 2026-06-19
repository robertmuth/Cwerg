// (c) Robert Muth - see LICENSE for more info

#include "BE/CodeGenX64/codegen.h"

#include <string_view>

#include "BE/Base/serialize.h"
#include "BE/CodeGenX64/isel_gen.h"
#include "BE/CodeGenX64/regs.h"
#include "BE/CodeGenCommon/cpu_neutral.h"
#include "BE/CpuX64/assembler.h"
#include "BE/CpuX64/opcode_gen.h"
#include "BE/CpuX64/opcode_gen_enum.h"
#include "BE/CpuX64/symbolic.h"
#include "Util/parse.h"

namespace cwerg::code_gen_x64 {

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


bool SimpifyCpuIns(x64::Ins cpu_ins) {
  if (cpu_ins.operands[0] != cpu_ins.operands[1]) return true;
  x64::OPC opc = x64::OpcodeOPC(cpu_ins.opcode);
  return opc != x64::OPC::mov_8_r_mr && opc != x64::OPC::mov_16_r_mr &&
         opc != x64::OPC::mov_64_r_mr;
}

x64::Ins HandleInline(const char* cpu_asm_str) {
  std::vector<std::string_view> token;
  ParseLineWithStrings(cpu_asm_str, false, &token);
  x64::Ins cpu_ins;
  if (!InsFromSymbolized(token, &cpu_ins)) {
    ASSERT(false, "internal parse error " << token[0]);
  }
  return cpu_ins;
}

void FunCodeGen(Fun fun, std::ostream* output) {
  ASSERT(FunKind(fun) != FUN_KIND::EXTERN, "");
  *output << "# sig: IN: ";
  EmitParamList(FunNumInputTypes(fun), FunInputTypes(fun), output);
  *output << " -> OUT: ";
  EmitParamList(FunNumOutputTypes(fun), FunOutputTypes(fun), output);
  *output << "  stk_size:" << FunStackSize(fun) << "\n";
  *output << ".fun " << Name(fun) << " 16\n";
  for (Jtb jtb : FunJtbIter(fun)) {
    JtbCodeGenSimpleText(jtb, output, 8);
  }

  std::vector<x64::Ins> inss;
  std::vector<std::string> ops;
  auto drain = [&]() {
    for (const auto& ins : inss) {
      ops.clear();
      std::string_view name = x64::InsSymbolize(ins, true, false, &ops);
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
      } else if (InsOPC(ins) == OPC::INLINE) {
        inss.push_back(HandleInline(StrData(Str(InsOperand(ins, 0)))));
      } else {
        const Pattern* pat = FindMatchingPattern(ins);
        if (pat == nullptr) {
          InsRenderToAsm(ins, &std::cerr);
          ASSERT(false, "Cannot find for pattern for INS above");
        }

        for (unsigned i = 0; i < pat->length; ++i) {
          x64::Ins cpu_ins = MakeInsFromTmpl(pat->start[i], ins, ctx);
          if (SimpifyCpuIns(cpu_ins)) {
            inss.push_back(cpu_ins);
          }
        }
      }
    }
    drain();
  }
  *output << ".endfun\n";
}





}  // namespace

void EmitUnitAsText(base::Unit unit, std::ostream* output) {
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGenText(mem, output);
  }
  for (Fun fun : UnitFunIter(unit)) {
    if (FunKind(fun) == FUN_KIND::SIGNATURE) continue;
    FunCodeGen(fun, output);
  }
}

x64::X64Unit EmitUnitAsBinary(base::Unit unit) {
  x64::X64Unit out;
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGenBinary(mem, +elf::RELOC_TYPE_X86_64::X_64, &out);
  }

  std::vector<x64::Ins> inss;
  auto drain = [&]() {
    for (auto& ins : inss) {
      AddIns(&out, &ins);
    }
    inss.clear();
  };

  for (Fun fun : UnitFunIter(unit)) {
    ASSERT(FunKind(fun) != FUN_KIND::EXTERN, "");
    out.FunStart(StrData(Name(fun)), 16, x64::TextPadder);
    for (Jtb jtb : FunJtbIter(fun)) {
      JtbCodeGenSimpleBinary(jtb, 8, +elf::RELOC_TYPE_X86_64::X_64, &out);
    }
    EmitContext ctx = FunComputeEmitContext(fun);
    EmitFunProlog(ctx, &inss);
    drain();
    for (Bbl bbl : FunBblIter(fun)) {
      out.AddLabel(StrData(Name(bbl)), 1, x64::TextPadder);
      for (Ins ins : BblInsIter(bbl)) {
        if (InsOPC(ins) == OPC::NOP1) {
          ctx.scratch_cpu_reg = CpuReg(RegCpuReg(Reg(InsOperand(ins, 0))));
        } else if (InsOPC(ins) == OPC::RET) {
          EmitFunEpilog(ctx, &inss);
        } else if (InsOPC(ins) == OPC::LINE) {
          // TODO
        } else if (InsOPC(ins) == OPC::INLINE) {
          inss.push_back(HandleInline(StrData(Str(InsOperand(ins, 0)))));
        } else {
          const Pattern* pat = FindMatchingPattern(ins);
          ASSERT(pat != nullptr, "could not find matching pattern for "
                                     << ins << " in " << Name(fun));
          for (unsigned i = 0; i < pat->length; ++i) {
            x64::Ins cpu_ins = MakeInsFromTmpl(pat->start[i], ins, ctx);
            if (SimpifyCpuIns(cpu_ins)) {
              inss.push_back(cpu_ins);
            }
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

}  // namespace  cwerg::code_gen_x64
