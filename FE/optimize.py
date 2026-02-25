from typing import Any
from FE import cwast
from FE import stats

from FE import eval


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
    elif isinstance(n, (cwast.Id, cwast.ValAuto, cwast.ValUndef, cwast.ValNum, cwast.ValVoid)):
        return False
    elif isinstance(n, (cwast.ExprAddrOf)):
        return MayHaveSideEffects(n.expr_lhs)
    elif isinstance(n, (cwast.ExprPointer)):
        return MayHaveSideEffects(n.expr1) or MayHaveSideEffects(n.expr2) or MayHaveSideEffects(n.expr_bound_or_undef)
    elif isinstance(n, (cwast.ExprFront, cwast.ExprField, cwast.ExprLen)):
        return MayHaveSideEffects(n.container)
    elif isinstance(n, (cwast.Expr1, cwast.ExprDeref, cwast.ExprAs, cwast.ExprBitCast,
                        cwast.ExprWiden, cwast.ExprNarrow, cwast.ExprUnionUntagged, cwast.ExprUnwrap)):
        return MayHaveSideEffects(n.expr)
    elif isinstance(n, (cwast.Expr2)):
        return MayHaveSideEffects(n.expr1) or MayHaveSideEffects(n.expr2)
    elif isinstance(n, (cwast.Expr3)):
        return MayHaveSideEffects(n.cond) or MayHaveSideEffects(n.expr1) or MayHaveSideEffects(n.expr2)
    elif isinstance(n, (cwast.ValCompound)):
        for item in n.inits:
            if MayHaveSideEffects(item.point_or_undef) or MayHaveSideEffects(item.value_or_undef):
                return True
        return False
    elif isinstance(n, (cwast.ValSpan)):
        return MayHaveSideEffects(n.pointer) or MayHaveSideEffects(n.expr_size)
    else:
        assert False, f"MayHaveSideEffects: unexpected {n} in {n.x_srcloc}"


def FunRemoveUnusedDefVar(fun: cwast.DefFun):
    """ """
    used: set[Any] = set()

    def visit(node: Any):
        nonlocal used
        if isinstance(node, cwast.Id):
            used.add(node.x_symbol)

    cwast.VisitAstRecursivelyPost(fun, visit)

    def update(node,  _parent):
        nonlocal used

        if isinstance(node, cwast.DefVar):
            if node not in used and not MayHaveSideEffects(node.initial_or_undef_or_auto):
                stats.IncCounter("Removed", "DefVar", 1)
                return []
        return None
    # if we remove a node we do not need to recurse into the subtree
    cwast.MaybeReplaceAstRecursively(fun, update)


def FunPeepholeOpts(fun: cwast.DefFun):
    """Misc Peephole Opts"""

    def replace(node):
        if isinstance(node, cwast.ExprDeref) and isinstance(node.expr, cwast.ExprAddrOf):
            stats.IncCounter("Peephole", "DerefAddrOf", 1)
            return node.expr.expr_lhs
        if isinstance(node, cwast.ExprAddrOf) and isinstance(node.expr_lhs, cwast.ExprDeref):
            stats.IncCounter("Peephole", "AddrOfDeref", 1)
            return node.expr_lhs.expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replace)


def FunCopyPropagation(fun: cwast.DefFun):
    """Propagate copies of constant Id Nodes"""
    replacements: dict[Any, Any] = {}

    def visit(node: Any):
        nonlocal replacements
        if not isinstance(node, cwast.DefVar) or node.mut or not isinstance(node.initial_or_undef_or_auto, cwast.Id):
            return
        init_id: cwast.Id = node.initial_or_undef_or_auto
        sym = init_id.x_symbol
        if not _IsConstantSymbol(sym):
            return
        # Do not migrate a non-ref to a ref
        # This still causes weird corner cases:
        # let x : [6]int = {: 1, 1, 2, 3, 4}
        # let y = x
        # -> &x != &y before propagation and &x == &y after
        # TODO: rethink this
        if node.ref and isinstance(sym, (cwast.DefVar, cwast.DefGlobal)) and not sym.ref:
            return

        replacements[node] = sym

    cwast.VisitAstRecursivelyPost(fun, visit)

    def update(node: Any):
        nonlocal replacements
        # TODO: support Fun?
        if hasattr(node, 'x_eval') and isinstance(node.x_eval, (eval.EvalVarAddr, eval.EvalGlobalAddr)):
            new_sym = replacements.get(node.x_eval.sym)
            # while new_sym in replacements:
            #    new_sym = replacements.get(new_sym)
            if new_sym:
                node.x_eval = eval.MakeEvalVarOrGlobalAddr(new_sym)
        if isinstance(node, cwast.Id):
            new_sym = replacements.get(node.x_symbol)
            # while new_sym in replacements:
            #    new_sym = replacements.get(new_sym)
            if new_sym is not None:
                stats.IncCounter("CopyProp", "Id", 1)
                node.name = new_sym.name
                node.x_symbol = new_sym
                # TODO: explain why this is needed
                node.x_type = new_sym.x_type
                # print(f">>>>>>>> {node.name} {node.x_type}  <- {r.name} {r.x_srcloc}")
    cwast.VisitAstRecursivelyPost(fun, update)


def MakeExprStmtForCall(call: cwast.ExprCall) -> cwast.ExprStmt:
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
        dv = cwast.DefVar(cwast.NAME.Make(f"inl_arg"),
                          at,
                          a,
                          x_srcloc=sl,
                          x_type=at.x_type)
        out.body.append(dv)
        var_map[p] = dv
    target_map = {fun_def: out}

    for s in fun_def.body:
        c = cwast.CloneNodeRecursively(s, var_map, target_map)
        out.body.append(c)
    return out


_INLINE_NODE_CUT_OFF = 20


def FunInlineSmallFuns(fun: cwast.DefFun):

    def replacer(call: Any, _parent: Any):
        nonlocal fun
        if not isinstance(call, cwast.ExprCall):
            return None
        # TODO: why not use x_eval?
        if not isinstance(call.callee, cwast.Id):
            return None
        fun_def: cwast.DefFun = call.callee.x_symbol

        if not isinstance(fun_def, cwast.DefFun):
            return None
        if fun is fun_def:  # no inlining of recursions
            return None
        if fun.extern:
            return None
        # TODO
        # if fun_def.name.name != "fib":
        #    return None
        if fun_def.extern:
            return None
        n = 0
        for s in fun_def.body:
            n += cwast.NumberOfNodes(s)
        if n > _INLINE_NODE_CUT_OFF:
            return None

        stats.IncCounter("Inlining", "Calls", 1)
        stats.IncCounter("Inlining", "Nodes", n)
        # print("INLINING ", call, call.x_srcloc,
        #      "    ->     ", f"{repr(fun_def.name)}", fun_def)
        return MakeExprStmtForCall(call)
    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunRemoveSimpleExprStmts(fun: cwast.DefFun):
    # deal with common simple cases until we have something more general in place

    def replacer(node: Any):
        if isinstance(node, cwast.StmtReturn) and isinstance(node.expr_ret, cwast.ExprStmt):
            target_map = {node.expr_ret: node.x_target}
            # TODO: this should specialized to the case updating a single x_target
            cwast.UpdateSymbolAndTargetLinks(node.expr_ret, {}, target_map)
            stats.IncCounter("Removed", "ExprStmt.1", 1)
            return node.expr_ret.body
        if isinstance(node, cwast.ExprStmt) and len(node.body) == 1 and isinstance(node.body[0], cwast.StmtReturn):
            # assert False, f"{node.body}"
            stats.IncCounter("Removed", "ExprStmt.2", 1)
            return node.body[0].expr_ret
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def FunOptimize(fun: cwast.DefFun):
    FunInlineSmallFuns(fun)
    FunCopyPropagation(fun)
    FunRemoveUnusedDefVar(fun)
    FunPeepholeOpts(fun)
    FunRemoveSimpleExprStmts(fun)
