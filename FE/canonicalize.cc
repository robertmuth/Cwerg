
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

}  // namespace cwerg::fe