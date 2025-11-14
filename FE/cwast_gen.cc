#include "FE/cwast_gen.h"

#include <cstdint>
#include <map>

#include "Util/assert.h"

namespace cwerg::fe {

#define BIT_B(x) 1ull << uint32_t(BF::x)
#define BIT_X(x) 1ull << uint32_t(NFD_X_FIELD::x)

struct StringKind {
  const char* name;
  uint8_t kind;
};

constexpr std::array<uint16_t, 17> InitBF2MASK() {
  std::array<uint16_t, 17> out;
  //
  out[int(BF::MUT)] = 1 << 1;
  out[int(BF::UNCHECKED)] = 1 << 1;
  out[int(BF::UNTAGGED)] = 1 << 1;
  //
  out[int(BF::PRESERVE_MUT)] = 1 << 2;
  out[int(BF::REF)] = 1 << 2;
  out[int(BF::ARG_REF)] = 1 << 2;
  out[int(BF::WRAPPED)] = 1 << 2;
  out[int(BF::COLON)] = 1 << 2;
  //
  out[int(BF::RES_REF)] = 1 << 3;
  out[int(BF::PUB)] = 1 << 3;
  //
  out[int(BF::BUILTIN)] = 1 << 4;
  out[int(BF::CDECL)] = 1 << 5;
  out[int(BF::EXTERN)] = 1 << 6;
  out[int(BF::FINI)] = 1 << 7;
  out[int(BF::INIT)] = 1 << 8;
  out[int(BF::POLY)] = 1 << 9;
  //
  return out;
}

const std::array<uint16_t, 17> BF2MASK = InitBF2MASK();

// clang-format off
/* @AUTOGEN-START@ */
const NodeFieldDesc GlobalNodeFieldDescs[] = {
    {}, // invalid
    {  1, NFD_KIND::LIST },  // args
    {  2, NFD_KIND::LIST },  // args_mod
    {  3, NFD_KIND::LIST },  // body
    {  3, NFD_KIND::LIST },  // body_f
    {  2, NFD_KIND::LIST },  // body_for
    {  3, NFD_KIND::LIST },  // body_macro
    {  3, NFD_KIND::LIST },  // body_mod
    {  2, NFD_KIND::LIST },  // body_t
    {  0, NFD_KIND::NODE },  // callee
    {  0, NFD_KIND::LIST },  // cases
    {  1, NFD_KIND::NODE },  // cond
    {  0, NFD_KIND::NODE },  // container
    {  1, NFD_KIND::NAME },  // enum_name
    {  0, NFD_KIND::NODE },  // expr
    {  0, NFD_KIND::NODE },  // expr1
    {  1, NFD_KIND::NODE },  // expr2
    {  2, NFD_KIND::NODE },  // expr_bound_or_undef
    {  2, NFD_KIND::NODE },  // expr_f
    {  1, NFD_KIND::NODE },  // expr_index
    {  0, NFD_KIND::NODE },  // expr_lhs
    {  0, NFD_KIND::NODE },  // expr_ret
    {  1, NFD_KIND::NODE },  // expr_rhs
    {  1, NFD_KIND::NODE },  // expr_size
    {  0, NFD_KIND::NODE },  // expr_t
    {  2, NFD_KIND::NODE },  // field
    {  1, NFD_KIND::LIST },  // fields
    {  2, NFD_KIND::LIST },  // gen_ids
    {  2, NFD_KIND::NODE },  // initial_or_undef_or_auto
    {  0, NFD_KIND::LIST },  // inits
    {  1, NFD_KIND::LIST },  // items
    {  0, NFD_KIND::NAME },  // label
    {  0, NFD_KIND::NODE },  // lhs
    {  0, NFD_KIND::STR },  // message
    {  0, NFD_KIND::NAME },  // name
    {  1, NFD_KIND::NAME },  // name_list
    {  0, NFD_KIND::STR },  // number
    {  1, NFD_KIND::LIST },  // params
    {  1, NFD_KIND::LIST },  // params_macro
    {  1, NFD_KIND::LIST },  // params_mod
    {  1, NFD_KIND::STR },  // path
    {  1, NFD_KIND::NODE },  // point_or_undef
    {  0, NFD_KIND::NODE },  // pointer
    {  2, NFD_KIND::NODE },  // result
    {  0, NFD_KIND::NODE },  // size
    {  0, NFD_KIND::STR },  // string
    {  0, NFD_KIND::NODE },  // subtrahend
    {  0, NFD_KIND::NAME },  // target
    {  1, NFD_KIND::NODE },  // type
    {  1, NFD_KIND::NODE },  // type_or_auto
    {  0, NFD_KIND::LIST },  // types
    {  1, NFD_KIND::NODE },  // value_or_auto
    {  0, NFD_KIND::NODE },  // value_or_undef
};

const NodeDesc GlobalNodeDescs[] = {
    {}, // invalid
    { { NFD_SLOT::invalid,NFD_SLOT::cond,NFD_SLOT::invalid,NFD_SLOT::body }, 0, 0 }, // Case
    { { NFD_SLOT::name,NFD_SLOT::items,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(PUB), BIT_X(type)| BIT_X(eval) }, // DefEnum
    { { NFD_SLOT::name,NFD_SLOT::params,NFD_SLOT::result,NFD_SLOT::body }, BIT_B(INIT)| BIT_B(FINI)| BIT_B(EXTERN)| BIT_B(CDECL)| BIT_B(POLY)| BIT_B(PUB)| BIT_B(REF), BIT_X(type) }, // DefFun
    { { NFD_SLOT::name,NFD_SLOT::type_or_auto,NFD_SLOT::initial_or_undef_or_auto,NFD_SLOT::invalid }, BIT_B(PUB)| BIT_B(MUT)| BIT_B(REF)| BIT_B(CDECL), BIT_X(type)| BIT_X(eval) }, // DefGlobal
    { { NFD_SLOT::name,NFD_SLOT::params_macro,NFD_SLOT::gen_ids,NFD_SLOT::body_macro }, BIT_B(BUILTIN)| BIT_B(PUB), 0 }, // DefMacro
    { { NFD_SLOT::name,NFD_SLOT::params_mod,NFD_SLOT::invalid,NFD_SLOT::body_mod }, BIT_B(BUILTIN), 0 }, // DefMod
    { { NFD_SLOT::name,NFD_SLOT::fields,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(PUB), BIT_X(type) }, // DefRec
    { { NFD_SLOT::name,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(PUB)| BIT_B(WRAPPED), BIT_X(type) }, // DefType
    { { NFD_SLOT::name,NFD_SLOT::type_or_auto,NFD_SLOT::initial_or_undef_or_auto,NFD_SLOT::invalid }, BIT_B(MUT)| BIT_B(REF), BIT_X(type)| BIT_X(eval) }, // DefVar
    { { NFD_SLOT::name,NFD_SLOT::value_or_auto,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // EnumVal
    { { NFD_SLOT::invalid,NFD_SLOT::args,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(COLON), 0 }, // EphemeralList
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // Expr1
    { { NFD_SLOT::expr1,NFD_SLOT::expr2,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // Expr2
    { { NFD_SLOT::expr_t,NFD_SLOT::cond,NFD_SLOT::expr_f,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // Expr3
    { { NFD_SLOT::expr_lhs,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(MUT), BIT_X(type)| BIT_X(eval) }, // ExprAddrOf
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprAs
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprBitCast
    { { NFD_SLOT::callee,NFD_SLOT::args,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprCall
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprDeref
    { { NFD_SLOT::container,NFD_SLOT::invalid,NFD_SLOT::field,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprField
    { { NFD_SLOT::container,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(MUT)| BIT_B(PRESERVE_MUT), BIT_X(type)| BIT_X(eval) }, // ExprFront
    { { NFD_SLOT::container,NFD_SLOT::expr_index,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(UNCHECKED), BIT_X(type)| BIT_X(eval) }, // ExprIndex
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprIs
    { { NFD_SLOT::container,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprLen
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(UNCHECKED), BIT_X(type)| BIT_X(eval) }, // ExprNarrow
    { { NFD_SLOT::invalid,NFD_SLOT::type,NFD_SLOT::field,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprOffsetof
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprParen
    { { NFD_SLOT::expr1,NFD_SLOT::expr2,NFD_SLOT::expr_bound_or_undef,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprPointer
    { { NFD_SLOT::invalid,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprSizeof
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // ExprSrcLoc
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::body }, 0, BIT_X(type)| BIT_X(eval) }, // ExprStmt
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprStringify
    { { NFD_SLOT::invalid,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprTypeId
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprUnionTag
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprUnionUntagged
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprUnwrap
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprWiden
    { { NFD_SLOT::expr,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ExprWrap
    { { NFD_SLOT::name,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(ARG_REF)| BIT_B(RES_REF), BIT_X(type) }, // FunParam
    { { NFD_SLOT::name,NFD_SLOT::enum_name,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval)| BIT_X(symbol) }, // Id
    { { NFD_SLOT::name,NFD_SLOT::path,NFD_SLOT::args_mod,NFD_SLOT::invalid }, 0, 0 }, // Import
    { { NFD_SLOT::name,NFD_SLOT::name_list,NFD_SLOT::body_for,NFD_SLOT::invalid }, 0, 0 }, // MacroFor
    { { NFD_SLOT::name,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // MacroId
    { { NFD_SLOT::name,NFD_SLOT::args,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(symbol) }, // MacroInvoke
    { { NFD_SLOT::name,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // MacroParam
    { { NFD_SLOT::name,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // ModParam
    { { NFD_SLOT::name,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // RecField
    { { NFD_SLOT::lhs,NFD_SLOT::expr_rhs,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtAssignment
    { { NFD_SLOT::label,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::body }, 0, 0 }, // StmtBlock
    { { NFD_SLOT::target,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(target) }, // StmtBreak
    { { NFD_SLOT::lhs,NFD_SLOT::expr_rhs,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtCompoundAssignment
    { { NFD_SLOT::cases,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtCond
    { { NFD_SLOT::target,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(target) }, // StmtContinue
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::body }, 0, 0 }, // StmtDefer
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtExpr
    { { NFD_SLOT::invalid,NFD_SLOT::cond,NFD_SLOT::body_t,NFD_SLOT::body_f }, 0, 0 }, // StmtIf
    { { NFD_SLOT::expr_ret,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(target) }, // StmtReturn
    { { NFD_SLOT::message,NFD_SLOT::cond,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtStaticAssert
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, 0 }, // StmtTrap
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeAuto
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeBase
    { { NFD_SLOT::invalid,NFD_SLOT::params,NFD_SLOT::result,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeFun
    { { NFD_SLOT::expr,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeOf
    { { NFD_SLOT::invalid,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(MUT), BIT_X(type) }, // TypePtr
    { { NFD_SLOT::invalid,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(MUT), BIT_X(type) }, // TypeSpan
    { { NFD_SLOT::types,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, BIT_B(UNTAGGED), BIT_X(type) }, // TypeUnion
    { { NFD_SLOT::subtrahend,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeUnionDelta
    { { NFD_SLOT::size,NFD_SLOT::type,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type) }, // TypeVec
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValAuto
    { { NFD_SLOT::inits,NFD_SLOT::type_or_auto,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValCompound
    { { NFD_SLOT::number,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValNum
    { { NFD_SLOT::value_or_undef,NFD_SLOT::point_or_undef,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValPoint
    { { NFD_SLOT::pointer,NFD_SLOT::expr_size,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValSpan
    { { NFD_SLOT::string,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValString
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(eval) }, // ValUndef
    { { NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid,NFD_SLOT::invalid }, 0, BIT_X(type)| BIT_X(eval) }, // ValVoid
};

const char* const MOD_PARAM_KIND_ToStringMap[] = {
    "INVALID", // 0
    "CONST_EXPR", // 1
    "TYPE", // 2
};
const char* EnumToString(MOD_PARAM_KIND x) { return MOD_PARAM_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind MOD_PARAM_KIND_FromStringMap[] = {
    {"CONST_EXPR", 1},
    {"INVALID", 0},
    {"TYPE", 2},
    {"ZZZ", 0},
};

const uint8_t MOD_PARAM_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 0, 255, 255, 255, 255, 255, 1, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 2, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

const char* const MACRO_PARAM_KIND_ToStringMap[] = {
    "INVALID", // 0
    "ID", // 1
    "EXPR", // 2
    "FIELD", // 3
    "TYPE", // 4
    "ID_DEF", // 5
    "STMT_LIST", // 6
    "EXPR_LIST_REST", // 7
};
const char* EnumToString(MACRO_PARAM_KIND x) { return MACRO_PARAM_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind MACRO_PARAM_KIND_FromStringMap[] = {
    {"EXPR", 2},
    {"EXPR_LIST_REST", 7},
    {"FIELD", 3},
    {"ID", 1},
    {"ID_DEF", 5},
    {"INVALID", 0},
    {"STMT_LIST", 6},
    {"TYPE", 4},
    {"ZZZ", 0},
};

const uint8_t MACRO_PARAM_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 0, 2, 255, 255, 3, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 6, 7, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

const char* const MACRO_RESULT_KIND_ToStringMap[] = {
    "INVALID", // 0
    "STMT", // 1
    "STMT_LIST", // 2
    "EXPR", // 3
    "EXPR_LIST", // 4
    "TYPE", // 5
};
const char* EnumToString(MACRO_RESULT_KIND x) { return MACRO_RESULT_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind MACRO_RESULT_KIND_FromStringMap[] = {
    {"EXPR", 3},
    {"EXPR_LIST", 4},
    {"INVALID", 0},
    {"STMT", 1},
    {"STMT_LIST", 2},
    {"TYPE", 5},
    {"ZZZ", 0},
};

const uint8_t MACRO_RESULT_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 0, 255, 255, 255, 2, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 3, 5, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

const char* const BASE_TYPE_KIND_ToStringMap[] = {
    "invalid", // 0
    "", // 1
    "", // 2
    "", // 3
    "", // 4
    "", // 5
    "", // 6
    "", // 7
    "", // 8
    "", // 9
    "", // 10
    "", // 11
    "", // 12
    "", // 13
    "", // 14
    "", // 15
    "sint", // 16
    "s8", // 17
    "s16", // 18
    "s32", // 19
    "s64", // 20
    "", // 21
    "", // 22
    "", // 23
    "", // 24
    "", // 25
    "", // 26
    "", // 27
    "", // 28
    "", // 29
    "", // 30
    "", // 31
    "uint", // 32
    "u8", // 33
    "u16", // 34
    "u32", // 35
    "u64", // 36
    "", // 37
    "", // 38
    "", // 39
    "", // 40
    "", // 41
    "", // 42
    "", // 43
    "", // 44
    "", // 45
    "", // 46
    "", // 47
    "", // 48
    "", // 49
    "", // 50
    "r32", // 51
    "r64", // 52
    "", // 53
    "", // 54
    "", // 55
    "", // 56
    "", // 57
    "", // 58
    "", // 59
    "", // 60
    "", // 61
    "", // 62
    "", // 63
    "", // 64
    "bool", // 65
    "", // 66
    "", // 67
    "", // 68
    "", // 69
    "", // 70
    "", // 71
    "", // 72
    "", // 73
    "", // 74
    "", // 75
    "", // 76
    "", // 77
    "", // 78
    "", // 79
    "typeid", // 80
    "", // 81
    "", // 82
    "", // 83
    "", // 84
    "", // 85
    "", // 86
    "", // 87
    "", // 88
    "", // 89
    "", // 90
    "", // 91
    "", // 92
    "", // 93
    "", // 94
    "", // 95
    "void", // 96
    "noret", // 97
};
const char* EnumToString(BASE_TYPE_KIND x) { return BASE_TYPE_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind BASE_TYPE_KIND_FromStringMap[] = {
    {"bool", 65},
    {"invalid", 0},
    {"noret", 97},
    {"r32", 51},
    {"r64", 52},
    {"s16", 18},
    {"s32", 19},
    {"s64", 20},
    {"s8", 17},
    {"sint", 16},
    {"typeid", 80},
    {"u16", 34},
    {"u32", 35},
    {"u64", 36},
    {"u8", 33},
    {"uint", 32},
    {"void", 96},
    {"ZZZ", 0},
};

const uint8_t BASE_TYPE_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 0, 255, 255, 255, 255, 255, 255, 1, 255, 255, 255, 255, 2, 255,
 255, 255, 3, 5, 10, 11, 16, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

const struct StringKind ASSIGNMENT_KIND_FromStringMap[] = {
    {"%=", 5},
    {"&=", 12},
    {"*=", 4},
    {"+=", 1},
    {"-=", 2},
    {"/=", 3},
    {"<<<=", 11},
    {"<<=", 9},
    {">>=", 8},
    {">>>=", 10},
    {"max=", 7},
    {"min=", 6},
    {"|=", 13},
    {"~=", 14},
    {"ZZZ", 0},
};

const uint8_t ASSIGNMENT_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 0, 1, 255, 255, 255, 2, 3, 255, 4, 255, 5,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 6, 255, 8, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 10, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 12, 255, 13, 255,
};

const char* const ASSIGNMENT_ToStringMap[] = {
    "", // 0
    "+=", // 1
    "-=", // 2
    "/=", // 3
    "*=", // 4
    "%=", // 5
    "min=", // 6
    "max=", // 7
    ">>=", // 8
    "<<=", // 9
    ">>>=", // 10
    "<<<=", // 11
    "&=", // 12
    "|=", // 13
    "~=", // 14
};
const char* EnumToString_ASSIGNMENT(BINARY_EXPR_KIND x) { return ASSIGNMENT_ToStringMap[unsigned(x)]; }


const char* const POINTER_EXPR_KIND_ToStringMap[] = {
    "", // 0
    "ptr_inc", // 1
    "ptr_dec", // 2
};
const char* EnumToString(POINTER_EXPR_KIND x) { return POINTER_EXPR_KIND_ToStringMap[unsigned(x)]; }


const char* const BINARY_EXPR_KIND_ToStringMap[] = {
    "", // 0
    "+", // 1
    "-", // 2
    "/", // 3
    "*", // 4
    "%", // 5
    "min", // 6
    "max", // 7
    ">>", // 8
    "<<", // 9
    ">>>", // 10
    "<<<", // 11
    "&", // 12
    "|", // 13
    "~", // 14
    "==", // 15
    "!=", // 16
    "<", // 17
    "<=", // 18
    ">", // 19
    ">=", // 20
    "&&", // 21
    "||", // 22
    "ptr_diff", // 23
};
const char* EnumToString(BINARY_EXPR_KIND x) { return BINARY_EXPR_KIND_ToStringMap[unsigned(x)]; }


const char* const UNARY_EXPR_KIND_ToStringMap[] = {
    "", // 0
    "!", // 1
    "-", // 2
    "abs", // 3
    "sqrt", // 4
};
const char* EnumToString(UNARY_EXPR_KIND x) { return UNARY_EXPR_KIND_ToStringMap[unsigned(x)]; }


const char* const NT_ToStringMap[] = {
    "invalid", // 0
    "Case", // 1
    "DefEnum", // 2
    "DefFun", // 3
    "DefGlobal", // 4
    "DefMacro", // 5
    "DefMod", // 6
    "DefRec", // 7
    "DefType", // 8
    "DefVar", // 9
    "EnumVal", // 10
    "EphemeralList", // 11
    "Expr1", // 12
    "Expr2", // 13
    "Expr3", // 14
    "ExprAddrOf", // 15
    "ExprAs", // 16
    "ExprBitCast", // 17
    "ExprCall", // 18
    "ExprDeref", // 19
    "ExprField", // 20
    "ExprFront", // 21
    "ExprIndex", // 22
    "ExprIs", // 23
    "ExprLen", // 24
    "ExprNarrow", // 25
    "ExprOffsetof", // 26
    "ExprParen", // 27
    "ExprPointer", // 28
    "ExprSizeof", // 29
    "ExprSrcLoc", // 30
    "ExprStmt", // 31
    "ExprStringify", // 32
    "ExprTypeId", // 33
    "ExprUnionTag", // 34
    "ExprUnionUntagged", // 35
    "ExprUnwrap", // 36
    "ExprWiden", // 37
    "ExprWrap", // 38
    "FunParam", // 39
    "Id", // 40
    "Import", // 41
    "MacroFor", // 42
    "MacroId", // 43
    "MacroInvoke", // 44
    "MacroParam", // 45
    "ModParam", // 46
    "RecField", // 47
    "StmtAssignment", // 48
    "StmtBlock", // 49
    "StmtBreak", // 50
    "StmtCompoundAssignment", // 51
    "StmtCond", // 52
    "StmtContinue", // 53
    "StmtDefer", // 54
    "StmtExpr", // 55
    "StmtIf", // 56
    "StmtReturn", // 57
    "StmtStaticAssert", // 58
    "StmtTrap", // 59
    "TypeAuto", // 60
    "TypeBase", // 61
    "TypeFun", // 62
    "TypeOf", // 63
    "TypePtr", // 64
    "TypeSpan", // 65
    "TypeUnion", // 66
    "TypeUnionDelta", // 67
    "TypeVec", // 68
    "ValAuto", // 69
    "ValCompound", // 70
    "ValNum", // 71
    "ValPoint", // 72
    "ValSpan", // 73
    "ValString", // 74
    "ValUndef", // 75
    "ValVoid", // 76
};
const char* EnumToString(NT x) { return NT_ToStringMap[unsigned(x)]; }


const char* const NFD_SLOT_ToStringMap[] = {
    "invalid", // 0
    "args", // 1
    "args_mod", // 2
    "body", // 3
    "body_f", // 4
    "body_for", // 5
    "body_macro", // 6
    "body_mod", // 7
    "body_t", // 8
    "callee", // 9
    "cases", // 10
    "cond", // 11
    "container", // 12
    "enum_name", // 13
    "expr", // 14
    "expr1", // 15
    "expr2", // 16
    "expr_bound_or_undef", // 17
    "expr_f", // 18
    "expr_index", // 19
    "expr_lhs", // 20
    "expr_ret", // 21
    "expr_rhs", // 22
    "expr_size", // 23
    "expr_t", // 24
    "field", // 25
    "fields", // 26
    "gen_ids", // 27
    "initial_or_undef_or_auto", // 28
    "inits", // 29
    "items", // 30
    "label", // 31
    "lhs", // 32
    "message", // 33
    "name", // 34
    "name_list", // 35
    "number", // 36
    "params", // 37
    "params_macro", // 38
    "params_mod", // 39
    "path", // 40
    "point_or_undef", // 41
    "pointer", // 42
    "result", // 43
    "size", // 44
    "string", // 45
    "subtrahend", // 46
    "target", // 47
    "type", // 48
    "type_or_auto", // 49
    "types", // 50
    "value_or_auto", // 51
    "value_or_undef", // 52
};
const char* EnumToString(NFD_SLOT x) { return NFD_SLOT_ToStringMap[unsigned(x)]; }


const char* const BF_ToStringMap[] = {
    "invalid", // 0
    "builtin", // 1
    "init", // 2
    "fini", // 3
    "extern", // 4
    "cdecl", // 5
    "poly", // 6
    "pub", // 7
    "mut", // 8
    "preserve_mut", // 9
    "ref", // 10
    "colon", // 11
    "wrapped", // 12
    "unchecked", // 13
    "untagged", // 14
    "arg_ref", // 15
    "res_ref", // 16
};
const char* EnumToString(BF x) { return BF_ToStringMap[unsigned(x)]; }


const struct StringKind BF_FromStringMap[] = {
    {"arg_ref", 15},
    {"builtin", 1},
    {"cdecl", 5},
    {"colon", 11},
    {"extern", 4},
    {"fini", 3},
    {"init", 2},
    {"invalid", 0},
    {"mut", 8},
    {"poly", 6},
    {"preserve_mut", 9},
    {"pub", 7},
    {"ref", 10},
    {"res_ref", 16},
    {"unchecked", 13},
    {"untagged", 14},
    {"wrapped", 12},
    {"ZZZ", 0},
};

const uint8_t BF_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 0, 1, 2, 255, 4, 5, 255, 255, 6, 255, 255, 255, 8, 255, 255,
 9, 255, 12, 255, 255, 14, 255, 16, 255, 255, 255, 255, 255, 255, 255, 255,
};

const char* const BF_CURLY_ToStringMap[] = {
    "{{invalid}}", // 0
    "{{builtin}}", // 1
    "{{init}}", // 2
    "{{fini}}", // 3
    "{{extern}}", // 4
    "{{cdecl}}", // 5
    "{{poly}}", // 6
    "{{pub}}", // 7
    "{{mut}}", // 8
    "{{preserve_mut}}", // 9
    "{{ref}}", // 10
    "{{colon}}", // 11
    "{{wrapped}}", // 12
    "{{unchecked}}", // 13
    "{{untagged}}", // 14
    "{{arg_ref}}", // 15
    "{{res_ref}}", // 16
};
const char* EnumToString_CURLY(BF x) { return BF_CURLY_ToStringMap[unsigned(x)]; }


const std::map<std::string_view, NT> KeywordToNodeTypeMap = {
    {"case", NT::Case},
    {"enum", NT::DefEnum},
    {"fun", NT::DefFun},
    {"global", NT::DefGlobal},
    {"global!", NT::DefGlobal},
    {"macro", NT::DefMacro},
    {"module", NT::DefMod},
    {"rec", NT::DefRec},
    {"type", NT::DefType},
    {"let", NT::DefVar},
    {"let!", NT::DefVar},
    {"as", NT::ExprAs},
    {"bitwise_as", NT::ExprBitCast},
    {"front", NT::ExprFront},
    {"front!", NT::ExprFront},
    {"at", NT::ExprIndex},
    {"at!", NT::ExprIndex},
    {"is", NT::ExprIs},
    {"len", NT::ExprLen},
    {"narrow_as", NT::ExprNarrow},
    {"narrow_as!", NT::ExprNarrow},
    {"offset_of", NT::ExprOffsetof},
    {"size_of", NT::ExprSizeof},
    {"srcloc", NT::ExprSrcLoc},
    {"expr", NT::ExprStmt},
    {"stringify", NT::ExprStringify},
    {"typeid_of", NT::ExprTypeId},
    {"union_tag", NT::ExprUnionTag},
    {"union_untagged", NT::ExprUnionUntagged},
    {"unwrap", NT::ExprUnwrap},
    {"widen_as", NT::ExprWiden},
    {"wrap_as", NT::ExprWrap},
    {"import", NT::Import},
    {"mfor", NT::MacroFor},
    {"block", NT::StmtBlock},
    {"break", NT::StmtBreak},
    {"cond", NT::StmtCond},
    {"continue", NT::StmtContinue},
    {"defer", NT::StmtDefer},
    {"do", NT::StmtExpr},
    {"if", NT::StmtIf},
    {"return", NT::StmtReturn},
    {"static_assert", NT::StmtStaticAssert},
    {"trap", NT::StmtTrap},
    {"auto", NT::TypeAuto},
    {"funtype", NT::TypeFun},
    {"type_of", NT::TypeOf},
    {"span", NT::TypeSpan},
    {"span!", NT::TypeSpan},
    {"union", NT::TypeUnion},
    {"union!", NT::TypeUnion},
    {"union_delta", NT::TypeUnionDelta},
    {"vec", NT::TypeVec},
    {"auto_val", NT::ValAuto},
    {"make_span", NT::ValSpan},
    {"undef", NT::ValUndef},
    {"void_val", NT::ValVoid},
};
/* @AUTOGEN-END@ */
// clang-format on

// =======================================
// Str Helpers
// =======================================

ImmutablePool gStringPool(4);

// =======================================
// Name Helpers
// =======================================
ImmutablePool gNamePool(4);

// =======================================
// All Stripes
// =======================================
struct Alloc {
  uint32_t dummy;
};
struct Stripe<Alloc, Node> gNodeAlloc("NodeAlloc");

struct Stripe<NodeCore, Node> gNodeCore("NodeCore");
struct Stripe<NodeExtra, Node> gNodeExtra("NodeExtra");
struct Stripe<NodeAuxTyping, Node> gNodeAuxTyping("NodeAuxTyping");
struct Stripe<NodeValidation, Node> gNodeValidation("NodeValidation");

StripeBase* const gAllStripesNode[] = {&gNodeAlloc,      &gNodeCore,
                                       &gNodeExtra,      &gNodeAuxTyping,
                                       &gNodeValidation, nullptr};
struct StripeGroup gStripeGroupNode("Node", gAllStripesNode, 256 * 1024);

// =======================================

int string_view_cmp(const char* a, std::string_view b) {
  int x = strncmp(a, b.data(), b.size());
  if (x == 0 && a[b.size()] != 0) return 1;
  return x;
}

static uint8_t LinearSearch(const StringKind* table, const uint8_t* jumper,
                            std::string_view sym, uint8_t def_val) {
  ASSERT(sym[0] <= 127, "");
  uint8_t start = jumper[uint8_t(sym[0])];
  if (start == 255) return def_val;
  while (true) {
    int cmp = string_view_cmp(table[start].name, sym);
    if (cmp == 0) {
      return table[start].kind;
    }
    ++start;
    if (cmp > 0) break;
  }
  return def_val;
}

MACRO_PARAM_KIND MACRO_PARAM_KIND_FromString(std::string_view name) {
  return MACRO_PARAM_KIND(LinearSearch(MACRO_PARAM_KIND_FromStringMap,
                                       MACRO_PARAM_KIND_Jumper, name, 0));
}

MACRO_RESULT_KIND MACRO_RESULT_KIND_FromString(std::string_view name) {
  return MACRO_RESULT_KIND(LinearSearch(MACRO_RESULT_KIND_FromStringMap,
                                        MACRO_RESULT_KIND_Jumper, name, 0));
}

MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name) {
  return MOD_PARAM_KIND(LinearSearch(MOD_PARAM_KIND_FromStringMap,
                                     MOD_PARAM_KIND_Jumper, name, 0));
}

BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name) {
  return BASE_TYPE_KIND(LinearSearch(BASE_TYPE_KIND_FromStringMap,
                                     BASE_TYPE_KIND_Jumper, name, 0));
}

BINARY_EXPR_KIND ASSIGNMENT_KIND_FromString(std::string_view name) {
  return BINARY_EXPR_KIND(LinearSearch(ASSIGNMENT_KIND_FromStringMap,
                                       ASSIGNMENT_KIND_Jumper, name, 0));
}

BF BF_FromString(std::string_view name) {
  return BF(LinearSearch(BF_FromStringMap, BF_Jumper, name, 0));
}

NT KeywordToNT(std::string_view kw) {
  auto it = KeywordToNodeTypeMap.find(kw);
  if (it == KeywordToNodeTypeMap.end()) return NT::invalid;
  return it->second;
}

void RemoveNodesOfType(Node node, NT kind) {
  auto replacer = [kind](Node node, Node parent) -> Node {
    if (Node_kind(node) == kind) {
      NodeFreeRecursively(node);
      return kNodeInvalid;
    }
    return node;
  };
  MaybeReplaceAstRecursively(node, replacer);
}

Node NodeCloneRecursively(Node node, std::map<Node, Node>* symbol_map,
                          std::map<Node, Node>* target_map) {
  Node clone = NodeCloneBasics(node);

  switch (Node_kind(clone)) {
    case NT::DefVar:
      (*symbol_map)[node] = clone;
      break;
    case NT::StmtBlock:
    case NT::ExprStmt:
      (*target_map)[node] = clone;
      break;
    case NT::Id:
      Node_x_symbol(clone) = GetWithDefault(*symbol_map, Node_x_symbol(node));
      break;
    case NT::StmtBreak:
    case NT::StmtContinue:
    case NT::StmtReturn:
      Node_x_target(clone) = GetWithDefault(*target_map, Node_x_target(node));
      break;
    default:
      break;
  }

  auto& core_clone = gNodeCore[clone];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core_clone.children_node[i];
    if (child.raw_kind() == kKindStr || child.raw_kind() == kKindName ||
        child.isnull()) {
      core_clone.children_node[i] = child;
      continue;
    }
    Node clone = NodeCloneRecursively(child, symbol_map, target_map);
    core_clone.children_node[i] = clone;

    while (!Node_next(child).isnull()) {
      child = Node_next(child);
      Node new_clone = NodeCloneRecursively(child, symbol_map, target_map);
      Node_next(clone) = new_clone;
      clone = new_clone;
    }
  }
  return clone;
}

std::string ExpandStringConstant(Str s) {
  ASSERT(false, "NYI");
  std::string_view payload = StrData(s);
  uint8_t kind = payload[0];
  if (kind != '"') {
    payload.remove_prefix(1);
  }

  if (payload.starts_with("\"\"\"")) {
    payload.remove_prefix(3);
    payload.remove_suffix(3);
  } else {
    payload.remove_prefix(1);
    payload.remove_suffix(1);
  }
  if (kind == 'r') {
    return std::string(payload);
  }

  std::string out;

  if (kind == 'x') {
  } else {
  }
  return "";
}

BASE_TYPE_KIND MakeSint(int bitwidth) {
  switch (bitwidth) {
    case 8:
      return BASE_TYPE_KIND::S8;
    case 16:
      return BASE_TYPE_KIND::S16;
    case 32:
      return BASE_TYPE_KIND::S32;
    case 64:
      return BASE_TYPE_KIND::S64;
    default:
      ASSERT(false, "");
      return BASE_TYPE_KIND::INVALID;
  }
}
BASE_TYPE_KIND MakeUint(int bitwidth) {
  switch (bitwidth) {
    case 8:
      return BASE_TYPE_KIND::U8;
    case 16:
      return BASE_TYPE_KIND::U16;
    case 32:
      return BASE_TYPE_KIND::U32;
    case 64:
      return BASE_TYPE_KIND::U64;
    default:
      ASSERT(false, "");
      return BASE_TYPE_KIND::INVALID;
  }
}

SizeOrDim BaseTypeKindByteSize(BASE_TYPE_KIND kind) {
  static const std::array<int, 4> bztab = {1, 2, 4, 8};

  if (kind == BASE_TYPE_KIND::VOID || kind == BASE_TYPE_KIND::NORET) return SizeOrDim(0);
  int x = (int(kind) & 0xf) - 1;
  ASSERT(0 <= x && x <= bztab.size(), "");
  return SizeOrDim(bztab[x]);
}

}  // namespace cwerg::fe
