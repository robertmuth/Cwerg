#!/usr/bin/python3

"""
 Canonicalize the C source:

 * remove void parameter lists: foo(void) -> foo()
 * insert all implicit casts

"""

import sys
from typing import Optional

from pycparser import c_ast, parse_file, c_generator

import printf_transform
import sym_tab
import type_tab


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


def CanonicalizeIdentifierTypes(node: c_ast.Node):
    if isinstance(node, c_ast.IdentifierType):
        node.names = type_tab.CanonicalizeIdentifierType(node.names)
    for c in node:
        CanonicalizeIdentifierTypes(c)


def CanonicalScalarType(node):
    if not isinstance(node, c_ast.IdentifierType): return None
    return type_tab.CanonicalizeIdentifierType(node.names)


def MakeCast(canonical_scalar_type, node):
    # print("ADD CAST")
    it = c_ast.IdentifierType(list(canonical_scalar_type))
    return c_ast.Cast(c_ast.Typename(None, [], c_ast.TypeDecl(None, [], it)), node)


def AddExplicitCasts(node: c_ast.Node, ttab, parent: c_ast.Node):
    for c in node:
        AddExplicitCasts(c, ttab, node)

    if isinstance(node, c_ast.BinaryOp):
        # Needs a ton of work
        p = CanonicalScalarType(ttab[node])
        if not p: return
        left = CanonicalScalarType(ttab[node.left])
        right = CanonicalScalarType(ttab[node.right])
        if left != p:
            node.left = MakeCast(p, node.left)
        if right != p:
            node.right = MakeCast(p, node.right)

    if isinstance(node, c_ast.Assignment):
        p = CanonicalScalarType(ttab[node])
        if not p: return
        right = CanonicalScalarType(ttab[node.rvalue])
        if right != p:
            node.rvalue = MakeCast(p, node.rvalue)


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
        #return None
        assert False, node


def MakePrintfCall(fmt_str, arg_node: Optional[c_ast.Node]):
    args = [c_ast.Constant("string", '"' + fmt_str + '"')]
    if arg_node: args.append(arg_node)
    return c_ast.FuncCall(c_ast.ID("printf"), c_ast.ExprList(args))


def FindMatchingNodes(node: c_ast.Node, parent: c_ast.Node, matcher):
    res = []
    for c in node:
        res += FindMatchingNodes(c, node, matcher)
    if matcher(node, parent):
        res.append((node, parent))
    return res


def DoPrintfSplitter(call, parent):
    args = call.args.exprs
    fmt_pieces = printf_transform.TokenizeFormatString(args[0].value[1:-1])
    if not fmt_pieces: return
    if len(fmt_pieces) == 1: return

    stmts = GetStatementList(parent)
    if not stmts: return

    calls = []
    args = args[1:]  # skip the format string
    for f in fmt_pieces:
        arg = None
        if f[0] == '%' and len(f) > 1:
            arg = args.pop(0)
        calls.append(MakePrintfCall(f, arg))
    pos = stmts.index(call)
    stmts[pos:pos+1] = calls


def PrintfSplitter(ast: c_ast.Node):
    candidates = FindMatchingNodes(ast, ast, IsSuitablePrintf)

    for call, parent in candidates:
        DoPrintfSplitter(call, parent)


def main(argv):
    filename = argv[0]
    ast = parse_file(filename, use_cpp=True)
    stab = sym_tab.ExtractSymTab(ast)
    su_tab = sym_tab.ExtractStructUnionTab(ast)
    sym_links = {}
    sym_links.update(stab.links)
    sym_links.update(su_tab.links)

    ttab = type_tab.TypeTab()
    type_tab.Typify(ast, None, ttab, sym_links, None)

    RemoveVoidParam(ast)
    CanonicalizeIdentifierTypes(ast)
    # AddExplicitCasts(ast, ttab.links, ast)
    CanonicalizeIdentifierTypes(ast)
    PrintfSplitter(ast)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
