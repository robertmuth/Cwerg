#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"

namespace cwerg::base {

extern void BblCheck(Bbl bbl, Fun fun);

extern void FunCheck(Fun fun);

extern void UnitCheck(Unit unit);

}  // namespace cwerg::base
