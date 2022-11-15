#!/usr/bin/python3

"""Symbol Table for Cwerg AST

"""

import dataclasses
import sys
import logging
import collections
import heapq

from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)


class Unresolved:
    def __init__(self):
        pass


class SymTab:
    """Symbol Table"""

    def __init__(self):
        self._type_syms: Dict[str, cwast.DefType] = {}
        self._const_syms: Dict[str, cwast.DefConst] = {}

        self._rec_syms: Dict[str, cwast.DefRec] = {}
        self._enum_syms: Dict[str, cwast.DefEnum] = {}

        self._fun_syms: Dict[str, cwast.DefFun] = {}
        self._var_syms: Dict[str, cwast.DefVar] = {}
        self._mod_syms: Dict[str, cwast.DefMod] = {}

        self._local_var_syms: Dict[str, cwast.DefVar] = []
        #

    def _push_scope(self):
        self._local_var_syms.append({})

    def _pop_scope(self):
        self._local_var_syms.pop(-1)

    def _add_local_symbol(self, name, node):
        if isinstance(node, cwast.LOCAL_SYM_DEF_NODES):
            self._local_var_syms[-1][name] = node
        else:
            assert False, f"unexpected node: {node}"

    def _resolve_enum_item(self, node: cwast.DefEnum, components) -> cwast.EnumVal:
        assert len(components) == 1
        for item in node.items:
            if isinstance(item, cwast.EnumVal) and item.name == components[0]:
                return item
        assert False, f"unknown enum [{components[0]}] for [{node.name}]"

    def _resolve_rec_field(self, components) -> Optional[cwast.RecField]:
        if len(components) != 2:
            return None
        node = self._enum_syms.get(components[0])
        assert isinstance(node, cwast.DefRec)
        for item in node.fields:
            if isinstance(item, cwast.RecField) and item.name == components[1]:
                return item
        return None

    def resolve_sym(self, components: List[str], symtab_map, must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        logger.info("resolving %s", components)
        if len(components) > 1:
            s = self._enum_syms.get(components[0])
            if s:
                assert isinstance(s, cwast.DefEnum)
                if must_be_public:
                    assert s.pub, f"{components} must be public"
                return self._resolve_enum_item(s, components[1:])
            # TODO: pub check?
            s = self._mod_syms.get(components[0])
            if s:
                assert isinstance(s, cwast.DefMod), f"{s}"
                mod_symtab = symtab_map[s.name]
                return mod_symtab.resolve_sym(components[1:], symtab_map, True)
            assert False, f"could not resolve name {components}"

        for l in reversed(self._local_var_syms):
            s = l.get(components[0])
            if s:
                return s
        for syms in (self._type_syms, self._const_syms, self._fun_syms,
                     self._rec_syms, self._enum_syms, self._var_syms):
            s = syms.get(components[0])
            if s:
                if must_be_public:
                    assert s.pub, f"{components} must be public"
                return s
        return None

    def _add_link(self, id_node: cwast.Id, def_node):
        assert isinstance(id_node, cwast.Id)
        assert isinstance(def_node,
                          cwast.GLOBAL_SYM_DEF_NODES +
                          cwast.LOCAL_SYM_DEF_NODES), f"unpexpected node: {def_node}"
        id_node.x_symbol = def_node

    def resolve_symbols_recursively(self, node, mod_map, symtab_map):
        logger.info("UNSYMBOLIZE %s", type(node).__name__)
        if isinstance(node, cwast.DefVar):
            self._add_local_symbol(node.name, node)
        elif isinstance(node, cwast.Catch):
            self._add_local_symbol(node.name, node)
        elif isinstance(node, cwast.Try):
            # we do not want to add the local symbol yet.
            # Otherwise, we would make that symbol visible to `catch``
            pass
        elif isinstance(node, cwast.Id):
            def_node = self.resolve_sym(
                node.name.split("/"), symtab_map, False)
            if def_node:
                self._add_link(node, def_node)
                return
            else:
                logger.error(f"cannot resolve symbol {node}")
                exit(1)

        if cwast.NF.NEW_SCOPE in node.__class__.FLAGS:
            logger.info("push scope for %s", type(node).__name__)
            self._push_scope()
            if isinstance(node, cwast.StmtFor):
                self._add_local_symbol(node.name, node)
            elif isinstance(node, cwast.DefFun):
                for p in node.params:
                    self._add_local_symbol(p.name, p)

        # recurse using a little bit of introspection
        for c in node.__class__.FIELDS:
            nfd = cwast.ALL_FIELDS_MAP[c]
            if nfd.kind is cwast.NFK.NODE:
                self.resolve_symbols_recursively(
                    getattr(node, c), mod_map, symtab_map)
            elif nfd.kind is cwast.NFK.LIST:
                if c in ("body_t", "body_f"):
                    logger.info("push scope for if blocks")
                    self._push_scope()
                for cc in getattr(node, c):
                    self.resolve_symbols_recursively(cc, mod_map, symtab_map)
                if c in ("body_t", "body_f"):
                    logger.info("push scope for if blocks")
                    self._pop_scope()

        if cwast.NF.NEW_SCOPE in node.__class__.FLAGS:
            self._pop_scope()
            logger.info("pop scope for %s", type(node).__name__)
        if isinstance(node, cwast.Try):
            self._add_local_symbol(node.name, node)

    def add_top_level_sym(self, node, mod_map):
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
        elif isinstance(node, cwast.Import):
            name = node.alias if node.alias else node.name
            assert name not in self._mod_syms
            self._mod_syms[name] = mod_map[node.name]
        else:
            assert False, f"unexpected node: {node}"


def ExtractSymTab(mod, mod_map, symtab_map) -> SymTab:
    symtab = SymTab()
    assert isinstance(mod, cwast.DefMod), mod
    logger.info("Processing %s", mod.name)
    # pass 1: get all the top level symbols
    for node in mod.body_mod:
        if isinstance(node, cwast.Comment):
            pass
        else:
            symtab.add_top_level_sym(node, mod_map)

    # pass 2:
    for node in mod.body_mod:
        if isinstance(node, cwast.Comment):
            continue
        logger.info("ExtractSymbolTable %s", node.name)
        if isinstance(node, cwast.DefVar):
            # we already registered the var in the previous step
            symtab.resolve_symbols_recursively(
                node.type_or_auto, mod_map, symtab_map)
            symtab.resolve_symbols_recursively(
                node.initial_or_undef, mod_map, symtab_map)
        else:
            symtab.resolve_symbols_recursively(node, mod_map, symtab_map)
    #
    assert not symtab._local_var_syms
    return symtab


def ExtractAllSymTabs(mod_topo_order: List[cwast.DefMod],
                      mod_map: Dict[str, cwast.DefMod]) -> Dict[str, SymTab]:
    symtab_map: Dict[str, SymTab] = {}
    for m in mod_topo_order:
        symtab_map[m] = ExtractSymTab(mod_map[m], mod_map, symtab_map)
    return symtab_map


def ModulesInTopologicalOrder(asts: List[cwast.DefMod]) -> Tuple[
        List[cwast.DefMod], Dict[str, cwast.DefMod]]:
    """The order is also deterministic"""
    mod_map: Dict[str, cwast.DefMod] = {}
    for mod in asts:
        assert isinstance(mod, cwast.DefMod)
        mod_map[mod.name] = mod

    deps_in = collections.defaultdict(list)
    deps_out = collections.defaultdict(list)
    # candidates have no incoming deps
    candidates = []
    for mod in asts:
        assert isinstance(mod, cwast.DefMod)
        mod_map[mod.name] = mod
        for node in mod.body_mod:
            if isinstance(node, cwast.Import):
                assert node.name in mod_map
                logging.info(
                    "found mod deps [%s] imported by [%s]", node.name, mod.name)
                deps_in[mod.name].append(node.name)
                deps_out[node.name].append(mod.name)

    for m in mod_map.keys():
        if not deps_in[m]:
            logging.info("found leaf mod [%s]", m)
            heapq.heappush(candidates, m)
    out = []
    while len(out) != len(mod_map):
        assert candidates
        x = heapq.heappop(candidates)
        logging.info("picking next mod: %s", x)
        out.append(x)
        for importer in deps_out[x]:
            deps_in[importer].remove(x)
            if not deps_in[importer]:
                heapq.heappush(candidates, importer)
    return out, mod_map


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
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

    mod_topo_order, mod_map = ModulesInTopologicalOrder(asts)
    ExtractAllSymTabs(mod_topo_order, mod_map)
