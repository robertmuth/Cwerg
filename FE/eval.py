#!/bin/env python3

"""Partial evaluator and value annotator for Cwerg AST

"""

import enum
import logging
import struct
from typing import Optional, Any, Union\

from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import typify
from FE import canonicalize


logger = logging.getLogger(__name__)


# use with cwast.ValNum if the value is defined by x_eval
EVAL_STR = "@eval"

class EvalBase:
    pass


class EvalUndef(EvalBase):
    def __init__(self):
        pass

    def __str__(self):
        return "EvalUndef"


class EvalVoid(EvalBase):
    def __init__(self):
        pass

    def __str__(self):
        return "EvalVoid"


class EvalSymAddr(EvalBase):
    def __init__(self, sym):
        assert isinstance(sym, (cwast.DefGlobal, cwast.DefVar)), f"{sym}"
        self.sym = sym

    def __eq__(self, other):
        if not isinstance(other, EvalSymAddr):
            return False
        return self.sym == other.sym

    def __str__(self):
        return f"EvalSymAddress[{self.sym.name}]"


class EvalFunAddr(EvalBase):
    def __init__(self, sym):
        assert isinstance(sym, cwast.DefFun)
        self.sym = sym

    def __eq__(self, other):
        if not isinstance(other, EvalFunAddr):
            return False
        return self.sym == other.sym

    def __str__(self):
        return f"EvalFunAddress[{self.sym.name}]"


class EvalCompound(EvalBase):
    def __init__(self, init_node, sym):
        # if compound is None, the default initialization is used
        if init_node is not None:
            assert isinstance(init_node, (cwast.ValString, cwast.ValCompound))
        self.init_node = init_node
        # if sym is not None it has been materialized as `sym`
        if sym is not None:
            assert isinstance(sym, (cwast.DefVar, cwast.DefGlobal))
        self.sym = sym

    def __str__(self):
        return "EvalCompound"


class EvalSpan(EvalBase):
    def __init__(self, pointer, size, content):
        assert pointer is None or isinstance(
            pointer, (cwast.DefGlobal, cwast.DefVar)), f"{pointer}"
        assert size is None or isinstance(size, int), f"{size}"
        self.pointer = pointer
        self.size = size
        self.content = content

    def __str__(self):
        return f"EvalSpan[{self.pointer}, {self.size}]"


class EvalNum(EvalBase):
    def __init__(self, val, kind: cwast.BASE_TYPE_KIND):
        assert isinstance(val, (int, float, bool)), f"{val}"
        assert isinstance(kind, cwast.BASE_TYPE_KIND)
        assert kind != cwast.BASE_TYPE_KIND.INVALID
        self.kind = kind
        self.val = val

    def __str__(self):
        return f"EvalNum[{self.val}]"


VAL_EMPTY_SPAN = EvalSpan(None, 0, None)
VAL_UNDEF = EvalUndef()
VAL_VOID = EvalVoid()
VAL_TRUE = EvalNum(True, cwast.BASE_TYPE_KIND.BOOL)
VAL_FALSE = EvalNum(False, cwast.BASE_TYPE_KIND.BOOL)


def SerializeBaseType(v: EvalNum) -> bytes:
    assert isinstance(v, EvalNum)
    bt = v.kind
    val = v.val
    if bt.IsInt():
        return val.to_bytes(bt.ByteSize(), 'little', signed=bt.IsSint())
    elif bt is cwast.BASE_TYPE_KIND.BOOL:
        return b"\1" if val else b"\0"
    elif bt is cwast.BASE_TYPE_KIND.R32:
        return struct.pack("f", val)
    elif bt is cwast.BASE_TYPE_KIND.R64:
        return struct.pack("d", val)
    else:
        assert False, f"unsupported type {bt} {val}"


def DeserializeBaseType(bt: cwast.BASE_TYPE_KIND, data: bytes) -> EvalNum:
    if bt.IsInt():
        val = int.from_bytes(data, 'little', signed=bt.IsSint())
    elif bt is cwast.BASE_TYPE_KIND.BOOL:
        val = True if int.from_bytes(data) else False
    elif bt is cwast.BASE_TYPE_KIND.R32:
        val = struct.unpack("f", data)[0]
    elif bt is cwast.BASE_TYPE_KIND.R64:
        val = struct.unpack("d", data)[0]
    else:
        assert False, f"unsupported type {bt} {data}"
    return EvalNum(val, bt)


def _AssignValue(node, val: EvalBase):
    assert isinstance(val, EvalBase), f"unexpected value {val} for {node}"
    logger.info("EVAL of %s: %s", node, val)
    node.x_eval = val


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
    assert cwast.NF.EVAL_ANNOTATED in node.FLAGS
    if isinstance(node, (cwast.ValString, cwast.ValVoid, cwast.ValUndef, cwast.ValNum)):
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
                    x_eval=def_node.initial_or_undef_or_auto.x_eval, x_symbol=def_node)


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

    def EliminateValStringAndValCompoundOutsideOfDefGlobal(self, node):
        # if we relace a node we do not need to recurse into the subtree
        cwast.MaybeReplaceAstRecursively(node, self._maybe_replace)

    def GetDefGlobals(self) -> list[cwast.DefGlobal]:
        return self._all_globals


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
    elif ct.is_unwrapped_complex():
        return EvalCompound(None, None)
    else:
        return None


def _EvalExpr1(node: cwast.Expr1) -> Optional[EvalBase]:
    e = node.expr.x_eval
    if e is None:
        return None
    e = e.val
    bt = node.x_type.base_type_kind
    op = node.unary_expr_kind
    if op == cwast.UNARY_EXPR_KIND.NOT:
        if bt == cwast.BASE_TYPE_KIND.BOOL:
            v = not e
        elif bt.IsUint():
            v = ~e & ((1 << (node.x_type.size * 8)) - 1)
        else:
            assert False
    elif op == cwast.UNARY_EXPR_KIND.NEG:
        assert bt.IsNumber()
        v = -e
    else:
        assert False
    return EvalNum(v, bt)


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
    mask = (1 << (8 * kind.ByteSize())) - 1
    return val & mask


def _EvalExpr2(node: cwast.Expr2) -> Optional[EvalBase]:
    e1 = node.expr1.x_eval
    e2 = node.expr2.x_eval
    op = node.binary_expr_kind
    if e1 is None or e2 is None:
        return None
    ct = node.x_type
    bt = ct.base_type_kind
    ct_operand = node.expr1.x_type
    if ct_operand.is_pointer() or ct_operand.is_fun():
        return EvalNum(_EVAL_EQ_NE[op](e1, e2), bt)
    # Note, we can compare pointers but there seem to few useful case
    # where we want to compare them at compile time.
    assert isinstance(e1, EvalNum) and isinstance(e2, EvalNum)
    e1 = e1.val
    e2 = e2.val
    bt_operand = ct_operand.base_type_kind
    if bt_operand.IsUint():
        v = _EVAL_UINT[op](e1, e2)
        if bt != cwast.BASE_TYPE_KIND.BOOL:
            v = _HandleUintOverflow(bt_operand, v)
        return EvalNum(v, bt)
    elif bt_operand.IsSint():
        return EvalNum(_EVAL_SINT[op](e1, e2), bt)
    elif bt_operand.IsReal():
        return EvalNum(_EVAL_REAL[op](e1, e2), bt)
    elif bt_operand == cwast.BASE_TYPE_KIND.BOOL:
        return EvalNum(_EVAL_BOOL[op](e1, e2), bt)
    else:
        assert False, f"unexpected type {ct_operand}"
        return None


def _GetValForVecAtPos(container_val, index: int, ct: cwast.CanonType):
    if isinstance(container_val, EvalSpan):
        container_val = container_val.content
        if container_val is None:
            return None

    assert isinstance(container_val, EvalCompound)
    init_node = container_val.init_node

    if init_node is None:
        return GetDefaultForType(ct)

    assert index < init_node.x_type.array_dim()

    if isinstance(init_node, cwast.ValString):
        s = init_node.get_bytes()
        assert index < len(s)
        return EvalNum(s[index], cwast.BASE_TYPE_KIND.U8)

    assert isinstance(init_node, cwast.ValCompound), f"{init_node}"
    n = 0
    for point in init_node.inits:
        if not isinstance(point.point_or_undef, cwast.ValUndef):
            assert isinstance(point.point_or_undef.x_eval, EvalNum)
            n = point.point_or_undef.x_eval.val
        if n == index:
            return point.value_or_undef.x_eval
        if n > index:
            break
        n += 1
    return GetDefaultForType(ct)


def _GetValForRecAtField(container_val, field: cwast.RecField):
    assert isinstance(container_val, EvalCompound)
    container_val = container_val.init_node
    if container_val is None:
        return GetDefaultForType(field.x_type)
    for rec_field, init in symbolize.IterateValRec(container_val.inits, container_val.x_type):
        if field == rec_field:
            if init:
                return init.x_eval
            else:
                return GetDefaultForType(field.x_type)
    assert False
    return None


def _EvalValWithPossibleImplicitConversion(dst_type: cwast.CanonType,
                                           src_node):
    src_value = src_node.x_eval
    if isinstance(src_node, cwast.ValUndef):
        return src_value
    src_type: cwast.CanonType = src_node.x_type
    if src_type is dst_type or type_corpus.IsDropMutConversion(src_type, dst_type):
        return src_value

    if type_corpus.IsVecToSpanConversion(src_type, dst_type):
        if src_value is None:
            return EvalSpan(None, src_type.array_dim(), None)
        else:
            assert isinstance(src_value, EvalCompound
                              ), f"{src_value} {src_node.x_srcloc}"
            return EvalSpan(src_value.sym, src_type.array_dim(), src_value)
    elif src_value is None:
        return None
    # assert False, f"{src_node}: {src_node.x_type} -> {dst_type} [{src_value}]"
    return src_value


def _EvalExprIs(node: cwast.ExprIs) -> Optional[EvalBase]:
    expr_ct: cwast.CanonType = node.expr.x_type
    test_ct: cwast.CanonType = node.type.x_type
    if expr_ct.get_original_typeid() == test_ct.get_original_typeid():
        return VAL_TRUE
    if expr_ct.is_tagged_union():
        if test_ct.is_tagged_union():
            test_elements = set(
                [x.name for x in test_ct.union_member_types()])
            expr_elements = set(
                [x.name for x in expr_ct.union_member_types()])
            if expr_elements.issubset(test_elements):
                return VAL_TRUE
        return None
    elif test_ct.is_tagged_union():
        test_elements = set(
            [x.name for x in test_ct.union_member_types()])
        return VAL_TRUE if expr_ct.name in test_elements else VAL_FALSE
    else:
        return VAL_FALSE


def _EvalNode(node: cwast.NODES_EXPR_T) -> Optional[EvalBase]:
    """Returns True if node could be evaluated."""

    if isinstance(node, cwast.Id):
        # this case is why we need the sym_tab
        def_node = node.x_symbol
        assert def_node is not None, f"{node}"
        if isinstance(def_node, (cwast.DefGlobal, cwast.DefVar)):
            if def_node.x_eval is not None:
                assert not def_node.mut
            return def_node.x_eval
        elif isinstance(def_node, cwast.EnumVal):
            return def_node.value_or_auto.x_eval
        elif isinstance(def_node, cwast.DefFun):
            return EvalFunAddr(def_node)
        return None
    elif isinstance(node, cwast.ValVoid):
        return VAL_VOID
    elif isinstance(node, cwast.ValUndef):
        return VAL_UNDEF
    elif isinstance(node, cwast.ValNum):
        # Note, later we use ValNum with other times
        # but at this point they are all of type TypeBase
        ct: cwast.CanonType = node.x_type
        assert ct.is_base_type()
        return EvalNum(typify.ParseNum(node), ct.base_type_kind)
    elif isinstance(node, cwast.ValPoint):
        return _EvalValWithPossibleImplicitConversion(
            node.x_type, node.value_or_undef)
    elif isinstance(node, (cwast.ValCompound, cwast.ValString)):
        return EvalCompound(node, None)
    elif isinstance(node, (cwast.DefGlobal, cwast.DefVar)):
        initial = node.initial_or_undef_or_auto
        if initial.x_eval is None and isinstance(initial, cwast.ValAuto):
            # ValAuto has differernt meanings in different context
            # so we deal with it explicity here and elsewhere
            _AssignValue(initial, GetDefaultForType(initial.x_type))
        if node.mut:
            return None
        val = _EvalValWithPossibleImplicitConversion(node.x_type, initial)
        if isinstance(val, EvalCompound):
            val = EvalCompound(val.init_node, node)
        return val
    elif isinstance(node, cwast.ExprIndex):
        index_val = node.expr_index.x_eval
        if index_val is None:
            return None
        container_val = node.container.x_eval
        if container_val is None:
            return None

        return _GetValForVecAtPos(container_val, index_val.val, node.x_type)
    elif isinstance(node, cwast.ExprField):
        container_val = node.container.x_eval
        if container_val is None:
            return None
        return _GetValForRecAtField(container_val, node.field.x_symbol)
    elif isinstance(node, cwast.Expr1):
        return _EvalExpr1(node)
    elif isinstance(node, cwast.Expr2):
        return _EvalExpr2(node)
    elif isinstance(node, cwast.Expr3):
        if node.cond.x_eval is not None:
            if node.cond.x_eval:
                return node.expr_t.x_eval
            else:
                return node.expr_f.x_eval
        return None
    elif isinstance(node, cwast.ExprTypeId):
        typeid = node.type.x_type.get_original_typeid()
        assert typeid >= 0
        return EvalNum(typeid, node.x_type.base_type_kind)
    elif isinstance(node, cwast.ExprAs):
        # TODO: some transforms may need to be applied, make sure it matches c++ version
        ct = node.x_type
        val = node.expr.x_eval
        if isinstance(val, EvalNum):
            new_bt = ct.get_unwrapped_base_type_kind()
            assert new_bt is not None, f"{node.expr.x_type} -> {ct.x_type}"
            return EvalNum(val.val, new_bt)
        elif isinstance(val, EvalVoid):
            return val
        return None
    elif isinstance(node, (cwast.ExprWrap, cwast.ExprNarrow, cwast.ExprWiden, cwast.ExprUnwrap)):
        return node.expr.x_eval
    elif isinstance(node, cwast.ExprIs):
        return _EvalExprIs(node)
    elif isinstance(node, cwast.ExprFront):
        cont = node.container
        ct_container = cont.x_type
        if ct_container.is_vec():
            if isinstance(cont, cwast.Id):
                return EvalSymAddr(cont.x_symbol)
        else:
            assert ct_container.is_span()
            val_cont = cont.x_eval
            if val_cont is not None and val_cont.pointer is not None:
                assert isinstance(val_cont, EvalSpan), f"{val_cont}"
                return EvalSymAddr(val_cont.pointer)
        return None
    elif isinstance(node, cwast.ExprLen):
        cont = node.container
        bt_src = node.x_type.base_type_kind
        if cont.x_type.is_vec():
            return EvalNum(cont.x_type.array_dim(), bt_src)
        elif isinstance(cont.x_eval, EvalSpan) and cont.x_eval.size is not None:
            return EvalNum(cont.x_eval.size, bt_src)
        return None
    elif isinstance(node, cwast.ExprAddrOf):
        if isinstance(node.expr_lhs, cwast.Id):
            return EvalSymAddr(node.expr_lhs.x_symbol)
        return None
    elif isinstance(node, cwast.ExprOffsetof):
        # assert node.x_field.x_offset > 0
        return EvalNum(node.field.x_symbol.x_offset, node.x_type.base_type_kind)
    elif isinstance(node, cwast.ExprSizeof):
        return EvalNum(node.type.x_type.size, node.x_type.base_type_kind)
    elif isinstance(node, cwast.ValSpan):
        p = node.pointer.x_eval
        s = node.expr_size.x_eval
        if p is None and s is None:
            return None
        if p:
            assert isinstance(p, EvalSymAddr)
            p = p.sym
        if s:
            assert isinstance(s, EvalNum)
            s = s.val
        return EvalSpan(p, s, None)
    elif isinstance(node, cwast.ExprParen):
        return node.expr.x_eval
    elif isinstance(node, cwast.DefEnum):
        bt_src = node.x_type.get_unwrapped_base_type_kind()
        val = None
        for c in node.items:
            if c.x_eval is not None:
                break

            assert isinstance(c, cwast.EnumVal)
            v = c.value_or_auto
            if isinstance(v, cwast.ValAuto):
                if val is None:
                    val = EvalNum(0, bt_src)
                else:
                    val = EvalNum(val.val + 1, bt_src)
            else:
                val = v.x_eval
            assert val
            _AssignValue(v, val)
            _AssignValue(c, val)
        return None
    elif isinstance(node, cwast.ExprCall):
        # TODO
        return None
    elif isinstance(node, cwast.ExprStmt):
        return None
    elif isinstance(node, cwast.ExprUnionUntagged):
        # TODO: we can do better here
        return None
    elif isinstance(node, cwast.ExprBitCast):
        val = node.expr.x_eval
        if val is None:
            return None
        if isinstance(val, EvalSymAddr):
            return val
        assert isinstance(val, EvalNum)
        assert node.expr.x_type.is_base_type(), f"{node.expr.x_type}"
        assert node.x_type.is_base_type(), f"{node.x_type}"
        data = SerializeBaseType(val)
        return DeserializeBaseType(node.x_type.base_type_kind, data)
    elif isinstance(node, cwast.ExprUnionTag):
        return None
    elif isinstance(node, cwast.ExprPointer):
        # TODO: we can do better here
        return None
    elif isinstance(node, cwast.ExprDeref):
        # TODO maybe track symbolic addresses
        return None
    elif isinstance(node, cwast.EnumVal):
        return None  # handles as part of DefEnum
    elif isinstance(node, cwast.ValAuto):
        # we do not evaluate this during the recursion
        # Instead we evaluate this inside DefGlobal, DefVar, DefEnum
        return None
    else:
        assert False, f"unexpected node {node}"
        return None


def EvalRecursively(node) -> bool:
    seen_change = False

    def visitor(node):
        nonlocal seen_change
        if cwast.NF.EVAL_ANNOTATED not in node.FLAGS:
            return
        if node.x_eval is not None:
            return
        val = _EvalNode(node)
        if val is not None:
            seen_change = True
            _AssignValue(node, val)
    cwast.VisitAstRecursivelyPost(node, visitor)

    if seen_change:
        logger.info("SEEN CHANGE %s", node)
    return seen_change


def VerifyASTEvalsRecursively(node):
    """Make sure that everything that is partial evaluated as expected.

    * sanity check EVAL_ANNOTATED nodes
    * check const nodes
    * check StaticAsserts"""
    is_const = False

    def visitor(node: Any, parent: Any):
        nonlocal is_const
        # logger.info(f"EVAL-VERIFY: {node}")
        if isinstance(node, cwast.ValUndef):
            return

        if isinstance(node, cwast.StmtStaticAssert):
            if node.cond.x_eval is None:
                cwast.CompilerError(
                    node.x_srcloc, f"Cannot evaluate static assert: {node}")

            if node.cond.x_eval.val is not True:
                cwast.CompilerError(
                    node.x_srcloc, f"Failed static assert: {node} is {node.cond.x_eval}")

        if cwast.NF.TOP_LEVEL in node.FLAGS:
            # we must be able to initialize data these at compile time
            is_const = isinstance(
                node, (cwast.DefGlobal, cwast.DefEnum))
            return

        if isinstance(node, cwast.ValNum):
            assert node.x_eval is not None, f"{node}"

        if is_const and cwast.NF.EVAL_ANNOTATED in node.FLAGS:
            if isinstance(node, cwast.Id):
                def_node = node.x_symbol
                if cwast.NF.EVAL_ANNOTATED in def_node.FLAGS:

                    if def_node.x_eval is None:
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
                if node.x_eval is None:
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
            assert node.size.x_eval is not None, f"uneval'ed type dim: {node}"

    cwast.VisitAstRecursivelyWithParent(node, visitor, None)

    def visitor2(node: Any, parent: Any):
        if cwast.NF.EVAL_ANNOTATED not in node.FLAGS:
            return
        val = node.x_eval
        if isinstance(node, (cwast.ValNum, cwast.EnumVal, cwast.ValAuto, cwast.ValUndef)):
            assert val is not None, f"NODE={node} {node.x_srcloc}  PARENT={parent}  {parent.x_srcloc}"
        if val is None:
            return
        assert isinstance(val, EvalBase), f"{node} <- {parent}"

    cwast.VisitAstRecursivelyWithParent(node, visitor2, None)


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
    for mod in mp.mods_in_topo_order:
        typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_WEAK)

    DecorateASTWithPartialEvaluation(mp.mods_in_topo_order)
    for mod in mp.mods_in_topo_order:
        VerifyASTEvalsRecursively(mod)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
