#!/bin/env python3

import pathlib
import logging
import collections
import heapq

from FE import cwast
from FE import parse_sexpr
from FE import symbolize
from FE import parse

from typing import Optional, Sequence

ModId = tuple[pathlib.PurePath, ...]

logger = logging.getLogger(__name__)

EXTENSION_CWS = ".cws"
EXTENSION_CW = ".cw"


class ModInfo:
    def __init__(self, uid: ModId, mod: cwast.DefMod):
        self.uid = uid
        self.mod = mod
        # the second component holds the normalized args
        self.imports = [
            (node, [None] * len(node.args_mod)) for node in mod.body_mod if isinstance(node, cwast.Import)]

    def __str__(self):
        return f"{self.mod.x_modname}:{self.uid}"


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
    # mod.x_modname to make it deterministic
    candidates: list[tuple[str, cwast.DefMod]] = []
    for mi in mod_infos:
        mod = mi.mod
        assert isinstance(mod, cwast.DefMod)
        if not deps_in[mod]:
            logger.info("found leaf mod [%s]", mod)
            heapq.heappush(candidates, (mod.x_modname, mod))

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
                heapq.heappush(candidates, (importer.x_modname, importer))
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


def _ModUniquePathName(root: pathlib.PurePath,
                       curr: Optional[pathlib.PurePath],
                       pathname: str) -> pathlib.PurePath:
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
        return (root / pathname).resolve()



class ModPoolBase:
    """
    Will set the following fields:
        * x_import field of the Import nodes
        * x_module (name) field of the DefMod nodes
        * x_normalized field of the ModParam nodes
    (non parameterized imports)
    """

    def __init__(self, root: pathlib.Path):
        logger.info("Init ModPool with: %s", root)
        self._root: pathlib.Path = root
        # all modules keyed by ModHandle
        self._all_mods: dict[ModId, ModInfo] = {}
        self._main_mod: Optional[cwast.DefMod] = None
        self._taken_names: set[str] = set()
        self._raw_generic: dict[pathlib.PurePath, cwast.DefMod] = {}

    def __str__(self):
        return f"root={self._root}"

    def _AddModInfoCommon(self, mid: ModId, mod: cwast.DefMod) -> ModInfo:
        mod_info = ModInfo(mid, mod)
        #print("Adding new mod: ", mid[0].name, mid[1:])
        logger.info("Adding new mod: %s", mod_info)
        self._all_mods[mid] = mod_info
        name = mid[0].name
        assert name not in self._taken_names
        self._taken_names.add(name)
        mod_info.mod.x_modname = name
        return mod_info

    def _AddModInfoSimple(self, uid: ModId) -> ModInfo:
        """Register regular module"""
        assert isinstance(uid, tuple), uid
        mod = self._ReadMod(uid[0])
        cwast.AnnotateImportsForQualifers(mod)
        mod.x_symtab = symbolize.ExtractSymTabPopulatedWithGlobals(mod)
        return self._AddModInfoCommon(uid, mod)

    def _AddModInfoForGeneric(self, mid: ModId) -> ModInfo:
        """Specialize Generic Mod and register it"""
        path = mid[0]
        args = list(mid)[1:]
        generic_mod = self._raw_generic.get(path)
        if not generic_mod:
            logger.info("reading raw generic from: %s", path)
            generic_mod = self._ReadMod(path)
            self._raw_generic[path] = generic_mod
        mod = cwast.CloneNodeRecursively(generic_mod, {}, {})
        cwast.AnnotateImportsForQualifers(mod)
        mod.x_symtab = symbolize.ExtractSymTabPopulatedWithGlobals(mod)
        return self._AddModInfoCommon(mid, symbolize.SpecializeGenericModule(mod, args))

    def _FindModInfo(self, uid) -> Optional[ModInfo]:
        return self._all_mods.get(uid)

    def _ReadMod(self, _handle: pathlib.PurePath) -> cwast.DefMod:
        assert False, "to be implemented by derived class"

    def AllModInfos(self) -> Sequence[ModInfo]:
        return self._all_mods.values()

    def MainEntryFun(self) -> cwast.DefFun:
        assert self._main_mod
        for fun in self._main_mod.body_mod:
            if isinstance(fun, cwast.DefFun) and fun.name == "main":
                return fun
        assert False

    def ReadModulesRecursively(self, seed_modules: list[str], add_builtin: bool):
        active: list[ModInfo] = []
        if add_builtin:
            uid = (_ModUniquePathName(self._root, None, "builtin"),)
            mod_info = self._AddModInfoSimple(uid)
            active.append(mod_info)

        for pathname in seed_modules:
            assert not pathname.startswith(".")
            uid = (_ModUniquePathName(self._root, None, pathname),)
            assert self._FindModInfo(uid) is None, f"duplicate module {uid}"
            mod_info = self._AddModInfoSimple(uid)
            if not self._main_mod:
                self._main_mod =  mod_info.mod
            active.append(mod_info)

        buitin_syms = symbolize.GetSymTabForBuiltInOrEmpty(
            [m.mod for m in self.AllModInfos()])

        # fix point computation for resolving imports
        while active:
            new_active: list[ModInfo] = []
            seen_change = False
            # this probably needs to be a fix point computation as well
            symbolize.ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                [m.mod for m in self.AllModInfos()], buitin_syms, False)
            for mod_info in active:
                assert isinstance(mod_info, ModInfo), mod_info
                logger.info("start resolving imports for %s", mod_info)
                num_unresolved = 0
                for import_node, normalized_args in mod_info.imports:
                    if import_node.x_module:
                        continue
                    path = import_node.path if import_node.path else import_node.name
                    if import_node.args_mod:
                        done = _TryToNormalizeModArgs(
                            import_node.args_mod, normalized_args)
                        args_strs = [f"{_FormatModArg(a)}->{_FormatModArg(n)}"
                                     for a, n in zip(import_node.args_mod, normalized_args)]
                        logger.info(
                            "generic module: [%s] %s %s", done, import_node.name, ','.join(args_strs))
                        if done:
                            mid = (_ModUniquePathName(
                                self._root, mod_info.uid[0], path),
                                *normalized_args)
                            import_mod_info = self._AddModInfoForGeneric(mid)
                            import_node.x_module = import_mod_info.mod
                            import_node.args_mod.clear()
                            mod_info.mod.x_symtab.AddImport(import_node)
                            new_active.append(import_mod_info)
                            seen_change = True
                        else:
                            num_unresolved += 1
                    else:
                        mid = (_ModUniquePathName(
                            self._root, mod_info.uid[0], path),)
                        import_mod_info = self._FindModInfo(mid)
                        if not import_mod_info:
                            import_mod_info = self._AddModInfoSimple(
                                mid)
                            new_active.append(import_mod_info)
                            seen_change = True
                        logger.info(
                            f"in {mod_info.mod.x_modname} resolving inport of {import_mod_info.mod.x_modname}")
                        import_node.x_module = import_mod_info.mod
                        mod_info.mod.x_symtab.AddImport(import_node)
                if num_unresolved:
                    new_active.append(mod_info)
                logger.info("finish resolving imports for %s - unresolved: %d",
                            mod_info, num_unresolved)

            if not seen_change and new_active:
                assert False, "module import does not terminate"
            active = new_active

    def ModulesInTopologicalOrder(self) -> list[cwast.DefMod]:
        return ModulesInTopologicalOrder(self.AllModInfos())


class ModPool(ModPoolBase):

    def _ReadMod(self, handle: pathlib.PurePath) -> cwast.DefMod:
        """Overload"""
        fn = str(handle) + EXTENSION_CW
        if pathlib.Path(fn).exists():
            mod = parse.ReadModFromStream(open(fn, encoding="utf8"), fn)
            assert isinstance(mod, cwast.DefMod)
            return mod
        fn = str(handle) + EXTENSION_CWS
        if pathlib.Path(fn).exists():
            mod = parse_sexpr.ReadModFromStream(open(fn, encoding="utf8"), fn)
            assert isinstance(mod, cwast.DefMod)
            return mod
        assert False, f"module {str(handle)} does not exist"


if __name__ == "__main__":
    import os
    import sys

    def main(argv):
        assert len(argv) == 1
        assert argv[0].endswith(EXTENSION_CW)

        cwd = os.getcwd()
        mp: ModPool = ModPool(pathlib.Path(cwd) / "Lib")
        mp.ReadModulesRecursively(
            ["builtin", str(pathlib.Path(argv[0][:-3]).resolve())])

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)

    main(sys.argv[1:])
