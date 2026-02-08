
#include "BE/CpuA64/symbolic.h"

#include <cstring>

#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::a64 {
using namespace cwerg;

char* strappend(char* dst, std::string_view src) {
  std::memcpy(dst, src.data(), src.size());
  dst[src.size()] = 0;
  return dst + src.size();
}

char* strappenddec(char* dst, int64_t n) {
  if (n >= 0) {
    return dst + ToDecString(n, dst).size();
  } else {
    *dst++ = '-';
    return dst + ToDecString(-n, dst).size();
  }
}

char* strappendhex(char* dst, int64_t n) {
  dst = strappend(dst, "0x");
  return dst + ToHexString(n, dst).size();
}

char* strappendflt(char* dst, double d) {
  return dst + ToFltString(d, dst).size();
}

double Flt64FromBits(uint64_t i) {
  union {
    uint64_t i;
    double d;
  } u = {i};
  return u.d;
}

uint64_t Flt64ToBits(double d) {
  union {
    double d;
    uint64_t i;
  } u = {d};
  return u.i;
}

char* SymbolizeOperand(char* buf, uint32_t data, OK ok) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  const uint64_t val = DecodeOperand(ok, data);
  switch (fi.kind) {
    default:
      ASSERT(false, "");
      return nullptr;
    case FK::LIST:
      return strappend(buf, fi.names[val]);
    case FK::FLT_CUSTOM: {
      return strappendflt(buf, Flt64FromBits(val));
    }
    case FK::INT_SIGNED:
    case FK::INT:  // TODO: add unsigned version
      return strappenddec(buf, (int64_t)val);
    case FK::INT_HEX_CUSTOM:
    case FK::INT_HEX:
      return strappendhex(buf, (int64_t)val);
  }
}

void SymbolizeReloc(char* cp, const Ins& ins, uint32_t addend) {
  cp = strappend(cp, "expr:");
  switch (ins.reloc_kind) {
    case elf::RELOC_TYPE_AARCH64::JUMP26:
      ASSERT(ins.is_local_sym, "");
      cp = strappend(cp, "jump26:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::ADR_PREL_PG_HI21:
      cp = strappend(
          cp, ins.is_local_sym ? "loc_adr_prel_pg_hi21:" : "adr_prel_pg_hi21:");
      cp = strappend(cp, ins.reloc_symbol);
      break;
    case elf::RELOC_TYPE_AARCH64::ADD_ABS_LO12_NC:
      cp = strappend(
          cp, ins.is_local_sym ? "loc_add_abs_lo12_nc:" : "add_abs_lo12_nc:");
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

std::string_view InsSymbolize(const a64::Ins& ins,
                              std::vector<std::string>* ops) {
  char buffer[128];
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    if (ins.has_reloc() && i == ins.reloc_pos) {
      SymbolizeReloc(buffer, ins, ins.operands[i]);
    } else {
      SymbolizeOperand(buffer, ins.operands[i], ins.opcode->fields[i]);
    }
    ops->emplace_back(buffer);
  }
  return ins.opcode->name;
}

uint32_t UnsymbolizeOperand(OK ok, std::string_view op) {
  const FieldInfo& fi = FieldInfoTable[uint8_t(ok)];
  uint64_t val;
  switch (fi.kind) {
    default:
      ASSERT(false, "");
      return kEncodeFailure;
    case FK::LIST:
      for (val = 0; val < fi.num_names; val++) {
        if (fi.names[val] == op) break;
      }
      if (val == fi.num_names) return kEncodeFailure;
      break;
    case FK::FLT_CUSTOM: {
      auto maybe = ParseReal(op);
      if (!maybe) return kEncodeFailure;
      val = Flt64ToBits(maybe.value());
      break;
    }
    case FK::INT_SIGNED: {
      auto maybe = ParseInt<int64_t>(op);
      if (!maybe) return kEncodeFailure;
      val = maybe.value();
      break;
    }
    case FK::INT:  // TODO: add unsigned version
    case FK::INT_HEX_CUSTOM:
    case FK::INT_HEX: {
      auto maybe = ParseInt<uint64_t>(op);
      if (!maybe) return kEncodeFailure;
      val = maybe.value();
      break;
    }
  }

  return EncodeOperand(ok, val);
}

const constexpr struct {
  std::string_view expr_kind;
  elf::RELOC_TYPE_AARCH64 reloc_kind;
  bool local;
} kExprToReloc[] = {
    // order by frequency
    {"jump26", elf::RELOC_TYPE_AARCH64::JUMP26, true},
    {"condbr19", elf::RELOC_TYPE_AARCH64::CONDBR19, true},
    {"call26", elf::RELOC_TYPE_AARCH64::CALL26, false},
    {"adr_prel_pg_hi21", elf::RELOC_TYPE_AARCH64::ADR_PREL_PG_HI21, false},
    {"add_abs_lo12_nc", elf::RELOC_TYPE_AARCH64::ADD_ABS_LO12_NC, false},
    {"loc_adr_prel_pg_hi21", elf::RELOC_TYPE_AARCH64::ADR_PREL_PG_HI21, true},
    {"loc_add_abs_lo12_nc", elf::RELOC_TYPE_AARCH64::ADD_ABS_LO12_NC, true},
    {"abs32", elf::RELOC_TYPE_AARCH64::ABS32, false},
    {"abs64", elf::RELOC_TYPE_AARCH64::ABS64, false},
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

bool InsFromSymbolized(const std::vector<std::string_view>& token, Ins* ins) {
  ins->opcode = FindOpcodeForMnemonic(token[0]);
  if (ins->opcode == nullptr) {
    std::cerr << "unknown opcode " << token[0] << "\n";
    return false;
  }
  ASSERT(token.size() - 1 == ins->opcode->num_fields,
         "bad number of token " << token.size() << " expected "
                                << ins->opcode->num_fields + 1 << " for "
                                << token[0]);
  for (unsigned i = 1; i < token.size(); ++i) {
    if (token[i].substr(0, 5) == "expr:") {
      if (!HandleRelocation(token[i].substr(5), i - 1, ins)) {
        std::cerr << "malformed relocation expression " << token[i] << "\n";
        return false;
      }
    } else {
      const OK ok = ins->opcode->fields[i - 1];
      auto val = UnsymbolizeOperand(ok, token[i]);
      if (val == kEncodeFailure) {
        std::cerr << "cannot parse " << token[i] << " for ok [" << int(ok)
                  << "]\n";
        return false;
      }
      ins->operands[i - 1] = val;
    }
  }
  return true;
}

// std::string_view InsSymbolize(const a64::Ins& ins,
//                              std::vector<std::string>* operands) {}

}  // namespace cwerg::a64
