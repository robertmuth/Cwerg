from collections.abc import Iterable

from typing import Any
import collections
from FE import cwast


def UpdateNodeHistogram(node: Any, counters: collections.defaultdict):

    def visitor(node, _field):
        nonlocal counters
        counters[node.__class__.__name__] += 1

    cwast.VisitAstRecursivelyPost(node, visitor)


def ComputeNodeHistogram(nodes: Iterable[Any]) -> collections.defaultdict:
    counters = collections.defaultdict(int)
    for n in nodes:
        UpdateNodeHistogram(n, counters)
    return counters


def DumpCounter(counters: collections.defaultdict):
    for kv in reversed(sorted(counters.items(), key=lambda x: x[1])):
        print (f"{kv[1]:-5} {kv[0]}")