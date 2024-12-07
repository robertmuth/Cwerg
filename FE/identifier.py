"""Id Generator"""

from typing import Any, Tuple, Union

from FE import cwast


class IdGenIR:
    """This is used to generate new local names (labels, registers, stack locations, etc.)
       for Cwerg IR. Clashes with names in AST nodes are avoided by having each
       generated name contain a "." (dot) which is not valid for AST names.

       We assume that all global of local names in the AST nodes
       are also valid IR names and use them verbatim.
       """

    def __init__(self: "IdGenIR"):
        self._names: dict[str, int] = {}

    def NewName(self, prefix: str) -> str:
        assert "." not in prefix, f"{prefix}"
        no = self._names.get(prefix, 0)
        self._names[prefix] = no + 1
        if no == 0:
            return prefix
        else:
            return f"{prefix}.{no}"


class IdGen:
    """This is used to generate new names for the AST.
    """

    def __init__(self: "IdGen"):
        self._names: dict[str, int] = {}

    def RegisterExistingLocals(self, fun: cwast.DefFun):
        # TODO: should we take global symbols into account?
        # one could argue that the names do not matter anymore anyway,
        # after symbol resolution only x_symbol links matter
        def visitor(node: Any, _f: str):
            if isinstance(node, (cwast.FunParam, cwast.DefVar)):
                n: cwast.NAME = node.name
                self._names[n.name] = max(n.seq, self._names.get(n.name, 0))

        cwast.VisitAstRecursively(fun, visitor)

    def NewName(self, prefix: str) -> cwast.NAME:
        # TODO: 10 is arbitrary
        no = self._names.get(prefix, 10)
        self._names[prefix] = no + 1
        return cwast.NAME(prefix,  no + 1)


class IdGenCache:
    def __init__(self: "IdGenCache"):
        self._cache: dict[cwast.DefFun, IdGen] = {}

    def Get(self, fun: cwast.DefFun) -> IdGen:
        ig = self._cache.get(fun)
        if ig is None:
            ig = IdGen()
            self._cache[fun] = ig
            ig.RegisterExistingLocals(fun)
        return ig
