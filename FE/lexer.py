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
    COMMENT = enum.auto()
    PREFIX_OP = enum.auto()
    OTHER_OP = enum.auto()
    COMMA = enum.auto()
    COLON = enum.auto()
    EOL = enum.auto()   # not used by parser
    WS = enum.auto()    # not used by parser
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
    SQUARE_OPEN_EXCL = enum.auto()
    SQUARE_CLOSED = enum.auto()
    CURLY_OPEN = enum.auto()
    CURLY_CLOSED = enum.auto()
    ANNOTATION = enum.auto()
    GENERIC_ANNOTATION = enum.auto()  # pub, ref, poly

    SPECIAL_EOF = enum.auto()


# reversing makes sure that  "trylet!" is checked before "trylet"
_KEYWORDS_ALL = reversed(sorted(
    (cwast.KeyWordsForConcreteSyntax() +
     ["else", "set", "for",
      "while", "tryset", "trylet", "trylet!"])))
_UNARY_OPS = reversed(sorted(cwast.UnaryOpsForConcreteSyntax()))
_BINARY_OPS = reversed(sorted(cwast.BinaryOpsForConcreteSyntax()))


_GENERIC_ANNOTATION_RE = r"\{\{[_a-zA-Z]+\}\}"
ID_RE = r"[$_a-zA-Z](?:[_a-zA-Z0-9])*(?:::[_a-zA-Z0-9]+)?(?::[_a-zA-Z0-9]+)?[#]?"
COMMENT_RE = r"--.*[\n]"
CHAR_RE = r"['](?:[^'\\]|[\\].)*(?:[']|$)"


def _EscapeAndConcat(lst) -> str:
    return "(?:" + "|".join(re.escape(x) for x in lst) + r")"


_FOLLOWED_BY_WS = r"(?=\s|$)"
_FOLLOWED_BY_NON_ID_CHAR = r"(?=[^_a-zA-Z0-9]|$)"

_token_spec = [
    (TK_KIND.GENERIC_ANNOTATION.name, _GENERIC_ANNOTATION_RE),
    (TK_KIND.ANNOTATION.name, _EscapeAndConcat(
        ["pub", "ref", "poly", "wrapped"]) + _FOLLOWED_BY_NON_ID_CHAR),
    (TK_KIND.COMPOUND_ASSIGN.name,
     _EscapeAndConcat(cwast.ASSIGNMENT_SHORTCUT.keys()) + _FOLLOWED_BY_WS),
    (TK_KIND.KW.name, _EscapeAndConcat(_KEYWORDS_ALL) + _FOLLOWED_BY_NON_ID_CHAR),
    (TK_KIND.COLON.name, ":"),
    (TK_KIND.COMMA.name, ","),
    (TK_KIND.PAREN_OPEN.name, "[(]"),
    (TK_KIND.PAREN_CLOSED.name, "[)]"),
    (TK_KIND.CURLY_OPEN.name, "[{]"),
    (TK_KIND.CURLY_CLOSED.name, "[}]"),
    (TK_KIND.SQUARE_OPEN_EXCL.name, r"\[!"),
    (TK_KIND.SQUARE_OPEN.name, r"\["),
    (TK_KIND.SQUARE_CLOSED.name, r"\]"),
    (TK_KIND.COMMENT.name, COMMENT_RE),  # remark
    (TK_KIND.NUM.name, parse_sexpr.RE_STR_NUM),
    (TK_KIND.EOL.name, "\n"),
    (TK_KIND.WS.name, "[ \t]+"),
    (TK_KIND.MSTR.name, string_re.MULTI_START),
    (TK_KIND.RMSTR.name, string_re.MULTI_START_R),
    (TK_KIND.XMSTR.name, string_re.MULTI_START_X),

    (TK_KIND.ID.name, ID_RE),

    (TK_KIND.OTHER_OP.name, _EscapeAndConcat(_BINARY_OPS)),
    # OP1 must follow OP2 and NUM because of matching overlap involving "!"
    # dealing with unary +/- is done explicitly
    (TK_KIND.PREFIX_OP.name, _EscapeAndConcat(_UNARY_OPS)),
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


@ dataclasses.dataclass()
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
    """ No Peek ability"""

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

    def _get_lines_until_match(self, regex) -> list[str]:
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
        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        if kind in (TK_KIND.WS, TK_KIND.EOL):
            return self.next_token()

        sl = self._GetSrcLoc()

        if kind == TK_KIND.GENERIC_ANNOTATION:
            kind = TK_KIND.ANNOTATION
            # remove curlies
            token = token[2:-2]
        elif kind in (TK_KIND.MSTR, TK_KIND.RMSTR, TK_KIND.XMSTR):
            if not token.endswith('"""'):
                rest = self._get_lines_until_match(
                    _MSTR_TERMINATION_REGEX[kind])
                token += "".join(rest)
            kind = TK_KIND.STR
        return TK(kind, sl, sys.intern(token),  col)


_MSTR_TERMINATION_REGEX = {
    TK_KIND.MSTR: re.compile(string_re.MULTI_END),
    TK_KIND.RMSTR: re.compile(string_re.MULTI_END_R),
    TK_KIND.XMSTR:  re.compile(string_re.MULTI_END_X),
}


class Lexer:

    def __init__(self, lexer: LexerRaw):
        self._lexer: LexerRaw = lexer
        self._peek_cache: Optional[TK] = None

    def next(self) -> TK:
        if self._peek_cache:
            out = self._peek_cache
            self._peek_cache = None
            return out
        tk: TK = self._lexer.next_token()
        comments = []
        while tk.kind is TK_KIND.COMMENT:
            comments.append(tk)
            tk = self._lexer.next_token()
        annotations = []
        while tk.kind is TK_KIND.ANNOTATION:
            annotations.append(tk)
            tk = self._lexer.next_token()
        out: TK = tk
        out.comments = comments
        out.annotations = annotations
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
