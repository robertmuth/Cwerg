
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

NodeChain MakeAndRegisterUnionTypeReplacements(TypeCorpus* tc) {
  NodeChain out;
  tc->ClearReplacementInfo();
  for (CanonType ct : tc->InTopoOrder()) {
    CanonType new_ct;
    if (CanonType_is_union(ct) && !CanonType_untagged(ct)) {
      Node rec = MakeUnionReplacementStruct(ct, tc);
      out.Append(rec);
      new_ct = Node_x_type(rec);
    } else {
      new_ct = tc->MaybeGetReplacementType(ct);
      if (new_ct.isnull()) {
        continue;
      }
    }
    CanonTypeLinkReplacementType(ct, new_ct);
  }
  return out;
}

void ReplaceUnions(Node mod) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprUnionTag) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      Node def_rec = CanonType_ast_node(rec_ct);
      Node union_field = Node_next(Node_fields(def_rec));
      return MakeExprField(Node_container(node), union_field,
                           Node_srcloc(node));
    }

    if (node.kind() == NT::ExprUnionUntagged) {
      CanonType rec_ct = Node_x_type(Node_container(node));
      Node def_rec = CanonType_ast_node(rec_ct);
      Node tag_field = Node_fields(def_rec);
      return MakeExprField(Node_container(node), tag_field, Node_srcloc(node));
    }
    // TODO

    return node;
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
