#include <cstdint>

#include "FE/cwast_gen.h"

namespace cwerg::fe {


#define BIT_NODE(x) 1ull << uint64_t(NFD_NODE_FIELD::x)
#define BIT_STRING(x) 1ull << uint64_t(NFD_STRING_FIELD::x)

/* @AUTOGEN-START@ */
NodeDesc GlobalNodeDescs[] = {
    {}, // invalid
    { BIT_NODE(cond)| BIT_NODE(body) , 0 }, // Case
    { BIT_NODE(items) , BIT_STRING(name) }, // DefEnum
    { BIT_NODE(params)| BIT_NODE(result)| BIT_NODE(body) , BIT_STRING(name) }, // DefFun
    { BIT_NODE(type_or_auto)| BIT_NODE(initial_or_undef_or_auto) , BIT_STRING(name) }, // DefGlobal
    { BIT_NODE(params_macro)| BIT_NODE(gen_ids)| BIT_NODE(body_macro) , BIT_STRING(name) }, // DefMacro
    { BIT_NODE(params_mod)| BIT_NODE(body_mod) , 0 }, // DefMod
    { BIT_NODE(fields) , BIT_STRING(name) }, // DefRec
    { BIT_NODE(type) , BIT_STRING(name) }, // DefType
    { BIT_NODE(type_or_auto)| BIT_NODE(initial_or_undef_or_auto) , BIT_STRING(name) }, // DefVar
    { BIT_NODE(value_or_auto) , BIT_STRING(name) }, // EnumVal
    { BIT_NODE(args) , 0 }, // EphemeralList
    { BIT_NODE(expr) , 0 }, // Expr1
    { BIT_NODE(expr1)| BIT_NODE(expr2) , 0 }, // Expr2
    { BIT_NODE(cond)| BIT_NODE(expr_t)| BIT_NODE(expr_f) , 0 }, // Expr3
    { BIT_NODE(expr_lhs) , 0 }, // ExprAddrOf
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprAs
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprBitCast
    { BIT_NODE(callee)| BIT_NODE(args) , 0 }, // ExprCall
    { BIT_NODE(expr) , 0 }, // ExprDeref
    { BIT_NODE(container)| BIT_NODE(field) , 0 }, // ExprField
    { BIT_NODE(container) , 0 }, // ExprFront
    { BIT_NODE(container)| BIT_NODE(expr_index) , 0 }, // ExprIndex
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprIs
    { BIT_NODE(container) , 0 }, // ExprLen
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprNarrow
    { BIT_NODE(type)| BIT_NODE(field) , 0 }, // ExprOffsetof
    { BIT_NODE(expr) , 0 }, // ExprParen
    { BIT_NODE(expr1)| BIT_NODE(expr2)| BIT_NODE(expr_bound_or_undef) , 0 }, // ExprPointer
    { BIT_NODE(type) , 0 }, // ExprSizeof
    { BIT_NODE(expr) , 0 }, // ExprSrcLoc
    { BIT_NODE(body) , 0 }, // ExprStmt
    { BIT_NODE(expr) , 0 }, // ExprStringify
    { BIT_NODE(type) , 0 }, // ExprTypeId
    { BIT_NODE(expr) , 0 }, // ExprUnionTag
    { BIT_NODE(expr) , 0 }, // ExprUnionUntagged
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprUnsafeCast
    { BIT_NODE(expr) , 0 }, // ExprUnwrap
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprWiden
    { BIT_NODE(expr)| BIT_NODE(type) , 0 }, // ExprWrap
    { BIT_NODE(type) , BIT_STRING(name) }, // FunParam
    { 0 , BIT_STRING(mod_name)| BIT_STRING(base_name)| BIT_STRING(enum_name) }, // Id
    { BIT_NODE(args_mod) , BIT_STRING(name)| BIT_STRING(path) }, // Import
    { BIT_NODE(body_for) , BIT_STRING(name)| BIT_STRING(name_list) }, // MacroFor
    { 0 , BIT_STRING(name) }, // MacroId
    { BIT_NODE(args) , BIT_STRING(name) }, // MacroInvoke
    { 0 , BIT_STRING(name) }, // MacroParam
    { BIT_NODE(type_or_auto)| BIT_NODE(initial_or_undef_or_auto) , BIT_STRING(name) }, // MacroVar
    { 0 , BIT_STRING(name) }, // ModParam
    { BIT_NODE(type) , BIT_STRING(name) }, // RecField
    { BIT_NODE(lhs)| BIT_NODE(expr_rhs) , 0 }, // StmtAssignment
    { BIT_NODE(body) , BIT_STRING(label) }, // StmtBlock
    { 0 , BIT_STRING(target) }, // StmtBreak
    { BIT_NODE(lhs)| BIT_NODE(expr_rhs) , 0 }, // StmtCompoundAssignment
    { BIT_NODE(cases) , 0 }, // StmtCond
    { 0 , BIT_STRING(target) }, // StmtContinue
    { BIT_NODE(body) , 0 }, // StmtDefer
    { BIT_NODE(expr) , 0 }, // StmtExpr
    { BIT_NODE(cond)| BIT_NODE(body_t)| BIT_NODE(body_f) , 0 }, // StmtIf
    { BIT_NODE(expr_ret) , 0 }, // StmtReturn
    { BIT_NODE(cond) , BIT_STRING(message) }, // StmtStaticAssert
    { 0 , 0 }, // StmtTrap
    { 0 , 0 }, // TypeAuto
    { 0 , 0 }, // TypeBase
    { BIT_NODE(params)| BIT_NODE(result) , 0 }, // TypeFun
    { BIT_NODE(expr) , 0 }, // TypeOf
    { BIT_NODE(type) , 0 }, // TypePtr
    { BIT_NODE(type) , 0 }, // TypeSpan
    { BIT_NODE(types) , 0 }, // TypeUnion
    { BIT_NODE(type)| BIT_NODE(subtrahend) , 0 }, // TypeUnionDelta
    { BIT_NODE(size)| BIT_NODE(type) , 0 }, // TypeVec
    { 0 , 0 }, // ValAuto
    { BIT_NODE(type_or_auto)| BIT_NODE(inits) , 0 }, // ValCompound
    { 0 , 0 }, // ValFalse
    { 0 , BIT_STRING(number) }, // ValNum
    { BIT_NODE(value_or_undef)| BIT_NODE(point) , 0 }, // ValPoint
    { BIT_NODE(pointer)| BIT_NODE(expr_size) , 0 }, // ValSpan
    { 0 , BIT_STRING(string) }, // ValString
    { 0 , 0 }, // ValTrue
    { 0 , 0 }, // ValUndef
    { 0 , 0 }, // ValVoid
};
/* @AUTOGEN-END@ */
}  // namespace cwerg::fe
