// (c) Robert Muth - see LICENSE for more info

#include "BE/CodeGenA32/codegen.h"

#include "BE/Base/cfg.h"
#include "BE/Base/ir.h"
#include "BE/Base/optimize.h"
#include "BE/Base/sanity.h"
#include "BE/Base/serialize.h"
#include "BE/CodeGenA32/isel_gen.h"
#include "BE/CodeGenA32/legalize.h"
#include "BE/CodeGenA32/regs.h"
#include "BE/CpuA32/opcode_gen.h"
#include "BE/CpuA32/symbolic.h"
#include "Util/parse.h"

namespace cwerg::code_gen_a32 {

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
std::string_view padding_nop("\x00\xf0\x20\xe3", 4);

void JtbCodeGen(Jtb jtb, std::ostream* output) {
  std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
  for (Jen jen : JtbJenIter(jtb)) {
    table[JenPos(jen)] = JenBbl(jen);
  }
  *output << ".localmem " << Name(jtb) << " 4 rodata\n";
  for (Bbl bbl : table) {
    *output << "    .addr.bbl 4 " << Name(bbl) << "\n";
  }
  *output << ".endmem\n";
}

void FunCodeGenArm32(Fun fun, std::ostream* output) {
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

std::string_view MemKindToSectionName(MEM_KIND kind) {
  switch (kind) {
    case MEM_KIND::RO:
      return "rodata";
    case MEM_KIND::RW:
      return "data";
    default:
      ASSERT(false, "unsupported mem kind " << base::EnumToString(kind));
      return "";
  }
}

void MemCodeGenArm32(Mem mem, std::ostream* output) {
  *output << "# size " << MemSize(mem) << "\n"
          << ".mem " << Name(mem) << " " << MemAlignment(mem) << " "
          << MemKindToSectionName(MemKind(mem)) << "\n";
  for (Data data : MemDataIter(mem)) {
    uint32_t size = DataSize(data);
    Handle target = DataTarget(data);
    int32_t extra = DataExtra(data);
    if (Kind(target) == RefKind::STR) {
      size_t len = size;
      char buffer[4096];
      if (len > 0) {
        len = BytesToEscapedString({StrData(Str(target)), len}, buffer);
      }
      buffer[len] = 0;
      *output << "    .data " << extra << " \"" << buffer << "\"\n";
    } else if (Kind(target) == RefKind::FUN) {
      *output << "    .addr.fun " << size << " " << Name(Fun(target)) << "\n";
    } else {
      ASSERT(Kind(target) == RefKind::MEM, "");
      *output << "    .addr.mem " << size << " " << Name(Mem(target))
              << std::hex << " 0x" << extra << std::dec << "\n";
    }
  }

  *output << ".endmem\n";
}

}  // namespace

void EmitUnitAsText(Unit unit, std::ostream* output) {
  for (Mem mem : UnitMemIter(unit)) {
    ASSERT(MemKind(mem) != MEM_KIND::EXTERN, "");
    if (MemKind(mem) == MEM_KIND::BUILTIN) continue;
    MemCodeGenArm32(mem, output);
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
    out.MemStart(StrData(Name(mem)), MemAlignment(mem),
                 MemKindToSectionName(MemKind(mem)), padding_zero, false);
    for (Data data : MemDataIter(mem)) {
      uint32_t size = DataSize(data);
      Handle target = DataTarget(data);
      int32_t extra = DataExtra(data);
      if (Kind(target) == RefKind::STR) {
        out.AddData(extra, StrData(Str(target)), size);
      } else if (Kind(target) == RefKind::FUN) {
        out.AddFunAddr(size, +elf::RELOC_TYPE_ARM::ABS32,
                       StrData(Name(Fun(target))));
      } else {
        ASSERT(Kind(target) == RefKind::MEM, "");
        out.AddMemAddr(size, +elf::RELOC_TYPE_ARM::ABS32,
                       StrData(Name(Mem(target))), extra);
      }
    }
    out.MemEnd();
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
      std::vector<Bbl> table(JtbSize(jtb), JtbDefBbl(jtb));
      for (Jen jen : JtbJenIter(jtb)) {
        table[JenPos(jen)] = JenBbl(jen);
      }
      out.MemStart(StrData(Name(jtb)), 4, "rodata", padding_zero, true);
      for (Bbl bbl : table) {
        out.AddBblAddr(4, +elf::RELOC_TYPE_ARM::ABS32, StrData(Name(bbl)));
      }
      out.MemEnd();
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

void LegalizeAll(Unit unit, bool verbose, std::ostream* fout) {
  std::cout << "@@@ LEG ALL " << "\n";

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
    PhaseLegalization(fun, unit, fout);
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

}  // namespace  cwerg::code_gen_a32
