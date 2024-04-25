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

logger = logging.getLogger(__name__)


@enum.unique
class TK_KIND(enum.Enum):
    INVALID = 0
    KW = enum.auto()
    ANNOTATION = enum.auto()
    COMMENT = enum.auto()
    OP = enum.auto()
    COMMA = enum.auto()
    COLON = enum.auto()
    EOL = enum.auto()
    WS = enum.auto()
    ID = enum.auto()
    NUM = enum.auto()
    CHAR = enum.auto()
    STR = enum.auto()
    BR = enum.auto()  # brace/bracket
    SPECIAL_ASSIGN = enum.auto()
    SPECIAL_MUT = enum.auto()
    SPECIAL_EOF = enum.auto()


_KEYWORDS_SIMPLE = [
    "auto",    # type/val
    "bool",
    "slice",
    "typeof",
    "union",
    "array",
    "uniondelta",
    "true",
    "false",
    "void",
    "noreturn",
    "front",
    "uniontag",
    "is",
    "expr",
    "continue",
    "break",
    "trap",
    "return",
    "shed",
    "defer",
    "case",
    "cond",
    "block",
    "if",
    "while",
    "sig",
    "for",
    "if",
    "else",
    "set",
    "tryset",
    #
    "pinc",
    "pdec",
    #
    "as",
    "aswrapped",
    "asbits",
    "asnarrowed",
    "unwrap",
    #
    "offsetof",
    "sizeof",
    "typeid",
    "len",
    #
    "sint",
    "uint",
    "s8",
    "s16",
    "s32",
    "s64",
    "u8",
    "u16",
    "u32",
    "u64"
    "r32",
    "r64",
    #
    "macro",
    "stringfy",
    #
    "module",
    "enum",
    "import",
    "fun",
    "type",
    "static_assert",
]

_KEYWORDS_OPERATOR_EQ_SUFFIX = [
    "min",
    "max",
    "and",
    "or",
    "xor",
]


_KEYWORDS_WITH_EXCL_SUFFIX = [
    "trylet",
    "mlet",
    "mfor",
    "let",
    "global",
]

KEYWORDS = {}
for k in _KEYWORDS_SIMPLE:
    KEYWORDS[k] = TK_KIND.KW
for k in _KEYWORDS_WITH_EXCL_SUFFIX:
    KEYWORDS[k] = TK_KIND.SPECIAL_MUT
for k in _KEYWORDS_OPERATOR_EQ_SUFFIX:
    KEYWORDS[k] = TK_KIND.OP

# Note, order is important: e.g. >> must come before >
_OPERATORS_SIMPLE = [
    "~",
    "&&",
    "||",
    "^",
    ".",
    "&-&",
    "!",
]


_OPERATORS_WITH_EXCL_SUFFIX = [
    "&",
]

_OPERATORS_WITH_EQ_SUFFIX = [
    "!",
    "=",
    ">>>",
    "<<<",
    ">>",
    "<<",
    "<",
    ">",
    "+",
    "-",
    "/",
    "*",
    "%"
]


_ASSIGNMENT_OPS = set([
    "=",
    ">>>=",
    "<<<=",
    ">>=",
    "<<=",
    "+=",
    "-=",
    "/=",
    "*=",
    "%="
])

OPERATORS = {}
for o in _OPERATORS_SIMPLE:
    OPERATORS[o] = TK_KIND.OP
for o in _OPERATORS_WITH_EQ_SUFFIX:
    OPERATORS[o] = TK_KIND.SPECIAL_ASSIGN
for o in _KEYWORDS_OPERATOR_EQ_SUFFIX:
    OPERATORS[o] = TK_KIND.SPECIAL_ASSIGN
for o in _OPERATORS_WITH_EXCL_SUFFIX:
    OPERATORS[o] = TK_KIND.SPECIAL_MUT

ANNOTATION_RE = r"@[a-zA-Z]+"
ID_RE = r"[$_a-zA-Z](?:[_a-zA-Z0-9]|::)*#?"
NUM_RE = r"[0-9](?:[_0-9a-f.xp])*(?:sint|uint|[sru][0-9]+)?"
COMMENT_RE = r"--.*[\n]"
CHAR_RE = r"['](?:[^'\\]|[\\].)*(?:[']|$)"

#
_STR_START_RE = r'x?"(?:[^"\\]|[\\].)*'
_R_STR_START_RE = r'r"(?:[^"])*'
_STR_END_RE = '(?:"|$)'   # Note, this also covers the unterminated case

_operators = ([re.escape(x) for x in _OPERATORS_SIMPLE] +
              [re.escape(x) for x in _OPERATORS_WITH_EQ_SUFFIX] +
              [re.escape(x) for x in _OPERATORS_WITH_EXCL_SUFFIX])

_token_spec = [
    (TK_KIND.ANNOTATION.name, ANNOTATION_RE),
    (TK_KIND.COLON.name, ":"),           # colon
    (TK_KIND.COMMA.name, ","),           # comma
    (TK_KIND.BR.name, "[{}\[\]()]"),  # bracket
    (TK_KIND.COMMENT.name, COMMENT_RE),  # remark
    (TK_KIND.ID.name, ID_RE),
    (TK_KIND.NUM.name, NUM_RE),
    (TK_KIND.EOL.name, "\n"),
    (TK_KIND.WS.name, "[ \t]+"),
    (TK_KIND.STR.name, "(?:" + _R_STR_START_RE + \
     "|" + _STR_START_RE + ")" + _STR_END_RE),
    (TK_KIND.OP.name, "|".join(_operators)),
    (TK_KIND.CHAR.name, CHAR_RE),
]


TOKEN_RE = re.compile("|".join(f'(?P<{a}>{b})' for a, b in _token_spec))


assert TOKEN_RE.fullmatch("_::abb#")
assert not TOKEN_RE.fullmatch("$_:_:abb#")
assert TOKEN_RE.fullmatch("<")
assert TOKEN_RE.fullmatch("<<")
assert TOKEN_RE.fullmatch("<<<")
assert not TOKEN_RE.fullmatch("<<<<")
assert TOKEN_RE.fullmatch("aa")

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
        while True:
            self._line_no += 1
            line = self._fp.readline()
            # an empty line means EOF
            # skip lines with just newline
            if not line or line != "\n":
                return line

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
        elif kind == TK_KIND.OP:
            k = OPERATORS[token]
            if k == TK_KIND.SPECIAL_ASSIGN:
                if self._current_line.startswith("=", len(token)):
                    token = token + "="
            elif k == TK_KIND.SPECIAL_MUT:
                if self._current_line.startswith("!", len(token)):
                    token = token + "!"
        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        return TK(kind, cwast.SrcLoc(self._fileamame, self._line_no), token,  col)


class Lexer:

    def __init__(self, lexer: LexerRaw):
        self._lexer = lexer
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
        out: TK = tk
        out.comments = comments
        out.annotations = annotations
        tk = self._next_skip_space()
        if tk.kind is TK_KIND.COMMENT and tk.srcloc.lineno == out.srcloc.lineno:
            out.comments.append(tk)
        else:
            self._peek_cache_small = tk
        print(out)
        for a in annotations:
            if a.srcloc.lineno == out.srcloc.lineno:
                out.column = a.column
                break
        return out

    def peek(self) -> TK:
        if not self._peek_cache:
            self._peek_cache = self.next()
        return self._peek_cache


def _ExpectToken(inp: Lexer, kind: TK_KIND, text=None) -> TK:
    tk = inp.next()
    if tk.kind != kind or text is not None and tk.text != text:
        cwast.CompilerError(
            tk.srcloc, f"Expected {kind}, got {tk.kind} [{tk.text}]")
    return tk


_FUN_LIKE = {
    "pinc": "EE",
    "pdec": "EE",
    "offsetof": "TF",
    "slice": "EE",
    "as": "ET",
    "wrap": "ET",
    "narrowto": "ET",
    "widdento": "ET",
    "cast": "ET",
    "bitcast": "ET",
}

_OPERATOR_LIKE = {
    "unwrap": "E",
    "uniontypetag": "E",
    "unionuntagged": "E",
    "sizeof": "T",
}

PAREN_VALUE = {
    "{": 1,
    "}": -1,
    "(": 100,
    ")": -100,
    "[": 10000,
    "]": -10000,
}


def _ParseExpr(inp: Lexer):
    nesting = 0
    tk = inp.next()
    while True:
        p = inp.peek()
        pv = PAREN_VALUE.get(p.text, 0)
        if nesting == 0:
            if p.kind in (TK_KIND.COMMA, TK_KIND.COLON, TK_KIND.SPECIAL_EOF):
                break
            if p.srcloc.lineno != tk.srcloc.lineno:
                break
            if p.text in _ASSIGNMENT_OPS:
                break
            if pv < 0:
                break
        nesting += pv
        tk = inp.next()

    return

    if tk.kind in (TK_KIND.ID, TK_KIND.NUM):
        pass
    elif tk.kind is TK_KIND.KW:
        args = _FUN_LIKE.get(tk.text)
        if not args:
            assert False
        first = True
        for a in args:
            if first:
                _ExpectToken(inp, TK_KIND.BR, "(")
                first = False
            else:
                _ExpectToken(inp, TK_KIND.COMMA)
            _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.BR, ")"),
    elif tk.kind is TK_KIND.BR and tk.text == '(':
        _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.BR, ")"),
    else:
        assert False, f"{tk}"

    tk = inp.peek()


def _ParseTypeExpr(inp: Lexer):
    tk = inp.next()
    if tk.kind is TK_KIND.ID:
        return cwast.Id(tk.text)
    elif tk.kind is TK_KIND.KW:

        if tk.text == "auto":
            return cwast.TypeAuto()
        kind = cwast.KeywordToBaseTypeKind(tk.text)
        assert kind is not cwast.BASE_TYPE_KIND.INVALID
        return cwast.TypeBase(kind)
    elif tk.text == '[':
        if inp.peek().text == "]":
            _ExpectToken(inp, TK_KIND.BR, "]")
            type = _ParseTypeExpr(inp)
            return cwast.TypeSlice(type, False)
        elif inp.peek().text == "!":
            _ExpectToken(inp, TK_KIND.OP, "!")
            _ExpectToken(inp, TK_KIND.BR, "]")
            type = _ParseTypeExpr(inp)
            return cwast.TypeSlice(type, True)
        else:
            dim = _ParseTypeExpr(inp)
            _ExpectToken(inp, TK_KIND.BR, "]")
            type = _ParseTypeExpr(inp)
            return cwast.TypeArray(dim, type)
    elif tk.text == "sig":
        assert False
    elif tk.text == "^":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest)
    else:
        assert False


def _ParseFormalParams(inp: Lexer):
    _ExpectToken(inp, TK_KIND.BR, "(")
    tk = inp.next()
    while tk.text != ")":
        _ParseTypeExpr(inp)
        tk = inp.next()
        if tk.kind is TK_KIND.COMMA:
            tk = inp.next()


def _ParseArguments(inp: Lexer):

    while True:
        tk = inp.next()
        if tk.text == "(":
            if inp.peek().text == ")":
                tk = inp.next()
        if tk.text == ")":
            break
        assert tk.text in ("(", ","), f"P{tk}"
        _ParseExpr(inp)


def _ParseStatementMacro(kw: TK, inp: Lexer):
    assert kw.text.endswith("#")
    if inp.peek().text == "(":
        _ParseArguments(inp)
    else:
        assert False


def _MaybeLabel(tk: TK, inp: Lexer):
    p = inp.peek()
    if p.kind is TK_KIND.ID and p.srcloc.lineno == tk.srcloc.lineno:
        tk = inp.next()


def _ParseStatement(kw: TK, inp: Lexer):
    if kw.kind is TK_KIND.ID:
        return _ParseStatementMacro(kw, inp)
    assert kw.kind is TK_KIND.KW, f"{kw}"
    tokens = [kw]
    print(f"-- {kw.column}: {tokens}")
    if kw.text in ("let", "let!"):
        tokens.append(_ExpectToken(inp, TK_KIND.ID))
        _ParseTypeExpr(inp)
        tk = inp.peek()
        if tk.text in ("=", "+=", "-=", "*="):
            tokens.append(inp.next())
            _ParseExpr(inp)
    elif kw.text == "while":
        tokens.append(_ParseExpr(inp))
        _ParseStatementList(inp)
    elif kw.text == "if":
        tokens.append(_ParseExpr(inp))
        _ParseStatementList(inp)
    elif kw.text == "else":
        _ParseStatementList(inp)
    elif kw.text in ("trylet", "trylet!"):
        tokens.append(_ExpectToken(inp, TK_KIND.ID))
        _ParseTypeExpr(inp)
        _ExpectToken(inp, TK_KIND.OP, text="=")
        _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.COMMA)
        _ExpectToken(inp, TK_KIND.ID)
        _ParseStatementList(inp)
    elif kw.text == "set":
        _ParseExpr(inp)
        assert inp.peek().text in _ASSIGNMENT_OPS
        _ExpectToken(inp, TK_KIND.OP)
        _ParseExpr(inp)
    elif kw.text == "return":
        _ParseExpr(inp)
    elif kw.text == "for":
        _ExpectToken(inp, TK_KIND.ID)
        _ExpectToken(inp, TK_KIND.OP, text="=")
        _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.COMMA)
        _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.COMMA)
        _ParseExpr(inp)
        _ParseStatementList(inp)
    elif kw.text in ("break", "contimue"):
        _MaybeLabel(kw, inp)
    elif kw.text == "block":
        _MaybeLabel(kw, inp)
        _ParseStatementList(inp)
    elif kw.text == "cond":
        _ParseCondList(inp)
    else:
        assert False, f"{kw}"

    print(f"-- {kw.column}: {tokens}")


def _ParseStatementList(inp: Lexer):
    _ExpectToken(inp, TK_KIND.COLON)
    indent = inp.peek().column
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        _ParseStatement(inp.next(), inp)


def _ParseCondList(inp: Lexer):
    _ExpectToken(inp, TK_KIND.COLON)
    indent = inp.peek().column
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        _ExpectToken(inp, TK_KIND.KW, text="case")
        _ParseExpr(inp)
        _ParseStatementList(inp)


def _ParseFieldList(inp: Lexer):
    _ExpectToken(inp, TK_KIND.COLON)
    indent = inp.peek().column
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        _ExpectToken(inp, TK_KIND.ID)
        _ParseTypeExpr(inp)


def _ParseFun(kw, inp: Lexer):
    tokens = [kw,  _ExpectToken(inp, TK_KIND.ID)]
    _ParseFormalParams(inp)
    _ParseTypeExpr(inp)
    _ParseStatementList(inp)


def _ParseTopLevel(inp: Lexer):
    kw = inp.next()
    if kw.text == "import":
        name = _ExpectToken(inp, TK_KIND.ID)
        out = cwast.Import(name.text, "", [])
        return out
    elif kw.text == "fun":
        return _ParseFun(kw, inp)
    elif kw.text == "rec":
        name = _ExpectToken(inp, TK_KIND.ID)
        fields = _ParseFieldList(inp)
        out = cwast.DefRec(name.text, fields)
        return out
    elif kw.text in ("global", "global!"):
        name = _ExpectToken(inp, TK_KIND.ID)
        if inp.peek().text == "=":
            _ExpectToken(inp, TK_KIND.OP, "=")
            type = _ParseTypeExpr(inp)
        else:
            type = cwast.TypeAuto()
        if inp.peek().text == "=":
            _ExpectToken(inp, TK_KIND.OP, "=")
            init = _ParseExpr(inp)
        else:
            init = cwast.ValAuto()
        return cwast.DefGlobal(name.text, type, init)
    else:
        assert False, f"topelevel {kw}"


def _ParseModule(inp: Lexer):
    # comments, annotations = _ParseOptionalCommentsAttributes(inp)
    # print(comments, annotations)
    kw = _ExpectToken(inp, TK_KIND.KW, "module")
    name = _ExpectToken(inp, TK_KIND.ID)
    _ExpectToken(inp, TK_KIND.COLON)
    out = cwast.DefMod(name.text, [], [])

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
