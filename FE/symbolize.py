#!/bin/env python3

"""Symbol Resolution

"""

import logging

from typing import Optional, Any, Sequence

from FE import cwast

logger = logging.getLogger(__name__)


_BUILT_IN_PLACE_HOLDER = None


def AnnotateNodeSymbol(id_node: cwast.Id, def_node: Any):
    """Sets the x_symol field to a node like DefGlobal, DefVar, DefFun, DefRec, etc ."""
    logger.debug("resolving %s [%s] -> %s", id_node, id(id_node), def_node)
    assert (cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS or
            cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS), f"unpexpected node: {def_node}"
    assert id_node.x_symbol is cwast.INVALID_SYMBOL
    id_node.x_symbol = def_node


def UpdateNodeSymbolForPolyCall(id_node: cwast.Id, new_def_node: cwast.DefFun):
    old_def_node = id_node.x_symbol
    assert isinstance(
        old_def_node, cwast.DefFun) and old_def_node.poly
    assert new_def_node.poly
    id_node.x_symbol = new_def_node


def HasImportedSymbolReference(node: cwast.Id) -> bool:
    """This is only used during symbol resolution after
    the x_import field has been set.

    Note: Some Id nodes that get created during macro instatiations do not have
    the x_import field set. (TODO: is this still true?)
    """
    if not node.x_import:
        return False
    return not node.x_import.name.IsSelfImport()


def _resolve_enum_item(node: cwast.DefEnum, entry_name, srcloc) -> cwast.EnumVal:
    for item in node.items:
        if isinstance(item, cwast.EnumVal) and item.name == entry_name:
            return item
    cwast.CompilerError(srcloc,
                        f"unknown enum [{entry_name}] for [{node.name}]")


class SymTab:
    """Symbol Table For Global and Local Symbols in one Mod"""

    def __init__(self: Any):
        self._syms: dict[cwast.NAME, Any] = {}

    def is_empty(self) -> int:
        return len(self._syms) == 0

    def add_with_dup_check(self, name: cwast.NAME, node):
        prev = self._syms.get(name)
        if prev is not None:
            cwast.CompilerError(node.x_srcloc,
                                f"Duplicate symbol name [{name}] for\n {node}\npreviously defined by\n {prev}")
        self._syms[name] = node

    def has_sym(self, name):
        return name in self._syms

    def del_sym(self, name):
        assert name in self._syms
        del self._syms[name]

    def resolve_name(self, name):
        return self._syms.get(name)

    def resolve_name_with_visibility_check(self, name, must_be_public, srcloc):
        s = self.resolve_name(name)
        if s:
            if must_be_public and not s.pub:
                cwast.CompilerError(srcloc, f"{name} must be public")
            return s

        return None

    def resolve_sym(self, ident: cwast.Id, must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        # the mod_name has already been used to pick this SymTab
        name = ident.name
        out = self.resolve_name_with_visibility_check(
            name, must_be_public, ident.x_srcloc)
        if ident.enum_name is not None:
            if not out:
                cwast.CompilerError(
                    ident.x_srcloc, f"could not resolve enum base-name [{name}]")
            assert isinstance(out, cwast.DefEnum)
            return _resolve_enum_item(out, ident.enum_name, ident.x_srcloc)
        return out

    def resolve_macro(self, macro_invoke: cwast.MacroInvoke,
                      builtin_syms: "SymTab", must_be_public: bool) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""

        # We are already in the "right" symtab
        name = macro_invoke.name.GetSymbolNameWithoutQualifier()
        out = self.resolve_name_with_visibility_check(
            name, must_be_public, macro_invoke.x_srcloc)
        if not out:
            out = builtin_syms._syms.get(name)
        if not out:
            return out
        assert isinstance(out, cwast.DefMacro)
        return out


def _IsFieldNode(node, parent) -> bool:
    return isinstance(parent, (cwast.ExprOffsetof, cwast.ExprField)) and parent.field is node


def _IsPointNode(node, parent) -> bool:
    return isinstance(parent, cwast.ValPoint) and parent.point is node


def _HelperResolveGlobalSymbols(node, builtin_syms: SymTab, must_resolve_all: bool):
    # this may be called multiple times for the same module
    def visitor(node: Any, parent):
        nonlocal builtin_syms
        if not isinstance(node, cwast.Id) or node.x_symbol:
            return

        # must wait until type info is available
        if _IsFieldNode(node, parent):
            return

        if node.x_import.x_module == cwast.INVALID_MOD:
            if must_resolve_all:
                cwast.CompilerError(
                    node.x_srcloc, f"import of {node.name} not resolved")
            return
        symtab: SymTab = node.x_import.x_module.x_symtab
        is_qualified = HasImportedSymbolReference(node)
        def_node = symtab.resolve_sym(node, is_qualified)
        if not def_node and not is_qualified:
            def_node = builtin_syms.resolve_sym(node, True)
        if def_node:
            AnnotateNodeSymbol(node, def_node)
        else:
            if must_resolve_all and not _IsPointNode(node, parent):
                cwast.CompilerError(
                    node.x_srcloc, f"cannot resolve symbol {node.FullName()}")

    cwast.VisitAstRecursivelyWithParent(node, visitor, None)


def ResolveSymbolsOutsideFunctionsAndMacros(mod_topo_order: Sequence[cwast.DefMod],
                                            builtin_syms: SymTab,
                                            must_resolve_all):
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro)):
                logger.info("Resolving global object: %s", node)
                _HelperResolveGlobalSymbols(
                    node, builtin_syms, must_resolve_all)


def _ResolveSymbolInsideFunction(node: cwast.Id, builtin_syms: SymTab, scopes) -> Any:
    if node.x_symbol:
        # this happens for module parameter
        return
    name = node.name
    was_qualified = HasImportedSymbolReference(node)

    if not was_qualified and node.enum_name is None:
        for symtab in reversed(scopes):
            def_node = symtab.resolve_name(name)
            if def_node is not None:
                AnnotateNodeSymbol(node, def_node)
                return

    # symbol is not a local symbol - so we fall through to looking in the global scope
    # assert False, f"{node}"
    symtab: SymTab = node.x_import.x_module.x_symtab
    def_node = symtab.resolve_sym(node, was_qualified)
    if not def_node:
        def_node = builtin_syms.resolve_sym(node, True)
    if def_node is None:
        cwast.CompilerError(
            node.x_srcloc, f"cannot resolve symbol for {node}")
    AnnotateNodeSymbol(node, def_node)


def _HelperResolveSymbolsInsideFunctions(
        fun, symtab: SymTab, builtin_syms: SymTab, scopes: list[SymTab]):

    def record_local_sym(node):
        logger.debug("recording local symbol: %s", node)
        scopes[-1].add_with_dup_check(node.name, node)

    def visitor(node: Any, parent: Any):
        nonlocal builtin_syms, scopes
        if isinstance(node, cwast.Id) and not _IsFieldNode(node, parent):
            _ResolveSymbolInsideFunction(node, builtin_syms, scopes)
        if isinstance(node, cwast.DefVar):
            assert not node.name.IsMacroVar()
            record_local_sym(node)

    def scope_enter(node: Any):
        nonlocal scopes
        logger.debug("push scope for %s", node)
        scopes.append(SymTab())
        if isinstance(node, cwast.DefFun):
            for p in node.params:
                if isinstance(p, cwast.FunParam):
                    record_local_sym(p)

    def scope_exit(node: Any):
        nonlocal scopes, symtab
        logger.debug("pop scope for %s", node)
        scopes.pop(-1)

    cwast.VisitAstRecursivelyWithScopeTracking(
        fun, visitor, scope_enter, scope_exit, None)


def ResolveSymbolsInsideFunctions(
        mods: list[cwast.DefMod], builtin_symtab: SymTab):
    """
    At this point:
    * DefMods have a valid x_symtab populated with the global symbols
    * Imports have a valid x_module field
    * Ids referencing imported symbols have a valid x_import field

    """

    for mod in mods:
        logger.info("Resolving symbols inside module: %s", mod.name)
        symtab = mod.x_symtab
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun)):
                logger.info("Resolving symbols inside fun: %s", node.name)
                scopes: list[SymTab] = []
                _HelperResolveSymbolsInsideFunctions(
                    node, symtab, builtin_symtab, scopes)
                assert not scopes


def _CheckAddressCanBeTaken(lhs):
    if isinstance(lhs, cwast.Id):
        node_def = lhs.x_symbol
        if isinstance(node_def, cwast.DefGlobal):
            pass
        elif isinstance(node_def, cwast.DefVar):
            if not node_def.ref:
                cwast.CompilerError(
                    lhs.x_srcloc, f"in {lhs.x_srcloc} expect ref flag for {node_def}")
        else:
            cwast.CompilerError(
                lhs.x_srcloc, f"expect DefVar node for lhs {node_def}")
    elif isinstance(lhs, cwast.ExprIndex):
        _CheckAddressCanBeTaken(lhs.container)
    elif isinstance(lhs, cwast.ExprDeref):
        pass
    elif isinstance(lhs, cwast.ExprField):
        if isinstance(lhs.container, cwast.ExprDeref):
            # somebody has taken the address already, otherwise
            # we could not dereference
            return True
        _CheckAddressCanBeTaken(lhs.container)
    else:
        assert False, f"{lhs}"


def VerifySymbols(node):
    """all macros should have been resolved by now"""
    in_def_macro = False

    def visitor(node: Any, nfd: cwast.NFD):
        nonlocal in_def_macro

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            in_def_macro = isinstance(node, cwast.DefMacro)

        if in_def_macro:
            return

        assert cwast.NF.TO_BE_EXPANDED not in node.FLAGS, f"{node}"
        if cwast.NF.SYMBOL_ANNOTATED in node.FLAGS:
            if node.x_symbol is None:
                assert nfd.name in cwast.FIELD_NAME_FIELDS, f"unresolved symbol {
                    node} {node.x_srcloc}"
        if isinstance(node, cwast.Id):
            def_node = node.x_symbol
            is_type_node = nfd.name in cwast.TYPE_FIELDS
            if is_type_node != isinstance(def_node, (cwast.DefType, cwast.DefRec, cwast.TypeUnion, cwast.DefEnum)):
                cwast.CompilerError(
                    node.x_srcloc, f"unexpected id {node.FullName()}: {type(def_node)}")
        elif isinstance(node, (cwast.StmtBreak, cwast.StmtContinue)):
            assert isinstance(
                node.x_target, cwast.StmtBlock), f"break/continue with bad target {node.x_target}"
        elif isinstance(node, cwast.StmtReturn):
            assert isinstance(node.x_target, (cwast.DefFun, cwast.ExprStmt))
        elif isinstance(node, cwast.DefRec):
            seen = set()
            for f in node.fields:
                if isinstance(f, cwast.RecField):
                    if f.name in seen:
                        cwast.CompilerError(
                            f.x_srcloc, f"duplicate record field: {f.name}")
                    seen.add(f.name)

        if isinstance(node, cwast.ExprAddrOf):
            _CheckAddressCanBeTaken(node.expr_lhs)

    cwast.VisitAstRecursivelyWithField(node, visitor, None)


def _HelperSetTargetField(node):
    parents = []

    def visitor_pre(node):
        nonlocal parents
        if isinstance(node, cwast.DefMacro):
            return True

        parents.append(node)

        if isinstance(node, (cwast.StmtBreak, cwast.StmtContinue)):
            target = node.target
            for p in reversed(parents):
                if isinstance(p, cwast.StmtBlock):
                    if p.label == target or target.IsEmpty():
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
                assert False, f"{
                    node} --- {[p.__class__.__name__ for p in parents]}"

    def visitor_post(node):
        nonlocal parents
        parents.pop(-1)

    cwast.VisitAstRecursivelyPreAndPost(
        node, visitor_pre, visitor_post)


def SetTargetFields(mods: list[cwast.DefMod]):
    for mod in mods:
        logger.info("Resolving symbols inside module: %s", mod.name)
        # we wait until macro expansion before resolving control flow targets
        _HelperSetTargetField(mod)


def IterateValRec(points: list[cwast.ValPoint], def_rec: cwast.CanonType):
    """Pairs given ValPoints from a ValCompound repesenting a DefRec with RecFields"""
    assert isinstance(def_rec.ast_node, cwast.DefRec)
    next_point = 0
    for f in def_rec.ast_node.fields:
        if next_point < len(points):
            p = points[next_point]
            if isinstance(p.point, cwast.ValAuto):
                yield f, p
                next_point += 1
                continue

            assert isinstance(p.point, cwast.Id)
            if p.point.GetBaseNameStrict() == f.name:
                yield f, p
                next_point += 1
                continue

        yield f, None
    if next_point != len(points):
        cwast.CompilerError(points[-1].x_srcloc,
                            "bad initializer {points[-1]}")


_UNDEF = cwast.ValUndef()


def IterateValVec(points: list[cwast.ValPoint], dim, srcloc):
    """Pairs given ValPoints from a ValCompound repesenting a Vec with their indices"""
    curr_index = 0
    for init in points:
        if isinstance(init.point, cwast.ValAuto):
            yield curr_index, init
            curr_index += 1
            continue
        index = init.point.x_value
        assert isinstance(index, int)
        while curr_index < index:
            yield curr_index, None
            curr_index += 1
        yield curr_index, init
        curr_index += 1
    if curr_index > dim:
        cwast.CompilerError(
            srcloc, f"Out of bounds array access at {curr_index}. Array size is  {dim}")
    while curr_index < dim:
        yield curr_index, None
        curr_index += 1
