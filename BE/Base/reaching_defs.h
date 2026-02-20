#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/ir.h"

namespace cwerg::base {

extern void FunComputeReachingDefs(Fun fun);


extern void FunPropagateRegsAndConsts(Fun fun);


extern void FunLoadStoreSimplify(Fun fun);

extern void FunMergeMoveWithSrcDef(Fun fun, std::vector<Ins>* inss);

// Does not need reaching defs
extern int FunConstantFold(Fun fun, bool allow_conv_conversion,
                           std::vector<Ins>* to_delete);
}  // namespace cwerg::base
