from collections.abc import Iterable

from typing import Any
import collections
from FE import cwast


def UpdateNodeHistogram(node: Any, counters: collections.defaultdict):

    def visitor(node):
        nonlocal counters
        counters[node.__class__.__name__] += 1

    cwast.VisitAstRecursivelyPost(node, visitor)


def ComputeNodeHistogram(nodes: Iterable[Any]) -> collections.defaultdict:
    counters = collections.defaultdict(int)
    for n in nodes:
        UpdateNodeHistogram(n, counters)
    return counters


def DumpCounter(counters: collections.defaultdict):
    total = 0
    for kv in reversed(sorted(counters.items(), key=lambda x: x[1])):
        kind, count = kv
        total += count
        print(f"{count:-7} {kind}")

    print(f"{total:-7} TOTAL")

_Counters: collections.defaultdict[tuple[str,
                                         str], int] = collections.defaultdict(int)


def IncCounter(family: str, metric: str, val: int):
    _Counters[(family, metric)] += val


def DumpStats():
    for kv in sorted(_Counters.items(), key=lambda x: x[0]):
        [family, metric], val = kv
        print(f"{family:10}{metric:10} {val:-5}")
