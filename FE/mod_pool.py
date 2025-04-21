#!/bin/env python3

import dataclasses
import pathlib
import logging
import collections
import heapq

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
        return cwast.NAME.FromStr(tokens[0])
    assert 1 == len(tokens)
    return None


def _ResolveImportsForQualifers(mod: cwast.DefMod):
    """Set the x_import field.

    We do this even for unqualified names using a `dummy_import`.
    This is important for macros whose
    syntax tree might get copied into a different from where it originated.
    """
    imports: dict[cwast.NAME, cwast.Import] = {}
    self_import = cwast.Import(cwast.NAME.SelfImport(), "", [], x_module=mod)

    def annotate(node, q) -> bool:
        if q:
            if q not in imports:
                cwast.CompilerError(node.x_srcloc, f"unkown module {repr(q)}")
            node.x_import = imports[q]
            return True
        else:
            node.x_import = self_import
            return False

    def visitor(node: Any):
        nonlocal imports, self_import
        if isinstance(node, cwast.Import):
            name = node.name
            if name in imports:
                cwast.CompilerError(node.x_srcloc, f"duplicate import {name}")
            imports[name] = node
        elif isinstance(node, (cwast.DefFun, cwast.Id, cwast.MacroInvoke)):
            if annotate(node, _GetQualifierIfPresent(node.name.name)):
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
            if symbolize.HasImportedSymbolReference(node) or symtab.has_sym(name):
                continue
        symtab.add_with_dup_check(name, node)
    return symtab


EXTENSION_CWS = ".cws"
EXTENSION_CW = ".cw"

# for now no DefEnum
_NORMALIZED_NODES_FOR_MOD_ARGS = (cwast.DefFun, cwast.DefRec, cwast.TypeUnion,
                                  cwast.DefType,
                                  cwast.TypeBase, cwast.TypePtr, cwast.TypeSpan,
                                  cwast.ValFalse, cwast.ValTrue, cwast.ValNum, cwast.ValVoid)


def _IsNormalizeModParam(node):
    if isinstance(node, _NORMALIZED_NODES_FOR_MOD_ARGS):
        return True
    elif isinstance(node, cwast.DefType) and node.wrapped:
        return True
    else:
        return False


def _NormalizeModParam(node):
    if _IsNormalizeModParam(node):
        return node
    elif isinstance(node, cwast.DefType) and not node.wrapped:
        return _NormalizeModParam(node.type)
    elif isinstance(node, cwast.Id):
        if node.x_symbol:
            return _NormalizeModParam(node.x_symbol)
        else:
            return None
    else:
        assert False, f"NYI: {node}"


# def AreEqualNormalizedModParam(a, b) -> bool:
#     if a is None or b is None:
#         return False
#     if a is not type(b):
#         return False
#     if a is b:
#         return True

#     return False


def _SpecializeGenericModule(mod: cwast.DefMod, args: list[Any]) -> cwast.DefMod:
    assert len(mod.params_mod) == len(
        args), f"{len(mod.params_mod)} vs {len(args)} {type(args)}"
    translation: dict[cwast.NAME, Any] = {}
    for p, a in zip(mod.params_mod, args):
        sl = p.x_srcloc
        if isinstance(a, cwast.DefFun):
            assert p.mod_param_kind is cwast.MOD_PARAM_KIND.CONST_EXPR
            translation[p.name] = cwast.Id(
                a.name, None, x_symbol=a, x_srcloc=sl)
        elif isinstance(a, (cwast.DefRec, cwast.DefType)):
            translation[p.name] = cwast.Id(
                a.name, None, x_symbol=a, x_srcloc=sl)
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


class _ImportInfo:
    def __init__(self, import_node: cwast.Import):
        self.import_node = import_node
        # the normalized args are None initially because they have not been normalized
        self.normalized_args = [None] * len(import_node.args_mod)

    def TryToNormalizeArgs(self) -> bool:
        all_args_are_normalized = True
        for i, n in enumerate(self.normalized_args):
            if n is None:
                n = _NormalizeModParam(self.import_node.args_mod[i])
                if n:
                    self.normalized_args[i] = n
                else:
                    all_args_are_normalized = False
        return all_args_are_normalized

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
    candidates: list[tuple[str, cwast.DefMod]] = []
    for mi in mod_infos:
        mod = mi.mod
        assert isinstance(mod, cwast.DefMod)
        if not deps_in[mod]:
            logger.info("found leaf mod [%s]", mod)
            heapq.heappush(candidates, (str(mod.name), mod))

    # topological order
    out: list[cwast.DefMod] = []
    while len(out) != len(mod_infos):
        assert candidates
        _, x = heapq.heappop(candidates)
        logger.info("picking next mod: %s", x)
        out.append(x)

        for importer in deps_out[x]:
            deps_in[importer].remove(x)
            if not deps_in[importer]:
                heapq.heappush(candidates, (str(importer.name), importer))
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


_MAIN_FUN_NAME = cwast.NAME.FromStr("main")


def _ReadMod(handle: Path, mod_name: str) -> cwast.DefMod:
    """Overload"""
    fn = str(handle) + EXTENSION_CW
    if pathlib.Path(fn).exists():
        mod = parse.ReadModFromStream(open(fn, encoding="utf8"), fn, mod_name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    fn = str(handle) + EXTENSION_CWS
    if pathlib.Path(fn).exists():
        mod = parse_sexpr.ReadModFromStream(
            open(fn, encoding="utf8"), fn, mod_name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    assert False, f"module {str(handle)} does not exist"


@dataclasses.dataclass()
class _ModPoolState:
    read_mod_fun: Callable
    # all modules keyed by ModHandle
    all_mods: dict[ModId, _ModInfo] = dataclasses.field(default_factory=dict)
    taken_names: set[str] = dataclasses.field(default_factory=set)
    raw_generic: dict[Path, cwast.DefMod] = dataclasses.field(
        default_factory=dict)

    def AddModInfoCommon(self, path: Path, args: list, mod: cwast.DefMod, symtab) -> _ModInfo:
        mid = (path, *args)
        name = path.name
        mod_info = _ModInfo(mid, mod, symtab)
        # print("Adding new mod: ", mid[0].name, mid[1:])
        logger.info("Adding new mod: %s", mod_info)
        self.all_mods[mid] = mod_info

        assert name not in self.taken_names
        # TODO: deal with generics and possible name clashes
        self.taken_names.add(name)
        mod.x_symtab = mod_info.symtab
        return mod_info

    def GetModInfo(self, mid: ModId) -> Optional[_ModInfo]:
        return self.all_mods.get(mid)

    def AllMods(self) -> Sequence[cwast.DefMod]:
        return [info.mod for info in self.all_mods.values()]

    def AllModInfos(self) -> Sequence[_ModInfo]:
        return self.all_mods.values()

    def AddModInfoSimple(self, path: Path, mod_name: str) -> _ModInfo:
        """Register regular module"""
        mod = self.read_mod_fun(path, mod_name)
        _ResolveImportsForQualifers(mod)
        symtab = _ExtractSymTabPopulatedWithGlobals(mod)
        return self.AddModInfoCommon(path, [], mod, symtab)

    def AddModInfoForGeneric(self, path: Path, args: list, mod_name: str) -> _ModInfo:
        """Specialize Generic Mod and register it"""
        generic_mod = self.raw_generic.get(path)
        if not generic_mod:
            logger.info("reading raw generic from: %s", path)
            generic_mod = self.read_mod_fun(path, mod_name)
            self.raw_generic[path] = generic_mod
        mod = cwast.CloneNodeRecursively(generic_mod, {}, {})
        _ResolveImportsForQualifers(mod)
        symtab = _ExtractSymTabPopulatedWithGlobals(mod)
        return self.AddModInfoCommon(path, args, _SpecializeGenericModule(mod, args), symtab)


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


def ReadModulesRecursively(root: Path,
                           seed_modules: list[str], add_builtin: bool, read_mod_fun=_ReadMod) -> ModPool:
    """Reads all the seed_modules and their imports, also instantiates generic modules

    Will set the following Node fields of all read Modules as a side-effect:
        * x_symtab on DefMod nodes (includes creation of SymTabs for all topelevel symbols)
        * x_import field for all DefFun, DefMacro and Id nodes
        * x_module field of all Import nodes
        * x_symbol field for Id Nodes outside of Functions or Macros

    The setting of x_symbol fields facilitates specialization of generic modules.
    Setting the x_import fields has important consequences for Macro bodies:
    If an Id in the macro body references a symbol not defined prior in the body AND
    not defined in the function instantiating the macro then the symtab of the module containing
    the macro will be used for the symbol resolution.
    """
    state = _ModPoolState(read_mod_fun)
    out = ModPool()

    active: list[_ModInfo] = []
    if add_builtin:
        mod_name = "builtin"
        path = _ModUniquePathName(root, None, mod_name)
        mod_info = state.AddModInfoSimple(path, mod_name)
        assert mod_info.mod.builtin
        active.append(mod_info)
        assert out.builtin_symtab.is_empty()
        out.builtin_symtab = mod_info.symtab

    for pathname in seed_modules:
        assert not pathname.startswith(".")
        path = _ModUniquePathName(root, None, pathname)
        mod_name = path.name

        assert state.GetModInfo(
            (path,)) is None, f"duplicate module {pathname}"
        mod_info = state.AddModInfoSimple(path, mod_name)
        if not out.main_fun:
            out.main_fun = _MainEntryFun(mod_info.mod)
        active.append(mod_info)
        assert not mod_info.mod.builtin

    # fix point computation for resolving imports
    while active:
        new_active: list[_ModInfo] = []
        seen_change = False
        # this probably needs to be a fix point computation as well
        symbolize.ResolveSymbolsOutsideFunctionsAndMacros(
            state.AllMods(), out.builtin_symtab, False)
        for mod_info in active:
            assert isinstance(mod_info, _ModInfo), mod_info
            logger.info("start resolving imports for %s", mod_info)
            num_unresolved = 0
            for import_info in mod_info.imports:
                import_node = import_info.import_node
                if import_node.x_module != cwast.INVALID_MOD:
                    # import has been processed
                    continue
                pathname = import_node.path
                if pathname:
                    if pathname.startswith('"'):
                        pathname = pathname[1:-1]
                else:
                    pathname = str(import_node.name)
                if import_node.args_mod:
                    # import of generic module
                    done = import_info.TryToNormalizeArgs()
                    logger.info(
                        "generic module: [%s] %s %s", done, import_node.name, import_info.ArgString())
                    if done:
                        path = _ModUniquePathName(
                            root, mod_info.mid[0], pathname)
                        mi = state.AddModInfoForGeneric(
                            path, import_info.normalized_args, path.name)
                        import_info.ResolveImport(mi.mod)
                        new_active.append(mi)
                        seen_change = True
                    else:
                        num_unresolved += 1
                else:
                    path = _ModUniquePathName(
                        root, mod_info.mid[0], pathname)
                    mi = state.GetModInfo((path,))
                    if not mi:
                        mi = state.AddModInfoSimple(path, path.name)
                        new_active.append(mi)
                        seen_change = True
                    logger.info(
                        f"in {mod_info.mod} resolving inport of {mi.mod.name}")
                    import_info.ResolveImport(mi.mod)

            if num_unresolved:
                new_active.append(mod_info)
            logger.info("finish resolving imports for %s - unresolved: %d",
                        mod_info, num_unresolved)

        if not seen_change and new_active:
            assert False, "module import does not terminate"
        active = new_active

    out.mods_in_topo_order = _ModulesInTopologicalOrder(state.AllModInfos())
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
