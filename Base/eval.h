#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
namespace cwerg::base {

extern bool EvaluateCondBra(OPC opc, Const a, Const b);
extern Const EvaluateALU(OPC opc, Const a, Const b);
extern Const EvaluateALU1(OPC opc, Const a);

extern Const ConvertIntValue(DK kind_dst, Const a);
}
