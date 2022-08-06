// (c) Robert Muth - see LICENSE for more info

#include "CodeGenX64/codegen.h"

#include <string_view>

#include "Base/serialize.h"
#include "CodeGenX64/isel_gen.h"
#include "CodeGenX64/regs.h"
#include "CpuX64/assembler.h"
#include "CpuX64/opcode_gen.h"
#include "CpuX64/opcode_gen_enum.h"
#include "CpuX64/symbolic.h"
#include "Util/parse.h"

namespace cwerg::code_gen_x64 {

using namespace cwerg;
using namespace cwerg::base;

namespace {

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

std::string_view padding_zero("\0", 1);

void JtbCodeGen(Jtb jtb, std::ostream* output) {
  std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
  for (Jen jen : JtbJenIter(jtb)) {
    table[JenPos(jen)] = JenBbl(jen);
  }
  *output << ".localmem " << Name(jtb) << " 8 rodata\n";
  for (Bbl bbl : table) {
    *output << "    .addr.bbl 8 " << Name(bbl) << "\n";
  }
  *output << ".endmem\n";
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
    JtbCodeGen(jtb, output);
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

std::string_view MemKindToSectionName(MEM_KIND kind) {
  switch (kind) {
    case MEM_KIND::RO:
      return "rodata";
    case MEM_KIND::RW:
      return "data";
    default:
      ASSERT(false, "");
      return "";
  }
}

void MemCodeGen(Mem mem, std::ostream* output) {
  *output << "# size " << MemSize(mem) << "\n"
          << ".mem " << Name(mem) << " " << MemAlignment(mem) << " "
          << MemKindToSectionName(MemKind(mem)) << "\n";
  for (Data data : MemDataIter(mem)) {
    uint32_t size = DataSize(data);
    Handle target = DataTarget(data);
    int32_t extra = DataExtra(data);
    if (target.kind() == RefKind::STR) {
      size_t len = size;
      char buffer[4096];
      if (len > 0) {
        len = BytesToEscapedString({StrData(Str(target)), len}, buffer);
      }
      buffer[len] = 0;
      *output << "    .data " << extra << " \"" << buffer << "\"\n";
    } else if (target.kind() == RefKind::FUN) {
      *output << "    .addr.fun " << size << " " << Name(Fun(target)) << "\n";
    } else {
      ASSERT(target.kind() == RefKind::MEM, "");
      *output << "    .addr.mem " << size << " " << Name(Mem(target))
              << std::hex << " 0x" << extra << std::dec << "\n";
    }
  }

  *output << ".endmem\n";
}

}  // namespace

void EmitUnitAsText(base::Unit unit, std::ostream* output) {
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGen(mem, output);
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
    out.MemStart(StrData(Name(mem)), MemAlignment(mem),
                 MemKindToSectionName(MemKind(mem)), padding_zero, false);
    for (Data data : MemDataIter(mem)) {
      uint32_t size = DataSize(data);
      Handle target = DataTarget(data);
      int32_t extra = DataExtra(data);
      if (target.kind() == RefKind::STR) {
        out.AddData(extra, StrData(Str(target)), size);
      } else if (target.kind() == RefKind::FUN) {
        out.AddFunAddr(size, +elf::RELOC_TYPE_X86_64::X_64,
                       StrData(Name(Fun(target))));
      } else {
        ASSERT(target.kind() == RefKind::MEM, "");
        out.AddMemAddr(size, +elf::RELOC_TYPE_X86_64::X_64,
                       StrData(Name(Mem(target))), extra);
      }
    }
    out.MemEnd();
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
      std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
      for (Jen jen : JtbJenIter(jtb)) {
        table[JenPos(jen)] = JenBbl(jen);
      }
      out.MemStart(StrData(Name(jtb)), 8, "rodata", padding_zero, true);
      for (Bbl bbl : table) {
        out.AddBblAddr(8, +elf::RELOC_TYPE_X86_64::X_64, StrData(Name(bbl)));
      }
      out.MemEnd();
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
