"""Id Generator"""

import sys

from typing import Any

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

    def NewName(self, prefix: str) -> cwast.NAME:
        no = self._names.get(prefix, 1)
        self._names[prefix] = no + 1
        # this should be the only place introducing a "%" in an identifier
        return cwast.NAME.Make(f"{prefix}%{no}")
