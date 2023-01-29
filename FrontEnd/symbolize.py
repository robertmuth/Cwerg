#!/usr/bin/python3

"""Symbol Resolution

"""

import dataclasses
import sys
import logging
import collections
import heapq

from typing import List, Dict, Set, Optional, Union, Any, Tuple

from FrontEnd import pp
from FrontEnd import macros
from FrontEnd import cwast
from FrontEnd import parse

logger = logging.getLogger(__name__)

BUILTIN_MOD = "$builtin"
POLYMORPHIC_MOD = "$polymorphic"


def _add_symbol_link(id_node, def_node):
    logger.info("resolving %s [%s] -> %s", id_node, id(id_node), def_node)
    assert cwast.NF.SYMBOL_ANNOTATED in id_node.__class__.FLAGS
    assert (cwast.NF.GLOBAL_SYM_DEF in def_node.__class__.FLAGS or
            cwast.NF.LOCAL_SYM_DEF in def_node.__class__.FLAGS), f"unpexpected node: {def_node}"
    id_node.x_symbol = def_node


def _resolve_enum_item(node: cwast.DefEnum, components) -> cwast.EnumVal:
    assert len(components) == 1
    for item in node.items:
        if isinstance(item, cwast.EnumVal) and item.name == components[0]:
            return item
    assert False, f"unknown enum [{components[0]}] for [{node.name}]"


class SymTab:
    """Symbol Table For Global Symbols"""

    def __init__(self):
        self._type_syms: Dict[str, cwast.DefType] = {}

        self._rec_syms: Dict[str, cwast.DefRec] = {}
        self._enum_syms: Dict[str, cwast.DefEnum] = {}

        self._fun_syms: Dict[str, cwast.DefFun] = {}
        self._macro_syms: Dict[str, cwast.DefMacro] = {}

        self._var_syms: Dict[str, cwast.DefVar] = {}
        self._mod_syms: Dict[str, cwast.DefMod] = {}
        self._all_syms: Dict[str, Any] = {}

    def AddSymWithDupCheck(self, name, node):
        prev = self._all_syms.get(name)
        if prev is not None:
            cwast.CompilerError(node.x_srcloc,
                                f"Duplicate symbol name for {node} previously defined by {prev}")
        self._all_syms[name] = node

    def DelSym(self, name):
        assert name in self._all_syms
        del self._all_syms[name]

    def resolve_sym_here(self, name, must_be_public):
        for syms in (self._type_syms, self._fun_syms,
                     self._rec_syms, self._enum_syms, self._var_syms, self._macro_syms):
            s = syms.get(name)
            if s:
                if must_be_public:
                    assert s.pub, f"{name} must be public"
                return s

        return None

    def resolve_sym(self, components: List[str], symtab_map, must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        if len(components) == 2:
            s = self._enum_syms.get(components[0])
            if s:
                assert isinstance(s, cwast.DefEnum)
                if must_be_public:
                    assert s.pub, f"{components} must be public"
                return _resolve_enum_item(s, components[1:])
        if len(components) > 1:
            # TODO: pub check?
            s = self._mod_syms.get(components[0])
            if s:
                assert isinstance(s, cwast.DefMod), f"{s}"
                mod_symtab = symtab_map[s.name]
                return mod_symtab.resolve_sym(components[1:], symtab_map, True)
            assert False, f"could not resolve name {components}"

        out = self.resolve_sym_here(components[0], must_be_public)
        if not out:
            s = symtab_map.get(BUILTIN_MOD)
            if s:
                out = s.resolve_sym_here(components[0], must_be_public)
        return out

    def resolve_macro(self, components: List[str], symtab_map, must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        if len(components) > 1:
            assert len(components) == 2
            # TODO: pub check?
            s = self._mod_syms.get(components[0])
            if s:
                assert isinstance(s, cwast.DefMod), f"{s}"
                mod_symtab = symtab_map[s.name]
                return mod_symtab._macro_syms.get(components[1])
            assert False, f"could not resolve name {components}"

        out = self._macro_syms.get(components[0])
        if not out:
            s = symtab_map.get(BUILTIN_MOD)
            if s:
                out = s._macro_syms.get(components[0])

        return out

    def add_top_level_sym(self, node, mod_map):
        logger.info("recording global symbol: %s", node)
        name = node.name
        if isinstance(node, cwast.DefFun):
            assert name not in self._fun_syms, f"duplicate symbol {name}"
            self._fun_syms[name] = node
        elif isinstance(node, cwast.DefMacro):
            assert name not in self._macro_syms, f"duplicate symbol {name}"
            self._macro_syms[name] = node
        elif isinstance(node, cwast.DefGlobal):
            assert name not in self._var_syms
            self._var_syms[name] = node
        elif isinstance(node, cwast.DefRec):
            assert name not in self._rec_syms
            self._rec_syms[name] = node
        elif isinstance(node, cwast.DefEnum):
            assert name not in self._enum_syms
            self._enum_syms[name] = node
        elif isinstance(node, cwast.DefType):
            if name in self._type_syms:
                cwast.CompilerError(
                    node.x_srcloc, f"duplicate toplevel symbol {name}")
            self._type_syms[name] = node
        elif isinstance(node, cwast.Import):
            name = node.alias if node.alias else node.name
            assert name not in self._mod_syms
            self._mod_syms[name] = mod_map[node.name]
        else:
            cwast.CompilerError(
                node.x_srcloc, f"Unexpected toplevel node {node}")
        self.AddSymWithDupCheck(name, node)


def _ExtractSymTabPopulatedWithGlobals(mod, mod_map) -> SymTab:
    symtab = SymTab()
    assert isinstance(mod, cwast.DefMod), mod
    logger.info("Processing %s", mod.name)
    # pass 1: get all the top level symbols
    for node in mod.body_mod:
        if isinstance(node, (cwast.StmtStaticAssert, cwast.Comment)):
            continue
        elif isinstance(node, cwast.DefFun) and node.polymorphic:
            # these can only be handled when we have types
            continue
        else:
            symtab.add_top_level_sym(node, mod_map)
    return symtab


def _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
        node, symtab: SymTab, symtab_map):
    def visitor(node):
        if isinstance(node, cwast.Id):
            def_node = symtab.resolve_sym(
                node.name.split("/"), symtab_map, False)
            if def_node is None:
                cwast.CompilerError(
                    node.x_srcloc, f"cannot resolve symbol {node.name}")
            _add_symbol_link(node, def_node)

    cwast.VisitAstRecursively(node, visitor)


MAX_MACRO_NESTING = 4


def ExpandMacroOrMacroLike(node, sym_tab, symtab_map, nesting, ctx: macros.MacroContext):
    assert nesting < MAX_MACRO_NESTING
    assert cwast.NF.TO_BE_EXPANDED in node.FLAGS
    if isinstance(node, cwast.ExprSrcLoc):
        # TODO: encode file and line properly
        return cwast.ValNum(f"{12345}_u32")
    elif isinstance(node, cwast.ExprStringify):
        assert isinstance(node.expr, cwast.Id)
        return cwast.ValString(True, f'"{node.expr.name}"')

    assert isinstance(node, cwast.MacroInvoke)
    macro = sym_tab.resolve_macro(
        node.name.split("/"), symtab_map, False)
    if macro is None:
        cwast.CompilerError(
            node.x_srcloc, f"invocation of unknown macro `{node.name}`")
    exp = macros.ExpandMacro(node, macro, ctx)
    assert not isinstance(exp, list)
    FindAndExpandMacrosRecursively(
        exp, sym_tab, symtab_map, nesting + 1, ctx)
    if cwast.NF.TO_BE_EXPANDED in exp.FLAGS:
        return ExpandMacroOrMacroLike(exp, sym_tab, symtab_map, nesting + 1, ctx)
    # pp.PrettyPrint(exp)
    return exp


def FindAndExpandMacrosRecursively(node, sym_tab, symtab_map, nesting, ctx: macros.MacroContext):
    # TODO: support macro-invocatios which produce new macro-invocations
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, c)
            FindAndExpandMacrosRecursively(
                child, sym_tab, symtab_map, nesting, ctx)
            if cwast.NF.TO_BE_EXPANDED in child.FLAGS:
                new_child = ExpandMacroOrMacroLike(
                    child, sym_tab, symtab_map, nesting, ctx)
                assert not isinstance(new_child, cwast.EphemeralList)
                setattr(node, c, new_child)
        elif nfd.kind is cwast.NFK.LIST:
            children = getattr(node, c)
            new_children = []
            for child in children:
                FindAndExpandMacrosRecursively(
                    child, sym_tab, symtab_map, nesting, ctx)
                if cwast.NF.TO_BE_EXPANDED not in child.FLAGS:
                    new_children.append(child)
                else:
                    exp = ExpandMacroOrMacroLike(
                        child, sym_tab, symtab_map, nesting, ctx)
                    if isinstance(exp, cwast.EphemeralList):
                        for a in exp.args:
                            new_children.append(a)
                    else:
                        new_children.append(exp)
            setattr(node, c, new_children)


def _resolve_symbol_inside_function_or_macro(name: str, symtab: SymTab, symtab_map, scopes):
    components = name.split("/")
    if len(components) == 1:
        for s in reversed(scopes):
            def_node = s.get(components[0])
            if def_node is not None:
                return def_node
    return symtab.resolve_sym(components, symtab_map, False)


def ResolveSymbolsInsideFunctionsRecursively(
        node, symtab: SymTab, symtab_map, scopes):

    def record_local_sym(node):
        name = node.name
        logger.info("recording local symbol: %s", node)
        assert name not in scopes[-1], f"duplicate symbol: {name}"
        scopes[-1][name] = node
        symtab.AddSymWithDupCheck(name, node)

    if isinstance(node, cwast.DefVar):
        record_local_sym(node)
    elif isinstance(node, cwast.Id):
        def_node = _resolve_symbol_inside_function_or_macro(
            node.name, symtab, symtab_map, scopes)
        assert def_node is not None, f"cannot resolve symbol for {node}"
        _add_symbol_link(node, def_node)
        return

    # recurse using a little bit of introspection
    for c in node.__class__.FIELDS:
        if isinstance(node, cwast.ExprCall) and node.polymorphic and c == "callee":
            # polymorphic stuff can only be handled once we have types
            continue
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            ResolveSymbolsInsideFunctionsRecursively(
                getattr(node, c), symtab, symtab_map, scopes)
        elif nfd.kind is cwast.NFK.LIST:
            if c in cwast.NEW_SCOPE_FIELDS:
                logger.info("push scope for %s: %s" % (node, c))
                scopes.append({})
                if isinstance(node, cwast.DefFun):
                    for p in node.params:
                        if isinstance(p, cwast.FunParam):
                            record_local_sym(p)
            for cc in getattr(node, c):
                ResolveSymbolsInsideFunctionsRecursively(
                    cc, symtab, symtab_map, scopes)
            if c in cwast.NEW_SCOPE_FIELDS:
                logger.info("pop scope for if block: %s" % c)
                for name in scopes[-1].keys():
                    symtab.DelSym(name)
                scopes.pop(-1)


def VerifyASTSymbolsRecursively(node):
    if isinstance(node, cwast.DefMacro):
        return
    assert cwast.NF.TO_BE_EXPANDED not in node.FLAGS
    if isinstance(node, cwast.Id):
        # all macros should have been resolved
        assert not node.name.startswith("$")
    assert cwast.NF.TO_BE_EXPANDED not in node.FLAGS
    if cwast.NF.SYMBOL_ANNOTATED in node.__class__.FLAGS:
        assert node.x_symbol is not None, f"unresolved symbol {node}"
    if isinstance(node, (cwast.StmtBreak, cwast.StmtContinue, cwast.StmtReturn)):
        assert node.x_target is not None
    #
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            if isinstance(node, cwast.ExprCall) and node.polymorphic and c == "callee":
                # polymorphic stuff can only be handled once we have types
                continue
            VerifyASTSymbolsRecursively(getattr(node, c))
        elif nfd.kind is cwast.NFK.LIST:
            for cc in getattr(node, c):
                VerifyASTSymbolsRecursively(cc)


def _SetTargetFieldRecursively(node):
    def visitor(node, parents):
        if isinstance(node, cwast.DefMacro):
            return True
        if isinstance(node, (cwast.StmtBreak, cwast.StmtContinue)):
            target = node.target
            for p in reversed(parents):
                if isinstance(p, cwast.StmtBlock):
                    if p.label == target or target == "":
                        node.x_target = p
                        break
            else:
                assert False
        if isinstance(node, cwast.StmtReturn):
            for p in reversed(parents):
                if isinstance(p, (cwast.DefFun, cwast.ExprStmt)):
                    node.x_target = p
                    break
            else:
                assert False, f"{node} --- {[p.__class__.__name__ for p in parents]}"
    cwast.VisitAstRecursivelyWithAllParents(node, [], visitor)


def MacroExpansionDecorateASTWithSymbols(mod_topo_order: List[cwast.DefMod],
                           mod_map: Dict[str, cwast.DefMod]):
    symtab_map: Dict[str, SymTab] = {}
    for mod in mod_topo_order:
        symtab_map[mod.name] = _ExtractSymTabPopulatedWithGlobals(mod, mod_map)

    for mod in mod_topo_order:
        symtab = symtab_map[mod.name]
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro, cwast.Comment)):
                logger.info("Resolving global object: %s", node)
                _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, symtab, symtab_map)

    for mod in mod_topo_order:
        symtab = symtab_map[mod.name]
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun):
                logger.info("Expanding macros in: %s", node)
                ctx = macros.MacroContext(1)
                FindAndExpandMacrosRecursively(
                    node, symtab, symtab_map, 0, ctx)

    for mod in mod_topo_order:
        # we wait until macro expansion with this
        _SetTargetFieldRecursively(mod)

        symtab = symtab_map[mod.name]
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun)):
                logger.info("Resolving symbols inside fun: %s", node)
                scopes = []
                ResolveSymbolsInsideFunctionsRecursively(
                    node, symtab, symtab_map, scopes)
                assert not scopes

    for mod in mod_topo_order:
        VerifyASTSymbolsRecursively(mod)


def ModulesInTopologicalOrder(asts: List[cwast.DefMod]) -> Tuple[
        List[cwast.DefMod], Dict[str, cwast.DefMod]]:
    """The order is also deterministic

    This means modules cannot have circular dependencies except for module arguments
    to parameterized modules which are ignored in the topo order.
    """
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
                logger.info(
                    "found mod deps [%s] imported by [%s]", node.name, mod.name)
                deps_in[mod.name].append(node.name)
                deps_out[node.name].append(mod.name)

    for m in mod_map.keys():
        if not deps_in[m]:
            logger.info("found leaf mod [%s]", m)
            heapq.heappush(candidates, m)
    out = []
    while len(out) != len(mod_map):
        assert candidates
        x = heapq.heappop(candidates)
        logger.info("picking next mod: %s", x)
        out.append(mod_map[x])
        for importer in deps_out[x]:
            deps_in[importer].remove(x)
            if not deps_in[importer]:
                heapq.heappush(candidates, importer)
    return out, mod_map


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)
    mod_topo_order, mod_map = ModulesInTopologicalOrder(asts)
    MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for ast in asts:
        pp.PrettyPrint(ast)
