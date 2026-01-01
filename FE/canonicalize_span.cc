
#include "FE/canonicalize_span.h"

#include <array>

#include "FE/canonicalize.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/typify.h"
#include "Util/parse.h"

namespace cwerg::fe {

Node MakeSpanReplacementStruct(CanonType span_ct, TypeCorpus* tc) {
  std::array<NameAndType, 2> fields = {{
      NameAndType{NameNew("pointer"), tc->InsertPtrFromSpan(span_ct)},
      NameAndType{NameNew("length"), tc->get_uint_canon_type()},
  }};
  std::string name = "xtuple_";
  name += NameData(CanonType_name(span_ct));
  return MakeDefRec(NameNew(name), fields, tc);
}

void MakeAndRegisterSpanTypeReplacements(TypeCorpus* tc, NodeChain* out) {
  tc->ClearReplacementInfo();
  CanonType new_ct;
  for (CanonType ct : tc->InTopoOrder()) {
    if (CanonType_is_span(ct)) {
      Node rec = MakeSpanReplacementStruct(ct, tc);
      out->Append(rec);
      new_ct = Node_x_type(rec);
    } else {
      new_ct = tc->MaybeGetReplacementType(ct);
      if (new_ct.isnull()) {
        continue;
      }
    }
    CanonTypeLinkReplacementType(ct, new_ct);
  }
  // TODO:
  for (CanonType ct : tc->InTopoOrder()) {
    if (CanonType_is_wrapped(ct)) {
      CanonType unwrapped = CanonType_underlying_type(ct);
      new_ct = tc->MaybeGetReplacementType(unwrapped);
      if (!new_ct.isnull()) {
        CanonType_children(ct)[0] = new_ct;
      }
    }
  }
}

Node MakeValUndef(const SrcLoc& sl) {
  Node out = NodeNew(NT::ValUndef);
  NodeInitValUndef(out, kStrInvalid, sl);
  Node_x_eval(out) = kConstUndef;
  return out;
}

Node MakeValPoint(Node field_val, CanonType ct, const SrcLoc& sl) {
  Node out = NodeNew(NT::ValPoint);
  NodeInitValPoint(out, field_val, MakeValUndef(sl), kStrInvalid, sl, ct);
  Node_x_eval(out) = Node_x_eval(field_val);
  return out;
}

Node MakeValRecForSpan(Node pointer, Node length, CanonType replacement_ct,
                       const SrcLoc& sl) {
  Node field_pointer = Node_fields(CanonType_ast_node(replacement_ct));
  Node field_length = Node_next(field_pointer);

  NodeChain fields;
  fields.Append(MakeValPoint(pointer, Node_x_type(field_pointer), sl));
  fields.Append(MakeValPoint(length, Node_x_type(field_length), sl));

  Node out = NodeNew(NT::ValCompound);
  NodeInitValCompound(out, MakeTypeAuto(replacement_ct, sl), fields.First(),
                      kStrInvalid, sl, replacement_ct);
  return out;
}

void ReplaceSpans(Node mod) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprLen) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      if (CanonType_kind(rec_ct) == NT::DefRec) {
        Node def_rec = CanonType_ast_node(rec_ct);
        Node len_field = Node_next(Node_fields(def_rec));
        ASSERT(len_field.kind() == NT::RecField, "");
        const SrcLoc& sl = Node_srcloc(node);
        Node container = Node_container(node);
        NodeFree(node);
        return MakeExprField(container, len_field, sl);
      }
    }

    if (node.kind() == NT::ExprFront) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      if (CanonType_kind(rec_ct) == NT::DefRec) {
        Node def_rec = CanonType_ast_node(rec_ct);
        Node pointer_field = Node_fields(def_rec);
        ASSERT(pointer_field.kind() == NT::RecField, "");
        const SrcLoc& sl = Node_srcloc(node);
        Node container = Node_container(node);
        NodeFree(node);
        return MakeExprField(container, pointer_field, sl);
      }
    }

    if (!NodeHasField(node, NFD_X_FIELD::type)) {
      return node;
    }

    CanonType ct = Node_x_type(node);
    CanonType replacement_ct = CanonType_replacement_type(ct);
    if (replacement_ct.isnull()) {
      return node;
    }
    switch (node.kind()) {
      case NT::DefFun:
      case NT::DefGlobal:
      case NT::DefVar:
      //
      case NT::Expr3:
      case NT::ExprAddrOf:
      case NT::ExprCall:
      case NT::ExprDeref:
      case NT::ExprField:
      case NT::ExprNarrow:
      case NT::ExprStmt:
      case NT::ExprUnionUntagged:
      case NT::ExprUnwrap:
      case NT::ExprWiden:
      //
      case NT::FunParam:
      case NT::Id:
      case NT::RecField:
      case NT::TypeAuto:
      //
      case NT::ValAuto:
      case NT::ValPoint:
      case NT::ValCompound:
        NodeChangeType(node, replacement_ct);
        return node;
      case NT::ValSpan: {
        Node out = MakeValRecForSpan(Node_pointer(node), Node_expr_size(node),
                                     replacement_ct, Node_srcloc(node));
        NodeFree(node);
        return out;
      }
      default:
        ASSERT(false, "Unhandled span replacement for node kind "
                          << EnumToString(node.kind()));
        return node;
    }
  };

  MaybeReplaceAstRecursivelyPost(mod, replacer, kNodeInvalid);
}

}  // namespace cwerg::fe