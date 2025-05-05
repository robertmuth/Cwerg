"""Canonicalizer For Tagged Unions


Protocol:
* MakeUnionsTypeReplacementMap(mod_topo_order)
* for mod in mod_in_top_order:
  - ReplaceUnionss(mod)
"""


from typing import Optional

from FE import cwast
from FE import type_corpus
from FE import typify
from FE import canonicalize

############################################################
# Convert Tagged Unions to equvalent struct
#
# sum[r64, bool, ...] -> struct {tag u16, union untagged-sum[r64, bool, ... ]}
############################################################
SUM_FIELD_TAG = cwast.NAME.Make("tag")
SUM_FIELD_UNION = cwast.NAME.Make("union")


def _MakeUnionReplacementStruct(union_type: cwast.CanonType,
                                tc: type_corpus.TypeCorpus) -> cwast.DefRec:
    assert not union_type.untagged
    fields = [
        (SUM_FIELD_TAG, tc.get_base_canon_type(cwast.BASE_TYPE_KIND.TYPEID)),
        (SUM_FIELD_UNION, tc.insert_union_type(
            union_type.union_member_types(), True))
    ]
    return canonicalize.MakeDefRec(f"xtuple_{union_type.name}", fields, tc, cwast.SRCLOC_GENERATED)


def MakeAndRegisterUnionTypeReplacements(mod_gen: cwast.DefMod, tc: type_corpus.TypeCorpus):
    """For all types directly involving tagged sums, produce a replacement type, a DefRec,
    and return the map from one the other.

    Note: recs containing sum fields are not thought of as directly involving sums
    """

    # Go through the type table in topological order and generate the map.
    # Note; we add new types to the map while iterating over it so we take a snapshot first
    def add_replacement(old_ct: cwast.CanonType, new_ct: cwast.CanonType):
        assert old_ct.replacement_type is None
        old_ct.replacement_type = new_ct
        new_ct.original_type = old_ct

    for ct in tc.topo_order[:]:
        if ct.replacement_type is not None:
            continue
        if ct.is_tagged_union():
            rec = _MakeUnionReplacementStruct(ct, tc)
            mod_gen.body_mod.append(rec)
            add_replacement(ct, rec.x_type)
        elif ct.is_fun():
            new_ct = canonicalize.MaybeMakeFunSigReplacementType(ct, tc)
            if new_ct:
                add_replacement(ct, new_ct)
        elif ct.is_pointer():
            replacement = ct.underlying_pointer_type().replacement_type
            if replacement is not None:
                add_replacement(ct, tc.insert_ptr_type(ct.mut, replacement))
        elif ct.is_vec():
            replacement = ct.underlying_array_type().replacement_type
            if replacement is not None:
                add_replacement(ct, tc.insert_array_type(
                    ct.array_dim(), replacement))
        elif ct.is_span():
            # This is now run this after spans have been eliminated so
            # we do not have to deal with this case anymore
            assert False
            replacement = ct.underlying_span_type().replacement_type
            if replacement is not None:
                add_replacement(ct, tc.insert_span_type(
                    ct.mut, replacement))


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc) -> cwast.Id:
    return cwast.Id(def_rec.ast_node.name, None, x_symbol=def_rec.ast_node, x_type=def_rec,
                    x_srcloc=srcloc)


def _MakeTypeidVal(typeid: int, srcloc,  ct_typeid: cwast.CanonType) -> cwast.ValNum:
    assert typeid >= 0
    return cwast.ValNum(str(typeid), x_value=typeid, x_srcloc=srcloc,
                        x_type=ct_typeid)


def _MakeValRecForUnion(sum_rec: cwast.CanonType, tag_value, union_value, srcloc) -> cwast.ValCompound:
    tag_field, union_field = sum_rec.ast_node.fields
    return cwast.ValCompound(_MakeIdForDefRec(sum_rec, srcloc), [
        cwast.ValPoint(tag_value, cwast.ValAuto(x_srcloc=srcloc),
                       x_type=tag_field.x_type, x_srcloc=srcloc,
                       x_value=tag_value.x_value),
        cwast.ValPoint(union_value, cwast.ValAuto(x_srcloc=srcloc),
                       x_type=union_field.x_type,
                       x_srcloc=srcloc, x_value=union_value.x_value)

    ], x_srcloc=srcloc,
        x_type=sum_rec)


def _MakeValRecForWidenFromNonUnion(value: cwast.ExprWiden, sum_rec: cwast.CanonType) -> cwast.ValCompound:
    assert sum_rec.is_rec()
    assert value.x_type.is_tagged_union()
    assert not value.expr.x_type.is_union(
    ), f"{value.expr.x_type} -> {sum_rec} {value.x_srcloc}"

    tag_field, union_field = sum_rec.ast_node.fields
    srcloc = value.x_srcloc
    value.x_type = union_field.x_type
    value.type = cwast.TypeAuto(x_srcloc=srcloc, x_type=union_field.x_type)

    return _MakeValRecForUnion(sum_rec,
                               _MakeTypeidVal(
                                   value.expr.x_type.get_original_typeid(), srcloc, tag_field.x_type),
                               value,
                               srcloc)


def _CloneId(node: cwast.Id) -> cwast.Id:
    assert isinstance(node, cwast.Id)
    return cwast.Id(node.name, None, x_symbol=node.x_symbol, x_type=node.x_type,
                    x_srcloc=node.x_srcloc)


def _MakeValRecForNarrow(value: cwast.ExprNarrow, dst_sum_rec: cwast.CanonType) -> cwast.ValCompound:
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

    src_tag = cwast.ExprField(_CloneId(value.expr), canonicalize.IdNodeFromRecField(src_tag_field, sl),
                              x_srcloc=sl, x_type=src_tag_field.x_type)
    src_union = cwast.ExprField(_CloneId(value.expr), canonicalize.IdNodeFromRecField(src_union_field, sl),
                                x_srcloc=sl, x_type=src_union_field.x_type)
    union_value = cwast.ExprNarrow(src_union,
                                   cwast.TypeAuto(x_srcloc=sl,
                                                  x_type=dst_untagged_union_ct),
                                   unchecked=True,
                                   x_srcloc=sl,
                                   x_value=value.x_value,
                                   x_type=dst_untagged_union_ct)
    # tag is the same as with the src but (untagged) union is narrowed
    return _MakeValRecForUnion(dst_sum_rec, src_tag, union_value, sl)


def _MakeValRecForWidenFromUnion(value: cwast.ExprWiden, dst_sum_rec: cwast.CanonType) -> cwast.ValCompound:
    assert dst_sum_rec.is_rec()
    _, dst_union_field = dst_sum_rec.ast_node.fields
    src_sum_rec: cwast.CanonType = value.expr.x_type
    assert src_sum_rec.is_rec()
    assert src_sum_rec.original_type.is_tagged_union()
    src_tag_field, src_union_field = src_sum_rec.ast_node.fields
    # to drop this we would need to introduce a temporary since we access it more than once
    assert isinstance(value.expr, cwast.Id), f"{value.expr}"
    sl = value.x_srcloc
    # assert False, f"{value.expr} {value.expr.x_type} -> {value.x_type} {value.x_srcloc}"

    tag_value = cwast.ExprField(_CloneId(value.expr), canonicalize.IdNodeFromRecField(src_tag_field, sl),
                                x_srcloc=sl, x_type=src_tag_field.x_type)
    union_field = cwast.ExprField(_CloneId(value.expr),  canonicalize.IdNodeFromRecField(src_union_field, sl),
                                  x_srcloc=sl, x_type=src_union_field.x_type)
    union_value = cwast.ExprWiden(union_field,
                                  cwast.TypeAuto(
                                      x_srcloc=sl, x_type=dst_union_field.x_type),
                                  x_srcloc=sl,
                                  x_value=value.x_value,
                                  x_type=dst_union_field.x_type)

    return _MakeValRecForUnion(dst_sum_rec,
                               tag_value, union_value,
                               sl)


def _ConvertTaggedNarrowToUntaggedNarrow(node: cwast.ExprNarrow, tc: type_corpus.TypeCorpus):
    tagged_ct: cwast.CanonType = node.expr.x_type
    untagged_ct = tc.insert_union_type(tagged_ct.union_member_types(), True)
    node.unchecked = True
    node.expr = cwast.ExprUnionUntagged(node.expr, x_srcloc=node.x_srcloc,
                                        x_type=untagged_ct)


def SimplifyTaggedExprNarrow(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
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
    def replacer(node, _parent):
        nonlocal tc
        if not isinstance(node, cwast.ExprNarrow):
            return None
        if not node.expr.x_type.is_tagged_union():
            return None
        if node.unchecked:
            if not node.x_type.is_union():
                _ConvertTaggedNarrowToUntaggedNarrow(node, tc)
                return None

        else:
            sl = node.x_srcloc
            body = []
            expr = cwast.ExprStmt(body, x_srcloc=sl, x_type=node.x_type)
            node.expr = canonicalize.MakeNodeCopyableWithoutRiskOfSideEffects(
                node.expr, body, False)
            assert canonicalize.IsNodeCopyableWithoutRiskOfSideEffects(
                node.expr)
            # assert isinstance(node.expr, cwast.Id), f"NYI: {node.expr}"
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

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def ReplaceUnions(node):
    """
    Replaces all sum expressions with rec named tuple_sum<X>
    """
    def replacer(node, _parent):
        sl = node.x_srcloc
        if isinstance(node, cwast.ExprUnionTag):
            # get the tag field from the rec that now represents the union
            # because of the post-order traversal, node.expr has already been processed
            new_ct = node.expr.x_type
            assert new_ct.is_rec()
            assert new_ct.original_type is not None
            assert new_ct.original_type.is_union()
            assert len(new_ct.ast_node.fields) == 2
            tag_field: cwast.RecField = new_ct.ast_node.fields[0]
            return cwast.ExprField(node.expr,  canonicalize.IdNodeFromRecField(tag_field, sl),
                                   x_srcloc=sl, x_type=tag_field.x_type)
        elif isinstance(node, cwast.ExprUnionUntagged):
            # get the payload field from the rec that now represents the union
            new_ct = node.expr.x_type
            assert new_ct.is_rec()
            assert new_ct.original_type is not None
            assert new_ct.original_type.is_union()
            assert len(new_ct.ast_node.fields) == 2
            union_field: cwast.RecField = new_ct.ast_node.fields[1]
            return cwast.ExprField(node.expr, canonicalize.IdNodeFromRecField(union_field, sl),
                                   x_srcloc=sl,
                                   x_type=union_field.x_type)
        if cwast.NF.TYPE_ANNOTATED not in node.FLAGS:
            return None
        # now deal with type/expression nodes whose type is changing
        new_ct: Optional[cwast.CanonType] = node.x_type.replacement_type
        if new_ct is None:
            return None
        if isinstance(node, (cwast.TypeAuto, cwast.Expr3, cwast.DefType,
                             cwast.ExprStmt, cwast.DefFun, cwast.TypeFun,
                             cwast.TypeVec, cwast.DefVar, cwast.DefGlobal,
                             cwast.FunParam, cwast.ExprCall, cwast.RecField,
                             cwast.ExprField, cwast.ValPoint,
                             cwast.ValCompound, cwast.TypePtr, cwast.ExprPointer,
                             cwast.ExprFront, cwast.ExprDeref, cwast.ExprAddrOf)):
            typify.UpdateNodeType(node, new_ct)
            return None
        elif isinstance(node, cwast.TypeUnion):
            return _MakeIdForDefRec(new_ct, sl)
        elif isinstance(node, cwast.ExprWiden):
            ct_src: cwast.CanonType = node.expr.x_type
            if ct_src.original_type is not None and ct_src.original_type.is_tagged_union():
                return _MakeValRecForWidenFromUnion(node, new_ct)
            else:
                return _MakeValRecForWidenFromNonUnion(node, new_ct)

        elif isinstance(node, cwast.ExprNarrow):
            if new_ct.original_type.is_tagged_union():
                assert new_ct.is_rec()
                # node.expr has already been processed
                assert node.expr.x_type.original_type.is_tagged_union()
                assert node.expr.x_type.is_rec()
                # if the old type of the expression was an untagged unoion
                # we must translate it to ValRec representing the new type.
                # Note: if the narrowed type is an untagged union, the starting
                # type must also be one
                return _MakeValRecForNarrow(node, new_ct)
            else:
                typify.UpdateNodeType(node, new_ct)
                return None
        elif isinstance(node, cwast.Id):
            typify.UpdateNodeType(node, new_ct)
            return None
        else:
            assert False, f"do not know how to convert sum node [{
                new_ct.name}]:\n {node} {node.x_srcloc}"

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)
