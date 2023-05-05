"""Canonicalizer For Slices

"""

import dataclasses
import logging
import pp

from typing import List, Dict, Set, Optional, Union, Any

from FrontEnd import identifier
from FrontEnd import cwast
from FrontEnd import types
from FrontEnd import typify
from FrontEnd import symbolize

############################################################
# Convert Slices to equvalent struct
#
# slice mut u8 -> struct {pointer ptr mut  u8, len uint}
############################################################
SLICE_FIELD_POINTER = "pointer"
SLICE_FIELD_LENGTH = "length"


def _MakeSliceReplacementStruct(slice: cwast.TypeSlice, tc: types.TypeCorpus) -> cwast.DefRec:
    srcloc = slice.x_srcloc
    pointer_type = cwast.TypePtr(slice.mut, cwast.CloneNodeRecursively(
        slice.type, {}, {}), x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, pointer_type, tc.insert_ptr_type(
        pointer_type.mut, pointer_type.type.x_type))
    pointer_field = cwast.RecField(SLICE_FIELD_POINTER, pointer_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, pointer_field, pointer_type.x_type)
    length_type = cwast.TypeBase(tc.uint_kind, x_srcloc=srcloc)
    typify.AnnotateNodeType(
        tc, length_type, tc.insert_base_type(length_type.base_type_kind))
    length_field = cwast.RecField(SLICE_FIELD_LENGTH, length_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(tc, length_field, length_type.x_type)
    name = f"tuple_{tc.canon_name(slice.x_type)}"
    rec = cwast.DefRec(True, name, [pointer_field, length_field],
                       x_srcloc=srcloc)
    cstr = tc.insert_rec_type(f"{name}", rec)
    assert cstr == rec
    typify.AnnotateNodeType(tc, rec, cstr)
    tc.finalize_rec_type(rec)
    assert rec.x_type == rec
    return rec


def _DoesFunSigContainSlices(fun_sig: cwast.TypeFun, slice_to_struct_map) -> bool:
    if fun_sig.result.x_type in slice_to_struct_map:
        return True
    for p in fun_sig.params:
        if p.type in slice_to_struct_map:
            return True
    return False


def _SliceRewriteFunSig(fun_sig: cwast.TypeFun, tc: types.TypeCorpus, slice_to_struct_map) -> cwast.TypeFun:
    result = slice_to_struct_map.get(fun_sig.result, fun_sig.result)
    params = [slice_to_struct_map.get(p.type, p.type) for p in fun_sig.params]
    return tc.insert_fun_type(params, result)


def MakeSliceTypeReplacementMap(mods, tc: types.TypeCorpus):

    slice_type_to_slice = {}

    def visitor(node, _):
        nonlocal slice_type_to_slice
        if isinstance(node, cwast.TypeSlice):
            if node.x_type not in slice_type_to_slice:
                slice_type_to_slice[node.x_type] = node

    for mod in mods:
        cwast.VisitAstRecursivelyPost(mod, visitor)

    out = {}
    for cstr in tc.topo_order[:]:
        if isinstance(cstr, cwast.TypeSlice):
            assert cstr in slice_type_to_slice
            out[cstr] = _MakeSliceReplacementStruct(
                slice_type_to_slice[cstr], tc)
        elif isinstance(cstr, cwast.TypeFun) and _DoesFunSigContainSlices(cstr, out):
            out[cstr] = _SliceRewriteFunSig(cstr, tc, out)
        elif isinstance(cstr, cwast.TypePtr) and cstr.type in out:
            out[cstr] = tc.insert_ptr_type(cstr.mut, out[cstr.type])
        elif isinstance(cstr, cwast.TypeArray) and cstr.type in out:
            out[cstr] = tc.insert_array_type(cstr.size, out[cstr.type])

    return out


def _MakeIdForDefRec(def_rec, srcloc):
    return cwast.Id(def_rec.name, x_symbol=def_rec, x_type=def_rec.x_type, x_srcloc=srcloc)


def _ConvertValArrayToPointer(node, pointer_type, index_type):
    zero_offset = cwast.ValNum(
        f"0", x_srcloc=node.x_srcloc, x_type=index_type, x_value=0)
    return cwast.ExprAddrOf(pointer_type.mut,
                            cwast.ExprIndex(node, zero_offset,
                                            x_type=pointer_type.type, x_srcloc=node.x_srcloc), x_type=pointer_type,
                            x_srcloc=node.x_srcloc)


def _MakeValRecForSlice(pointer, length, slice_rec: cwast.DefRec, srcloc):
    pointer_field, length_field = slice_rec.fields
    inits = [cwast.FieldVal(pointer, "",
                            x_field=pointer_field, x_type=pointer_field.x_type,
                            x_srcloc=srcloc),
             cwast.FieldVal(length, "",
                            x_field=length_field, x_type=length_field.x_type,
                            x_srcloc=srcloc)]
    return cwast.ValRec(_MakeIdForDefRec(slice_rec, srcloc), inits, x_srcloc=srcloc, x_type=slice_rec.x_type)


def _ConvertValArrayToSliceValRec(node, slice_rec: cwast.DefRec, srcloc):
    assert isinstance(node.x_type, cwast.TypeArray)
    pointer_field, length_field = slice_rec.fields
    width = node.x_type.size.x_value
    assert width is not None
    pointer = _ConvertValArrayToPointer(
        node, pointer_field.x_type, length_field.x_type)
    length = cwast.ValNum(f"{width}", x_value=width,
                          x_srcloc=srcloc, x_type=length_field.x_type)
    return _MakeValRecForSlice(pointer, length, slice_rec, srcloc)


def _ConvertMutSliceValRecToSliceValRec(node, slice_rec: cwast.DefRec):
    assert isinstance(node.x_type, cwast.TypeSlice)
    assert node.x_type.mut
    # assert node.x_type.type == slice_rec.fields[0].x_type
    return cwast.ExprBitCast(node, _MakeIdForDefRec(slice_rec, node.x_srcloc), x_srcloc=node.x_srcloc, x_type=slice_rec.x_type)


def _ImplicitSliceConversion(rhs, lhs_type, def_rec, srcloc):
    """Convert:
    slice-mut -> slice
    array -> slice
    array-mut -> slice-mut
    """
    if isinstance(rhs.x_type, cwast.TypeSlice):
        assert lhs_type.type == rhs.x_type.type
        assert not lhs_type.mut and rhs.x_type.mut
        return _ConvertMutSliceValRecToSliceValRec(rhs, def_rec)
    elif isinstance(rhs.x_type, cwast.TypeArray):
        return _ConvertValArrayToSliceValRec(rhs, def_rec, srcloc)
    else:
        assert False


def _MakeValSliceFromArray(node, dst_type: cwast.TypeSlice, tc: types.TypeCorpus, uint_type):
    pointer = cwast.ExprFront(dst_type.mut, node, x_srcloc=node.x_type,
                              x_type=tc.insert_ptr_type(dst_type.mut, dst_type.type))
    width = node.x_type.size.x_value
    length = cwast.ValNum(f"{width}", x_value=width,
                          x_srcloc=node.x_srcloc, x_type=uint_type)
    return cwast.ValSlice(pointer, length, x_srcloc=node.x_srcloc, x_type=dst_type)


def InsertExplicitValSlice(node, tc:  types.TypeCorpus):
    uint_type = tc.insert_base_type(cwast.BASE_TYPE_KIND.UINT)

    def visitor(node, field):
        nonlocal tc, uint_type
        # Also look into the initialization of structs
        if isinstance(node, cwast.StmtAssignment):
            if (node.lhs.x_type != node.expr_rhs.x_type and
                isinstance(node.lhs.x_type, cwast.TypeSlice) and
                    isinstance(node.expr_rhs.x_type, cwast.TypeArray)):
                node.expr_rhs = _MakeValSliceFromArray(
                    node.expr_rhs, node.lhs.x_type, tc, uint_type)
        elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
            if not isinstance(node.initial_or_undef, cwast.ValUndef):
                if (node.type_or_auto.x_type != node.initial_or_undef.x_type and
                    isinstance(node.type_or_auto.x_type, cwast.TypeSlice) and
                        isinstance(node.initial_or_undef.x_type, cwast.TypeArray)):
                    node.initial_or_undef = _MakeValSliceFromArray(
                        node.initial_or_undef, node.type_or_auto.x_type, tc, uint_type)
        elif isinstance(node, cwast.ExprCall):
            # Note: result conversion is dealt with as a lhs recursively
            fun_sig: cwast.TypeFun = node.callee.x_type
            for n, (p, a) in enumerate(zip(fun_sig.params, node.args)):
                if (p.type != a.x_type and
                    isinstance(p.type, cwast.TypeSlice) and
                        isinstance(a.x_type, cwast.TypeArray)):
                    node.args[n] = _MakeValSliceFromArray(
                        a, p.type, tc, uint_type)

    cwast.VisitAstRecursivelyPost(node, visitor)


def ReplaceSlice(node, tc: types.TypeCorpus, slice_to_struct_map):
    """
     This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

     Complications:
     TODO: see unused _ConvertMutSliceValRecToSliceValRec helper
     `slice<u8> = slice-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node, field):
        nonlocal tc

        if isinstance(node, cwast.ExprLen):
            def_rec: cwast.DefRec = slice_to_struct_map.get(
                node.container.x_type)
            if def_rec is not None:
                cwast.MaybeReplaceAstRecursively(node, replacer)
                return cwast.ExprField(node.container, SLICE_FIELD_LENGTH,
                                       x_srcloc=node.x_srcloc, x_type=node.x_type,
                                       x_field=def_rec.fields[1])
        elif isinstance(node, cwast.ExprFront):
            def_rec: cwast.DefRec = slice_to_struct_map.get(
                node.container.x_type)
            if def_rec is not None:
                cwast.MaybeReplaceAstRecursively(node, replacer)
                return cwast.ExprField(node.container, SLICE_FIELD_POINTER,
                                       x_srcloc=node.x_srcloc, x_type=node.x_type,
                                       x_field=def_rec.fields[0])

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:

            def_rec: cwast.DefRec = slice_to_struct_map.get(node.x_type)
            if def_rec is not None:
                if isinstance(node, (cwast.TypeAuto, cwast.Expr3, cwast.DefType, cwast.ExprStmt,
                                     cwast.DefFun, cwast.TypeFun, cwast.FunParam)):
                    typify.UpdateNodeType(tc, node, def_rec)
                elif isinstance(node, cwast.TypeSlice):
                    return _MakeIdForDefRec(def_rec, node.x_srcloc)
                elif isinstance(node, cwast.ValSlice):
                    return _MakeValRecForSlice(node.pointer, node.expr_size, def_rec, node.x_srcloc)
                elif isinstance(node, cwast.Id):
                    sym = node.x_symbol
                    # TODO
                    # This needs a lot of work also what about field references to
                    # rewritten fields
                    if isinstance(sym, cwast.TypeSlice):
                        symbolize.AnnotateNodeSymbol(node, def_rec)
                    typify.UpdateNodeType(tc, node, def_rec)
                    return None
                elif isinstance(node, cwast.ExprAs):
                    assert node.type.x_type in slice_to_struct_map
                    assert isinstance(node.expr.x_type, cwast.TypeArray)
                    return _ConvertValArrayToSliceValRec(node.expr, def_rec, node.x_srcloc)

                else:
                    assert False, f"do not know how to convert slice node [{field}]: {node}"
        return None

    cwast.MaybeReplaceAstRecursively(node, replacer)
