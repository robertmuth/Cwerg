"""Canonicalizer For Spans

"""


from typing import Optional

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
SLICE_FIELD_POINTER = "pointer"
SLICE_FIELD_LENGTH = "length"


def _MakeSpanReplacementStruct(span_type: cwast.CanonType,
                               tc: type_corpus.TypeCorpus) -> cwast.DefRec:
    fields = [
        (SLICE_FIELD_POINTER, tc.insert_ptr_type(
            span_type.mut, span_type.underlying_span_type())),
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
    def add_replacement(old_ct: cwast.CanonType, new_ct: cwast.CanonType):
        assert old_ct.replacement_type is None
        old_ct.replacement_type = new_ct
        new_ct.original_type = old_ct

    for ct in tc.topo_order[:]:
        if ct.replacement_type:
            continue
        if ct.is_span():
            # maybe add the DefRec to the module with generated code
            rec = _MakeSpanReplacementStruct(ct, tc)
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
        elif ct.is_array():
            replacement = ct.underlying_array_type().replacement_type
            if replacement is not None:
                add_replacement(ct,  tc.insert_array_type(
                    ct.array_dim(), replacement))


def _MakeIdForDefRec(def_rec: cwast.CanonType, srcloc) -> cwast.Id:
    return cwast.Id.Make(def_rec.ast_node.name, x_symbol=def_rec.ast_node, x_type=def_rec, x_srcloc=srcloc)


def _MakeValRecForSpan(pointer, length, span_rec: cwast.CanonType, srcloc) -> cwast.ValCompound:
    pointer_field, length_field = span_rec.ast_node.fields
    inits = [cwast.PointVal(pointer, cwast.ValAuto(x_srcloc=srcloc),
                            x_type=pointer_field.x_type,
                            x_srcloc=srcloc, x_value=pointer.x_value),
             cwast.PointVal(length, cwast.ValAuto(x_srcloc=srcloc),
                            x_type=length_field.x_type,
                            x_srcloc=srcloc, x_value=length.x_value)]
    return cwast.ValCompound(_MakeIdForDefRec(span_rec, srcloc), inits, x_srcloc=srcloc, x_type=span_rec)



def ReplaceExplicitSpanCast(node, tc: type_corpus.TypeCorpus):
    """Eliminate Array to Span casts. """
    uint_type: cwast.CanonType = tc.get_uint_canon_type()

    def replacer(node, _parent, _field):
        nonlocal tc, uint_type
        if isinstance(node, cwast.ExprAs):
            if (node.x_type != node.expr.x_type and
                node.x_type.is_span() and
                    node.expr.x_type.is_array()):
                return canonicalize.MakeValSpanFromArray(
                    node.expr, node.x_type, tc, uint_type)
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)


def ReplaceSpans(node):
    """
    Replaces all span<X> expressions with rec named xtuple_span<X>
    (cast to spans are eliminated by ReplaceExplicitSpanCast)
    This should elminate all of ExprSizeOf and ExprOffsetOf as a side-effect

    Complications:
     TODO: see unused _ConvertMutSpanValRecToSpanValRec helper
     `span<u8> = span-mut<u8>` is ok before the change to structs but not afterwards
    """
    def replacer(node, _parent, field):

        # len of array is constant and should have already been eliminated
        if isinstance(node, cwast.ExprLen):
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                assert len(def_rec.ast_node.fields) == 2
                field = def_rec.ast_node.fields[1]
                return cwast.ExprField(node.container, SLICE_FIELD_LENGTH,
                                       x_srcloc=node.x_srcloc, x_type=field.x_type,
                                       x_field=field)
        elif isinstance(node, cwast.ExprFront):
            def_rec = node.container.x_type
            if def_rec.is_rec():
                assert def_rec.original_type is not None
                assert def_rec.original_type.is_span()
                assert len(def_rec.ast_node.fields) == 2
                field = def_rec.ast_node.fields[0]
                return cwast.ExprField(node.container, SLICE_FIELD_POINTER,
                                       x_srcloc=node.x_srcloc, x_type=field.x_type,
                                       x_field=field)

        if cwast.NF.TYPE_ANNOTATED in node.FLAGS:

            def_rec = node.x_type.replacement_type
            if def_rec is not None:
                if isinstance(node, (cwast.TypeAuto, cwast.DefType, cwast.TypePtr,
                                     cwast.ExprStmt, cwast.DefFun, cwast.TypeFun,
                                     cwast.FunParam, cwast.RecField, cwast.ExprField,
                                     cwast.Expr3, cwast.ExprDeref, cwast.ExprNarrow,
                                     cwast.ExprAddrOf, cwast.ExprCall,
                                     cwast.ValAuto, cwast.TypeVec,
                                     cwast.PointVal, cwast.ValCompound)):
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, cwast.TypeSpan):
                    return _MakeIdForDefRec(def_rec, node.x_srcloc)
                elif isinstance(node, cwast.ValSpan):
                    return _MakeValRecForSpan(node.pointer, node.expr_size, def_rec, node.x_srcloc)
                elif isinstance(node, cwast.Id):
                    sym = node.x_symbol
                    # TODO
                    # This needs a lot of work also what about field references to
                    # rewritten fields
                    if isinstance(sym, cwast.TypeSpan):
                        symbolize.AnnotateNodeSymbol(node, def_rec)
                    typify.UpdateNodeType(node, def_rec)
                    return None
                elif isinstance(node, (cwast.ExprAs, cwast.ExprUnwrap)):
                    ct_src = node.expr.x_type
                    ct_dst = node.x_type
                    if ct_src.is_wrapped() and ct_src.underlying_wrapped_type() == ct_dst:
                        typify.UpdateNodeType(node, def_rec)
                        return None

                cwast.CompilerError(
                    node.x_srcloc, "do not know how to convert span related node " +
                    f"[{def_rec.name}]: {type(node)} of type {node.x_type}")
        return None

    cwast.MaybeReplaceAstRecursivelyPost(node, replacer)
