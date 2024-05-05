#!/usr/bin/python3
"""Concrete Syntax Pretty printer (PP) for Cwerg AST

"""

import logging
import enum
import dataclasses

from typing import Optional

from FrontEnd import cwast


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

_ANNOTATION_PREFIX = "@"
_DEREFERENCE_OP = "^"
_ADDRESS_OF_OP = "&"

_OPS_PRECENDENCE_EXPR2 = {
    cwast.BINARY_EXPR_KIND.SHL: 20,
    cwast.BINARY_EXPR_KIND.ROTL: 20,
    cwast.BINARY_EXPR_KIND.SHR: 20,
    cwast.BINARY_EXPR_KIND.ROTR: 20,
    #
    cwast.BINARY_EXPR_KIND.MUL: 30,
    cwast.BINARY_EXPR_KIND.DIV: 30,
    cwast.BINARY_EXPR_KIND.MOD: 30,
    cwast.BINARY_EXPR_KIND.AND: 30,
    cwast.BINARY_EXPR_KIND.XOR: 30,
    #
    cwast.BINARY_EXPR_KIND.OR: 35,
    cwast.BINARY_EXPR_KIND.ADD: 35,
    cwast.BINARY_EXPR_KIND.SUB: 35,
    #
    cwast.BINARY_EXPR_KIND.MAX: 40,
    cwast.BINARY_EXPR_KIND.MIN: 40,
    #
    cwast.BINARY_EXPR_KIND.GE: 60,
    cwast.BINARY_EXPR_KIND.GT: 60,
    cwast.BINARY_EXPR_KIND.LE: 60,
    cwast.BINARY_EXPR_KIND.LT: 60,
    cwast.BINARY_EXPR_KIND.EQ: 65,
    cwast.BINARY_EXPR_KIND.NE: 65,
    #
    cwast.BINARY_EXPR_KIND.ANDSC: 70,
    cwast.BINARY_EXPR_KIND.ORSC: 75,
}


def _NodeNeedsParen(node, parent, field: str):
    if isinstance(parent, cwast.Expr2):
        if field == "expr1":
            if isinstance(node, cwast.Expr2):
                return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind] > _OPS_PRECENDENCE_EXPR2[parent.binary_expr_kind]
        if field == "expr2":
            if isinstance(node, cwast.Expr2):
                return _OPS_PRECENDENCE_EXPR2[node.binary_expr_kind] > _OPS_PRECENDENCE_EXPR2[parent.binary_expr_kind]

    return False


def AddMissingParens(node):
    """Eliminate Array to Slice casts. """

    def replacer(node, parent, field: str):
        if _NodeNeedsParen(node, parent, field):
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
    KW = 2  # intro keyword (line beginning)

    SEP = 3  # sequence seperator
    BINOP = 5  # binary operator
    BINOP_NO_SPACE = 6  # binary operator

    UNOP_PREFIX = 7  # unary operator - not space afterwards
    UNOP_SUFFIX = 8  # unary operator - not space before

    END = 9
    BEG_COLON = 10

    ANNOTATION_SHORT = 11
    ANNOTATION_LONG = 12
    EOL_COMMENT = 13
    COMMENT = 14
    ITEM = 15
    EOL = 16
    BEG_PAREN = 20 # white space after
    BEG_EXPR_PAREN = 21  # white space before and after
    BEG_VEC_TYPE_PAREN = 22  # white space before and after

KEYWORDS_TOPLEVEL = [
    "enum", "fun", "import", "rec", "static_assert", "type",
]

KEYWORDS = [
    "module", "defer", "block", "expr",
    "break", "continue",  "cond", "type", "if",
    "shed", "discard", "case", "set", "for", "macro",
    "while", "tryset", "trap", "return",
    "mfor", "swap", "else",
] + KEYWORDS_TOPLEVEL

KEYWORDS_WITH_EXCL_SUFFIX = [
    "trylet", "mlet", "slice", "let", "global", "front"]

BEG_TOKENS = set(KEYWORDS + KEYWORDS_WITH_EXCL_SUFFIX + [
    k + "!" for k in KEYWORDS_WITH_EXCL_SUFFIX])

INDENT = 1
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
        if self.kind is TK.END:
            tag = self.beg.kind.name
        return f"{self.kind.name} [{tag}]"


_MATCHING_CLOSING_BRACE = {
    "(": ")",
    "[": "]",
    "{": "}",
}


class TS:
    """TokenStream"""

    def __init__(self):
        self._tokens: list[Token] = []
        self._count = 0

    def tokens(self):
        return self._tokens

    def LastTokenIsEOL(self) -> bool:
        if not self._tokens:
            return False
        last = self._tokens[-1]
        return last.kind is TK.EOL or last.kind is TK.END and last.beg.kind is TK.BEG_COLON

    def Pos(self) -> int:
        return self._count

    def EmitToken(self, kind: TK, tag="", beg=None):
        if tag == "(" or tag == "[":
            assert kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN, TK.BEG_VEC_TYPE_PAREN)
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

    def EmitKW(self, a: str):
        return self.EmitToken(TK.KW, a)

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

    def EmitStmtEnd(self):
        return self._EmitToken(Token(TK.EOL, ""))

    # space after paren
    def EmitBegParen(self, a: str):
        return self.EmitToken(TK.BEG_PAREN, a)

    def EmitBegVecTypeParen(self, a: str):
        return self.EmitToken(TK.BEG_VEC_TYPE_PAREN, a)

    # space before  and after paren
    def EmitBegExprParen(self, a: str):
        return self.EmitToken(TK.BEG_EXPR_PAREN, a)

    def EmitEnd(self, beg: Token):
        if beg.kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN, TK.BEG_VEC_TYPE_PAREN):
            return self.EmitToken(TK.END, _MATCHING_CLOSING_BRACE[beg.tag], beg=beg)
        return self.EmitToken(TK.END, beg=beg)

    def EmitBegColon(self):
        return self.EmitToken(TK.BEG_COLON, ":")


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
    ts.EmitAttr(node2)


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
            if field == "eoldoc":
                continue
            elif field == "doc":
                if val.startswith('"""'):
                    val = val[3:-3]
                else:
                    val = val[1:-1]
                for line in val.split("\n"):
                    ts.EmitComment("-- " + line)

            else:
                ts.EmitAnnotationLong(_ANNOTATION_PREFIX + field + "=" + val)

    # next handle non-docs
    for field, nfd in node.ATTRS:
        # mut is handled directly
        if nfd.kind is not cwast.NFK.ATTR_BOOL or field == "mut":
            continue

        val = getattr(node, field)
        if val:
            ts.EmitAnnotationShort(_ANNOTATION_PREFIX + field)


def TokensAnnotationsPost(ts: TS, node):
    for field, _ in node.ATTRS:
        # these attributes will be rendered directly
        if field != "eoldoc":
            continue
        val = getattr(node, field)
        if val:
            if val.startswith('"""'):
                val = val[3:-3]
            else:
                val = val[1:-1]
            ts.EmitComment("  -- " + val)


def TokensMacroInvokeArgs(ts: TS, args):
    sep = False
    for a in args:
        if sep:
            if not isinstance(a, cwast.EphemeralList) or not a.colon:
                ts.EmitSep(",")
        sep = True
        if isinstance(a, cwast.Id):
            ts.EmitAttr(a.name)
        elif isinstance(a, cwast.EphemeralList):
            if a.colon:
                EmitTokensCodeBlock(ts, a.args)
            else:
                sep2 = False
                beg = ts.EmitBegParen("{")
                for e in a.args:
                    if sep2:
                        ts.EmitSep(",")
                    sep2 = True
                    EmitTokens(ts, e)
                ts.EmitEnd(beg)
        elif isinstance(a, (cwast.TypeBase, cwast.TypeAuto, cwast.TypeOf,
                            cwast.TypeArray, cwast.TypePtr, cwast.TypeSlice)):
            EmitTokens(ts, a)
        else:
            EmitTokens(ts, a)


def TokensMacroInvoke(ts: TS, node: cwast.MacroInvoke):
    if node.name == "->":
        assert len(node.args) == 2
        TokensBinaryInfixNoSpace(
            ts, "^.", node.args[0], node.args[1].name, node)
        return
    ts.EmitKW(node.name)
    is_block_like = node.name in ["for", "while", "tryset", "trylet"]
    if not is_block_like:
        beg_paren = ts.EmitBegParen("(")

    args = node.args
    if node.name == "for" or node.name == "tryset":
        assert isinstance(args[0], (cwast.Id, cwast.MacroId)), f"{args[0]}"
        ts.EmitAttr(args[0].name)
        args = args[1:]
        ts.EmitBinOp("=")
    elif node.name == "trylet":
        assert isinstance(args[0], cwast.Id)
        ts.EmitAttr(args[0].name)
        EmitTokens(ts, args[1])
        args = args[2:]
        ts.EmitBinOp("=")

    TokensMacroInvokeArgs(ts, args)

    if not is_block_like:
        ts.EmitEnd(beg_paren)


def TokensSimpleStmt(ts: TS, kind: str, arg):
    ts.EmitAttr(kind)
    if arg:
        if isinstance(arg, str):
            ts.EmitAttr(arg)
        elif not isinstance(arg, cwast.ValVoid):
            # for return
            EmitTokens(ts, arg)

    ts.EmitStmtEnd()


def TokensStmtBlock(ts: TS, kind, arg, stmts):
    ts.EmitAttr(kind)
    if arg:
        if type(arg) == str:
            ts.EmitAttr(arg)
        else:
            EmitTokens(ts, arg)
    EmitTokensCodeBlock(ts, stmts)


def TokensStmtSet(ts: TS, kind, lhs, rhs):
    ts.EmitAttr("set")
    EmitTokens(ts, lhs)
    ts.EmitBinOp(kind)
    EmitTokens(ts, rhs)
    ts.EmitStmtEnd()


def TokensStmtLet(ts: TS, kind, name: str, type_or_auto, init_or_auto):
    ts.EmitAttr(kind)
    ts.EmitAttr(name)
    if not isinstance(type_or_auto, cwast.TypeAuto):
        EmitTokens(ts, type_or_auto)
    if not isinstance(init_or_auto, cwast.ValAuto):
        ts.EmitBinOp("=")
        EmitTokens(ts, init_or_auto)
    ts.EmitStmtEnd()


def TokensMacroFor(ts: TS, node: cwast.MacroFor):
    ts.EmitAttr("mfor")
    ts.EmitAttr(node.name)
    ts.EmitAttr(node.name_list)
    EmitTokensCodeBlock(ts, node.body_for)


def ConcreteIf(ts: TS, node: cwast.StmtIf):
    ts.EmitAttr("if")
    EmitTokens(ts, node.cond)
    EmitTokensCodeBlock(ts, node.body_t)
    #
    if node.body_f:
        ts.EmitAttr("else")
        EmitTokensCodeBlock(ts, node.body_f)


def TokensValRec(ts: TS, node: cwast.ValRec):
    EmitTokens(ts, node.type)
    beg = ts.EmitBegParen("{")
    sep = False
    for e in node.inits_field:
        if sep:
            ts.EmitSep(",")
        sep = True
        if e.init_field:
            ts.EmitAttr(e.init_field)
            ts.EmitAttr(":")
        EmitTokens(ts, e.value_or_undef)

    ts.EmitEnd(beg)


def TokensIndexVal(ts: TS, node: cwast.IndexVal):
    if not isinstance(node.init_index, cwast.ValAuto):
        EmitTokens(ts, node.init_index)
        ts.EmitAttr(":")
    EmitTokens(ts, node.value_or_undef)


def TokensVecType(ts: TS, size, type):
    beg = ts.EmitBegVecTypeParen("[")
    EmitTokens(ts, size)
    ts.EmitEnd(beg)
    EmitTokens(ts, type)


def TokensValVec(ts: TS, node: cwast.ValArray):
    TokensVecType(ts, node.expr_size, node.type)
    beg = ts.EmitBegParen("{")
    sizes = []
    sep = False
    for e in node.inits_array:
        assert isinstance(e, cwast.IndexVal)
        if sep:
            ts.EmitSep(",")
        sep = True
        start = ts.Pos()
        EmitTokens(ts, e)
        sizes.append(ts.Pos() - start)
    if len(sizes) > 5 and max(sizes) < MAX_LINE_LEN:
        beg.long_array_val = True
    ts.EmitEnd(beg)


def WithMut(name: str, mutable: bool) -> str:
    return name + "!" if mutable else name


def TokensTypeFun(ts: TS, node: cwast.TypeFun):
    ts.EmitUnOp("funtype")
    beg_paren = ts.EmitBegParen("(")
    sep = False
    for p in node.params:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(p.name)
        EmitTokens(ts, p.type)
    ts.EmitEnd(beg_paren)
    EmitTokens(ts, node.result)


def TokensRecField(ts: TS, node: cwast.RecField):
    ts.EmitName(node.name)
    EmitTokens(ts, node.type)
    ts.EmitStmtEnd()


def TokensEnumVal(ts: TS, node: cwast.EnumVal):
    ts.EmitName(node.name)
    EmitTokens(ts, node.value_or_auto)
    ts.EmitStmtEnd()


def EmitTokenFunSig(ts: TS, params, result):
    beg_paren = ts.EmitBegParen("(")
    sep = False
    for p in params:
        if sep:
            ts.EmitSep(",")
        sep = True
        ts.EmitAttr(p.name)
        EmitTokens(ts, p.type)
    ts.EmitEnd(beg_paren)
    EmitTokens(ts, result)


def EmitTokensCodeBlock(ts: TS, stmts):
    beg = ts.EmitBegColon()
    for child in stmts:
        EmitTokens(ts, child)
        if not ts.LastTokenIsEOL():
            ts.EmitStmtEnd()
    ts.EmitEnd(beg)


def TokensMacroId(ts: TS, node: cwast.MacroId):
    ts.EmitAttr(node.name)


def TokensExprIndex(ts: TS, node: cwast.ExprIndex):
    EmitTokens(ts, node.container)
    beg_paren = ts.EmitBegParen("[")
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


_CONCRETE_SYNTAX = {
    cwast.Id: lambda ts, n:  (ts.EmitAttr(n.name)),
    #
    cwast.MacroId: TokensMacroId,
    cwast.MacroInvoke: TokensMacroInvoke,
    cwast.MacroVar: lambda ts, n: TokensStmtLet(ts, WithMut("mlet", n.mut), n.name, n.type_or_auto, n.initial_or_undef_or_auto),
    cwast.MacroFor: TokensMacroFor,
    #
    cwast.TypeAuto: lambda ts, n: ts.EmitAttr("auto"),
    cwast.TypeBase: lambda ts, n: ts.EmitAttr(cwast.BaseTypeKindToKeyword(n.base_type_kind)),
    cwast.TypeSlice: lambda ts, n: TokensFunctional(ts, WithMut("slice", n.mut), [n.type]),
    cwast.TypeOf: lambda ts, n: TokensFunctional(ts, "typeof", [n.expr]),
    cwast.TypeUnion: lambda ts, n: TokensFunctional(ts, "union", n.types),
    cwast.TypePtr: lambda ts, n: TokensUnaryPrefix(ts, WithMut("^", n.mut), n.type),
    cwast.TypeArray: lambda ts, n: TokensVecType(ts, n.size, n.type),
    cwast.TypeUnionDelta: lambda ts, n: TokensFunctional(ts, "uniondelta", [n.type, n.subtrahend]),
    cwast.TypeFun:  TokensTypeFun,
    #
    cwast.ValNum: lambda ts, n: ts.EmitAttr(n.number),
    cwast.ValTrue: lambda ts, n: ts.EmitAttr("true"),
    cwast.ValFalse: lambda ts, n: ts.EmitAttr("false"),
    cwast.ValUndef: lambda ts, n: ts.EmitAttr("undef"),
    cwast.ValVoid: lambda ts, n: ts.EmitAttr("void"),
    cwast.ValAuto: lambda ts, n: ts.EmitAttr("auto"),
    cwast.ValString: TokensValString,
    cwast.ValRec: TokensValRec,
    cwast.ValArray: TokensValVec,

    #
    cwast.ExprFront: lambda ts, n: TokensFunctional(ts, WithMut("front", n.mut), [n.container]),
    cwast.ExprUnionTag: lambda ts, n: TokensFunctional(ts, "uniontag", [n.expr]),
    cwast.ExprAs: lambda ts, n: TokensFunctional(ts, "as", [n.expr, n.type]),
    cwast.ExprUnsafeCast: lambda ts, n: TokensFunctional(ts, "unsafeas", [n.expr, n.type]),
    cwast.ExprIs: lambda ts, n: TokensFunctional(ts, "is", [n.expr, n.type]),
    cwast.ExprBitCast: lambda ts, n: TokensFunctional(ts, "bitsas", [n.expr, n.type]),
    cwast.ExprOffsetof: lambda ts, n: TokensFunctional(ts, "offsetof", [n.type, cwastId(n.field)]),
    cwast.ExprLen: lambda ts, n: TokensFunctional(ts, "len", [n.container]),
    cwast.ExprSizeof: lambda ts, n: TokensFunctional(ts, "sizeof", [n.type]),
    cwast.ExprTypeId: lambda ts, n: TokensFunctional(ts, "typeid", [n.type]),
    cwast.ExprNarrow: lambda ts, n: TokensFunctional(ts, "narrowto", [n.expr, n.type]),
    cwast.Expr1: lambda ts, n: TokensUnaryPrefix(ts, cwast.UNARY_EXPR_SHORTCUT_CONCRETE_INV[n.unary_expr_kind], n.expr),
    cwast.ExprPointer: lambda ts, n: TokensFunctional(
        ts, cwast.POINTER_EXPR_SHORTCUT_INV[n.pointer_expr_kind],
        [n.expr1, n.expr2] if isinstance(n.expr_bound_or_undef, cwast.ValUndef) else
        [n.expr1, n.expr2, n.expr_bound_or_undef]),
    cwast.ExprIndex: TokensExprIndex,
    cwast.ValSlice: lambda ts, n: TokensFunctional(ts, "slice", [n.pointer, n.expr_size]),
    cwast.ExprWrap: lambda ts, n: TokensFunctional(ts, "wrapas", [n.expr, n.type]),
    cwast.ExprUnwrap: lambda ts, n: TokensFunctional(ts, "unwrap", [n.expr]),
    cwast.ExprField: lambda ts, n: TokensBinaryInfixNoSpace(ts, ".", n.container, n.field, n),
    cwast.ExprDeref: lambda ts, n: TokensUnarySuffix(ts, "^", n.expr),
    cwast.ExprAddrOf: lambda ts, n: TokensUnaryPrefix(ts, WithMut(_ADDRESS_OF_OP, n.mut), n.expr_lhs),
    cwast.Expr2: lambda ts, n: TokensBinaryInfix(ts, cwast.BINARY_EXPR_SHORTCUT_INV[n.binary_expr_kind],
                                                 n.expr1, n.expr2, n),
    cwast.Expr3: EmitExpr3,
    cwast.ExprStringify: lambda ts, n: TokensFunctional(ts, "stringify", [n.expr]),
    cwast.ExprCall: lambda ts, n: TokensFunctional(ts, n.callee, n.args),
    cwast.ExprStmt: lambda ts, n: TokensStmtBlock(ts, "expr", "", n.body),
    cwast.ExprParen: lambda ts, n: TokensParenGrouping(ts, n.expr),

    #
    cwast.StmtContinue: lambda ts, n: TokensSimpleStmt(ts, "continue", n.target),
    cwast.StmtBreak: lambda ts, n: TokensSimpleStmt(ts, "break", n.target),
    cwast.StmtTrap: lambda ts, n: TokensSimpleStmt(ts, "trap", ""),
    cwast.StmtReturn: lambda ts, n: TokensSimpleStmt(ts, "return", n.expr_ret),
    cwast.StmtExpr: lambda ts, n: TokensSimpleStmt(ts, "shed", n.expr),
    cwast.StmtDefer: lambda ts, n: TokensStmtBlock(ts, "defer", "", n.body),
    cwast.StmtBlock: lambda ts, n: TokensStmtBlock(ts, "block", n.label, n.body),
    cwast.Case: lambda ts, n: TokensStmtBlock(ts, "case", n.cond, n.body),

    cwast.StmtCond: lambda ts, n: TokensStmtBlock(ts, "cond", "", n.cases),
    cwast.StmtCompoundAssignment: lambda ts, n: TokensStmtSet(ts, cwast.ASSIGNMENT_SHORTCUT_INV[n.assignment_kind],
                                                              n.lhs, n.expr_rhs),
    cwast.StmtAssignment: lambda ts, n: TokensStmtSet(ts, "=", n.lhs, n.expr_rhs),
    cwast.DefVar: lambda ts, n: TokensStmtLet(ts, WithMut("let", n.mut), n.name, n.type_or_auto, n.initial_or_undef_or_auto),
    cwast.StmtIf: ConcreteIf,
    #
    cwast.EnumVal:  TokensEnumVal,
    cwast.RecField:  TokensRecField,
    cwast.IndexVal:  TokensIndexVal,
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


def EmitTokensToplevel(ts: TS, node):
    # extra newline before every toplevel stanza
    ts.EmitStmtEnd()

    TokensAnnotationsPre(ts, node)
    if isinstance(node, cwast.DefGlobal):
        ts.EmitKW(WithMut("global", node.mut))
        ts.EmitName(node.name)
        if not isinstance(node.type_or_auto, cwast.TypeAuto):
            EmitTokens(ts, node.type_or_auto)
        if not isinstance(node.initial_or_undef_or_auto, cwast.ValAuto):
            ts.EmitBinOp("=")
            EmitTokens(ts, node.initial_or_undef_or_auto)
        ts.EmitStmtEnd()
    elif isinstance(node, cwast.Import):
        ts.EmitKW("import")
        ts.EmitName(node.name)
        if node.alias:
            ts.EmitBinOp("as")
            ts.EmitAttr(node.alias)
        ts.EmitStmtEnd()
    elif isinstance(node, cwast.DefType):
        ts.EmitKW("type")
        ts.EmitName(node.name)
        ts.EmitBinOp("=")
        EmitTokens(ts, node.type)
        ts.EmitStmtEnd()
    elif isinstance(node, cwast.DefRec):
        ts.EmitKW("rec")
        ts.EmitName(node.name)
        beg_colon = ts.EmitBegColon()
        for f in node.fields:
            EmitTokens(ts, f)
        ts.EmitEnd(beg_colon)
    elif isinstance(node, cwast.StmtStaticAssert):
        ts.EmitKW("static_assert")
        EmitTokens(ts, node.cond)
        ts.EmitStmtEnd()
    elif isinstance(node, cwast.DefEnum):
        ts.EmitKW("enum")
        ts.EmitName(node.name)
        ts.EmitAttr(node.base_type_kind.name.lower())
        beg_colon = ts.EmitBegColon()
        for f in node.items:
            EmitTokens(ts, f)
        ts.EmitEnd(beg_colon)
    elif isinstance(node, cwast.DefFun):
        ts.EmitKW("fun")
        ts.EmitName(node.name)
        EmitTokenFunSig(ts, node.params, node.result)
        EmitTokensCodeBlock(ts, node.body)
    elif isinstance(node, cwast.DefMacro):
        ts.EmitKW("macro")
        ts.EmitName(node.name)
        ts.EmitAttr(node.macro_result_kind.name)
        beg_paren = ts.EmitBegParen("(")
        sep = False
        for p in node.params_macro:
            if sep:
                ts.EmitSep(",")
            sep = True
            ts.EmitAttr(p.name)
            ts.EmitAttr(p.macro_param_kind.name)
        ts.EmitEnd(beg_paren)
        #
        beg_paren = ts.EmitBegParen("[")
        sep = False
        for gen_id in node.gen_ids:
            if sep:
                ts.EmitSep(",")
            sep = True
            ts.EmitAttr(gen_id)
        ts.EmitEnd(beg_paren)
        EmitTokensCodeBlock(ts, node.body_macro)
    else:
        assert False


def EmitTokensModule(ts: TS, node):
    ts.EmitKW("module")
    # we do not want the next item to be indented
    ts.EmitName(node.name)
    beg_colon = ts.EmitBegColon()
    for child in node.body_mod:
        EmitTokensToplevel(ts, child)
    ts.EmitEnd(beg_colon)


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

    def __init__(self):
        self._indent = 0
        self._col = 0

    def CurrenColumn(self):
        return self._col

    def newline(self):
        print()
        self._col = 0

    def emit_token(self, token):
        if self._col == 0:
            ws = " " * (4 * self._indent)
            # ws = f"{len(ws):02}" + ws[2:]
            print(ws, end="")
            self._col = len(ws)
        print(token, end="")
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
            if kind not in (TK.END, TK.BEG_PAREN, TK.BEG_COLON,
                            TK.UNOP_SUFFIX, TK.SEP, TK.BINOP_NO_SPACE):
                sink.emit_space()
        want_space = True
        #
        if kind is TK.COMMENT:
            sink.emit_token(tag)
            newline()
        elif kind is TK.BEG_COLON:
            sink.emit_token(tag)
            newline()
            indent = stack.push(tk, INDENT if stack.depth() > 0 else 0)
            sink.set_indent(indent)
        elif kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN, TK.BEG_VEC_TYPE_PAREN):
            sink.emit_token(tag)
            if sink.CurrenColumn() + tk.length > MAX_LINE_LEN:
                break_after_sep = (not tk.long_array_val) and stack.CurrentIndent(
                ) + tk.length > MAX_LINE_LEN
                indent = stack.push(
                    tk, INDENT, break_after_sep=break_after_sep)
                sink.set_indent(indent)
                newline()
            else:
                stack.push(tk, 0)

        elif kind is TK.END:
            beg, _, _ = stack.pop()
            sink.set_indent(stack.CurrentIndent())
            if beg.kind is TK.BEG_COLON:
                pass
            elif beg.kind in (TK.BEG_EXPR_PAREN, TK.BEG_PAREN, TK.BEG_VEC_TYPE_PAREN):
                assert tag
                sink.emit_token(tag)
            else:
                assert False
        elif kind is TK.EOL:
            newline()
        elif kind is TK.ANNOTATION_LONG:
            newline()
            sink.emit_token(tag)
            newline()
        elif kind in (TK.UNOP_SUFFIX, TK.ANNOTATION_SHORT, TK.ITEM, TK.KW, TK.UNOP_PREFIX, TK.BINOP,
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
        if kind in (TK.BEG_PAREN, TK.BEG_EXPR_PAREN, TK.BEG_VEC_TYPE_PAREN, TK.UNOP_PREFIX, TK.BINOP_NO_SPACE):
            want_space = False
        if kind is TK.END:
            if tk.beg.kind is TK.BEG_VEC_TYPE_PAREN:
                want_space = False
            elif tk.beg.kind is TK.BEG_COLON:
                want_space = False
                if not tokens:
                    return

        assert tokens, f"{tag} {kind}"
        # TODO: this stopped working after comment support was added
        # assert stack._stack[0][0] == "module", stack._stack[0][1] == TK.BEG


############################################################
#
############################################################
if __name__ == "__main__":
    import argparse

    from FrontEnd import parse_sexpr

    def main():
        parser = argparse.ArgumentParser(description='pretty_printer')
        parser.add_argument('files', metavar='F', type=str, nargs='+',
                            help='an input source file')
        args = parser.parse_args()

        logging.basicConfig(level=logging.WARN)
        logger.setLevel(logging.INFO)
        assert len(args.files) == 1
        assert args.files[0].endswith(".cw")

        with open(args.files[0], encoding="utf8") as f:
            mods = parse_sexpr.ReadModsFromStream(f)
            assert len(mods) == 1
            for m in mods:
                assert isinstance(m, cwast.DefMod)
                cwast.AnnotateRoleForMacroInvoke(m)
                AddMissingParens(m)
                cwast.CheckAST(m, set(), pre_symbolize=True)
            # we first produce an output token stream from the AST
            ts = TS()
            EmitTokensModule(ts, mods[0])
            tokens = list(ts.tokens())
            if 0:
                indent = 0
                for tk in tokens:
                    if tk.kind is TK.END and tk.beg.kind is TK.BEG_COLON:
                        indent -= 2
                    print(" " * indent, tk)
                    if tk.kind is TK.BEG_COLON:
                        indent += 2

            # reverse once because popping of the end of a list is more efficient
            tokens.reverse()
            # and now format the stream
            FormatTokenStream(tokens, Stack(), Sink())

    main()
