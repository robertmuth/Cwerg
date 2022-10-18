#!/usr/bin/python3

"""Symbol Table for Cwerg AST

"""

import dataclasses
import sys
import logging

from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


class Unresolved:
    def __init__(self):
        pass


MODULES = {}


class SymTab:

    def __init__(self):
        self._type_syms = {}
        self._const_syms = {}

        self._rec_syms = {}
        self._enum_syms = {}

        self._fun_syms = {}
        self._var_syms = {}

        self._local_var_syms = []
        #
        self._links = {}

    def _push_scope(self):
        self._local_var_syms.append({})

    def _pop_scope(self):
        self._local_var_syms.pop(-1)

    def _add_local_symbol(self, node):
        if isinstance(node, cwast.LOCAL_SYM_DEF_NODES):
            self._local_var_syms[-1][node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def _resolve_enum_item(self, components) -> Optional[cwast.EnumVal]:
        if len(components) != 2:
            return None
        node = self._enum_syms.get(components[0])
        assert isinstance(node, cwast.DefEnum)
        for item in node.items:
            if isinstance(item, cwast.EnumVal) and item.name == components[1]:
                return item
        return None

    def _resolve_rec_field(self, components) -> Optional[cwast.RecField]:
        if len(components) != 2:
            return None
        node = self._enum_syms.get(components[0])
        assert isinstance(node, cwast.DefRec)
        for item in node.fields:
            if isinstance(item, cwast.RecField) and item.name == components[1]:
                return item
        return None

    def resolve_sym(self, node: cwast.Id) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        logger.info("resolving %s", node)
        name = node.name
        components = name.split("/")
        if len(components) > 1:
            s = self._resolve_enum_item(components)
            if s:
                return s
            assert False

        for l in reversed(self._local_var_syms):
            s = l.get(name)
            if s:
                self._links[id(node)] = s
                return s
        for syms in (self._type_syms, self._const_syms, self._fun_syms,
                     self._rec_syms, self._enum_syms, self._var_syms):
            s = syms.get(name)
            if s:
                self._links[id(node)] = s
                return s
        return None

    def _add_link(self, id_node: cwast.Id, def_node):
        assert isinstance(id_node, (cwast.Id))
        assert isinstance(def_node,
                          cwast.GLOBAL_SYM_DEF_NODES +
                          cwast.LOCAL_SYM_DEF_NODES), f"unpexpected node: {def_node}"
        self._links[id(id_node)] = def_node

    def resolve_symbols_recursively(self, node):
        logger.info("UNSYMBOLIZE %s", type(node).__name__)
        if isinstance(node, cwast.DefVar):
            self._add_local_symbol(node)
        elif isinstance(node, cwast.Id):
            def_node = self.resolve_sym(node)
            if def_node:
                self._add_link(node, def_node)
                return
            else:
                logger.error(f"cannot resolve symbol {node}")
                exit(1)
        elif isinstance(node, cwast.SCOPING_NODES):
            logger.info("push scope for %s", type(node).__name__)
            self._push_scope()
            if isinstance(node, cwast.StmtFor):
                self._add_local_symbol(node)
            elif isinstance(node, cwast.DefFun):
                for p in node.params:
                    self._add_local_symbol(p)

        # recurse using a little bit of introspection
        for c in node.__class__.FIELDS:
            nfd = cwast.ALL_FIELDS_MAP[c]
            if nfd.kind is cwast.NFK.NODE:
                self.resolve_symbols_recursively(getattr(node, c))
            elif nfd.kind is cwast.NFK.LIST:
                if c in ("body_t", "body_f"):
                    logger.info("push scope for if blocks")
                    self._push_scope()
                for cc in getattr(node, c):
                    self.resolve_symbols_recursively(cc)
                if c in ("body_t", "body_f"):
                    logger.info("push scope for if blocks")
                    self._pop_scope()

        if isinstance(node, cwast.SCOPING_NODES):
            self._pop_scope()
            logger.info("pop scope for %s", type(node).__name__)

    def add_top_level_sym(self, node):
        logger.info("recording top level symbol [%s]", node.name)
        if isinstance(node, cwast.DefFun):
            assert node.name not in self._fun_syms
            self._fun_syms[node.name] = node
        elif isinstance(node, cwast.DefVar):
            assert node.name not in self._var_syms
            self._var_syms[node.name] = node
        elif isinstance(node, cwast.DefConst):
            assert node.name not in self._const_syms
            self._const_syms[node.name] = node
        elif isinstance(node, cwast.DefRec):
            assert node.name not in self._rec_syms
            self._rec_syms[node.name] = node
        elif isinstance(node, cwast.DefEnum):
            assert node.name not in self._enum_syms
            self._enum_syms[node.name] = node
        elif isinstance(node, cwast.DefType):
            assert node.name not in self._type_syms
            self._type_syms[node.name] = node
        else:
            assert False, f"unexpected node: {node}"

    def get_definition_for_symbol(self, node: cwast.Id):
        return self._links[id(node)]


def ExtractSymTab(asts: List) -> SymTab:
    global MODULES
    symtab = SymTab()
    for mod in asts:
        assert isinstance(mod, cwast.DefMod), mod
        logger.info("Processing %s", mod.name)
        MODULES[mod.name] = mod
        # pass 1: get all the top level symbols
        for node in mod.body_mod:
            if isinstance(node, cwast.Comment):
                pass
            else:
                symtab.add_top_level_sym(node)

        # pass 2:
        for node in mod.body_mod:
            if isinstance(node, cwast.Comment):
                continue
            logger.info("ExtractSymbolTable %s", node.name)
            if isinstance(node, cwast.DefVar):
                # we already registered the var in the previous step
                symtab.resolve_symbols_recursively(node.type)
                symtab.resolve_symbols_recursively(node.initial)
            else:
                symtab.resolve_symbols_recursively(node)
        #
        assert not symtab._local_var_syms
    return symtab


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = []
    try:
        while True:
            stream = cwast.ReadTokens(sys.stdin)
            t = next(stream)
            assert t == "("
            sexpr = cwast.ReadSExpr(stream)
            # print(sexpr)
            asts.append(sexpr)
    except StopIteration:
        pass
    symtab = ExtractSymTab(asts)
