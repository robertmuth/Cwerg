#!/bin/env python3
"""Pretty printer for AST using unicode box chars:

https://www.w3.org/TR/xml-entity-names/025.html
"""

import logging

from typing import Any

from FE import cwast
from FE import symbolize
from FE import type_corpus
from FE import typify
from FE import canonicalize
from FE import eval

logger = logging.getLogger(__name__)

_INDENTATION = 4


def _EmitLine(line: list[str], indent: int, fout, active_columns: list[int], is_last: bool):
    if indent >= 0:
        spaces = [" "] * (indent * _INDENTATION + 1)
        for a in active_columns:
            spaces[a * _INDENTATION] = "┃"
        spaces[indent * _INDENTATION] = "┗" if is_last else "┣"

        print("".join(spaces), file=fout, end="")
    print(" ".join(line), file=fout)


def _DumpList(name: str, lst, indent,  labels: dict[Any, str], fout, active_columns, is_last):
    if lst:

        _EmitLine([name], indent + 1,
                  fout, active_columns,  is_last)
        active_columns.append(indent + 2)
        for n in lst:
            if n == lst[-1]:
                active_columns.pop(-1)

            _DumpNode(n, indent + 2, labels, fout,
                      active_columns, n == lst[-1])

    else:
        _EmitLine([name, "[Empty]"],
                  indent + 1, fout, active_columns, is_last)


def _GetFlags(node) -> str:
    cls = type(node)
    flags = []
    has_flags = False
    for nfd in cls.ATTRS:
        if nfd.name == 'doc':
            continue
        assert nfd.kind == cwast.NFK.ATTR_BOOL, f"{nfd.name}"
        has_flags = True
        val = getattr(node, nfd.name)
        if val:
            flags.append(nfd.name)
    if has_flags:
        return f"[{','.join(sorted(flags))}]"
    return ""


def _DumpNode(node: Any, indent: int,  labels: dict[Any, str],  fout, active_columns, is_last):
    cls = type(node)
    line = [cls.__name__]
    flags = _GetFlags(node)
    if flags:
        line.append(flags)
    for nfd in cls.KIND_FIELDS:
        # these are all enum
        val = getattr(node, nfd.name).name
        line.append(val)
    for nfd in cls.STR_FIELDS:
        val = getattr(node, nfd.name)
        if val is not None:
            if nfd.kind == cwast.NFK.NAME:
                val = val.name
                assert val is not None
            if nfd.name == "name":
                line.append(val)
            else:
                line.append(f"{nfd.name}={val}")
    label = labels.get(node)
    if label is not None:
        line.append(f"label={label}")

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
            line.append(f"{name}={labels[def_sym]}")
            continue
        if name == "x_import" or name == "x_symtab":
            continue
        line.append(f"{name}={val}")

    _EmitLine(line, indent, fout, active_columns, is_last)

    if cls.NODE_FIELDS:
        active_columns.append(indent + 1)

        last = cls.NODE_FIELDS[-1]

        for nfd in cls.NODE_FIELDS:
            if nfd == last:
                active_columns.pop(-1)
            if nfd.kind == cwast.NFK.NODE:
                _DumpNode(getattr(node, nfd.name),
                          indent + 1, labels, fout, active_columns, nfd == last)
            else:
                assert nfd.kind == cwast.NFK.LIST
                _DumpList(nfd.name, getattr(node, nfd.name),
                          indent, labels, fout, active_columns, nfd == last)


_LABEL_KIND = {
    cwast.DefMod: "m",
    cwast.DefFun: "f",
    cwast.DefRec: "r",
    cwast.RecField: "F",
    cwast.DefEnum: "e",
    cwast.DefMacro: "x",
    cwast.DefType: "t",
    cwast.DefGlobal: "g",
    cwast.DefVar: "v",
    cwast.FunParam: "p",
}


def _LabeDefs(node: Any, prefix: list[int], out: dict[Any, str]):
    tag = _LABEL_KIND.get(type(node))
    if tag:
        out[node] = tag + ".".join((str(x) for x in prefix))
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
        _DumpNode(mod, -1, labels, fout, [], True)

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
