#!/bin/env python3

import dataclasses
import pathlib
import logging
import collections
import heapq
import enum

from FE import cwast
from FE import parse_sexpr
from FE import symbolize
from FE import parse

from typing import Optional, Sequence, Any, Callable

Path = pathlib.PurePath

ModId = tuple[Path, ...]

logger = logging.getLogger(__name__)


def _GetQualifierIfPresent(name: str) -> Optional[cwast.NAME]:
    tokens = name.split(cwast.ID_PATH_SEPARATOR)
    if len(tokens) == 2:
        return cwast.NAME.Make(tokens[0])
    assert 1 == len(tokens)
    return None


def _ResolveImportsForQualifers(mod: cwast.DefMod):
    """Set the x_import field.

    We do this even for unqualified names using a `dummy_import`.
    This is important for macros whose
    syntax tree might get copied into a different from where it originated.
    """
    imports: dict[cwast.NAME, cwast.Import] = {}

    def visitor(node: Any):
        nonlocal imports
        if isinstance(node, cwast.Import):
            # assert node.x_module != cwast.INVALID_MOD
            name = node.name
            if name in imports:
                cwast.CompilerError(node.x_srcloc, f"duplicate import {name}")
            imports[name] = node
        elif isinstance(node, (cwast.DefFun, cwast.Id, cwast.MacroInvoke)):
            q = _GetQualifierIfPresent(node.name.name)
            if q:
                if q not in imports:
                    cwast.CompilerError(
                        node.x_srcloc, f"unkown module {repr(q)}")
                node.x_import = imports[q]
                node.name = node.name.GetSymbolNameWithoutQualifier()

    cwast.VisitAstRecursivelyPost(mod, visitor)


def _ExtractSymTabPopulatedWithGlobals(mod: cwast.DefMod) -> symbolize.SymTab:
    symtab = symbolize.SymTab()
    assert isinstance(mod, cwast.DefMod), mod
    logger.info("Processing %s", mod)
    # pass 1: get all the top level symbols
    for node in mod.body_mod:
        if not isinstance(node, (cwast.DefFun, cwast.DefMacro, cwast.DefGlobal,
                                 cwast.DefRec, cwast.DefEnum, cwast.DefType)):
            continue

        name: cwast.NAME = node.name
        # we only record the first occurrence of a poly functions which is why
        # only that function's visibility setting matters
        if isinstance(node, cwast.DefFun) and node.poly:
            if node.x_import or symtab.has_sym(name):
                continue
        symtab.add_with_dup_check(name, node)
    return symtab


EXTENSION_CWS = ".cws"
EXTENSION_CW = ".cw"


# def AreEqualNormalizedModParam(a, b) -> bool:
#     if a is None or b is None:
#         return False
#     if a is not type(b):
#         return False
#     if a is b:
#         return True

#     return False


def _SpecializeGenericModule(mod: cwast.DefMod, args: list[Any]):
    """"Note, this only add adds resolved Id Nodes"""
    assert len(mod.params_mod) == len(
        args), f"{len(mod.params_mod)} vs {len(args)} {type(args)}"
    arg_map: dict[cwast.NAME, Any] = {}
    for p, a in zip(mod.params_mod, args):
        if isinstance(a, (cwast.DefFun, cwast.DefRec, cwast.DefType, cwast.DefEnum)):
            arg_map[p.name] = cwast.Id(
                a.name, None, x_symbol=a, x_srcloc=p.x_srcloc)
        elif isinstance(a, (cwast.ValNum, cwast.ValVoid)):
            arg_map[p.name] = a
        else:
            assert cwast.NF.TYPE_CORPUS in a.FLAGS
            arg_map[p.name] = a

    mod.params_mod.clear()

    def replacer(node, _parent):
        nonlocal arg_map
        if not isinstance(node, cwast.MacroId):
            return None
        name = node.name
        assert name.IsMacroVar(), f" non macro name: {node}"
        t = arg_map[name]

        return cwast.CloneNodeRecursively(t, {}, {})

    cwast.MaybeReplaceAstRecursivelyWithParentPost(mod, replacer)


_NORMALIZED_NODES_FOR_MOD_ARGS = (cwast.DefFun, cwast.DefRec, cwast.DefEnum,
                                  #
                                  cwast.TypeUnion, cwast.TypeBase, cwast.TypePtr, cwast.TypeSpan,
                                  #
                                  cwast.ValNum, cwast.ValVoid)


def _NormalizeModArgOneStep(node) -> Any:
    """Returns `node` if no further normalization is impossible

    Returns `None`, if normalization cannot proceed at the moment
    because of unresolved symbols.

    In the future this could also include simple exressions.
    DefGlobal which are constant are probably fine too

    """
    if isinstance(node, cwast.Id):
        return node.x_symbol  # note, this may be None
    elif isinstance(node, cwast.DefType):
        if node.wrapped:
            return node
        else:
            return node.type
    elif isinstance(node, _NORMALIZED_NODES_FOR_MOD_ARGS):
        return node
    else:
        assert False, f"unexpected ModParam type: {type(node)}"


class _ImportInfo:
    def __init__(self, import_node: cwast.Import):
        self.import_node = import_node
        # the normalized args are None initially because they have not been normalized
        self.normalized_args = import_node.args_mod

    def HasBeenResolved(self) -> bool:
        return self.import_node.x_module != cwast.INVALID_MOD

    def TryToNormalizeModArgs(self) -> bool:
        for i, n in enumerate(self.normalized_args):
            while True:
                x = _NormalizeModArgOneStep(n)
                if not x:
                    return False
                elif x is n:
                    break
                else:
                    self.normalized_args[i] = x  # record incremental progress
                    n = x
        return True

    def ArgString(self) -> str:
        return ' '.join([f"{_FormatModArg(a)}->{_FormatModArg(n)}"
                         for a, n in zip(self.import_node.args_mod, self.normalized_args)])

    def ResolveImport(self, imported_mod: cwast.DefMod):
        # we have specialized the module for the given args so the args are no
        # longer necessary
        self.import_node.args_mod.clear()
        self.import_node.x_module = imported_mod


class _ModInfo:
    def __init__(self, mid: ModId, mod: cwast.DefMod, symtab: symbolize.SymTab):
        self.mid = mid
        self.mod = mod
        self.symtab = symtab

        self.imports: list[_ImportInfo] = [
            _ImportInfo(node) for node in mod.body_mod if isinstance(node, cwast.Import)]

    def __str__(self):
        return f"{self.name}:{self.mid}"


def _ModulesInTopologicalOrder(mod_infos: Sequence[_ModInfo]) -> list[cwast.DefMod]:
    """The order is also deterministic

    This means modules cannot have circular dependencies except for module arguments
    to parameterized modules which are ignored in the topo order.
    """
    deps_in: dict[cwast.DefMod, list[cwast.DefMod]
                  ] = collections.defaultdict(list)
    deps_out: dict[cwast.DefMod, list[cwast.DefMod]
                   ] = collections.defaultdict(list)

    # populate deps_in/deps_out
    for mi in mod_infos:
        mod = mi.mod
        assert isinstance(mod, cwast.DefMod)
        for import_info in mi.imports:
            node = import_info.import_node
            importee = node.x_module
            assert isinstance(importee, cwast.DefMod), node

            logger.info(
                "found mod deps [%s] imported by [%s]", importee, mod)
            deps_in[mod].append(importee)
            deps_out[importee].append(mod)

    # start with candidates with no incoming deps, candidates is sorted by
    # mod.name to make it deterministic
    candidates: list[cwast.DefMod] = []
    for mi in mod_infos:
        mod = mi.mod
        assert isinstance(mod, cwast.DefMod)
        if not deps_in[mod]:
            logger.info("found leaf mod [%s]", mod)
            heapq.heappush(candidates, mod)

    # topological order
    out: list[cwast.DefMod] = []
    while len(out) != len(mod_infos):
        assert candidates
        x = heapq.heappop(candidates)
        logger.info("picking next mod: %s", x)
        out.append(x)

        for importer in deps_out[x]:
            deps_in[importer].remove(x)
            if not deps_in[importer]:
                heapq.heappush(candidates, importer)
    return out


def _FormatModArg(node) -> str:
    if node is None:
        return "None"
    return cwast.NODE_NAME(node)


def _ModUniquePathName(root: Path,
                       curr: Optional[Path],
                       pathname: str) -> Path:
    """
    Provide a unique id for a module.

    Currently thid is essentially the absolute pathanme.
    `curr` is the handle of the curr module will be used relative paths.

    Other options (not yet explored): use checksums
    """
    if pathname.startswith("/"):
        return pathlib.Path(pathname).resolve()
    elif pathname.startswith("."):
        # drop the libname from curr
        pc = pathlib.Path(curr).parent
        return (pc / pathname).resolve()
    else:
        return pathlib.Path(root / pathname).resolve()


_MAIN_FUN_NAME = cwast.NAME.Make("main")


def _ReadMod(path: Path) -> cwast.DefMod:
    """Overload"""
    fn = str(path) + EXTENSION_CW
    if pathlib.Path(fn).exists():
        mod = parse.ReadModFromStream(open(fn, encoding="utf8"), fn, path.name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    fn = str(path) + EXTENSION_CWS
    if pathlib.Path(fn).exists():
        mod = parse_sexpr.ReadModFromStream(
            open(fn, encoding="utf8"), fn, path.name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    assert False, f"module {str(path)} does not exist"


class _ModPoolState:
    def __init__(self):
        # all modules keyed by ModHandle
        self._all_mods: dict[ModId, _ModInfo] = {}
        self._raw_generic: dict[Path, cwast.DefMod] = {}
        self.gen_mod_uid: int = 0

    def ReadMod(self, path: Path) -> cwast.DefMod:
        return self._read_mod_fun(path)

    def AddModInfo(self, path: Path, args: list, mod: cwast.DefMod) -> _ModInfo:
        symtab = _ExtractSymTabPopulatedWithGlobals(mod)
        _ResolveImportsForQualifers(mod)
        mid = (path, *args)
        mod_info = _ModInfo(mid, mod, symtab)
        # print("Adding new mod: ", mid[0].name, mid[1:])
        logger.info("Adding new mod: %s", mod_info)
        self._all_mods[mid] = mod_info

        mod.x_symtab = mod_info.symtab
        return mod_info

    def GetModInfo(self, mid: ModId) -> Optional[_ModInfo]:
        return self._all_mods.get(mid)

    def AllMods(self) -> Sequence[cwast.DefMod]:
        return [info.mod for info in self._all_mods.values()]

    def AllModInfos(self) -> Sequence[_ModInfo]:
        return self._all_mods.values()

    def GetCloneOfGenericMod(self, path: Path, read_mod_fun: Callable) -> cwast.DefMod:
        generic_mod = self._raw_generic.get(path)
        if not generic_mod:
            logger.info("reading raw generic from: %s", path)
            generic_mod = read_mod_fun(path)
            self._raw_generic[path] = generic_mod
        mod = cwast.CloneNodeRecursively(generic_mod, {}, {})
        self.gen_mod_uid += 1
        mod.name = cwast.NAME.Make(f"{generic_mod.name}/{self.gen_mod_uid}")
        return mod


def _MainEntryFun(mod: cwast.DefMod) -> Optional[cwast.DefFun]:
    for fun in mod.body_mod:
        if isinstance(fun, cwast.DefFun) and fun.name == _MAIN_FUN_NAME:
            return fun
    return None


@dataclasses.dataclass()
class ModPool:
    builtin_symtab: symbolize.SymTab = dataclasses.field(
        default_factory=symbolize.SymTab)
    main_fun: Optional[cwast.DefFun] = None
    mods_in_topo_order: list[cwast.DefMod] = dataclasses.field(
        default_factory=list)


def _ResolvePolyMods(mods: list[cwast.DefMod]):

    for mod in mods:
        logger.info("Resolving symbols inside module: %s", mod.name)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun) and node.poly:
                if node.x_import:
                    node.x_poly_mod = node.x_import.x_module
                else:
                    node.x_poly_mod = mod


def ReadModulesRecursively(root: Path,
                           seed_modules: list[str], add_builtin: bool, read_mod_fun=_ReadMod) -> ModPool:
    """Reads all the seed_modules and their imports, also instantiates generic modules

    Will set the following Node fields of all read Modules as a side-effect:
        * x_symtab on DefMod nodes (includes creation of SymTabs for all topelevel symbols)
        * x_import field for all DefFun, DefMacro and Id nodes
        * x_module field of all Import nodes
        * x_symbol field for Id Nodes for global symbols (done in two phases)


    For polymorphic functions x_symbol will point to a canonical DefFun instance.
    After typing it will be replaced with the correct DefFun instance.

    """
    state = _ModPoolState()
    out = ModPool()

    active: list[_ModInfo] = []
    if add_builtin:
        path = _ModUniquePathName(root, None, "builtin")
        mod = read_mod_fun(path)
        mod_info = state.AddModInfo(path, [], mod)
        assert mod_info.mod.builtin
        active.append(mod_info)
        assert out.builtin_symtab.is_empty()
        out.builtin_symtab = mod_info.symtab

    for pathname in seed_modules:
        assert not pathname.startswith(".")
        path = _ModUniquePathName(root, None, pathname)

        assert state.GetModInfo(
            (path,)) is None, f"duplicate module {pathname}"
        mod = read_mod_fun(path)
        mod_info = state.AddModInfo(path, [], mod)
        if not out.main_fun:
            out.main_fun = _MainEntryFun(mod_info.mod)
        active.append(mod_info)
        assert not mod_info.mod.builtin

    # Fix point computation for resolving imports
    # -------------------------------------------
    # for each "active" module we look at all its imports
    #    we then try to read each imported module - if it has not already been imported.
    #    however, for parameterized imports, this may not be possible yet.
    #  Once all imports have been resolved, the module is no longer "active"
    while active:
        new_active: list[_ModInfo] = []
        # this probably needs to be a fix point computation as well
        symbolize.ResolveGlobalAndImportedSymbolsOutsideFunctionsAndMacros(
            state.AllMods(), out.builtin_symtab)
        for mod_info in active:
            assert isinstance(mod_info, _ModInfo), mod_info
            logger.info("start resolving imports for %s", mod_info)
            num_unresolved_imports = 0
            for import_info in mod_info.imports:
                import_node = import_info.import_node
                if import_info.HasBeenResolved():
                    continue
                if import_node.args_mod and not import_info.TryToNormalizeModArgs():
                    num_unresolved_imports += 1
                    continue
                pathname = import_node.path
                if pathname:
                    if pathname.startswith('"'):
                        pathname = pathname[1:-1]
                else:
                    pathname = str(import_node.name)
                path = _ModUniquePathName(root, mod_info.mid[0], pathname)
                if import_node.args_mod:
                    logger.info(
                        "generic module: %s %s", import_node.name, import_info.ArgString())

                    mod = state.GetCloneOfGenericMod(path, read_mod_fun)
                    _SpecializeGenericModule(mod, import_info.normalized_args)
                    mi = state.AddModInfo(
                        path, import_info.normalized_args, mod)
                    new_active.append(mi)
                else:
                    # see if the module has been read already
                    mi = state.GetModInfo((path,))
                    if not mi:
                        mod = read_mod_fun(path)
                        mi = state.AddModInfo(path, [], mod)
                        new_active.append(mi)
                logger.info(
                    f"in {mod_info.mod} resolving inport of {mi.mod.name}")
                import_info.ResolveImport(mi.mod)

            if num_unresolved_imports:
                new_active.append(mod_info)
            logger.info("finish resolving imports for %s - unresolved: %d",
                        mod_info, num_unresolved_imports)

        active = new_active

    out.mods_in_topo_order = _ModulesInTopologicalOrder(state.AllModInfos())
    _ResolvePolyMods(out.mods_in_topo_order)
    symbolize.ResolveGlobalAndImportedSymbolsInsideFunctionsAndMacros(
        out.mods_in_topo_order, out.builtin_symtab)
    # after resolving all global symbols there is not need for Imports
    # anymore
    for mod in out.mods_in_topo_order:
        cwast.RemoveNodesOfType(mod, cwast.Import)

    return out


if __name__ == "__main__":
    import os
    import sys

    def main(argv: list[str]):
        assert len(argv) == 1
        assert argv[0].endswith(EXTENSION_CW)

        cwd = os.getcwd()
        ReadModulesRecursively(pathlib.Path(cwd) / "Lib",
                               ["builtin", str(pathlib.Path(argv[0][:-3]).resolve())], False)

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)

    main(sys.argv[1:])
