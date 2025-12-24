"""Canonicalizer For Spans

"""


from FE import canonicalize
from FE import cwast
from FE import type_corpus
from FE import typify
from FE import symbolize
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
    return canonicalize.MakeDefRec(f"xtuple_{span_type.name}", fields, tc, cwast.SRCLOC_GENERATED)


def MakeAndRegisterSpanTypeReplacements(mod_gen: cwast.DefMod, tc: type_corpus.TypeCorpus):
    """For all types directly involving spans, produce a replacement type
    and return the map from one the other

    Note: recs containing span fields are not thought of as directly involving spans
    TODO: what about sum types?
    """

    # Go through the type table in topological order.
    # Note: we add new types to the map while iterating over it so we take
    # a snapshot first
    for ct in tc.topo_order[:]:
        assert ct.replacement_type is None

        if ct.is_span():
            rec = _MakeSpanReplacementStruct(ct, tc)
            mod_gen.body_mod.append(rec)
            new_ct = rec.x_type
        else:
            new_ct = tc.MaybeGetReplacementType(ct)
            if not new_ct:
                continue
        ct.replacement_type = new_ct
        new_ct.original_type = ct


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc) -> cwast.Id:
    return cwast.Id(def_rec.ast_node.name, None, x_symbol=def_rec.ast_node, x_type=def_rec, x_srcloc=srcloc)


def _MakeValRecForSpan(pointer, length, span_rec: cwast.CanonType, srcloc) -> cwast.ValCompound:
    pointer_field, length_field = span_rec.ast_node.fields
    inits = [cwast.ValPoint(pointer, cwast.ValUndef(x_srcloc=srcloc, x_eval=eval.VAL_UNDEF),
                            x_type=pointer_field.x_type,
                            x_srcloc=srcloc, x_eval=pointer.x_eval),
             cwast.ValPoint(length, cwast.ValUndef(x_srcloc=srcloc, x_eval=eval.VAL_UNDEF),
                            x_type=length_field.x_type,
                            x_srcloc=srcloc, x_eval=length.x_eval)]
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
    def replacer(node, _parent):

        # len of array is constant and should have already been eliminated
        if isinstance(node, cwast.ExprLen):
            sl = node.x_srcloc
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                _, len_field = def_rec.ast_node.fields
                return cwast.ExprField(node.container, canonicalize.IdNodeFromRecField(len_field, sl),
                                       x_srcloc=sl, x_type=len_field.x_type)
        elif isinstance(node, cwast.ExprFront):
            sl = node.x_srcloc
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                pointer_field, _ = def_rec.ast_node.fields
                return cwast.ExprField(node.container,  canonicalize.IdNodeFromRecField(pointer_field, sl),
                                       x_srcloc=sl, x_type=pointer_field.x_type)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:
            def_rec = node.x_type.replacement_type
            if def_rec is not None:
                if isinstance(node, (cwast.Id, cwast.TypeAuto, cwast.DefType,
                                     cwast.ExprWiden, cwast.ExprUnionUntagged,
                                     cwast.ExprStmt, cwast.DefFun,
                                     cwast.FunParam, cwast.DefVar, cwast.DefGlobal,
                                     cwast.RecField, cwast.ExprField,
                                     cwast.Expr3, cwast.ExprDeref, cwast.ExprNarrow,
                                     cwast.ExprAddrOf, cwast.ExprCall,
                                     cwast.ValAuto,
                                     cwast.ValPoint, cwast.ValCompound)):
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, (cwast.ExprUnwrap)):
                    ct_src = node.expr.x_type
                    ct_dst = node.x_type
                    assert ct_src.is_wrapped() and ct_src.underlying_type() == ct_dst
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.ValSpan):
                    return _MakeValRecForSpan(node.pointer, node.expr_size, def_rec, node.x_srcloc)

                cwast.CompilerError(
                    node.x_srcloc, "do not know how to convert span related node " +
                    f"[{def_rec.name}]: {type(node)} of type {node.x_type}")
        return None

    cwast.MaybeReplaceAstRecursivelyWithParentPost(node, replacer)
