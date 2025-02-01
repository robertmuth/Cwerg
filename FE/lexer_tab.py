#!/bin/env python3

import collections
from FE import cwast


_DIGITS = "0123456789"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_ID_CHARS = set(ord(c) for c in "_" + _DIGITS + _LOWER + _UPPER)
_ALL_CHARS = set(range(256))


NODE_NULL = -1

NODE = list[int]
TRIE = list[list[int]]


TAG_KW = 2000
TAG_KW_SENTINEL = 2001
TAG_COMPOUND = 2002
TAG_COMPOUND_SENTINEL = 2003
TAG_BINARY = 2004
TAG_BINARY_SENTINEL = 2005
TAG_UNARY = 2006
TAG_UNARY_SENTINEL = 2007
TAG_ANNOTATION = 2008
TAG_ANNOTATION_SENTINEL = 2009
TAG_ASSIGN = 2010
TAG_ASSIGN_SENTINEL = 2011

def IsEmptyNode(n: NODE):
    for x in n:
        if x != -1:
            return False
    return True


def OptimizeTrie(trie: TRIE) -> TRIE:

    print("Optimize")
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
                return n, x ^ 1
            else:
                return n + 1, x
        node = trie[x]
    return 0, 0


def VerifyTrie(trie: TRIE, KWs):
    print("\nVERIFY")
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


def MakeTrieForKW():
    trie = []

    def add_node():
        l = [-1] * 256
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
        node[last] = tag

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
                    node[c] = tag
                    return
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]

        # handle terminators
        for i in range(len(node)):
            if i not in non_succ:
                if node[i] == -1:
                    node[i] = tag + 1

    KWs = []
    KWs += [(kw, TAG_KW) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, TAG_COMPOUND) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, TAG_BINARY) for kw in cwast.BinaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG_UNARY) for kw in cwast.UnaryOpsForConcreteSyntax()]
    KWs += [(kw, TAG_KW) for kw in ["pub", "ref", "poly", "wrapped"]]
    KWs += [(kw, TAG_KW) for kw in ["else", "set", "for",
                                    "while", "tryset", "trylet", "trylet!"]]
    KWs += [("=", TAG_ASSIGN)]


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
        elif tag == TAG_COMPOUND:
            add_kw_simple(kw, tag)
        elif tag == TAG_ASSIGN:
            add_kw(kw, tag, set([ord("=")]))
        elif tag == TAG_BINARY or tag == TAG_UNARY:
            add_kw(kw, tag, set())
    #
    VerifyTrie(trie, KWs)
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


if __name__ == "__main__":
    MakeTrieForKW()
