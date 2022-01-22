// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <cstring>
#include <string_view>

namespace cwerg::a32 {
namespace {

char* strappenddec(char* dst, uint32_t n) {
  if (n <= 0x7fffffff) {
    return dst + ToDecString(n, dst).size();
  } else {
    *dst++ = '-';
    return dst + ToDecString(~n + 1, dst).size();
  }
}

char* strappendhex(char* dst, uint32_t n) {
  return dst + ToHexString(n, dst).size();
}

char* strappend(char* dst, std::string_view src) {
  std::memcpy(dst, src.data(), src.size());
  dst[src.size()] = 0;
  return dst + src.size();
}

char* SymbolizeOperand(char* buffer, uint32_t data, OK ok) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  const uint32_t x = a32::DecodeOperand(data, ok);
  switch (fi.kind) {
    default:
    case FK::NONE:
      ASSERT(false, "unreachable");
      return nullptr;
    case FK::INT_SIGNED_CUSTOM:
      return strappenddec(buffer, x);
    case FK::FLT_CUSTOM:
      ASSERT(x == 0, "");
      return strappend(buffer, "0.0");
    case FK::LIST:
      ASSERT(x < fi.num_names, "out of range for list " << x << " " << (int)ok);
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

bool has_prefix(std::string_view name, std::string_view prefix) {
  return name.substr(0, prefix.size()) == prefix;
}

uint32_t UnsymbolizeOperandString(const FieldInfo& fi, std::string_view s) {
  switch (fi.kind) {
    default:
    case FK::NONE:
      ASSERT(false, "unreachable");
      return kEncodeFailure;
    case FK::INT_SIGNED:
    case FK::INT_SIGNED_CUSTOM: {
      auto val = ParseInt<int32_t>(s);
      if (!val) return kEncodeFailure;
      return val.value();
    }
    case FK::FLT_CUSTOM:
      if (s != "0.0" && s != ".0" && s != "0") return kEncodeFailure;
      return 0;  // this is really the bit representation of float(0.0)
    case FK::LIST:
      for (unsigned i = 0; i < fi.num_names; ++i) {
        if (s == fi.names[i]) return i;
      }
      return kEncodeFailure;
    case FK::INT:
    case FK::INT_HEX: {
      auto val = ParseInt<uint32_t>(s);
      if (!val) return kEncodeFailure;
      return val.value();
    }
  }
}

uint32_t UnsymbolizeOperand(OK ok, std::string_view s) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  if (!fi.prefix.empty() && has_prefix(s, fi.prefix)) {
    s.remove_prefix(fi.prefix.size());
  } else if (s == "r10")
    s = "sl";
  else if (s == "r11")
    s = "fp";
  else if (s == "r12")
    s = "ip";

  return a32::EncodeOperand(UnsymbolizeOperandString(fi, s), ok);
}

const constexpr struct {
  std::string_view expr_kind;
  elf::RELOC_TYPE_ARM reloc_kind;
  bool local;
} kExprToReloc[] = {
    // order by frequency
    {"jump24", elf::RELOC_TYPE_ARM::JUMP24, true},
    {"call", elf::RELOC_TYPE_ARM::CALL, false},
    {"abs32", elf::RELOC_TYPE_ARM::ABS32, false},
    {"movw_abs_nc", elf::RELOC_TYPE_ARM::MOVW_ABS_NC, false},
    {"movt_abs", elf::RELOC_TYPE_ARM::MOVT_ABS, false},
    {"loc_movw_abs_nc", elf::RELOC_TYPE_ARM::MOVW_ABS_NC, true},
    {"loc_movt_abs", elf::RELOC_TYPE_ARM::MOVT_ABS, true},
};

bool HandleRelocation(std::string_view expr, unsigned pos, Ins* ins) {
  auto expr_op = ParseExpressionOp(expr);
  if (!expr_op) return false;
  ins->operands[pos] = expr_op->offset;
  for (const auto& x : kExprToReloc) {
    if (x.expr_kind == expr_op->reloc_name) {
      ins->set_reloc(x.reloc_kind, x.local, pos, expr_op->symbol_name);
      return true;
    }
  }
  return false;
}

void SymbolizeReloc(char* cp, const Ins& ins, uint32_t addend) {
  cp = strappend(cp, "expr:");
  switch (ins.reloc_kind) {
    case elf::RELOC_TYPE_ARM::JUMP24:
      ASSERT(ins.is_local_sym, "");
      cp = strappend(cp, "jump24:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_ARM::CALL:
      cp = strappend(cp, "call:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_ARM::MOVT_ABS:
      cp = strappend(cp, ins.is_local_sym ? "loc_movt_abs:" : "movt_abs:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_ARM::MOVW_ABS_NC:
      cp =
          strappend(cp, ins.is_local_sym ? "loc_movw_abs_nc:" : "movw_abs_nc:");
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

}  // namespace

std::string_view InsSymbolize(const Ins& ins, std::vector<std::string>* ops) {
  char buffer[128];
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    if (ins.has_reloc() && i == ins.reloc_pos) {
      SymbolizeReloc(buffer, ins, ins.operands[i]);
    } else {
      SymbolizeOperand(buffer, ins.operands[i], ins.opcode->fields[i]);
    }
    ops->emplace_back(buffer);
  }
  return ins.opcode->enum_name;
}

bool InsFromSymbolized(const std::vector<std::string_view>& token, Ins* ins) {
  ins->opcode = FindOpcodeForMnemonic(token[0]);
  if (ins->opcode == nullptr) {
    std::cerr << "unknown opcode " << token[0] << "\n";
    return false;
  }
  uint32_t operand_count = 0;
  // CodeGenA32 relies on this
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
      const OK ok = ins->opcode->fields[operand_count];
      auto val = UnsymbolizeOperand(ok, token[i]);
      if (val == kEncodeFailure) {
        std::cerr << "cannot parse " << token[i] << " "
                  << "\n";
        return false;
      }
      ins->operands[operand_count] = val;
    }
  }
  return true;
}

std::string SymbolizeRegListMask(uint32_t mask) {
  std::string regs = "{";
  std::string_view sep;
  for (unsigned int i = 0; i < 16; ++i) {
    if (mask & (1U << i)) {
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

}  // namespace cwerg::a32
