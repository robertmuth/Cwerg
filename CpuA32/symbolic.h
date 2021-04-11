#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <optional>
#include <string_view>
#include <vector>
#include "CpuA32/opcode_gen.h"

namespace cwerg::a32 {

extern void RenderInsSystematic(const Ins& ins, char buffer[512]);

extern std::string_view InsSymbolize(const Ins& ins, std::vector<std::string>* ops);

extern bool InsFromSymbolized(const std::vector<std::string_view>& token, Ins* ins);

extern std::string SymbolizeRegListMask(uint32_t mask);

extern std::string SymbolizeRegRange(uint32_t start_reg_no,
                                     uint32_t count,
                                     bool single);
}  // namespace cwerg::a32
