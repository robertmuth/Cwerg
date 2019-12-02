#!/usr/bin/python3

"""
 Canonicalize the C source:

 * remove void parameter lists: foo(void) -> foo()
 * insert all implicit casts
 * replace for/while/do-while with label and gotos

"""

import sys
from typing import Optional, List, Tuple

from pycparser import c_ast, parse_file, c_generator

import common
import meta
import printf_transform

__all__ = ["Canonicalize"]

CONST_ZERO = c_ast.Constant("int", "0")

CONST_ONE = c_ast.Constant("int", "1")

label_counter = 0


def GetLabel():
    global label_counter
    label_counter += 1
    return "label_%s" % label_counter


def FindMatchingNodesPostOrder(node: c_ast.Node, parent: c_ast.Node, matcher):
    res: List[Tuple[c_ast.Node, c_ast.Node]] = []
    for c in node:
        res += FindMatchingNodesPostOrder(c, node, matcher)
    if matcher(node, parent):
        res.append((node, parent))
    return res


def FindMatchingNodesPreOrder(node: c_ast.Node, parent: c_ast.Node, matcher):
    res: List[Tuple[c_ast.Node, c_ast.Node]] = []
    if matcher(node, parent):
        res.append((node, parent))
    for c in node:
        res += FindMatchingNodesPreOrder(c, node, matcher)

    return res


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
# This transformation splits printf calls with constant format string into several printf
# calls. Each of which has at most one argument besides the format string
# This eliminates the primary use case of variable argument lists.
#
# This invalidates sym_tab and type_tab
# ================================================================================
def IsSuitablePrintf(node: c_ast.Node, _):
    if not isinstance(node, c_ast.FuncCall): return None
    if not isinstance(node.name, c_ast.ID): return None
    if node.name.name != "printf": return None
    assert isinstance(node.args, c_ast.ExprList)
    assert len(node.args.exprs) > 0
    format_arg = node.args.exprs[0]
    if not isinstance(format_arg, c_ast.Constant): return None
    assert format_arg.type == "string"
    return True


# TODO: update sym and type tabs
def GetStatementList(node: c_ast.Node):
    if isinstance(node, (c_ast.Default, c_ast.Case)):
        return node.stmts
    elif isinstance(node, c_ast.Compound):
        return node.block_items
    else:
        # return None
        assert False, node


def MakePrintfCall(fmt_str, arg_node: Optional[c_ast.Node]):
    args = [c_ast.Constant("string", '"' + fmt_str + '"')]
    if arg_node: args.append(arg_node)
    return c_ast.FuncCall(c_ast.ID("printf"), c_ast.ExprList(args))


def DoPrintfSplitter(call: c_ast.FuncCall, parent, meta_info: meta.MetaInfo):
    args = call.args.exprs
    fmt_pieces = printf_transform.TokenizeFormatString(args[0].value[1:-1])
    if not fmt_pieces: return
    if len(fmt_pieces) == 1: return

    stmts = GetStatementList(parent)
    if not stmts:
        assert False, parent

    calls = []
    args = args[1:]  # skip the format string
    for f in fmt_pieces:
        arg = None
        if f[0] == '%' and len(f) > 1:
            arg = args.pop(0)
        c = MakePrintfCall(f, arg)
        meta_info.type_links[c] = meta_info.type_links[call]
        meta_info.type_links[c.args] = meta_info.type_links[call.args]
        meta_info.type_links[c.args.exprs[0]] = meta_info.type_links[call.args.exprs[0]]
        meta_info.type_links[c.name] = meta_info.type_links[call.name]
        meta_info.sym_links[c.name] = meta_info.sym_links[call.name]
        calls.append(c)
    pos = stmts.index(call)
    stmts[pos:pos + 1] = calls


def PrintfSplitter(ast: c_ast.Node, meta: meta.MetaInfo):
    candidates = FindMatchingNodesPostOrder(ast, ast, IsSuitablePrintf)

    for call, parent in candidates:
        DoPrintfSplitter(call, parent, meta)


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
    candidates = FindMatchingNodesPostOrder(ast, ast, IsSuitablePostIncDec)

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
    candidates = FindMatchingNodesPostOrder(ast, ast, IsNodeRequiringBoolInt)
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

    candidates = FindMatchingNodesPostOrder(ast, ast, IsPreIncDec)
    meta_info.type_links[CONST_ONE] = meta.INT_IDENTIFIER_TYPE

    for node, parent in candidates:
        op = "+=" if node.op == "++" else "-="
        a = c_ast.Assignment(op, node.expr, CONST_ONE)
        meta_info.type_links[a] = meta_info.type_links[node.expr]
        common.ReplaceNode(parent, node, a)


# ================================================================================
#
# ================================================================================
def ConvertWhileLoop(ast, meta_info):
    def IsWhileLoop(node, _):
        return isinstance(node, (c_ast.DoWhile, c_ast.While))

    candidates = FindMatchingNodesPostOrder(ast, ast, IsWhileLoop)
    for node, parent in candidates:
        loop_label = GetLabel()
        test_label = GetLabel()
        exit_label = GetLabel()
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
def ExtractForInitStatements(node):
    if node is None:
        return []
    elif isinstance(node, c_ast.DeclList):
        return node.decls
    else:
        return [node]


def ConvertForLoop(ast, meta_info):
    candidates: List[Tuple[c_ast.For, c_ast.Node]] = FindMatchingNodesPostOrder(ast, ast, lambda n, _: isinstance(n, c_ast.For))
    for node,  parent in candidates:
        loop_label = GetLabel()
        next_label = GetLabel()
        test_label = GetLabel()
        exit_label = GetLabel()
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
# Note the ArrayRefs, e.g.
# board[i][j])
# are parsed left to right
#  ArrayRef:
#      ArrayRef:
#          ID: board
#           ID: i
#      ID: j
# But the ArrayDecls, e.g.
# char board[10][20];
# are parsed right to left
#   ArrayDecl: []
#       ArrayDecl: []
#           TypeDecl: board, []
#               IdentifierType: ['char']
#           Constant: int, 20
#       Constant: int, 10
# ================================================================================
def GetStride(node):
    stride = 1
    while node and isinstance(node, c_ast.ArrayDecl):
        assert isinstance(node.dim, c_ast.Constant), node.dim
        assert node.dim.type == "int"
        stride *= int(node.dim.value)
        node = node.type
    return stride


def GetArrayRefMultiplier(node, type):
    if isinstance(type, c_ast.ArrayDecl):
        return GetStride(type)
    elif isinstance(type, c_ast.IdentifierType):
        return 1
    else:
        assert False, type


def MakeCombinedSubscript(node, meta_info):
        subscripts = []
        while isinstance(node, c_ast.ArrayRef):
            #print (node)
            #print (meta_info.type_links[node])
            #print (node.subscript)
            old_subscript = node.subscript
            assert meta_info.type_links[old_subscript] in common.ALLOWED_IDENTIFIER_TYPES
            multiplier = GetArrayRefMultiplier(node, meta_info.type_links[node])
            if common.IsZeroConstant(old_subscript):
                continue
            elif multiplier == 1:
                subscripts.append(old_subscript)
            else:
                new_subscript = c_ast.BinaryOp("*", old_subscript, c_ast.Constant("int", str(multiplier)))
                subscripts.append(new_subscript)
                meta_info.type_links[new_subscript] = meta_info.type_links[old_subscript]
                meta_info.type_links[new_subscript.right] = common.GetCanonicalIdentifierType(["int"])

            node = node.name
        s = subscripts[0]
        for x in subscripts[1:]:
            s = c_ast.BinaryOp("+", s, x)
            # TODO: compute the max type
            meta_info.type_links[s] =  meta_info.type_links[x]
        return node, s


def ConvertArrayIndexToPointerDereference(ast, meta_info):
    def IsArrayRefChain(node, parent):
        # this may need some extra checks to ensure the chain is for the  same type
        return isinstance(node, c_ast.ArrayRef) and not isinstance(parent, c_ast.ArrayRef)

    candidates: List[Tuple[c_ast.ArrayRef, c_ast.Node]] = FindMatchingNodesPreOrder(ast, ast, IsArrayRefChain)


    for node, parent in candidates:
        name, s = MakeCombinedSubscript(node, meta_info)
        deref = c_ast.UnaryOp("*", c_ast.BinaryOp("+", name, s))
        # TODO: this is totally wrong
        meta_info.type_links[deref.expr] = meta_info.type_links[node]
        meta_info.type_links[deref] = meta_info.type_links[node]  # expression has not changed
        common.ReplaceNode(parent, node, deref)


def CollapseArrayDeclChains(ast, meta_info):
    def IsArrayDeclChain(node, parent):
        # this may need some extra checks to ensure the chain is for the  same type
        return isinstance(node, c_ast.ArrayDecl) and not isinstance(parent, c_ast.ArrayDecl)

    candidates: List[Tuple[c_ast.ArrayDecl, c_ast.Node]] = FindMatchingNodesPreOrder(ast, ast, IsArrayDeclChain)
    for node, parent in candidates:
        pass


# ================================================================================
#
# ================================================================================
def ConfirmAbsenceOfUnsupportedFeatures(node: c_ast.Node):
    for c in node:
        ConfirmAbsenceOfUnsupportedFeatures(c)

    if isinstance(node, c_ast.UnaryOp):
        # assert node.op not in common.POST_INC_DEC_OPS
        assert node.op not in common.PRE_INC_DEC_OPS

    elif isinstance(node, c_ast.ParamList):
        params = node.params
        assert not params or not IsVoidArg(params[0])
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

    PrintfSplitter(ast, meta_info)
    meta_info.CheckConsistency(ast)

    FixNodeRequiringBoolInt(ast, meta_info)
    meta_info.CheckConsistency(ast)

    ConvertPreIncDecToCompoundAssignment(ast, meta_info)
    meta_info.CheckConsistency(ast)

    ConvertWhileLoop(ast, meta_info)
    ConvertForLoop(ast, meta_info)
    meta_info.CheckConsistency(ast)

    #ConvertArrayIndexToPointerDereference(ast, meta_info)
    #meta_info.CheckConsistency(ast)

    # This should go last so that we do not have worry to mess this
    # up in other phases.
    AddExplicitCasts(ast, ast, meta_info, False)
    meta_info.CheckConsistency(ast)

    ConfirmAbsenceOfUnsupportedFeatures(ast)


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
