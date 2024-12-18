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
        return isinstance(s, cwast.DefGlobal) or isinstance(s, cwast.DefVar) and s.ref
    return False


def address_can_be_taken(node) -> bool:
    return (is_ref_def(node) or
            isinstance(node, cwast.ExprField) or
            isinstance(node, cwast.ExprDeref) or
            isinstance(node, cwast.ExprIndex) and
            node.container.x_type.is_span() or
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


def _NumCleanupAndTypeExtraction(num: str) -> tuple[str, cwast.BASE_TYPE_KIND]:
    num = num.replace("_", "")
    suffix = ""
    if num[-4:] in ("uint", "sint"):
        suffix = num[-4:]
    elif num[-3:] in ("u16", "u32", "u64", "s16", "s32", "s64", "r32", "r64"):
        suffix = num[-3:]
    elif num[-2:] in ("u8", "s8"):
        suffix = num[-2:]
    else:
        return num, cwast.BASE_TYPE_KIND.INVALID
    return num[:-len(suffix)], cwast.BASE_TYPE_KIND[suffix.upper()]


def ParseNumRaw(num_val: cwast.ValNum, kind: cwast.BASE_TYPE_KIND) -> Tuple[Any,  cwast.BASE_TYPE_KIND]:
    num = num_val.number
    if num[0] == "'":
        if kind is cwast.BASE_TYPE_KIND.INVALID:
            cwast.CompilerError(
                num_val.x_srcloc, f"Number needs explicit type {num_val}")
        assert num[-1] == "'"
        if num[1] == "\\":
            if num[2] == "n":
                return ord('\n'), kind
            elif num[2] == "t":
                return ord('\t'), kind
            elif num[2] == "r":
                return ord('\r'), kind
            elif num[2] == "\\":
                return ord('\\'), kind
            assert False, f"unsupported escape sequence: [{num}]"

        else:
            return ord(num[1]), kind

    num, kind_explicit = _NumCleanupAndTypeExtraction(num)
    if kind_explicit != cwast.BASE_TYPE_KIND.INVALID:
        kind = kind_explicit

    if kind in cwast.BASE_TYPE_KIND_INT:
        return int(num, 0), kind
    elif kind in cwast.BASE_TYPE_KIND_REAL:
        if "0x" in num:
            return float.fromhex(num), kind
        return float(num), kind
    else:
        cwast.CompilerError(
            num_val.x_srcloc, f"cannot parse number: {num} {kind}")
        return (None, cwast.BASE_TYPE_KIND.INVALID)


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
        self._map: dict[Tuple[cwast.DefMod,
                              cwast.NAME, str], cwast.DefFun] = {}
        self._type_corpus = tc

    def Register(self, fun: cwast.DefFun):
        ct: cwast.CanonType = fun.x_type
        mod: cwast.DefMod = fun.x_import.x_module
        name = fun.name.GetSymbolNameWithoutQualifier()
        first_param_type = ct.children[0].name
        logger.info("Register polymorphic fun %s::%s: %s",
                    mod.x_modname, name, first_param_type)
        # TODO: Should this work with parameterized volumes
        key = (mod, name, first_param_type)
        assert key not in self._map, f"duplicate poly def {fun.x_srcloc}"
        self._map[key] = fun

    def Resolve(self, callee: cwast.Id, first_param_type: cwast.CanonType) -> cwast.DefFun:
        # TODO: why are we not using the mod_name here?
        fun_name = callee.base_name
        type_name = first_param_type.name
        logger.info("Resolving polymorphic fun %s: %s", fun_name, type_name)
        callee_mod: cwast.DefMod = callee.x_import.x_module
        out = self._map.get((callee_mod, fun_name, type_name))
        if out:
            return out
        # TODO: why do we need this - seems unsafe:
        if first_param_type.is_vec():
            span_type = self._type_corpus. insert_span_type(
                False, first_param_type.underlying_array_type())
            type_name = span_type.name

            out = self._map.get((callee_mod, fun_name, type_name))
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
    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"node not meant for type annotation: {
        node}"
    assert ct, f"No valid type for {node}"
    node.x_type = ct
    return ct


def AnnotateNodeType(node, ct: cwast.CanonType):
    logger.info("TYPE of %s: %s", node, ct.name)
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

    def visitor(node, _):
        nonlocal result, root
        if node != root and isinstance(node, cwast.ExprStmt):
            return VerifyTypesRecursively
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
                             ctx: _TypeContext):
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
            _TypifyNodeRecursively(initial, tc, ct, ctx)
    AnnotateNodeType(node, ct)


def _TypifyTypeFunOrDefFun(node, tc: type_corpus.TypeCorpus,
                           ctx: _TypeContext):
    params = []
    for p in node.params:
        assert isinstance(p, cwast.FunParam)
        ct = _TypifyNodeRecursively(p.type, tc, cwast.NO_TYPE, ctx)
        AnnotateNodeType(p, ct)
        params.append(p.type.x_type)
    result = _TypifyNodeRecursively(
        node.result, tc, cwast.NO_TYPE, ctx)
    ct = tc.insert_fun_type(params, result)
    return AnnotateNodeType(node, ct)


def _TypifyUnevaluableNodeRecursively(node, tc: type_corpus.TypeCorpus,
                                      target_type: cwast.CanonType,
                                      ctx: _TypeContext) -> cwast.CanonType:

    if isinstance(node, cwast.TypeAuto):
        assert target_type is not cwast.NO_TYPE, f"cannot typify auto in {node.x_srcloc}"
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.TypeBase):
        return AnnotateNodeType(node, tc.get_base_canon_type(node.base_type_kind))
    elif isinstance(node, cwast.TypePtr):
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_ptr_type(node.mut, t))
    elif isinstance(node, cwast.TypeSpan):
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_span_type(node.mut, t))
    elif isinstance(node, cwast.TypeFun):
        return _TypifyTypeFunOrDefFun(node, tc, ctx)
    elif isinstance(node, cwast.TypeVec):
        # note this is the only place where we need a comptime eval for types
        t = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.size, tc, uint_type, ctx)
        dim = _ComputeArrayLength(node.size, uint_type.base_type_kind)
        return AnnotateNodeType(node, tc.insert_array_type(dim, t))
    elif isinstance(node, cwast.TypeUnion):
        # this is tricky code to ensure that children of TypeUnion
        # are not TypeUnion themselves on the canonical side
        pieces = [_TypifyNodeRecursively(
            f, tc, cwast.NO_TYPE, ctx) for f in node.types]
        return AnnotateNodeType(node, tc.insert_union_type(pieces, node.untagged))
    elif isinstance(node, cwast.TypeUnionDelta):
        minuend = _TypifyNodeRecursively(
            node.type, tc, cwast.NO_TYPE, ctx)
        subtrahend = _TypifyNodeRecursively(
            node.subtrahend, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.insert_union_complement(minuend, subtrahend))
    elif isinstance(node, cwast.TypeOf):
        ct = _TypifyNodeRecursively(node.expr, tc,  cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    else:
        assert False, f"{node}"
        return cwast.NO_TYPE


def _TypifyTopLevel(node, tc: type_corpus.TypeCorpus,
                    ctx: _TypeContext):
    if isinstance(node, cwast.Import):
        return
    elif isinstance(node, cwast.StmtStaticAssert):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        return

    if node.x_type != cwast.NO_TYPE:
        return

    if isinstance(node, cwast.DefGlobal):
        _TypifyDefGlobalOrDefVar(node, tc, ctx)
    elif isinstance(node, cwast.DefType):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        if node.wrapped:
            ct = tc.insert_wrapped_type(ct)
        AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.DefFun):
        # note, this does not recurse into the function body
        _TypifyTypeFunOrDefFun(node, tc, ctx)
    elif isinstance(node, cwast.DefEnum):
        ct = tc.insert_enum_type(f"{ctx.mod_name}/{node.name}", node)
        for f in node.items:
            _TypifyNodeRecursively(f, tc, ct, ctx)
        AnnotateNodeType(node, ct)

    else:
        assert False, f"unexpected Node {node}"


def _TypifyStmtSeq(body: list[Any], tc: type_corpus.TypeCorpus, tt: cwast.CanonType, ctx: _TypeContext):
    for c in body:
        _TypifyStatement(c, tc, tt, ctx)


def _TypifyStatement(node, tc: type_corpus.TypeCorpus,
                     tt: cwast.CanonType,
                     ctx: _TypeContext):
    # tt is used by cwast.StmtReturn
    if isinstance(node, cwast.StmtReturn):
        _TypifyNodeRecursively(node.expr_ret, tc, tt, ctx)
    elif isinstance(node, cwast.StmtIf):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        _TypifyStmtSeq(node.body_f, tc, tt, ctx)
        _TypifyStmtSeq(node.body_t, tc, tt, ctx)

    elif isinstance(node, cwast.Case):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        _TypifyStmtSeq(node.body, tc, tt, ctx)
    elif isinstance(node, cwast.StmtCond):
        _TypifyStmtSeq(node.cases, tc, tt, ctx)
    elif isinstance(node, cwast.StmtBlock):
        _TypifyStmtSeq(node.body, tc, tt, ctx)
    elif isinstance(node, (cwast.StmtBreak, cwast.StmtContinue,
                           cwast.StmtTrap)):
        pass
    elif isinstance(node, cwast.StmtAssignment):
        ct = _TypifyNodeRecursively(node.lhs, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, ct, ctx)
    elif isinstance(node, cwast.StmtCompoundAssignment):
        ct = _TypifyNodeRecursively(node.lhs, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr_rhs, tc, ct, ctx)
    elif isinstance(node, cwast.DefVar):
        _TypifyDefGlobalOrDefVar(node, tc, ctx)
    elif isinstance(node, cwast.StmtExpr):
        _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
    elif isinstance(node, cwast.StmtDefer):
        _TypifyStmtSeq(node.body, tc, tt, ctx)
    else:
        assert False, f"unexpected node: {node}"


def _TypifyValCompound(node: cwast.ValCompound, tc: type_corpus.TypeCorpus,
                       target_type: cwast.CanonType,
                       ctx: _TypeContext) -> cwast.CanonType:
    ct = _TypifyNodeRecursively(node.type_or_auto, tc, target_type, ctx)
    if ct.is_vec():
        for point in node.inits:
            assert isinstance(point, cwast.ValPoint)
            val = point.value_or_undef
            if not isinstance(val, cwast.ValUndef):
                _TypifyNodeRecursively(
                    val, tc, ct.underlying_array_type(), ctx)
            AnnotateNodeType(point, ct.underlying_array_type())

            index = point.point
            uint_type = tc.get_uint_canon_type()
            if isinstance(index, cwast.ValAuto):
                AnnotateNodeType(index, uint_type)
            else:
                _TypifyNodeRecursively(index, tc, uint_type, ctx)
    else:
        assert ct.is_rec(), f"expected rec got {ct} in {node.x_srcloc}"
        for field, point in symbolize.IterateValRec(node.inits, ct):
            if point:
                field_ct = field.x_type
                AnnotateNodeType(point, field_ct)
                if isinstance(point.point, cwast.Id):
                    # an over-eager symbolizer may have found
                    # a variable name the matches the field name
                    # an created a link between the two.
                    # we overwrite it here again
                    point.point.x_symbol = cwast.INVALID_SYMBOL
                    AnnotateFieldWithTypeAndSymbol(point.point, field)
                if not isinstance(point.value_or_undef, cwast.ValUndef):
                    _TypifyNodeRecursively(
                        point.value_or_undef, tc, field_ct, ctx)

    return AnnotateNodeType(node, ct)


def _TypifyId(node: cwast.Id, tc: type_corpus.TypeCorpus,
              target_type: cwast.CanonType,
              ctx: _TypeContext) -> cwast.CanonType:
    # this case is why we need the sym_tab
    def_node = node.x_symbol
    assert cwast.NF.LOCAL_SYM_DEF in def_node.FLAGS or cwast.NF.GLOBAL_SYM_DEF in def_node.FLAGS
    ct = def_node.x_type
    if isinstance(def_node, cwast.DefVar):
        if ct == cwast.NO_TYPE:
            _TypifyStatement(def_node, tc, target_type, ctx)
            ct = def_node.x_type
    elif isinstance(def_node, (cwast.DefType, cwast.DefFun, cwast.DefEnum, cwast.DefGlobal)):
        if ct == cwast.NO_TYPE:
            _TypifyTopLevel(def_node, tc, ctx)
            ct = def_node.x_type
    elif isinstance(def_node, cwast.EnumVal):
        # TODO: this assert can happen if we use an enum value at the top level
        #       before the Enum has been defined.
        #       What needs to happen is to typify the whole Enum which would require a
        #       some back reference from the EnumVal to the DefEnum
        assert ct != cwast.NO_TYPE
    else:
        assert isinstance(def_node, (cwast.FunParam,  cwast.DefRec))
    assert ct != cwast.NO_TYPE
    return AnnotateNodeType(node, ct)

def _IsPolymorphicCall(call: cwast.ExprCall) -> bool:
    if not isinstance(call.callee, cwast.Id):
        return False
    def_sym = call.callee.x_symbol
    if not isinstance(def_sym, cwast.DefFun):
        return False
    return def_sym.poly

def _TypifyNodeRecursively(node, tc: type_corpus.TypeCorpus,
                           target_type: cwast.CanonType,
                           ctx: _TypeContext) -> cwast.CanonType:
    """Do not call this outside of functions"""
    extra = "" if target_type == cwast.NO_TYPE else f"[{target_type.name}]"
    logger.debug("TYPIFYING%s %s", extra, node)

    assert cwast.NF.TYPE_ANNOTATED in node.FLAGS, f"unexpected node {node}"

    ct = node.x_type
    if ct is not cwast.NO_TYPE:
        # has been typified already
        return ct

    # we break out a few more cases to make if statement below more manageable
    if cwast.NF.VALUE_ANNOTATED not in node.FLAGS:
        return _TypifyUnevaluableNodeRecursively(node, tc, target_type, ctx)

    if isinstance(node, cwast.Id):
        return _TypifyId(node, tc, target_type, ctx)
    elif isinstance(node, cwast.EnumVal):
        if isinstance(node.value_or_auto, cwast.ValAuto):
            AnnotateNodeType(node.value_or_auto, target_type)
        else:
            ct = _TypifyNodeRecursively(
                node.value_or_auto, tc, target_type, ctx)
        return AnnotateNodeType(node, target_type)
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
    elif isinstance(node, cwast.ValAuto):
        assert target_type is not cwast.NO_TYPE
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ValCompound):
        return _TypifyValCompound(node, tc, target_type, ctx)
    elif isinstance(node, cwast.ValString):
        dim = ComputeStringSize(node.strkind, node.string)
        ct = tc.insert_array_type(
            dim, tc.get_base_canon_type(cwast.BASE_TYPE_KIND.U8))
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprIndex):
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr_index, tc, uint_type, ctx)
        ct = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        if not ct.is_vec_or_span():
            cwast.CompilerError(
                node.container.x_srcloc, f"expected array or span for {node} but got {ct}")
        return AnnotateNodeType(node, ct.contained_type())
    elif isinstance(node, cwast.ExprField):
        ct = _TypifyNodeRecursively(node.container, tc, target_type, ctx)
        if not ct.is_rec():
            cwast.CompilerError(
                node.x_srcloc, f"container type is not record {node.container}")
        field_node = tc.lookup_rec_field(ct, node.field.GetBaseNameStrict())
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateFieldWithTypeAndSymbol(node.field, field_node)
        return AnnotateNodeType(node, field_node.x_type)
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
        if node.binary_expr_kind in cwast.BINOP_BOOL:
            # for comparisons the type of the expressions has nothing to do with
            # the type of the operands
            # TODO introduce BINOP_OPS_HAVE_SAME_TYPE_AS_EXPRESSION
            target_type = cwast.NO_TYPE
        ct = _TypifyNodeRecursively(
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
            elif ct.is_span():
                assert ct2.is_span()
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
        if not ct.is_span() and not ct.is_vec():
            cwast.CompilerError(
                node.x_srcloc, "expected container in front expression")
        mut = node.mut
        if node.preserve_mut and ct.is_span() and ct.mut:
            mut = True
        p_type = tc.insert_ptr_type(mut, ct.underlying_vec_or_span_type())
        return AnnotateNodeType(node, p_type)
    elif isinstance(node, cwast.Expr3):
        _TypifyNodeRecursively(node.cond, tc, tc.get_bool_canon_type(), ctx)
        ct = _TypifyNodeRecursively(node.expr_t, tc, target_type, ctx)
        _TypifyNodeRecursively(node.expr_f, tc, ct, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprStmt):
        _TypifyStmtSeq(node.body, tc, target_type, ctx)
        if target_type == cwast.NO_TYPE:
            target_type = _GetExprStmtType(node)
        return AnnotateNodeType(node, target_type)
    elif isinstance(node, cwast.ExprCall):
        callee = node.callee
        if _IsPolymorphicCall(node):
            assert len(node.args) > 0
            assert isinstance(callee, cwast.Id)
            t = _TypifyNodeRecursively(
                node.args[0], tc, cwast.NO_TYPE, ctx)
            called_fun = ctx.poly_map.Resolve(callee, t)
            symbolize.UpdateNodeSymbolForPolyCall(callee, called_fun)
            AnnotateNodeType(callee, called_fun.x_type)
            ct_callee: cwast.CanonType = called_fun.x_type
            assert ct_callee.is_fun(), f"{ct}"
            params_ct = ct_callee.parameter_types()
            if len(params_ct) != len(node.args):
                cwast.CompilerError(
                    node.x_srcloc, f"parameter size mismatch in call to {callee} - macro issues?")
            # we already process the first arg
            for p, a in zip(params_ct[1:], node.args[1:]):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct_callee.result_type())
        else:
            ct = _TypifyNodeRecursively(callee, tc, cwast.NO_TYPE, ctx)
            params_ct = ct.parameter_types()
            if len(params_ct) != len(node.args):
                cwast.CompilerError(node.x_srcloc,
                                    f"args number mismatch for call to {callee}: {len(params_ct)} vs {len(node.args)}")
            for p, a in zip(params_ct, node.args):
                _TypifyNodeRecursively(a, tc, p, ctx)
            return AnnotateNodeType(node, ct.result_type())

    elif isinstance(node, (cwast.ExprAs, cwast.ExprNarrow, cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, ct)
    elif isinstance(node, cwast.ExprWrap):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        assert ct.is_wrapped() or ct.is_enum(), f"Expected wrapped type in {
            node} {node.x_srcloc}"
        if ct.is_enum():
            expr_ct = tc.get_base_canon_type(ct.base_type_kind)
        else:
            expr_ct = ct.underlying_wrapped_type()
        _TypifyNodeRecursively(node.expr, tc, expr_ct, ctx)
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
        mut = node.mut
        return AnnotateNodeType(node, tc.insert_ptr_type(mut, cstr_expr))
    elif isinstance(node, cwast.ExprOffsetof):
        ct = _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        field_node = tc.lookup_rec_field(ct, node.field.GetBaseNameStrict())
        if not field_node:
            cwast.CompilerError(
                node.x_srcloc, f"unknown record field {node.field}")
        AnnotateFieldWithTypeAndSymbol(node.field, field_node)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprSizeof):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.get_uint_canon_type())
    elif isinstance(node, cwast.ExprUnionUntagged):
        ct = _TypifyNodeRecursively(node.expr, tc, cwast.NO_TYPE, ctx)
        assert ct.is_tagged_union()
        return AnnotateNodeType(node, tc.insert_union_type(ct.children, True))
    elif isinstance(node, cwast.ExprTypeId):
        _TypifyNodeRecursively(node.type, tc, cwast.NO_TYPE, ctx)
        return AnnotateNodeType(node, tc.get_typeid_canon_type())
    elif isinstance(node, cwast.ValSpan):
        uint_type = tc.get_uint_canon_type()
        _TypifyNodeRecursively(node.expr_size, tc, uint_type, ctx)
        if isinstance(target_type, cwast.TypeSpan):
            ptr_type = tc.insert_ptr_type(target_type.mut, target_type.type)
            _TypifyNodeRecursively(node.pointer, tc, ptr_type, ctx)
            return AnnotateNodeType(node, target_type)
        else:
            ptr_type = _TypifyNodeRecursively(
                node.pointer, tc, cwast.NO_TYPE, ctx)
            return AnnotateNodeType(
                node, tc.insert_span_type(ptr_type.mut, ptr_type.underlying_pointer_type()))
    elif isinstance(node, cwast.ExprParen):
        ct = _TypifyNodeRecursively(node.expr, tc, target_type, ctx)
        return AnnotateNodeType(node, ct)
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
        if (actual.node in (cwast.TypePtr, cwast.TypeSpan, cwast.TypeVec, cwast.TypePtr) and
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
                            f"{node}:\n incompatible actual: {actual} expected: {expected}")


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

        elif op1_type.is_span():
            assert op2_type.is_span() and result_type == op1_type
            _CheckTypeSame(node, op1_type.underlying_span_type(),
                           op2_type.underlying_span_type())
        else:
            assert False
    else:
        assert op1_type.is_base_type(), f"{node}"
        _CheckTypeSame(node, op1_type, result_type)
        _CheckTypeSame(node, op2_type, result_type)


def _CheckValVec(node: cwast.ValCompound, ct: cwast.CanonType):
    for point in node.inits:
        assert isinstance(point, cwast.ValPoint), f"{point}"
        if not isinstance(point.point, cwast.ValAuto):
            assert point.point.x_type.is_int()
        # TODO: this should be  _CheckTypeCompatibleForAssignment
        _CheckTypeSame(point,  point.x_type, ct)


def _CheckValCompound(node: cwast.ValCompound, _tc: type_corpus.TypeCorpus):
    ct: cwast.CanonType = node.type_or_auto.x_type
    if ct.is_vec():
        _CheckValVec(node, ct.underlying_array_type())
    else:
        assert ct.is_rec()
        for field, point in symbolize.IterateValRec(node.inits, ct):
            if point:
                _CheckTypeSame(point, field.x_type, point.x_type)
                if not isinstance(point.value_or_undef, cwast.ValUndef):
                    _CheckTypeCompatibleForAssignment(
                        point, point.value_or_undef.x_type, point.x_type, type_corpus.is_mutable_array(
                            point.value_or_undef),
                        point.value_or_undef.x_srcloc)


def CheckValCompoundStrict(node: cwast.ValCompound, _tc: type_corpus.TypeCorpus):
    ct: cwast.CanonType = node.type_or_auto.x_type
    if ct.is_vec():
        _CheckValVec(node, ct.underlying_array_type())
    else:
        assert ct.is_rec()
        for field, point in symbolize.IterateValRec(node.inits, ct):
            if point:
                _CheckTypeSame(point, field.x_type, point.x_type)
                if not isinstance(point.value_or_undef, cwast.ValUndef):
                    _CheckTypeSameExceptMut(
                        point, point.value_or_undef.x_type, point.x_type)


def CheckExpr3(node: cwast.Expr3, _tc: type_corpus.TypeCorpus):
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
    ct: cwast.CanonType = node.expr1.x_type
    if not ct.is_pointer():
        cwast.CompilerError(
            node.x_srcloc, f"expected pointer got {node.expr1.x_type}")
    # _CheckTypeUint(node, tc, node.expr2.x_type)
    _CheckTypeSame(node, node.expr1.x_type, node.x_type)


def CheckExprField(node: cwast.ExprField, _):
    recfield = node.field.GetRecFieldRef()
    # _CheckTypeSame(node,  node.x_field.x_type, ct)
    assert node.x_type is recfield.x_type, f"field node {
        node.container.x_type} type mismatch: {node.x_type} {recfield.x_type}"


def CheckExprFront(node: cwast.ExprFront, _):

    assert node.container.x_type.is_vec_or_span(
    ), f"unpected front expr {node.container.x_type}"
    mut = node.x_type.mut
    if mut:
        if not type_corpus.is_mutable_array_or_span(node.container):
            cwast.CompilerError(
                node.x_srcloc, f"container not mutable: {node} {node.container}")

    if node.container.x_type.is_vec():
        # TODO: check if address can be taken
        pass

    assert node.x_type.is_pointer()
    _CheckTypeSame(node, node.x_type.underlying_pointer_type(),
                   node.container.x_type.underlying_vec_or_span_type())


def _CheckExprWiden(node: cwast.ExprWiden, _):
    ct_src: cwast.CanonType = node.expr.x_type
    if ct_src.original_type:
        ct_src = ct_src.original_type
    ct_dst: cwast.CanonType = node.type.x_type
    if not type_corpus.is_compatible_for_widen(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad widen {ct_src} -> {ct_dst}: {node.expr}")


def _CheckExprNarrow(node: cwast.ExprNarrow, _):
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if not type_corpus.is_compatible_for_narrow(ct_src, ct_dst, node.x_srcloc):
        cwast.CompilerError(
            node.x_srcloc,  f"bad narrow {ct_src.original_type} -> {ct_dst}: {node.expr}")


def _CheckExprNarrowUnchecked(node: cwast.ExprNarrow, _):
    ct_src: cwast.CanonType = node.expr.x_type
    ct_dst: cwast.CanonType = node.type.x_type
    if ct_src.is_tagged_union() and not node.unchecked:
        cwast.CompilerError(
            node.x_srcloc,  f"narrow must be unchecked {ct_src.original_type} -> {ct_dst}: {node.expr}")


def _CheckExprAddrOf(node: cwast.ExprAddrOf, _):
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


def _CheckExprUnionUntagged(node: cwast.ExprUnionUntagged, _):
    assert node.x_type.is_untagged_union()
    assert node.expr.x_type.is_tagged_union(), f"{node.expr.x_type}"
    for c1, c2 in zip(node.x_type.union_member_types(), node.expr.x_type.union_member_types()):
        _CheckTypeSame(node, c1, c2)


def _CheckValNum(node: cwast.ValNum, _):
    ct = node.x_type
    if not ct.is_base_type() and not ct.is_enum():
        cwast.CompilerError(node.x_srcloc, f"type mismatch {node} vs {ct}")


def _CheckExprCall(node: cwast.ExprCall,  _):
    fun_sig: cwast.CanonType = node.callee.x_type
    assert fun_sig.is_fun(), f"{fun_sig}"
    assert fun_sig.result_type(
    ) == node.x_type, f"{fun_sig.result_type()} {node.x_type}"
    for p, a in zip(fun_sig.parameter_types(), node.args):
        _CheckTypeCompatibleForAssignment(
            p,  a.x_type, p, type_corpus.is_mutable_array(a), a.x_srcloc)


def _CheckExprCallStrict(node: cwast.ExprCall,  _):
    fun_sig: cwast.CanonType = node.callee.x_type
    assert fun_sig.is_fun(), f"{fun_sig}"
    assert fun_sig.result_type(
    ) == node.x_type, f"{fun_sig.result_type()} {node.x_type}"
    for p, a in zip(fun_sig.parameter_types(), node.args):
        _CheckTypeSameExceptMut(
            p,  a.x_type, p, a.x_srcloc)


def _CheckExprIndex(node: cwast.ExprIndex, _):
    assert node.x_type is node.container.x_type.underlying_vec_or_span_type()


def _CheckExprWrap(node: cwast.ExprWrap,  _):
    ct_node: cwast.CanonType = node.x_type
    ct_expr: cwast.CanonType = node.expr.x_type
    assert ct_node == node.type.x_type
    if not type_corpus.is_compatible_for_wrap(ct_expr, ct_node):
        cwast.CompilerError(
            node.x_srcloc, f"bad wrap {ct_expr} -> {ct_node}")


def _CheckExprUnwrap(node: cwast.ExprUnwrap,  _):
    ct_node: cwast.CanonType = node.x_type
    ct_expr: cwast.CanonType = node.expr.x_type
    if ct_expr.is_enum():
        assert ct_node.is_base_type() and ct_expr.base_type_kind == ct_node.base_type_kind
    elif ct_expr.is_wrapped():
        assert ct_expr.underlying_wrapped_type() in (
            ct_node, ct_node.original_type), f"{ct_node} vs {ct_expr}"
    else:
        assert False


def _CheckDefFunTypeFun(node, _):
    ct = node.x_type
    assert ct.is_fun()
    _CheckTypeSame(node.result, ct.result_type(), node.result.x_type)
    for a, b in zip(ct.parameter_types(), node.params):
        _CheckTypeSame(b, a, b.type.x_type)
    # We should also ensure three is a proper return but that requires dataflow


def _CheckValSpan(node: cwast.ValSpan, _):
    assert node.x_type.is_mutable() == node.pointer.x_type.is_mutable()
    _CheckTypeSame(node, node.x_type.underlying_span_type(),
                   node.pointer.x_type.underlying_pointer_type())


def _CheckExprUnionTag(node: cwast.ExprUnionTag, tc: type_corpus.TypeCorpus):
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


def _CheckDefRecDefEnum(node, _):
    assert node.x_type.ast_node is node


def _CheckIsBool(node: Any, _):
    assert node.x_type.is_bool()


def _CheckIsVoid(node: Any, _):
    assert node.x_type.is_void()


def _CheckIsUint(node: Any,  tc: type_corpus.TypeCorpus):
    assert node.x_type is tc.get_uint_canon_type()


def _CheckIsTypeId(node: Any, tc: type_corpus.TypeCorpus):
    assert node.x_type is tc.get_typeid_canon_type()


def _CheckStmtCompoundAssignment(node: cwast.StmtCompoundAssignment,  tc: type_corpus.TypeCorpus):
    if not type_corpus.is_proper_lhs(node.lhs):
        cwast.CompilerError(
            node.x_srcloc, f"cannot assign to readonly data: {node}")
    kind = cwast.COMPOUND_KIND_TO_EXPR_KIND[node.assignment_kind]
    var_ct = node.lhs.x_type
    expr_ct = node.expr_rhs.x_type
    _CheckExpr2Types(node, var_ct, var_ct, expr_ct, kind, tc)


def _CheckStmtAssignment(node: cwast.StmtAssignment, _):
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


def _CheckStmtReturn(node: cwast.StmtReturn, _):
    target = node.x_target
    actual = node.expr_ret.x_type
    if isinstance(target, cwast.DefFun):
        expected = target.result.x_type
    else:
        assert isinstance(target, cwast.ExprStmt)
        expected = target.x_type
    _CheckTypeCompatible(node,  actual, expected)


def _CheckStmtReturnStrict(node: cwast.StmtReturn, _):
    target = node.x_target
    actual = node.expr_ret.x_type
    if isinstance(target, cwast.DefFun):
        expected = target.result.x_type
    else:
        assert isinstance(target, cwast.ExprStmt)
        expected = target.x_type
    _CheckTypeSameExceptMut(node,  actual, expected)


def _CheckStmtIfStmtCond(node, _):
    assert node.cond.x_type.is_bool()


def _CheckDefVarDefGlobal(node, _):
    initial = node.initial_or_undef_or_auto
    ct = node.type_or_auto.x_type

    if not isinstance(initial, cwast.ValUndef):
        _CheckTypeCompatibleForAssignment(
            node, initial.x_type, ct, type_corpus.is_mutable_array(
                initial),
            initial.x_srcloc)
    _CheckTypeSame(node, node.x_type, ct)


def _CheckDefVarDefGlobalStrict(node, _):
    initial = node.initial_or_undef_or_auto
    ct = node.type_or_auto.x_type
    if not isinstance(initial, cwast.ValUndef):
        ct = node.type_or_auto.x_type
        _CheckTypeSameExceptMut(
            node, initial.x_type, ct, initial.x_srcloc)
    _CheckTypeSame(node, node.x_type, ct)


def CheckExprAs(node: cwast.ExprAs, _):
    ct_src = node.expr.x_type
    ct_dst = node.type.x_type
    if not type_corpus.is_compatible_for_as(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad cast {ct_src} -> {ct_dst}: {node.expr}")


def _CheckExprUnsafeCast(node: cwast.ExprUnsafeCast,  tc: type_corpus.TypeCorpus):
    if not node.x_type.is_pointer() or not node.expr.x_type.is_pointer():
        cwast.CompilerError(
            node.x_srcloc, "unsafe_cast must convert pointer to pointer")


def _CheckExprBitCast(node: cwast.ExprAs, _):
    ct_src = node.expr.x_type
    ct_dst = node.type.x_type
    if not type_corpus.is_compatible_for_bitcast(ct_src, ct_dst):
        cwast.CompilerError(
            node.x_srcloc,  f"bad cast {ct_src} -> {ct_dst}: {node.expr}")


def _CheckNothing(_, _2):
    pass


class TypeVerifier:
    """"This class allows us to switch out per node checkers as we modify the AST"""

    def __init__(self):
        # maps nodes
        self._map = {
            cwast.ValCompound: _CheckValCompound,
            cwast.ValPoint: _CheckNothing,

            cwast.Expr1: lambda node, tc: _CheckTypeSame(node, node.x_type, node.expr.x_type),

            cwast.TypeOf: lambda node, tc: _CheckTypeSame(node, node.x_type, node.expr.x_type),
            cwast.Expr2: lambda node, tc:  _CheckExpr2Types(node, node.x_type,  node.expr1.x_type,
                                                            node.expr2.x_type, node.binary_expr_kind, tc),
            cwast.Expr3: CheckExpr3,
            cwast.ExprDeref: CheckExprDeref,
            cwast.ExprPointer: CheckExprPointer,
            cwast.ExprIndex: _CheckExprIndex,
            cwast.ExprField: CheckExprField,
            cwast.ExprFront: CheckExprFront,
            cwast.ExprWiden: _CheckExprWiden,
            cwast.ExprNarrow: _CheckExprNarrow,
            cwast.ExprAddrOf: _CheckExprAddrOf,
            cwast.ExprUnionTag: _CheckExprUnionTag,
            cwast.ExprUnionUntagged: _CheckExprUnionUntagged,
            cwast.ExprWrap: _CheckExprWrap,
            cwast.ExprUnwrap: _CheckExprUnwrap,
            cwast.ExprCall: _CheckExprCall,

            cwast.Id: CheckId,
            #
            cwast.TypeUnion: lambda node, tc: node.x_type.is_union(),
            cwast.TypeFun: _CheckDefFunTypeFun,
            #
            cwast.DefRec: _CheckDefRecDefEnum,
            cwast.DefEnum: _CheckDefRecDefEnum,
            #
            cwast.DefFun: _CheckDefFunTypeFun,
            #
            cwast.ValSpan: _CheckValSpan,
            #
            cwast.ValNum: _CheckValNum,
            #
            cwast.ExprIs: _CheckIsBool,
            cwast.ValTrue: _CheckIsBool,
            cwast.ValFalse: _CheckIsBool,
            #
            cwast.ValVoid: _CheckIsVoid,
            #
            cwast.ExprTypeId: _CheckIsTypeId,
            #
            cwast.ExprOffsetof: _CheckIsUint,
            cwast.ExprSizeof:  _CheckIsUint,
            cwast.ExprLen: _CheckIsUint,
            #
            cwast.DefType: _CheckNothing,
            cwast.TypeBase: _CheckNothing,
            cwast.TypeSpan: _CheckNothing,
            cwast.TypeVec: _CheckNothing,
            cwast.TypeAuto: _CheckNothing,
            cwast.TypePtr: _CheckNothing,
            cwast.FunParam: _CheckNothing,
            cwast.EnumVal: _CheckNothing,
            cwast.ValAuto: _CheckNothing,
            cwast.ValString: _CheckNothing,
            cwast.ExprStmt: _CheckNothing,
            cwast.RecField: _CheckNothing,
            cwast.TypeUnionDelta:  _CheckNothing,
            # minuned = node.type.x_type
            #  subtrahend = node.subtrahend.x_type
            # TODO: need to use original types if available
            cwast.ExprUnsafeCast: _CheckExprUnsafeCast,
            cwast.ExprAs: CheckExprAs,
            cwast.ExprBitCast: _CheckExprBitCast,

            # Statements
            cwast.StmtIf: _CheckStmtIfStmtCond,
            cwast.StmtCond: _CheckStmtIfStmtCond,
            cwast.StmtExpr:  _CheckNothing,
            cwast.StmtCompoundAssignment: _CheckStmtCompoundAssignment,
            cwast.StmtAssignment: _CheckStmtAssignment,
            cwast.StmtReturn: _CheckStmtReturn,
            cwast.DefVar: _CheckDefVarDefGlobal,
            cwast.DefGlobal: _CheckDefVarDefGlobal,
            cwast.ExprParen: lambda node, tc: _CheckTypeSame(node, node.x_type, node.expr.x_type),
        }

    def Verify(self, node: cwast.ALL_NODES, tc: type_corpus.TypeCorpus):
        self._map[type(node)](node, tc)

    def Replace(self, node_type, checker):
        self._map[node_type] = checker


def VerifyTypesRecursively(node, tc: type_corpus.TypeCorpus,
                           verifier: TypeVerifier):
    def visitor(node, field):
        nonlocal verifier
        if cwast.NF.TOP_LEVEL in node.FLAGS:
            logger.info("TYPE-VERIFYING %s", node)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            ct: cwast.CanonType = node.x_type
            if ct is cwast.NO_TYPE:
                assert field == "point", f"missing type for {
                    node} in {node.x_srcloc}"
            else:
                assert ct.name in tc.corpus, f"bad type annotation for {
                    node}: {node.x_type}"
                assert ct.replacement_type is None
                verifier.Verify(node, tc)

        elif isinstance(node, UNTYPED_NODES_TO_BE_TYPECHECKED):
            verifier.Verify(node, tc)

    cwast.VisitAstRecursivelyPost(node, visitor)


def DecorateASTWithTypes(mod_topo_order: list[cwast.DefMod],
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
    # make rec types known without fully processing the rec fields
    # so that they can be used for recursive type definitions
    # We stil need to process the fields which is done later below
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefRec):
                ct = tc.insert_rec_type(f"{ctx.mod_name}/{node.name}", node)
                AnnotateNodeType(node, ct)
    #
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefRec):
                ct = node.x_type
                for f in node.fields:
                    assert isinstance(f,  cwast.RecField)
                    fct = _TypifyNodeRecursively(
                        f.type, tc, cwast.NO_TYPE, ctx)
                    AnnotateNodeType(f, fct)
                # we delay this until after fields have been typified this is necessary
                # because of recursive types
                tc.finalize_rec_type(ct)
    # deal with the top level stuff - not function bodies
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            if not isinstance(node, cwast.DefRec):
                # we already dealt with DefRecs
                _TypifyTopLevel(node, tc, ctx)
            if isinstance(node, cwast.DefFun) and node.poly:
                ct = node.x_type
                assert ct.node is cwast.TypeFun, f"{node} -> {ct.name}"
                poly_map.Register(node)
    # now typify function bodies
    for mod in mod_topo_order:
        ctx = _TypeContext(mod.x_modname, poly_map)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun) and not node.extern:
                for c in node.body:
                    _TypifyStatement(
                        c, tc, node.result.x_type, ctx)


def RemoveUselessCast(node, tc: type_corpus.TypeCorpus):
    def replacer(node, _parent, _field):
        nonlocal tc
        if isinstance(node, cwast.ExprAs):
            if node.x_type is node.expr.x_type:
                return node.expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
############################################################
#
############################################################


def main(argv):
    assert len(argv) == 1
    fn = argv[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    cwd = os.getcwd()
    mp: mod_pool.ModPool = mod_pool.ModPool(pathlib.Path(cwd) / "Lib")
    main = str(pathlib.Path(fn).resolve())
    mp.ReadModulesRecursively([main], add_builtin=fn != "Lib/builtin")
    mod_topo_order = mp.ModulesInTopologicalOrder()
    for mod in mod_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    fun_id_gens = identifier.IdGenCache()
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, fun_id_gens)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    DecorateASTWithTypes(mod_topo_order, tc)
    verifier = TypeVerifier()
    for mod in mod_topo_order:
        VerifyTypesRecursively(mod, tc, verifier)

    for t, n in tc.corpus.items():
        logger.info("%s %s %d %d", t, n.register_types, n.size, n.alignment)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import identifier

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
