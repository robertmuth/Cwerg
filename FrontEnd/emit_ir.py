#!/usr/bin/python3

"""Translator from AST to Cwerg IR"""

import logging
import argparse
import dataclasses
import enum
import struct

from typing import Union, Any, Optional, List

from Util.parse import BytesToEscapedString

from FrontEnd import canonicalize_large_args
from FrontEnd import canonicalize_slice
from FrontEnd import canonicalize_sum
from FrontEnd import canonicalize
from FrontEnd import symbolize
from FrontEnd import type_corpus
from FrontEnd import cwast
from FrontEnd import typify
from FrontEnd import eval
from FrontEnd import identifier
from FrontEnd import parse
from FrontEnd import pp


logger = logging.getLogger(__name__)

TAB = "  "

ZEROS = [b"\0" * i for i in range(128)]


_DUMMY_VOID_REG = "@DUMMY_FOR_VOID_RESULTS@"


@enum.unique
class STORAGE_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = enum.auto()
    REGISTER = enum.auto()
    STACK = enum.auto()
    DATA = enum.auto()


def _IsDefVarOnStack(node: cwast.DefVar) -> bool:
    if node.ref:
        return True
    return not node.type_or_auto.x_type.fits_in_register()


def _StorageForId(node: cwast.Id) -> STORAGE_KIND:
    def_node = node.x_symbol
    if isinstance(def_node, cwast.DefGlobal):
        return STORAGE_KIND.DATA
    if isinstance(def_node, cwast.FunParam):
        return STORAGE_KIND.REGISTER
    elif isinstance(def_node, cwast.DefVar):
        return STORAGE_KIND.STACK if _IsDefVarOnStack(def_node) else STORAGE_KIND.REGISTER
    else:
        assert False, f"Unexpected ID {def_node}"


@dataclasses.dataclass()
class BaseOffset:
    """Represents and address as pair of base and offset"""
    base: str
    offset: Any


@dataclasses.dataclass()
class ReturnResultLocation:
    """Where to store a return expression

    if type is str, the result must fit into a register whose name is provide.
    Otherwise the result is to be copied into the memory location provided.
    """
    dst: Union[str, BaseOffset]


def _InitDataForBaseType(x_type: cwast.CanonType, x_value) -> bytes:
    assert x_type.is_base_or_enum_type()
    byte_width = x_type.size
    if x_value is None or isinstance(x_value, cwast.ValUndef):
        return ZEROS[byte_width]
    elif x_type.is_uint():
        return x_value.to_bytes(byte_width, 'little')
    elif x_type.is_sint():
        return x_value.to_bytes(byte_width, 'little', signed=True)
    elif x_type.is_bool():
        return b"\1" if x_value else b"\0"
    elif x_type.is_real():
        fmt = "f" if x_type.base_type_kind is cwast.BASE_TYPE_KIND.R32 else "d"
        return struct.pack(fmt, x_value)
    else:
        assert False, f"unsupported type {x_type}"


def RenderList(items):
    return "[" + " ".join(items) + "]"


def _EmitFunctionHeader(fun: cwast.DefFun):
    sig: cwast.TypeFun = fun.x_type
    ins = []
    for p in sig.parameter_types():
        #
        ins += p.register_types
    result = ""
    if not sig.result_type().is_void():
        result = sig.result_type().get_single_register_type()
    print(
        f"\n\n.fun {fun.name} NORMAL [{result}] = [{' '.join(ins)}]")


def _EmitFunctionProlog(fun: cwast.DefFun,
                        id_gen: identifier.IdGen):
    print(f".bbl {id_gen.NewName('entry')}")
    for p in fun.params:
        # this uniquifies names
        p.name = id_gen.NewName(p.name)
        reg_types = p.type.x_type.register_types
        if len(reg_types) == 1:
            print(f"{TAB}poparg {p.name}:{reg_types[0]}")
        else:
            assert False
            assert len(reg_types) == 2
            print(f"{TAB}poparg {p.name}..1:{reg_types[0]}")
            print(f"{TAB}poparg {p.name}..2:{reg_types[1]}")


def RLE(data: bytes):
    last = None
    count = 0
    for d in data:
        if d != last:
            if last is not None:
                yield count, last
            last = d
            count = 1
        else:
            count += 1
    else:
        yield count, last


def is_repeated_single_char(data: bytes):
    c = data[0]
    for x in data:
        if x != c:
            return False
    return True


ZERO_INDEX = "0"


def OffsetScaleToOffset(offset_expr, scale: int, tc: type_corpus.TypeCorpus,
                        id_gen: identifier.IdGenIR) -> BaseOffset:
    if offset_expr.x_value is not None:
        return offset_expr.x_value * scale
    else:
        offset = EmitIRExpr(offset_expr, tc, id_gen)
        if scale == 1:
            return offset
        scaled = id_gen.NewName("scaled")
        sint_type = tc.get_sint_canon_type()
        print(
            f"{TAB}conv {scaled}:{sint_type.get_single_register_type()} = {offset}")
        print(
            f"{TAB}mul {scaled} = {scaled} {scale}")
        return scaled


def _GetLValueAddressAsBaseOffset(node, tc: type_corpus.TypeCorpus,
                                  id_gen: identifier.IdGenIR) -> BaseOffset:
    if isinstance(node, cwast.ExprIndex):
        x_type: cwast.CanonType = node.container.x_type
        assert x_type.is_array(), f"{x_type}"
        base = _GetLValueAddress(node.container, tc, id_gen)
        offset = OffsetScaleToOffset(node.expr_index, x_type.underlying_array_type().size,
                                     tc, id_gen)
        return BaseOffset(base, offset)

    elif isinstance(node, cwast.ExprDeref):
        return BaseOffset(EmitIRExpr(node.expr, tc, id_gen), 0)
    elif isinstance(node, cwast.ExprField):
        base = _GetLValueAddress(node.container, tc, id_gen)
        offset = node.x_field.x_offset
        return BaseOffset(base, offset)
    elif isinstance(node, cwast.Id):
        name = node.x_symbol.name
        base = id_gen.NewName(f"lhsaddr_{name}")
        kind = tc.get_data_address_reg_type()
        storage = _StorageForId(node)
        if storage is STORAGE_KIND.DATA:
            print(f"{TAB}lea.mem {base}:{kind} = {name} 0")
        elif storage is STORAGE_KIND.STACK:
            print(f"{TAB}lea.stk {base}:{kind} = {name} 0")
        else:
            assert False, f"unsupported storage class {storage}"
        return BaseOffset(base, 0)
    elif isinstance(node, cwast.ExprAs):
        assert node.expr.x_type.is_untagged_sum()
        base = _GetLValueAddress(node.expr, tc, id_gen)
        return BaseOffset(base, 0)
    else:
        assert False, f"unsupported node for lvalue {node}"


def _GetLValueAddress(node, tc: type_corpus.TypeCorpus, id_gen: identifier.IdGenIR) -> str:
    bo = _GetLValueAddressAsBaseOffset(node, tc, id_gen)
    if bo.offset == 0:
        return bo.base
    else:
        res = id_gen.NewName("at")
        kind = tc.get_data_address_reg_type()
        print(f"{TAB}lea {res}:{kind} = {bo.base} {bo.offset}")
        return res


_MAP_COMPARE = {
    cwast.BINARY_EXPR_KIND.NE: "bne",
    cwast.BINARY_EXPR_KIND.EQ: "beq",
    cwast.BINARY_EXPR_KIND.LT: "blt",
    cwast.BINARY_EXPR_KIND.LE: "ble",
}

_MAP_COMPARE_INVERT = {
    cwast.BINARY_EXPR_KIND.NE: cwast.BINARY_EXPR_KIND.EQ,
    cwast.BINARY_EXPR_KIND.EQ:  cwast.BINARY_EXPR_KIND.NE,
    cwast.BINARY_EXPR_KIND.LT: cwast.BINARY_EXPR_KIND.GE,
    cwast.BINARY_EXPR_KIND.LE: cwast.BINARY_EXPR_KIND.GT,
    cwast.BINARY_EXPR_KIND.GT:  cwast.BINARY_EXPR_KIND.LE,
    cwast.BINARY_EXPR_KIND.GE:  cwast.BINARY_EXPR_KIND.LT,
}


def IsUnconditionalBranch(node):
    if cwast.NF.CONTROL_FLOW not in node.FLAGS:
        return False
    return not isinstance(node, cwast.StmtReturn) or isinstance(node.x_target, cwast.DefFun)


def EmitIRConditional(cond, invert: bool, label_false: str, tc: type_corpus.TypeCorpus,
                      id_gen: identifier.IdGenIR):
    """The emitted code assumes that the not taken label immediately succceeds the code generated here"""
    if cond.x_value is True:
        if not invert:
            print(f"{TAB}bra {label_false}")
    elif cond.x_value is False:
        if invert:
            print(f"{TAB}bra {label_false}")
    elif isinstance(cond, cwast.Expr1):
        assert cond.unary_expr_kind is cwast.UNARY_EXPR_KIND.NOT
        EmitIRConditional(cond.expr, not invert, label_false, tc, id_gen)
    elif isinstance(cond, cwast.Expr2):
        kind = cond.binary_expr_kind
        if kind is cwast.BINARY_EXPR_KIND.ANDSC:
            if invert:
                EmitIRConditional(cond.expr1, True, label_false, tc, id_gen)
                EmitIRConditional(cond.expr2, True, label_false, tc, id_gen)
            else:
                failed = id_gen.NewName("br_failed_and")
                EmitIRConditional(cond.expr1, True, failed, tc, id_gen)
                EmitIRConditional(cond.expr2, False, label_false, tc, id_gen)
                print(f".bbl {failed}")
        elif kind is cwast.BINARY_EXPR_KIND.ORSC:
            if invert:
                failed = id_gen.NewName("br_failed_or")
                EmitIRConditional(cond.expr1, False, failed, tc, id_gen)
                EmitIRConditional(cond.expr2, True, label_false, tc, id_gen)
                print(f".bbl {failed}")
            else:
                EmitIRConditional(cond.expr1, False, label_false, tc, id_gen)
                EmitIRConditional(cond.expr2, False, label_false, tc, id_gen)
        else:
            op1 = EmitIRExpr(cond.expr1, tc, id_gen)
            op2 = EmitIRExpr(cond.expr2, tc, id_gen)

            if invert:
                kind = _MAP_COMPARE_INVERT[kind]
            # reduce comparison to what can be easily tranalate IR

            if kind is cwast.BINARY_EXPR_KIND.GT:
                kind = cwast.BINARY_EXPR_KIND.LT
                op1, op2 = op2, op1
            elif kind is cwast.BINARY_EXPR_KIND.GE:
                kind = cwast.BINARY_EXPR_KIND.LE
                op1, op2 = op2, op1
            print(
                f"{TAB}{_MAP_COMPARE[kind]} {op1} {op2} {label_false}  # {cond}")
    elif isinstance(cond, (cwast.ExprCall, cwast.ExprStmt)):
        op = EmitIRExpr(cond, tc, id_gen)
        if invert:
            print(f"{TAB}beq {op} 0 {label_false}")
        else:
            print(f"{TAB}bne {op} 0 {label_false}")
    elif isinstance(cond, cwast.Id):
        assert cond.x_type.is_bool()
        assert isinstance(cond.x_symbol, (cwast.DefVar, cwast.FunParam))
        if invert:
            print(f"{TAB}beq {cond.name} 0 {label_false}")
        else:
            print(f"{TAB}bne {cond.name} 0 {label_false}")
    else:
        assert False, f"unexpected expression {cond}"


_BIN_OP_MAP = {
    cwast.BINARY_EXPR_KIND.MUL: "mul",
    cwast.BINARY_EXPR_KIND.ADD: "add",
    cwast.BINARY_EXPR_KIND.SUB: "sub",
    cwast.BINARY_EXPR_KIND.DIV: "div",
    cwast.BINARY_EXPR_KIND.REM: "rem",
    cwast.BINARY_EXPR_KIND.SHL: "shl",
    cwast.BINARY_EXPR_KIND.SHR: "shr",
    cwast.BINARY_EXPR_KIND.XOR: "xor",
    cwast.BINARY_EXPR_KIND.OR: "or",
    cwast.BINARY_EXPR_KIND.AND: "and",
}


def _EmitExpr2(kind: cwast.BINARY_EXPR_KIND, res, ct: cwast.CanonType, op1, op2):
    res_type = ct.get_single_register_type()
    op = _BIN_OP_MAP.get(kind)
    if op is not None:
        print(
            f"{TAB}{op} {res}:{res_type} = {op1} {op2}")
    elif kind is cwast.BINARY_EXPR_KIND.MAX:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op2} {op1}")
    elif kind is cwast.BINARY_EXPR_KIND.MIN:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op1} {op2}")
    else:
        assert False, f"unsupported expression {kind}"


def _EmitExpr1(kind: cwast.UNARY_EXPR_KIND, res, ct: cwast.CanonType, op):
    res_type = ct.get_single_register_type()
    ff = (1 << (8 * cwast.BASE_TYPE_KIND_TO_SIZE[ct.base_type_kind])) - 1
    if kind is cwast.UNARY_EXPR_KIND.MINUS:
        print(f"{TAB}sub {res}:{res_type} = 0 {op}")
    elif kind is cwast.UNARY_EXPR_KIND.NOT:
        print(f"{TAB}xor {res}:{res_type} = 0x{ff:x} {op}")
    else:
        assert False, f"unsupported expression {kind}"


def EmitIRExpr(node, tc: type_corpus.TypeCorpus, id_gen: identifier.IdGenIR) -> Any:
    ct_dst: cwast.CanonType = node.x_type
    assert ct_dst.is_void_or_wrapped_void() or ct_dst.fits_in_register()
    if isinstance(node, cwast.ExprCall):
        sig: cwast.CanonType = node.callee.x_type
        assert sig.is_fun()
        args = [EmitIRExpr(a, tc, id_gen) for a in node.args]
        for a in reversed(args):
            assert not a.startswith("["), f"{a} {node.args[4]}"
            print(f"{TAB}pusharg {a}")
        if isinstance(node.callee, cwast.Id):
            print(f"{TAB}bsr {node.callee.x_symbol.name}")
        else:
            assert False
        if sig.result_type().is_void():
            return None
        else:
            res = id_gen.NewName("call")
            print(f"{TAB}poparg {res}:{sig.result_type().get_single_register_type()}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{node.x_value}:{node.x_type.get_single_register_type()}"
    elif isinstance(node, cwast.ValFalse):
        return "0:U8"
    elif isinstance(node, cwast.ValTrue):
        return "1:U8"
    elif isinstance(node, cwast.Id):
        def_node = node.x_symbol
        if isinstance(def_node, cwast.DefGlobal):
            res = id_gen.NewName("globread")
            print(
                f"{TAB}ld.mem {res}:{node.x_type.get_single_register_type()} = {node.x_symbol.name} 0")
            return res
        else:
            return node.x_symbol.name
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr_lhs, tc, id_gen)
    elif isinstance(node, cwast.Expr1):
        op = EmitIRExpr(node.expr, tc, id_gen)
        res = id_gen.NewName("expr1")
        _EmitExpr1(node.unary_expr_kind, res, node.x_type, op)
        return res
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, tc, id_gen)
        op2 = EmitIRExpr(node.expr2, tc, id_gen)
        res = id_gen.NewName("expr2")
        _EmitExpr2(node.binary_expr_kind, res, node.x_type, op1, op2)
        return res
    elif isinstance(node, cwast.ExprPointer):
        base = EmitIRExpr(node.expr1, tc, id_gen)
        # TODO: add range check
        # assert isinstance(node.expr_bound_or_undef, cwast.ValUndef)
        res = id_gen.NewName("expr2")
        ct: cwast.CanonType = node.expr1.x_type
        if node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP:
            assert ct.is_pointer()
            offset = OffsetScaleToOffset(
                node.expr2, ct.underlying_pointer_type().size, tc, id_gen)
            kind = tc.get_data_address_reg_type()
            print(f"{TAB}lea {res}:{kind} = {base} {offset}")
        else:
            assert False, f"unsupported expression {node}"
        return res
    elif isinstance(node, cwast.ExprBitCast):
        res = id_gen.NewName("bitcast")
        expr = EmitIRExpr(node.expr, tc, id_gen)
        print(
            f"{TAB}bitcast {res}:{node.type.x_type.get_single_register_type()} = {expr}")
        return res
    elif isinstance(node, cwast.ExprAs):
        ct_src: cwast.CanonType = node.expr.x_type
        if ct_src.is_base_type() and ct_dst.is_base_type():
            # more compatibility checking needed
            expr = EmitIRExpr(node.expr, tc, id_gen)
            res = id_gen.NewName("as")
            print(
                f"{TAB}conv {res}:{ct_dst.get_single_register_type()} = {expr}")
            return res
        elif ct_src.is_wrapped() and ct_dst is ct_src.underlying_wrapped_type():
            # just ignore the wrapped type
            return EmitIRExpr(node.expr, tc, id_gen)
        elif ct_dst.is_wrapped() and ct_src is ct_dst.underlying_wrapped_type():
            # just ignore the wrapped type
            return EmitIRExpr(node.expr, tc, id_gen)
        elif ct_src.is_untagged_sum():
            addr = _GetLValueAddress(node.expr, tc, id_gen)
            res = id_gen.NewName("union_access")
            print(
                f"{TAB}ld {res}:{ct_dst.get_single_register_type()} = {addr} 0")
            return res
        else:
            assert False, f"unsupported cast {node.expr} ({ct_src.name}) -> {ct_dst.name}"
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, tc, id_gen)
        res = id_gen.NewName("deref")
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        if node.x_type.is_void_or_wrapped_void():
            result = _DUMMY_VOID_REG
        else:
            result = id_gen.NewName("expr")
            print(
                f"{TAB}.reg {node.x_type.get_single_register_type()} [{result}]")
        for c in node.body:
            EmitIRStmt(c, ReturnResultLocation(result), tc, id_gen)
        return result
    elif isinstance(node, cwast.ExprIndex):
        src = _GetLValueAddressAsBaseOffset(node, tc, id_gen)
        res = id_gen.NewName("at")
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {src.base} {src.offset}")
        return res
    elif isinstance(node, cwast.ExprFront):
        assert node.container.x_type.is_array(), f"unexpected {node}"
        return _GetLValueAddress(node.container, tc, id_gen)
    elif isinstance(node, cwast.ExprField):
        res = id_gen.NewName(f"field_{node.x_field.name}")
        addr = _GetLValueAddress(node.container, tc, id_gen)
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} {node.x_field.x_offset}")
        return res
    elif isinstance(node, cwast.ValVoid):
        pass
    else:
        assert False, f"unsupported expression {node.x_srcloc} {node}"


def _EmitZero(dst: BaseOffset, length, alignment,
              id_gen: identifier.IdGenIR):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        while curr + width <= length:
            print(f"{TAB}st {dst.base} {dst.offset + curr} = 0:U{width}")
            curr += width


def EmitIRExprToMemory(ct_target: cwast.CanonType, init_node, dst: BaseOffset,
                       tc: type_corpus.TypeCorpus,
                       id_gen: identifier.IdGenIR):
    if isinstance(init_node, (cwast.ExprCall, cwast.ValNum, cwast.ValFalse,
                              cwast.ValTrue, cwast.ExprLen, cwast.ExprAddrOf,
                              cwast.Expr2, cwast.ExprPointer, cwast.ExprBitCast,
                              cwast.ExprFront, cwast.ExprBitCast)):
        reg = EmitIRExpr(init_node, tc, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, cwast.ExprAs):
        if init_node.x_type.fits_in_register():
            # same as above
            reg = EmitIRExpr(init_node, tc, id_gen)
            print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
        elif init_node.x_type.is_untagged_sum() and init_node.expr.x_type.fits_in_register():
            reg = EmitIRExpr(init_node.expr, tc, id_gen)
            print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
        else:
            assert False, f"{init_node} {init_node.x_type}"
    elif isinstance(init_node, cwast.Id) and _StorageForId(init_node) is STORAGE_KIND.REGISTER:
        reg = EmitIRExpr(init_node, tc, id_gen)
        assert reg is not None
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, (cwast.Id, cwast.ExprDeref, cwast.ExprIndex, cwast.ExprField)):
        src_base = _GetLValueAddress(init_node, tc, id_gen)
        src_type = init_node.x_type
        _EmitCopy(dst, BaseOffset(
            src_base, 0), src_type.size, src_type.alignment, id_gen)
    elif isinstance(init_node, cwast.ExprStmt):
        for c in init_node.body:
            EmitIRStmt(c, ReturnResultLocation(dst), tc, id_gen)
    elif isinstance(init_node, cwast.ValRec):
        src_type = init_node.x_type
        for field, init in symbolize.IterateValRec(init_node.inits_field, src_type):
            if init is not None and not isinstance(init, cwast.ValUndef):
                EmitIRExprToMemory(field.type.x_type, init.value, BaseOffset(
                    dst.base, dst.offset+field.x_offset), tc, id_gen)
    elif isinstance(init_node, cwast.ValArray):
        for _, c in symbolize.IterateValArray(init_node, init_node.x_type.array_dim()):
            if c is None:
                continue
            if isinstance(c.value_or_undef, cwast.ValUndef):
                continue
            assert False
    elif isinstance(init_node, cwast.ValAuto):
        # TODO: check if auto is legit (maybe add a check for this in another phase)
        _EmitZero(dst, init_node.x_type.size,
                  init_node.x_type.alignment, id_gen)
    else:
        assert False, f"NYI: {init_node}"


def _AssignmentLhsIsInReg(lhs):
    if not isinstance(lhs, cwast.Id):
        return False
    def_node = lhs.x_symbol
    # TODO: support stack allocated objects
    if isinstance(def_node, cwast.DefGlobal):
        return False
    elif isinstance(def_node, cwast.FunParam):
        return True
    elif isinstance(def_node, cwast.DefVar):
        return not def_node.ref
    else:
        assert False, f"unpected lhs {lhs}"


def _EmitCopy(dst: BaseOffset, src: BaseOffset, length, alignment,
              id_gen: identifier.IdGenIR):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        tmp = id_gen.NewName(f"copy{width}")
        print(f"{TAB}.reg U{width*8} [{tmp}]")
        while curr + width <= length:
            print(f"{TAB}ld {tmp} = {src.base} {src.offset + curr}")
            print(f"{TAB}st {dst.base} {dst.offset + curr} = {tmp}")
            curr += width


def _EmitInitialization(dst: BaseOffset, src_init,  tc: type_corpus.TypeCorpus,
                        id_gen: identifier.IdGenIR):

    def emit_recursively(offset, init):
        nonlocal dst, tc, id_gen
        src_type: cwast.CanonType = init.x_type
        assert not isinstance(init, cwast.ValUndef)

        if isinstance(init, cwast.Id):
            storage = _StorageForId(init)
            if storage is STORAGE_KIND.REGISTER:
                res = EmitIRExpr(init, tc, id_gen)
                assert res is not None
                print(f"{TAB}st {dst.base} {offset} = {res}")
            else:
                src = _GetLValueAddressAsBaseOffset(init, tc, id_gen)
                _EmitCopy(BaseOffset(dst.base, offset), src,
                          src_type.size, src_type.alignment, id_gen)

        elif isinstance(init, cwast.ValRec):
            for field, init in symbolize.IterateValRec(init.inits_field, src_type):
                if init is not None and not isinstance(init, cwast.ValUndef):
                    emit_recursively(offset + field.x_offset, init.value)
        elif isinstance(init, (cwast.ExprAddrOf, cwast.ValNum, cwast.ExprCall, cwast.ExprStmt)):
            res = EmitIRExpr(init, tc, id_gen)
            assert res is not None
            print(f"{TAB}st {dst.base} {offset} = {res}")
        elif isinstance(init, cwast.ExprFront):
            assert init.container.x_type.is_array()
            res = _GetLValueAddress(init.container, tc, id_gen)
            print(f"{TAB}st {dst.base} {offset} = {res}")
        elif isinstance(init, cwast.ExprDeref):
            src = _GetLValueAddressAsBaseOffset(init, tc, id_gen)
            _EmitCopy(BaseOffset(dst.base, offset), src,
                      src_type.size, src_type.alignment, id_gen)
        else:
            assert False, f"{init.x_srcloc} {init} {src_type}"

    emit_recursively(dst.offset, src_init)


def EmitIRStmt(node, result: Optional[ReturnResultLocation], tc: type_corpus.TypeCorpus,
               id_gen: identifier.IdGenIR):
    if isinstance(node, cwast.DefVar):
        def_type: cwast.CanonType = node.type_or_auto.x_type
        # This uniquifies names
        node.name = id_gen.NewName(node.name)
        initial = node.initial_or_undef_or_auto
        if _IsDefVarOnStack(node):
            print(f"{TAB}.stk {node.name} {def_type.alignment} {def_type.size}")
            if not isinstance(initial, cwast.ValUndef):
                init_base = id_gen.NewName("init_base")
                kind = tc.get_data_address_reg_type()
                print(f"{TAB}lea.stk {init_base}:{kind} {node.name} 0")
                EmitIRExprToMemory(node.type_or_auto.x_type, initial,  BaseOffset(
                    init_base, 0), tc, id_gen)
        else:
            if isinstance(initial, cwast.ValUndef):
                print(
                    f"{TAB}.reg {def_type.get_single_register_type()} [{node.name}]")
            else:
                out = EmitIRExpr(initial, tc, id_gen)
                assert out is not None, f"Failure to gen code for {initial}"
                print(
                    f"{TAB}mov {node.name}:{def_type.get_single_register_type()} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        continue_label = id_gen.NewName(node.label)
        break_label = id_gen.NewName(node.label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}  # block start")
        for c in node.body:
            EmitIRStmt(c, result, tc, id_gen)
        print(f".bbl {break_label}  # block end")
    elif isinstance(node, cwast.StmtReturn):
        if isinstance(node.x_target, cwast.ExprStmt):
            if not node.expr_ret.x_type.is_void_or_wrapped_void():
                assert result is not None
                if isinstance(result.dst, str):
                    out = EmitIRExpr(node.expr_ret, tc, id_gen)
                    print(f"{TAB}mov {result.dst} {out}")
                else:
                    EmitIRExprToMemory(node.x_target.x_type, node.expr_ret, result.dst,
                                       tc, id_gen)
            else:
                EmitIRExpr(node.expr_ret, tc, id_gen)
        else:
            out = EmitIRExpr(node.expr_ret, tc, id_gen)
            if not node.expr_ret.x_type.is_void_or_wrapped_void():
                print(f"{TAB}pusharg {out}")
            print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label[1]
        print(f"{TAB}bra {block}  # break")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label[0]
        print(f"{TAB}bra {block}  # continue")
    elif isinstance(node, cwast.StmtExpr):
        EmitIRExpr(node.expr, tc, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_f = id_gen.NewName("br_f")
        label_join = id_gen.NewName("br_join")
        if node.body_t and node.body_f:
            EmitIRConditional(node.cond, True, label_f, tc, id_gen)
            for c in node.body_t:
                EmitIRStmt(c, result, tc, id_gen)
            if not IsUnconditionalBranch(node.body_t[-1]):
                print(f"{TAB}bra {label_join}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                EmitIRStmt(c, result, tc, id_gen)
            print(f".bbl {label_join}")
        elif node.body_t:
            EmitIRConditional(node.cond, True, label_join, tc, id_gen)
            for c in node.body_t:
                EmitIRStmt(c, result, tc, id_gen)
            print(f".bbl {label_join}")
        elif node.body_f:
            EmitIRConditional(node.cond, False, label_join, tc, id_gen)
            for c in node.body_f:
                EmitIRStmt(c, result, tc, id_gen)
            print(f".bbl {label_join}")
        else:
            EmitIRConditional(node.cond, False, label_join, tc, id_gen)
            print(f".bbl {label_join}")
    elif isinstance(node, cwast.StmtAssignment):
        if node.lhs.x_type.fits_in_register() and _AssignmentLhsIsInReg(node.lhs):
            out = EmitIRExpr(node.expr_rhs, tc, id_gen)
            print(f"{TAB}mov {node.lhs.x_symbol.name} = {out}  # {node}")
        else:
            lhs = _GetLValueAddressAsBaseOffset(node.lhs, tc, id_gen)
            EmitIRExprToMemory(node.lhs.x_type, node.expr_rhs, lhs, tc, id_gen)
    elif isinstance(node, cwast.StmtTrap):
        print(f"{TAB}trap")
    else:
        assert False, f"cannot generate code for {node}"


def _EmitMem(data, comment) -> int:
    if len(data) == 0:
        print(f'.data 0 []  # {comment}')
    elif is_repeated_single_char(data):
        print(f'.data {len(data)} [{data[0]}]  # {comment}')
    elif isinstance(data, (bytes, bytearray)):
        if len(data) < 100:
            print(f'.data 1 "{BytesToEscapedString(data)}"  # {comment}')
        else:
            for count, value in RLE(data):
                print(f".data {count} [{value}]  # {comment}")
    else:
        assert False
    return len(data)


_BYTE_UNDEF = b"\0"
_BYTE_PADDING = b"\x6f"


def EmitIRDefGlobal(node: cwast.DefGlobal, tc: type_corpus.TypeCorpus) -> int:
    def_type: cwast.CanonType = node.type_or_auto.x_type
    print(
        f"\n.mem {node.name} {def_type.alignment} {'RW' if node.mut else 'RO'}")

    def _emit_recursively(node, ct: cwast.CanonType, offset: int) -> int:
        assert offset == type_corpus.align(offset, ct.alignment)
        if isinstance(node, cwast.ValUndef):
            return _EmitMem(_BYTE_UNDEF * ct.size, f"{offset} undef={ct.name}")

        if isinstance(node, cwast.Id):
            node_def = node.x_symbol
            assert isinstance(node_def, cwast.DefGlobal)
            return _emit_recursively(node_def.initial_or_undef_or_auto, ct, offset)
        elif isinstance(node, cwast.ExprFront):
            # we need to emit an address
            assert isinstance(node.container, cwast.Id)
            name = node.container.x_symbol.name
            print(f".addr.mem {tc.get_address_size()} {name} 0")
            # assert False, f"{name} {node.container}"
            return tc.get_address_size()

        if ct.is_base_or_enum_type():
            return _EmitMem(_InitDataForBaseType(ct, node.x_value),  f"{offset} {ct.name}")
        elif ct.is_array():
            assert isinstance(
                node, (cwast.ValArray, cwast.ValString)), f"{node}"
            print(f"# array: {ct.name}")
            width = ct.array_dim()
            x_type = ct.underlying_array_type()
            if x_type.is_base_type():
                if isinstance(node.x_value, bytes):
                    assert len(
                        node.x_value) == width, f"length mismatch {len(node.x_value)} vs {width}"
                    return _EmitMem(node.x_value, f"{offset} {ct.name}")
                else:

                    x_value = node.x_value
                    assert x_type.is_base_type()
                    assert width == len(x_value), f"{width} vs {len(x_value)}"
                    out = bytearray()
                    for v in x_value:
                        out += _InitDataForBaseType(x_type, v)
                    return _EmitMem(out, ct.name)
            else:
                assert isinstance(node, cwast.ValArray), f"{node}"
                last = cwast.ValUndef()
                stride = ct.size // width
                assert stride * width == ct.size, f"{ct.size} {width}"
                for n, init in symbolize.IterateValArray(node, width):
                    if init is None:
                        count = _emit_recursively(
                            last, x_type, offset + n * stride)
                    else:
                        assert isinstance(init, cwast.IndexVal)
                        last = init.value_or_undef
                        count = _emit_recursively(
                            last, x_type, offset + n * stride)
                    if count != stride:
                        _EmitMem(_BYTE_PADDING * (stride - count),
                                 f"{stride - count} padding")
                return ct.size
        elif ct.is_rec():
            assert isinstance(node, cwast.ValRec)
            print(f"# record: {ct.name}")
            rel_off = 0
            for f, i in symbolize. IterateValRec(node.inits_field, ct):

                if f.x_offset > rel_off:
                    rel_off += _EmitMem(_BYTE_PADDING *
                                        (f.x_offset - rel_off), f"{offset+rel_off} padding")
                if i is not None and not isinstance(i.value, cwast.ValUndef):
                    rel_off += _emit_recursively(i.value,
                                                 f.type.x_type, offset + rel_off)
                else:
                    rel_off += _EmitMem(_BYTE_UNDEF * f.type.x_type.size,
                                        f.type.x_type.name)
            return rel_off

        else:
            assert False, f"unhandled node for DefGlobal: {node} {ct.name}"

    return _emit_recursively(node.initial_or_undef_or_auto,
                             node.type_or_auto.x_type, 0)


def EmitIRDefFun(node, tc: type_corpus.TypeCorpus, id_gen: identifier.IdGenIR):
    if not node.extern:
        _EmitFunctionHeader(node)
        _EmitFunctionProlog(node, id_gen)
        for c in node.body:
            EmitIRStmt(c, None, tc, id_gen)


def SanityCheckMods(phase_name: str, emit_ir: bool, mods: List[cwast.DefMod], tc,
                    eliminated_node_types, allow_type_auto=True,
                    allow_implicit_type_conversion=False):
    logger.info(phase_name)
    if emit_ir:
        for mod in mods:
            pp.PrettyPrintHTML(mod, tc)
            # pp.PrettyPrint(mod)
        exit(0)

    for mod in mods:
        cwast.CheckAST(mod, eliminated_node_types, allow_type_auto)
        symbolize.VerifyASTSymbolsRecursively(mod)
        typify.VerifyTypesRecursively(mod, tc, allow_implicit_type_conversion)
        eval.VerifyASTEvalsRecursively(mod)


ELIMIMATED_NODES = set()


def main():
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument(
        '-emit_ir', help='stop before emitting asm', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='an input source file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    # logger.setLevel(logging.INFO)
    logger.info("Start Parsing")
    asts = []
    for f in args.files:
        asts += parse.ReadModsFromStream(open(f, encoding="utf8"), f)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)

    ELIMIMATED_NODES.add(cwast.ExprParen)  # this needs more work

    for mod in mod_topo_order:
        cwast.CheckAST(mod, ELIMIMATED_NODES)

    logger.info("Expand macros and link most IDs to their definition")
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.DefMacro)
        cwast.StripFromListRecursively(mod, cwast.Import)

    ELIMIMATED_NODES.add(cwast.Import)
    ELIMIMATED_NODES.add(cwast.DefMacro)
    ELIMIMATED_NODES.add(cwast.MacroInvoke)
    ELIMIMATED_NODES.add(cwast.MacroId)
    ELIMIMATED_NODES.add(cwast.MacroVar)
    ELIMIMATED_NODES.add(cwast.MacroFor)
    ELIMIMATED_NODES.add(cwast.MacroParam)
    ELIMIMATED_NODES.add(cwast.ExprSrcLoc)
    ELIMIMATED_NODES.add(cwast.ExprStringify)
    ELIMIMATED_NODES.add(cwast.EphemeralList)
    ELIMIMATED_NODES.add(cwast.ModParam)

    for mod in mod_topo_order:
        cwast.CheckAST(mod, ELIMIMATED_NODES)

    logger.info("Typify the nodes")
    tc: type_corpus.TypeCorpus = type_corpus.TypeCorpus(
        type_corpus.STD_TARGET_X64)
    typify.DecorateASTWithTypes(mod_topo_order, tc)

    logger.info("partial eval and static assert validation")
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)

    ELIMIMATED_NODES.add(cwast.StmtStaticAssert)
    for mod in mod_topo_order:
        cwast.StripFromListRecursively(mod, cwast.StmtStaticAssert)

    SanityCheckMods("AST is now fully decorated", args.emit_ir and False,
                    mod_topo_order, tc, ELIMIMATED_NODES, 
                    allow_type_auto=False,
                    allow_implicit_type_conversion=True)

    logger.info("Legalize 1")
    mod_gen = cwast.DefMod("$generated", [], [],
                           x_srcloc=cwast.SRCLOC_GENERATED)
    id_gen_global = identifier.IdGen()
    str_val_map = {}
    # for key, val in fun_sigs_with_large_args.items():
    #    print (key.name, " -> ", val.name)
    for mod in mod_topo_order:
        canonicalize.ReplaceExprIndex(mod, tc)
        canonicalize.ReplaceConstExpr(mod)
        canonicalize.EliminateImplicitConversions(mod, tc)

        canonicalize_slice.ReplaceExplicitSliceCast(mod, tc)
        canonicalize.CanonicalizeDefer(mod, [])
        cwast.EliminateEphemeralsRecursively(mod)

    ELIMIMATED_NODES.add(cwast.ExprSizeof)
    ELIMIMATED_NODES.add(cwast.ExprOffsetof)
    ELIMIMATED_NODES.add(cwast.ExprIndex)
    ELIMIMATED_NODES.add(cwast.StmtDefer)

    SanityCheckMods("initial lowering", args.emit_ir and False,
                    mod_topo_order, tc, ELIMIMATED_NODES)

    logger.info("Legalize 2")
    for mod in mod_topo_order:
        canonicalize.OptimizeKnownConditionals(mod)
        canonicalize.CanonicalizeStringVal(mod, str_val_map, id_gen_global)
        for node in mod.body_mod:
            canonicalize.CanonicalizeTernaryOp(node, identifier.IdGen())
            if isinstance(node, cwast.DefFun) and not node.extern:
                canonicalize.AddMissingReturnStmts(node)

    ELIMIMATED_NODES.add(cwast.Expr3)
    mod_gen.body_mod += list(str_val_map.values())

    slice_to_struct_map = canonicalize_slice.MakeSliceTypeReplacementMap(
        mod_topo_order, tc)
    mod_gen.body_mod += [
        v for v in slice_to_struct_map.values() if isinstance(v, cwast.DefRec)]
    for mod in mod_topo_order:
        canonicalize_slice.ReplaceSlice(mod, slice_to_struct_map)
    ELIMIMATED_NODES.add(cwast.ExprLen)
    ELIMIMATED_NODES.add(cwast.ValSlice)
    ELIMIMATED_NODES.add(cwast.TypeSlice)

    sum_to_struct_map = canonicalize_sum.MakeSumTypeReplacementMap(
        mod_topo_order, tc)
    for mod in mod_topo_order:
        canonicalize_sum.ReplaceExplicitSumCast(mod, sum_to_struct_map, tc)
        canonicalize_sum.ReplaceSums(mod, sum_to_struct_map)

    SanityCheckMods("After slice elimination", args.emit_ir,
                    [mod_gen] + mod_topo_order, tc, ELIMIMATED_NODES)

    id_gens: Dict[cwast.Fun,  identifier.IdGen] = {}
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                id_gens[fun] = identifier.IdGen()

    logger.info("Canonicalization")
    fun_sigs_with_large_args = canonicalize_large_args.FindFunSigsWithLargeArgs(
        tc)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            id_gen = id_gens[fun]
            canonicalize_large_args.RewriteLargeArgsCallerSide(
                fun, fun_sigs_with_large_args, tc, id_gen)
            if fun.x_type in fun_sigs_with_large_args:
                canonicalize_large_args.RewriteLargeArgsCalleeSide(
                    fun, fun_sigs_with_large_args[fun.x_type], tc, id_gen)

    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue

            id_gen = id_gens[fun]
            # continue
            # why doing this so late?
            canonicalize.CanonicalizeBoolExpressionsNotUsedForConditionals(
                fun, tc)
            canonicalize.CanonicalizeTernaryOp(fun, id_gen)
            canonicalize.CanonicalizeCompoundAssignments(fun, id_gen)
            canonicalize.CanonicalizeRemoveStmtCond(fun)

    ELIMIMATED_NODES.add(cwast.StmtCompoundAssignment)
    ELIMIMATED_NODES.add(cwast.StmtCond)
    ELIMIMATED_NODES.add(cwast.Case)

    # TODO
    ELIMIMATED_NODES.add(cwast.ExprTypeId)

    for node in cwast.ALL_NODES:
        if cwast.NF.NON_CORE in node.FLAGS:
            assert node in ELIMIMATED_NODES, f"node: {node} must be eliminated before codegen"

    SanityCheckMods("After canonicalization", args.emit_ir and False,
                    [mod_gen] + mod_topo_order, tc, ELIMIMATED_NODES)

    mod_topo_order = [mod_gen] + mod_topo_order

    # Naming cleanup:
    # * Set fully qualified names for all module level symbols
    for mod in mod_topo_order:
        # when we emit Cwerg IR we use the "/" sepearator not "::" because
        # : is used for type annotations
        mod_name = "" if mod.name in ("main", "$builtin") else mod.name + "/"
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                suffix = ""
                if isinstance(node, (cwast.DefFun)) and node.polymorphic:
                    suffix = f"<{node.x_type.parameter_types()[0].name}>"
                node.name = mod_name + node.name + suffix

    SanityCheckMods("After slice elimination", args.emit_ir,
                    mod_topo_order, tc, ELIMIMATED_NODES)

    # Emit Cwert IR
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                EmitIRDefGlobal(node, tc)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                EmitIRDefFun(node, tc, identifier.IdGenIR())


if __name__ == "__main__":
    # import cProfile
    # cProfile.run('main()')
    exit(main())
