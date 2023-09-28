#!/usr/bin/python3

import pathlib
import logging
import collections
import heapq

from FrontEnd import cwast
from FrontEnd import parse

from typing import Optional, List, Set, Dict

ModHandle = pathlib.PurePath

logger = logging.getLogger(__name__)


def _DecorateIdsWithQualifer(mod: cwast.DefMod):
    """Record the original module

    We do this even for unqualified names. This is important for macros whose
    syntax tree might get copied into a different from where it originated.
    """
    imports: Dict[str, cwast.DefMod] = {}

    def visitor(node, _):
        nonlocal imports, mod
        if isinstance(node, cwast.Import):
            name = node.name
            # TODO: strip off path component if present
            if node.alias:
                name = node.alias
            assert name not in imports
            imports[name] = node.x_module
        if isinstance(node, (cwast.Id, cwast.MacroInvoke, cwast.DefFun)):
            q = cwast.GetQualifierIfPresent(node.name)
            if q:
                if isinstance(node, cwast.DefFun):
                    assert node.polymorphic
                assert q in imports
                node.x_module = imports[q]
            else:
                node.x_module = mod

    cwast.VisitAstRecursivelyPost(mod, visitor)

class ModPoolBase:
    """
    class protocol:
    * InsertSeedMod() +
    * ReadAndFinalizedMods()
    * ModulesInTopologicalOrder()
    """

    def __init__(self, root: pathlib.Path):
        self._root: pathlib.Path = root
        # _started is used to prevent import cycles
        self._started: Set[ModHandle] = set()
        self._mods: Dict[ModHandle, cwast.DefMod] = {}
        self.builtin = None

    def __str__(self):
        return f"root={self._root}"

    def ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        assert False, "to be implemented by derived class"

    def _ModUniqueId(self, curr: Optional[ModHandle], pathname: str) -> ModHandle:
        # other options, would be to use checksums
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
        if uid not in self._mods and uid not in self._started:
            logger.info("Insert Mod %s", uid)
            self._started.add(uid)
        return uid

    def InsertSeedMod(self, pathname: str) -> ModHandle:
        assert not pathname.startswith(".")
        uid = self._ModUniqueId(None, pathname)
        assert uid not in self._mods and uid not in self._started
        self._started.add(uid)
        logger.info("Insert RootMod %s", uid)
        return uid

    def _FinalizeMod(self, uid: ModHandle, def_mod: cwast.DefMod):
        assert isinstance(
            def_mod, cwast.DefMod), f"expect mod but got {def_mod} {type(def_mod)}"
        logger.info("FinalizeMod %s", uid)
        assert uid in self._started
        self._started.discard(uid)
        assert uid not in self._mods
        self._mods[uid] = def_mod

    def _GetNextUnfinalized(self) -> Optional[ModHandle]:
        if not self._started:
            return None
        return next(iter(self._started))

    def _Finalize(self):
        taken_names: Set[str] = set()
        assert not self._started
        for def_mod in self._mods.values():
            assert isinstance(def_mod, cwast.DefMod)
            for node in def_mod.body_mod:
                if isinstance(node, cwast.Import):
                    assert isinstance(node.x_module, ModHandle)
                    node.x_module = self._mods[node.x_module]
                    assert isinstance(node.x_module, cwast.DefMod)
            _DecorateIdsWithQualifer(def_mod)
            if def_mod.name not in taken_names:
                def_mod.x_modname = def_mod.name
            else:
                assert False
            taken_names.add(def_mod.x_modname)
            cwast.CheckAST(def_mod, set())



    def ReadAndFinalizedMods(self):
        while True:
            handle = self._GetNextUnfinalized()
            if handle is None:
                break
            logger.info("Processing %s", handle)
            def_mod: cwast.DefMod = self.ReadMod(handle)
            for i in def_mod.body_mod:
                if isinstance(i, cwast.Import):
                    i.x_module = self._FindOrInsertModForImport(handle, i)
            self._FinalizeMod(handle, def_mod)
        self._Finalize()

    def ModulesInTopologicalOrder(self) -> List[cwast.DefMod]:
        """The order is also deterministic

        This means modules cannot have circular dependencies except for module arguments
        to parameterized modules which are ignored in the topo order.
        """

        deps_in = collections.defaultdict(list)
        deps_out = collections.defaultdict(list)
        # candidates have no incoming deps
        candidates = []
        for def_mod in self._mods.values():
            assert isinstance(
                def_mod, cwast.DefMod), f"expect mod but got {def_mod}"
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

        for def_mod in self._mods.values():
            if not deps_in[def_mod]:
                logger.info("found leaf mod [%s]", def_mod)
                heapq.heappush(candidates, def_mod)
        out = []
        while len(out) != len(self._mods):
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


class ModPool(ModPoolBase):

    def ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        fn = str(handle) + ".cw"
        asts = parse.ReadModsFromStream(open(fn, encoding="utf8"), fn)
        assert len(asts) == 1, f"multiple modules in {fn}"
        assert isinstance(asts[0], cwast.DefMod)
        return asts[0]


_test_mods_std = {
    "builtin": cwast.DefMod("builtin", [], []),
    "os": cwast.DefMod("os", [], []),
    "math": cwast.DefMod("math", [], []),
    "std":  cwast.DefMod("std", [], []),
}
_test_mods_local = {
    "helper": cwast.DefMod("helper", [], [cwast.Import("os", "")]),
    "math":  cwast.DefMod("math", [], [cwast.Import("std", "")]),
    "main": cwast.DefMod("main", [], [cwast.Import("std", ""),
                                      cwast.Import("math", ""),
                                      cwast.Import("./math", ""),
                                      cwast.Import("./helper", "")])
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
