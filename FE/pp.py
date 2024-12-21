#!/bin/env python3
"""Concrete Syntax Pretty printer (PP) for Cwerg AST to concrete syntax

"""

import logging
import enum
import dataclasses

from typing import Optional, Any, Callable

from FE import cwast


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


def NodeNeedsParen(node, parent, field: str):
    """Do we need to add parenthesese around an expression
    so that the (naive) concrete syntax emitter does not
    produce invalid code.
    """
    if isinstance(parent, cwast.Expr2):
        if parent.binary_expr_kind in _FUNCTIONAL_BINOPS:
            return False
        if field == "expr1":
            if isinstance(node, cwast.Expr2):
                # parent: (expr2 node ...)
                # BAD EXAMPLES:
                # (* (+ a b ) c) =>  a + b * c
                return _prec2(node) < _prec2(parent) and node.binary_expr_kind not in _FUNCTIONAL_BINOPS
        if field == "expr2":
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
    def replacer(node, parent, field: str):
        if NodeNeedsParen(node, parent, field):
            return cwast.ExprParen(node, x_srcloc=node.x_srcloc, x_type=node.x_type)

        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)

############################################################
# Token
############################################################


@enum.unique
class TK(enum.Enum):
    """Token"""
    INVALID = 0

    ATTR = 1  # attribute

    SEP = 3  # sequence seperator
    BINOP = 4  # binary operator
    BINOP_NO_SPACE = 5  # binary operator without space around it

    UNOP_PREFIX = 6  # unary operator - not space afterwards
    UNOP_SUFFIX = 7  # unary operator - not space before

    ANNOTATION_SHORT = 11
    ANNOTATION_LONG = 12
    EOL_COMMENT = 13
    COMMENT = 14
    ITEM = 15
    NL = 16

    COLON_BEG = 9
    COLON_END = 10

    STMT_END = 31
    STMT_BEG = 30  # intro keyword (line beginning)

    PAREN_BEG = 20  # white space after
    PAREN_BEG_EXPR = 21  # white space before and after
    PAREN_BEG_VEC_TYPE = 22  # [12] as in "[12]int"
    PAREN_END = 23


_KEYWORDS = [
    "enum", "fun", "import", "rec", "static_assert", "type",

    "module", "defer", "block", "expr",
    "break", "continue",  "cond", "type", "if",
    "do", "case", "set", "for", "macro",
    "while", "tryset", "trap", "return",
    "mfor", "else",
]

KEYWORDS_WITH_EXCL_SUFFIX = {
    # Statements
    "trylet": "mut",
    "mlet": "mut",
    "let": "mut",
    "global": "mut",
    # Expressions
    "span": "mut",
    "front": "mut",
    "union": "untagged",
    "narrow_as": "unchecked"
}

BEG_TOKENS = set(_KEYWORDS +
                 [k for k in KEYWORDS_WITH_EXCL_SUFFIX] +
                 [k + "!" for k in KEYWORDS_WITH_EXCL_SUFFIX])

MAX_LINE_LEN = 80


@dataclasses.dataclass()
class Token:
    """Node Field Descriptor"""
    kind: TK
    tag: str
    beg: Optional["Token"] = None
    start: int = 0
    length: int = 0
    long_array_val: bool = False

    def __repr__(self):
        tag = self.tag
        if self.kind is TK.PAREN_END:
            tag = self.beg.kind.name
        elif self.kind is TK.STMT_END:
            tag = self.beg.tag

        return f"{self.kind.name} [{tag}]"


_MATCHING_CLOSING_BRACE = {
    "(": ")",
    "[": "]",
    "{": "}",
}


class TS:
    """TokenStream"""

    def __init__(self) -> None:
        self._tokens: list[Token] = []
        self._count = 0

    def tokens(self):
        return self._tokens

    def LastTokenIsCodeBlock(self) -> bool:
        if not self._tokens:
            return False
        last = self._tokens[-1]
        return last.kind is TK.COLON_END

    def Pos(self) -> int:
        return self._count

    def EmitToken(self, kind: TK, tag: str = "", beg=None):
        if tag == "(" or tag == "[":
            assert kind in (TK.PAREN_BEG, TK.PAREN_BEG_EXPR,
                            TK.PAREN_BEG_VEC_TYPE)
        # elif tag == ":":
        #    assert kind is TK.BEG_COLON
        tk = Token(kind, tag=tag, beg=beg, start=self._count)
        self._count += len(tag)
        self._tokens.append(tk)
        if beg is not None:
            beg.length = self._count - beg.start
        return tk

    def _EmitToken(self, tk: Token):
        self._count += len(tk.tag)
        self._tokens.append(tk)
        return tk

    def EmitUnOp(self, a: str, suffix=False):
        return self.EmitToken(TK.UNOP_SUFFIX if suffix else TK.UNOP_PREFIX, a)

    def EmitBinOpNoSpace(self, a: str):
        return self.EmitToken(TK.BINOP_NO_SPACE, a)

    def EmitBinOp(self, a: str):
        return self.EmitToken(TK.BINOP, a)

    def EmitStmtBeg(self, a: str):
        return self.EmitToken(TK.STMT_BEG, a)

    def EmitStmtEnd(self, beg):
        assert beg.kind is TK.STMT_BEG
        return self._EmitToken(Token(TK.STMT_END, "", beg))

    def EmitAttr(self, a: str):
        return self.EmitToken(TK.ATTR, a)

    def EmitName(self, s: str):
        return self._EmitToken(Token(TK.ITEM, s))

    def EmitAnnotationShort(self, a: str):
        return self.EmitToken(TK.ANNOTATION_SHORT, a)

    def EmitAnnotationLong(self, a: str):
        return self.EmitToken(TK.ANNOTATION_LONG, a)

    def EmitEolComment(self, a: str):
        return self.EmitToken(TK.EOL_COMMENT, a)

    def EmitComment(self, a: str):
        return self.EmitToken(TK.COMMENT, a)

    def EmitSep(self, a: str):
        return self.EmitToken(TK.SEP, a)

    def EmitNewline(self):
        return self._EmitToken(Token(TK.NL, ""))

    # space after paren
    def EmitBegParen(self, a: str):
        return self.EmitToken(TK.PAREN_BEG, a)

    def EmitBegVecTypeParen(self, a: str):
        return self.EmitToken(TK.PAREN_BEG_VEC_TYPE, a)

    # space before  and after paren
    def EmitBegExprParen(self, a: str):
        return self.EmitToken(TK.PAREN_BEG_EXPR, a)

    def EmitEnd(self, beg: Token):
        assert beg.kind in (TK.PAREN_BEG, TK.PAREN_BEG_EXPR,
                            TK.PAREN_BEG_VEC_TYPE)
        return self.EmitToken(TK.PAREN_END, _MATCHING_CLOSING_BRACE[beg.tag], beg=beg)

    def EmitColonBeg(self):
        return self.EmitToken(TK.COLON_BEG, ":")

    def EmitColonEnd(self, beg):
        assert beg.kind == TK.COLON_BEG
        return self.EmitToken(TK.COLON_END, "", beg=beg)


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


def TokensFunctional(ts: TS, name, nodes: list):
    if isinstance(name, str):
        ts.EmitName(name)
    else:
        EmitTokens(ts, name)
    TokensParenList(ts, nodes)


def TokensBinaryInfix(ts: TS, name: str, node1, node2, node):
    EmitTokens(ts, node1)
    TokensAnnotationsPre(ts, node)
    ts.EmitBinOp(name)
    EmitTokens(ts, node2)


def TokensBinaryInfixNoSpace(ts: TS, name: str, node1, node2, node):
    EmitTokens(ts, node1)
    TokensAnnotationsPre(ts, node)
    ts.EmitBinOpNoSpace(name)
    EmitTokens(ts, node2)


def TokensUnaryPrefix(ts: TS, name: str, node):
    ts.EmitUnOp(name)
    EmitTokens(ts, node)


def TokensUnarySuffix(ts: TS, name: str, node):
    EmitTokens(ts, node)
    ts.EmitUnOp(name, suffix=True)


def EmitExpr3(ts: TS, node: cwast.Expr3):
    EmitTokens(ts, node.cond)
    ts.EmitAttr("?")
    EmitTokens(ts, node.expr_t)
    ts.EmitAttr(":")
    EmitTokens(ts, node.expr_f)


def TokensAnnotationsPre(ts: TS, node):
    # handle docs first
    for field, nfd in node.ATTRS:
        # these attributes will be rendered directly
        if nfd.kind is not cwast.NFK.ATTR_STR:
            continue
        val = getattr(node, field)
        if val:
            if field == "doc":
                if val.startswith('"""'):
                    val = val[3:-3]
                else:
                    val = val[1:-1]
                for line in val.split("\n"):
                    if not line:
                        ts.EmitComment("--")
                    else:
                        ts.EmitComment("-- " + line)

            else:
                ts.EmitAnnotationLong("{{" + field + "=" + val + "}}")

    # next handle non-docs
    for field, nfd in node.ATTRS:
        if nfd.kind is not cwast.NFK.ATTR_BOOL:
            continue
        if field in ("untagged", "mut", "unchecked"):
            # these are handled by the ! suffix
            continue
        val = getattr(node, field)
        if val:
            if field not in ("pub", "wrapped", "ref", "poly"):
                field = "{{" + field + "}}"
            ts.EmitAnnotationShort(field)


def TokensAnnotationsPost(_ts: TS, _node):
    pass


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
                EmitTokensCodeBlock(ts, a.args)
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


def TokensParameterList(ts: TS, lst):
    sep = False
    beg = ts.EmitBegParen("(")
    for param in lst:
        if sep:
            ts.EmitSep(",")
        sep = True
        TokensAnnotationsPre(ts, param)
        if isinstance(param, cwast.FunParam):
            ts.EmitName(str(param.name))
            EmitTokens(ts, param.type)
        elif isinstance(param, cwast.ModParam):
            ts.EmitName(str(param.name))
            ts.EmitAttr(param.mod_param_kind.name)
        elif isinstance(param, cwast.MacroParam):
            ts.EmitName(str(param.name))
            ts.EmitAttr(param.macro_param_kind.name)
        else:
            assert False
    ts.EmitEnd(beg)


def TokensTypeFun(ts: TS, node: cwast.TypeFun):
    ts.EmitUnOp("funtype")
    TokensParameterList(ts, node.params)
    EmitTokens(ts, node.result)


def EmitTokensCodeBlock(ts: TS, stmts):
    beg_colon = ts.EmitColonBeg()
    for child in stmts:
        EmitTokensStatement(ts, child)
    ts.EmitColonEnd(beg_colon)


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


def TokensValString(ts: TS, node: cwast.ValString):
    quotes = '"""' if node.triplequoted else '"'
    prefix = ""
    if node.strkind == "raw":
        prefix = "r"
    elif node.strkind == "hex":
        prefix = "x"
    ts.EmitAttr(f'{prefix}{quotes}{node.string}{quotes}'),


def WithExcl(name: str, mutable: bool) -> str:
    return name + "!" if mutable else name


def KW(node) -> str:
    return node.ALIAS


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
    cwast.Id: lambda ts, n:  (ts.EmitAttr(n.FullName())),
    cwast.MacroId: lambda ts, n:  (ts.EmitAttr(str(n.name))),
    cwast.MacroInvoke: TokensExprMacroInvoke,
    #
    cwast.TypeAuto: lambda ts, n: ts.EmitAttr(KW(n)),
    cwast.TypeBase: lambda ts, n: ts.EmitAttr(cwast.BaseTypeKindToKeyword(n.base_type_kind)),
    #
    cwast.TypeSpan: lambda ts, n: TokensFunctional(ts, WithExcl("span", n.mut), [n.type]),
    cwast.TypeOf: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr]),
    cwast.TypeUnion: lambda ts, n: TokensFunctional(ts, WithExcl("union", n.untagged), n.types),
    cwast.TypePtr: lambda ts, n: TokensUnaryPrefix(ts, WithExcl("^", n.mut), n.type),
    cwast.TypeVec: lambda ts, n: TokensVecType(ts, n.size, n.type),
    cwast.TypeUnionDelta: lambda ts, n: TokensFunctional(ts, KW(n), [n.type, n.subtrahend]),
    cwast.TypeFun:  TokensTypeFun,
    #
    cwast.ValNum: lambda ts, n: ts.EmitAttr(n.number),
    cwast.ValTrue: lambda ts, n: ts.EmitAttr(KW(n)),
    cwast.ValFalse: lambda ts, n: ts.EmitAttr(KW(n)),
    cwast.ValUndef: lambda ts, n: ts.EmitAttr(KW(n)),
    cwast.ValVoid: lambda ts, n: ts.EmitAttr("void"),
    cwast.ValAuto: lambda ts, n: ts.EmitAttr("auto"),
    cwast.ValSpan: lambda ts, n: TokensFunctional(ts, "span", [n.pointer, n.expr_size]),
    cwast.ValString: TokensValString,
    cwast.ValCompound: TokensValCompound,
    #
    cwast.ExprFront: lambda ts, n: TokensFunctional(ts, WithExcl(KW(n), n.mut), [n.container]),
    cwast.ExprUnionTag: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr]),
    cwast.ExprAs: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr, n.type]),
    cwast.ExprIs: lambda ts, n: TokensFunctional(ts,  KW(n), [n.expr, n.type]),
    cwast.ExprOffsetof: lambda ts, n: TokensFunctional(ts, KW(n), [n.type, n.field]),
    cwast.ExprLen: lambda ts, n: TokensFunctional(ts, KW(n), [n.container]),
    cwast.ExprSizeof: lambda ts, n: TokensFunctional(ts, KW(n), [n.type]),
    cwast.ExprTypeId: lambda ts, n: TokensFunctional(ts, KW(n), [n.type]),
    cwast.ExprUnsafeCast: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr, n.type]),
    cwast.ExprBitCast: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr, n.type]),
    cwast.ExprNarrow: lambda ts, n: TokensFunctional(ts, WithExcl(KW(n), n.unchecked), [n.expr, n.type]),
    cwast.ExprWiden: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr, n.type]),
    cwast.ExprWrap: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr, n.type]),
    cwast.ExprUnwrap: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr]),
    cwast.ExprStringify: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr]),
    cwast.ExprSrcLoc: lambda ts, n: TokensFunctional(ts, KW(n), [n.expr]),
    cwast.ExprCall: lambda ts, n: TokensFunctional(ts, n.callee, n.args),
    cwast.ExprPointer: lambda ts, n: TokensFunctional(
        ts, cwast.POINTER_EXPR_SHORTCUT_INV[n.pointer_expr_kind],
        [n.expr1, n.expr2] if isinstance(n.expr_bound_or_undef, cwast.ValUndef) else
        [n.expr1, n.expr2, n.expr_bound_or_undef]),
    #
    cwast.Expr1: TokensExpr1,
    cwast.Expr2: TokensExpr2,
    cwast.Expr3: EmitExpr3,
    cwast.ExprIndex: TokensExprIndex,
    cwast.ExprField: lambda ts, n: TokensBinaryInfixNoSpace(ts, ".", n.container, n.field, n),
    cwast.ExprDeref: lambda ts, n: TokensUnarySuffix(ts, "^", n.expr),
    cwast.ExprAddrOf: lambda ts, n: TokensUnaryPrefix(ts, WithExcl(_ADDRESS_OF_OP, n.mut), n.expr_lhs),
    cwast.ExprStmt: lambda ts, n: _TokensStmtBlock(ts, "expr", "", n.body),
    cwast.ExprParen: lambda ts, n: TokensParenGrouping(ts, n.expr),
}


def EmitTokens(ts: TS, node):
    # emit any comments and annotations preceeding the node
    if node.__class__ not in _INFIX_OPS:
        TokensAnnotationsPre(ts, node)

    gen = _CONCRETE_SYNTAX.get(node.__class__)
    assert gen, f"unknown node {node.__class__}"
    gen(ts, node)
    # emit any tail comments
    if node.__class__ not in _INFIX_OPS:
        TokensAnnotationsPost(ts, node)


def _TokensSimpleStmt(ts: TS, kind: str, arg):
    beg = ts.EmitStmtBeg(kind)
    if arg:
        if isinstance(arg, str):
            ts.EmitAttr(arg)
        elif not isinstance(arg, cwast.ValVoid):
            # for return
            EmitTokens(ts, arg)
    ts.EmitStmtEnd(beg)


def _TokensStmtBlock(ts: TS, kind, arg, stmts):
    beg = ts.EmitStmtBeg(kind)
    if arg:
        if isinstance(arg, str):
            ts.EmitAttr(arg)
        else:
            EmitTokens(ts, arg)
    ts.EmitStmtEnd(beg)
    #
    EmitTokensCodeBlock(ts, stmts)


def _TokensStmtSet(ts: TS, kind, lhs, rhs):
    beg = ts.EmitStmtBeg("set")
    EmitTokens(ts, lhs)
    ts.EmitBinOp(kind)
    EmitTokens(ts, rhs)
    ts.EmitStmtEnd(beg)


def _TokensStmtLet(ts: TS, kind, name: str, type_or_auto, init_or_auto):
    beg = ts.EmitStmtBeg(kind)
    ts.EmitAttr(name)
    if not isinstance(type_or_auto, cwast.TypeAuto):
        EmitTokens(ts, type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        ts.EmitBinOp("=")
        EmitTokens(ts, init_or_auto)
    ts.EmitStmtEnd(beg)


def _IsMacroWithBlock(node: cwast.MacroInvoke):
    if node.name in cwast.BUILT_IN_STMT_MACROS:
        return True
    if node.args:
        last = node.args[-1]
        if isinstance(last, cwast.EphemeralList) and last.colon:
            return True
    return False


def _GetOriginalVarName(node) -> str:
    if isinstance(node, cwast.Id):
        return node.FullName()
    else:
        assert isinstance(node, cwast.MacroId), f"{node}"
        return str(node.name)


def _TokensStmtMacroInvoke(ts: TS, node: cwast.MacroInvoke):
    """Handles Stmt Macros"""
    beg = ts.EmitStmtBeg(str(node.name))
    is_block_like = _IsMacroWithBlock(node)
    if not is_block_like:
        beg_paren = ts.EmitBegParen("(")

    args = node.args
    name = node.name.name
    if name == "for":
        ts.EmitAttr(_GetOriginalVarName(args[0]))
        args = args[1:]
        ts.EmitBinOp("=")
    elif name == "tryset":
        EmitTokens(ts, args[0])
        args = args[1:]
        ts.EmitBinOp("=")
    elif name == "trylet" or name == "trylet!":
        ts.EmitAttr(_GetOriginalVarName(args[0]))
        EmitTokens(ts, args[1])
        args = args[2:]
        ts.EmitBinOp("=")

    had_colon = TokensMacroInvokeArgs(ts, args, beg)

    if not is_block_like:
        ts.EmitEnd(beg_paren)
    if not had_colon:
        ts.EmitStmtEnd(beg)


def EmitTokensStatement(ts: TS, n):
    TokensAnnotationsPre(ts, n)
    if isinstance(n, cwast.StmtContinue):
        _TokensSimpleStmt(ts, "continue", n.target)
    elif isinstance(n, cwast.StmtBreak):
        _TokensSimpleStmt(ts, "break", n.target)
    elif isinstance(n, cwast.StmtTrap):
        _TokensSimpleStmt(ts, "trap", "")
    elif isinstance(n, cwast.StmtReturn):
        _TokensSimpleStmt(ts, "return", n.expr_ret)
    elif isinstance(n, cwast.StmtExpr):
        _TokensSimpleStmt(ts, "do", n.expr)
    elif isinstance(n, cwast.StmtDefer):
        _TokensStmtBlock(ts, "defer", "", n.body)
    elif isinstance(n, cwast.StmtBlock):
        _TokensStmtBlock(ts, "block", n.label, n.body)
    elif isinstance(n,  cwast.Case):
        _TokensStmtBlock(ts, "case", n.cond, n.body)
    elif isinstance(n, cwast.StmtCond):
        _TokensStmtBlock(ts, "cond", "", n.cases)
    elif isinstance(n, cwast.StmtCompoundAssignment):
        _TokensStmtSet(ts, cwast.ASSIGNMENT_SHORTCUT_INV[n.assignment_kind],
                       n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.StmtAssignment):
        _TokensStmtSet(ts, "=", n.lhs, n.expr_rhs)
    elif isinstance(n, cwast.DefVar):
        _TokensStmtLet(ts, WithExcl("let", n.mut), str(n.name),
                       n.type_or_auto, n.initial_or_undef_or_auto)
    elif isinstance(n, cwast.MacroVar):
        _TokensStmtLet(ts, WithExcl("mlet", n.mut), str(n.name),
                       n.type_or_auto, n.initial_or_undef_or_auto)
    elif isinstance(n, cwast.StmtIf):
        _TokensStmtBlock(ts, "if", n.cond, n.body_t)
        if n.body_f:
            _TokensStmtBlock(ts, "else", "", n.body_f)
    elif isinstance(n, cwast.MacroFor):
        beg = ts.EmitStmtBeg("mfor")
        ts.EmitAttr(str(n.name))
        ts.EmitAttr(str(n.name_list))
        ts.EmitStmtEnd(beg)
        # we now the content of body of the MacroFor must be stmts
        # since it occurs in a stmt context
        EmitTokensCodeBlock(ts, n.body_for)
    elif isinstance(n, cwast.MacroInvoke):
        _TokensStmtMacroInvoke(ts, n)
    elif isinstance(n, cwast.MacroId):
        ts.EmitAttr(str(n.name))
        ts.EmitNewline()
    else:
        assert False, f"unexpected stmt node {n}"
    #
    if not ts.LastTokenIsCodeBlock():
        ts.EmitNewline()


def EmitTokensExprMacroBlock(ts: TS, stmts):
    beg_colon = ts.EmitColonBeg()
    for child in stmts:
        if child.__class__ in _CONCRETE_SYNTAX:
            EmitTokens(ts, child)
            ts.EmitNewline()
        else:
            assert False
    ts.EmitColonEnd(beg_colon)


def _EmitTokensToplevel(ts: TS, node):
    # extra newline before every toplevel stanza
    ts.EmitNewline()

    TokensAnnotationsPre(ts, node)
    if isinstance(node, cwast.DefGlobal):
        beg = ts.EmitStmtBeg(WithExcl("global", node.mut))
        ts.EmitName(str(node.name))
        if not isinstance(node.type_or_auto, cwast.TypeAuto):
            EmitTokens(ts, node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            ts.EmitBinOp("=")
            EmitTokens(ts, node.initial_or_undef_or_auto)
        ts.EmitStmtEnd(beg)
    elif isinstance(node, cwast.Import):
        beg = ts.EmitStmtBeg("import")
        ts.EmitName(str(node.name))
        path = node.path
        if path:
            ts.EmitBinOp("=")
            if "/" in path:
                path = '"' + path + '"'
            ts.EmitAttr(path)
        if node.args_mod:
            TokensParenList(ts, node.args_mod)
        ts.EmitStmtEnd(beg)
    elif isinstance(node, cwast.DefType):
        beg = ts.EmitStmtBeg("type")
        ts.EmitName(str(node.name))
        ts.EmitBinOp("=")
        EmitTokens(ts, node.type)
        ts.EmitStmtEnd(beg)
    elif isinstance(node, cwast.DefRec):
        beg = ts.EmitStmtBeg("rec")
        ts.EmitName(str(node.name))
        ts.EmitStmtEnd(beg)
        #
        beg_colon = ts.EmitColonBeg()
        for f in node.fields:
            TokensAnnotationsPre(ts, f)
            beg = ts.EmitStmtBeg(str(f.name))
            EmitTokens(ts, f.type)
            ts.EmitStmtEnd(beg)
            ts.EmitNewline()
        ts.EmitColonEnd(beg_colon)
    elif isinstance(node, cwast.StmtStaticAssert):
        beg = ts.EmitStmtBeg("static_assert")
        EmitTokens(ts, node.cond)
        ts.EmitStmtEnd(beg)
    elif isinstance(node, cwast.DefEnum):
        beg = ts.EmitStmtBeg("enum")
        ts.EmitName(str(node.name))
        ts.EmitAttr(node.base_type_kind.name.lower())
        ts.EmitStmtEnd(beg)
        #
        beg_colon = ts.EmitColonBeg()
        for ef in node.items:
            TokensAnnotationsPre(ts, ef)
            beg = ts.EmitStmtBeg(str(ef.name))
            EmitTokens(ts, ef.value_or_auto)
            ts.EmitStmtEnd(beg)
            ts.EmitNewline()

        ts.EmitColonEnd(beg_colon)
    elif isinstance(node, cwast.DefFun):
        beg = ts.EmitStmtBeg("fun")
        ts.EmitName(str(node.name))
        TokensParameterList(ts, node.params)
        EmitTokens(ts, node.result)
        ts.EmitStmtEnd(beg)
        #
        EmitTokensCodeBlock(ts, node.body)
    elif isinstance(node, cwast.DefMacro):
        beg = ts.EmitStmtBeg("macro")
        ts.EmitName(str(node.name))
        ts.EmitAttr(node.macro_result_kind.name)
        TokensParameterList(ts, node.params_macro)
        #
        beg_paren = ts.EmitBegParen("[")
        sep = False
        for gen_id in node.gen_ids:
            if sep:
                ts.EmitSep(",")
            sep = True
            ts.EmitAttr(str(gen_id))
        ts.EmitEnd(beg_paren)
        ts.EmitStmtEnd(beg)
        #
        if node.macro_result_kind in (cwast.MACRO_PARAM_KIND.STMT, cwast.MACRO_PARAM_KIND.STMT_LIST):
            EmitTokensCodeBlock(ts, node.body_macro)
        else:
            EmitTokensExprMacroBlock(ts, node.body_macro)
    else:
        assert False
    #
    if not ts.LastTokenIsCodeBlock():
        ts.EmitNewline()


def EmitTokensModule(ts: TS, node: cwast.DefMod):
    TokensAnnotationsPre(ts, node)
    beg = ts.EmitStmtBeg("module")
    if node.params_mod:
        TokensParameterList(ts, node.params_mod)
    ts.EmitStmtEnd(beg)
    #
    beg_colon = ts.EmitColonBeg()
    for child in node.body_mod:
        _EmitTokensToplevel(ts, child)
    ts.EmitColonEnd(beg_colon)


class Stack:
    """TBD"""

    def __init__(self):
        self._stack = []

    def depth(self):
        return len(self._stack)

    def empty(self):
        return 0 == len(self._stack)

    def push(self, tk: Token, indent_delta: int, break_after_sep=False) -> int:
        # assert tk.IsBeg(), f"{tk}"
        new_indent = self.CurrentIndent() + indent_delta
        self._stack.append((tk, new_indent, break_after_sep))
        return new_indent

    def pop(self):
        return self._stack.pop(-1)

    def CurrentIndent(self) -> int:
        if self._stack:
            return self._stack[-1][1]
        return 0

    def BreakAfterSep(self) -> bool:
        if self._stack:
            return self._stack[-1][2]
        assert False


class Sink:
    """TBD"""

    def __init__(self,  outp, indent_amount=4):
        self._indent_amount = indent_amount
        self._indent = 0
        self._col = 0
        self._outp = outp

    def CurrenColumn(self):
        return self._col

    def newline(self):
        print(file=self._outp)
        self._col = 0

    def emit_token(self, token):
        if self._col == 0:
            ws = " " * (self._indent_amount * self._indent)
            # ws = f"{len(ws):02}" + ws[2:]
            print(ws, end="", file=self._outp)
            self._col = len(ws)
        print(token, end="", file=self._outp)
        self._col += len(token)

    def emit_space(self):
        self.emit_token(" ")

    def set_indent(self, indent):
        self._indent = indent


def FormatTokenStream(tokens, stack: Stack, sink: Sink):
    """
    TK.BEG may force a new indentation level

    """
    want_space = False

    def newline():
        nonlocal want_space
        sink.newline()
        want_space = False

    while True:
        tk: Token = tokens.pop(-1)
        kind = tk.kind
        tag = tk.tag
        # maybe emit space
        if want_space:
            # if the next token is one of these we do not want a space preceeding it
            if kind not in (TK.STMT_END, TK.PAREN_END, TK.PAREN_BEG, TK.COLON_BEG,
                            TK.UNOP_SUFFIX, TK.SEP, TK.BINOP_NO_SPACE):
                sink.emit_space()
        want_space = True
        #
        if kind is TK.COMMENT:
            if sink.CurrenColumn() != 0:
                newline()
            sink.emit_token(tag)
            newline()
        elif kind is TK.COLON_BEG:
            sink.emit_token(tag)
            newline()
            indent = stack.push(tk, 1 if stack.depth() > 0 else 0)
            sink.set_indent(indent)
        elif kind in (TK.PAREN_BEG, TK.PAREN_BEG_EXPR, TK.PAREN_BEG_VEC_TYPE):
            sink.emit_token(tag)
            if sink.CurrenColumn() + tk.length > MAX_LINE_LEN:
                break_after_sep = (not tk.long_array_val) and stack.CurrentIndent(
                ) + tk.length > MAX_LINE_LEN
                indent = stack.push(
                    tk, 1, break_after_sep=break_after_sep)
                sink.set_indent(indent)
                newline()
            else:
                stack.push(tk, 0)
        elif kind is TK.STMT_BEG:
            sink.emit_token(tag)
            indent = stack.push(tk, 1)
            sink.set_indent(indent)
        elif kind is TK.STMT_END:
            beg, _, _ = stack.pop()
            assert beg.kind is TK.STMT_BEG, f"{beg}"
            sink.set_indent(stack.CurrentIndent())
        elif kind is TK.COLON_END:
            beg, _, _ = stack.pop()
            assert beg.kind is TK.COLON_BEG
            sink.set_indent(stack.CurrentIndent())
        elif kind is TK.PAREN_END:
            beg, _, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            assert beg.kind in (TK.PAREN_BEG_EXPR,
                                TK.PAREN_BEG, TK.PAREN_BEG_VEC_TYPE)
            sink.emit_token(tag)
        elif kind is TK.NL:
            newline()
        elif kind is TK.ANNOTATION_LONG:
            newline()
            sink.emit_token(tag)
            newline()
        elif kind in (TK.UNOP_SUFFIX, TK.ANNOTATION_SHORT, TK.ITEM, TK.UNOP_PREFIX, TK.BINOP,
                      TK.BINOP_NO_SPACE):
            sink.emit_token(tag)
        elif kind is TK.ATTR:
            if sink.CurrenColumn() + tk.length > MAX_LINE_LEN:
                newline()
            sink.emit_token(tag)
        elif kind is TK.SEP:
            sink.emit_token(tag)
            if stack.BreakAfterSep():
                newline()
        else:
            assert False, f"{kind}"
        #
        if kind in (TK.PAREN_BEG, TK.STMT_END, TK.PAREN_BEG_EXPR, TK.PAREN_BEG_VEC_TYPE, TK.UNOP_PREFIX, TK.BINOP_NO_SPACE):
            want_space = False
        elif kind is TK.PAREN_END:
            if tk.beg.kind is TK.PAREN_BEG_VEC_TYPE:
                want_space = False
        elif kind is TK.COLON_END:
            want_space = False
            if not tokens:
                return

        assert tokens, f"{tag} {kind}"
        # TODO: this stopped working after comment support was added
        # assert stack._stack[0][0] == "module", stack._stack[0][1] == TK.BEG


def PrettyPrint(mod: cwast.DefMod, outp):
    cwast.CheckAST(mod, set(), pre_symbolize=True)
    # we first produce an output token stream from the AST
    ts = TS()
    EmitTokensModule(ts, mod)
    tokens = list(ts.tokens())
    if 0:
        indent = 0
        for tk in tokens:
            if tk.kind in (TK.COLON_END, TK.STMT_END):
                indent -= 2

            print(" " * indent, tk)

            if tk.kind in (TK.COLON_BEG, TK.STMT_BEG):
                indent += 2

    # reverse once because popping of the end of a list is more efficient
    tokens.reverse()
    # and now format the stream
    FormatTokenStream(tokens, Stack(), Sink(outp))


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
