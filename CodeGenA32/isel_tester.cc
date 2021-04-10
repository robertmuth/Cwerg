// (c) Robert Muth - see LICENSE for more info

#include "Base/serialize.h"
#include "CodeGenA32/isel_gen.h"
#include "CodeGenA32/regs.h"
#include "CpuA32/symbolic.h"
#include "Util/parse.h"

#include <iostream>

namespace {

using namespace cwerg;
using namespace cwerg::base;

const char* OpTypeString(Handle op) {
  switch (op.kind()) {
    default:
      return "_";
    case RefKind::CONST:
      return EnumToString(ConstKind(Const(op)));
    case RefKind::REG:
      return EnumToString(RegKind(Reg(op)));
  }
}

void HandleIns(Ins ins) {
  std::cout << "INS: ";
  InsRenderToAsm(ins, &std::cout);
  std::cout << "  [";
  const char* sep = "";
  for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
    std::cout << sep << OpTypeString(InsOperand(ins, i));
    sep = " ";
  }
  std::cout << "]\n";
  if (InsOPC(ins) == OPC::NOP1 || InsOPC(ins) == OPC::RET) {
    std::cout << "    SPECIAL\n";
    return;
  }

  const uint8_t mismatches =
      code_gen_a32::FindtImmediateMismatchesInBestMatchPattern(ins);
  if (mismatches == code_gen_a32::MATCH_IMPOSSIBLE) {
    std::cout << "    MATCH_IMPOSSIBLE\n";
  } else if (mismatches > 0) {
    std::cout << "    mismatches: " << std::hex << (unsigned)mismatches
              << std::dec << "\n";
  } else {
    const code_gen_a32::Pattern* pat = code_gen_a32::FindMatchingPattern(ins);
    ASSERT(pat != nullptr, "");
    std::cout << "PAT: reg:[";
    sep = "";
    for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
      std::cout << sep << EnumToString(pat->reg_constraints[i]);
      sep = " ";
    }
    std::cout << "]  imm:[";
    sep = "";
    for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
      std::cout << sep << code_gen_a32::EnumToString(pat->imm_constraints[i]);
      sep = " ";
    }
    std::cout << "]\n";

    code_gen_a32::EmitContext ctx;
    for (unsigned i = 0; i < pat->length; ++i) {
      const code_gen_a32::InsTmpl& tmpl = pat->start[i];
      a32::Ins a32ins = code_gen_a32::MakeInsFromTmpl(tmpl, ins, ctx);
      char buffer[128];
      a32::RenderInsSystematic(a32ins, buffer);
      std::cout << "    " << buffer << "\n";
    }
  }
}

void Process(std::istream* input) {
  code_gen_a32::InitCodeGenA32();
  std::vector<char> data = SlurpDataFromStream(input);

  Unit unit = UnitParseFromAsm("unit", {data.data(), data.size()},
                               code_gen_a32::GetAllRegs());
  // UnitRenderToAsm(unit, &std::cout);
  for (Fun fun : UnitFunIter(unit)) {
    for (Bbl bbl : FunBblIter(fun)) {
      for (Ins ins : BblInsIter(bbl)) {
        std::cout << "\n";
        HandleIns(ins);
      }
    }
  }
}

}  // namespace

int main(int argc, const char* argv[]) {
  InitStripes(1);
  Process(&std::cin);
  return 0;
}
