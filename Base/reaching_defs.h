#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"

namespace cwerg::base {

extern void FunComputeReachingDefs(Fun fun);

extern void FunPropagateConsts(Fun fun);

extern void FunPropagateRegs(Fun fun);

extern int FunConstantFold(Fun fun,
                           bool allow_conv_conversion,
                           std::vector<Ins>* to_delete);

extern void FunLoadStoreSimplify(Fun fun);

}  // namespace cwerg::base
