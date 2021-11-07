#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
namespace cwerg::base {

bool EvaluateCondBra(OPC opc, Const a, Const b);
Const EvaluateALU(OPC opc, Const a, Const b);
Const EvaluateALU1(OPC opc, Const a);

}
