#pragma once
// (c) Robert Muth - see LICENSE for more info
//
// Expressions that can be (partiatally) evaluated at compile time are annotated
// with a Const (handle). The encoding is quite complex and consists of a kind
// (BASE_TYPE_KIND) and a value. Short values are directly encoded the handle.
// For details see the implementation of: std::ostream& operator<<(std::ostream&
// os, Const c)
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/identifier.h"
#include "Util/assert.h"

namespace cwerg::fe {

constexpr const Const kConstUndef(0, BASE_TYPE_KIND::UNDEF);
constexpr const Const kConstVoid(0, BASE_TYPE_KIND::VOID);
constexpr const Const kConstFalse(1U << 23U | 0, BASE_TYPE_KIND::BOOL);
constexpr const Const kConsTrue(1U << 23U | 1, BASE_TYPE_KIND::BOOL);

extern ImmutablePool ConstPool;

constexpr const char EVAL_STR[] = "@eval@";

struct EvalSpan {
  Node pointer;
  SizeOrDim size;  // invalid if < 0
  Const content;   // usually a compound
};

// TODO: try converting this into a Handle Transformer from
// ValCompound/ValString -> Const
struct EvalCompound {
  Node init_node;
};

inline bool ValIsShortConstUnsigned(uint64_t val) {
  return val < (1ULL << 23U);
}
inline bool ValIsShortConstSigned(int64_t val) {
  return -(1 << 22U) <= val && val < (1 << 22U);
}

inline Const ConstNewShortSigned(int64_t val, BASE_TYPE_KIND kind) {
  ASSERT(IsSint(kind), "");
  return Const(1U << 23U | (uint32_t)val, kind);
}

inline Const ConstNewShortUnsigned(uint32_t val, BASE_TYPE_KIND kind) {
  ASSERT(IsUint(kind) || kind == BASE_TYPE_KIND::BOOL,
         "not a uint " << int(kind));
  return Const(1U << 23U | val, kind);
}

inline uint32_t ConstShortGetUnsigned(Const c) {
  ASSERT(IsUint(c.kind()) || c.kind() == BASE_TYPE_KIND::BOOL,
         "not unsigned " << int(c.kind()));
  return c.value << 1U >> 9U;
}

inline int32_t ConstShortGetSigned(Const c) {
  ASSERT(IsSint(c.kind()), "");
  return std::bit_cast<int32_t, uint32_t>(c.value << 1U) >> 9U;
}

inline Const ConstNewBool(bool val) {
  return ConstNewShortUnsigned(val, BASE_TYPE_KIND::BOOL);
}

inline Const ConstNewU8(uint8_t val) {
  return ConstNewShortUnsigned(val, BASE_TYPE_KIND::U8);
}
inline Const ConstNewU16(uint16_t val) {
  return ConstNewShortUnsigned(val, BASE_TYPE_KIND::U16);
}

inline Const ConstNewU32(uint32_t val) {
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, BASE_TYPE_KIND::U32);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::U32);
}

inline Const ConstNewU64(uint64_t val) {
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, BASE_TYPE_KIND::U64);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::U64);
}

inline Const ConstNewS8(int8_t val) {
  return ConstNewShortSigned(val, BASE_TYPE_KIND::S8);
}
inline Const ConstNewS16(int16_t val) {
  return ConstNewShortSigned(val, BASE_TYPE_KIND::S16);
}

inline Const ConstNewS32(int32_t val) {
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, BASE_TYPE_KIND::S32);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::U32);
}

inline Const ConstNewS64(int64_t val) {
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortUnsigned(val, BASE_TYPE_KIND::S64);
  }
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::U64);
}

inline Const ConstNewR32(float val) {
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::R32);
}

inline Const ConstNewR64(double val) {
  return Const(ConstPool.Intern(std::string_view((char*)&val, sizeof(val))),
               BASE_TYPE_KIND::R64);
}

extern Const ConstNewUnsigned(uint64_t val, BASE_TYPE_KIND bt);
extern Const ConstNewSigned(int64_t val, BASE_TYPE_KIND bt);
inline Const ConstNewReal(double val, BASE_TYPE_KIND bt) {
  if (bt == BASE_TYPE_KIND::R32) return ConstNewR32(val);
  ASSERT(bt == BASE_TYPE_KIND::R64, "");
  return ConstNewR64(val);
}

inline Const ConstNewSymAddr(Node sym) {
  ASSERT(sym.kind() == NT::DefVar || sym.kind() == NT::DefGlobal, "");
  return Const(ConstPool.Intern(std::string_view((char*)&sym, sizeof(sym))),
               BASE_TYPE_KIND::SYM_ADDR);
}

inline Const ConstNewFunAddr(Node sym) {
  return Const(ConstPool.Intern(std::string_view((char*)&sym, sizeof(sym))),
               BASE_TYPE_KIND::FUN_ADDR);
}

// represents the value of arrays and recs
inline Const ConstNewCompound(EvalCompound compound) {
  return Const(
      ConstPool.Intern(std::string_view((char*)&compound, sizeof(compound))),
      BASE_TYPE_KIND::COMPOUND);
}

inline EvalCompound ConstGetCompound(Const c) {
  ASSERT(c.kind() == BASE_TYPE_KIND::COMPOUND, "");
  return *(EvalCompound*)ConstPool.Data(c.index());
}

inline Node ConstGetSymbol(Const c) {
  ASSERT(c.kind() == BASE_TYPE_KIND::SYM_ADDR ||
             c.kind() == BASE_TYPE_KIND::FUN_ADDR,
         "cannot get symbol");
  return *(Node*)ConstPool.Data(c.index());
}

inline Const ConstNewSpan(EvalSpan span) {
  return Const(ConstPool.Intern(std::string_view((char*)&span, sizeof(span))),
               BASE_TYPE_KIND::SPAN);
}

extern int64_t ConstGetSigned(Const c);
extern uint64_t ConstGetUnsigned(Const c);
extern double ConstGetFloat(Const c);

extern uint64_t ConstGetBitcastUnsigned(Const c);
extern Const ConstNewBitcastUnsigned(uint64_t val, BASE_TYPE_KIND bt);

inline EvalSpan ConstGetSpan(Const c) {
  ASSERT(c.kind() == BASE_TYPE_KIND::SPAN, "");
  return *(EvalSpan*)ConstPool.Data(c.index());
}

extern std::ostream& operator<<(std::ostream& os, Const c);

extern std::string to_string(Const c, const std::map<Node, std::string>* labels);

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods);
}  // namespace cwerg::fe