#!/usr/bin/python3

"""Translator from AST to Cwerg IR

"""

import dataclasses
import sys
import logging

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

def _EmitFunctionHeader(mod: cwast.DefMod, fun: cwast.DefFun):
    sig: cwast.TypeFun = fun.x_type
    outs = [StringifyType(sig.result)]
    ins = [StringifyType(p.type) for p in sig.params]
    print(
        f"\n\n.fun {GetName(fun)} NORMAL {RenderList(outs)} = {RenderList(ins)}")


def _EmitFunctionProlog(fun: cwast.DefFun, id_gen: UniqueId):
    print(f".bbl {id_gen.NewLabel('entry')}")
    sig: cwast.TypeFun = fun.x_type
    for p in sig.params:
        p.name = id_gen.NewName(p.name)
        print(f"{TAB}poparg {p.name}:{StringifyType(p.type)}")


def _EmitMem(name, align, rw, data):
    print(f"\n.mem {name} {align} {'RW' if rw else 'RO'}")
    if isinstance(data, bytes):
        print(f'.data 1 "{parse.BytesToEscapedString(data)}"')


def _GetLValueAddress(node_stack, id_gen: UniqueId) -> Any:
    node = node_stack[-1]

    if isinstance(node, cwast.ExprIndex):
        container = _GetLValueAddress(node_stack + [node.container], id_gen)
        if node.expr_index.x_value == 0:
            return container
        else:
            assert False
            index = EmitIRExpr(node_stack + [node.expr_index, id_gen])
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


def EmitIRExpr(node_stack, id_gen: UniqueId) -> Any:
    node = node_stack[-1]
    if isinstance(node, cwast.ExprCall):
        sig = node.callee.x_type
        assert isinstance(sig, cwast.TypeFun)
        args = [EmitIRExpr(node_stack + [a], id_gen) for a in node.args]
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
    elif isinstance(node, cwast.ExprAddrOf):
        return _GetLValueAddress(node_stack + [node.expr], id_gen)


def EmitIR(node_stack, id_gen: UniqueId):
    node = node_stack[-1]
    if isinstance(node, cwast.Comment):
        return
    elif isinstance(node, cwast.DefMod):
        for c in node.body_mod:
            EmitIR(node_stack + [c], id_gen)
    elif isinstance(node, cwast.DefFun):
        if not node.extern:
            _EmitFunctionHeader(node_stack[0], node)
            _EmitFunctionProlog(node, id_gen)
            for c in node.body:
                EmitIR(node_stack + [c], id_gen)
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

    elif isinstance(node, cwast.StmtReturn):
        if node.expr_ret:
            out = EmitIRExpr(node_stack + [node.expr_ret], id_gen)
            print(f"{TAB}pusharg {out}")
        print(f"{TAB}ret")
    elif isinstance(node, cwast.StmtExpr):
        EmitIRExpr(node_stack + [node.expr], id_gen)
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
    typify.DecorateASTWithTypes(mod_topo_order, mod_map, type_corpus)
    eval.DecorateASTWithPartialEvaluation(mod_topo_order, mod_map)

    id_gen = UniqueId()
    for mod in asts:
        EmitIR([mod], id_gen)
