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

############################################################
# Convert large parameter into pointer to object allocated
# in the caller
############################################################


def FindFunSigsWithLargeArgs(tc: type_corpus.TypeCorpus) -> dict[Any, Any]:
    out = {}
    for fun_sig in list(tc.corpus.values()):
        if not fun_sig.is_fun():
            continue
        change = False
        params: list[cwast.CanonType] = fun_sig.parameter_types()
        for n, p in enumerate(params):
            if not p.fits_in_register():
                params[n] = tc.InsertPtrType(False, p)
                change = True
        result = fun_sig.result_type()
        if not result.is_void() and not result.fits_in_register():
            change = True
            params.append(tc.InsertPtrType(True, result))
            result = tc.get_void_canon_type()
        if change:
            out[fun_sig] = tc.InsertFunType(params, result)
    return out


def _FixupFunctionPrototypeForLargArgs(fun: cwast.DefFun, new_sig: cwast.CanonType,
                                       tc: type_corpus.TypeCorpus):
    old_sig: cwast.CanonType = fun.x_type
    typify.UpdateNodeType(fun, new_sig)
    result_changes = old_sig.result_type() != new_sig.result_type()
    if result_changes:
        assert new_sig.result_type().is_void()
        assert len(new_sig.parameter_types()) == 1 + \
            len(old_sig.parameter_types())
        sl = fun.x_srcloc
        result_type = cwast.TypePtr(
            fun.result, mut=True, x_srcloc=sl, x_type=new_sig.parameter_types()[-1])
        result_param = cwast.FunParam(cwast.NAME.Make(
            "large_result"), result_type, x_srcloc=sl, x_type=result_type.x_type, res_ref=True)
        fun.params.append(result_param)
        fun.result = cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID, x_srcloc=sl,
                                    x_type=tc.get_void_canon_type())
    changing_params = {}

    # note: new_sig may contain an extra param at the end
    for p, old, new in zip(fun.params, old_sig.parameter_types(), new_sig.parameter_types()):
        if old != new:
            changing_params[p] = new
            p.type = cwast.TypePtr(p.type, x_srcloc=p.x_srcloc, x_type=new)
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
            typify.UpdateNodeType(node, changing_params[node.x_symbol])
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


def FunRewriteLargeArgsCallerSide(fun: cwast.DefFun, fun_sigs_with_large_args,
                                  tc: type_corpus.TypeCorpus):
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
        if isinstance(call, cwast.ExprCall) and call.callee.x_type in fun_sigs_with_large_args:
            sl = call.x_srcloc
            old_sig: cwast.CanonType = call.callee.x_type
            new_sig: cwast.CanonType = fun_sigs_with_large_args[old_sig]
            typify.UpdateNodeType(call.callee, new_sig)
            expr_body: list[Any] = []
            expr = cwast.ExprStmt(
                expr_body, x_srcloc=call.x_srcloc, x_type=call.x_type)
            # note: new_sig might be longer if the result type was changed
            for n, (old, new) in enumerate(zip(old_sig.parameter_types(),
                                               new_sig.parameter_types())):
                if old != new:
                    at = cwast.TypeAuto(x_srcloc=sl, x_type=old)
                    new_def = cwast.DefVar(cwast.NAME.Make(f"arg{n}"),
                                           at,
                                           call.args[n], ref=True,
                                           x_srcloc=sl,
                                           x_type=old)
                    expr_body.append(new_def)
                    name = cwast.Id(
                        new_def.name, None, x_srcloc=sl, x_type=old, x_symbol=new_def)
                    call.args[n] = cwast.ExprAddrOf(
                        name, x_srcloc=sl, x_type=new)
            if len(old_sig.parameter_types()) != len(new_sig.parameter_types()):
                # the result is not a argument
                at = cwast.TypeAuto(x_srcloc=sl, x_type=old_sig.result_type())
                new_def = cwast.DefVar(cwast.NAME.Make("result"),
                                       at,
                                       cwast.ValUndef(x_srcloc=sl, x_eval=eval.VAL_UNDEF),
                                       mut=True, ref=True,
                                       x_srcloc=sl,
                                       x_type=at.x_type)

                name = cwast.Id(new_def.name, None, x_srcloc=sl,
                                x_type=old_sig.result_type(), x_symbol=new_def)
                call.args.append(cwast.ExprAddrOf(
                    name, mut=True, x_srcloc=call.x_srcloc, x_type=new_sig.parameter_types()[-1]))
                typify.UpdateNodeType(call, tc.get_void_canon_type())
                expr_body.append(new_def)
                expr_body.append(cwast.StmtExpr(call, x_srcloc=sl))
                expr_body.append(cwast.StmtReturn(
                    expr_ret=name, x_srcloc=call.x_srcloc, x_target=expr))
            else:
                expr_body.append(cwast.StmtReturn(
                    expr_ret=call, x_srcloc=call.x_srcloc, x_target=expr))
            return expr
        return None
    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)
