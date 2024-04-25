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
    PAREN_OPEN = enum.auto()
    PAREN_CLOSED = enum.auto()
    SQUARE_OPEN = enum.auto()
    SQUARE_CLOSED = enum.auto()
    CURLY_OPEN = enum.auto()
    CURLY_CLOSED = enum.auto()
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
    (TK_KIND.PAREN_OPEN.name, "[(]"),
    (TK_KIND.PAREN_CLOSED.name, "[)]"),
    (TK_KIND.CURLY_OPEN.name, "[{]"),
    (TK_KIND.CURLY_CLOSED.name, "[}]"),
    (TK_KIND.SQUARE_OPEN.name, r"\["),
    (TK_KIND.SQUARE_CLOSED.name, r"\]"),
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


_PREFIX_EXPR_PARSERS = {}
_INFIX_EXPR_PARSERS = {}


def _ParseExpr(inp: Lexer, precedence=0):
    """Pratt Parser"""

    tk = inp.next()
    prec, parser = _PREFIX_EXPR_PARSERS.get(tk.kind, (0, None))
    if not parser:
        raise RuntimeError(f"could not parse '{tk.kind}'")
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


_PREFIX_EXPR_PARSERS = {
    TK_KIND.ID: (10, _PParseId),
    TK_KIND.NUM: (10, _PParseNum),
    TK_KIND.SQUARE_OPEN: (10, _PParseArrayType),
}


def _PParserInfixOp(inp: Lexer, lhs, tk: TK, precedence) -> Any:
    rhs = _ParseExpr(inp, precedence)
    return cwast.Expr2(cwast.BINARY_EXPR_SHORTCUT[tk.text], lhs, rhs)


def _PParseFunctionCall(inp: Lexer, callee, tk: TK, precedence) -> Any:
    assert tk.kind is TK_KIND.PAREN_OPEN
    args = []
    if not inp.match(TK_KIND.PAREN_CLOSED):
        args.append(_ParseExpr(inp))
        while inp.match(TK_KIND.COMMA):
            args.append(_ParseExpr(inp))
        inp.match_or_die(TK_KIND.PAREN_CLOSED)
    return cwast.ExprCall(callee, args)


def _ParseArrayInit(inp: Lexer) -> Any:
    if inp.match(TK_KIND.SQUARE_OPEN):
        assert False
    else:
        index = cwast.ValAuto()
    return cwast.IndexVal(_ParseExpr(inp), index)


def _PParseInitializer(inp: Lexer, type, tk: TK, precedence) -> Any:
    assert tk.kind is TK_KIND.CURLY_OPEN
    if isinstance(type, cwast.Id):
        assert False, "NYI - record initializer"
    else:
        assert isinstance(type, cwast.TypeArray)
        inits = []
        if not inp.match(TK_KIND.CURLY_CLOSED):
            inits.append(_ParseArrayInit(inp))
            while inp.match(TK_KIND.COMMA):
                inits.append(_ParseArrayInit(inp))
            inp.match_or_die(TK_KIND.CURLY_CLOSED)

        return cwast.ValArray(type.size, type.type, inits)


def _PParseIndex(inp: Lexer, array, tk: TK, precedence) -> Any:
    assert tk.kind is TK_KIND.SQUARE_OPEN
    index = _ParseExpr(inp)
    inp.match_or_die(TK_KIND.SQUARE_CLOSED)
    return cwast.ExprIndex(array, index)


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
    #
    "&-&": (10, _PParserInfixOp),
    #
    "(": (10, _PParseFunctionCall),
    "{": (10, _PParseInitializer),
    "[":  (10, _PParseIndex),

}


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
            _ExpectToken(inp, TK_KIND.SQUARE_CLOSED)
            type = _ParseTypeExpr(inp)
            return cwast.TypeSlice(type, False)
        elif inp.peek().text == "!":
            _ExpectToken(inp, TK_KIND.OP, "!")
            _ExpectToken(inp, TK_KIND.SQUARE_CLOSED)
            type = _ParseTypeExpr(inp)
            return cwast.TypeSlice(type, True)
        else:
            dim = _ParseTypeExpr(inp)
            _ExpectToken(inp, TK_KIND.SQUARE_CLOSED)
            type = _ParseTypeExpr(inp)
            return cwast.TypeArray(dim, type)
    elif tk.text == "sig":
        assert False
    elif tk.text == "^":
        rest = _ParseTypeExpr(inp)
        return cwast.TypePtr(rest)
    else:
        assert False, f"unexpected token {tk}"


def _ParseFormalParams(inp: Lexer):
    out = []
    inp.match_or_die(TK_KIND.PAREN_OPEN)
    if not inp.match(TK_KIND.PAREN_CLOSED):
        name = inp.match_or_die(TK_KIND.ID)
        type = _ParseTypeExpr(inp)
        out.append(cwast.FunParam(name.text, type))
        while inp.match(TK_KIND.COMMA):
            name = inp.match_or_die(TK_KIND.ID)
            type = _ParseTypeExpr(inp)
            out.append(cwast.FunParam(name.text, type))
        inp.match_or_die(TK_KIND.PAREN_CLOSED)
    return out


def _ParseMacroCall(inp: Lexer) -> Any:
    args = []
    if not inp.match(TK_KIND.PAREN_CLOSED):
        args.append(_ParseExpr(inp))
        while inp.match(TK_KIND.COMMA):
            args.append(_ParseExpr(inp))
        inp.match_or_die(TK_KIND.PAREN_CLOSED)
    return args


def _ParseStatementMacro(kw: TK, inp: Lexer):
    assert kw.text.endswith("#")
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
        return _ParseStatementMacro(kw, inp)
    assert kw.kind is TK_KIND.KW, f"{kw}"
    if kw.text in ("let", "let!"):
        name = inp.match(TK_KIND.ID)
        if inp.match(TK_KIND.OP, "="):
            type = cwast.TypeAuto()
            init = _ParseExpr(inp)
        else:
            type = _ParseTypeExpr(inp)
            if inp.match(TK_KIND.OP, "="):
                init = _ParseExpr(inp)
            else:
                init = cwast.ValAuto()
        return cwast.DefVar(name.text, type, init, mut=kw.text.endswith("!"))
    elif kw.text == "while":
        cond = _ParseExpr(inp)
        stmts = _ParseStatementList(inp)
        return cwast.MacroInvoke(cwast.Id("while"), [cond, cwast.EphemeralList(stmts, colon=True)])
    elif kw.text == "if":
        cond = _ParseExpr(inp)
        stmts_t = _ParseStatementList(inp)
        stmts_f = []
        p = inp.peek()
        if p.column == kw.column and p.text == "else":
            p.next()
            stmts_f = _ParseStatementList(inp)
        return cwast.StmtIf(cond, stmts_t, stmts_f)
    elif kw.text in ("trylet", "trylet!"):
        assert False
        tokens.append(_ExpectToken(inp, TK_KIND.ID))
        _ParseTypeExpr(inp)
        _ExpectToken(inp, TK_KIND.OP, text="=")
        _ParseExpr(inp)
        _ExpectToken(inp, TK_KIND.COMMA)
        _ExpectToken(inp, TK_KIND.ID)
        _ParseStatementList(inp)
    elif kw.text == "set":
        lhs = _ParseExpr(inp)
        kind = inp.match_or_die(TK_KIND.OP)
        assert kind.text in _ASSIGNMENT_OPS
        rhs = _ParseExpr(inp)
        if kind.text == "=":
            return cwast.StmtAssignment(lhs, rhs)
        else:
            return cwast.StmtCompoundAssignment(lhs, rhs)
    elif kw.text == "return":
        val = _ParseExpr(inp)
        return cwast.StmtReturn(val)
    elif kw.text == "for":
        name = inp.match_or_die(TK_KIND.ID)
        inp.match_or_die(TK_KIND.OP, "=")
        start = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.COMMA)
        end = _ParseExpr(inp)
        inp.match_or_die(TK_KIND.COMMA)
        step = _ParseExpr(inp)
        stmts = _ParseStatementList(inp)
        return cwast.MacroInvoke(cwast.Id("for"),
                                 [cwast.Id(name.text), start, end, step, cwast.EphemeralList(stmts, colon=True)])
    elif kw.text == "break":
        return cwast.StmtBreak(_ParseOptionalLabel(inp))
    elif kw.text == "continue":
        return cwast.StmtContinue(_ParseOptionalLabel(inp))
    elif kw.text == "block":
        label = _ParseOptionalLabel(inp)
        stmts = _ParseStatementList(inp)
        return cwast.StmtBlock(label, stmts)
    elif kw.text == "cond":
        assert False
        _ParseCondList(inp)
    else:
        assert False, f"{kw}"

    print(f"-- {kw.column}: {tokens}")


def _ParseStatementList(inp: Lexer):
    inp.match_or_die(TK_KIND.COLON)
    indent = inp.peek().column
    out = []
    while True:
        tk = inp.peek()
        if tk.column < indent:
            break
        stmt = _ParseStatement(inp)
        print("STATEMENT: ", stmt)
    return out


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
    name = inp.match_or_die(TK_KIND.ID)
    params = _ParseFormalParams(inp)
    result = _ParseTypeExpr(inp)
    body = _ParseStatementList(inp)
    return cwast.DefFun(name.text, params, result, body)


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
        name = inp.match_or_die(TK_KIND.ID)
        if inp.match(TK_KIND.OP, "="):
            type = cwast.TypeAuto()
            init = _ParseExpr(inp)
        else:
            type = _ParseTypeExpr(inp)
            if inp.match(TK_KIND.OP, "="):
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
