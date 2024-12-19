import re
import io
import logging
import enum
import dataclasses
import sys

from typing import Any, Optional

from FE import string_re
from FE import cwast
from FE import pp
from FE import parse_sexpr

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
    # SPECIAL_xxx will be rewritten to one of the ones above
    SPECIAL_MUT = enum.auto()   # keyword with ! suffix
    SPECIAL_ANNOTATION = enum.auto()  # pub, ref, poly
    SPECIAL_EOF = enum.auto()


_KEYWORDS_SIMPLE = [
    "auto",    # type/val
    "span",
    "vec",
    "true",
    "false",
    "front",
    "funtype",
    "else",
    #
    "pinc",
    "pdec",
    #
    "span_inc",
    #
    "abs",
    "sqrt",
    "min",
    "max",
] + [nt.ALIAS for nt in [cwast.TypeOf, cwast.TypeUnion, cwast.TypeUnionDelta,
                         cwast.ExprUnionTag, cwast.ExprIs,
                         #
                         cwast.ValUndef,
                         #
                         cwast.ExprAs, cwast.ExprWrap, cwast.ExprUnwrap, cwast.ExprWiden, cwast.ExprSrcLoc,
                         cwast.ExprBitCast, cwast.ExprUnsafeCast, cwast.ExprNarrow, cwast.ExprTypeId,
                         cwast.ExprOffsetof, cwast.ExprSizeof, cwast.ExprLen, cwast.ExprStringify]]


KEYWORDS: dict[str, TK_KIND] = ({
    "pub": TK_KIND.SPECIAL_ANNOTATION,
    "ref": TK_KIND.SPECIAL_ANNOTATION,
    "poly": TK_KIND.SPECIAL_ANNOTATION,

    "wrapped": TK_KIND.SPECIAL_ANNOTATION
}
    | {k: TK_KIND.KW for k in _KEYWORDS_SIMPLE}
    | {k: TK_KIND.KW for k in pp.KEYWORDS}
    | {k: TK_KIND.SPECIAL_MUT for k in pp.KEYWORDS_WITH_EXCL_SUFFIX}
    # some operators are textual (xor, max, etc.)
    | {k: TK_KIND.OP2 for k in cwast.BINARY_EXPR_SHORTCUT}
    | {k: TK_KIND.SPECIAL_MUT for k in pp.KEYWORDS_WITH_EXCL_SUFFIX}
    | {cwast.BaseTypeKindToKeyword(k): TK_KIND.KW for k in cwast.BASE_TYPE_KIND
       if k is not cwast.BASE_TYPE_KIND.INVALID}
)


_OPERATORS_SIMPLE1 = [
    "-",  # note, also in binops
    "^!",
    "^",
    "&!",
    "&",
    "!",
]


ANNOTATION_RE = r"@[a-zA-Z]+"
ID_RE = r"[$_a-zA-Z](?:[_a-zA-Z0-9])*(?:::[_a-zA-Z0-9]+)?(?::[_a-zA-Z0-9]+)?[#]?"
COMMENT_RE = r"--.*[\n]"
CHAR_RE = r"['](?:[^'\\]|[\\].)*(?:[']|$)"


_operators2 = [re.escape(x) for x in cwast.BINARY_EXPR_SHORTCUT
               if x not in ("max", "min")]


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
    (TK_KIND.NUM.name, parse_sexpr.RE_STR_NUM),
    (TK_KIND.QUESTION_MARK.name, r"\?"),
    (TK_KIND.DOT.name, r"\."),
    (TK_KIND.EOL.name, "\n"),
    (TK_KIND.WS.name, "[ \t]+"),
    (TK_KIND.MSTR.name,  string_re.MULTI_START),
    (TK_KIND.RMSTR.name, string_re.MULTI_START_R),
    (TK_KIND.XMSTR.name,  string_re.MULTI_START_X),
    (TK_KIND.COMPOUND_ASSIGN.name,
     "(?:" + "|".join(_compound_assignment) + r")(?=\s|$)"),
    (TK_KIND.ID.name, ID_RE),
    # require binary ops to be followed by whitespace, this helps with
    # disambiguating unary +/-
    (TK_KIND.OP2.name, "(?:" + "|".join(_operators2) + r")(?=\s|$)"),
    # OP1 must follow OP2 and NUM because of matching overlap
    (TK_KIND.OP1.name, "|".join(_operators1)),
    (TK_KIND.STR.name, "(?:" + string_re.START + \
     "|" + string_re.R_START + ")" + string_re.END),
    (TK_KIND.CHAR.name, CHAR_RE),
    (TK_KIND.ASSIGN.name, "="),
]


TOKEN_RE = re.compile("|".join(f'(?P<{a}>{b})' for a, b in _token_spec))


def assert_match(a, b=None):
    # note that re.fullmatch tries harder to match the full string than match
    if b is None:
        b = a
    assert TOKEN_RE.match(a).group() == b


assert_match("0.0_r64")
assert_match("5_u16")
assert_match("5_u16")
assert_match('-0x1.5555555555549p-3')
assert_match("_::abb#")
assert not TOKEN_RE.fullmatch("$_:_:abb#")
assert_match("< ", "<")
assert_match("<<")
assert_match("<<<")
assert not TOKEN_RE.fullmatch("<<<<")
assert_match("aa")
assert_match('''"""aa"""''')
assert_match('''r"""aa"""''')
assert_match('''x"""aa"""''')
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

    def has_annotation(self, a: str) -> bool:
        for x in self.annotations:
            if x.text == a:
                return True
        return False

    def __repr__(self):
        return f"{self.srcloc}:{self.column} {self.text} [{self.kind.name}]"


class LexerRaw:
    """ """

    def __init__(self: Any, filename: str, fp: io.TextIOWrapper):
        self._fileamame: str = sys.intern(filename)
        self._fp = fp
        self._line_no = 0
        self._col_no = 0
        self._current_line = ""

    def _GetSrcLoc(self) -> cwast.SrcLoc:
        return cwast.SrcLoc(self._fileamame, self._line_no)

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
            return TK(TK_KIND.SPECIAL_EOF, cwast.INVALID_SRCLOC, "", 0)
        m = TOKEN_RE.match(self._current_line)
        if not m:
            cwast.CompilerError(
                self._GetSrcLoc(), f"bad line or character: [{self._current_line}]")
        kind = TK_KIND[m.lastgroup]
        token = m.group(0)
        col = self._col_no
        if kind == TK_KIND.ID:
            kind = KEYWORDS.get(token, TK_KIND.ID)
            if kind == TK_KIND.SPECIAL_MUT:
                kind = TK_KIND.KW
                if self._current_line.startswith(cwast.MUTABILITY_SUFFIX, len(token)):
                    token = token + cwast.MUTABILITY_SUFFIX
            elif kind == TK_KIND.OP2:
                # rewrite operartor with names like xor, etc.
                kind = TK_KIND.KW
            elif kind == TK_KIND.SPECIAL_ANNOTATION:
                kind = TK_KIND.ANNOTATION
                token = "@" + token

        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        return TK(kind, self._GetSrcLoc(), sys.intern(token),  col)


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
        # if we have annotations the node starts at the first one
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
                tk.srcloc, f"Expected {kind} [{text}], got {tk.kind} [{tk.text}]")
        return self.next()
