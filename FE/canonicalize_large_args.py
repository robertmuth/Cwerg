"""Canonicalize Large Args (and Results)

The goal of this step is to simplify code generation.
We want to avoid having to deal with values that do not fit into registers.
Those values are primarily rec and sum-types. Slices would also fall into this
category but we convert them to rec in the prior step.

The only place where we allow values  that do not fit into register
are let statements.

Effects of this step:
* Rewrite arguments and results which cannot be passed in registers
  as pointers.
* Large results will become an extra pointer parameter appended to the end
  of the parameter list.

"""

from typing import Optional, Any

from FE import cwast
from FE import type_corpus
from FE import typify
from FE import eval
from FE import canonicalize

############################################################
# Convert large parameter into pointer to object allocated
# in the caller
############################################################


def MakeAndRegisterLargeArgReplacements(tc: type_corpus.TypeCorpus):
    tc.ClearReplacementInfo()
    for fun_sig in tc.topo_order[:]:
        if not fun_sig.is_fun():
            continue
        change = False
        params: list[cwast.CanonType] = []
        for p in fun_sig.parameter_types():
            if p.fits_in_register():
                params.append(p)
            else:
                params.append(tc.InsertPtrType(False, p))
                change = True
        result = fun_sig.result_type()
        if not result.is_void() and not result.fits_in_register():
            change = True
            params.append(tc.InsertPtrType(True, result))
            result = tc.get_void_canon_type()
        if change:
            fun_sig.LinkReplacementType(tc.InsertFunType(params, result))


def _FixupFunctionPrototypeForLargArgs(fun: cwast.DefFun, new_sig: cwast.CanonType,
                                       tc: type_corpus.TypeCorpus):
    old_sig: cwast.CanonType = fun.x_type
    typify.NodeChangeType(fun, new_sig)
    result_changes = old_sig.result_type() != new_sig.result_type()
    if result_changes:
        assert new_sig.result_type().is_void()
        assert len(new_sig.parameter_types()) == 1 + \
            len(old_sig.parameter_types())
        sl = fun.x_srcloc
        result_type = cwast.TypeAuto(sl, new_sig.parameter_types()[-1])
        result_param = cwast.FunParam(cwast.NAME.Make(
            "large_result"), result_type, x_srcloc=sl, x_type=result_type.x_type, res_ref=True)
        fun.params.append(result_param)
        fun.result = cwast.TypeAuto(sl, tc.get_void_canon_type())
    changing_params = {}

    # note: new_sig may contain an extra param at the end
    for p, old, new in zip(fun.params, old_sig.parameter_types(), new_sig.parameter_types()):
        if old != new:
            changing_params[p] = new
            p.type = cwast.TypeAuto(x_srcloc=p.x_srcloc, x_type=new)
            p.arg_ref = True
    assert result_changes or changing_params
    return changing_params, result_changes


def FunRewriteLargeArgsCalleeSide(fun: cwast.DefFun, new_sig: cwast.CanonType,
                                  tc: type_corpus.TypeCorpus):
    changing_params, result_changes = _FixupFunctionPrototypeForLargArgs(
        fun, new_sig, tc)

    # print([k.name for k, v in changing_params.items()], result_changes)

    def replacer(node) -> Optional[Any]:

        if isinstance(node, cwast.Id) and node.x_symbol in changing_params:
            new_node = cwast.ExprDeref(
                node, x_srcloc=node.x_srcloc, x_type=node.x_type)
            typify.NodeChangeType(node, changing_params[node.x_symbol])
            return new_node

        if isinstance(node, cwast.StmtReturn) and node.x_target == fun and result_changes:
            result_param: cwast.FunParam = fun.params[-1]
            result_type: cwast.CanonType = result_param.type.x_type
            assert result_type.is_pointer()
            lhs = cwast.ExprDeref(
                cwast.Id(result_param.name, None, x_srcloc=node.x_srcloc,
                         x_type=result_type, x_symbol=result_param),
                x_srcloc=node.x_srcloc, x_type=result_type.underlying_type())
            assign = cwast.StmtAssignment(
                lhs, node.expr_ret, x_srcloc=node.x_srcloc)
            node.expr_ret = cwast.ValVoid(x_srcloc=node.x_srcloc,
                                          x_type=tc.get_void_canon_type())
            return [assign, node]
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def MakeDefAndAddrOfForParam(name, init, ct_old: cwast.CanonType,
                             ct_new, mut: bool) -> tuple[cwast.DefVar,
                                                         cwast.ExprAddrOf]:
    sl = init.x_srcloc
    at = cwast.TypeAuto(x_srcloc=sl, x_type=ct_old)
    def_var = cwast.DefVar(name, at, init, x_srcloc=sl,
                           x_type=ct_old, ref=True, mut=mut)
    sym = canonicalize.IdNodeFromDef(def_var, sl)
    addr_of = cwast.ExprAddrOf(sym, x_srcloc=sl, x_type=ct_new)
    return def_var, addr_of


def FunRewriteLargeArgsCallerSide(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """Assuming the callee signature was changed like so
          foo(a: rec A, b: rec B, c: rec C)
       To
          foo(a: ptr(rec A), b: ptr(rec B), c: ptr(rec C))


       The call site changes from;
           foo(a, b, c)
       To
           aa = a
           bb = b
           cc = c
           foo(&aa, &bb, &cc)

       We have to play it safe and materialize aa, bb, cc under certain conditions:
       * a, b, c are expression
         we cannot take address of an expression so we have to make copy first.
       * a, b, c are mutable storage locations
         we cannot be sure if mutable aliases to a, b, c are accessed by foo
         of functions called by foo, so we have to make a copy with value just before the call.
    """
    def replacer(call, _parent) -> Optional[Any]:
        if not isinstance(call, cwast.ExprCall):
            return None
        orig_fun_ct: cwast.CanonType = call.callee.x_type
        new_fun_ct: cwast.CanonType = orig_fun_ct.replacement_type
        if new_fun_ct is None:
            return None
        sl = call.x_srcloc

        typify.NodeChangeType(call.callee, new_fun_ct)
        expr_body: list[Any] = []
        expr = cwast.ExprStmt(
            expr_body, x_srcloc=call.x_srcloc, x_type=call.x_type)
        # note: new_sig might be longer if the result type was changed
        for n, (old_ct, new_ct) in enumerate(zip(orig_fun_ct.parameter_types(),
                                                 new_fun_ct.parameter_types())):
            if old_ct == new_ct:
                continue
            # Note: the type of this new variable is NOT call.args[n].x_type
            # BUT old since we still rely on some basic implicit conversion.
            # E.g. from mut to non-mut.
            new_def, addr_of = MakeDefAndAddrOfForParam(cwast.NAME.Make(f"arg{n}"),
                                                        call.args[n], old_ct, new_ct, mut=False)
            expr_body.append(new_def)
            call.args[n] = addr_of
        if len(orig_fun_ct.parameter_types()) != len(new_fun_ct.parameter_types()):
            old_ct = orig_fun_ct.result_type()
            new_ct = new_fun_ct.parameter_types()[-1]
            undef_init = cwast.ValUndef(x_srcloc=sl, x_eval=eval.VAL_UNDEF)
            # the result is not a argument
            new_def, addr_of = MakeDefAndAddrOfForParam(cwast.NAME.Make("result"),
                                                        undef_init, old_ct, new_ct, mut=True)
            call.args.append(addr_of)
            typify.NodeChangeType(call, tc.get_void_canon_type())
            expr_body.append(new_def)
            expr_body.append(cwast.StmtExpr(call, x_srcloc=sl))
            expr_body.append(cwast.StmtReturn(
                canonicalize.IdNodeFromDef(new_def, sl), x_srcloc=call.x_srcloc, x_target=expr))
        else:
            expr_body.append(cwast.StmtReturn(
                call, x_srcloc=sl, x_target=expr))
        return expr
    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)
