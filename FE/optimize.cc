#include "FE/optimize.h"

#include <set>

namespace cwerg::fe {

bool MayHaveSideEffects(Node n) {
  switch (Node_kind(n)) {
    case NT::ExprCall:
    case NT::ExprStmt:
      return true;
    case NT::Id:
    case NT::ValAuto:
    case NT::ValUndef:
    case NT::ValVoid:
    case NT::ValNum:
      return false;
    case NT::ExprAddrOf:
      return MayHaveSideEffects(Node_expr_lhs(n));
    case NT::ExprPointer:
      return MayHaveSideEffects(Node_expr1(n)) ||
             MayHaveSideEffects(Node_expr2(n)) ||
             MayHaveSideEffects(Node_expr_bound_or_undef(n));
    case NT::ExprFront:
    case NT::ExprField:
    case NT::ExprLen:
      return MayHaveSideEffects(Node_container(n));
    case NT::Expr1:
    case NT::ExprDeref:
    case NT::ExprAs:
    case NT::ExprBitCast:
    case NT::ExprWiden:
    case NT::ExprNarrow:
    case NT::ExprUnionUntagged:
    case NT::ExprUnwrap:
      return MayHaveSideEffects(Node_expr(n));
    case NT::Expr2:
      return MayHaveSideEffects(Node_expr1(n)) ||
             MayHaveSideEffects(Node_expr2(n));
    case NT::Expr3:
      return MayHaveSideEffects(Node_cond(n)) ||
             MayHaveSideEffects(Node_expr_t(n)) ||
             MayHaveSideEffects(Node_expr_f(n));
    case NT::ValCompound: {
      for (Node item = Node_inits(n); !item.isnull(); item = Node_next(item)) {
        if (MayHaveSideEffects(Node_point_or_undef(item)) ||
            MayHaveSideEffects(Node_value_or_undef(item))) {
          return true;
        }
      }
      return false;
    }
    default:
      CHECK(false, "unexpected " << EnumToString(n.kind()));
      return false;
  }
}

void FunRemoveUnusedDefVar(Node fun) {
  std::set<Node> used;
  auto visitor = [&used](Node node, Node parent) {
    if (Node_kind(node) == NT::Id) {
      used.insert(Node_x_symbol(node));
    }
    return false;
  };

  VisitAstRecursivelyPre(fun, visitor, kNodeInvalid);

  auto replacer = [&used](Node node, Node parent) -> Node {
    if (Node_kind(node) == NT::DefVar) {
      if (used.find(node) == used.end() &&
          !MayHaveSideEffects(Node_initial_or_undef_or_auto(node))) {
        NodeFreeRecursively(node);
        return kNodeInvalid;
      }
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunPeepholeOpts(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
#if 1
    if (node.kind() == NT::ExprDeref &&
        Node_expr(node).kind() == NT::ExprAddrOf) {
      Node out = Node_expr_lhs(Node_expr(node));
      NodeFree(Node_expr(node));
      NodeFree(node);
      return out;
    }
#endif
#if 0
    if (node.kind() == NT::ExprAddrOf &&
        Node_expr_lhs(node).kind() == NT::ExprDeref) {
      Node out = Node_expr(Node_expr_lhs(node));
      NodeFree(Node_expr_lhs(node));
      NodeFree(node);
      return out;
    }
#endif
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
  FunRemoveUnusedDefVar(fun);
  // FunPeepholeOpts(fun);
  FunRemoveSimpleExprStmts(fun);
}

}  // namespace cwerg::fe