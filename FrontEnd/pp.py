#!/usr/bin/python3

"""Pretty printer (PP) for Cwerg AST

"""

import dataclasses
import sys
import logging

from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)


def MaybeSimplifyLeafNode(node) -> Optional[str]:
    if isinstance(node, cwast.TypeBase):
        return node.base_type_kind.name.lower()
    elif isinstance(node, cwast.ValUndef):
        return "undef"
    elif isinstance(node, cwast.Auto):
        return "auto"
    elif isinstance(node, cwast.Id):
        return node.name
    elif isinstance(node, cwast.ValTrue):
        return "true"
    elif isinstance(node, cwast.ValFalse):
        return "false"
    elif isinstance(node, cwast.ValNum):
        return node.number
    elif isinstance(node, cwast.ValVoid):
        return "void"
    elif isinstance(node, cwast.ValArrayString):
        return node.string
    else:
        return None


def IsFieldWithDefaultValue(field, val):
    expected = cwast.OPTIONAL_FIELDS.get(field)
    return val == expected


def GetNodeTypeAndFields(node, condense=True):
    cls = node.__class__
    fields = cls.FIELDS[:]
    if not condense:
        return cls.__name__, fields
 
    if isinstance(node, cwast.StmtCompoundAssignment):
        fields.pop(0)
        return cwast.ASSIGMENT_SHORTCUT_INV[node.assignment_kind], fields
    elif isinstance(node, cwast.Expr1):
        fields.pop(0)
        return cwast.UNARY_SHORTCUT_INV[node.unary_expr_kind], fields
    elif isinstance(node, cwast.Expr2):
        fields.pop(0)
        return cwast.BINOP_SHORTCUT_INV[node.binary_expr_kind], fields
    elif cls.ALIAS:
        return cls.ALIAS, fields
    else:
        return cls.__name__, fields


def _RenderRecursively(node, out, indent: str):
    line = out[-1]
    abbrev = MaybeSimplifyLeafNode(node)
    if abbrev:
        line.append(abbrev)
        return

    node_name, fields = GetNodeTypeAndFields(node)
    line.append("(" + node_name)

    for field in fields:
        line = out[-1]
        field_kind = cwast.ALL_FIELDS_MAP[field].kind
        val = getattr(node, field)
        if field_kind is cwast.NFK.FLAG:
            if val:
                line.append(" " + field)
        elif IsFieldWithDefaultValue(field, val):
            continue
        elif field_kind is cwast.NFK.STR:
            line.append(" " + str(val))
        elif field_kind is cwast.NFK.INT:
            line.append(" " + str(val))
        elif field_kind is cwast.NFK.KIND:
            line.append(" " + val.name)
        elif field_kind is cwast.NFK.NODE:
            line.append(" ")
            _RenderRecursively(val, out, indent)
        elif field_kind is cwast.NFK.LIST:
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
