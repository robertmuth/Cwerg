#!/usr/bin/python3

"""
 Canonicalize the C source:

 * remove void parameter lists: foo(void) -> foo()
 * insert all implicit casts

"""

import sys
from typing import Optional

import sym_tab
import type_tab
from pycparser import c_ast, parse_file, c_generator


def IsVoidArg(node):
    if not isinstance(node, c_ast.Typename): return False
    if not isinstance(node.type, c_ast.TypeDecl): return False
    type = node.type.type
    if not isinstance(type, c_ast.IdentifierType): return False
    names = type.names
    return len(names) == 1 and names[0] == "void"


def RemoveVoidParam(node: c_ast.Node, parent: Optional[c_ast.Node]):
    if isinstance(node, c_ast.ParamList) and len(node.params) == 1:
        if IsVoidArg(node.params[0]):
            node.params = []
    for c in node:
        RemoveVoidParam(c, node)


def CanonicalizeIdentifierTypes(node: c_ast.Node):
    if isinstance(node, c_ast.IdentifierType):
        node.names = type_tab.CanonicalizeIdentifierType(node.names)
    for c in node:
        CanonicalizeIdentifierTypes(c)


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

    RemoveVoidParam(ast, None)
    CanonicalizeIdentifierTypes(ast)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
