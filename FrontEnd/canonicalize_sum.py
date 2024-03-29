"""Canonicalizer For Tagged Sum


Protocol:
* sum_to_struct_map = canonicalize_sum.MakeSumTypeReplacementMap(mod_topo_order)
* for mod in mod_in_top_order:
  - ReplaceExplicitSumCast(mod, sum_to_struct_map, tc)
  - ReplaceSums(mod, sum_to_struct_map)
"""


from typing import Optional

from FrontEnd import cwast
from FrontEnd import type_corpus
from FrontEnd import typify
from FrontEnd import symbolize
from FrontEnd import canonicalize
from FrontEnd import identifier

############################################################
# Convert Tagged Sum to equvalent struct
#
# sum[r64, bool, ...] -> struct {tag u16, union untagged-sum[r64, bool, ... ]}
############################################################
SUM_FIELD_TAG = "tag"
SUM_FIELD_UNION = "union"

# TypeSum -> DefRec
SUM_TO_STRUCT_MAP = dict[cwast.CanonType, cwast.CanonType]


def _MakeSumReplacementStruct(sum_type: cwast.CanonType,
                              tc: type_corpus.TypeCorpus) -> cwast.CanonType:
    assert not sum_type.untagged
    srcloc = cwast.SRCLOC_GENERATED
    #
    tag_ct: cwast.CanonType = tc.get_base_canon_type(
        cwast.BASE_TYPE_KIND.TYPEID)
    tag_type = cwast.TypeBase(tag_ct.base_type_kind,
                              x_srcloc=srcloc, x_type=tag_ct)
    tag_field = cwast.RecField(
        SUM_FIELD_TAG, tag_type, x_srcloc=srcloc, x_type=tag_ct)
    #
    union_ct = tc.insert_union_type(sum_type.union_member_types(), True)
    union_type = cwast.TypeAuto(x_srcloc=srcloc, x_type=union_ct)
    union_field = cwast.RecField(
        SUM_FIELD_UNION, union_type, x_srcloc=srcloc, x_type=union_ct)
    #
    name = f"tuple_{sum_type.name}"
    rec = cwast.DefRec(name, [tag_field, union_field],
                       pub=True, x_srcloc=srcloc)
    rec_ct: cwast.CanonType = tc.insert_rec_type(
        f"{name}", rec, original_type=sum_type)
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
                      sum_to_struct_map: SUM_TO_STRUCT_MAP) -> cwast.CanonType:
    assert fun_sig.is_fun()
    result = sum_to_struct_map.get(
        fun_sig.result_type(), fun_sig.result_type())
    params = [sum_to_struct_map.get(p, p) for p in fun_sig.parameter_types()]
    return tc.insert_fun_type(params, result, original_type=fun_sig)


def MakeSumTypeReplacementMap(_mods, tc: type_corpus.TypeCorpus) -> SUM_TO_STRUCT_MAP:
    """For all types directly involving tagged sums, produce a replacement type, a DefRec,
    and return the map from one the other.

    Note: recs containing sum fields are not thought of as directly involving sums
    """

    # Go through the type table in topological order and generate the map.
    # Note; we add new types to the map while iterating over it so we take a snapshot first
    out: SUM_TO_STRUCT_MAP = {}
    for ct in tc.topo_order[:]:
        if ct.is_tagged_union():
            out[ct] = _MakeSumReplacementStruct(ct, tc)
        elif ct.is_fun() and _DoesFunSigContainSums(ct, out):
            out[ct] = _SumRewriteFunSig(ct, tc, out)
        elif ct.is_pointer():
            replacement = out.get(ct.underlying_pointer_type())
            if replacement is not None:
                out[ct] = tc.insert_ptr_type(
                    ct.mut, replacement, original_type=ct)
        elif ct.is_array():
            replacement = out.get(ct.underlying_array_type())
            if replacement is not None:
                out[ct] = tc.insert_array_type(
                    ct.array_dim(), replacement, original_type=ct)
        elif ct.is_slice():
            replacement = out.get(ct.underlying_slice_type())
            # we probably should run this after slices have been eliminated so we
            # we do not have to deal with this case
            if replacement is not None:
                out[ct] = tc.insert_slice_type(
                    ct.mut, replacement, original_type=ct)
    return out


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc) -> cwast.Id:
    return cwast.Id(def_rec.ast_node.name, x_symbol=def_rec.ast_node, x_type=def_rec,
                    x_srcloc=srcloc)


def _MakeTypeidVal(typeid: int, srcloc,  ct_typeid: cwast.CanonType) -> cwast.ValNum:
    assert typeid >= 0
    return cwast.ValNum(str(typeid), x_value=typeid, x_srcloc=srcloc,
                        x_type=ct_typeid)


def _MakeValRecForSum(sum_rec: cwast.CanonType, tag_value, union_value, srcloc):
    tag_field, union_field = sum_rec.ast_node.fields
    return cwast.ValRec(_MakeIdForDefRec(sum_rec, srcloc), [
        cwast.FieldVal(tag_value, "",
                       x_field=tag_field, x_type=tag_field.x_type, x_srcloc=srcloc,
                       x_value=tag_value.x_value),
        cwast.FieldVal(union_value, "",
                       x_field=union_field, x_type=union_field.x_type,
                       x_srcloc=srcloc, x_value=union_value.x_value)

    ], x_srcloc=srcloc,
        x_type=sum_rec)


def _MakeValRecForWidenFromNonUnion(value: cwast.ExprWiden, sum_rec: cwast.CanonType) -> cwast.ValRec:
    assert sum_rec.is_rec()
    assert value.x_type.is_tagged_union()
    assert not value.expr.x_type.is_union(
    ), f"{value.expr.x_type} -> {sum_rec} {value.x_srcloc}"

    tag_field, union_field = sum_rec.ast_node.fields
    srcloc = value.x_srcloc
    value.x_type = union_field.x_type
    value.type = cwast.TypeAuto(x_srcloc=srcloc, x_type=union_field.x_type)

    return _MakeValRecForSum(sum_rec,
                             _MakeTypeidVal(
                                 value.expr.x_type.get_original_typeid(), srcloc, tag_field.x_type),
                             value,
                             srcloc)


def _CloneId(node: cwast.Id) -> cwast.Id:
    assert isinstance(node, cwast.Id)
    return cwast.Id(node.name, x_symbol=node.x_symbol, x_type=node.x_type,
                    x_srcloc=node.x_srcloc)


def _MakeValRecForNarrow(value: cwast.ExprNarrow, dst_sum_rec: cwast.CanonType) -> cwast.ValRec:
    assert dst_sum_rec.is_rec()
    dst_untagged_union_ct: cwast.CanonType = dst_sum_rec.ast_node.fields[1].x_type
    assert dst_untagged_union_ct.is_untagged_union()
    src_sum_rec: cwast.CanonType = value.expr.x_type
    assert src_sum_rec.is_rec()
    assert src_sum_rec.original_type.is_tagged_union()
    src_tag_field, src_union_field = src_sum_rec.ast_node.fields
    # to drop this we would need to introducea temporary
    assert isinstance(value.expr, cwast.Id)
    sl = value.x_srcloc
    # assert False, f"{value.expr} {value.expr.x_type} -> {value.x_type} {value.x_srcloc}"

    src_tag = cwast.ExprField(_CloneId(value.expr), SUM_FIELD_TAG,
                              x_srcloc=sl, x_type=src_tag_field.x_type,
                              x_field=src_tag_field)
    src_union = cwast.ExprField(_CloneId(value.expr), SUM_FIELD_UNION,
                                x_srcloc=sl, x_type=src_union_field.x_type,
                                x_field=src_union_field)
    union_value = cwast.ExprNarrow(src_union,
                                   cwast.TypeAuto(x_srcloc=sl,
                                                  x_type=dst_untagged_union_ct),
                                   unchecked=True,
                                   x_srcloc=sl,
                                   x_value=value.x_value,
                                   x_type=dst_untagged_union_ct)
    # tag is the same as with the src but (untagged) union is narrowed
    return _MakeValRecForSum(dst_sum_rec, src_tag, union_value, sl)


def _MakeValRecForWidenFromUnion(value: cwast.ExprNarrow, dst_sum_rec: cwast.CanonType) -> cwast.ValRec:
    assert dst_sum_rec.is_rec()
    _, dst_union_field = dst_sum_rec.ast_node.fields
    src_sum_rec: cwast.CanonType = value.expr.x_type
    assert src_sum_rec.is_rec()
    assert src_sum_rec.original_type.is_tagged_union()
    src_tag_field, src_union_field = src_sum_rec.ast_node.fields
    # to drop this we would need to introducea temporary
    assert isinstance(value.expr, cwast.Id)
    srcloc = value.x_srcloc
    # assert False, f"{value.expr} {value.expr.x_type} -> {value.x_type} {value.x_srcloc}"

    tag_value = cwast.ExprField(_CloneId(value.expr), SUM_FIELD_TAG,
                                x_srcloc=srcloc, x_type=src_tag_field.x_type,
                                x_field=src_tag_field)
    union_field = cwast.ExprField(_CloneId(value.expr), SUM_FIELD_UNION,
                                  x_srcloc=srcloc, x_type=src_union_field.x_type,
                                  x_field=src_union_field)
    union_value = cwast.ExprWiden(union_field,
                                  cwast.TypeAuto(x_srcloc=srcloc,
                                                 x_type=dst_union_field.x_type),
                                  x_srcloc=srcloc,
                                  x_value=value.x_value,
                                  x_type=dst_union_field.x_type)

    return _MakeValRecForSum(dst_sum_rec,
                             tag_value, union_value,
                             srcloc)


def _ConvertTaggedNarrowToUntaggedNarrow(node: cwast.ExprNarrow, tc: type_corpus.TypeCorpus):
    tagged_ct: cwast.CanonType = node.expr.x_type
    untagged_ct = tc.insert_union_type(tagged_ct.union_member_types(), True)
    node.unchecked = True
    node.expr = cwast.ExprUnionUntagged(node.expr, x_srcloc=node.x_srcloc,
                                        x_type=untagged_ct)


def SimplifyTaggedExprNarrow(fun: cwast.DefFun, tc: type_corpus.TypeCorpus, id_gen: identifier.IdGen):
    """Simplifies ExprNarrow for tagged unions `u`

    (narrowto @unchecked u t)

    case: if t is a non-union type

    ... (narrowto @unchecked (unionuntagged u) t) ...

    (narrowto u t)

    case: t is union

    case: if t is a non-union type

    (expr [
        (if (is u t) [] [(trap)])
        (return (narrowto @unchecked (unionuntagged u) t))
    ])

    (expr [
        (if (is u t) [] [(trap)])
        (return (narrowto @unchecked u t))
    ])

    """
    def replacer(node, _parent, _field):
        nonlocal tc, id_gen
        if not isinstance(node, cwast.ExprNarrow):
            return None
        if not node.expr.x_type.is_tagged_union():
            return None
        if node.unchecked:
            if not node.x_type.is_union():
                _ConvertTaggedNarrowToUntaggedNarrow(node, tc)
                return False

        else:
            sl = node.x_srcloc
            body  = []
            expr = cwast.ExprStmt(body, x_srcloc=sl, x_type=node.x_type)
            node.expr = canonicalize.MakeNodeCopyableWithoutRiskOfSideEffects(node.expr, body, id_gen, False)
            assert canonicalize.IsNodeCopyableWithoutRiskOfSideEffects(node.expr)
            #assert isinstance(node.expr, cwast.Id), f"NYI: {node.expr}"
            cond = cwast.ExprIs(cwast.CloneNodeRecursively(node.expr, {}, {}), cwast.TypeAuto(
                x_srcloc=sl, x_type=node.x_type), x_srcloc=sl)
            if node.x_type.is_union():
                node.unchecked = True
            else:
                _ConvertTaggedNarrowToUntaggedNarrow(node, tc)
            body.append(cwast.StmtIf(cond, [],
                                 [(cwast.StmtTrap(x_srcloc=sl))], x_srcloc=sl))
            body.append(cwast.StmtReturn(node, x_srcloc=sl, x_target=expr))
            return expr
        return None

    cwast.MaybeReplaceAstRecursivelyPost(fun, replacer)


def ReplaceSums(node, sum_to_struct_map: SUM_TO_STRUCT_MAP):
    """
    Replaces all sum expressions with rec named tuple_sum<X>
    """
    def replacer(node, _parent, _field):

        if isinstance(node, cwast.ExprUnionTag):
            def_rec = node.expr.x_type
            assert def_rec.is_rec()
            assert len(def_rec.ast_node.fields) == 2
            tag_field: cwast.RecField = def_rec.ast_node.fields[0]
            # this is only reached if this used to be a slice
            return cwast.ExprField(node.expr, SUM_FIELD_TAG,
                                   x_srcloc=node.x_srcloc, x_type=tag_field.x_type,
                                   x_field=tag_field)
        elif isinstance(node, cwast.ExprUnionUntagged):
            def_rec = node.expr.x_type
            assert def_rec.is_rec()
            assert len(def_rec.ast_node.fields) == 2
            tag_field: cwast.RecField = def_rec.ast_node.fields[1]
            # this is only reached if this used to be a slice
            return cwast.ExprField(node.expr, SUM_FIELD_UNION,
                                   x_srcloc=node.x_srcloc, x_type=tag_field.x_type,
                                   x_field=tag_field)
        if cwast.NF.TYPE_ANNOTATED not in node.FLAGS:
            return None
        def_rec: Optional[cwast.CanonType] = sum_to_struct_map.get(
            node.x_type)
        if def_rec is None:
            return None
        if isinstance(node, (cwast.TypeAuto, cwast.Expr3, cwast.DefType,
                             cwast.ExprStmt, cwast.DefFun, cwast.TypeFun,
                             cwast.FunParam, cwast.ExprCall, cwast.RecField,
                             cwast.ExprField, cwast.FieldVal)):
            typify.UpdateNodeType(node, def_rec)
            return None
        elif isinstance(node, cwast.TypeUnion):
            return _MakeIdForDefRec(def_rec, node.x_srcloc)
        elif isinstance(node, cwast.ExprWiden):
            ct_src: cwast.CanonType = node.expr.x_type
            if ct_src.original_type is not None and ct_src.original_type.is_tagged_union():
                return _MakeValRecForWidenFromUnion(node, sum_to_struct_map[node.x_type])
            else:
                return _MakeValRecForWidenFromNonUnion(node, sum_to_struct_map[node.x_type])

        elif isinstance(node, cwast.ExprNarrow):
            # applies to the destination of the narrow
            assert isinstance(
                node.expr, cwast.Id), "need to introduce ExprStmt"
            ct_src: cwast.CanonType = node.expr.x_type
            assert ct_src.is_rec(
            ), f"{ct_src} -> {node.x_type}: {node.x_srcloc}"

            return _MakeValRecForNarrow(node, sum_to_struct_map[node.x_type])
        elif isinstance(node, cwast.Id):
            sym = node.x_symbol
            # TODO
            # This needs a lot of work also what about field references to
            # rewritten fields
            if isinstance(sym, cwast.TypeUnion):
                symbolize.AnnotateNodeSymbol(node, def_rec)
            typify.UpdateNodeType(node, def_rec)
            return None
        elif isinstance(node, cwast.ExprPointer):
            assert node.pointer_expr_kind is cwast.POINTER_EXPR_KIND.INCP
            assert False
        else:
            assert False, f"do not know how to convert sum node [{def_rec.name}]: {node} {node.x_srcloc}"

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
