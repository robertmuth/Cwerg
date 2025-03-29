from typing import Any
from FE import cwast
from FE import identifier
from FE import stats


def _IsConstantSymbol(sym) -> bool:
    if isinstance(sym, cwast.DefFun):
        return True
    elif isinstance(sym,  cwast.FunParam):
        return True
    elif isinstance(sym, (cwast.DefVar, cwast.DefGlobal)):
        return not sym.mut
    else:
        assert False, f"{sym}"


def MayHaveSideEffects(n: Any):
    # we could try harder but it is probably not worth it.
    if isinstance(n, (cwast.ExprCall, cwast.ExprStmt)):
        return True
    elif isinstance(n, (cwast.Id, cwast.ValAuto, cwast.ValTrue, cwast.ValFalse, cwast.ValUndef, cwast.ValNum)):
        return False
    elif isinstance(n, (cwast.ExprAddrOf)):
        return MayHaveSideEffects(n.expr_lhs)
    elif isinstance(n, (cwast.ExprDeref, cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast,
                        cwast.ExprWiden, cwast.ExprNarrow, cwast.ExprUnionUntagged)):
        return MayHaveSideEffects(n.expr)
    elif isinstance(n, (cwast.ExprFront, cwast.ExprField)):
        return MayHaveSideEffects(n.container)
    elif isinstance(n, (cwast.Expr2)):
        return MayHaveSideEffects(n.expr1) or MayHaveSideEffects(n.expr2)
    elif isinstance(n, (cwast.ExprPointer)):
        return MayHaveSideEffects(n.expr1) or MayHaveSideEffects(n.expr2) or MayHaveSideEffects(n.expr_bound_or_undef)
    elif isinstance(n, (cwast.ValCompound)):
        for item in n.inits:
            if MayHaveSideEffects(item.point) or MayHaveSideEffects(item.value_or_undef):
                return True
        return False
    else:
        assert False, f"unexpected {n} in {n.x_srcloc}"


def FunRemoveUnusedDefVar(fun: cwast.DefFun):
    """ """
    used: set[Any] = set()

    def visit(node: Any):
        nonlocal used
        if isinstance(node, cwast.Id):
            used.add(node.x_symbol)

    cwast.VisitAstRecursivelyPost(fun, visit)

    def update(node,  _parent, _field):
        nonlocal used

        if isinstance(node, cwast.DefVar):
            if node not in used and not MayHaveSideEffects(node.initial_or_undef_or_auto):
                stats.IncCounter("Removed", "DefVar", 1)
                return cwast.EphemeralList([])
        return None
    cwast.MaybeReplaceAstRecursively(fun, update)


def FunPeepholeOpts(fun: cwast.DefFun):
    """Misc Peephole Opts"""

    def replace(node):
        if isinstance(node, cwast.ExprDeref) and isinstance(node.expr, cwast.ExprAddrOf):
            stats.IncCounter("Peephole", "DerefAddrOf", 1)
            return node.expr.expr_lhs
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replace)


def FunCopyPropagation(fun: cwast.DefFun):
    """ """
    replacements: dict[Any, Any] = {}

    def visit(node: Any):
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

    cwast.VisitAstRecursivelyPost(fun, visit)

    def update(node: Any):
        nonlocal replacements

        if isinstance(node, cwast.Id):
            r = replacements.get(node.x_symbol)
            while r in replacements:
                r = replacements.get(r)
            if r is not None:
                stats.IncCounter("CopyProp", "Id", 1)
                node.name = r.name
                node.x_symbol = r
                node.x_type = r.x_type
                # print(f">>>>>>>> {node.FullName()} {node.x_type}  <- {r.name} {r.x_srcloc}")
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
        at = cwast.TypeAuto(x_srcloc=sl, x_type=p.type.x_type)
        t = cwast.DefVar(id_gen.NewName("inl_arg"),
                         at,
                         a,
                         x_srcloc=sl,
                         x_type=at.x_type)
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


_INLINE_NODE_CUT_OFF = 20


def FunInlineSmallFuns(fun: cwast.DefFun, id_gen: identifier.IdGen):

    def replacer(call: Any, _parent: Any, _field: str):
        nonlocal fun
        if not isinstance(call, cwast.ExprCall):
            return None
        if not isinstance(call.callee, cwast.Id):
            return None
        fun_def: cwast.DefFun = call.callee.x_symbol
        if not isinstance(fun_def, cwast.DefFun):
            return None
        # TODO
        #if fun_def.name.name != "fib":
        #    return None
        if fun_def.extern:
            return None
        n = 0
        for s in fun_def.body:
            n += cwast.NumberOfNodes(s)
        if n > _INLINE_NODE_CUT_OFF:
            return None
        if fun is fun_def:  # no inlining of recursions
            return None

        stats.IncCounter("Inlining", "Calls", 1)
        stats.IncCounter("Inlining", "Nodes", n)
        # print("INLINING ", call, call.x_srcloc,
        #      "    ->     ", f"{repr(fun_def.name)}", fun_def)
        return MakeExprStmtForCall(call, id_gen)
    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunRemoveSimpleExprStmts(fun: cwast.DefFun):
    # deal with common simple cases until we have something more general in place

    def replacer(node: Any):
        if isinstance(node, cwast.StmtReturn) and isinstance(node.expr_ret, cwast.ExprStmt):
            target_map = {node.expr_ret: node.x_target}
            cwast.UpdateSymbolAndTargetLinks(node.expr_ret, {}, target_map)
            stats.IncCounter("Removed", "ExprStmt.1", 1)
            return cwast.EphemeralList(node.expr_ret.body, colon=True)
        if isinstance(node, cwast.ExprStmt) and len(node.body) == 1 and isinstance(node.body[0], cwast.StmtReturn):
            # assert False, f"{node.body}"
            stats.IncCounter("Removed", "ExprStmt.2", 1)
            return node.body[0].expr_ret
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunOptimize(fun: cwast.DefFun, id_gen: identifier.IdGen):
    FunInlineSmallFuns(fun, id_gen)
    FunCopyPropagation(fun)
    FunRemoveUnusedDefVar(fun)
    cwast.EliminateEphemeralsRecursively(fun)
    FunPeepholeOpts(fun)
    FunRemoveSimpleExprStmts(fun)
