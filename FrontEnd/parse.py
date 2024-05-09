#!/usr/bin/python3
"""
The Parser is recursice descent (RD) combined with Pratt Parsing for
Expressions.

References:

https://martin.janiczek.cz/2023/07/03/demystifying-pratt-parsers.html
https://github.com/feroldi/pratt-parser-in-python

"""


import re

import logging
import enum
import dataclasses

from typing import Any, Tuple, Union, List, Optional

from FrontEnd import cwast
from FrontEnd import pp
from FrontEnd import string_re

logger = logging.getLogger(__name__)


@enum.unique
class TK_KIND(enum.Enum):
    INVALID = 0
    KW = enum.auto()
    ANNOTATION = enum.auto()
    COMMENT = enum.auto()
    OP1 = enum.auto()
    OP2 = enum.auto()
    COMMA = enum.auto()
    COLON = enum.auto()
    QUESTION_MARK = enum.auto()
    DOT = enum.auto()
    EOL = enum.auto()
    WS = enum.auto()
    ID = enum.auto()
    NUM = enum.auto()
    CHAR = enum.auto()
    STR = enum.auto()
    MSTR = enum.auto()  # multi-line
    RMSTR = enum.auto()  # multi-line
    XMSTR = enum.auto()  # multi-line
    ASSIGN = enum.auto()
    COMPOUND_ASSIGN = enum.auto()
    PAREN_OPEN = enum.auto()
    PAREN_CLOSED = enum.auto()
    SQUARE_OPEN = enum.auto()
    SQUARE_CLOSED = enum.auto()
    CURLY_OPEN = enum.auto()
    CURLY_CLOSED = enum.auto()
    #
    SPECIAL_MUT = enum.auto()
    SPECIAL_EOF = enum.auto()


_KEYWORDS_SIMPLE = [
    "auto",    # type/val
    "slice",
    "typeof",
    "union",
    "array",
    "uniondelta",
    "true",
    "false",
    "front",
    "uniontag",
    "is",
    "funtype",
    "else",
    #
    "pinc",
    "pdec",
    #
    "narrowto",
    #
    "as",
    "wrapas",
    "bitsas",
    "unsafeas",
    "asnarrowed",
    "unwrap",
    #
    "offsetof",
    "sizeof",
    "len",
    #
    "stringfy",
]


KEYWORDS = {}
for k in _KEYWORDS_SIMPLE:
    KEYWORDS[k] = TK_KIND.KW
for k in pp.KEYWORDS:
    KEYWORDS[k] = TK_KIND.KW
for k in cwast.BASE_TYPE_KIND:
    if k is not cwast.BASE_TYPE_KIND.INVALID:
        KEYWORDS[cwast.BaseTypeKindToKeyword(k)] = TK_KIND.KW
for k in pp.KEYWORDS_WITH_EXCL_SUFFIX:
    KEYWORDS[k] = TK_KIND.SPECIAL_MUT
# some operators are textual (xor, max, etc.)
for k in cwast.BINARY_EXPR_SHORTCUT:
    KEYWORDS[k] = TK_KIND.OP2


_OPERATORS_SIMPLE1 = [
    # "-",
    "^!",
    "^",
    "&!",
    "&",
    "!",
]


ANNOTATION_RE = r"@[a-zA-Z]+"
ID_RE = r"[$_a-zA-Z](?:[_a-zA-Z0-9])*(?:::[_a-zA-Z0-9]+)?(?::[_a-zA-Z0-9]+)?#?"
NUM_RE = r"[0-9](?:[_0-9a-f.xp])*(?:sint|uint|[sru][0-9]+)?"
COMMENT_RE = r"--.*[\n]"
CHAR_RE = r"['](?:[^'\\]|[\\].)*(?:[']|$)"


_operators2 = [re.escape(x) for x in cwast.BINARY_EXPR_SHORTCUT]

_operators1 = [re.escape(x) for x in _OPERATORS_SIMPLE1]

_compound_assignment = [re.escape(x) for x in cwast.ASSIGNMENT_SHORTCUT]

_token_spec = [
    (TK_KIND.ANNOTATION.name, ANNOTATION_RE),
    (TK_KIND.COLON.name, ":"),
    (TK_KIND.COMMA.name, ","),
    (TK_KIND.PAREN_OPEN.name, "[(]"),
    (TK_KIND.PAREN_CLOSED.name, "[)]"),
    (TK_KIND.CURLY_OPEN.name, "[{]"),
    (TK_KIND.CURLY_CLOSED.name, "[}]"),
    (TK_KIND.SQUARE_OPEN.name, r"\["),
    (TK_KIND.SQUARE_CLOSED.name, r"\]"),
    (TK_KIND.COMMENT.name, COMMENT_RE),  # remark
    (TK_KIND.NUM.name, NUM_RE),
    (TK_KIND.QUESTION_MARK.name, r"\?"),
    (TK_KIND.DOT.name, r"\."),
    (TK_KIND.EOL.name, "\n"),
    (TK_KIND.WS.name, "[ \t]+"),
    (TK_KIND.MSTR.name,  string_re.MULTI_START),
    (TK_KIND.RMSTR.name, string_re.MULTI_START_R),
    (TK_KIND.XMSTR.name,  string_re.MULTI_START_X),
    (TK_KIND.COMPOUND_ASSIGN.name, "|".join(_compound_assignment)),
    (TK_KIND.ID.name, ID_RE),
    (TK_KIND.OP2.name, "|".join(_operators2)),
    (TK_KIND.OP1.name, "|".join(_operators1)),
    (TK_KIND.STR.name, "(?:" + string_re.START + \
     "|" + string_re.R_START + ")" + string_re.END),
    (TK_KIND.CHAR.name, CHAR_RE),

    (TK_KIND.ASSIGN.name, "="),
]


TOKEN_RE = re.compile("|".join(f'(?P<{a}>{b})' for a, b in _token_spec))


assert TOKEN_RE.fullmatch("_::abb#")
assert not TOKEN_RE.fullmatch("$_:_:abb#")
assert TOKEN_RE.fullmatch("<")
assert TOKEN_RE.fullmatch("<<")
assert TOKEN_RE.fullmatch("<<<")
assert not TOKEN_RE.fullmatch("<<<<")
assert TOKEN_RE.fullmatch("aa")
assert TOKEN_RE.fullmatch('''"""aa"""''')
assert TOKEN_RE.fullmatch('''r"""aa"""''')
assert TOKEN_RE.fullmatch('''x"""aa"""''')
# assert TOKEN_RE.fullmatch("^!")

# print(TOKEN_RE.findall("zzzzz+aa*7u8 <<<<"))


@dataclasses.dataclass()
class TK:
    kind: TK_KIND
    srcloc: cwast.SrcLoc
    text: str
    column: int
    comments: list = dataclasses.field(default_factory=list)
    annotations: list = dataclasses.field(default_factory=list)

    def __repr__(self):
        return f"{self.srcloc}:{self.column} {self.text} [{self.kind.name}]"


class LexerRaw:
    """ """

    def __init__(self, filename, fp):
        self._fileamame: str = filename
        self._fp = fp
        self._line_no = 0
        self._col_no = 0
        self._current_line = ""

    def _fill_line(self):
        self._line_no += 1
        line = self._fp.readline()
        return line

    def get_lines_until_match(self, regex) -> list[str]:
        """use for multiline strings"""
        assert not self._current_line
        out = []
        while True:
            self._current_line = self._fill_line()
            if not self._current_line:
                cwast.CompilerError("", "unterminated string")
            m = regex.match(self._current_line)
            if m and m.group(0).endswith('"""'):
                token = m.group(0)
                self._col_no += len(token)
                self._current_line = self._current_line[len(token):]
                out.append(token)
                break
            out.append(self._current_line)
        return out

    def next_token(self) -> TK:
        if not self._current_line:
            self._col_no = 0
            self._current_line = self._fill_line()
        if not self._current_line:
            return TK(TK_KIND.SPECIAL_EOF, cwast.SRCLOC_UNKNOWN, "", 0)
        m = TOKEN_RE.match(self._current_line)
        if not m:
            cwast.CompilerError("", f"bad line: [{self._current_line}]")
        kind = TK_KIND[m.lastgroup]
        token = m.group(0)
        col = self._col_no
        if kind == TK_KIND.ID:
            kind = KEYWORDS.get(token, TK_KIND.ID)
            if kind == TK_KIND.SPECIAL_MUT:
                kind = TK_KIND.KW
                if self._current_line.startswith("!", len(token)):
                    token = token + "!"
            elif kind == TK_KIND.OP2:
                kind = TK_KIND.KW

        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        return TK(kind, cwast.SrcLoc(self._fileamame, self._line_no), token,  col)


_MSTR_TERMINATION_REGEX = {
    TK_KIND.MSTR: re.compile(string_re.MULTI_END),
    TK_KIND.RMSTR: re.compile(string_re.MULTI_END_R),
    TK_KIND.XMSTR:  re.compile(string_re.MULTI_END_X),
}


class Lexer:

    def __init__(self, lexer: LexerRaw):
        self._lexer: LexerRaw = lexer
        self._peek_cache_small: Optional[TK] = None
        self._peek_cache: Optional[TK] = None

    def _next_skip_space(self) -> TK:
        if self._peek_cache_small:
            tk = self._peek_cache_small
            self._peek_cache_small = None
        else:
            tk = self._lexer.next_token()
        while tk.kind in (TK_KIND.WS, TK_KIND.EOL):
            tk = self._lexer.next_token()
        return tk

    def next(self) -> TK:
        if self._peek_cache:
            out = self._peek_cache
            self._peek_cache = None
            return out
        tk: TK = self._next_skip_space()
        comments = []
        while tk.kind is TK_KIND.COMMENT:
            comments.append(tk)
            tk = self._next_skip_space()
        annotations = []
        while tk.kind is TK_KIND.ANNOTATION:
            annotations.append(tk)
            tk = self._next_skip_space()
        if tk.kind in (TK_KIND.MSTR, TK_KIND.RMSTR, TK_KIND.XMSTR):
            if not tk.text.endswith('"""'):
                rest = self._lexer.get_lines_until_match(
                    _MSTR_TERMINATION_REGEX[tk.kind])
                tk.text += "".join(rest)
            tk.kind = TK_KIND.STR
        out: TK = tk
        out.comments = comments
        out.annotations = annotations
        tk = self._next_skip_space()
        if tk.kind is TK_KIND.COMMENT and tk.srcloc.lineno == out.srcloc.lineno:
            out.comments.append(tk)
        else:
            self._peek_cache_small = tk
        # print(out)
        for a in annotations:
            if a.srcloc.lineno == out.srcloc.lineno:
                out.column = a.column
                break
        return out

    def peek(self) -> TK:
        if not self._peek_cache:
            self._peek_cache = self.next()
        return self._peek_cache

    def match(self, kind: TK_KIND, text=None) -> bool:
        tk = self.peek()
        if tk.kind != kind or text is not None and tk.text != text:
            return False
        self.next()
        return True

    def match_or_die(self, kind: TK_KIND, text=None):
        tk = self.peek()
        if tk.kind != kind or text is not None and tk.text != text:
            cwast.CompilerError(
                tk.srcloc, f"Expected {kind}, got {tk.kind} [{tk.text}]")
        return self.next()


PAREN_VALUE = {
    "{": 1,
    "}": -1,
    "(": 100,
    ")": -100,
    "[": 10000,
    "]": -10000,
}


_PREFIX_EXPR_PARSERS = {}
_INFIX_EXPR_PARSERS = {}


def _ParseExpr(inp: Lexer, precedence=0):
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


def _PParseId(_inp: Lexer, tk: TK, _precedence) -> Any:
    return cwast.Id(tk.text)


def _PParseNum(_inp: Lexer, tk: TK, _precedence) -> Any:
    return cwast.ValNum(tk.text)


def _PParseArrayType(inp: Lexer, tk: TK, _precedence) -> Any:
    assert tk.kind is TK_KIND.SQUARE_OPEN
    dim = _ParseExpr(inp)
    inp.match_or_die(TK_KIND.SQUARE_CLOSED)
    type = _ParseTypeExpr(inp)
    return cwast.TypeArray(dim, type)


_FUN_LIKE = {
    "len": (cwast.ExprLen, "E"),
    "pinc": (cwast.ExprPointer, "pEEe"),
    "pdec": (cwast.ExprPointer, "pEEe"),
    "offsetof": (cwast.ExprOffsetof, "TE"),
    "slice": (cwast.ValSlice, "EE"),
    "slice!": (cwast.ValSlice, "EE"),
    "front":  (cwast.ExprFront, "E"),
    "front!":  (cwast.ExprFront, "E"),
    "unwrap": (cwast.ExprUnwrap, "E"),
    "uniontag": (cwast.ExprUnionTag, "E"),
    #
    "typeof": (cwast.TypeOf, "E"),
    #
    "sizeof": (cwast.ExprSizeof, "T"),
    "typeid": (cwast.ExprTypeId, "T"),
    #
    "uniondelta": (cwast.TypeUnionDelta, "TT"),
    # mixing expression and types
    "as": (cwast.ExprAs, "ET"),
    "wrapas": (cwast.ExprWrap, "ET"),
    "is": (cwast.ExprIs, "ET"),
    "narrowto": (cwast.ExprNarrow, "ET"),
    "widdento": (cwast.ExprWiden, "ET"),
    "unsafeas": (cwast.ExprBitCast, "ET"),
    "bitsas": (cwast.ExprBitCast, "ET"),
}


def _ParseFunLike(inp: Lexer, name: str) -> Any:
    ctor, args = _FUN_LIKE[name]
    inp.match_or_die(TK_KIND.PAREN_OPEN)
    first = True
    params = []
    for a in args:
        if inp.peek().kind is TK_KIND.PAREN_CLOSED and a == "e":
            params.append(cwast.ValUndef())
            break
        if a == "p":
            params.append(cwast.POINTER_EXPR_SHORTCUT[name])
            continue
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        if a == "E" or a == "e":
            params.append(_ParseExpr(inp))

        else:
            assert a == "T", f"unknown parameter [{a}]"
            params.append(_ParseTypeExpr(inp))

    inp.match_or_die(TK_KIND.PAREN_CLOSED)
    return ctor(*params)


def _PParseKeywordConstants(inp: Lexer, tk: TK, _precedence) -> Any:
    if tk.text == "true":
        return cwast.ValTrue()
    elif tk.text == "false":
        return cwast.ValFalse()
    elif tk.text == "void":
        return cwast.ValVoid()
    elif tk.text == "auto":
        return cwast.ValAuto()
    elif tk.text in _FUN_LIKE:
        return _ParseFunLike(inp, tk.text)
    else:
        assert False, f"{tk}"


def _PParseStr(_inp: Lexer, tk: TK, _precedence) -> Any:
    return cwast.ValString(tk.text)


def _PParseChar(_inp: Lexer, tk: TK, _precedence) -> Any:
    return cwast.ValNum(tk.text)


def _PParsePrefix(inp: Lexer, tk: TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    if tk.kind is TK_KIND.OP2:
        assert tk.text == "-"
        return cwast.Expr1(cwast.UNARY_EXPR_KIND.MINUS, rhs)
    if tk.text.startswith("&"):
        return cwast.ExprAddrOf(rhs, mut=tk.text == "&!")
    kind = cwast.UNARY_EXPR_SHORTCUT[tk.text]
    return cwast.Expr1(kind, rhs)


def _PParseParenGroup(inp: Lexer, tk: TK, _precedence) -> Any:
    assert tk.kind is TK_KIND.PAREN_OPEN
    inner = _ParseExpr(inp)
    inp.match_or_die(TK_KIND.PAREN_CLOSED)
    return cwast.ExprParen(inner)


_PREFIX_EXPR_PARSERS = {
    TK_KIND.KW: (10, _PParseKeywordConstants),
    TK_KIND.OP1: (10, _PParsePrefix),
    TK_KIND.OP2: (10, _PParsePrefix),
    TK_KIND.ID: (10, _PParseId),
    TK_KIND.NUM: (10, _PParseNum),
    TK_KIND.SQUARE_OPEN: (10, _PParseArrayType),
    TK_KIND.STR: (10, _PParseStr),
    TK_KIND.CHAR: (10, _PParseChar),
    TK_KIND.PAREN_OPEN: (10, _PParseParenGroup),
}


def _PParserInfixOp(inp: Lexer, lhs, tk: TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    return cwast.Expr2(cwast.BINARY_EXPR_SHORTCUT[tk.text], lhs, rhs)


def _PParseFunctionCall(inp: Lexer, callee, tk: TK, precedence) -> Any:
    assert tk.kind is TK_KIND.PAREN_OPEN
    args = []
    first = True
    while not inp.match(TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        args.append(_ParseExpr(inp))
    return cwast.ExprCall(callee, args)


def _ParseArrayInit(inp: Lexer) -> Any:
    val = _ParseExpr(inp)
    if inp.match(TK_KIND.COLON):
        index = val
        val = _ParseExpr(inp)
    else:
        index = cwast.ValAuto()
    return cwast.IndexVal(val, index)


def _ParseRecInit(inp: Lexer) -> Any:
    val = _ParseExpr(inp)
    if inp.match(TK_KIND.COLON):
        assert isinstance(val, cwast.Id)
        field = val.name
        val = _ParseExpr(inp)

    else:
        field = ""
    return cwast.FieldVal(val, field)


def _PParseInitializer(inp: Lexer, type, tk: TK, _precedence) -> Any:
    assert tk.kind is TK_KIND.CURLY_OPEN
    if isinstance(type, cwast.Id):
        inits = []
        first = True
        while not inp.match(TK_KIND.CURLY_CLOSED):
            if not first:
                inp.match_or_die(TK_KIND.COMMA)
            first = False
            inits.append(_ParseRecInit(inp))
        return cwast.ValRec(type, inits)
    else:
        assert isinstance(type, cwast.TypeArray)
        inits = []
        first = True
        while not inp.match(TK_KIND.CURLY_CLOSED):
            if not first:
                inp.match_or_die(TK_KIND.COMMA)
            first = False
            inits.append(_ParseArrayInit(inp))
        return cwast.ValArray(type.size, type.type, inits)


def _PParseIndex(inp: Lexer, array, tk: TK, _precedence) -> Any:
    assert tk.kind is TK_KIND.SQUARE_OPEN
    index = _ParseExpr(inp)
    inp.match_or_die(TK_KIND.SQUARE_CLOSED)
    return cwast.ExprIndex(array, index)


def _PParseDeref(_inp: Lexer, pointer, _tk: TK, _precedence) -> Any:
    return cwast.ExprDeref(pointer)


def _PParseFieldAccess(inp: Lexer, rec, _tk: TK, _precedence) -> Any:
    field = inp.match_or_die(TK_KIND.ID)
    return cwast.ExprField(rec, field.text)


def _PParseTernary(inp: Lexer, cond, _tk: TK, _precedence) -> Any:
    expr_t = _ParseExpr(inp)
    inp.match_or_die(TK_KIND.COLON)
    expr_f = _ParseExpr(inp)
    return cwast.Expr3(cond, expr_t, expr_f)


_INFIX_EXPR_PARSERS = {
    "<": (10, _PParserInfixOp),
    "<=": (10, _PParserInfixOp),
    ">": (10, _PParserInfixOp),
    ">=": (10, _PParserInfixOp),
    #
    "==": (10, _PParserInfixOp),
    "!=": (10, _PParserInfixOp),
    #
    "+": (10, _PParserInfixOp),
    "-": (10, _PParserInfixOp),
    "/": (10, _PParserInfixOp),
    "*": (10, _PParserInfixOp),
    "%": (10, _PParserInfixOp),
    #
    "||": (10, _PParserInfixOp),
    "&&": (10, _PParserInfixOp),
    #
    "<<": (10, _PParserInfixOp),
    ">>": (10, _PParserInfixOp),
    #
    "&-&": (10, _PParserInfixOp),
    #
    "xor": (10, _PParserInfixOp),
    "or": (10, _PParserInfixOp),
    "and": (10, _PParserInfixOp),
    #
    "min": (10, _PParserInfixOp),
    "max": (10, _PParserInfixOp),

    #
    "(": (10, _PParseFunctionCall),
    "{": (10, _PParseInitializer),
    "[":  (10, _PParseIndex),
    "^": (10, _PParseDeref),
    ".": (10, _PParseFieldAccess),
    "?": (10, _PParseTernary),
}


def _ParseTypeExpr(inp: Lexer):
    tk = inp.next()
    if tk.kind is TK_KIND.ID:
        return cwast.Id(tk.text)
    elif tk.kind is TK_KIND.KW:
        if tk.text == "auto":
            return cwast.TypeAuto()
        elif tk.text == "funtype":
            params = _ParseFormalParams(inp)
            result = _ParseTypeExpr(inp)
            return cwast.TypeFun(params, result)
        elif tk.text in ("slice", "slice!"):
            inp.match_or_die(TK_KIND.PAREN_OPEN)
            type = _ParseTypeExpr(inp)
            inp.match_or_die(TK_KIND.PAREN_CLOSED)
            return cwast.TypeSlice(type, mut=tk.text.endswith("!"))
        elif tk.text == "typeof":
            return _ParseFunLike(inp, tk.text)
        elif tk.text == "uniondelta":
            return _ParseFunLike(inp, tk.text)
        elif tk.text == "union":
            inp.match_or_die(TK_KIND.PAREN_OPEN)
            members = []
            first = True
            while not inp.match(TK_KIND.PAREN_CLOSED):
                if not first:
                    inp.match_or_die(TK_KIND.COMMA)
                first = False
                members.append(_ParseTypeExpr(inp))
            return cwast.TypeUnion(members)
        kind = cwast.KeywordToBaseTypeKind(tk.text)
        assert kind is not cwast.BASE_TYPE_KIND.INVALID, f"{tk}"
        return cwast.TypeBase(kind)
    elif tk.text == '[':
        dim = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.SQUARE_CLOSED)
        type = _ParseTypeExpr(inp)
        return cwast.TypeArray(dim, type)
    elif tk.text == "^":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest)
    elif tk.text == "^!":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest, mut=True)
    else:
        assert False, f"unexpected token {tk}"


def _ParseFormalParams(inp: Lexer):
    out = []
    inp.match_or_die(TK_KIND.PAREN_OPEN)
    first = True
    while not inp.match(TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        out.append(cwast.FunParam(name.text, type))
    return out


def _ParseMacroArg(inp: Lexer) -> Any:
    if inp.match(TK_KIND.CURLY_OPEN):
        args = []
        first = True
        while not inp.match(TK_KIND.CURLY_CLOSED):
            if not first:
                inp.match_or_die(TK_KIND.COMMA)
            first = False
            args.append(_ParseMacroArg(inp))
        return cwast.EphemeralList(args)
    else:
        return _ParseExpr(inp)


def _ParseMacroCall(inp: Lexer) -> Any:
    args = []
    first = True
    while not inp.match(TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        args.append(_ParseMacroArg(inp))
    return args


def _ParseStatementMacro(kw: TK, inp: Lexer):
    assert kw.text.endswith("#"), f"{kw}"
    if inp.match(TK_KIND.PAREN_OPEN):
        args = _ParseMacroCall(inp)
        return cwast.MacroInvoke(kw.text, args)
    else:
        assert False


def _MaybeLabel(tk: TK, inp: Lexer):
    p = inp.peek()
    if p.kind is TK_KIND.ID and p.srcloc.lineno == tk.srcloc.lineno:
        tk = inp.next()


def _ParseOptionalLabel(inp: Lexer):
    p = inp.peek()
    if p.kind is TK_KIND.ID:
        inp.next()
        return p.text
    return ""


def _ParseStatement(inp: Lexer):
    kw = inp.next()
    if kw.kind is TK_KIND.ID:
        if kw.text.endswith("#"):
            return _ParseStatementMacro(kw, inp)
        else:
            # this happends inside a macro body
            assert kw.text.startswith("$")
            return cwast.MacroId(kw.text)
    assert kw.kind is TK_KIND.KW, f"{kw}"
    if kw.text in ("let", "let!", "mlet", "mlet!"):
        name = inp.match_or_die(TK_KIND.ID)
        if inp.match(TK_KIND.ASSIGN):
            type = cwast.TypeAuto()
            init = _ParseExpr(inp)
        else:
            type = _ParseTypeExpr(inp)
            if inp.match(TK_KIND.ASSIGN):
                init = _ParseExpr(inp)
            else:
                init = cwast.ValAuto()
        return cwast.DefVar(name.text, type, init, mut=kw.text.endswith("!"))
    elif kw.text == "while":
        cond = _ParseExpr(inp)
        stmts = _ParseStatementList(inp, kw.column)
        return cwast.MacroInvoke(cwast.Id("while"), [cond, cwast.EphemeralList(stmts, colon=True)])
    elif kw.text == "if":
        cond = _ParseExpr(inp)
        stmts_t = _ParseStatementList(inp, kw.column)
        stmts_f = []
        p = inp.peek()
        if p.column == kw.column and p.text == "else":
            inp.next()
            stmts_f = _ParseStatementList(inp, kw.column)
        return cwast.StmtIf(cond, stmts_t, stmts_f)
    elif kw.text in ("trylet", "trylet!"):
        name = inp.match_or_die(TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        inp.match_or_die(TK_KIND.ASSIGN)
        expr = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.COMMA)
        name2 = inp.match_or_die(TK_KIND.ID)
        stmts = _ParseStatementList(inp, kw.column)
        return cwast.MacroInvoke(cwast.Id(kw.text),
                                 [cwast.Id(name), type, expr,  cwast.Id(name2),
                                  cwast.EphemeralList(stmts, colon=True)])
    elif kw.text == "set":
        lhs = _ParseExpr(inp)
        kind = inp.next()
        rhs = _ParseExpr(inp)
        if kind.kind is TK_KIND.ASSIGN:
            return cwast.StmtAssignment(lhs, rhs)
        else:
            assert kind.kind is TK_KIND.COMPOUND_ASSIGN
            op = cwast.ASSIGNMENT_SHORTCUT[kind.text]
            return cwast.StmtCompoundAssignment(op, lhs, rhs)
    elif kw.text == "return":
        if inp.peek().srcloc.lineno == kw.srcloc.lineno:
            val = _ParseExpr(inp)
        else:
            val = cwast.ValVoid()
        return cwast.StmtReturn(val)
    elif kw.text == "for":
        name = inp.match_or_die(TK_KIND.ID)
        inp.match_or_die(TK_KIND.ASSIGN)
        start = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.COMMA)
        end = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.COMMA)
        step = _ParseExpr(inp)
        stmts = _ParseStatementList(inp, kw.column)
        return cwast.MacroInvoke(cwast.Id("for"),
                                 [cwast.Id(name.text), start, end, step, cwast.EphemeralList(stmts, colon=True)])
    elif kw.text == "break":
        return cwast.StmtBreak(_ParseOptionalLabel(inp))
    elif kw.text == "continue":
        return cwast.StmtContinue(_ParseOptionalLabel(inp))
    elif kw.text == "block":
        label = _ParseOptionalLabel(inp)
        stmts = _ParseStatementList(inp, kw.column)
        return cwast.StmtBlock(label, stmts)
    elif kw.text == "cond":
        return _ParseCondList(inp)
    elif kw.text == "mfor":
        var = inp.match_or_die(TK_KIND.ID)
        container = inp.match_or_die(TK_KIND.ID)
        stmts = _ParseStatementList(inp, kw.column)
        return cwast.MacroFor(var.text, container.text, stmts)
    elif kw.text == "shed":
        expr = _ParseExpr(inp)
        return cwast.StmtExpr(expr)
    elif kw.text == "trap":
        return cwast.StmtTrap()
    elif kw.text == "defer":
        body = _ParseStatementList(inp, kw.column)
        return cwast.StmtDefer(body)
    else:
        assert False, f"{kw}"

    print(f"-- {kw.column}: {tokens}")


def _ParseStatementList(inp: Lexer, outer_indent: int):
    inp.match_or_die(TK_KIND.COLON)
    indent = inp.peek().column
    if indent <= outer_indent:
        return []
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        stmt = _ParseStatement(inp)
        print("STATEMENT: ", stmt)
        out.append(stmt)
    return out


def _ParseExprList(inp: Lexer, outer_indent):
    inp.match_or_die(TK_KIND.COLON)
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


def _ParseCondList(inp: Lexer):
    inp.match_or_die(TK_KIND.COLON)
    indent = inp.peek().column
    cases = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        case = inp.match_or_die(TK_KIND.KW, "case")
        cond = _ParseExpr(inp)
        stmts = _ParseStatementList(inp, case.column)
        cases.append(cwast.Case(cond, stmts))
    return cwast.StmtCond(cases)


def _ParseFieldList(inp: Lexer):
    inp.match_or_die(TK_KIND.COLON)
    indent = inp.peek().column
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        name = inp.match_or_die(TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        out.append(cwast.RecField(name.text, type))
    return out


def _ParseEnumList(inp: Lexer, outer_indent):
    inp.match_or_die(TK_KIND.COLON)
    indent = inp.peek().column
    if indent <= outer_indent:
        return []
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        name = inp.match_or_die(TK_KIND.ID)
        val = _ParseExpr(inp)
        out.append(cwast.EnumVal(name.text, val))
    return out


def _ParseMacroParams(inp: Lexer):
    out = []
    inp.match_or_die(TK_KIND.PAREN_OPEN)
    first = True
    while not inp.match(TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(TK_KIND.ID)
        kind = inp.match_or_die(TK_KIND.ID)
        out.append(cwast.MacroParam(
            name.text, cwast.MACRO_PARAM_KIND[kind.text]))
    return out


def _ParseMacroParams(inp: Lexer):
    out = []
    inp.match_or_die(TK_KIND.PAREN_OPEN)
    first = True
    while not inp.match(TK_KIND.PAREN_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(TK_KIND.ID)
        kind = inp.match_or_die(TK_KIND.ID)
        out.append(cwast.MacroParam(
            name.text, cwast.MACRO_PARAM_KIND[kind.text]))
    return out


def _ParseMacroGenIds(inp: Lexer):
    out = []
    inp.match_or_die(TK_KIND.SQUARE_OPEN)
    first = True
    while not inp.match(TK_KIND.SQUARE_CLOSED):
        if not first:
            inp.match_or_die(TK_KIND.COMMA)
        first = False
        name = inp.match_or_die(TK_KIND.ID)
        out.append(cwast.Id(name.text))
    return out


def _ParseTopLevel(inp: Lexer):
    kw = inp.next()
    alias = ""
    if kw.text == "import":
        name = inp.match_or_die(TK_KIND.ID)
        path = ""
        if inp.match(TK_KIND.ASSIGN):
            path = inp.next().text
            if path.startswith('"'):
                assert path.endswith('"')
                path = path[1:-1]
        params = []
        if inp.match(TK_KIND.PAREN_OPEN):
            first = True
            while not  inp.match(TK_KIND.PAREN_OPEN):
                if not first:
                    inp.match(TK_KIND.COMMA)
                first = False
                params.append(_ParseExpr(inp))
        return cwast.Import(name.text, path, params)
    elif kw.text == "fun":
        name = inp.match_or_die(TK_KIND.ID)
        params = _ParseFormalParams(inp)
        result = _ParseTypeExpr(inp)
        body = _ParseStatementList(inp, kw.column)
        return cwast.DefFun(name.text, params, result, body)
    elif kw.text == "rec":
        name = inp.match_or_die(TK_KIND.ID)
        fields = _ParseFieldList(inp)
        return cwast.DefRec(name.text, fields)
    elif kw.text in ("global", "global!"):
        name = inp.match_or_die(TK_KIND.ID)
        if inp.match(TK_KIND.ASSIGN):
            type = cwast.TypeAuto()
            init = _ParseExpr(inp)
        else:
            type = _ParseTypeExpr(inp)
            if inp.match(TK_KIND.ASSIGN):
                init = _ParseExpr(inp)
            else:
                init = cwast.ValAuto()
        return cwast.DefGlobal(name.text, type, init)
    elif kw.text == "macro":
        if inp.peek().kind is TK_KIND.KW:
            name = inp.next()
            assert name.text in pp.BUILTIN_MACROS, f"{name}"
        else:
            name = inp.match_or_die(TK_KIND.ID)
            assert name.text.endswith("#")
        kind = inp.match_or_die(TK_KIND.ID)
        params = _ParseMacroParams(inp)
        gen_ids = _ParseMacroGenIds(inp)
        if kind.text in ("EXPR", "EXPR_LIST"):
            body = _ParseExprList(inp, kw.column)
        else:
            body = _ParseStatementList(inp, kw.column)
        return cwast.DefMacro(name.text, cwast.MACRO_PARAM_KIND[kind.text],
                              params, gen_ids, body)
    elif kw.text == "type":
        name = inp.match_or_die(TK_KIND.ID)
        inp.match_or_die(TK_KIND.ASSIGN)
        type = _ParseTypeExpr(inp)
        return cwast.DefType(name.text, type)
    elif kw.text == "enum":
        name = inp.match_or_die(TK_KIND.ID)
        base_type = inp.match_or_die(TK_KIND.KW)
        entries = _ParseEnumList(inp, kw.column)
        return cwast.DefEnum(name.text, cwast.KeywordToBaseTypeKind(base_type.text),
                             entries)
    elif kw.text == "static_assert":
        cond = _ParseExpr(inp)
        return cwast.StmtStaticAssert(cond, "")
    else:
        assert False, f"unexpected topelevel [{kw}]"


def _ParseModule(inp: Lexer):
    # comments, annotations = _ParseOptionalCommentsAttributes(inp)
    # print(comments, annotations)
    kw = inp.match_or_die(TK_KIND.KW, "module")
    name = inp.match_or_die(TK_KIND.ID)
    params = []
    if inp.match(TK_KIND.PAREN_OPEN):
        first = True
        while not inp.match(TK_KIND.PAREN_CLOSED):
            if not first:
                inp.match_or_die(TK_KIND.COMMA)
            first = False
            name = inp.match_or_die(TK_KIND.ID)
            kind = inp.match_or_die(TK_KIND.ID)
            params.append(cwast.ModParam(name.text,
                                         cwast.MOD_PARAM_KIND[kind.text]))
    kw = inp.match_or_die(TK_KIND.COLON)
    out = cwast.DefMod(name.text, params, [])

    while True:
        if inp.peek().kind is TK_KIND.SPECIAL_EOF:
            break
        toplevel = _ParseTopLevel(inp)
        print("TOPLEVEL: ", toplevel)
        out.body_mod.append(toplevel)
    return out


def ParseFile(inp: Lexer) -> Any:
    mod = _ParseModule(inp)


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    ParseFile(Lexer(LexerRaw("stdin", sys.stdin)))
