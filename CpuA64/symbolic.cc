
#include "CpuA64/symbolic.h"
#include <cstring>
#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::a64 {
using namespace cwerg;

uint64_t MakeIeee64(uint64_t sign, uint64_t mantissa, uint64_t exponent) {
  ASSERT(0 <= exponent && exponent <= 7, "");
  ASSERT(0 <= mantissa && mantissa <= 15, "");
  return (sign << 63) | ((exponent - 3 + 1023) << 52) | (mantissa << 48);
}

uint32_t Encode8BitFlt(double val) {
  union {
    double d;
    uint64_t i;
  } dtoi;
  dtoi.d = val;

  uint64_t ieee64 = dtoi.i;
  uint64_t mantissa = ieee64 & ((1ULL << 52) - 1);
  ieee64 >>= 52;
  uint64_t exponent = (ieee64 & ((1 << 11) - 1)) - 1023 + 3;
  uint64_t sign = ieee64 >> 11;
  if (0 <= exponent <= 7 && ((mantissa >> 48) << 48) == mantissa) {
    return (sign << 7) | ((exponent ^ 4) << 4) | (mantissa >> 48);
  }
  return kEncodeFailure;
}

double Decode8BitFlt(uint32_t x) {
  const uint32_t mantissa = (x & 0xf);
  x >>= 4;
  const uint32_t exponent = (x & 7) ^ 4;
  const uint32_t sign = (x >> 3);
  union {
    double d;
    uint64_t i;
  } dtoi;
  dtoi.i = MakeIeee64(sign, mantissa, exponent);
  return dtoi.d;
}

int32_t SignedIntFromBits(uint32_t data, unsigned n_bits) {
  uint32_t mask = (1 << n_bits) - 1;
  data &= mask;
  bool is_neg = data & (1 << (n_bits - 1));
  return is_neg ? data - (1 << n_bits) : data;
}

uint64_t ror(uint64_t x, uint32_t bit_size, uint32_t amount) {
  uint64_t mask = (1ULL << amount) - 1;
  return (x >> amount) | ((x & mask) << (bit_size - amount));
}

uint64_t Decode_10_15_16_22(uint32_t x, uint32_t reg_size) {
  const uint32_t n = x >> 12;
  const uint32_t r = (x >> 6) & 0x3f;
  const uint32_t s = x & 0x3f;
  uint32_t size = 64;
  uint32_t ones = s + 1;
  if (n != 1) {
    size = 32;
    while ((size & s) != 0) size >>= 1;
    ones = 1 + (s & (size - 1));
    ASSERT(ones != size, "");
  }
  uint64_t pattern = (1ULL << ones) - 1;
  while (size < reg_size) {
    pattern |= pattern << size;
    size *= 2;
  }
  return ror(pattern, reg_size, r);
}

uint32_t Encode_10_15_16_22_X(uint64_t x) {
  if (x == 0 || (x + 1) == 0) return kEncodeFailure;
  // for size, sm in
  // [(64, 0), (32, 0), (16, 0x20), (8, 0x30), (4, 0x38), (2, 0x3c)]
  uint32_t size;
  uint32_t sm = 0;
  for (size = 64; size >= 2; size >>= 1) {
      const uint32_t shift = size >> 1;
      const uint32_t a = x & ((1 << shift) - 1);
      const uint32_t b = x >> shift;
      if (a == b) {
        x = a;
      } else {
        break;
      }

     if (size <= 32) {
       sm += size;
     }
  }
  ASSERT(size != 1, "");
  // const uint32_t sm = size > 16 ? 0 :
  const uint32_t n = size == 64 ? 1 : 0;
  const uint32_t ones = __builtin_popcountll(x);
  const uint64_t ones_mask = (1ULL << ones) - 1;
  for (uint32_t r = 0; r < size; ++r) {
    if (x == ror(ones_mask, size, r)) {
      const uint32_t s = sm | (ones - 1);
      return (n << 12) | (r << 6) | s;
    }
  }
  return kEncodeFailure;
}

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

const char* _STR_SHIFT_15_W[] = {"uxtw", "sxtw"};
const char* _STR_SHIFT_15_X[] = {"lsl", "sxtx"};
const char* _STR_SHIFT_22_23[] = {"lsl", "lsr", "asr", "ror"};
const char* _STR_SHIFT_22_23_NO_ROR[] = {"lsl", "lsr", "asr"};

char* RenderOperand(char buffer[64], int32_t x, OK ok) {
  switch (ok) {
      // REGISTER
    case OK::WREG_0_4_SP:
    case OK::WREG_5_9_SP:
      if (x == 31) return strappend(buffer, "sp");
      *buffer++ = 'w';
      return strappenddec(buffer, x);
    case OK::WREG_0_4:
    case OK::WREG_5_9:
    case OK::WREG_10_14:
    case OK::WREG_16_20:
      if (x == 31) return strappend(buffer, "wzr");
      *buffer++ = 'w';
      return strappenddec(buffer, x);
    case OK::XREG_0_4_SP:
    case OK::XREG_5_9_SP:
      if (x == 31) return strappend(buffer, "sp");
      *buffer++ = 'x';
      return strappenddec(buffer, x);
    case OK::XREG_0_4:
    case OK::XREG_5_9:
    case OK::XREG_10_14:
    case OK::XREG_16_20:
      if (x == 31) return strappend(buffer, "xzr");
      *buffer++ = 'x';
      return strappenddec(buffer, x);
    case OK::BREG_0_4:
    case OK::BREG_5_9:
    case OK::BREG_10_14:
    case OK::BREG_16_20:
      *buffer++ = 'b';
      return strappenddec(buffer, x);
    case OK::HREG_0_4:
    case OK::HREG_5_9:
    case OK::HREG_10_14:
    case OK::HREG_16_20:
      *buffer++ = 'h';
      return strappenddec(buffer, x);
    case OK::SREG_0_4:
    case OK::SREG_5_9:
    case OK::SREG_10_14:
    case OK::SREG_16_20:
      *buffer++ = 's';
      return strappenddec(buffer, x);
    case OK::DREG_0_4:
    case OK::DREG_5_9:
    case OK::DREG_10_14:
    case OK::DREG_16_20:
      *buffer++ = 'd';
      return strappenddec(buffer, x);
    case OK::QREG_0_4:
    case OK::QREG_5_9:
    case OK::QREG_10_14:
    case OK::QREG_16_20:
      *buffer++ = 'q';
      return strappenddec(buffer, x);
      // EASY IMMEDIATES
    case OK::IMM_5_20:
      return strappendhex(buffer, x);
    case OK::IMM_16_20:
      return strappendhex(buffer, x);
    case OK::IMM_COND_0_3:
      return strappendhex(buffer, x);
      //
    case OK::IMM_16_21:
      return strappenddec(buffer, x);
    case OK::IMM_10_15:
      return strappenddec(buffer, x);
    case OK::IMM_10_21:
      return strappenddec(buffer, x);
    case OK::IMM_19_23_31:
      return strappenddec(buffer, x);
    case OK::IMM_10_12_LIMIT4:
      return strappenddec(buffer, x);
      //
    case OK::IMM_10_21_times_2:
      return strappenddec(buffer, x * 2);
    case OK::IMM_10_21_times_4:
      return strappenddec(buffer, x * 4);
    case OK::IMM_10_21_times_8:
      return strappenddec(buffer, x * 8);
    case OK::IMM_10_21_times_16:
      return strappenddec(buffer, x * 16);
    case OK::IMM_12_MAYBE_SHIFT_0:
      return strappenddec(buffer, x * 0);  // zero
    case OK::IMM_12_MAYBE_SHIFT_1:
      return strappenddec(buffer, x * 1);
    case OK::IMM_12_MAYBE_SHIFT_2:
      return strappenddec(buffer, x * 2);
    case OK::IMM_12_MAYBE_SHIFT_3:
      return strappenddec(buffer, x * 3);
    case OK::IMM_12_MAYBE_SHIFT_4:
      return strappenddec(buffer, x * 4);
      //
    case OK::SIMM_15_21_TIMES4:
      return strappenddec(buffer, SignedIntFromBits(x, 7) * 4);
    case OK::SIMM_15_21_TIMES8:
      return strappenddec(buffer, SignedIntFromBits(x, 7) * 8);
    case OK::SIMM_15_21_TIMES16:
      return strappenddec(buffer, SignedIntFromBits(x, 7) * 16);
    case OK::SIMM_12_20:
      return strappenddec(buffer, SignedIntFromBits(x, 9));
    case OK::SIMM_PCREL_0_25:
      return strappenddec(buffer, SignedIntFromBits(x, 26));
    case OK::SIMM_PCREL_5_23:
      return strappenddec(buffer, SignedIntFromBits(x, 19));
    case OK::SIMM_PCREL_5_18:
      return strappenddec(buffer, SignedIntFromBits(x, 14));
    case OK::SIMM_PCREL_5_23_29_30:
      return strappenddec(buffer, SignedIntFromBits(x, 21));
    // MISC
    case OK::IMM_FLT_ZERO:
      return strappend(buffer, "0.0");
    case OK::REG_LINK:
      return strappend(buffer, "lr");
      // SHIFT
    case OK::SHIFT_15_W:
      return strappend(buffer, _STR_SHIFT_15_W[x]);
    case OK::SHIFT_15_X:
      return strappend(buffer, _STR_SHIFT_15_X[x]);
    case OK::SHIFT_22_23:
      return strappend(buffer, _STR_SHIFT_22_23[x]);
    case OK::SHIFT_22_23_NO_ROR:
      return strappend(buffer, _STR_SHIFT_22_23_NO_ROR[x]);
    //
    default:
      ASSERT(false, "unhandled OK: " << (unsigned)ok);
      return buffer;
  }
}

// std::string_view InsSymbolize(const a64::Ins& ins,
//                              std::vector<std::string>* operands) {}

}  // namespace cwerg::a64
