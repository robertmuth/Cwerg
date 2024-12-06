#!/bin/env python3

"""Macro Expander

"""

import dataclasses
import logging

from typing import Any, Tuple

from FE import cwast
from FE import identifier

logger = logging.getLogger(__name__)


class MacroContext:
    """TBD"""

    def __init__(self, id_gen: identifier.IdGen):
        self._id_gen = id_gen
        # these need to become lists
        self.macro_parameter: dict[str, Tuple[cwast.MacroParam, Any]] = {}
        self.srcloc = None

    def PushScope(self, srcloc):
        self.macro_parameter.clear()
        self.srcloc = srcloc

    def PopScope(self):
        # TBD
        pass

    def GenUniqueName(self, name: str):
        # TODO: add
        assert name.startswith(
            cwast.MACRO_VAR_PREFIX), f"expected macro id {name}"
        return self._id_gen.NewName(name[1:])

    def RegisterSymbol(self, name, value, check_clash=False):
        if check_clash:
            assert name not in self.macro_parameter
        self.macro_parameter[name] = value

    def GetSymbol(self, name) -> Tuple[cwast.MacroParam, Any]:
        return self.macro_parameter[name]


def ExpandMacroRecursively(node, ctx: MacroContext) -> Any:
    if isinstance(node, cwast.MacroVar):
        assert node.name.startswith(cwast.MACRO_VAR_PREFIX)
        kind, new_name = ctx.GetSymbol(node.name)
        assert kind is cwast.MACRO_PARAM_KIND.ID
        # Why is this not a MacroVar
        assert isinstance(new_name, cwast.Id)
        assert not new_name.IsMacroVar()
        type_or_auto = ExpandMacroRecursively(node.type_or_auto, ctx)
        initial = ExpandMacroRecursively(node.initial_or_undef_or_auto, ctx)
        return cwast.DefVar(new_name.GetBaseNameStrict(), type_or_auto, initial,
                            x_srcloc=ctx.srcloc, mut=node.mut, ref=node.ref)
    elif isinstance(node, cwast.MacroId):
        assert node.name.startswith(
            cwast.MACRO_VAR_PREFIX), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name)
        # We dont support `FIELD``
        assert kind in (cwast.MACRO_PARAM_KIND.EXPR,
                        cwast.MACRO_PARAM_KIND.ID,
                        cwast.MACRO_PARAM_KIND.FIELD,
                        cwast.MACRO_PARAM_KIND.TYPE,
                        cwast.MACRO_PARAM_KIND.EXPR_LIST,
                        cwast.MACRO_PARAM_KIND.EXPR_LIST_REST,
                        cwast.MACRO_PARAM_KIND.STMT_LIST), f"{node.name} -> {kind} {arg}"
        return cwast.CloneNodeRecursively(arg, {}, {})
    elif isinstance(node, cwast.MacroFor):
        assert node.name.startswith(
            cwast.MACRO_VAR_PREFIX), f" non macro name: {node}"
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
        return cwast.EphemeralList(out, colon=False)

    clone = dataclasses.replace(node)

    for c, nfd in node.__class__.FIELDS:
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
    params: list[cwast.MacroParam] = macro.params_macro
    args = invoke.args
    if params and params[-1].macro_param_kind is cwast.MACRO_PARAM_KIND.EXPR_LIST_REST:
        rest = cwast.EphemeralList(args[len(params)-1:], colon=False)
        args = args[:len(params)-1:] + [rest]
    if len(params) != len(args):
        cwast.CompilerError(invoke.x_srcloc, f"parameter mismatch in: {invoke}: "
                            f"actual {len(args)} expected: {len(params)}")
    logger.info("Expanding Macro Invocation: %s", invoke)
    # pp_sexpr.PrettyPrint(invoke)
    # pp_sexpr.PrettyPrint(macro)
    ctx.PushScope(invoke.x_srcloc)
    for p, a in zip(params, args):
        assert p.name.startswith(cwast.MACRO_VAR_PREFIX)
        kind = p.macro_param_kind
        if kind is cwast.MACRO_PARAM_KIND.EXPR:
            pass
        elif kind in (cwast.MACRO_PARAM_KIND.STMT_LIST, cwast.MACRO_PARAM_KIND.EXPR_LIST,
                      cwast.MACRO_PARAM_KIND.EXPR_LIST_REST):
            if not isinstance(a, cwast.EphemeralList):
                cwast.CompilerError(invoke.x_srcloc,
                                    f"expected EphemeralList for macro param {p} got {a}")
        elif kind is cwast.MACRO_PARAM_KIND.TYPE:
            pass
        elif kind is cwast.MACRO_PARAM_KIND.FIELD:
            assert isinstance(a, cwast.Id)
        elif kind is cwast.MACRO_PARAM_KIND.ID:
            assert isinstance(
                a, cwast.Id), f"while expanding macro {macro.name} expected parameter id but got: {a}"
        else:
            assert False
        ctx.RegisterSymbol(p.name, (p.macro_param_kind, a))
    for gen_id in macro.gen_ids:
        assert gen_id.startswith(cwast.MACRO_VAR_PREFIX)
        new_name = ctx.GenUniqueName(gen_id)
        ctx.RegisterSymbol(
            gen_id, (cwast.MACRO_PARAM_KIND.ID, cwast.Id.Make(new_name, x_srcloc=macro.x_srcloc)))
    out = []
    for node in macro.body_macro:
        logger.debug("Expand macro body node: %s", node)
        # pp_sexpr.PrettyPrint(node)
        exp = ExpandMacroRecursively(node, ctx)
        # pp_sexpr.PrettyPrint(exp)
        if isinstance(exp, cwast.EphemeralList):
            out += exp.args
        else:
            out.append(exp)
    ctx.PopScope()
    if len(out) == 1:
        return out[0]
    return cwast.EphemeralList(out, colon=False)
