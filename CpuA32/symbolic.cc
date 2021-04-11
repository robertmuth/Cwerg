// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <cstring>
#include <map>
#include <string_view>

namespace cwerg {
namespace a32 {

// TODO: stop using printf and realted cruft from <cstring>

char* strappend(char* dst, const char* src) {
  strcpy(dst, src);
  return dst + strlen(dst);
}

char* strappenddec(char* dst, int64_t n) {
  if (n >= 0) {
    ToDecString(n, dst);
  } else {
    *dst++ = '-';
    ToDecString(-n, dst);
  }
  return dst + strlen(dst);
}

char* strappendhex(char* dst, int64_t n) {
  ToHexString(n, dst);
  return dst + strlen(dst);
}

char* strappend(char* dst, std::string_view src) {
  memcpy(dst, src.data(), src.size());
  dst[src.size()] = 0;
  return dst + src.size();
}



char* SymbolizeOperand(char* buffer, int32_t x, OK ok) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  switch (fi.kind) {
    default:
    case FK::NONE:
      ASSERT(false, "unreachable");
      return 0;
    case FK::INT_SIGNED_CUSTOM:
      return strappenddec(buffer, x);
    case FK::FLT_CUSTOM:
      ASSERT(x == 0, "");
      return strappend(buffer, "0.0");
    case FK::LIST:
      ASSERT(x < fi.num_names, "");
      return strappend(buffer, fi.names[x]);
    case FK::INT_SIGNED:
      return strappenddec(buffer, x);
    case FK::INT:
      buffer = strappend(buffer, fi.prefix);
      return strappenddec(buffer, x);
    case FK::INT_HEX:
      buffer = strappend(buffer, fi.prefix);
      buffer = strappend(buffer, "0x");
      return strappendhex(buffer, x);
  }
}

// Render the given instruction using a systematic notation into `buffer`
void RenderInsSystematic(const Ins& ins, char buffer[512]) {
  buffer = strappend(buffer, ins.opcode->enum_name);
  buffer = strappend(buffer, " ");

  const char* sep = "";
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    buffer = strappend(buffer, sep);
    if (ins.reloc_kind != elf::RELOC_TYPE_ARM::NONE && i == ins.reloc_pos) {
      switch (ins.reloc_kind) {
        case elf::RELOC_TYPE_ARM::JUMP24:
          ASSERT(ins.is_local_sym, "");
          buffer = strappend(buffer, "expr:jump24:");
          buffer = strappend(buffer, ins.reloc_symbol);
          break;
        case elf::RELOC_TYPE_ARM::CALL:
          buffer = strappend(buffer, "expr:call:");
          buffer = strappend(buffer, ins.reloc_symbol);
          break;
        case elf::RELOC_TYPE_ARM::MOVT_ABS:
          buffer = strappend(buffer, ins.is_local_sym ? "expr:loc_movt_abs:"
                                                      : "expr:movt_abs:");
          buffer = strappend(buffer, ins.reloc_symbol);
          break;
        case elf::RELOC_TYPE_ARM::MOVW_ABS_NC:
          buffer = strappend(buffer, ins.is_local_sym ? "expr:loc_movw_abs_nc:"
                                                      : "expr:movw_abs_nc:");
          buffer = strappend(buffer, ins.reloc_symbol);

          break;
        default:
          ASSERT(false, "");
      }
      if (ins.operands[i] != 0) {
        *buffer++ = ':';
        buffer = strappenddec(buffer, ins.operands[i]);
      }
    } else {
      buffer = SymbolizeOperand(buffer, ins.operands[i], ins.opcode->fields[i]);
    }
    sep = " ";
  }
}

// clang-format off
// @formatter:off
std::map<std::string_view, uint32_t> operand_symbols = {
    {"eq", 0}, {"ne", 1}, {"cs", 2}, {"cc", 3},
    {"mi", 4}, {"pl", 5}, {"vs", 6}, {"vc", 7},
    {"hi", 8},   {"ls", 9}, {"ge", 10}, {"lt", 11},
    {"gt", 12}, {"le", 13},  {"al", 14},
     //
    {"r0", 0},  {"r1", 1}, {"r2", 2}, {"r3", 3},
    {"r4", 4}, {"r5", 5}, {"r6", 6}, {"r7", 7},
    {"r8", 8}, {"r9", 9}, {"r10", 10}, {"r11", 11},
    {"r12", 12}, {"r13", 13}, {"r14", 14}, {"r15", 15},
    //
    {"sl", 10}, {"fp", 11},
    {"ip", 12}, {"sp", 13}, {"lr", 14}, {"pc", 15},
    //
    {"s0", 0}, {"s1", 1}, {"s2", 2}, {"s3", 3},
    {"s4", 4}, {"s5", 5}, {"s6", 6}, {"s7", 7},
    {"s8", 8}, {"s9", 9}, {"s10", 10}, {"s11", 11},
    {"s12", 12}, {"s13", 13}, {"s14", 14}, {"s15", 15},
    //
    {"s16", 16}, {"s17", 17}, {"s18", 18}, {"s19", 19},
    {"s20", 20}, {"s21", 21}, {"s22", 22}, {"s23", 23},
    {"s24", 24}, {"s25", 25}, {"s26", 26}, {"s27", 27},
    {"s28", 28}, {"s29", 29}, {"s30", 30}, {"s31", 31},
    //
    {"d0", 0}, {"d1", 1}, {"d2", 2}, {"d3", 3},
    {"d4", 4}, {"d5", 5}, {"d6", 6}, {"d7", 7},
    {"d8", 8}, {"d9", 9}, {"d10", 10}, {"d11", 11},
    {"d12", 12}, {"d13", 13}, {"d14", 14}, {"d15", 15},
    //
    {"lsl",  0}, {"lsr", 1}, {"asr", 2}, {"ror_rrx", 3},
};
// @formatter:on
// clang-format on

std::optional<uint32_t> UnsymbolizeOperand(OK ok, std::string_view s) {
  size_t colon_pos = s.find(':');
  if (colon_pos == std::string_view::npos) {
    auto it = operand_symbols.find(s);
    if (it != operand_symbols.end()) {
      return it->second;
    }
    return ParseInt<uint32_t>(s);
  }
  std::string_view num({s.data() + colon_pos + 1, s.size() - colon_pos - 1});
  return ParseInt<uint32_t>(num);
}

std::string SymbolizeRegListMask(uint32_t mask) {
  std::string regs = "{";
  std::string_view sep;
  for (unsigned int i = 0; i < 16; ++i) {
    if (mask & (1 << i)) {
      regs += sep;
      regs += EnumToString(a32::REG(i));
      sep = ", ";
    }
  }
  regs += "}";
  return regs;
}

std::string SymbolizeRegRange(uint32_t start_reg_no,
                              uint32_t count,
                              bool single) {
  ASSERT(count > 0, "");
  std::string_view start_reg = single ? EnumToString(a32::SREG(start_reg_no))
                                      : EnumToString(a32::DREG(start_reg_no));
  std::string out = "{";
  out += start_reg;
  if (count > 1) {
    uint32_t end_reg_no = start_reg_no + count - 1;
    std::string_view end_reg = single ? EnumToString(a32::SREG(end_reg_no))
                                      : EnumToString(a32::DREG(end_reg_no));
    out += "-";
    out += end_reg;
  }
  return out + "}";
}

}  // namespace a32
}  // namespace cwerg
