// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/disassembler.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <stdio.h>
#include <cstring>
#include <string_view>

namespace cwerg {
namespace a32 {

const char* kArmRegNames[] = {                       //
    "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",  //
    "r8", "r9", "sl", "fp", "ip", "sp", "lr", "pc"};

const constexpr std::string_view kNumZero("#0");

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

char* RenderOperandSystematic(char* buffer, int32_t x, OK ok) {
  switch (ok) {
    case OK::PRED_28_31:
      return strappend(buffer, EnumToString(PRED(x)));
    case OK::REG_0_3:
    case OK::REG_12_15:
    case OK::REG_16_19:
    case OK::REG_8_11:
    case OK::REG_PAIR_12_15:
      ASSERT(x <= 15, "REG out of range " << x);
      return strappend(buffer, kArmRegNames[x]);
    case OK::DREG_0_3_5:
    case OK::DREG_12_15_22:
    case OK::DREG_16_19_7:
      ASSERT(x <= 15, " DREG out of range " << x);
      *buffer++ = 'd';
      return strappenddec(buffer, x);
    case OK::SREG_0_3_5:
    case OK::SREG_12_15_22:
    case OK::SREG_16_19_7:
      ASSERT(x <= 31, "SREG out of range " << x);
      *buffer++ = 's';
      return strappenddec(buffer, x);
    case OK::IMM_0_11:
    case OK::IMM_0_11_16_19:
    case OK::IMM_0_3_8_11:
    case OK::IMM_0_7_8_11:
    case OK::IMM_0_7_TIMES_4:
    case OK::IMM_10_11_TIMES_8:
    case OK::IMM_7_11:
    case OK::IMM_0_23:
    case OK::IMM_FLT_ZERO:
      sprintf(buffer, "%u", (uint32_t)x);
      return buffer + strlen(buffer);
    case OK::SIMM_0_23:
      return strappenddec(buffer, x);
    case OK::REG_RANGE_0_7:
    case OK::REG_RANGE_1_7:
      buffer = strappend(buffer, "regrange:");
      return strappenddec(buffer, x);
    case OK::REGLIST_0_15:
      sprintf(buffer, "reglist:0x%04x", x);
      return buffer + strlen(buffer);
    case OK::SHIFT_MODE_5_6:
      return  strappend(buffer, EnumToString(SHIFT(x)));
    case OK::Invalid:
    default:
      ASSERT(false, "unhandled OK: " << (unsigned)ok);
      return buffer;
  }
}

// render a single operand, e.g. and address like  `[r3, #-116]`
// Used to sanity check against objdump output
char* RenderOperandStd(char* buffer, const Opcode& opcode, int32_t x, OK ok) {
  switch (ok) {
    case OK::REG_0_3:
      if (opcode.classes & OPC_FLAG::ADDR_DEC) *buffer++ = '-';
      // FALL-THROUGH
    case OK::REG_12_15:
    case OK::REG_16_19:
    case OK::REG_8_11:
    case OK::REG_PAIR_12_15:
    case OK::DREG_0_3_5:
    case OK::DREG_12_15_22:
    case OK::DREG_16_19_7:
    case OK::SREG_0_3_5:
    case OK::SREG_12_15_22:
    case OK::SREG_16_19_7:
    //
    case OK::PRED_28_31:
    case OK::SHIFT_MODE_5_6:
      return RenderOperandSystematic(buffer, x, ok);
    case OK::IMM_0_7_TIMES_4:
    case OK::IMM_0_11:
    case OK::IMM_0_3_8_11:
      *buffer++ = '#';
      if (opcode.classes & OPC_FLAG::ADDR_DEC) {
        *buffer++ = '-';
      }
      return strappenddec(buffer, x);
    case OK::IMM_0_11_16_19:
    case OK::IMM_0_7_8_11:
    case OK::IMM_10_11_TIMES_8:
    case OK::IMM_7_11:
    case OK::IMM_0_23:
    case OK::IMM_FLT_ZERO:
    case OK::SIMM_0_23:
    case OK::REG_RANGE_0_7:
    case OK::REG_RANGE_1_7:
      *buffer++ = '#';
      return strappenddec(buffer, x);
    case OK::REGLIST_0_15: {
      const char* sep = "";
      buffer = strappend(buffer, "{");
      for (int i = 0; i < 16; ++i) {
        if (x & (1 << i)) {
          buffer = strappend(buffer, sep);
          buffer = strappend(buffer, kArmRegNames[i]);
          sep = ", ";
        }
      }
      buffer = strappend(buffer, "}");
    }
      return buffer;
    case OK::Invalid:
    default:
      ASSERT(false, "Invalid");
      return buffer;
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
      buffer = RenderOperandSystematic(buffer, ins.operands[i],
                                       ins.opcode->fields[i]);
    }
    sep = " ";
  }
}

}  // namespace a32
}  // namespace cwerg
