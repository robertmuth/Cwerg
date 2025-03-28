#!/bin/env python3

import pathlib
import logging
import collections
import heapq

from FE import cwast
from FE import parse_sexpr
from FE import symbolize
from FE import parse

from typing import Optional, Sequence, Any

Path = pathlib.PurePath

ModId = tuple[Path, ...]

logger = logging.getLogger(__name__)


def _GetQualifierIfPresent(name: str) -> Optional[cwast.NAME]:
    tokens = name.split(cwast.ID_PATH_SEPARATOR)
    if len(tokens) == 2:
        return cwast.NAME.FromStr(tokens[0])
    assert 1 == len(tokens)
    return None


def AnnotateImportsForQualifers(mod: cwast.DefMod):
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
        elif isinstance(node, cwast.DefFun):
            if annotate(node, _GetQualifierIfPresent(node.name.name)):
                # only polymorphic functions may have qualifiers
                assert node.poly
                node.name = node.name.GetSymbolNameWithoutQualifier()
        elif isinstance(node, cwast.MacroInvoke):
            if annotate(node, _GetQualifierIfPresent(node.name.name)):
                node.name = node.name.GetSymbolNameWithoutQualifier()
        elif isinstance(node, cwast.Id):
            if annotate(node, node.mod_name):
                pass

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
            if not node.x_import.name.IsSelfImport() or symtab.has_sym(name):
                continue
        symtab.add_with_dup_check(name, node)
    return symtab


EXTENSION_CWS = ".cws"
EXTENSION_CW = ".cw"


class ModInfo:
    def __init__(self, mid: ModId, mod: cwast.DefMod, symtab: symbolize.SymTab):
        self.mid = mid
        self.mod = mod
        self.symtab = symtab
        # the second component holds the normalized args
        self.imports: list[tuple[cwast.Import, Any]] = [
            (node, [None] * len(node.args_mod)) for node in mod.body_mod if isinstance(node, cwast.Import)]

    def __str__(self):
        return f"{self.name}:{self.mid}"


def ModulesInTopologicalOrder(mod_infos: Sequence[ModInfo]) -> list[cwast.DefMod]:
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
        for node, _ in mi.imports:
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


def _TryToNormalizeModArgs(args, normalized) -> bool:
    count = 0
    for i, n in enumerate(normalized):
        if n is None:
            n = symbolize.NormalizeModParam(args[i])
            if n:
                normalized[i] = n
                count += 1
        else:
            count += 1
    return count == len(args)


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


def _ReadMod(handle: Path, name: str) -> cwast.DefMod:
    """Overload"""
    fn = str(handle) + EXTENSION_CW
    if pathlib.Path(fn).exists():
        mod = parse.ReadModFromStream(open(fn, encoding="utf8"), fn, name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    fn = str(handle) + EXTENSION_CWS
    if pathlib.Path(fn).exists():
        mod = parse_sexpr.ReadModFromStream(
            open(fn, encoding="utf8"), fn, name)
        assert isinstance(mod, cwast.DefMod)
        return mod
    assert False, f"module {str(handle)} does not exist"


class ModPool:
    """
    Will set the following fields:
        * x_import field of the Import nodes
        * x_module (name) field of the DefMod nodes
    """

    def __init__(self, root: Path, read_mod_fun=_ReadMod):
        logger.info("Init ModPool with: %s", root)
        self._root: Path = root
        self._read_mod_fun = read_mod_fun
        # all modules keyed by ModHandle
        self._all_mods: dict[ModId, ModInfo] = {}
        self._taken_names: set[str] = set()
        self._raw_generic: dict[Path, cwast.DefMod] = {}
        #
        self._builtin_modinfo: Optional[ModInfo] = None
        self._main_modinfo: Optional[ModInfo] = None

    def __str__(self):
        return f"root={self._root}"

    def _AddModInfoCommon(self, path: Path, args: list, mod: cwast.DefMod, symtab) -> ModInfo:
        mid = (path, *args)
        name = path.name
        mod_info = ModInfo(mid, mod, symtab)
        # print("Adding new mod: ", mid[0].name, mid[1:])
        logger.info("Adding new mod: %s", mod_info)
        self._all_mods[mid] = mod_info

        assert name not in self._taken_names
        # TODO: deal with generics and possible name clashes
        self._taken_names.add(name)
        mod.x_symtab = mod_info.symtab
        return mod_info

    def _AddModInfoSimple(self, path: Path, name: str) -> ModInfo:
        """Register regular module"""
        mod = self._read_mod_fun(path, name)
        AnnotateImportsForQualifers(mod)
        symtab = _ExtractSymTabPopulatedWithGlobals(mod)
        return self._AddModInfoCommon(path, [], mod, symtab)

    def _AddModInfoForGeneric(self, path: Path, args: list, name: str) -> ModInfo:
        """Specialize Generic Mod and register it"""
        generic_mod = self._raw_generic.get(path)
        if not generic_mod:
            logger.info("reading raw generic from: %s", path)
            generic_mod = self._read_mod_fun(path, name)
            self._raw_generic[path] = generic_mod
        mod = cwast.CloneNodeRecursively(generic_mod, {}, {})
        AnnotateImportsForQualifers(mod)
        symtab = _ExtractSymTabPopulatedWithGlobals(mod)
        return self._AddModInfoCommon(path, args, symbolize.SpecializeGenericModule(mod, args), symtab)

    def MainEntryFun(self) -> cwast.DefFun:
        assert self._main_modinfo
        for fun in self._main_modinfo.mod.body_mod:
            if isinstance(fun, cwast.DefFun) and fun.name == _MAIN_FUN_NAME:
                return fun
        assert False

    def BuiltinSymtab(self):
        if self._builtin_modinfo:
            return self._builtin_modinfo.symtab
        return symbolize.SymTab()

    def ReadModulesRecursively(self, seed_modules: list[str], add_builtin: bool):
        active: list[ModInfo] = []
        if add_builtin:
            mod_name = "builtin"
            path = _ModUniquePathName(self._root, None, mod_name)
            mod_info = self._AddModInfoSimple(path, mod_name)
            assert mod_info.mod.builtin
            active.append(mod_info)
            assert not self._builtin_modinfo
            self._builtin_modinfo = mod_info

        for pathname in seed_modules:
            assert not pathname.startswith(".")
            path = _ModUniquePathName(self._root, None, pathname)
            mod_name = path.name

            assert self._all_mods.get(
                (path,)) is None, f"duplicate module {pathname}"
            mod_info = self._AddModInfoSimple(path, mod_name)
            if not self._main_modinfo:
                self._main_modinfo = mod_info
            active.append(mod_info)
            assert not mod_info.mod.builtin

        # fix point computation for resolving imports
        while active:
            new_active: list[ModInfo] = []
            seen_change = False
            # this probably needs to be a fix point computation as well
            symbolize.ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                [m.mod for m in self._all_mods.values()], self.BuiltinSymtab(), False)
            for mod_info in active:
                assert isinstance(mod_info, ModInfo), mod_info
                logger.info("start resolving imports for %s", mod_info)
                num_unresolved = 0
                for import_node, normalized_args in mod_info.imports:
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
                        done = _TryToNormalizeModArgs(
                            import_node.args_mod, normalized_args)
                        args_strs = [f"{_FormatModArg(a)}->{_FormatModArg(n)}"
                                     for a, n in zip(import_node.args_mod, normalized_args)]
                        logger.info(
                            "generic module: [%s] %s %s", done, import_node.name, ','.join(args_strs))
                        if done:
                            path = _ModUniquePathName(
                                self._root, mod_info.mid[0], pathname)
                            mod_name = path.name
                            import_mod_info = self._AddModInfoForGeneric(
                                path, normalized_args, mod_name)
                            import_node.args_mod.clear()
                            import_node.x_module = import_mod_info.mod
                            new_active.append(import_mod_info)
                            seen_change = True
                        else:
                            num_unresolved += 1
                    else:
                        path = _ModUniquePathName(
                            self._root, mod_info.mid[0], pathname)
                        import_mod_info = self._all_mods.get((path,))
                        if not import_mod_info:
                            mod_name = path.name
                            import_mod_info = self._AddModInfoSimple(
                                path, mod_name)
                            new_active.append(import_mod_info)
                            seen_change = True
                        logger.info(
                            f"in {mod_info.mod} resolving inport of {import_mod_info.mod.name}")
                        import_node.x_module = import_mod_info.mod
                if num_unresolved:
                    new_active.append(mod_info)
                logger.info("finish resolving imports for %s - unresolved: %d",
                            mod_info, num_unresolved)

            if not seen_change and new_active:
                assert False, "module import does not terminate"
            active = new_active

    def ModulesInTopologicalOrder(self) -> list[cwast.DefMod]:
        return ModulesInTopologicalOrder(self._all_mods.values())


if __name__ == "__main__":
    import os
    import sys

    def main(argv: list[str]):
        assert len(argv) == 1
        assert argv[0].endswith(EXTENSION_CW)

        cwd = os.getcwd()
        mp: ModPool = ModPool(pathlib.Path(cwd) / "Lib")
        mp.ReadModulesRecursively(
            ["builtin", str(pathlib.Path(argv[0][:-3]).resolve())], False)

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)

    main(sys.argv[1:])
