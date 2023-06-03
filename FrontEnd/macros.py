#!/usr/bin/python3

"""Macro Expander

"""

import dataclasses
import logging

from typing import List, Dict, Set, Optional, Union, Any, Tuple

from FrontEnd import cwast


logger = logging.getLogger(__name__)


class MacroContext:

    def __init__(self, no):
        self._no = no
        # these need to become lists
        self.macro_parameter: Dict[str, Tuple[cwast.MacroParam, Any]] = {}
        self.srcloc = None

    def PushScope(self, srcloc):
        self.macro_parameter.clear()
        self.srcloc = srcloc

    def PopScope(self):
        # TBD
        pass

    def GenUniqueName(self, name: str):
        assert name.startswith("$"), f"expected macro id {name}"
        self._no += 1
        return f"{name[1:]}${self._no}"

    def RegisterSymbol(self, name, value, check_clash=False):
        if check_clash:
            assert name not in self.macro_parameter
        self.macro_parameter[name] = value

    def GetSymbol(self, name) -> Tuple[cwast.MacroParam, Any]:
        return self.macro_parameter[name]


def ExpandMacroRecursively(node, ctx: MacroContext) -> Any:
    if isinstance(node, cwast.MacroVar):
        assert node.name.startswith("$")
        kind, new_name = ctx.GetSymbol(node.name)
        assert kind is cwast.MACRO_PARAM_KIND.ID
        assert isinstance(new_name, cwast.Id)
        assert not new_name.name.startswith("$")
        type_or_auto = ExpandMacroRecursively(node.type_or_auto, ctx)
        initial_or_undef = ExpandMacroRecursively(node.initial_or_undef, ctx)
        return cwast.DefVar(node.mut, node.ref, new_name.name, type_or_auto, initial_or_undef, x_srcloc=ctx.srcloc)
    elif isinstance(node, cwast.MacroId):
        assert node.name.startswith("$"), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name)
        assert kind in (cwast.MACRO_PARAM_KIND.EXPR,
                        cwast.MACRO_PARAM_KIND.ID,
                        cwast.MACRO_PARAM_KIND.TYPE,
                        cwast.MACRO_PARAM_KIND.STMT_LIST), f"{node.name} -> {kind} {arg}"
        return cwast.CloneNodeRecursively(arg, {}, {})
    elif isinstance(node, cwast.MacroFor):
        assert node.name.startswith("$"), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name_list)
        assert isinstance(arg, cwast.EphemeralList)
        out = []
        for item in arg.args:
            ctx.RegisterSymbol(node.name, (cwast.MACRO_PARAM_KIND.EXPR, item))
            for b in node.body_for:
                exp = ExpandMacroRecursively(b, ctx)
                if isinstance(exp, cwast.EphemeralList):
                    out += exp.args
                else:
                    out.append(exp)
        return cwast.EphemeralList(out)

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
                if isinstance(exp, cwast.EphemeralList) and not isinstance(cc, cwast.EphemeralList):
                    out += exp.args
                else:
                    out.append(exp)
            setattr(clone, c, out)
    return clone


def ExpandMacro(invoke: cwast.MacroInvoke, macro: cwast.DefMacro, ctx: MacroContext) -> Any:
    params = macro.params_macro
    args = invoke.args
    if len(params) != len(invoke.args):
        cwast.CompilerError(invoke.x_srcloc, f"parameter mismatch in: {invoke}: "
                            f"actual {len(invoke.args)} expected: {len(params)}")
    logger.info("Expanding Macro Invocation: %s", invoke)
    logger.info("Macro: %s", macro)
    # pp.PrettyPrint(invoke)
    # pp.PrettyPrint(macro)
    ctx.PushScope(invoke.x_srcloc)
    for p, a in zip(params, invoke.args):
        assert p.name.startswith("$")
        if p.macro_param_kind == cwast.MACRO_PARAM_KIND.EXPR:
            pass
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.STMT_LIST:
            if not isinstance(a, cwast.EphemeralList):
                cwast.CompilerError(invoke.x_srcloc,
                                    f"expected EphemeralList for macro param {p} got {a}")
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.TYPE:
            pass
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.FIELD:
            assert isinstance(a, cwast.Id)
        elif p.macro_param_kind == cwast.MACRO_PARAM_KIND.ID:
            assert isinstance(
                a, cwast.Id), f"while expanding macro {macro.name} expected parameter id but got: {a}"
        else:
            assert False
        ctx.RegisterSymbol(p.name, (p.macro_param_kind, a))
    for gen_id in macro.gen_ids:
        assert gen_id.startswith("$")
        new_name = ctx.GenUniqueName(gen_id)
        ctx.RegisterSymbol(
            gen_id, (cwast.MACRO_PARAM_KIND.ID, cwast.Id(new_name, x_srcloc=macro.x_srcloc)))
    out = []
    for node in macro.body_macro:
        logger.info("Expand macro body node: %s", node)
        # pp.PrettyPrint(node)
        exp = ExpandMacroRecursively(node, ctx)
        # pp.PrettyPrint(exp)
        if isinstance(exp, cwast.EphemeralList):
            out += exp.args
        else:
            out.append(exp)
    ctx.PopScope()
    if len(out) == 1:
        return out[0]
    return cwast.EphemeralList(out)
