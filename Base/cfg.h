#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"

namespace cwerg::base {

extern void EdgUnlink(Edg edg);

extern void EdgLink(Edg edg);

extern Fun InsCallee(Ins ins);

extern void FunSplitBbls(Fun fun);

extern void FunInitCFG(Fun fun);

extern void FunRemoveUnconditionalBranches(Fun fun);

extern void FunRemoveEmptyBbls(Fun fun);

extern void FunAddUnconditionalBranches(Fun fun);

}  // namespace cwerg
