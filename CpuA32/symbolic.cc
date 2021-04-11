// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"
#include "Elf/elfhelper.h"

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

bool has_prefix(std::string_view name, std::string_view prefix) {
  return name.substr(0, prefix.size()) == prefix;
}

std::optional<uint32_t> UnsymbolizeOperand(OK ok, std::string_view s) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  if (!fi.prefix.empty() && has_prefix(s, fi.prefix)) {
    s.remove_prefix(fi.prefix.size());
  } else if (s == "r10")
    s = "sl";
  else if (s == "r11")
    s = "fp";
  else if (s == "r12")
    s = "ip";

  switch (fi.kind) {
    default:
    case FK::NONE:
      ASSERT(false, "unreachable");
      return std::nullopt;
    case FK::INT_SIGNED:
    case FK::INT_SIGNED_CUSTOM:
      return ParseInt<uint32_t>(s);
    case FK::FLT_CUSTOM:
      if (s != "0.0" && s != ".0" && s != "0") return std::nullopt;
      return 0;
    case FK::LIST:
      for (unsigned i = 0; i < fi.num_names; ++i) {
        if (s == fi.names[i]) return i;
      }
      return std::nullopt;
    case FK::INT:
    case FK::INT_HEX:
      return ParseInt<uint32_t>(s);
  }
}



bool HandleRelocation(std::string_view expr, unsigned pos, Ins* ins) {
  ins->reloc_pos = pos;
  const size_t colon_sym = expr.find(':');
  if (colon_sym == std::string_view::npos) return false;
  const std::string_view kind_name = expr.substr(0, colon_sym);
  elf::RELOC_TYPE_ARM rel_type;
  if (kind_name == "abs32") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::ABS32;
  } else if (kind_name == "jump24") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::JUMP24;
    ins->is_local_sym = true;
  } else if (kind_name == "call") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::CALL;
  } else if (kind_name == "movw_abs_nc") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::MOVW_ABS_NC;
  } else if (kind_name == "movt_abs") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::MOVT_ABS;
  } else if (kind_name == "loc_movw_abs_nc") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::MOVW_ABS_NC;
    ins->is_local_sym = true;
  } else if (kind_name == "loc_movt_abs") {
    ins->reloc_kind = elf::RELOC_TYPE_ARM::MOVT_ABS;
    ins->is_local_sym = true;
  } else {
    return false;
  }
  //
  std::string_view rest = expr.substr(colon_sym + 1);
  const size_t colon_addend = rest.find(':');
  ins->reloc_symbol = rest.substr(0, colon_addend);

  ins->operands[pos] = 0;
  if (colon_addend != std::string_view::npos) {
    auto val = ParseInt<int32_t>(rest.substr(colon_addend + 1));
    if (!val.has_value()) return false;
    ins->operands[pos] = val.value();
  }
  return true;
}

bool InsParse(const std::vector<std::string_view>& token, Ins* ins) {
  ins->opcode = FindOpcodeForMnemonic(token[0]);
  if (ins->opcode == nullptr) {
    std::cerr << "unknown opcode " << token[0] << "\n";
    return false;
  }
  uint32_t operand_count = 0;
  if (token.size() == ins->opcode->num_fields) {
    ins->operands[operand_count++] = 14;  // predicate 'al'
  }
  ASSERT(token.size() - 1 + operand_count == ins->opcode->num_fields, "");
  for (unsigned i = 1; i < token.size(); ++i, ++operand_count) {
    if (token[i].substr(0, 5) == "expr:") {
      if (!HandleRelocation(token[i].substr(5), operand_count, ins)) {
        std::cerr << "malformed relocation expression " << token[i] << "\n";
        return false;
      }
    } else {
      auto val = UnsymbolizeOperand(ins->opcode->fields[operand_count], token[i]);
      if (!val.has_value()) {
        std::cerr << "cannot parse " << token[i] << "\n";
        return false;
      }
      ins->operands[operand_count] = val.value();
    }
  }
  return true;
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
