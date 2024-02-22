#!/usr/bin/python3

import pathlib
import logging
import collections
import heapq

from FrontEnd import cwast
from FrontEnd import parse

from typing import Optional, List, Set, Dict, Sequence

ModHandle = pathlib.PurePath

logger = logging.getLogger(__name__)


class ModInfo:
    def __init__(self, mod: cwast.DefMod):
        self.mod = mod
        self.imports = [
            node for node in mod.body_mod if isinstance(node, cwast.Import)]


def ModulesInTopologicalOrder(mod_infos: Sequence[ModInfo]) -> List[cwast.DefMod]:
    """The order is also deterministic

    This means modules cannot have circular dependencies except for module arguments
    to parameterized modules which are ignored in the topo order.
    """
    deps_in: Dict[cwast.DefMod, List[cwast.DefMod]
                  ] = collections.defaultdict(list)
    deps_out: Dict[cwast.DefMod, List[cwast.DefMod]
                   ] = collections.defaultdict(list)

    # populate deps_in/deps_out
    for mi in mod_infos:
        mod = mi.mod
        assert isinstance(mod, cwast.DefMod)
        for node in mi.imports:
            importee = node.x_module
            assert isinstance(importee, cwast.DefMod)

            logger.info(
                "found mod deps [%s] imported by [%s]", importee, mod)
            deps_in[mod].append(importee)
            deps_out[importee].append(mod)

    # start with candidates with no incoming deps
    candidates: List[cwast.DefMod] = []
    for mi in mod_infos:
        mod = mi.mod
        if not deps_in[mod]:
            logger.info("found leaf mod [%s]", mod)
            heapq.heappush(candidates, mod)

    # topological order
    out: List[cwast.DefMod] = []
    while len(out) != len(mod_infos):
        assert candidates
        x = heapq.heappop(candidates)
        assert isinstance(x, cwast.DefMod)
        logger.info("picking next mod: %s", x)
        out.append(x)

        for importer in deps_out[x]:
            deps_in[importer].remove(x)
            if not deps_in[importer]:
                heapq.heappush(candidates, importer)
    return out


class ModPoolBase:
    """
    class protocol:
    * InsertSeedMod()+
    * ReadAndFinalizedMods()
    * ModulesInTopologicalOrder()


    Will set the x_module field of the import nodes WITH empty args_mod
    (non parameterized imports)
    """

    def __init__(self, root: pathlib.Path):
        self._root: pathlib.Path = root
        # _started is used to prevent import cycles
        # all modules to be processed start here and upon parsing will
        # be "promoted" to  all_modes.
        # This serves as a TODO list for modules
        self._started: Set[ModHandle] = set()
        # all modules keyed by ModHandle
        self._all_mods: Dict[ModHandle, ModInfo] = {}
        self._active: list[ModHandle] = []
        self._taken_names: set[str] = set()

    def __str__(self):
        return f"root={self._root}"

    def _AddModeInfo(self, uid, mod_info: ModInfo):
        self._all_mods[uid] = mod_info
        name = mod_info.mod.name
        assert name not in self._taken_names
        self._taken_names.add(name)
        mod_info.mod.x_modname = name
        if mod_info.imports:
            self._active.append(uid)

    def _IsKnownModule(self, uid: ModHandle) -> bool:
        return uid in self._all_mods or uid in self._started

    def _ReadMod(self, _handle: ModHandle) -> cwast.DefMod:
        assert False, "to be implemented by derived class"

    def _ModUniqueId(self, curr: Optional[ModHandle], pathname: str) -> ModHandle:
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
            return (self._root / pathname).resolve()

    def ReadModulesRecursively(self, seed_modules: List[str]):
        for pathname in seed_modules:
            assert not pathname.startswith(".")
            uid = self._ModUniqueId(None, pathname)
            assert not self._IsKnownModule(uid)
            mod_info = ModInfo(self._ReadMod(uid))
            self._AddModeInfo(uid, mod_info)

        while self._active:
            uid = self._active.pop(0)
            mod_info = self._all_mods[uid]
            for import_node in mod_info.imports:
                uid = self._ModUniqueId(uid, import_node.name)
                mod_info = self._all_mods.get(uid)
                if not mod_info:
                    mod_info = ModInfo(self._ReadMod(uid))
                    self._AddModeInfo(uid, mod_info)
                import_node.x_module = mod_info.mod

    def ModulesInTopologicalOrder(self) -> List[cwast.DefMod]:
        return ModulesInTopologicalOrder(self._all_mods.values())


class ModPool(ModPoolBase):

    def _ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        fn = str(handle) + ".cw"
        asts = parse.ReadModsFromStream(open(fn, encoding="utf8"), fn)
        assert len(asts) == 1, f"multiple modules in {fn}"
        assert isinstance(asts[0], cwast.DefMod)
        cwast.AnnotateImportsForQualifers(asts[0])
        return asts[0]


_test_mods_std = {
    "builtin": cwast.DefMod("builtin", [], []),
    "os": cwast.DefMod("os", [], []),
    "math": cwast.DefMod("math", [], []),
    "std":  cwast.DefMod("std", [], []),
}
_test_mods_local = {
    "helper": cwast.DefMod("helper", [], [cwast.Import("os", "", [])]),
    "math":  cwast.DefMod("math", [], [cwast.Import("std", "", [])]),
    "main": cwast.DefMod("main", [], [cwast.Import("std", "", []),
                                      cwast.Import("math", "", []),
                                      cwast.Import("./math", "", []),
                                      cwast.Import("./helper", "", [])])
}


class ModPoolForTest(ModPoolBase):

    def _ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        name = handle.name
        dir = handle.parent.name
        return _test_mods_std[name] if dir == "Lib" else _test_mods_local[name]


def tests(cwd: str):

    pool = ModPoolForTest(pathlib.Path(cwd) / "Lib")
    logger.info("Pool %s", pool)

    pool._InsertSeedMod("builtin")
    pool._InsertSeedMod(str(pathlib.Path("./main").resolve()))
    pool._ReadAndFinalizedMods()
    print([m.name for m in pool.ModulesInTopologicalOrder()])
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
