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

NODE_NULL = -1

NODE = list[int]
TRIE = list[list[int]]


@enum.unique
class TK_KIND(enum.Enum):
    KW = 1000
    COMPOUND_ASSIGN = 1001
    OTHER_OP = 1002
    PREFIX_OP = 1003
    ANNOTATION = 1004
    ASSIGN = 1005
    COLON = 1006
    COMMA = 1007
    PAREN_OPEN = 1008
    PAREN_CLOSED = 1009
    CURLY_OPEN = 1010
    CURLY_CLOSED = 1011
    SQUARE_OPEN = 1012
    SQUARE_OPEN_EXCL = 1013
    SQUARE_CLOSED = 1014
    # These just match the prefix  of the lexeme
    COMMENT = 1015
    GENERIC_ANNOTATION = 1016
    CHAR = 1017
    STR = 1018
    NUM = 1020
    ID = 1021
    SPECIAL_EOF = 1022


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
        if x == -1:
            return 0, 0
        if x >= len(trie):
            if x & 1:
                return n, TK_KIND(x >> 1)
            else:
                return n + 1, TK_KIND(x >> 1)
        node = trie[x]
    return 0, 0


def VerifyTrie(trie: TRIE, KWs):
    for kw, tag in sorted(KWs):
        # print (kw, tag)
        res_len, res_tag = FindInTrie(trie, kw + "\x01")
        assert res_tag == tag


def DumpStats(trie: TRIE):
    print("TRIE ANALYSIS")
    print(f"Nodes: {len(trie)}")
    histo = collections.defaultdict(int)
    for t in trie:
        non_null = len(t) - t.count(-1)
        histo[non_null] += 1
    for k, v in sorted(histo.items()):
        print(k, v)


def GetAllKWAndOps():
    KWs = []
    KWs += [(kw, TK_KIND.KW) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, TK_KIND.COMPOUND_ASSIGN) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, TK_KIND.OTHER_OP)
            for kw in cwast.BinaryOpsForConcreteSyntax()]
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
    KWs += [("[!", TK_KIND.SQUARE_OPEN_EXCL)]
    KWs += [("]", TK_KIND.SQUARE_CLOSED)]
    #
    KWs += [(";", TK_KIND.COMMENT)]
    KWs += [("'", TK_KIND.CHAR)]
    KWs += [("{{", TK_KIND.GENERIC_ANNOTATION)]
    KWs += [('"', TK_KIND.STR)]
    KWs += [('x"', TK_KIND.STR)]
    KWs += [('r"', TK_KIND.STR)]
    return KWs


SIMPLE_TAGS = set([
    TK_KIND.COMPOUND_ASSIGN, TK_KIND.COLON, TK_KIND.COMMA, TK_KIND.PAREN_OPEN,
    TK_KIND.PAREN_CLOSED, TK_KIND.CURLY_CLOSED, TK_KIND.SQUARE_CLOSED,
    TK_KIND.SQUARE_OPEN_EXCL, TK_KIND.COMMENT, TK_KIND.CHAR, TK_KIND.STR,
])

MAY_BE_PREFIX_TAGS = set([
    TK_KIND.OTHER_OP, TK_KIND.PREFIX_OP, TK_KIND.ASSIGN, TK_KIND.SQUARE_OPEN,
    TK_KIND.CURLY_OPEN,  TK_KIND.GENERIC_ANNOTATION,

])


def MakeInitialTrie(KWs):
    trie = []

    def add_node():
        node = [-1] * 129
        trie.append(node)
        return len(trie) - 1

    # root node
    add_node()

    def add_kw_simple(kw, tag):
        last = ord(kw[-1])
        node = trie[0]
        for cc in kw[:-1]:
            c = ord(cc)
            if node[c] == -1:
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]
        assert node[last] == -1, f"[{kw}] {node[last]} {node is trie[0]}"
        node[last] = tag.value << 1

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
            if node[c] == -1:
                if n == len(kw) - 1 and non_succ == set():
                    node[c] = tag.value << 1
                    return
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]

        # handle terminators
        for i in range(len(node)):
            if i not in non_succ:
                if node[i] == -1:
                    node[i] = (tag.value << 1) + 1

    # KWs = list(sorted(KWs))[0:1]

    # the sortorder ensures that a prefixes are procressed later
    for kw, tag in reversed(sorted(KWs)):
        # print (kw, tag)
        if tag in (TK_KIND.KW, TK_KIND.ANNOTATION):
            if kw.endswith("!"):
                add_kw_simple(kw, tag)
            else:
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
    DumpStats(trie)

    for i in range(1000):
        print(f"Optimization round {i}")
        old_len = len(trie)
        trie = OptimizeTrie(trie)
        if len(trie) == old_len:
            break
        DumpStats(trie)
        VerifyTrie(trie, KWs)
    return trie


def MakeTrie():
    KWs = GetAllKWAndOps()
    trie = MakeInitialTrie(KWs)
    for i in range(1000):
        old_len = len(trie)
        trie = OptimizeTrie(trie)
        if len(trie) == old_len:
            break
    return trie


def GenerateCodeCC(fout):
    trie = MakeTrie()

    # we reserver a few bytes for terminal markers
    assert len(trie) < 240
    print("int KeywordAndOpRecognizer[128][] = {", file=fout)

    print("}", file=fout)


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


ID_RE = re.compile(
    "^" + r"[$_a-zA-Z](?:[_a-zA-Z0-9])*(?:::[_a-zA-Z0-9]+)?(?::[_a-zA-Z0-9]+)?[#]?")
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
        self._trie: TRIE = MakeTrie()

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
            else:
                kind = TK_KIND.ID
                m = ID_RE.search(self._current_line)
            assert m, f"{repr(self._current_line)}"
            size = m.end()
            assert size > 0, f"{repr(self._current_line)}"
        if kind == TK_KIND.COMMENT:
            size = len(self._current_line)
        elif kind == TK_KIND.CHAR:
            m = CHAR_RE.search(self._current_line)
            assert m, f"{repr(self._current_line)}"
            size = m.end()
            assert size > 0, f"{repr(self._current_line)}"
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
                assert m, f"{repr(self._current_line)}"
                size = m.end()
                assert size > 0, f"{repr(self._current_line)}"
        token = self._current_line[:size]
        col = self._col_no
        self._col_no += len(token)
        self._current_line = self._current_line[len(token):]
        if kind == TK_KIND.GENERIC_ANNOTATION:
            kind = TK_KIND.ANNOTATION
            # remove curlies
            token = token[2:-2]
        return TK(kind, sl, sys.intern(token),  col)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        MakeTrieNoisy()
    elif sys.argv[1] == "gen_cc":
        cgen.ReplaceContent(GenerateCodeCC, sys.stdin, sys.stdout)
