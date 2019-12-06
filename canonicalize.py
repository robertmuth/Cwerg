#!/usr/bin/python3
"""
 Canonicalize the C source
 Transforms the ast into a simpler one using few node classes. etc.
 This will simplify code generation.
 The new ast can be re=emitted as working C code to test the correctness
 of the transformations

Currently implemented
 * remove void parameter lists: foo(void) -> foo()
 * insert all implicit casts
 * remove For,While, DoWhile nodes
 * remove ArrayRef node
 * remove UnaryOp("++") and UnaryOp("--") nodes
 * printf simplifications (goal is to get rid of EllipsisParam for most programs)
"""

import sys
from typing import List, Tuple

from pycparser import c_ast, parse_file, c_generator

import arrayref_transform
import common
import meta
import if_transform
import printf_transform

__all__ = ["Canonicalize"]

CONST_ZERO = c_ast.Constant("int", "0")

CONST_ONE = c_ast.Constant("int", "1")

label_counter = 0


def GetLabel(prefix="label"):
    global label_counter
    label_counter += 1
    return "%s_%s" % (prefix, label_counter)


# ================================================================================
# Remove void in favor of empty function argument expressions.
# E.g.:
# void fun(void)   =>  void fun()
# ================================================================================
def IsVoidArg(node):
    if not isinstance(node, c_ast.Typename): return False
    if not isinstance(node.type, c_ast.TypeDecl): return False
    type = node.type.type
    if not isinstance(type, c_ast.IdentifierType): return False
    names = type.names
    return len(names) == 1 and names[0] == "void"


def RemoveVoidParam(node: c_ast.Node):
    if isinstance(node, c_ast.ParamList) and len(node.params) == 1:
        if IsVoidArg(node.params[0]):
            node.params = []
    for c in node:
        RemoveVoidParam(c)


# ================================================================================
# Conversations of the form:
# unsigned -> int unsigned
# signed  ->  int
#
# After this step only types from NUM_TYPE_ORDER should occur
# ================================================================================
def CanonicalizeBaseTypes(node: c_ast.Node):
    if isinstance(node, c_ast.IdentifierType):
        node.names = common.CanonicalizeIdentifierType(node.names)
    for c in node:
        CanonicalizeBaseTypes(c)


# ================================================================================
# Make implicit conversions explicit by adding casts
# ================================================================================
def MakeCast(identifier_type, node):
    return c_ast.Cast(c_ast.Typename(None, [], c_ast.TypeDecl(None, [], identifier_type)), node)


def AddExplicitCasts(node: c_ast.Node, parent: c_ast.Node, meta_info, skip_constants):
    def constant_check(node):
        return not skip_constants or not isinstance(node, c_ast.Constant)

    for c in node:
        AddExplicitCasts(c, node, meta_info, skip_constants)

    if isinstance(node, c_ast.BinaryOp):
        tl = meta_info.type_links[node.left]
        tr = meta_info.type_links[node.right]
        if not isinstance(tl, c_ast.IdentifierType) or not isinstance(tr, c_ast.IdentifierType):
            return

        cmp = common.TypeCompare(tl, tr)
        if cmp == "<" and constant_check(node.left):
            node.left = MakeCast(tr, node.left)
            meta_info.type_links[node.left] = tr
        elif cmp == ">" and constant_check(node.right):
            node.right = MakeCast(tl, node.right)
            meta_info.type_links[node.right] = tl

    elif isinstance(node, c_ast.Assignment):
        left = meta_info.type_links[node.lvalue]
        right = meta_info.type_links[node.rvalue]
        if not isinstance(left, c_ast.IdentifierType) or not isinstance(right, c_ast.IdentifierType):
            return
        if left is not right and constant_check(node.rvalue):
            node.rvalue = MakeCast(left, node.rvalue)
            meta_info.type_links[node.rvalue] = left

    #     if not p: return
    #     right = CanonicalScalarType(ttab[node.rvalue])
    #     if right != p:
    #         node.rvalue = MakeCast(p, node.rvalue)
    #
    # elif isinstance(node, c_ast.FuncCall):
    #     pass
    elif isinstance(node, c_ast.Return):
        if node.expr and constant_check(node.expr):
            src = meta_info.type_links[node.expr]
            dst = meta_info.type_links[node]
            if not isinstance(src, c_ast.IdentifierType) or not isinstance(dst, c_ast.IdentifierType):
                return
            if src is not dst:
                node.expr = MakeCast(dst, node.expr)
                meta_info.type_links[node.expr] = dst
    # TODO: function call


# ================================================================================
# Transform post inc/dev to pre inc/dec which are sementically simpler
# ================================================================================
def IsSuitablePostIncDec(node, parent):
    if not isinstance(node, c_ast.UnaryOp): return False
    if node.op not in common.POST_INC_DEC_OPS: return False
    if isinstance(parent, (c_ast.Compound, c_ast.Case, c_ast.Default)): return True
    if isinstance(parent, c_ast.If) and node != parent.cond: return True
    if isinstance(parent, c_ast.For) and node != parent.cond: return True
    if isinstance(parent, c_ast.DoWhile) and node != parent.cond: return True
    if isinstance(parent, c_ast.While) and node != parent.cond: return True
    if isinstance(parent, c_ast.Switch) and node != parent.cond: return True
    return False


def ConvertPostToPreIncDec(ast: c_ast.Node):
    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsSuitablePostIncDec)

    for node, parent in candidates:
        node.op = node.op[1:]  # strip out the leading "p"


# ================================================================================
# This transformation ensures that arguments of logic ops are either other logic ops  or comparisons
# E.g.:
# !p   =>  (p == 0)
# (a+b) && <expr>   =>    (a+b) != 0 && <expr>\
#
# Produces untyped nodes
# ================================================================================
def IsNodeRequiringBoolInt(node: c_ast, _):
    return (isinstance(node, c_ast.If) or
            isinstance(node, c_ast.For) or
            isinstance(node, c_ast.BinaryOp) and node.op in common.SHORT_CIRCUIT_OPS or
            isinstance(node, c_ast.UnaryOp) and node.op == "!")


def IsExprOfTypeBoolInt(node: c_ast):
    return (isinstance(node, c_ast.BinaryOp) and node.op in common.BOOL_INT_TYPE_BINARY_OPS or
            isinstance(node, c_ast.UnaryOp) and node.op in common.BOOL_INT_TYPE_UNARY_OPS)


def FixNodeRequiringBoolInt(ast: c_ast.Node, meta_info):
    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsNodeRequiringBoolInt)
    meta_info.type_links[CONST_ZERO] = meta.INT_IDENTIFIER_TYPE
    for node, parent in candidates:
        if isinstance(node, c_ast.If):
            if not IsExprOfTypeBoolInt(node.cond):
                node.cond = c_ast.BinaryOp("!=", node.cond, CONST_ZERO)
                meta_info.type_links[node.cond] = meta.INT_IDENTIFIER_TYPE
        elif isinstance(node, c_ast.For) and node.cond:
            if not IsExprOfTypeBoolInt(node.cond):
                node.cond = c_ast.BinaryOp("!=", node.cond, CONST_ZERO)
                meta_info.type_links[node.cond] = meta.INT_IDENTIFIER_TYPE
        elif isinstance(node, c_ast.UnaryOp) and node.op == "!":
            if not IsExprOfTypeBoolInt(node.expr):
                node = c_ast.BinaryOp("==", node.expr, CONST_ZERO)  # note: we are replacing the "!" node
                meta_info.type_links[node] = meta.INT_IDENTIFIER_TYPE

        elif isinstance(node, c_ast.BinaryOp) and node.op in common.SHORT_CIRCUIT_OPS:
            if not IsExprOfTypeBoolInt(node.left):
                node.left = c_ast.BinaryOp("!=", node.left, CONST_ZERO)
                meta_info.type_links[node.left] = meta.INT_IDENTIFIER_TYPE
            if not IsExprOfTypeBoolInt(node.right):
                node.right = c_ast.BinaryOp("!=", node.right, CONST_ZERO)
                meta_info.type_links[node.right] = meta.INT_IDENTIFIER_TYPE


# ================================================================================
#
# ================================================================================
def ConvertPreIncDecToCompoundAssignment(ast, meta_info):
    def IsPreIncDec(node, parent):
        return isinstance(node, c_ast.UnaryOp) and node.op in common.PRE_INC_DEC_OPS

    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsPreIncDec)
    meta_info.type_links[CONST_ONE] = meta.INT_IDENTIFIER_TYPE

    for node, parent in candidates:
        op = "+=" if node.op == "++" else "-="
        a = c_ast.Assignment(op, node.expr, CONST_ONE)
        meta_info.type_links[a] = meta_info.type_links[node.expr]
        common.ReplaceNode(parent, node, a)


# ================================================================================
#
# ================================================================================
def ConvertWhileLoop(ast):
    def IsWhileLoop(node, _):
        return isinstance(node, (c_ast.DoWhile, c_ast.While))

    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsWhileLoop)
    for node, parent in candidates:
        loop_label = GetLabel("while")
        test_label = GetLabel("while_cond")
        exit_label = GetLabel("while_exit")
        conditional = c_ast.If(node.cond, c_ast.Goto(loop_label), None)
        block = [c_ast.Label(loop_label, node.stmt),
                 c_ast.Label(test_label, conditional),
                 c_ast.Label(exit_label, c_ast.EmptyStatement())]
        if isinstance(node, c_ast.While):
            block = [c_ast.Goto(test_label)] + block
        common.ReplaceBreakAndContinue(node.stmt, node, test_label, exit_label)
        common.ReplaceNode(parent, node, c_ast.Compound(block))


# ================================================================================
#
# ================================================================================
def EliminateExpressionLists(ast):
    """This is works best after for loop conversions
    TODO: make this work for all cases
    currently we duplicate some work in the "if transform"
    """
    def IsExpressionList(node, parent):
        return isinstance(node, c_ast.ExprList) and not isinstance(parent, c_ast.FuncCall)

    candidates = common.FindMatchingNodesPostOrder(ast, ast, IsExpressionList)
    for node, parent in candidates:
        stmts = common.GetStatementList(parent)
        if stmts:
            pos = stmts.index(node)
            stmts[pos:pos+1] = node.exprs


# ================================================================================
#
# ================================================================================
def ExtractForInitStatements(node):
    if node is None:
        return []
    elif isinstance(node, c_ast.DeclList):
        return node.decls
    else:
        return [node]


def ConvertForLoop(ast):
    candidates: List[Tuple[c_ast.For, c_ast.Node]] = common.FindMatchingNodesPostOrder(ast, ast,
                                                                                       lambda n, _: isinstance(n,
                                                                                                               c_ast.For))
    for node, parent in candidates:
        loop_label = GetLabel("for")
        next_label = GetLabel("for_next")
        test_label = GetLabel("for_cond")
        exit_label = GetLabel("for_exit")
        goto = c_ast.Goto(loop_label)
        conditional = c_ast.If(node.cond, goto, None) if node.cond else goto
        block = ExtractForInitStatements(node.init) + [
            c_ast.Goto(test_label),
            c_ast.Label(loop_label, node.stmt),
            c_ast.Label(next_label, node.next if node.next else c_ast.EmptyStatement()),
            c_ast.Label(test_label, conditional),
            c_ast.Label(exit_label, c_ast.EmptyStatement())]
        common.ReplaceBreakAndContinue(node.stmt, node, next_label, exit_label)
        common.ReplaceNode(parent, node, c_ast.Compound(block))


# ================================================================================
#
# ================================================================================
def ConfirmAbsenceOfUnsupportedFeatures(node: c_ast.Node, parent):
    for c in node:
        ConfirmAbsenceOfUnsupportedFeatures(c, node)

    if isinstance(node, c_ast.UnaryOp):
        # assert node.op not in common.POST_INC_DEC_OPS
        assert node.op not in common.PRE_INC_DEC_OPS

    elif isinstance(node, c_ast.ParamList):
        params = node.params
        assert not params or not IsVoidArg(params[0])

    elif isinstance(node, c_ast.ArrayRef):
        assert False

    elif isinstance(node, c_ast.ExprList) and not isinstance(parent, c_ast.FuncCall):
        assert False, parent

    elif isinstance(node, c_ast.If):
        assert isinstance(node.iftrue, c_ast.Goto), node
        assert isinstance(node.iffalse, c_ast.Goto), node

    # elif isinstance(node, c_ast.EllipsisParam):
    #    assert False


# ================================================================================
#
# ================================================================================
def Canonicalize(ast: c_ast.Node, meta_info: meta.MetaInfo):
    ConvertPostToPreIncDec(ast)
    RemoveVoidParam(ast)
    CanonicalizeBaseTypes(ast)
    meta_info.CheckConsistency(ast)

    printf_transform.PrintfSplitterTransform(ast, meta_info)
    meta_info.CheckConsistency(ast)

    ConvertPreIncDecToCompoundAssignment(ast, meta_info)
    meta_info.CheckConsistency(ast)

    ConvertWhileLoop(ast)
    ConvertForLoop(ast)
    meta_info.CheckConsistency(ast)

    EliminateExpressionLists(ast)

    if_transform.IfTransform(ast, meta_info)
    meta_info.CheckConsistency(ast)

    FixNodeRequiringBoolInt(ast, meta_info)
    meta_info.CheckConsistency(ast)

    arrayref_transform.ConvertArrayIndexToPointerDereference(ast, meta_info)
    meta_info.CheckConsistency(ast)

    # This should go last so that we do not have worry to mess this
    # up in other phases.
    AddExplicitCasts(ast, ast, meta_info, False)
    meta_info.CheckConsistency(ast)

    ConfirmAbsenceOfUnsupportedFeatures(ast, ast)


def main(argv):
    filename = argv[0]
    ast = parse_file(filename, use_cpp=True)
    meta_info = meta.MetaInfo(ast)
    Canonicalize(ast, meta_info)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
