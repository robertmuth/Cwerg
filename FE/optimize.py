from typing import Any, Optional
from FE import cwast
from FE import identifier


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
                # print(f">>>>>>>> {node.FullName()} -> {r.name}")
                # assert False
    cwast.VisitAstRecursivelyPost(fun, update)


def MakeExprStmtForCall(call: cwast.ExprCall, id_gen: identifier.IdGen) -> cwast.ExprStmt:
    """ Note: this duplicates fields from `call` so call shold be
    deleted afterwards
    """
    fun = call.callee
    assert isinstance(fun, cwast.Id)
    fun_def = fun.x_symbol
    assert isinstance(fun_def, cwast.DefFun)
    assert not fun_def.extern
    out = cwast.ExprStmt([], call.x_srcloc, call.x_type)
    var_map = {}
    for a, p in zip(call.args, fun_def.params):
        sl = a.x_srcloc
        t = cwast.DefVar(id_gen.NewName("inl_arg"),
                         cwast.TypeAuto(x_srcloc=sl, x_type=p.type.x_type),
                         a,
                         x_srcloc=sl)
        out.body.append(t)
        var_map[p] = t
    block_map = {fun_def: out}

    for s in fun_def.body:
        if isinstance(s, cwast.StmtReturn):
            assert s.x_target is fun_def
        c = cwast.CloneNodeRecursively(s, var_map, block_map)
        if isinstance(c, cwast.StmtReturn):
            assert c.x_target is out
        out.body.append(c)

    return out


_INLINE_NODE_CUT_OFF = 5

def FunInlineSmallFuns(fun: cwast.DefFun, id_gen: identifier.IdGen):
    def replacer(call: Any, parent: Any, field: str):
        if not isinstance(call, cwast.ExprCall):
            return
        fun = call.callee
        if not isinstance(fun, cwast.Id):
            return
        fun_def = fun.x_symbol
        if not isinstance(fun_def, cwast.DefFun):
            return
        if fun_def.extern:
            return
        n = 0
        for s in fun_def.body:
            n += cwast.NumberOfNodes(s)
        if n > _INLINE_NODE_CUT_OFF:
            return
        # print ("@@@@@@@@ ", call, "    ->     ", fun_def)
        return MakeExprStmtForCall(call, id_gen)
    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunOptimize(fun: cwast.DefFun, id_gen: identifier.IdGen):
    FunInlineSmallFuns(fun, id_gen)
    # FunCopyPropagation(fun)
