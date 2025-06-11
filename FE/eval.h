#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/identifier.h"

#include "Util/assert.h"

namespace cwerg::fe {

struct ConstCore {
  union {
    float val_r32;
    double val_r64;
    uint32_t val_u32;
    uint64_t val_u64;
    int32_t val_s32;
    int64_t val_s64;
    Node symbol;
    struct {
      Node pointers;
      Const size;
      Node content;
    } span;
  };
};

extern struct Stripe<ConstCore, Const> gConstCore;
extern struct StripeGroup gStripeGroupConst;

inline ConstCore& ConstGetCore(Const c) { return gConstCore[c]; }

inline Const ConstNewLong(CONST_KIND kind) {
  Const out = Const(gStripeGroupConst.New().index(), kind);
  // ASSERT(out.index() != xxx, "");
  return out;
}

inline bool ConstIsShort(Const num) { return int32_t(num.value) < 0; }
inline bool ValIsShortConstUnsigned(uint32_t val) { return val < (1U << 23U); }

inline bool ValIsShortConstSigned(uint64_t val) {
  return -(1U << 12U) <= val && val < (1U << 22U);
}

inline Const ConstNewShortSigned(int64_t val, CONST_KIND kind) {
  return Const(1U << 23U | (uint32_t)val, kind);
}

inline Const ConstNewShortUnsigned(uint32_t val, CONST_KIND kind) {
  return Const(1U << 23U | val, kind);
}

inline uint32_t ConstShortGetUnsigned(Const c) { return c.value << 1U >> 9U; }
inline int32_t ConstShortGetSigned(Const c) {
  return int32_t(c.value) << 1U >> 9U;
}

inline Const ConstNewBool(bool val) {
  return ConstNewShortUnsigned(val, CONST_KIND::BOOL);
}

inline Const ConstNewU8(uint8_t val) {
  return ConstNewShortUnsigned(val, CONST_KIND::U8);
}
inline Const ConstNewU16(uint16_t val) {
  return ConstNewShortUnsigned(val, CONST_KIND::U16);
}
inline Const ConstNewU32(uint32_t val) {
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, CONST_KIND::U32);
  }
  Const out = ConstNewLong(CONST_KIND::U32);
  ConstGetCore(out).val_u32 = val;
  return out;
}
inline Const ConstNewU64(uint64_t val) {
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, CONST_KIND::U64);
  }
  Const out = ConstNewLong(CONST_KIND::U64);
  ConstGetCore(out).val_u64 = val;
  return out;
}

extern Const ConstNewUnsigned(uint64_t val, BASE_TYPE_KIND bt);
extern Const ConstNewSigned(int64_t val, BASE_TYPE_KIND bt);

inline Const ConstNewS8(int8_t val) {
  return ConstNewShortSigned(val, CONST_KIND::S8);
}
inline Const ConstNewS16(int16_t val) {
  return ConstNewShortSigned(val, CONST_KIND::S16);
}
inline Const ConstNewS32(int32_t val) {
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, CONST_KIND::U32);
  }
  Const out = ConstNewLong(CONST_KIND::S32);
  ConstGetCore(out).val_s32 = val;
  return out;
}
inline Const ConstNewS64(int64_t val) {
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, CONST_KIND::S64);
  }
  Const out = ConstNewLong(CONST_KIND::S64);
  ConstGetCore(out).val_s64 = val;
  return out;
}
inline Const ConstNewUndef() { return Const(0, CONST_KIND::UNDEF); }
inline Const ConstNewVoid() { return Const(0, CONST_KIND::VOID); }
inline Const ConstNewComplexDefault() {
  return Const(0, CONST_KIND::COMPLEX_DEFAULT);
}

inline Const ConstNewSymAddr(Node sym) {
  Const out = ConstNewLong(CONST_KIND::SYM_ADDR);
  ConstGetCore(out).symbol = sym;
  return out;
}

inline Const ConstNewFunAddr(Node sym) {
  Const out = ConstNewLong(CONST_KIND::FUN_ADDR);
  ConstGetCore(out).symbol = sym;
  return out;
}

inline Const ConstNewCompound(Node sym) {
  Const out = ConstNewLong(CONST_KIND::COMPOUND);
  ConstGetCore(out).symbol = sym;
  return out;
}

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods);
}  // namespace cwerg::fe