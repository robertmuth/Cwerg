#!/usr/bin/python3
"""
Ensures that if statements only have gotos in iftrue/iffalse and that
cond only consists of a simple expression.

"""
from pycparser import c_ast

import common
import meta

__all__ = ["IfTransform"]

branch_counter = 0


def GetLabel(prefix="branch"):
    global branch_counter
    branch_counter += 1
    return "%s_%s" % (prefix, branch_counter)


def ConvertToGotos(if_stmt: c_ast.If, parent, meta):
    if (isinstance(if_stmt.iftrue, c_ast.Goto) and
            isinstance(if_stmt.iffalse, c_ast.Goto) and
            not isinstance(if_stmt.cond, c_ast.ExprList)):
        return

    stmts = common.GetStatementList(parent)
    if not stmts:
        stmts = []
        parent = common.ReplaceNode(parent, if_stmt, c_ast.Compound(stmts))
        if isinstance(if_stmt.cond, c_ast.ExprList):
            exprs = if_stmt.cond.exprs
            if_stmt.cond = exprs.pop(-1)
            stmts.extend(exprs)
        stmts.append(if_stmt)
        #TODO: fix the branches

def IfTransform(ast: c_ast.Node, meta: meta.MetaInfo):
    """ make sure that there is not expression list inside the condition and that the
     true and false consist of at most a goto.
     This should be run after the loop conversions"""
    candidates = common.FindMatchingNodesPostOrder(ast, ast, lambda n, _: isinstance(n, c_ast.If))

    for if_stmt, parent in candidates:
        ConvertToGotos(if_stmt, parent, meta)
