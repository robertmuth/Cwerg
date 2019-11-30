#!/usr/bin/python3

"""
Non-functional translator from C to a non-existent IR

"""

import sys
from typing import Optional, List, Tuple

from pycparser import c_ast, parse_file, c_generator

import common
import meta
import canonicalize


def GetVarKind(node, parent):
    if isinstance(parent, c_ast.ParamList):
        return "param"
    elif isinstance(parent, c_ast.FileAST):
        return "\nglobal"
    elif isinstance(parent, c_ast.FuncDef):
        return "result"
    else:
        return "local"


def EmitIR(node_stack, meta_info):
    node = node_stack[-1]
    if isinstance(node, c_ast.FuncDef):
        print ("\nfunction definition", node.decl.name)
    elif isinstance(node, c_ast.Constant):
      if meta_info.type_links[node] is meta.STRING_IDENTIFIER_TYPE:
        print("string constant", node.value)
    elif isinstance(node, c_ast.Label):
        print("LABEL:", node.name)
    elif isinstance(node, c_ast.Goto):
        print("goto", node.name)
    elif isinstance(node, c_ast.Decl):
        parent = node_stack[-2]
        kind = GetVarKind(node, parent)
        print (kind, node.name, node.quals, node.storage)
    for c in node:
        node_stack.append(c)
        EmitIR(node_stack, meta_info)
        node_stack.pop(-1)
    if isinstance(node, c_ast.FuncDef):
        print ("end function definition", node.decl.name)


def main(argv):
    filename = argv[0]
    ast = parse_file(filename, use_cpp=True)
    meta_info = meta.MetaInfo(ast)
    canonicalize.Canonicalize(ast, meta_info)
    EmitIR([ast], meta_info)
    #generator = c_generator.CGenerator()
    #print(generator.visit(ast))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
