#!/bin/env python3

"""Type annotator for Cwerg AST

This will run after

* macro eliminiation,
* generic module specialization
* symbolization

and before

* partial evaluation

However, some adhoc partial evaluation is necessary here as
well to determine vec dimensions.

We cannot run the fulll partial evaluation earlier because
it depends on type information.

Generally the typifier works recursively, meaning
if you want to typify a complex expression, the typifier will
likely recurse and typify the subexpressions first.

At the module level we try to typify in topological module order
but this is imperfect because of generic modules where type information
flows both ways: the importing module will both provide type information
to the generic module and use type info from it.
"""

import logging

from typing import Tuple, Any, Optional


from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import canonicalize


logger = logging.getLogger(__name__)


def is_ref_def(node) -> bool:
    if isinstance(node, cwast.Id):
        s = node.x_symbol
        return (isinstance(s, cwast.DefGlobal) or isinstance(s, cwast.DefVar)) and s.ref
    return False


def AddressCanBeTaken(node) -> bool:
    # handle ExprNarrow
    return (is_ref_def(node) or
            isinstance(node, cwast.ExprField) or
            isinstance(node, cwast.ExprDeref) or
            isinstance(node, cwast.ExprIndex) and
            node.container.x_type.is_span() or
            isinstance(node, cwast.ExprIndex) and
            AddressCanBeTaken(node.container))


def _NumCleanupAndTypeExtraction(num: str, target_kind: cwast.BASE_TYPE_KIND) -> tuple[str, cwast.BASE_TYPE_KIND]:
    suffix = ""
    if num in ("true", "false"):
        return num, cwast.BASE_TYPE_KIND.BOOL
    elif num[-4:] in ("uint", "sint"):
        suffix = num[-4:]
    elif num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64", "r32", "r64"):
        suffix = num[-3:]
    elif num[-2:] in ("u8", "s8"):
        suffix = num[-2:]
    else:
        return num, target_kind
    return num[:-len(suffix)], cwast.BASE_TYPE_KIND[suffix.upper()]


def ParseNumRaw(num_val: cwast.ValNum, target_kind: cwast.BASE_TYPE_KIND) -> Tuple[Any,  cwast.BASE_TYPE_KIND]:
    num = num_val.number
    if num[0] == "'":
        if target_kind is cwast.BASE_TYPE_KIND.INVALID:
            cwast.CompilerError(
                num_val.x_srcloc, f"Number needs explicit type {num_val}")
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return ord('\n'), target_kind
            elif num[2] == "t":
                return ord('\t'), target_kind
            elif num[2] == "r":
                return ord('\r'), target_kind
            elif num[2] == "\\":
                return ord('\\'), target_kind
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1]), target_kind

    num, target_kind = _NumCleanupAndTypeExtraction(num, target_kind)
    num = num.replace("_", "")
    if target_kind.IsInt():
        return int(num, 0), target_kind
    elif target_kind.IsReal():
        if "0x" in num:
            return float.fromhex(num), target_kind
        return float(num), target_kind
    elif target_kind == cwast.BASE_TYPE_KIND.BOOL:
        if num == "true":
            return True, target_kind
        assert num == "false"
        return False, target_kind
    else:
        cwast.CompilerError(
            num_val.x_srcloc, f"cannot parse number: {num} {target_kind}")
        return (None, cwast.BASE_TYPE_KIND.INVALID)


def ParseNum(num: cwast.ValNum) -> Any:
    assert num.x_type.is_base_type()
    kind = num.x_type.base_type_kind
    val, _ = ParseNumRaw(num, kind)
    bitsize = kind.ByteSize() * 8
    if kind.IsUint():
        assert 0 <= val < (1 << bitsize), f"val {num} out of bounds for {kind}"
    elif kind.IsSint():
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
        self._map: dict[Tuple[cwast.DefMod,
                              cwast.NAME, cwast.CanonType], cwast.DefFun] = {}
        self._type_corpus = tc

    def Register(self, fun: cwast.DefFun):
        assert fun.poly
        ct: cwast.CanonType = fun.x_type
        mod: cwast.DefMod = fun.x_poly_mod
        name = fun.name
        first_param_type = ct.children[0]
        logger.info("Register polymorphic fun %s::%s: %s",
                    str(mod.name), name, first_param_type.name)
        # TODO: Should this work with parameterized volumes
        key = (mod, name, first_param_type)
        assert key not in self._map, f"duplicate poly def {fun.x_srcloc}"
        self._map[key] = fun

    def Resolve(self, callee: cwast.Id, first_param_type: cwast.CanonType) -> cwast.DefFun:
        # TODO: why are we not using the mod_name here?
        fun_name = callee.name
        type_name = first_param_type
        logger.info("Resolving polymorphic fun %s: %s",
                    fun_name, type_name.name)
        callee_mod: cwast.DefMod = callee.x_symbol.x_poly_mod

        out = self._map.get((callee_mod, fun_name, type_name))
        if out:
            return out
        # Handle implicit conversion from vec to span
        if first_param_type.is_vec():
            span_type = self._type_corpus.InsertSpanType(
                False, first_param_type.underlying_type())

            out = self._map.get((callee_mod, fun_name, span_type))
            if out:
                return out
        cwast.CompilerError(
            callee.x_srcloc, f"cannot resolve polymorphic {fun_name} {type_name}")


def _ComputeArrayLength(node) -> int:
    # TODO: this should be more strict WRT to the exact type/bitwidth of integer
    if isinstance(node, cwast.ValNum):
        num, target_kind = _NumCleanupAndTypeExtraction(
            node.number, cwast.BASE_TYPE_KIND.UINT)
        assert target_kind.IsInt()
        return int(num.replace("_", ""), 0)
    elif isinstance(node, cwast.Id):
        return _ComputeArrayLength(node.x_symbol)
    elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
        assert not node.mut
        return _ComputeArrayLength(node.initial_or_undef_or_auto)
    elif isinstance(node, cwast.Expr2):
        op1 = _ComputeArrayLength(node.expr1)
        op2 = _ComputeArrayLength(node.expr2)
        if node.binary_expr_kind is cwast.BINARY_EXPR_KIND.ADD:
            return op1 + op2
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.SUB:
            return op1 - op2
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.MUL:
            return op1 * op2
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.DIV:
            return op1 // op2
        else:
            assert False
    else:
        assert False, f"unexpected dim node: {node}"


def UpdateNodeType(node, ct: cwast.CanonType) -> cwast.CanonType:
    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"node not meant for type annotation: {
        node}"
    assert ct, f"No valid type for {node}"
    node.x_type = ct
    return ct


def AnnotateNodeType(node, ct: cwast.CanonType) -> cwast.CanonType:
    logger.info("Set type of %s: %s  [%s]", node, ct.name, node.x_srcloc)
    assert ct != cwast.NO_TYPE
    assert node.x_type is cwast.NO_TYPE, f"duplicate annotation for {node}"
    return UpdateNodeType(node, ct)


def AnnotateFieldWithTypeAndSymbol(node, field_node: cwast.RecField):
    assert isinstance(node, cwast.Id), f"{node}"
    AnnotateNodeType(node, field_node.x_type)
    assert node.x_symbol is cwast.INVALID_SYMBOL, f"Id already field annotate: {
        node}"
    node.x_symbol = field_node


def _GetExprStmtType(root: cwast.ExprStmt) -> cwast.CanonType:
    result: Optional[cwast.CanonType] = None

    def visitor(node):
        nonlocal result, root
        if node != root and isinstance(node, cwast.ExprStmt):
            return True  # do not recurse
        if not isinstance(node, cwast.StmtReturn):
            return False
        if result:
            assert result is node.expr_ret.x_type
        else:
            result = node.expr_ret.x_type
    cwast.VisitAstRecursively(root, visitor)
    assert result is not None
    return result


def _TypifyDefGlobalOrDefVar(node, tc: type_corpus.TypeCorpus,
                             pm: _PolyMap) -> cwast.CanonType:
    initial = node.initial_or_undef_or_auto
    type = node.type_or_auto
    if isinstance(type, cwast.TypeAuto):
        assert not isinstance(initial, cwast.ValUndef)
        ct = _TypifyExprOrType(initial, tc, cwast.NO_TYPE, pm)
        _TypifyExprOrType(type, tc, ct, pm)
    else:
        ct = _TypifyExprOrType(type, tc, cwast.NO_TYPE, pm)
        if not isinstance(initial, cwast.ValUndef):
            _TypifyExprOrType(initial, tc, ct, pm)
    return AnnotateNodeType(node, ct)


def _TypifyTypeFunOrDefFun(node, tc: type_corpus.TypeCorpus,
                           pm: _PolyMap) -> cwast.CanonType:
    params = []
    for p in node.params:
        assert isinstance(p, cwast.FunParam)
        ct = _TypifyExprOrType(p.type, tc, cwast.NO_TYPE, pm)
        AnnotateNodeType(p, ct)
        params.append(ct)
    result = _TypifyExprOrType(
        node.result, tc, cwast.NO_TYPE, pm)
    return AnnotateNodeType(node, tc.InsertFunType(params, result))


def _TypifyType(node, tc: type_corpus.TypeCorpus,
                target_type: cwast.CanonType,
                pm: _PolyMap) -> cwast.CanonType:

    if isinstance(node, cwast.TypeAuto):
        assert target_type is not cwast.NO_TYPE, f"cannot typify auto in {
            node.x_srcloc}"
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.TypeBase):
        return AnnotateNodeType(node, tc.get_base_canon_type(node.base_type_kind))
    elif isinstance(node, cwast.TypePtr):
        t = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.InsertPtrType(node.mut, t))
    elif isinstance(node, cwast.TypeSpan):
        t = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.InsertSpanType(node.mut, t))
    elif isinstance(node, cwast.TypeFun):
        return _TypifyTypeFunOrDefFun(node, tc, pm)
    elif isinstance(node, cwast.TypeVec):
        # note this is the only place where we need a comptime eval for types
        t = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        _TypifyExprOrType(node.size, tc, tc.get_uint_canon_type(), pm)
        dim = _ComputeArrayLength(node.size)
        return AnnotateNodeType(node, tc.InsertVecType(dim, t))
    elif isinstance(node, cwast.TypeUnion):
        # this is tricky code to ensure that children of TypeUnion
        # are not TypeUnion themselves on the canonical side
        pieces = [_TypifyExprOrType(f, tc, cwast.NO_TYPE, pm)
                  for f in node.types]
        return AnnotateNodeType(node, tc.InsertUnionType(node.untagged, pieces))
    elif isinstance(node, cwast.TypeUnionDelta):
        minuend = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        subtrahend = _TypifyExprOrType(node.subtrahend, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.insert_union_complement(minuend, subtrahend))
    elif isinstance(node, cwast.TypeOf):
        ct = _TypifyExprOrType(node.expr, tc,  cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, ct)
    else:
        assert False, f"{node}"
        return cwast.NO_TYPE


def _TypifyStmtSeq(body: list[Any], tc: type_corpus.TypeCorpus, tt: cwast.CanonType, ctx: _PolyMap):
    for c in body:
        _TypifyStmt(c, tc, tt, ctx)


def _TypifyStmt(node, tc: type_corpus.TypeCorpus,
                tt: cwast.CanonType,
                pm: _PolyMap):
    # tt is used by cwast.StmtReturn
    if isinstance(node, cwast.StmtReturn):
        _TypifyExprOrType(node.expr_ret, tc, tt, pm)
    elif isinstance(node, cwast.StmtIf):
        _TypifyExprOrType(node.cond, tc, tc.get_bool_canon_type(), pm)
        _TypifyStmtSeq(node.body_f, tc, tt, pm)
        _TypifyStmtSeq(node.body_t, tc, tt, pm)

    elif isinstance(node, cwast.Case):
        _TypifyExprOrType(node.cond, tc, tc.get_bool_canon_type(), pm)
        _TypifyStmtSeq(node.body, tc, tt, pm)
    elif isinstance(node, cwast.StmtCond):
        _TypifyStmtSeq(node.cases, tc, tt, pm)
    elif isinstance(node, cwast.StmtBlock):
        _TypifyStmtSeq(node.body, tc, tt, pm)
    elif isinstance(node, (cwast.StmtBreak, cwast.StmtContinue,
                           cwast.StmtTrap)):
        pass
    elif isinstance(node, (cwast.StmtAssignment, cwast.StmtCompoundAssignment)):
        ct = _TypifyExprOrType(node.lhs, tc, cwast.NO_TYPE, pm)
        _TypifyExprOrType(node.expr_rhs, tc, ct, pm)
    elif isinstance(node, cwast.DefVar):
        _TypifyDefGlobalOrDefVar(node, tc, pm)
    elif isinstance(node, cwast.StmtExpr):
        _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
    elif isinstance(node, cwast.StmtDefer):
        _TypifyStmtSeq(node.body, tc, tt, pm)
    else:
        assert False, f"unexpected node: {node}"


def _TypifyValCompound(node: cwast.ValCompound, tc: type_corpus.TypeCorpus,
                       target_type: cwast.CanonType,
                       pm: _PolyMap) -> cwast.CanonType:
    ct = _TypifyExprOrType(node.type_or_auto, tc, target_type, pm)
    if ct.is_vec():
        element_type = ct.underlying_type()
        for point in node.inits:
            assert isinstance(point, cwast.ValPoint)
            AnnotateNodeType(point, element_type)
            #
            val = point.value_or_undef
            if not isinstance(val, cwast.ValUndef):
                _TypifyExprOrType(val, tc, element_type, pm)
            #
            index = point.point_or_undef
            uint_type = tc.get_uint_canon_type()
            if not isinstance(index, cwast.ValUndef):
                _TypifyExprOrType(index, tc, uint_type, pm)
    else:
        assert ct.is_rec(), f"expected rec got {ct} in {node.x_srcloc}"
        for field, point in symbolize.IterateValRec(node.inits, ct):
            if point:
                field_ct = field.x_type
                AnnotateNodeType(point, field_ct)
                if isinstance(point.point_or_undef, cwast.Id):
                    AnnotateFieldWithTypeAndSymbol(point.point_or_undef, field)
                if not isinstance(point.value_or_undef, cwast.ValUndef):
                    _TypifyExprOrType(
                        point.value_or_undef, tc, field_ct, pm)

    return AnnotateNodeType(node, ct)


def _TypifyId(node: cwast.Id, tc: type_corpus.TypeCorpus,
              target_type: cwast.CanonType,
              pm: _PolyMap) -> cwast.CanonType:
    # this case is why we need the sym_tab
    def_node = node.x_symbol
    assert cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS or cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS
    ct = def_node.x_type
    if ct == cwast.NO_TYPE:
        if isinstance(def_node, (cwast.DefVar, cwast.DefGlobal)):
            ct = _TypifyDefGlobalOrDefVar(def_node, tc, pm)
        elif isinstance(def_node, cwast.DefFun):
            ct = _TypifyTypeFunOrDefFun(node, tc, pm)
        else:
            assert False, f"symbol should have a type: {node} -> {def_node}"
    assert ct != cwast.NO_TYPE
    return AnnotateNodeType(node, ct)


def _IsPolymorphicCallee(callee: Any) -> bool:
    if not isinstance(callee, cwast.Id):
        return False
    def_sym = callee.x_symbol
    if not isinstance(def_sym, cwast.DefFun):
        return False
    return def_sym.poly


def _TypifyExprCall(node: cwast.ExprCall, tc: type_corpus.TypeCorpus,
                    target_type: cwast.CanonType,
                    pm: _PolyMap) -> cwast.CanonType:
    callee = node.callee
    if _IsPolymorphicCallee(callee):
        assert len(node.args) > 0
        assert isinstance(callee, cwast.Id)
        t = _TypifyExprOrType(
            node.args[0], tc, cwast.NO_TYPE, pm)
        called_fun = pm.Resolve(callee, t)
        symbolize.UpdateNodeSymbolForPolyCall(callee, called_fun)
        AnnotateNodeType(callee, called_fun.x_type)
        ct_fun = called_fun.x_type
    else:
        ct_fun = _TypifyExprOrType(callee, tc, cwast.NO_TYPE, pm)
    #
    params_ct = ct_fun.parameter_types()
    if len(params_ct) != len(node.args):
        cwast.CompilerError(node.x_srcloc,
                            f"args number mismatch for call to {node.callee}: {len(params_ct)} vs {len(node.args)}")
    for p, a in zip(params_ct, node.args):
        _TypifyExprOrType(a, tc, p, pm)
    return AnnotateNodeType(node, ct_fun.result_type())


def _TypifyVal(node, tc: type_corpus.TypeCorpus,
               target_type: cwast.CanonType,
               pm: _PolyMap) -> cwast.CanonType:
    if isinstance(node, cwast.ValVoid):
        return AnnotateNodeType(node, tc.get_void_canon_type())
    elif isinstance(node, cwast.ValUndef):
        assert False, "Must not try to typify UNDEF"
    elif isinstance(node, cwast.ValNum):
        # note, ct_target may be a union
        target_kind = cwast.BASE_TYPE_KIND.INVALID if target_type == cwast.NO_TYPE else target_type.base_type_kind
        actual_kind = _NumCleanupAndTypeExtraction(node.number, target_kind)[1]
        ct = tc.get_base_canon_type(actual_kind)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ValAuto):
        assert target_type is not cwast.NO_TYPE
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ValCompound):
        return _TypifyValCompound(node, tc, target_type, pm)
    elif isinstance(node, cwast.ValString):
        dim = len(node.get_bytes())
        ct = tc.InsertVecType(
            dim, tc.get_base_canon_type(cwast.BASE_TYPE_KIND.U8))
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ValSpan):
        _TypifyExprOrType(node.expr_size, tc, tc.get_uint_canon_type(), pm)
        if target_type == cwast.NO_TYPE:
            ct_ptr = _TypifyExprOrType(node.pointer, tc, cwast.NO_TYPE, pm)
            target_type = tc.InsertSpanType(
                ct_ptr.mut, ct_ptr.underlying_type())
        else:
            assert target_type.node is cwast.TypeSpan, f"expected span got {target_type}"
            ct_ptr = tc.InsertPtrType(
                target_type.mut, target_type.underlying_type())
            _TypifyExprOrType(node.pointer, tc, ct_ptr, pm)
        return AnnotateNodeType(node, target_type)
    else:
        assert False, f"unexpected node {node}"


def _TypifyExprOrType(node, tc: type_corpus.TypeCorpus,
                      target_type: cwast.CanonType,
                      pm: _PolyMap) -> cwast.CanonType:
    """Do not call this outside of functions"""
    extra = "" if target_type == cwast.NO_TYPE else f"[{target_type.name}]"
    logger.debug("TYPIFYING%s %s", extra, node)

    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"unexpected node {node}"

    ct = node.x_type
    if ct is not cwast.NO_TYPE:
        # has been typified already
        return ct

    # we break out a few more cases to make if statement below more manageable
    if node.GROUP is cwast.GROUP.Type:
        return _TypifyType(node, tc, target_type, pm)

    if node.GROUP is cwast.GROUP.Value:
        return _TypifyVal(node, tc, target_type, pm)

    if isinstance(node, cwast.Id):
        return _TypifyId(node, tc, target_type, pm)

    elif isinstance(node, cwast.ExprIndex):
        uint_type = tc.get_uint_canon_type()
        _TypifyExprOrType(node.expr_index, tc, uint_type, pm)
        ct = _TypifyExprOrType(node.container, tc, cwast.NO_TYPE, pm)
        if not ct.is_vec() and not ct.is_span():
            cwast.CompilerError(
                node.container.x_srcloc, f"expected array or span for {node} but got {ct}")
        return AnnotateNodeType(node, ct.contained_type())
    elif isinstance(node, cwast.ExprField):
        ct = _TypifyExprOrType(node.container, tc, target_type, pm)
        if not ct.is_rec():
            cwast.CompilerError(
                node.x_srcloc, f"container type is not record {node.container}")
        field_name = node.field
        field_node = ct.lookup_rec_field(field_name.GetBaseNameStrict())
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {field_name}")
        AnnotateFieldWithTypeAndSymbol(field_name, field_node)
        return AnnotateNodeType(node, field_node.x_type)
    elif isinstance(node, cwast.ExprDeref):
        ct = _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        if not ct.is_pointer():
            cwast.CompilerError(
                node.x_srcloc, f"dereferenced expr must be pointer {node} but got {ct}")
        # TODO: how is mutability propagated?
        # most likely because we only check mutability for assignments
        return AnnotateNodeType(node, ct.underlying_type())
    elif isinstance(node, cwast.Expr1):
        ct = _TypifyExprOrType(node.expr, tc, target_type, pm)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.Expr2):
        if node.binary_expr_kind.IsComparison():
            # for comparisons the type of the expressions has nothing to do with
            # the type of the operands
            target_type = cwast.NO_TYPE
        ct_left = _TypifyExprOrType(node.expr1, tc, target_type, pm)
        ct_right = _TypifyExprOrType(node.expr2, tc, ct_left, pm)

        if node.binary_expr_kind.IsComparison():
            ct = tc.get_bool_canon_type()
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.PDELTA:
            ct = tc.get_sint_canon_type()
            assert ct_left.is_pointer()
            assert ct_right.is_pointer()
        else:
            ct = ct_left
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprPointer):
        ct = _TypifyExprOrType(node.expr1, tc, target_type, pm)
        _TypifyExprOrType(node.expr2, tc, tc.get_uint_canon_type(), pm)
        if not isinstance(node.expr_bound_or_undef, cwast.ValUndef):
            _TypifyExprOrType(
                node.expr_bound_or_undef, tc, tc.get_uint_canon_type(), pm)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprUnionTag):
        ct = _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        assert ct.is_tagged_union()
        return AnnotateNodeType(node, tc.get_typeid_canon_type())
    elif isinstance(node, cwast.ExprFront):
        ct = _TypifyExprOrType(
            node.container, tc, cwast.NO_TYPE, pm)
        if not ct.is_span() and not ct.is_vec():
            cwast.CompilerError(
                node.x_srcloc, "expected container in front expression")
        mut = node.mut or (node.preserve_mut and ct.is_span() and ct.mut)
        p_type = tc.InsertPtrType(mut, ct.underlying_type())
        return AnnotateNodeType(node, p_type)
    elif isinstance(node, cwast.Expr3):
        _TypifyExprOrType(node.cond, tc, tc.get_bool_canon_type(), pm)
        ct = _TypifyExprOrType(node.expr_t, tc, target_type, pm)
        _TypifyExprOrType(node.expr_f, tc, ct, pm)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprStmt):
        _TypifyStmtSeq(node.body, tc, target_type, pm)
        if target_type == cwast.NO_TYPE:
            target_type = _GetExprStmtType(node)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ExprCall):
        return _TypifyExprCall(node, tc, target_type, pm)
    elif isinstance(node, (cwast.ExprAs, cwast.ExprNarrow, cwast.ExprBitCast)):
        ct = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprWrap):
        ct = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        assert ct.is_enum() or ct.is_wrapped()
        expr_ct = ct.underlying_type()
        _TypifyExprOrType(node.expr, tc, expr_ct, pm)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprUnwrap):
        ct = _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        if ct.is_wrapped():
            return AnnotateNodeType(node, ct.underlying_type())
        elif ct.is_enum():
            return AnnotateNodeType(node, ct.underlying_type())
        else:
            assert False
    elif isinstance(node, cwast.ExprIs):
        _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.get_bool_canon_type())
    elif isinstance(node, cwast.ExprLen):
        _TypifyExprOrType(node.container, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprAddrOf):
        cstr_expr = _TypifyExprOrType(
            node.expr_lhs, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.InsertPtrType(node.mut, cstr_expr))
    elif isinstance(node, cwast.ExprOffsetof):
        ct = _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        field_node = ct.lookup_rec_field(node.field.GetBaseNameStrict())
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateFieldWithTypeAndSymbol(node.field, field_node)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprSizeof):
        _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprUnionUntagged):
        ct = _TypifyExprOrType(node.expr, tc, cwast.NO_TYPE, pm)
        assert ct.is_tagged_union()
        return AnnotateNodeType(node, tc.InsertUnionType(True, ct.children))
    elif isinstance(node, cwast.ExprTypeId):
        _TypifyExprOrType(node.type, tc, cwast.NO_TYPE, pm)
        return AnnotateNodeType(node, tc.get_typeid_canon_type())
    elif isinstance(node, cwast.ExprParen):
        ct = _TypifyExprOrType(node.expr, tc, target_type, pm)
        return AnnotateNodeType(node, ct)
    else:
        assert False, f"unexpected node {node}"


def _CheckTypeIs(node, expected: cwast.CanonType):
    actual = node.x_type
    if actual is not expected:
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: not the same actual: {actual}  original={actual.original_type} expected: {expected}")


def _CheckValUndefOrTypeIsUint(node):
    if not isinstance(node, cwast.ValUndef):
        ct = node.x_type
        if not ct.is_base_type() or not ct.base_type_kind.IsUint():
            cwast.CompilerError(node.x_srcloc,
                                f"{node}: uint expected: {ct}")


def _CheckUnderlyingTypeIs(node, expected: cwast.CanonType):
    actual = node.x_type.underlying_type()
    if actual != expected:
        cwast.CompilerError(node.x_srcloc,
                            f"{node}: unerlying types not the same actual: {actual} expected: {expected}")


def _CheckTypeKind(node, kind):
    assert node.x_type.node is kind, f"Expect {kind} got {node.x_type.node}"


def _CheckExpr2TypesArithmetic(result_type: cwast.CanonType, op1, op2):
    assert result_type.is_base_type(), f"{result_type}"
    _CheckTypeIs(op1, result_type)
    _CheckTypeIs(op2, result_type)


def _CheckExpr2Types(node, op1, op2, kind: cwast.BINARY_EXPR_KIND,
                     tc: type_corpus.TypeCorpus):
    if kind.IsArithmetic():
        _CheckExpr2TypesArithmetic(node.x_type, op1, op2)
    elif kind.IsComparison():
        _CheckTypeIs(node, tc.get_bool_canon_type())
        if kind in (cwast.BINARY_EXPR_KIND.EQ, cwast.BINARY_EXPR_KIND.NE):
            if not type_corpus.IsCompatibleTypeForEq(op1.x_type, op2.x_type):
                cwast.CompilerError(op1.x_srcloc,
                                    f"incompatible type for equality testing")
        else:
            if not type_corpus.IsCompatibleTypeForCmp(op1.x_type, op2.x_type):
                cwast.CompilerError(op1.x_srcloc,
                                    f"incompatible type for comparison")
    elif kind.IsShortCircuit():
        ct_bool = tc.get_bool_canon_type()
        _CheckTypeIs(op1, ct_bool)
        _CheckTypeIs(op2, ct_bool)
        _CheckTypeIs(node, ct_bool)
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        # note: we ignore mutability
        _CheckTypeKind(op1, cwast.TypePtr)
        _CheckTypeIs(node, tc.get_sint_canon_type())
        _CheckTypeKind(op2, cwast.TypePtr)
        if op1.x_type.underlying_type() != op2.x_type.underlying_type():
            cwast.CompilerError(op1.x_srcloc, "invalid ops to PDELTA")
    else:
        assert False, f"{kind}"


def _CheckValCompound(node: cwast.ValCompound):
    ct = node.type_or_auto.x_type
    if ct.is_vec():
        ct_underlying = node.type_or_auto.x_type.underlying_type()
        for point in node.inits:
            _CheckTypeIs(point, ct_underlying)
            _CheckValUndefOrTypeIsUint(point.point_or_undef)
    else:
        assert ct.is_rec()
        for field, point in symbolize.IterateValRec(node.inits, ct):
            if point:
                _CheckTypeIs(point, field.x_type)
                if not isinstance(point.point_or_undef, cwast.ValUndef):
                    assert point.point_or_undef.x_symbol == field


def _CheckExpr3(node: cwast.Expr3, tc: type_corpus.TypeCorpus):
    ct = node.x_type
    _CheckTypeIs(node.expr_t, ct)
    _CheckTypeIs(node.expr_f, ct)
    _CheckTypeIs(node.cond, tc.get_bool_canon_type())


def _CheckExprDeref(node: cwast.ExprDeref, _):
    _CheckTypeKind(node.expr, cwast.TypePtr)
    _CheckTypeIs(node, node.expr.x_type.underlying_type())


def _CheckExprPointer(node: cwast.ExprPointer, _):
    _CheckValUndefOrTypeIsUint(node.expr_bound_or_undef)
    _CheckTypeKind(node.expr1, cwast.TypePtr)
    _CheckTypeIs(node.expr1, node.x_type)


def _CheckExprField(node: cwast.ExprField, _):
    _CheckTypeKind(node.container, cwast.DefRec)
    _CheckTypeIs(node, node.field.GetRecFieldRef().x_type)


def _CheckExprFront(node: cwast.ExprFront, _):
    _CheckTypeKind(node, cwast.TypePtr)
    container = node.container
    container_ct = container.x_type
    mut = node.x_type.mut
    if container_ct.is_span():
        if mut and not container_ct.mut:
            cwast.CompilerError(
                node.x_srcloc, f"span not mutable: {node} {container}")
    else:
        assert container_ct.is_vec()
        if mut and not type_corpus.IsProperLhs(container):
            cwast.CompilerError(
                node.x_srcloc, f"vec not mutable: {node} {container}")
        # TODO: check if address can be taken

    _CheckUnderlyingTypeIs(node, container_ct.underlying_type())


def _CheckExprWiden(node: cwast.ExprWiden, _):
    ct_src: cwast.CanonType = node.expr.x_type
    if ct_src.original_type:
        ct_src = ct_src.original_type
    ct_dst: cwast.CanonType = node.type.x_type
    _CheckTypeIs(node, ct_dst)
    if not type_corpus.IsSubtypeToUnionConversion(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad widen {ct_src} -> {ct_dst}: {node.expr}")


def _CheckExprNarrow(node: cwast.ExprNarrow, _):
    ct_src: cwast.CanonType = node.expr.x_type
    if ct_src.original_type is not None:
        ct_src = ct_src.original_type
    ct_dst: cwast.CanonType = node.type.x_type
    _CheckTypeIs(node, ct_dst)
    # note: inverse from widen
    if not type_corpus.IsSubtypeToUnionConversion(ct_dst, ct_src):
        cwast.CompilerError(
            node.x_srcloc,  f"bad narrow {ct_src} -> {ct_dst}: {node.expr}")


def _CheckExprNarrowUnchecked(node: cwast.ExprNarrow, _):
    # TODO: explain logic
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if ct_src.is_tagged_union() and not node.unchecked:
        cwast.CompilerError(
            node.x_srcloc,  f"narrow must be unchecked {ct_src.original_type} -> {ct_dst}: {node.expr}")


def _CheckExprAddrOf(node: cwast.ExprAddrOf, _):
    _CheckTypeKind(node, cwast.TypePtr)
    lhs = node.expr_lhs
    lhs_ct = node.expr_lhs.x_type
    if node.mut:
        if not type_corpus.IsProperLhs(lhs):
            cwast.CompilerError(node.x_srcloc, f"not mutable: {lhs}")
    if not AddressCanBeTaken(lhs):
        cwast.CompilerError(
            node.x_srcloc, f"address cannot be taken: {node} {lhs_ct}")
    _CheckUnderlyingTypeIs(node, lhs_ct)


def _CheckExprUnionUntagged(node: cwast.ExprUnionUntagged, _):
    assert node.x_type.is_untagged_union()
    assert node.expr.x_type.is_tagged_union(), f"{node.expr.x_type}"
    for c1, c2 in zip(node.x_type.union_member_types(), node.expr.x_type.union_member_types()):
        if c1 is not c2:
            cwast.CompilerError(node.x_srcloc,
                                f"{node}: union member mismatch actual: {c1} expected: {c1}")


def _CheckValNum(node: cwast.ValNum, _):
    ct = node.x_type
    if not ct.get_unwrapped().is_base_type():
        cwast.CompilerError(node.x_srcloc, f"type mismatch {node} vs {ct}")


def _CheckExprIndex(node: cwast.ExprIndex, _):
    c = node.container
    assert c.x_type.is_vec() or c.x_type.is_span()
    _CheckUnderlyingTypeIs(node.container, node.x_type)


def _CheckExprUnwrap(node: cwast.ExprUnwrap,  _):
    ct_node: cwast.CanonType = node.x_type
    ct_expr: cwast.CanonType = node.expr.x_type
    if ct_expr.is_wrapped() or ct_expr.is_enum():
        assert ct_expr.underlying_type() in (
            ct_node, ct_node.original_type), f"{ct_node} vs {ct_expr}"
    else:
        assert False


def _CheckDefFunTypeFun(node, _):
    _CheckTypeKind(node, cwast.TypeFun)
    ct = node.x_type
    _CheckTypeIs(node.result, ct.result_type())
    for a, b in zip(ct.parameter_types(), node.params):
        _CheckTypeIs(b.type, a)
    # We should also ensure three is a proper return but that requires dataflow


def _CheckValSpan(node: cwast.ValSpan, _):
    _CheckTypeKind(node, cwast.TypeSpan),
    _CheckUnderlyingTypeIs(node, node.pointer.x_type.underlying_type())


def _CheckExprUnionTag(node: cwast.ExprUnionTag, tc: type_corpus.TypeCorpus):
    _CheckTypeKind(node.expr, cwast.TypeUnion),
    assert not node.expr.x_type.untagged
    _CheckTypeIs(node, tc.get_typeid_canon_type())


def _CheckId(node: cwast.Id,  _):
    ct = node.x_type
    def_node = node.x_symbol
    if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
        _CheckTypeIs(node, def_node.type_or_auto.x_type)
    elif isinstance(def_node, (cwast.FunParam)):
        _CheckTypeIs(node, def_node.type.x_type)
    elif isinstance(def_node, (cwast.DefRec, cwast.DefType, cwast.DefFun,
                               cwast.DefEnum, cwast.EnumVal, cwast.RecField)):
        _CheckTypeIs(node, def_node.x_type)
    else:
        assert False, f"{def_node}"


def _CheckAstNode(node, _):
    assert node.x_type.ast_node is node


def _CheckStmtCompoundAssignment(node: cwast.StmtCompoundAssignment,  tc: type_corpus.TypeCorpus):
    if not type_corpus.IsProperLhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")
    assert node.binary_expr_kind.IsArithmetic(), f"{node.binary_expr_kind}"
    _CheckExpr2TypesArithmetic(node.lhs.x_type, node.lhs, node.expr_rhs)


def _CheckExprAs(node: cwast.ExprAs, _):
    ct_src = node.expr.x_type
    ct_dst = node.x_type
    if not type_corpus.IsCompatibleTypeForAs(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad cast {ct_src} -> {ct_dst}: {node.expr}")
    _CheckTypeIs(node, node.type.x_type)


def _CheckExprBitCast(node: cwast.ExprAs, _):
    ct_src = node.expr.x_type
    ct_dst = node.x_type
    if not type_corpus.IsCompatibleTypeForBitcast(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad cast {ct_src} -> {ct_dst}: {node.expr}")
    _CheckTypeIs(node, node.type.x_type)


def _CheckExprWrap(node: cwast.ExprWrap,  _):
    ct_dst: cwast.CanonType = node.type.x_type
    _CheckTypeIs(node, ct_dst)
    ct_target = ct_dst.underlying_type()
    ct_src = node.expr.x_type

    if ct_target is ct_src:
        return
    if ct_dst.is_wrapped() and type_corpus.IsDropMutConversion(ct_src, ct_target):
        return

    cwast.CompilerError(node.expr.x_srcloc,
                        f"not the same actual: {ct_src} expected: {ct_dst}")


def _CheckNothing(_, _2):
    pass


VERIFIERS_COMMON = {
    cwast.ExprIs: lambda n, tc: _CheckTypeIs(n, tc.get_bool_canon_type()),
    #
    cwast.ExprOffsetof: lambda n, tc: _CheckTypeIs(n, tc.get_uint_canon_type()),
    cwast.ExprSizeof: lambda n, tc: _CheckTypeIs(n, tc.get_uint_canon_type()),
    cwast.ExprLen: lambda n, tc: _CheckTypeIs(n, tc.get_uint_canon_type()),
    #
    cwast.StmtIf: lambda n, tc:   _CheckTypeIs(n.cond, tc.get_bool_canon_type()),
    cwast.Case: lambda n, tc:   _CheckTypeIs(n.cond, tc.get_bool_canon_type()),
    cwast.StmtStaticAssert: lambda n, tc:   _CheckTypeIs(n.cond, tc.get_bool_canon_type()),
    #
    cwast.ValVoid: lambda n, tc: _CheckTypeIs(n, tc.get_void_canon_type()),
    #
    cwast.ExprTypeId: lambda n, tc: _CheckTypeIs(n, tc.get_typeid_canon_type()),
    #
    cwast.Expr1: lambda n, tc: _CheckTypeIs(n, n.expr.x_type),

    cwast.TypeOf: lambda n, tc: _CheckTypeIs(n, n.expr.x_type),
    cwast.ExprParen: lambda n, tc: _CheckTypeIs(n, n.expr.x_type),
    cwast.FunParam: _CheckNothing,
    # this needs more work because we do not properly update the type
    # when rewriting complex function args
    # cwast.FunParam: lambda n, tc: _CheckTypeIs(n, n.type.x_type),
    #
    cwast.TypeBase: lambda n, tc: _CheckTypeKind(n, cwast.TypeBase),
    cwast.TypeSpan: lambda n, tc: _CheckTypeKind(n, cwast.TypeSpan),
    cwast.TypeVec: lambda n, tc: _CheckTypeKind(n, cwast.TypeVec),
    cwast.TypePtr: lambda n, tc: _CheckTypeKind(n, cwast.TypePtr),
    cwast.TypeUnion: lambda n, tc: _CheckTypeKind(n, cwast.TypeUnion),
    # TODO: check underlying
    cwast.ValString: lambda n, tc: _CheckTypeKind(n, cwast.TypeVec),
    cwast.ValSpan: _CheckValSpan,
    #
    cwast.ExprUnionTag: _CheckExprUnionTag,
    cwast.ExprDeref: _CheckExprDeref,

    cwast.Expr3: _CheckExpr3,
    cwast.Id: _CheckId,
    cwast.Expr2: lambda n, tc:  _CheckExpr2Types(n,  n.expr1,
                                                 n.expr2, n.binary_expr_kind, tc),
    cwast.ExprField: _CheckExprField,
    cwast.ExprPointer: _CheckExprPointer,
    cwast.DefType: lambda n, tc: _CheckTypeKind(n, cwast.DefType) if n.wrapped else
    _CheckTypeIs(n.type, n.x_type),
    # TODO: need to use original types if available
    cwast.ExprAs: _CheckExprAs,
    cwast.ExprBitCast: _CheckExprBitCast,
    cwast.StmtCompoundAssignment: _CheckStmtCompoundAssignment,
    cwast.ExprIndex: _CheckExprIndex,
    cwast.ExprFront: _CheckExprFront,
    cwast.ExprAddrOf: _CheckExprAddrOf,
    cwast.ExprWiden: _CheckExprWiden,
    cwast.ExprUnionUntagged: _CheckExprUnionUntagged,
    cwast.ExprUnwrap: _CheckExprUnwrap,
    cwast.ExprWrap: _CheckExprWrap,

    cwast.ValNum: _CheckValNum,
    cwast.EnumVal: lambda n, tc: _CheckTypeKind(n, cwast.DefEnum),
    cwast.DefRec: _CheckAstNode,
    cwast.DefEnum: _CheckAstNode,
    cwast.RecField: lambda n, tc:  _CheckTypeIs(n.type, n.x_type),
    cwast.ValCompound: lambda n, tc: _CheckValCompound(n),
    cwast.TypeFun: _CheckDefFunTypeFun,
    cwast.DefFun: _CheckDefFunTypeFun,
    #
    cwast.TypeAuto: _CheckNothing,
    cwast.ValAuto: _CheckNothing,
    cwast.ExprStmt: _CheckNothing,
    cwast.TypeUnionDelta:  _CheckNothing,
}


def _CheckTypeCompatibleWithOptionalStrict(src_node, dst_ct: cwast.CanonType, strict: bool):
    src_ct = src_node.x_type
    if src_ct == dst_ct:
        return
    if strict:
        if not type_corpus.IsDropMutConversion(src_ct, dst_ct):
            cwast.CompilerError(src_node.x_srcloc,
                                f"{src_node}: not the same actual: {src_ct} expected: {dst_ct}")
    else:
        mutable = src_ct.is_vec() and type_corpus.IsProperLhs(src_node)
        if not type_corpus.IsCompatibleType(src_ct, dst_ct, mutable):
            cwast.CompilerError(src_node.x_srcloc,
                                f"incompatible type for {src_node}: {src_ct} expected: {dst_ct}")


def _CheckValPoint(point: cwast.ValPoint, strict: bool):
    val = point.value_or_undef
    if not isinstance(val, cwast.ValUndef):
        _CheckTypeCompatibleWithOptionalStrict(val, point.x_type, strict)


def _CheckExprCall(node: cwast.ExprCall, strict: bool):
    fun_sig: cwast.CanonType = node.callee.x_type
    assert fun_sig.is_fun(), f"{fun_sig}"
    _CheckTypeIs(node, fun_sig.result_type())
    for p, a in zip(fun_sig.parameter_types(), node.args):
        _CheckTypeCompatibleWithOptionalStrict(a, p, strict)


def _CheckStmtAssignment(node: cwast.StmtAssignment, strict: bool):
    if not type_corpus.IsProperLhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")
    _CheckTypeCompatibleWithOptionalStrict(
        node.expr_rhs, node.lhs.x_type, strict)


def _CheckStmtReturn(node: cwast.StmtReturn, strict: bool):
    target = node.x_target
    if isinstance(target, cwast.DefFun):
        expected = target.result.x_type
    else:
        assert isinstance(target, cwast.ExprStmt)
        expected = target.x_type
    _CheckTypeCompatibleWithOptionalStrict(node.expr_ret, expected, strict)


def _CheckDefVarDefGlobal(node, strict: bool):
    initial = node.initial_or_undef_or_auto
    ct = node.type_or_auto.x_type
    if not isinstance(initial, cwast.ValUndef):
        _CheckTypeCompatibleWithOptionalStrict(initial, ct, strict)
    _CheckTypeIs(node, ct)


VERIFIERS_WEAK = VERIFIERS_COMMON | {
    cwast.ExprNarrow: _CheckExprNarrow,
    # These reflect all the node where implicit conversion beyond the
    # drop of "mut" may occur. This includes:
    # *
    cwast.ExprCall: lambda n, tc: _CheckExprCall(n, False),
    cwast.StmtAssignment: lambda n, tc:  _CheckStmtAssignment(n, False),
    cwast.StmtReturn: lambda n, tc: _CheckStmtReturn(n, False),
    cwast.DefGlobal: lambda n, tc: _CheckDefVarDefGlobal(n, False),
    cwast.DefVar: lambda n, tc: _CheckDefVarDefGlobal(n, False),
    cwast.ValPoint: lambda n, tc: _CheckValPoint(n, False),
}

VERIFIERS_STRICT = VERIFIERS_COMMON | {
    cwast.ExprNarrow: _CheckExprNarrowUnchecked,
    cwast.ExprCall: lambda n, tc: _CheckExprCall(n, True),
    cwast.StmtAssignment: lambda n, tc:  _CheckStmtAssignment(n, True),
    cwast.StmtReturn: lambda n, tc: _CheckStmtReturn(n, True),
    cwast.DefGlobal: lambda n, tc: _CheckDefVarDefGlobal(n, True),
    cwast.DefVar: lambda n, tc: _CheckDefVarDefGlobal(n, True),
    cwast.ValPoint: lambda n, tc: _CheckValPoint(n, True),
}


def VerifyTypesRecursively(node, tc: type_corpus.TypeCorpus, verifier_table):
    def visitor(node, parent):
        nonlocal verifier_table
        if cwast.NF.TOP_LEVEL in node.FLAGS:
            logger.info("TYPE-VERIFYING %s", node)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            ct: cwast.CanonType = node.x_type
            if ct is cwast.NO_TYPE:
                assert isinstance(
                    node, (cwast.Id, cwast.ValAuto)), f"untype node {node}"
                assert isinstance(parent, cwast.ValPoint)
                assert parent.point == node, f"missing type for {
                    node} in {node.x_srcloc}"
            else:
                assert ct.name in tc.corpus, f"bad type annotation for {
                    node}: {node.x_type}"
                assert ct.replacement_type is None

                verifier_table[type(node)](node, tc)

        else:
            handler = verifier_table.get(type(node))
            if handler:
                handler(node, tc)

    cwast.VisitAstRecursivelyWithParentPost(node, visitor, None)


def AddTypesToAst(mod_topo_order: list[cwast.DefMod],
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

    logger.info("phase 2")
    # process types that have the module name in their canonical type name
    # We process them first while we know that module name.
    # We could just do the processing when we encounter them naturally
    # during processing or recursion but then we do not have access to the
    # module name.
    for mod in mod_topo_order:
        mod_name = str(mod.name)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefRec):
                ct = tc.InsertRecType(f"{mod_name}/{node.name}", node, process_children=False)
                AnnotateNodeType(node, ct)
            elif isinstance(node, cwast.DefEnum):
                ct = tc.InsertEnumType(f"{mod_name}/{node.name}", node)
                AnnotateNodeType(node, ct)
            elif isinstance(node, cwast.DefType) and node.wrapped:
                ct = tc.InsertWrappedTypePrep(f"{mod_name}/{node.name}")
                AnnotateNodeType(node, ct)

    logger.info("phase 2")
    # finish processing the types from phase 1
    # Now handle the child nodes which have become unvisible to the recursion
    # because parent has a type annotation
    poly_map = _PolyMap(tc)
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefRec):
                children = []
                for f in node.fields:
                    assert isinstance(f,  cwast.RecField)
                    ct = _TypifyExprOrType(f.type, tc, cwast.NO_TYPE, poly_map)
                    children.append(ct)
                    AnnotateNodeType(f, ct)
                # HACK: sinxe we did not process the children in pass 1
                node.x_type.children = children
            elif isinstance(node, cwast.DefEnum):
                ct = node.x_type
                bt = ct.underlying_type()
                for f in node.items:
                    assert isinstance(f,  cwast.EnumVal)
                    _TypifyExprOrType(f.value_or_auto, tc, bt, poly_map)
                    AnnotateNodeType(f, ct)
            elif isinstance(node, cwast.DefType):
                ct = _TypifyExprOrType(
                    node.type, tc, cwast.NO_TYPE, poly_map)
                if node.wrapped:
                    # note: node has been annotated above
                    assert node.x_type is not cwast.NO_TYPE
                    tc.InsertWrappedTypeFinalize(node.x_type, ct)
                else:
                    AnnotateNodeType(node, ct)

    logger.info("phase 3")
    # deal with remaining top level stuff - but not function bodies
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefEnum, cwast.DefRec, cwast.DefType, cwast.Import)):
                pass
            elif isinstance(node, cwast.StmtStaticAssert):
                _TypifyExprOrType(
                    node.cond, tc, tc.get_bool_canon_type(), poly_map)
            elif isinstance(node, cwast.DefGlobal):
                if node.x_type is cwast.NO_TYPE:
                    _TypifyDefGlobalOrDefVar(node, tc, poly_map)
            elif isinstance(node, cwast.DefFun):
                # note, this does not recurse into the function body
                if node.x_type is cwast.NO_TYPE:
                    _TypifyTypeFunOrDefFun(node, tc, poly_map)
                if node.poly:
                    ct = node.x_type
                    assert ct.node is cwast.TypeFun, f"{node} -> {ct.name}"
                    poly_map.Register(node)
            else:
                assert False, f"unexpected Node {node}"

    logger.info("phase 4")
    # now typify function bodies
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun) and not node.extern:
                for c in node.body:
                    _TypifyStmt(
                        c, tc, node.result.x_type, poly_map)

    # after this call, all invocations of InsertXXXType() will set thw AbiInfo
    # implicitly
    tc.SetAbiInfoForall()


def RemoveUselessCast(node, tc: type_corpus.TypeCorpus):
    def replacer(node, _parent):
        nonlocal tc
        if isinstance(node, cwast.ExprAs):
            if node.x_type is node.expr.x_type:
                return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)
############################################################
#
############################################################


def main(argv: list[str]):
    assert len(argv) == 1
    fn = argv[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    cwd = os.getcwd()
    main = str(pathlib.Path(fn).resolve())
    mp = mod_pool.ReadModulesRecursively(pathlib.Path(
        cwd) / "Lib", [main], add_builtin=fn != "Lib/builtin")
    for mod in mp.mods_in_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    macro.ExpandMacrosAndMacroLike(mp.mods_in_topo_order)
    symbolize.SetTargetFields(mp.mods_in_topo_order)
    symbolize.ResolveSymbolsInsideFunctions(
        mp.mods_in_topo_order, mp.builtin_symtab)
    for mod in mp.mods_in_topo_order:
        symbolize.VerifySymbols(mod)

    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    AddTypesToAst(mp.mods_in_topo_order, tc)
    for mod in mp.mods_in_topo_order:
        VerifyTypesRecursively(mod, tc, VERIFIERS_WEAK)

    for t, n in tc.corpus.items():
        logger.info("%s %s %d %d", t, n.register_types, n.size, n.alignment)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
