"""Id Generator"""


class IdGenIR:
    """This is used to generate new local names (labels, registers, stack locations, etc.)
       for Cwerg IR. Clashes with names in AST nodes are avoided by having each
       generated name contain a "." (dot) which is not valid for AST names.

       We assume that all global of local names in the AST nodes
       are also valid IR names and use them verbatim.
       """

    def __init__(self, handle: str = ""):
        self.handle = handle
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

    def __init__(self, handle=""):
        self.handle = handle
        self._names: dict[str, int] = {}

    def NewName(self, prefix: str) -> str:
        assert "%" not in prefix
        no = self._names.get(prefix, 0)
        self._names[prefix] = no + 1
        return f"{prefix}%{no}"
