
#include "CpuA64/symbolic.h"
#include <cstring>
#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::a64 {
using namespace cwerg;

char* strappend(char* dst, std::string_view src) {
  memcpy(dst, src.data(), src.size());
  dst[src.size()] = 0;
  return dst + src.size();
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

char* strappendflt(char* dst, double d) {
  ToFltString(d, dst);
  return dst + strlen(dst);
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
  ASSERT(false, "NYI");
}

std::string_view InsSymbolize(const a64::Ins& ins,
                              std::vector<std::string>* ops) {
  char buffer[128];
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    if (ins.reloc_kind != elf::RELOC_TYPE_AARCH64::NONE && i == ins.reloc_pos) {
      SymbolizeReloc(buffer, ins, ins.operands[i]);
    } else {
      SymbolizeOperand(buffer, ins.operands[i], ins.opcode->fields[i]);
    }
    ops->emplace_back(buffer);
  }
  return ins.opcode->name;
}

uint32_t UnsymbolizeOperand(OK ok, std::string_view op) {
  return  kEncodeFailure;
}

bool HandleRelocation(std::string_view, uint32_t pos, Ins* ins) {
  ASSERT(false, "NYI");
  return false;
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

// std::string_view InsSymbolize(const a64::Ins& ins,
//                              std::vector<std::string>* operands) {}

}  // namespace cwerg::a64
