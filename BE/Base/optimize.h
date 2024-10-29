#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/ir.h"
#include "BE/Base/reg_stats.h"

namespace cwerg::base {

extern void FunCfgInit(Fun fun);

extern void FunCfgExit(Fun fun);

extern void FunOptBasic(Fun fun, bool allow_conv_conversions);

extern void FunOpt(Fun fun, const DK_MAP& rk_map);

}  // namespace cwerg::base
