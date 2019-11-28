#!/usr/bin/python3

"""
This module provides conceptual symbol table support for pycparser.
Currently this mostly results in additional cross links in the AST that
link IDs to their definition.

Essentially we are creating a symbol table on the fly,
performing all the lookups and recording the results.
It is not clear yet if this fairly static approach works for all the corner
cases of the C language.

The following cross links are created:

c_ast.ID's associated with variables are linked to the declaration of the variable
(c_ast.Decl)

c_ast.ID's associated with field names of structs/unions are not linked
as we cannot resolve them until we have type information.

Just like the sym_tab module cross links symbols with their definition,
type_tab links expressions with the corresponding TypeDecls.
Along the way it fills in the missing symbol links we could
not resolve in sym_tab

By far the biggest complication results from StructRef
which require both symbol and type links.
"""

import logging
from typing import Optional

from pycparser import c_ast, parse_file

import common


__all__ = ["MetaInfo"]

def IsGlobalSym(decl, parent):
    return (isinstance(parent, c_ast.FuncDef) or
            isinstance(parent, c_ast.FileAST) or
            "extern" in decl.storage)


UNRESOLVED_STRUCT_UNION_MEMBER = "@UNRESOLVED@"

_ALLOWED_SYMBOL_LINKS = (c_ast.Decl, c_ast.Struct, c_ast.Union)

_STRUCT_OR_UNION = (c_ast.Struct, c_ast.Union)


class SymTab:

    def __init__(self):
        # we currently lump vars and funs together, this may not be quite right
        self.global_syms = {}
        self.local_syms = []
        #
        self.links = {}

    def push_scope(self):
        self.local_syms.append({})

    def pop_scope(self):
        self.local_syms.pop(-1)

    def add_symbol(self, decl, is_global: bool):
        assert isinstance(decl, (c_ast.Decl, c_ast.Struct, c_ast.Union))
        if is_global:
            self.global_syms[decl.name] = decl
        else:
            self.local_syms[-1][decl.name] = decl

    def find_symbol(self, name):
        for l in reversed(self.local_syms):
            s = l.get(name)
            if s:
                return s
        s = self.global_syms.get(name)
        if s:
            return s
        assert False, "symbol not found: %s" % name

    def add_link(self, id: c_ast.ID, decl: c_ast.Node):
        assert isinstance(id, (c_ast.ID, c_ast.Struct, c_ast.Union))
        assert decl is UNRESOLVED_STRUCT_UNION_MEMBER or isinstance(decl, _ALLOWED_SYMBOL_LINKS)
        self.links[id] = decl


def _IsNewScope(node):
    return isinstance(node, (c_ast.Compound,
                             c_ast.For,
                             c_ast.While,
                             c_ast.DoWhile,
                             c_ast.FuncDef))


_DECL_TYPES = (c_ast.Struct, c_ast.Union, c_ast.ArrayDecl,
               c_ast.PtrDecl, c_ast.TypeDecl, c_ast.FuncDecl)


def _ProcessDecls(node, sym_tab, parent):
    type = node.type
    assert isinstance(type, _DECL_TYPES)
    if isinstance(type, (c_ast.Struct, c_ast.Union)):
        assert node.name is None
        return

    assert node.name is not None
    if node.init:
        _PopulateSymTab(node.init, sym_tab, node)
    logging.info("Var %s %s %s %s", node.name, node.storage,
                 node.quals, node.type.__class__.__name__)
    sym_tab.add_symbol(node, IsGlobalSym(node, parent))

    if isinstance(node.type, c_ast.FuncDecl) and isinstance(parent, c_ast.FuncDef):
        # add params as local symbols
        params = node.type.args
        if params:
            assert isinstance(params, c_ast.ParamList)
            for p in params:
                logging.info("Param %s %s", p.name, p.type.__class__.__name__)
                if isinstance(p, c_ast.Typename):
                    assert p.type.type.names[0] == "void"
                else:
                    assert isinstance(p, c_ast.Decl)
                    sym_tab.add_symbol(p, False)


def _PopulateSymTab(node, sym_tab, parent):
    if _IsNewScope(node):
        sym_tab.push_scope()

    if isinstance(node, c_ast.FuncDef):
        logging.info("\nFUNCTION [%s]" % node.decl.name)

    if isinstance(node, c_ast.Decl):
        _ProcessDecls(node, sym_tab, parent)
        return

    if isinstance(node, c_ast.ID):
        if isinstance(parent, c_ast.StructRef) and parent.field == node:
            sym_tab.add_link(node, UNRESOLVED_STRUCT_UNION_MEMBER)
        else:
            sym = sym_tab.find_symbol(node.name)
            logging.info("LINK ID %d %s [%s]", id(node), id(sym), node.name)

            sym_tab.add_link(node, sym)
        return

    for c in node:
        _PopulateSymTab(c, sym_tab, node)

    if _IsNewScope(node):
        sym_tab.pop_scope()


def ExtractSymTab(ast: c_ast.FileAST):
    sym_tab = SymTab()
    _PopulateSymTab(ast, sym_tab, None)
    return sym_tab


def VerifySymbolLinks(node: c_ast.Node, symbol_links, strict=True):
    if isinstance(node, c_ast.ID):
        decl = symbol_links[node]
        if not strict and decl is UNRESOLVED_STRUCT_UNION_MEMBER:
            return
        assert isinstance(decl, _ALLOWED_SYMBOL_LINKS), decl
        # print ("ID", node.name, decl.type.__class__.__name__)
        return

    for c in node:
        VerifySymbolLinks(c, symbol_links, strict)


def _PopulateStructUnionTab(node: c_ast.Node, sym_tab, top_level):
    if _IsNewScope(node):
        sym_tab.push_scope()

    if isinstance(node, _STRUCT_OR_UNION):
        if node.decls:
            logging.info("Struct %s #members %s", node.name, len(node.decls))
            sym_tab.add_symbol(node, top_level)
            # avoid special casing later
            sym_tab.add_link(node, node)
        else:
            sym = sym_tab.find_symbol(node.name)
            assert sym
            logging.info("LINK STRUCT ID %s %s %s", id(node), id(sym), node.name)
            sym_tab.add_link(node, sym)

    if isinstance(node, c_ast.FuncDef):
        top_level = False
    for c in node:
        _PopulateStructUnionTab(c, sym_tab, top_level)

    if _IsNewScope(node):
        sym_tab.pop_scope()


def ExtractStructUnionTab(ast: c_ast.FileAST):
    sym_tab = SymTab()
    _PopulateStructUnionTab(ast, sym_tab, True)
    return sym_tab


def VerifyStructLinks(node: c_ast.Node, struct_links):
    if isinstance(node, _STRUCT_OR_UNION):
        decl = struct_links[node]
        assert decl.decls
        assert isinstance(decl, _STRUCT_OR_UNION)
        # print ("ID", node.name, decl.type.__class__.__name__)
        return


_ALLOWED_TYPE_LINKS = (c_ast.ParamList,   # for ExpressionList which are function arguments
                       c_ast.TypeDecl,
                       c_ast.ArrayDecl,
                       c_ast.PtrDecl,
                       c_ast.IdentifierType,
                       c_ast.Struct,
                       c_ast.Union)


class TypeTab:
    """class for keeping track of per node type info """

    def __init__(self):
        self.links = {}

    def link_expr(self, node, type):
        assert isinstance(node, common.EXPRESSION_NODES), "unexpected type: [%s]" % type
        # TODO: add missing classes as needed
        assert isinstance(type, _ALLOWED_TYPE_LINKS), "unexpected type %s" % type
        self.links[node] = type


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


SIZE_T_IDENTIFIER_TYPE = c_ast.IdentifierType(["int", "unsigned"])

INT_IDENTIFIER_TYPE = c_ast.IdentifierType(["int"])


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
    elif isinstance(decl, c_ast.ParamList):
        return [TypePrettyPrint(x.type if isinstance(x, (c_ast.Decl, c_ast.Typename)) else x) for x in decl.params]
    elif isinstance(decl, c_ast.Struct):
        return "struct %s" % decl.name
    elif isinstance(decl, c_ast.Union):
        return "union %s" % decl.name
    elif isinstance(decl, c_ast.ArrayDecl):
        return "array-decl"
    elif isinstance(decl, c_ast.PtrDecl):
        return "ptr-decl"
    else:
        assert False, "unexpected %s" % decl


def GetBinopType(node, t1, t2):
    if node.op in common.BOOL_INT_TYPE_BINARY_OPS:
        return INT_IDENTIFIER_TYPE

    if node.op not in common.SAME_TYPE_BINARY_OPS:
        assert False, node

    return common.MaxType(node, t1, t2)


def MakePtrType(t):
    # add missing ones as needed
    if isinstance(t, c_ast.IdentifierType):
        return c_ast.PtrDecl([], c_ast.TypeDecl(None, [], t))
    elif isinstance(t, c_ast.PtrDecl):
        return c_ast.PtrDecl([], t)
    else:
        assert False, t


def GetUnaryType(node, t):
    if node.op == "sizeof":
        # really size_t
        return SIZE_T_IDENTIFIER_TYPE
    elif node.op in common.BOOL_INT_TYPE_UNARY_OPS:
        return INT_IDENTIFIER_TYPE
    elif node.op == "&":
        return MakePtrType(t)
    elif node.op == "*":
        assert isinstance(t, c_ast.PtrDecl)
        return GetTypeForDecl(t.type)
    elif node.op in common.SAME_TYPE_UNARY_OPS:
        return t
    else:
        assert False, node

    return t


def _FindStructMember(struct, field):
    for member in struct.decls:
        if member.name == field.name:
            return member
    assert False, "cannot field %s in struct %s" % (field, struct)


def _GetFieldRefTypeAndUpdateSymbolLink(node: c_ast.StructRef, sym_links, struct_links, type_tab):
    assert isinstance(node, c_ast.StructRef)
    # Note: we assume here that the node.name side of the AST has already been processed
    struct = type_tab.links[node.name]
    if isinstance(struct, c_ast.TypeDecl):
        struct = struct.type
    assert isinstance(struct, (c_ast.Struct, c_ast.Union)), struct
    struct = struct_links[struct]

    field = node.field
    # print ("@@ STRUCT FIELD @@", field)
    assert isinstance(field, c_ast.ID)
    assert sym_links[field] == UNRESOLVED_STRUCT_UNION_MEMBER
    member = _FindStructMember(struct, field)
    logging.info("STRUCT_DEREF base %s (%s) field %s (%s)",
                 common.NodePrettyPrint(node.name), TypePrettyPrint(struct),
                 common.NodePrettyPrint(field), TypePrettyPrint(GetTypeForDecl(member.type)))

    sym_links[field] = member
    return GetTypeForDecl(member.type)


def TypeForNode(node, parent, sym_links, struct_links, type_tab, child_types, fundef):
    if isinstance(node, c_ast.Constant):
        return c_ast.IdentifierType(node.type.split())
    elif isinstance(node, c_ast.ID):
        if isinstance(parent, c_ast.StructRef) and parent.field == node:
            return _GetFieldRefTypeAndUpdateSymbolLink(parent, sym_links, struct_links, type_tab)
        else:
            decl = sym_links[node].type
            return GetTypeForDecl(decl)
    elif isinstance(node, c_ast.BinaryOp):
        return GetBinopType(node, child_types[0], child_types[1])
    elif isinstance(node, c_ast.UnaryOp):
        return GetUnaryType(node, child_types[0])
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
        # unfortunately ExprList have multiple uses which we need to disambiguate
        if isinstance(parent, c_ast.FuncCall):
            args = sym_links[parent.name].type.args
            assert isinstance(args, c_ast.ParamList)
            return args
        else:
            return child_types[-1]
    elif isinstance(node, c_ast.TernaryOp):
        return common.MaxType(node, child_types[1], child_types[2])
    elif isinstance(node, c_ast.StructRef):
        # This was computed by _GetFieldRefTypeAndUpdateSymbolLink
        return child_types[1]
    elif isinstance(node, c_ast.Cast):
        return GetTypeForDecl(node.to_type.type)
    else:
        assert False, "unsupported expression node %s" % node


def Typify(node: c_ast.Node, parent: Optional[c_ast.Node], type_tab, sym_links, struct_links,
           fundef: Optional[c_ast.FuncDef]):
    """Determine the type of all expression  nodes and record it in type_tab"""
    if isinstance(node, c_ast.FuncDef):
        logging.info("\nFUNCTION [%s]", node.decl.name)
        fundef = node

    child_types = [Typify(c, node, type_tab, sym_links, struct_links, fundef) for c in node]
    # print("@@@@", [TypePrettyPrint(x) for x in child_types])
    if not isinstance(node, common.EXPRESSION_NODES):
        return None

    t = TypeForNode(node, parent, sym_links, struct_links, type_tab, child_types, fundef)

    logging.info("%s %s %s", common.NodePrettyPrint(node), TypePrettyPrint(t),
                 [TypePrettyPrint(x) for x in child_types])
    type_tab.link_expr(node, t)
    return t


def VerifyTypeLinks(node: c_ast.Node, type_links):
    """This checks what the typing module is trying to accomplish"""
    if isinstance(node, common.EXPRESSION_NODES):
        type = type_links.get(node)
        assert type is not None, node
        isinstance(type, _ALLOWED_TYPE_LINKS)
    for c in node:
        VerifyTypeLinks(c, type_links)


class MetaInfo:
    """Represents Symbol and Type information for the  AST

    This information is maintained as links between c_ast.Node
    either using existing AST nodes or new ones
    """

    def __init__(self, ast: c_ast.FileAST):
        stab = ExtractSymTab(ast)
        VerifySymbolLinks(ast, stab.links, strict=False)
        su_tab = ExtractStructUnionTab(ast)
        VerifyStructLinks(ast, su_tab.links)

        type_tab = TypeTab()
        Typify(ast, None, type_tab, stab.links, su_tab.links, None)
        VerifyTypeLinks(ast, type_tab.links)
        VerifySymbolLinks(ast, stab.links, strict=True)

        self.sym_links = stab.links
        self.struct_links = su_tab.links
        self.type_links = type_tab.links

    def GetDecl(self, sym: c_ast.Node):
        return self.sym_links[sym]

    def GetType(self, expr: c_ast.Node):
        return self.type_links[expr]

    def CheckConsistency(self, ast: c_ast.Node):
        VerifySymbolLinks(ast, self.sym_links)
        VerifyStructLinks(ast, self.struct_links)
        VerifyTypeLinks(ast, self.type_links)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)


    def process(filename):
        ast = parse_file(filename, use_cpp=True)
        meta_info = MetaInfo(ast)


    for filename in sys.argv[1:]:
        print("=" * 60)
        print(filename)
        print("=" * 60)
        process(filename)
