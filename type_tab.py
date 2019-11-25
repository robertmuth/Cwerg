#!/usr/bin/python3

"""
Just like the sym_tab module cross links symbols with their definition,
type_tab links expressions with the corresponding TypeDecls.
Along the way it fills in the missing symbol links we could
not resolve in sym_tab

By far the biggest complication results from StructRef
which require both symbol and type links.
"""

import logging
from typing import Optional

import sym_tab
from pycparser import c_ast, parse_file

_ALLOWED_TYPE_LINKS = (list,
                       c_ast.TypeDecl,
                       c_ast.ArrayDecl,
                       c_ast.PtrDecl,
                       c_ast.IdentifierType,
                       c_ast.Struct,
                       c_ast.Union)

_EXPRESSION_CLASSES = (c_ast.ArrayRef,
                       c_ast.Assignment,
                       c_ast.BinaryOp,
                       c_ast.Cast,
                       c_ast.Constant,
                       c_ast.ExprList,
                       c_ast.FuncCall,
                       c_ast.ID,
                       c_ast.Return,
                       c_ast.StructRef,
                       c_ast.TernaryOp,
                       c_ast.UnaryOp)


class TypeTab:
    """Classs for keeping track of types """

    def __init__(self):
        self.links = {}

    def link_expr(self, node, type):
        assert isinstance(node, _EXPRESSION_CLASSES), "unexpected type: [%s]" % type
        # TODO: add missing classes as needed
        assert isinstance(type, _ALLOWED_TYPE_LINKS), "unexpected type %s" % type
        self.links[node] = type


def IsExpression(node):
    return isinstance(node, _EXPRESSION_CLASSES)


def GetTypeForDecl(decl: c_ast.Node):
    if isinstance(decl, c_ast.IdentifierType):
        return decl
    elif isinstance(decl, c_ast.TypeDecl):
        # for simple decl extract the type
        assert isinstance(decl.type, (c_ast.IdentifierType, c_ast.Struct, c_ast.Union))
        return decl.type
    elif isinstance(decl, c_ast.FuncDecl):
        # for function get the return type
        return GetTypeForDecl(decl.type)
    elif isinstance(decl, (c_ast.ArrayDecl, c_ast.PtrDecl)):
        # for the rest do nothing
        return decl
    else:
        assert False, decl


def GetTypeForFunArg(arg: c_ast.Node):
    if isinstance(arg, c_ast.Decl):
        return arg.type
    elif isinstance(arg, c_ast.Typename):
        return arg.type
    elif isinstance(arg, c_ast.EllipsisParam):
        return arg
    else:
        assert False, arg


SIZE_T_IDENTIFIER_TYPE = c_ast.IdentifierType(["unsigned"])


def IdentifierTypeToString(node: c_ast.IdentifierType):
    return "-".join(node.names)


def NodePrettyPrint(node):
    if node is None:
        return "none"
    elif isinstance(node, c_ast.ID):
        return "id[%s]" % node.name
    elif isinstance(node, c_ast.BinaryOp):
        return "op[%s]" % node.op
    elif isinstance(node, c_ast.UnaryOp):
        return "op[%s]" % node.op
    else:
        return node.__class__.__name__


def TypePrettyPrint(decl):
    if decl is None:
        return "none"
    elif isinstance(decl, str):
        return decl
    elif isinstance(decl, c_ast.TypeDecl):
        return TypePrettyPrint(decl.type)
    elif isinstance(decl, c_ast.EllipsisParam):
        return "..."
    elif isinstance(decl, c_ast.IdentifierType):
        return "-".join(decl.names)
    elif isinstance(decl, list):
        return [TypePrettyPrint(x) for x in decl]
    elif isinstance(decl, c_ast.Struct):
        return "struct " + decl.name
    elif isinstance(decl, c_ast.ArrayDecl):
        return "array-decl"
    elif isinstance(decl, c_ast.PtrDecl):
        return "ptr-decl"
    else:
        assert False, "unexpected %s" % decl


# This needs a lot more work and may be too simplistic
# But note that the standard dictates: signed x unsigned -> unsigned
# (citation needed)
_NUM_TYPE_ORDER = [
    "signed-char", "char", "unsigned-char",
    "int-short", "signed-short", "short", "unsigned-short",
    "signed-int", "signed", "int", "unsigned-int", "unsigned",
    "long",
    "long-long-int", "long-long",
    "float", "double"
]


def GetBinopType(node, t1, t2):
    # note: type of && || is always "int"
    if isinstance(t1, c_ast.IdentifierType) and isinstance(t2, c_ast.IdentifierType):
        n1 = IdentifierTypeToString(t1)
        n2 = IdentifierTypeToString(t2)
        if n1 == n2:
            return t1

        if n1 in _NUM_TYPE_ORDER and n2 in _NUM_TYPE_ORDER:
            i1 = _NUM_TYPE_ORDER.index(n1)
            i2 = _NUM_TYPE_ORDER.index(n2)
            return t2 if i1 < i2 else t1
        assert False, "incomparable types: %s %s" % (n1, n2)

    print("T1", t1)
    print("T2", t2)
    assert False, node


def _FindStructMember(struct, field):
    for member in struct.decls:
        if member.name == field.name:
            return member
    assert False, "cannot field %s in struct %s" % (field, struct)


def _GetFieldRefTypeAndUpdateSymbolLink(node: c_ast.StructRef, sym_links, type_tab):
    assert isinstance(node, c_ast.StructRef)
    # Note: we assume here that the node.name side of the AST has already been processed
    struct = type_tab.links[node.name]
    if isinstance(struct, c_ast.TypeDecl):
        struct = struct.type
    assert isinstance(struct, (c_ast.Struct, c_ast.Union)), struct
    struct = sym_links[struct]

    field = node.field
    # print ("@@ STRUCT FIELD @@", field)
    assert isinstance(field, c_ast.ID)
    assert sym_links[field] == sym_tab.UNRESOLVED_STRUCT_UNION_MEMBER
    member = _FindStructMember(struct, field)
    logging.info("STRUCT_DEREF base %s (%s) field %s (%s)",
                 NodePrettyPrint(node.name), TypePrettyPrint(struct),
                 NodePrettyPrint(field), TypePrettyPrint(GetTypeForDecl(member.type)))

    sym_links[field] = member
    return GetTypeForDecl(member.type)


def TypeForNode(node, parent, sym_links, type_tab, child_types, fundef):
    if isinstance(node, c_ast.Constant):
        return c_ast.IdentifierType(node.type.split())
    elif isinstance(node, c_ast.ID):
        if isinstance(parent, c_ast.StructRef) and parent.field == node:
            return _GetFieldRefTypeAndUpdateSymbolLink(parent, sym_links, type_tab)
        else:
            decl = sym_links[node].type
            return GetTypeForDecl(decl)
    elif isinstance(node, c_ast.BinaryOp):
        return GetBinopType(node, child_types[0], child_types[1])
    elif isinstance(node, c_ast.UnaryOp):
        if node.op == "sizeof":
            # really size_t
            return SIZE_T_IDENTIFIER_TYPE
        return child_types[0]
    elif isinstance(node, c_ast.FuncCall):
        return child_types[0]
    elif isinstance(node, c_ast.ArrayRef):
        a = child_types[0]
        assert isinstance(a, (c_ast.ArrayDecl, c_ast.PtrDecl)
                          ), a.__class__.__name__
        # TODO: check that child_types[1] is integer
        return GetTypeForDecl(a.type)
    elif isinstance(node, c_ast.Return):
        return fundef.decl.type.type
    elif isinstance(node, c_ast.Assignment):
        return child_types[0]
    elif isinstance(node, c_ast.ExprList):
        # unfortunately ExprList have mutliple uses which we need to disambiguate
        if isinstance(parent, c_ast.FuncCall):
            args = sym_links[parent.name].type.args
            assert isinstance(args, c_ast.ParamList)
            return [GetTypeForFunArg(x) for x in args.params]
        else:
            return child_types[-1]
    elif isinstance(node, c_ast.TernaryOp):
        return GetBinopType(node, child_types[1], child_types[2])
    elif isinstance(node, c_ast.StructRef):
        # This was computed by _GetFieldRefTypeAndUpdateSymbolLink
        return child_types[1]
    elif isinstance(node, c_ast.Cast):
        return GetTypeForDecl(node.to_type.type)
    else:
        assert False, "unsupported expression node %s" % node


def Typify(node: c_ast.Node, parent: Optional[c_ast.Node], type_tab, sym_links, fundef: Optional[c_ast.FuncDef]):
    """Determine the type of all expression  nodes and record it in type_tab"""
    if isinstance(node, c_ast.FuncDef):
        logging.info("\nFUNCTION [%s]", node.decl.name)
        fundef = node

    child_types = [Typify(c, node, type_tab, sym_links, fundef) for c in node]
    # print("@@@@", [TypePrettyPrint(x) for x in child_types])
    if not IsExpression(node):
        return None

    t = TypeForNode(node, parent, sym_links, type_tab, child_types, fundef)

    logging.info("%s %s %s", NodePrettyPrint(node), TypePrettyPrint(t), [TypePrettyPrint(x) for x in child_types])
    type_tab.link_expr(node, t)
    return t


def VerifyTypeLinks(node: c_ast.Node, type_links):
    """This checks what the typing module is trying to accomplish"""
    if IsExpression(node):
        type = type_links.get(node)
        assert type is not None
        isinstance(type, _ALLOWED_TYPE_LINKS)
    for c in node:
        VerifyTypeLinks(c, type_links)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)


    def process(filename):
        ast = parse_file(filename, use_cpp=True)
        stab = sym_tab.ExtractSymTab(ast)
        su_tab = sym_tab.ExtractStructUnionTab(ast)
        sym_links = {}
        sym_links.update(stab.links)
        sym_links.update(su_tab.links)

        type_tab = TypeTab()
        Typify(ast, None, type_tab, sym_links, None)
        VerifyTypeLinks(ast, type_tab.links)


    for filename in sys.argv[1:]:
        print(filename)
        process(filename)
