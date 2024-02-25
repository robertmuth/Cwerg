#!/usr/bin/python3

"""Symbol Resolution

"""

import logging

from typing import Optional, Any

from FrontEnd import pp
from FrontEnd import macros
from FrontEnd import cwast

logger = logging.getLogger(__name__)


_BUILT_IN_PLACE_HOLDER = None


def AnnotateNodeSymbol(id_node, def_node):
    """Sets the x_symol field to a node like DefGlobal, DefVar, DefFun, DefRec, etc ."""
    logger.info("resolving %s [%s] -> %s", id_node, id(id_node), def_node)
    assert cwast.NF.SYMBOL_ANNOTATED in id_node.FLAGS
    assert (cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS or
            cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS), f"unpexpected node: {def_node}"
    assert id_node.x_symbol is None
    id_node.x_symbol = def_node


def _resolve_enum_item(node: cwast.DefEnum, entry_name) -> cwast.EnumVal:
    for item in node.items:
        if isinstance(item, cwast.EnumVal) and item.name == entry_name:
            return item
    assert False, f"unknown enum [{entry_name}] for [{node.name}]"


class SymTab:
    """Symbol Table For Global and Local Symbols


    """

    def __init__(self):
        self._imports: dict[str, cwast.DefMod] = {}
        self._syms: dict[str, Any] = {}

    def AddLocalSym(self, name, node):
        assert isinstance(node, (cwast.DefVar, cwast.FunParam)), f"{node}"
        prev = self._syms.get(name)
        if prev is not None:
            cwast.CompilerError(node.x_srcloc,
                                f"Duplicate symbol name for {node} previously defined by {prev}")
        self._syms[name] = node

    def AddTopLevelSym(self, node):
        logger.info("recording global symbol: %s", node)
        if not isinstance(node, (cwast.DefFun, cwast.DefMacro, cwast.DefGlobal,
                                 cwast.DefRec, cwast.DefEnum, cwast.DefType)):
            cwast.CompilerError(
                node.x_srcloc, f"Unexpected toplevel node {node}")
        name = node.name
        if name in self._syms:
            cwast.CompilerError(node.x_srcloc, f"duplicate name {name}")
        self._syms[name] = node

    def AddImport(self, node: cwast.Import):
        name = node.alias if node.alias else node.name
        if name in self._imports:
            cwast.CompilerError(node.x_srcloc, f"dup import {name}")
        assert isinstance(node.x_module, cwast.DefMod)
        self._imports[name] = node.x_module

    def DelSym(self, name):
        assert name in self._syms
        del self._syms[name]

    def resolve_sym_here(self, name, must_be_public, srcloc):
        s = self._syms.get(name)
        if s:
            if must_be_public and not s.pub:

                cwast.CompilerError(srcloc, f"{name} must be public")
            return s

        return None

    def resolve_sym(self, ident: cwast.Id, builtin_syms: "SymTab", must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""
        name = cwast.GetSymbolName(ident.name)
        if ":" in name:
            enum_name, entry_name = name.split(":")
            s = self._syms.get(enum_name)
            if s:
                assert isinstance(s, cwast.DefEnum)
                if must_be_public:
                    assert s.pub, f"{name} must be public"
                return _resolve_enum_item(s, entry_name)
            cwast.CompilerError(
                ident.x_srcloc, f"could not resolve enum base-name [{enum_name}]")

        out = self.resolve_sym_here(name, must_be_public, ident.x_srcloc)
        if not out:
            out = builtin_syms.resolve_sym_here(
                name, must_be_public, ident.x_srcloc)
        return out

    def resolve_macro(self, macro_invoke: cwast.MacroInvoke,
                      builtin_syms: "SymTab", _must_be_public) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""

        name = cwast.GetSymbolName(macro_invoke.name)
        # TODO: pub check?
        out = self._syms.get(name)
        if not out:
            out = builtin_syms._syms.get(name)
        return out


def _ResolveSymbolInsideFunction(node: cwast.Id, builtin_syms: SymTab, scopes):
    name = cwast.GetSymbolName(node.name)
    is_qualified = cwast.IsQualifiedName(node.name)
    if not is_qualified:
        for s in reversed(scopes):
            def_node = s.get(name)
            if def_node is not None:
                return def_node
    symtab = node.x_import.x_module.x_symtab
    return symtab.resolve_sym(node, builtin_syms, is_qualified)


def ExtractSymTabPopulatedWithGlobals(mod: cwast.DefMod) -> SymTab:
    symtab = SymTab()
    assert isinstance(mod, cwast.DefMod), mod
    logger.info("Processing %s", mod.x_modname)
    # pass 1: get all the top level symbols
    for node in mod.body_mod:
        if isinstance(node, cwast.StmtStaticAssert):
            continue
        if isinstance(node, cwast.DefFun) and node.polymorphic:
            # symbol resolution for these can only be handled when we have
            # types so we skip them here
            continue
        elif isinstance(node, cwast.Import):
            # these will be processed during the recursive module reading
            continue
        else:
            symtab.AddTopLevelSym(node)
    return symtab


def _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(node, builtin_syms: SymTab,
                                                        must_resolve_all: bool):

    def visitor(node, _):
        nonlocal builtin_syms
        if isinstance(node, cwast.Id):
            if node.x_symbol:
                return
            symtab = node.x_import.x_module.x_symtab
            def_node = symtab.resolve_sym(
                node, builtin_syms, cwast.IsQualifiedName(node.name))
            if def_node:
                AnnotateNodeSymbol(node, def_node)
            else:
                if must_resolve_all:
                    cwast.CompilerError(
                        node.x_srcloc, f"cannot resolve symbol {node.name}")

    cwast.VisitAstRecursivelyPost(node, visitor)


MAX_MACRO_NESTING = 4


def ExpandMacroOrMacroLike(node,  builtin_syms: SymTab, nesting, ctx: macros.MacroContext):
    assert nesting < MAX_MACRO_NESTING
    assert cwast.NF.TO_BE_EXPANDED in node.FLAGS
    if isinstance(node, cwast.ExprSrcLoc):
        # TODO: encode file and line properly
        return cwast.ValNum(f"{12345}_u32")
    elif isinstance(node, cwast.ExprStringify):
        # assert isinstance(node.expr, cwast.Id)
        return cwast.ValString(f'"{node.expr}"', strkind="raw", x_srcloc=node.x_srcloc)

    assert isinstance(node, cwast.MacroInvoke)
    symtab = node.x_import.x_module.x_symtab
    macro = symtab.resolve_macro(
        node,  builtin_syms,  cwast.IsQualifiedName(node.name))
    if macro is None:
        cwast.CompilerError(
            node.x_srcloc, f"invocation of unknown macro `{node.name}`")
    exp = macros.ExpandMacro(node, macro, ctx)
    assert not isinstance(exp, list)
    FindAndExpandMacrosRecursively(exp, builtin_syms, nesting + 1, ctx)
    if cwast.NF.TO_BE_EXPANDED in exp.FLAGS:
        return ExpandMacroOrMacroLike(exp, builtin_syms, nesting + 1, ctx)
    # pp.PrettyPrint(exp)
    return exp


def FindAndExpandMacrosRecursively(node, builtin_syms, nesting, ctx: macros.MacroContext):
    # TODO: support macro-invocatios which produce new macro-invocations
    for c, nfd in node.__class__.FIELDS:
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, c)
            FindAndExpandMacrosRecursively(child, builtin_syms, nesting, ctx)
            if cwast.NF.TO_BE_EXPANDED in child.FLAGS:
                new_child = ExpandMacroOrMacroLike(
                    child, builtin_syms, nesting, ctx)
                assert not isinstance(new_child, cwast.EphemeralList)
                setattr(node, c, new_child)
        elif nfd.kind is cwast.NFK.LIST:
            children = getattr(node, c)
            new_children = []
            for child in children:
                FindAndExpandMacrosRecursively(
                    child, builtin_syms, nesting, ctx)
                if cwast.NF.TO_BE_EXPANDED not in child.FLAGS:
                    new_children.append(child)
                else:
                    exp = ExpandMacroOrMacroLike(
                        child, builtin_syms, nesting, ctx)
                    if isinstance(exp, cwast.EphemeralList):
                        for a in exp.args:
                            new_children.append(a)
                    else:
                        new_children.append(exp)
            setattr(node, c, new_children)


def ResolveSymbolsInsideFunctionsRecursively(
        node, symtab: SymTab, builtin_syms: SymTab, scopes: list[dict]):

    def record_local_sym(node):
        name = node.name
        logger.info("recording local symbol: %s", node)
        if name in scopes[-1]:
            cwast.CompilerError(node.x_srcloc,
                                f"redefinition of symbol: {name}")
        scopes[-1][name] = node
        symtab.AddLocalSym(name, node)

    if isinstance(node, cwast.DefVar):
        record_local_sym(node)
    elif isinstance(node, cwast.Id):
        def_node = _ResolveSymbolInsideFunction(node, builtin_syms, scopes)
        if def_node is None:
            cwast.CompilerError(
                node.x_srcloc, f"cannot resolve symbol for {node}")
        AnnotateNodeSymbol(node, def_node)
        return

    # recurse using a little bit of introspection
    for c, nfd in node.__class__.FIELDS:
        if isinstance(node, cwast.ExprCall) and node.polymorphic and c == "callee":
            # polymorphic stuff can only be handled once we have types
            continue
        if nfd.kind is cwast.NFK.NODE:
            ResolveSymbolsInsideFunctionsRecursively(
                getattr(node, c), symtab, builtin_syms, scopes)
        elif nfd.kind is cwast.NFK.LIST:
            # blocks introduce new scopes
            if c in cwast.NEW_SCOPE_FIELDS:
                logger.info("push scope for %s: %s", node, c)
                scopes.append({})
                if isinstance(node, cwast.DefFun):
                    for p in node.params:
                        if isinstance(p, cwast.FunParam):
                            record_local_sym(p)
            for cc in getattr(node, c):
                ResolveSymbolsInsideFunctionsRecursively(
                    cc, symtab, builtin_syms, scopes)
            if c in cwast.NEW_SCOPE_FIELDS:
                logger.info("pop scope for if block: %s", c)
                for name in scopes[-1].keys():
                    symtab.DelSym(name)
                scopes.pop(-1)


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
        _CheckAddressCanBeTaken(lhs.container)
    else:
        assert False, f"{lhs}"


def VerifyASTSymbolsRecursively(node):
    in_def_macro = False

    def visitor(node, parent, field):
        nonlocal in_def_macro

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            in_def_macro = isinstance(node, cwast.DefMacro)

        if in_def_macro:
            return

        if field == "callee" and isinstance(parent, cwast.ExprCall) and parent.polymorphic:
            return
        assert cwast.NF.TO_BE_EXPANDED not in node.FLAGS, f"{node}"
        if cwast.NF.SYMBOL_ANNOTATED in node.FLAGS:
            assert node.x_symbol is not None, f"unresolved symbol {node}"
        if isinstance(node, cwast.Id):
            # all macros should have been resolved
            assert not node.name.startswith("$"), f"{node.name}"
            def_node = node.x_symbol
            is_type_node = field in (
                "type", "types", "result", "type_or_auto", "subtrahend")
            if is_type_node != isinstance(def_node, (cwast.DefType, cwast.DefRec, cwast.TypeUnion, cwast.DefEnum)):
                cwast.CompilerError(
                    node.x_srcloc, f"unexpected id {node.name}: {type(def_node)} {field}")
        elif isinstance(node, (cwast.StmtBreak, cwast.StmtContinue)):
            assert isinstance(
                node.x_target, cwast.StmtBlock), f"break/continue with bad target {node.x_target}"
        elif isinstance(node, cwast.StmtReturn):
            assert isinstance(node.x_target, (cwast.DefFun, cwast.ExprStmt))
        elif isinstance(node, cwast.DefRec):
            seen = set()
            for field in node.fields:
                if isinstance(field, cwast.RecField):
                    if field.name in seen:
                        cwast.CompilerError(
                            field.x_srcloc, f"duplicate record field: {field.name}")
                    seen.add(field.name)

        if isinstance(node, cwast.ExprAddrOf):
            _CheckAddressCanBeTaken(node.expr_lhs)

    cwast.VisitAstRecursivelyWithParent(node, visitor, None, None)


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


def GetSymTabForBuiltInOrEmpty(mod_topo_order: list[cwast.DefMod]) -> SymTab:
    builtin_syms = None
    for mod in mod_topo_order:
        if mod.builtin:
            assert builtin_syms is None
            builtin_syms = mod.x_symtab
    return builtin_syms if builtin_syms else SymTab()


def ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(mod_topo_order: list[cwast.DefMod],
                                                       builtin_syms: SymTab,
                                                       must_resolve_all):
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro)):
                logger.info("Resolving global object: %s", node)
                _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, builtin_syms, must_resolve_all)


def MacroExpansionDecorateASTWithSymbols(mod_topo_order: list[cwast.DefMod]):
    """
    At this point every DefMod has a symtable populated with the global symbols
    and the Imports. All Imports have a valid x_module field.
    Ids that are not inside DefFuns have their x_symbol fields set.

    * expand macros recursively (macros are global symbols)
    * reolve symbols within functions (= setting x_symbol)
    """
    builtin_syms = GetSymTabForBuiltInOrEmpty(mod_topo_order)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro)):
                logger.info("Resolving global object: %s", node)
                _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, builtin_syms, True)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun):
                logger.info("Expanding macros in: %s", node)
                ctx = macros.MacroContext(1)
                FindAndExpandMacrosRecursively(node, builtin_syms, 0, ctx)

    for mod in mod_topo_order:
        # we wait until macro expansion with this
        _SetTargetFieldRecursively(mod)

        symtab = mod.x_symtab
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun)):
                logger.info("Resolving symbols inside fun: %s", node)
                scopes: list[dict] = []
                ResolveSymbolsInsideFunctionsRecursively(
                    node, symtab, builtin_syms, scopes)
                assert not scopes

    for mod in mod_topo_order:
        VerifyASTSymbolsRecursively(mod)


def IterateValRec(inits_field: list[cwast.RecField], def_rec: cwast.CanonType):
    inits: dict[cwast.RecField,
                cwast.FieldVal] = {i.x_field: i for i in inits_field}
    used = 0
    assert isinstance(def_rec.ast_node, cwast.DefRec)
    for f in def_rec.ast_node.fields:
        assert isinstance(f, cwast.RecField)
        i = inits.get(f)
        if i is not None:
            used += 1
        yield f, i
    assert used == len(inits)


_UNDEF = cwast.ValUndef()


def IterateValArray(val_array: cwast.ValArray, width):
    curr_val = 0
    for init in val_array.inits_array:
        assert isinstance(init, cwast.IndexVal)
        if isinstance(init.init_index, cwast.ValAuto):
            yield curr_val, init
            curr_val += 1
            continue
        index = init.init_index.x_value
        assert isinstance(index, int)
        while curr_val < index:
            yield curr_val, None
            curr_val += 1
        yield curr_val, init
        curr_val += 1
    if curr_val > width:
        cwast.CompilerError(
            val_array.x_srcloc, f"Out of bounds array access at {curr_val}. Array size is  {width}")
    while curr_val < width:
        yield curr_val, None
        curr_val += 1


_NORMALIZED_NODES_FOR_MOD_ARGS = (cwast.DefFun, cwast.DefRec, cwast.TypeUnion,
                                  cwast.TypeBase, cwast.TypePtr, cwast.TypeSlice, cwast.DefEnum,
                                  cwast.ValFalse, cwast.ValTrue, cwast.ValNum, cwast.ValVoid)


def IsNormalizeModParam(node):
    if isinstance(node, _NORMALIZED_NODES_FOR_MOD_ARGS):
        return True
    elif isinstance(node, cwast.DefType) and node.wrapped:
        return True
    else:
        return False


def NormalizeModParam(node):
    if IsNormalizeModParam(node):
        return node
    elif isinstance(node, cwast.DefType) and not node.wrapped:
        return NormalizeModParam(node.type)
    elif isinstance(node, cwast.Id):
        if node.x_symbol:
            return NormalizeModParam(node.x_symbol)
        else:
            return None
    else:
        assert False, f"NYI: {node}"


def AreEqualNormalizedModParam(a, b) -> bool:
    if a is None or b is None:
        return False
    if a is not type(b):
        return False
    if a is b:
        return True

    return False

############################################################
#
############################################################


def main(argv):
    assert len(argv) == 1
    assert argv[0].endswith(".cw")

    cwd = os.getcwd()
    mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
    mp.ReadModulesRecursively(
        ["builtin", str(pathlib.Path(argv[0][:-3]).resolve())])
    mod_topo_order = mp.ModulesInTopologicalOrder()
    MacroExpansionDecorateASTWithSymbols(mod_topo_order)
    for ast in mod_topo_order:
        cwast.CheckAST(ast, set())
        VerifyASTSymbolsRecursively(ast)
        pp.PrettyPrint(ast)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FrontEnd import mod_pool

    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    main(sys.argv[1:])
