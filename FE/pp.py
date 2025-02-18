#!/bin/env python3
"""Concrete Syntax Pretty printer (PP) for Cwerg AST to concrete syntax

"""

import logging
import enum
import dataclasses

from typing import Optional, Any, Callable

from FE import cwast
from Util import pretty as PP


logger = logging.getLogger(__name__)


_OPS_PRECENDENCE = {
    # "->": 10,
    cwast.ExprField: 10,
    cwast.ExprAs: 10,
    #
    cwast.Expr1: 11,
    cwast.ExprDeref: 11,
    cwast.ExprAddrOf: 11,

    cwast.ExprIs: 50,
}

_DEREFERENCE_OP = "^"
_ADDRESS_OF_OP = "@"

PREC2_ORSC = 5
PREC2_ANDSC = 6
PREC2_COMPARISON = 7
PREC2_MAX = 9  # max min
PREC2_ADD = 10  # + - or xor
PREC2_MUL = 11  # * / % and
PREC2_SHIFT = 12
PREC1_NOT = 13
PREC_INDEX = 14  # &a[i] &struct^.field
# PREC_DEREF = 15


_OPS_PRECENDENCE_EXPR2 = {
    cwast.BINARY_EXPR_KIND.SHL: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.ROTL: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.SHR: PREC2_SHIFT,
    cwast.BINARY_EXPR_KIND.ROTR: PREC2_SHIFT,
    #
    cwast.BINARY_EXPR_KIND.MUL: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.DIV: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.MOD: PREC2_MUL,
    cwast.BINARY_EXPR_KIND.AND: PREC2_MUL,
    #
    cwast.BINARY_EXPR_KIND.ADD: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.SUB: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.XOR: PREC2_ADD,
    cwast.BINARY_EXPR_KIND.OR: PREC2_ADD,
    #
    cwast.BINARY_EXPR_KIND.MAX: PREC2_MAX,
    cwast.BINARY_EXPR_KIND.MIN: PREC2_MAX,
    #
    cwast.BINARY_EXPR_KIND.GE: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.GT: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.LE: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.LT: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.EQ: PREC2_COMPARISON,
    cwast.BINARY_EXPR_KIND.NE: PREC2_COMPARISON,
    #
    cwast.BINARY_EXPR_KIND.ANDSC: PREC2_ANDSC,
    cwast.BINARY_EXPR_KIND.ORSC: PREC2_ORSC,
}


def _prec2(node: cwast.Expr2):
    return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind]


_FUNCTIONAL_BINOPS = (cwast.BINARY_EXPR_KIND.MAX,
                      cwast.BINARY_EXPR_KIND.MIN,
                      cwast.BINARY_EXPR_KIND.PDELTA)
_FUNCTIONAL_UNOPS = (cwast.UNARY_EXPR_KIND.ABS, cwast.UNARY_EXPR_KIND.SQRT)


def NodeNeedsParen(node, parent, nfd: cwast.NFD):
    """Do we need to add parenthesese around an expression
    so that the (naive) concrete syntax emitter does not
    produce invalid code.
    """
    if isinstance(parent, cwast.Expr2):
        if parent.binary_expr_kind in _FUNCTIONAL_BINOPS:
            return False
        if nfd.name == "expr1":
            if isinstance(node, cwast.Expr2):
                # parent: (expr2 node ...)
                # BAD EXAMPLES:
                # (* (+ a b ) c) =>  a + b * c
                return _prec2(node) < _prec2(parent) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS
        if nfd.name == "expr2":
            if isinstance(node, cwast.Expr2):
                # parent: (expr2 ... node)
                # BAD EXAMPLES:
                # (* c (+ a b)) =>  c * a + b
                # (/ c (/ a b)) =>  c / a / b
                return _prec2(node) <= _prec2(parent) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS
    elif isinstance(parent, cwast.Expr1):
        if parent.unary_expr_kind in _FUNCTIONAL_UNOPS:
            return False
        # BAD EXAMPLES:
        # (! (< a b)) => ! a < b
        return isinstance(node, cwast.Expr2) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS

    return False


def AddMissingParens(node):
    """Add Missing Parenthesis to help with translation to concrete syntax. """
    def replacer(node, parent, nfd: cwast.NFD):
        if NodeNeedsParen(node, parent, nfd):
            return cwast.ExprParen(node, x_srcloc=node.x_srcloc, x_type=node.x_type)

        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)

############################################################
# Token
############################################################


TS = str


def TokensParenList(ts: TS, lst):
    sep = False
    beg = ts.EmitBegParen("(")
    for t in lst:
        if sep:
            ts.EmitSep(",")
        sep = True
        EmitTokens(ts, t)
    ts.EmitEnd(beg)


def TokensParenGrouping(ts: TS, expr):
    beg = ts.EmitBegExprParen("(")
    EmitTokens(ts, expr)
    ts.EmitEnd(beg)


def TokensBinaryInfixNoSpace(ts: TS, name: str, node1, node2, node):
    EmitTokens(ts, node1)
    TokensAnnotationsPre(ts, node)
    ts.EmitBinOpNoSpace(name)
    EmitTokens(ts, node2)


def TokensUnarySuffix(ts: TS, name: str, node):
    EmitTokens(ts, node)
    ts.EmitUnOp(name, suffix=True)


def EmitExpr3(ts: TS, node: cwast.Expr3):
    EmitTokens(ts, node.cond)
    ts.EmitAttr("?")
    EmitTokens(ts, node.expr_t)
    ts.EmitAttr(":")
    EmitTokens(ts, node.expr_f)


def TokensMacroInvokeArgs(ts: TS, args, beg_invoke):
    had_colon = False
    sep = False
    for a in args:
        if sep:
            if not isinstance(a, cwast.EphemeralList) or not a.colon:
                ts.EmitSep(",")
        sep = True
        if isinstance(a, cwast.Id):
            ts.EmitAttr(a.FullName())
        elif isinstance(a, cwast.EphemeralList):

            if a.colon:
                assert beg_invoke is not None
                ts.EmitStmtEnd(beg_invoke)
                had_colon = True
                _EmitCodeBlock(ts, a.args)
            else:
                assert False, "EphemeralList should not longer occur in code"
                # if we reconsider this - we should use "{{ ... }}" notation
                sep2 = False
                beg = ts.EmitBegParen("{")
                for e in a.args:
                    if sep2:
                        ts.EmitSep(",")
                    sep2 = True
                    EmitTokens(ts, e)
                ts.EmitEnd(beg)
        elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeOf,
                            cwast.TypeVec, cwast.TypePtr, cwast.TypeSpan)):
            EmitTokens(ts, a)
        else:
            EmitTokens(ts, a)
    return had_colon


def TokensExprMacroInvoke(ts: TS, node: cwast.MacroInvoke):
    """Handle Expression Macros"""
    ts.EmitName(str(node.name))
    beg_paren = ts.EmitBegParen("(")
    TokensMacroInvokeArgs(ts, node.args, None)
    ts.EmitEnd(beg_paren)


def TokensValCompound(ts: TS, node: cwast.ValCompound):
    # EmitTokens(ts, node.type)
    sizes = []
    beg = ts.EmitBegExprParen("{")
    if not isinstance(node.type_or_auto, cwast.TypeAuto):
        EmitTokens(ts, node.type_or_auto)
    ts.EmitToken(TK.UNOP_SUFFIX, ":")

    sep = False
    for e in node.inits:
        if sep:
            ts.EmitSep(",")
        sep = True
        TokensAnnotationsPre(ts, e)
        start = ts.Pos()
        if isinstance(e, cwast.ValPoint):
            if not isinstance(e.point, cwast.ValAuto):
                EmitTokens(ts, e.point)
                ts.EmitAttr("=")
            EmitTokens(ts, e.value_or_undef)
        else:
            assert False
        sizes.append(ts.Pos() - start)
    if len(sizes) > 5 and max(sizes) < MAX_LINE_LEN:
        beg.long_array_val = True
    ts.EmitEnd(beg)


def TokensVecType(ts: TS, size, type):
    beg = ts.EmitBegVecTypeParen("[")
    EmitTokens(ts, size)
    ts.EmitEnd(beg)
    EmitTokens(ts, type)





def TokensTypeFun(ts: TS, node: cwast.TypeFun):
    ts.EmitUnOp("funtype")
    _EmitParameterList(ts, node.params)
    EmitTokens(ts, node.result)


def TokensExprIndex(ts: TS, node: cwast.ExprIndex):
    EmitTokens(ts, node.container)
    beg_paren = ts.EmitBegParen("[!" if node.unchecked else "[")
    EmitTokens(ts, node.expr_index)
    ts.EmitEnd(beg_paren)


_INFIX_OPS = set([
    cwast.ExprIndex,
    cwast.ExprField,
    cwast.Expr2,
])


def TokensExpr1(ts: TS, node: cwast.Expr1):
    kind = node.unary_expr_kind
    sym = cwast.UNARY_EXPR_SHORTCUT_CONCRETE_INV[kind]
    if kind in _FUNCTIONAL_UNOPS:
        TokensFunctional(ts, sym, [node.expr])
    else:
        TokensUnaryPrefix(ts, sym, node.expr)


def TokensExpr2(ts: TS, n: cwast.Expr2):
    kind = n.binary_expr_kind
    sym = cwast.BINARY_EXPR_SHORTCUT_INV[kind]
    if kind in _FUNCTIONAL_BINOPS:
        return TokensFunctional(ts, sym, [n.expr1, n.expr2])
    else:
        return TokensBinaryInfix(ts, sym, n.expr1, n.expr2, n)


_CONCRETE_SYNTAX: dict[Any, Callable[[TS, Any], None]] = {
    cwast.MacroInvoke: TokensExprMacroInvoke,
    #
    #
    cwast.TypeVec: lambda ts, n: TokensVecType(ts, n.size, n.type),


    cwast.TypeFun:  TokensTypeFun,
    #

    cwast.ValCompound: TokensValCompound,
    #

    cwast.Expr3: EmitExpr3,
    cwast.ExprIndex: TokensExprIndex,
    cwast.ExprField: lambda ts, n: TokensBinaryInfixNoSpace(ts, ".", n.container, n.field, n),
    cwast.ExprStmt: lambda ts, n: _TokensStmtBlock(ts, "expr", "", n.body),
    cwast.ExprParen: lambda ts, n: TokensParenGrouping(ts, n.expr),
}


def _GetDoc(node):
    for nfd in node.ATTRS:
        if nfd.name == "doc":
            val = getattr(node, "doc")
            return val
    return None


def _MaybeEmitDoc(out, node):
    doc = _GetDoc(node)
    if doc:
        for line in doc.split("\n"):
            if not line:
                out += [PP.String(";"), PP.LineBreak()]
            else:
                out += [PP.String("; " + line), PP.LineBreak()]


def _MaybeEmitAnnotations(out, node):
    for nfd in node.ATTRS:
        if nfd.kind is not cwast.NFK.ATTR_BOOL:
            continue
        field = nfd.name
        if field in ("untagged", "mut", "unchecked"):
            # these are handled by the ! suffix
            continue
        val = getattr(node, field)
        if not val:
            continue
        if field not in ("pub", "wrapped", "ref", "poly"):
            field = "{{" + field + "}}"
        out += [PP.String(field), PP.Break()]


def WithExcl(name: str, mutable: bool) -> str:
    return name + "!" if mutable else name


def KW(node) -> str:
    return node.ALIAS


def _EmitParenList(out, lst):
    out += [PP.String("(")]
    first = True
    for param in lst:
        if first:
            out += [PP.Break(0)]
        else:
            out += [PP.WeakBreak(0), PP.String(","), PP.Break()]
        first = False
        _MaybeEmitDoc(out, param)
        out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
        _MaybeEmitAnnotations(out, param)
        _EmitExprOrType(out, param)
        out += [PP.End()]
    out += [PP.Break(0), PP.String(")")]


def _EmitFunctional(out, name, nodes: list):
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
    if isinstance(name, str):
        out += [PP.String(name)]
    else:
        _EmitExprOrType(out, name)
    out += [PP.WeakBreak(0)]
    _EmitParenList(out, nodes)
    out += [PP.End()]

def _EmitParameterList(out, lst):
    out += [PP.Begin(PP.BreakType.CONSISTENT, 2), PP.String("(")]
    first = True
    for param in lst:
        if first:
            out += [PP.Break(0)]
        else:
            out += [PP.WeakBreak(0), PP.String(","), PP.Break()]
        first = False
        _MaybeEmitDoc(out, param)
        #
        out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
        _MaybeEmitAnnotations(out, param)
        out += [PP.String(str(param.name)), PP.Break()]
        if isinstance(param, cwast.FunParam):
            _EmitExprOrType(out, param.type)
        elif isinstance(param, cwast.ModParam):
            out += [PP.String(param.mod_param_kind.name)]
        elif isinstance(param, cwast.MacroParam):
            out += [PP.String(param.macro_param_kind.name)]
        else:
            assert False
        out += [PP.End()]
    out += [PP.Break(0), PP.String(")"), PP.End()]

def _EmitUnary(out, a, b):
    if isinstance(a, str):
        out += [PP.String(a)]
    else:
        _EmitExprOrType(out, a)

    out += [PP.Break(0)]
    if isinstance(b, str):
        out += [PP.String(b)]
    else:
        _EmitExprOrType(out, b)


def _EmitExpr1(out, node: cwast.Expr1):
    kind = node.unary_expr_kind
    sym = cwast.UNARY_EXPR_SHORTCUT_CONCRETE_INV[kind]
    if kind in _FUNCTIONAL_UNOPS:
        _EmitFunctional(out, sym, [node.expr])
    else:
        _EmitUnary(out, sym, node.expr)


def _EmitExpr2(out, n: cwast.Expr2):
    kind = n.binary_expr_kind
    sym = cwast.BINARY_EXPR_SHORTCUT_INV[kind]
    if kind in _FUNCTIONAL_BINOPS:
        _EmitFunctional(out, sym, [n.expr1, n.expr2])
    else:
        _EmitExprOrType(out, n.expr1)
        out += [PP.Break()]
        _MaybeEmitAnnotations(out, n)
        out += [PP.String(sym), PP.Break()]
        _EmitExprOrType(out, n.expr2)


_EMITTER_TAB: dict[Any, Callable[[Any, Any], None]] = {
    cwast.Id: lambda out, n:  out.extend([PP.String(n.FullName())]),
    cwast.MacroId: lambda out, n: out.extend([PP.String(str(n.name))]),
    #
    cwast.ValTrue: lambda out, n: out.append(PP.String(KW(n))),
    cwast.ValFalse: lambda out, n: out.append(PP.String(KW(n))),
    cwast.ValUndef: lambda out, n: out.append(PP.String(KW(n))),
    cwast.ValVoid: lambda out, n: out.append(PP.String(KW(n))),
    cwast.ValAuto: lambda out, n: out.append(PP.String(KW(n))),
    cwast.TypeAuto: lambda out, n: out.append(PP.String(KW(n))),
    #
    cwast.ValNum: lambda out, n: out.append(PP.String(n.number)),
    cwast.TypeBase: lambda out, n: out.append(
        PP.String(cwast.BaseTypeKindToKeyword(n.base_type_kind))),
    #
    cwast.ExprFront: lambda out, n: _EmitFunctional(out, WithExcl(KW(n), n.mut), [n.container]),
    cwast.ExprUnionTag: lambda out, n: _EmitFunctional(out, KW(n), [n.expr]),
    cwast.ExprAs: lambda out, n: _EmitFunctional(out, KW(n), [n.expr, n.type]),
    cwast.ExprIs: lambda out, n: _EmitFunctional(out,  KW(n), [n.expr, n.type]),
    cwast.ExprOffsetof: lambda out, n: _EmitFunctional(out, KW(n), [n.type, n.field]),
    cwast.ExprLen: lambda out, n: _EmitFunctional(out, KW(n), [n.container]),
    cwast.ExprSizeof: lambda out, n: _EmitFunctional(out, KW(n), [n.type]),
    cwast.ExprTypeId: lambda out, n: _EmitFunctional(out, KW(n), [n.type]),
    cwast.ExprUnsafeCast: lambda out, n: _EmitFunctional(out, KW(n), [n.expr, n.type]),
    cwast.ExprBitCast: lambda out, n: _EmitFunctional(out, KW(n), [n.expr, n.type]),
    cwast.ExprNarrow: lambda out, n: _EmitFunctional(out, WithExcl(KW(n), n.unchecked), [n.expr, n.type]),
    cwast.ExprWiden: lambda out, n: _EmitFunctional(out, KW(n), [n.expr, n.type]),
    cwast.ExprWrap: lambda out, n: _EmitFunctional(out, KW(n), [n.expr, n.type]),
    cwast.ExprUnwrap: lambda out, n: _EmitFunctional(out, KW(n), [n.expr]),
    cwast.ExprStringify: lambda out, n: _EmitFunctional(out, KW(n), [n.expr]),
    cwast.ExprSrcLoc: lambda out, n: _EmitFunctional(out, KW(n), [n.expr]),
    cwast.ExprCall: lambda out, n: _EmitFunctional(out, n.callee, n.args),
    #
    cwast.TypeSpan: lambda out, n: _EmitFunctional(out, WithExcl("span", n.mut), [n.type]),
    cwast.TypeOf: lambda out, n: _EmitFunctional(out, KW(n), [n.expr]),
    cwast.TypeUnion: lambda out, n: _EmitFunctional(out, WithExcl("union", n.untagged), n.types),
    cwast.TypeUnionDelta: lambda out, n: _EmitFunctional(out, KW(n), [n.type, n.subtrahend]),
    cwast.ValSpan: lambda out, n: _EmitFunctional(out, "make_span", [n.pointer, n.expr_size]),
    #
    cwast.ExprPointer: lambda out, n: _EmitFunctional(
        out, cwast.POINTER_EXPR_SHORTCUT_INV[n.pointer_expr_kind],
        [n.expr1, n.expr2] if isinstance(n.expr_bound_or_undef, cwast.ValUndef) else
        [n.expr1, n.expr2, n.expr_bound_or_undef]),
    #
    cwast.ValString: lambda out, n:  out.extend([PP.String(n.render())]),
    #
    cwast.Expr1: _EmitExpr1,
    cwast.Expr2: _EmitExpr2,
    #
    cwast.ExprDeref: lambda out, n: _EmitUnary(out, "^", n.expr),
    cwast.ExprAddrOf: lambda out, n: _EmitUnary(out, WithExcl(_ADDRESS_OF_OP, n.mut), n.expr_lhs),
    cwast.TypePtr: lambda out, n: _EmitUnary(out, WithExcl("^", n.mut), n.type),

}


def _EmitExprOrType(out, node):
    # emit any comments and annotations preceeding the node
    if node.__class__ not in _INFIX_OPS:
        _MaybeEmitAnnotations(out, node)
    emitter = _EMITTER_TAB.get(node.__class__)
    if emitter:
        emitter(out, node)
    else:
        out += [PP.String("TODO-EXPR")]
    return

    gen = _CONCRETE_SYNTAX.get(node.__class__)
    assert gen, f"unknown node {node.__class__}"
    gen(ts, node)
    # emit any tail comments
    if node.__class__ not in _INFIX_OPS:
        TokensAnnotationsPost(ts, node)


def _EmitStmtSet(out, kind, lhs, rhs):
    out += [PP.String("set"), PP.Break()]
    _EmitExprOrType(out, lhs)
    out += [PP.Break(), PP.String(kind),
            PP.Break()]
    _EmitExprOrType(out, rhs)


def _EmitStmtLetOrGlobal(out, kind: str, name: str, type_or_auto, init_or_auto):
    out += [PP.String(kind), PP.Break(),
            PP.String(str(name))]
    if not isinstance(type_or_auto, cwast.TypeAuto):
        out += [PP.Break()]
        _EmitExprOrType(out, type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        out += [PP.Break(), PP.String("="), PP.Break()]
        _EmitExprOrType(out, init_or_auto)


def _IsColonEmphemeral(node) -> bool:
    return isinstance(node, cwast.EphemeralList) and node.colon


def _IsMacroWithBlock(node: cwast.MacroInvoke) -> bool:
    if node.name in cwast.BUILT_IN_STMT_MACROS:
        return True
    if node.args:
        last = node.args[-1]
        if _IsColonEmphemeral(last):
            return True
    return False


def _GetOriginalVarName(node) -> str:
    if isinstance(node, cwast.Id):
        return node.FullName()
    else:
        assert isinstance(node, cwast.MacroId), f"{node}"
        return str(node.name)


def _EmitIdList(out, lst):
    out += [PP.Begin(PP.BreakType.CONSISTENT, 2), PP.String("[")]
    first = True
    for gen_id in lst:
        if first:
            out += [PP.Break(0)]
        else:
            out += [PP.WeakBreak(0), PP.String(","), PP.Break()]
        first = False
        assert isinstance(gen_id, cwast.MacroId)
        out += [PP.String(gen_id.name.name)]
    out += [PP.Break(0), PP.String("]"), PP.End()]


def _EmitStmtMacroInvoke(out, node: cwast.MacroInvoke):
    """Handle  Macro Invocation in Stmt Context"""
    name = node.name.name
    out += [PP.String(str(name))]
    is_block_like = _IsMacroWithBlock(node)
    if not is_block_like:
        out += [PP.Break(0),
                PP.Begin(PP.BreakType.INCONSISTENT, 2),
                PP.String("(")]
    args = node.args
    if name == "for":
        out += [PP.Break(),
                PP.String(_GetOriginalVarName(args[0])),
                PP.Break(),
                PP.String("="),
                PP.Break(),
                ]
        args = args[1:]
    elif name == "tryset":
        out += [PP.Break(),
                PP.String(_GetOriginalVarName(args[0])),
                PP.Break(),
                PP.String("="),
                PP.Break(),
                ]
        args = args[1:]
    elif name == "trylet" or name == "trylet!":
        out += [PP.Break(),
                PP.String(_GetOriginalVarName(args[0])),
                PP.Break()]
        _EmitExprOrType(out, args[1])
        out += [PP.Break(),
                PP.String("="),
                PP.Break(),
                ]
        args = args[2:]
    #
    first = True
    for a in args:
        if _IsColonEmphemeral(a):
            out += [PP.Break(0), PP.String(":"), PP.End()]
            out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
            _EmitStatements(out, a.args)
            continue
        elif not first:
            out += [PP.Break(0), PP.String(","), PP.Break()]
        first = False
        #
        if isinstance(a, cwast.Id):
            out += [PP.String(a.FullName())]
        elif isinstance(a, cwast.EphemeralList):
            out += [PP.String("TODO-LIST")]
        else:
            _EmitExprOrType(out, a)

    if not is_block_like:
        out += [PP.Break(0), PP.String(")"), PP.End()]


def _EmitStatements(out, lst):
    emit_break = False
    for child in lst:
        if emit_break:
            out += [PP.Break()]
        emit_break = True
        _EmitStatement(out, child)


def _EmitStatement(out, n):
    _MaybeEmitDoc(out, n)
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
    _MaybeEmitAnnotations(out, n)
    #
    if isinstance(n, cwast.StmtContinue):
        out += [PP.String("continue")]
        if n.target:
            out += [PP.Break(), PP.String(n.target.name)]
    elif isinstance(n, cwast.StmtBreak):
        out += [PP.String("break")]
        if n.target:
            out += [PP.Break(), PP.String(n.target.name)]
    elif isinstance(n, cwast.StmtReturn):
        out += [PP.String("return")]
        if not isinstance(n.expr_ret, cwast.ValVoid):
            out += [PP.Break()]
            _EmitExprOrType(out, n.expr_ret)
    elif isinstance(n, cwast.StmtTrap):
        out += [PP.String("trap")]
    elif isinstance(n, cwast.StmtAssignment):
        _EmitStmtSet(out, "=", n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.StmtCompoundAssignment):
        _EmitStmtSet(out,
                     cwast.ASSIGNMENT_SHORTCUT_INV[n.assignment_kind],
                     n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.DefVar):
        _EmitStmtLetOrGlobal(out, WithExcl("let", n.mut),
                             n.name, n.type_or_auto, n.initial_or_undef_or_auto)
    elif isinstance(n, cwast.StmtExpr):
        out += [PP.String("do"), PP.Break()]
        _EmitExprOrType(out, n.expr)
    elif isinstance(n, cwast.StmtDefer):
        out += [PP.String("defer"), PP.Break(0), PP.String(":"),
                PP.Break(),
                PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, n.body)
        out += [PP.End()]

    elif isinstance(n, cwast.StmtCond):
        out += [PP.String("cond"), PP.Break(0), PP.String(":"),
                PP.End(),
                PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, n.cases)
    elif isinstance(n, cwast.Case):
        out += [PP.String("case"), PP.Break()]
        _EmitExprOrType(out, n.cond)
        out += [PP.Break(0), PP.String(":"), PP.End(),
                PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, n.body)
    elif isinstance(n, cwast.MacroInvoke):
        _EmitStmtMacroInvoke(out, n)
    elif isinstance(n, cwast.MacroId):
        out += [PP.String(str(n.name))]
    elif isinstance(n, cwast.StmtBlock):
        out += [PP.String("block"), PP.Break(), PP.String(str(n.label)),
                PP.Break(0), PP.String(":"), PP.End(),
                PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, n.body)
    elif isinstance(n, cwast.StmtIf):
        out += [PP.String("if"), PP.Break()]
        _EmitExprOrType(out, n.cond)
        out += [PP.Break(0), PP.String(":"), PP.End(),
                PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, n.body_t)
        if n.body_f:
            out += [PP.End(), PP.Break(),
                    PP.Begin(PP.BreakType.INCONSISTENT, 2),
                    PP.String("else"), PP.Break(0), PP.String(":"),
                    PP.End(), PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
            _EmitStatements(out, n.body_f)
    elif isinstance(n, cwast.MacroFor):
        out += [PP.String("mfor"), PP.Break(), PP.String(str(n.name)),
                PP.Break(), PP.String(str(n.name_list)),   PP.Break(0), PP.String(":"),
                PP.End(), PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]

        # we know the content of body of the MacroFor must be stmts
        # since it occurs in a stmt context
        _EmitStatements(out, n.body_f)

    else:
        assert False, f"{n}"
    out += [PP.End()]


def _EmitTokensExprMacroBlock(out, stmts):
    emit_break = False
    for child in stmts:
        if emit_break:
            out += [PP.Break()]
        emit_break = True
        _EmitExprOrType(out, child)


def _EmitTokensToplevel(out, node):
    _MaybeEmitDoc(out, node)
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
    _MaybeEmitAnnotations(out, node)

    if isinstance(node, cwast.DefGlobal):
        _EmitStmtLetOrGlobal(out, WithExcl("global", node.mut),
                             node.name, node.type_or_auto, node.initial_or_undef_or_auto)
    elif isinstance(node, cwast.Import):
        out += [PP.String("import"),
                PP.Break(),
                PP.String(str(node.name))]
        path = node.path
        if path:
            if "/" in path:
                path = '"' + path + '"'
            out += [PP.Break(), PP.String("="), PP.Break(), PP.String(path)]
        if node.args_mod:
            pass
            # TokensParenList(ts, node.args_mod)
    elif isinstance(node, cwast.DefType):
        out += [PP.String("type"),
                PP.Break(),
                PP.String(str(node.name)),
                PP.Break(), PP.String("="), PP.Break()]
        _EmitExprOrType(out, node.type)
    elif isinstance(node, cwast.DefRec):
        out += [PP.String("rec"),
                PP.Break(),
                PP.String(str(node.name)),
                PP.Break(0),
                PP.String(":"), PP.End()]
        out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        emit_break = False
        for f in node.fields:
            _MaybeEmitDoc(out, f)
            if emit_break:
                out += [PP.Break()]
            emit_break = True
            out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
            _MaybeEmitAnnotations(out, f)
            out += [PP.String(str(f.name)), PP.Break()]
            _EmitExprOrType(out, f.type)
            out += [PP.End()]
    elif isinstance(node, cwast.StmtStaticAssert):
        out += [PP.String("static_assert"), PP.Break()]
        _EmitExprOrType(out, node.cond)
        out += [PP.End()]
    elif isinstance(node, cwast.DefEnum):
        out += [PP.String("enum"),
                PP.Break(),
                PP.String(str(node.name)),
                PP.Break(),
                PP.String(node.base_type_kind.name.lower()),
                PP.Break(0),
                PP.String(":"),
                PP.End()]
        out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        for ef in node.items:
            _MaybeEmitDoc(out, ef)
            out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
            _MaybeEmitAnnotations(out, ef)
            out += [PP.String(str(ef.name)), PP.Break()]
            # EmitTokens(ts, ef.value_or_auto)
            out += [PP.String("VALUE"),
                    PP.End()]
    elif isinstance(node, cwast.DefFun):
        out += [PP.String("fun"),
                PP.Break(),
                PP.String(str(node.name))]
        out += [PP.Break(0)]
        _EmitParameterList(out, node.params)
        out += [PP.Break()]
        _EmitExprOrType(out, node.result)
        out += [PP.Break(0), PP.String(":"), PP.End()]
        out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        _EmitStatements(out, node.body)
    elif isinstance(node, cwast.DefMacro):
        out += [PP.String("macro"),
                PP.Break(),
                PP.String(str(node.name)),
                PP.Break(),
                PP.String(node.macro_result_kind.name),
                PP.Break()]
        _EmitParameterList(out, node.params_macro)
        out += [PP.Break()]
        _EmitIdList(out, node.gen_ids)
        out += [PP.Break(0), PP.String(":")]
        out += [PP.End()]
        out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 4)]
        if node.macro_result_kind in (cwast.MACRO_PARAM_KIND.STMT, cwast.MACRO_PARAM_KIND.STMT_LIST):
            _EmitStatements(out, node.body_macro)
        else:
            _EmitTokensExprMacroBlock(out, node.body_macro)
    else:
        assert False
    out += [PP.End()]


def EmitTokensModule(out: list[PP.Token], node: cwast.DefMod):
    _MaybeEmitDoc(out, node)
    out += [PP.Begin(PP.BreakType.INCONSISTENT, 2)]
    _MaybeEmitAnnotations(out, node)

    out += [PP.String("module")]
    if node.params_mod:
        out += [PP.Break(0)]
        _EmitParameterList(out, node.params_mod)
    out += [PP.Break(0), PP.String(":"), PP.End()]
    if node.body_mod:
        out += [PP.Begin(PP.BreakType.FORCE_LINE_BREAK, 0)]
        emit_break = False
        for child in node.body_mod:
            out += [PP.LineBreak()]
            if emit_break:
                out += [PP.LineBreak()]
            emit_break = True
            _EmitTokensToplevel(out, child)
        out += [PP.End()]

############################################################
#
############################################################


def PrettyPrint(mod: cwast.DefMod, outp):
    cwast.CheckAST(mod, set(), pre_symbolize=True)
    out: list[PP.Token] = [PP.Begin(PP.BreakType.CONSISTENT, 0)]
    EmitTokensModule(out, mod)
    out += [PP.End()]
    result = PP.PrettyPrint(out, 80)
    print(result, file=outp)


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    from FE import parse

    def process_file(inp, _outp):
        mod = parse.ReadModFromStream(inp, "stdin")
        # cwast.AnnotateRoleForMacroInvoke(mod)
        # AddMissingParens(mod)
        # cwast.EliminateEphemeralsRecursively(mod)
        PrettyPrint(mod, sys.stdout)

    def main():
        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        process_file(sys.stdin, sys.stdout)
    main()
