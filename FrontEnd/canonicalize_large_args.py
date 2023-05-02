"""Canonicalize Large Args (and Results)

Rewrite arguments and results which cannot be passed in registers
as pointers.

Large results will become an extra pointer parameter appended to the end
of the parameter list

"""

import dataclasses
import logging
import pp

from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import types
from FrontEnd import typify
from FrontEnd import symbolize

############################################################
# Convert large parameter into pointer to object allocated
# in the caller
############################################################


def MakeTypeVoid(tc, srcloc):
    return cwast.TypeBase(cwast.BASE_TYPE_KIND.VOID, x_srcloc=srcloc,
                          x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))


def FindFunSigsWithLargeArgs(tc: types.TypeCorpus) -> Dict[Any, Any]:
    out = {}
    for fun_sig in list(tc.corpus.values()):
        if not isinstance(fun_sig, cwast.TypeFun):
            continue
        change = False
        params = [p.type for p in fun_sig.params]
        for n, p in enumerate(params):
            reg_type = tc.register_types(p)
            if reg_type is None or len(reg_type) > 1:
                params[n] = tc.insert_ptr_type(False, p)
                change = True
        result = fun_sig.result
        reg_type = tc.register_types(result)
        if not types.is_void(result) and reg_type is None or len(reg_type) > 1:
            change = True
            params.append(tc.insert_ptr_type(True, result))
            result = tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID)
        if change:
            out[fun_sig] = tc.insert_fun_type(params, result)
    return out


def _FixupFunctionPrototypeForLargArgs(fun: cwast.DefFun, new_sig: cwast.TypeFun,
                                       tc: types.TypeCorpus, id_gen: identifier.IdGen):
    old_sig: cwast.TypeFun = fun.x_type
    typify.UpdateNodeType(tc, fun, new_sig)
    result_changes = old_sig.result != new_sig.result
    if result_changes:
        assert types.is_void(new_sig.result)
        assert len(new_sig.params) == 1 + len(old_sig.params)
        result_type = cwast.TypePtr(
            True, fun.result, x_srcloc=fun.x_srcloc, x_type=new_sig.params[-1].type)
        result_param = cwast.FunParam(id_gen.NewName(
            "result"), result_type, x_srcloc=fun.x_srcloc)
        fun.params.append(result_param)
        fun.result = MakeTypeVoid(tc, fun.x_srcloc)
    changing_params = {}

    # note: new_sig may contain an extra param at the end
    for p, old, new in zip(fun.params, old_sig.params, new_sig.params):
        if old.type != new.type:
            changing_params[p] = new.type
            p.type = cwast.TypePtr(
                False, p.type, x_srcloc=p.x_srcloc, x_type=new.type)
    assert result_changes or changing_params
    return changing_params, result_changes


def RewriteLargeArgsCalleeSide(fun: cwast.DefFun, new_sig: cwast.TypeFun,
                               tc: types.TypeCorpus, id_gen: identifier.IdGen):
    changing_params, result_changes = _FixupFunctionPrototypeForLargArgs(
        fun, new_sig, tc, id_gen)

    # print([k.name for k, v in changing_params.items()], result_changes)

    def replacer(node, field) -> Optional[Any]:

        if isinstance(node, cwast.Id) and node.x_symbol in changing_params:
            new_node = cwast.ExprDeref(
                node, x_srcloc=node.x_srcloc, x_type=node.x_type)
            typify.UpdateNodeType(tc, node, changing_params[node.x_symbol])
            return new_node
        elif isinstance(node, cwast.StmtReturn) and node.x_target == fun and result_changes:
            result_param: cwast.FunParam = fun.params[-1]
            result_type = result_param.type.x_type
            assert isinstance(result_type, cwast.TypePtr)
            lhs = cwast.ExprDeref(
                cwast.Id(result_param.name, "", x_srcloc=node.x_srcloc,
                         x_type=result_type, x_symbol=result_param),
                x_srcloc=node.x_srcloc, x_type=result_type.type)
            assign = cwast.StmtAssignment(
                lhs, node.expr_ret, x_srcloc=node.x_srcloc)
            node.expr_ret = cwast.ValVoid(
                x_srcloc=node.x_srcloc, x_type=tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))
            return cwast.EphemeralList([assign, node], x_srcloc=node.x_srcloc)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
    cwast.EliminateEphemeralsRecursively(fun)


def RewriteLargeArgsCallerSide(fun: cwast.DefFun, fun_sigs_with_large_args,
                               tc: types.TypeCorpus, id_gen: identifier.IdGen):

    def replacer(call, field) -> Optional[Any]:
        if isinstance(call, cwast.ExprCall) and call.callee.x_type in fun_sigs_with_large_args:
            old_sig: cwast.TypeFun = call.callee.x_type
            new_sig: cwast.TypeFun = fun_sigs_with_large_args[old_sig]
            typify.UpdateNodeType(tc, call.callee, new_sig)
            expr_body = []
            expr = cwast.ExprStmt(
                expr_body, x_srcloc=call.x_srcloc, x_type=call.x_type)
            # note: new_sig might be longer if the result type was changed
            for n, (old, new) in enumerate(zip(old_sig.params, new_sig.params)):
                if old.type != new.type:
                    new_def = cwast.DefVar(False, True, id_gen.NewName(f"arg{n}"),
                                           cwast.TypeAuto(
                                               x_srcloc=call.x_srcloc, x_type=old.type),
                                           call.args[n],
                                           x_srcloc=call.x_srcloc)
                    expr_body.append(new_def)
                    name = cwast.Id(new_def.name, "",
                                    x_srcloc=call.x_srcloc, x_type=old.type, x_symbol=new_def)
                    call.args[n] = cwast.ExprAddrOf(
                        False, name, x_srcloc=call.x_srcloc, x_type=new.type)
            if len(old_sig.params) != len(new_sig.params):
                # the result is not a argument
                new_def = cwast.DefVar(True, id_gen.NewName("result"),
                                       cwast.TypeAuto(x_srcloc=call.x_srcloc),
                                       cwast.ValUndef(x_srcloc=call.x_srcloc),
                                       x_srcloc=call.x_srcloc, x_type=old_sig.result)
                name = cwast.Id(new_def.name, "",
                                x_srcloc=call.x_srcloc, x_type=old_sig.result, x_symbol=new_def)
                call.args.append(cwast.ExprAddrOf(
                    True, name, x_srcloc=call.x_srcloc, x_type=new_sig.params[-1].type))
                typify.UpdateNodeType(
                    tc, call, tc.insert_base_type(cwast.BASE_TYPE_KIND.VOID))
                expr_body.append(new_def)
                expr_body.append(cwast.StmtExpr(
                    False, call, x_srcloc=call.x_srcloc))
                expr_body.append(cwast.StmtReturn(
                    expr_ret=name, x_srcloc=call.x_srcloc, x_target=expr))
            else:
                expr_body.append(cwast.StmtReturn(
                    expr_ret=call, x_srcloc=call.x_srcloc, x_target=expr))
            return expr
        return None
    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)
