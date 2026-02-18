// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/canonicalize.h"
#include "IR/opcode_gen.h"

namespace cwerg::base {

int FunCanonicalize(Fun fun) {
  int count = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      if (!InsOpcode(ins).HasAttribute(OA::COMMUTATIVE)) continue;
      switch (InsOpcodeKind(ins)) {
        case OPC_KIND::ALU:
          if (Kind(InsOperand(ins, 1)) == RefKind::CONST &&
              Kind(InsOperand(ins, 2)) == RefKind::REG) {
            InsSwapOps(ins, 1, 2);
            ++count;
          }
          break;
        case OPC_KIND::CMP:
          if (Kind(InsOperand(ins, 3)) == RefKind::CONST &&
              Kind(InsOperand(ins, 4)) == RefKind::REG) {
            InsSwapOps(ins, 3, 4);
            ++count;
          }
          break;
        case OPC_KIND::COND_BRA:
          if (Kind(InsOperand(ins, 0)) == RefKind::CONST &&
              Kind(InsOperand(ins, 1)) == RefKind::REG) {
            if (InsOPC(ins) == OPC::BEQ || InsOPC(ins) == OPC::BNE) {
              InsSwapOps(ins, 0, 1);
              ++count;
            }
          }
          break;
        default:
          break;
      }
    }
  }
  return count;
}
}  // namespace cwerg::base
