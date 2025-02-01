#!/bin/env python3

import collections
from FE import cwast


_DIGITS = "0123456789"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_ID_CHARS = set(ord(c) for c in "_" + _DIGITS + _LOWER + _UPPER)
_ALL_CHARS = set(range(256))


NODE_NULL = -1


def OptimizeTrie(trie):

    print("Optimize")
    nodes = list(sorted((b, a, len(b) - b.count(-1))
                 for a, b in enumerate((trie))))

    trans = [-1] * len(trie)
    last = nodes[0]
    for i in range(1, len(nodes)):
        curr = nodes[i]
        if last[0] == curr[0]:
            #print("@@", curr[1], "->", last[1], last[2])
            trans[curr[1]] = last[1]
        else:
            last = curr
    print(trans)
    new_indices = []
    n = 0
    for t in trans:
        if t == -1:
            new_indices.append(n)
            n += 1
        else:
            # this node will be dropped
            new_indices.append(-1)


    def rewrite(t):
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


def VerifyTrie(trie, KWs):
    print("\nVERIFY")
    for kw, tag in sorted(KWs):
        # print (kw, tag)
        kw = kw + "\x01"
        node = trie[0]
        for n, cc in enumerate(kw):
            x = node[ord(cc)]
            if x == tag:
                break
            assert x != -1, f"{kw} {n} {cc}"
            node = trie[x]

def DumpStats(trie):
    print("\nTRIE ANALYSIS")
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

    def add_kw(kw, tag, non_succ):
        last = None
        if non_succ is None:
            last = ord(kw[-1])
            kw = kw[:-1]
        node = trie[0]
        for cc in kw:
            c = ord(cc)
            if node[c] == -1:
                node[c] = add_node()
            # no kw can be prefix of another
            assert node[c] < len(trie), f"{kw} -- {node[c]}"
            node = trie[node[c]]

        # handle terminators
        if last:
            assert node[last] == -1, f"{kw}"
            node[last] = tag
        else:
            for i in range(len(node)):
                if i not in non_succ:
                    if node[i] == -1:
                        node[i] = tag

    KWs = []
    KWs += [(kw, 1001) for kw in cwast.KeyWordsForConcreteSyntax()]
    KWs += [(kw, 1002) for kw in cwast.ASSIGNMENT_SHORTCUT]
    KWs += [(kw, 1003) for kw in cwast.BinaryOpsForConcreteSyntax()]
    # KWs = list(sorted(KWs))[0:1]

    print("\nCREATE")
    for kw, tag in reversed(sorted(KWs)):
        # print (kw, tag)
        if tag == 1001:
            if kw.endswith("!"):
                add_kw(kw, tag, None)
            else:
                add_kw(kw, tag, _ID_CHARS)
        elif tag == 1002:
            add_kw(kw, tag, None)
        elif tag == 1003:
            add_kw(kw, tag, set())
    #
    VerifyTrie(trie, KWs)
    #
    DumpStats(trie)

    while True:
        old_len = len(trie)
        trie = OptimizeTrie(trie)
        if len(trie) == old_len:
            break
        DumpStats(trie)
        VerifyTrie(trie, KWs)

if __name__ == "__main__":
    MakeTrieForKW()