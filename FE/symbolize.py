#!/bin/env python3

"""Symbol Resolution

"""

import logging

from typing import Optional, Any, Sequence, Union

from FE import pp_sexpr
from FE import macros
from FE import cwast
from FE import canonicalize
from FE import identifier

logger = logging.getLogger(__name__)


_BUILT_IN_PLACE_HOLDER = None


def AnnotateNodeSymbol(id_node: cwast.Id, def_node: Any):
    """Sets the x_symol field to a node like DefGlobal, DefVar, DefFun, DefRec, etc ."""
    logger.debug("resolving %s [%s] -> %s", id_node, id(id_node), def_node)
    assert cwast.NF.SYMBOL_ANNOTATED in id_node.FLAGS
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


def _resolve_enum_item(node: cwast.DefEnum, entry_name, srcloc) -> cwast.EnumVal:
    for item in node.items:
        if isinstance(item, cwast.EnumVal) and item.name == entry_name:
            return item
    cwast.CompilerError(srcloc,
                        f"unknown enum [{entry_name}] for [{node.name}]")


class SymTab:
    """Symbol Table For Global and Local Symbols in one Mod


    """

    def __init__(self: Any):
        self._imports: dict[cwast.NAME, cwast.DefMod] = {}
        self._syms: dict[cwast.NAME, Any] = {}

    def AddLocalSym(self, name: cwast.NAME, node):
        assert not name.IsMacroVar()
        assert isinstance(node, (cwast.DefVar, cwast.FunParam)), f"{node}"
        prev = self._syms.get(name)
        if prev is not None:
            cwast.CompilerError(node.x_srcloc,
                                f"Duplicate symbol name [{name}] for\n {node}\npreviously defined by\n {prev}")
        self._syms[name] = node

    def AddTopLevelSym(self: "SymTab", node: Any):
        logger.info("recording global symbol: %s", node)
        if not isinstance(node, (cwast.DefFun, cwast.DefMacro, cwast.DefGlobal,
                                 cwast.DefRec, cwast.DefEnum, cwast.DefType)):
            cwast.CompilerError(
                node.x_srcloc, f"Unexpected toplevel node {node}")
        name: cwast.NAME = node.name
        # we only recored the first occurrence of a poly functions which is why
        # only that function's visibility setting matters
        if isinstance(node, cwast.DefFun) and node.poly:
            if name.IsQualifiedName() or name in self._syms:
                return

        if name in self._syms:
            cwast.CompilerError(node.x_srcloc, f"duplicate name {name}")
        self._syms[name] = node

    def AddImport(self, node: cwast.Import):
        name = node.name
        if name in self._imports:
            cwast.CompilerError(node.x_srcloc, f"dup import {name}")
        assert node.x_module != cwast.INVALID_MOD
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
        # the mod_name has already been used to pick this SymTab
        base_name = ident.base_name
        if ident.enum_name is not None:
            s = self._syms.get(base_name)
            if s:
                assert isinstance(s, cwast.DefEnum)
                if must_be_public:
                    assert s.pub, f"{ident.FullName()} must be public"
                return _resolve_enum_item(s, ident.enum_name, ident.x_srcloc)
            cwast.CompilerError(
                ident.x_srcloc, f"could not resolve enum base-name [{ident.enum_name}]")

        out = self.resolve_sym_here(base_name, must_be_public, ident.x_srcloc)
        if not out:
            out = builtin_syms.resolve_sym_here(
                base_name, must_be_public, ident.x_srcloc)
        return out

    def resolve_macro(self, macro_invoke: cwast.MacroInvoke,
                      builtin_syms: "SymTab", must_be_public: bool) -> Optional[Any]:
        """We could be more specific here if we narrow down the symbol type"""

        # We are already in the "right" symtab
        name = macro_invoke.name.GetSymbolNameWithoutQualifier()
        out = self._syms.get(name)
        if not out:
            out = builtin_syms._syms.get(name)
        if not out:
            return out
        assert isinstance(out, cwast.DefMacro)
        if must_be_public:
            assert out.pub, f"{out.name} must be public"
        return out


def _ResolveSymbolInsideFunction(node: cwast.Id, builtin_syms: SymTab, scopes) -> Any:
    if node.x_symbol:
        # this happens for module parameter
        return
    name = node.base_name
    is_qualified = node.mod_name is not None
    if not is_qualified and node.enum_name is None:
        for s in reversed(scopes):
            def_node = s.get(name)
            if def_node is not None:
                AnnotateNodeSymbol(node, def_node)
                return
        # symbol is not a local symbol - so we fall through to looking in the global scope
    symtab: SymTab = node.x_import.x_module.x_symtab
    def_node = symtab.resolve_sym(node, builtin_syms, is_qualified)
    if def_node is None:
        cwast.CompilerError(
            node.x_srcloc, f"cannot resolve symbol for {node}")
    AnnotateNodeSymbol(node, def_node)


def ExtractSymTabPopulatedWithGlobals(mod: cwast.DefMod) -> SymTab:
    symtab = SymTab()
    assert isinstance(mod, cwast.DefMod), mod
    logger.info("Processing %s", mod)
    # pass 1: get all the top level symbols
    for node in mod.body_mod:
        if isinstance(node, cwast.StmtStaticAssert):
            continue
        elif isinstance(node, cwast.Import):
            # these will be processed during the recursive module reading
            continue
        else:
            symtab.AddTopLevelSym(node)
    return symtab


def _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(node, builtin_syms: SymTab,
                                                        must_resolve_all: bool):

    def visitor(node: Any, nfd: cwast.NFD):
        nonlocal builtin_syms
        if isinstance(node, cwast.Id):
            if nfd.name == "field":
                # must wait until type info is available
                return
            if node.x_symbol:
                return
            if node.x_import.x_module == cwast.INVALID_MOD:
                if must_resolve_all:
                    cwast.CompilerError(
                        node.x_srcloc, f"import of {node.base_name} not resolved")
                return
            symtab = node.x_import.x_module.x_symtab
            def_node = symtab.resolve_sym(
                node, builtin_syms, (node.mod_name is not None))
            if def_node:
                AnnotateNodeSymbol(node, def_node)
            else:
                if must_resolve_all and nfd.name != "point":
                    cwast.CompilerError(
                        node.x_srcloc, f"cannot resolve symbol {node.FullName()}")

    cwast.VisitAstRecursivelyWithFieldPost(node, visitor)


MAX_MACRO_NESTING = 8


def ExpandMacroOrMacroLike(node: Union[cwast.ExprSrcLoc, cwast.ExprStringify, cwast.MacroInvoke],
                           builtin_syms: SymTab, nesting: int, ctx: macros.MacroContext):
    """This will recursively expand the macro so returned node does not contain any expandables"""
    while cwast.NF.TO_BE_EXPANDED in node.FLAGS:
        assert nesting < MAX_MACRO_NESTING
        if isinstance(node, cwast.ExprSrcLoc):
            return cwast.ValString(f'r"{node.expr.x_srcloc}"', x_srcloc=node.x_srcloc)
        elif isinstance(node, cwast.ExprStringify):
            # assert isinstance(node.expr, cwast.Id)
            return cwast.ValString(f'r"{node.expr}"', x_srcloc=node.x_srcloc)

        assert isinstance(node, cwast.MacroInvoke)
        symtab: SymTab = node.x_import.x_module.x_symtab
        macro = symtab.resolve_macro(
            node,  builtin_syms,  node.name.IsQualifiedName())
        if macro is None:
            cwast.CompilerError(
                node.x_srcloc, f"invocation of unknown macro `{node.name}`")
        node = macros.ExpandMacro(node, macro, ctx)
        nesting += 1

    assert cwast.NF.TO_BE_EXPANDED not in node.FLAGS, node
    # recurse and resolve any expandables
    FindAndExpandMacrosRecursively(node, builtin_syms, nesting + 1, ctx)
    # pp_sexpr.PrettyPrint(exp)
    return node


def FindAndExpandMacrosRecursively(node, builtin_syms, nesting: int, ctx: macros.MacroContext):

    def replacer(node: Any):
        nonlocal builtin_syms, nesting, ctx
        if cwast.NF.TO_BE_EXPANDED in node.FLAGS:
            return ExpandMacroOrMacroLike(node, builtin_syms, nesting, ctx)

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def ResolveSymbolsInsideFunctionsRecursively(
        node, symtab: SymTab, builtin_syms: SymTab, scopes: list[dict]):

    def record_local_sym(node):
        name = node.name
        logger.debug("recording local symbol: %s", node)
        if name in scopes[-1]:
            cwast.CompilerError(node.x_srcloc,
                                f"redefinition of symbol: {name}")
        scopes[-1][name] = node
        symtab.AddLocalSym(name, node)

    def visitor(node: Any, nfd: cwast.NFD):
        nonlocal builtin_syms, scopes
        if isinstance(node, cwast.Id) and nfd.name != "field":
            _ResolveSymbolInsideFunction(node, builtin_syms, scopes)
        if isinstance(node, cwast.DefVar) and not node.name.IsMacroVar():
            record_local_sym(node)

    def scope_enter(node: Any, nfd: cwast.NFD):
        nonlocal scopes
        logger.debug("push scope for %s: %s", node, nfd.name)
        scopes.append({})
        if isinstance(node, cwast.DefFun):
            for p in node.params:
                if isinstance(p, cwast.FunParam):
                    record_local_sym(p)

    def scope_exit(node: Any, nfd: cwast.NFD):
        nonlocal scopes, symtab
        logger.debug("pop scope for %s: %s", node, nfd.name)
        for name in scopes[-1].keys():
            symtab.DelSym(name)
        scopes.pop(-1)

    cwast.VisitAstRecursivelyWithScopeTracking(
        node, visitor, scope_enter, scope_exit)


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


def VerifyASTSymbolsRecursively(node):
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


def _SetTargetFieldRecursively(node):
    parents = []

    def visitor_pre(node, _):
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

    def visitor_post(node, _):
        nonlocal parents
        parents.pop(-1)

    cwast.VisitAstRecursivelyPreAndPost(
        node, visitor_pre, visitor_post)


def ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(mod_topo_order: Sequence[cwast.DefMod],
                                                       builtin_syms: SymTab,
                                                       must_resolve_all):
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro)):
                logger.info("Resolving global object: %s", node)
                _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, builtin_syms, must_resolve_all)


def MacroExpansionDecorateASTWithSymbols(
        mod_topo_order: list[cwast.DefMod], builtin_symtab: SymTab, fun_id_gens: identifier.IdGenCache):
    """
    At this point every DefMod has a symtable populated with the global symbols
    and the Imports. All Imports have a valid x_module field.
    Ids that are not inside DefFuns have their x_symbol fields set.

    * expand macros recursively (macros are global symbols)
    * reolve symbols within functions (= setting x_symbol)
    """

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro)):
                logger.info("Resolving global object: %s", node)
                _ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, builtin_symtab, True)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun):
                logger.info("Expanding macros in: %s", node.name)
                ctx = macros.MacroContext(fun_id_gens.Get(node))
                FindAndExpandMacrosRecursively(node, builtin_symtab, 0, ctx)

    for mod in mod_topo_order:
        logger.info("Resolving symbols inside module: %s", mod.name)
        # we wait until macro expansion with this
        _SetTargetFieldRecursively(mod)

        symtab = mod.x_symtab
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun)):
                logger.info("Resolving symbols inside fun: %s", node.name)
                scopes: list[dict] = []
                ResolveSymbolsInsideFunctionsRecursively(
                    node, symtab, builtin_symtab, scopes)
                assert not scopes

    for mod in mod_topo_order:
        VerifyASTSymbolsRecursively(mod)


def IterateValRec(points: list[cwast.ValPoint], def_rec: cwast.CanonType):
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


def IterateValArray(inits, width, srcloc):
    curr_val = 0
    for init in inits:
        assert isinstance(init, cwast.ValPoint)
        if isinstance(init.point, cwast.ValAuto):
            yield curr_val, init
            curr_val += 1
            continue
        index = init.point.x_value
        assert isinstance(index, int)
        while curr_val < index:
            yield curr_val, None
            curr_val += 1
        yield curr_val, init
        curr_val += 1
    if curr_val > width:
        cwast.CompilerError(
            srcloc, f"Out of bounds array access at {curr_val}. Array size is  {width}")
    while curr_val < width:
        yield curr_val, None
        curr_val += 1


# for now no DefEnum
_NORMALIZED_NODES_FOR_MOD_ARGS = (cwast.DefFun, cwast.DefRec, cwast.TypeUnion,
                                  cwast.DefType,
                                  cwast.TypeBase, cwast.TypePtr, cwast.TypeSpan,
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


_GENERIC_DUMMY_MODULE = cwast.NAME.FromStr("GENERIC")


def SpecializeGenericModule(mod: cwast.DefMod, args: list[Any]) -> cwast.DefMod:
    assert len(mod.params_mod) == len(args), f"{len(mod.params_mod)} vs {len(args)} {type(args)}"
    translation: dict[cwast.NAME, Any] = {}
    for p, a in zip(mod.params_mod, args):
        sl = p.x_srcloc
        if isinstance(a, cwast.DefFun):
            assert p.mod_param_kind is cwast.MOD_PARAM_KIND.CONST_EXPR
            translation[p.name] = cwast.Id(
                _GENERIC_DUMMY_MODULE, a.name, None, x_symbol=a, x_srcloc=sl)
        elif isinstance(a, (cwast.DefRec, cwast.DefType)):
            translation[p.name] = cwast.Id(
                _GENERIC_DUMMY_MODULE, a.name, None, x_symbol=a, x_srcloc=sl)
        elif isinstance(a, (cwast.ValFalse, cwast.ValTrue, cwast.ValNum, cwast.ValVoid)):
            translation[p.name] = a
        else:
            assert cwast.NF.TYPE_CORPUS in a.FLAGS
            translation[p.name] = a

    mod.params_mod.clear()

    def replacer(node, _parent, _field):
        nonlocal translation
        if not isinstance(node, cwast.MacroId):
            return None
        name = node.name
        assert name.IsMacroVar(), f" non macro name: {node}"
        t = translation[name]

        return cwast.CloneNodeRecursively(t, {}, {})

    cwast.MaybeReplaceAstRecursivelyWithParentPost(mod, replacer)
    return mod
############################################################
#
############################################################


def main(argv: list[str]):
    assert len(argv) == 1
    fn = argv[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    cwd = os.getcwd()
    mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
    main = str(pathlib.Path(fn).resolve())
    mp.ReadModulesRecursively([main], add_builtin=fn != "Lib/builtin")
    mod_topo_order = mp.ModulesInTopologicalOrder()
    for mod in mod_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    fun_id_gens = identifier.IdGenCache()
    MacroExpansionDecorateASTWithSymbols(
        mod_topo_order, mp.BuiltinSymtab(), fun_id_gens)
    for ast in mod_topo_order:
        cwast.CheckAST(ast, set())
        VerifyASTSymbolsRecursively(ast)
        pp_sexpr.PrettyPrint(ast, sys.stdout)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool

    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)
    macros.logger.setLevel(logging.INFO)

    main(sys.argv[1:])
