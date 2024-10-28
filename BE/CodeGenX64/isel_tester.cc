// (c) Robert Muth - see LICENSE for more info

#include "Base/serialize.h"
#include "BE/CodeGenX64/isel_gen.h"
#include "BE/CodeGenX64/regs.h"
#include "BE/CpuX64/symbolic.h"
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

void HandleIns(Ins ins, const code_gen_x64::EmitContext& ctx) {
  std::cout << "INS: ";
  InsRenderToAsm(ins, &std::cout);
  std::cout << "  [";
  const char* sep = "";
  for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
    std::cout << sep << OpTypeString(InsOperand(ins, i));
    sep = " ";
  }
  std::cout << "]\n";

  const code_gen_x64::Pattern* pat = code_gen_x64::FindMatchingPattern(ins);
  ASSERT(pat != nullptr, "");
  std::cout << "PAT: reg:[";
  sep = "";
  for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
    std::cout << sep << EnumToString(pat->type_curbs[i]);
    sep = " ";
  }
  std::cout << "]  op:[";
  sep = "";
  for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
    std::cout << sep << code_gen_x64::EnumToString(pat->op_curbs[i]);
    sep = " ";
  }
  std::cout << "]\n";

  std::vector<std::string> ops;
  for (unsigned i = 0; i < pat->length; ++i) {
    const code_gen_x64::InsTmpl& tmpl = pat->start[i];
    x64::Ins cpu_ins = code_gen_x64::MakeInsFromTmpl(tmpl, ins, ctx);
    ops.clear();
    std::string_view name = x64::InsSymbolize(cpu_ins, true, false, &ops);
    std::cout << "    " << name;
    for (const std::string& op : ops) std::cout << " " << op;
    std::cout << "\n";
  }
}

void Process(std::istream* input) {
  code_gen_x64::InitCodeGenX64();
  std::vector<char> data = SlurpDataFromStream(input);

  Unit unit = UnitParseFromAsm("unit", {data.data(), data.size()},
                               code_gen_x64::GetAllRegs());
  code_gen_x64::EmitContext ctx;
  // UnitRenderToAsm(unit, &std::cout);
  for (Fun fun : UnitFunIter(unit)) {
    FunFinalizeStackSlots(fun);
    ctx.scratch_cpu_reg =  code_gen_x64::GPR_REGS[0];
    for (Bbl bbl : FunBblIter(fun)) {
      for (Ins ins : BblInsIter(bbl)) {
        std::cout << "\n";
        HandleIns(ins, ctx);
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
