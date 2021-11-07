// (c) Robert Muth - see LICENSE for more info

#include "Base/eval.h"
#include "Base/opcode_gen.h"
#include "Base/serialize.h"

#include <set>

namespace cwerg::base {
namespace {

template <typename VAL>
bool GenericEvaluateCondBra(OPC opc, VAL a, VAL b) {
  switch (opc) {
    case OPC::BEQ:
      return a == b;
    case OPC::BNE:
      return a != b;
    case OPC::BLE:
      return a <= b;
    case OPC::BLT:
      return a < b;
    default:
      ASSERT(false, "");
      return false;
  }
}

template <typename VAL>
VAL GenericEvaluateALU(OPC opc, DK dk, VAL va, VAL vb) {
  switch (opc) {
    case OPC::ADD:
      return va + vb;
    case OPC::SUB:
      return va - vb;
    case OPC::MUL:
      return va * vb;
    case OPC::DIV:
      return vb == 0 ? 0 : va / vb;
    case OPC::OR:
        return va | vb;
      case OPC::AND:
        return va & vb;
      case OPC::XOR:
          return va ^ vb;
      // TODO: REM
    case OPC::SHL:
      return va << (vb % DKBitWidth(dk));
    case OPC::SHR:
      return va >> (vb % DKBitWidth(dk));
    default:
      ASSERT(false, "unimplemented eval for " << EnumToString(opc));
      return 0;  // invalid
  }
}

template <>
double GenericEvaluateALU<double>(OPC opc, DK dk, double va, double vb) {
  switch (opc) {
    case OPC::ADD:
      return va + vb;
    case OPC::SUB:
      return va - vb;
    case OPC::MUL:
      return va * vb;
    case OPC::DIV:
      return vb == 0.0 ? 0 : va / vb;
    default:
      ASSERT(false, "unimplemented eval for " << EnumToString(opc));
      return 0;  // invalid
  }
}

}  // namespace

bool EvaluateCondBra(OPC opc, Const a, Const b) {
  switch (DKFlavor(ConstKind(a))) {
    case DK_FLAVOR_A:
    case DK_FLAVOR_C:
    case DK_FLAVOR_S: {
      return GenericEvaluateCondBra<int64_t>(opc, ConstValueACS(a),
                                             ConstValueACS(b));
    }
    case DK_FLAVOR_U: {
      return GenericEvaluateCondBra<uint64_t>(opc, ConstValueU(a),
                                              ConstValueU(b));
    }
      // TODO: DK_FLAVOR_F:
    default:
      ASSERT(false, "not supported");
      return false;
  }
}

Const EvaluateALU(OPC opc, Const a, Const b) {
  ASSERT(a.kind() == b.kind(), "");
  if (DKFlavor(ConstKind(a)) == DK_FLAVOR_U) {
    return ConstNewU(ConstKind(a),
                     GenericEvaluateALU<uint64_t>(
                         opc, ConstKind(a), ConstValueU(a), ConstValueU(b)));
  } else if (DKFlavor(ConstKind(a)) == DK_FLAVOR_F) {
    return ConstNewF(ConstKind(a),
                     GenericEvaluateALU<double>(
                         opc, ConstKind(a), ConstValueF(a), ConstValueF(b)));
  } else {
    return ConstNewACS(ConstKind(a), GenericEvaluateALU<int64_t>(
                                         opc, ConstKind(a), ConstValueACS(a),
                                         ConstValueACS(b)));
  }
}


Const EvaluateALU1(OPC opc, Const a) {
  ASSERT(false, "unimplemented eval for " << EnumToString(opc));
  return Const();
}

}  // namespace cwerg::base
