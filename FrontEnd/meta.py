#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

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


def ParseNum(num: str, kind: cwast.BASE_TYPE_KIND) -> int:
    # TODO use kind argument
    num = num.replace("_", "")
    if num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64"):
        return int(num[: -3])
    elif num[-2:] in ("u8", "s8"):
        return int(num[: -2])
    elif num[-4:] in ("uint", "sint"):
        return int(num[: -4])
    elif num[-3:] in ("r32", "r64"):
        return float(num[: -3])
    if num[0] == "'":
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return 10
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1])
    else:
        return int(num)


def ParseArrayIndex(pos: str) -> int:
    return int(pos)


class TypeContext:
    def __init__(self, mod_name):
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


def is_compatible_for_as(self, src: types.CanonType, dst: types.CanonType) -> bool:
    # TODO: deal with distinct types

    if types.is_int(src):
        return types.is_int(dst) or types.is_real(dst)


def _ComputeArrayLength(node) -> int:
    if isinstance(node, cwast.ValNum):
        return ParseNum(node.number, cwast.BASE_TYPE_KIND.INVALID)
    elif isinstance(node, cwast.Id):
        node = node.x_symbol
        return _ComputeArrayLength(node)
    elif isinstance(node, cwast.DefConst):
        return _ComputeArrayLength(node.value)
    else:
        assert False, f"unexpected dim node: {node}"


def _AnnotateType(corpus, node, cstr: types.CanonType):
    logger.info(f"TYPE of {node}: {corpus.canon_name(cstr)}")
    assert cwast.NF.TYPE_CORPUS in cstr.__class__.FLAGS, f"bad type corpus node {repr(cstr)}"
    assert cwast.NF.TYPE_ANNOTATED in node.__class__.FLAGS, f"node not meant for type annotation: {node}"
    assert cstr, f"No valid type for {node}"
    assert node.x_type is None, f"duplicate annotation for {node}"
    node.x_type = cstr
    return cstr


def _AnnotateField(node, field_node: cwast.RecField):
    assert isinstance(
        node, (cwast.ExprField, cwast.FieldVal, cwast.ExprOffsetof))
    assert node.x_field is None
    node.x_field = field_node


class TypeTab:
    """Type Table

    Requires SymTab info to resolve DefType symnbols
    TODO: get rid of this class
    """

    def __init__(self, corpus: types.TypeCorpus):
        self.corpus: types.TypeCorpus = corpus

    def typify_node(self, node,  ctx: TypeContext) -> types.CanonType:
        target_type = ctx.get_target_type()
        extra = "" if target_type == types.NO_TYPE else f"[{target_type}]"
        logger.debug(f"TYPIFYING{extra} {node}")
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
            def_node = node.x_symbol
            # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
            cstr = self.typify_node(def_node, ctx)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.TypeBase):
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(node.base_type_kind))
        elif isinstance(node, cwast.TypePtr):
            t = self.typify_node(node.type, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_ptr_type(node.mut, t))
        elif isinstance(node, cwast.TypeSlice):
            t = self.typify_node(node.type, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_slice_type(node.mut, t))
        elif isinstance(node, cwast.FunParam):
            cstr = self.typify_node(node.type, ctx)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
            params = [self.typify_node(p, ctx)
                      for p in node.params if not isinstance(p, cwast.Comment)]
            result = self.typify_node(node.result, ctx)
            cstr = self.corpus.insert_fun_type(params, result)
            _AnnotateType(self.corpus, node, cstr)
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
            dim = _ComputeArrayLength(node.size)
            return _AnnotateType(self.corpus, node, self.corpus.insert_array_type(node.mut, dim, t))
        elif isinstance(node, cwast.RecField):
            cstr = self.typify_node(node.type, ctx)
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.DefRec):
            # allow recursive definitions referring back to rec inside
            # the fields
            cstr = self.corpus.insert_rec_type(node.name, node)
            _AnnotateType(self.corpus, node, cstr)
            for f in node.fields:
                self.typify_node(f, ctx)
            # we delay this until after fields have been typified
            self.corpus.set_size_and_offset_for_rec_type(node)
            return cstr
        elif isinstance(node, cwast.EnumVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value_or_auto, cwast.ValAuto):
                cstr = self.typify_node(node.value_or_auto, ctx)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.DefEnum):
            cstr = self.corpus.insert_enum_type(
                f"{ctx.mod_name}/{node.name}", node)
            base_type = self.corpus.insert_base_type(node.base_type_kind)
            ctx.push_target(cstr)
            for f in node.items:
                if not isinstance(f, cwast.Comment):
                    self.typify_node(f, ctx)
            ctx.pop_target()
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.DefType):
            cstr = self.typify_node(node.type, ctx)
            if node.wrapped:
                cstr = self.corpus.insert_wrapped_type(cstr)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.TypeSum):
            # this is tricky code to ensure that children of TypeSum
            # are not TypeSum themselves on the canonical side
            pieces = [self.typify_node(f, ctx) for f in node.types]
            return _AnnotateType(self.corpus, node, self.corpus.insert_sum_type(pieces))
        if isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ValVoid):
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.VOID))
        elif isinstance(node, cwast.ValUndef):
            assert False, "Must not try to typify UNDEF"
        elif isinstance(node, cwast.ValNum):
            cstr = self.corpus.num_type(node.number)
            if cstr != types.NO_TYPE:
                return _AnnotateType(self.corpus, node, cstr)
            return _AnnotateType(self.corpus, node, ctx.get_target_type())
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
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.IndexVal):
            cstr = ctx.get_target_type()
            if not isinstance(node.value_or_undef, cwast.ValUndef):
                self.typify_node(node.value_or_undef, ctx)
            if not isinstance(node.init_index, cwast.ValAuto):
                ctx.push_target(self.corpus.insert_base_type(
                    cwast.BASE_TYPE_KIND.UINT))
                self.typify_node(node.init_index, ctx)
                ctx.pop_target()
            return _AnnotateType(self.corpus, node, cstr)
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
            dim = _ComputeArrayLength(node.expr_size)
            return _AnnotateType(self.corpus, node, self.corpus.insert_array_type(False, dim, cstr))
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
                field_cstr = field_node.x_type
                _AnnotateField(val, field_node)
                _AnnotateType(self.corpus, val, field_cstr)
                ctx.push_target(field_cstr)
                self.typify_node(val.value, ctx)
                ctx.pop_target()
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.ValString):
            dim = ComputeStringSize(node.raw, node.string)
            cstr = self.corpus.insert_array_type(
                False, dim, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.U8))
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.ExprIndex):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
            self.typify_node(node.expr_index, ctx)
            ctx.pop_target()
            cstr = self.typify_node(node.container, ctx)
            return _AnnotateType(self.corpus, node, types.get_contained_type(cstr))
        elif isinstance(node, cwast.ExprField):
            cstr = self.typify_node(node.container, ctx)
            field_node = self.corpus.lookup_rec_field(cstr, node.field)
            _AnnotateField(node, field_node)
            return _AnnotateType(self.corpus, node, field_node.x_type)
        elif isinstance(node, cwast.DefVar):
            cstr = (types.NO_TYPE if isinstance(node.type_or_auto, cwast.TypeAuto)
                    else self.typify_node(node.type_or_auto, ctx))
            initial_cstr = types.NO_TYPE
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                ctx.push_target(cstr)
                initial_cstr = self.typify_node(node.initial_or_undef, ctx)
                ctx.pop_target()
            if cstr == types.NO_TYPE:
                cstr = initial_cstr
            # special hack for arrays: if variable is mutable and of type array,
            # this means we can update array elements but we cannot assign a new
            # array to the variable.
            # TODO: revisit this
            if isinstance(cstr, cwast.TypeArray) and node.mut:
                cstr = self.corpus.insert_array_type(True,
                                                     types.get_array_dim(cstr),
                                                     types.get_contained_type(cstr))
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.ExprDeref):
            cstr = self.typify_node(node.expr, ctx)
            assert isinstance(cstr, cwast.TypePtr)
            # TODO: how is mutability propagated?
            return _AnnotateType(self.corpus, node, cstr.type)
        elif isinstance(node, cwast.Expr1):
            cstr = self.typify_node(node.expr, ctx)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.Expr2):
            cstr = self.typify_node(node.expr1, ctx)
            if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE and types.is_number(cstr):
                ctx.push_target(cstr)
                self.typify_node(node.expr2, ctx)
                ctx.pop_target()
            else:
                self.typify_node(node.expr2, ctx)

            if node.binary_expr_kind in cwast.BINOP_BOOL:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
            elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
                cstr = self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.SINT)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.Expr3):
            self.typify_node(node.cond, ctx)
            cstr = self.typify_node(node.expr_t, ctx)
            ctx.push_target(cstr)
            self.typify_node(node.expr_f, ctx)
            ctx.pop_target()
            return _AnnotateType(self.corpus, node, cstr)
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
            return _AnnotateType(self.corpus, node, cstr.result)
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
        elif isinstance(node, cwast.StmtTrap):
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
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, cwast.ExprAsNot):
            cstr = self.typify_node(node.type, ctx)
            union = self.typify_node(node.expr, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_sum_complement(union, cstr))
        elif isinstance(node, cwast.ExprIs):
            self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
        elif isinstance(node, cwast.ExprLen):
            self.typify_node(node.container, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprChop):
            if not isinstance(node.start, cwast.ValAuto):
                self.typify_node(node.start, ctx)
            if not isinstance(node.width, cwast.ValAuto):
                self.typify_node(node.width, ctx)
            cstr_cont = self.typify_node(node.container, ctx)
            cstr = types.get_contained_type(cstr_cont)
            mut = types.is_mutable(cstr_cont)
            return _AnnotateType(self.corpus, node, self.corpus.insert_slice_type(mut, cstr))
        elif isinstance(node, cwast.ExprAddrOf):
            cstr_expr = self.typify_node(node.expr, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_ptr_type(node.mut, cstr_expr))
        elif isinstance(node, cwast.ExprOffsetof):
            cstr = self.typify_node(node.type, ctx)
            field_node = self.corpus.lookup_rec_field(cstr, node.field)
            _AnnotateField(node, field_node)
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprSizeof):
            cstr = self.typify_node(node.type, ctx)
            return _AnnotateType(self.corpus, node, self.corpus.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
        elif isinstance(node, cwast.ExprTryAs):
            cstr = self.typify_node(node.type, ctx)
            self.typify_node(node.expr, ctx)
            if not isinstance(node.default_or_undef, cwast.ValUndef):
                self.typify_node(node.default_or_undef, ctx)
            return _AnnotateType(self.corpus, node, cstr)
        elif isinstance(node, (cwast.StmtStaticAssert)):
            ctx.push_target(self.corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.BOOL))
            self.typify_node(node.cond, ctx)
            ctx.pop_target()
            return types.NO_TYPE
        elif isinstance(node, cwast.Import):
            return types.NO_TYPE
        else:
            assert False, f"unexpected node {node}"


UNTYPED_NODES_TO_BE_TYPECHECKED = (
    cwast.StmtReturn, cwast.StmtIf,
    cwast.StmtAssignment, cwast.StmtCompoundAssignment, cwast.StmtExpr)


def _TypeMismatch(corpus: types.TypeCorpus, msg: str, actual, expected):
    return f"{msg}: actual: {corpus.canon_name(actual)} expected: {corpus.canon_name(expected)}"


def _TypeVerifyNode(node: cwast.ALL_NODES, corpus: types.TypeCorpus, enclosing_fun):
    assert (cwast.NF.TYPE_ANNOTATED in node.__class__.FLAGS or isinstance(
        node, UNTYPED_NODES_TO_BE_TYPECHECKED))

    if isinstance(node, cwast.ValArray):
        cstr = node.type.x_type
        for x in node.inits_array:
            if isinstance(x, cwast.IndexVal):
                if not isinstance(x.init_index, cwast.ValAuto):
                    assert types.is_int(x.init_index.x_type)
                assert cstr == x.x_type, _TypeMismatch(
                    corpus, "type mismatch {x}:", x.x_type, cstr)
    elif isinstance(node, cwast.ValRec):
        for x in node.inits_rec:
            if isinstance(x, cwast.FieldVal):
                field_node = x.x_field
                assert field_node.x_type == x.x_type
    elif isinstance(node, cwast.RecField):
        if not isinstance(node.initial_or_undef, cwast.ValUndef):
            type_cstr = node.type.x_type
            initial_cstr = node.initial_or_undef.x_type
            assert types.is_compatible(
                initial_cstr, type_cstr),  _TypeMismatch(
                    corpus, f"type mismatch {node}:", initial_cstr, type_cstr)
    elif isinstance(node, cwast.ExprIndex):
        cstr = node.x_type
        assert cstr == types.get_contained_type(node.container.x_type)
    elif isinstance(node, cwast.ExprField):
        cstr = node.x_type
        field_node = node.x_field
        assert cstr == field_node.x_type
    elif isinstance(node, cwast.DefVar):
        cstr = node.x_type
        if node.mut and isinstance(cstr, cwast.TypeArray):
            assert cstr.mut
            cstr = corpus.drop_mutability(cstr)
        if not isinstance(node.initial_or_undef, cwast.ValUndef):
            initial_cstr = node.initial_or_undef.x_type
            assert types.is_compatible_for_defvar(initial_cstr, cstr), _TypeMismatch(
                f"incompatible types", initial_cstr, cstr)
        if not isinstance(node.type_or_auto, cwast.TypeAuto):
            type_cstr = node.type_or_auto.x_type
            assert cstr == type_cstr, _TypeMismatch(f"{node}", cstr, type_cstr)
    elif isinstance(node, cwast.ExprDeref):
        cstr = node.x_type
        assert cstr == node.expr.x_type.type
    elif isinstance(node, cwast.Expr1):
        cstr = node.x_type
        assert cstr == node.expr.x_type
    elif isinstance(node, cwast.Expr2):
        cstr = node.x_type
        cstr1 = node.expr1.x_type
        cstr2 = node.expr2.x_type
        if node.binary_expr_kind in cwast.BINOP_BOOL:
            assert cstr1 == cstr2, _TypeMismatch(
                f"binop mismatch in {node}:", cstr1, cstr2)
            assert types.is_bool(cstr)
        elif node.binary_expr_kind in (cwast.BINARY_EXPR_KIND.PADD,
                                       cwast.BINARY_EXPR_KIND.PSUB):
            assert cstr == cstr1
            assert types.is_int(cstr2)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
            assert (isinstance(cstr1, cwast.TypePtr) and isinstance(cstr2, cwast.TypePtr) and
                    cstr1.type == cstr2.type)
            assert cstr == corpus.insert_base_type(
                cwast.BASE_TYPE_KIND.SINT)
        else:
            assert cstr == cstr1
            assert cstr == cstr2
    elif isinstance(node, cwast.Expr3):
        cstr = node.x_type
        cstr_t = node.expr_t.x_type
        cstr_f = node.expr_f.x_type
        cstr_cond = node.cond.x_type
        assert cstr == cstr_t
        assert cstr == cstr_f
        assert types.is_bool(cstr_cond)
    elif isinstance(node, cwast.ExprCall):
        result = node.x_type
        fun = node.callee.x_type
        assert isinstance(fun, cwast.TypeFun)
        assert fun.result == result
        for p, a in zip(fun.params, node.args):
            arg_cstr = a.x_type
            assert types.is_compatible(
                arg_cstr, p.type), _TypeMismatch(f"incompatible fun arg: {a}",  arg_cstr, p)
    elif isinstance(node, cwast.StmtReturn):
        fun = enclosing_fun.x_type
        assert isinstance(fun, cwast.TypeFun)
        actual = node.expr_ret.x_type
        assert types.is_compatible(
            actual, fun.result),  _TypeMismatch(f"{node}", actual, fun.result)
    elif isinstance(node, cwast.StmtIf):
        assert types.is_bool(node.cond.x_type)
    elif isinstance(node, cwast.Case):
        assert types.is_bool(node.cond.x_type)
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr.x_type
        assert types.is_compatible(expr_cstr, var_cstr)
    elif isinstance(node, cwast.StmtCompoundAssignment):
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr.x_type
        assert types.is_compatible(expr_cstr, var_cstr)
    elif isinstance(node, cwast.StmtExpr):
        cstr = node.expr.x_type
        assert types.is_void(cstr) != node.discard
    elif isinstance(node, cwast.ExprAsNot):
        pass
    elif isinstance(node, cwast.ExprAs):
        src = node.expr.x_type
        dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
    elif isinstance(node, cwast.ExprUnsafeCast):
        src = node.expr.x_type
        dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
    elif isinstance(node, cwast.ExprBitCast):
        src = node.expr.x_type
        dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
    elif isinstance(node, cwast.ExprIs):
        assert types.is_bool(node.x_type)
    elif isinstance(node, cwast.ExprLen):
        assert node.x_type == corpus.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprChop):
        cstr = node.x_type
        cstr_cont = node.container.x_type
        assert types.get_contained_type(
            cstr_cont) == types.get_contained_type(cstr)
        assert types.is_mutable(cstr_cont) == types.is_mutable(cstr)
        if not isinstance(node.start, cwast.ValAuto):
            assert types.is_int(node.start.x_type)
        if not isinstance(node.width, cwast.ValAuto):
            assert types.is_int(node.width.x_type)
    elif isinstance(node, cwast.Id):
        cstr = node.x_type
        assert cstr != types.NO_TYPE
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = node.expr.x_type
        cstr = node.x_type
        assert isinstance(cstr, cwast.TypePtr) and cstr.type == cstr_expr
    elif isinstance(node, cwast.ExprOffsetof):
        assert node.x_type == corpus.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprSizeof):
        assert node.x_type == corpus.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprTryAs):
        cstr = node.x_type
        assert cstr == node.type.x_type, _TypeMismatch(f"type mismatch", cstr, node.type.x_type)
        if not isinstance(node.default_or_undef, cwast.ValUndef):
            assert cstr == node.default_or_undef.x_type, _TypeMismatch(f"type mismatch", cstr, node.type.x_type)
        assert types.is_compatible(cstr, node.expr.x_type)
    elif isinstance(node, cwast.ValNum):
        assert isinstance(node.x_type, (cwast.TypeBase, cwast.DefEnum)
                          ), f"bad type for {node}: {node.x_type}"
    elif isinstance(node, cwast.TypeSum):
        assert isinstance(node.x_type, cwast.TypeSum)
    elif isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValVoid)):
        assert isinstance(node.x_type, cwast.TypeBase)
    elif isinstance(node, (cwast.DefFun, cwast.TypeFun)):
        assert isinstance(node.x_type, cwast.TypeFun)
    elif isinstance(node, (cwast.DefType, cwast.TypeBase, cwast.TypeSlice, cwast.IndexVal,
                           cwast.TypeArray, cwast.DefConst, cwast.DefFun,
                           cwast.TypePtr, cwast.FunParam, cwast.DefRec, cwast.DefEnum,
                           cwast.EnumVal, cwast.ValString, cwast.FieldVal)):
        pass
    else:
        assert False, f"unsupported  node type: {node.__class__} {node}"


def DecorateASTWithTypes(mod_topo_order: List[cwast.DefMod],
                         mod_map: Dict[str, cwast.DefMod], type_corpus):
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.

    The following node fields will be initialized:
    * x_type
    * x_field
    * some x_value (only array dimention as they are related to types)
    """
    typetab = TypeTab(type_corpus)
    for m in mod_topo_order:
        ctx = TypeContext(m)
        for node in mod_map[m].body_mod:
            if not isinstance(node, (cwast.Comment, cwast.DefMacro)):
                typetab.typify_node(node, ctx)


def _TypeVerifyNodeRecursively(node, corpus, enclosing_fun):
    if isinstance(node, (cwast.Comment, cwast.DefMacro)):
        return
    logger.info(f"VERIFYING {node}")

    if isinstance(node, cwast.DefFun):
        enclosing_fun = node
    if (cwast.NF.TYPE_ANNOTATED in node.__class__.FLAGS or
            isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED)):
        if cwast.NF.TYPE_ANNOTATED in node.__class__.FLAGS:
            assert node.x_type is not None, f"untyped node: {node}"
        _TypeVerifyNode(node, corpus, enclosing_fun)

    if cwast.NF.FIELD_ANNOTATED in node.__class__.FLAGS:
        assert node.x_field is not None, f"node withou field annotation: {node}"
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            _TypeVerifyNodeRecursively(getattr(node, c), corpus, enclosing_fun)
        elif nfd.kind is cwast.NFK.LIST:
            for cc in getattr(node, c):
                _TypeVerifyNodeRecursively(cc, corpus, enclosing_fun)


def VerifyASTTypes(mod_topo_order: List[cwast.DefMod],
                   mod_map: Dict[str, cwast.DefMod], type_corpus):
    for m in mod_topo_order:

        _TypeVerifyNodeRecursively(mod_map[m], type_corpus, None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = cwast.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symtab.ModulesInTopologicalOrder(asts)
    symtab.DecorateASTWithSymbols(mod_topo_order, mod_map)
    type_corpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    DecorateASTWithTypes(mod_topo_order, mod_map, type_corpus)
    VerifyASTTypes(mod_topo_order, mod_map, type_corpus)

    for t in type_corpus.corpus:
        print(t)
