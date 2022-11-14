#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import dataclasses
from inspect import signature
from math import exp
import sys
import logging

from FrontEnd import cwast
from FrontEnd import symtab
from FrontEnd import types

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


def ComputeStringSize(raw: bool, string: str) -> int:
    assert string[0] == '"'
    assert string[-1] == '"'
    string = string[1:-1]
    n = len(string)
    if raw:
        return n
    esc = False
    for c in string:
        if esc:
            esc = False
            if c == "x":
                n -= 3
            else:
                n -= 1
        elif c == "\\":
            esc = True
    return 8


def ParseInt(num: str) -> int:
    num = num.replace("_", "")
    if num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64"):
        return int(num[: -3])
    elif num[-2:] in ("u8", "s8"):
        return int(num[: -2])
    else:
        return int(num)


def ParseArrayIndex(pos: str) -> int:
    return int(pos)


class TypeContext:
    def __init__(self, symtab, mod_name):
        self.symtab: symtab.SymTab = symtab
        self.mod_name: str = mod_name
        self.enclosing_fun: Optional[cwast.DefFun] = None
        self._enclosing_rec_type: List[types.CanonType] = []
        self._target_type: List[types.CanonType] = [types.NO_TYPE]

    def push_target(self, cstr: types.CanonType):
        """use to suport limited type inference

        contains the type the current expression/type is expected to
        have or types.types.NO_TYPE
        """

        self._target_type.append(cstr)

    def pop_target(self):
        self._target_type.pop(-1)

    def get_target_type(self):
        return self._target_type[-1]


class TypeTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    TODO: get rid of this class
    """

    def __init__(self, uint_kind, sint_kind):
        self.corpus = types.TypeCorpus(uint_kind, sint_kind)

    def type_link(self, node) -> types.CanonType:
        return node.x_type

    def field_link(self, node) -> cwast.RecField:
        return node.x_field

    def compute_dim(self, node, ctx) -> int:
        if isinstance(node, cwast.ValNum):
            return ParseInt(node.number)
        elif isinstance(node, cwast.Id):
            node = ctx.symtab.get_definition_for_symbol(node)
            return self.compute_dim(node, ctx)
        elif isinstance(node, cwast.DefConst):
            return self.compute_dim(node.value, ctx)
        else:
            assert False, f"unexpected dim node: {node}"

    def annotate(self, node, cstr: types.CanonType):
        assert isinstance(
            cstr, cwast.TYPE_CORPUS_NODES), f"bad type corpus node {repr(cstr)}"
        assert isinstance(
            node, cwast.TYPED_ANNOTATED_NODES), f"node not meant for type annotation: {node}"
        assert cstr, f"No valid type for {node}"
        assert node.x_type is None, f"duplicate annotation for {node}"
        node.x_type = cstr
        return cstr

    def annotate_field(self, node, field_node: cwast.RecField):
        assert isinstance(node, (cwast.ExprField, cwast.FieldVal))
        assert node.x_field is None
        node.x_field = field_node

    def is_compatible_for_as(self, src: types.CanonType, dst: types.CanonType) -> bool:
        # TODO: deal with distinct types

        if types.is_int(src):
            return types.is_int(dst) or types.is_real(dst)

    def typify_node(self, node,  ctx: TypeContext) -> types.CanonType:
        target_type = ctx.get_target_type()
        extra = "" if target_type == types.NO_TYPE else f"[{target_type}]"
        logger.info(f"TYPIFYING{extra} {node}")
        cstr = None
        if cwast.NF.TYPE_ANNOTATED in node.__class__.FLAGS:
            cstr = node.x_type
        if cstr is not None:
            # has been typified already
            return cstr
        if isinstance(node, cwast.Comment):
            return types.NO_TYPE
        elif isinstance(node, cwast.Id):
            # this case is why we need the sym_tab
            def_node = ctx.symtab.get_definition_for_symbol(node)
            # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
            cstr = self.typify_node(def_node, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.TypeBase):
            return self.annotate(node, self.corpus.insert_base_type(node.base_type_kind))
        elif isinstance(node, cwast.TypePtr):
            t = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_ptr_type(node.mut, t))
        elif isinstance(node, cwast.TypeSlice):
            t = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_slice_type(node.mut, t))
        elif isinstance(node, cwast.FunParam):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
            params = [self.typify_node(p, ctx)
                      for p in node.params if not isinstance(p, cwast.Comment)]
            result = self.typify_node(node.result, ctx)
            cstr = self.corpus.insert_fun_type(params, result)
            self.annotate(node, cstr)
            if isinstance(node, cwast.DefFun) and not node.extern:
                save_fun = ctx.enclosing_fun
                ctx.enclosing_fun = node
                for c in node.body:
                    self.typify_node(c, ctx)
                ctx.enclosing_fun = save_fun
            return cstr
        elif isinstance(node, cwast.TypeArray):
            # note this is the only place where we need a comptime eval for types
            t = self.typify_node(node.type, ctx)
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.size, ctx)
            ctx.pop_target()
            dim = self.compute_dim(node.size, ctx)
            return self.annotate(node, self.corpus.insert_array_type(False, dim, t))
        elif isinstance(node, cwast.RecField):
            cstr = self.typify_node(node.type, ctx)
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefRec):
            # allow recursive definitions referring back to rec inside
            # the fields
            cstr = self.corpus.insert_rec_type(node.name, node)
            self.annotate(node, cstr)
            for f in node.fields:
                self.typify_node(f, ctx)
            return cstr
        elif isinstance(node, cwast.EnumVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value_or_auto, cwast.ValAuto):
                cstr = self.typify_node(node.value_or_auto, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefEnum):
            cstr = self.corpus.insert_enum_type(
                f"{ctx.mod_name}/{node.name}", node)
            base_type = self.corpus.insert_base_type(node.base_type_kind)
            ctx.push_target(cstr)
            for f in node.items:
                if not isinstance(f, cwast.Comment):
                    self.typify_node(f, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.DefType):
            cstr = self.typify_node(node.type, ctx)
            if node.wrapped:
                cstr = self.corpus.insert_wrapped_type(cstr, node)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.TypeSum):
            # this is tricky code to ensure that children of TypeSum
            # are not TypeSum themselves on the canonical side
            pieces = [self.typify_node(f, ctx) for f in node.types]
            return self.annotate(node, self.corpus.insert_sum_type(pieces))
        if isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ValVoid):
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.VOID))
        elif isinstance(node, cwast.ValUndef):
            assert False, "Must not try to typify UNDEF"
        elif isinstance(node, cwast.ValNum):
            cstr = self.corpus.num_type(node.number)
            if cstr != types.NO_TYPE:
                return self.annotate(node, cstr)
            return self.annotate(node, ctx.get_target_type())
        elif isinstance(node, cwast.TypeAuto):
            assert False, "Must not try to typify TypeAuto"
        elif isinstance(node, cwast.ValAuto):
            assert False, "Must not try to typify ValAuto"
        elif isinstance(node, cwast.DefConst):
            ctx.push_target(types.NO_TYPE if
                            isinstance(node.type_or_auto, cwast.TypeAuto) else
                            self.typify_node(node.type_or_auto, ctx))
            cstr = self.typify_node(node.value, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.IndexVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value_or_undef, cwast.ValUndef):
                self.typify_node(node.value_or_undef, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ValArray):
            cstr = self.typify_node(node.type, ctx)
            ctx.push_target(cstr)
            for x in node.inits_array:
                if isinstance(x, cwast.IndexVal):
                    self.typify_node(x, ctx)
            ctx.pop_target()
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.expr_size, ctx)
            ctx.pop_target()
            dim = self.compute_dim(node.expr_size, ctx)
            return self.annotate(node, self.corpus.insert_array_type(False, dim, cstr))
        elif isinstance(node, cwast.ValRec):
            cstr = self.typify_node(node.type, ctx)
            assert isinstance(cstr, cwast.DefRec)
            all_fields: List[cwast.RecField] = [
                f for f in cstr.fields if isinstance(f, cwast.RecField)]
            for val in node.inits_rec:
                if not isinstance(val, cwast.FieldVal):
                    continue
                if val.init_field:
                    while True:
                        field_node = all_fields.pop(0)
                        if val.init_field == field_node.name:
                            break
                else:
                    field_node = all_fields.pop(0)
                # TODO: make sure this link is set
                field_cstr = self.type_link(field_node)
                self.annotate_field(val, field_node)
                self.annotate(val, field_cstr)
                ctx.push_target(field_cstr)
                self.typify_node(val.value, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ValString):
            dim = ComputeStringSize(node.raw, node.string)
            cstr = self.corpus.insert_array_type(
                False, dim, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.U8))
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ExprIndex):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.expr_index, ctx)
            ctx.pop_target()
            cstr = self.typify_node(node.container, ctx)
            return self.annotate(node, types.get_contained_type(cstr))
        elif isinstance(node, cwast.ExprField):
            cstr = self.typify_node(node.container, ctx)
            field_node = self.corpus.lookup_rec_field(cstr, node.field)
            self.annotate_field(node, field_node)
            return self.annotate(node, field_node.x_type)
        elif isinstance(node, cwast.DefVar):
            cstr = (types.NO_TYPE if isinstance(node.type_or_auto, cwast.TypeAuto)
                    else self.typify_node(node.type_or_auto, ctx))
            initial_cstr = types.NO_TYPE
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                initial_cstr = self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            # special hack for arrays: if variable is mutable and of type array,
            # this means we can update array elements but we cannot assign a new
            # array to the variable.
            if isinstance(initial_cstr, cwast.TypeArray) and node.mut:
                cstr = types.get_contained_type(initial_cstr)
                dim = types.get_array_dim(initial_cstr)
                return self.annotate(node, self.corpus.insert_array_type(True, dim, cstr))
            return self.annotate(node, cstr if cstr != types.NO_TYPE else initial_cstr)
        elif isinstance(node, cwast.ExprRange):
            cstr = self.typify_node(node.end, ctx)
            if not isinstance(node.begin_or_auto, cwast.ValAuto):
                self.typify_node(node.begin_or_auto, ctx)
            if not isinstance(node.step_or_auto, cwast.ValAuto):
                self.typify_node(node.step_or_auto, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.StmtFor):
            ctx.push_target(types.NO_TYPE if
                            isinstance(node.type_or_auto, cwast.TypeAuto)
                            else self.typify_node(node.type_or_auto, ctx))
            cstr = self.typify_node(node.range, ctx)
            ctx.pop_target()
            self.annotate(node, cstr)
            for c in node.body:
                self.typify_node(c, ctx)
            return cstr
        elif isinstance(node, cwast.ExprDeref):
            cstr = self.typify_node(node.expr, ctx)
            assert isinstance(cstr, cwast.TypePtr)
            # TODO: how is mutability propagated?
            return self.annotate(node, cstr.type)
        elif isinstance(node, cwast.Expr1):
            cstr = self.typify_node(node.expr, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Expr2):
            cstr = self.typify_node(node.expr1, ctx)
            if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE:
                ctx.push_target(cstr)
                self.typify_node(node.expr2, ctx)
                ctx.pop_target()
            else:
                self.typify_node(node.expr2, ctx)

            if node.binary_expr_kind in cwast.BINOP_BOOL:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
            elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.SINT)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Expr3):
            self.typify_node(node.cond, ctx)
            cstr = self.typify_node(node.expr_t, ctx)
            ctx.push_target(cstr)
            self.typify_node(node.expr_f, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.StmtExpr):
            self.typify_node(node.expr, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.ExprCall):
            cstr = self.typify_node(node.callee, ctx)
            assert isinstance(cstr, cwast.TypeFun)
            assert len(cstr.params) == len(node.args)
            for p, a in zip(cstr.params, node.args):
                ctx.push_target(p.type)
                self.typify_node(a, ctx)
                ctx.pop_target()
            return self.annotate(node, cstr.result)
        elif isinstance(node, cwast.StmtReturn):
            cstr = ctx.enclosing_fun.result.x_type
            ctx.push_target(cstr)
            self.typify_node(node.expr_ret, ctx)
            ctx.pop_target()
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtIf):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body_f:
                self.typify_node(c, ctx)
            for c in node.body_t:
                self.typify_node(c, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.Case):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body:
                self.typify_node(c, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtCond):
            for c in node.cases:
                self.typify_node(c, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtBlock):
            for c in node.body:
                self.typify_node(c, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtBreak):
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtContinue):
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtAssignment):
            var_cstr = self.typify_node(node.lhs, ctx)
            ctx.push_target(var_cstr)
            self.typify_node(node.expr, ctx)
            ctx.pop_target()
            return types.NO_TYPE
        elif isinstance(node, cwast.StmtCompoundAssignment):
            var_cstr = self.typify_node(node.lhs, ctx)
            ctx.push_target(var_cstr)
            self.typify_node(node.expr, ctx)
            ctx.pop_target()
            return types.NO_TYPE
        elif isinstance(node, (cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
            cstr = self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.ExprIs):
            self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ExprLen):
            self.typify_node(node.container, ctx)
            return self.annotate(node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprChop):
            if not isinstance(node.start, cwast.ValAuto):
                self.typify_node(node.start, ctx)
            if not isinstance(node.width, cwast.ValAuto):
                self.typify_node(node.width, ctx)
            cstr_cont = self.typify_node(node.container, ctx)
            cstr = types.get_contained_type(cstr_cont)
            mut = types.is_mutable(cstr_cont)
            return self.annotate(node, self.corpus.insert_slice_type(mut, cstr))
        elif isinstance(node, cwast.ExprAddrOf):
            cstr_expr = self.typify_node(node.expr, ctx)
            return self.annotate(node, self.corpus.insert_ptr_type(node.mut, cstr_expr))
        elif isinstance(node, cwast.ExprOffsetof):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprSizeof):
            cstr = self.typify_node(node.type, ctx)
            return self.annotate(node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.Try):
            cstr = self.typify_node(node.type, ctx)
            cstr_expr = self.typify_node(node.expr, ctx)
            cstr_complement = self.corpus.insert_sum_complement(
                cstr_expr, cstr)
            ctx.push_target(cstr_complement)
            self.typify_node(node.catch, ctx)
            ctx.pop_target()
            return self.annotate(node, cstr)
        elif isinstance(node, cwast.Catch):
            cstr = self.annotate(node, ctx.get_target_type())
            for c in node.body_except:
                self.typify_node(c, ctx)
            return cstr
        elif isinstance(node, cwast.StmtWhile):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            for c in node.body:
                self.typify_node(c, ctx)
            return types.NO_TYPE
        elif isinstance(node, cwast.Import):
            return types.NO_TYPE
        else:
            assert False, f"unexpected node {node}"

    def verify_node(self, node, ctx: TypeContext):
        if isinstance(node, cwast.TYPED_ANNOTATED_NODES):
            assert node.x_type is not None, f"untypified node {node}"
        if isinstance(node, cwast.ValArray):
            cstr = self.type_link(node.type)
            for x in node.inits_array:
                if not isinstance(x, cwast.Comment):
                    assert cstr == self.type_link(
                        x), f"expected {cstr} got {self.type_link(x)}"
        elif isinstance(node, cwast.ValRec):
            for x in node.inits_rec:
                if isinstance(x, cwast.IndexVal):
                    field_node = self.field_link(x)
                    assert self.type_link(field_node) == self.type_link(x)
        elif isinstance(node, cwast.RecField):
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                type_cstr = self.type_link(node.type)
                initial_cstr = self.type_link(node.initial_or_undef)
                assert types.is_compatible(
                    initial_cstr, type_cstr), f"{node}: {type_cstr} {initial_cstr}"
        elif isinstance(node, cwast.ExprIndex):
            cstr = self.type_link(node)
            assert cstr == types.get_contained_type(
                self.type_link(node.container))
        elif isinstance(node, cwast.ExprField):
            cstr = self.type_link(node)
            field_node = self.field_link(node)
            assert cstr == self.type_link(field_node)
        elif isinstance(node, cwast.DefVar):
            cstr = self.type_link(node)
            if node.mut and isinstance(cstr, cwast.TypeArray):
                assert cstr.mut
                cstr = self.corpus.drop_mutability(cstr)
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                initial_cstr = self.type_link(node.initial_or_undef)
                assert types.is_compatible(initial_cstr, cstr)
            if not isinstance(node.type_or_auto, cwast.TypeAuto):
                type_cstr = self.type_link(node.type_or_auto)
                assert cstr == type_cstr, f"{node}: expected {cstr} got {type_cstr}"
        elif isinstance(node, cwast.ExprRange):
            cstr = self.type_link(node)
            if not isinstance(node.begin_or_auto, cwast.ValAuto):
                assert cstr == self.type_link(node.begin_or_auto)
            assert cstr == self.type_link(node.end)
            if not isinstance(node.step_or_auto, cwast.ValAuto):
                assert cstr == self.type_link(node.step_or_auto)
        elif isinstance(node, cwast.StmtFor):
            if not isinstance(node.type_or_auto, cwast.TypeAuto):
                assert self.type_link(
                    node.range) == self.type_link(node.type_or_auto), f"type mismatch in FOR"
        elif isinstance(node, cwast.ExprDeref):
            cstr = self.type_link(node)
            assert cstr == self.type_link(node.expr).type
        elif isinstance(node, cwast.Expr1):
            cstr = self.type_link(node)
            assert cstr == self.type_link(node.expr)
        elif isinstance(node, cwast.Expr2):
            cstr = self.type_link(node)
            cstr1 = self.type_link(node.expr1)
            cstr2 = self.type_link(node.expr2)
            if node.binary_expr_kind in cwast.BINOP_BOOL:
                assert cstr1 == cstr2, f"binop mismatch {cstr1} != {cstr2}"
                assert types.is_bool(cstr)
            elif node.binary_expr_kind in (cwast.BINARY_EXPR_KIND.PADD,
                                           cwast.BINARY_EXPR_KIND.PSUB):
                assert cstr == cstr1
                assert types.is_int(cstr2)
            elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
                assert (isinstance(cstr1, cwast.TypePtr) and isinstance(cstr2, cwast.TypePtr) and
                        cstr1.type == cstr2.type)
                assert cstr == self.corpus.insert_base_type(
                    cwast.BASE_TYPE_KIND.SINT)
            else:
                assert cstr == cstr1
                assert cstr == cstr2
        elif isinstance(node, cwast.Expr3):
            cstr = self.type_link(node)
            cstr_t = self.type_link(node.expr_t)
            cstr_f = self.type_link(node.expr_f)
            cstr_cond = self.type_link(node.cond)
            assert cstr == cstr_t
            assert cstr == cstr_f
            assert types.is_bool(cstr_cond)
        elif isinstance(node, cwast.ExprCall):
            result = self.type_link(node)
            fun = self.type_link(node.callee)
            assert (fun, cwast.TypeFun)
            assert fun.result == result
            for p, a in zip(fun.params, node.args):
                arg_cstr = self.type_link(a)
                assert types.is_compatible(
                    arg_cstr, p.type), f"incompatible fun arg: {a} {arg_cstr} expected={p}"
        elif isinstance(node, cwast.StmtReturn):
            fun = self.type_link(ctx.enclosing_fun)
            assert isinstance(fun, cwast.TypeFun)
            actual = self.type_link(node.expr_ret)
            assert types.is_compatible(
                actual, fun.result), f"{node}: {actual} {fun.result}"
        elif isinstance(node, cwast.StmtIf):
            assert types.is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.Case):
            assert types.is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.StmtWhile):
            assert types.is_bool(self.type_link(node.cond))
        elif isinstance(node, cwast.StmtAssignment):
            var_cstr = self.type_link(node.lhs)
            expr_cstr = self.type_link(node.expr)
            assert types.is_compatible(expr_cstr, var_cstr)
        elif isinstance(node, cwast.StmtCompoundAssignment):
            var_cstr = self.type_link(node.lhs)
            expr_cstr = self.type_link(node.expr)
            assert types.is_compatible(expr_cstr, var_cstr)
        elif isinstance(node, cwast.StmtExpr):
            cstr = self.type_link(node.expr)
            assert types.is_void(cstr) != node.discard
        elif isinstance(node, cwast.ExprAs):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprUnsafeCast):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprBitCast):
            src = self.type_link(node.expr)
            dst = self.type_link(node.type)
            # TODO
            # assert is_compatible_for_as(src, dst)
        elif isinstance(node, cwast.ExprIs):
            assert types.is_bool(self.type_link(node))
        elif isinstance(node, cwast.ExprLen):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.ExprChop):
            cstr = self.type_link(node)
            cstr_cont = self.type_link(node.container)
            assert types.get_contained_type(
                cstr_cont) == types.get_contained_type(cstr)
            assert types.is_mutable(cstr_cont) == types.is_mutable(cstr)
            if not isinstance(node.start, cwast.ValAuto):
                assert types.is_int(self.type_link(node.start))
            if not isinstance(node.width, cwast.ValAuto):
                assert types.is_int(self.type_link(node.width))
        elif isinstance(node, cwast.Id):
            cstr = self.type_link(node)
            assert cstr != types.NO_TYPE
        elif isinstance(node, cwast.ExprAddrOf):
            cstr_expr = self.type_link(node.expr)
            cstr = self.type_link(node)
            assert isinstance(cstr, cwast.TypePtr) and cstr.type == cstr_expr
        elif isinstance(node, cwast.ExprOffsetof):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.ExprSizeof):
            assert self.type_link(node) == self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT)
        elif isinstance(node, cwast.Try):
            all = set()
            cstr = self.type_link(node)
            if isinstance(cstr, cwast.TypeSum):
                for c in cstr.types:
                    all.add(id(c))
            else:
                all.add(id(cstr))
            cstr_complement = self.type_link(node.catch)
            if isinstance(cstr_complement, cwast.TypeSum):
                for c in cstr_complement.types:
                    all.add(id(c))
            else:
                all.add(id(cstr_complement))
            assert all == set(id(c) for c in self.type_link(node.expr).types)
        elif isinstance(node, cwast.Catch):
            pass
        elif isinstance(node, (cwast.Comment, cwast.DefMod, cwast.DefFun, cwast.FunParam,
                               cwast.TypeBase, cwast.TypeArray, cwast.TypePtr, cwast.Id,
                               cwast.TypeSlice, cwast.TypeSum, cwast.TypeAuto, cwast.ValAuto, cwast.ValUndef,
                               cwast.ValNum, cwast.DefType, cwast.DefRec, cwast.ValTrue,
                               cwast.ValFalse, cwast.ValVoid, cwast.DefEnum, cwast.EnumVal,
                               cwast.TypeFun, cwast.DefConst, cwast.ValString,
                               cwast.IndexVal, cwast.FieldVal, cwast.StmtBlock, cwast.StmtBreak,
                               cwast.StmtContinue, cwast.StmtDefer, cwast.StmtCond, cwast.Import)):
            pass
        else:
            assert False, f"unsupported  node type: {node.__class__} {node}"

    def verify_node_recursively(self, node, ctx: TypeContext):
        if isinstance(node, cwast.DefFun):
            ctx.enclosing_fun = node
        self.verify_node(node, ctx)
        for c in node.__class__.FIELDS:
            nfd = cwast.ALL_FIELDS_MAP[c]
            if nfd.kind is cwast.NFK.NODE:
                self.verify_node_recursively(getattr(node, c), ctx)
            elif nfd.kind is cwast.NFK.LIST:
                for cc in getattr(node, c):
                    self.verify_node_recursively(cc, ctx)


def ExtractTypeTab(mod_topo_order: List[cwast.DefMod],
                   mod_map: Dict[str, cwast.DefMod], symtab: Dict[str, symtab.SymTab]) -> TypeTab:
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.
    """
    typetab = TypeTab(cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    for m in mod_topo_order:
        ctx = TypeContext(symtab_map[m], m)
        for node in mod_map[m].body_mod:
            typetab.typify_node(node, ctx)
    return typetab


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = []
    try:
        while True:
            stream = cwast.ReadTokens(sys.stdin)
            t = next(stream)
            assert t == "("
            sexpr = cwast.ReadSExpr(stream)
            # print(sexpr)
            asts.append(sexpr)
    except StopIteration:
        pass

    mod_topo_order, mod_map = symtab.ModulesInTopologicalOrder(asts)
    symtab_map = symtab.ExtractAllSymTabs(mod_topo_order, mod_map)
    typetab = ExtractTypeTab(mod_topo_order, mod_map, symtab_map)
    for m in mod_topo_order:
        typetab.verify_node_recursively(mod_map[m], TypeContext(None, None))
    for t in typetab.corpus.corpus:
        print(t)
