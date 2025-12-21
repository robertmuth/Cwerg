#!/bin/env python3

"""Translator from AST to Cwerg IR"""

import logging
import argparse
import dataclasses
import enum
import math
import pathlib
import os

from typing import Union, Any, Optional

from Util.parse import BytesToEscapedString

from FE import canonicalize_large_args
from FE import canonicalize_span
from FE import canonicalize_union
from FE import canonicalize
from FE import macro
from FE import symbolize
from FE import type_corpus
from FE import cwast
from FE import typify
from FE import eval
from FE import identifier
from FE import mod_pool
from FE import dead_code
from FE import optimize
from FE import stats
from FE import checker

logger = logging.getLogger(__name__)

TAB = "  "

ZEROS = [b"\0" * i for i in range(128)]


_DUMMY_VOID_REG = "@DUMMY_FOR_VOID_RESULTS@"


def _IterateValVec(points: list[cwast.ValPoint], dim, srcloc):
    """Pairs given ValPoints from a ValCompound repesenting a Vec with their indices"""
    curr_index = 0
    for init in points:
        if isinstance(init.point_or_undef, cwast.ValUndef):
            yield curr_index, init
            curr_index += 1
            continue
        index = init.point_or_undef.x_eval.val
        assert isinstance(index, int)
        while curr_index < index:
            yield curr_index, None
            curr_index += 1
        yield curr_index, init
        curr_index += 1
    if curr_index > dim:
        cwast.CompilerError(
            srcloc, f"Out of bounds array access at {curr_index}. Array size is  {dim}")
    while curr_index < dim:
        yield curr_index, None
        curr_index += 1


def _MangledGlobalName(mod: cwast.DefMod, mod_name: str, node: Any, is_cdecl: bool) -> cwast.NAME:
    assert isinstance(node, (cwast.DefFun, cwast.DefGlobal))
    # when we emit Cwerg IR we use the "/" sepearator not "::" because
    # : is used for type annotations
    poly_suffix = ""
    if isinstance(node, (cwast.DefFun)) and node.poly:
        poly_suffix = f"<{node.x_type.parameter_types()[0].name}>"
    n = node.name
    if is_cdecl:
        return cwast.NAME.Make(f"{n}{poly_suffix}")
    else:
        return cwast.NAME.Make(f"{mod_name}/{n}{poly_suffix}")


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
    end_label: str


def _InitDataForBaseType(x_type: cwast.CanonType, val: Union[eval.EvalNum, eval.EvalUndef]) -> bytes:
    byte_width = x_type.size
    if isinstance(val, eval.EvalUndef):
        return ZEROS[byte_width]
    assert isinstance(val, eval.EvalNum), f"{val} {x_type}"
    assert (x_type.get_unwrapped_base_type_kind() == val.kind)
    return eval.SerializeBaseType(val)


def RenderList(items):
    return "[" + " ".join(items) + "]"


def _FunTypeStrings(ct: cwast.CanonType) -> tuple[str, list[str]]:
    assert ct.is_fun()
    arg_types: list[Any] = []
    for p in ct.parameter_types():
        arg_types.append(p.get_single_register_type())
    result_type = ""
    if not ct.result_type().is_void():
        result_type = ct.result_type().get_single_register_type()
    return result_type, arg_types


def _MakeFunSigName(ct: cwast.CanonType) -> str:
    result_type, arg_types = _FunTypeStrings(ct)
    if not result_type:
        result_type = "void"
    if not arg_types:
        arg_types = ["void"]
    return f"$sig/{result_type}_{'_'.join(arg_types)}"


def _EmitFunctionHeader(name, kind, ct: cwast.CanonType):
    result_type, arg_types = _FunTypeStrings(ct)
    print(
        f"\n\n.fun {name} {kind} [{result_type}] = [{' '.join(arg_types)}]")


def _EmitFunctionProlog(fun: cwast.DefFun,
                        id_gen: identifier.IdGenIR):
    print(f".bbl {id_gen.NewName('entry')}")
    for p in fun.params:
        # TODO: NewName returns a str but p.name is really a NAME
        # this uniquifies names
        # Name translation!
        p.name = id_gen.NewName(str(p.name))
        print(f"{TAB}poparg {p.name}:{p.type.x_type.get_single_register_type()}")


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
    yield count, last


def is_repeated_single_char(data: bytes):
    c = data[0]
    for x in data:
        if x != c:
            return False
    return True


ZERO_INDEX = "0"


def OffsetScaleToOffset(offset_expr, scale: int, ta: type_corpus.TargetArchConfig,
                        id_gen: identifier.IdGenIR) -> str:
    if offset_expr.x_eval is not None:
        return offset_expr.x_eval.val * scale
    else:
        offset = EmitIRExpr(offset_expr, ta, id_gen)
        if scale == 1:
            return offset
        scaled = id_gen.NewName("scaled")
        print(
            f"{TAB}conv {scaled}:{ta.get_sint_reg_type()} = {offset}")
        print(
            f"{TAB}mul {scaled} = {scaled} {scale}")
        return scaled


def _GetLValueAddressAsBaseOffset(node, ta: type_corpus.TargetArchConfig,
                                  id_gen: identifier.IdGenIR) -> BaseOffset:
    if isinstance(node, cwast.ExprIndex):
        x_type: cwast.CanonType = node.container.x_type
        assert x_type.is_vec(), f"{x_type}"
        base = _GetLValueAddress(node.container, ta, id_gen)
        offset = OffsetScaleToOffset(node.expr_index, x_type.underlying_type().size,
                                     ta, id_gen)
        return BaseOffset(base, offset)

    elif isinstance(node, cwast.ExprDeref):
        return BaseOffset(EmitIRExpr(node.expr, ta, id_gen), 0)
    elif isinstance(node, cwast.ExprField):
        base = _GetLValueAddress(node.container, ta, id_gen)
        return BaseOffset(base, node.field.GetRecFieldRef().x_offset)
    elif isinstance(node, cwast.Id):
        name = node.x_symbol.name
        base = id_gen.NewName("lhsaddr")
        kind = ta.get_data_address_reg_type()
        storage = _StorageForId(node)
        if storage is STORAGE_KIND.DATA:
            print(f"{TAB}lea.mem {base}:{kind} = {name} 0")
        elif storage is STORAGE_KIND.STACK:
            print(f"{TAB}lea.stk {base}:{kind} = {name} 0")
        else:
            assert False, f"unsupported storage class {storage}"
        return BaseOffset(base, 0)
    elif isinstance(node, cwast.ExprNarrow):
        #
        assert node.expr.x_type.is_untagged_union()
        base = _GetLValueAddress(node.expr, ta, id_gen)
        return BaseOffset(base, 0)
    elif isinstance(node, cwast.ExprStmt):
        ct = node.x_type
        name = id_gen.NewName("expr_stk_var")
        assert ct.size > 0
        print(f"{TAB}.stk {name} {ct.alignment} {ct.size}")
        base = id_gen.NewName("stmt_stk_base")
        kind = ta.get_data_address_reg_type()
        print(f"{TAB}lea.stk {base}:{kind} {name} 0")
        EmitIRExprToMemory(node,  BaseOffset(base, 0), ta, id_gen)
        return BaseOffset(base, 0)
    else:
        assert False, f"unsupported node for lvalue {node} at {node.x_srcloc}"


def _GetLValueAddress(node, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR) -> str:
    bo = _GetLValueAddressAsBaseOffset(node, ta, id_gen)
    if bo.offset == 0:
        return bo.base
    else:
        res = id_gen.NewName("at")
        kind = ta.get_data_address_reg_type()
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
    if cwast.NF.TARGET_ANNOTATED not in node.FLAGS:
        return False
    return not isinstance(node, cwast.StmtReturn) or isinstance(node.x_target, cwast.DefFun)


def EmitIRConditional(cond, invert: bool, label_false: str, ta: type_corpus.TargetArchConfig,
                      id_gen: identifier.IdGenIR):
    """The emitted code assumes that the not taken label immediately succceeds the code generated here"""
    if cond.x_eval is not None:
        if cond.x_eval.val != invert:
            print(f"{TAB}bra {label_false}")
    elif isinstance(cond, cwast.Expr1):
        assert cond.unary_expr_kind is cwast.UNARY_EXPR_KIND.NOT
        EmitIRConditional(cond.expr, not invert, label_false, ta, id_gen)
    elif isinstance(cond, cwast.Expr2):
        kind: cwast.BINARY_EXPR_KIND = cond.binary_expr_kind
        if kind is cwast.BINARY_EXPR_KIND.ANDSC:
            if invert:
                EmitIRConditional(cond.expr1, True, label_false, ta, id_gen)
                EmitIRConditional(cond.expr2, True, label_false, ta, id_gen)
            else:
                failed = id_gen.NewName("br_failed_and")
                EmitIRConditional(cond.expr1, True, failed, ta, id_gen)
                EmitIRConditional(cond.expr2, False, label_false, ta, id_gen)
                print(f".bbl {failed}")
        elif kind is cwast.BINARY_EXPR_KIND.ORSC:
            if invert:
                failed = id_gen.NewName("br_failed_or")
                EmitIRConditional(cond.expr1, False, failed, ta, id_gen)
                EmitIRConditional(cond.expr2, True, label_false, ta, id_gen)
                print(f".bbl {failed}")
            else:
                EmitIRConditional(cond.expr1, False, label_false, ta, id_gen)
                EmitIRConditional(cond.expr2, False, label_false, ta, id_gen)
        elif kind in (cwast.BINARY_EXPR_KIND.AND, cwast.BINARY_EXPR_KIND.OR,
                      cwast.BINARY_EXPR_KIND.XOR):
            op = EmitIRExpr(cond, ta, id_gen)
            if invert:
                print(f"{TAB}beq {op} 0 {label_false}")
            else:
                print(f"{TAB}bne {op} 0 {label_false}")
        else:
            assert cond.expr1.x_type.fits_in_register(
            ), f"NYI Expr2 for {cond} {cond.expr1.x_type}"
            op1 = EmitIRExpr(cond.expr1, ta, id_gen)
            op2 = EmitIRExpr(cond.expr2, ta, id_gen)
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
    elif isinstance(cond, (cwast.ExprCall, cwast.ExprStmt, cwast.ExprField,
                           cwast.ExprIndex, cwast.ExprDeref)):
        op = EmitIRExpr(cond, ta, id_gen)
        if invert:
            print(f"{TAB}beq {op} 0 {label_false}")
        else:
            print(f"{TAB}bne {op} 0 {label_false}")
    elif isinstance(cond, cwast.Id):
        assert cond.x_type.is_bool()
        assert isinstance(cond.x_symbol, (cwast.DefVar, cwast.FunParam))
        if invert:
            print(f"{TAB}beq {cond.x_symbol.name} 0 {label_false}")
        else:
            print(f"{TAB}bne {cond.x_symbol.name} 0 {label_false}")
    else:
        assert False, f"unexpected expression {cond}"


_BIN_OP_MAP = {
    cwast.BINARY_EXPR_KIND.MUL: "mul",
    cwast.BINARY_EXPR_KIND.ADD: "add",
    cwast.BINARY_EXPR_KIND.SUB: "sub",
    cwast.BINARY_EXPR_KIND.DIV: "div",
    cwast.BINARY_EXPR_KIND.MOD: "rem",
    cwast.BINARY_EXPR_KIND.SHL: "shl",
    cwast.BINARY_EXPR_KIND.SHR: "shr",
    cwast.BINARY_EXPR_KIND.XOR: "xor",
    cwast.BINARY_EXPR_KIND.OR: "or",
    cwast.BINARY_EXPR_KIND.AND: "and",
}


def _EmitExpr2(node: cwast.Expr2, res, op1, op2, id_gen: identifier.IdGenIR):
    kind = node.binary_expr_kind
    ct = node.x_type
    res_type = ct.get_single_register_type()
    op = _BIN_OP_MAP.get(kind)
    if op is not None:
        print(f"{TAB}{op} {res}:{res_type} = {op1} {op2}")
    elif kind is cwast.BINARY_EXPR_KIND.PDELTA:
        conv_op1 = id_gen.NewName("pdelta1")
        conv_op2 = id_gen.NewName("pdelta2")
        print(f"{TAB}bitcast {conv_op1}:{res_type} = {op1}")
        print(f"{TAB}bitcast {conv_op2}:{res_type} = {op2}")

        print(f"{TAB}sub {res}:{res_type} = {conv_op1} {conv_op2}")
        print(f"{TAB}div {res} = {res} {
              node.expr1.x_type.underlying_type().aligned_size()}")
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
    ff = (1 << (8 * ct.base_type_kind.ByteSize())) - 1
    if kind is cwast.UNARY_EXPR_KIND.NEG:
        print(f"{TAB}sub {res}:{res_type} = 0 {op}")
    elif kind is cwast.UNARY_EXPR_KIND.NOT:
        print(f"{TAB}xor {res}:{res_type} = 0x{ff:x} {op}")
    elif kind is cwast.UNARY_EXPR_KIND.ABS:
        # TODO: special case unsigned
        print(f"{TAB}sub {res}:{res_type} = 0 {op}")
        print(f"{TAB}cmplt {res} = {res} {op} {op} {0}")
    elif kind is cwast.UNARY_EXPR_KIND.SQRT:
        # TODO: check float type
        print(f"{TAB}sqrt {res}:{res_type} = {op}")
    else:
        assert False, f"unsupported expression {kind}"


def _FormatNumber(val: cwast.ValNum) -> str:
    assert isinstance(val.x_eval, eval.EvalNum)
    bt = val.x_type.get_unwrapped_base_type_kind()
    assert bt == val.x_eval.kind, f"{val.x_eval} {bt} {val.x_eval.kind}"
    num = val.x_eval.val
    assert num is not None, f"{val.x_eval}"

    if bt is cwast.BASE_TYPE_KIND.BOOL:
        return "1" if num else "0"
    elif bt.IsInt():
        return str(num)
    elif bt.IsReal():
        if math.isnan(num) or math.isinf(num):
            # note, python renders -nan and +nan as just nan
            sign = math.copysign(1, num)
            num = abs(num)
            return ("+" if sign >= 0 else "-") + str(num)
        return str(num)
    else:
        assert False, f"unsupported scalar: {bt} {val}"


def EmitIRExpr(node, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR) -> Any:
    """Returns None if the type is void"""
    ct_dst: cwast.CanonType = node.x_type
    assert ct_dst.size == 0 or ct_dst.fits_in_register(), f"{node} ct={ct_dst}"
    if isinstance(node, cwast.ExprCall):
        sig: cwast.CanonType = node.callee.x_type
        assert sig.is_fun()
        args = [EmitIRExpr(a, ta, id_gen) for a in node.args]
        for a in reversed(args):
            assert not a.startswith("["), f"{a} {node.args[4]}"
            print(f"{TAB}pusharg {a}")
        if isinstance(node.callee, cwast.Id):
            def_node = node.callee.x_symbol
            is_direct = isinstance(def_node, cwast.DefFun)
            name = node.callee.x_symbol.name
            if is_direct:
                print(f"{TAB}bsr {name}")
            else:
                print(f"{TAB}jsr {name} {_MakeFunSigName(node.callee.x_type)}")
        else:
            assert False
        if sig.result_type().is_void():
            return None
        else:
            res = id_gen.NewName("call")
            print(f"{TAB}poparg {res}:{
                  sig.result_type().get_single_register_type()}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{_FormatNumber(node)}:{node.x_type.get_single_register_type()}"
    elif isinstance(node, cwast.Id):
        if node.x_type.size == 0:
            return "@@@@@ BAD, DO NOT USE @@@@@@ "
        def_node = node.x_symbol
        if isinstance(def_node, cwast.DefGlobal):
            res = id_gen.NewName("globread")
            print(
                f"{TAB}ld.mem {res}:{node.x_type.get_single_register_type()} = {node.x_symbol.name} 0")
            return res
        elif isinstance(def_node, cwast.FunParam):
            return str(node.x_symbol.name)
        elif isinstance(def_node, cwast.DefFun):
            res = id_gen.NewName("funaddr")
            print(
                f"{TAB}lea.fun {res}:{node.x_type.get_single_register_type()} = {node.x_symbol.name}")
            return res
        elif _IsDefVarOnStack(def_node):
            res = id_gen.NewName("stkread")
            print(
                f"{TAB}ld.stk {res}:{node.x_type.get_single_register_type()} = {node.x_symbol.name} 0")
            return res
        else:
            return str(node.x_symbol.name)
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr_lhs, ta, id_gen)
    elif isinstance(node, cwast.Expr1):
        op = EmitIRExpr(node.expr, ta, id_gen)
        res = id_gen.NewName("expr1")
        _EmitExpr1(node.unary_expr_kind, res, node.x_type, op)
        return res
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, ta, id_gen)
        op2 = EmitIRExpr(node.expr2, ta, id_gen)
        res = id_gen.NewName("expr2")
        _EmitExpr2(node, res, op1, op2, id_gen)
        return res
    elif isinstance(node, cwast.ExprPointer):
        base = EmitIRExpr(node.expr1, ta, id_gen)
        # TODO: add range check
        # assert isinstance(node.expr_bound_or_undef, cwast.ValUndef)
        res = id_gen.NewName("expr2")
        ct: cwast.CanonType = node.expr1.x_type
        if node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP:
            assert ct.is_pointer()
            # print ("@@@@@ ", ct,  ct.underlying_type().size)
            offset = OffsetScaleToOffset(
                node.expr2, ct.underlying_type().aligned_size(), ta, id_gen)
            kind = ta.get_data_address_reg_type()
            print(f"{TAB}lea {res}:{kind} = {base} {offset}")
        else:
            assert False, f"unsupported expression {node}"
        return res
    elif isinstance(node, cwast.ExprBitCast):
        res = id_gen.NewName("bitcast")
        expr = EmitIRExpr(node.expr, ta, id_gen)
        src_reg_type = node.expr.x_type.get_single_register_type()
        dst_reg_type = node.type.x_type.get_single_register_type()
        if src_reg_type == dst_reg_type:
            print(f"{TAB}mov {res}:{dst_reg_type} = {expr}")
        else:
            print(f"{TAB}bitcast {res}:{dst_reg_type} = {expr}")
        return res
    elif isinstance(node, cwast.ExprNarrow):
        addr = _GetLValueAddress(node.expr, ta, id_gen)
        if ct_dst.is_zero_sized():
            return None
        ct_src: cwast.CanonType = node.expr.x_type
        assert ct_src.is_union() or ct_src.original_type.is_union()
        res = id_gen.NewName("union_access")
        print(
            f"{TAB}ld {res}:{ct_dst.get_single_register_type()} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprAs):
        ct_src: cwast.CanonType = node.expr.x_type
        if ct_src.is_base_type() and ct_dst.is_base_type():
            # more compatibility checking needed
            expr = EmitIRExpr(node.expr, ta, id_gen)
            res = id_gen.NewName("as")
            print(
                f"{TAB}conv {res}:{ct_dst.get_single_register_type()} = {expr}")
            return res
        elif ct_src.is_pointer() and ct_dst.is_pointer():
            return EmitIRExpr(node.expr, ta, id_gen)
        else:
            assert False, f"unsupported cast {
                node.expr} ({ct_src.name}) -> {ct_dst.name}"
    elif isinstance(node, (cwast.ExprWrap, cwast.ExprUnwrap)):
        return EmitIRExpr(node.expr, ta, id_gen)
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, ta, id_gen)
        res = id_gen.NewName("deref")
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        if node.x_type.is_zero_sized():
            result = _DUMMY_VOID_REG
        else:
            result = id_gen.NewName("expr")
            print(
                f"{TAB}.reg {node.x_type.get_single_register_type()} [{result}]")
        end_label = id_gen.NewName("end_expr")
        for c in node.body:
            EmitIRStmt(c, ReturnResultLocation(result, end_label), ta, id_gen)
        print(f".bbl {end_label}  # block end")
        return result
    elif isinstance(node, cwast.ExprIndex):
        src = _GetLValueAddressAsBaseOffset(node, ta, id_gen)
        res = id_gen.NewName("at")
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {src.base} {src.offset}")
        return res
    elif isinstance(node, cwast.ExprFront):
        assert node.container.x_type.is_vec(), f"unexpected {node}"
        return _GetLValueAddress(node.container, ta, id_gen)
    elif isinstance(node, cwast.ExprField):
        recfield: cwast.RecField = node.field.GetRecFieldRef()
        res = id_gen.NewName(f"field_{recfield.name}")
        addr = _GetLValueAddress(node.container, ta, id_gen)
        if node.x_type.size == 0:
            return None
        print(
            f"{TAB}ld {res}:{node.x_type.get_single_register_type()} = {addr} {recfield.x_offset}")
        return res
    elif isinstance(node, cwast.ExprWiden):
        # this should only happen for widening empty untagged unions
        assert node.x_type.size == 0
        # make sure we evaluate the rest for side-effects
        return EmitIRExpr(node.expr, ta, id_gen)
    elif isinstance(node, cwast.ValVoid):
        return None
    # elif isinstance(node, cwast.ValCompound):
    #    assert node.x_type.size == 0, f"{node} {node.x_type} {node.x_type.size}"
    #    return None
    else:
        assert False, f"unsupported expression {node.x_srcloc} {node}"


def _EmitZero(dst: BaseOffset, length, alignment,
              _id_gen: identifier.IdGenIR):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        while curr + width <= length:
            print(f"{TAB}st {dst.base} {dst.offset + curr} = 0:U{width * 8}")
            curr += width


def EmitIRExprToMemory(init_node, dst: BaseOffset,
                       ta: type_corpus.TargetArchConfig,
                       id_gen: identifier.IdGenIR):
    """This will instantiate objects on the stack or heap.

    Note, that this can occur in two ways:
    1) we populate the object from the information AST
    2) we copy the contents from a global const location
       (this works in conjunction with the GlobalConstantPool)
    """
    assert init_node.x_type.size > 0, f"{init_node}"
    if isinstance(init_node, (cwast.ExprCall, cwast.ValNum, cwast.ExprLen, cwast.ExprAddrOf,
                              cwast.Expr1, cwast.Expr2, cwast.ExprPointer, cwast.ExprFront)):
        reg = EmitIRExpr(init_node, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, cwast.ExprBitCast):
        # both imply scalar and both do not change the bits
        reg = EmitIRExpr(init_node.expr, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, (cwast.ExprWrap, cwast.ExprUnwrap)):
        # these do NOT imply scalars
        EmitIRExprToMemory(init_node.expr, dst, ta, id_gen)
    elif isinstance(init_node, cwast.ExprAs):
        # this implies scalar
        # TODO: add the actual conversion step using IR opcode `conv`
        #       bools may need special treatment
        assert init_node.x_type == init_node.type.x_type, f"ExprAs {
            init_node.type.x_type} ->  {init_node.x_type}"
        assert init_node.x_type.fits_in_register(
        ), f"{init_node} {init_node.x_type}"
        reg = EmitIRExpr(init_node, ta, id_gen)
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, cwast.ExprNarrow):
        # if we are narrowing the dst determines the size
        ct: cwast.CanonType = init_node.x_type
        if ct.size != 0:
            src_base = _GetLValueAddress(init_node.expr, ta, id_gen)
            _EmitCopy(dst, BaseOffset(src_base, 0),
                      ct.size, ct.alignment, id_gen)
    elif isinstance(init_node, cwast.ExprWiden):
        assert init_node.x_type.is_untagged_union()
        ct: cwast.CanonType = init_node.expr.x_type
        if ct.size != 0:
            EmitIRExprToMemory(init_node.expr, dst, ta, id_gen)
    elif isinstance(init_node, cwast.Id) and _StorageForId(init_node) is STORAGE_KIND.REGISTER:
        reg = EmitIRExpr(init_node, ta, id_gen)
        assert reg is not None
        print(f"{TAB}st {dst.base} {dst.offset} = {reg}")
    elif isinstance(init_node, (cwast.Id, cwast.ExprDeref, cwast.ExprIndex, cwast.ExprField)):
        src_base = _GetLValueAddress(init_node, ta, id_gen)
        src_type = init_node.x_type
        # if isinstance(init_node,  cwast.ExprField):
        #    print ("@@@@@@", init_node, src_type)
        _EmitCopy(dst, BaseOffset(


            src_base, 0), src_type.size, src_type.alignment, id_gen)
    elif isinstance(init_node, cwast.ExprStmt):
        end_label = id_gen.NewName("end_expr")
        for c in init_node.body:
            EmitIRStmt(c, ReturnResultLocation(dst, end_label), ta, id_gen)
        print(f".bbl {end_label}  # block end")
    elif isinstance(init_node, cwast.ValString):
        assert False, f"NYI {init_node}"
    elif isinstance(init_node, cwast.ValAuto):
        # TODO: check if auto is legit (maybe add a check for this in another phase)
        _EmitZero(dst, init_node.x_type.size,
                  init_node.x_type.alignment, id_gen)
    elif isinstance(init_node, cwast.ValCompound):
        src_type = init_node.x_type
        if src_type.is_rec():
            if not init_node.inits:
                _EmitZero(dst, src_type.size, src_type.alignment, id_gen)
                return
            for field, init in symbolize.IterateValRec(init_node.inits, src_type):

                if init is None:
                    _EmitZero(BaseOffset(dst.base, dst.offset+field.x_offset),
                              field.x_type.size, field.x_type.alignment, id_gen)
                elif isinstance(init.value_or_undef, cwast.ValUndef):
                    pass
                elif init.value_or_undef.x_type.size == 0:
                    pass
                else:
                    EmitIRExprToMemory(init.value_or_undef, BaseOffset(
                        dst.base, dst.offset+field.x_offset), ta, id_gen)
        else:
            assert src_type.is_vec()
            element_size: int = src_type.array_element_size()
            for index, c in _IterateValVec(init_node.inits,
                                           init_node.x_type.array_dim(),
                                           init_node.x_srcloc):
                if c is None:
                    continue
                if isinstance(c.value_or_undef, cwast.ValUndef):
                    continue
                EmitIRExprToMemory(
                    c.value_or_undef, BaseOffset(dst.base, dst.offset + element_size * index), ta, id_gen)
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


def EmitIRStmt(node, result: Optional[ReturnResultLocation], ta: type_corpus.TargetArchConfig,
               id_gen: identifier.IdGenIR):
    if isinstance(node, cwast.DefVar):
        # name translation!
        node.name = id_gen.NewName(str(node.name))

        def_type: cwast.CanonType = node.type_or_auto.x_type
        initial = node.initial_or_undef_or_auto
        if def_type.size == 0:
            if not isinstance(initial, cwast.ValUndef):
                # still need to evaluate the expression for the side effect
                EmitIRExpr(initial, ta, id_gen)
        elif _IsDefVarOnStack(node):
            assert def_type.size > 0
            print(f"{TAB}.stk {node.name} {
                  def_type.alignment} {def_type.size}")
            if not isinstance(initial, cwast.ValUndef):
                init_base = id_gen.NewName("init_base")
                kind = ta.get_data_address_reg_type()
                print(f"{TAB}lea.stk {init_base}:{kind} {node.name} 0")
                EmitIRExprToMemory(initial, BaseOffset(
                    init_base, 0), ta, id_gen)
        else:
            if isinstance(initial, cwast.ValUndef):
                print(
                    f"{TAB}.reg {def_type.get_single_register_type()} [{node.name}]")
            else:
                out = EmitIRExpr(initial, ta, id_gen)
                assert out is not None, f"Failure to gen code for {initial}"
                print(
                    f"{TAB}mov {node.name}:{def_type.get_single_register_type()} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        label = str(node.label)
        if not label:
            label = "_"

        continue_label = id_gen.NewName(label)
        break_label = id_gen.NewName(label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}  # block start")
        for c in node.body:
            EmitIRStmt(c, result, ta, id_gen)
        print(f".bbl {break_label}  # block end")
    elif isinstance(node, cwast.StmtReturn):
        if isinstance(node.x_target, cwast.ExprStmt):
            assert result is not None

            # for this kind of return we need to save the computed value
            # and the branch to the end of the ExprStmt
            if not node.expr_ret.x_type.is_zero_sized():
                if isinstance(result.dst, str):
                    out = EmitIRExpr(node.expr_ret, ta, id_gen)
                    print(f"{TAB}mov {result.dst} {out}")
                else:
                    EmitIRExprToMemory(node.expr_ret, result.dst, ta, id_gen)
            else:
                # nothing to save here
                EmitIRExpr(node.expr_ret, ta, id_gen)
            print(f"{TAB}bra {result.end_label}  # end of expr")
        else:
            out = EmitIRExpr(node.expr_ret, ta, id_gen)
            if not node.expr_ret.x_type.is_zero_sized():
                print(f"{TAB}pusharg {out}")
            print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label[1]
        print(f"{TAB}bra {block}  # break")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label[0]
        print(f"{TAB}bra {block}  # continue")
    elif isinstance(node, cwast.StmtExpr):
        ct: cwast.CanonType = node.expr.x_type
        if ct.is_zero_sized() or ct.fits_in_register():
            EmitIRExpr(node.expr, ta, id_gen)
        else:
            name = id_gen.NewName("stmt_stk_var")
            assert ct.size > 0
            print(f"{TAB}.stk {name} {ct.alignment} {ct.size}")
            base = id_gen.NewName("stmt_stk_base")
            kind = ta.get_data_address_reg_type()
            print(f"{TAB}lea.stk {base}:{kind} {name} 0")
            EmitIRExprToMemory(node.expr,  BaseOffset(base, 0), ta, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_f = id_gen.NewName("br_f")
        label_join = id_gen.NewName("br_join")
        if node.body_t and node.body_f:
            EmitIRConditional(node.cond, True, label_f, ta, id_gen)
            for c in node.body_t:
                EmitIRStmt(c, result, ta, id_gen)
            if not IsUnconditionalBranch(node.body_t[-1]):
                print(f"{TAB}bra {label_join}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                EmitIRStmt(c, result, ta, id_gen)
            print(f".bbl {label_join}")
        elif node.body_t:
            EmitIRConditional(node.cond, True, label_join, ta, id_gen)
            for c in node.body_t:
                EmitIRStmt(c, result, ta, id_gen)
            print(f".bbl {label_join}")
        elif node.body_f:
            EmitIRConditional(node.cond, False, label_join, ta, id_gen)
            for c in node.body_f:
                EmitIRStmt(c, result, ta, id_gen)
            print(f".bbl {label_join}")
        else:
            EmitIRConditional(node.cond, False, label_join, ta, id_gen)
            print(f".bbl {label_join}")
    elif isinstance(node, cwast.StmtAssignment):
        lhs = node.lhs
        if lhs.x_type.fits_in_register() and _AssignmentLhsIsInReg(lhs):
            assert isinstance(node.lhs, cwast.Id)
            out = EmitIRExpr(node.expr_rhs, ta, id_gen)
            print(f"{TAB}mov {lhs.x_symbol.name} = {out}  # {node}")
        else:
            lhs = _GetLValueAddressAsBaseOffset(lhs, ta, id_gen)
            assert node.expr_rhs.x_type.size > 0, f"{node.expr_rhs} {node.x_srcloc} {node.expr_rhs.x_type}"
            EmitIRExprToMemory(node.expr_rhs, lhs, ta, id_gen)
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


_BYTE_ZERO = b"\0"
_BYTE_UNDEF = b"\0"
_BYTE_PADDING = b"\x6f"   # intentioanlly not zero?


def EmitIRDefGlobal(node: cwast.DefGlobal, ta: type_corpus.TargetArchConfig) -> int:
    """Note there is some similarity to  EmitIRExprToMemory

    returns the amount of bytes emitted
    """
    def_type: cwast.CanonType = node.type_or_auto.x_type
    if def_type.get_unwrapped().is_void():
        return 0
    print(
        f"\n.mem {node.name} {def_type.alignment} {'RW' if node.mut else 'RO'}")

    def _emit_recursively(node, ct: cwast.CanonType, offset: int) -> int:
        """When does  node.x_type != ct not hold?"""
        if ct.is_zero_sized():
            # global data initialization may not have side-effects
            return 0
        assert offset == type_corpus.align(offset, ct.alignment)
        if isinstance(node, cwast.ValUndef):
            return _EmitMem(_BYTE_UNDEF * ct.size, f"{offset} undef={ct.name}")

        if isinstance(node, cwast.Id):
            node_def = node.x_symbol
            assert isinstance(node_def, cwast.DefGlobal), f"{node_def}"
            return _emit_recursively(node_def.initial_or_undef_or_auto, ct, offset)
        elif isinstance(node, cwast.ExprFront):
            # we need to emit an address
            assert isinstance(node.container, cwast.Id), f"{node.container}"
            name = node.container.x_symbol.name
            print(f".addr.mem {ta.get_address_size()} {name} 0")
            # assert False, f"{name} {node.container}"
            return ta.get_address_size()
        elif isinstance(node, cwast.ExprAddrOf):
            assert isinstance(
                node.expr_lhs, cwast.Id), "NYI complex static addresses"
            data = node.expr_lhs
            print(
                f"\n.addr.mem {ta.get_address_size()} {data.x_symbol.name} 0")
            return ta.get_address_size()
        elif isinstance(node, cwast.ExprWiden):
            count = _emit_recursively(node.expr, node.expr.x_type, offset)
            target = node.x_type.size
            if target != count:
                _EmitMem(_BYTE_PADDING * (target - count),
                         f"{target - count} padding")
            return target
        elif isinstance(node, cwast.ValNum):
            assert ct.get_unwrapped().is_base_type()
            assert node.x_eval
            return _EmitMem(_InitDataForBaseType(ct, node.x_eval),  f"{offset} {ct.name}")

        if ct.is_wrapped():
            assert isinstance(node, cwast.ExprWrap)
            return _emit_recursively(node.expr, node.expr.x_type, offset)
        elif ct.is_vec():
            if isinstance(node, cwast.ValAuto):
                return _EmitMem(_BYTE_ZERO * ct.size, f"{ct.size} zero")
            assert isinstance(
                node, (cwast.ValCompound, cwast.ValString)), f"{node}"
            print(f"# array: {ct.name}")
            width = ct.array_dim()
            x_type = ct.underlying_type()
            if isinstance(node, cwast.ValString):
                value = node.get_bytes()
                assert len(
                    value) == width, f"length mismatch {len(value)} vs {width} [{value}]"
                return _EmitMem(value, f"{offset} {ct.name}")

            assert isinstance(node, cwast.ValCompound), f"{node}"
            if x_type.is_base_type() or x_type.is_enum():
                # this special case creates a smaller IR
                out = bytearray()
                last = _InitDataForBaseType(
                    x_type, eval.GetDefaultForBaseType(x_type.base_type_kind))
                for n, init in _IterateValVec(node.inits, width, node.x_srcloc):
                    if init is not None:
                        last = _InitDataForBaseType(x_type, init.x_eval)
                    out += last
                return _EmitMem(out, ct.name)
            else:
                last = cwast.ValUndef()
                stride = ct.size // width
                assert stride * width == ct.size, f"{ct.size} {width}"
                for n, init in _IterateValVec(node.inits, width, node.x_srcloc):
                    if init is None:
                        count = _emit_recursively(
                            last, x_type, offset + n * stride)
                    else:
                        assert isinstance(init, cwast.ValPoint)
                        last = init.value_or_undef
                        count = _emit_recursively(
                            last, x_type, offset + n * stride)
                    if count != stride:
                        _EmitMem(_BYTE_PADDING * (stride - count),
                                 f"{stride - count} padding")
                return ct.size
        elif ct.is_rec():
            if isinstance(node, cwast.ValAuto):
                return _EmitMem(_BYTE_ZERO * ct.size, f"{ct.size} zero")
            assert isinstance(
                node, cwast.ValCompound), f"unexpected value {node}"
            print(f"# record: {ct.name}")
            rel_off = 0
            # note node.x_type may be compatible but not equal to ct
            for f, i in symbolize.IterateValRec(node.inits, node.x_type):
                if f.x_offset > rel_off:
                    rel_off += _EmitMem(_BYTE_PADDING *
                                        (f.x_offset - rel_off), f"{offset+rel_off} padding")
                if i is not None and not isinstance(i.value_or_undef, cwast.ValUndef):
                    rel_off += _emit_recursively(i.value_or_undef,
                                                 f.type.x_type, offset + rel_off)
                else:
                    rel_off += _EmitMem(_BYTE_UNDEF * f.type.x_type.size,
                                        f.type.x_type.name)
            return rel_off
        else:
            assert False, f"unhandled node: {node} {ct.name}"

    return _emit_recursively(node.initial_or_undef_or_auto,
                             node.type_or_auto.x_type, 0)


def EmitIRDefFun(node: cwast.DefFun, ta: type_corpus.TargetArchConfig, id_gen: identifier.IdGenIR):
    if not node.extern:
        _EmitFunctionHeader(node.name, "NORMAL", node.x_type)
        _EmitFunctionProlog(node, id_gen)
        for c in node.body:
            EmitIRStmt(c, None, ta, id_gen)


_GENERATED_MODULE_NAME = "GeNeRaTeD"


def SanityCheckMods(phase_name: str, stage: checker.COMPILE_STAGE, args: Any,
                    mods: list[cwast.DefMod], tc: Optional[type_corpus.TypeCorpus],
                    eliminated_node_types):

    logger.info(phase_name)
    if args.emit_stats == phase_name:
        node_histo = stats.ComputeNodeHistogram(mods)
        stats.DumpCounter(node_histo)
        stats.DumpStats()

    if args.dump_ast_html == phase_name:
        from FE import pp_html
        for mod in mods:
            pp_html.PrettyPrintHTML(mod)
            # pp_sexpr.PrettyPrint(mod)
        exit(0)

    if args.dump_ast == phase_name:
        from FE import pp_ast
        import sys
        pp_ast.DumpMods(mods, sys.stdout)
        exit(0)

    if args.dump_types == phase_name:
        for m in mods:
            print(m.name)
        assert tc
        tc.Dump()
        exit(0)

    if args.stop == phase_name:
        exit(0)

    no_symbols = stage.value < checker.COMPILE_STAGE.AFTER_TYPIFY.value
    allow_type_auto = stage.value >= checker.COMPILE_STAGE.AFTER_DESUGAR.value
    for mod in mods:
        checker.CheckAST(mod, eliminated_node_types, allow_type_auto,
                         pre_symbolize=no_symbols)

        if stage.value >= checker.COMPILE_STAGE.AFTER_SYMBOLIZE.value:
            symbolize.VerifySymbols(mod)

        if stage in (checker.COMPILE_STAGE.AFTER_TYPIFY, checker.COMPILE_STAGE.AFTER_EVAL):
            typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_WEAK)
        if stage.value > checker.COMPILE_STAGE.AFTER_EVAL.value:
            typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_STRICT)

        if stage.value >= checker.COMPILE_STAGE.AFTER_EVAL.value:
            eval.VerifyASTEvalsRecursively(mod)


_ARCH_MAP = {
    "x64": type_corpus.STD_TARGET_X64,
    "a64": type_corpus.STD_TARGET_A64,
    "a32": type_corpus.STD_TARGET_A32,
}


def PhaseInitialLowering(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    # for key, val in fun_sigs_with_large_args.items():
    #    print (key.name, " -> ", val.name)
    # ct_bool = tc.get_bool_canon_type()
    typeid_ct = tc.get_typeid_canon_type()
    for mod in mod_topo_order:
        typify.ModStripTypeNodesRecursively(mod)
        for fun in mod.body_mod:
            canonicalize.FunReplaceConstExpr(fun, tc)
            canonicalize.FunMakeImplicitConversionsExplicit(fun, tc)
            canonicalize.FunReplaceExprIndex(fun, tc)
            canonicalize.FunDesugarTaggedUnionComparisons(fun)
            canonicalize.FunReplaceSpanCastWithSpanVal(fun, tc)
            if not isinstance(fun, cwast.DefFun):
                continue

            # note: ReplaceTaggedExprNarrow introduces new ExprIs nodes
            canonicalize_union.FunSimplifyTaggedExprNarrow(fun, tc)
            canonicalize.FunDesugarExprIs(fun, typeid_ct)
            canonicalize.FunEliminateDefer(fun)
            canonicalize.FunRemoveUselessCast(fun)
            # this creates TernaryOps
            canonicalize.FunCanonicalizeBoolExpressionsNotUsedForConditionals(
                fun)
            canonicalize.FunDesugarExpr3(fun)
            canonicalize.FunOptimizeKnownConditionals(fun)
            if not fun.extern:
                canonicalize.FunAddMissingReturnStmts(fun)


def PhaseOptimization(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                optimize.FunOptimize(fun)


def MakeModWithComplexConstants(mod_topo_order: list[cwast.DefMod]) -> cwast.DefMod:
    constant_pool = eval.GlobalConstantPool()
    for mod in mod_topo_order:
        constant_pool.EliminateValStringAndValCompoundOutsideOfDefGlobal(mod)
    mod_gen = cwast.DefMod(cwast.NAME.Make(_GENERATED_MODULE_NAME),
                           [], [], x_srcloc=cwast.SRCLOC_GENERATED)
    # the checker neeeds a symtab, so we add an empty one
    mod_gen.x_symtab = symbolize.SymTab()
    mod_gen.body_mod += constant_pool.GetDefGlobals()
    return mod_gen


def PhaseEliminateSpanAndUnion(mod_gen: cwast.DefMod, mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    canonicalize_span.MakeAndRegisterSpanTypeReplacements(mod_gen, tc)
    for mod in ([mod_gen] + mod_topo_order):
        canonicalize_span.ReplaceSpans(mod)
    # TODO: comment on orrdering:
    canonicalize_union.MakeAndRegisterUnionTypeReplacements(mod_gen, tc)
    for mod in ([mod_gen] + mod_topo_order):
        canonicalize_union.ReplaceUnions(mod)


def PhaseEliminateLargeArgs(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    fun_sigs_with_large_args = canonicalize_large_args.FindFunSigsWithLargeArgs(
        tc)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            canonicalize_large_args.FunRewriteLargeArgsCallerSide(
                fun, fun_sigs_with_large_args, tc)
            if fun.x_type in fun_sigs_with_large_args:
                canonicalize_large_args.FunRewriteLargeArgsCalleeSide(
                    fun, fun_sigs_with_large_args[fun.x_type], tc)


def PhaseLegalize(mod_topo_order: list[cwast.DefMod], tc: type_corpus.TypeCorpus):
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if not isinstance(fun, cwast.DefFun):
                continue
            canonicalize.FunCanonicalizeCompoundAssignments(fun)
            canonicalize.FunCanonicalizeRemoveStmtCond(fun)
            canonicalize.FunRewriteComplexAssignments(fun, tc)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                # Note, the inlining inside FunOptimize will invalidate id_gen
                optimize.FunOptimize(fun)


def main() -> int:
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument("-shake_tree",
                        action="store_true", help='remove unreachable functions')
    parser.add_argument(
        '-stdlib', help='path to stdlib directory', default="./Lib")
    parser.add_argument(
        '-arch', help='architecture to generated IR for', default="x64")
    parser.add_argument(
        '-dump_ast_html', help='stop at the given stage and dump ast in html format')
    parser.add_argument(
        '-dump_ast', help='stop at the given stage and dump ast')
    parser.add_argument(
        '-dump_types', help='stop at the given stage and dump types')
    parser.add_argument(
        '-stop', help='stop at the given stage')
    parser.add_argument(
        '-emit_stats', help='stop at the given stage and emit stats')
    parser.add_argument('files', metavar='F', type=str, nargs='+',
                        help='an input source file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    # typify.logger.setLevel(logging.INFO)
    logger.info("Start Parsing")
    assert len(args.files) == 1
    fn = args.files[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    main = str(pathlib.Path(fn).resolve())
    mp = mod_pool.ReadModulesRecursively(
        pathlib.Path(args.stdlib), [main], add_builtin=True)
    eliminated_nodes: set[Any] = set()
    eliminated_nodes.add(cwast.Import)
    eliminated_nodes.add(cwast.ModParam)
    mod_topo_order = mp.mods_in_topo_order
    main_entry_fun: cwast.DefFun = mp.main_fun

    SanityCheckMods("after_parsing", checker.COMPILE_STAGE.AFTER_PARSING,
                    args, mod_topo_order, tc=None,
                    eliminated_node_types=eliminated_nodes)

    # keeps track of those node classes which have been eliminated and hence must not
    # occur in the AST anymore
    for mod in mod_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    eliminated_nodes.add(cwast.ExprParen)  # this needs more work

    #
    logger.info("Expand macros and link most IDs to their definition")
    macro.ExpandMacrosAndMacroLike(mod_topo_order)
    eliminated_nodes.update([cwast.MacroInvoke,
                             cwast.MacroId,
                             cwast.MacroFor,
                             cwast.MacroParam,
                             cwast.ExprSrcLoc,
                             cwast.ExprStringify,
                             cwast.EphemeralList,
                             cwast.DefMacro])
    symbolize.SetTargetFields(mod_topo_order)
    # global symbols have already been resolved
    symbolize.ResolveSymbolsInsideFunctions(mod_topo_order, mp.builtin_symtab)
    # Before Typing we cannot set the symbol links for rec fields
    SanityCheckMods("after_symbolizing", checker.COMPILE_STAGE.AFTER_SYMBOLIZE,
                    args, mod_topo_order, None, eliminated_nodes)

    ta: type_corpus.TargetArchConfig = _ARCH_MAP[args.arch]
    tc: type_corpus.TypeCorpus = type_corpus.TypeCorpus(ta)

    #
    logger.info("Typify the nodes")
    typify.AddTypesToAst(mod_topo_order, tc)
    SanityCheckMods("after_typing", checker.COMPILE_STAGE.AFTER_TYPIFY, args, mod_topo_order, tc=tc,
                    eliminated_node_types=eliminated_nodes)

    #
    if args.shake_tree:
        dead_code.ShakeTree(mod_topo_order, main_entry_fun)

    #
    logger.info("partial eval and static assert validation")
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)
    for mod in mod_topo_order:
        cwast.RemoveNodesOfType(mod, cwast.StmtStaticAssert)
    eliminated_nodes.add(cwast.StmtStaticAssert)
    SanityCheckMods("after_partial_eval", checker.COMPILE_STAGE.AFTER_EVAL, args,
                    mod_topo_order, tc, eliminated_nodes)

    #
    logger.info("phase: initial lowering")
    PhaseInitialLowering(mod_topo_order, tc)
    eliminated_nodes.update([cwast.ExprIndex,
                             cwast.ExprIs,
                             cwast.ExprOffsetof,
                             cwast.ExprSizeof,
                             cwast.ExprTypeId,
                             cwast.StmtDefer,
                             cwast.TypeOf,
                             cwast.TypeUnionDelta])
    SanityCheckMods("after_initial_lowering", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args,
                    mod_topo_order, tc,  eliminated_nodes)

    # This section coould probably happen AFTER the next phase

    #
    logger.info("phase: early cleanup and optimization")
    PhaseOptimization(mod_topo_order, tc)
    eliminated_nodes.add(cwast.Expr3)

    SanityCheckMods("after_optimization", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args, mod_topo_order, tc,  eliminated_nodes)

    #
    mod_gen = MakeModWithComplexConstants(mod_topo_order)

    #
    logger.info("phase: eliminate span and union")
    PhaseEliminateSpanAndUnion(mod_gen, mod_topo_order, tc)
    eliminated_nodes.update([cwast.ExprLen,
                             cwast.ValSpan,
                             cwast.TypeSpan,
                             cwast.ExprUnionTag,
                             cwast.ExprUnionUntagged])
    SanityCheckMods("after_eliminate_span_and_union", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    [mod_gen] + mod_topo_order, tc, eliminated_nodes)

    #
    logger.info("phase: eliminate large args")
    PhaseEliminateLargeArgs(mod_topo_order, tc)
    SanityCheckMods("after_large_arg_conversion", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    mod_topo_order, tc,  eliminated_nodes)
    #
    logger.info("phase: legalize")
    PhaseLegalize(mod_topo_order, tc)
    eliminated_nodes.update([cwast.StmtCompoundAssignment,
                             cwast.StmtCond,
                             cwast.Case])
    SanityCheckMods("after_canonicalization", checker.COMPILE_STAGE.AFTER_DESUGAR, args,
                    [mod_gen] + mod_topo_order, tc, eliminated_nodes)

    assert eliminated_nodes == cwast.ALL_NODES_NON_CORE
    mod_topo_order = [mod_gen] + mod_topo_order

    # Naming cleanup:
    # * Set fully qualified names for all module level symbols
    # * uniquify local variables so we can use them directly
    #   for codegen without having to worry about name clashes
    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                node.name = _MangledGlobalName(
                    mod, str(mod.name), node, node.cdecl or node == main_entry_fun)

    SanityCheckMods("after_name_cleanup", checker.COMPILE_STAGE.AFTER_DESUGAR,
                    args,
                    mod_topo_order, tc, eliminated_nodes)

    # Emit Cwert IR
    # print ("# TOPO-ORDER")
    # for mod in mod_topo_order:
    #    print (f"# {mod.name}")

    sig_names: set[str] = set()
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            if isinstance(fun, cwast.DefFun):
                sn = _MakeFunSigName(fun.x_type)
                if sn not in sig_names:
                    _EmitFunctionHeader(sn, "SIGNATURE", fun.x_type)
                    sig_names.add(sn)

    for mod in mod_topo_order:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                EmitIRDefGlobal(node, ta)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                EmitIRDefFun(node, ta, identifier.IdGenIR())
    return 0


if __name__ == "__main__":
    if 0:
        # consider using:
        # python -m cProfile -o output.pstats path/to/your/script arg1 arg2
        # gprof2dot.py -f pstats output.pstats | dot -Tpng -o output.png
        from cProfile import Profile
        from pstats import SortKey, Stats
        with Profile() as profile:
            ret = main()
            Stats(profile).strip_dirs().sort_stats(SortKey.CALLS).print_stats()
            exit(ret)
    else:
        exit(main())
