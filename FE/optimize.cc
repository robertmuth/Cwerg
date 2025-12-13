#include "FE/optimize.h"

namespace cwerg::fe {

void FunPeepholeOpts(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprDeref &&
        Node_expr(node).kind() == NT::ExprAddrOf) {
      Node out = Node_expr(Node_expr(node));
      NodeFree(Node_expr(node));
      NodeFree(node);
      return out;
    }
    if (node.kind() == NT::ExprAddrOf &&
        Node_expr_lhs(node).kind() == NT::ExprDeref) {
      Node out = Node_expr_lhs(Node_expr_lhs(node));
      NodeFree(Node_expr_lhs(node));
      NodeFree(node);
      return out;
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunRemoveSimpleExprStmts(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::StmtReturn &&
        Node_expr_ret(node).kind() == NT::ExprStmt) {
      std::map<Node, Node> dummy1;
      std::map<Node, Node> target_map;
      target_map[Node_expr_ret(node)] = Node_x_target(node);
      Node ret_expr = Node_expr_ret(node);
      UpdateSymbolAndTargetLinks(ret_expr, &dummy1, &target_map);

      Node body = Node_body(ret_expr);
      NodeFree(ret_expr);
      NodeFree(node);
      return body;
    }
    if (node.kind() == NT::ExprStmt) {
      Node first = Node_body(node);
      if (first.kind() == NT::StmtReturn) {
        ASSERT(Node_next(first).isnull(), "");
        Node out = Node_expr_ret(first);
        NodeFree(first);
        NodeFree(node);
        return out;
      }
    }

    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunOptimize(Node fun) {
  FunPeepholeOpts(fun);
  FunRemoveSimpleExprStmts(fun);
}

}  // namespace cwerg::fe