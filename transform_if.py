"""
Ensures that if statements only have gotos in iftrue/iffalse and that
cond only consists of a simple expression.

"""
from pycparser import c_ast

import common

__all__ = ["IfTransform", "ShortCircuitIfTransform"]

branch_counter = 0


def GetLabel(prefix="branch"):
    global branch_counter
    branch_counter += 1
    return "%s_%s" % (prefix, branch_counter)


def ConvertToGotos(if_stmt: c_ast.If, parent):
    if (isinstance(if_stmt.iftrue, c_ast.Goto) and
            isinstance(if_stmt.iffalse, c_ast.Goto) and
            not isinstance(if_stmt.cond, c_ast.ExprList)):
        return

    label = GetLabel("if")
    labeltrue = label + "_true"
    labelfalse = label + "_false"
    labelend = label + "_end"
    emptytrue = common.IsEmpty(if_stmt.iftrue) or isinstance(if_stmt.iftrue, c_ast.Goto)
    emptyfalse = common.IsEmpty(if_stmt.iffalse) or isinstance(if_stmt.iffalse, c_ast.Goto)

    seq = []
    # TODO: this should be done in  EliminateExpressionLists(
    if isinstance(if_stmt.cond, c_ast.ExprList):
        exprs = if_stmt.cond.exprs
        if_stmt.cond = exprs.pop(-1)
        seq += exprs
    seq.append(if_stmt)
    if not emptytrue:
        seq += [c_ast.Label(labeltrue, c_ast.EmptyStatement()), if_stmt.iftrue]
        if not emptyfalse:
            seq.append(c_ast.Goto(labelend))
    if not emptyfalse:
        seq += [c_ast.Label(labelfalse, c_ast.EmptyStatement()), if_stmt.iffalse]
    seq.append(c_ast.Label(labelend, c_ast.EmptyStatement()))

    if not isinstance(if_stmt.iftrue, c_ast.Goto):
        if_stmt.iftrue = c_ast.Goto(labelend if emptytrue else labeltrue)
    if not isinstance(if_stmt.iffalse, c_ast.Goto):
        if_stmt.iffalse = c_ast.Goto(labelend if emptyfalse else labelfalse)

    stmts = common.GetStatementList(parent)
    if not stmts:
        stmts = [if_stmt]
        parent = common.ReplaceNode(parent, if_stmt, c_ast.Compound(stmts))

    pos = stmts.index(if_stmt)
    stmts[pos: pos + 1] = seq


def IfTransform(ast: c_ast.Node):
    """ make sure that there is not expression list inside the condition and that the
     true and false consist of at most a goto.
     This should be run after the loop conversions"""
    candidates = common.FindMatchingNodesPostOrder(ast, ast, lambda n, _: isinstance(n, c_ast.If))

    for if_stmt, parent in candidates:
        ConvertToGotos(if_stmt, parent)


def ConvertShortCircuitIf(if_stmt: c_ast.If, parent: c_ast.Node):
    cond = if_stmt.cond
    if isinstance(cond, c_ast.UnaryOp) and cond.op == "!":
        # for a not not just swap the branches
        if_stmt.cond = cond.expr
        if_stmt.iffalse, if_stmt.iftrue = if_stmt.iftrue, if_stmt.iffalse
        ConvertShortCircuitIf(if_stmt, parent)
        return

    if not isinstance(cond, c_ast.BinaryOp):
        return

    if cond.op != "&&" and cond.op != "||":
        return

    labelnext = GetLabel(prefix="branch")
    if cond.op == "&&":
        if_stmt2 = c_ast.If(cond.left, c_ast.Goto(labelnext), if_stmt.iffalse)
    else:
        assert cond.op == "||"
        if_stmt2 = c_ast.If(cond.left, if_stmt.iftrue, c_ast.Goto(labelnext))
    if_stmt.cond = cond.right

    stmts = common.GetStatementList(parent)
    # this is easy to fix but basically guaranteed after running IfTransform
    assert stmts, parent
    pos = stmts.index(if_stmt)
    stmts[pos:pos + 1] = [if_stmt2, c_ast.Label(labelnext, c_ast.EmptyStatement()), if_stmt]
    ConvertShortCircuitIf(if_stmt2, parent)
    ConvertShortCircuitIf(if_stmt, parent)


def ShortCircuitIfTransform(ast: c_ast.Node):
    """Requires that if statements only have gotos"""
    candidates = common.FindMatchingNodesPostOrder(ast, ast, lambda n, _: isinstance(n, c_ast.If))

    for if_stmt, parent in candidates:
        ConvertShortCircuitIf(if_stmt, parent)
