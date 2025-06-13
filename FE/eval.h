#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/identifier.h"
#include "Util/assert.h"

namespace cwerg::fe {

extern ImmutablePool ConstPool;

struct EvalSpan {
  Node pointer;
  int32_t size;   // invalid if < 0
  Const content;  // usually a compound
};

inline bool ValIsShortConstUnsigned(uint32_t val) { return val < (1 << 23U); }
inline bool ValIsShortConstSigned(int64_t val) {
  return -(1 << 12U) <= val && val < (1 << 22U);
}

inline Const ConstNewShortSigned(int64_t val, CONST_KIND kind) {
  ASSERT(IsSint(kind), "");
  return Const(1U << 23U | (uint32_t)val, kind);
}

inline Const ConstNewShortUnsigned(uint32_t val, CONST_KIND kind) {
  ASSERT(IsUintOrBool(kind), "not a uint " << int(kind));
  return Const(1U << 23U | val, kind);
}

inline uint32_t ConstShortGetUnsigned(Const c) {
  ASSERT(IsUint(c.kind()), "");
  return c.value << 1U >> 9U;
}

inline int32_t ConstShortGetSigned(Const c) {
  ASSERT(IsSint(c.kind()), "");
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
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::U32);
}

inline Const ConstNewU64(uint64_t val) {
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, CONST_KIND::U64);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::U64);
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
    return ConstNewShortUnsigned(val, CONST_KIND::S32);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::U32);
}

inline Const ConstNewS64(int64_t val) {
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortUnsigned(val, CONST_KIND::S64);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::U64);
}

inline Const ConstNewR32(float val) {
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::R32);
}

inline Const ConstNewR64(double val) {
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               CONST_KIND::R64);
}

inline Const ConstNewFloat(double val, BASE_TYPE_KIND bt) {
  if (bt == BASE_TYPE_KIND::R32) return ConstNewR32(val);
  ASSERT(bt == BASE_TYPE_KIND::R64, "");
  return ConstNewR64(val);
}

inline Const ConstNewUndef() { return Const(0, CONST_KIND::UNDEF); }
inline Const ConstNewVoid() { return Const(0, CONST_KIND::VOID); }

inline Const ConstNewComplexDefault() {
  return Const(0, CONST_KIND::COMPLEX_DEFAULT);
}

inline Const ConstNewSymAddr(Node sym) {
  return Const(ConstPool.Intern(std::string_view((char*)&sym, sizeof(sym))),
               CONST_KIND::SYM_ADDR);
}

inline Const ConstNewFunAddr(Node sym) {
  return Const(ConstPool.Intern(std::string_view((char*)&sym, sizeof(sym))),
               CONST_KIND::FUN_ADDR);
}

inline Const ConstNewCompound(Node sym) {
  return Const(ConstPool.Intern(std::string_view((char*)&sym, sizeof(sym))),
               CONST_KIND::COMPOUND);
}

inline Node ConstGetSymbol(Const c) {
  ASSERT(c.kind() == CONST_KIND::SYM_ADDR || c.kind() == CONST_KIND::FUN_ADDR ||
             c.kind() == CONST_KIND::COMPOUND,
         "");
  return *(Node*)ConstPool.Data(c.index());
}

inline Const ConstNewSpan(EvalSpan span) {
  return Const(ConstPool.Intern(std::string_view((char*)&span, sizeof(span))),
               CONST_KIND::SPAN);
}

extern int64_t ConstGetSigned(Const c);
extern uint64_t ConstGetUnsigned(Const c);
extern double ConstGetFloat(Const c);

inline EvalSpan ConstGetSpan(Const c) {
  ASSERT(c.kind() == CONST_KIND::SPAN, "");
  return *(EvalSpan*)ConstPool.Data(c.index());
}

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods);
}  // namespace cwerg::fe