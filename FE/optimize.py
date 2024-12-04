from typing import Any, Optional
from FE import cwast

def _IsConstantSymbol(sym) -> bool:
    if isinstance(sym, cwast.DefFun):
        return True
    elif isinstance(sym,  cwast.FunParam):
        return True
    elif isinstance(sym, (cwast.DefVar, cwast.DefGlobal)):
        return not sym.mut
    else:
        assert False, f"{sym}"


def FunCopyPropagation(fun: cwast.DefFun):
    """ """
    replacements: dict[Any, Any] = {}

    def visit(node: Any, _field: str):
        nonlocal replacements
        if not isinstance(node, cwast.DefVar) or node.mut or not isinstance(node.initial_or_undef_or_auto, cwast.Id):
            return None
        id_node: cwast.Id = node.initial_or_undef_or_auto
        sym = id_node.x_symbol
        if not _IsConstantSymbol(sym):
            return None
        if isinstance(node, (cwast.DefVar, cwast.DefGlobal)) and node.ref:
            if not sym.ref:
                return None

        replacements[node] = sym
        # print ("@@@@@@@@@@", node)

    cwast.VisitAstRecursivelyPost(fun, visit)

    def update(node, _field):
        nonlocal replacements

        if isinstance(node, cwast.Id):
            r = replacements.get(node.x_symbol)
            while r in replacements:
                r = replacements.get(r)
            if r is not None:
                node.base_name = r.name
                node.x_symbol = r
                #print(f">>>>>>>> {node.FullName()} -> {r.name}")
                # assert False
    cwast.VisitAstRecursivelyPost(fun, update)
