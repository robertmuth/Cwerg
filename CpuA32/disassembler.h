#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/opcode_gen.h"

namespace cwerg::a32 {

void RenderInsStd(const Ins& ins, char buffer[128]);
void RenderInsSystematic(const Ins& ins, char buffer[128]);

}  // namespace cwerg::a32
