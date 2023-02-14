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
from FrontEnd import typify

############################################################
#
############################################################


def _IdNodeFromDef(def_node: cwast.DefVar, x_srcloc):
    return cwast.Id(def_node.name, "", x_srcloc=x_srcloc, x_type=def_node.x_type,
                    x_value=def_node.x_value, x_symbol=def_node)


def CanonicalizeStringVal(node, str_map: Dict[str, Any], id_gen: identifier.IdGen):
    """Move string/array values into global (un-mutable variables)"""
    def replacer(node, field):
        # TODO: add support for ValArray
        if isinstance(node, cwast.ValString):
            assert isinstance(
                node.x_value, bytes), f"expected str got {node.x_value}"
            def_node = str_map.get(node.x_value)
            if not def_node:
                def_node = cwast.DefGlobal(True, False, id_gen.NewName("global_str"),
                                           cwast.TypeAuto(node.x_srcloc), node,
                                           x_srcloc=node.x_srcloc,
                                           x_type=node.x_type,
                                           x_value=node.x_value)
                str_map[node.x_value] = def_node

            return _IdNodeFromDef(def_node, node.x_srcloc)
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


def CanonicalizeBoolExpressionsNotUsedForConditionals(node, tc: types.TypeCorpus):
    """transform a bool expression e into "e ? true : false"

    This will make it eligible for CanonicalizeTernaryOp
     """
    def replacer(node, field):
        if (field in ("args", "expr_rhs", "inits_array", "inits_rec", "initial_or_undef") and
            not isinstance(node, (cwast.ValTrue, cwast.ValFalse, cwast.ValUndef)) and
                types.is_bool(node.x_type)):
            cstr_bool = tc.insert_base_type(cwast.BASE_TYPE_KIND.BOOL)
            return cwast.Expr3(node,
                               cwast.ValTrue(x_srcloc=node.x_srcloc,
                                             x_type=cstr_bool, x_value=True),
                               cwast.ValFalse(
                                   x_srcloc=node.x_srcloc, x_type=cstr_bool, x_value=False),
                               x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def CanonicalizeTernaryOp(node, id_gen: identifier.IdGen):
    """Convert ternary operator nodes into  expr with if statements

    Note we could implement the ternary op as a macro but would lose some
    of type inference, so instead we use this hardcoded rewrite"""
    def replacer(node, field):
        if isinstance(node, cwast.Expr3):
            srcloc = node.x_srcloc
            name_t = id_gen.NewName("op_t")
            def_t = cwast.DefVar(False, name_t, cwast.TypeAuto(x_srcloc=srcloc), node.expr_t,
                                 x_srcloc=srcloc, x_type=node.x_type, x_value=node.expr_t.x_value)
            name_f = id_gen.NewName("op_f")
            def_f = cwast.DefVar(False, name_f, cwast.TypeAuto(x_srcloc=srcloc), node.expr_f,
                                 x_srcloc=srcloc, x_type=node.x_type, x_value=node.expr_f.x_value)

            expr = cwast.ExprStmt([], x_srcloc=srcloc,
                                  x_type=node.x_type, x_value=node.x_value)
            expr.body = [
                def_t,
                def_f,
                cwast.StmtIf(node.cond, [
                    cwast.StmtReturn(_IdNodeFromDef(
                        def_t, srcloc), x_srcloc=srcloc, x_target=expr)
                ], [
                    cwast.StmtReturn(_IdNodeFromDef(
                        def_f, srcloc), x_srcloc=srcloc, x_target=expr)
                ],  x_srcloc=srcloc)

            ]
            return expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)




############################################################
#
############################################################


def _AssigmemtNode(assignment_kind, lhs, expr, x_srcloc):
    rhs = cwast.Expr2(cwast.COMPOUND_KIND_TO_EXPR_KIND[assignment_kind],
                      cwast.CloneNodeRecursively(lhs),
                      expr, x_srcloc=x_srcloc, x_type=lhs.x_type)
    return cwast.StmtAssignment(lhs, rhs, x_srcloc=x_srcloc)


def CanonicalizeCompoundAssignments(node, tc: types.TypeCorpus, id_gen: identifier.IdGen):
    """Convert StmtCompoundAssignment to StmtAssignment"""
    def replacer(node, field):
        if isinstance(node, cwast.StmtCompoundAssignment):
            if isinstance(node.lhs, cwast.Id):
                return _AssigmemtNode(node.assignment_kind, node.lhs, node.expr_rhs, node.x_srcloc)
            else:
                addr_type = tc.insert_ptr_type(True, node.lhs.x_type)
                addr = cwast.ExprAddrOf(True, node.lhs,
                                        x_srcloc=node.x_srcloc, x_type=addr_type)
                def_node = cwast.DefVar(False, id_gen.NewName("assign"),
                                        cwast.TypeAuto(
                    x_srcloc=node.x_srcloc), addr,
                    x_srcloc=node.x_srcloc, x_type=addr_type)
                lhs = cwast.ExprDeref(_IdNodeFromDef(
                    def_node, node.x_srcloc), x_srcloc=node.x_srcloc, x_type=node.lhs.x_type)
                return cwast.EphemeralList([def_node,
                                            _AssigmemtNode(node.assignment_kind, lhs, node.expr, node.x_srcloc)])
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def ReplaceConstExpr(node):
    """
     This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect
    """
    def replacer(node, field):
        if isinstance(node, cwast.EnumVal) and isinstance(node.value_or_auto, cwast.ValAuto):
            assert  node.x_value is not None            
        if (field not in ("lhs", "inits_array", "inits_rec") and
            cwast.NF.VALUE_ANNOTATED in node.FLAGS and
            not isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.ValUndef)) and
                node.x_value is not None):
            if (isinstance(node.x_type, cwast.TypeBase) and
                types.is_int(node.x_type) and
                    not isinstance(node, cwast.ValNum)):
                return cwast.ValNum(str(node.x_value),
                                    x_srcloc=node.x_srcloc, x_type=node.x_type, x_value=node.x_value)
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


def CanonicalizeRemoveStmtCond(node):
    """Convert StmtCond to nested StmtIf"""
    def replacer(node, _):
        if not isinstance(node, cwast.StmtCond):
            return None
        if not node.cases:
            return cwast.EphemeralList([])

        out = None
        for case in reversed(node.cases):
            assert isinstance(case, cwast.Case)
            out = cwast.StmtIf(case.cond, case.body, [] if out is None else [
                               out], x_srcloc=case.x_srcloc)
        return out

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def OptimizeKnownConditionals(node):
    def replacer(node, _):
        if isinstance(node, cwast.StmtIf):
            if isinstance(node.cond, cwast.ValTrue):
                node.body_f.clear()
            elif isinstance(node.cond, cwast.ValFalse):
                node.body_t.clear()
        return None

    cwast.VisitAstRecursivelyPost(node, replacer)

############################################################
# Convert Slices to equvalent struct
#
# slice mut u8 -> struct {pointer ptr mut  u8, len uint}
############################################################


def _MakeSliceReplacementStruct(slice: cwast.TypeSlice, tc: types.TypeCorpus) -> cwast.DefRec:
    srcloc = slice.x_srcloc
    pointer_type = cwast.TypePtr(slice.mut, cwast.CloneNodeRecursively(
        slice.type), x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, pointer_type, tc.insert_ptr_type(
        pointer_type.mut, pointer_type.type.x_type))
    pointer_field = cwast.RecField("pointer",
                                   pointer_type, cwast.ValUndef(
                                       x_srcloc=srcloc),
                                   x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, pointer_field, pointer_type.x_type)
    length_type = cwast.TypeBase(tc.uint_kind, x_srcloc=srcloc)
    typify.AnnotateNodeType(
        tc, length_type, tc.insert_base_type(length_type.base_type_kind))
    length_field = cwast.RecField("length", length_type, cwast.ValUndef(x_srcloc=srcloc),
                                  x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, length_field, length_type.x_type)
    name = f"$rec_{tc.canon_name(slice.x_type)}"
    rec = cwast.DefRec(True, name, [pointer_field, length_field],
                       x_srcloc=srcloc)
    cstr = tc.insert_rec_type(f"{name}", rec)
    typify.AnnotateNodeType(tc, rec, cstr)
    tc.finalize_rec_type(rec)
    return rec


def CreateSliceReplacementStructs(node, tc: types.TypeCorpus, slice_to_struct_map):
    def visitor(node, _):
        if isinstance(node, cwast.TypeSlice):
            if node.x_type not in slice_to_struct_map:
                slice_to_struct_map[node.x_type] = _MakeSliceReplacementStruct(
                    node, tc)

    cwast.VisitAstRecursively(node, visitor)
