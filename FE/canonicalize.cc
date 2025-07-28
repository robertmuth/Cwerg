
#include "FE/canonicalize.h"

namespace cwerg::fe {

void FunRemoveParentheses(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (Node_kind(node) == NT::ExprParen) {
      Node expr = Node_expr(node);
      NodeFree(node);
      return expr;
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunReplaceTypeOfAndTypeUnionDelta(Node node) {
  auto visitor = [](Node node, Node parent) -> void {
    if (Node_kind(node) == NT::TypeOf) {
      NodeFree(Node_expr(node));
      // Tricky: x_type stays unchanged
      NodeInitTypeAuto(node, Node_comment(node), Node_srcloc(node));
    } else if (Node_kind(node) == NT::TypeUnionDelta) {
      NodeFree(Node_type(node));
      NodeFree(Node_subtrahend(node));
      // Tricky: x_type stays unchanged
      NodeInitTypeAuto(node, Node_comment(node), Node_srcloc(node));
    }
  };
  VisitAstRecursivelyPost(node, visitor, kNodeInvalid);
}

#if 0
void ConvertExprIndex(Node node, CanonType uint_ct, TypeCorpus* tc) {
  CanonType container_ct = Node_x_type(Node_container(node));
  Node bound = kNodeInvalid;
  bool mut = false;
  if (CanonType_kind(container_ct) == NT::TypeVec) {

  } else {
   ASSERT(CanonType_kind(container_ct) == NT::TypeSpan, "");
  }
}

void FunReplaceExprIndex(Node node, TypeCorpus* tc) {
  CanonType uint_ct = tc->get_uint_canon_type();
  auto visitor = [&](Node node, Node parent) -> void {
    if (node.kind() == NT::ExprIndex) {
      ConvertExprIndex(node, uint_ct, tc);
    }
  };
  VisitAstRecursivelyPost(node, visitor, kNodeInvalid);
}
#endif

}  // namespace cwerg::fe