#include "FE/cwast_gen.h"

#include <cstdint>
#include <map>

#include "Util/assert.h"

namespace cwerg::fe {

#define BIT_N(x) 1ull << uint64_t(NFD_NODE_FIELD::x)
#define BIT_S(x) 1ull << uint64_t(NFD_STRING_FIELD::x)
#define BIT_B(x) 1ull << uint64_t(NFD_BOOL_FIELD::x)

struct StringKind {
  const char* name;
  uint8_t kind;
};

// clang-format off
/* @AUTOGEN-START@ */
NodeDesc GlobalNodeDescs[] = {
    {}, // invalid
    { BIT_N(cond)| BIT_N(body), 0, 0 }, // Case
    { BIT_N(items), BIT_S(name), BIT_B(pub) }, // DefEnum
    { BIT_N(params)| BIT_N(result)| BIT_N(body), BIT_S(name), BIT_B(init)| BIT_B(fini)| BIT_B(pub)| BIT_B(ref)| BIT_B(poly)| BIT_B(externx)| BIT_B(cdecl) }, // DefFun
    { BIT_N(type_or_auto)| BIT_N(initial_or_undef_or_auto), BIT_S(name), BIT_B(pub)| BIT_B(mut)| BIT_B(ref)| BIT_B(cdecl) }, // DefGlobal
    { BIT_N(params_macro)| BIT_N(gen_ids)| BIT_N(body_macro), BIT_S(name), BIT_B(pub)| BIT_B(builtin) }, // DefMacro
    { BIT_N(params_mod)| BIT_N(body_mod), 0, BIT_B(builtin) }, // DefMod
    { BIT_N(fields), BIT_S(name), BIT_B(pub) }, // DefRec
    { BIT_N(type), BIT_S(name), BIT_B(pub)| BIT_B(wrapped) }, // DefType
    { BIT_N(type_or_auto)| BIT_N(initial_or_undef_or_auto), BIT_S(name), BIT_B(mut)| BIT_B(ref) }, // DefVar
    { BIT_N(value_or_auto), BIT_S(name), 0 }, // EnumVal
    { BIT_N(args), 0, BIT_B(colon) }, // EphemeralList
    { BIT_N(expr), 0, 0 }, // Expr1
    { BIT_N(expr1)| BIT_N(expr2), 0, 0 }, // Expr2
    { BIT_N(cond)| BIT_N(expr_t)| BIT_N(expr_f), 0, 0 }, // Expr3
    { BIT_N(expr_lhs), 0, BIT_B(mut) }, // ExprAddrOf
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprAs
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprBitCast
    { BIT_N(callee)| BIT_N(args), 0, 0 }, // ExprCall
    { BIT_N(expr), 0, 0 }, // ExprDeref
    { BIT_N(container)| BIT_N(field), 0, 0 }, // ExprField
    { BIT_N(container), 0, BIT_B(mut)| BIT_B(preserve_mut) }, // ExprFront
    { BIT_N(container)| BIT_N(expr_index), 0, BIT_B(unchecked) }, // ExprIndex
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprIs
    { BIT_N(container), 0, 0 }, // ExprLen
    { BIT_N(expr)| BIT_N(type), 0, BIT_B(unchecked) }, // ExprNarrow
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
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprUnsafeCast
    { BIT_N(expr), 0, 0 }, // ExprUnwrap
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprWiden
    { BIT_N(expr)| BIT_N(type), 0, 0 }, // ExprWrap
    { BIT_N(type), BIT_S(name), BIT_B(arg_ref)| BIT_B(res_ref) }, // FunParam
    { 0, BIT_S(mod_name)| BIT_S(base_name)| BIT_S(enum_name), 0 }, // Id
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
    { BIT_N(type), 0, BIT_B(mut) }, // TypePtr
    { BIT_N(type), 0, BIT_B(mut) }, // TypeSpan
    { BIT_N(types), 0, BIT_B(untagged) }, // TypeUnion
    { BIT_N(type)| BIT_N(subtrahend), 0, 0 }, // TypeUnionDelta
    { BIT_N(size)| BIT_N(type), 0, 0 }, // TypeVec
    { 0, 0, 0 }, // ValAuto
    { BIT_N(type_or_auto)| BIT_N(inits), 0, 0 }, // ValCompound
    { 0, 0, 0 }, // ValFalse
    { 0, BIT_S(number), 0 }, // ValNum
    { BIT_N(value_or_undef)| BIT_N(point), 0, 0 }, // ValPoint
    { BIT_N(pointer)| BIT_N(expr_size), 0, 0 }, // ValSpan
    { 0, BIT_S(string), 0 }, // ValString
    { 0, 0, 0 }, // ValTrue
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
    "STMT_LIST", // 2
    "EXPR_LIST", // 3
    "EXPR", // 4
    "STMT", // 5
    "FIELD", // 6
    "TYPE", // 7
    "EXPR_LIST_REST", // 8
};
const char* EnumToString(MACRO_PARAM_KIND x) { return MACRO_PARAM_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind MACRO_PARAM_KIND_FromStringMap[] = {
    {"EXPR", 4},
    {"EXPR_LIST", 3},
    {"EXPR_LIST_REST", 8},
    {"FIELD", 6},
    {"ID", 1},
    {"INVALID", 0},
    {"STMT", 5},
    {"STMT_LIST", 2},
    {"TYPE", 7},
    {"ZZZ", 0},
};

const uint8_t MACRO_PARAM_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 0, 3, 255, 255, 4, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 6, 8, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

const char* const STR_KIND_ToStringMap[] = {
    "NORMAL", // 0
    "NORMAL_TRIPLE", // 1
    "RAW", // 2
    "RAW_TRIPLE", // 3
    "HEX", // 4
    "HEX_TRIPLE", // 5
};
const char* EnumToString(STR_KIND x) { return STR_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind STR_KIND_FromStringMap[] = {
    {"HEX", 4},
    {"HEX_TRIPLE", 5},
    {"NORMAL", 0},
    {"NORMAL_TRIPLE", 1},
    {"RAW", 2},
    {"RAW_TRIPLE", 3},
    {"ZZZ", 0},
};

const uint8_t STR_KIND_Jumper[128] = {
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
 255, 255, 255, 255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255, 2, 255,
 255, 255, 4, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
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
    "sint", // 10
    "s8", // 11
    "s16", // 12
    "s32", // 13
    "s64", // 14
    "", // 15
    "", // 16
    "", // 17
    "", // 18
    "", // 19
    "uint", // 20
    "u8", // 21
    "u16", // 22
    "u32", // 23
    "u64", // 24
    "", // 25
    "", // 26
    "", // 27
    "", // 28
    "", // 29
    "r32", // 30
    "r64", // 31
    "", // 32
    "", // 33
    "", // 34
    "", // 35
    "", // 36
    "", // 37
    "", // 38
    "", // 39
    "void", // 40
    "noret", // 41
    "bool", // 42
    "typeid", // 43
};
const char* EnumToString(BASE_TYPE_KIND x) { return BASE_TYPE_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind BASE_TYPE_KIND_FromStringMap[] = {
    {"bool", 42},
    {"invalid", 0},
    {"noret", 41},
    {"r32", 30},
    {"r64", 31},
    {"s16", 12},
    {"s32", 13},
    {"s64", 14},
    {"s8", 11},
    {"sint", 10},
    {"typeid", 43},
    {"u16", 22},
    {"u32", 23},
    {"u64", 24},
    {"u8", 21},
    {"uint", 20},
    {"void", 40},
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

const char* const ASSIGNMENT_KIND_ToStringMap[] = {
    "", // 0
    "+=", // 1
    "-=", // 2
    "/=", // 3
    "*=", // 4
    "%=", // 5
    "min=", // 6
    "max=", // 7
    "", // 8
    "", // 9
    "&=", // 10
    "|=", // 11
    "~=", // 12
    "", // 13
    "", // 14
    "", // 15
    "", // 16
    "", // 17
    "", // 18
    "", // 19
    "", // 20
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
    "", // 32
    "", // 33
    "", // 34
    "", // 35
    "", // 36
    "", // 37
    "", // 38
    "", // 39
    ">>=", // 40
    "<<=", // 41
    ">>>=", // 42
    "<<<=", // 43
};
const char* EnumToString(ASSIGNMENT_KIND x) { return ASSIGNMENT_KIND_ToStringMap[unsigned(x)]; }


const struct StringKind ASSIGNMENT_KIND_FromStringMap[] = {
    {"%=", 5},
    {"&=", 10},
    {"*=", 4},
    {"+=", 1},
    {"-=", 2},
    {"/=", 3},
    {"<<<=", 43},
    {"<<=", 41},
    {">>=", 40},
    {">>>=", 42},
    {"max=", 7},
    {"min=", 6},
    {"|=", 11},
    {"~=", 12},
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
    "", // 8
    "", // 9
    "&", // 10
    "|", // 11
    "~", // 12
    "", // 13
    "", // 14
    "", // 15
    "", // 16
    "", // 17
    "", // 18
    "", // 19
    "==", // 20
    "!=", // 21
    "<", // 22
    "<=", // 23
    ">", // 24
    ">=", // 25
    "", // 26
    "", // 27
    "", // 28
    "", // 29
    "&&", // 30
    "||", // 31
    "", // 32
    "", // 33
    "", // 34
    "", // 35
    "", // 36
    "", // 37
    "", // 38
    "", // 39
    ">>", // 40
    "<<", // 41
    ">>>", // 42
    "<<<", // 43
    "", // 44
    "", // 45
    "", // 46
    "", // 47
    "", // 48
    "", // 49
    "", // 50
    "", // 51
    "ptr_diff", // 52
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
    "ExprUnsafeCast", // 36
    "ExprUnwrap", // 37
    "ExprWiden", // 38
    "ExprWrap", // 39
    "FunParam", // 40
    "Id", // 41
    "Import", // 42
    "MacroFor", // 43
    "MacroId", // 44
    "MacroInvoke", // 45
    "MacroParam", // 46
    "ModParam", // 47
    "RecField", // 48
    "StmtAssignment", // 49
    "StmtBlock", // 50
    "StmtBreak", // 51
    "StmtCompoundAssignment", // 52
    "StmtCond", // 53
    "StmtContinue", // 54
    "StmtDefer", // 55
    "StmtExpr", // 56
    "StmtIf", // 57
    "StmtReturn", // 58
    "StmtStaticAssert", // 59
    "StmtTrap", // 60
    "TypeAuto", // 61
    "TypeBase", // 62
    "TypeFun", // 63
    "TypeOf", // 64
    "TypePtr", // 65
    "TypeSpan", // 66
    "TypeUnion", // 67
    "TypeUnionDelta", // 68
    "TypeVec", // 69
    "ValAuto", // 70
    "ValCompound", // 71
    "ValFalse", // 72
    "ValNum", // 73
    "ValPoint", // 74
    "ValSpan", // 75
    "ValString", // 76
    "ValTrue", // 77
    "ValUndef", // 78
    "ValVoid", // 79
};
const char* EnumToString(NT x) { return NT_ToStringMap[unsigned(x)]; }


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
    {"unsafe_as", NT::ExprUnsafeCast},
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
    {"false", NT::ValFalse},
    {"make_span", NT::ValSpan},
    {"true", NT::ValTrue},
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

struct Stripe<NodeCore, Node> gNodeCore("NodeCore");
struct Stripe<NodeExtra, Node> gNodeExtra("NodeExtra");
StripeBase* const gAllStripesNode[] = {&gNodeCore, &gNodeExtra, nullptr};
struct StripeGroup gStripeGroupNode("Node", gAllStripesNode, 256 * 1024);

struct Stripe<NameCore, Name> gNameCore("NameCore");
StripeBase* const gAllStripesName[] = {&gNameCore, nullptr};
struct StripeGroup gStripeGroupName("Name", gAllStripesName, 256 * 1024);

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

MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name) {
  return MOD_PARAM_KIND(LinearSearch(MOD_PARAM_KIND_FromStringMap,
                                     MOD_PARAM_KIND_Jumper, name, 0));
}

BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name) {
  return BASE_TYPE_KIND(LinearSearch(BASE_TYPE_KIND_FromStringMap,
                                     BASE_TYPE_KIND_Jumper, name, 0));
}

ASSIGNMENT_KIND ASSIGNMENT_KIND_FromString(std::string_view name) {
  return ASSIGNMENT_KIND(LinearSearch(ASSIGNMENT_KIND_FromStringMap,
                                      ASSIGNMENT_KIND_Jumper, name, 0));
}

NT KeywordToNT(std::string_view kw) {
  auto it = KeywordToNodeTypeMap.find(kw);
  if (it == KeywordToNodeTypeMap.end()) return NT::invalid;
  return it->second;
}

}  // namespace cwerg::fe
