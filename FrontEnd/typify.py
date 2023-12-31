#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import logging

from typing import List, Dict, Tuple, Any


from FrontEnd import cwast
from FrontEnd import symbolize
from FrontEnd import type_corpus
from FrontEnd import pp


logger = logging.getLogger(__name__)


def is_ref_def(node) -> bool:
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        return isinstance(s, cwast.DefGlobal) or isinstance(s, cwast.DefVar) and s.ref
    return False


def address_can_be_taken(node) -> bool:
    return (is_ref_def(node) or
            isinstance(node, cwast.ExprField) or
            isinstance(node, cwast.ExprDeref) or
            isinstance(node, cwast.ExprIndex) and
            node.container.x_type.is_slice() or
            isinstance(node, cwast.ExprIndex) and
            address_can_be_taken(node.container))


def ComputeStringSize(strkind: str, string: str) -> int:
    n = len(string)
    if strkind == "raw":
        return n
    if strkind == "hex":
        n = 0
        last = None
        for c in string:
            if c in " \t\n":
                continue
            if last:
                last = None
            else:
                last = c
                n += 1
        assert last is None
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


def ParseNumRaw(num_val: cwast.ValNum, kind: cwast.BASE_TYPE_KIND) -> Tuple[Any,  cwast.BASE_TYPE_KIND]:
    num = num_val.number

    def get_kind(length):
        return cwast.BASE_TYPE_KIND[num[-length:].upper()]

    if num[0] == "'":
        if kind is cwast.BASE_TYPE_KIND.INVALID:
            cwast.CompilerError(
                num_val.x_srcloc, f"Number needs explicit type {num_val}")
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return 10, kind
            elif num[2] == "t":
                return 8, kind
            elif num[2] == "r":
                return 13, kind
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1]), kind

    num = num.replace("_", "")
    if num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64"):
        return int(num[: -3], 0), get_kind(3)
    elif num[-2:] in ("u8", "s8"):
        return int(num[: -2], 0), get_kind(2)
    elif num[-4:] in ("uint", "sint"):
        return int(num[: -4], 0), get_kind(4)
    elif num[-3:] in ("r32", "r64"):
        return float(num[: -3]), get_kind(3)
    elif kind in cwast.BASE_TYPE_KIND_INT:
        return int(num, 0), kind
    elif kind in cwast.BASE_TYPE_KIND_REAL:
        if "p" in num:
            return float.fromhex(num), kind
        return float(num), kind
    else:
        cwast.CompilerError(
            num_val.x_srcloc, f"cannot parse number: {num} {kind}")


def ParseNum(num: cwast.ValNum, kind: cwast.BASE_TYPE_KIND) -> Any:
    val, _ = ParseNumRaw(num, kind)
    bitsize = cwast.BASE_TYPE_KIND_TO_SIZE[kind] * 8
    if kind in cwast.BASE_TYPE_KIND_UINT:
        assert 0 <= val < (1 << bitsize), f"val {num} out of bounds for {kind}"
    elif kind in cwast.BASE_TYPE_KIND_SINT:
        t = 1 << (bitsize - 1)
        if val >= t:
            if num.number.startswith("0x"):
                val -= t * 2
        assert -t <= val < t

    return val


def ParseArrayIndex(pos: str) -> int:
    return int(pos)


class _PolyMap:
    """Polymorphism map"""

    def __init__(self, tc: type_corpus.TypeCorpus):
        self._map: Dict[Tuple[cwast.DefMod, str, str], cwast.DefFun] = {}
        self._type_corpus = tc

    def Register(self, fun: cwast.DefFun):
        ct: cwast.CanonType = fun.x_type
        mod = fun.x_module
        name = cwast.GetSymbolName(fun.name)
        first_param_type = ct.children[0].name
        logger.info("Register polymorphic fun %s::%s: %s",
                    mod.x_modname, name, first_param_type)
        # TODO: Should this work with parameterized volumes
        self._map[(mod, name, first_param_type)] = fun

    def Resolve(self, callee: cwast.Id, first_param_type: cwast.CanonType) -> cwast.DefFun:
        fun_name = cwast.GetSymbolName(callee.name)
        type_name = first_param_type.name
        logger.info("Resolving polymorphic fun %s: %s", fun_name, type_name)
        out = self._map.get((callee.x_module, fun_name, type_name))
        if out:
            return out
        # TODO: why do we need this - seems unsafe:
        if first_param_type.is_array():
            slice_type = self._type_corpus. insert_slice_type(
                False, first_param_type.underlying_array_type())
            type_name = slice_type.name

            out = self._map.get((callee.x_module, fun_name, type_name))
            if out:
                return out
        cwast.CompilerError(
            callee.x_srcloc, f"cannot resolve polymorphic {fun_name} {type_name}")


class _TypeContext:
    def __init__(self, mod_name, poly_map: _PolyMap):
        self.mod_name: str = mod_name
        self.poly_map: _PolyMap = poly_map


def _ComputeArrayLength(node, kind: cwast.BASE_TYPE_KIND) -> int:
    if isinstance(node, cwast.ValNum):
        return ParseNumRaw(node, kind)[0]
    elif isinstance(node, cwast.Id):
        node = node.x_symbol
        return _ComputeArrayLength(node, kind)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)) and not node.mut:
        return _ComputeArrayLength(node.initial_or_undef_or_auto, kind)
    elif isinstance(node, cwast.Expr2):
        if node.binary_expr_kind is cwast.BINARY_EXPR_KIND.ADD:
            return _ComputeArrayLength(node.expr1, kind) + _ComputeArrayLength(node.expr2, kind)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.MUL:
            return _ComputeArrayLength(node.expr1, kind) * _ComputeArrayLength(node.expr2, kind)
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.DIV:
            return _ComputeArrayLength(node.expr1, kind) // _ComputeArrayLength(node.expr2, kind)
        else:
            assert False
    elif isinstance(node, cwast.ValAuto):
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
    assert node.x_type is cwast.NO_TYPE, f"duplicate annotation for {node}"
    return UpdateNodeType(node, ct)


def AnnotateNodeField(node, field_node: cwast.RecField):
    assert isinstance(
        node, (cwast.ExprField, cwast.FieldVal, cwast.ExprOffsetof))
    assert node.x_field is None
    node.x_field = field_node


def _TypifyNodeRecursively(node, tc: type_corpus.TypeCorpus,
                           target_type: cwast.CanonType,
                           ctx: _TypeContext) -> cwast.CanonType:
    """Do not call this outside of functions"""
    extra = "" if target_type == cwast.NO_TYPE else f"[{target_type.name}]"
    logger.debug("TYPIFYING%s %s", extra, node)
    ct = cwast.NO_TYPE
    if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
        ct = node.x_type
    if ct is not cwast.NO_TYPE:
        # has been typified already
        return ct

    if isinstance(node, cwast.TypeAuto):
        assert target_type is not cwast.NO_TYPE
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS or cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS
        # assert isinstance(def_node, cwast.DefType), f"unexpected node {def_node}"
        _TypifyNodeRecursively(def_node, tc, target_type, ctx)
        if isinstance(def_node, (cwast.DefType, cwast.DefFun, cwast.DefRec, cwast.EnumVal,
                                 cwast.DefEnum)):
            ct = def_node.x_type
        elif isinstance(def_node, cwast.FunParam):
            ct = def_node.type.x_type
        else:
            assert isinstance(
                def_node, (cwast.DefVar, cwast.DefGlobal, cwast.FunParam)), f"{def_node}"
            ct = def_node.type_or_auto.x_type
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.TypeBase):
        return AnnotateNodeType(node, tc.get_base_canon_type(node.base_type_kind))
    elif isinstance(node, cwast.TypePtr):
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, t))
    elif isinstance(node, cwast.TypeSlice):
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_slice_type(node.mut, t))
    elif isinstance(node, cwast.FunParam):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, (cwast.TypeFun, cwast.DefFun)):
        params = []
        for p in node.params:
            _TypifyNodeRecursively(p, tc, cwast.NO_TYPE, ctx)
            params.append(p.type.x_type)
        result = _TypifyNodeRecursively(
            node.result, tc, cwast.NO_TYPE, ctx)
        ct = tc.insert_fun_type(params, result)
        AnnotateNodeType(node, ct)
        # recursing into the body is done explicitly
        return ct
    elif isinstance(node, cwast.TypeArray):
        # note this is the only place where we need a comptime eval for types
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.size, tc, uint_type, ctx)
        dim = _ComputeArrayLength(node.size, uint_type.base_type_kind)
        return AnnotateNodeType(node, tc.insert_array_type(dim, t))
    elif isinstance(node, cwast.RecField):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.DefRec):
        # allow recursive definitions referring back to rec inside
        # the fields
        ct = tc.insert_rec_type(f"{ctx.mod_name}/{node.name}", node)
        AnnotateNodeType(node, ct)
        for f in node.fields:
            _TypifyNodeRecursively(f, tc, cwast.NO_TYPE, ctx)
        # we delay this until after fields have been typified this is necessary
        # because of recursive types
        tc.finalize_rec_type(ct)
        return ct
    elif isinstance(node, cwast.EnumVal):
        if isinstance(node.value_or_auto, cwast.ValAuto):
            AnnotateNodeType(node.value_or_auto, target_type)
        else:
            ct = _TypifyNodeRecursively(
                node.value_or_auto, tc, target_type, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.DefEnum):
        ct = tc.insert_enum_type(f"{ctx.mod_name}/{node.name}", node)
        for f in node.items:
            _TypifyNodeRecursively(f, tc, ct, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.DefType):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        if node.wrapped:
            ct = tc.insert_wrapped_type(ct)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.TypeUnion):
        # this is tricky code to ensure that children of TypeSum
        # are not TypeSum themselves on the canonical side
        pieces = [_TypifyNodeRecursively(
            f, tc, cwast.NO_TYPE, ctx) for f in node.types]
        return AnnotateNodeType(node, tc.insert_union_type(pieces, node.untagged))
    elif isinstance(node, cwast.TypeUnionDelta):
        minuend = _TypifyNodeRecursively(
            node.type, tc, cwast.NO_TYPE, ctx)
        subtrahend = _TypifyNodeRecursively(
            node.subtrahend, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_sum_complement(minuend, subtrahend))
    elif isinstance(node, (cwast.ValTrue, cwast.ValFalse)):
        return AnnotateNodeType(node, tc.get_bool_canon_type())
    elif isinstance(node, cwast.ValVoid):
        return AnnotateNodeType(node, tc.get_void_canon_type())
    elif isinstance(node, cwast.ValUndef):
        assert False, "Must not try to typify UNDEF"
    elif isinstance(node, cwast.ValNum):
        target_kind = target_type.base_type_kind if target_type else cwast.BASE_TYPE_KIND.INVALID
        actual_kind = ParseNumRaw(node, target_kind)[1]
        ct = tc.get_base_canon_type(actual_kind)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.TypeOf):
        ct = _TypifyNodeRecursively(node.expr, tc,  cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ValAuto):
        assert target_type is not cwast.NO_TYPE
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.IndexVal):
        if not isinstance(node.value_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(node.value_or_undef,
                                   tc, target_type, ctx)
        uint_type = tc.get_uint_canon_type()
        if isinstance(node.init_index, cwast.ValAuto):
            AnnotateNodeType(node.init_index, uint_type)
        else:
            _TypifyNodeRecursively(node.init_index, tc, uint_type, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ValArray):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        for x in node.inits_array:
            assert isinstance(x, cwast.IndexVal)
            _TypifyNodeRecursively(x, tc, ct, ctx)
        #
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr_size, tc, uint_type, ctx)
        dim = _ComputeArrayLength(node.expr_size, uint_type.base_type_kind)
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
            if not isinstance(val.value_or_undef, cwast.ValUndef):
                _TypifyNodeRecursively(val.value_or_undef, tc, field_ct, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ValString):
        dim = ComputeStringSize(node.strkind, node.string)
        ct = tc.insert_array_type(
            dim, tc.get_base_canon_type(cwast.BASE_TYPE_KIND.U8))
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprIndex):
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr_index, tc, uint_type, ctx)
        ct = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        return AnnotateNodeType(node, ct.contained_type())
    elif isinstance(node, cwast.ExprField):
        ct = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        field_node = tc.lookup_rec_field(ct, node.field)
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(node, field_node.x_type)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        initial = node.initial_or_undef_or_auto
        if isinstance(node.type_or_auto, cwast.TypeAuto):
            assert not isinstance(initial, cwast.ValUndef)
            ct = _TypifyNodeRecursively(
                node.initial_or_undef_or_auto, tc, cwast.NO_TYPE, ctx)
            _TypifyNodeRecursively(node.type_or_auto, tc, ct, ctx)
        else:
            ct = _TypifyNodeRecursively(
                node.type_or_auto, tc, cwast.NO_TYPE, ctx)
            if not isinstance(initial, cwast.ValUndef):
                ct = _TypifyNodeRecursively(initial, tc, ct, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.ExprDeref):
        ct = _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        if not ct.is_pointer():
            cwast.CompilerError(
                node.x_srcloc, f"dereferenced expr must be pointer {node} but got {ct}")
        # TODO: how is mutability propagated?
        return AnnotateNodeType(node, ct.underlying_pointer_type())
    elif isinstance(node, cwast.Expr1):
        ct = _TypifyNodeRecursively(node.expr, tc, target_type, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.Expr2):
        ct: cwast.CanonType = _TypifyNodeRecursively(
            node.expr1, tc, target_type, ctx)
        if node.binary_expr_kind in cwast.BINOP_OPS_HAVE_SAME_TYPE and ct.is_number():
            ct2 = _TypifyNodeRecursively(node.expr2, tc, ct, ctx)
        else:
            ct2 = _TypifyNodeRecursively(
                node.expr2, tc, cwast.NO_TYPE, ctx)

        if node.binary_expr_kind in cwast.BINOP_BOOL:
            ct = tc.get_bool_canon_type()
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
            if ct.is_pointer():
                assert ct2.is_pointer()
                ct = tc.get_sint_canon_type()
            elif ct.is_slice():
                assert ct2.is_slice()
            else:
                assert False
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprPointer):
        ct = _TypifyNodeRecursively(node.expr1, tc, target_type, ctx)
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr2, tc, uint_type, ctx)
        if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
            _TypifyNodeRecursively(
                node.expr_bound_or_undef, tc, uint_type, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprUnionTag):
        ct = _TypifyNodeRecursively(
            node.expr, tc, cwast.NO_TYPE, ctx)
        assert ct.is_tagged_union()
        return AnnotateNodeType(node, tc.get_typeid_canon_type())
    elif isinstance(node, cwast.ExprFront):
        ct = _TypifyNodeRecursively(
            node.container, tc, cwast.NO_TYPE, ctx)
        if not ct.is_slice() and not ct.is_array():
            cwast.CompilerError(
                node.x_srcloc, "expected container in front expression")
        p_type = tc.insert_ptr_type(
            node.mut, ct.underlying_array_or_slice_type())
        return AnnotateNodeType(node, p_type)
    elif isinstance(node, cwast.Expr3):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        ct = _TypifyNodeRecursively(node.expr_t, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr_f, tc, ct, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.StmtExpr):
        _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.ExprStmt):
        assert target_type != cwast.NO_TYPE
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ExprCall):
        callee = node.callee
        if node.polymorphic:
            assert len(node.args) > 0
            assert isinstance(callee, cwast.Id)
            t = _TypifyNodeRecursively(
                node.args[0], tc, cwast.NO_TYPE, ctx)
            called_fun = ctx.poly_map.Resolve(callee, t)
            symbolize.AnnotateNodeSymbol(callee, called_fun)
            AnnotateNodeType(callee, called_fun.x_type)
            ct_callee: cwast.CanonType = called_fun.x_type
            assert ct_callee.is_fun(), f"{ct}"
            params_ct = ct_callee.parameter_types()
            assert len(params_ct) == len(node.args)
            # we already process the first arg
            for p, a in zip(params_ct[1:], node.args[1:]):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct_callee.result_type())
        else:
            ct = _TypifyNodeRecursively(callee, tc, cwast.NO_TYPE, ctx)
            params_ct = ct.parameter_types()
            if len(params_ct) != len(node.args):
                cwast.CompilerError(node.x_srcloc,
                                    f"number of args does not match for call to {callee}")
            for p, a in zip(params_ct, node.args):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct.result_type())
    elif isinstance(node, cwast.StmtReturn):
        _TypifyNodeRecursively(node.expr_ret, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtIf):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        for c in node.body_f:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        for c in node.body_t:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.Case):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtCond):
        for c in node.cases:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtBlock):
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtBreak):
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtContinue):
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtTrap):
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtAssignment):
        var_cstr = _TypifyNodeRecursively(
            node.lhs, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtCompoundAssignment):
        var_cstr = _TypifyNodeRecursively(
            node.lhs, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, var_cstr, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, (cwast.ExprAs, cwast.ExprNarrow, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprWrap):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        assert ct.is_wrapped()
        _TypifyNodeRecursively(
            node.expr, tc, ct.underlying_wrapped_type(), ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprUnwrap):
        ct = _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        if ct.is_wrapped():
            return AnnotateNodeType(node, ct.underlying_wrapped_type())
        elif ct.is_enum():
            return AnnotateNodeType(node, tc.get_base_canon_type(ct.base_type_kind))
        else:
            assert False
    elif isinstance(node, cwast.ExprIs):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.get_bool_canon_type())
    elif isinstance(node, cwast.ExprLen):
        _TypifyNodeRecursively(node.container, tc, cwast.NO_TYPE, ctx)
        uint_type = tc.get_uint_canon_type()
        return AnnotateNodeType(node, uint_type)
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = _TypifyNodeRecursively(
            node.expr_lhs, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, cstr_expr))
    elif isinstance(node, cwast.ExprOffsetof):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        field_node = tc.lookup_rec_field(ct, node.field)
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateNodeField(node, field_node)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprSizeof):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprUnionUntagged):
        ct = _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        assert ct.is_tagged_union()
        return AnnotateNodeType(node, tc.insert_union_type(ct.children, True))
    elif isinstance(node, (cwast.StmtStaticAssert)):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.Import):
        return cwast.NO_TYPE
    elif isinstance(node, cwast.StmtDefer):
        for c in node.body:
            _TypifyNodeRecursively(c, tc, target_type, ctx)
        return cwast.NO_TYPE
    elif isinstance(node, cwast.ExprTypeId):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.get_typeid_canon_type())
    elif isinstance(node, cwast.ValSlice):
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr_size, tc, uint_type, ctx)
        if isinstance(target_type, cwast.TypeSlice):
            ptr_type = tc.insert_ptr_type(target_type.mut, target_type.type)
            _TypifyNodeRecursively(node.pointer, tc, ptr_type, ctx)
            return AnnotateNodeType(node, target_type)
        else:
            ptr_type = _TypifyNodeRecursively(
                node.pointer, tc, cwast.NO_TYPE, ctx)
            return AnnotateNodeType(
                node, tc.insert_slice_type(ptr_type.mut, ptr_type.underlying_pointer_type()))
    else:
        assert False, f"unexpected node {node}"


UNTYPED_NODES_TO_BE_TYPECHECKED = (
    cwast.StmtReturn, cwast.StmtIf, cwast.DefVar, cwast.DefGlobal,
    cwast.StmtAssignment, cwast.StmtCompoundAssignment, cwast.StmtExpr)


def _CheckTypeUint(node, actual: cwast.CanonType):
    if not actual.is_uint():
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not uint: {actual}")


def _CheckTypeSame(node, actual: cwast.CanonType, expected: cwast.CanonType):
    if actual is not expected:
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not the same actual: {actual} expected: {expected}")


def _CheckTypeCompatibleForEq(node, actual: cwast.CanonType, expected: cwast.CanonType):
    if expected.original_type is not None:
        expected = expected.original_type
    if actual.original_type is not None:
        actual = actual.original_type
    if not type_corpus.is_compatible_for_eq(actual, expected):
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: incompatible actual: {actual} expected: {expected}")


def _CheckTypeSameExceptMut(node, actual: cwast.CanonType, expected: cwast.CanonType,
                            srcloc=None):
    if actual is expected:
        return
    if actual.node is expected.node and actual.mut and not expected.mut:
        if (actual.node in (cwast.TypePtr, cwast.TypeSlice, cwast.TypeArray, cwast.TypePtr) and
                actual.children[0] == expected.children[0]):
            return
    if actual.original_type and expected.original_type:
        _CheckTypeSameExceptMut(node, actual.original_type, expected.original_type,
                                srcloc)
        return
    cwast.CompilerError(srcloc if srcloc else node.x_srcloc,
                        f"{node}: not the same actual: {actual} expected: {expected}")


def _CheckTypeCompatible(node, actual: cwast.CanonType, expected: cwast.CanonType,
                         srcloc=None):
    if expected.original_type is not None:
        expected = expected.original_type
    if not type_corpus.is_compatible(actual, expected):
        cwast.CompilerError(srcloc if srcloc else node.x_srcloc,
                            f"{node}: incompatible actual: {actual} expected: {expected}")


def _CheckTypeCompatibleForAssignment(node, actual: cwast.CanonType,
                                      expected: cwast.CanonType, mutable: bool, srcloc=None):
    if not type_corpus.is_compatible(actual, expected, mutable):
        cwast.CompilerError(srcloc if srcloc else node.x_srcloc,
                            f"{node}: incompatible actual: {actual} expected: {expected}")


def _CheckExpr2Types(node, result_type: cwast.CanonType, op1_type: cwast.CanonType,
                     op2_type: cwast.CanonType, kind: cwast.BINARY_EXPR_KIND,
                     tc: type_corpus.TypeCorpus):
    if kind in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
        assert result_type.is_bool()
        _CheckTypeCompatibleForEq(node, op1_type, op2_type)
    elif kind in cwast.BINOP_BOOL:
        assert op1_type.is_base_type() and result_type.is_bool()
        _CheckTypeSame(node, op1_type, op2_type)
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        if op1_type.is_pointer():
            if result_type != tc.get_sint_canon_type():
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


def _CheckFieldVal(node: cwast.FieldVal, tc: type_corpus.TypeCorpus):
    field_node = node.x_field
    _CheckTypeSame(node, field_node.x_type, node.x_type)
    if not isinstance(node.value_or_undef, cwast.ValUndef):
        _CheckTypeCompatibleForAssignment(
            node, node.value_or_undef.x_type, node.x_type, type_corpus.is_mutable_array(
                node.value_or_undef),
            node.value_or_undef.x_srcloc)


def CheckFieldValStrict(node: cwast.FieldVal, tc: type_corpus.TypeCorpus):
    field_node = node.x_field
    _CheckTypeSame(node, field_node.x_type, node.x_type)
    if not isinstance(node.value_or_undef, cwast.ValUndef):
        _CheckTypeSameExceptMut(
            node, node.value_or_undef.x_type, node.x_type)


def CheckValArray(node: cwast.ValArray, tc: type_corpus.TypeCorpus):
    cstr = node.type.x_type
    for x in node.inits_array:
        assert isinstance(x, cwast.IndexVal), f"{x}"
        if not isinstance(x.init_index, cwast.ValAuto):
            assert x.init_index.x_type.is_int()
        # TODO: this should be  _CheckTypeCompatibleForAssignment
        _CheckTypeSame(node,  x.x_type, cstr)


def CheckExpr3(node: cwast.Expr3, tc: type_corpus.TypeCorpus):
    ct = node.x_type
    t_ct = node.expr_t.x_type
    f_ct = node.expr_f.x_type
    cond_ct = node.cond.x_type
    _CheckTypeSame(node, t_ct, ct)
    _CheckTypeSame(node, f_ct, ct)
    assert cond_ct.is_bool()


def CheckExprDeref(node: cwast.ExprDeref, _):
    expr_type: cwast.CanonType = node.expr.x_type
    assert expr_type.is_pointer()
    _CheckTypeSame(node, node.x_type, expr_type.underlying_pointer_type())


def CheckExprPointer(node: cwast.ExprPointer, _):
    if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
        _CheckTypeUint(node, node.expr_bound_or_undef.x_type)
    assert node.expr1.x_type.is_pointer() or node.expr1.x_type.is_slice()
    # _CheckTypeUint(node, tc, node.expr2.x_type)
    _CheckTypeSame(node, node.expr1.x_type, node.x_type)


def CheckExprField(node: cwast.ExprField, _):
    # _CheckTypeSame(node,  node.x_field.x_type, ct)
    assert node.x_type is node.x_field.x_type, f"field node {node.container.x_type} type mismatch: {node.x_type} {node.x_field.x_type}"


def CheckExprFront(node: cwast.ExprFront, _):

    assert node.container.x_type.is_array_or_slice(
    ), f"unpected front expr {node.container.x_type}"
    if node.mut:
        if not type_corpus.is_mutable_array_or_slice(node.container):
            cwast.CompilerError(
                node.x_srcloc, f"container not mutable: {node} {node.container}")

    if node.container.x_type.is_array():
        # TODO: check if address can be taken
        pass

    assert node.x_type.is_pointer()
    _CheckTypeSame(node, node.x_type.underlying_pointer_type(),
                   node.container.x_type.underlying_array_or_slice_type())


def CheckExprAs(node: cwast.ExprAs, _):
    ct_src = node.expr.x_type
    ct_dst = node.type.x_type
    if not type_corpus.is_compatible_for_as(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad cast {ct_src} -> {ct_dst}: {node.expr}")


def _CheckExprWiden(node: cwast.ExprWiden, _):
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if not type_corpus.is_compatible_for_widen(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad widen {ct_src.original_type} -> {ct_dst}: {node.expr}")


def _CheckExprNarrow(node: cwast.ExprNarrow, _):
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if not type_corpus.is_compatible_for_narrow(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad narrow {ct_src.original_type} -> {ct_dst}: {node.expr}")


def CheckExprNarrowUnchecked(node: cwast.ExprNarrow, _):
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if ct_src.is_tagged_union() and not node.unchecked:
        cwast.CompilerError(
            node.x_srcloc,  f"narrow must be unchecked {ct_src.original_type} -> {ct_dst}: {node.expr}")


def CheckExprAddrOf(node: cwast.ExprAddrOf, _):
    ct = node.x_type
    expr_ct = node.expr_lhs.x_type
    if node.mut:
        if not type_corpus.is_proper_lhs(node.expr_lhs):
            cwast.CompilerError(node.x_srcloc,
                                f"not mutable: {node.expr_lhs}")
    if not address_can_be_taken(node.expr_lhs):
        cwast.CompilerError(node.x_srcloc,
                            f"address cannot be take: {node} {node.expr_lhs.x_type.name}")
    assert ct.is_pointer() and ct.underlying_pointer_type() == expr_ct


def CheckExprSumUntagged(node: cwast.ExprUnionUntagged, _):
    assert node.x_type.is_untagged_union()
    assert node.expr.x_type.is_tagged_union(), f"{node.expr.x_type}"
    for c1, c2 in zip(node.x_type.union_member_types(), node.expr.x_type.union_member_types()):
        _CheckTypeSame(node, c1, c2)


def CheckValNum(node: cwast.ValNum, _):
    ct = node.x_type
    if not ct.is_base_type() and not ct.is_enum():
        cwast.CompilerError(node.x_srcloc, f"type mismatch {node} vs {ct}")


def CheckExprCall(node: cwast.ExprCall,  _):
    fun_sig: cwast.CanonType = node.callee.x_type
    assert fun_sig.is_fun(), f"{fun_sig}"
    assert fun_sig.result_type(
    ) == node.x_type, f"{fun_sig.result} {node.x_type}"
    for p, a in zip(fun_sig.parameter_types(), node.args):
        _CheckTypeCompatibleForAssignment(
            p,  a.x_type, p, type_corpus.is_mutable_array(a), a.x_srcloc)


def CheckExprCallStrict(node: cwast.ExprCall,  _):
    fun_sig: cwast.CanonType = node.callee.x_type
    assert fun_sig.is_fun(), f"{fun_sig}"
    assert fun_sig.result_type(
    ) == node.x_type, f"{fun_sig.result} {node.x_type}"
    for p, a in zip(fun_sig.parameter_types(), node.args):
        _CheckTypeSameExceptMut(
            p,  a.x_type, p, a.x_srcloc)


def CheckExprIndex(node: cwast.ExprIndex, _):
    assert node.x_type is node.container.x_type.underlying_array_or_slice_type()


def CheckExprWrap(node: cwast.ExprWrap,  _):
    ct_node: cwast.CanonType = node.x_type
    ct_expr: cwast.CanonType = node.expr.x_type
    assert ct_node == node.type.x_type
    if not type_corpus.is_compatible_for_wrap(ct_expr, ct_node):
        cwast.CompilerError(
            node.x_srcloc, f"bad wrap {ct_expr} -> {ct_node}")


def CheckExprUnwrap(node: cwast.ExprUnwrap,  _):
    ct_node: cwast.CanonType = node.x_type
    ct_expr: cwast.CanonType = node.expr.x_type
    if ct_expr.is_enum():
        assert ct_node.is_base_type() and ct_expr.base_type_kind == ct_node.base_type_kind
    elif ct_expr.is_wrapped():
        assert ct_expr.underlying_wrapped_type() in (
            ct_node, ct_node.original_type), f"{ct_node} vs {ct_expr}"
    else:
        assert False


def CheckDefFunTypeFun(node, _):
    ct = node.x_type
    assert ct.is_fun()
    _CheckTypeSame(node.result, ct.result_type(), node.result.x_type)
    for a, b in zip(ct.parameter_types(), node.params):
        _CheckTypeSame(b, a, b.type.x_type)
    # We should also ensure three is a proper return but that requires dataflow


def CheckValSlice(node: cwast.ValSlice, _):
    assert node.x_type.is_mutable() == node.pointer.x_type.is_mutable()
    _CheckTypeSame(node, node.x_type.underlying_slice_type(),
                   node.pointer.x_type.underlying_pointer_type())


def CheckExprSumTag(node: cwast.ExprUnionTag, tc: type_corpus.TypeCorpus):
    assert node.x_type is tc.get_typeid_canon_type()
    assert node.expr.x_type.is_tagged_union()


def CheckId(node: cwast.Id,  _):
    ct = node.x_type
    def_node = node.x_symbol
    if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
        _CheckTypeSame(node, ct, def_node.type_or_auto.x_type)
    elif isinstance(def_node, (cwast.FunParam)):
        _CheckTypeSame(node,  ct, def_node.type.x_type)
    # else:
    #    _CheckTypeSame(node, tc, node.x_type, def_node.x_type)


def CheckDefRecDefEnum(node, _):
    assert node.x_type.ast_node is node


def CheckIsBool(node: Any, _):
    assert node.x_type.is_bool()


def CheckIsVoid(node: Any, _):
    assert node.x_type.is_void()


def CheckIsUint(node: Any,  tc: type_corpus.TypeCorpus):
    assert node.x_type is tc.get_uint_canon_type()


def CheckIsTypeId(node: Any, tc: type_corpus.TypeCorpus):
    assert node.x_type is tc.get_typeid_canon_type()


def CheckStmtCompoundAssignment(node: cwast.StmtCompoundAssignment,  tc: type_corpus.TypeCorpus):
    if not type_corpus.is_proper_lhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")
    kind = cwast.COMPOUND_KIND_TO_EXPR_KIND[node.assignment_kind]
    var_ct = node.lhs.x_type
    expr_ct = node.expr_rhs.x_type
    _CheckExpr2Types(node, var_ct, var_ct, expr_ct, kind, tc)


def CheckStmtAssignment(node: cwast.StmtAssignment, _):
    var_ct = node.lhs.x_type
    expr_ct = node.expr_rhs.x_type
    _CheckTypeCompatibleForAssignment(
        node, expr_ct, var_ct, type_corpus.is_mutable_array(
            node.expr_rhs),
        node.expr_rhs.x_srcloc)

    if not type_corpus.is_proper_lhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")


def CheckStmtAssignmentStrict(node: cwast.StmtAssignment, _):
    var_ct = node.lhs.x_type
    expr_ct = node.expr_rhs.x_type

    _CheckTypeSameExceptMut(
        node, expr_ct, var_ct, node.expr_rhs.x_srcloc)
    if not type_corpus.is_proper_lhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")


def CheckStmtReturn(node: cwast.StmtReturn, _):
    target = node.x_target
    actual = node.expr_ret.x_type
    if isinstance(target, cwast.DefFun):
        expected = target.result.x_type
    else:
        assert isinstance(target, cwast.ExprStmt)
        expected = target.x_type
    _CheckTypeCompatible(node,  actual, expected)


def CheckStmtReturnStrict(node: cwast.StmtReturn, _):
    target = node.x_target
    actual = node.expr_ret.x_type
    if isinstance(target, cwast.DefFun):
        expected = target.result.x_type
    else:
        assert isinstance(target, cwast.ExprStmt)
        expected = target.x_type
    _CheckTypeSameExceptMut(node,  actual, expected)


def CheckStmtIfStmtCond(node, _):
    assert node.cond.x_type.is_bool()


def CheckDefVarDefGlobal(node, _):
    initial = node.initial_or_undef_or_auto
    if not isinstance(initial, cwast.ValUndef):
        ct = node.type_or_auto.x_type
        _CheckTypeCompatibleForAssignment(
            node, initial.x_type, ct, type_corpus.is_mutable_array(
                initial),
            initial.x_srcloc)


def CheckDefVarDefGlobalStrict(node, _):
    initial = node.initial_or_undef_or_auto
    if not isinstance(initial, cwast.ValUndef):
        ct = node.type_or_auto.x_type
        _CheckTypeSameExceptMut(
            node, initial.x_type, ct, initial.x_srcloc)


def CheckNothing(_, _2):
    pass


class TypeVerifier:
    """"This class allows us to switch out per node checkers as we modify the AST"""

    def __init__(self):
        # maps nodes
        self._map = {
            cwast.FieldVal: _CheckFieldVal,
            cwast.ValArray: CheckValArray,
            cwast.Expr1: lambda node, tc: _CheckTypeSame(node, node.x_type, node.expr.x_type),

            cwast.TypeOf: lambda node, tc: _CheckTypeSame(node, node.x_type, node.expr.x_type),
            cwast.Expr2: lambda node, tc:  _CheckExpr2Types(node, node.x_type,  node.expr1.x_type,
                                                            node.expr2.x_type, node.binary_expr_kind, tc),
            cwast.Expr3: CheckExpr3,
            cwast.ExprDeref: CheckExprDeref,
            cwast.ExprPointer: CheckExprPointer,
            cwast.ExprIndex: CheckExprIndex,
            cwast.ExprField: CheckExprField,
            cwast.ExprFront: CheckExprFront,
            cwast.ExprAs: CheckExprAs,
            cwast.ExprWiden: _CheckExprWiden,
            cwast.ExprNarrow: _CheckExprNarrow,
            cwast.ExprAddrOf: CheckExprAddrOf,
            cwast.ExprUnionTag: CheckExprSumTag,
            cwast.ExprUnionUntagged: CheckExprSumUntagged,
            cwast.ExprWrap: CheckExprWrap,
            cwast.ExprUnwrap: CheckExprUnwrap,
            cwast.ExprCall: CheckExprCall,

            cwast.Id: CheckId,
            #
            cwast.TypeUnion: lambda node, tc: node.x_type.is_union(),
            cwast.TypeFun: CheckDefFunTypeFun,
            #
            cwast.DefRec: CheckDefRecDefEnum,
            cwast.DefEnum: CheckDefRecDefEnum,
            #
            cwast.DefFun: CheckDefFunTypeFun,
            #
            cwast.ValSlice: CheckValSlice,
            #
            cwast.ValNum: CheckValNum,
            #
            cwast.ExprIs: CheckIsBool,
            cwast.ValTrue: CheckIsBool,
            cwast.ValFalse: CheckIsBool,
            #
            cwast.ValVoid: CheckIsVoid,
            #
            cwast.ExprTypeId: CheckIsTypeId,
            #
            cwast.ExprOffsetof: CheckIsUint,
            cwast.ExprSizeof:  CheckIsUint,
            cwast.ExprLen: CheckIsUint,
            #
            cwast.DefType: CheckNothing,
            cwast.TypeBase: CheckNothing,
            cwast.TypeSlice: CheckNothing,
            cwast.IndexVal: CheckNothing,
            cwast.TypeArray: CheckNothing,
            cwast.TypeAuto: CheckNothing,
            cwast.TypePtr: CheckNothing,
            cwast.FunParam: CheckNothing,
            cwast.EnumVal: CheckNothing,
            cwast.ValAuto: CheckNothing,
            cwast.ValString: CheckNothing,
            cwast.ExprStmt: CheckNothing,
            cwast.ValRec: CheckNothing,
            cwast.RecField: CheckNothing,
            cwast.TypeUnionDelta:  CheckNothing,
            # minuned = node.type.x_type
            #  subtrahend = node.subtrahend.x_type
            # TODO: need to use origianal types if available
            cwast.ExprUnsafeCast: CheckNothing,
            # src = node.expr.x_type
            # dst = node.type.x_type
            # TODO
            # assert is_compatible_for_as(src, dst)
            cwast.ExprBitCast: CheckNothing,
            # src = node.expr.x_type
            # dst = node.type.x_type
            # TODO
            # assert is_compatible_for_as(src, dst)
            #
            # Statements
            cwast.StmtIf: CheckStmtIfStmtCond,
            cwast.StmtCond: CheckStmtIfStmtCond,
            cwast.StmtExpr:  CheckNothing,
            cwast.StmtCompoundAssignment: CheckStmtCompoundAssignment,
            cwast.StmtAssignment: CheckStmtAssignment,
            cwast.StmtReturn: CheckStmtReturn,
            cwast.DefVar: CheckDefVarDefGlobal,
            cwast.DefGlobal: CheckDefVarDefGlobal,
        }

    def Verify(self, node: cwast.ALL_NODES, tc: type_corpus.TypeCorpus):

        self._map[type(node)](node, tc)

    def Replace(self, node_type, checker):
        self._map[node_type] = checker


def VerifyTypesRecursively(node, tc: type_corpus.TypeCorpus,
                           verifier: TypeVerifier):
    def visitor(node, _):
        nonlocal verifier
        if cwast.NF.TOP_LEVEL in node.FLAGS:
            logger.info("TYPE-VERIFYING %s", node)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            ct: cwast.CanonType = node.x_type
            assert ct is not cwast.NO_TYPE, f"missing type for {node} in {node.x_srcloc}"
            assert ct.name in tc.corpus, f"bad type annotation for {node}: {node.x_type}"
            verifier.Verify(node, tc)

        elif isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED):
            verifier.Verify(node, tc)

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
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            # Note: _TypifyNodeRecursivel() does NOT recurse into function bodies
            ct = _TypifyNodeRecursively(node, tc, cwast.NO_TYPE, ctx)
            if isinstance(node, cwast.DefFun) and node.polymorphic:
                assert ct.node is cwast.TypeFun, f"{node} -> {ct.name}"
                poly_map.Register(node)

    for mod in mod_topo_order:
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun) and not node.extern:
                for c in node.body:
                    _TypifyNodeRecursively(
                        c, tc, node.result.x_type, ctx)

############################################################
#
############################################################


def main(argv):
    assert len(argv) == 1
    assert argv[0].endswith(".cw")

    cwd = os.getcwd()
    mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
    mp.InsertSeedMod("builtin")
    mp.InsertSeedMod(str(pathlib.Path(argv[0][:-3]).resolve()))
    mp.ReadAndFinalizedMods()
    mod_topo_order = mp.ModulesInTopologicalOrder()

    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    DecorateASTWithTypes(mod_topo_order, tc)
    verifier = TypeVerifier()
    for mod in mod_topo_order:
        VerifyTypesRecursively(mod, tc, verifier)

    for t, n in tc.corpus.items():
        logger.warning("%s %s %d %d", t, n.register_types, n.size, n.alignment)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FrontEnd import mod_pool

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
