#!/bin/env python3
"""SEXPR Pretty printer (PP) for Cwerg AST to sexpr syntax
https://www.w3.org/TR/xml-entity-names/025.html
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


def emit_line(line, indent, fout, active_columns, is_last):
    spaces = [" "] * (indent + 1)
    for a in active_columns:
        spaces[a] = "┃"
    if indent > 0:
        spaces[indent] = "┗" if is_last else "┣"
    spaces.append(line)
    print("".join(spaces), file=fout)


def _DumpList(nfd, lst, indent,  labels: dict[Any, str], fout, active_columns, is_last):
    assert nfd.kind == cwast.NFK.LIST
    if lst:

        emit_line(f"[{nfd.name}]", indent + 2,
                  fout, active_columns,  is_last)
        active_columns.append(indent + 4)
        for n in lst:
            if n == lst[-1]:
                active_columns.pop(-1)

            _DumpNode(n, indent + 4, labels, fout,
                      active_columns, n == lst[-1])

    else:
        emit_line(f"[{nfd.name}] Empty",
                  indent + 2, fout, active_columns, is_last)


def _DumpNode(node: Any, indent: int,  labels: dict[Any, str],  fout, active_columns, is_last):
    cls = type(node)
    names = [cwast.NODE_NAME(node)]
    for nfd in cls.KIND_FIELDS:
        val = getattr(node, nfd.name)
        val = str(val).split(".")[1]
        names.append(val)
    for nfd in cls.STR_FIELDS:
        val = getattr(node, nfd.name)
        if val is not None:
            if nfd.kind == cwast.NFK.NAME:
                val = val.name
                assert val is not None
            if nfd.name == "name":
                names.append(val)
            else:
                names.append(f"{nfd.name}={val}")
    label = labels.get(node)
    if label is not None:
        names.append(f"label={label}")
    for nfd in cls.ATTRS:
        if nfd.name == 'doc':
            continue
        val = getattr(node, nfd.name)
        if nfd.kind == cwast.NFK.ATTR_BOOL and not val:
            continue
        names.append(f"{nfd.name}={val}")
    for name in cls.X_FIELD_NAMES:
        val = getattr(node, name)
        if val is None:
            continue
        if name == "x_srcloc":
            continue
        if name == "x_type":
            if isinstance(node, cwast.TypeAuto):
                val = val.name
            else:
                continue
        if name == "x_eval":
            continue
        if name == "x_symbol" or name == "x_target" or name == "x_poly_mod":
            def_sym = getattr(node, name)
            assert def_sym in labels, f"{node} -> {def_sym}"
            names.append(f"{name}={labels[def_sym]}")
            continue
        if name == "x_import" or name == "x_symtab":
            continue
        names.append(f"{name}={val}")

    emit_line(" ".join(names), indent, fout, active_columns, is_last)

    if cls.NODE_FIELDS:
        active_columns.append(indent + 2)

        last = cls.NODE_FIELDS[-1]

        for nfd in cls.NODE_FIELDS:
            if nfd == last:
                active_columns.pop(-1)
            if nfd.kind == cwast.NFK.NODE:
                _DumpNode(getattr(node, nfd.name),
                          indent + 2, labels, fout, active_columns, nfd == last)
            else:
                _DumpList(nfd, getattr(node, nfd.name),
                          indent, labels, fout, active_columns, nfd == last)


LABEL_KIND = {
    cwast.DefMod: "x",
    cwast.DefFun: "f",
    cwast.DefRec: "r",
    cwast.RecField: "t",
    cwast.DefEnum: "e",
    cwast.DefMacro: "m",
    cwast.DefType: "t",
    cwast.DefGlobal: "g",
    cwast.DefVar: "v",
    cwast.FunParam: "p",
    #
    cwast.StmtBlock: "b",
    cwast.ExprStmt: "s",
}


def _LabeDefs(node: Any, prefix: list[int], out: dict[Any, str]):
    if isinstance(node, (cwast.DefMod, cwast.DefFun, cwast.DefRec, cwast.DefEnum,
                         cwast.DefMacro, cwast.DefType, cwast.DefGlobal,
                         cwast.DefVar, cwast.FunParam, cwast.RecField)):
        out[node] = LABEL_KIND[type(node)] + ".".join((str(x) for x in prefix))
    for nfd in type(node).NODE_FIELDS:
        if nfd.kind == cwast.NFK.LIST:
            prefix.append(-1)
            for n, child in enumerate(getattr(node, nfd.name)):
                prefix[-1] = n
                _LabeDefs(child, prefix, out)
            prefix.pop(-1)


def _ExtractSymDefLabels(mods: list[cwast.DefMod], out: dict[Any, str]):
    for n, mod in enumerate(mods):
        _LabeDefs(mod, [n], out)


def _LabelTargets(node: Any, n: int, out: dict[Any, str]):
    block_counter = 0
    expr_counter = 0

    def visit(node):
        nonlocal n, out, block_counter, expr_counter
        if isinstance(node, cwast.StmtBlock):
            out[node] = f"b{n}.{block_counter}"
            block_counter += 1
        elif isinstance(node, cwast.ExprStmt):
            print(f"{id(node)} -> {node}")
            out[node] = f"s{n}.{expr_counter}"
            expr_counter += 1

    cwast.VisitAstRecursively(node, visit)


def _ExtractTargetLabels(mods: list[cwast.DefMod], out: dict[Any, str]):
    for n, mod in enumerate(mods):
        _LabelTargets(mod, n, out)


def DumpMods(mods: list[cwast.DefMod], fout):
    labels: dict[Any, str] = {}
    _ExtractSymDefLabels(mods, labels)

    _ExtractTargetLabels(mods, labels)

    for mod in mods:
        print("", file=fout)
        _DumpNode(mod, 0, labels, fout, [], True)

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

    DumpMods(mp.mods_in_topo_order, sys.stdout)


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    from FE import mod_pool
    from FE import macro

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.WARN)
    main(sys.argv[1:])
