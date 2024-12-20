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
from FE import lexer

logger = logging.getLogger(__name__)


def _ExtractAnnotations(tk: lexer.TK) -> dict[str, Any]:
    out: dict[str, Any] = {"x_srcloc": tk.srcloc}
    # print ("@@@@",tk)
    comments = []
    for c in tk.comments:
        com = c.text
        if com == "--\n":
            com = ""
        elif com.startswith("-- "):
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

        assert a.text.startswith(cwast.ANNOTATION_PREFIX)
        out[a.text[1:]] = True
    return out


PAREN_VALUE = {
    "{": 1,
    "}": -1,
    "(": 100,
    ")": -100,
    "[": 10000,
    "]": -10000,
}


_PREFIX_EXPR_PARSERS: dict[lexer.TK, tuple[int, Any]] = {}
_INFIX_EXPR_PARSERS: dict[str, tuple[int, Any]] = {}


def _ParseExpr(inp: lexer.Lexer, precedence=0):
    """Pratt Parser"""
    tk = inp.next()
    prec, parser = _PREFIX_EXPR_PARSERS.get(tk.kind, (0, None))
    if not parser:
        raise RuntimeError(f"could not parse '{tk}'")
    lhs = parser(inp, tk, prec)
    while True:
        tk = inp.peek()

        prec, parser = _INFIX_EXPR_PARSERS.get(tk.text, (0, None))
        if precedence >= prec:
            break
        inp.next()
        lhs = parser(inp, lhs, tk, prec)
    return lhs


def _PParseId(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    if tk.text.startswith(cwast.MACRO_VAR_PREFIX):
        return cwast.MacroId(cwast.NAME.FromStr(tk.text), x_srcloc=tk.srcloc)
    return cwast.Id.Make(tk.text, x_srcloc=tk.srcloc)


def _PParseNum(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    assert not tk.text.startswith(cwast.MACRO_VAR_PREFIX)
    return cwast.ValNum(tk.text, x_srcloc=tk.srcloc)


_FUN_LIKE: dict[str, tuple[Callable, str]] = {
    "abs": (lambda x, **kw: cwast.Expr1(cwast.UNARY_EXPR_KIND.ABS, x, **kw), "E"),
    "sqrt": (lambda x, **kw: cwast.Expr1(cwast.UNARY_EXPR_KIND.SQRT, x, **kw), "E"),
    "max": (lambda x, y, **kw: cwast.Expr2(cwast.BINARY_EXPR_KIND.MAX, x, y, **kw), "EE"),
    "min": (lambda x, y, **kw: cwast.Expr2(cwast.BINARY_EXPR_KIND.MIN, x, y, **kw), "EE"),
    cwast.ExprLen.ALIAS: (cwast.ExprLen, "E"),
    "pinc": (cwast.ExprPointer, "pEEe"),
    "pdec": (cwast.ExprPointer, "pEEe"),
    cwast.ExprOffsetof.ALIAS: (cwast.ExprOffsetof, "TE"),
    "span": (cwast.ValSpan, "EE"),
    "span!": (cwast.ValSpan, "EE"),
    cwast.ExprFront.ALIAS:  (cwast.ExprFront, "E"),
    cwast.ExprFront.ALIAS + "!":  (cwast.ExprFront, "E"),
    cwast.ExprUnwrap.ALIAS: (cwast.ExprUnwrap, "E"),
    cwast.ExprUnionTag.ALIAS: (cwast.ExprUnionTag, "E"),
    #
    cwast.TypeOf.ALIAS: (cwast.TypeOf, "E"),
    #
    cwast.ExprSizeof.ALIAS: (cwast.ExprSizeof, "T"),
    cwast.ExprTypeId.ALIAS: (cwast.ExprTypeId, "T"),
    #
    cwast.TypeUnionDelta.ALIAS: (cwast.TypeUnionDelta, "TT"),
    # mixing expression and types
    cwast.ExprAs.ALIAS: (cwast.ExprAs, "ET"),
    cwast.ExprWrap.ALIAS: (cwast.ExprWrap, "ET"),
    cwast.ExprIs.ALIAS: (cwast.ExprIs, "ET"),
    # TODO: handle unchecked
    cwast.ExprNarrow.ALIAS: (cwast.ExprNarrow, "ET"),
    cwast.ExprWiden.ALIAS: (cwast.ExprWiden, "ET"),
    cwast.ExprUnsafeCast.ALIAS: (cwast.ExprUnsafeCast, "ET"),
    cwast.ExprBitCast.ALIAS: (cwast.ExprBitCast, "ET"),
    #
    cwast.ExprStringify.ALIAS: (cwast.ExprStringify, "E"),
    cwast.ExprSrcLoc.ALIAS: (cwast.ExprSrcLoc, "E"),
}


def _ParseFunLike(inp: lexer.Lexer, name: lexer.TK) -> Any:
    ctor, args = _FUN_LIKE[name.text]
    inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
    first = True
    params: list[Any] = []
    extra = _ExtractAnnotations(name)
    if name.text.endswith(cwast.MUTABILITY_SUFFIX):
        extra["mut"] = True
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


def _PParseKeywordConstants(inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    if tk.text == "true":
        return cwast.ValTrue(x_srcloc=tk.srcloc)
    elif tk.text == "false":
        return cwast.ValFalse(x_srcloc=tk.srcloc)
    elif tk.text == "void":
        return cwast.ValVoid(x_srcloc=tk.srcloc)
    elif tk.text == "auto":
        return cwast.ValAuto(x_srcloc=tk.srcloc)
    elif tk.text == "undef":
        return cwast.ValUndef(x_srcloc=tk.srcloc)
    elif tk.text in cwast.BUILT_IN_EXPR_MACROS:
        inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
        args = _ParseMacroCallArgs(inp, tk.srcloc)
        return cwast.MacroInvoke(cwast.NAME.FromStr(tk.text), args, x_srcloc=tk.srcloc)
    elif tk.text in _FUN_LIKE:
        return _ParseFunLike(inp, tk)
    elif tk.text == "expr":
        # we use "0" as the indent intentionally
        # allowing the next statement to begin at any column
        body = _ParseStatementList(inp, 0)
        return cwast.ExprStmt(body, x_srcloc=tk.srcloc)
    else:
        assert False, f"unexpected keyword {tk}"


def _PParseStr(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    t = tk.text
    strkind = ""
    tq = False
    if t.startswith('"""'):
        assert t.endswith('"""')
        t = t[3:-3]
        tq = True
    elif t.startswith('r"""'):
        assert t.endswith('"""')
        t = t[4:-3]
        tq = True
        strkind = "raw"
    elif t.startswith('x"""'):
        assert t.endswith('"""')
        t = t[4:-3]
        tq = True
        strkind = "hex"
    elif t.startswith('"'):
        assert t.endswith('"')
        t = t[1:-1]
    else:
        assert False, f"unexpected string [{t}]"
    return cwast.ValString(t, triplequoted=tq, strkind=strkind, x_srcloc=tk.srcloc)


def _PParseChar(_inp: lexer.Lexer, tk: lexer.TK, _precedence) -> Any:
    return cwast.ValNum(tk.text, x_srcloc=tk.srcloc)


def _PParsePrefix(inp: lexer.Lexer, tk: lexer.TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    if tk.text.startswith("-"):
        kind = cwast.UNARY_EXPR_KIND.MINUS
    elif tk.text.startswith("&"):
        return cwast.ExprAddrOf(rhs, mut=tk.text == "&!", x_srcloc=tk.srcloc)
    else:
        kind = cwast.UNARY_EXPR_SHORTCUT[tk.text]
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
    lexer.TK_KIND.OP1: (pp.PREC1_NOT, _PParsePrefix),
    lexer.TK_KIND.OP2: (10, _PParsePrefix),  # only used for "-"
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


def _ParseMacroArg(inp: lexer.Lexer, srcloc) -> Any:
    if inp.match(lexer.TK_KIND.CURLY_OPEN):
        assert False, "EphemeralList are no longer supported"
        # if we decice to re-introduce them, we should use "{{ ... }}"
        # notation to make them different from compound values
        args = []
        first = True
        while not inp.match(lexer.TK_KIND.CURLY_CLOSED):
            if not first:
                inp.match_or_die(lexer.TK_KIND.COMMA)
            first = False
            args.append(_ParseMacroArg(inp, srcloc))
        return cwast.EphemeralList(args, x_srcloc=srcloc)
    else:
        return _ParseExpr(inp)


def _ParseMacroCallArgs(inp: lexer.Lexer, srloc) -> list[Any]:
    args = []
    first = True
    while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(lexer.TK_KIND.COMMA)
        first = False
        args.append(_ParseMacroArg(inp, srloc))
    return args


def _ParseExprMacro(name: cwast.Id, inp: lexer.Lexer):
    args = _ParseMacroCallArgs(inp, name.x_srcloc)
    assert name.IsMacroCall()
    return cwast.MacroInvoke(cwast.NAME.FromStr(name.FullName()), args, x_srcloc=name.x_srcloc)


def _PParseFunctionCall(inp: lexer.Lexer, callee, tk: lexer.TK, precedence) -> Any:
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
    tk = inp.peek()
    index = _ParseExpr(inp)
    inp.match_or_die(lexer.TK_KIND.SQUARE_CLOSED)
    # TODO: handle unchecked
    return cwast.ExprIndex(array, index, **_ExtractAnnotations(tk))


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
    "<": (pp.PREC2_COMPARISON, _PParserInfixOp),
    "<=": (pp.PREC2_COMPARISON, _PParserInfixOp),
    ">": (pp.PREC2_COMPARISON, _PParserInfixOp),
    ">=": (pp.PREC2_COMPARISON, _PParserInfixOp),
    #
    "==": (pp.PREC2_COMPARISON, _PParserInfixOp),
    "!=": (pp.PREC2_COMPARISON, _PParserInfixOp),
    #
    "+": (pp.PREC2_ADD, _PParserInfixOp),
    "-": (pp.PREC2_ADD, _PParserInfixOp),
    "/": (pp.PREC2_MUL, _PParserInfixOp),
    "*": (pp.PREC2_MUL, _PParserInfixOp),
    "%": (pp.PREC2_MUL, _PParserInfixOp),
    #
    "||": (pp.PREC2_ORSC, _PParserInfixOp),
    "&&": (pp.PREC2_ANDSC, _PParserInfixOp),
    #
    "<<": (pp.PREC2_SHIFT, _PParserInfixOp),
    ">>": (pp.PREC2_SHIFT, _PParserInfixOp),
    "<<<": (pp.PREC2_SHIFT, _PParserInfixOp),
    ">>>": (pp.PREC2_SHIFT, _PParserInfixOp),
    #
    # "ptr_diff": (10, _PParserInfixOp),
    #
    "xor": (pp.PREC2_ADD, _PParserInfixOp),
    "or": (pp.PREC2_ADD, _PParserInfixOp),
    "and": (pp.PREC2_MUL, _PParserInfixOp),
    #
    # "min": (pp.PREC2_MAX, _PParserInfixOp),
    # "max": (pp.PREC2_MAX, _PParserInfixOp),

    #
    "(": (20, _PParseFunctionCall),
    "[":  (pp.PREC_INDEX, _PParseIndex),
    "^": (pp.PREC_INDEX, _PParseDeref),
    ".": (pp.PREC_INDEX, _PParseFieldAccess),
    "?": (6, _PParseTernary),
}


def _ParseTypeExpr(inp: lexer.Lexer) -> Any:
    tk = inp.next()
    extra = _ExtractAnnotations(tk)
    if tk.kind is lexer.TK_KIND.ID:
        if tk.text.startswith(cwast.MACRO_VAR_PREFIX):
            return cwast.MacroId(cwast.NAME.FromStr(tk.text), **extra)
        return cwast.Id.Make(tk.text, **extra)
    elif tk.kind is lexer.TK_KIND.KW:
        if tk.text == cwast.TypeAuto.ALIAS:
            return cwast.TypeAuto(**extra)
        elif tk.text == "funtype":
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
        elif tk.text == cwast.TypeUnion.ALIAS:
            inp.match_or_die(lexer.TK_KIND.PAREN_OPEN)
            members = []
            first = True
            while not inp.match(lexer.TK_KIND.PAREN_CLOSED):
                if not first:
                    inp.match_or_die(lexer.TK_KIND.COMMA)
                first = False
                members.append(_ParseTypeExpr(inp))
            return cwast.TypeUnion(members, **extra)
        kind = cwast.KeywordToBaseTypeKind(tk.text)
        assert kind is not cwast.BASE_TYPE_KIND.INVALID, f"{tk}"
        return cwast.TypeBase(kind, **extra)
    elif tk.text == '[':
        dim = _ParseExpr(inp)
        inp.match_or_die(lexer.TK_KIND.SQUARE_CLOSED)
        type = _ParseTypeExpr(inp)
        return cwast.TypeVec(dim, type, **extra)
    elif tk.text == "^":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest, **extra)
    elif tk.text == "^!":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest, mut=True, **extra)
    else:
        assert False, f"unexpected token {tk}"


_TYPE_START_KW = set([cwast.TypeAuto.ALIAS, "funtype", "span", "span!", cwast.TypeOf.ALIAS,
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


def _ParseStatementMacro(kw: lexer.TK, inp: lexer.Lexer):
    assert kw.text.endswith(cwast.MACRO_CALL_SUFFIX), f"{kw}"
    args = []
    if inp.match(lexer.TK_KIND.PAREN_OPEN):
        args = _ParseMacroCallArgs(inp, kw.srcloc)
    else:
        while inp.peek().kind is not lexer.TK_KIND.COLON:
            args.append(_ParseExpr(inp))
            if not inp.match(lexer.TK_KIND.COMMA):
                break
        stmts = _ParseStatementList(inp, kw.column)
        args.append(cwast.EphemeralList(stmts, colon=True, x_srcloc=kw.srcloc))
    return cwast.MacroInvoke(cwast.NAME.FromStr(kw.text), args, **_ExtractAnnotations(kw))


def _MaybeLabel(tk: lexer.TK, inp: lexer.Lexer):
    p = inp.peek()
    if p.kind is lexer.TK_KIND.ID and p.srcloc.lineno == tk.srcloc.lineno:
        tk = inp.next()


def _ParseOptionalLabel(inp: lexer.Lexer):
    p = inp.peek()
    if p.kind is lexer.TK_KIND.ID:
        # this should be easy to support once we switched
        # break/cont to using an Id for the label
        assert not p.text.startswith(cwast.MACRO_VAR_PREFIX), f"{p.text}"
        inp.next()
        return p.text
    return ""


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
    if kw.text.startswith("m"):
        return cwast.MacroVar(cwast.NAME.FromStr(name.text), type, init, mut=kw.text.endswith(cwast.MUTABILITY_SUFFIX),
                              **extra)
    else:
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
        var = cwast.MacroId(cwast.NAME.FromStr(
            name.text), x_srcloc=name.srcloc)
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
    label = ""
    if inp.peek().srcloc.lineno == kw.srcloc.lineno:
        label = _ParseOptionalLabel(inp)
    return cwast.StmtBreak(label, **extra)


def _ParseStmtContinue(inp: lexer.Lexer, kw: lexer.TK, extra: dict[str, Any]):
    label = ""
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
    "mlet": _ParseStmtLetLike,
    "mlet!": _ParseStmtLetLike,
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
            return _ParseStatementMacro(kw, inp)
        else:
            # this happends inside a macro body
            if not kw.text.startswith(cwast.MACRO_VAR_PREFIX):
                cwast.CompilerError(
                    kw.srcloc, f"expect macro var but got {kw.text}")
            return cwast.MacroId(cwast.NAME.FromStr(kw.text), **extra)
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
        out.append(cwast.NAME.FromStr(name.text))
    return out


def _ParseTopLevel(inp: lexer.Lexer):
    kw = inp.next()
    extra = _ExtractAnnotations(kw)
    alias = ""
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
        base_type = inp.match_or_die(lexer.TK_KIND.KW)
        entries = _ParseEnumList(inp, kw.column)
        return cwast.DefEnum(cwast.NAME.FromStr(name.text), cwast.KeywordToBaseTypeKind(base_type.text),
                             entries, **extra)
    elif kw.text == "static_assert":
        cond = _ParseExpr(inp)
        return cwast.StmtStaticAssert(cond, "", **extra)
    else:
        assert False, f"unexpected topelevel [{kw}]"


def _ParseModule(inp: lexer.Lexer):
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

    def replacer(node, parent, field: str):
        if isinstance(node, cwast.ExprParen):
            if pp.NodeNeedsParen(node.expr, parent, field):
                return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def ReadModFromStream(fp, fn) -> cwast.DefMod:
    inp = lexer.Lexer(lexer.LexerRaw(fn, fp))
    return _ParseModule(inp)


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    def main():
        logging.basicConfig(level=logging.WARNING)
        logger.setLevel(logging.WARNING)
        inp = lexer.Lexer(lexer.LexerRaw("stdin", sys.stdin))
        mod = _ParseModule(inp)
        RemoveRedundantParens(mod)
        pp_sexpr.PrettyPrint(mod)

    main()
