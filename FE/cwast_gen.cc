#include "FE/cwast_gen.h"

#include <cstdint>
#include <map>

#include "Util/assert.h"

namespace cwerg::fe {

#define BIT_N(x) 1ull << uint64_t(NFD_NODE_FIELD::x)
#define BIT_S(x) 1ull << uint64_t(NFD_STRING_FIELD::x)
#define BIT_B(x) 1ull << uint32_t(BF::x)

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
const NodeDesc GlobalNodeDescs[] = {
    {}, // invalid
    { BIT_N(cond)| BIT_N(body), 0, 0 }, // Case
    { BIT_N(items), BIT_S(name), BIT_B(PUB) }, // DefEnum
    { BIT_N(params)| BIT_N(result)| BIT_N(body), BIT_S(name), BIT_B(INIT)| BIT_B(FINI)| BIT_B(EXTERN)| BIT_B(CDECL)| BIT_B(POLY)| BIT_B(PUB)| BIT_B(REF) }, // DefFun
    { BIT_N(type_or_auto)| BIT_N(initial_or_undef_or_auto), BIT_S(name), BIT_B(PUB)| BIT_B(MUT)| BIT_B(REF)| BIT_B(CDECL) }, // DefGlobal
    { BIT_N(params_macro)| BIT_N(gen_ids)| BIT_N(body_macro), BIT_S(name), BIT_B(BUILTIN)| BIT_B(PUB) }, // DefMacro
    { BIT_N(params_mod)| BIT_N(body_mod), BIT_S(name), BIT_B(BUILTIN) }, // DefMod
    { BIT_N(fields), BIT_S(name), BIT_B(PUB) }, // DefRec
    { BIT_N(type), BIT_S(name), BIT_B(PUB)| BIT_B(WRAPPED) }, // DefType
    { BIT_N(type_or_auto)| BIT_N(initial_or_undef_or_auto), BIT_S(name), BIT_B(MUT)| BIT_B(REF) }, // DefVar
    { BIT_N(value_or_auto), BIT_S(name), 0 }, // EnumVal
    { BIT_N(args), 0, BIT_B(COLON) }, // EphemeralList
    { BIT_N(expr), 0, 0 }, // Expr1
    { BIT_N(expr1)| BIT_N(expr2), 0, 0 }, // Expr2
    { BIT_N(cond)| BIT_N(expr_t)| BIT_N(expr_f), 0, 0 }, // Expr3
    { BIT_N(expr_lhs), 0, BIT_B(MUT) }, // ExprAddrOf
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprAs
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprBitCast
    { BIT_N(callee)| BIT_N(args), 0, 0 }, // ExprCall
    { BIT_N(expr), 0, 0 }, // ExprDeref
    { BIT_N(container)| BIT_N(field), 0, 0 }, // ExprField
    { BIT_N(container), 0, BIT_B(MUT)| BIT_B(PRESERVE_MUT) }, // ExprFront
    { BIT_N(container)| BIT_N(expr_index), 0, BIT_B(UNCHECKED) }, // ExprIndex
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprIs
    { BIT_N(container), 0, 0 }, // ExprLen
    { BIT_N(expr)| BIT_N(type), 0, BIT_B(UNCHECKED) }, // ExprNarrow
    { BIT_N(type)| BIT_N(field), 0, 0 }, // ExprOffsetof
    { BIT_N(expr), 0, 0 }, // ExprParen
    { BIT_N(expr1)| BIT_N(expr2)| BIT_N(expr_bound_or_undef), 0, 0 }, // ExprPointer
    { BIT_N(type), 0, 0 }, // ExprSizeof
    { BIT_N(expr), 0, 0 }, // ExprSrcLoc
    { BIT_N(body), 0, 0 }, // ExprStmt
    { BIT_N(expr), 0, 0 }, // ExprStringify
    { BIT_N(type), 0, 0 }, // ExprTypeId
    { BIT_N(expr), 0, 0 }, // ExprUnionTag
    { BIT_N(expr), 0, 0 }, // ExprUnionUntagged
    { BIT_N(expr), 0, 0 }, // ExprUnwrap
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprWiden
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprWrap
    { BIT_N(type), BIT_S(name), BIT_B(ARG_REF)| BIT_B(RES_REF) }, // FunParam
    { 0, BIT_S(name)| BIT_S(enum_name), 0 }, // Id
    { BIT_N(args_mod), BIT_S(name)| BIT_S(path), 0 }, // Import
    { BIT_N(body_for), BIT_S(name)| BIT_S(name_list), 0 }, // MacroFor
    { 0, BIT_S(name), 0 }, // MacroId
    { BIT_N(args), BIT_S(name), 0 }, // MacroInvoke
    { 0, BIT_S(name), 0 }, // MacroParam
    { 0, BIT_S(name), 0 }, // ModParam
    { BIT_N(type), BIT_S(name), 0 }, // RecField
    { BIT_N(lhs)| BIT_N(expr_rhs), 0, 0 }, // StmtAssignment
    { BIT_N(body), BIT_S(label), 0 }, // StmtBlock
    { 0, BIT_S(target), 0 }, // StmtBreak
    { BIT_N(lhs)| BIT_N(expr_rhs), 0, 0 }, // StmtCompoundAssignment
    { BIT_N(cases), 0, 0 }, // StmtCond
    { 0, BIT_S(target), 0 }, // StmtContinue
    { BIT_N(body), 0, 0 }, // StmtDefer
    { BIT_N(expr), 0, 0 }, // StmtExpr
    { BIT_N(cond)| BIT_N(body_t)| BIT_N(body_f), 0, 0 }, // StmtIf
    { BIT_N(expr_ret), 0, 0 }, // StmtReturn
    { BIT_N(cond), BIT_S(message), 0 }, // StmtStaticAssert
    { 0, 0, 0 }, // StmtTrap
    { 0, 0, 0 }, // TypeAuto
    { 0, 0, 0 }, // TypeBase
    { BIT_N(params)| BIT_N(result), 0, 0 }, // TypeFun
    { BIT_N(expr), 0, 0 }, // TypeOf
    { BIT_N(type), 0, BIT_B(MUT) }, // TypePtr
    { BIT_N(type), 0, BIT_B(MUT) }, // TypeSpan
    { BIT_N(types), 0, BIT_B(UNTAGGED) }, // TypeUnion
    { BIT_N(type)| BIT_N(subtrahend), 0, 0 }, // TypeUnionDelta
    { BIT_N(size)| BIT_N(type), 0, 0 }, // TypeVec
    { 0, 0, 0 }, // ValAuto
    { BIT_N(type_or_auto)| BIT_N(inits), 0, 0 }, // ValCompound
    { 0, BIT_S(number), 0 }, // ValNum
    { BIT_N(value_or_undef)| BIT_N(point_or_undef), 0, 0 }, // ValPoint
    { BIT_N(pointer)| BIT_N(expr_size), 0, 0 }, // ValSpan
    { 0, BIT_S(string), 0 }, // ValString
    { 0, 0, 0 }, // ValUndef
    { 0, 0, 0 }, // ValVoid
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
    "", // 97
    "", // 98
    "", // 99
    "", // 100
    "", // 101
    "", // 102
    "", // 103
    "", // 104
    "", // 105
    "", // 106
    "", // 107
    "", // 108
    "", // 109
    "", // 110
    "", // 111
    "noret", // 112
};
const char* EnumToString(BASE_TYPE_KIND x) { return BASE_TYPE_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind BASE_TYPE_KIND_FromStringMap[] = {
    {"bool", 65},
    {"invalid", 0},
    {"noret", 112},
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

int BaseTypeKindByteSize(BASE_TYPE_KIND kind) {
  static const std::array<int, 4> bztab = {1, 2, 4, 8};

  if (kind == BASE_TYPE_KIND::VOID || kind == BASE_TYPE_KIND::NORET) return 0;
  int x = (int(kind) & 0xf) - 1;
  ASSERT(0 <= x && x <= bztab.size(), "");
  return bztab[x];
}

}  // namespace cwerg::fe
