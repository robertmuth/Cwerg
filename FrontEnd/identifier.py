
from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any


def _GetAllLocalNames(node, seen_names: Set[str]):
    assert False

    def visitor(node, seen_names):
        if isinstance(node, (cwast.DefVar, cwast.FunParam)):
            seen_names.add(node.name)
        if isinstance(node, cwast.StmtBlock):
            seen_names.add(node.label)

    cwast.VisitAstRecursivelyPost(node, visitor, seen_names)


class IdGen:
    def __init__(self):
        self._global_names: Set[str] = set()
        self._local_names: Set[str] = set()

    def ClearGlobalNames(self):
        self._global_names.clear()

    def LoadGlobalNames(self, mod: cwast.DefMod):
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                self._global_names.add(node.name)

    def ClearLocalNames(self):
        self._local_names.clear()

    def LoadLocalNames(self, fun: cwast.DefFun):
        self._local_names.clear()
        _GetAllLocalNames(fun, self._local_names)

    def UniquifyLocalNames(self, node):
        def visitor(node, _):
            # assumes LoadGlobalNames has already occurred
            if isinstance(node, (cwast.DefVar, cwast.FunParam)):
                node.name = self.NewName(node.name)
            if isinstance(node, cwast.StmtBlock):
                node.label = self.NewName(node.label)

        cwast.VisitAstRecursivelyPost(node, visitor)

    def NewName(self, prefix) -> str:
        token = prefix.split("$")
        assert len(token) <= 2
        prefix = token[0]
        name = prefix
        if name not in self._local_names and name not in self._global_names:
            self._local_names.add(name)
            return name
        for i in range(1, 200):
            name = f"{prefix}${i}"
            if name not in self._local_names and name not in self._global_names:
                self._local_names.add(name)
                return name
        assert False, f"could not find new name for {prefix}"
