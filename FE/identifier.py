"""Id Generator"""

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

    This should be the only place that introduces "%" into
    identifier names.
    """

    def __init__(self: "IdGen"):
        self._names: dict[str, int] = {}

    def RegisterExistingLocals(self, fun: cwast.DefFun):

        def visitor(node, _f):
            if isinstance(node, cwast.DefVar):
                assert "%" not in node.name
                self._names[node.name] = 0


        cwast.VisitAstRecursively(fun, visitor)

    def NewName(self, prefix: str) -> str:
        assert "%" not in prefix
        no = self._names.get(prefix, -1)
        self._names[prefix] = no + 1
        # return cwast.NAME(prefix,  no + 1)
        return f"{prefix}%{no + 1}"

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