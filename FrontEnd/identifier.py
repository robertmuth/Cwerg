
from FrontEnd import cwast
from typing import List, Dict, Set, Optional, Union, Any


class IdGenIR:
    """This is used to generate new local names (labels, registers, stack locations, etc.)
       for Cwerg IR. Clashes with names in AST nodes are avoided by having each
       generated name contain a "." (dot) which is not valid for AST names.

       We assume that all global of local names in the AST nodes
       are also valid IR names and use them verbatim.
       """

    def __init__(self):
        self._names: Dict[str, int] = {}

    def NewName(self, prefix) -> str:
        no = self._names.get(prefix, 0)
        self._names[prefix] = no + 1
        if no == 0:
            return prefix
        else:
            return f"{prefix}.{no}"


class IdGen:
    """This is used to generate new names for the AST. Note the 
       """
       
    def __init__(self):
        self._names: Dict[str, int] = {}

    def NewName(self, prefix) -> str:
        no = self._names.get(prefix, 0)
        self._names[prefix] = no + 1
        return f"{prefix}%{no}"
        
        
        

