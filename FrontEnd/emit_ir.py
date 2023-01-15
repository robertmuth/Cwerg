#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

import sys
import logging

from typing import List, Dict, Set, Optional, Union, Any, Tuple


from FrontEnd import canonicalize
from FrontEnd import symbolize
from FrontEnd import types
from FrontEnd import cwast
from FrontEnd import typify
from FrontEnd import eval
from FrontEnd import identifier
from FrontEnd import parse

from Util.parse import BytesToEscapedString


logger = logging.getLogger(__name__)

TAB = "  "


def RenderList(items):
    return "[" + " ".join(items) + "]"


def StringifyOneType(node, type_corpus: types.TypeCorpus):
    t = type_corpus.register_types(node)
    assert len(t) == 1
    return t[0]


def _EmitFunctionHeader(fun: cwast.DefFun, type_corpus: types.TypeCorpus):
    sig: cwast.TypeFun = fun.x_type
    ins = []
    for p in sig.params:
        ins += type_corpus.register_types(p.type)
    print(
        f"\n\n.fun {fun.name} NORMAL [{StringifyOneType(sig.result, type_corpus)}] = [{' '.join(ins)}]")


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


def _EmitMem(name, align, rw, data):
    print(f"\n.mem {name} {align} {'RW' if rw else 'RO'}")
    if isinstance(data, bytes):
        print(f'.data 1 "{BytesToEscapedString(data)}"')


ZERO_INDEX = "0"


def _GetLValueAddress(node, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprIndex):
        container = _GetLValueAddress(node.container, id_gen)
        if node.expr_index.x_value == 0:
            return container
        else:
            assert False
            index = EmitIRExpr(node_stack + [node.expr_index, id_gen])
    elif isinstance(node, cwast.ExprDeref):
        return EmitIRExpr(node.expr, type_corpus, id_gen)
    elif isinstance(node, cwast.Id):
        assert isinstance(node.x_type, cwast.TypeArray)
        name = node.x_symbol.name
        res = id_gen.NewName("tmp")
        # TODO
        kind = "A64"
        print(f"{TAB}lea.mem {res}:{kind} = {name} 0")
        return res
    else:
        assert False, f"unsupported node for lvalue {node}"


_MAP_COMPARE = {
    cwast.BINARY_EXPR_KIND.NE: "bne",
    cwast.BINARY_EXPR_KIND.EQ: "beq",
    cwast.BINARY_EXPR_KIND.LT: "blt",
    cwast.BINARY_EXPR_KIND.LE: "ble",
}


def EmitIRConditional(cond, label_t: str, label_f: str, id_gen: identifier.IdGen):
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
            op1 = EmitIRExpr(cond.expr1, type_corpus, id_gen)
            op2 = EmitIRExpr(cond.expr2, type_corpus, id_gen)

            if kind is cwast.BINARY_EXPR_KIND.GT:
                kind = cwast.BINARY_EXPR_KIND.LT
                op1, op2 = op2, op1
            elif kind is cwast.BINARY_EXPR_KIND.GE:
                kind = cwast.BINARY_EXPR_KIND.LE
                op1, op2 = op2, op1
            print(f"{TAB}{_MAP_COMPARE[kind]} {op1} {op2} {label_t}")
            print(f"{TAB}br {label_f}")

    elif isinstance(cond, cwast.Id):
        assert types.is_bool(cond.x_type)
        assert isinstance(cond.x_symbol, (cwast.DefVar, cwast.FunParam))
        print(f"{TAB}bne {cond.name} 0 {label_t}")
        print(f"{TAB}br {label_f}")
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


def EmitIRExpr(node, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen) -> Any:
    if isinstance(node, cwast.ExprCall):
        sig = node.callee.x_type
        assert isinstance(sig, cwast.TypeFun)
        args = [EmitIRExpr(a, type_corpus, id_gen) for a in node.args]
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
            print(f"{TAB}poparg {res}:{StringifyOneType(sig.result, type_corpus)}")
            return res
    elif isinstance(node, cwast.ValNum):
        return f"{node.number}:{StringifyOneType(node.x_type, type_corpus)}"
    elif isinstance(node, cwast.ExprLen):
        if node.container.x_value is not None:
            return f"{len(node.container.x_value)}:{StringifyOneType(node.x_type, type_corpus)}"
        else:
            assert False, f"{node} {node.container}"
    elif isinstance(node, cwast.Id):
        return node.x_symbol.name
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node.expr, id_gen)
    elif isinstance(node, cwast.Expr2):
        op1 = EmitIRExpr(node.expr1, type_corpus, id_gen)
        op2 = EmitIRExpr(node.expr2, type_corpus, id_gen)
        res = id_gen.NewName("tmp")
        op = _BIN_OP_MAP.get(node.binary_expr_kind)
        if op is not None:
            print(
                f"{TAB}{op} {res}:{StringifyOneType(node.x_type, type_corpus)} = {op1} {op2}")
        elif node.binary_expr_kind is cwast.BINARY_EXPR_KIND.INCP:
            assert isinstance(node.expr1.x_type, cwast.TypePtr)
            assert node.expr1.x_type.type.x_size == 1
            # TODO assumed 64
            print(f"{TAB}lea {res}:A64 = {op1} {op2}")
        else:
            assert False
        return res
    elif isinstance(node, cwast.ExprAs):
        if (isinstance(node.expr.x_type, cwast.TypeArray) and
                isinstance(node.type.x_type, cwast.TypeSlice)):
            addr = _GetLValueAddress(node.expr, id_gen)
            size = node.expr.x_type.size.x_value
            return addr, f"{size}:U64"
        assert False, f"unsupported cast {node.expr} -> {node.type}"
    elif isinstance(node, cwast.ExprDeref):
        addr = EmitIRExpr(node.expr, type_corpus, id_gen)
        res = id_gen.NewName("tmp")
        print(
            f"{TAB}ld {res}:{StringifyOneType(node.expr.x_type, type_corpus)} = {addr} 0")
        return res
    elif isinstance(node, cwast.ExprStmt):
        result = id_gen.NewName("expr")
        for c in node.body:
            EmitIRStmt(c, result, type_corpus, id_gen)
    else:
        assert False, f"unsupported expression {node}"


def EmitIRStmt(node, result, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen):
    if isinstance(node, cwast.Comment):
        return
    elif isinstance(node, cwast.DefVar):
        def_type = node.x_type
        node.name = id_gen.NewName(node.name)
        assert type_corpus.register_types(
            def_type) is not None, f"unsupported type {def_type}"
        out = EmitIRExpr(node.initial_or_undef, type_corpus, id_gen)
        print(f"{TAB}mov {node.name} = {out}")
    elif isinstance(node, cwast.StmtBlock):
        continue_label = id_gen.NewName(node.label)
        break_label = id_gen.NewName(node.label)
        node.label = (continue_label, break_label)

        print(f".bbl {continue_label}")
        for c in node.body:
            EmitIRStmt(c, result, type_corpus, id_gen)
        print(f".bbl {break_label}")

    elif isinstance(node, cwast.StmtReturn):
        out = EmitIRExpr(node.expr_ret, type_corpus, id_gen)
        if isinstance(node.x_target, cwast.ExprStmt):
            print(f"{TAB}mov {result} {out}")
        else:
            if node.expr_ret:
                print(f"{TAB}pusharg {out}")
            print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtBreak):
        block = node.x_target.label[1]
        print(f"{TAB}br {block}")
    elif isinstance(node, cwast.StmtContinue):
        block = node.x_target.label[0]
        print(f"{TAB}br {block}")
    elif isinstance(node, cwast.StmtExpr):
        EmitIRExpr(node.expr, type_corpus, id_gen)
    elif isinstance(node, cwast.StmtIf):
        label_t = id_gen.NewName("br_t")
        label_f = id_gen.NewName("br_f")
        EmitIRConditional(node.cond, label_t, label_f, id_gen)
        if node.body_t and node.body_f:
            label_n = id_gen.NewName("br_n")
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f"{TAB}br {label_n}")
            print(f".bbl {label_f}")
            for c in node.body_f:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_n}")
        elif node.body_t:
            print(f".bbl {label_t}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_f}")
        elif node.body_f:
            print(f".bbl {label_f}")
            for c in node.body_t:
                EmitIRStmt(c, result, type_corpus, id_gen)
            print(f".bbl {label_t}")
        else:
            print(f".bbl {label_t}")
            print(f".bbl {label_f}")
    elif isinstance(node, cwast.StmtAssignment):
        out = EmitIRExpr(node.expr, type_corpus, id_gen)
        if isinstance(node.lhs, cwast.Id):
            # because of the canonicalization step only register promotable
            # scalars will be naked like this
            print(f"{TAB}mov {node.lhs.x_symbol.name} = {out}")
        else:
            lhs = _GetLValueAddress(node.lhs, id_gen)
            print(f"{TAB}st {lhs} 0 = {out}")
    else:
        assert False, f"cannot generate code for {node}"


def EmitIRDefGlobal(node: cwast.DefGlobal):
    def_type = node.x_type
    if isinstance(def_type, cwast.TypeBase):
        assert False, f"top level defvar base type"
    elif isinstance(def_type, cwast.TypeArray):
        init = node.initial_or_undef.x_value
        if isinstance(init, bytes):
            assert isinstance(def_type.type, cwast.TypeBase)
            _EmitMem(node.name, 1, node.mut, init)
        else:
            out = []
            size = def_type.size.x_value
            init = node.initial_or_undef.x_value
            print("@@@@", init, size)


def EmitIRDefFun(node, type_corpus: types.TypeCorpus, id_gen: identifier.IdGen):
    if not node.extern:
        _EmitFunctionHeader(node, type_corpus)
        _EmitFunctionProlog(node, type_corpus, id_gen)
        for c in node.body:
            EmitIRStmt(c, None, type_corpus, id_gen)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = parse.ReadModsFromStream(sys.stdin)

    mod_topo_order, mod_map = symbolize.ModulesInTopologicalOrder(asts)
    symbolize.DecorateASTWithSymbols(mod_topo_order, mod_map)
    type_corpus: types.TypeCorpus = types.TypeCorpus(
        cwast.BASE_TYPE_KIND.U64, cwast.BASE_TYPE_KIND.S64)
    typify.DecorateASTWithTypes(mod_topo_order, type_corpus)
    eval.DecorateASTWithPartialEvaluation(mod_topo_order)
    mod_gen = cwast.DefMod("$generated", [], [])
    id_gen = identifier.IdGen()
    str_map = {}
    for mod in mod_topo_order:
        canonicalize.CanonicalizeStringVal(mod, str_map, id_gen)
        canonicalize.CanonicalizeTernaryOp(mod, id_gen)
    mod_gen.body_mod += list(str_map.values())

    mod_topo_order = [mod_gen] + mod_topo_order
    for mod in mod_topo_order:
        mod_name = "" if mod.name == "main" else mod.name + "/"
        for node in mod.body_mod:
            if isinstance(node, (cwast.DefFun, cwast.DefGlobal)):
                node.name = mod_name + node.name
                if isinstance(node, cwast.DefFun):
                    id_gen = identifier.IdGen()

    for mod in mod_topo_order:
        id_gen.ClearGlobalNames()
        id_gen.LoadGlobalNames(mod)
        for node in mod.body_mod:
            if isinstance(node, cwast.DefGlobal):
                EmitIRDefGlobal(node)
        for node in mod.body_mod:

            if isinstance(node, cwast.DefFun):
                id_gen.ClearLocalNames()
                id_gen.UniquifyLocalNames(node)
                EmitIRDefFun(node, type_corpus, id_gen)
