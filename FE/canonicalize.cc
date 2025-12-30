
#include "FE/canonicalize.h"

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "Util/parse.h"

namespace cwerg::fe {

Node CloneId(Node id) {
  Node out = NodeNew(NT::Id);
  NodeInitId(out, Node_name(id), kNameInvalid, kStrInvalid, Node_srcloc(id),
             Node_x_symbol(id), Node_x_type(id));
  // TODO: set Node_eval ?
  return out;
}



Node MakeExprField(Node container, Node rec_field, const SrcLoc& sl) {
    Node field = NodeNew(NT::Id);
  NodeInitId(field, Node_name(rec_field), kNameInvalid, kStrInvalid, sl,
             Node_x_symbol(rec_field), Node_x_type(rec_field));
  Node out = NodeNew(NT::ExprField);
  NodeInitExprField(out, container, field, kStrInvalid, sl, Node_x_type(rec_field));
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
        container, Node_expr_index(node), bound, mut, sl, elem_ct, tc);
    NodeFree(node);  // Recursive is not necessary since we are
                     // re-using expr_index and container
    Node deref = NodeNew(NT::ExprDeref);
    NodeInitExprDeref(deref, pinc, kStrInvalid, sl, elem_ct);
    Node_x_eval(deref) = Node_x_eval(node);
    // TODO: reuse node for deref?
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
      Node at = MakeTypeAuto(container_ct, sl);
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
  auto replacer = [&](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprIndex) {
      return RewriteExprIndex(node, uint_ct, tc);
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(node, replacer, kNodeInvalid);
}

void FunReplaceConstExpr(Node node, const TypeCorpus& tc) {
  auto replacer = [tc](Node node, Node parent) -> Node {
    if (!NodeHasField(node, NFD_X_FIELD::eval)) {
      return node;
    }

    NT kind = node.kind();
    Const val = Node_x_eval(node);

    if (kind == NT::ValNum || kind == NT::EnumVal || kind == NT::ValUndef) {
      ASSERT(val != kConstInvalid || kind == NT::ValUndef,
             "expected valid x_eval for " << EnumToString(kind));
      return node;
    }

    if (kind == NT::ValAuto) {
      ASSERT(val != kConstInvalid, "bad ValAuto at " << Node_srcloc(node));
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

    if (parent.kind() == NT::ExprAddrOf && Node_expr_lhs(parent) == node) {
      return node;
    }

    CanonType ct = CanonType_get_unwrapped(Node_x_type(node));

    if (CanonType_is_base_type(ct)) {
      ct = Node_x_type(node);
    } else {
      CanonType val_ct = tc.get_base_canon_type(val.kind());
      ASSERT(CanonType_is_union(ct) && CanonType_union_contains(ct, val_ct),
             "");
      ct = val_ct;
    }
    Node new_node = NodeNew(NT::ValNum);
    NodeInitValNum(new_node, StrNew(EVAL_STR), Node_comment(node),
                   Node_srcloc(node), ct);
    Node_x_eval(new_node) = val;
    NodeFreeRecursively(node);
    return new_node;
  };
  MaybeReplaceAstRecursively(node, replacer);
}

CanonType GetFrontTypeForVec(CanonType ct, TypeCorpus* tc) {
  return tc->InsertPtrType(CanonType_mut(ct), CanonType_underlying_type(ct));
}

Node MakeValSpanFromArray(Node node, CanonType expected_ct, CanonType uint_ct,
                          TypeCorpus* tc) {
  ASSERT(CanonType_is_vec(Node_x_type(node)) && CanonType_is_span(expected_ct),
         "");
  SizeOrDim dim = CanonType_dim(Node_x_type(node));
  const SrcLoc& sl = Node_srcloc(node);
  CanonType ptr_ct = GetFrontTypeForVec(expected_ct, tc);
  Node sym = node.kind() == NT::Id ? Node_x_symbol(node) : kNodeInvalid;
  Node front = NodeNew(NT::ExprFront);
  NodeInitExprFront(front, node, CanonType_mut(expected_ct) ? Mask(BF::MUT) : 0,
                    kStrInvalid, sl, ptr_ct);
  Node_x_eval(front) = sym == kNodeInvalid
                           ? kConstInvalid
                           : ConstNewSymbolAddr(Node_x_symbol(node));

  Node length = NodeNew(NT::ValNum);
  NodeInitValNum(length, StrNew(EVAL_STR), kStrInvalid, sl, uint_ct);
  Node_x_eval(length) =
      ConstNewUnsigned(dim, CanonType_base_type_kind(uint_ct));
  //
  Node span = NodeNew(NT::ValSpan);
  NodeInitValSpan(span, front, length, kStrInvalid, sl, expected_ct);
  Const v_span = ConstNewSpan({sym, dim, kConstInvalid});
  Node_x_eval(span) = v_span;
  return span;
}

Node MaybeMakeImplicitConversionExplicit(Node orig_node, CanonType expected_ct,
                                         CanonType uint_ct, TypeCorpus* tc) {
  if (orig_node.kind() == NT::ValUndef) {
    return orig_node;
  }
  CanonType actual_ct = Node_x_type(orig_node);
  if (actual_ct == expected_ct || IsDropMutConversion(actual_ct, expected_ct)) {
    return orig_node;
  }
  if (CanonType_is_vec(Node_x_type(orig_node)) &&
      CanonType_is_span(expected_ct)) {
    return MakeValSpanFromArray(orig_node, expected_ct, uint_ct, tc);
  } else {
    ASSERT(CanonType_is_union(expected_ct),
           "expected union type for " << EnumToString(orig_node.kind())
                                      << " but got " << expected_ct);
    Node sum_type = MakeTypeAuto(expected_ct, Node_srcloc(orig_node));

    Node widen = NodeNew(NT::ExprWiden);
    NodeInitExprWiden(widen, orig_node, sum_type, kStrInvalid,
                      Node_srcloc(orig_node), expected_ct);
    Node_x_eval(widen) = Node_x_eval(orig_node);
    return widen;
  }
}

void FunMakeImplicitConversionsExplicit(Node node, TypeCorpus* tc) {
  CanonType uint_ct = tc->get_uint_canon_type();

  auto visitor = [tc, uint_ct](Node node, Node parent) -> void {
    switch (node.kind()) {
      case NT::ValPoint:
        Node_value_or_undef(node) = MaybeMakeImplicitConversionExplicit(
            Node_value_or_undef(node), Node_x_type(node), uint_ct, tc);
        break;
      case NT::DefVar:
      case NT::DefGlobal:
        Node_initial_or_undef_or_auto(node) =
            MaybeMakeImplicitConversionExplicit(
                Node_initial_or_undef_or_auto(node),
                Node_x_type(Node_type_or_auto(node)), uint_ct, tc);
        break;
      case NT::ExprCall: {
        CanonType fun_sig = Node_x_type(Node_callee(node));
        NodeChain new_args;
        Node arg = Node_args(node);
        if (arg.isnull()) {
          break;
        }
        int arg_pos = 0;
        do {
          Node next = Node_next(arg);
          Node_next(arg) = kNodeInvalid;
          Node new_arg = MaybeMakeImplicitConversionExplicit(
              arg, CanonType_children(fun_sig)[arg_pos], uint_ct, tc);
          new_args.Append(new_arg);
          arg = next;
          ++arg_pos;
        } while (!arg.isnull());
        Node_args(node) = new_args.First();
      } break;
      case NT::ExprWrap: {
        CanonType ct = Node_x_type(node);
        if (!CanonType_is_enum(ct)) {
          ASSERT(CanonType_is_wrapped(ct), "");
          Node_expr(node) = MaybeMakeImplicitConversionExplicit(
              Node_expr(node), CanonType_underlying_type(ct), uint_ct, tc);
        }
      } break;
      case NT::StmtReturn: {
        Node target = Node_x_target(node);
        ASSERT(target.kind() == NT::DefFun || target.kind() == NT::ExprStmt,
               "");
        CanonType expected_ct = target.kind() == NT::DefFun
                                    ? Node_x_type(Node_result(target))
                                    : Node_x_type(target);

        Node_expr_ret(node) = MaybeMakeImplicitConversionExplicit(
            Node_expr_ret(node), expected_ct, uint_ct, tc);
      } break;
      case NT::StmtAssignment:
        Node_expr_rhs(node) = MaybeMakeImplicitConversionExplicit(
            Node_expr_rhs(node), Node_x_type(Node_lhs(node)), uint_ct, tc);
        break;
      default:
        return;
    }
  };
  VisitAstRecursivelyPost(node, visitor, kNodeInvalid);
}

void FunReplaceSpanCastWithSpanVal(Node fun, TypeCorpus* tc) {
  CanonType uint_ct = tc->get_uint_canon_type();

  auto replacer = [tc, uint_ct](Node node, Node parent) -> Node {
    if (node.kind() != NT::ExprAs) {
      return node;
    }
    CanonType ct_src = Node_x_type(Node_expr(node));
    CanonType ct_dst = Node_x_type(node);
    if (ct_src == ct_dst || !CanonType_is_vec(ct_src) ||
        !CanonType_is_span(ct_dst)) {
      return node;
    }
    Node out = MakeValSpanFromArray(Node_expr(node), ct_dst, uint_ct, tc);
    NodeFree(node);
    return out;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

Node MakeTagCheck(Node union_id, CanonType ct, CanonType ct_bool,
                  const SrcLoc& sl) {
  Node type = MakeTypeAuto(ct, sl);
  Node check = NodeNew(NT::ExprIs);
  NodeInitExprIs(check, union_id, type, kStrInvalid, sl, ct_bool);
  return check;
}

Node MakeUnionNarrow(Node union_id, CanonType ct, const SrcLoc& sl) {
  Node type_expr = MakeTypeAuto(ct, sl);
  Node narrow = NodeNew(NT::ExprNarrow);
  NodeInitExprNarrow(narrow, union_id, type_expr, Mask(BF::UNCHECKED),
                     kStrInvalid, sl, ct);
  return narrow;
}

Node MakeCmp(Node cmp, Node union_id, Node field, BINARY_EXPR_KIND kind) {
  ASSERT(union_id.kind() == NT::Id, "NYI " << Node_srcloc(union_id));
  CanonType ct_field = Node_x_type(field);
  CanonType ct_bool = Node_x_type(cmp);
  const SrcLoc& sl = Node_srcloc(cmp);
  Node tag_check = MakeTagCheck(union_id, ct_field, ct_bool, sl);
  if (kind == BINARY_EXPR_KIND::EQ) {
    if (CanonType_get_unwrapped_base_type_kind(ct_field) ==
        BASE_TYPE_KIND::VOID) {
      NodeFree(field);
      NodeFree(cmp);
      return tag_check;
    }
    Node_expr1(cmp) = MakeUnionNarrow(CloneId(union_id), ct_field, sl);
    Node_expr2(cmp) = field;
    //
    Node and_expr = NodeNew(NT::Expr2);
    NodeInitExpr2(and_expr, BINARY_EXPR_KIND::ANDSC, tag_check, cmp,
                  kStrInvalid, sl, ct_bool);
    return and_expr;
  } else {
    ASSERT(kind == BINARY_EXPR_KIND::NE, "");
    Node not_tag_check = NodeNew(NT::Expr1);
    NodeInitExpr1(not_tag_check, UNARY_EXPR_KIND::NOT, tag_check, kStrInvalid,
                  sl, ct_bool);
    if (CanonType_get_unwrapped_base_type_kind(ct_field) ==
        BASE_TYPE_KIND::VOID) {
      NodeFree(field);
      NodeFree(cmp);
      return not_tag_check;
    }

    Node_expr1(cmp) = MakeUnionNarrow(CloneId(union_id), ct_field, sl);
    Node_expr2(cmp) = field;
    //
    Node or_expr = NodeNew(NT::Expr2);
    NodeInitExpr2(or_expr, BINARY_EXPR_KIND::ORSC, not_tag_check, cmp,
                  kStrInvalid, sl, ct_bool);
    return or_expr;
  }
}

void FunDesugarTaggedUnionComparisons(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() != NT::Expr2) {
      return node;
    }

    BINARY_EXPR_KIND op_kind = Node_binary_expr_kind(node);

    if (op_kind != BINARY_EXPR_KIND::EQ && op_kind != BINARY_EXPR_KIND::NE) {
      return node;
    }

    Node e1 = Node_expr1(node);
    Node e2 = Node_expr2(node);
    CanonType t1 = Node_x_type(e1);
    CanonType t2 = Node_x_type(e2);
    if (CanonType_is_union(t1) && !CanonType_untagged(t1)) {
      return MakeCmp(node, e1, e2, op_kind);
    }
    if (CanonType_is_union(t2) && !CanonType_untagged(t2)) {
      return MakeCmp(node, e2, e1, op_kind);
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

bool IsNodeCopyableWithoutRiskOfSideEffects(Node node) {
  switch (node.kind()) {
    case NT::Id:
      return true;
    case NT::ExprDeref:
      return Node_expr(node).kind() == NT::Id;
    case NT::ExprField: {
      Node c = Node_container(node);
      while (true) {
        if (c.kind() == NT::Id)
          return true;
        else if (c.kind() != NT::ExprField) {
          c = Node_container(node);
        } else {
          return c.kind() == NT::ExprDeref && Node_expr(c).kind() == NT::Id;
        }
      }
    }

    default:
      return false;
  }
}

Node DefVarNew(Name name, Node init) {
  const SrcLoc& sl = Node_srcloc(init);
  CanonType ct = Node_x_type(init);
  Node at = MakeTypeAuto(ct, sl);
  Node out = NodeNew(NT::DefVar);
  NodeInitDefVar(out, name, at, init, 0, kStrInvalid, sl, ct);
  return out;
}

Node MakeNodeCopyableWithoutRiskOfSideEffects(Node lhs, NodeChain* stmts,
                                              bool is_lhs) {
  switch (lhs.kind()) {
    case NT::Id:
      return lhs;
    case NT::ExprDeref: {
      Node pointer = Node_expr(lhs);
      if (pointer.kind() == NT::Id) {
        return lhs;
      }
      Node def_node = DefVarNew(NameNew("deref_assign"), pointer);
      stmts->Append(def_node);
      Node_expr(lhs) = IdNodeFromDef(def_node, Node_srcloc(def_node));
      return lhs;
    }
    case NT::ExprField:
      Node_expr(lhs) = MakeNodeCopyableWithoutRiskOfSideEffects(
          Node_container(lhs), stmts, is_lhs);
      return lhs;
    case NT::ExprIndex:
      ASSERT(false, "UNREACHABLE");
      return kNodeInvalid;
    default: {
      ASSERT(!is_lhs, "NYI");
      Node def_node = DefVarNew(NameNew("assign"), lhs);
      stmts->Append(def_node);
      return IdNodeFromDef(def_node, Node_srcloc(def_node));
    }
  }
}

Node MakeValNumBool(bool val, const SrcLoc& sl, CanonType ct) {
  Node out = NodeNew(NT::ValNum);
  NodeInitValNum(out, StrNew(EVAL_STR), kStrInvalid, sl, ct);
  Node_x_eval(out) = ConstNewBool(val);
  return out;
}

void FunDesugarExprIs(Node fun, const TypeCorpus* tc) {
  auto replacer = [tc](Node node, Node parent) -> Node {
    if (node.kind() != NT::ExprIs) {
      return node;
    }
    CanonType src_ct = Node_x_type(Node_expr(node));
    CanonType dst_ct = Node_x_type(Node_type(node));
    CanonType bool_ct = Node_x_type(node);
    const SrcLoc& sl = Node_srcloc(node);

    if (!CanonType_is_union(src_ct)) {
      bool val = src_ct == dst_ct || (CanonType_is_union(dst_ct) &&
                                      CanonType_union_contains(dst_ct, src_ct));
      NodeFreeRecursively(node);
      return MakeValNumBool(val, sl, bool_ct);
    }

    ASSERT(!CanonType_untagged(src_ct),
           "expected tagged union at " << Node_srcloc(node));
    std::vector<int> typeids;
    if (CanonType_is_union(dst_ct)) {
      for (CanonType ct : CanonType_children(dst_ct)) {
        if (CanonType_union_contains(src_ct, ct)) {
          typeids.push_back(CanonType_get_original_typeid(ct));
        }
      }
    } else {
      typeids.push_back(CanonType_get_original_typeid(dst_ct));
    }

    CanonType typeid_ct = tc->get_typeid_canon_type();

    Node tag = NodeNew(NT::ExprUnionTag);
    NodeInitExprUnionTag(tag, Node_expr(node), kStrInvalid, sl, typeid_ct);

    auto MakeTypeIdTest = [&sl, typeid_ct, bool_ct](int type_id,
                                                    Node tag) -> Node {
      Node val = NodeNew(NT::ValNum);
      NodeInitValNum(val, StrNew(EVAL_STR), kStrInvalid, sl, typeid_ct);
      Node_x_eval(val) =
          ConstNewUnsigned(type_id, CanonType_base_type_kind(typeid_ct));
      Node eq = NodeNew(NT::Expr2);
      NodeInitExpr2(eq, BINARY_EXPR_KIND::EQ, tag, val, kStrInvalid, sl,
                    bool_ct);
      return eq;
    };

    ASSERT(typeids.size() > 0, "no matching typeids for ExprIs at " << sl);
    NodeFreeRecursively(Node_type(node));
    NodeFree(node);

    Node out = MakeTypeIdTest(typeids.back(), tag);
    typeids.pop_back();
    while (!typeids.empty()) {
      ASSERT(IsNodeCopyableWithoutRiskOfSideEffects(Node_expr(tag)), "");
      std::map<Node, Node> dummy1;
      std::map<Node, Node> dummy2;
      Node next_test = MakeTypeIdTest(
          typeids.back(), NodeCloneRecursively(tag, &dummy1, &dummy2));
      typeids.pop_back();
      Node new_out = NodeNew(NT::Expr2);
      NodeInitExpr2(new_out, BINARY_EXPR_KIND::ORSC, next_test, out,
                    kStrInvalid, sl, bool_ct);
      out = new_out;
    }
    return out;
  };

  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunRemoveUselessCast(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() == NT::ExprAs &&
        Node_x_type(node) == Node_x_type(Node_expr(node))) {
      Node out = Node_expr(node);
      NodeFreeRecursively(Node_type(node));
      NodeFree(node);
      return out;
    }
    return node;
  };

  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

struct Scope {
  Scope(Node anode) : target(anode) {}
  Node target;
  std::vector<Node> defer_stmts;
};

Node EliminateDeferRecursively(Node node, std::vector<Scope>* scopes) {
  auto handle_cfg = [scopes](Node target, NodeChain* chain) {
    for (auto s = scopes->rbegin(); s != scopes->rend(); ++s) {
      for (auto d = s->defer_stmts.rbegin(); d != s->defer_stmts.rend(); ++d) {
        for (Node n = Node_body(*d); !n.isnull(); n = Node_next(n)) {
          std::map<Node, Node> dummy1;
          std::map<Node, Node> dummy2;
          chain->Append(NodeCloneRecursively(n, &dummy1, &dummy2));
        }
      }
      if (s->target == target) break;
    }
  };

  if (node.kind() == NT::StmtDefer) {
    scopes->back().defer_stmts.push_back(node);
  }

  if (NodeHasField(node, NFD_X_FIELD::target)) {
    NodeChain chain;
    handle_cfg(Node_x_target(node), &chain);
    chain.Append(node);
    return chain.First();
  }

  auto& core = gNodeCore[node];
  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;
    bool is_new_scope =
        (i == SLOT_BODY) || (Node_kind(node) == NT::StmtIf && i == SLOT_BODY_T);
    if (is_new_scope) {
      scopes->emplace_back(Scope(node));
    }

    NodeChain new_children;
    do {
      Node next = Node_next(child);
      Node_next(child) = kNodeInvalid;
      Node new_child = EliminateDeferRecursively(child, scopes);
      new_children.Append(new_child);
      child = next;
    } while (!child.isnull());

    if (is_new_scope) {
      Node last_child = new_children.Last();
      const Scope& current = scopes->back();
      if (last_child.isnull() ||
          !NodeHasField(last_child, NFD_X_FIELD::target)) {
        handle_cfg(current.target, &new_children);
      }
      for (auto d = current.defer_stmts.begin(); d != current.defer_stmts.end();
           ++d) {
        NodeFreeRecursively(*d);
      }
      scopes->pop_back();
    }
    core.children_node[i] = new_children.First();
  }

  if (node.kind() == NT::StmtDefer) {
    return kNodeInvalid;
  }
  return node;
}

void FunEliminateDefer(Node fun) {
  std::vector<Scope> scope;
  EliminateDeferRecursively(fun, &scope);
}

bool ShouldBeBoolExpanded(Node node, Node parent) {
  if (node.kind() != NT::Expr1 && node.kind() != NT::Expr2) {
    return false;
  }
  CanonType ct = Node_x_type(node);
  if (!CanonType_is_base_type(ct) ||
      CanonType_base_type_kind(ct) != BASE_TYPE_KIND::BOOL) {
    return false;
  }

  switch (parent.kind()) {
    case NT::ExprCall:
    case NT::StmtReturn:
    case NT::StmtAssignment:
    case NT::StmtCompoundAssignment:
    case NT::DefVar:
    case NT::DefGlobal:
    case NT::ValPoint:
      return true;
    default:
      return false;
  }
}

void FunCanonicalizeBoolExpressionsNotUsedForConditionals(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (!ShouldBeBoolExpanded(node, parent)) return node;
    const SrcLoc& sl = Node_srcloc(node);
    CanonType bool_ct = Node_x_type(node);

    Node out = NodeNew(NT::Expr3);
    NodeInitExpr3(out, node, MakeValNumBool(true, sl, bool_ct),
                  MakeValNumBool(false, sl, bool_ct), kStrInvalid, sl, bool_ct);
    Node_x_eval(out) = Node_x_eval(node);
    return out;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunDesugarExpr3(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() != NT::Expr3) return node;
    const SrcLoc& sl = Node_srcloc(node);
    //
    Node out = NodeNew(NT::ExprStmt);
    NodeInitExprStmt(out, node, kStrInvalid, sl, Node_x_type(node));
    Node_x_eval(out) = Node_x_eval(node);
    NodeChain body;

    //
    Node val_t = Node_expr_t(node);
    if (val_t.kind() != NT::ValNum && val_t.kind() != NT::Id) {
      Node at = MakeTypeAuto(Node_x_type(node), sl);
      Node def_t = NodeNew(NT::DefVar);
      NodeInitDefVar(def_t, NameNew("expr3_t"), at, val_t, 0, kStrInvalid, sl,
                     Node_x_type(node));
      body.Append(def_t);
      val_t = IdNodeFromDef(def_t, sl);
      Node_x_eval(val_t) = Node_x_eval(Node_expr_t(node));
    }
    Node ret_t = NodeNew(NT::StmtReturn);
    NodeInitStmtReturn(ret_t, val_t, kStrInvalid, sl, out);
    //
    Node val_f = Node_expr_f(node);
    if (val_f.kind() != NT::ValNum && val_f.kind() != NT::Id) {
      Node at = MakeTypeAuto(Node_x_type(node), sl);
      Node def_f = NodeNew(NT::DefVar);
      NodeInitDefVar(def_f, NameNew("expr3_f"), at, val_f, 0, kStrInvalid, sl,
                     Node_x_type(node));
      body.Append(def_f);
      val_f = IdNodeFromDef(def_f, sl);
      Node_x_eval(val_f) = Node_x_eval(Node_expr_f(node));
    }
    Node ret_f = NodeNew(NT::StmtReturn);
    NodeInitStmtReturn(ret_f, val_f, kStrInvalid, sl, out);
    //
    Node if_stmt = NodeNew(NT::StmtIf);
    NodeInitStmtIf(if_stmt, Node_cond(node), ret_t, ret_f, kStrInvalid, sl);
    body.Append(if_stmt);

    //
    NodeFree(node);
    Node_body(out) = body.First();
    return out;
  };

  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunAddMissingReturnStmts(Node fun) {
  CanonType result_ct = CanonType_result_type(Node_x_type(fun));
  CanonType unwrapped_ct = CanonType_get_unwrapped(result_ct);
  if (!CanonType_is_base_type(unwrapped_ct) ||
      CanonType_base_type_kind(unwrapped_ct) != BASE_TYPE_KIND::VOID) {
    return;
  }
  Node last = NodeLastSibling(Node_body(fun));
  if (last.kind() == NT::StmtReturn) {
    return;
  }
  const SrcLoc& sl = last.isnull() ? Node_srcloc(fun) : Node_srcloc(last);
  Node void_val = NodeNew(NT::ValVoid);
  NodeInitValVoid(void_val, kStrInvalid, sl, result_ct);

  Node ret = NodeNew(NT::StmtReturn);
  NodeInitStmtReturn(ret, void_val, kStrInvalid, sl, fun);
  if (last.isnull()) {
    Node_body(fun) = ret;
  } else {
    Node_next(last) = ret;
  }
}

void FunOptimizeKnownConditionals(Node fun) {
  auto visitor = [](Node node, Node parent) {
    if (node.kind() == NT::StmtIf && Node_cond(node).kind() == NT::ValNum) {
      Const val = Node_x_eval(Node_cond(node));
      ASSERT(val.kind() == BASE_TYPE_KIND::BOOL,
             "unexpected cond type " << Node_cond(node) << " at "
                                     << Node_srcloc(node));
      if (ConstGetUnsigned(val) == 0) {
        Node n = Node_body_t(node);
        while (!n.isnull()) {
          Node next = Node_next(n);
          NodeFreeRecursively(n);
          n = next;
        }
        Node_body_t(node) = kNodeInvalid;
      } else {
        Node n = Node_body_f(node);
        while (!n.isnull()) {
          Node next = Node_next(n);
          NodeFreeRecursively(n);
          n = next;
        }
        Node_body_f(node) = kNodeInvalid;
      }
    }
  };

  VisitAstRecursivelyPost(fun, visitor, kNodeInvalid);
}

}  // namespace cwerg::fe