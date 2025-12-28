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

    Note: recs containing span fields are not thought of as directly involving spans
    TODO: what about sum types?
    """
    tc.ClearReplacementInfo()
    # Go through the type table in topological order.
    # Note: we add new types to the map while iterating over it so we take
    # a snapshot first
    out = []
    for ct in tc.topo_order[:]:
        if ct.is_span():
            rec = _MakeSpanReplacementStruct(ct, tc)
            out.append(rec)
            new_ct = rec.x_type
        else:
            new_ct = tc.MaybeGetReplacementType(ct)
            if not new_ct:
                continue
        ct.LinkReplacementType(new_ct)
    return out


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc) -> cwast.Id:
    return cwast.Id(def_rec.ast_node.name, None, x_symbol=def_rec.ast_node, x_type=def_rec, x_srcloc=srcloc)


def _MakeValPoint(val, ct, sl) -> cwast.ValPoint:
    return cwast.ValPoint(val, cwast.ValUndef(x_srcloc=sl, x_eval=eval.VAL_UNDEF),
                          x_type=ct, x_srcloc=sl, x_eval=val.x_eval)


def _MakeValRecForSpan(pointer, length, span_rec: cwast.CanonType, srcloc) -> cwast.ValCompound:
    pointer_field, length_field = span_rec.ast_node.fields
    inits = [_MakeValPoint(pointer, pointer_field.x_type, srcloc),
             _MakeValPoint(length, length_field.x_type, srcloc)]
    return cwast.ValCompound(_MakeIdForDefRec(span_rec, srcloc), inits, x_srcloc=srcloc, x_type=span_rec)


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
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                pointer_field = def_rec.ast_node.fields[0]
                return canonicalize.MakeExprField(node.container,  pointer_field, node.x_srcloc)

        # len of array is constant and should have already been eliminated
        elif isinstance(node, cwast.ExprLen):
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                len_field = def_rec.ast_node.fields[1]
                return canonicalize.MakeExprField(node.container, len_field, node.x_srcloc)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            def_rec = node.x_type.replacement_type
            if def_rec is not None:
                if isinstance(node, (cwast.DefVar, cwast.DefGlobal, cwast.DefFun,  cwast.DefType,
                                     #
                                     cwast.Expr3, cwast.ExprAddrOf, cwast.ExprCall,
                                     cwast.ExprDeref, cwast.ExprField, cwast.ExprNarrow,
                                     cwast.ExprStmt, cwast.ExprUnionUntagged, cwast.ExprUnwrap,
                                     cwast.ExprWiden,
                                     #
                                     cwast.FunParam, cwast.Id, cwast.RecField, cwast.TypeAuto,
                                     #
                                     cwast.ValAuto, cwast.ValPoint, cwast.ValCompound)):
                    typify.NodeChangeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.ValSpan):
                    return _MakeValRecForSpan(node.pointer, node.expr_size, def_rec, node.x_srcloc)

                cwast.CompilerError(
                    node.x_srcloc, "do not know how to convert span related node " +
                    f"[{def_rec.name}]: {type(node)} of type {node.x_type}")
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
