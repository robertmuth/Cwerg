"""
TODO
"""
from typing import Mapping

from pycparser import c_ast

import common

__all__ = ["PruneUselessLabels"]


# ================================================================================
#
# ================================================================================
def IsStateChange(node):
    if isinstance(node, (c_ast.FuncCall, c_ast.Assignment, c_ast.ArrayRef, c_ast.Return)):
        return True
    if isinstance(node, c_ast.UnaryOp) and node.op in ["*", "p++", "p--"]:
        return True
    return False


def IsStateChangeAndFollowChildren(node):
    if isinstance(node, (c_ast.For, c_ast.If, c_ast.While, c_ast.DoWhile)):
        return True
    return False


def SerializeLabelsAndGotos(node: c_ast.Node):
    """this is meant to be very conservative
    The idea is to put all the Label nodes in order into a list
    separated by one or more None entries if there is intervening
    code. Labels which are adjacent can be merged
    """
    out = []
    if isinstance(node, c_ast.Label):
        out.append(node)
        out += SerializeLabelsAndGotos(node.stmt)
    if isinstance(node, c_ast.Goto):
        out.append(node)
    elif isinstance(node, c_ast.EmptyStatement):
        pass
    elif IsStateChange(node):
        out.append(node.__class__.__name__)
    elif isinstance(node, (c_ast.For, c_ast.While, c_ast.If, c_ast.DoWhile)):
        out.append(node.__class__.__name__)
        for c in node:
            out += SerializeLabelsAndGotos(c)
    else:
        for c in node:
            out += SerializeLabelsAndGotos(c)
    return out


def ForwardGotosAndRemoveUnusedLabels(node: c_ast.Node, forwards: Mapping[str, str]):
    def IsGotoOrLabel(node, _):
        return isinstance(node, (c_ast.Goto, c_ast.Label))

    candidates = common.FindMatchingNodesPostOrder(node, node, IsGotoOrLabel)

    for node, parent in candidates:
        if isinstance(node, c_ast.Goto):
            while node.name in forwards:
                node.name = forwards[node.name]
        elif isinstance(node, c_ast.Label) and node.name in forwards:
            stmts = common.GetStatementList(parent)
            assert stmts, parent
            stmts.remove(node)


def ComputeLabelForwards(serialized):
    forwards = {}
    last = None
    for item in serialized:
        if isinstance(item, c_ast.Label) and isinstance(last, c_ast.Label):
            forwards[last.name] = item.name
        last = item
    return forwards


def PruneUselessLabels(fun: c_ast.Node):
    serialized = SerializeLabelsAndGotos(fun)
    forwards = ComputeLabelForwards(serialized)
    ForwardGotosAndRemoveUnusedLabels(fun, forwards)
    serialized = SerializeLabelsAndGotos(fun)
    forwards = ComputeLabelForwards(serialized)
    assert not forwards
