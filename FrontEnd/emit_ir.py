#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

import sys
import logging

# from FrontEnd import canoncalize
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import cwast
from FrontEnd import typify
from FrontEnd import eval
from Util import parse

from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)

TAB = "  "


class UniqueId:
    def __init__(self):
        self._names = set()
        self._labels = set()

    def NewCommon(self, prefix, seen) -> str:
        token = prefix.split("$")
        assert len(token) <= 2
        prefix = token[0]
        name = prefix
        if name not in seen:
            seen.add(name)
            return name
        for i in range(1, 100):
            name = f"{prefix}${i}"
            if name not in seen:
                seen.add(name)
                return name
        assert False

    def NewName(self, prefix) -> str:
        return self.NewCommon(prefix, self._names)

    def NewLabel(self, prefix) -> str:
        return self.NewCommon(prefix, self._labels)


def RenderList(items):
    return "[" + " ".join(items) + "]"


_BASE_TYPE_MAP = {
    cwast.BASE_TYPE_KIND.SINT: "S64",
    cwast.BASE_TYPE_KIND.S8: "S8",
    cwast.BASE_TYPE_KIND.S16: "S16",
    cwast.BASE_TYPE_KIND.S32: "S32",
    cwast.BASE_TYPE_KIND.S64: "S64",
    #
    cwast.BASE_TYPE_KIND.UINT: "U64",
    cwast.BASE_TYPE_KIND.U8: "U8",
    cwast.BASE_TYPE_KIND.U16: "U16",
    cwast.BASE_TYPE_KIND.U32: "U32",
    cwast.BASE_TYPE_KIND.U64: "U64",
    #
    cwast.BASE_TYPE_KIND.R32: "F32",
    cwast.BASE_TYPE_KIND.R64: "F64",
    #
    cwast.BASE_TYPE_KIND.BOOL: "U8",
}


def StringifyType(type):
    if isinstance(type, cwast.TypePtr):
        return "A64"
    elif isinstance(type, cwast.TypeBase):
        return _BASE_TYPE_MAP[type.base_type_kind]
    else:
        assert False, f"unsupported type: {type}"


def GetName(node):
    if isinstance(node,  cwast.DefFun):
        mod = node.x_parent
        mod_name = "" if mod.name == "main" else mod.name + "/"
        return mod_name + node.name
    elif isinstance(node,  cwast.DefGlobal):
        mod = node.x_parent
        mod_name = "" if mod.name == "main" else mod.name + "/"
        return mod_name + node.name
    else:
        assert False


def _EmitFunctionHeader(fun: cwast.DefFun):
    sig: cwast.TypeFun = fun.x_type
    outs = [StringifyType(sig.result)]
    ins = [StringifyType(p.type) for p in sig.params]
    print(
        f"\n\n.fun {GetName(fun)} NORMAL {RenderList(outs)} = {RenderList(ins)}")


def _EmitFunctionProlog(fun: cwast.DefFun, id_gen: UniqueId):
    print(f".bbl {id_gen.NewLabel('entry')}")
    for p in fun.params:
        p.name = id_gen.NewName(p.name)
        print(f"{TAB}poparg {p.name}:{StringifyType(p.type.x_type)}")


def _EmitMem(name, align, rw, data):
    print(f"\n.mem {name} {align} {'RW' if rw else 'RO'}")
    if isinstance(data, bytes):
        print(f'.data 1 "{parse.BytesToEscapedString(data)}"')


def _GetLValueAddress(node, id_gen: UniqueId) -> Any:
    if isinstance(node, cwast.ExprIndex):
        container = _GetLValueAddress(node.container, id_gen)
        if node.expr_index.x_value == 0:
            return container
        else:
            assert False
            index = EmitIRExpr(node_stack + [node.expr_index, id_gen])
    elif isinstance(node, cwast.ExprDeref):
        return EmitIRExpr(node.expr, id_gen)
    elif isinstance(node, cwast.Id):
        assert isinstance(node.x_type, cwast.TypeArray)
        name = GetName(node.x_symbol)
        res = id_gen.NewName("tmp")
        # TODO
        kind = "A64"
        print(f"{TAB}lea.mem {res}:{kind} = {name} 0")
        return res
    else:
        assert False


_MAP_COMPARE = {
    cwast.BINARY_EXPR_KIND.NE: "bne",
    cwast.BINARY_EXPR_KIND.EQ: "beq",
    cwast.BINARY_EXPR_KIND.LT: "blt",
    cwast.BINARY_EXPR_KIND.LE: "ble",
}


def EmitIRConditional(cond, label_t: str, label_f: str, id_gen: UniqueId):
    if isinstance(cond, cwast.Expr1):
        assert cond.unary_expr_kind is cwast.UNARY_EXPR_KIND.NOT
        EmitIRConditional(cond.expr, label_f, label_t, id_gen)
    elif isinstance(cond, cwast.Expr2):
        kind = cond.binary_expr_kind
        if kind is cwast.BINARY_EXPR_KIND.ANDSC:
            label_and = id_gen.next("br_and")
            EmitIRConditional(cond.expr1, label_and, label_f, id_gen)
            print(f".bbl {label_and}")
            EmitIRConditional(cond.expr2, label_t, label_f, id_gen)
        elif kind is cwast.BINARY_EXPR_KIND.ORSC:
            label_or = id_gen.next("br_or")
            EmitIRConditional(cond.expr1, label_t, label_or, id_gen)
            print(f".bbl {label_or}")
            EmitIRConditional(cond.expr2, label_t, label_f, id_gen)
        else:
            op1 = EmitIRExpr(cond.expr1, id_gen)
            op2 = EmitIRExpr(cond.expr2, id_gen)

            if kind is cwast.BINARY_EXPR_KIND.GT:
                kind = cwast.BINARY_EXPR_KIND.LT
                op1, op2 = op2, op1
            elif kind is cwast.BINARY_EXPR_KIND.GE:
                kind = cwast.BINARY_EXPR_KIND.LE
                op1, op2 = op2, op1
            print(f"{TAB}{_MAP_COMPARE[kind]} {op1} {op2} {label_t}")
            print(f"{TAB}br {label_f}")

    else:
        assert False


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


def EmitIRExpr(node, id_gen: UniqueId) -> Any:
    if isinstance(node, cwast.ExprCall):
        sig = node.callee.x_type
        assert isinstance(sig, cwast.TypeFun)
        args = [EmitIRExpr(a, id_gen) for a in node.args]
        for a in reversed(args):
            print(f"{TAB}pusharg {a}")
        if isinstance(node.callee, cwast.Id):
            print(f"{TAB}bsr {node.callee.x_symbol.name}")
        else:
            assert False
        if types.is_void(sig.result):
            return None
        else:
            res = id_gen.NewName("tmp")
            print(f"{TAB}poparg {res}:{StringifyType(sig.result)}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{node.number}:{StringifyType(node.x_type)}"
    elif isinstance(node, cwast.ExprLen):
        if node.container.x_value is not None:
            return f"{len(node.container.x_value)}:{StringifyType(node.x_type)}"
        else:
            assert False
    elif isinstance(node, cwast.Id):
        def_node = node.x_symbol
        assert isinstance(
            def_node, (cwast.DefVar, cwast.FunParam)), f"{def_node}"
        assert not isinstance(
            def_node.x_type, (cwast.TypeArray, cwast.TypeSlice))
        return node.name
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr, id_gen)
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, id_gen)
        op2 = EmitIRExpr(node.expr2, id_gen)
        res = id_gen.NewName("tmp")
        op = _BIN_OP_MAP.get(node.binary_expr_kind)
        if op is not None:
            print(f"{TAB}{op} {res}:{StringifyType(node.x_type)} = {op1} {op2}")
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.INCP:
            assert isinstance(node.expr1.x_type, cwast.TypePtr)
            assert node.expr1.x_type.type.x_size == 1
            # TODO assumed 64
            print(f"{TAB}lea {res}:A64 = {op1} {op2}")
        else:
            assert False
        return res
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, id_gen)
        res = id_gen.NewName("tmp")
        print(f"{TAB}ld {res}:{StringifyType(node.expr.x_type)} = {addr} 0")
        return res
    else:
        assert False, f"unsupported expression {node}"


def EmitIR(node, id_gen: UniqueId):
    if isinstance(node, cwast.Comment):
        return
    elif isinstance(node, cwast.DefEnum):
        return
    elif isinstance(node, cwast.DefRec):
        return
    elif isinstance(node, cwast.DefMacro):
        return
    elif isinstance(node, cwast.DefMod):
        for c in node.body_mod:
            EmitIR(c, id_gen)
    elif isinstance(node, cwast.DefFun):
        if not node.extern:
            _EmitFunctionHeader(node)
            _EmitFunctionProlog(node, id_gen)
            for c in node.body:
                EmitIR(c, id_gen)
    elif isinstance(node, cwast.DefGlobal):
        def_type = node.x_type
        if isinstance(def_type, cwast.TypeBase):
            assert False, f"top level defvar base type"
        elif isinstance(def_type, cwast.TypeArray):
            init = node.initial_or_undef.x_value
            if isinstance(init, bytes):
                assert isinstance(def_type.type, cwast.TypeBase)
                _EmitMem(GetName(node), 1, node.mut, init)
            else:
                out = []
                size = def_type.size.x_value
                init = node.initial_or_undef.x_value
                print("@@@@", init, size)

        else:
            assert False, f"top level defvar unsupported type {node.x_type}"
    elif isinstance(node, cwast.DefVar):
        def_type = node.x_type
        node.name = id_gen.NewName(node.name)
        if isinstance(def_type, cwast.TypeBase):
            out = EmitIRExpr(node.initial_or_undef, id_gen)
            print(f"{TAB}mov {node.name} = {out}")
        else:
            assert False, f"defvar non base type"
    elif isinstance(node, cwast.StmtBlock):
        continue_label = id_gen.NewLabel(node.label)
        break_label = id_gen.NewLabel(node.label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}")
        for c in node.body:
            EmitIR(c, id_gen)
        print(f".bbl {break_label}")

    elif isinstance(node, cwast.StmtReturn):
        if node.expr_ret:
            out = EmitIRExpr(node.expr_ret, id_gen)
            print(f"{TAB}pusharg {out}")
        print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label[1]
        print(f"{TAB}br {block}")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label[0]
        print(f"{TAB}br {block}")
    elif isinstance(node, cwast.StmtExpr):
        EmitIRExpr(node.expr, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_t = id_gen.NewLabel("br_t")
        label_f = id_gen.NewLabel("br_f")
        EmitIRConditional(node.cond, label_t, label_f, id_gen)
        if node.body_t and node.body_f:
            label_n = id_gen.NewLabel("br_n")
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIR(c, id_gen)
            print(f"{TAB}br {label_n}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                EmitIR(c, id_gen)
            print(f".bbl {label_n}")
        elif node.body_t:
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIR(c, id_gen)
            print(f".bbl {label_f}")
        elif node.body_f:
            print(f".bbl {label_f}")
            for c in node.body_t:
                EmitIR(c, id_gen)
            print(f".bbl {label_t}")
        else:
            print(f".bbl {label_t}")
            print(f".bbl {label_f}")
    elif isinstance(node, cwast.StmtAssignment):
        out = EmitIRExpr(node.expr, id_gen)
        if isinstance(node.lhs, cwast.Id):
            # because of the canonicalization step only register promotable
            # scalars will naked like this
            print(f"{TAB}mov {node.lhs.x_symbol.name} = {out}")
        else:
            lhs = _GetLValueAddress(node.lhs, id_gen)
            print(f"{TAB}st {lhs} 0 = {out}")
    else:
        assert False, f"cannot generate code for {node}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = cwast.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.DecorateASTWithSymbols(mod_topo_order, mod_map)
    type_corpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, type_corpus)
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)
    
    id_gen = UniqueId()
    for mod in asts:
        EmitIR(mod, id_gen)
