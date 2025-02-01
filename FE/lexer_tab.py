#!/bin/env python3

import collections
import enum
import sys
import io

import dataclasses

from typing import Any, Optional

from FE import cwast
from Util import cgen


_DIGITS = "0123456789"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_ID_CHARS = set(ord(c) for c in "_" + _DIGITS + _LOWER + _UPPER)
_ALL_CHARS = set(range(256))


NODE_NULL = -1

NODE = list[int]
TRIE = list[list[int]]

@enum.unique
class TAG(enum.Enum):
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
    EOF = 1019


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

    def rewrite(t: NODE) -> NODE:
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
                return n, TAG(x >> 1)
            else:
                return n + 1, TAG(x >> 1)
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
    KWs += [(kw, TAG.KW) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, TAG.COMPOUND_ASSIGN) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, TAG.OTHER_OP) for kw in cwast.BinaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG.PREFIX_OP) for kw in cwast.UnaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG.KW) for kw in ["pub", "ref", "poly", "wrapped"]]
    KWs += [(kw, TAG.KW) for kw in ["else", "set", "for", "while",
                                    "tryset", "trylet", "trylet!"]]
    KWs += [("=", TAG.ASSIGN)]
    KWs += [(",", TAG.COMMA)]
    KWs += [(":", TAG.COLON)]
    #
    KWs += [("(", TAG.PAREN_OPEN)]
    KWs += [(")", TAG.PAREN_CLOSED)]
    KWs += [("{", TAG.CURLY_OPEN)]
    KWs += [("}", TAG.CURLY_CLOSED)]
    KWs += [("[", TAG.SQUARE_OPEN)]
    KWs += [("[!", TAG.SQUARE_OPEN_EXCL)]
    KWs += [("]", TAG.SQUARE_CLOSED)]
    #
    KWs += [(";", TAG.COMMENT)]
    KWs += [("'", TAG.CHAR)]
    KWs += [("{{", TAG.GENERIC_ANNOTATION)]
    KWs += [('"', TAG.STR)]
    KWs += [('x"', TAG.STR)]
    KWs += [('r"', TAG.STR)]

    return KWs


SIMPLE_TAGS = set([
    TAG.COMPOUND_ASSIGN, TAG.COLON, TAG.COMMA, TAG.PAREN_OPEN,
    TAG.PAREN_CLOSED, TAG.CURLY_CLOSED, TAG.SQUARE_CLOSED,
    TAG.SQUARE_OPEN_EXCL, TAG.COMMENT, TAG.CHAR, TAG.STR,
])

MAY_BE_PREFIX_TAGS = set([
    TAG.OTHER_OP, TAG.PREFIX_OP, TAG.ASSIGN, TAG.SQUARE_OPEN,
    TAG.CURLY_OPEN,  TAG.GENERIC_ANNOTATION,

])


def MakeInitialTrie(KWs):
    trie = []

    def add_node():
        l = [-1] * 129
        trie.append(l)
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

    print("\nCREATE")
    # the sortorder ensures that a prefixes are procressed later
    for kw, tag in reversed(sorted(KWs)):
        # print (kw, tag)
        if tag == TAG.KW:
            if kw.endswith("!"):
                add_kw_simple(kw, tag)
            else:
                add_kw(kw, tag, _ID_CHARS)
        elif tag in SIMPLE_TAGS:
            add_kw_simple(kw, tag)
        elif tag in MAY_BE_PREFIX_TAGS:
            add_kw(kw, tag, set())
        else:
            assert False
    #
    VerifyTrie(trie, KWs)
    return trie


def MakeTrieForKW():
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


def GenerateCodeCC(fout):
    KWs = GetAllKWAndOps()
    trie = MakeInitialTrie(KWs)
    for i in range(1000):
        old_len = len(trie)
        trie = OptimizeTrie(trie)
        if len(trie) == old_len:
            break

        VerifyTrie(trie, KWs)
    # we reserver a few bytes for terminal markers
    assert len(trie) < 240
    print("int KeywordAndOpRecognizer[128][] = {", file=fout)

    print("}", file=fout)


@dataclasses.dataclass()
class TK:
    kind: TAG
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
            return TK(TAG.SPECIAL_EOF, cwast.INVALID_SRCLOC, "", 0)
        if False:
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

if __name__ == "__main__":
    if len(sys.argv) == 1:
        MakeTrieForKW()
    elif sys.argv[1] == "gen_cc":
        cgen.ReplaceContent(GenerateCodeCC, sys.stdin, sys.stdout)
