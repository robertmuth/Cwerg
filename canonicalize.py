#!/usr/bin/python3

"""
 Canonicalize the C source:

 * remove void parameter lists: foo(void) -> foo()
 * insert all implicit casts

"""

import sys
from typing import Optional

from pycparser import c_ast, parse_file, c_generator

import common
import printf_transform
import meta


def FindMatchingNodesPostOrder(node: c_ast.Node, parent: c_ast.Node, matcher):
    res = []
    for c in node:
        res += FindMatchingNodesPostOrder(c, node, matcher)
    if matcher(node, parent):
        res.append((node, parent))
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
#
# ================================================================================
def CanonicalizeIdentifierTypes(node: c_ast.Node):
    if isinstance(node, c_ast.IdentifierType):
        node.names = common.CanonicalizeIdentifierType(node.names)
    for c in node:
        CanonicalizeIdentifierTypes(c)


def CanonicalScalarType(node):
    if not isinstance(node, c_ast.IdentifierType): return None
    return type_tab.CanonicalizeIdentifierType(node.names)


def MakeCast(canonical_scalar_type, node):
    # print("ADD CAST")
    it = c_ast.IdentifierType(list(canonical_scalar_type))
    return c_ast.Cast(c_ast.Typename(None, [], c_ast.TypeDecl(None, [], it)), node)


# def AddExplicitCasts(node: c_ast.Node, ttab, parent: c_ast.Node):
#     for c in node:
#         AddExplicitCasts(c, ttab, node)
#
#     if isinstance(node, c_ast.BinaryOp):
#
#         if node.op in common.SHORT_CIRCUIT_OPS:
#             pass
#         else:
#             tl = ttab[node.left]
#             tr = ttab[node.right]
#             if isinstance(tl, c_ast.IdentifierType) and isinstance(tr, c_ast.IdentifierType):
#             m = common.MaxType(node, tl, tr)
#             #if tl !=
#
#
#         if left != p:
#             node.left = MakeCast(p, node.left)
#         if right != p:
#             node.right = MakeCast(p, node.right)
#
#     elif isinstance(node, c_ast.Assignment):
#         p = CanonicalScalarType(ttab[node])
#         if not p: return
#         right = CanonicalScalarType(ttab[node.rvalue])
#         if right != p:
#             node.rvalue = MakeCast(p, node.rvalue)
#
#     elif isinstance(node, c_ast.FuncCall):
#         pass

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


def DoPrintfSplitter(call, parent, meta):
    args = call.args.exprs
    fmt_pieces = printf_transform.TokenizeFormatString(args[0].value[1:-1])
    if not fmt_pieces: return
    if len(fmt_pieces) == 1: return

    stmts = GetStatementList(parent)
    if not stmts:
        assert False, parent
        return

    calls = []
    args = args[1:]  # skip the format string
    for f in fmt_pieces:
        arg = None
        if f[0] == '%' and len(f) > 1:
            arg = args.pop(0)
        c = MakePrintfCall(f, arg)
        meta.type_links[c] = meta.type_links[call]
        meta.type_links[c.args] = meta.type_links[call.args]
        meta.type_links[c.args.exprs[0]] = meta.type_links[call.args.exprs[0]]
        meta.type_links[c.name] = meta.type_links[call.name]
        meta.sym_links[c.name] = meta.sym_links[call.name]
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

CONST_ZERO = c_ast.Constant("int", 0)


def IsNodeRequiringBoolInt(node: c_ast, _):
    return (isinstance(node, c_ast.If) or
            isinstance(node, c_ast.For) or
            isinstance(node, c_ast.BinaryOp) and node.op in common.SHORT_CIRCUIT_OPS or
            isinstance(node, c_ast.UnaryOp) and node.op == "!")


def IsExprOfTypeBoolInt(node: c_ast):
    return (isinstance(node, c_ast.BinaryOp) and node.op in common.BOOL_INT_TYPE_BINARY_OPS or
            isinstance(node, c_ast.UnaryOp) and node.op in common.BOOL_INT_TYPE_UNARY_OPS)


def FixNodeRequiringBoolInt(ast: c_ast.Node):
    candidates = FindMatchingNodesPostOrder(ast, ast, IsNodeRequiringBoolInt)
    for node, parent in candidates:
        if isinstance(node, c_ast.If):
            if not IsExprOfTypeBoolInt(node.cond):
                node.cond = c_ast.BinaryOp("!=", node.cond, CONST_ZERO)
        elif isinstance(node, c_ast.For):
            if not IsExprOfTypeBoolInt(node.cond):
                node.cond = c_ast.BinaryOp("!=", node.cond, CONST_ZERO)
        elif node.op == "!":
            if not IsExprOfTypeBoolInt(node.expr):
                node = c_ast.BinaryOp("==", node.expr, CONST_ZERO)  # note: we are replacing the "!" node

        elif node.op in common.SHORT_CIRCUIT_OPS:
            if not IsExprOfTypeBoolInt(node.left):
                node.left = c_ast.BinaryOp("!=", node.left, CONST_ZERO)
            if not IsExprOfTypeBoolInt(node.right):
                node.right = c_ast.BinaryOp("!=", node.right, CONST_ZERO)


def main(argv):
    filename = argv[0]
    ast = parse_file(filename, use_cpp=True)
    meta_info = meta.MetaInfo(ast)

    ConvertPostToPreIncDec(ast)
    RemoveVoidParam(ast)
    CanonicalizeIdentifierTypes(ast)
    meta_info.CheckConsistency(ast)

    PrintfSplitter(ast, meta_info)
    meta_info.CheckConsistency(ast)

# AddExplicitCasts(ast, ttab.links, ast)
    FixNodeRequiringBoolInt(ast)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
