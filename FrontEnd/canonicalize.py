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
def CanonicalizeLargeArgs(node, changed_params: Set[Any], tc: types.TypeCorpus):
    def replacer(node, field):
        nonlocal changed_params, tc

        if isinstance(node, cwast.DefFun):
            for p in node.params:
                if isinstance(p, cwast.FunParam):
                    if tc.register_types[p.x_type] is None:
                        changed_params.add(p)
            return None
        if isinstance(node, cwast.Id) and isinstance(node.x_symbol, cwast.FunParam) in changed_params:
            deref = cwast.ExprDeref(node, x_srcloc=node.x_srcloc,
                                    x_type=node.x_type, x_value=node.x_value)
            node.x_type = node.x_symbol.x_type
            node.x_value = None
            return deref
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)


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
            def_t = cwast.DefVar(False, False, name_t, cwast.TypeAuto(x_srcloc=srcloc), node.expr_t,
                                 x_srcloc=srcloc, x_type=node.x_type, x_value=node.expr_t.x_value)
            name_f = id_gen.NewName("op_f")
            def_f = cwast.DefVar(False, False, name_f, cwast.TypeAuto(x_srcloc=srcloc), node.expr_f,
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
            assert node.x_value is not None
        if (field not in ("lhs", "inits_array", "inits_rec") and
            cwast.NF.VALUE_ANNOTATED in node.FLAGS and
            not isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.ValUndef, cwast.RecField)) and
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
    name = f"rec_{tc.canon_name(slice.x_type)}"
    rec = cwast.DefRec(True, name, [pointer_field, length_field],
                       x_srcloc=srcloc)
    cstr = tc.insert_rec_type(f"{name}", rec)
    typify.AnnotateNodeType(tc, rec, cstr)
    tc.finalize_rec_type(rec)
    return rec


def CreateSliceReplacementStructs(node, tc: types.TypeCorpus, slice_to_struct_map):
    """Populates slice_to_struct_map with {x_type, DefRec}"""
    def visitor(node, _):
        if isinstance(node, cwast.TypeSlice):
            if node.x_type not in slice_to_struct_map:
                slice_to_struct_map[node.x_type] = _MakeSliceReplacementStruct(
                    node, tc)

    cwast.VisitAstRecursivelyPost(node, visitor)


def _MakeIdForDefRec(def_rec, srcloc):
    return cwast.Id(def_rec.name, "", x_symbol=def_rec, x_type=def_rec.x_type, x_srcloc=srcloc)


def _ConvertValArrayToPointer(node, pointer_type, index_type):
    zero_offset = cwast.ValNum(
        f"0", x_srcloc=node.x_srcloc, x_type=index_type, x_value=0)
    return cwast.ExprAddrOf(pointer_type.mut,
                            cwast.ExprIndex(node, zero_offset,
                                            x_type=pointer_type.type, x_srcloc=node.x_srcloc), x_type=pointer_type,
                            x_srcloc=node.x_srcloc)


def _ConvertValArrayToSliceValRec(node, slice_rec: cwast.DefRec, srcloc):
    assert isinstance(node.x_type, cwast.TypeArray)
    pointer_field, length_field = slice_rec.fields
    width = node.x_type.size.x_value
    assert width is not None
    inits = [cwast.FieldVal(_ConvertValArrayToPointer(node, pointer_field.x_type, length_field.x_type), "",
                            x_field=pointer_field, x_type=pointer_field.x_type,
                            x_srcloc=srcloc),
             cwast.FieldVal(cwast.ValNum(f"{width}", x_value=width, x_srcloc=srcloc, x_type=length_field.x_type), "",
                            x_field=length_field, x_type=length_field.x_type,
                            x_srcloc=srcloc)]
    return cwast.ValRec(_MakeIdForDefRec(slice_rec, srcloc), inits, x_srcloc=srcloc, x_type=slice_rec.x_type)


def _ConvertMutSliceValRecToSliceValRec(node, slice_rec: cwast.DefRec):
    assert isinstance(node.x_type, cwast.TypeSlice)
    assert node.x_type.mut
    #assert node.x_type.type == slice_rec.fields[0].x_type
    return cwast.ExprBitCast(node, _MakeIdForDefRec(slice_rec, node.x_srcloc), x_srcloc=node.x_srcloc, x_type=slice_rec.x_type)


def ReplaceSlice(node, tc, slice_to_struct_map):
    """
     This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

     Complications:
     `slice<u8> = slice-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node, field):
        nonlocal tc

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            if isinstance(node, cwast.DefFun):
                fun_sig = node.x_type
                needs_rewrite = fun_sig.result.x_type in slice_to_struct_map
                for p in fun_sig.params:
                    if p.type in slice_to_struct_map:
                        needs_rewrite = True
                if needs_rewrite:
                    result = slice_to_struct_map.get(
                        fun_sig.result, fun_sig.result)
                    params = [slice_to_struct_map.get(
                        p.type, p.type) for p in fun_sig.params]
                    node.x_type = tc.insert_fun_type(params, result)
            def_rec: cwast.DefRec = slice_to_struct_map.get(node.x_type)
            if def_rec is not None:
                if isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
                    if node.x_type != node.initial_or_undef.x_type:
                        if isinstance(node.initial_or_undef.x_type, cwast.TypeSlice):
                            assert node.x_type.type == node.initial_or_undef.x_type.type
                            assert not node.x_type.mut and node.initial_or_undef.x_type.mut
                            node.initial_or_undef = _ConvertMutSliceValRecToSliceValRec(
                                node.initial_or_undef, def_rec)
                        elif isinstance(node.initial_or_undef.x_type, cwast.TypeArray):
                            node.initial_or_undef = _ConvertValArrayToSliceValRec(
                                node.initial_or_undef, def_rec, node.x_srcloc)
                        else:
                            assert False

                    node.x_type = def_rec.x_type

                elif isinstance(node, (cwast.FunParam, cwast.Expr3, cwast.DefType, cwast.ExprStmt)):
                    node.x_type = def_rec.x_type
                elif isinstance(node, cwast.TypeSlice):
                    return _MakeIdForDefRec(def_rec, node.x_srcloc)
                elif isinstance(node, cwast.Id):
                    sym = node.x_symbol
                    if isinstance(sym, cwast.TypeSlice):
                        node.x_symbol = def_rec
                        node.x_type = def_rec.x_type
                    elif isinstance(sym, (cwast.DefVar, cwast.FunParam, cwast.DefGlobal)):
                        node.x_type = def_rec.x_type
                    else:
                        assert False
                elif isinstance(node, cwast.ExprAs):
                    assert node.type.x_type in slice_to_struct_map
                    assert isinstance(node.expr.x_type, cwast.TypeArray)
                    return _ConvertValArrayToSliceValRec(node.expr, def_rec, node.x_srcloc)

                else:
                    assert False, f"do not know how to convert slice node [{field}]: {node}"
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)
