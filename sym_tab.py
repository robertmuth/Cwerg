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

"""

import logging
from pycparser import c_ast, parse_file


def IsGlobalSym(decl, parent):
    return (isinstance(parent, c_ast.FuncDef) or
            isinstance(parent, c_ast.FileAST) or
            "extern" in decl.storage)


UNRESOLVED_STRUCT_UNION_MEMBER = "@UNRESOLVED@"

_ALLOWED_SYMBOL_LINKS = (c_ast.Decl, c_ast.Struct, c_ast.Union, str)

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
        assert isinstance(decl, _ALLOWED_SYMBOL_LINKS)
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


def VerifySymbolLinks(node: c_ast.Node, symbol_links):
    if isinstance(node, c_ast.ID):
        decl = symbol_links[node]
        assert isinstance(decl, _ALLOWED_SYMBOL_LINKS)
        # print ("ID", node.name, decl.type.__class__.__name__)
        return

    for c in node:
        VerifySymbolLinks(c, symbol_links)


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

    for c in node:
        VerifyStructLinks(c, struct_links)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)

    def process(fn):
        ast = parse_file(fn, use_cpp=True)
        sym_tab = ExtractSymTab(ast)
        print("GLOBALS SYMS")
        print(sym_tab.global_syms.keys())
        print("VERIFY SYMS")
        VerifySymbolLinks(ast, sym_tab.links)

        su_tab = ExtractStructUnionTab(ast)
        print("GLOBALS SU")
        print(su_tab.global_syms.keys())
        print("VERIFY SU")
        VerifyStructLinks(ast, su_tab.links)

    for fn in sys.argv[1:]:
        print("processing ", fn)
        process(fn)
