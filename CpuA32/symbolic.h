#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <optional>
#include <string_view>
#include <vector>
#include "CpuA32/opcode_gen.h"

namespace cwerg::a32 {

extern char* SymbolizeOperand(char* buffer, int32_t x, OK ok);

extern void RenderInsSystematic(const Ins& ins, char buffer[512]);

extern bool InsParse(const std::vector<std::string_view>& token, Ins* ins);

extern std::string SymbolizeRegListMask(uint32_t mask);

extern std::string SymbolizeRegRange(uint32_t start_reg_no,
                                     uint32_t count,
                                     bool single);
}  // namespace cwerg::a32
