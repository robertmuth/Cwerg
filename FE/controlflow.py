from typing import Any, Optional

from FE import cwast
from FE import eval


def CondIsAlwaysTrue(cond: Any) -> bool:
    if isinstance(cond, cwast.ValNum):
        return cond.x_eval == eval.VAL_TRUE
    return False


def CondIsAlwaysFalse(cond: Any) -> bool:
    if isinstance(cond, cwast.ValNum):
        return cond.x_eval == eval.VAL_FALSE
    return False


# TODO: try converting this to VisitAstRecursivelyPreAndPost
def _EliminateDeferRecursively(node: Any, scopes: list[tuple[Any, list[Any]]]):

    def handle_cfg(target):
        out = []
        for scope, defers in reversed(scopes):
            for defer in reversed(defers):
                clone = cwast.CloneNodeRecursively(defer, {}, {})
                out += clone.body
            if scope is target:
                break
        for x in out:
            assert not isinstance(x, cwast.StmtDefer)
        return out

    if isinstance(node, cwast.StmtDefer):
        scopes[-1][1].append(node)

    if cwast.NF.TARGET_ANNOTATED in node.FLAGS:
        # inject the defer bodies just before the control flow change
        return handle_cfg(node.x_target) + [node]

    for nfd in node.__class__.NODE_FIELDS:
        field = nfd.name
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, field)
            new_child = _EliminateDeferRecursively(child, scopes)
            assert new_child is None
            if new_child:
                assert not isinstance(new_child, list)
                setattr(node, child, new_child)
        else:
            if field in cwast.NEW_SCOPE_FIELDS:
                scopes.append((node, []))
            #
            children = getattr(node, field)
            new_children = []
            change = False
            for n, child in enumerate(children):
                new_child = _EliminateDeferRecursively(child, scopes)
                if new_child is None:
                    new_children.append(child)
                else:
                    assert isinstance(new_child, list)
                    new_children += new_child
                    change = True

            #
            if field in cwast.NEW_SCOPE_FIELDS:
                # handle end of scope if the last statement was NOT a control flow change
                if not new_children or cwast.NF.TARGET_ANNOTATED not in children[-1].FLAGS:
                    out = handle_cfg(scopes[-1][0])
                    if out:
                        new_children += out
                        change = True
                scopes.pop(-1)
            #
            if change:
                setattr(node, field, new_children)

    if isinstance(node, cwast.StmtDefer):
        return []
    return None


def FunEliminateDefer(fun: cwast.DefFun):
    _EliminateDeferRecursively(fun, [])


def FunCanonicalizeRemoveStmtCond(fun: cwast.DefFun):
    """Convert StmtCond to nested StmtIf"""
    def replacer(node, _parent) -> Optional[list[Any]]:
        if not isinstance(node, cwast.StmtCond):
            return None
        out = []
        for case in reversed(node.cases):
            assert isinstance(case, cwast.Case)
            if CondIsAlwaysTrue(case.cond):
                assert not out, f"'case true' shold be the last case in a cond statement"
                out = case.body
            else:
                out = [cwast.StmtIf(case.cond, case.body,
                                    out, x_srcloc=case.x_srcloc)]
        return out

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def FunAddMissingReturnStmts(fun: cwast.DefFun):
    result_ct = fun.x_type.result_type()
    if not result_ct.get_unwrapped().is_void():
        return

    sl = fun.x_srcloc
    if fun.body:
        last = fun.body[-1]
        if isinstance(last, cwast.StmtReturn):
            return
        sl = last.x_srcloc
    void_expr = cwast.ValVoid(x_srcloc=sl, x_type=result_ct)

    fun.body.append(cwast.StmtReturn(void_expr, x_srcloc=sl, x_target=fun))
