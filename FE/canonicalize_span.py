"""Canonicalizer For Spans

"""


from FE import canonicalize
from FE import cwast
from FE import type_corpus
from FE import typify
from FE import eval

############################################################
# Convert Spans to equvalent struct
#
# span mut u8 -> struct {pointer ptr mut  u8, len uint}
############################################################
SLICE_FIELD_POINTER = cwast.NAME.Make("pointer")
SLICE_FIELD_LENGTH = cwast.NAME.Make("length")


def _MakeSpanReplacementStruct(span_type: cwast.CanonType,
                               tc: type_corpus.TypeCorpus) -> cwast.DefRec:
    fields = [
        (SLICE_FIELD_POINTER, tc.InsertPtrType(
            span_type.mut, span_type.underlying_type())),
        (SLICE_FIELD_LENGTH,  tc.get_uint_canon_type())
    ]
    return typify.MakeDefRec(f"xtuple_{span_type.name}", fields, tc, cwast.SRCLOC_GENERATED)


def MakeAndRegisterSpanTypeReplacements(tc: type_corpus.TypeCorpus) -> list[cwast.DefRec]:
    """For all types directly involving spans, produce a replacement type
    and return the map from one the other

    Note: recs need no replacement because the type name of a rec does no depend on the
          fields. So if a field contains a span we can just update that type which we do
          in ReplaceSpans()
    """
    tc.ClearReplacementInfo()
    # Go through the type table in topological order.
    # Note: we add new types to the map while iterating over it so we take
    # a snapshot first
    out = []
    for ct in tc.topo_order[:]:
        if ct.desugared:
            continue
        if ct.is_span():
            rec = _MakeSpanReplacementStruct(ct, tc)
            out.append(rec)
            new_ct = rec.x_type
        # Rec and DefType are handled are not replaced.
        # Their names do not reflect their children.
        # In the case of DefRec we patch up the RecFields separately.
        # DefType is handled further down
        elif ct.node in (cwast.DefRec, cwast.DefType):
            continue
        else:
            new_ct = tc.MaybeGetReplacementType(ct)
            if not new_ct:
                continue
        ct.LinkReplacementType(new_ct)
    # Note: the DefType can violate topplogical ordering
    # with respect to the underlying type in the presence of generic modules.
    # So we handle it in a sepatate loop
    # (For the same reason we use two phase for creating a wrapped type.)
    for ct in tc.topo_order[:]:
        if ct.node is cwast.DefType:
            ut = ct.underlying_type()
            if ut.node not in (cwast.DefRec, cwast.DefType):
                new_ct = tc.MaybeGetReplacementType(ut)
                if new_ct:
                    ct.children[0] = new_ct
    return out


def _MakeValRecForSpan(pointer, length, span_rec: cwast.CanonType, srcloc) -> cwast.ValCompound:

    pointer_field, length_field = span_rec.ast_node.fields
    return canonicalize.MakeValCompound(span_rec,
                                        [(pointer_field.x_type, pointer),
                                         (length_field.x_type, length)], srcloc)


def FunReplaceSpanCastWithSpanVal(node, tc: type_corpus.TypeCorpus):
    """Eliminate Array to Span casts. """
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def replacer(node, _parent):
        nonlocal tc, uint_type
        if isinstance(node, cwast.ExprAs):
            if (node.x_type != node.expr.x_type and
                node.x_type.is_span() and
                    node.expr.x_type.is_vec()):
                return canonicalize.MakeValSpanFromArray(
                    node.expr, node.x_type, tc, uint_type)
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)


def ReplaceSpans(node):
    """
    Replaces all span<X> expressions with rec named xtuple_span<X>
    (cast to spans are eliminated by ReplaceExplicitSpanCast)
    This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

    Complications:
     TODO: see unused _ConvertMutSpanValRecToSpanValRec helper
     `span<u8> = span-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node):
        if isinstance(node, cwast.ExprFront):
            cont_ct = node.container.x_type
            if cont_ct.is_rec():
                # get the pointer field from the rec that now represents the span
                # because of the post-order traversal, node.container has already been processed
                assert cont_ct.original_type.is_span()
                pointer_field = cont_ct.get_rec_field(0)
                return canonicalize.MakeExprField(node.container,  pointer_field, node.x_srcloc)

        # len of array is constant and should have already been eliminated
        elif isinstance(node, cwast.ExprLen):
            cont_ct = node.container.x_type
            if cont_ct.is_rec():
                # get the length field from the rec that now represents the span
                # because of the post-order traversal, node.container has already been processed
                assert cont_ct.original_type.is_span()
                length_field = cont_ct.get_rec_field(1)
                return canonicalize.MakeExprField(node.container, length_field, node.x_srcloc)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            rec_ct = node.x_type.replacement_type
            if rec_ct is not None:
                if isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.DefFun,
                                     #
                                     cwast.Expr3, cwast.ExprAddrOf, cwast.ExprCall,
                                     cwast.ExprDeref, cwast.ExprField, cwast.ExprNarrow,
                                     cwast.ExprStmt, cwast.ExprUnionUntagged, cwast.ExprUnwrap,
                                     cwast.ExprWiden,
                                     #
                                     cwast.FunParam, cwast.Id, cwast.RecField, cwast.TypeAuto,
                                     #
                                     cwast.ValAuto, cwast.ValPoint, cwast.ValCompound)):
                    typify.NodeChangeType(node, rec_ct)
                    return None
                elif isinstance(node, cwast.ValSpan):
                    return _MakeValRecForSpan(node.pointer, node.expr_size, rec_ct, node.x_srcloc)

                cwast.CompilerError(
                    node.x_srcloc, "do not know how to convert span related node " +
                    f"[{rec_ct.name}]: {type(node)} of type {node.x_type}")
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
