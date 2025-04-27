#!/bin/env python3

"""Macro Expander

"""

import dataclasses
import logging

from typing import Any, Tuple, Union

from FE import cwast
from FE import identifier
from FE import symbolize

logger = logging.getLogger(__name__)


class _MacroContext:
    """TBD"""

    def __init__(self, id_gen: identifier.IdGen):
        self._id_gen = id_gen
        # these need to become lists
        self.macro_parameter: dict[cwast.NAME,
                                   Tuple[cwast.MacroParam, Any]] = {}
        self.srcloc = None

    def PushScope(self, srcloc):
        self.macro_parameter.clear()
        self.srcloc = srcloc

    def PopScope(self):
        # TBD
        pass

    def GenUniqueName(self, name: cwast.NAME) -> cwast.NAME:
        assert name.IsMacroVar(), f"expected macro id {name}"
        # print (f"@@@@@@@@@@@@@@@ {name}")
        return self._id_gen.NewName(name.name[1:])

    def RegisterSymbol(self, name: cwast.NAME, value, check_clash=False):
        if check_clash:
            assert name not in self.macro_parameter
        self.macro_parameter[name] = value

    def GetSymbol(self: Any, name: cwast.NAME) -> Tuple[cwast.MacroParam, Any]:
        assert name.IsMacroVar()
        return self.macro_parameter[name]


def _ExpandMacroBodyRecursively(node, ctx: _MacroContext) -> Any:
    if isinstance(node, cwast.DefVar) and node.name.IsMacroVar():
        kind, new_name = ctx.GetSymbol(node.name)
        assert kind is cwast.MACRO_PARAM_KIND.ID
        # Why is this not a MacroVar
        assert isinstance(new_name, cwast.Id)
        type_or_auto = _ExpandMacroBodyRecursively(node.type_or_auto, ctx)
        initial = _ExpandMacroBodyRecursively(
            node.initial_or_undef_or_auto, ctx)
        return cwast.DefVar(new_name.GetBaseNameStrict(), type_or_auto, initial,
                            x_srcloc=ctx.srcloc, mut=node.mut, ref=node.ref)
    elif isinstance(node, cwast.MacroId):
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
        assert node.name.IsMacroVar(), f" non macro name: {node}"
        kind, arg = ctx.GetSymbol(node.name_list)
        assert isinstance(arg, cwast.EphemeralList)
        out = []
        for item in arg.args:
            ctx.RegisterSymbol(node.name, (cwast.MACRO_PARAM_KIND.EXPR, item))
            for b in node.body_for:
                exp = _ExpandMacroBodyRecursively(b, ctx)
                if isinstance(exp, cwast.EphemeralList):
                    out += exp.args
                else:
                    out.append(exp)
        return cwast.EphemeralList(out, colon=False)

    clone = dataclasses.replace(node)

    for nfd in node.__class__.NODE_FIELDS:
        c = nfd.name
        if nfd.kind is cwast.NFK.NODE:
            replacement = _ExpandMacroBodyRecursively(getattr(node, c), ctx)
            setattr(clone, c, replacement)
        else:
            out = []
            for cc in getattr(node, c):
                exp = _ExpandMacroBodyRecursively(cc, ctx)
                # TODO: this tricky and needs a comment
                if isinstance(exp, cwast.EphemeralList) and not isinstance(cc, cwast.EphemeralList):
                    out += exp.args
                else:
                    out.append(exp)
            setattr(clone, c, out)
    return clone


def _ExpandMacroInvokation(macro_invoke: cwast.MacroInvoke, def_macro: cwast.DefMacro, ctx: _MacroContext) -> Any:
    params: list[cwast.MacroParam] = def_macro.params_macro
    args = macro_invoke.args
    if params and params[-1].macro_param_kind is cwast.MACRO_PARAM_KIND.EXPR_LIST_REST:
        rest = cwast.EphemeralList(args[len(params)-1:], colon=False)
        args = args[:len(params)-1:] + [rest]
    if len(params) != len(args):
        cwast.CompilerError(macro_invoke.x_srcloc, f"parameter mismatch in: {macro_invoke}: "
                            f"actual {len(args)} expected: {len(params)}")
    logger.info("Expanding Macro Invocation: %s", macro_invoke)
    # pp_sexpr.PrettyPrint(invoke)
    # pp_sexpr.PrettyPrint(macro)
    ctx.PushScope(macro_invoke.x_srcloc)
    for p, a in zip(params, args):
        assert p.name.IsMacroVar()
        kind = p.macro_param_kind
        if kind is cwast.MACRO_PARAM_KIND.EXPR:
            pass
        elif kind in (cwast.MACRO_PARAM_KIND.STMT_LIST, cwast.MACRO_PARAM_KIND.EXPR_LIST,
                      cwast.MACRO_PARAM_KIND.EXPR_LIST_REST):
            if not isinstance(a, cwast.EphemeralList):
                cwast.CompilerError(macro_invoke.x_srcloc,
                                    f"expected EphemeralList for macro param {p} got {a}")
        elif kind is cwast.MACRO_PARAM_KIND.TYPE:
            pass
        elif kind is cwast.MACRO_PARAM_KIND.FIELD:
            assert isinstance(a, cwast.Id)
        elif kind is cwast.MACRO_PARAM_KIND.ID:
            assert isinstance(
                a, cwast.Id), f"while expanding macro {def_macro.name} expected parameter id but got: {a}"
        else:
            assert False
        ctx.RegisterSymbol(p.name, (p.macro_param_kind, a))
    for gen_id in def_macro.gen_ids:
        assert isinstance(gen_id, cwast.MacroId)
        new_name = ctx.GenUniqueName(gen_id.name)
        ctx.RegisterSymbol(
            gen_id.name, (cwast.MACRO_PARAM_KIND.ID, cwast.Id(new_name, None, x_srcloc=def_macro.x_srcloc)))
    out = []
    for node in def_macro.body_macro:
        logger.debug("Expand macro body node: %s", node)
        # pp_sexpr.PrettyPrint(node)
        exp = _ExpandMacroBodyRecursively(node, ctx)
        # pp_sexpr.PrettyPrint(exp)
        if isinstance(exp, cwast.EphemeralList):
            out += exp.args
        else:
            out.append(exp)
    ctx.PopScope()
    if len(out) == 1:
        return out[0]
    return cwast.EphemeralList(out, colon=False)


MAX_MACRO_NESTING = 8


def _ExpandMacroInvokeIteratively(macro_invoke: cwast.MacroInvoke,
                                  nesting: int, builtin_syms: symbolize.SymTab, ctx: _MacroContext):
    """This will recursively expand the macro so returned node does not contain any expandables"""
    while isinstance(macro_invoke, cwast.MacroInvoke):
        assert nesting < MAX_MACRO_NESTING
        assert isinstance(macro_invoke, cwast.MacroInvoke)
        symtab: symbolize.SymTab = macro_invoke.x_import.x_module.x_symtab
        def_macro = symtab.resolve_macro(
            macro_invoke,  builtin_syms, symbolize.HasImportedSymbolReference(macro_invoke))
        if def_macro is None:
            cwast.CompilerError(
                macro_invoke.x_srcloc, f"invocation of unknown macro `{macro_invoke.name}`")
        macro_invoke = _ExpandMacroInvokation(macro_invoke, def_macro, ctx)
        nesting += 1

    assert cwast.NF.TO_BE_EXPANDED not in macro_invoke.FLAGS, macro_invoke
    # recurse and resolve any expandables
    _ExpandMacrosAndMacroLikeRecursively(macro_invoke, nesting + 1, builtin_syms, ctx)
    # pp_sexpr.PrettyPrint(exp)
    return macro_invoke


def _ExpandMacrosAndMacroLikeRecursively(fun,  nesting: int, builtin_symtab: symbolize.SymTab, ctx: _MacroContext):
    def replacer(node: Any):
        nonlocal builtin_symtab, nesting, ctx
        orig_node = node
        if isinstance(node, cwast.MacroInvoke):
            node = _ExpandMacroInvokeIteratively(
                node, nesting, builtin_symtab, ctx)
        if isinstance(node, cwast.ExprSrcLoc):
            return cwast.ValString(f'r"{node.expr.x_srcloc}"', x_srcloc=node.x_srcloc)
        elif isinstance(node, cwast.ExprStringify):
            # assert isinstance(node.expr, cwast.Id)
            return cwast.ValString(f'r"{node.expr}"', x_srcloc=node.x_srcloc)
        return None if orig_node is node else node

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def ExpandMacrosAndMacroLike(mods: list[cwast.DefMod], builtin_symtab: symbolize.SymTab, id_gen_cache: identifier.IdGenCache):
    """Expands MacroInvoke, ExprSrcLoc, ExprStringify"""
    for mod in mods:
        for node in mod.body_mod:
            if isinstance(node, cwast.DefFun):
                logger.info("Expanding macros in: %s", node.name)
                ctx = _MacroContext(id_gen_cache.Get(node))
                _ExpandMacrosAndMacroLikeRecursively(
                    node, 0, builtin_symtab, ctx)


############################################################
#
############################################################


def main(argv: list[str]):
    assert len(argv) == 1
    fn = argv[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")
    cwd = os.getcwd()
    main = str(pathlib.Path(fn).resolve())
    mp = mod_pool.ReadModulesRecursively(pathlib.Path(
        cwd) / "Lib", [main], add_builtin=fn != "Lib/builtin")
    mod_topo_order = mp.mods_in_topo_order
    for mod in mod_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    fun_id_gens = identifier.IdGenCache()
    ExpandMacrosAndMacroLike(mod_topo_order, mp.builtin_symtab, fun_id_gens)
    symbolize.SetTargetFields(mp.mods_in_topo_order)
    symbolize.ResolveSymbolsInsideFunctions(
        mod_topo_order, mp.builtin_symtab)
    for ast in mod_topo_order:
        # cwast.CheckAST(ast, set())
        symbolize.VerifySymbols(ast)
        pp_sexpr.PrettyPrint(ast, sys.stdout)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import canonicalize
    from FE import pp_sexpr

    logging.basicConfig(level=logging.WARNING)
    symbolize.logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    main(sys.argv[1:])
