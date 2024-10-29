// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/canonicalize.h"
#include "BE/Base/opcode_gen.h"

namespace cwerg::base {

int FunCanonicalize(Fun fun) {
  int count = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      if (!InsOpcode(ins).HasAttribute(OA::COMMUTATIVE)) continue;
      switch (InsOpcodeKind(ins)) {
        case OPC_KIND::ALU:
          if (InsOperand(ins, 1).kind() == RefKind::CONST &&
              InsOperand(ins, 2).kind() == RefKind::REG) {
            InsSwapOps(ins, 1, 2);
            ++count;
          }
          break;
        case OPC_KIND::CMP:
          if (InsOperand(ins, 3).kind() == RefKind::CONST &&
              InsOperand(ins, 4).kind() == RefKind::REG) {
            InsSwapOps(ins, 3, 4);
            ++count;
          }
          break;
        case OPC_KIND::COND_BRA:
          if (InsOperand(ins, 0).kind() == RefKind::CONST &&
              InsOperand(ins, 2).kind() == RefKind::REG) {
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
