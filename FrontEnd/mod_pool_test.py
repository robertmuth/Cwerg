#!/usr/bin/python3

import pathlib
import logging

from FrontEnd import cwast
from FrontEnd import mod_pool

logger = logging.getLogger(__name__)

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
                                      # cwast.Import("./math", "", []),
                                      cwast.Import("./helper", "", [])])
}


class ModPoolForTest(mod_pool.ModPoolBase):

    def _ReadMod(self, handle: mod_pool.ModHandle) -> cwast.DefMod:
        name = handle.name
        dir = handle.parent.name
        return _test_mods_std[name] if dir == "Lib" else _test_mods_local[name]


def tests(cwd: str):

    pool = ModPoolForTest(pathlib.Path(cwd) / "Lib")
    logger.info("Pool %s", pool)
    pool.ReadModulesRecursively(["builtin",
                                 str(pathlib.Path("./main").resolve())])
    print([m.name for m in pool.ModulesInTopologicalOrder()])
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
