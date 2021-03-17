#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/opcode_gen.h"

namespace cwerg::a32 {

extern char* RenderOperandStd(char* buffer, const Opcode& opcode, int32_t x, OK ok);

extern char* RenderOperandSystematic(char* buffer, int32_t x, OK ok);

extern void RenderInsSystematic(const Ins& ins, char buffer[512]);

}  // namespace cwerg::a32
