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
    "helper": cwast.DefMod("helper", [],
                           [cwast.Import(cwast.NAME.FromStr("os"), "", [])]),
    "math":  cwast.DefMod("math", [],
                          [cwast.Import(cwast.NAME.FromStr("std"), "", [])]),
    "main": cwast.DefMod("main", [],
                         [cwast.Import(cwast.NAME.FromStr("std"), "", []),
                          cwast.Import(cwast.NAME.FromStr("math"), "", []),
                          # cwast.Import(cwast.NAME.FromStr("./math"), "", []),
                          cwast.Import(cwast.NAME.FromStr("./helper"), "", [])])
}


def _ReadMod(handle, _) -> cwast.DefMod:
    name = handle.name
    dir = handle.parent.name
    mod = _test_mods_std[name] if dir == "Lib" else _test_mods_local[name]
    return mod


def tests(cwd: str):
    mp = mod_pool.ReadModulesRecursively(
        pathlib.Path(cwd) / "Lib",
        ["builtin", str(pathlib.Path("./main").resolve())],
        False,
        _ReadMod)
    print([m.name for m in mp.mods_in_topo_order])
    print("OK")


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    tests(os.getcwd())
