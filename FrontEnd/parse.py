#!/usr/bin/python3

import re

import logging

from typing import Any, Tuple, Union

from FrontEnd import cwast

logger = logging.getLogger(__name__)

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
    "for",
    "if",
    "else",
    "set"
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
    KEYWORDS[k] = "KW"
for k in _KEYWORDS_WITH_EXCL_SUFFIX:
    KEYWORDS[k] = "!"
for k in _KEYWORDS_OPERATOR_EQ_SUFFIX:
    KEYWORDS[k] = "OP"

# Note, order is important: e.g. >> must come before >
_OPERATORS_SIMPLE = [
    "~",
    "&&",
    "||",
    "^",
    ".",
    "&-&",
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

OPERATORS = {}
for o in _OPERATORS_SIMPLE:
    OPERATORS[o] = "OP"
for o in _OPERATORS_WITH_EQ_SUFFIX:
    OPERATORS[o] = "="
for o in _KEYWORDS_OPERATOR_EQ_SUFFIX:
    OPERATORS[o] = "="
for o in _OPERATORS_WITH_EXCL_SUFFIX:
    OPERATORS[o] = "!"

ANNOTATION_RE = r"@[a-zA-Z]+"
ID_RE = r"[$_a-zA-Z](?:[_a-zA-Z0-9]|::)*#?"
NUM_RE = r"[0-9](?:[_0-9a-f.xp])*(?:sint|uint|[sru][0-9]+)?"
COMMENT_RE = "--.*"
CHAR_RE = r"['](?:[^'\\]|[\\].)*(?:[']|$)"

#
_STR_START_RE = r'x?"(?:[^"\\]|[\\].)*'
_R_STR_START_RE = r'r"(?:[^"])*'
_STR_END_RE = '(?:"|$)'   # Note, this also covers the unterminated case

_operators = ([re.escape(x) for x in _OPERATORS_SIMPLE] +
              [re.escape(x) for x in _OPERATORS_WITH_EQ_SUFFIX] +
              [re.escape(x) for x in _OPERATORS_WITH_EXCL_SUFFIX])

_token_spec = [
    ("AN", ANNOTATION_RE),
    ("CL", ":"),           # colon
    ("CM", ","),           # comma
    ("BR", "[{}\[\]()]"),  # bracket
    ("REM", COMMENT_RE),  # remark
    ("ID", ID_RE),
    ("NUM", NUM_RE),
    ("EOL", "\n"),
    ("SPC", "[ \t]+"),
    ("STR", "(?:" + _R_STR_START_RE + "|" + _STR_START_RE + ")" + _STR_END_RE),
    ("OP", "|".join(_operators)),
    ("CHR", CHAR_RE),
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


class Input:
    """ """

    def __init__(self, fp):
        self._fp = fp
        self._line_no = 0
        self._col_no = 0
        self._current_line = ""

    def next_token(self):
        if not self._current_line:
            self._col_no = 0
            self._line_no += 1
            self._current_line = self._fp.readline()
        if not self._current_line:
            return ("EOF", 0, "")
        m = TOKEN_RE.match(self._current_line)
        if not m:
            cwast.CompilerError("", f"bad line: [{self._current_line}]")
        kind = m.lastgroup
        token = m.group(0)
        col = self._col_no
        if kind == "ID":
            kind = KEYWORDS.get(token, "ID")
        if kind == "!":
            kind = "KW"
            if self._current_line.startswith("!", len(token)):
                token = token + "!"
        elif kind == "OP":
            k = OPERATORS[token]
            if k == "=":
                if self._current_line.startswith("=", len(token)):
                    token = token + "="
            elif k == "!":
                if self._current_line.startswith("!", len(token)):
                    token = token + "!"
        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        return kind, col, token


def ParseModule(inp: Input) -> Any:
    while True:
        k, no, s = inp.next_token()
        if k == "EOL":
            print("---")
        elif k == "SPC":
            continue
        else:
            print(k, no, s)
        if k == "EOF":
            break


############################################################
#
############################################################
if __name__ == "__main__":
    import sys

    ParseModule(Input(sys.stdin))
