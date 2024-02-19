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


def ModulesInTopologicalOrder(mods: Sequence[cwast.DefMod]) -> List[cwast.DefMod]:
    """The order is also deterministic

    This means modules cannot have circular dependencies except for module arguments
    to parameterized modules which are ignored in the topo order.
    """

    deps_in: Dict[cwast.DefMod, List[cwast.DefMod]
                  ] = collections.defaultdict(list)
    deps_out: Dict[cwast.DefMod, List[cwast.DefMod]
                   ] = collections.defaultdict(list)
    # candidates have no incoming deps
    candidates: List[cwast.DefMod] = []
    for def_mod in mods:
        for node in def_mod.body_mod:
            if isinstance(node, cwast.Import):
                importee = node.x_module
                assert isinstance(importee, cwast.DefMod)

                logger.info(
                    "found mod deps [%s] imported by [%s]", importee, def_mod)
                assert isinstance(
                    node.x_module, cwast.DefMod), "was Finalize() run?"
                deps_in[def_mod].append(importee)
                deps_out[importee].append(def_mod)

    for def_mod in mods:
        if not deps_in[def_mod]:
            logger.info("found leaf mod [%s]", def_mod)
            heapq.heappush(candidates, def_mod)
    out: List[cwast.DefMod] = []
    while len(out) != len(mods):
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
        self._all_mods: Dict[ModHandle, cwast.DefMod] = {}
        self._unresolved_paramterized_imports: dict[cwast.DefMod,
                                                    List[cwast.Import]] = collections.defaultdict(list)

    def __str__(self):
        return f"root={self._root}"

    def _IsKnownModule(self, uid: ModHandle) -> bool:
        return uid in self._all_mods or uid in self._started

    def ReadMod(self, _handle: ModHandle) -> cwast.DefMod:
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

    def _FindOrInsertModForImport(self, curr: ModHandle, import_node: cwast.Import) -> ModHandle:
        uid = self._ModUniqueId(curr, import_node.name)
        if not self._IsKnownModule(uid):
            logger.info("Insert Mod %s", uid)
            self._started.add(uid)
        return uid

    def InsertSeedMod(self, pathname: str) -> ModHandle:
        assert not pathname.startswith(".")
        uid = self._ModUniqueId(None, pathname)
        assert not self._IsKnownModule(uid)
        self._started.add(uid)
        logger.info("Insert RootMod %s", uid)
        return uid

    def _FinishMod(self, uid: ModHandle, def_mod: cwast.DefMod):
        assert isinstance(
            def_mod, cwast.DefMod), f"expect mod but got {def_mod} {type(def_mod)}"
        logger.info("FinalizeMod %s", uid)
        assert uid in self._started
        self._started.discard(uid)
        assert uid not in self._all_mods
        self._all_mods[uid] = def_mod

    def _GetNextUnfinalized(self) -> Optional[ModHandle]:
        if not self._started:
            return None
        return next(iter(self._started))

    def _Finalize(self):
        taken_names: Set[str] = set()
        assert not self._started
        for def_mod in self._all_mods.values():
            assert isinstance(def_mod, cwast.DefMod)
            for node in def_mod.body_mod:
                if isinstance(node, cwast.Import):
                    assert isinstance(node.x_module, ModHandle)
                    node.x_module = self._all_mods[node.x_module]
                    assert isinstance(node.x_module, cwast.DefMod)
            if def_mod.name not in taken_names:
                def_mod.x_modname = def_mod.name
            else:
                assert False
            taken_names.add(def_mod.x_modname)
            cwast.CheckAST(def_mod, disallowed_nodes=set())

    def ReadAndFinalizedMods(self):
        while True:
            handle = self._GetNextUnfinalized()
            if handle is None:
                break
            logger.info("Processing %s", handle)
            def_mod: cwast.DefMod = self.ReadMod(handle)
            for i in def_mod.body_mod:
                if isinstance(i, cwast.Import):
                    if i.args_mod:
                        # parameterized import
                        assert False
                    else:
                        i.x_module = self._FindOrInsertModForImport(handle, i)
            self._FinishMod(handle, def_mod)
        self._Finalize()

    def ReadModulesRecursively(self, seed_modules: List[str]):
        for m in seed_modules:
            self.InsertSeedMod(m)
        self.ReadAndFinalizedMods()

    def ModulesInTopologicalOrder(self) -> List[cwast.DefMod]:
        return ModulesInTopologicalOrder(self._all_mods.values())


class ModPool(ModPoolBase):

    def ReadMod(self, handle: ModHandle) -> cwast.DefMod:
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

    def ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        name = handle.name
        dir = handle.parent.name
        return _test_mods_std[name] if dir == "Lib" else _test_mods_local[name]


def tests(cwd: str):

    pool = ModPoolForTest(pathlib.Path(cwd) / "Lib")
    logger.info("Pool %s", pool)

    pool.InsertSeedMod("builtin")
    pool.InsertSeedMod(str(pathlib.Path("./main").resolve()))
    pool.ReadAndFinalizedMods()
    print([m.name for m in pool.ModulesInTopologicalOrder()])
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
