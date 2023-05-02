#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

import sys
import logging
import argparse

from typing import List, Dict, Set, Optional, Union, Any, Tuple

from FrontEnd import canonicalize_large_args
from FrontEnd import canonicalize_slice
from FrontEnd import canonicalize
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import cwast
from FrontEnd import typify
from FrontEnd import eval
from FrontEnd import identifier
from FrontEnd import parse
from FrontEnd import pp

from Util.parse import BytesToEscapedString


logger = logging.getLogger(__name__)

TAB = "  "

ZEROS = [b"\0" * i for i in range(128)]


_DUMMY_VOID_REG = "@DUMMY_FOR_VOID_RESULTS@"


def _InitDataForBaseType(x_type, x_value) -> bytes:
    assert isinstance(x_type, cwast.TypeBase)
    byte_width = x_type.x_size
    if x_value is None or isinstance(x_value, cwast.ValUndef):
        return ZEROS[byte_width]
    elif types.is_int(x_type):
        return x_value.to_bytes(byte_width, 'little')
    elif types.is_bool(x_type):
        return b"\1" if x_value else b"\0"
    assert False


def RenderList(items):
    return "[" + " ".join(items) + "]"


def StringifyOneType(node, type_corpus: types.TypeCorpus):
    t = type_corpus.register_types(node)
    assert len(t) == 1, f"bad type: {node}"
    return t[0]


def _EmitFunctionHeader(fun: cwast.DefFun, type_corpus: types.TypeCorpus):
    sig: cwast.TypeFun = fun.x_type
    ins = []
    for p in sig.params:
        ins += type_corpus.register_types(p.type)
    result = ""
    if not types.is_void(sig.result):
        result = StringifyOneType(sig.result, type_corpus)
    print(
        f"\n\n.fun {fun.name} NORMAL [{result}] = [{' '.join(ins)}]")


def _EmitFunctionProlog(fun: cwast.DefFun, type_corpus: types.TypeCorpus,
                        id_gen: identifier.IdGen):
    print(f".bbl {id_gen.NewName('entry')}")
    for p in fun.params:
        p.name = id_gen.NewName(p.name)
        reg_types = type_corpus.register_types(p.type.x_type)
        if len(reg_types) == 1:
            print(f"{TAB}poparg {p.name}:{reg_types[0]}")
        else:
            assert len(reg_types) == 2
            print(f"{TAB}poparg {p.name}.1:{reg_types[0]}")
            print(f"{TAB}poparg {p.name}.2:{reg_types[1]}")


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


def _GetLValueAddress(node, tc: types.TypeCorpus, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprIndex):
        x_type = node.container.x_type
        assert isinstance(x_type, cwast.TypeArray), f"{x_type}"
        container = _GetLValueAddress(node.container, tc, id_gen)
        if node.expr_index.x_value == 0:
            return container
        else:
            index = EmitIRExpr(node.expr_index, tc, id_gen)
            scale = x_type.type.x_size
            if scale != 1:
                scaled = id_gen.NewName("scaled")
                # TODO: widen index
                print(
                    f"{TAB}mul {scaled}:{StringifyOneType(node.expr_index.x_type, tc)} = {index} {scale}")
                index = scaled
            res = id_gen.NewName("at")
            # TODO A64
            kind = "A64"
            print(f"{TAB}lea {res}:{kind} = {container} {index}")
            return res

    elif isinstance(node, cwast.ExprDeref):
        return EmitIRExpr(node.expr, tc, id_gen)
    elif isinstance(node, cwast.ExprField):
        assert False
    elif isinstance(node, cwast.Id):
        def_node = node.x_symbol
        name = def_node.name
        res = id_gen.NewName(f"lhsaddr_{node.name}")
        # TODO
        kind = "A64"
        if isinstance(def_node, cwast.DefGlobal):
            print(f"{TAB}lea.mem {res}:{kind} = {name} 0")
        else:
            assert isinstance(def_node, cwast.DefVar)
            print(f"{TAB}lea.stk {res}:{kind} = {name} 0")
        return res
    else:
        assert False, f"unsupported node for lvalue {node}"


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


def EmitIRConditional(cond, invert: bool, label_false: str, tc: types.TypeCorpus, id_gen: identifier.IdGen):
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
                assert False  # this branch has not been tested
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
        print(f"{TAB}beq {op} 0 {label_false}")
    elif isinstance(cond, cwast.Id):
        assert types.is_bool(cond.x_type)
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


def _EmitExpr2(binary_expr_kind, res, res_type, op1, op2):
    op = _BIN_OP_MAP.get(binary_expr_kind)
    if op is not None:
        print(
            f"{TAB}{op} {res}:{res_type} = {op1} {op2}")
    elif binary_expr_kind is cwast.BINARY_EXPR_KIND.MAX:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op2} {op1}")
    elif binary_expr_kind is cwast.BINARY_EXPR_KIND.MIN:
        print(
            f"{TAB}cmplt {res}:{res_type} = {op1} {op2} {op1} {op2}")
    else:
        assert False, f"unsupported expression {binary_expr_kind}"


def EmitIRExpr(node, tc: types.TypeCorpus, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprCall):
        sig = node.callee.x_type
        assert isinstance(sig, cwast.TypeFun)
        args = [EmitIRExpr(a, tc, id_gen) for a in node.args]
        for a in reversed(args):
            print(f"{TAB}pusharg {a}")
        if isinstance(node.callee, cwast.Id):
            print(f"{TAB}bsr {node.callee.x_symbol.name}")
        else:
            assert False
        if types.is_void(sig.result):
            return None
        else:
            res = id_gen.NewName("call")
            print(f"{TAB}poparg {res}:{StringifyOneType(sig.result, tc)}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{node.x_value}:{StringifyOneType(node.x_type, tc)}"
    elif isinstance(node, cwast.ValFalse):
        return f"0:U8"
    elif isinstance(node, cwast.ValTrue):
        return f"1:U8"
    elif isinstance(node, cwast.ExprLen):
        if isinstance(node.container.x_type, cwast.TypeArray):
            assert False, f"{node} {node.x_value}"
        else:
            assert False, f"{node} container={node.container} type={node.container.x_type}"
    elif isinstance(node, cwast.Id):
        # What we really need to check here is if we need a memcpy
        assert isinstance(node.x_type, (cwast.TypeBase,
                          cwast.TypePtr)), f"{node.x_type}"
        def_node = node.x_symbol
        if isinstance(def_node, cwast.DefGlobal):
            res = id_gen.NewName("globread")
            print(
                f"{TAB}ld.mem {res}:{StringifyOneType(node.x_type, tc)} = {node.x_symbol.name} 0")
            return res
        else:
            return node.x_symbol.name
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr_lhs, tc, id_gen)
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, tc, id_gen)
        op2 = EmitIRExpr(node.expr2, tc, id_gen)
        res = id_gen.NewName("expr2")
        res_type = StringifyOneType(node.x_type, tc)
        _EmitExpr2(node.binary_expr_kind, res, res_type, op1, op2)
        return res
    elif isinstance(node, cwast.ExprPointer):
        op1 = EmitIRExpr(node.expr1, tc, id_gen)
        op2 = EmitIRExpr(node.expr2, tc, id_gen)
        # TODO: add range check
        # assert isinstance(node.expr_bound_or_undef, cwast.ValUndef)
        res = id_gen.NewName("expr2")
        if node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP:
            assert isinstance(node.expr1.x_type, cwast.TypePtr)
            scale = node.expr1.x_type.type.x_size
            # TODO assumed 64
            if scale != 1:
                scaled = id_gen.NewName("scaled")
                # TODO: widen index
                print(
                    f"{TAB}mul {scaled}:{StringifyOneType(node.expr2.x_type, tc)} = {op2} {scale}")
                op2 = scaled
            print(f"{TAB}lea {res}:A64 = {op1} {op2}")
        else:
            assert False, f"unsupported expression {node}"
        return res
    elif isinstance(node, cwast.ExprBitCast):
        res = id_gen.NewName("bitcast")
        expr = EmitIRExpr(node.expr, tc, id_gen)
        print(f"{TAB}bitcast {res}:{StringifyOneType(node.type.x_type, tc)} = {expr}")
        return res
    elif isinstance(node, cwast.ExprAs):
        if (isinstance(node.expr.x_type, cwast.TypeBase) and isinstance(node.type.x_type, cwast.TypeBase)):
            # more compatibility checking needed
            expr = EmitIRExpr(node.expr, tc, id_gen)
            res = id_gen.NewName("as")
            print(
                f"{TAB}conv {res}:{StringifyOneType(node.type.x_type, tc)} = {expr}")
            return res
        elif (isinstance(node.expr.x_type, cwast.TypeArray) and
                isinstance(node.type.x_type, cwast.TypeSlice)):
            addr = _GetLValueAddress(node.expr, tc, id_gen)
            size = node.expr.x_type.size.x_value
            return addr, f"{size}:U64"
        else:
            assert False, f"unsupported cast {node.expr} ({node.expr.x_type}) -> {node.type}"
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, tc, id_gen)
        res = id_gen.NewName("deref")
        print(
            f"{TAB}ld {res}:{StringifyOneType(node.x_type, tc)} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        if types.is_void_or_wrapped_void(node.x_type):
            result = _DUMMY_VOID_REG
        else:
            result = id_gen.NewName("expr")
            print(f"{TAB}.reg {StringifyOneType(node.x_type, tc)} [{result}]")
        for c in node.body:
            EmitIRStmt(c, result, tc, id_gen)
        return result
    elif isinstance(node, cwast.ExprIndex):
        addr = _GetLValueAddress(node, tc, id_gen)
        res = id_gen.NewName("at")
        print(f"{TAB}ld {res}:{StringifyOneType(node.x_type, tc)} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprFront):
        assert isinstance(node.container.x_type,
                          cwast.TypeArray), f"unexpected {node}"
        return _GetLValueAddress(node.container, tc, id_gen)
    elif isinstance(node, cwast.ExprField):
        res = id_gen.NewName("field")
        addr = _GetLValueAddress(node.container, tc, id_gen)
        print(
            f"{TAB}ld {res}:{StringifyOneType(node.x_type, tc)} = {addr} {node.x_field.x_offset}")
        return res
    elif isinstance(node, cwast.ValVoid):
        pass
    else:
        assert False, f"unsupported expression {node.x_srcloc} {node}"

# TODO: support stack allocated objects


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


def _EmitCopy(dst_base, dst_offset, src_base, src_offset, length, alignment, id_gen: identifier.IdGen):
    width = alignment  # TODO: may be capped at 4 for 32bit platforms
    curr = 0
    while curr < length:
        while width > (length - curr):
            width //= 2
        tmp = id_gen.NewName(f"copy{width}")
        print(f"{TAB}.reg U{width*8} [{tmp}]")
        while curr + width <= length:
            print(f"{TAB}ld {tmp} = {src_base} {src_offset + curr}")
            print(f"{TAB}st {dst_base} {dst_offset + curr} = {tmp}")
            curr += width


def _EmitInitialization(dst_base, dst_offset, src_init,  tc: types.TypeCorpus, id_gen: identifier.IdGen):

    def emit_recursively(offset, init):
        nonlocal dst_base, tc, id_gen
        src_type = init.x_type
        assert not isinstance(init, cwast.ValUndef)

        if isinstance(init, cwast.Id):
            if tc.register_types(src_type) is not None and len(tc.register_types(src_type)) == 1:
                res = EmitIRExpr(init, tc, id_gen)
                assert res is not None
                print(f"{TAB}st {dst_base} {offset} = {res}")
            else:
                if isinstance(init.x_type, cwast.DefRec):
                    src = _GetLValueAddress(init, tc, id_gen)
                    _EmitCopy(dst_base, offset, src,
                              0, src_type.x_size, src_type.x_alignment, id_gen)
                else:
                    assert False, f"{init.x_srcloc} {src_type} {init}"
        elif isinstance(init, cwast.ValRec):
            for field, init in symbolize.IterateValRec(init, src_type):
                if init is not None and not isinstance(init, cwast.ValUndef):
                    emit_recursively(offset + field.x_offset, init.value)
        elif isinstance(init, (cwast.ExprAddrOf, cwast.ValNum, cwast.ExprCall, cwast.ExprStmt)):
            res = EmitIRExpr(init, tc, id_gen)
            assert res is not None
            print(f"{TAB}st {dst_base} {offset} = {res}")
        elif isinstance(init, cwast.ExprFront):
            assert isinstance(init.container.x_type, cwast.TypeArray)
            res = _GetLValueAddress(init.container, tc, id_gen)
            print(f"{TAB}st {dst_base} {offset} = {res}")
        elif isinstance(init, cwast.ExprDeref):
            src = _GetLValueAddress(init, tc, id_gen)
            _EmitCopy(src, 0, dst_base, offset,
                      src_type.x_size, src_type.x_alignment, id_gen)
        else:
            assert False, f"{init.x_srcloc} {init} {src_type}"

    emit_recursively(dst_offset, src_init)


def EmitIRStmt(node, result, tc: types.TypeCorpus, id_gen: identifier.IdGen):
    if isinstance(node, cwast.DefVar):
        def_type = node.type_or_auto.x_type
        node.name = id_gen.NewName(node.name)
        if tc.register_types(def_type) is None or len(tc.register_types(def_type)) != 1:
            print(f"{TAB}.stk {node.name} {def_type.x_alignment} {def_type.x_size}")
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                init_base = id_gen.NewName("init_base")
                print(f"{TAB}lea.stk {init_base}:A64 {node.name} 0")
                _EmitInitialization(
                    init_base, 0, node.initial_or_undef, tc, id_gen)
        else:
            if isinstance(node.initial_or_undef, cwast.ValUndef):
                print(
                    f"{TAB}.reg {StringifyOneType(def_type, tc)} [{node.name}]")
            else:
                out = EmitIRExpr(node.initial_or_undef, tc, id_gen)
                assert out is not None, f"Failure to gen code for {node.initial_or_undef}"
                print(
                    f"{TAB}mov {node.name}:{StringifyOneType(def_type, tc)} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        continue_label = id_gen.NewName(node.label)
        break_label = id_gen.NewName(node.label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}  # block start")
        for c in node.body:
            EmitIRStmt(c, result, tc, id_gen)
        print(f".bbl {break_label}  # block end")
    elif isinstance(node, cwast.StmtReturn):
        out = EmitIRExpr(node.expr_ret, tc, id_gen)
        if isinstance(node.x_target, cwast.ExprStmt):
            if not types.is_void_or_wrapped_void(node.expr_ret.x_type):
                print(f"{TAB}mov {result} {out}")
        else:
            if not types.is_void_or_wrapped_void(node.expr_ret.x_type):
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
        if tc.register_types(node.lhs.x_type) and len(tc.register_types(node.lhs.x_type)) == 1:
            out = EmitIRExpr(node.expr_rhs, tc, id_gen)
            if _AssignmentLhsIsInReg(node.lhs):
                # because of the canonicalization step only register promotable
                # scalars will be naked like this
                print(f"{TAB}mov {node.lhs.x_symbol.name} = {out}  # {node}")
            else:
                lhs = _GetLValueAddress(node.lhs, tc, id_gen)
                print(f"{TAB}st {lhs} 0 = {out}")
        else:
            lhs = _GetLValueAddress(node.lhs, tc, id_gen)
            _EmitInitialization(lhs, 0, node.expr_rhs, tc, id_gen)
    elif isinstance(node, cwast.StmtTrap):
        print(f"{TAB}trap")
    else:
        assert False, f"cannot generate code for {node}"


def _EmitMem(data, comment) -> int:
    if is_repeated_single_char(data):
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


def EmitIRDefGlobal(node: cwast.DefGlobal, tc: types.TypeCorpus):
    def_type = node.type_or_auto.x_type
    print(
        f"\n.mem {node.name} {def_type.x_alignment} {'RW' if node.mut else 'RO'}")

    def _emit_recursively(node, cstr, offset: int) -> int:
        nonlocal tc
        assert offset == types.align(offset, cstr.x_alignment)
        if isinstance(node, cwast.ValUndef):
            return _EmitMem(_BYTE_UNDEF * cstr.x_size, f"{offset} undef={tc.canon_name(cstr)}")

        if isinstance(node, cwast.Id):
            node_def = node.x_symbol
            assert isinstance(node_def, cwast.DefGlobal)
            return _emit_recursively(node_def.initial_or_undef, cstr, offset)
        if isinstance(cstr, cwast.TypeBase):
            return _EmitMem(_InitDataForBaseType(cstr, node.x_value),  f"{offset} {tc.canon_name(cstr)}")
        elif isinstance(cstr, cwast.TypeArray):
            print(f"# array: {tc.canon_name(cstr)}")
            width = cstr.size.x_value
            x_type = cstr.type
            if isinstance(x_type, cwast.TypeBase):
                if isinstance(node.x_value, bytes):
                    assert isinstance(x_type, cwast.TypeBase)
                    return _EmitMem(node.x_value, f"{offset} {tc.canon_name(cstr)}")
                else:

                    x_value = node.x_value
                    assert isinstance(x_type, cwast.TypeBase)
                    assert width == len(x_value), f"{width} vs {len(x_value)}"
                    out = bytearray()
                    for v in x_value:
                        out += _InitDataForBaseType(x_type, v)
                    return _EmitMem(out, tc.canon_name(cstr))
            else:
                assert isinstance(node, cwast.ValArray)
                last = cwast.ValUndef()
                stride = cstr.x_size // width
                assert stride * width == cstr.x_size, f"{cstr.x_size} {width}"
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
                return cstr.x_size
        elif isinstance(cstr, cwast.DefRec):
            print(f"# record: {tc.canon_name(cstr)}")
            rel_off = 0
            for f, i in symbolize. IterateValRec(node, cstr):

                if f.x_offset > rel_off:
                    rel_off += _EmitMem(_BYTE_PADDING *
                                        (f.x_offset - rel_off), f"{offset+rel_off} padding")
                if i is not None and not isinstance(i.value, cwast.ValUndef):
                    rel_off += _emit_recursively(i.value,
                                                 f.type.x_type, offset + rel_off)
                else:
                    rel_off += _EmitMem(_BYTE_UNDEF * f.type.x_type.x_size,
                                        tc.canon_name(f.type.x_type))
            return rel_off
        else:
            assert False, f"unhandled node: {cstr}"

    _emit_recursively(node.initial_or_undef, node.type_or_auto.x_type, 0)


def EmitIRDefFun(node, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen):
    if not node.extern:
        _EmitFunctionHeader(node, type_corpus)
        _EmitFunctionProlog(node, type_corpus, id_gen)
        for c in node.body:
            EmitIRStmt(c, None, type_corpus, id_gen)


def main():
    parser = argparse.ArgumentParser(description='pretty_printer')
    parser.add_argument(
        '-emit_ir', help='stop before emitting asm', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.MacroExpansionDecorateASTWithSymbols(mod_topo_order, mod_map)
    for mod in mod_topo_order:
        cwast.StripNodes(mod, cwast.Comment)
        cwast.StripNodes(mod, cwast.DefMacro)
        cwast.StripNodes(mod, cwast.ExprParen)
        cwast.StripNodes(mod, cwast.StmtStaticAssert)

    tc: types.TypeCorpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, tc)
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)

    # Legalize so that code emitter works
    mod_gen = cwast.DefMod("$generated", [], [],
                           x_srcloc=cwast.SRCLOC_GENERATED)
    id_gen = identifier.IdGen()
    str_val_map = {}
    # for key, val in fun_sigs_with_large_args.items():
    #    print (tc.canon_name(key), " -> ", tc.canon_name(val))
    for mod in mod_topo_order:
        canonicalize.ReplaceExprIndex(mod, tc)
        canonicalize.ReplaceConstExpr(mod)
        canonicalize_slice.InsertExplicitValSlice(mod, tc)
        canonicalize.CanonicalizeDefer(mod, [])
        cwast.EliminateEphemeralsRecursively(mod)

    slice_to_struct_map = canonicalize_slice.MakeSliceTypeReplacementMap(
        mod_topo_order, tc)

    for mod in mod_topo_order:
        canonicalize.OptimizeKnownConditionals(mod)
        canonicalize.CanonicalizeStringVal(mod, str_val_map, id_gen)
        canonicalize.CanonicalizeTernaryOp(mod, id_gen)
        canonicalize_slice.ReplaceSlice(mod, tc, slice_to_struct_map)

    for mod in mod_topo_order:
        cwast.CheckAST(mod, set())
        symbolize.VerifyASTSymbolsRecursively(mod)
        typify.VerifyTypesRecursively(mod, tc)
        eval.VerifyASTEvalsRecursively(mod)

    fun_sigs_with_large_args = canonicalize_large_args.FindFunSigsWithLargeArgs(
        tc)
    for mod in mod_topo_order:
        for fun in mod.body_mod:
            # continue
            canonicalize.CanonicalizeBoolExpressionsNotUsedForConditionals(
                fun, tc)
            typify.VerifyTypesRecursively(fun, tc)
            if isinstance(fun, cwast.DefFun):
                canonicalize_large_args.RewriteLargeArgsCallerSide(
                    fun, fun_sigs_with_large_args, tc, id_gen)
                if fun.x_type in fun_sigs_with_large_args:
                    canonicalize_large_args.RewriteLargeArgsCalleeSide(
                        fun, fun_sigs_with_large_args[fun.x_type], tc, id_gen)
                canonicalize.CanonicalizeCompoundAssignments(fun, tc, id_gen)
                canonicalize.CanonicalizeRemoveStmtCond(fun)
            if isinstance(fun, cwast.DefFun) and types.is_void_or_wrapped_void(fun.x_type.result):
                if fun.body:
                    last = fun.body[-1]
                    if isinstance(last, cwast.StmtReturn):
                        continue
                else:
                    last = fun
                void_expr = cwast.ValVoid(
                    x_srcloc=last.x_srcloc, x_type=fun.x_type.result)
                fun.body.append(cwast.StmtReturn(
                    void_expr, x_srcloc=last.x_srcloc, x_target=fun))

    for mod in mod_topo_order:
        cwast.CheckAST(mod, set())
        symbolize.VerifyASTSymbolsRecursively(mod)
        typify.VerifyTypesRecursively(mod, tc)
        eval.VerifyASTEvalsRecursively(mod)

    mod_gen.body_mod += list(str_val_map.values()) + \
        list(slice_to_struct_map.values())
    mod_topo_order = [mod_gen] + mod_topo_order

    if args.emit_ir:
        for mod in mod_topo_order:
            pp.PrettyPrintHTML(mod, tc)
            # pp.PrettyPrint(mod)

        exit(0)

    # Set fully qualified names for all symbols
    for mod in mod_topo_order:
        mod_name = "" if mod.name in ("main", "$builtin") else mod.name + "/"
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                node.name = mod_name + node.name

    # Emit Cwert IR
    for mod in mod_topo_order:
        id_gen.ClearGlobalNames()
        id_gen.LoadGlobalNames(mod)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                EmitIRDefGlobal(node, tc)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                id_gen.ClearLocalNames()
                id_gen.UniquifyLocalNames(node)
                EmitIRDefFun(node, tc, id_gen)


if __name__ == "__main__":
    # import cProfile
    # cProfile.run('main()')
    exit(main())
