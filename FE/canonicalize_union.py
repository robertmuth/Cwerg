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
from FE import eval
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
        (SUM_FIELD_TAG, tc.get_typeid_canon_type()),
        (SUM_FIELD_UNION, tc.InsertUnionType(
            True, union_type.union_member_types()))
    ]
    return typify.MakeDefRec(f"xtuple_{union_type.name}", fields, tc, cwast.SRCLOC_GENERATED)


def MakeAndRegisterUnionTypeReplacements(tc: type_corpus.TypeCorpus) -> list[cwast.DefRec]:
    """For all types directly involving tagged sums, produce a replacement type, a DefRec,
    and return the map from one the other.

    Note: recs need no replacement because the type name of a rec does no depend on the
          fields. So if a field contains a union we can just update that type which we do
          in ReplaceSpans()
    """

    # Go through the type table in topological order and generate the map.
    # Note; we add new types to the map while iterating over it so we take a snapshot first
    tc.ClearReplacementInfo()
    out = []
    for ct in tc.topo_order[:]:
        if ct.desugared:
            continue
        if ct.is_tagged_union():
            rec = _MakeUnionReplacementStruct(ct, tc)
            out.append(rec)
            new_ct = rec.x_type
        elif ct.node in (cwast.DefRec, cwast.DefType):
            continue
        else:
            new_ct = tc.MaybeGetReplacementType(ct)
            if not new_ct:
                continue
        ct.LinkReplacementType(new_ct)
    # TODO: what about DefType?
    return out


def _MakeTypeidVal(ct: cwast.CanonType, srcloc,  ct_typeid: cwast.CanonType) -> cwast.ValNum:
    typeid = ct.get_original_typeid()
    assert typeid >= 0
    return cwast.ValNum(eval.EVAL_STR,
                        x_eval=eval.EvalNum(typeid, ct_typeid.base_type_kind),
                        x_type=ct_typeid, x_srcloc=srcloc)


def _MakeValRecForTaggedUnion(sum_rec: cwast.CanonType, tag_value, union_value, srcloc) -> cwast.ValCompound:
    tag_field, union_field = sum_rec.ast_node.fields
    return canonicalize.MakeValCompound(sum_rec,
                                        [(tag_field.x_type, tag_value),
                                         (union_field.x_type, union_value)], srcloc)


def _CloneId(node: cwast.Id) -> cwast.Id:
    assert isinstance(node, cwast.Id)
    return cwast.Id(node.name, x_symbol=node.x_symbol, x_type=node.x_type,
                    x_srcloc=node.x_srcloc)


def _MakeExpWidenBetweeUntaggedUnions(expr, dst_ct, sl, x_eval):
    return cwast.ExprWiden(expr, cwast.TypeAuto(x_srcloc=sl, x_type=dst_ct),
                           x_srcloc=sl, x_eval=x_eval, x_type=dst_ct)


def _MakeValRecForWidenFromUnion(widen: cwast.ExprWiden, dst_ct: cwast.CanonType) -> cwast.ValCompound:
    src = widen.expr
    sl = widen.x_srcloc
    dst_union_field = dst_ct.get_rec_field(1)

    src_ct: cwast.CanonType = src.x_type
    assert src_ct.original_type.is_tagged_union()
    src_tag_field = src_ct.get_rec_field(0)
    src_union_field = src_ct.get_rec_field(1)
    # to drop this we would need to introduce a temporary since we access it more than once
    assert isinstance(src, cwast.Id), f"{src}"
    # assert False, f"{value.expr} {value.expr.x_type} -> {value.x_type} {value.x_srcloc}"

    tag_value = canonicalize.MakeExprField(
        _CloneId(src), src_tag_field, sl)
    union_field = canonicalize.MakeExprField(
        _CloneId(src),  src_union_field, sl)
    union_value = _MakeExpWidenBetweeUntaggedUnions(
        union_field, dst_union_field.x_type, sl, widen.x_eval)

    return _MakeValRecForTaggedUnion(
        dst_ct, tag_value, union_value, sl)


def _MakeValRecForWidenFromNonUnion(widen: cwast.ExprWiden, dst_ct: cwast.CanonType) -> cwast.ValCompound:
    assert widen.x_type.is_tagged_union()
    assert not widen.expr.x_type.is_union(
    ), f"{widen.expr.x_type} -> {dst_ct} {widen.x_srcloc}"

    dst_tag_field = dst_ct.get_rec_field(0)
    dst_union_field = dst_ct.get_rec_field(1)
    sl = widen.x_srcloc
    tag_value = _MakeTypeidVal(widen.expr.x_type, sl, dst_tag_field.x_type)
    #
    widen.x_type = dst_union_field.x_type
    assert isinstance(widen.type, cwast.TypeAuto)
    widen.type.x_type = dst_union_field.x_type

    return _MakeValRecForTaggedUnion(dst_ct, tag_value, widen, sl)


def _MakeValRecForNarrow(narrow: cwast.ExprNarrow, dst_ct: cwast.CanonType) -> cwast.ValCompound:
    src = narrow.expr
    src_ct: cwast.CanonType = src.x_type
    assert src_ct.original_type.is_tagged_union()
    dst_union_field: cwast.CanonType = dst_ct.get_rec_field(1)
    src_tag_field = src_ct.get_rec_field(0)
    src_union_field = src_ct.get_rec_field(1)
    # TODO
    # to drop this we would need to introduce a temporary
    assert isinstance(src, cwast.Id)
    sl = narrow.x_srcloc
    # assert False, f"{value.expr} {value.expr.x_type} -> {value.x_type} {value.x_srcloc}"

    val_tag = canonicalize.MakeExprField(_CloneId(src), src_tag_field, sl)
    val_union_tmp = canonicalize.MakeExprField(
        _CloneId(src), src_union_field, sl)
    val_union = cwast.ExprNarrow(val_union_tmp,
                                 cwast.TypeAuto(sl, dst_union_field.x_type),
                                 unchecked=True,
                                 x_srcloc=sl,
                                 x_eval=narrow.x_eval,
                                 x_type=dst_union_field.x_type)
    # tag is the same as with the src but (untagged) union is narrowed
    return _MakeValRecForTaggedUnion(dst_ct, val_tag, val_union, sl)


def _ConvertTaggedNarrowToUntaggedNarrow(node: cwast.ExprNarrow, tc: type_corpus.TypeCorpus):
    tagged_ct: cwast.CanonType = node.expr.x_type
    untagged_ct = tc.InsertUnionType(True, tagged_ct.union_member_types())
    node.unchecked = True
    node.expr = cwast.ExprUnionUntagged(node.expr, x_srcloc=node.x_srcloc,
                                        x_type=untagged_ct)


def FunSimplifyTaggedExprNarrow(fun: cwast.DefFun, tc: type_corpus.TypeCorpus):
    """Simplifies ExprNarrow for tagged unions `u`

    After this only unchecked ExprNarrow will be left in the AST

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
    ct_bool = tc.get_bool_canon_type()

    def replacer(node, _parent):
        nonlocal tc, ct_bool
        if not isinstance(node, cwast.ExprNarrow):
            return None
        if not node.expr.x_type.is_tagged_union():
            return None

        if node.unchecked:
            if not node.x_type.is_union():
                _ConvertTaggedNarrowToUntaggedNarrow(node, tc)
            return None

        # ExprNarrow is checked
        sl = node.x_srcloc
        ct_dst = node.x_type
        body = []
        expr = cwast.ExprStmt(body, x_srcloc=sl, x_type=node.x_type)
        node.expr = canonicalize.MakeNodeCopyableWithoutRiskOfSideEffects(
            node.expr, body, False)
        assert canonicalize.IsNodeCopyableWithoutRiskOfSideEffects(
            node.expr)
        # assert isinstance(node.expr, cwast.Id), f"NYI: {node.expr}"
        cond = cwast.ExprIs(cwast.CloneNodeRecursively(node.expr, {}, {}), cwast.TypeAuto(
            x_srcloc=sl, x_type=ct_dst), x_srcloc=sl, x_type=ct_bool)
        if ct_dst.is_union():
            # we already did the check manually
            node.unchecked = True
        else:
            _ConvertTaggedNarrowToUntaggedNarrow(node, tc)
        trap = cwast.StmtTrap(x_srcloc=sl)
        body.append(cwast.StmtIf(cond, [], [trap],  x_srcloc=sl))
        body.append(cwast.StmtReturn(node, x_srcloc=sl, x_target=expr))
        return expr

    cwast.MaybeReplaceAstRecursivelyWithParentPost(fun, replacer)


def ReplaceUnions(node: cwast.DefMod):
    """
    Replaces all sum expressions with rec named tuple_sum<X>

    After this tagged unions will be gone from the ASTs
    """
    def replacer(node, _parent):
        if isinstance(node, cwast.ExprUnionTag):
            # get the tag field from the rec that now represents the union
            # because of the post-order traversal, node.expr has already been processed
            tag_field: cwast.RecField = node.expr.x_type.get_rec_field(0)
            return canonicalize.MakeExprField(node.expr, tag_field, node.x_srcloc)
        elif isinstance(node, cwast.ExprUnionUntagged):
            # get the payload field from the rec that now represents the union
            union_field: cwast.RecField = node.expr.x_type.get_rec_field(1)
            return canonicalize.MakeExprField(node.expr, union_field, node.x_srcloc)

        if cwast.NF.TYPE_ANNOTATED not in node.FLAGS:
            return None
        # now deal with type/expression nodes whose type is changing
        new_ct: Optional[cwast.CanonType] = node.x_type.replacement_type
        if new_ct is None:
            return None
        if isinstance(node, (cwast.DefFun, cwast.DefGlobal,  cwast.DefVar,
                             #
                             cwast.Expr3, cwast.ExprAddrOf, cwast.ExprCall,
                             cwast.ExprDeref, cwast.ExprField, cwast.ExprFront,
                             cwast.ExprPointer, cwast.ExprStmt,
                             #
                             cwast.FunParam,
                             cwast.Id,
                             cwast.RecField,

                             cwast.TypeAuto,
                             #
                             cwast.ValPoint, cwast.ValCompound)):
            typify.NodeChangeType(node, new_ct)
            return None
        elif isinstance(node, cwast.ExprWiden):
            # Note, node.expr has already been processed by the recursion
            ct_orig: cwast.CanonType = node.expr.x_type.original_type
            if ct_orig is not None and ct_orig.is_tagged_union():
                return _MakeValRecForWidenFromUnion(node, new_ct)
            else:
                return _MakeValRecForWidenFromNonUnion(node, new_ct)

        elif isinstance(node, cwast.ExprNarrow):
            # checked ExprNarrow were eliminated by FunSimplifyTaggedExprNarrow
            assert node.unchecked
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
                typify.NodeChangeType(node, new_ct)
                return None
        else:
            assert False, f"do not know how to convert sum node [{
                new_ct.name}]:\n {node} {node.x_srcloc}"

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)
