#!/usr/bin/python3

import pathlib
import logging
import collections
import heapq

from FrontEnd import cwast

from typing import Union, Any, Optional, List, Set

ModHandle = pathlib.PurePath

logger = logging.getLogger(__name__)


class ModPool:

    def __init__(self, root: pathlib.Path):
        self._root: pathlib.Path = root
        # _started is used to prevent import cycles
        self._started: Set[ModHandle] = set()
        self._mods: Dict[ModHandle, cwast.DefMod] = {}
        self.builtin = None

    def __str__(self):
        return f"root={self._root}"

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

    def FindOrInsertModForImport(self, curr: ModHandle, import_node: cwast.Import) -> ModHandle:
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

    def FinalizeMod(self, uid: ModHandle, def_mod: cwast.DefMod):
        assert isinstance(def_mod, cwast.DefMod), f"expect mod but got {def_mod} {type(def_mod)}"
        logger.info("FinalizeMod %s", uid)
        assert uid in self._started
        self._started.discard(uid)
        assert uid not in self._mods
        self._mods[uid] = def_mod

    def GetNextUnfinalized(self) -> Optional[ModHandle]:
        if not self._started:
            return None
        return next(iter(self._started))

    def IsFinalized(self):
        return not self._started

    def ModulesInTopologicalOrder(self) -> List[cwast.DefMod]:
        """The order is also deterministic

        This means modules cannot have circular dependencies except for module arguments
        to parameterized modules which are ignored in the topo order.
        """

        deps_in = collections.defaultdict(list)
        deps_out = collections.defaultdict(list)
        # candidates have no incoming deps
        candidates = []
        for handle, def_mod in self._mods.items():
            assert isinstance(def_mod, cwast.DefMod), f"expect mod but got {def_mod}"
            for node in def_mod.body_mod:
                if isinstance(node, cwast.Import):
                    logger.info("found mod deps [%s] imported by [%s]", node.x_module, handle)
                    assert node.x_module in self._mods
                    deps_in[handle].append(node.x_module)
                    deps_out[node.x_module].append(handle)

        for h in self._mods:
            if not deps_in[h]:
                logger.info("found leaf mod [%s]", h)
                heapq.heappush(candidates, h)
        out=[]
        while len(out) != len(self._mods):
            assert candidates
            x=heapq.heappop(candidates)
            logger.info("picking next mod: %s", x)
            out.append(self._mods[x])
            for importer in deps_out[x]:
                deps_in[importer].remove(x)
                if not deps_in[importer]:
                    heapq.heappush(candidates, importer)
        return out

    def FixupImports(self):
        for mod in self._mods.values():
            assert isinstance(mod, cwast.DefMod)
            for node in mod.body_mod:
                if isinstance(node, cwast.Import):
                    node.x_module = self._mods[node.x_module]


def tests(cwd: str):
    mods_std={
        "builtin": cwast.DefMod("builtin", [], []),
        "os": cwast.DefMod("os", [], []),
        "math": cwast.DefMod("math", [], []),
        "std":  cwast.DefMod("std", [], []),
    }
    mods_local={
        "helper": cwast.DefMod("helper", [], [cwast.Import("os", "")]),
        "math":  cwast.DefMod("math", [], [cwast.Import("std", "")]),
        "main": cwast.DefMod("main", [], [cwast.Import("std", ""),
                                          cwast.Import("math", ""),
                                          cwast.Import("./math", ""),
                                          cwast.Import("./helper", "")])
    }
    pool=ModPool(pathlib.Path(cwd) / "Lib")
    logger.info("Pool %s", pool)

    pool.InsertSeedMod("builtin")
    pool.InsertSeedMod(str(pathlib.Path("./main").resolve()))
    while True:
        handle=pool.GetNextUnfinalized()
        if handle is None:
            break
        assert isinstance(handle, ModHandle), f"Not a path: {handle}"
        logger.info("Processing %s", handle)

        name=handle.name
        dir=handle.parent.name
        mod: cwast.DefMod=mods_std[name] if dir == "Lib" else mods_local[name]
        for i in mod.body_mod:
            assert isinstance(i, cwast.Import)
            i.x_module = pool.FindOrInsertModForImport(handle, i)
        pool.FinalizeMod(handle, mod)
    assert pool.IsFinalized()
    print([m.name for m in pool.ModulesInTopologicalOrder()])
    pool.FixupImports()
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
