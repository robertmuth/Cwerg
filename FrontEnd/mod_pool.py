#!/usr/bin/python3

import pathlib
import logging
import collections
import heapq

from FrontEnd import cwast
from FrontEnd import parse
from FrontEnd import symbolize

from typing import Optional, Sequence, Any

ModHandle = pathlib.PurePath

logger = logging.getLogger(__name__)


class ModInfo:
    def __init__(self, uid: ModHandle, mod: cwast.DefMod):
        self.uid = uid
        self.mod = mod
        # the second component holds the normalized args
        self.imports = [
            (node, [None] * len(node.args_mod)) for node in mod.body_mod if isinstance(node, cwast.Import)]

    def __str__(self):
        return f"{self.mod.name}:{self.uid}"


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
            assert isinstance(importee, cwast.DefMod)

            logger.info(
                "found mod deps [%s] imported by [%s]", importee, mod)
            deps_in[mod].append(importee)
            deps_out[importee].append(mod)

    # start with candidates with no incoming deps
    candidates: list[cwast.DefMod] = []
    for mi in mod_infos:
        mod = mi.mod
        if not deps_in[mod]:
            logger.info("found leaf mod [%s]", mod)
            heapq.heappush(candidates, mod)

    # topological order
    out: list[cwast.DefMod] = []
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
        self._all_mods: dict[ModHandle, ModInfo] = {}
        self._taken_names: set[str] = set()

    def __str__(self):
        return f"root={self._root}"

    def _AddModInfo(self, uid) -> ModInfo:
        mod_info = ModInfo(uid, self._ReadMod(uid))
        logger.info("Adding new mod: %s", mod_info)
        self._all_mods[uid] = mod_info
        name = mod_info.mod.name
        assert name not in self._taken_names
        self._taken_names.add(name)
        mod_info.mod.x_modname = name
        return mod_info

    def _IsKnownModule(self, uid: ModHandle) -> bool:
        return uid in self._all_mods

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

    def ReadModulesRecursively(self, seed_modules: list[str]):
        active: list[ModHandle] = []

        for pathname in seed_modules:
            assert not pathname.startswith(".")
            uid = self._ModUniqueId(None, pathname)
            assert not self._IsKnownModule(uid)
            self._AddModInfo(uid)
            active.append(uid)

        buitin_syms = symbolize.GetSymTabForBuiltInOrEmpty(
            [m.mod for m in self._all_mods.values()])

        # fix point computation for resolving imports
        while active:
            new_active: list[ModHandle] = []
            seen_change = False
            for uid in active:
                symbolize.ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    [m.mod for m in self._all_mods.values()], buitin_syms, False)

                mod_info = self._all_mods[uid]
                logger.info("start resolving imports for %s", mod_info)
                num_unresolved = 0
                for import_node, normalized_args in mod_info.imports:
                    if import_node.x_module:
                        continue
                    if import_node.args_mod:
                        done = _TryToNormalizeModArgs(
                            import_node.args_mod, normalized_args)
                        args_strs = [f"{_FormatModArg(a)}->{_FormatModArg(n)}"
                                     for a, n in zip(import_node.args_mod, normalized_args)]
                        logger.info(
                            "generic module: [%s] %s %s", done, import_node.name, ','.join(args_strs))
                        if done:
                            assert False
                        num_unresolved += 1
                    else:
                        import_uid = self._ModUniqueId(uid, import_node.name)
                        import_mod_info = self._all_mods.get(import_uid)
                        if not import_mod_info:
                            import_mod_info = self._AddModInfo(import_uid)
                            new_active.append(import_uid)
                            seen_change = True
                        logger.info(
                            f"in {mod_info.mod.name} resolving inport of {import_mod_info.mod.name}")
                        import_node.x_module = import_mod_info.mod
                        mod_info.mod.x_symtab.AddImport(import_node)
                if num_unresolved:
                    new_active.append(uid)
                logger.info("finish resolving imports for %s - unresolved: %d",
                            mod_info, num_unresolved)

            if not seen_change and new_active:
                assert False, "module import does not terminate"
            active = new_active

    def ModulesInTopologicalOrder(self) -> list[cwast.DefMod]:
        return ModulesInTopologicalOrder(self._all_mods.values())


class ModPool(ModPoolBase):

    def _ReadMod(self, handle: ModHandle) -> cwast.DefMod:
        fn = str(handle) + ".cw"
        asts = parse.ReadModsFromStream(open(fn, encoding="utf8"), fn)
        assert len(asts) == 1, f"multiple modules in {fn}"
        mod = asts[0]
        assert isinstance(mod, cwast.DefMod)
        cwast.AnnotateImportsForQualifers(mod)
        mod.x_symtab = symbolize.ExtractSymTabPopulatedWithGlobals(mod)
        return asts[0]


if __name__ == "__main__":
    import os
    import sys

    def main(argv):
        assert len(argv) == 1
        assert argv[0].endswith(".cw")

        cwd = os.getcwd()
        mp: ModPool = ModPool(pathlib.Path(cwd) / "Lib")
        mp.ReadModulesRecursively(
            ["builtin", str(pathlib.Path(argv[0][:-3]).resolve())])

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)

    main(sys.argv[1:])
