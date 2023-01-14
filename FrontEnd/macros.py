#!/usr/bin/python3

"""Macro Expander

"""

import dataclasses
import logging
import pp

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

    def RegisterSymbol(self, name, value, check_clash=False):
        if check_clash:
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
        kind, new_name = ctx.GetSymbol(node.name)
        assert kind is cwast.MACRO_PARAM_KIND.ID
        assert isinstance(new_name, cwast.Id)
        assert not new_name.name.startswith("$")
        type_or_auto = ExpandMacroRecursively(node.type_or_auto, ctx)
        initial_or_undef = ExpandMacroRecursively(node.initial_or_undef, ctx)
        return cwast.DefVar(node.mut, new_name.name, type_or_auto, initial_or_undef)
    elif isinstance(node, cwast.MacroId):
        assert node.name.startswith("$"), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name)
        assert kind in (cwast.MACRO_PARAM_KIND.EXPR,
                        cwast.MACRO_PARAM_KIND.ID,
                        cwast.MACRO_PARAM_KIND.TYPE,
                        cwast.MACRO_PARAM_KIND.STMT_LIST), f"{node.name} -> {kind} {arg}"
        return CloneNodeRecursively(arg)
    elif isinstance(node, cwast.MacroFor):
        assert node.name.startswith("$"), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name_list)
        assert isinstance(arg, cwast.MacroListArg)
        out = []
        for item in arg.args:
            ctx.RegisterSymbol(node.name, (cwast.MACRO_PARAM_KIND.EXPR, item))
            for b in node.body_for:
                exp = ExpandMacroRecursively(b, ctx)
                if isinstance(exp, cwast.MacroListArg):
                    out += exp.args
                else:
                    out.append(exp)
        return cwast.MacroListArg(out)

    clone = dataclasses.replace(node)
    if isinstance(clone, cwast.FieldVal) and clone.init_field.startswith("$"):
        kind, arg = ctx.GetSymbol(clone.init_field)
        assert kind == cwast.MACRO_PARAM_KIND.FIELD
        clone.init_field = arg.name
    elif isinstance(clone, (cwast.ExprField, cwast.ExprOffsetof)) and clone.field.startswith("$"):
        kind, arg = ctx.GetSymbol(clone.field)
        assert kind == cwast.MACRO_PARAM_KIND.FIELD, f"expexted id got {kind} {arg}"
        clone.field = arg.name

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            replacement = ExpandMacroRecursively(getattr(node, c), ctx)
            setattr(clone, c, replacement)
        elif nfd.kind is cwast.NFK.LIST:
            out = []
            for cc in getattr(node, c):
                exp = ExpandMacroRecursively(cc, ctx)
                # TODO: this tricky and needs a comment
                if isinstance(exp, cwast.MacroListArg) and not isinstance(cc, cwast.MacroListArg):
                    out += exp.args
                else:
                    out.append(exp)
            setattr(clone, c, out)
    return clone


def ExpandMacro(invoke: cwast.MacroInvoke, macro: cwast.DefMacro, ctx: MacroContext) -> Any:
    params = macro.params_macro
    args = invoke.args
    assert len(params) == len(
        invoke.args), f"parameter mismatch in: {invoke}: actual {invoke.args} expected: {len(params)}"
    logger.info("Expanding Macro Invocation: %s", invoke)
    logger.info("Macro: %s", macro)
    # pp.PrettyPrint(invoke)
    # pp.PrettyPrint(macro)
    ctx.Reset()
    for p, a in zip(params, invoke.args):
        assert p.name.startswith("$")
        if p.macro_param_kind == cwast.MACRO_PARAM_KIND.EXPR:
            pass
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.STMT_LIST:
            assert isinstance(a, cwast.MacroListArg)
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.TYPE:
            pass
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.FIELD:
            assert isinstance(a, cwast.Id)
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.ID:
            assert isinstance(a, cwast.Id)
        else:
            assert False
        ctx.RegisterSymbol(p.name, (p.macro_param_kind, a))
    for gen_id in macro.gen_ids:
        assert gen_id.startswith("$")
        new_name = ctx.GenUniqueName(gen_id)
        ctx.RegisterSymbol(
            gen_id, (cwast.MACRO_PARAM_KIND.ID, cwast.Id(new_name, "")))
    out = []
    for node in macro.body_macro:
        logger.info("Expand macro body node: %s", node)
        # pp.PrettyPrint(node)
        exp = ExpandMacroRecursively(node, ctx)
        # pp.PrettyPrint(exp)
        if isinstance(exp, cwast.MacroListArg):
            out += exp.args
        else:
            out.append(exp)
    if len(out) == 1:
        return out[0]
    return cwast.MacroListArg(out)
