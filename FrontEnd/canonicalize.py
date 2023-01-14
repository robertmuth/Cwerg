#!/usr/bin/python3

"""Canonicalizer

"""

import dataclasses
import logging
import pp
from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import types

############################################################
# Move string/array values into global (un-mutable variables)
############################################################


def CanonicalizeStringVal(node, str_map: Dict[str, Any], id_gen: identifier.IdGen):
    def replacer(node):
        # TODO: add support for ValArray
        if isinstance(node, cwast.ValString):
            assert isinstance(
                node.x_value, bytes), f"expected str got {node.x_value}"
            def_node = str_map.get(node.x_value)
            if not def_node:
                def_node = cwast.DefGlobal(True, False, id_gen.NewName("global_str"),
                                           node.x_type, node,
                                           x_srcloc=node.x_srcloc,
                                           x_type=node.x_type,
                                           x_value=node.x_value)
                str_map[node.x_value] = def_node

            return cwast.Id(def_node.name, "blahblah",
                            x_srcloc=node.x_srcloc,
                            x_type=node.x_type,
                            x_value=node.x_value,
                            x_symbol=def_node)
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


############################################################
# Convert large parameter into pointer to object allocated
# in the caller
############################################################
def _TransformLargeArgs(node, changed_params: Set[Any]):
    if isinstance(node, cwast.Id) and isinstance(node.x_symbol, cwast.FunParam) in changed_params:
        deref = cwast.ExprDeref(node, x_srcloc=node.x_srcloc,
                                x_type=node.x_type, x_value=node.x_value)
        node.x_type = node.x_symbol.x_type
        node.x_value = None
        return deref
    return None


def CanonicalizeLargeArgs(node, changed_params: Set[Any], type_corpus: types.TypeCorpus, id_gen):
    if isinstance(node, cwast.DefFun):
        for p in node.params:
            if isinstance(p, cwast.FunParam):
                if type_corpus.register_types[p.x_type] is None:
                    changed_params.add(p)

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, c)
            new_child = _TransformLargeArgs(child, changed_params)
            if new_child:
                setattr(node, c, new_child)
            else:
                CanonicalizeLargeArgs(child, changed_params, id_gen)
        elif nfd.kind is cwast.NFK.LIST:
            children = getattr(node, c)
            for n, child in enumerate(children):
                new_child = _TransformLargeArgs(child, changed_params)
                if new_child:
                    children[n] = new_child
                else:
                    CanonicalizeLargeArgs(child, changed_params, id_gen)


def CanonicalizeLargeArgs(node, changed_params: Set[Any], type_corpus: types.TypeCorpus, id_gen):
    if isinstance(node, cwast.DefFun):
        for p in node.params:
            if isinstance(p, cwast.FunParam):
                if type_corpus.register_types[p.x_type] is None:
                    changed_params.add(p)

    for c in node.__class__.FIELDS:
        nfd = cwast.ALL_FIELDS_MAP[c]
        if nfd.kind is cwast.NFK.NODE:
            child = getattr(node, c)
            new_child = _TransformLargeArgs(child, changed_params)
            if new_child:
                setattr(node, c, new_child)
            else:
                CanonicalizeLargeArgs(child, changed_params, id_gen)
        elif nfd.kind is cwast.NFK.LIST:
            children = getattr(node, c)
            for n, child in enumerate(children):
                new_child = _TransformLargeArgs(child, changed_params)
                if new_child:
                    children[n] = new_child
                else:
                    CanonicalizeLargeArgs(child, changed_params, id_gen)


def FindLargeArgs(node, large_args: Dict[Any, Any], type_corpus: types.TypeCorpus, id_gen):
    pass

############################################################
# Convert ternary operator into  expr with if statements
#
# Note we could implement the ternary op as a macro but would lose some
# of type inference, so instead we use this hardcoded rewrite
############################################################


def CanonicalizeTernaryOp(node, id_gen: identifier.IdGen):
    def replacer(node):
        if isinstance(node, cwast.Expr3):
            name_t = id_gen.NewName("op_t")
            def_t = cwast.DefVar(False, name_t, cwast.TypeAuto(), node.expr_t,
                                 x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.expr_t.x_value)
            id_t = cwast.Id(name_t, "", x_srcloc=node.x_srcloc, x_type=node.expr_t.x_type,
                            x_value=node.expr_t.x_value, x_symbol=def_t)
            name_f = id_gen.NewName("op_f")
            def_f = cwast.DefVar(False, name_f, cwast.TypeAuto(), node.expr_f,
                                 x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.expr_f.x_value)
            id_f = cwast.Id(name_f, "", x_srcloc=node.x_srcloc, x_type=node.expr_f.x_type,
                            x_value=node.expr_f.x_value, x_symbol=def_f)

            expr = cwast.ExprStmt([], x_srcloc=node.x_srcloc,
                                  x_type=node.x_type, x_value=node.x_value)
            expr.body = [
                def_t,
                def_f,
                cwast.StmtIf(node.cond, [
                    cwast.StmtReturn(
                        id_t, x_srcloc=node.x_srcloc, x_target=expr)
                ], [
                    cwast.StmtReturn(
                        id_f, x_srcloc=node.x_srcloc, x_target=expr)
                ],  x_srcloc=node.x_srcloc)

            ]
            return expr
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)
