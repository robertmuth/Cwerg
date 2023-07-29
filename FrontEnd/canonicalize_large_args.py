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

from typing import Dict, Optional, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import type_corpus
from FrontEnd import typify

############################################################
# Convert large parameter into pointer to object allocated
# in the caller
############################################################


def MakeTypeVoid(tc, srcloc):
    return cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID, x_srcloc=srcloc,
                          x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))


def FindFunSigsWithLargeArgs(tc: type_corpus.TypeCorpus) -> Dict[Any, Any]:
    out = {}
    for fun_sig in list(tc.corpus.values()):
        if not fun_sig.is_fun():
            continue
        change = False
        params = fun_sig.parameter_types()
        for n, p in enumerate(params):
            reg_type = p.register_types
            if reg_type is None or len(reg_type) > 1:
                params[n] = tc.insert_ptr_type(False, p)
                change = True
        result = fun_sig.result_type()
        reg_type = result.register_types
        if not result.is_void() and reg_type is None or len(reg_type) > 1:
            change = True
            params.append(tc.insert_ptr_type(True, result))
            result = tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID)
        if change:
            out[fun_sig] = tc.insert_fun_type(params, result)
    return out


def _FixupFunctionPrototypeForLargArgs(fun: cwast.DefFun, new_sig: cwast.CanonType,
                                       tc: type_corpus.TypeCorpus, id_gen: identifier.IdGen):
    old_sig: cwast.CanonType = fun.x_type
    typify.UpdateNodeType(tc, fun, new_sig)
    result_changes = old_sig.result_type() != new_sig.result_type()
    if result_changes:
        assert new_sig.result_type().is_void()
        assert len(new_sig.parameter_types()) == 1 + \
            len(old_sig.parameter_types())
        result_type = cwast.TypePtr(
            fun.result, mut=True, x_srcloc=fun.x_srcloc, x_type=new_sig.parameter_types()[-1])
        result_param = cwast.FunParam(id_gen.NewName(
            "result"), result_type, x_srcloc=fun.x_srcloc)
        fun.params.append(result_param)
        fun.result = MakeTypeVoid(tc, fun.x_srcloc)
    changing_params = {}

    # note: new_sig may contain an extra param at the end
    for p, old, new in zip(fun.params, old_sig.parameter_types(), new_sig.parameter_types()):
        if old != new:
            changing_params[p] = new
            p.type = cwast.TypePtr(p.type, x_srcloc=p.x_srcloc, x_type=new)
    assert result_changes or changing_params
    return changing_params, result_changes


def RewriteLargeArgsCalleeSide(fun: cwast.DefFun, new_sig: cwast.CanonType,
                               tc: type_corpus.TypeCorpus, id_gen: identifier.IdGen):
    changing_params, result_changes = _FixupFunctionPrototypeForLargArgs(
        fun, new_sig, tc, id_gen)

    # print([k.name for k, v in changing_params.items()], result_changes)

    def replacer(node, _) -> Optional[Any]:

        if isinstance(node, cwast.Id) and node.x_symbol in changing_params:
            new_node = cwast.ExprDeref(
                node, x_srcloc=node.x_srcloc, x_type=node.x_type)
            typify.UpdateNodeType(tc, node, changing_params[node.x_symbol])
            return new_node
        elif isinstance(node, cwast.StmtReturn) and node.x_target == fun and result_changes:
            result_param: cwast.FunParam = fun.params[-1]
            result_type: cwast.CanonType = result_param.type.x_type
            assert result_type.is_pointer()
            lhs = cwast.ExprDeref(
                cwast.Id(result_param.name, x_srcloc=node.x_srcloc,
                         x_type=result_type, x_symbol=result_param),
                x_srcloc=node.x_srcloc, x_type=result_type.underlying_pointer_type())
            assign = cwast.StmtAssignment(
                lhs, node.expr_ret, x_srcloc=node.x_srcloc)
            node.expr_ret = cwast.ValVoid(
                x_srcloc=node.x_srcloc, x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))
            return cwast.EphemeralList([assign, node], x_srcloc=node.x_srcloc)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
    cwast.EliminateEphemeralsRecursively(fun)


def RewriteLargeArgsCallerSide(fun: cwast.DefFun, fun_sigs_with_large_args,
                               tc: type_corpus.TypeCorpus, id_gen: identifier.IdGen):

    def replacer(call, _) -> Optional[Any]:
        if isinstance(call, cwast.ExprCall) and call.callee.x_type in fun_sigs_with_large_args:
            old_sig: cwast.CanonType = call.callee.x_type
            new_sig: cwast.CanonType = fun_sigs_with_large_args[old_sig]
            typify.UpdateNodeType(tc, call.callee, new_sig)
            expr_body = []
            expr = cwast.ExprStmt(
                expr_body, x_srcloc=call.x_srcloc, x_type=call.x_type)
            # note: new_sig might be longer if the result type was changed
            for n, (old, new) in enumerate(zip(old_sig.parameter_types(), new_sig.parameter_types())):
                if old != new:
                    new_def = cwast.DefVar(id_gen.NewName(f"arg{n}"),
                                           cwast.TypeAuto(
                                               x_srcloc=call.x_srcloc, x_type=old),
                                           call.args[n], ref=True,
                                           x_srcloc=call.x_srcloc)
                    expr_body.append(new_def)
                    name = cwast.Id(new_def.name,
                                    x_srcloc=call.x_srcloc, x_type=old, x_symbol=new_def)
                    call.args[n] = cwast.ExprAddrOf(
                        name, x_srcloc=call.x_srcloc, x_type=new)
            if len(old_sig.parameter_types()) != len(new_sig.parameter_types()):
                # the result is not a argument
                new_def = cwast.DefVar(id_gen.NewName("result"),
                                       cwast.TypeAuto(x_srcloc=call.x_srcloc,
                                                      x_type=old_sig.result_type()),
                                       cwast.ValUndef(x_srcloc=call.x_srcloc),
                                       mut=True, ref=True,
                                       x_srcloc=call.x_srcloc)
                name = cwast.Id(new_def.name,
                                x_srcloc=call.x_srcloc, x_type=old_sig.result_type(), x_symbol=new_def)
                call.args.append(cwast.ExprAddrOf(
                    name, mut=True, x_srcloc=call.x_srcloc, x_type=new_sig.parameter_types()[-1]))
                typify.UpdateNodeType(
                    tc, call, tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))
                expr_body.append(new_def)
                expr_body.append(cwast.StmtExpr(
                    call, x_srcloc=call.x_srcloc))
                expr_body.append(cwast.StmtReturn(
                    expr_ret=name, x_srcloc=call.x_srcloc, x_target=expr))
            else:
                expr_body.append(cwast.StmtReturn(
                    expr_ret=call, x_srcloc=call.x_srcloc, x_target=expr))
            return expr
        return None
    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
