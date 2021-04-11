#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/opcode_gen.h"
#include <string_view>
#include <optional>

namespace cwerg::a32 {



extern std::optional<uint32_t> UnsymbolizeOperand(OK ok, std::string_view s);

extern char* SymbolizeOperand(char* buffer, int32_t x, OK ok);

extern void RenderInsSystematic(const Ins& ins, char buffer[512]);

extern std::string SymbolizeRegListMask(uint32_t mask);

extern std::string SymbolizeRegListMask(uint32_t mask);

extern std::string SymbolizeRegRange(uint32_t start_reg_no,
                              uint32_t count,
                              bool single);
}  // namespace cwerg::a32
