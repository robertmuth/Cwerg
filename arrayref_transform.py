from pycparser import c_ast
from typing import List, Tuple

import common

__all__ = ["ConvertArrayIndexToPointerDereference"]


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
        # print (node)
        # print (meta_info.type_links[node])
        # print (node.subscript)
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
        meta_info.type_links[s] = meta_info.type_links[x]
    return node, s


def ConvertArrayIndexToPointerDereference(ast, meta_info):
    def IsArrayRefChain(node, parent):
        # this may need some extra checks to ensure the chain is for the  same type
        return isinstance(node, c_ast.ArrayRef) and not isinstance(parent, c_ast.ArrayRef)

    candidates: List[Tuple[c_ast.ArrayRef, c_ast.Node]] = common.FindMatchingNodesPreOrder(ast, ast, IsArrayRefChain)

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

    candidates: List[Tuple[c_ast.ArrayDecl, c_ast.Node]] = common.FindMatchingNodesPreOrder(ast, ast, IsArrayDeclChain)
    for node, parent in candidates:
        pass
