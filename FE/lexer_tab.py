#!/bin/env python3

import collections
import sys
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


TAG_KW = 1000
TAG_COMPOUND_ASSIGN = 1001
TAG_OTHER_OP = 1002
TAG_PREFIX_OP = 1003
TAG_ANNOTATION = 1004
TAG_ASSIGN = 1005
TAG_COLON = 1006
TAG_COMMA = 1007
TAG_PAREN_OPEN = 1008
TAG_PAREN_CLOSED = 1009
TAG_CURLY_OPEN = 1010
TAG_CURLY_CLOSED = 1011
TAG_SQUARE_OPEN = 1012
TAG_SQUARE_OPEN_EXCL = 1013
TAG_SQUARE_CLOSED = 1014


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
                return n, x >> 1
            else:
                return n + 1, x >> 1
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
    KWs += [(kw, TAG_KW) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, TAG_COMPOUND_ASSIGN) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, TAG_OTHER_OP) for kw in cwast.BinaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG_PREFIX_OP) for kw in cwast.UnaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG_KW) for kw in ["pub", "ref", "poly", "wrapped"]]
    KWs += [(kw, TAG_KW) for kw in ["else", "set", "for",
                                    "while", "tryset", "trylet", "trylet!"]]
    KWs += [("=", TAG_ASSIGN)]
    KWs += [(",", TAG_COMMA)]
    KWs += [(":", TAG_COLON)]
    #
    KWs += [("(", TAG_PAREN_OPEN)]
    KWs += [(")", TAG_PAREN_CLOSED)]
    # KWs += [("{", TAG_CURLY_OPEN)]
    KWs += [("}", TAG_CURLY_CLOSED)]
    KWs += [("[", TAG_SQUARE_OPEN)]
    KWs += [("[!", TAG_SQUARE_OPEN_EXCL)]
    KWs += [("]", TAG_SQUARE_CLOSED)]
    return KWs

SIMPLE_TAGS = set([
    TAG_COMPOUND_ASSIGN, TAG_COLON, TAG_COMMA, TAG_PAREN_OPEN,
    TAG_PAREN_CLOSED, TAG_CURLY_CLOSED, TAG_SQUARE_CLOSED,
    TAG_SQUARE_OPEN_EXCL,
])

MAY_BE_PREFIX_TAGS = set([
    TAG_OTHER_OP, TAG_PREFIX_OP, TAG_ASSIGN, TAG_SQUARE_OPEN,
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
        node[last] = tag << 1

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
                    node[c] = tag << 1
                    return
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]

        # handle terminators
        for i in range(len(node)):
            if i not in non_succ:
                if node[i] == -1:
                    node[i] = (tag << 1) + 1

    # KWs = list(sorted(KWs))[0:1]

    print("\nCREATE")
    # the sortorder ensures that a prefixes are procressed later
    for kw, tag in reversed(sorted(KWs)):
        # print (kw, tag)
        if tag == TAG_KW:
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


if __name__ == "__main__":
    if len(sys.argv) == 1:
        MakeTrieForKW()
    elif sys.argv[1] == "gen_cc":
        cgen.ReplaceContent(GenerateCodeCC, sys.stdin, sys.stdout)
