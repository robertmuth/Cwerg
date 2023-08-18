"""Canonicalizer For Tagged Sum

"""


from typing import Optional, Dict

from FrontEnd import cwast
from FrontEnd import type_corpus
from FrontEnd import typify
from FrontEnd import symbolize

############################################################
# Convert Tagged Sum to equvalent struct
#
# sum[r64, bool, ...] -> struct {tag u16, union untagged-sum[r64, bool, ... ]}
############################################################
SUM_FIELD_TAG = "tag"
SUM_FIELD_UNION = "union"

SUM_TO_STRUCT_MAP = Dict[cwast.CanonType, cwast.CanonType]


def _MakeSumReplacementStruct(sum_type: cwast.TypeSum,
                              tc: type_corpus.TypeCorpus) -> cwast.CanonType:
    assert not sum_type.untagged
    srcloc = sum_type.x_srcloc
    #
    tag_ct: cwast.CanonType = tc.get_base_canon_type(cwast.BASE_TYPE_KIND.TYPEID)
    tag_type = cwast.TypeBase(tag_ct.base_type_kind, x_srcloc=srcloc)
    typify.AnnotateNodeType(tag_type, tag_ct)
    tag_field = cwast.RecField(SUM_FIELD_TAG, tag_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(tag_field, tag_ct)
    #
    union_type = cwast.TypeSum([cwast.CloneNodeRecursively(
        x, {}, {}) for x in sum_type.types], untagged=True, x_srcloc=srcloc)
    union_ct = tc.insert_sum_type(sum_type.x_type.sum_types(), True)
    typify.AnnotateNodeType(union_type, union_ct)
    union_field = cwast.RecField(SUM_FIELD_UNION, union_type, x_srcloc=srcloc)
    typify.AnnotateNodeType(union_field, union_ct)
    #
    name = f"tuple_{sum_type.x_type.name}"
    rec = cwast.DefRec(name, [tag_field, union_field], pub=True, x_srcloc=srcloc)
    rec_ct: cwast.CanonType = tc.insert_rec_type(f"{name}", rec)
    typify.AnnotateNodeType(rec, rec_ct)
    tc.finalize_rec_type(rec_ct)
    return rec_ct


def _DoesFunSigContainSums(fun_sig: cwast.CanonType,
                           sum_to_struct_map: SUM_TO_STRUCT_MAP) -> bool:
    if fun_sig.result_type() in sum_to_struct_map:
        return True
    for p in fun_sig.parameter_types():
        if p in sum_to_struct_map:
            return True
    return False


def _SumRewriteFunSig(fun_sig: cwast.CanonType, tc: type_corpus.TypeCorpus,
                      sum_to_struct_map: SUM_TO_STRUCT_MAP) -> cwast.TypeFun:
    assert fun_sig.is_fun()
    result = sum_to_struct_map.get(
        fun_sig.result_type(), fun_sig.result_type())
    params = [sum_to_struct_map.get(p, p) for p in fun_sig.parameter_types()]
    return tc.insert_fun_type(params, result)


def MakeSumTypeReplacementMap(mods, tc: type_corpus.TypeCorpus) -> SUM_TO_STRUCT_MAP:
    """For all types directly involving tagged sums, produce a replacement type
    and return the map from one the other

    Note: recs containing sum fields are not thought of as directly involving sums
    """

    # first collect all the slice types occuring in the program.
    # we collect one node witness for each to be used in the next step.
    sum_type_to_struct: SUM_TO_STRUCT_MAP = {}

    def visitor(node, _):
        nonlocal sum_type_to_struct
        if isinstance(node, cwast.TypeSum) and not node.untagged:
            if node.x_type not in sum_type_to_struct:
                sum_type_to_struct[node.x_type] = node

    for mod in mods:
        cwast.VisitAstRecursivelyPost(mod, visitor)

    # now go through the type table in topological order and generate the map.
    # Note; we add new types to the map while iterating over it
    out: SUM_TO_STRUCT_MAP = {}
    for ct in tc.topo_order[:]:
        if ct.is_tagged_sum():
            assert ct in sum_type_to_struct
            out[ct] = _MakeSumReplacementStruct(sum_type_to_struct[ct], tc)
        elif ct.is_fun() and _DoesFunSigContainSums(ct, out):
            out[ct] = _SumRewriteFunSig(ct, tc, out)
        elif ct.is_pointer():
            elem_ct: cwast.CanonType = ct.underlying_pointer_type()
            if elem_ct in out:
                out[ct] = tc.insert_ptr_type(ct.mut, out[elem_ct])
        elif ct.is_array():
            elem_ct: cwast.CanonType = ct.underlying_array_type()
            if elem_ct in out:
                out[ct] = tc.insert_array_type(ct.array_dim(), elem_ct)
        elif ct.is_slice():
            elem_ct: cwast.CanonType = ct.underlying_slice_type()
            # we probably should run this after slices have been eliminates so we
            # we do not have to deal with this case
            if elem_ct in out:
                out[ct] = tc.insert_slice_type(elem_ct)
    return out


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc):
    return cwast.Id(def_rec.ast_node.name, x_symbol=def_rec.ast_node,
                    x_type=def_rec, x_srcloc=srcloc)




def ReplaceSums(node, sum_to_struct_map: SUM_TO_STRUCT_MAP):
    """
    Replaces all sum expressions with rec named tuple_sum<X>
    (cast to slices are eliminated by ReplaceExplicitSliceCast)
    This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

    Complications:
     TODO: see unused _ConvertMutSliceValRecToSliceValRec helper
     `slice<u8> = slice-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node, field):

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:

            def_rec: Optional[cwast.CanonType] = sum_to_struct_map.get(node.x_type)
            if def_rec is not None:
                if isinstance(node, (cwast.TypeAuto, cwast.Expr3, cwast.DefType,
                                     cwast.ExprStmt, cwast.DefFun, cwast.TypeFun,
                                     cwast.FunParam, cwast.ExprCall, cwast.RecField,
                                     cwast.ExprField, cwast.FieldVal)):
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.TypeSum):
                    return _MakeIdForDefRec(def_rec, node.x_srcloc)
                elif isinstance(node, cwast.Id):
                    sym = node.x_symbol
                    # TODO
                    # This needs a lot of work also what about field references to
                    # rewritten fields
                    if isinstance(sym, cwast.TypeSum):
                        symbolize.AnnotateNodeSymbol(node, def_rec)
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.ExprPointer):
                    assert node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP
                    assert False
                else:
                    assert False, f"do not know how to convert sum node [{def_rec.name}]: {node}"
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
