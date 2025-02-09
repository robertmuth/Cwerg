#!/bin/env python3

import collections
import enum
import sys
import io
import re
import dataclasses

from typing import Any, Optional

from FE import cwast
from Util import cgen
from FE import parse_sexpr
from FE import string_re


_DIGITS = "0123456789"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_ID_CHARS: set[int] = set(ord(c) for c in "_$" + _DIGITS + _LOWER + _UPPER)
_NUM_CHARS: set[int] = set(ord(c) for c in ".01234567890")
_NO_CHARS: set[int] = set()

NODE_NULL = 0

NODE = list[int]
TRIE = list[list[int]]


TK_KIND_OFFSET = 1000
TK_KIND_OFFSET_FOR_LOOK_AHEAD = 2000


@enum.unique
class TK_KIND(enum.Enum):
    INVALID = 0
    # for the items below we may need to check one char extra:
    COMPARISON_OP = enum.auto()
    SHIFT_OP = enum.auto()
    ADD_OP = enum.auto()
    MUL_OP = enum.auto()
    OR_SC_OP = enum.auto()
    AND_SC_OP = enum.auto()
    DEREF_OR_POINTER_OP = enum.auto()  # ^, ^!
    ADDR_OF_OP = enum.auto()  # @, @!
    PREFIX_OP = enum.auto()
    BASE_TYPE = enum.auto()
    KW = enum.auto()
    KW_SIMPLE_VAL = enum.auto()
    ANNOTATION = enum.auto()
    ASSIGN = enum.auto()  # =, ==
    SQUARE_OPEN = enum.auto()  # [, [!]
    CURLY_OPEN = enum.auto()   # {}
    GENERIC_ANNOTATION = enum.auto()  # {{

    # The items below are never prefixes of others
    TERNARY_OP = enum.auto()
    DOT_OP = enum.auto()
    COMPOUND_ASSIGN = enum.auto()
    COLON = enum.auto()
    COMMA = enum.auto()
    PAREN_OPEN = enum.auto()
    PAREN_CLOSED = enum.auto()
    CURLY_CLOSED = enum.auto()
    SQUARE_CLOSED = enum.auto()
    # These just match the  enum.auto()prefix  of the lexeme
    COMMENT = enum.auto()
    CHAR = enum.auto()
    STR = enum.auto()
    # these items are synthesized during lexing
    NUM = enum.auto()
    ID = enum.auto()
    SPECIAL_EOF = enum.auto()


def IsEmptyNode(n: NODE):
    for x in n:
        if x != -1:
            return False
    return True


def OptimizeTrie(trie: TRIE) -> TRIE:
    nodes = list(sorted((b, a, len(b) - b.count(-1))
                 for a, b in enumerate((trie))))

    trans = [-1] * len(trie)
    last = nodes[0]
    for i in range(1, len(nodes)):
        curr = nodes[i]
        if last[0] == curr[0]:
            # print("@@", curr[1], "->", last[1], last[2])
            trans[curr[1]] = last[1]
        else:
            last = curr
    # print(trans)
    new_indices = []
    n = 0
    for t in trans:
        if t == -1:
            new_indices.append(n)
            n += 1
        else:
            # this node will be dropped
            new_indices.append(-1)

    def rewrite(t: NODE):
        for n, c in enumerate(t):
            if c == -1 or c > len(trie):
                continue
            if trans[c] != -1:
                c = trans[c]
            t[n] = new_indices[c]
    out = []
    for n, t in enumerate(trie):
        if new_indices[n] != -1:
            rewrite(t)
            out.append(t)
    return out


def FindInTrie(trie: TRIE, s: str) -> tuple[int, int]:
    node = trie[0]
    for n, cc in enumerate(s):
        x = node[ord(cc)]
        if x == NODE_NULL:
            return 0, 0
        if x >= len(trie):
            if x >= TK_KIND_OFFSET_FOR_LOOK_AHEAD:
                return n, TK_KIND(x - TK_KIND_OFFSET_FOR_LOOK_AHEAD)
            else:
                return n + 1, TK_KIND(x - TK_KIND_OFFSET)
        node = trie[x]
    return 0, 0


def VerifyTrie(trie: TRIE, KWs):
    for kw, tag in sorted(KWs):
        # print (kw, tag)
        res_len, res_tag = FindInTrie(trie, kw + "\x01")
        assert res_tag == tag


def DumpTrieStats(trie: TRIE):
    print("TRIE ANALYSIS")
    print(f"Nodes: {len(trie)}")
    histo = collections.defaultdict(int)
    for t in trie:
        non_null = len(t) - t.count(NODE_NULL)
        histo[non_null] += 1
    for k, v in sorted(histo.items()):
        print(k, v)


def GetAllKWAndOps():
    KWs = []
    KWs += [(kw, TK_KIND.KW) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, TK_KIND.KW_SIMPLE_VAL) for kw in cwast.KeyWordsSimpleVal()]
    KWs += [(kw, TK_KIND.BASE_TYPE) for kw in cwast.KeywordsBaseTypes()]

    KWs += [(kw, TK_KIND.COMPOUND_ASSIGN) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, TK_KIND.COMPARISON_OP)
            for kw in ["<", ">", ">=", "<=", "==", "!="]]
    KWs += [(kw, TK_KIND.SHIFT_OP)
            for kw in ["<<", ">>", "<<<", ">>>"]]
    KWs += [(kw, TK_KIND.ADD_OP)
            for kw in ["+", "-", "~", "|"]]
    KWs += [(kw, TK_KIND.MUL_OP)
            for kw in ["/", "*", "%", "&"]]
    KWs += [("&&", TK_KIND.AND_SC_OP)]
    KWs += [("||", TK_KIND.OR_SC_OP)]
    KWs += [(kw, TK_KIND.PREFIX_OP)
            for kw in cwast.UnaryOpsForConcreteSyntax()]
    KWs += [(kw, TK_KIND.ANNOTATION)
            for kw in ["pub", "ref", "poly", "wrapped"]]
    KWs += [(kw, TK_KIND.KW) for kw in ["else", "set", "for", "while",
                                        "tryset", "trylet", "trylet!"]]
    KWs += [("=", TK_KIND.ASSIGN)]
    KWs += [(",", TK_KIND.COMMA)]
    KWs += [(":", TK_KIND.COLON)]
    #
    KWs += [("(", TK_KIND.PAREN_OPEN)]
    KWs += [(")", TK_KIND.PAREN_CLOSED)]
    KWs += [("{", TK_KIND.CURLY_OPEN)]
    KWs += [("}", TK_KIND.CURLY_CLOSED)]
    KWs += [("[", TK_KIND.SQUARE_OPEN)]
    KWs += [("[!", TK_KIND.SQUARE_OPEN)]
    KWs += [("]", TK_KIND.SQUARE_CLOSED)]
    #
    KWs += [(";", TK_KIND.COMMENT)]
    KWs += [("'", TK_KIND.CHAR)]
    KWs += [("{{", TK_KIND.GENERIC_ANNOTATION)]
    KWs += [('"', TK_KIND.STR)]
    KWs += [('x"', TK_KIND.STR)]
    KWs += [('r"', TK_KIND.STR)]
    #
    KWs += [(cwast.Expr3.ALIAS, TK_KIND.TERNARY_OP)]
    KWs += [(cwast.ExprField.ALIAS, TK_KIND.DOT_OP)]
    KWs += [(cwast.ExprDeref.ALIAS, TK_KIND.DEREF_OR_POINTER_OP)]
    KWs += [(cwast.ExprDeref.ALIAS + cwast.MUTABILITY_SUFFIX,
             TK_KIND.DEREF_OR_POINTER_OP)]
    KWs += [(cwast.ExprAddrOf.ALIAS, TK_KIND.ADDR_OF_OP)]
    KWs += [(cwast.ExprAddrOf.ALIAS + cwast.MUTABILITY_SUFFIX,
             TK_KIND.ADDR_OF_OP)]

    return KWs


# these can not be prefixes of other lexemes
SIMPLE_TAGS = set([
    TK_KIND.COMPOUND_ASSIGN, TK_KIND.COLON, TK_KIND.COMMA, TK_KIND.PAREN_OPEN,
    TK_KIND.PAREN_CLOSED, TK_KIND.CURLY_CLOSED, TK_KIND.SQUARE_CLOSED,
    TK_KIND.COMMENT, TK_KIND.CHAR, TK_KIND.STR,
    TK_KIND.TERNARY_OP, TK_KIND.DOT_OP,

])

MAY_BE_PREFIX_TAGS = set([
    TK_KIND.COMPARISON_OP,
    TK_KIND.SHIFT_OP,
    TK_KIND.ADD_OP,
    TK_KIND.MUL_OP,
    TK_KIND.OR_SC_OP,
    TK_KIND.AND_SC_OP,
    TK_KIND.PREFIX_OP,
    TK_KIND.PREFIX_OP, TK_KIND.ASSIGN, TK_KIND.SQUARE_OPEN,
    TK_KIND.CURLY_OPEN,  TK_KIND.GENERIC_ANNOTATION, TK_KIND.DEREF_OR_POINTER_OP,
    TK_KIND.ADDR_OF_OP,
])


def MakeInitialTrie(KWs):
    trie = []

    def add_node():
        node = [NODE_NULL] * 128
        trie.append(node)
        return len(trie) - 1

    # root node
    add_node()

    def add_kw_simple(kw, tag):
        last = ord(kw[-1])
        node = trie[0]
        for cc in kw[:-1]:
            c = ord(cc)
            if node[c] == NODE_NULL:
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]
        assert node[last] == NODE_NULL, f"[{kw}] {
            node[last]} {node is trie[0]}"
        node[last] = tag.value + TK_KIND_OFFSET

    def add_kw(kw, tag, non_succ):
        # keyword is only valid if not followed by char in non_succ
        # E.g.
        # if is a keyword but ifoo is not
        # simarly
        # >> is an operator(-keyword) for most subsequent chars
        # except >>> and >>=
        # Not that >>> and >>=  will have been processeed earlier
        node = trie[0]
        for n, cc in enumerate(kw):
            c = ord(cc)
            if node[c] == NODE_NULL:
                if n == len(kw) - 1 and non_succ == set():
                    node[c] = tag.value + TK_KIND_OFFSET
                    return
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]

        # handle terminators
        for i in range(len(node)):
            if i not in non_succ:
                if node[i] == NODE_NULL:
                    node[i] = tag.value + TK_KIND_OFFSET_FOR_LOOK_AHEAD

    # KWs = list(sorted(KWs))[0:1]

    # the sortorder ensures that a prefixes are procressed later
    for kw, tag in reversed(sorted(KWs)):
        # print (kw, tag)
        if tag in (TK_KIND.KW, TK_KIND.KW_SIMPLE_VAL, TK_KIND.ANNOTATION, TK_KIND.BASE_TYPE):
            if kw.endswith("!"):
                add_kw_simple(kw, tag)
            else:
                # if the KW is followed by alphanumeric chars, it is not a KW
                add_kw(kw, tag, _ID_CHARS)
        elif tag in SIMPLE_TAGS:
            add_kw_simple(kw, tag)
        elif tag in MAY_BE_PREFIX_TAGS:
            excl = _NUM_CHARS if kw in ("+", "-") else _NO_CHARS
            add_kw(kw, tag, excl)
        else:
            assert False
    #
    VerifyTrie(trie, KWs)
    return trie


def MakeTrieNoisy():
    KWs = GetAllKWAndOps()
    trie = MakeInitialTrie(KWs)
    #
    print("Stats")
    DumpTrieStats(trie)

    for i in range(1000):
        print(f"Optimization round {i}")
        old_len = len(trie)
        trie = OptimizeTrie(trie)
        if len(trie) == old_len:
            break
        print("Stats")
        DumpTrieStats(trie)
        VerifyTrie(trie, KWs)
    return trie


def MakeTrie(optimize):
    KWs = GetAllKWAndOps()
    trie = MakeInitialTrie(KWs)
    if optimize:
        for i in range(1000):
            old_len = len(trie)
            trie = OptimizeTrie(trie)
            if len(trie) == old_len:
                break
    return trie


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


GENERIC_ANNOTATION_RE = re.compile(r"^\{\{[_a-zA-Z]+\}\}")

ID_RE = re.compile(
    "^" + r"[_a-zA-Z](?:[_a-zA-Z0-9])*(?:::[_a-zA-Z0-9]+)?(?::[_a-zA-Z0-9]+)?[#]?")

MACRO_ID_RE = re.compile(
    "^" + r"[$][_a-zA-Z][_a-zA-Z0-9]*")

NUM_RE = re.compile("^" + parse_sexpr.RE_STR_NUM)
CHAR_RE = re.compile(r"^['](?:[^'\\]|[\\].)*(?:[']|$)")
#
STR_RE = re.compile("^" + string_re.START + string_re.END)
X_STR_RE = re.compile("^" + string_re.START + string_re.END)
R_STR_RE = re.compile("^" + string_re.R_START + string_re.END)
ALL_STR_RE = {
    '"': STR_RE,
    'x': X_STR_RE,
    'r': R_STR_RE,

}
#
MSTR_START_RE = re.compile("^" + string_re.MULTI_START)
X_MSTR_START_RE = re.compile("^" + string_re.MULTI_START_X)
R_MSTR_START_RE = re.compile("^" + string_re.MULTI_START_R)
MSTR_END_RE = re.compile("^" + string_re.MULTI_END)
X_MSTR_END_RE = re.compile("^" + string_re.MULTI_END_X)
R_MSTR_END_RE = re.compile("^" + string_re.MULTI_END_R)
ALL_MSTR_RE = {
    '"': (MSTR_START_RE, MSTR_END_RE),
    'x': (X_MSTR_START_RE, X_MSTR_END_RE),
    'r': (R_MSTR_START_RE, R_MSTR_END_RE),
}


class LexerRaw:
    """ No Peek ability"""

    def __init__(self: Any, filename: str, fp: io.TextIOWrapper):
        self._fileamame: str = sys.intern(filename)
        self._fp = fp
        self._line_no = 0
        self._col_no = 0
        self._current_line = ""
        self._trie: TRIE = MakeTrie(False)

    def _GetSrcLoc(self) -> cwast.SrcLoc:
        return cwast.SrcLoc(self._fileamame, self._line_no)

    def _fill_line(self):
        self._line_no += 1
        line = self._fp.readline()
        return line

    def _SkipWS(self):
        while True:
            for n, c in enumerate(self._current_line):
                if c not in (' ', '\t', '\n'):
                    self._col_no += n
                    self._current_line = self._current_line[n:]
                    return
            else:
                self._col_no = 0
                self._current_line = self._fill_line()
                if not self._current_line:
                    # eof
                    return

    def _HandleTripleQuotedStrings(self, start_re, end_re):
        col = self._col_no
        sl = self._GetSrcLoc()
        m = start_re.search(self._current_line)
        data = m.group(0)
        if not data.endswith('"""'):
            while True:
                self._current_line = self._fill_line()
                self._col_no = 0
                if not self._current_line:
                    cwast.CompilerError("", "unterminated string")
                    m = end_re.search(self._current_line)
                m = end_re.search(self._current_line)
                if m:
                    data += m.group(0)
                    break
                data += self._current_line
        size = m.end()
        self._col_no += size
        self._current_line = self._current_line[size:]
        return TK(TK_KIND.STR, sl, sys.intern(data),  col)

    def next_token(self) -> TK:
        self._SkipWS()
        if not self._current_line:
            return TK(TK_KIND.SPECIAL_EOF, cwast.INVALID_SRCLOC, "", 0)
        sl = self._GetSrcLoc()
        size, kind = FindInTrie(self._trie, self._current_line)
        if size == 0:
            first = self._current_line[0]
            # we must be dealing with an ID or NUM
            if first <= "9" and first != '$':
                kind = TK_KIND.NUM
                # what we are really trying todo is testing membership in "+-.0123456789"
                m = NUM_RE.search(self._current_line)
            elif first == "$":
                kind = TK_KIND.ID
                m = MACRO_ID_RE.search(self._current_line)
            else:
                kind = TK_KIND.ID
                m = ID_RE.search(self._current_line)
            size = m.end()
        if kind == TK_KIND.COMMENT:
            size = len(self._current_line)
        elif kind == TK_KIND.CHAR:
            m = CHAR_RE.search(self._current_line)
            size = m.end()
        elif kind == TK_KIND.STR:
            first = self._current_line[0]
            if first == '"':
                triple = self._current_line.startswith('"""')
            else:
                triple = self._current_line[1:].startswith('"""')
            if triple:
                return self._HandleTripleQuotedStrings(*ALL_MSTR_RE[first])
            else:
                m = ALL_STR_RE[first].search(self._current_line)
                size = m.end()
        elif kind == TK_KIND.GENERIC_ANNOTATION:
            m = GENERIC_ANNOTATION_RE.search(self._current_line)
            size = m.end()
        token = self._current_line[:size]
        col = self._col_no
        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        if kind == TK_KIND.GENERIC_ANNOTATION:
            kind = TK_KIND.ANNOTATION
            # remove curlies
            token = token[2:-2]
        return TK(kind, sl, sys.intern(token),  col)


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
        out = tk
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

_NAMED_OP_RE = re.compile(r"[_a-zA-Z]+")

def GenerateCodeCC(fout, max_items_per_row=16):
    trie = MakeTrie(True)

    # we reserver a few bytes for terminal markers
    assert len(trie) < 240
    num_nodes = len(trie)

    def render_val(x):
        if x < num_nodes:
            return f"{x}"
        else:
            if x >= TK_KIND_OFFSET_FOR_LOOK_AHEAD:
                kind = TK_KIND(x - TK_KIND_OFFSET_FOR_LOOK_AHEAD)
                return f"VALX({kind.name})"
            else:
                kind = TK_KIND(x - TK_KIND_OFFSET)
                return f"VAL({kind.name})"

    def render_strip(lst: list[int]):
        sep = ""
        while lst:
            first = lst[0]
            count = 1
            for x in lst[1:]:
                if x == first:
                    count += 1
                else:
                    break
            if count < 3:
                count = 1
            lst = lst[count:]
            val = render_val(first)
            if count == 1:
                print(f"{sep}{val}", end="", file=fout)
            else:
                print(f"{sep}REP{count}({val})", end="", file=fout)
            sep = ", "

    offset = len(trie)
    print(f"#define VAL(x) {
          offset} + uint16_t(TK_KIND::x)\n", file=fout)
    offset += TK_KIND.SPECIAL_EOF.value + 1
    print(f"#define VALX(x) {offset} + uint16_t(TK_KIND::x)\n", file=fout)

    print(f"uint16_t TrieNodeCount = {len(trie)};\n", file=fout)

    print(f"uint16_t KeywordAndOpRecognizer[{len(trie)}][128] = {{", file=fout)
    for n in trie:
        sep = "    {"
        for i in range(0, len(n), max_items_per_row):
            print(sep, end="", file=fout)
            sep = ",\n     "
            stripe = n[i:i+max_items_per_row]
            render_strip(stripe)
        print("},\n", file=fout)

    print("};", file=fout)

    prefix = TK_KIND.__name__
    cgen.RenderEnumToStringMap(
        cgen.NameValues(TK_KIND), prefix, fout)
    cgen.RenderEnumToStringFun(prefix, fout)

    print("BINARY_EXPR_KIND BINARY_EXPR_KIND_PerfectHash[64] = {", file=fout)
    m = MakePerfectHashForBinOp()
    for i in range(64):
        x = m.get(i, cwast.BASE_TYPE_KIND.INVALID)
        print(f"  BINARY_EXPR_KIND::{x.name},", file=fout)

    print("};", file=fout)

    print(
        "\nconst std::map<std::string_view, NT> KeywordToNodeTypeMap = {", file=fout)
    for node in cwast.ALL_NODES:
        if node.ALIAS and _NAMED_OP_RE.fullmatch(node.ALIAS):
            print(f'{{"{node.ALIAS}", NT::{node.__name__}}},', file=fout)
    print("};", file=fout)


def GenerateCodeH(fout):
    cgen.RenderEnumClass(cgen.NameValues(TK_KIND), "TK_KIND", fout)


def MakePerfectHashForBinOp():
    KWs = []
    KWs += [(kw, TK_KIND.COMPARISON_OP)
            for kw in ["<", ">", ">=", "<=", "==", "!="]]
    KWs += [(kw, TK_KIND.SHIFT_OP)
            for kw in ["<<", ">>", "<<<", ">>>"]]
    KWs += [(kw, TK_KIND.ADD_OP)
            for kw in ["+", "-", "~", "|"]]
    KWs += [(kw, TK_KIND.MUL_OP)
            for kw in ["/", "*", "%", "&"]]
    KWs += [("&&", TK_KIND.AND_SC_OP)]
    KWs += [("||", TK_KIND.OR_SC_OP)]
    m = {}
    for a, b, in KWs:
        o = ord(a[0])
        l = len(a)
        c = b.value
        x = (o << 1) + l + (c << 3)
        m[x & 0x3f] = cwast.BINARY_EXPR_SHORTCUT[a]
    assert len(m) == len(KWs), f"{len(m)} != {len(KWs)}"
    return m


if __name__ == "__main__":
    if len(sys.argv) == 1:
        MakeTrieNoisy()
    elif sys.argv[1] == "gen_cc":
        cgen.ReplaceContent(GenerateCodeCC, sys.stdin, sys.stdout)
    elif sys.argv[1] == "gen_h":
        cgen.ReplaceContent(GenerateCodeH, sys.stdin, sys.stdout)
    elif sys.argv[1] == "ph":
        m = MakePerfectHashForBinOp()
        for a, b in m.items():
            print(f"{a:x}", b)
    else:
        assert False
