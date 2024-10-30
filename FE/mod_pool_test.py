#!/bin/env python3

import pathlib
import logging

from FE import cwast
from FE import mod_pool
from FE import symbolize

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

    def _ReadMod(self, mid: mod_pool.ModId) -> cwast.DefMod:
        handle = mid[0]
        name = handle.name
        dir = handle.parent.name
        mod = _test_mods_std[name] if dir == "Lib" else _test_mods_local[name]
        cwast.AnnotateImportsForQualifers(mod)
        mod.x_symtab = symbolize.ExtractSymTabPopulatedWithGlobals(mod)
        return mod

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
