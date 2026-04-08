from typing import Any, Optional

from FE import cwast
from FE import type_corpus
from FE import eval
from FE import canonicalize


def CondIsAlwaysTrue(cond: Any) -> bool:
    return cond.x_eval == eval.VAL_TRUE


def CondIsAlwaysFalse(cond: Any) -> bool:
    return cond.x_eval == eval.VAL_FALSE


def _ContainsBreakRecurtsively(node_list: list[Any], block_target: cwast.StmtBlock) -> bool:
    for node in node_list:
        if isinstance(node, cwast.StmtBreak):
            # no reason to continue - reamaining stmts are unreachable
            return node.x_target is block_target
        elif isinstance(node, (cwast.StmtReturn, cwast.StmtTrap, cwast.StmtContinue)):
            return False
        elif isinstance(node, cwast.StmtBlock):
            return _ContainsBreakRecurtsively(node.body, block_target)
        elif isinstance(node, cwast.StmtIf):
            if not CondIsAlwaysTrue(node.cond):
                if _ContainsBreakRecurtsively(node.body_f, block_target):
                    return True
            if not CondIsAlwaysFalse(node.cond):
                if _ContainsBreakRecurtsively(node.body_t, block_target):
                    return True
        elif isinstance(node, cwast.StmtDefer):
            return _ContainsBreakRecurtsively(node.body, block_target)
        elif isinstance(node, cwast.StmtCond):
            for c in node.cases:
                if _ContainsBreakRecurtsively(c.body, block_target):
                    return True
    return False


def _LastStmtFallsThrough(last) -> bool:
    if isinstance(last, (cwast.StmtContinue, cwast.StmtReturn, cwast.StmtTrap)):
        return False
    elif isinstance(last, cwast.StmtBreak):
        return True
    elif isinstance(last, cwast.StmtIf):
        if not CondIsAlwaysTrue(last.cond):
            if _BodyFallsThru(last.body_f):
                return True
        if not CondIsAlwaysFalse(last.cond):
            if _BodyFallsThru(last.body_t):
                return True
        return False
    elif isinstance(last, cwast.StmtCond):
        seen_always_true = False
        for x in last.cases:
            if CondIsAlwaysTrue(x.cond):
                seen_always_true = True
            # This is incomplete as it does not ensure full coverge of all connditions
            if _BodyFallsThru(x.body):
                return True
        return not seen_always_true
    elif isinstance(last, cwast.StmtBlock):
        if len(last.body) == 0:
            return True
        elif len(last.body) >= 2:
            if _ContainsBreakRecurtsively(last.body, last):
                return True
        return _LastStmtFallsThrough(last.body[-1])
    else:
        return True


def _BodyFallsThru(body) -> bool:
    if len(body) == 0:
        return True
    return _LastStmtFallsThrough(body[-1])


def ModVerifyFunFallthrus(mod: cwast.DefMod):
    for fun in mod.body_mod:
        if not isinstance(fun, cwast.DefFun) or fun.extern or fun.x_type.result_type().is_void():
            continue
        if _BodyFallsThru(fun.body):
            # from FE import pp_ast
            # import sys
            # pp_ast.DumpNode(fun, fout=sys.stdout)
            cwast.CompilerError(
                fun.x_srcloc, f"{fun.name} has non-void return type but does not end with a return statement")


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


def _IdNodeFromDefFun(fun: cwast.DefFun) -> cwast.Id:
    return cwast.Id(fun.name, x_srcloc=fun.x_srcloc, x_symbol=fun, x_type=fun.x_type, x_eval=eval.EvalFunAddr(fun))


def _MakeInitFiniFun(name: str, callees: list[cwast.DefFun], fun_ct, void_ct) -> cwast.DefFun:
    sl = cwast.SRCLOC_GENERATED
    at = cwast.TypeAuto(x_srcloc=sl, x_type=void_ct)
    out = cwast.DefFun(cwast.NAME(name), [], at, [],
                       cdecl=True, x_type=fun_ct, x_srcloc=sl)
    void_expr = cwast.ValVoid(x_srcloc=sl, x_type=void_ct)
    for c in callees:
        if c.x_type != fun_ct:
            cwast.CompilerError(
                c.x_srcloc, f"init function {c.name} must have type 'void ()'")
        call = cwast.ExprCall(_IdNodeFromDefFun(
            c), [], x_srcloc=cwast.SRCLOC_GENERATED, x_type=void_ct)
        out.body.append(cwast.StmtExpr(call, x_srcloc=cwast.SRCLOC_GENERATED))
    out.body.append(cwast.StmtReturn(void_expr, x_srcloc=sl, x_target=out))
    return out


def MakeInitFun(name: str, mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus) -> cwast.DefFun:
    fun_ct = tc.InsertFunType([], tc.get_void_canon_type())
    void_ct = tc.get_void_canon_type()
    lst: list[cwast.DefFun] = []
    for mod in mod_topo_order:
        seen_one = False
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun) and fun.init:
                lst.append(fun)
                if seen_one:
                    cwast.CompilerError(
                        fun.x_srcloc, f"multiple init functions in module {mod.name}")
                seen_one = True
    return _MakeInitFiniFun(name, lst, fun_ct, void_ct)


def MakeFiniFun(name: str, mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus) -> cwast.DefFun:
    fun_ct = tc.InsertFunType([], tc.get_void_canon_type())
    void_ct = tc.get_void_canon_type()
    lst: list[cwast.DefFun] = []
    for mod in mod_topo_order:
        seen_one = False
        for fun in reversed(mod.body_mod):
            if isinstance(fun, cwast.DefFun) and fun.fini:
                lst.append(fun)
                if seen_one:
                    cwast.CompilerError(
                        fun.x_srcloc, f"multiple fini functions in module {mod.name}")
                seen_one = True
    return _MakeInitFiniFun(name, lst, fun_ct, void_ct)
