// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <stdio.h>
#include <cstring>
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

int RenderMultipleVFP(const char* reg_prefix,
                      int32_t start_reg,
                      int32_t count,
                      char* buffer) {
  ASSERT(count > 0, "");
  if (count == 1) {
    buffer = strappend(buffer, "{");
    buffer = strappend(buffer, reg_prefix);
    buffer = strappenddec(buffer, start_reg);
    buffer = strappend(buffer, "}");
  } else {
    sprintf(buffer, "{%s%d-%s%d}", reg_prefix, start_reg, reg_prefix,
            start_reg + count - 1);
  }
  return 1;
}

char* RenderOperand(char* buffer, int32_t x, OK ok) {
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
      buffer = RenderOperand(buffer, ins.operands[i], ins.opcode->fields[i]);
    }
    sep = " ";
  }
}

}  // namespace a32
}  // namespace cwerg
