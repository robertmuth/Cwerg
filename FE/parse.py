#!/bin/env python3
"""
The Parser is recursice descent (RD) combined with Pratt Parsing for
Expressions.

References:

https://martin.janiczek.cz/2023/07/03/demystifying-pratt-parsers.html
https://github.com/feroldi/pratt-parser-in-python

"""


import logging

from typing import Any
from collections.abc import Callable

from FE import cwast
from FE import pp
from FE import pp_sexpr
from FE import lexer_tab as lexer

logger = logging.getLogger(__name__)


def _ExtractAnnotations(tk: lexer.TK) -> dict[str, Any]:
    out: dict[str, Any] = {"x_srcloc": tk.srcloc}
    # print ("@@@@",tk)
    comments = []
    for c in tk.comments:
        com = c.text
        if com == ";\n":
            com = ""
        elif com.startswith("; "):
            com = com[3:-1]
        else:
            cwast.CompilerError(tk.srcloc, f"expected comment got: [{com}]")
        comments.append(com)
    if comments:
        if len(comments) == 1 and '"' not in comments[0]:
            out["doc"] = f'"{comments[0]}"'
        else:
            c = '\n'.join(comments)
            out["doc"] = f'"""{c}"""'
    for a in tk.annotations:
        out[a.text] = True
    return out


PAREN_VALUE = {
    "{": 1,
    "}": -1,
    "(": 100,
    ")": -100,
    "[": 10000,
    "]": -10000,
}


_PREFIX_EXPR_PARSERS: dict[lexer.TK_KIND, tuple[int, Any]] = {}
_INFIX_EXPR_PARSERS: dict[lexer.TK_KIND, tuple[int, Any]] = {}


def _ParseExpr(inp: lexer.Lexer, precedence=0):
    """Pratt Parser"""
    tk = inp.next()
    prec, parser = _PREFIX_EXPR_PARSERS.get(tk.kind, (0, None))
    if not parser:
        raise RuntimeError(f"could not parse '{tk}'")
    lhs = parser(inp, tk, prec)
    while True:
        tk = inp.peek()
        prec, parser = _INFIX_EXPR_PARSERS.get(tk.kind, (0, None))
        if precedence >= prec:
            break
        inp.next()
        lhs = parser(inp, lhs, tk, prec)
    return lhs


def _PParseId(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    if tk.text.startswith(cwast.MACRO_VAR_PREFIX):
        return cwast.MacroId.Make(tk.text, x_srcloc=tk.srcloc)
    return cwast.Id.Make(tk.text, x_srcloc=tk.srcloc)


def _PParseNum(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    assert not tk.text.startswith(cwast.MACRO_VAR_PREFIX)
    return cwast.ValNum(tk.text, x_srcloc=tk.srcloc)


_FUN_LIKE: dict[str, tuple[Callable, str]] = {
    "abs": (lambda x, **kw: cwast.Expr1(cwast.UNARY_EXPR_KIND.ABS, x, **kw), "E"),
    "sqrt": (lambda x, **kw: cwast.Expr1(cwast.UNARY_EXPR_KIND.SQRT, x, **kw), "E"),
    "max": (lambda x, y, **kw: cwast.Expr2(cwast.BINARY_EXPR_KIND.MAX, x, y, **kw), "EE"),
    "min": (lambda x, y, **kw: cwast.Expr2(cwast.BINARY_EXPR_KIND.MIN, x, y, **kw), "EE"),
    "ptr_diff": (lambda x, y, **kw: cwast.Expr2(cwast.BINARY_EXPR_KIND.PDELTA, x, y, **kw), "EE"),
    "ptr_inc": (cwast.ExprPointer, "pEEe"),
    "ptr_dec": (cwast.ExprPointer, "pEEe"),
    #
    cwast.ExprOffsetof.ALIAS: (cwast.ExprOffsetof, "TE"),
    cwast.ValSpan.ALIAS: (cwast.ValSpan, "EE"),
    cwast.TypeUnionDelta.ALIAS: (cwast.TypeUnionDelta, "TT"),
    #
    cwast.ExprLen.ALIAS: (cwast.ExprLen, "E"),
    cwast.ExprFront.ALIAS:  (cwast.ExprFront, "E"),
    cwast.ExprFront.ALIAS + "!":  (cwast.ExprFront, "E"),
    cwast.ExprUnwrap.ALIAS: (cwast.ExprUnwrap, "E"),
    cwast.ExprUnionTag.ALIAS: (cwast.ExprUnionTag, "E"),
    cwast.ExprStringify.ALIAS: (cwast.ExprStringify, "E"),
    cwast.ExprSrcLoc.ALIAS: (cwast.ExprSrcLoc, "E"),
    cwast.TypeOf.ALIAS: (cwast.TypeOf, "E"),
    #
    cwast.ExprSizeof.ALIAS: (cwast.ExprSizeof, "T"),
    cwast.ExprTypeId.ALIAS: (cwast.ExprTypeId, "T"),
    #
    # mixing expression and types
    cwast.ExprAs.ALIAS: (cwast.ExprAs, "ET"),
    cwast.ExprWrap.ALIAS: (cwast.ExprWrap, "ET"),
    cwast.ExprIs.ALIAS: (cwast.ExprIs, "ET"),
    cwast.ExprNarrow.ALIAS: (cwast.ExprNarrow, "ET"),
    cwast.ExprNarrow.ALIAS + "!": (cwast.ExprNarrow, "ET"),
    cwast.ExprWiden.ALIAS: (cwast.ExprWiden, "ET"),
    cwast.ExprUnsafeCast.ALIAS: (cwast.ExprUnsafeCast, "ET"),
    cwast.ExprBitCast.ALIAS: (cwast.ExprBitCast, "ET"),
    #

}


def _ParseFunLike(inp: lexer.Lexer, name: lexer.TK) -> Any:
    fun_name = name.text
    ctor, args = _FUN_LIKE[fun_name]
    inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
    first = True
    params: list[Any] = []
    extra = _ExtractAnnotations(name)
    if name.text.endswith(cwast.MUTABILITY_SUFFIX):
        extra[pp.KEYWORDS_WITH_EXCL_SUFFIX[fun_name[:-1]]] = True
    for a in args:
        if inp.peek().kind is lexer.TK_KIND.PAREN_CLOSED and a == "e":
            params.append(cwast.ValUndef(x_srcloc=name.srcloc))
            break
        if a == "p":
            params.append(cwast.POINTER_EXPR_SHORTCUT[name.text])
            continue
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        if a == "E" or a == "e":
            params.append(_ParseExpr(inp))
        elif a == "S":
            # used for field name
            f = _ParseExpr(inp)
            assert isinstance(f, cwast.Id)
            params.append(f.base_name)
        else:
            assert a == "T", f"unknown parameter [{a}]"
            params.append(_ParseTypeExpr(inp))

    inp.match_or_die(lexer.TK_KIND.PAREN_CLOSED)
    return ctor(*params, **extra)


_SIMPLE_VAL_NODES: dict[str, Callable] = {
    "true": cwast.ValTrue,
    "false": cwast.ValFalse,
    "void_val": cwast.ValVoid,
    "auto_val": cwast.ValAuto,
    "undef": cwast.ValUndef
}


def _PParseSimpleVal(inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    return _SIMPLE_VAL_NODES[tk.text](x_srcloc=tk.srcloc)


def _PParseKeywordConstants(inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    if tk.text in cwast.BUILT_IN_EXPR_MACROS:
        inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
        args = _ParseMacroCallArgs(inp)
        return cwast.MacroInvoke(cwast.NAME.FromStr(tk.text), args, x_srcloc=tk.srcloc)
    elif tk.text in _FUN_LIKE:
        return _ParseFunLike(inp, tk)
    elif tk.text == cwast.ExprStmt.ALIAS:
        # we use "0" as the indent intentionally
        # allowing the next statement to begin at any column
        body = _ParseStatementList(inp, 0)
        return cwast.ExprStmt(body, x_srcloc=tk.srcloc)
    else:
        assert False, f"unexpected keyword {tk}"


def _PParseStr(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    return cwast.MakeValString(tk.text, tk.srcloc)


def _PParseChar(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    return cwast.ValNum(tk.text, x_srcloc=tk.srcloc)


def _PParseAddressOf(inp: lexer.Lexer, tk: lexer.TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    return cwast.ExprAddrOf(rhs, mut=tk.text == "@!", x_srcloc=tk.srcloc)


def _PParsePrefix(inp: lexer.Lexer, tk: lexer.TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    if tk.text.startswith("-"):
        kind = cwast.UNARY_EXPR_KIND.NEG
    else:
        kind = cwast.UNARY_EXPR_SHORTCUT_SEXPR.get(tk.text)
        if kind is None:
            cwast.CompilerError(tk.srcloc, f"cannot parse tolken {tk.text}")
    return cwast.Expr1(kind, rhs, x_srcloc=tk.srcloc)


def _PParseParenGroup(inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    assert tk.kind is lexer.TK_KIND.PAREN_OPEN
    inner = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.PAREN_CLOSED)
    return cwast.ExprParen(inner, x_srcloc=tk.srcloc)


def _ParseValPoint(inp: lexer.Lexer) -> Any:
    tk: lexer.TK = inp.peek()
    val = _ParseExpr(inp)
    if inp.match(lexer.TK_KIND.ASSIGN):
        index = val
        val = _ParseExpr(inp)
    else:
        index = cwast.ValAuto(x_srcloc=tk.srcloc)
    return cwast.ValPoint(val, index, **_ExtractAnnotations(tk))


def _PParseValCompound(inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    assert tk.kind is lexer.TK_KIND.CURLY_OPEN
    if inp.match(lexer.TK_KIND.COLON):
        type = cwast.TypeAuto(x_srcloc=tk.srcloc)
    else:
        type = _ParseTypeExpr(inp)
        inp.match_or_die(lexer.TK_KIND.COLON)

    inits = []
    first = True
    while not inp.match(lexer.TK_KIND.CURLY_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        inits.append(_ParseValPoint(inp))
    return cwast.ValCompound(type, inits, x_srcloc=tk.srcloc)


_PREFIX_EXPR_PARSERS: dict[lexer.TK_KIND, tuple[int, Callable]] = {
    lexer.TK_KIND.KW: (10, _PParseKeywordConstants),
    lexer.TK_KIND.KW_SIMPLE_VAL: (10, _PParseSimpleVal),
    lexer.TK_KIND.PREFIX_OP: (pp.PREC1_NOT, _PParsePrefix),
    lexer.TK_KIND.ADDR_OF_OP: (pp.PREC1_NOT, _PParseAddressOf),
    lexer.TK_KIND.ADD_OP: (10, _PParsePrefix),  # only used for "-"
    lexer.TK_KIND.ID: (10, _PParseId),
    lexer.TK_KIND.NUM: (10, _PParseNum),
    lexer.TK_KIND.STR: (10, _PParseStr),
    lexer.TK_KIND.CHAR: (10, _PParseChar),
    lexer.TK_KIND.PAREN_OPEN: (10, _PParseParenGroup),
    lexer.TK_KIND.CURLY_OPEN: (10, _PParseValCompound),
}


def _PParserInfixOp(inp: lexer.Lexer, lhs, tk: lexer.TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    return cwast.Expr2(cwast.BINARY_EXPR_SHORTCUT[tk.text], lhs, rhs, x_srcloc=tk.srcloc)


def _ParseMacroCallArgs(inp: lexer.Lexer) -> list[Any]:
    args = []
    first = True
    while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        args.append(_ParseTypeExprOrExpr(inp))
    return args


def _ParseExprMacro(name: cwast.Id, inp: lexer.Lexer):
    args = _ParseMacroCallArgs(inp)
    assert name.IsMacroCall()
    return cwast.MacroInvoke(cwast.NAME.FromStr(name.FullName()), args, x_srcloc=name.x_srcloc)


def _PParseCall(inp: lexer.Lexer, callee, tk: lexer.TK, precedence) -> Any:
    if isinstance(callee, cwast.Id) and callee.IsMacroCall():
        return _ParseExprMacro(callee, inp)
    assert tk.kind is lexer.TK_KIND.PAREN_OPEN
    args = []
    first = True
    while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        args.append(_ParseExpr(inp))
    return cwast.ExprCall(callee, args, **_ExtractAnnotations(tk))


def _PParseIndex(inp: lexer.Lexer, array, tk: lexer.TK, _precedence) -> Any:
    assert tk.kind is lexer.TK_KIND.SQUARE_OPEN
    is_unchecked = tk.text.endswith(cwast.MUTABILITY_SUFFIX)
    tk = inp.peek()
    index = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.SQUARE_CLOSED)
    extra = _ExtractAnnotations(tk)
    if is_unchecked:
        extra["unchecked"] = True
    return cwast.ExprIndex(array, index, **extra)


def _PParseDeref(_inp: lexer.Lexer, pointer, tk: lexer.TK, _precedence) -> Any:
    return cwast.ExprDeref(pointer, tk.srcloc)


def _PParseFieldAccess(inp: lexer.Lexer, rec, _tk: lexer.TK, _precedence) -> Any:
    field = inp.match_or_die(lexer.TK_KIND.ID)
    return cwast.ExprField(rec, cwast.Id.Make(field.text, x_srcloc=field.srcloc), x_srcloc=field.srcloc)


def _PParseTernary(inp: lexer.Lexer, cond, tk: lexer.TK, _precedence) -> Any:
    expr_t = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.COLON)
    expr_f = _ParseExpr(inp)
    return cwast.Expr3(cond, expr_t, expr_f, x_srcloc=tk.srcloc)


_INFIX_EXPR_PARSERS = {
    lexer.TK_KIND.COMPARISON_OP: (pp.PREC2_COMPARISON, _PParserInfixOp),
    #
    lexer.TK_KIND.ADD_OP: (pp.PREC2_ADD, _PParserInfixOp),
    lexer.TK_KIND.MUL_OP: (pp.PREC2_MUL, _PParserInfixOp),
    #
    lexer.TK_KIND.OR_SC_OP: (pp.PREC2_ORSC, _PParserInfixOp),
    lexer.TK_KIND.AND_SC_OP: (pp.PREC2_ANDSC, _PParserInfixOp),
    #
    lexer.TK_KIND.SHIFT_OP: (pp.PREC2_SHIFT, _PParserInfixOp),
    #
    # "ptr_diff": (10, _PParserInfixOp),
    #
    #
    # "min": (pp.PREC2_MAX, _PParserInfixOp),
    # "max": (pp.PREC2_MAX, _PParserInfixOp),

    #
    lexer.TK_KIND.PAREN_OPEN: (20, _PParseCall),
    lexer.TK_KIND.SQUARE_OPEN:  (pp.PREC_INDEX, _PParseIndex),
    lexer.TK_KIND.DEREF_OR_POINTER_OP: (pp.PREC_INDEX, _PParseDeref),
    lexer.TK_KIND.DOT_OP: (pp.PREC_INDEX, _PParseFieldAccess),
    lexer.TK_KIND.TERNARY_OP: (6, _PParseTernary),
}


def _ParseTypeExpr(inp: lexer.Lexer) -> Any:
    tk = inp.next()
    extra = _ExtractAnnotations(tk)
    if tk.kind is lexer.TK_KIND.ID:
        if tk.text.startswith(cwast.MACRO_VAR_PREFIX):
            return cwast.MacroId.Make(tk.text, **extra)
        return cwast.Id.Make(tk.text, **extra)
    elif tk.kind is lexer.TK_KIND.BASE_TYPE:
        kind = cwast.KeywordToBaseTypeKind(tk.text)
        assert kind is not cwast.BASE_TYPE_KIND.INVALID, f"{tk}"
        return cwast.TypeBase(kind, **extra)
    elif tk.kind is lexer.TK_KIND.KW:
        if tk.text == cwast.TypeAuto.ALIAS:
            return cwast.TypeAuto(**extra)
        elif tk.text == cwast.TypeFun.ALIAS:
            params = _ParseFormalParams(inp)
            result = _ParseTypeExpr(inp)
            return cwast.TypeFun(params, result, **extra)
        elif tk.text in ("span", "span!"):
            inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
            type = _ParseTypeExpr(inp)
            inp.match_or_die(lexer.TK_KIND.PAREN_CLOSED)
            return cwast.TypeSpan(type, mut=tk.text.endswith(cwast.MUTABILITY_SUFFIX), **extra)
        elif tk.text == cwast.TypeOf.ALIAS:
            return _ParseFunLike(inp, tk)
        elif tk.text == cwast.TypeUnionDelta.ALIAS:
            return _ParseFunLike(inp, tk)
        elif tk.text in ("union", "union!"):
            inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
            members = []
            first = True
            while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
                if not first:
                    inp.match_or_die(lexer.TK_KIND.COMMA)
                first = False
                members.append(_ParseTypeExpr(inp))
            return cwast.TypeUnion(members, untagged=tk.text.endswith(cwast.MUTABILITY_SUFFIX), **extra)
        else:
            assert False, "Not Reachable"
    elif tk.kind is lexer.TK_KIND.SQUARE_OPEN:
        dim = _ParseExpr(inp)
        inp.match_or_die(lexer.TK_KIND.SQUARE_CLOSED)
        type = _ParseTypeExpr(inp)
        return cwast.TypeVec(dim, type, **extra)
    elif tk.kind is lexer.TK_KIND.DEREF_OR_POINTER_OP:
        mut = tk.text.endswith(cwast.MUTABILITY_SUFFIX)
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest, mut=mut, **extra)
    else:
        assert False, f"unexpected token {tk}"


_TYPE_START_KW = set([cwast.TypeAuto.ALIAS, cwast.TypeFun.ALIAS, "span", "span!", cwast.TypeOf.ALIAS,
                     cwast.TypeUnionDelta.ALIAS, cwast.TypeUnion.ALIAS, "[", "^", "^!"])


def MaybeTypeExprStart(tk: lexer.TK) -> bool:
    return tk.text in _TYPE_START_KW or cwast.KeywordToBaseTypeKind(tk.text) != cwast.BASE_TYPE_KIND.INVALID


def _ParseTypeExprOrExpr(inp: lexer.Lexer):
    tk = inp.peek()
    if MaybeTypeExprStart(tk):
        return _ParseTypeExpr(inp)
    return _ParseExpr(inp)


def _ParseFormalParams(inp: lexer.Lexer):
    out = []
    inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
    first = True
    while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(lexer.TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        out.append(cwast.FunParam(cwast.NAME.FromStr(name.text), type,
                                  **_ExtractAnnotations(name)))
    return out


def _ParseStatementMacro( inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    assert kw.text.endswith(cwast.MACRO_CALL_SUFFIX), f"{kw}"
    args = []
    if inp.match(lexer.TK_KIND.PAREN_OPEN):
        args = _ParseMacroCallArgs(inp)
    else:
        while inp.peek().kind is not lexer.TK_KIND.COLON:
            args.append(_ParseExpr(inp))
            if not inp.match(lexer.TK_KIND.COMMA) and not inp.match(lexer.TK_KIND.ASSIGN):
                break
        stmts = _ParseStatementList(inp, kw.column)
        args.append(cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc))
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text), args, **extra)


def _MaybeLabel(tk: lexer.TK, inp: lexer.Lexer):
    p = inp.peek()
    if p.kind is lexer.TK_KIND.ID and p.srcloc.lineno == tk.srcloc.lineno:
        tk = inp.next()


def _ParseOptionalLabel(inp: lexer.Lexer) -> cwast.NAME:
    p = inp.peek()
    if p.kind is lexer.TK_KIND.ID:
        # this should be easy to support once we switched
        # break/cont to using an Id for the label
        assert not p.text.startswith(cwast.MACRO_VAR_PREFIX), f"{p.text}"
        inp.next()
        return cwast.NAME.FromStr(p.text)
    return cwast.NAME.Empty()


def _ParseStmtLetLike(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    name = inp.match_or_die(lexer.TK_KIND.ID)
    if inp.match(lexer.TK_KIND.ASSIGN):
        type = cwast.TypeAuto(x_srcloc=name.srcloc)
        init = _ParseExpr(inp)
    else:
        type = _ParseTypeExpr(inp)
        if inp.match(lexer.TK_KIND.ASSIGN):
            init = _ParseExpr(inp)
        else:
            init = cwast.ValAuto(x_srcloc=name.srcloc)

    return cwast.DefVar(cwast.NAME.FromStr(name.text), type, init, mut=kw.text.endswith(cwast.MUTABILITY_SUFFIX),
                        **extra)


def _ParseStmtWhile(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    cond = _ParseExpr(inp)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text), [cond, cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc)],
                             **extra)


def _ParseStmtIf(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    cond = _ParseExpr(inp)
    stmts_t = _ParseStatementList(inp, kw.column)
    stmts_f = []
    p = inp.peek()
    if p.column == kw.column and p.text == "else":
        inp.next()
        stmts_f = _ParseStatementList(inp, kw.column)
    return cwast.StmtIf(cond, stmts_t, stmts_f, **_ExtractAnnotations(kw))


def _ParseStmtTryLet(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    name = inp.match_or_die(lexer.TK_KIND.ID)
    type = _ParseTypeExpr(inp)
    inp.match_or_die(lexer.TK_KIND.ASSIGN)
    expr = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.COMMA)
    name2 = inp.match_or_die(lexer.TK_KIND.ID)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text),
                             [cwast.Id.Make(name.text, x_srcloc=name.srcloc), type, expr,  cwast.Id.Make(name2.text, x_srcloc=name2.srcloc),
                              cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc)],
                             **extra)


def _ParseStmtTrySet(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    lhs = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.ASSIGN)
    expr = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.COMMA)
    name2 = inp.match_or_die(lexer.TK_KIND.ID)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text),
                             [lhs, expr,  cwast.Id.Make(name2.text, x_srcloc=name2.srcloc),
                              cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc)],
                             **extra)


def _ParseStmtSet(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    lhs = _ParseExpr(inp)
    kind = inp.next()
    rhs = _ParseExpr(inp)
    if kind.kind is lexer.TK_KIND.ASSIGN:
        return cwast.StmtAssignment(lhs, rhs, **extra)
    else:
        assert kind.kind is lexer.TK_KIND.COMPOUND_ASSIGN, f"{kind}"
        op = cwast.ASSIGNMENT_SHORTCUT[kind.text]
        return cwast.StmtCompoundAssignment(op, lhs, rhs, **extra)


def _ParseStmReturn(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    if inp.peek().srcloc.lineno == kw.srcloc.lineno:
        val = _ParseExpr(inp)
    else:
        val = cwast.ValVoid(kw.srcloc)
    return cwast.StmtReturn(val, **extra)


def _ParseStmtFor(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    name = inp.match_or_die(lexer.TK_KIND.ID)
    if name.text.startswith(cwast.MACRO_VAR_PREFIX):
        var = cwast.MacroId.Make(name.text, x_srcloc=name.srcloc)
    else:
        var = cwast.Id.Make(name.text, x_srcloc=name.srcloc)
    inp.match_or_die(lexer.TK_KIND.ASSIGN)
    start = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.COMMA)
    end = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.COMMA)
    step = _ParseExpr(inp)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text),
                             [var, start, end, step,
                              cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc)],
                             **extra)


def _ParseStmtBreak(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    label = cwast.NAME.Empty()
    if inp.peek().srcloc.lineno == kw.srcloc.lineno:
        label = _ParseOptionalLabel(inp)
    return cwast.StmtBreak(label, **extra)


def _ParseStmtContinue(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    label = cwast.NAME.Empty()
    if inp.peek().srcloc.lineno == kw.srcloc.lineno:
        label = _ParseOptionalLabel(inp)
    return cwast.StmtContinue(label, **extra)


def _ParseStmtBlock(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    label = _ParseOptionalLabel(inp)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.StmtBlock(label, stmts, **extra)


def _ParseStmtCond(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    inp.match_or_die(lexer.TK_KIND.COLON)
    indent = inp.peek().column
    cases = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        case = inp.match_or_die(lexer.TK_KIND.KW, "case")
        cond = _ParseExpr(inp)
        stmts = _ParseStatementList(inp, case.column)
        cases.append(cwast.Case(
            cond, stmts, **_ExtractAnnotations(case)))
    return cwast.StmtCond(cases, **extra)


def _ParseStmtMfor(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    var = inp.match_or_die(lexer.TK_KIND.ID)
    container = inp.match_or_die(lexer.TK_KIND.ID)
    stmts = _ParseStatementList(inp, kw.column)
    return cwast.MacroFor(cwast.NAME.FromStr(var.text), cwast.NAME.FromStr(container.text), stmts, **extra)


_STMT_HANDLERS = {
    "let": _ParseStmtLetLike,
    "let!": _ParseStmtLetLike,
    "while": _ParseStmtWhile,
    "if": _ParseStmtIf,
    "trylet": _ParseStmtTryLet,
    "trylet!": _ParseStmtTryLet,
    "tryset": _ParseStmtTrySet,
    "set": _ParseStmtSet,
    "return": _ParseStmReturn,
    "for": _ParseStmtFor,
    "break": _ParseStmtBreak,
    "continue": _ParseStmtContinue,
    "block": _ParseStmtBlock,
    "cond": _ParseStmtCond,
    "mfor": _ParseStmtMfor,
    "do": lambda inp, kw, extra: cwast.StmtExpr(_ParseExpr(inp), **extra),
    "trap": lambda inp, kw, extra: cwast.StmtTrap(**extra),
    "defer": lambda inp, kw, extra: cwast.StmtDefer(_ParseStatementList(inp, kw.column), **extra),
}


def _ParseStatement(inp: lexer.Lexer):
    kw = inp.next()
    extra = _ExtractAnnotations(kw)
    if kw.kind is lexer.TK_KIND.ID:
        if kw.text.endswith(cwast.MACRO_CALL_SUFFIX):
            return _ParseStatementMacro(inp, kw, _ExtractAnnotations(kw))
        else:
            # this happends inside a macro body
            if not kw.text.startswith(cwast.MACRO_VAR_PREFIX):
                cwast.CompilerError(
                    kw.srcloc, f"expect macro var but got {kw.text}")
            return cwast.MacroId.Make(kw.text, **extra)
    if kw.kind is not lexer.TK_KIND.KW:
        cwast.CompilerError(
            kw.srcloc, f"expected statement keyword but got: {kw}")

    handler = _STMT_HANDLERS.get(kw.text)
    if not handler:
        cwast.CompilerError(kw.srcloc, f"unexpected keyword {
                            kw} at statement position")
    return handler(inp, kw, extra)


def _ParseStatementList(inp: lexer.Lexer, outer_indent: int):
    inp.match_or_die(lexer.TK_KIND.COLON)
    indent = inp.peek().column
    if indent <= outer_indent:
        return []
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        if tk.column != indent:
            cwast.CompilerError(tk.srcloc, "Bad indent")
        stmt = _ParseStatement(inp)
        logger.info("STATEMENT: %s", stmt)
        out.append(stmt)
    return out


def _ParseExprList(inp: lexer.Lexer, outer_indent):
    inp.match_or_die(lexer.TK_KIND.COLON)
    indent = inp.peek().column
    if indent <= outer_indent:
        return []
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        out.append(_ParseExpr(inp))
    return out


def _ParseFieldList(inp: lexer.Lexer):
    inp.match_or_die(lexer.TK_KIND.COLON)
    indent = inp.peek().column
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        name = inp.match_or_die(lexer.TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        out.append(cwast.RecField(cwast.NAME.FromStr(name.text), type,
                   **_ExtractAnnotations(name)))
    return out


def _ParseEnumList(inp: lexer.Lexer, outer_indent):
    inp.match_or_die(lexer.TK_KIND.COLON)
    indent = inp.peek().column
    if indent <= outer_indent:
        return []
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        name = inp.match_or_die(lexer.TK_KIND.ID)
        val = _ParseExpr(inp)
        out.append(cwast.EnumVal(cwast.NAME.FromStr(name.text), val,
                   **_ExtractAnnotations(name)))
    return out


def _ParseMacroParams(inp: lexer.Lexer):
    out = []
    inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
    first = True
    while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(lexer.TK_KIND.ID)
        kind = inp.match_or_die(lexer.TK_KIND.ID)
        out.append(cwast.MacroParam(
            cwast.NAME.FromStr(name.text), cwast.MACRO_PARAM_KIND[kind.text],
            **_ExtractAnnotations(name)))
    return out


def _ParseMacroGenIds(inp: lexer.Lexer):
    out = []
    inp.match_or_die(lexer.TK_KIND.SQUARE_OPEN)
    first = True
    while not inp.match(lexer.TK_KIND.SQUARE_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(lexer.TK_KIND.ID)
        out.append(cwast.MacroId.Make(name.text, x_srcloc=name.srcloc))
    return out


def _ParseTopLevel(inp: lexer.Lexer):
    kw = inp.next()
    extra = _ExtractAnnotations(kw)
    if kw.text == "import":
        name = inp.match_or_die(lexer.TK_KIND.ID)
        path = ""
        if inp.match(lexer.TK_KIND.ASSIGN):
            path = inp.next().text
            if path.startswith('"'):
                assert path.endswith('"')
                path = path[1:-1]
        params = []
        if inp.match(lexer.TK_KIND.PAREN_OPEN):
            first = True
            while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
                if not first:
                    inp.match(lexer.TK_KIND.COMMA)
                first = False
                params.append(_ParseTypeExprOrExpr(inp))
        return cwast.Import(cwast.NAME.FromStr(name.text), path, params, **extra)
    elif kw.text == "fun":
        name = inp.match_or_die(lexer.TK_KIND.ID)
        params = _ParseFormalParams(inp)
        result = _ParseTypeExpr(inp)
        body = _ParseStatementList(inp, kw.column)
        return cwast.DefFun(cwast.NAME.FromStr(name.text), params, result, body, **extra)
    elif kw.text == "rec":
        name = inp.match_or_die(lexer.TK_KIND.ID)
        fields = _ParseFieldList(inp)
        return cwast.DefRec(cwast.NAME.FromStr(name.text), fields, **extra)
    elif kw.text in ("global", "global!"):
        name = inp.match_or_die(lexer.TK_KIND.ID)
        if inp.match(lexer.TK_KIND.ASSIGN):
            type = cwast.TypeAuto(x_srcloc=name.srcloc)
            init = _ParseExpr(inp)
        else:
            type = _ParseTypeExpr(inp)
            if inp.match(lexer.TK_KIND.ASSIGN):
                init = _ParseExpr(inp)
            else:
                init = cwast.ValAuto(x_srcloc=name.srcloc)
        return cwast.DefGlobal(cwast.NAME.FromStr(name.text), type, init, mut=kw.text.endswith(cwast.MUTABILITY_SUFFIX),
                               **extra)
    elif kw.text == "macro":
        name = inp.next()
        if not name.text.endswith(cwast.MACRO_CALL_SUFFIX):
            assert "builtin" in extra, f"bad macro name: {name}"
        kind = inp.match_or_die(lexer.TK_KIND.ID)
        params = _ParseMacroParams(inp)
        gen_ids = _ParseMacroGenIds(inp)
        if kind.text in ("EXPR", "EXPR_LIST"):
            body = _ParseExprList(inp, kw.column)
        else:
            body = _ParseStatementList(inp, kw.column)
        return cwast.DefMacro(cwast.NAME.FromStr(name.text), cwast.MACRO_PARAM_KIND[kind.text],
                              params, gen_ids, body, **extra)
    elif kw.text == "type":
        name = inp.match_or_die(lexer.TK_KIND.ID)
        inp.match_or_die(lexer.TK_KIND.ASSIGN)
        type = _ParseTypeExpr(inp)
        return cwast.DefType(cwast.NAME.FromStr(name.text), type, **extra)
    elif kw.text == "enum":
        name = inp.match_or_die(lexer.TK_KIND.ID)
        base_type = inp.match_or_die(lexer.TK_KIND.BASE_TYPE)
        entries = _ParseEnumList(inp, kw.column)
        return cwast.DefEnum(cwast.NAME.FromStr(name.text), cwast.KeywordToBaseTypeKind(base_type.text),
                             entries, **extra)
    elif kw.text == "static_assert":
        cond = _ParseExpr(inp)
        # TODO
        return cwast.StmtStaticAssert(cond, "", **extra)
    else:
        assert False, f"unexpected topelevel [{kw}]"


def _ParseDefMod(inp: lexer.Lexer):
    # comments, annotations = _ParseOptionalCommentsAttributes(inp)
    # print(comments, annotations)
    kw = inp.match_or_die(lexer.TK_KIND.KW, "module")
    params = []
    if inp.match(lexer.TK_KIND.PAREN_OPEN):
        first = True
        while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
            if not first:
                inp.match_or_die(lexer.TK_KIND.COMMA)
            first = False
            pname = inp.match_or_die(lexer.TK_KIND.ID)
            pkind = inp.match_or_die(lexer.TK_KIND.ID)
            params.append(cwast.ModParam(cwast.NAME.FromStr(pname.text),
                                         cwast.MOD_PARAM_KIND[pkind.text],
                                         **_ExtractAnnotations(pname)))
    inp.match_or_die(lexer.TK_KIND.COLON)
    out = cwast.DefMod(params, [], **_ExtractAnnotations(kw))

    while True:
        if inp.peek().kind is lexer.TK_KIND.SPECIAL_EOF:
            break
        toplevel = _ParseTopLevel(inp)
        logger.info("TOPLEVEL: %s", toplevel)
        out.body_mod.append(toplevel)
    return out


def RemoveRedundantParens(node):
    """Remove Parens which would be re-added by AddMissingParens."""

    def replacer(node, parent, nfd: cwast.NFD):
        if isinstance(node, cwast.ExprParen):
            if pp.NodeNeedsParen(node.expr, parent, nfd):
                return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)


def ReadModFromStream(fp, fn) -> cwast.DefMod:
    inp = lexer.Lexer(lexer.LexerRaw(fn, fp))
    return _ParseDefMod(inp)


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    def main():
        logging.basicConfig(level=logging.WARNING)
        logger.setLevel(logging.WARNING)
        inp = lexer.Lexer(lexer.LexerRaw("stdin", sys.stdin))
        mod = _ParseDefMod(inp)
        RemoveRedundantParens(mod)
        pp_sexpr.PrettyPrint(mod)

    main()
