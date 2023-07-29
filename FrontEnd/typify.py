#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import sys
import logging

from typing import List, Dict, Tuple, Any


from FrontEnd import cwast
from FrontEnd import symbolize
from FrontEnd import type_corpus
from FrontEnd import parse
from FrontEnd import pp


logger = logging.getLogger(__name__)


def is_ref_def(node) -> bool:
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        return isinstance(s, cwast.DefGlobal) or isinstance(s, cwast.DefVar) and s.ref
    return False


def address_can_be_taken(node) -> bool:
    return (is_ref_def(node) or
            isinstance(node, cwast.ExprDeref) or
            isinstance(node, cwast.ExprIndex) and isinstance(node.container.x_type, cwast.TypeSlice) or
            isinstance(node, cwast.ExprIndex) and address_can_be_taken(node.container))


def ComputeStringSize(raw: bool, string: str) -> int:
    if string.startswith('"""') and string.endswith('"""'):
        string = string[3:-3]
    elif string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    else:
        assert False
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
    if num[0] == "'":
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return 10
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1])

    num = num.replace("_", "")
    if num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64"):
        return int(num[: -3], 0)
    elif num[-2:] in ("u8", "s8"):
        return int(num[: -2], 0)
    elif num[-4:] in ("uint", "sint"):
        return int(num[: -4], 0)
    elif num[-3:] in ("r32", "r64"):
        return float(num[: -3])
    elif kind in cwast.BASE_TYPE_KIND_INT:
        return int(num, 0)
    elif kind in cwast.BASE_TYPE_KIND_REAL:
        if "p" in num:
            return float.fromhex(num)
        return float(num)
    else:
        assert kind is cwast.BASE_TYPE_KIND.INVALID
        if "." in num:
            return float(num)
        else:
            return int(num, 0)


def ParseArrayIndex(pos: str) -> int:
    return int(pos)


class _PolyMap:
    """Polymorphism map"""

    def __init__(self, tc: type_corpus.TypeCorpus):
        self._map: Dict[Tuple[str, str], cwast.DefFun] = {}
        self._type_corpus = tc

    def Register(self, fun: cwast.DefFun):
        ct: cwast.CanonType = fun.x_type
        first_param_type = ct.children[0].name
        logger.info("Register polymorphic fun %s: %s",
                    fun.name, first_param_type)
        self._map[(fun.name, first_param_type)] = fun

    def Resolve(self, fun_name: str, first_param_type: cwast.CanonType) -> cwast.DefFun:
        type_name = first_param_type.name
        logger.info("Resolving polymorphic fun %s: %s",
                    fun_name, type_name)
        out = self._map.get((fun_name, type_name))
        if out:
            return out
        # TODO: why do we need this - seems unsafe:
        if first_param_type.is_array():
            slice_type = self._type_corpus. insert_slice_type(
                False, first_param_type.underlying_array_type())
            type_name = slice_type.name

            out = self._map.get((fun_name, type_name))
            if out:
                return out
        cwast.CompilerError(
            0, f"cannot resolve polymorphic {fun_name} {type_name}")


class _TypeContext:
    def __init__(self, mod_name, poly_map: _PolyMap):
        self.mod_name: str = mod_name
        self._poly_map: _PolyMap = poly_map


def is_compatible_for_as(src: cwast.CanonType, dst: cwast.CanonType) -> bool:
    # TODO: deal with distinct types

    if src.is_int():
        return dst.is_int() or dst.is_real()
    return False


def _ComputeArrayLength(node) -> int:
    if isinstance(node, cwast.ValNum):
        return ParseNum(node.number, cwast.BASE_TYPE_KIND.INVALID)
    elif isinstance(node, cwast.Id):
        node = node.x_symbol
        return _ComputeArrayLength(node)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)) and not node.mut:
        return _ComputeArrayLength(node.initial_or_undef_or_auto)
    elif isinstance(node, cwast.Expr2):
        if node.binary_expr_kind is cwast.BINARY_EXPR_KIND.ADD:
            return _ComputeArrayLength(node.expr1) + _ComputeArrayLength(node.expr2)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.MUL:
            return _ComputeArrayLength(node.expr1) * _ComputeArrayLength(node.expr2)
        else:
            assert False
    else:
        assert False, f"unexpected dim node: {node}"


def UpdateNodeType(node, ct: cwast.CanonType):
    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"node not meant for type annotation: {node}"
    assert ct, f"No valid type for {node}"
    node.x_type = ct
    return ct


def AnnotateNodeType(node, ct: cwast.CanonType):
    logger.info("TYPE of %s: %s", node, ct.name)
    assert node.x_type is None, f"duplicate annotation for {node}"
    return UpdateNodeType(node, ct)


def AnnotateNodeField(node, field_node: cwast.RecField):
    assert isinstance(
        node, (cwast.ExprField, cwast.FieldVal, cwast.ExprOffsetof))
    assert node.x_field is None
    node.x_field = field_node


def _TypifyNodeRecursively(node, tc: type_corpus.TypeCorpus, target_type: cwast.CanonType, ctx: _TypeContext) -> cwast.CanonType:
    """Do not call this outside of functions"""
    extra = "" if target_type == type_corpus.NO_TYPE else f"[{target_type.name}]"
    logger.debug("TYPIFYING%s %s", extra, node)
    cstr = None
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        cstr = node.x_type
    if cstr is not None:
        # has been typified already
        return cstr

    if isinstance(node, cwast.TypeAuto):
        assert target_type is not type_corpus.NO_TYPE
        return AnnotateNodeType(node, target_type)
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
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.TypeBase):
        return AnnotateNodeType(node, tc.insert_base_type(node.base_type_kind))
    elif isinstance(node, cwast.TypePtr):
        t = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, t))
    elif isinstance(node, cwast.TypeSlice):
        t = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_slice_type(node.mut, t))
    elif isinstance(node, cwast.FunParam):
        _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
        params = []
        for p in node.params:
            _TypifyNodeRecursively(p, tc, type_corpus.NO_TYPE, ctx)
            params.append(p.type.x_type)
        result = _TypifyNodeRecursively(
            node.result, tc, type_corpus.NO_TYPE, ctx)
        cstr = tc.insert_fun_type(params, result)
        AnnotateNodeType(node, cstr)
        # recursing into the body is done explicitly
        return cstr
    elif isinstance(node, cwast.TypeArray):
        # note this is the only place where we need a comptime eval for types
        t = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.size, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        dim = _ComputeArrayLength(node.size)
        return AnnotateNodeType(node, tc.insert_array_type(dim, t))
    elif isinstance(node, cwast.RecField):
        ct = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.DefRec):
        # allow recursive definitions referring back to rec inside
        # the fields
        ct = tc.insert_rec_type(f"{ctx.mod_name}/{node.name}", node)
        AnnotateNodeType(node, ct)
        for f in node.fields:
            _TypifyNodeRecursively(f, tc, type_corpus.NO_TYPE, ctx)
        # we delay this until after fields have been typified this is necessary
        # because of recursive types
        tc.finalize_rec_type(ct)
        return ct
    elif isinstance(node, cwast.EnumVal):
        if isinstance(node.value_or_auto, cwast.ValAuto):
            AnnotateNodeType(node.value_or_auto, target_type)
        else:
            cstr = _TypifyNodeRecursively(
                node.value_or_auto, tc, target_type, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.DefEnum):
        cstr = tc.insert_enum_type(
            f"{ctx.mod_name}/{node.name}", node)
        # base_type = corpus.insert_base_type(node.base_type_kind)
        for f in node.items:
            _TypifyNodeRecursively(f, tc, cstr, ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.DefType):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        if node.wrapped:
            cstr = tc.insert_wrapped_type(cstr)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.TypeSum):
        # this is tricky code to ensure that children of TypeSum
        # are not TypeSum themselves on the canonical side
        pieces = [_TypifyNodeRecursively(
            f, tc, type_corpus.NO_TYPE, ctx) for f in node.types]
        return AnnotateNodeType(node, tc.insert_sum_type(pieces))
    if isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
        return AnnotateNodeType(node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL))
    elif isinstance(node, cwast.ValVoid):
        return AnnotateNodeType(node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.VOID))
    elif isinstance(node, cwast.ValUndef):
        assert False, "Must not try to typify UNDEF"
    elif isinstance(node, cwast.ValNum):
        ct = tc.get_type_for_num_literal(node.number, target_type)
        if ct != type_corpus.NO_TYPE:
            return AnnotateNodeType(node, ct)
        cwast.CompilerError(
            node.x_srcloc, f"cannot determine number type of: {node}")
    elif isinstance(node, cwast.ValAuto):
        assert target_type is not None
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.IndexVal):
        if not isinstance(node.value_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.value_or_undef,
                                   tc, target_type, ctx)
        index_target = tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
        if isinstance(node.init_index, cwast.ValAuto):
            AnnotateNodeType(node.init_index, index_target)
        else:
            _TypifyNodeRecursively(node.init_index, tc, index_target, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ValArray):
        ct = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        for x in node.inits_array:
            assert isinstance(x, cwast.IndexVal)
            _TypifyNodeRecursively(x, tc, ct, ctx)
        #
        _TypifyNodeRecursively(node.expr_size, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        dim = _ComputeArrayLength(node.expr_size)
        return AnnotateNodeType(node, tc.insert_array_type(dim, ct))
    elif isinstance(node, cwast.ValRec):
        ct = _TypifyNodeRecursively(node.type, tc, target_type, ctx)
        assert ct.is_rec()
        all_fields: List[cwast.RecField] = [f for f in ct.ast_node.fields]
        for val in node.inits_field:
            assert isinstance(val, cwast.FieldVal)
            if val.init_field:
                while True:
                    if not all_fields:
                        cwast.CompilerError(
                            node.x_srcloc, "too many fields for record literal")
                    field_node = all_fields.pop(0)
                    if val.init_field == field_node.name:
                        break
            else:
                field_node = all_fields.pop(0)
            # TODO: make sure this link is set
            field_ct = field_node.x_type
            AnnotateNodeField(val, field_node)
            AnnotateNodeType(val, field_ct)
            _TypifyNodeRecursively(val.value, tc, field_ct, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ValString):
        dim = ComputeStringSize(node.raw, node.string)
        cstr = tc.insert_array_type(
            dim, tc.insert_base_type(cwast.BASE_TYPE_KIND.U8))
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.ExprIndex):
        _TypifyNodeRecursively(node.expr_index, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        ct = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        return AnnotateNodeType(node, ct.contained_type())
    elif isinstance(node, cwast.ExprField):
        cstr = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        field_node = tc.lookup_rec_field(cstr, node.field)
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(node, field_node.x_type)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        initial = node.initial_or_undef_or_auto
        if isinstance(node.type_or_auto, cwast.TypeAuto):
            assert not isinstance(initial, cwast.ValUndef)
            cstr = _TypifyNodeRecursively(
                node.initial_or_undef_or_auto, tc, type_corpus.NO_TYPE, ctx)
            _TypifyNodeRecursively(node.type_or_auto, tc, cstr, ctx)
        else:
            cstr = _TypifyNodeRecursively(
                node.type_or_auto, tc, type_corpus.NO_TYPE, ctx)
            if not isinstance(initial, cwast.ValUndef):
                cstr = _TypifyNodeRecursively(initial, tc, cstr, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.ExprDeref):
        ct = _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        if not ct.is_pointer():
            cwast.CompilerError(
                node.x_srcloc, f"dereferenced expr must be pointer {node} but got {cstr}")
        # TODO: how is mutability propagated?
        return AnnotateNodeType(node, ct.underlying_pointer_type())
    elif isinstance(node, cwast.Expr1):
        cstr = _TypifyNodeRecursively(node.expr, tc, target_type, ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.Expr2):
        ct: cwast.CanonType = _TypifyNodeRecursively(
            node.expr1, tc, target_type, ctx)
        if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE and ct.is_number():
            ct2 = _TypifyNodeRecursively(node.expr2, tc, ct, ctx)
        else:
            ct2 = _TypifyNodeRecursively(
                node.expr2, tc, type_corpus.NO_TYPE, ctx)

        if node.binary_expr_kind in cwast.BINOP_BOOL:
            ct = tc.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
            if ct.is_pointer():
                assert ct2.is_pointer()
                ct = tc.insert_base_type(cwast.BASE_TYPE_KIND.SINT)
            elif ct.is_slice():
                assert ct2.is_slice()
            else:
                assert False
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprPointer):
        cstr = _TypifyNodeRecursively(node.expr1, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr2, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT), ctx)
        if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.expr_bound_or_undef, tc,  tc.insert_base_type(
                cwast.BASE_TYPE_KIND.UINT), ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.ExprFront):
        ct = _TypifyNodeRecursively(
            node.container, tc, type_corpus.NO_TYPE, ctx)
        if not ct.is_slice() and not ct.is_array():
            cwast.CompilerError(
                node.x_srcloc, "expected container in front expression")
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, ct.underlying_array_or_slice_type()))
    elif isinstance(node, cwast.Expr3):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        cstr = _TypifyNodeRecursively(node.expr_t, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr_f, tc, cstr, ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.StmtExpr):
        _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.ExprStmt):
        assert target_type != type_corpus.NO_TYPE
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ExprCall):
        if node.polymorphic:
            assert len(node.args) > 0
            assert isinstance(node.callee, cwast.Id)
            t = _TypifyNodeRecursively(
                node.args[0], tc, type_corpus.NO_TYPE, ctx)
            called_fun = ctx._poly_map.Resolve(node.callee.name, t)
            symbolize.AnnotateNodeSymbol(node.callee, called_fun)
            AnnotateNodeType(node.callee, called_fun.x_type)
            ct_callee: cwast.CanonType = called_fun.x_type
            assert ct_callee.is_fun(), f"{cstr}"
            params_ct = ct_callee.parameter_types()
            assert len(params_ct) == len(node.args)
            # we already process the first arg
            for p, a in zip(params_ct[1:], node.args[1:]):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct_callee.result_type())
        else:
            ct = _TypifyNodeRecursively(
                node.callee, tc, type_corpus.NO_TYPE, ctx)
            params_ct = ct.parameter_types()
            if len(params_ct) != len(node.args):
                cwast.CompilerError(node.x_srcloc,
                                    f"number of args does not match for call to {node.callee}")
            for p, a in zip(params_ct, node.args):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct.result_type())
    elif isinstance(node, cwast.StmtReturn):
        _TypifyNodeRecursively(node.expr_ret, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtIf):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        for c in node.body_f:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        for c in node.body_t:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.Case):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtCond):
        for c in node.cases:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtBlock):
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtBreak):
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtContinue):
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtTrap):
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = _TypifyNodeRecursively(
            node.lhs, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtCompoundAssignment):
        var_cstr = _TypifyNodeRecursively(
            node.lhs, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, (cwast.ExprAs, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, cwast.ExprAsNot):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        union = _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_sum_complement(union, cstr))
    elif isinstance(node, cwast.ExprIs):
        _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL))
    elif isinstance(node, cwast.ExprLen):
        _TypifyNodeRecursively(node.container, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = _TypifyNodeRecursively(
            node.expr_lhs, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, cstr_expr))
    elif isinstance(node, cwast.ExprOffsetof):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        field_node = tc.lookup_rec_field(cstr, node.field)
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(node, tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprSizeof):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT))
    elif isinstance(node, cwast.ExprTryAs):
        cstr = _TypifyNodeRecursively(node.type, tc, type_corpus.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, type_corpus.NO_TYPE, ctx)
        if not isinstance(node.default_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.default_or_undef, tc, cstr, ctx)
        return AnnotateNodeType(node, cstr)
    elif isinstance(node, (cwast.StmtStaticAssert)):
        _TypifyNodeRecursively(node.cond, tc, tc.insert_base_type(
            cwast.BASE_TYPE_KIND.BOOL), ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.Import):
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.StmtDefer):
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return type_corpus.NO_TYPE
    elif isinstance(node, cwast.ValSlice):
        len_type = tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT)
        _TypifyNodeRecursively(node.expr_size, tc, len_type, ctx)
        if isinstance(target_type, cwast.TypeSlice):
            ptr_type = tc.insert_ptr_type(target_type.mut, target_type.type)
            _TypifyNodeRecursively(node.pointer, tc, ptr_type, ctx)
            return AnnotateNodeType(node, target_type)
        else:
            ptr_type = _TypifyNodeRecursively(
                node.pointer, tc, type_corpus.NO_TYPE, ctx)
            return AnnotateNodeType(node, tc.insert_slice_type(ptr_type.mut, ptr_type.underlying_pointer_type()))
    else:
        assert False, f"unexpected node {node}"


UNTYPED_NODES_TO_BE_TYPECHECKED = (
    cwast.StmtReturn, cwast.StmtIf, cwast.DefVar, cwast.DefGlobal,
    cwast.StmtAssignment, cwast.StmtCompoundAssignment, cwast.StmtExpr)


def _CheckTypeUint(node, actual: cwast.CanonType):
    if not actual.is_uint():
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not uint: {actual.name}")


def _CheckTypeSame(node, actual, expected):
    if actual is not expected:
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not the same actual: {actual.name} expected: {expected.name}")


def _CheckTypeCompatible(node, actual: cwast.CanonType, expected: cwast.CanonType):
    if not type_corpus.is_compatible(actual, expected):
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: incompatible actual: {actual.name} expected: {expected.name}")


def _CheckTypeCompatibleForAssignment(node, actual: cwast.CanonType,
                                      expected: cwast.CanonType, mutable, srcloc=None):
    if not type_corpus.is_compatible(actual, expected, mutable):
        cwast.CompilerError(srcloc if srcloc else node.x_srcloc,
                            f"{node}: incompatible actual: {actual.name} expected: {expected.name}")


def _CheckExpr2Types(node, result_type: cwast.CanonType, op1_type: cwast.CanonType,
                     op2_type: cwast.CanonType, kind: cwast.BINARY_EXPR_KIND, tc):
    if kind in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
        assert result_type.is_bool()
        _CheckTypeSame(node, op1_type, op2_type)
    elif kind in cwast.BINOP_BOOL:
        assert op1_type.is_base_type() and result_type.is_bool()
        _CheckTypeSame(node, op1_type, op2_type)
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        if op1_type.is_pointer():
            if result_type != tc.insert_base_type(cwast.BASE_TYPE_KIND.SINT):
                cwast.CompilerError(
                    node.x_srcloc, "result of pointer delta must SINT")
            if not op2_type.is_pointer():
                cwast.CompilerError(
                    node.x_srcloc, "rhs of pointer delta must be pointer")
            _CheckTypeSame(node, op1_type.underlying_pointer_type(),
                           op2_type.underlying_pointer_type())

        elif op1_type.is_slice():
            assert op2_type.is_slice() and result_type == op1_type
            _CheckTypeSame(node, op1_type.underlying_slice_type(),
                           op2_type.underlying_slice_type())
        else:
            assert False
    else:
        assert op1_type.is_base_type()
        _CheckTypeSame(node, op1_type, result_type)
        _CheckTypeSame(node, op2_type, result_type)


def _TypeVerifyNode(node: cwast.ALL_NODES, tc: type_corpus.TypeCorpus):
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        ct: cwast.CanonType = node.x_type
        assert ct is not type_corpus.NO_TYPE
        assert ct.name in tc.corpus, f"bad type annotation for {node}: {node.x_type}"
        if isinstance(node, (cwast.DefRec, cwast.DefEnum)):
            assert ct.ast_node == node
    else:
        assert isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED)

    if isinstance(node, cwast.ValArray):
        cstr = node.type.x_type
        for x in node.inits_array:
            assert isinstance(x, cwast.IndexVal), f"{x}"
            if not isinstance(x.init_index, cwast.ValAuto):
                assert x.init_index.x_type.is_int()
            _CheckTypeSame(node,  x.x_type, cstr)
    elif isinstance(node, cwast.ValRec):
        for x in node.inits_field:
            assert isinstance(x, cwast.FieldVal), f"unexpected field: {x}"
            field_node = x.x_field
            _CheckTypeSame(node, field_node.x_type, x.x_type)
            _CheckTypeCompatible(node, x.value.x_type, x.x_type)
    elif isinstance(node, cwast.RecField):
        pass
    elif isinstance(node, cwast.ExprIndex):
        assert node.x_type == node.container.x_type.underlying_array_or_slice_type()
    elif isinstance(node, cwast.ExprField):
        cstr = node.x_type
        field_node = node.x_field
        assert cstr == field_node.x_type, f"field node {node.container.x_type} type mismatch: {cstr} {field_node.x_type}"
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        initial = node.initial_or_undef_or_auto
        if not isinstance(initial, cwast.ValUndef):
            cstr = node.type_or_auto.x_type
            initial_cstr = initial.x_type
            _CheckTypeCompatibleForAssignment(
                node, initial_cstr, cstr, type_corpus.is_mutable_def(
                    initial),
                initial.x_srcloc)
    elif isinstance(node, cwast.ExprDeref):
        node_type = node.x_type
        expr_type: cwast.CanonType = node.expr.x_type
        assert expr_type.is_pointer()
        _CheckTypeSame(node, node_type,
                       expr_type.underlying_pointer_type())
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
            _CheckTypeUint(node, node.expr_bound_or_undef.x_type)
        assert node.expr1.x_type.is_pointer() or node.expr1.x_type.is_slice()
        # _CheckTypeUint(node, tc, node.expr2.x_type)
        _CheckTypeSame(node, node.expr1.x_type, node.x_type)
    elif isinstance(node, cwast.ExprFront):
        assert node.container.x_type.is_array_or_slice(
        ), f"unpected front expr {node.container.x_type}"
        if node.mut:
            assert type_corpus.is_mutable_container(
                node.container), f"container not mutable: {node} {node.container}"

        if isinstance(node.container.x_type, cwast.TypeArray):
            # TODO: check if address can be taken
            pass

        assert node.x_type.is_pointer()
        _CheckTypeSame(node, node.x_type.underlying_pointer_type(),
                       node.container.x_type.underlying_array_or_slice_type())
    elif isinstance(node, cwast.Expr3):
        cstr = node.x_type
        cstr_t = node.expr_t.x_type
        cstr_f = node.expr_f.x_type
        cstr_cond = node.cond.x_type
        _CheckTypeSame(node, cstr_t, cstr)
        _CheckTypeSame(node, cstr_f, cstr)
        assert cstr_cond.is_bool()
    elif isinstance(node, cwast.ExprCall):
        result = node.x_type
        fun_sig: cwast.CanonType = node.callee.x_type
        assert fun_sig.is_fun(), f"{fun_sig}"
        assert fun_sig.result_type() == result, f"{fun_sig.result} {result}"
        for p, a in zip(fun_sig.parameter_types(), node.args):
            arg_cstr = a.x_type
            _CheckTypeCompatibleForAssignment(
                p,  arg_cstr, p, type_corpus.is_mutable_def(a), a.x_srcloc)
    elif isinstance(node, cwast.StmtReturn):
        target = node.x_target
        actual = node.expr_ret.x_type
        if isinstance(target, cwast.DefFun):
            expected = target.result.x_type
            _CheckTypeCompatible(node, actual, expected)
        else:
            assert isinstance(target, cwast.ExprStmt)
            expected = target.x_type
            _CheckTypeCompatible(node,  actual, expected)
    elif isinstance(node, cwast.StmtIf):
        assert node.cond.x_type.is_bool()
    elif isinstance(node, cwast.Case):
        assert node.cond.x_type.is_bool()
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr_rhs.x_type
        _CheckTypeCompatibleForAssignment(
            node, expr_cstr, var_cstr, type_corpus.is_mutable_def(
                node.expr_rhs),
            node.expr_rhs.x_srcloc)
        if not type_corpus.is_proper_lhs(node.lhs):
            cwast.CompilerError(
                node.x_srcloc, f"cannot assign to readonly data: {node}")
    elif isinstance(node, cwast.StmtCompoundAssignment):
        if not type_corpus.is_proper_lhs(node.lhs):
            cwast.CompilerError(
                node.x_srcloc, f"cannot assign to readonly data: {node}")
        kind = cwast.COMPOUND_KIND_TO_EXPR_KIND[node.assignment_kind]
        var_cstr = node.lhs.x_type
        expr_cstr = node.expr_rhs.x_type
        _CheckExpr2Types(node, var_cstr, var_cstr, expr_cstr, kind, tc)
    elif isinstance(node, cwast.StmtExpr):
        pass
    elif isinstance(node, cwast.ExprAsNot):
        pass
    elif isinstance(node, cwast.ExprAs):
        pass
        # src = node.expr.x_type
        # dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
    elif isinstance(node, cwast.ExprUnsafeCast):
        # src = node.expr.x_type
        # dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
        pass
    elif isinstance(node, cwast.ExprBitCast):
        # src = node.expr.x_type
        # dst = node.type.x_type
        # TODO
        # assert is_compatible_for_as(src, dst)
        pass
    elif isinstance(node, cwast.ExprIs):
        assert node.x_type.is_bool()
    elif isinstance(node, cwast.ExprLen):
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.Id):
        def_node = node.x_symbol
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            _CheckTypeSame(node, node.x_type, def_node.type_or_auto.x_type)
        elif isinstance(def_node, (cwast.FunParam)):
            _CheckTypeSame(node,  node.x_type, def_node.type.x_type)
        # else:
        #    _CheckTypeSame(node, tc, node.x_type, def_node.x_type)
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = node.expr_lhs.x_type
        cstr: cwast.CanonType = node.x_type
        if node.mut:
            if not address_can_be_taken(node.expr_lhs):
                cwast.CompilerError(node.x_srcloc,
                                    f"address cannot be take: {node} {node.expr_lhs.x_type.name}")
        assert cstr.is_pointer() and cstr.underlying_pointer_type() == cstr_expr
    elif isinstance(node, cwast.ExprOffsetof):
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprSizeof):
        assert node.x_type == tc.insert_base_type(
            cwast.BASE_TYPE_KIND.UINT)
    elif isinstance(node, cwast.ExprTryAs):
        cstr = node.x_type
        _CheckTypeSame(node, cstr, node.type.x_type)
        if not isinstance(node.default_or_undef, cwast.ValUndef):
            _CheckTypeSame(node, cstr, node.default_or_undef.x_type)
        assert type_corpus.is_compatible(cstr, node.expr.x_type)
    elif isinstance(node, cwast.ValNum):
        if not node.x_type.is_base_type() and not node.x_type.is_enum():
            cwast.CompilerError(
                node.x_srcloc, f"type mismatch {node} vs {node.x_type}")
    elif isinstance(node, cwast.TypeSum):
        assert node.x_type.is_sum()
    elif isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValVoid)):
        assert node.x_type.is_base_type()
    elif isinstance(node, (cwast.DefFun, cwast.TypeFun)):
        fun_type: cwast.CanonType = node.x_type
        assert fun_type.is_fun()
        _CheckTypeSame(node.result, fun_type.result_type(),
                       node.result.x_type)
        for a, b in zip(fun_type.parameter_types(), node.params):
            _CheckTypeSame(b, a, b.type.x_type)
        # We should also ensure three is a proper return but that requires dataflow

    elif isinstance(node, cwast.ValSlice):
        assert node.x_type.is_mutable() == node.pointer.x_type.is_mutable()
        _CheckTypeSame(node, node.x_type.underlying_slice_type(),
                       node.pointer.x_type.underlying_pointer_type())
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
            logger.info("TYPE-VERIFYING %s", node)

        if (cwast.NF.TYPE_ANNOTATED in node.FLAGS or
                isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED)):
            if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
                assert node.x_type is not None, f"untyped node: {node.x_srcloc}  {node}"
            _TypeVerifyNode(node, corpus)

        if cwast.NF.FIELD_ANNOTATED in node.FLAGS:
            field = node.x_field
            assert field is not None, f"node without field annotation: {node.x_srcloc} {node}"
            assert isinstance(field, cwast.RecField)

    cwast.VisitAstRecursivelyPost(node, visitor)


def DecorateASTWithTypes(mod_topo_order: List[cwast.DefMod],
                         tc: type_corpus.TypeCorpus):
    """This checks types and maps them to a canonical node

    Since array type include a fixed bound this also also includes
    the evaluation of constant expressions.

    The following node fields will be initialized:
    * x_type
    * x_field
    * some x_value (only array dimention as they are related to types)
    * some x_symbol for polymorphic invocations
    """
    poly_map = _PolyMap(tc)
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.name, poly_map)
        for node in mod.body_mod:
            # Note: _TypifyNodeRecursivel() does NOT recurse into function bodies
            ct = _TypifyNodeRecursively(node, tc, type_corpus.NO_TYPE, ctx)
            if isinstance(node, cwast.DefFun) and node.polymorphic:
                assert ct.node is cwast.TypeFun, f"{node} -> {ct.name}"
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

############################################################
#
############################################################


def main(inp):
    asts = parse.ReadModsFromStream(inp)
    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
    tc = type_corpus.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    DecorateASTWithTypes(mod_topo_order, tc)

    for t, n in tc.corpus.items():
        print(t, n.register_types, n.size, n.alignment)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    main(sys.stdin)
