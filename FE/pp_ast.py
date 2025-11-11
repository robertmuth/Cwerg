#!/bin/env python3
"""SEXPR Pretty printer (PP) for Cwerg AST to sexpr syntax

"""

import logging

from typing import Optional, Any

from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import typify
from FE import canonicalize
from FE import eval

logger = logging.getLogger(__name__)


def emit_line(line, indent, fout, is_last):
    print(" " * indent, "|-", line, file=fout)


def _DumpNode(node: Any, indent, fout, is_last):
    cls = type(node)
    names = [cwast.NODE_NAME(node)]
    for nfd in cls.STR_FIELDS:
        val =  getattr(node, nfd.name)
        if val:
            if nfd.kind == cwast.NFK.NAME:
                val = val.name
            names.append(f"{nfd.name}={val}")
        else:
            names.append("None")
    for nfd in cls.ATTRS:
        if nfd.name == 'doc':
            continue
        val = getattr(node, nfd.name)
        if nfd.kind == cwast.NFK.ATTR_BOOL and not val:
            continue
        names.append(f"{nfd.name}={val}")
    for name in cls.X_FIELD_NAMES:
        val = getattr(node, name)
        if name == "x_srcloc":
            continue
        if name == "x_type":
            continue
        if name == "x_eval":
            continue
        if name == "x_symbol":
            continue
        if name == "x_target":
            continue
        names.append(f"{nfd.name}={val}")

    emit_line(" ".join(names), indent, fout, is_last)

    if cls.NODE_FIELDS:
        last = cls.NODE_FIELDS[-1]

        for nfd in cls.NODE_FIELDS:
            if nfd.kind == cwast.NFK.NODE:
                _DumpNode(getattr(node, nfd.name),
                          indent + 2, fout, nfd == last)
            else:
                assert nfd.kind == cwast.NFK.LIST
                lst = getattr(node, nfd.name)
                if lst:
                    emit_line(f"[{nfd.name}]", indent + 2, fout, nfd == last)
                    for n in lst:
                        _DumpNode(n, indent + 4, fout, n == lst[-1])
                else:
                    emit_line(f"[{nfd.name}] Empty", indent + 2, fout, nfd == last)


def DumpMod(mod: cwast.DefMod, fout):
    print("", file=fout)
    _DumpNode(mod, 0, fout, False)


############################################################
#
############################################################


def main(argv: list[str]):
    cwast.ASSERT_AFTER_ERROR = False
    assert len(argv) == 1
    fn = argv[0]
    fn, ext = os.path.splitext(fn)
    assert ext in (".cw", ".cws")

    cwd = os.getcwd()
    main = str(pathlib.Path(fn).resolve())
    mp = mod_pool.ReadModulesRecursively(pathlib.Path(
        cwd) / "Lib", [main], add_builtin=fn != "Lib/builtin")
    for mod in mp.mods_in_topo_order:
        canonicalize.FunRemoveParentheses(mod)
    macro.ExpandMacrosAndMacroLike(mp.mods_in_topo_order)
    symbolize.SetTargetFields(mp.mods_in_topo_order)
    symbolize.ResolveSymbolsInsideFunctions(
        mp.mods_in_topo_order, mp.builtin_symtab)
    for mod in mp.mods_in_topo_order:
        symbolize.VerifySymbols(mod)

    tc = type_corpus.TypeCorpus(type_corpus.STD_TARGET_X64)
    typify.AddTypesToAst(mp.mods_in_topo_order, tc)
    for mod in mp.mods_in_topo_order:
        typify.VerifyTypesRecursively(mod, tc, typify.VERIFIERS_WEAK)

    eval.DecorateASTWithPartialEvaluation(mp.mods_in_topo_order)
    for mod in mp.mods_in_topo_order:
        eval.VerifyASTEvalsRecursively(mod)

    for mod in mp.mods_in_topo_order:
        DumpMod(mod, sys.stdout)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
