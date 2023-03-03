#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import sys
import logging

from typing import List, Dict, Set, Optional, Union, Any


from FrontEnd import cwast
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import parse
from FrontEnd import pp


logger = logging.getLogger(__name__)


def is_proper_lhs(node):
    # TODO: this needs to be rethought and cleaned up
    # x =  (x must be mutable definition)
    # ^x = (x must have type mutable pointer)
    #
    return (types.is_mutable_def(node) or
            isinstance(node, cwast.ExprDeref) and types.is_mutable(node.expr.x_type) or
            # isinstance(node, cwast.ExprDeref) and types.is_mutable_def(node.expr) or
            isinstance(node, cwast.ExprField) and is_proper_lhs(node.container) or
            isinstance(node, cwast.ExprIndex) and types.is_mutable_def(node.container) or
            isinstance(node, cwast.ExprIndex) and types.is_mutable(node.container.x_type))


def address_can_be_taken(node):
    return (types.is_ref_def(node) or
            isinstance(node, cwast.ExprDeref) or
            isinstance(node, cwast.ExprIndex) and isinstance(node.container.x_type, cwast.TypeSlice) or
            isinstance(node, cwast.ExprIndex) and address_can_be_taken(node.container))


def is_mutable_container(node):
    if isinstance(node.x_type, cwast.TypeSlice):
        return node.x_type.mut
    elif isinstance(node.x_type, cwast.TypeArray):
        return is_proper_lhs(node)
    else:
        assert False


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
    return n


def ParseNum(num: str, kind: cwast.BASE_TYPE_KIND) -> Any:
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
    #
    if num[0] == "'":
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return 10
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1])
    else:
        return int(num, 0)


def ParseArrayIndex(pos: str) -> int:
    return int(pos)


class _PolyMap:
    """Polymorphism map"""

    def __init__(self, type_corpus: types.TypeCorpus):
        self._map = {}
        self._type_corpus = type_corpus

    def Register(self, fun: cwast.DefFun):
        cstr = fun.x_type
        first_param_type = self._type_corpus.canon_name(
            cstr.params[0].type)
        logger.info("Register polymorphic fun %s: %s",
                    fun.name, first_param_type)
        self._map[(fun.name, first_param_type)] = fun

    def Resolve(self, fun_name: str, first_param_type) -> cwast.DefFun:
        type_name = self._type_corpus.canon_name(first_param_type)
        logger.info("Resolving polymorphic fun %s: %s",
                    fun_name, type_name)
        out = self._map.get((fun_name, type_name))
        if out:
            return out
        # TODO: why do we need this - seem unsafe:
        if isinstance(first_param_type, cwast.TypeArray):
            slice_type = self._type_corpus. insert_slice_type(
                False, first_param_type.type)
        type_name = self._type_corpus.canon_name(slice_type)
        out = self._map.get((fun_name, type_name))
        if out:
            return out
        assert False, f"cannot resolve polymorphic {fun_name}"


class _TypeContext:
    def __init__(self, mod_name, poly_map: _PolyMap):
        self.mod_name: str = mod_name
        self._poly_map: _PolyMap = poly_map


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
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)) and not node.mut:
        return _ComputeArrayLength(node.initial_or_undef)
    elif isinstance(node, cwast.Expr2):
        if node.binary_expr_kind is cwast.BINARY_EXPR_KIND.ADD:
            return _ComputeArrayLength(node.expr1) + _ComputeArrayLength(node.expr2)
        else:
            assert False
    else:
        assert False, f"unexpected dim node: {node}"


def UpdateNodeType(corpus, node, cstr: types.CanonType):
    assert cwast.NF.TYPE_CORPUS in cstr.FLAGS, f"bad type corpus node {repr(cstr)}"
    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"node not meant for type annotation: {node}"
    assert cstr, f"No valid type for {node}"
    node.x_type = cstr
    return cstr


def AnnotateNodeType(corpus, node, cstr: types.CanonType):
    logger.info(f"TYPE of {node}: {corpus.canon_name(cstr)}")
    assert node.x_type is None, f"duplicate annotation for {node}"
    return UpdateNodeType(corpus, node, cstr)


def AnnotateNodeField(node, field_node: cwast.RecField):
    assert isinstance(
        node, (cwast.ExprField, cwast.FieldVal, cwast.ExprOffsetof))
    assert node.x_field is None
    node.x_field = field_node


def _TypifyNodeRecursively(node, tc: types.TypeCorpus, target_type, ctx: _TypeContext) -> types.CanonType:
    """Do not call this outside of functions"""
    extra = "" if target_type == types.NO_TYPE else f"[{target_type}]"
    logger.debug(f"TYPIFYING{extra} {node}")
    cstr = None
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        cstr = node.x_type
    if cstr is not None:
        # has been typified already
        return cstr

    if isinstance(node, cwast.TypeAuto):
        assert target_type is not types.NO_TYPE
        return AnnotateNodeType(tc, node, target_type)
    elif isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS or cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS
        # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
        _TypifyNodeRecursively(def_node, tc, target_type, ctx)
        if isinstance(def_node, (cwast.DefType, cwast.DefFun, cwast.DefRec, cwast.EnumVal, cwast.DefEnum)):
            cstr = def_node.x_type
        elif isinstance(def_node, cwast.FunParam):
            cstr = def_node.type.x_type
        else:
            assert isinstance(
                def_node, (cwast.DefVar, cwast.DefGlobal, cwast.FunParam)), f"{def_node}"
            cstr = def_node.type_or_auto.x_type
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.TypeBase):
        return AnnotateNodeType(tc, node, tc.insert_base_type(node.base_type_kind))
    elif isinstance(node, cwast.TypePtr):
        t = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_ptr_type(node.mut, t))
    elif isinstance(node, cwast.TypeSlice):
        t = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_slice_type(node.mut, t))
    elif isinstance(node, cwast.FunParam):
        _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        return types.NO_TYPE
    elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
        params = []
        for p in node.params:
            _TypifyNodeRecursively(p, tc, types.NO_TYPE, ctx)
            params.append(p.type.x_type)
        result = _TypifyNodeRecursively(
            node.result, tc, types.NO_TYPE, ctx)
        cstr = tc.insert_fun_type(params, result)
        AnnotateNodeType(tc, node, cstr)
        # recursing into the body is done explicitly
        return cstr
    elif isinstance(node, cwast.TypeArray):
        # note this is the only place where we need a comptime eval for types
        t = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.size, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        dim = _ComputeArrayLength(node.size)
        return AnnotateNodeType(tc, node, tc.insert_array_type(dim, t))
    elif isinstance(node, cwast.RecField):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        if not isinstance(node.initial_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.initial_or_undef, tc, cstr, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.DefRec):
        # allow recursive definitions referring back to rec inside
        # the fields
        cstr = tc.insert_rec_type(f"{ctx.mod_name}/{node.name}", node)
        AnnotateNodeType(tc, node, cstr)
        for f in node.fields:
            _TypifyNodeRecursively(f, tc, types.NO_TYPE, ctx)
        # we delay this until after fields have been typified this is necessary
        # because of recursive types
        tc.finalize_rec_type(node)
        return cstr
    elif isinstance(node, cwast.EnumVal):
        if isinstance(node.value_or_auto, cwast.ValAuto):
            AnnotateNodeType(tc, node.value_or_auto, target_type)
        else:
            cstr = _TypifyNodeRecursively(
                node.value_or_auto, tc, target_type, ctx)
        return AnnotateNodeType(tc, node, target_type)
    elif isinstance(node, cwast.DefEnum):
        cstr = tc.insert_enum_type(
            f"{ctx.mod_name}/{node.name}", node)
        # base_type = corpus.insert_base_type(node.base_type_kind)
        for f in node.items:
            _TypifyNodeRecursively(f, tc, cstr, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.DefType):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        if node.wrapped:
            cstr = tc.insert_wrapped_type(cstr)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.TypeSum):
        # this is tricky code to ensure that children of TypeSum
        # are not TypeSum themselves on the canonical side
        pieces = [_TypifyNodeRecursively(
            f, tc, types.NO_TYPE, ctx) for f in node.types]
        return AnnotateNodeType(tc, node, tc.insert_sum_type(pieces))
    if isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
        return AnnotateNodeType(tc, node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL))
    elif isinstance(node, cwast.ValVoid):
        return AnnotateNodeType(tc, node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.VOID))
    elif isinstance(node, cwast.ValUndef):
        assert False, "Must not try to typify UNDEF"
    elif isinstance(node, cwast.ValNum):
        cstr = tc.num_type(node.number, target_type)
        if cstr != types.NO_TYPE:
            return AnnotateNodeType(tc, node, cstr)
        cwast.CompilerError(
            node.x_srcloc, f"cannot determine number type of: {node}")
    elif isinstance(node, cwast.ValAuto):
        assert False, "Must not try to typify ValAuto"
    elif isinstance(node, cwast.IndexVal):
        if not isinstance(node.value_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.value_or_undef,
                                   tc, target_type, ctx)
        index_target = tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
        if isinstance(node.init_index, cwast.ValAuto):
            AnnotateNodeType(tc, node.init_index, index_target)
        else:
            _TypifyNodeRecursively(node.init_index, tc, index_target, ctx)
        return AnnotateNodeType(tc, node, target_type)
    elif isinstance(node, cwast.ValArray):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        for x in node.inits_array:
            assert isinstance(x, cwast.IndexVal)
            _TypifyNodeRecursively(x, tc, cstr, ctx)
        #
        _TypifyNodeRecursively(node.expr_size, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        dim = _ComputeArrayLength(node.expr_size)
        return AnnotateNodeType(tc, node, tc.insert_array_type(dim, cstr))
    elif isinstance(node, cwast.ValRec):
        cstr = _TypifyNodeRecursively(node.type, tc, target_type, ctx)
        assert isinstance(cstr, cwast.DefRec)
        all_fields: List[cwast.RecField] = [
            f for f in cstr.fields if isinstance(f, cwast.RecField)]
        for val in node.inits_rec:
            assert isinstance(val, cwast.FieldVal)
            if val.init_field:
                while True:
                    field_node = all_fields.pop(0)
                    if val.init_field == field_node.name:
                        break
            else:
                field_node = all_fields.pop(0)
            # TODO: make sure this link is set
            field_cstr = field_node.x_type
            AnnotateNodeField(val, field_node)
            AnnotateNodeType(tc, val, field_cstr)
            _TypifyNodeRecursively(val.value, tc, field_cstr, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.ValString):
        dim = ComputeStringSize(node.raw, node.string)
        cstr = tc.insert_array_type(
            dim, tc.insert_base_type(cwast.BASE_TYPE_KIND.U8))
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.ExprIndex):
        _TypifyNodeRecursively(node.expr_index, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        cstr = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        return AnnotateNodeType(tc, node, types.get_contained_type(cstr))
    elif isinstance(node, cwast.ExprField):
        cstr = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        field_node = tc.lookup_rec_field(cstr, node.field)
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(tc, node, field_node.x_type)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        if isinstance(node.type_or_auto, cwast.TypeAuto):
            assert not isinstance(node.initial_or_undef, cwast.ValUndef)
            cstr = _TypifyNodeRecursively(
                node.initial_or_undef, tc, types.NO_TYPE, ctx)
            _TypifyNodeRecursively(node.type_or_auto, tc, cstr, ctx)
        else:
            cstr = _TypifyNodeRecursively(
                node.type_or_auto, tc, types.NO_TYPE, ctx)
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                cstr = _TypifyNodeRecursively(
                    node.initial_or_undef, tc, cstr, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.ExprDeref):
        cstr = _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        assert isinstance(cstr, cwast.TypePtr)
        # TODO: how is mutability propagated?
        return AnnotateNodeType(tc, node, cstr.type)
    elif isinstance(node, cwast.Expr1):
        cstr = _TypifyNodeRecursively(node.expr, tc, target_type, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.Expr2):
        cstr = _TypifyNodeRecursively(node.expr1, tc, target_type, ctx)
        if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE and types.is_number(cstr):
            cstr2 = _TypifyNodeRecursively(node.expr2, tc, cstr, ctx)
        else:
            cstr2 = _TypifyNodeRecursively(
                node.expr2, tc, types.NO_TYPE, ctx)

        if node.binary_expr_kind in cwast.BINOP_BOOL:
            cstr = tc.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
            if isinstance(cstr, cwast.TypePtr):
                assert isinstance(cstr2, cwast.TypePtr)
                cstr = tc.insert_base_type(cwast.BASE_TYPE_KIND.SINT)
            elif isinstance(cstr, cwast.TypeSlice):
                assert isinstance(cstr2, cwast.TypeSlice)
            else:
                assert False
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.ExprPointer):
        cstr = _TypifyNodeRecursively(node.expr1, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr2, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.expr_bound_or_undef, tc,  tc.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT), ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.ExprFront):
        cstr = _TypifyNodeRecursively(node.container, tc, types.NO_TYPE, ctx)
        if not isinstance(cstr, (cwast.TypeSlice, cwast.TypeArray)):
            cwast.CompilerError(
                node.x_srcloc, "expected container in front expression")
        return AnnotateNodeType(tc, node, tc.insert_ptr_type(node.mut, cstr.type))
    elif isinstance(node, cwast.Expr3):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        cstr = _TypifyNodeRecursively(node.expr_t, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr_f, tc, cstr, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.StmtExpr):
        _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.ExprStmt):
        assert target_type != types.NO_TYPE
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return AnnotateNodeType(tc, node, target_type)
    elif isinstance(node, cwast.ExprCall):
        if node.polymorphic:
            assert len(node.args) > 0
            assert isinstance(node.callee, cwast.Id)
            t = _TypifyNodeRecursively(
                node.args[0], tc, types.NO_TYPE, ctx)
            called_fun = ctx._poly_map.Resolve(node.callee.name, t)
            symbolize.AnnotateNodeSymbol(node.callee, called_fun)
            AnnotateNodeType(tc, node.callee, called_fun.x_type)
            cstr = called_fun.x_type
            assert isinstance(cstr, cwast.TypeFun), f"{cstr}"
            assert len(cstr.params) == len(node.args)
            # we already process the first arg
            for p, a in zip(cstr.params[1:], node.args[1:]):
                _TypifyNodeRecursively(a, tc, p.type, ctx)
            return AnnotateNodeType(tc, node, cstr.result)
        else:
            cstr = _TypifyNodeRecursively(
                node.callee, tc, types.NO_TYPE, ctx)
            assert isinstance(cstr, cwast.TypeFun)
            if len(cstr.params) != len(node.args):
                cwast.CompilerError(node.x_srcloc,
                                    f"number of args does not match for call to {node.callee}")
            for p, a in zip(cstr.params, node.args):
                _TypifyNodeRecursively(a, tc, p.type, ctx)
            return AnnotateNodeType(tc, node, cstr.result)
    elif isinstance(node, cwast.StmtReturn):
        _TypifyNodeRecursively(node.expr_ret, tc, target_type, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtIf):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        for c in node.body_f:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        for c in node.body_t:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.Case):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtCond):
        for c in node.cases:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtBlock):
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtBreak):
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtContinue):
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtTrap):
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = _TypifyNodeRecursively(node.lhs, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.StmtCompoundAssignment):
        var_cstr = _TypifyNodeRecursively(node.lhs, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return types.NO_TYPE
    elif isinstance(node, (cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, cwast.ExprAsNot):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        union = _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_sum_complement(union, cstr))
    elif isinstance(node, cwast.ExprIs):
        _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL))
    elif isinstance(node, cwast.ExprLen):
        _TypifyNodeRecursively(node.container, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = _TypifyNodeRecursively(
            node.expr_lhs, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_ptr_type(node.mut, cstr_expr))
    elif isinstance(node, cwast.ExprOffsetof):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        field_node = tc.lookup_rec_field(cstr, node.field)
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(tc, node, tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprSizeof):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        return AnnotateNodeType(tc, node, tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprTryAs):
        cstr = _TypifyNodeRecursively(node.type, tc, types.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, types.NO_TYPE, ctx)
        if not isinstance(node.default_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.default_or_undef, tc, cstr, ctx)
        return AnnotateNodeType(tc, node, cstr)
    elif isinstance(node, (cwast.StmtStaticAssert)):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        return types.NO_TYPE
    elif isinstance(node, cwast.Import):
        return types.NO_TYPE
    elif isinstance(node, cwast.ValSlice):
        len_type = tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT)
        _TypifyNodeRecursively(node.expr_size, tc, len_type, ctx)
        if isinstance(target_type, cwast.TypeSlice):
            ptr_type = tc.insert_ptr_type(target_type.mut, target_type.type)
            _TypifyNodeRecursively(node.pointer, tc, ptr_type, ctx)
            return AnnotateNodeType(tc, node, target_type)
        else:
            ptr_type = _TypifyNodeRecursively(
                node.pointer, tc, types.NO_TYPE, ctx)
            return AnnotateNodeType(tc, node, tc.insert_slice_type(ptr_type.mut, ptr_type.type))
    else:
        assert False, f"unexpected node {node}"


UNTYPED_NODES_TO_BE_TYPECHECKED = (
    cwast.StmtReturn, cwast.StmtIf,
    cwast.StmtAssignment, cwast.StmtCompoundAssignment, cwast.StmtExpr)


def _CheckTypeUint(node, tc: types.TypeCorpus, actual):
    if not types.is_uint(actual):
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not uint: {tc.canon_name(actual)}")


def _CheckTypeSame(node, tc: types.TypeCorpus, actual, expected):
    if actual is not expected:
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not the same actual: {tc.canon_name(actual)} expected: {tc.canon_name(expected)}")


def _CheckTypeCompatible(node, tc: types.TypeCorpus, actual, expected):
    if not types.is_compatible(actual, expected):
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: incompatible actual: {tc.canon_name(actual)} expected: {tc.canon_name(expected)}")


def _CheckTypeCompatibleForAssignment(node, tc: types.TypeCorpus, actual, expected, mutable):
    if not types.is_compatible(actual, expected, mutable):
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: incompatible actual: {tc.canon_name(actual)} expected: {tc.canon_name(expected)}")


def _CheckExpr2Types(node, result_type, op1_type, op2_type, kind: cwast.BINARY_EXPR_KIND, tc) -> bool:
    if kind in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
        assert types.is_bool(result_type)
        _CheckTypeSame(node, tc, op1_type, op2_type)
    elif kind in cwast.BINOP_BOOL:
        assert isinstance(
            op1_type, cwast.TypeBase) and types.is_bool(result_type)
        _CheckTypeSame(node, tc, op1_type, op2_type)
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        _CheckTypeSame(node, tc, op1_type.type, op2_type.type)
        if isinstance(op1_type, cwast.TypePtr):
            assert (isinstance(op2_type, cwast.TypeSlice) and
                    result_type == tc.insert_base_type(cwast.BASE_TYPE_KIND.SINT))
        elif isinstance(op1_type, cwast.TypeSlice):
            assert (isinstance(op2_type, cwast.TypeSlice) and
                    result_type == op1_type)
        else:
            assert False
    else:
        assert isinstance(op1_type, cwast.TypeBase)
        _CheckTypeSame(node, tc, op1_type, result_type)
        _CheckTypeSame(node, tc, op2_type, result_type)


def _TypeVerifyNode(node: cwast.ALL_NODES, tc: types.TypeCorpus):
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        assert node.x_type is not types.NO_TYPE
        assert node.x_type in tc._canon_name, f"bad type annotation for {node}: {node.x_type}"
        if isinstance(node, (cwast.DefRec, cwast.DefEnum)):
            assert node.x_type ==  node
        else:
            assert node.x_type !=  node, f"bad node: {node}"
    else:
        assert isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED)

    if isinstance(node, cwast.ValArray):
        cstr = node.type.x_type
        for x in node.inits_array:
            assert isinstance(x, cwast.IndexVal), f"{x}"
            if not isinstance(x.init_index, cwast.ValAuto):
                assert types.is_int(x.init_index.x_type)
            _CheckTypeSame(node, tc, x.x_type, cstr)
    elif isinstance(node, cwast.ValRec):
        for x in node.inits_rec:
            assert isinstance(x, cwast.FieldVal)
            field_node = x.x_field
            _CheckTypeSame(node, tc, field_node.x_type, x.x_type)
            _CheckTypeCompatible(node, tc, x.value.x_type, x.x_type)
    elif isinstance(node, cwast.RecField):
        if not isinstance(node.initial_or_undef, cwast.ValUndef):
            type_cstr = node.type.x_type
            initial_cstr = node.initial_or_undef.x_type
            _CheckTypeCompatible(node, tc, initial_cstr, type_cstr)
    elif isinstance(node, cwast.ExprIndex):
        cstr = node.x_type
        assert cstr == types.get_contained_type(node.container.x_type)
    elif isinstance(node, cwast.ExprField):
        cstr = node.x_type
        field_node = node.x_field
        assert cstr == field_node.x_type
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        if not isinstance(node.initial_or_undef, cwast.ValUndef):
            cstr = node.type_or_auto.x_type

            initial_cstr = node.initial_or_undef.x_type
            _CheckTypeCompatibleForAssignment(
                node, tc, initial_cstr, cstr, types.is_mutable_def(node.initial_or_undef))
    elif isinstance(node, cwast.ExprDeref):
        node_type = node.x_type
        expr_type = node.expr.x_type
        assert isinstance(expr_type, cwast.TypePtr)
        _CheckTypeSame(node, tc, node_type, expr_type.type)
    elif isinstance(node, cwast.ExprStmt):
        pass
    elif isinstance(node, cwast.Expr1):
        cstr = node.x_type
        assert cstr == node.expr.x_type
    elif isinstance(node, cwast.Expr2):
        _CheckExpr2Types(node, node.x_type,  node.expr1.x_type,
                         node.expr2.x_type, node.binary_expr_kind, tc)
    elif isinstance(node, cwast.ExprPointer):
        if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
            _CheckTypeUint(node, tc, node.expr_bound_or_undef.x_type)
        assert isinstance(node.expr1.x_type, (cwast.TypePtr, cwast.TypeSlice))
        _CheckTypeUint(node, tc, node.expr2.x_type)
        _CheckTypeSame(node, tc, node.expr1.x_type, node.x_type)
    elif isinstance(node, cwast.ExprFront):
        assert isinstance(node.container.x_type,
                          (cwast.TypeSlice, cwast.TypeArray)), f"unpected front expr {node.container.x_type}"
        if node.mut:
            assert is_mutable_container(
                node.container), f"container not mutable: {node} {node.container}"
            pass

        if isinstance(node.container.x_type, cwast.TypeArray):
            # TODO: check if address can be taken
            pass

        assert isinstance(node.x_type, cwast.TypePtr)
        _CheckTypeSame(node, tc, node.x_type.type, node.container.x_type.type)
    elif isinstance(node, cwast.Expr3):
        cstr = node.x_type
        cstr_t = node.expr_t.x_type
        cstr_f = node.expr_f.x_type
        cstr_cond = node.cond.x_type
        _CheckTypeSame(node, tc, cstr_t, cstr)
        _CheckTypeSame(node, tc, cstr_f, cstr)
        assert types.is_bool(cstr_cond)
    elif isinstance(node, cwast.ExprCall):
        result = node.x_type
        fun_sig = node.callee.x_type
        assert isinstance(fun_sig, cwast.TypeFun), f"{fun_sig}"
        assert fun_sig.result == result, f"{fun_sig.result} {result}"
        for p, a in zip(fun_sig.params, node.args):
            arg_cstr = a.x_type
            _CheckTypeCompatibleForAssignment(
                p, tc, arg_cstr, p.type, types.is_mutable_def(a))
    elif isinstance(node, cwast.StmtReturn):
        target = node.x_target
        actual = node.expr_ret.x_type
        if isinstance(target, cwast.DefFun):
            expected = target.result.x_type
            _CheckTypeCompatible(node, tc, actual, expected)
        else:
            assert isinstance(target, cwast.ExprStmt)
            expected = target.x_type
            _CheckTypeCompatible(node, tc, actual, expected)
    elif isinstance(node, cwast.StmtIf):
        assert types.is_bool(node.cond.x_type)
    elif isinstance(node, cwast.Case):
        assert types.is_bool(node.cond.x_type)
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr_rhs.x_type
        _CheckTypeCompatibleForAssignment(
            node, tc, expr_cstr, var_cstr, types.is_mutable_def(node.expr_rhs))
        if not is_proper_lhs(node.lhs):
            cwast.CompilerError(
                node.x_srcloc, f"cannot assign to readonly data: {node}")
    elif isinstance(node, cwast.StmtCompoundAssignment):
        assert is_proper_lhs(node.lhs)
        kind = cwast.COMPOUND_KIND_TO_EXPR_KIND[node.assignment_kind]
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr_rhs.x_type
        _CheckExpr2Types(node, var_cstr, var_cstr, expr_cstr, kind, tc)
    elif isinstance(node, cwast.StmtExpr):
        pass
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
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.Id):
        def_node = node.x_symbol
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            _CheckTypeSame(node, tc, node.x_type, def_node.type_or_auto.x_type)
        elif isinstance(def_node, (cwast.FunParam)):
            _CheckTypeSame(node, tc, node.x_type, def_node.type.x_type)
        # else:
        #    _CheckTypeSame(node, tc, node.x_type, def_node.x_type)
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = node.expr_lhs.x_type
        cstr = node.x_type
        if node.mut:
            if not address_can_be_taken(node.expr_lhs):
                cwast.CompilerError(node.x_srcloc,
                                    f"address cannot be take: {node} {tc.canon_name(node.expr_lhs.x_type)}")
        assert isinstance(cstr, cwast.TypePtr) and cstr.type == cstr_expr
    elif isinstance(node, cwast.ExprOffsetof):
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprSizeof):
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprTryAs):
        cstr = node.x_type
        _CheckTypeSame(node, tc, cstr, node.type.x_type)
        if not isinstance(node.default_or_undef, cwast.ValUndef):
            _CheckTypeSame(node, tc, cstr, node.default_or_undef.x_type)
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
        fun_type = node.x_type
        assert fun_type.result == node.result.x_type
        for a, b in zip(fun_type.params, node.params):
            _CheckTypeSame(b, tc, a.type, b.type.x_type)
    elif isinstance(node, cwast.ValSlice):
        assert node.x_type.mut == node.pointer.x_type.mut
        _CheckTypeSame(node, tc, node.x_type.type, node.pointer.x_type.type)
    elif isinstance(node, (cwast.DefType, cwast.TypeBase, cwast.TypeSlice, cwast.IndexVal,
                           cwast.TypeArray, cwast.DefFun, cwast.TypeAuto,
                           cwast.TypePtr, cwast.FunParam, cwast.DefRec, cwast.DefEnum,
                           cwast.EnumVal, cwast.ValAuto, cwast.ValString, cwast.FieldVal)):
        pass
    else:
        assert False, f"unsupported  node type: {node.__class__} {node}"


def VerifyTypesRecursively(node, corpus):
    def visitor(node, _):
        if cwast.NF.TOP_LEVEL in node.FLAGS:
            logger.info(f"TYPE-VERIFYING {node}")

        if (cwast.NF.TYPE_ANNOTATED in node.FLAGS or
                isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED)):
            if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
                assert node.x_type is not None, f"untyped node: {node.x_srcloc}  {node}"
            _TypeVerifyNode(node, corpus)

        if cwast.NF.FIELD_ANNOTATED in node.FLAGS:
            field = node.x_field
            assert field is not None, f"node withou field annotation: {node.x_srcloc} {node}"
            assert isinstance(field, cwast.RecField)

    cwast.VisitAstRecursivelyPost(node, visitor)


def DecorateASTWithTypes(mod_topo_order: List[cwast.DefMod],
                         tc: types.TypeCorpus):
    """This checks types and maps them to a cananical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.

    The following node fields will be initialized:
    * x_type
    * x_field
    * some x_value (only array dimention as they are related to types)
    """
    poly_map = _PolyMap(tc)
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.name, poly_map)
        for node in mod.body_mod:
            # Note: _TypifyNodeRecursivel() does NOT recurse into function bodies
            cstr = _TypifyNodeRecursively(
                node, tc, types.NO_TYPE, ctx)
            if isinstance(node, cwast.DefFun) and node.polymorphic:
                assert isinstance(cstr, cwast.TypeFun)
                poly_map.Register(node)

    for mod in mod_topo_order:
        ctx = _TypeContext(mod.name, poly_map)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun) and not node.extern:
                for c in node.body:
                    _TypifyNodeRecursively(
                        c, tc, node.result.x_type, ctx)
    for mod in mod_topo_order:
        VerifyTypesRecursively(mod, tc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripNodes(mod, cwast.Comment)
        cwast.StripNodes(mod, cwast.DefMacro)
    tc = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    DecorateASTWithTypes(mod_topo_order, tc)

    for t, n in tc.corpus.items():
        print(t, tc._register_types[n], n.x_size, n.x_alignment)
