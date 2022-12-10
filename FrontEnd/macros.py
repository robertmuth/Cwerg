#!/usr/bin/python3

"""Macro Expander

"""

import dataclasses
import sys
import logging

from FrontEnd import cwast


from typing import List, Dict, Set, Optional, Union, Any, Tuple

logger = logging.getLogger(__name__)


class MacroContext:

    def __init__(self, no):
        self._no = no
        self.macro_parameter: Dict[str, Tuple[cwast.MacroParam, Any]] = {}

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


def CloneNodeRecursively(node):
    clone = dataclasses.replace(node)
    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            setattr(clone, c, CloneNodeRecursively(getattr(node, c)))
        elif nfd.kind is cwast.NFK.LIST:
            out = [CloneNodeRecursively(cc) for cc in getattr(node, c)]
            setattr(clone, c, out)
    return clone


def ExpandMacroRecursively(node, ctx: MacroContext) -> Any:
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
                        cwast.MACRO_PARAM_KIND.TYPE,
                        cwast.MACRO_PARAM_KIND.STMT_LIST), f"{node.name} -> {kind} {arg}"
        return CloneNodeRecursively(arg)

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


def ExpandMacro(invoke: cwast.MacroInvoke, macro: cwast.DefMacro, ctx: MacroContext) -> Any:
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
            arg = a
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.STMT_LIST:
            assert isinstance(a, cwast.MacroListArg)
            arg = a
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.TYPE:
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
