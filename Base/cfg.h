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

extern void FunRemoveUnreachableBbls(Fun fun);

extern void FunAddUnconditionalBranches(Fun fun);

extern void BblSplitAfter(Bbl bbl, Ins new_bbl_first_ins, Bbl new_bbl);

extern void BblSplitBeforeFixEdges(Bbl bbl, Ins new_bbl_last_ins, Bbl new_bbl);

extern Str NewDerivedBblName(Str orig_name, const char* suffix, Fun fun);

extern void UnitRemoveUnreachableCode(Unit unit, const std::vector<Fun>& seeds);

}  // namespace cwerg
