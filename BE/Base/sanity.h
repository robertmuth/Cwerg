#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/ir.h"

namespace cwerg::base {

extern void FunCheck(Fun fun, bool check_cfg, bool check_push_pop, bool check_fallthroughs);

}  // namespace cwerg::base
