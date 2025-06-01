#!/bin/env python3

"""Partial evaluator and value annotator for Cwerg AST

"""

import enum
import logging
from typing import Optional, Any, Union\

from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import typify
from FE import canonicalize


logger = logging.getLogger(__name__)


class EvalUndef:
    def __init__(self):
        pass


class EvalVoid:
    def __init__(self):
        pass


class EvalZeroCompound:
    def __init__(self):
        pass


class EvalSymAddr:
    def __init__(self, sym):
        assert isinstance(sym, (cwast.DefGlobal, cwast.DefVar)), f"{sym}"
        self.sym = sym

    def __eq__(self, other):
        if not isinstance(other, EvalSymAddr):
            return False
        return self.sym == other.sym


class EvalFunAddr:
    def __init__(self, sym):
        assert isinstance(sym, cwast.DefFun)
        self.sym = sym

    def __eq__(self, other):
        if not isinstance(other, EvalFunAddr):
            return False
        return self.sym == other.sym


class EvalCompound:
    def __init__(self, compound, sym=None):
        assert isinstance(compound, (cwast.ValString, cwast.ValCompound))
        self.compound = compound
        # if sym is not None it has been materialized as `sym`
        self.sym = sym


class EvalSpan:
    def __init__(self, pointer, size, content=None):
        assert pointer is None or isinstance(
            pointer, (cwast.DefGlobal, cwast.DefVar)), f"{pointer}"
        assert size is None or isinstance(size, int), f"{size}"
        self.pointer = pointer
        self.size = size
        self.content = content


class EvalNum:
    def __init__(self, val, kind: cwast.BASE_TYPE_KIND):
        assert isinstance(val, (int, float, bool)), f"{val}"
        assert isinstance(kind, cwast.BASE_TYPE_KIND)
        self.kind = kind
        self.val = val


VAL_EMPTY_SPAN = EvalSpan(None, 0)
VAL_UNDEF = EvalUndef()
VAL_VOID = EvalVoid()
VAL_ZERO_COMPOUND = EvalZeroCompound()
VAL_TRUE = EvalNum(True, cwast.BASE_TYPE_KIND.BOOL)
VAL_FALSE = EvalNum(False, cwast.BASE_TYPE_KIND.BOOL)


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
                if not isinstance(field.point_or_undef, (cwast.ValUndef, cwast.ValNum)):
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
        def_node = cwast.DefGlobal(cwast.NAME.Make(f"global_val_{self._current_no}"),
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
            s = node.get_bytes()
            def_node = self._bytes_map.get(s)
            if not def_node:
                def_node = self._add_def_global(node)
                self._bytes_map[s] = def_node
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


def _AssignValue(node, val) -> bool:
    if val is None:
        return False

    assert isinstance(val, (EvalNum, EvalUndef, EvalZeroCompound, EvalVoid,
                            EvalFunAddr, EvalCompound, EvalSpan, EvalSymAddr)
                      ), f"unexpected value {val}"
    logger.info("EVAL of %s: %s", node, val)
    node.x_value = val
    return True


def _EvalDefEnum(node: cwast.DefEnum) -> bool:
    """TBD"""
    bt = node.x_type.base_type_kind
    out = False
    val = 0
    for c in node.items:
        assert isinstance(c, cwast.EnumVal)
        if not isinstance(c.value_or_auto, cwast.ValAuto):
            assert c.value_or_auto.x_value is not None
            val = c.value_or_auto.x_value.val
        if c.x_value is None:
            _AssignValue(c.value_or_auto, EvalNum(val, bt))
            _AssignValue(c, EvalNum(val, bt))
            out = True
        val += 1
    return out


def GetDefaultForBaseType(bt: cwast.BASE_TYPE_KIND) -> Any:
    if bt.IsReal():
        return EvalNum(0.0, bt)
    elif bt.IsInt():
        return EvalNum(0, bt)
    elif bt is cwast.BASE_TYPE_KIND.BOOL:
        return VAL_FALSE
    else:
        assert False


def GetDefaultForType(ct: cwast.CanonType) -> Any:
    if ct.is_base_type():
        return GetDefaultForBaseType(ct.base_type_kind)
    elif ct.is_wrapped():
        return GetDefaultForType(ct.underlying_type())
    elif ct.is_span():
        return VAL_EMPTY_SPAN
    else:
        return None


def _EvalExpr1(node: cwast.Expr1) -> bool:
    e = node.expr.x_value
    if e is None:
        return False
    e = e.val
    bt = node.x_type.base_type_kind
    op = node.unary_expr_kind
    if bt == cwast.BASE_TYPE_KIND.BOOL:
        if op == cwast.UNARY_EXPR_KIND.NOT:
            v = not e
        elif op == cwast.UNARY_EXPR_KIND.NEG:
            v = e
        else:
            assert False
    elif bt.IsInt():
        assert bt.IsUint()
        if op == cwast.UNARY_EXPR_KIND.NOT:
            v = ~e & ((1 << (node.x_type.size * 8)) - 1)
        elif op == cwast.UNARY_EXPR_KIND.NEG:
            v = -e
        else:
            assert False
    else:
        return False
    return _AssignValue(node, EvalNum(v, bt))


# TODO: naive implementation -> needs a lot more scrutiny
_EVAL_EQ_NE = {
    cwast.BINARY_EXPR_KIND.EQ: lambda x, y: x == y,
    cwast.BINARY_EXPR_KIND.NE: lambda x, y: x != y,
}

_EVAL_CMP = _EVAL_EQ_NE | {
    cwast.BINARY_EXPR_KIND.LT: lambda x, y: x < y,
    cwast.BINARY_EXPR_KIND.LE: lambda x, y: x <= y,
    cwast.BINARY_EXPR_KIND.GT: lambda x, y: x > y,
    cwast.BINARY_EXPR_KIND.GE: lambda x, y: x >= y,
}

_EVAL_ADD_SUB_MUL = {
    cwast.BINARY_EXPR_KIND.ADD: lambda x, y: x + y,
    cwast.BINARY_EXPR_KIND.SUB: lambda x, y: x - y,
    cwast.BINARY_EXPR_KIND.MUL: lambda x, y: x * y,
}

_EVAL_INT = _EVAL_ADD_SUB_MUL | {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x // y,
    cwast.BINARY_EXPR_KIND.MOD: lambda x, y: x % y,
    cwast.BINARY_EXPR_KIND.SHL: lambda x, y: x << y,
    cwast.BINARY_EXPR_KIND.SHR: lambda x, y: x >> y,
}

_EVAL_UINT_OR_BOOL = {
    cwast.BINARY_EXPR_KIND.OR: lambda x, y: x | y,
    cwast.BINARY_EXPR_KIND.AND: lambda x, y: x & y,
    cwast.BINARY_EXPR_KIND.XOR: lambda x, y: x ^ y,
}

_EVAL_BOOL = _EVAL_EQ_NE | _EVAL_UINT_OR_BOOL
_EVAL_SINT = _EVAL_CMP | _EVAL_INT
_EVAL_UINT = _EVAL_CMP | _EVAL_INT | _EVAL_UINT_OR_BOOL
_EVAL_REAL = _EVAL_CMP | _EVAL_ADD_SUB_MUL | {
    cwast.BINARY_EXPR_KIND.DIV: lambda x, y: x / y,
}


def _HandleUintOverflow(kind: cwast.BASE_TYPE_KIND, val: int) -> int:
    mask = (1 << (8 * cwast.BASE_TYPE_KIND_TO_SIZE[kind])) - 1
    return val & mask


def _EvalExpr2(node: cwast.Expr2) -> bool:
    e1 = node.expr1.x_value
    e2 = node.expr2.x_value
    op = node.binary_expr_kind
    if e1 is None or e2 is None:
        return False
    ct = node.x_type
    bt = ct.base_type_kind
    ct_operand = node.expr1.x_type
    if ct_operand.is_pointer() or ct_operand.is_fun():
        return _AssignValue(node,  EvalNum(_EVAL_EQ_NE[op](e1, e2), bt))
    assert isinstance(e1, EvalNum) and isinstance(e2, EvalNum)
    e1 = e1.val
    e2 = e2.val
    bt_operand = ct_operand.base_type_kind
    if bt_operand.IsUint():
        v = _EVAL_UINT[op](e1, e2)
        if bt != cwast.BASE_TYPE_KIND.BOOL:
            v = _HandleUintOverflow(bt_operand, v)
        return _AssignValue(node, EvalNum(v, bt))
    elif bt_operand.IsSint():
        return _AssignValue(node, EvalNum(_EVAL_SINT[op](e1, e2), bt))
    elif bt_operand.IsReal():
        return _AssignValue(node,  EvalNum(_EVAL_REAL[op](e1, e2), bt))
    elif bt_operand == cwast.BASE_TYPE_KIND.BOOL:
        return _AssignValue(node,  EvalNum(_EVAL_BOOL[op](e1, e2), bt))
    else:
        assert False, f"unexpected type {ct_operand}"


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


def _GetValForAuto(node: cwast.ValAuto) -> bool:
    ct: cwast.CanonType = node.x_type
    if ct.is_rec():
        return VAL_ZERO_COMPOUND
    elif ct.is_vec():
        return VAL_ZERO_COMPOUND
    elif ct.is_base_type():
        return GetDefaultForBaseType(ct.base_type_kind)
    return None


def _GetValForVecAtPos(container, index: int):
    if isinstance(container, cwast.ValAuto):
        return GetDefaultForType(container.x_type.underlying_type())

    val = container.x_value
    if isinstance(val, EvalCompound):
        container = val.compound

        if isinstance(container, cwast.ValString):

            s = container.get_bytes()
            assert index < len(s)
            return EvalNum(s[index], cwast.BASE_TYPE_KIND.U8)

        if isinstance(val, EvalCompound):
            container = val.compound
            assert isinstance(container, cwast.ValCompound), f"{container}"
            assert index < container.x_type.array_dim()
            n = 0
            for point in container.inits:
                if isinstance(point.point_or_undef, cwast.ValNum):
                    assert isinstance(point.point_or_undef.x_value, EvalNum)
                    n = point.point_or_undef.x_value.val
                if n == index:
                    return point.value_or_undef.x_value
                if n > index:

                    return GetDefaultForType(container.x_type.underlying_type())
                n += 1
    return None


def _GetValForRecAtField(container, field):
    if isinstance(container, cwast.ValAuto):
        return GetDefaultForType(field.x_symbol.x_type)

    val = container.x_value
    if isinstance(val, EvalCompound):
        val = val.compound
        for rec_field, init in symbolize.IterateValRec(val.inits, val.x_type):
            if field.x_symbol == rec_field:
                if init:
                    return init.x_value
                else:
                    return GetDefaultForType(field.x_type)
        assert False
    return None


def _EvalNode(node: cwast.NODES_EXPR_T) -> bool:
    """Returns True if node could be evaluated."""

    if isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert def_node is not None, f"{node}"
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            if def_node.x_value is not None:
                assert not def_node.mut
            return _AssignValue(node, def_node.x_value)
        elif isinstance(def_node, cwast.EnumVal):
            return _AssignValue(node, def_node.value_or_auto.x_value)
        elif isinstance(def_node, cwast.DefFun):
            return _AssignValue(node, EvalFunAddr(def_node))
        return False
    elif isinstance(node, cwast.EnumVal):
        return False  # handles as part of DefEnum
    elif isinstance(node, cwast.DefEnum):
        return _EvalDefEnum(node)
    elif isinstance(node, cwast.ValTrue):
        return _AssignValue(node, VAL_TRUE)
    if isinstance(node, cwast.ValFalse):
        return _AssignValue(node, VAL_FALSE)
    elif isinstance(node, cwast.ValVoid):
        return _AssignValue(node, VAL_VOID)
    elif isinstance(node, cwast.ValUndef):
        return _AssignValue(node, VAL_UNDEF)
    elif isinstance(node, cwast.ValNum):
        ct: cwast.CanonType = node.x_type
        if ct.is_base_type() or ct.is_enum():
            bt = ct.base_type_kind
            return _AssignValue(node, EvalNum(typify.ParseNum(node, bt), bt))
        else:
            assert False, f"unepxected type for ValNum: {ct}"
            return False
    elif isinstance(node, cwast.ValAuto):
        # we do not evaluate this during the recursion
        # Instead we evaluate this inside DefGlobal, DefVar, DefEnum
        return False
    elif isinstance(node, cwast.ValPoint):
        val = _EvalValWithPossibleImplicitConversion(
            node.x_type, node.value_or_undef)
        return _AssignValue(node, val)
    elif isinstance(node, cwast.ValCompound):
        return _AssignValue(node, EvalCompound(node))
    elif isinstance(node, cwast.ValString):
        return _AssignValue(node, EvalCompound(node))
    elif isinstance(node, cwast.ExprIndex):
        index_val = node.expr_index.x_value
        if index_val is None:
            return False
        val = _GetValForVecAtPos(node.container, index_val.val)
        if val is None:
            return False
        return _AssignValue(node, val)
    elif isinstance(node, cwast.ExprField):
        val = _GetValForRecAtField(node.container, node.field)
        if val is None:
            return False
        return _AssignValue(node, val)
    elif isinstance(node, cwast.Expr1):
        return _EvalExpr1(node)
    elif isinstance(node, cwast.Expr2):
        return _EvalExpr2(node)
    elif isinstance(node, cwast.Expr3):
        return _EvalExpr3(node)
    elif isinstance(node, cwast.ExprTypeId):
        typeid = node.type.x_type.get_original_typeid()
        assert typeid >= 0
        return _AssignValue(node, EvalNum(typeid, node.x_type.base_type_kind))
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
            return _AssignValue(node, VAL_TRUE)
        if expr_ct.is_tagged_union():
            if test_ct.is_tagged_union():
                test_elements = set(
                    [x.name for x in test_ct.union_member_types()])
                expr_elements = set(
                    [x.name for x in expr_ct.union_member_types()])
                if expr_elements.issubset(test_elements):
                    return _AssignValue(node, VAL_TRUE)
                return False
            else:
                return False
        elif test_ct.is_tagged_union():
            test_elements = set(
                [x.name for x in test_ct.union_member_types()])
            return _AssignValue(node, expr_ct.name in test_elements)
        else:
            return _AssignValue(node, VAL_FALSE)
    elif isinstance(node, cwast.ExprPointer):
        # TODO: we can do better here
        return False
    elif isinstance(node, cwast.ExprFront):
        container = node.container
        ct_container = container.x_type
        val = None
        if ct_container.is_vec():
            if isinstance(container, cwast.Id):
                val = EvalSymAddr(container.x_symbol)
        else:
            assert ct_container.is_span()
            v_container = container.x_value
            if v_container is not None and v_container.pointer is not None:
                assert isinstance(v_container, EvalSpan), f"{v_container}"
                val = EvalSymAddr(v_container.pointer)
        return _AssignValue(node, val)
    elif isinstance(node, cwast.ExprLen):
        container = node.container
        bt = container.x_type.base_type_kind
        val = None
        if container.x_type.is_vec():
            val = EvalNum(container.x_type.array_dim(), bt)
        elif isinstance(container.x_value, EvalSpan) and container.x_value.size is not None:
            val = EvalNum(container.x_value.size, bt)
        return _AssignValue(node, val)
    elif isinstance(node, cwast.ExprAddrOf):
        if isinstance(node.expr_lhs, cwast.Id):
            return _AssignValue(node, EvalSymAddr(node.expr_lhs.x_symbol))
        return False
    elif isinstance(node, cwast.ExprOffsetof):
        # assert node.x_field.x_offset > 0
        return _AssignValue(node, EvalNum(node.field.x_symbol.x_offset,
                                          node.x_type.base_type_kind))
    elif isinstance(node, cwast.ExprSizeof):
        return _AssignValue(node, EvalNum(node.type.x_type.size, node.x_type.base_type_kind))
    elif isinstance(node, cwast.ExprDeref):
        # TODO maybe track symbolic addresses
        return False
    elif isinstance(node, cwast.ValSpan):
        p = node.pointer.x_value
        s = node.expr_size.x_value
        if p is None and s is None:
            return False
        if p:
            assert isinstance(p, EvalSymAddr)
            p = p.sym
        if s:
            assert isinstance(s, EvalNum)
            s = s.val
        return _AssignValue(node, EvalSpan(p, s))
    elif isinstance(node, cwast.ExprUnionTag):
        return False
    elif isinstance(node, cwast.ExprParen):
        if _EvalNode(node.expr):
            return _AssignValue(node, node.expr.x_value)
        return False
    else:
        assert False, f"unexpected node {node}"


def _EvalValWithPossibleImplicitConversion(dst_type: cwast.CanonType,
                                           src_node):
    src_type: cwast.CanonType = dst_type if isinstance(
        src_node, cwast.ValUndef) else src_node.x_type
    src_value = src_node.x_value
    if type_corpus.IsSameTypeExceptMut(src_type, dst_type):
        return src_value

    if src_type.is_vec() and dst_type.is_span():
        if src_value is None:
            return EvalSpan(None, src_type.array_dim(), None)
        else:
            assert isinstance(src_value, EvalCompound)
            return EvalSpan(src_value.sym, src_type.array_dim(), src_value)
    elif src_value is None:
        return None
    # assert False, f"{src_node}: {src_node.x_type} -> {dst_type} [{src_value}]"
    return None


def EvalRecursively(node) -> bool:
    seen_change = False

    def visitor(node):
        nonlocal seen_change
        if cwast.NF.VALUE_ANNOTATED not in node.FLAGS:
            return
        if node.x_value is not None:
            return
        if isinstance(node, (cwast.DefGlobal, cwast.DefVar)):
            initial = node.initial_or_undef_or_auto
            if initial.x_value is None and isinstance(initial, cwast.ValAuto):
                # ValAuto has differernt meanings in different context
                # so we deal with it explicity here and elsewhere
                val = _GetValForAuto(initial)
                seen_change |= _AssignValue(initial, val)
            if node.mut:
                return
            val = _EvalValWithPossibleImplicitConversion(
                node.x_type, initial)
            if val is not None:
                seen_change |= _AssignValue(node, val)
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
            if node.cond.x_value is None:
                cwast.CompilerError(
                    node.x_srcloc, f"Cannot evaluate static assert: {node}")

            if node.cond.x_value.val is not True:
                cwast.CompilerError(
                    node.x_srcloc, f"Failed static assert: {node} is {node.cond.x_value}")

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            # we must be able to initialize data these at compile time
            is_const = isinstance(
                node, (cwast.DefGlobal, cwast.DefEnum))
            return

        if isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValNum)):
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
                            pass
                            # TODO
                            # cwast.CompilerError(def_node.x_srcloc,
                            #                    f"expected const node: {node} inside: {parent}")
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
                    elif isinstance(node, cwast.ValAuto):
                        pass
                    else:
                        pass
                        # TODO
                        # cwast.CompilerError(
                        #    node.x_srcloc, f"expected const node: {node} "
                        #    f"of type {node.x_type} inside {parent}")

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
    macro.ExpandMacrosAndMacroLike(mp.mods_in_topo_order)
    symbolize.SetTargetFields(mp.mods_in_topo_order)
    symbolize.ResolveSymbolsInsideFunctions(
        mp.mods_in_topo_order, mp.builtin_symtab)
    for mod in mp.mods_in_topo_order:
        symbolize.VerifySymbols(mod)
    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    typify.AddTypesToAst(mp.mods_in_topo_order, tc)
    DecorateASTWithPartialEvaluation(mp.mods_in_topo_order)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
