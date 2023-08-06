"""Canonicalizer For Slices

"""


from typing import Optional

from FrontEnd import cwast
from FrontEnd import type_corpus
from FrontEnd import typify
from FrontEnd import symbolize

############################################################
# Convert Slices to equvalent struct
#
# slice mut u8 -> struct {pointer ptr mut  u8, len uint}
############################################################
SLICE_FIELD_POINTER = "pointer"
SLICE_FIELD_LENGTH = "length"


def _MakeSliceReplacementStruct(slice: cwast.TypeSlice,
                                tc: type_corpus.TypeCorpus) -> cwast.CanonType:
    srcloc = slice.x_srcloc
    pointer_type = cwast.TypePtr(cwast.CloneNodeRecursively(
        slice.type, {}, {}), mut=slice.mut, x_srcloc=srcloc)
    typify.AnnotateNodeType(pointer_type, tc.insert_ptr_type(
        pointer_type.mut, pointer_type.type.x_type))
    pointer_field = cwast.RecField(
        SLICE_FIELD_POINTER, pointer_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(pointer_field, pointer_type.x_type)
    uint_ct = tc.get_uint_canon_type()
    length_type = cwast.TypeBase(uint_ct.base_type_kind, x_srcloc=srcloc)
    typify.AnnotateNodeType(length_type, uint_ct)
    length_field = cwast.RecField(
        SLICE_FIELD_LENGTH, length_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(length_field, length_type.x_type)
    name = f"tuple_{slice.x_type.name}"
    rec = cwast.DefRec(name, [pointer_field, length_field], pub=True,
                       x_srcloc=srcloc)
    cstr: cwast.CanonType = tc.insert_rec_type(f"{name}", rec)
    typify.AnnotateNodeType(rec, cstr)
    tc.finalize_rec_type(cstr)
    return cstr


def _DoesFunSigContainSlices(fun_sig: cwast.CanonType, slice_to_struct_map) -> bool:
    if fun_sig.result_type() in slice_to_struct_map:
        return True
    for p in fun_sig.parameter_types():
        if p in slice_to_struct_map:
            return True
    return False


def _SliceRewriteFunSig(fun_sig: cwast.CanonType, tc: type_corpus.TypeCorpus,
                        slice_to_struct_map) -> cwast.TypeFun:
    assert fun_sig.is_fun()
    result = slice_to_struct_map.get(
        fun_sig.result_type(), fun_sig.result_type())
    params = [slice_to_struct_map.get(p, p) for p in fun_sig.parameter_types()]
    return tc.insert_fun_type(params, result)


def MakeSliceTypeReplacementMap(mods, tc: type_corpus.TypeCorpus):
    """For all types directly involving slices, produce a replacement type
    and return the map from one the other

    Note: recs containing slice member are not thought of as directly involving slices
    TODO: what about sum types?
    """

    # first collect all the slice types occuring in the program.
    # we collect one node witness for each to be used in the next step.
    slice_type_to_slice = {}

    def visitor(node, _):
        nonlocal slice_type_to_slice
        if isinstance(node, cwast.TypeSlice):
            if node.x_type not in slice_type_to_slice:
                slice_type_to_slice[node.x_type] = node

    for mod in mods:
        cwast.VisitAstRecursivelyPost(mod, visitor)

    # now go through the type table in topological order and generate the map.
    # Note; we add new types to the map while iterating over it
    out = {}
    for cstr in tc.topo_order[:]:
        if cstr.is_slice():
            assert cstr in slice_type_to_slice
            out[cstr] = _MakeSliceReplacementStruct(
                slice_type_to_slice[cstr], tc)
        elif cstr.is_fun() and _DoesFunSigContainSlices(cstr, out):
            out[cstr] = _SliceRewriteFunSig(cstr, tc, out)
        elif cstr.is_pointer():
            elem_ct: cwast.CanonType = cstr.underlying_pointer_type()
            if elem_ct in out:
                out[cstr] = tc.insert_ptr_type(cstr.mut, out[elem_ct])
        elif cstr.is_array():
            elem_ct: cwast.CanonType = cstr.underlying_array_type()
            if elem_ct in out:
                out[cstr] = tc.insert_array_type(cstr.array_dim(), elem_ct)

    return out


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc):
    return cwast.Id(def_rec.ast_node.name, x_symbol=def_rec.ast_node, x_type=def_rec, x_srcloc=srcloc)


def _MakeValRecForSlice(pointer, length, slice_rec: cwast.CanonType, srcloc):
    pointer_field, length_field = slice_rec.ast_node.fields
    inits = [cwast.FieldVal(pointer, "",
                            x_field=pointer_field, x_type=pointer_field.x_type,
                            x_srcloc=srcloc),
             cwast.FieldVal(length, "",
                            x_field=length_field, x_type=length_field.x_type,
                            x_srcloc=srcloc, x_value=length.x_value)]
    return cwast.ValRec(_MakeIdForDefRec(slice_rec, srcloc), inits, x_srcloc=srcloc, x_type=slice_rec)


def _ConvertValArrayToSliceValRec(node, slice_rec: cwast.DefRec, srcloc):
    assert node.x_type.is_array()
    pointer_field, length_field = slice_rec.fields
    width = node.x_type.size.x_value
    assert width is not None
    pointer_type = pointer_field.x_type
    pointer = cwast.ExprFront(node, mut=pointer_type.mut,
                              x_type=pointer_type, x_srcloc=srcloc)
    length = cwast.ValNum(f"{width}", x_value=width,
                          x_srcloc=srcloc, x_type=length_field.x_type)
    return _MakeValRecForSlice(pointer, length, slice_rec, srcloc)


def _ConvertMutSliceValRecToSliceValRec(node, slice_rec: cwast.DefRec):
    node.x_type.is_slice()
    assert node.x_type.mut
    # assert node.x_type.type == slice_rec.fields[0].x_type
    return cwast.ExprBitCast(node, _MakeIdForDefRec(slice_rec, node.x_srcloc),
                             x_srcloc=node.x_srcloc, x_type=slice_rec.x_type)


def _ImplicitSliceConversion(rhs, lhs_type, def_rec, srcloc):
    """Convert:
    slice-mut -> slice
    array -> slice
    array-mut -> slice-mut
    """
    if rhs.x_type.is_slice():
        assert lhs_type.type == rhs.x_type.type
        assert not lhs_type.mut and rhs.x_type.mut
        return _ConvertMutSliceValRecToSliceValRec(rhs, def_rec)
    elif rhs.x_type.is_array():
        return _ConvertValArrayToSliceValRec(rhs, def_rec, srcloc)
    else:
        assert False


def _MakeValSliceFromArray(node, dst_type: cwast.CanonType, tc: type_corpus.TypeCorpus,
                           uint_type: cwast.CanonType):
    p_type = tc.insert_ptr_type(dst_type.mut, dst_type.underlying_slice_type())
    pointer = cwast.ExprFront(node, x_srcloc=node.x_type, mut=dst_type.mut, x_type=p_type)
    width = node.x_type.array_dim()
    length = cwast.ValNum(f"{width}", x_value=width,
                          x_srcloc=node.x_srcloc, x_type=uint_type)
    return cwast.ValSlice(pointer, length, x_srcloc=node.x_srcloc, x_type=dst_type)


def InsertExplicitValSlice(node, tc:  type_corpus.TypeCorpus):
    """Eliminate all the implcit Array to Slice conversions. """
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def visitor(node, _):
        nonlocal tc, uint_type
        # Also look into the initialization of structs
        if isinstance(node, cwast.StmtAssignment):
            if node.lhs.x_type.is_slice() and node.expr_rhs.x_type.is_array():
                node.expr_rhs = _MakeValSliceFromArray(
                    node.expr_rhs, node.lhs.x_type, tc, uint_type)
        elif isinstance(node, cwast.FieldVal):
            if node.x_type.is_slice() and node.value.x_type.is_array():
                node.value = _MakeValSliceFromArray(
                    node.value, node.x_type, tc, uint_type)
        elif isinstance(node, (cwast.DefVar, cwast.DefGlobal)):
            initial = node.initial_or_undef_or_auto
            if not isinstance(initial, cwast.ValUndef):
                if node.type_or_auto.x_type.is_slice() and initial.x_type.is_array():
                    node.initial_or_undef_or_auto = _MakeValSliceFromArray(
                        initial, node.type_or_auto.x_type, tc, uint_type)
        elif isinstance(node, cwast.StmtReturn):
            target = node.x_target
            expected = None
            if isinstance(target, cwast.DefFun):
                expected = target.result.x_type
            else:
                assert isinstance(target, cwast.ExprStmt)
                expected = target.x_type

            if expected.is_slice() and node.expr_ret.x_type.is_array():
                node.expr_ret = _MakeValSliceFromArray(
                    node.expr_ret, expected, tc, uint_type)
        elif isinstance(node, cwast.ExprCall):
            # Note: result conversion is dealt with as a lhs recursively
            fun_sig: cwast.CanonType = node.callee.x_type
            for n, (p, a) in enumerate(zip(fun_sig.parameter_types(), node.args)):
                if p != a.x_type and p.is_slice() and a.x_type.is_array():
                    node.args[n] = _MakeValSliceFromArray(
                        a, p, tc, uint_type)

    cwast.VisitAstRecursivelyPost(node, visitor)


def ReplaceExplicitSliceCast(node, tc: type_corpus.TypeCorpus):
    """Eliminate Array to Slice casts. """
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def replacer(node, _):
        nonlocal tc, uint_type
        if isinstance(node, cwast.ExprAs):
            if (node.x_type != node.expr.x_type and
                node.x_type.is_slice() and
                    node.expr.x_type.is_array()):
                return _MakeValSliceFromArray(
                    node.expr, node.x_type, tc, uint_type)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def ReplaceSlice(node, slice_to_struct_map):
    """
    Replaces all slice<X> expressions with rec named tuple_slice<X>
    (cast to slices are eliminated by ReplaceExplicitSliceCast)
    This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

    Complications:
     TODO: see unused _ConvertMutSliceValRecToSliceValRec helper
     `slice<u8> = slice-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node, field):

        # len of array is constant and should have already been eliminated
        if isinstance(node, cwast.ExprLen):
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert len(def_rec.ast_node.fields) == 2
                field = def_rec.ast_node.fields[1]
                # this is only reached if this used to be a slice
                return cwast.ExprField(node.container, SLICE_FIELD_LENGTH,
                                       x_srcloc=node.x_srcloc, x_type=field.x_type,
                                       x_field=field)
        elif isinstance(node, cwast.ExprFront):
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert len(def_rec.ast_node.fields) == 2
                field = def_rec.ast_node.fields[0]
                # this is only reached if this used to be a slice
                return cwast.ExprField(node.container, SLICE_FIELD_POINTER,
                                       x_srcloc=node.x_srcloc, x_type=field.x_type,
                                       x_field=field)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:

            def_rec: Optional[cwast.CanonType] = slice_to_struct_map.get(
                node.x_type)
            if def_rec is not None:
                if isinstance(node, (cwast.TypeAuto, cwast.Expr3, cwast.DefType,
                                     cwast.ExprStmt, cwast.DefFun, cwast.TypeFun,
                                     cwast.FunParam, cwast.ExprCall, cwast.RecField,
                                     cwast.ExprField)):
                    typify.UpdateNodeType(node, def_rec)
                elif isinstance(node, cwast.FieldVal):
                    # assert False
                    typify.UpdateNodeType(node, def_rec)
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
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.ExprPointer):
                    assert node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP
                    assert False
                else:
                    assert False, f"do not know how to convert slice node [{def_rec.name}]: {node}"
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
