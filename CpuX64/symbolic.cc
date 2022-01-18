
#include "CpuX64/symbolic.h"
#include <cstring>
#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::x64 {
using namespace cwerg;

const char Regnames8[][8] = {
    "al",  "cl",  "dl",   "bl",   "spl",  "bpl",  "sil",  "dil",  //
    "r8b", "r9b", "r10b", "r11b", "r12b", "r13b", "r14b", "r15b"};

const char Regnames16[][8] = {
    "ax",  "cx",  "dx",   "bx",   "sp",   "bp",   "si",   "di",  //
    "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w"};

const char Regnames32[][8] = {
    "eax", "ecx", "edx",  "ebx",  "esp",  "ebp",  "esi",  "edi",  //
    "r8d", "r9d", "r10d", "r11d", "r12d", "r13d", "r14d", "r15d"};

const char Regnames64[][8] = {
    "rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi",  //
    "r8",  "r9",  "r10", "r11", "r12", "r13", "r14", "r15"};

const char XRegnames[][8] = {
    "xmm0", "xmm1", "xmm2",  "xmm3",  "xmm4",  "xmm5",  "xmm6",  "xmm7",  //
    "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15"};

const char* SymbolizeOperand(char* buf,
                             int64_t val,
                             OK ok,
                             bool show_implicits,
                             bool objdump_compat) {
  switch (ok) {
    case OK::IMPLICIT_AL:
      return show_implicits ? "al" : nullptr;
    case OK::IMPLICIT_AX:
      return show_implicits ? "ax" : nullptr;
    case OK::IMPLICIT_EAX:
      return show_implicits ? "eax" : nullptr;
    case OK::IMPLICIT_RAX:
      return show_implicits ? "rax" : nullptr;
    case OK::IMPLICIT_DX:
      return show_implicits ? "dx" : nullptr;
    case OK::IMPLICIT_EDX:
      return show_implicits ? "edx" : nullptr;
    case OK::IMPLICIT_RDX:
      return show_implicits ? "rdx" : nullptr;
    case OK::IMPLICIT_CL:
      return show_implicits ? "cl" : nullptr;
    case OK::IMPLICIT_1:
      return show_implicits ? "1" : nullptr;
    case OK::MODRM_RM_XREG32:
    case OK::MODRM_RM_XREG64:
    case OK::MODRM_RM_XREG128:
    case OK::MODRM_XREG32:
    case OK::MODRM_XREG64:
    case OK::MODRM_XREG128:
      if (show_implicits)
        return XRegnames[val];
      else
        return 0;
    case OK::MODRM_RM_REG8:
    case OK::MODRM_REG8:
    case OK::BYTE_WITH_REG8:
      return Regnames8[val];
    case OK::MODRM_RM_REG16:
    case OK::MODRM_REG16:
    case OK::BYTE_WITH_REG16:
      return Regnames16[val];
    case OK::MODRM_RM_REG32:
    case OK::MODRM_REG32:
    case OK::BYTE_WITH_REG32:
      return Regnames32[val];
    case OK::MODRM_RM_REG64:
    case OK::MODRM_REG64:
    case OK::BYTE_WITH_REG64:
    case OK::MODRM_RM_BASE:
    case OK::SIB_BASE:
      return Regnames64[val];
    case OK::RIP_BASE:
      return "rip";
    case OK::SIB_INDEX_AS_BASE: {
      if (val == 4)
        return "nobase";
      else
        return Regnames64[val];
    }
    case OK::SIB_INDEX: {
      if (val == 4)
        return "noindex";
      else
        return Regnames64[val];
    }
    case OK::SIB_SCALE:
      if (objdump_compat) {
        ToDecSignedString(1 << val, buf);
      } else {
        ToDecSignedString(val, buf);
      }
      return buf;
    case OK::OFFPCREL8:
    case OK::OFFPCREL32:
    case OK::OFFABS8:
    case OK::OFFABS32:
      if (objdump_compat) {
        if (val >= 0) {
          buf[0] = '0';
          buf[1] = 'x';
          ToHexString(val, buf + 2);
        } else {
          buf[0] = '-';
          buf[1] = '0';
          buf[2] = 'x';
          ToHexString(-val, buf + 3);
        }
      } else {
        ToDecSignedString(val, buf);
      }
      return buf;
    case OK::IMM8:
    case OK::IMM16:
    case OK::IMM32:
    case OK::IMM8_16:
    case OK::IMM8_32:
    case OK::IMM8_64:
    case OK::IMM32_64:
    case OK::IMM64:
      buf[0] = '0';
      buf[1] = 'x';
      ToHexString(val, buf + 2);
      return buf;
  }
  ASSERT(false, "");
  return "";
}

#if 0
void SymbolizeReloc(char* cp, const Ins& ins, uint32_t addend) {
  cp = strappend(cp, "expr:");
  switch (ins.reloc_kind) {
    case elf::RELOC_TYPE_AARCH64::JUMP26:
      ASSERT(ins.is_local_sym, "");
      cp = strappend(cp, "jump26:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::ADR_PREL_PG_HI21:
      cp = strappend(cp, ins.is_local_sym ? "loc_adr_prel_pg_hi21:": "adr_prel_pg_hi21:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::ADD_ABS_LO12_NC:
      cp = strappend(cp, ins.is_local_sym ? "loc_add_abs_lo12_nc:": "add_abs_lo12_nc:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::CALL26:
      cp = strappend(cp, "call26:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::CONDBR19:
      ASSERT(ins.is_local_sym, "");
      cp = strappend(cp, "condbr19:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    default:
      ASSERT(false, "");
  }
  if (addend != 0) {
    *cp++ = ':';
    cp = strappenddec(cp, addend);
  }
}
#endif

std::string_view InsSymbolize(const x64::Ins& ins,
                              bool show_implicits,
                              bool objdump_compat,
                              std::vector<std::string>* ops) {
  bool skip_next = false;
  char buffer[128];
  const char* s;
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    const OK ok = ins.opcode->fields[i];
    if (skip_next) {
      skip_next = false;
      continue;
    }

    if (objdump_compat && ok == OK::SIB_INDEX && ins.operands[i] == 4) {
      skip_next = true;
      continue;
    }

    if (objdump_compat && (ok == OK::MODRM_RM_BASE || ok == OK::RIP_BASE ||
                           ok == OK::SIB_BASE || ok == OK::SIB_INDEX_AS_BASE)) {
      if (ins.opcode->mem_width_log > 0) {
        buffer[0] = 'M';
        buffer[1] = 'E';
        buffer[2] = 'M';
        ToDecString(4 << ins.opcode->mem_width_log, buffer + 3);
        ops->emplace_back(buffer);
      }
    }

    if (ins.has_reloc() && i == ins.reloc_pos) {
      ASSERT(false, "NYI");
      // SymbolizeReloc(buffer, ins, ins.operands[i]);
    } else {
      s = SymbolizeOperand(buffer, ins.operands[i], ok, show_implicits,
                           objdump_compat);
      if (s == nullptr) continue;
    }
    ops->emplace_back(s);
  }
  return OpcodeName(ins.opcode);
}

}  // namespace cwerg::x64
