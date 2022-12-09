#!/usr/bin/python3

"""Type annotator for Cwerg AST

"""

import dataclasses
import sys
import logging

from FrontEnd import cwast
from FrontEnd import symtab
from FrontEnd import types
from FrontEnd import pp

from typing import List, Dict, Set, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)


class CloningContext:

    def __init__(self, no, symtab_map: Dict[str, symtab.SymTab]):
        self._no = no
        self.macro_parameter: Dict[str, Tuple[cwast.MacroParam, Any]] = {}
        self.symtab_map = symtab_map

    def GenUniqueName(self, name: str):
        assert name.startswith("$"), f"expected macro id {name}"
        self._no += 1
        return f"{name[1:]}${self._no}"

    def RegisterSymbol(self, name, value):
        assert name not in self.macro_parameter
        self.macro_parameter[name] = value

    def GetSymbol(self, name):
        return self.macro_parameter[name]

    def Reset(self):
        self.macro_parameter.clear()


def CloneRecursively(node, ctx: CloningContext):
    clone = dataclasses.replace(node)
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            setattr(clone, c, CloneRecursively(getattr(node, c), ctx))
        elif nfd.kind is cwast.NFK.LIST:
            out = []
            if c in ("body_t", "body_f"):
                pass
            for cc in getattr(node, c):
                out.append(CloneRecursively(cc, ctx))
            if c in ("body_t", "body_f"):
                pass
            setattr(clone, c, out)
    return clone


def ExpandMacroRecursively(node, ctx: CloningContext) -> Any:
    if isinstance(node, cwast.MacroVar):
        assert node.name.startswith("$")
        new_name = ctx.GenUniqueName(node.name)
        type_or_auto = ExpandMacroRecursively(node.type_or_auto, ctx)
        initial_or_undef = ExpandMacroRecursively(node.initial_or_undef, ctx)
        ctx.RegisterSymbol(
            node.name, (cwast.MACRO_PARAM_KIND.EXPR, cwast.Id(new_name, "")))
        return cwast.DefVar(False, node.mut, new_name, type_or_auto, initial_or_undef)
    elif isinstance(node, cwast.MacroVarIndirect):
        assert node.name.startswith("$")
        kind, new_name = ctx.GetSymbol(node.name)
        assert kind is cwast.MACRO_PARAM_KIND.ID
        assert not new_name.startswith("$")
        type_or_auto = ExpandMacroRecursively(node.type_or_auto, ctx)
        initial_or_undef = ExpandMacroRecursively(node.initial_or_undef, ctx)
        return cwast.DefVar(False, node.mut, new_name, type_or_auto, initial_or_undef)
    elif isinstance(node, cwast.MacroId):
        assert node.name.startswith("$")
        kind, arg = ctx.GetSymbol(node.name)
        assert kind in (cwast.MACRO_PARAM_KIND.EXPR,
                        cwast.MACRO_PARAM_KIND.LAZY_EXPR,
                        cwast.MACRO_PARAM_KIND.STMT_LIST), f"{node.name} -> {kind} {arg}"
        return arg

    clone = dataclasses.replace(node)
    if isinstance(clone, cwast.FieldVal) and clone.init_field.startswith("$"):
        kind, arg = ctx.GetSymbol(clone.init_field)
        assert kind == cwast.MACRO_PARAM_KIND.FIELD
        clone.init_field = arg
    elif isinstance(clone, (cwast.ExprField, cwast.ExprOffsetof)) and clone.field.startswith("$"):
        kind, arg = ctx.GetSymbol(clone.field)
        assert kind == cwast.MACRO_PARAM_KIND.FIELD, f"expexted id got {kind} {arg}"
        clone.field = arg

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            replacement = ExpandMacroRecursively(getattr(node, c), ctx)
            setattr(clone, c, replacement)
        elif nfd.kind is cwast.NFK.LIST:
            out = []
            for cc in getattr(node, c):
                exp = ExpandMacroRecursively(cc, ctx)
                if isinstance(exp, cwast.MacroListArg):
                    out += exp.args
                else:
                    out.append(exp)
            setattr(clone, c, out)
    return clone


def ExpandMacro(invoke: cwast.MacroInvoke, sym_tab: symtab.SymTab, ctx: CloningContext) -> Any:
    macro = sym_tab.resolve_sym(invoke.name.split("/"), ctx.symtab_map, False)
    assert isinstance(macro, cwast.DefMacro)
    params = macro.params_macro
    args = invoke.args
    assert len(params) == len(invoke.args)
    logger.info("Expanding Macro Invocation: %s", invoke)
    logger.info("Macro: %s", macro)
    ctx.Reset()
    out = []
    for p, a in zip(params, invoke.args):
        assert p.name.startswith("$")
        if p.macro_param_kind == cwast.MACRO_PARAM_KIND.EXPR:
            name = ctx.GenUniqueName("$eval")
            out.append(cwast.DefVar(False, False, name, cwast.TypeAuto(), a))
            arg = cwast.Id(name, "")
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.LAZY_EXPR:
            arg = a
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.STMT_LIST:
            assert isinstance(a, cwast.MacroListArg)
            arg = a
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.ID:
            assert isinstance(a, cwast.Id)
            arg = a.name
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.FIELD:
            assert isinstance(a, cwast.Id)
            arg = a.name
        else:
            assert False
        ctx.RegisterSymbol(p.name, (p.macro_param_kind, arg))

    for node in macro.body_macro:
        logger.info("Expand macro body node: %s", node)
        exp = ExpandMacroRecursively(node, ctx)
        if isinstance(exp, cwast.MacroListArg):
            out += exp.args
        else:
            out.append(exp)
    if len(out) == 1:
        return out[0]
    return cwast.MacroListArg(out)


def FindAndExpandMacrosRecursively(node, sym_tab,  ctx):
    # TODO: support macro-invocatios which produce new macro-invocations
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, c)
            if isinstance(child, cwast.MacroInvoke):
                new_child = ExpandMacro(child, sym_tab, ctx)
                setattr(node, c, new_child)
                child = new_child
            FindAndExpandMacrosRecursively(child, sym_tab, ctx)
        elif nfd.kind is cwast.NFK.LIST:
            children = getattr(node, c)
            new_children = []
            for child in children:
                if isinstance(child, cwast.MacroInvoke):
                    exp = ExpandMacro(child, sym_tab, ctx)
                    if isinstance(exp, cwast.MacroListArg):
                        new_children += exp.args
                    else:
                        new_children.append(exp)
                else:
                    new_children.append(child)
            setattr(node, c, new_children)
            for child in new_children:
                FindAndExpandMacrosRecursively(child, sym_tab, ctx)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    asts = []
    try:
        while True:
            stream = cwast.ReadTokens(sys.stdin)
            t = next(stream)
            assert t == "("
            sexpr = cwast.ReadSExpr(stream)
            # print(sexpr)
            asts.append(sexpr)
    except StopIteration:
        pass

    mod_topo_order, mod_map = symtab.ModulesInTopologicalOrder(asts)

    symtab_map: Dict[str, symtab.SymTab] = {}
    for m in mod_topo_order:
        symtab_map[m] = symtab.ExtractGlobalSymTab(mod_map[m], mod_map)

    for m in mod_topo_order:
        mod = mod_map[m]
        sym_tab = symtab_map[mod.name]
        for node in mod.body_mod:
            if not isinstance(node, (cwast.DefFun, cwast.DefMacro, cwast.Comment)):
                logger.info("Resolving global object: %s", node)
                symtab.ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
                    node, sym_tab, symtab_map)

    for m in mod_topo_order:
        mod = mod_map[m]
        sym_tab = symtab_map[mod.name]
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun):
                logger.info("Expand macros in fun: %s", node)
                ctx = CloningContext(1, symtab_map)
                FindAndExpandMacrosRecursively(node, sym_tab, ctx)
                out = [[""]]
                pp.RenderRecursively(node, out, 0)
                for a in out:
                    print("".join(a))
