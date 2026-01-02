
#include "FE/canonicalize_union.h"

#include <array>

#include "FE/canonicalize.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/typify.h"
#include "Util/parse.h"

namespace cwerg::fe {

Node MakeUnionReplacementStruct(CanonType union_ct, TypeCorpus* tc) {
  std::array<NameAndType, 2> fields = {{
      NameAndType{NameNew("tag"), tc->get_typeid_canon_type()},
      NameAndType{NameNew("union"),
                  tc->InsertUntaggedFromTaggedUnion(union_ct)},
  }};
  std::string name = "xtuple_";
  name += NameData(CanonType_name(union_ct));
  return MakeDefRec(NameNew(name), fields, tc);
}

Node MakeValRecForTaggedUnion(CanonType replacement_ct, Node tag_value,
                              Node union_value, const SrcLoc& sl) {
  Node field_tag = Node_fields(CanonType_ast_node(replacement_ct));
  Node field_union = Node_next(field_tag);
  std::array<FieldTypeAndValue, 2> fields = {{
      {Node_x_type(field_tag), tag_value},
      {Node_x_type(field_union), union_value},
  }};
  return MakeValCompound(replacement_ct, fields, sl);
}

Node MakeTypeidVal(CanonType ct, const SrcLoc& sl, CanonType typeid_ct) {
  Node out = NodeNew(NT::ValNum);
  NodeInitValNum(out, StrNew(EVAL_STR), kStrInvalid, sl, typeid_ct);
  Node_x_eval(out) = ConstNewUnsigned(CanonType_get_original_typeid(ct),
                                      CanonType_base_type_kind(typeid_ct));
  return out;
}

Node MakeValRecForWidenFromNonUnion(Node widen, CanonType dst_ct) {
  const SrcLoc& sl = Node_srcloc(widen);
  Node src = Node_expr(widen);

  Node dst_rec = CanonType_ast_node(dst_ct);
  Node dst_tag_field = Node_fields(dst_rec);
  Node dst_union_field = Node_next(dst_tag_field);
  //
  Node tag_value = MakeTypeidVal(Node_x_type(src),
                          sl, Node_x_type(dst_tag_field));
  //
  Node_x_type(widen) = Node_x_type(dst_union_field);
  ASSERT(Node_type(widen).kind() == NT::TypeAuto, "");
  Node_x_type(Node_type(widen)) = Node_x_type(dst_union_field);

  return  MakeValRecForTaggedUnion(dst_ct, tag_value, widen, sl);
}

Node MakeExprWidenBetweeUntaggedUnions(Node expr, CanonType dst_ct,
                                       const SrcLoc& sl, Const eval) {
  Node out = NodeNew(NT::ExprWiden);
  NodeInitExprWiden(out, expr, MakeTypeAuto(dst_ct, sl), kStrInvalid, sl,
                    dst_ct);
  Node_x_eval(out) = eval;
  return out;
}

Node MakeValRecForWidenFromUnion(Node widen, CanonType dst_ct) {
  const SrcLoc& sl = Node_srcloc(widen);
  Node src = Node_expr(widen);

  Node dst_rec = CanonType_ast_node(dst_ct);
  Node dst_tag_field = Node_fields(dst_rec);
  Node dst_union_field = Node_next(dst_tag_field);

  Node src_rec = CanonType_ast_node(Node_x_type(src));
  Node src_tag_field = Node_fields(src_rec);
  Node src_union_field = Node_next(src_tag_field);

  CHECK(src.kind() == NT::Id, "Support for non-ID NYI");
  Node tag_value = MakeExprField(CloneId(src), src_tag_field, sl);
  Node union_field = MakeExprField(CloneId(src), src_union_field, sl);

  Node union_value = MakeExprWidenBetweeUntaggedUnions(
      union_field, Node_x_type(dst_union_field), sl, Node_x_eval(widen));
  return MakeValRecForTaggedUnion(dst_ct, tag_value, union_value, sl);
}

void MakeAndRegisterUnionTypeReplacements(TypeCorpus* tc, NodeChain* out) {
  tc->ClearReplacementInfo();
  for (CanonType ct : tc->InTopoOrder()) {
    if (CanonType_desugared(ct)) {
      continue;
    }

    CanonType new_ct;
    if (CanonType_is_tagged_union(ct)) {
      Node rec = MakeUnionReplacementStruct(ct, tc);
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
  // Fixup DefType related types
  for (CanonType ct : tc->InTopoOrder()) {
    if (CanonType_is_wrapped(ct)) {
      CanonType unwrapped = CanonType_underlying_type(ct);
      CanonType new_ct = tc->MaybeGetReplacementType(unwrapped);
      if (!new_ct.isnull()) {
        CanonType_children(ct)[0] = new_ct;
      }
    }
  }
}

void ReplaceUnions(Node mod) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprUnionTag) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      Node def_rec = CanonType_ast_node(rec_ct);
      Node union_field = Node_next(Node_fields(def_rec));
      const SrcLoc& sl = Node_srcloc(node);
      Node container = Node_container(node);
      NodeFree(node);
      return MakeExprField(container, union_field, sl);
    }

    if (node.kind() == NT::ExprUnionUntagged) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      Node def_rec = CanonType_ast_node(rec_ct);
      Node tag_field = Node_fields(def_rec);
      const SrcLoc& sl = Node_srcloc(node);
      Node container = Node_container(node);
      NodeFree(node);
      return MakeExprField(container, tag_field, sl);
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
      case NT::ExprFront:
      case NT::ExprPointer:
      case NT::ExprStmt:
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
      case NT::ExprWiden: {
        CanonType ct_orig =
            CanonType_original_type(Node_x_type(Node_expr(node)));
        if (!ct.isnull() && CanonType_is_tagged_union(ct_orig)) {
          return MakeValRecForWidenFromUnion(node, replacement_ct);
        } else {
          return MakeValRecForWidenFromNonUnion(node, replacement_ct);
        }
      }
      case NT::ExprNarrow:
        return node;
      default:
        CHECK(false, "");
        return node;
    }
  };
  MaybeReplaceAstRecursivelyPost(mod, replacer, kNodeInvalid);
}

void ConvertTaggedNarrowToUntaggedNarrow(Node node, TypeCorpus* tc) {
  CanonType tagged_ct = Node_x_type(Node_expr(node));
  CanonType untagged_ct =
      tc->InsertUnionType(true, CanonType_children(tagged_ct));
  Node untag = NodeNew(NT::ExprUnionUntagged);
  NodeInitExprUnionUntagged(untag, Node_expr(node), kStrInvalid,
                            Node_srcloc(node), untagged_ct);
  Node_set_flag(node, BF::UNCHECKED);
  Node_expr(node) = untag;
}

void FunSimplifyTaggedExprNarrow(Node fun, TypeCorpus* tc) {
  CanonType ct_bool = tc->get_bool_canon_type();

  auto replacer = [tc, ct_bool](Node node, Node parent) -> Node {
    if (node.kind() != NT::ExprNarrow) {
      return node;
    }

    CanonType ct_src = Node_x_type(Node_expr(node));
    CanonType ct_dst = Node_x_type(node);

    ASSERT(CanonType_is_union(ct_src), "");
    if (CanonType_untagged(ct_src)) {
      return node;
    }

    if (Node_has_flag(node, BF::UNCHECKED)) {
      if (!CanonType_is_union(ct_dst)) {
        ConvertTaggedNarrowToUntaggedNarrow(node, tc);
      }
      return node;
    }
    /// CHECKED case
    NodeChain body;
    const SrcLoc& sl = Node_srcloc(node);
    Node expr = NodeNew(NT::ExprStmt);
    NodeInitExprStmt(expr, kNodeInvalid, kStrInvalid, sl, ct_dst);
    Node_expr(node) = MakeNodeCopyableWithoutRiskOfSideEffects(
        Node_expr(node), &body, /*is_lhs=*/false);
    Node at = NodeNew(NT::TypeAuto);
    NodeInitTypeAuto(at, kStrInvalid, sl, ct_dst);
    Node cond = NodeNew(NT::ExprIs);
    std::map<Node, Node> dummy1;
    std::map<Node, Node> dummy2;
    NodeInitExprIs(cond,
                   NodeCloneRecursively(Node_expr(node), &dummy1, &dummy2), at,
                   kStrInvalid, sl, ct_bool);
    if (CanonType_is_union(ct_dst)) {
      Node_set_flag(node, BF::UNCHECKED);
    } else {
      ConvertTaggedNarrowToUntaggedNarrow(node, tc);
    }
    Node trap = NodeNew(NT::StmtTrap);
    NodeInitStmtTrap(trap, kStrInvalid, sl);
    Node if_stmt = NodeNew(NT::StmtIf);
    NodeInitStmtIf(if_stmt, cond, kNodeInvalid, trap, kStrInvalid, sl);
    body.Append(if_stmt);
    Node ret = NodeNew(NT::StmtReturn);
    NodeInitStmtReturn(ret, node, kStrInvalid, sl, expr);
    body.Append(ret);
    Node_body(expr) = body.First();
    return expr;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

}  // namespace cwerg::fe
