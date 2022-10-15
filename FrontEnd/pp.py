#!/usr/bin/python3

"""Pretty printer Cwerg AST

"""

import dataclasses
import sys
import logging

from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)


def _RenderRecursively(node, out, indent: str):
    line = out[-1]
    if isinstance(node, cwast.TypeBase):
        line.append(node.base_type_kind.name.lower())
        return
    elif isinstance(node, cwast.ValUndef):
        line.append("undef")
        return
    elif isinstance(node, cwast.Auto):
        line.append("auto")
        return
    elif isinstance(node, cwast.Id):
        line.append(node.name)
        return 
    elif isinstance(node, cwast.ValTrue):
        line.append("true")
        return 
    elif isinstance(node, cwast.ValFalse):
        line.append("true")
        return 
    elif isinstance(node, cwast.ValNum):
        line.append(node.number)
        return 

    line.append("(" + node.__class__.__name__)
    for field in node.__class__.FIELDS:
        line = out[-1]
        val = getattr(node, field)
        if field in cwast.FLAG_FIELDS:
            if val:
                line.append(" " + field)
        elif field in cwast.STR_FIELDS:
            line.append(" " + str(val))
        elif field in cwast.INT_FIELDS:
            line.append(" " + str(val))
        elif field in cwast.KIND_FIELDS:
            line.append(" " + val.name)
        elif field in cwast.NODE_FIELDS:
            line.append(" ")
            _RenderRecursively(val, out, indent)
        elif field in cwast.LIST_FIELDS:
            if not val:
                line.append(" []")
            else:
                line.append(" [")
                for cc in val:
                    out.append([" " * (indent + 1)])
                    _RenderRecursively(cc, out, indent + 1)
                out[-1].append("]")
        else:
            assert False

    line = out[-1]
    line.append(")")


def PrettyPrint(mod: cwast.DefMod) -> List[Tuple[int, str]]:
    out = [[""]]
    _RenderRecursively(mod, out, 0)
    for a in out:
        print("".join(a))


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    try:
        while True:
            stream = cwast.ReadTokens(sys.stdin)
            t = next(stream)
            assert t == "("
            sexpr = cwast.ReadSExpr(stream)
            PrettyPrint(sexpr)
    except StopIteration:
        pass
