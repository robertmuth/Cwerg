#!/usr/bin/python3

import pathlib
import logging

import cwast


ModHandle = str

logger = logging.getLogger(__name__)


class ModPool:

    def __init__(self, root: pathlib.Path):
        self._root: pathlib.Path = root
        # _started is used to prevent import cycles
        self._started = set()
        self._mods = {}
        self._mods = {}

    def __str__(self):
        return f"root={self._root}"

    def ModUniqueId(self, curr: ModHandle, pathname: str, drop_libname) -> ModHandle:
        if pathname.startswith("."):
            pc = pathlib.Path(curr)
            if drop_libname:
                pc = pc.parent
            return (pc / pathname).resolve()
        else:
            return (self._root / pathname).resolve()

        # other options, would be to use checksums
        return pathlib.Path(path_or_name).resolve()

    def InitMod(self,  curr: ModHandle, path_or_name: str, drop_libname=True) -> ModHandle:
        uid = self.ModUniqueId(curr, path_or_name, drop_libname)
        assert uid not in self._started
        assert uid not in self._mods
        self._started.add(uid)
        logger.info("InitMod %s", uid)
        return uid

    def LookupImportOrNone(self, curr: ModHandle, import_node: cwast.Import):
        uid = self.ModUniqueId(curr, import_node.name, True)
        assert uid not in self._started
        return self._mods.get(uid)

    def FiniMod(self, uid: ModHandle, mod: cwast.DefMod):
        logger.info("FiniMod %s", uid)
        assert uid in self._started
        self._started.discard(uid)
        assert uid not in self._mods
        self._mods[uid] = mod

    def IsFinalized(self):
        return not self._started


def tests(cwd: str):
    pool = ModPool(pathlib.Path(cwd) / "Lib")
    logger.info("Pool %s", pool)
    # init main module
    handle_main = pool.InitMod(cwd, "./main", drop_libname=False)

    # import std
    import_std = cwast.Import("std", "")
    assert not pool.LookupImportOrNone(handle_main, import_std)
    # init std module
    handle_std = pool.InitMod(handle_main, import_std.name)
    # fini std module
    mod_std = cwast.DefMod("std", [], [])
    pool.FiniMod(handle_std, mod_std)

    # import math
    import_math = cwast.Import("math", "")
    assert not pool.LookupImportOrNone(handle_main, import_math)
    # init math module
    handle_math = pool.InitMod(handle_main, import_math.name)
    # fini math module
    mod_math = cwast.DefMod("math", [], [])
    pool.FiniMod(handle_math, mod_math)

    # import local helper
    import_local_helper = cwast.Import("./helper", "")
    assert not pool.LookupImportOrNone(handle_main, import_local_helper)
    # init local helper module
    handle_local_helper = pool.InitMod(handle_main, import_local_helper.name)
    import_std2 = cwast.Import("std", "")
    assert pool.LookupImportOrNone(handle_local_helper, import_std2)

    # fini local helper module
    mod_local_helper = cwast.DefMod("helper", [], [import_std2])
    pool.FiniMod(handle_local_helper, mod_local_helper)

    # import local math
    import_local_math = cwast.Import("./math", "")
    assert not pool.LookupImportOrNone(handle_main, import_local_math)
    # init local math module
    handle_local_math = pool.InitMod(handle_main, import_local_math.name)
    # fini local math module
    mod_local_math = cwast.DefMod(
        "math", [], [import_std, import_math,
                     import_local_helper, import_local_math])
    pool.FiniMod(handle_local_math, mod_local_math)

    # fini main module
    mod_main = cwast.DefMod("main", [], [])
    pool.FiniMod(handle_main, mod_main)
    assert pool.IsFinalized()
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
