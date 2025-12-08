
#include "FE/canonicalize_union.h"

#include "FE/canonicalize.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "Util/parse.h"

namespace cwerg::fe {

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
