#include <cstdint>

#include "FE/cwast_gen.h"

namespace cwerg::fe {


#define BIT_N(x) 1ull << uint64_t(NFD_NODE_FIELD::x)
#define BIT_S(x) 1ull << uint64_t(NFD_STRING_FIELD::x)
#define BIT_B(x) 1ull << uint64_t(NFD_BOOL_FIELD::x)

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
    { BIT_N(type_or_auto)| BIT_N(initial_or_undef_or_auto), BIT_S(name), BIT_B(mut)| BIT_B(ref) }, // MacroVar
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
/* @AUTOGEN-END@ */
}  // namespace cwerg::fe
