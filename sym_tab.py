#!/usr/bin/python3


"""
This module provides conceptual symbol table support for pycparser.
Currently this mostly results in additional links within the AST that
link IDs to their definition. So it is more like creating a symbols
and then doing all the lookups and recording the results.


Concretely:

c_ast.ID's asociated with variables are linked to the declaration of the variable
(c_ast.Decl)

c_ast.ID's associated with field names of structs/unions are not linked
as we cannot resolve them until we have type information.

"""

from pycparser import c_parser, c_ast, parse_file


def IsGlobalSym(decl, parent):
    return (isinstance(parent, c_ast.FuncDef) or
            isinstance(parent, c_ast.FileAST) or
            "extern" in decl.storage)


UNRESOLVED_STRUCT_UNION_MEMBER = "@UNRESOLVED@"


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

    def add_link(self, id, decl):
        assert isinstance(decl, (c_ast.Decl, c_ast.Struct, c_ast.Union, str))
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
    print("Var", node.name, node.storage,
           node.quals, node.type.__class__.__name__)
    sym_tab.add_symbol(node, IsGlobalSym(node, parent))

    if isinstance(node.type, c_ast.FuncDecl) and isinstance(parent,  c_ast.FuncDef):
        # add params as local symbols
        params = node.type.args
        if params:
            assert isinstance(params, c_ast.ParamList)
            for p in params:
                print("Param", p.name, p.type.__class__.__name__)
                if isinstance(p, c_ast.Typename):
                    assert p.type.type.names[0] == "void"
                else:
                    assert isinstance(p,  c_ast.Decl)
                    sym_tab.add_symbol(p, False)


def _PopulateSymTab(node, sym_tab, parent):
    if _IsNewScope(node):
        sym_tab.push_scope()

    if isinstance(node, c_ast.FuncDef):
        print("\nFUNCTION [%s]" % node.decl.name)

    if isinstance(node, c_ast.Decl):
        _ProcessDecls(node, sym_tab, parent)
        return

    if isinstance(node, c_ast.ID):
        if isinstance(parent, c_ast.StructRef) and parent.field == node:
            sym_tab.add_link(node, UNRESOLVED_STRUCT_UNION_MEMBER)
        else:
            sym = sym_tab.find_symbol(node.name)
            print("LINK ID", id(node), id(sym), node.name)

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


def _VerifySymtab(links,  node):
    if isinstance(node, c_ast.FuncDef):
        # print("FUNCTION [%s]" % node.decl.name)
        pass
    if isinstance(node, c_ast.ID):
        decl = links[node]
        # print ("ID", node.name, decl.type.__class__.__name__)
        return

    for c in node:
        _VerifySymtab(links, c)


def _PopulateStructUnionTab(node: c_ast.Node, sym_tab, top_level):
    if _IsNewScope(node):
        sym_tab.push_scope()

    if isinstance(node, (c_ast.Struct, c_ast.Union)):
        if node.decls:
            print("Struct", node.name, len(node.decls))
            sym_tab.add_symbol(node, top_level)
            # avoid special casing later
            sym_tab.add_link(node, node)
        else:
            sym = sym_tab.find_symbol(node.name)
            assert sym
            print("LINK STRUCT ID", id(node), id(sym), node.name)
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


if __name__ == "__main__":
    import sys

    def process(fn):
        ast = parse_file(fn, use_cpp=True)
        sym_tab = ExtractSymTab(ast)
        print("GLOBALS SYMS")
        print(sym_tab.global_syms.keys())
        print("VERIFY SYMS")
        _VerifySymtab(sym_tab.links, ast)

        su_tab = ExtractStructUnionTab(ast)
        print("GLOBALS SU")
        print(su_tab.global_syms.keys())

    for fn in sys.argv[1:]:
        print("processing ", fn)
        process(fn)
