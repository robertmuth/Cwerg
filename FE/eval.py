#!/bin/env python3

"""Partial evaluator and value annotator for Cwerg AST

"""

import logging

from typing import Optional, Any, Union
import enum

from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import typify
from FE import identifier
from FE import canonicalize


logger = logging.getLogger(__name__)


class _ValSpecial:
    def __init__(self, kind: str):
        self._kind = kind

    def __str__(self):
        return f"VAL-{self._kind}"

    def __repr__(self):
        return f"VAL-{self._kind}"


VAL_UNDEF = _ValSpecial("UNDEF")
VAL_VOID = _ValSpecial("VOID")
VAL_GLOBALSYMADDR = _ValSpecial("GLOBALSYMADDR")
VAL_GLOBALSLICE = _ValSpecial("GLOBALSLICE")


@enum.unique
class CONSTANT_KIND(enum.Enum):
    # These form a simple straight line lattice
    NOT = 0    # not a constant
    WITH_GOBAL_ADDRESS = 3  # constant with addresses
    PURE = 4


def AddressConstKind(node) -> CONSTANT_KIND:
    if isinstance(node, cwast.Id):
        if isinstance(node.x_symbol, cwast.DefGlobal):
            return CONSTANT_KIND.WITH_GOBAL_ADDRESS
        elif isinstance(node.x_symbol, cwast.DefVar):
            return CONSTANT_KIND.NOT
        else:
            assert False
            return CONSTANT_KIND.NOT
    elif isinstance(node, cwast.ExprIndex):
        if not isinstance(node.expr_index, cwast.ValNum):
            return CONSTANT_KIND.NOT
        return AddressConstKind(node.container)
    else:
        return CONSTANT_KIND.NOT


def ValueConstKind(node) -> CONSTANT_KIND:
    """Determine the kind of constant the node represents

    This works best once constant folding has occurred
    NOT: not a constant
    WITH_GOBAL_ADDRESS: constant requiring relocation
    PURE: pure constant
    """
    assert cwast.NF.VALUE_ANNOTATED in node.FLAGS
    if isinstance(node, (cwast.ValString, cwast.ValFalse, cwast.ValTrue,
                         cwast.ValVoid, cwast.ValUndef, cwast.ValNum)):
        return CONSTANT_KIND.PURE
    if isinstance(node, cwast.ExprAddrOf):
        return AddressConstKind(node.expr_lhs)
    elif isinstance(node, cwast.ExprFront):
        return AddressConstKind(node.container)
    elif isinstance(node, cwast.ValSpan):
        if not isinstance(node.expr_size, cwast.ValNum):
            return CONSTANT_KIND.NOT
        return ValueConstKind(node.pointer)
    elif isinstance(node, cwast.ValCompound):
        out = CONSTANT_KIND.PURE
        is_vec = node.x_type.is_vec()
        for field in node.inits:
            if is_vec:
                if not isinstance(field.point, (cwast.ValAuto, cwast.ValNum)):
                    return CONSTANT_KIND.NOT
            o = ValueConstKind(field.value_or_undef)
            if o is CONSTANT_KIND.NOT:
                return o
            if o.value < out.value:
                out = o
        return out
    else:
        # cwast.CompilerError(node.x_srcloc, f"unexpected {node}")
        return CONSTANT_KIND.NOT

# def _ValueShouldBeGlobalConst(node) -> bool:
#     if not isinstance(node, cwast.ValString, cwast.ValArray, cwast.ValRec):
#         # do not bother with small values like spans, etc.
#         return False;
#     # Maybe instantiating small string directly?
#     if isinstance(node, cwast.ValString): return True
#     return eval.IsGlobalConst(node)


def _IdNodeFromDef(def_node: Union[cwast.DefVar, cwast.DefGlobal], x_srcloc) -> cwast.Id:
    assert def_node.type_or_auto.x_type is not None
    return cwast.Id(def_node.name, None, x_srcloc=x_srcloc, x_type=def_node.type_or_auto.x_type,
                    x_value=def_node.initial_or_undef_or_auto.x_value, x_symbol=def_node)


class GlobalConstantPool:
    """Manages a bunch of DefGlobal statements that were implicit in the orginal code

    We move string/array/etc values into globals (un-mutable variables) for two reasons:
    1) if these consts are used to initialize local variables, copying the data
       from a global might be more efficient in both terms of time and cache used
       Note: that we can also collapse idententical constants
    2) If the address of the  const is taken we must materialize the constant.
       This should only apply to case were strings/arrays are implicitly converted
       to a span.

    """

    def __init__(self):
        self._current_no = 0
        self._bytes_map: dict[bytes, cwast.DefGlobal] = {}
        self._all_globals: list[cwast.DefGlobal] = []

    def _add_def_global(self, node) -> cwast.DefGlobal:
        # TODO: leave this to code gen
        self._current_no += 1
        def_node = cwast.DefGlobal(cwast.NAME.FromStr(f"global_val_{self._current_no}"),
                                   cwast.TypeAuto(
            x_srcloc=node.x_srcloc, x_type=node.x_type), node,
            pub=True,
            x_srcloc=node.x_srcloc,
            x_type=node.x_type)
        self._all_globals.append(def_node)
        return def_node

    def _maybe_replace(self, node, parent) -> Optional[Any]:
        if isinstance(parent, cwast.DefGlobal):
            return None
        elif (isinstance(node, cwast.ValCompound) and
              # also allow this for rec vals this currently breaks for one test case
              # blocked on BUG(#40)
              node.x_type.is_vec() and
              ValueConstKind(node) is not CONSTANT_KIND.NOT and
              not isinstance(parent, cwast.DefVar)):
            # TODO: this should also be done for recs
            def_node = self._add_def_global(node)
            # TODO: maybe update str_map for the CONSTANT_KIND.PURE case
            return _IdNodeFromDef(def_node, node.x_srcloc)
        elif isinstance(node, cwast.ValString):
            assert isinstance(
                node.x_value, bytes), f"expected str got {node.x_value}"
            def_node = self._bytes_map.get(node.x_value)
            if not def_node:
                def_node = self._add_def_global(node)
                self._bytes_map[node.x_value] = def_node
            return _IdNodeFromDef(def_node, node.x_srcloc)

        return None

    def PopulateConstantPool(self, node):
        # if we relace a node we do not need to recurse into the subtree
        cwast.MaybeReplaceAstRecursively(node, self._maybe_replace)

    def GetDefGlobals(self) -> list[cwast.DefGlobal]:
        return self._all_globals


def IsGlobalSymId(node):
    # TODO: maybe include DefFun
    return isinstance(node, cwast.Id) and isinstance(node.x_symbol, cwast.DefGlobal)


def _VerifyEvalValue(val):
    # TODO: check this recusively
    # "None" is reserve for indicating that evaluation was not possible
    #
    if isinstance(val, list):
        for x in val:
            assert x is not None
    elif isinstance(val, tuple):
        for x in val:
            assert x is not None
    elif isinstance(val, dict):
        for x in val.values():
            assert x is not None, f"rec dict with None {val}"
    else:
        assert isinstance(val, (int, float, bytes, _ValSpecial)
                          ), f"unexpected value {val}"
        assert val is not None


def _AssignValue(node, val) -> bool:
    if val is None:
        return False
    _VerifyEvalValue(val)

    if isinstance(val, list):
        logger.info("EVAL of %s: %s...", node, val[:8])
    else:
        logger.info("EVAL of %s: %s", node, val)
    node.x_value = val
    return True


def _EvalDefEnum(node: cwast.DefEnum) -> bool:
    """TBD"""
    out = False
    val = 0
    for c in node.items:
        assert isinstance(c, cwast.EnumVal)
        if not isinstance(c.value_or_auto, cwast.ValAuto):
            assert c.value_or_auto.x_value is not None
            val = c.value_or_auto.x_value
        if c.x_value is None:
            _AssignValue(c.value_or_auto, val)
            _AssignValue(c, val)
            out = True
        val += 1
    return out


_BASE_TYPE_TO_DEFAULT = {
    cwast.BASE_TYPE_KIND.SINT: 0,
    cwast.BASE_TYPE_KIND.S8: 0,
    cwast.BASE_TYPE_KIND.S16: 0,
    cwast.BASE_TYPE_KIND.S32: 0,
    cwast.BASE_TYPE_KIND.S64:  0,
    #
    cwast.BASE_TYPE_KIND.UINT: 0,
    cwast.BASE_TYPE_KIND.U8: 0,
    cwast.BASE_TYPE_KIND.U16: 0,
    cwast.BASE_TYPE_KIND.U32: 0,
    cwast.BASE_TYPE_KIND.U64: 0,
    #
    cwast.BASE_TYPE_KIND.R32: 0.0,
    cwast.BASE_TYPE_KIND.R64: 0.0,
    #
    cwast.BASE_TYPE_KIND.BOOL: False,
}


def _GetDefaultForType(ct: cwast.CanonType, srcloc) -> Any:
    if ct.is_base_type():
        return _BASE_TYPE_TO_DEFAULT[ct.base_type_kind]
    elif ct.is_wrapped():
        return _GetDefaultForType(ct.underlying_wrapped_type(), srcloc)
    elif ct.is_span():
        return []  # null span
    elif ct.is_pointer():
        cwast.CompilerError(srcloc, f"ptr field  {ct} must be initialized")
    elif ct.is_rec():
        out = {}
        for field in ct.ast_node.fields:
            out[field.name] = _GetDefaultForType(field.x_type, srcloc)
        return out
    elif ct.is_vec():
        dim = ct.array_dim()
        v = _GetDefaultForType(ct.underlying_array_type(), srcloc)
        return [v] * dim
    else:
        assert False, f"{ct} {srcloc}"


def _EvalValCompound(ct: cwast.CanonType, inits: list, srcloc) -> Optional[Any]:
    if ct.is_rec():
        rec: dict[cwast.NAME, Any] = {}
        for field, init in symbolize.IterateValRec(inits, ct):
            assert isinstance(field, cwast.RecField)
            # print ("    ", field)
            if init is None:
                rec[field.name] = _GetDefaultForType(field.x_type, srcloc)
            else:
                assert isinstance(init, cwast.ValPoint), f"{init}"
                if init.x_value is None:
                    return None
                rec[field.name] = init.x_value
        return rec
    else:
        assert ct.is_vec()
        has_unknown = False
        # first pass if we cannot evaluate everyting, we must give up
        # This could be relaxed if we allow None values in "out"
        for c in inits:
            assert isinstance(c, cwast.ValPoint)
            index = c.point
            if not isinstance(index, cwast.ValAuto):
                if index.x_value is None:
                    has_unknown = True
                    break
            if not isinstance(c.value_or_undef, cwast.ValUndef):
                if c.value_or_undef.x_value is None:
                    has_unknown = True
                    break
        if has_unknown:
            return None
        curr_val = VAL_UNDEF
        array = []
        for _, c in symbolize.IterateValVec(inits, ct.array_dim(), srcloc):
            if c is None:
                array.append(curr_val)
                continue
            curr_val = c.value_or_undef.x_value
            if curr_val is None:
                return None
            array.append(curr_val)
        return array


def _eval_not(node) -> bool:
    if node.x_type.is_bool():
        return not node.x_value
    else:
        assert node.x_type.is_uint()
        return ~node.x_value & ((1 << (node.x_type.size * 8)) - 1)


def _eval_minus(node) -> Any:
    return - node.x_value


_EVAL1 = {
    cwast.UNARY_EXPR_KIND.NOT: _eval_not,
    cwast.UNARY_EXPR_KIND.NEG: _eval_minus,
}


def _EvalExpr1(node: cwast.Expr1) -> bool:
    if node.expr.x_value is None:
        return False
    return _AssignValue(node, _EVAL1[node.unary_expr_kind](node.expr))


# TODO: naive implementation -> needs a lot more scrutiny
_EVAL2_ANY = {
    cwast.BINARY_EXPR_KIND.ADD: lambda x, y: x.x_value + y.x_value,
    cwast.BINARY_EXPR_KIND.SUB: lambda x, y: x.x_value - y.x_value,
    cwast.BINARY_EXPR_KIND.MUL: lambda x, y: x.x_value * y.x_value,
    cwast.BINARY_EXPR_KIND.EQ: lambda x, y: x.x_value == y.x_value,
    cwast.BINARY_EXPR_KIND.NE: lambda x, y: x.x_value != y.x_value,
    cwast.BINARY_EXPR_KIND.LT: lambda x, y: x.x_value < y.x_value,
    cwast.BINARY_EXPR_KIND.LE: lambda x, y: x.x_value <= y.x_value,
    cwast.BINARY_EXPR_KIND.GT: lambda x, y: x.x_value > y.x_value,
    cwast.BINARY_EXPR_KIND.GE: lambda x, y: x.x_value >= y.x_value,
}

_EVAL2_REAL = {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x.x_value / y.x_value,
}

_EVAL2_INT = {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x.x_value // y.x_value,
    cwast.BINARY_EXPR_KIND.MOD: lambda x, y: x.x_value % y.x_value,
    cwast.BINARY_EXPR_KIND.SHL: lambda x, y: x.x_value << y.x_value,
    cwast.BINARY_EXPR_KIND.SHR: lambda x, y: x.x_value >> y.x_value,
}

_EVAL2_UINT = {
    cwast.BINARY_EXPR_KIND.OR: lambda x, y: x.x_value | y.x_value,
    cwast.BINARY_EXPR_KIND.AND: lambda x, y: x.x_value & y.x_value,
    cwast.BINARY_EXPR_KIND.XOR: lambda x, y: x.x_value ^ y.x_value,
}


def _HandleUintOverflow(kind: cwast.BASE_TYPE_KIND, val: int) -> int:
    mask = (1 << (8 * cwast.BASE_TYPE_KIND_TO_SIZE[kind])) - 1
    return val & mask


def _EvalExpr2(node: cwast.Expr2) -> bool:
    if node.expr1.x_value is None or node.expr2.x_value is None:
        return False
    op = node.binary_expr_kind
    x_type = node.x_type

    if x_type.is_real():
        if op in _EVAL2_ANY:
            return _AssignValue(node, _EVAL2_ANY[op](node.expr1, node.expr2))
        if op in _EVAL2_REAL:
            return _AssignValue(node, _EVAL2_REAL[op](node.expr1, node.expr2))
    elif x_type.is_sint():
        # TODO: deal with signed overflow
        if op in _EVAL2_ANY:
            return _AssignValue(node, _EVAL2_ANY[op](node.expr1, node.expr2))
        if op in _EVAL2_INT:
            return _AssignValue(node, _EVAL2_INT[op](node.expr1, node.expr2))
    elif x_type.is_uint():
        kind = x_type.base_type_kind
        if op in _EVAL2_ANY:
            return _AssignValue(node,
                                _HandleUintOverflow(kind, _EVAL2_ANY[op](node.expr1, node.expr2)))
        if op in _EVAL2_INT:
            return _AssignValue(node,
                                _HandleUintOverflow(kind, _EVAL2_INT[op](node.expr1, node.expr2)))
        if op in _EVAL2_UINT:
            return _AssignValue(node,
                                _HandleUintOverflow(kind, _EVAL2_UINT[op](node.expr1, node.expr2)))
    elif x_type.is_bool():
        if op in _EVAL2_ANY:
            return _AssignValue(node, _EVAL2_ANY[op](node.expr1, node.expr2))

    return False


def _EvalExpr3(node: cwast.Expr3) -> bool:
    if node.cond.x_value is None:
        return False
    if node.cond.x_value:
        if node.expr_t.x_value is not None:
            return _AssignValue(node, node.expr_t.x_value)
    else:
        if node.expr_f.x_value is not None:
            return _AssignValue(node, node.expr_f.x_value)
    return False


def _EvalAuto(node: cwast.ValAuto) -> bool:
    ct: cwast.CanonType = node.x_type
    if ct.is_base_type():
        if ct.is_bool():
            return _AssignValue(node, False)
        elif ct.is_int():
            return _AssignValue(node, 0)
        elif ct.is_real():
            return _AssignValue(node, 0.0)
        else:
            assert False
    elif ct.is_rec():
        return _AssignValue(node, _EvalValCompound(ct, [], node.x_srcloc))
    elif ct.is_vec():
        return _AssignValue(node, _EvalValCompound(ct, [], node.x_srcloc))
    elif isinstance(node, cwast.TypePtr):
        assert False
    else:
        return False


def _EvalNode(node: cwast.NODES_EXPR_T) -> bool:
    """Returns True if node could be evaluated."""

    if isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert def_node is not None, f"{node}"
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            initial = def_node.initial_or_undef_or_auto
            if not def_node.mut and initial.x_value is not None:
                return _AssignValue(node, initial.x_value)
        elif isinstance(def_node, cwast.EnumVal):
            return _AssignValue(node, def_node.value_or_auto.x_value)
        return False
    elif isinstance(node, cwast.EnumVal):
        return False  # handles as part of DefEnum
    elif isinstance(node, cwast.DefEnum):
        return _EvalDefEnum(node)
    elif isinstance(node, cwast.ValTrue):
        return _AssignValue(node, True)
    if isinstance(node, cwast.ValFalse):
        return _AssignValue(node, False)
    elif isinstance(node, cwast.ValVoid):
        return _AssignValue(node, VAL_VOID)
    elif isinstance(node, cwast.ValUndef):
        return _AssignValue(node, VAL_UNDEF)
    elif isinstance(node, cwast.ValNum):
        cstr: cwast.CanonType = node.x_type
        if cstr.is_base_type() or cstr.is_enum():
            return _AssignValue(node, typify.ParseNum(node, cstr.base_type_kind))
        else:
            assert False, f"unepxected type for ValNum: {cstr}"
            return False
    elif isinstance(node, cwast.ValAuto):
        # we do not evaluate this during the recursion
        # Instead we evaluate this inside DefGlobal, DefVar, DefEnum
        return False
    elif isinstance(node, cwast.ValPoint):
        if node.value_or_undef.x_value is None:
            if (node.x_type.is_span() and node.value_or_undef.x_type.is_vec() and
                    IsGlobalSymId(node.value_or_undef)):
                return _AssignValue(node, VAL_GLOBALSLICE)
        else:
            return _AssignValue(node, node.value_or_undef.x_value)
        return False
    elif isinstance(node, cwast.ValCompound):
        return _AssignValue(node, _EvalValCompound(node.x_type, node.inits, node.x_srcloc))
    elif isinstance(node, cwast.ValString):
        return _AssignValue(node, node.get_bytes())
    elif isinstance(node, cwast.ExprIndex):
        index_val = node.expr_index.x_value
        container_val = node.container.x_value
        if container_val is not None and index_val is not None:
            assert isinstance(container_val, (list, bytes)
                              ), f"{node.container.x_value}"
            assert index_val < len(
                container_val), f"{index_val} {container_val}"
            return _AssignValue(node, container_val[index_val])
        return False
    elif isinstance(node, cwast.ExprField):
        if node.container.x_value is not None:
            field_val = node.container.x_value.get(
                node.field.GetBaseNameStrict())
            assert field_val is not None
            assert not isinstance(
                field_val, cwast.ValUndef), f"unevaluated field {node.field}: {node.container.x_value}"
            return _AssignValue(node, field_val)
        return False
    elif isinstance(node, cwast.Expr1):
        return _EvalExpr1(node)
    elif isinstance(node, cwast.Expr2):
        return _EvalExpr2(node)
    elif isinstance(node, cwast.Expr3):
        return _EvalExpr3(node)
    elif isinstance(node, cwast.ExprTypeId):
        typeid = node.type.x_type.get_original_typeid()
        assert typeid >= 0
        return _AssignValue(node, typeid)
    elif isinstance(node, cwast.ExprCall):
        # TODO
        return False
    elif isinstance(node, cwast.ExprStmt):
        return False
    elif isinstance(node, (cwast.ExprAs, cwast.ExprNarrow, cwast.ExprWiden, cwast.ExprWrap, cwast.ExprUnwrap)):
        # TODO: some transforms may need to be applied
        if node.expr.x_value is not None:
            return _AssignValue(node, node.expr.x_value)
        return False
    elif isinstance(node, cwast.ExprUnionUntagged):
        # TODO: we can do better here
        return False
    elif isinstance(node, (cwast.ExprBitCast, cwast.ExprUnsafeCast)):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprIs):
        expr_ct: cwast.CanonType = node.expr.x_type
        test_ct: cwast.CanonType = node.type.x_type
        if expr_ct.get_original_typeid() == test_ct.get_original_typeid():
            return _AssignValue(node, True)
        if expr_ct.is_tagged_union():
            if test_ct.is_tagged_union():
                test_elements = set(
                    [x.name for x in test_ct.union_member_types()])
                expr_elements = set(
                    [x.name for x in expr_ct.union_member_types()])
                if expr_elements.issubset(test_elements):
                    return _AssignValue(node, True)
                return False
            else:
                return False
        elif test_ct.is_tagged_union():
            test_elements = set(
                [x.name for x in test_ct.union_member_types()])
            return _AssignValue(node, expr_ct.name in test_elements)
        else:
            return _AssignValue(node, False)
    elif isinstance(node, cwast.ExprPointer):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprFront):
        if IsGlobalSymId(node.container):
            return _AssignValue(node, VAL_GLOBALSYMADDR)
        return False
    elif isinstance(node, cwast.ExprLen):
        if node.container.x_type.is_vec():
            return _AssignValue(node, node.container.x_type.array_dim())
        elif node.container.x_value is not None:
            return _AssignValue(node, len(node.container.x_value))
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        if IsGlobalSymId(node.expr_lhs):
            return _AssignValue(node, VAL_GLOBALSYMADDR)
        return False
    elif isinstance(node, cwast.ExprOffsetof):
        # assert node.x_field.x_offset > 0
        return _AssignValue(node, node.field.x_symbol.x_offset)
    elif isinstance(node, cwast.ExprSizeof):
        return _AssignValue(node, node.type.x_type.size)
    elif isinstance(node, cwast.ExprDeref):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ExprAddrOf):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ValSpan):
        if node.pointer.x_value is not None and node.expr_size.x_value is not None:
            return _AssignValue(node,
                                (node.pointer.x_value, node.expr_size.x_value))
        return False
    elif isinstance(node, cwast.ExprUnionTag):
        return False
    elif isinstance(node, cwast.ExprParen):
        if _EvalNode(node.expr):
            return _AssignValue(node, node.expr.x_value)
        return False
    else:
        assert False, f"unexpected node {node}"


def EvalRecursively(node) -> bool:
    seen_change = False

    def visitor(node):
        nonlocal seen_change
        if isinstance(node, (cwast.DefGlobal, cwast.DefVar)):
            initial = node.initial_or_undef_or_auto
            if initial.x_value is not None:
                return
            if isinstance(initial, cwast.ValAuto):
                seen_change |= _EvalAuto(initial)
        if cwast.NF.VALUE_ANNOTATED not in node.FLAGS:
            return
        if node.x_value is not None:
            return

        seen_change |= _EvalNode(node)

    cwast.VisitAstRecursivelyPost(node, visitor)

    if seen_change:
        logger.info("SEEN CHANGE %s", node)
    return seen_change


def VerifyASTEvalsRecursively(node):
    """Make sure that everything that is supposed to be const was evaluated"""
    is_const = False

    def visitor(node: Any, parent: Any):
        nonlocal is_const
        # logger.info(f"EVAL-VERIFY: {node}")
        if isinstance(node, cwast.ValUndef):
            return

        if isinstance(node, cwast.StmtStaticAssert):
            if node.cond.x_value is not True:
                cwast.CompilerError(
                    node.x_srcloc, f"Failed static assert: {node} is {node.cond.x_value}")

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            # we must be able to initialize data these at compile time
            is_const = isinstance(
                node, (cwast.DefGlobal, cwast.DefEnum))
            return

        if isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValNum, cwast.ValString)):
            assert node.x_value is not None, f"{node}"

        if is_const and cwast.NF.VALUE_ANNOTATED in node.FLAGS:
            if isinstance(node, cwast.Id):
                def_node = node.x_symbol
                if cwast.NF.VALUE_ANNOTATED in def_node.FLAGS:

                    if def_node.x_value is None:
                        if parent.x_type.is_pointer():
                            # TODO: we do not track constant addresses yet
                            # for now assume they are constant
                            pass
                        elif parent.x_type.is_span():
                            # TODO: we do not track constant addresses yet
                            # for now assume they are constant
                            pass
                        else:
                            cwast.CompilerError(def_node.x_srcloc,
                                                f"expected const node: {node} inside: {parent}")
            else:
                if node.x_value is None:
                    if node.x_type.is_span() or (node.x_type.original_type and
                                                 node.x_type.original_type.is_span()):
                        # TODO: we do not track constant addresses yet
                        # for now assume they are constant
                        pass
                    elif isinstance(node, cwast.ValCompound):
                        # we still check that each field is const
                        pass
                    elif isinstance(node, cwast.ValAuto) and parent.point == node:
                        pass
                    else:
                        cwast.CompilerError(
                            node.x_srcloc, f"expected const node: {node} "
                            f"of type {node.x_type} inside {parent}")

        # Note: this info is currently filled in by the Type Decorator
        if isinstance(node, cwast.TypeVec):
            assert node.size.x_value is not None, f"uneval'ed type dim: {node}"

    cwast.VisitAstRecursivelyWithParent(node, visitor, None)


def DecorateASTWithPartialEvaluation(mod_topo_order: list[cwast.DefMod]):
    """Fills in the x_value field"""
    iteration = 0
    seen_change = True
    while seen_change:
        iteration += 1
        logger.info("Eval Iteration %d", iteration)
        seen_change = False
        for mod in mod_topo_order:
            for node in mod.body_mod:
                seen_change |= EvalRecursively(node)

    for mod in mod_topo_order:
        VerifyASTEvalsRecursively(mod)


def main(argv: list[str]):
    cwast.ASSERT_AFTER_ERROR = False
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
    fun_id_gens = identifier.IdGenCache()
    macro.ExpandMacrosAndMacroLike(
        mp.mods_in_topo_order, mp.builtin_symtab, fun_id_gens)
    symbolize.SetTargetFields(mp.mods_in_topo_order)
    symbolize.ResolveSymbolsInsideFunctions(
        mp.mods_in_topo_order, mp.builtin_symtab)
    for mod in mp.mods_in_topo_order:
        symbolize.VerifySymbols(mod)
    for mod in mp.mods_in_topo_order:
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    typify.DecorateASTWithTypes(mp.mods_in_topo_order, tc)
    DecorateASTWithPartialEvaluation(mp.mods_in_topo_order)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import identifier
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
