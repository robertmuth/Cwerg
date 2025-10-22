
#include "FE/canonicalize.h"

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "Util/parse.h"

namespace cwerg::fe {
Node IdNodeFromDef(Node def_var, const SrcLoc& sl) {
  Node out = NodeNew(NT::Id);
  NodeInitId(out, Node_name(def_var), kNameInvalid, kStrInvalid, sl, def_var,
             Node_x_type(Node_initial_or_undef_or_auto(def_var)));
  // TODO: set Node_eval
  return out;
}

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
      NodeInitTypeAuto(node, Node_comment(node), Node_srcloc(node),
                       Node_x_type(node));
    } else if (Node_kind(node) == NT::TypeUnionDelta) {
      NodeFree(Node_type(node));
      NodeFree(Node_subtrahend(node));
      // Tricky: x_type stays unchanged
      NodeInitTypeAuto(node, Node_comment(node), Node_srcloc(node),
                       Node_x_type(node));
    }
  };
  VisitAstRecursivelyPost(node, visitor, kNodeInvalid);
}

Node ConvertExprIndexToPointerArithmetic(Node container, Node index, Node bound,
                                         bool mut, const SrcLoc& srcloc,
                                         CanonType elem_ct, TypeCorpus* tc) {
  CanonType ptr_ct = tc->InsertPtrType(mut, elem_ct);
  Node start_addr = NodeNew(NT::ExprFront);
  NodeInitExprFront(start_addr, container, mut ? Mask(BF::MUT) : 0, kStrInvalid,
                    srcloc, ptr_ct);
  Node expr_pointer = NodeNew(NT::ExprPointer);
  NodeInitExprPointer(expr_pointer, POINTER_EXPR_KIND::INCP, start_addr, index,
                      bound, kStrInvalid, srcloc, ptr_ct);
  return expr_pointer;
}

Node RewriteExprIndex(Node node, CanonType uint_ct, TypeCorpus* tc) {
  Node container = Node_container(node);
  CanonType container_ct = Node_x_type(container);
  CanonType elem_ct = CanonType_underlying_type(container_ct);
  const SrcLoc& sl = Node_srcloc(node);
  if (CanonType_kind(container_ct) == NT::TypeVec) {
    bool mut = IsProperLhs(container);
    Const dim = ConstNewUnsigned(size_t(CanonType_dim(container_ct)),
                                 CanonType_base_type_kind(uint_ct));
    Node bound = NodeNew(NT::ValNum);
    NodeInitValNum(bound, StrNew(EVAL_STR), Node_comment(node),
                   Node_srcloc(node), uint_ct);
    Node_x_eval(bound) = dim;
    Node pinc = ConvertExprIndexToPointerArithmetic(
        container, Node_expr(node), bound, mut, sl, elem_ct, tc);
    Node deref = NodeNew(NT::ExprDeref);
    NodeInitExprDeref(deref, pinc, kStrInvalid, sl, elem_ct);
    Node_x_eval(deref) = Node_x_eval(node);
    // TODO: reuse node for deref?
    NodeFree(node);
    return deref;
  } else {
    ASSERT(CanonType_kind(container_ct) == NT::TypeSpan, "");
    bool mut = CanonType_mut(container_ct);
    if (Node_kind(container) == NT::Id) {
      std::map<Node, Node> dummy1;
      std::map<Node, Node> dummy2;
      Node bound = NodeNew(NT::ExprLen);
      NodeInitExprLen(bound, NodeCloneRecursively(container, &dummy1, &dummy2),
                      kStrInvalid, sl, uint_ct);
      // TODO
      // Node_x_eval = ...
      Node pinc = ConvertExprIndexToPointerArithmetic(
          container, Node_expr_index(node), bound, mut, sl, elem_ct, tc);
      Node deref = NodeNew(NT::ExprDeref);
      NodeInitExprDeref(deref, pinc, kStrInvalid, sl, elem_ct);
      Node_x_eval(deref) = Node_x_eval(node);
      // TODO: reuse node for deref?
      NodeFree(node);
      return deref;
    } else {
      // materialize the container to avoid evaluating it twice
      Node at = NodeNew(NT::TypeAuto);
      NodeInitTypeAuto(at, kStrInvalid, sl, container_ct);
      Node new_var = NodeNew(NT::DefVar);
      NodeInitDefVar(new_var, NameNew("val_span_tmp"), at, Node_container(node),
                     0, kStrInvalid, sl, container_ct);
      Node bound = NodeNew(NT::ExprLen);
      NodeInitExprLen(bound, IdNodeFromDef(new_var, sl), kStrInvalid, sl,
                      uint_ct);
      Node pinc = ConvertExprIndexToPointerArithmetic(
          IdNodeFromDef(new_var, sl), Node_expr_index(node), bound, mut, sl,
          elem_ct, tc);
      Node expr_stmt = NodeNew(NT::ExprStmt);
      NodeInitExprStmt(expr_stmt, new_var, kStrInvalid, sl, Node_x_type(pinc));
      Node stmt_ret = NodeNew(NT::StmtReturn);
      NodeInitStmtReturn(stmt_ret, pinc, kStrInvalid, sl, expr_stmt);
      Node_next(new_var) = stmt_ret;
      Node deref = NodeNew(NT::ExprDeref);
      NodeInitExprDeref(deref, expr_stmt, kStrInvalid, sl, elem_ct);
      Node_x_eval(deref) = Node_x_eval(node);
      NodeFree(node);
      return deref;
    }
  }
}

void FunReplaceExprIndex(Node node, TypeCorpus* tc) {
  CanonType uint_ct = tc->get_uint_canon_type();
  auto visitor = [&](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprIndex) {
      return RewriteExprIndex(node, uint_ct, tc);
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(node, visitor, kNodeInvalid);
}

void FunReplaceConstExpr(Node node, const TypeCorpus& tc) {
  auto replacer = [tc](Node node, Node parent) -> Node {
    if (!NodeHasField(node, NFD_X_FIELD::eval)) {
      return node;
    }

    NT kind = node.kind();
    Const val = Node_x_eval(node);

    if (kind == NT::ValNum || kind == NT::EnumVal || kind == NT::ValUndef) {
      ASSERT(val != kConstInvalid, "");
      return node;
    }

    if (kind == NT::ValAuto) {
      ASSERT(val != kConstInvalid, "");
    }

    if (val == kConstInvalid || val == kConstUndef) {
      return node;
    }

    if (!IsNumber(val.kind())) {
      return node;
    }

    if (kind == NT::DefVar || kind == NT::DefGlobal || kind == NT::ValPoint ||
        kind == NT::ValCompound) {
      return node;
    }
    CanonType ct = CanonType_get_unwrapped(Node_x_type(node));

    if (CanonType_is_base_type(ct)) {
      ct = Node_x_type(node);
    } else {
      CanonType val_ct = tc.get_base_canon_type(val.kind());
      ASSERT(CanonType_is_union(ct) && CanonType_union_contains(ct, val_ct), "");
      ct = val_ct;
    }
    Node new_node = NodeNew(NT::ValNum);
    NodeInitValNum(new_node, StrNew(EVAL_STR), Node_comment(node),
                   Node_srcloc(node), ct);
    Node_x_eval(new_node) = val;
    NodeFree(node);
    return new_node;
  };
  MaybeReplaceAstRecursively(node, replacer);
}

}  // namespace cwerg::fe