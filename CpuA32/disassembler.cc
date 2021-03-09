// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/disassembler.h"
#include "Util/assert.h"

#include <stdio.h>
#include <cstring>
#include <string_view>

namespace cwerg {
namespace a32 {

const char* kPredicates[] = {                        //
    "eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",  //
    "hi", "ls", "ge", "lt", "gt", "le", "al", "@@"};

const char* kArmRegNames[] = {                       //
    "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",  //
    "r8", "r9", "sl", "fp", "ip", "sp", "lr", "pc"};

const char* kShiftKindsWithComma[] = {  //
    ", lsl", ", lsr", ", asr", ", ror"};
const char* kShiftKindsZeroWithComma[] = {  //
    "", ", lsr #32", ", asr #32", ", rrx"};

const constexpr std::string_view kNumZero("#0");

// TODO: stop using printf and realted cruft from <cstring>

char* strappend(char* dst, const char* src) {
  strcpy(dst, src);
  return dst + strlen(dst);
}

char* strappend(char* dst, std::string_view src) {
  memcpy(dst, src.data(), src.size());
  dst[src.size()] = 0;
  return dst + src.size();
}

unsigned RenderName(const Ins& ins, char* buffer) {
  unsigned start = 0;
  int pred_bits = 14;
  if (ins.opcode->num_fields > 0 && ins.opcode->fields[0] == OK::PRED_28_31) {
    pred_bits = ins.operands[0];
    start = 1;
  }

  buffer = strappend(buffer, ins.opcode->name);
  if (pred_bits != 14) strcpy(buffer, kPredicates[pred_bits]);
  return start;
}

int RenderMultipleVFP(const char* reg_prefix,
                      int32_t start_reg,
                      int32_t count,
                      char* buffer) {
  ASSERT(count > 0, "");
  if (count == 1) {
    sprintf(buffer, "{%s%d}", reg_prefix, start_reg);
  } else {
    sprintf(buffer, "{%s%d-%s%d}", reg_prefix, start_reg, reg_prefix,
            start_reg + count - 1);
  }
  return 1;
}

void RenderOperandSystematic(char* buffer, const Ins& ins, unsigned pos) {
  const int32_t x = ins.operands[pos];
  const OK kind = ins.opcode->fields[pos];
  switch (kind) {
    case OK::PRED_28_31:
      strcpy(buffer, EnumToString(PRED(x)));
      return;
    case OK::REG_LINK:
      strcpy(buffer, kArmRegNames[14]);
      return;
    case OK::REG_0_3:
    case OK::REG_12_15:
    case OK::REG_16_19:
    case OK::REG_BASE_16_19:
    case OK::REG_8_11:
    case OK::REG_PAIR_12_15:
      ASSERT(x <= 15, "REG out of range " << x);
      strcpy(buffer, kArmRegNames[x]);
      return;
    case OK::DREG_0_3_5:
    case OK::DREG_12_15_22:
    case OK::DREG_16_19_7:
      ASSERT(x <= 15, " DREG out of range " << x);
      sprintf(buffer, "d%d", x);
      return;
    case OK::SREG_0_3_5:
    case OK::SREG_12_15_22:
    case OK::SREG_16_19_7:
      ASSERT(x <= 31, "SREG out of range " << x);
      sprintf(buffer, "s%d", x);
      return;
    case OK::IMM_0_11:
    case OK::IMM_0_11_16_19:
    case OK::IMM_0_3_8_11:
    case OK::IMM_0_7_8_11:
    case OK::IMM_0_7_times4:
    case OK::IMM_10_11:
    case OK::IMM_7_11:
    case OK::IMM_0_23:
    case OK::IMM_ZERO:
      sprintf(buffer, "%u", (uint32_t)x);
      return;
    case OK::SIMM_0_23:
      sprintf(buffer, "%d", x);
      return;
    case OK::REG_RANGE_0_7:
    case OK::REG_RANGE_1_7:
      sprintf(buffer, "regrange:%d", x);
      return;
    case OK::REGLIST_0_15:
      sprintf(buffer, "reglist:0x%04x", x);
      return;
    case OK::SHIFT_MODE_5_6:
    case OK::SHIFT_MODE_5_6_ADDR:
    case OK::SHIFT_MODE_ROT:
      strcpy(buffer, EnumToString(SHIFT(x)));
      return;
    case OK::Invalid:
    default:
      ASSERT(false, "unreachable");
      return;
  }
}

// forward declaration because of mutual recursion
unsigned RenderOperandStd(char* buffer, const Ins& ins, unsigned pos);

unsigned RenderOffsetStd(char* buffer, const Ins& ins, unsigned pos) {
  char* orig = buffer;
  strcat(buffer, " ,");
  buffer += strlen(buffer);
  if (ins.opcode->classes & OPC_FLAG::ADDR_INC) {
    pos = RenderOperandStd(buffer, ins, pos);
    if (0 == strcmp("#0", buffer)) orig[0] = 0;
    return pos;
  }

  strcat(buffer, "-");
  pos = RenderOperandStd(buffer + 1, ins, pos);
  if (0 == strcmp("#0", buffer + 1)) {
    orig[0] = 0;
    return pos;
  }

  if (buffer[1] == '#') {
    buffer[0] = '#';
    buffer[1] = '-';
  }
  return pos;
}

// render a single operand, e.g. and address like  `[r3, #-116]`
unsigned RenderOperandStd(char* buffer, const Ins& ins, unsigned pos) {
  const int32_t x = ins.operands[pos];
  const OK kind = ins.opcode->fields[pos];
  ++pos;
  //   printf("@@ processing kind: %d %d\n", kind, x);
  switch (kind) {
    case OK::REG_LINK:
    case OK::PRED_28_31:
      // no output
      return pos;
    case OK::REG_0_3:
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
      RenderOperandSystematic(buffer, ins, pos - 1);
      return pos;
    case OK::IMM_0_11:
    case OK::IMM_0_11_16_19:
    case OK::IMM_0_3_8_11:
    case OK::IMM_0_7_8_11:
    case OK::IMM_0_7_times4:
    case OK::IMM_10_11:
    case OK::IMM_7_11:
    case OK::IMM_0_23:
    case OK::IMM_ZERO:
    case OK::SIMM_0_23:
      sprintf(buffer, "#%d", x);
      return pos;
    case OK::SHIFT_MODE_5_6: {
      pos = RenderOperandStd(buffer, ins, pos);
      buffer += strlen(buffer);
      char* save = buffer;
      buffer = strappend(buffer, kShiftKindsWithComma[x]);
      buffer = strappend(buffer, " ");
      pos = RenderOperandStd(buffer, ins, pos);
      if (buffer == kNumZero) {
        *save = 0;
      }
      return pos;
    }
    case OK::SHIFT_MODE_5_6_ADDR: {
      pos = RenderOperandStd(buffer, ins, pos);
      buffer += strlen(buffer);
      char amount[128];
      pos = RenderOperandStd(amount, ins, pos);
      if (amount != kNumZero) {
        buffer = strappend(buffer, kShiftKindsWithComma[x]);
        buffer = strappend(buffer, " ");
        buffer = strappend(buffer, amount);
      } else {
        buffer = strappend(buffer, kShiftKindsZeroWithComma[x]);
      }
      return pos;
    }
    case OK::SHIFT_MODE_ROT: {
      pos = RenderOperandStd(buffer, ins, pos);
      buffer += strlen(buffer);
      char* save = buffer;
      buffer = strappend(buffer, ", ");
      pos = RenderOperandStd(buffer, ins, pos);
      if (buffer == kNumZero) {
        *save = 0;
      }
      return pos;
    }
    case OK::REG_BASE_16_19: {
      if (ins.opcode->classes & OPC_FLAG::MULTIPLE) {
        RenderOperandSystematic(buffer, ins, pos - 1);
        if (ins.opcode->classes & OPC_FLAG::ADDR_UPDATE) {
          strcat(buffer, "!");
        }
        return pos;
      }
      buffer[0] = '[';
      RenderOperandSystematic(buffer + 1, ins, pos - 1);
      if (ins.opcode->classes & (OPC_FLAG::ADDR_INC | OPC_FLAG::ADDR_DEC)) {
        if (ins.opcode->classes & OPC_FLAG::ADDR_PRE) {
          buffer += strlen(buffer);
          pos = RenderOffsetStd(buffer, ins, pos);
          strcat(buffer, "]");
          if (ins.opcode->classes & OPC_FLAG::ADDR_UPDATE) {
            strcat(buffer, "!");
          }
        } else {
          ASSERT(ins.opcode->classes & OPC_FLAG::ADDR_POST,
                 "unexpected addr mode " << ins.opcode->name);
          strcat(buffer, "]");
          buffer += strlen(buffer);
          pos = RenderOffsetStd(buffer, ins, pos);
        }
      } else {
        strcat(buffer, "]");
      }
      return pos;
    }
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
      return pos;
    case OK::REG_RANGE_0_7:
    case OK::REG_RANGE_1_7: {
      char reg[128];
      pos = RenderOperandStd(reg, ins, pos);
      if (x == 1) {
        sprintf(buffer, "{%s}", reg);
      } else {
        int32_t reg_last = atoi(reg + 1) + x - 1;
        sprintf(buffer, "{%s-%c%d}", reg, reg[0], reg_last);
      }
    }
      return pos;
    case OK::Invalid:
    default:
      ASSERT(false, "Invalid");
      return pos;
  }
}

int FirstOperandIsLast(const struct Opcode* opcode) {
  return ((opcode->classes & (STORE | MULTIPLE | ATOMIC)) == STORE) ||
         ((opcode->classes & (LOAD | MULTIPLE)) == (LOAD | MULTIPLE));
}

// Render the given instruction using standard assembler notation into `buffer`
// Note: not production quality - does not check for buffer overruns.
void RenderInsStd(const Ins& ins, char buffer[128]) {
  unsigned i = RenderName(ins, buffer);
  buffer += strlen(buffer);
  buffer = strappend(buffer, " ");

  // Move some operands to the end to be compatible with regular assemblers
  char suffix[128];
  if (FirstOperandIsLast(ins.opcode)) {
    strcpy(suffix, ", ");
    i = RenderOperandStd(suffix + 2, ins, i);
  } else {
    suffix[0] = 0;
  }

  if (ins.opcode == &OpcodeTable[unsigned(OPC::vmrs_APSR_nzcv_fpscr)]) {
    buffer = strappend(buffer, " APSR_nzcv, fpscr");
  }

  const char* sep = "";
  while (i < ins.opcode->num_fields) {
    buffer = strappend(buffer, sep);
    i = RenderOperandStd(buffer, ins, i);
    buffer += strlen(buffer);
    sep = ", ";
  }
  strcat(buffer, suffix);
}

// Render the given instruction using a systematic notation into `buffer`
void RenderInsSystematic(const Ins& ins, char buffer[128]) {
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
        sprintf(buffer, ":%d", ins.operands[i]);
        buffer += strlen(buffer);
      }
    } else {
      RenderOperandSystematic(buffer, ins, i);
      buffer += strlen(buffer);
    }
    sep = " ";
  }
}

}  // namespace a32
}  // namespace cwerg
