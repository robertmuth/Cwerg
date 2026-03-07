#include "FE/controlflow.h"

#include "FE/eval.h"

namespace cwerg::fe {

bool CondIsAlwaysTrue(Node cond) { return Node_x_eval(cond) == kConstTrue; }

bool CondIsAlwaysFalse(Node cond) { return Node_x_eval(cond) == kConstFalse; }

bool ContainsBreakRecurtsively(Node node_list, Node block_target) {
  for (Node n = node_list; !n.isnull(); n = Node_next(n)) {
    switch (n.kind()) {
      case NT::StmtBreak:
        return Node_x_target(n) == block_target;
      case NT::StmtReturn:
      case NT::StmtTrap:
      case NT::StmtContinue:
        return false;
      case NT::StmtIf:
        if (!CondIsAlwaysTrue(Node_cond(n))) {
          if (ContainsBreakRecurtsively(Node_body_f(n), block_target))
            return true;
        }
        if (!CondIsAlwaysFalse(Node_cond(n))) {
          if (ContainsBreakRecurtsively(Node_body_t(n), block_target))
            return true;
        }
        break;
      case NT::StmtDefer:
        return ContainsBreakRecurtsively(Node_body(n), block_target);
      case NT::StmtCond: {
        for (Node c = Node_cases(n); !c.isnull(); c = Node_next(c)) {
          if (ContainsBreakRecurtsively(Node_body(c), block_target)) {
            return true;
          }
        }
      }
      default:
        break;
    }
  }
  return false;
}

bool LastStmtIsBreak(Node body, Node block_target) {
  if (body.isnull()) return false;
  Node last = NodeLastSibling(body);
  if (last.kind() == NT::StmtBreak) {
    return Node_x_target(last) == block_target;
  }
  return false;
}

// forward declaration needed because of mutual recursion
bool BodyFallsThru(Node body);

bool LastStmtFallsThrough(Node last) {
  switch (last.kind()) {
    case NT::StmtReturn:
    case NT::StmtTrap:
    case NT::StmtContinue:
      return false;
    case NT::StmtBreak:
      return true;
    case NT::StmtIf: {
      if (!CondIsAlwaysTrue(Node_cond(last))) {
        if (BodyFallsThru(Node_body_f(last))) return true;
      }
      if (!CondIsAlwaysFalse(Node_cond(last))) {
        if (BodyFallsThru(Node_body_t(last))) return true;
      }
      return false;
    }
    case NT::StmtCond: {
      bool seen_always_true = false;

      for (Node c = Node_cases(last); !c.isnull(); c = Node_next(c)) {
        if (CondIsAlwaysTrue(Node_cond(c))) seen_always_true = true;
        if (BodyFallsThru(Node_body(c))) {
          return true;
        }
      }
      return !seen_always_true;
    }
    case NT::StmtBlock: {
      Node body = Node_body(last);
      if (body.isnull()) return true;
      if (ContainsBreakRecurtsively(body, last)) return true;
      return LastStmtFallsThrough(NodeLastSibling(body));
    }
    default:
      return true;
  }
}

bool BodyFallsThru(Node body) {
  if (body.isnull()) return true;
  return LastStmtFallsThrough(NodeLastSibling(body));
}

void ModVerifyFunFallthrus(Node mod) {
  ASSERT(mod.kind() == NT::DefMod, "");
  for (Node fun = Node_body_mod(mod); !fun.isnull(); fun = Node_next(fun)) {
    if (fun.kind() != NT::DefFun || Node_has_flag(fun, BF::EXTERN) ||
        CanonType_is_void(CanonType_result_type(Node_x_type(fun)))) {
      continue;
    }
    if (BodyFallsThru(Node_body(fun))) {
      CompilerError(Node_srcloc(fun))
          << "function may fall thru without returning";
    }
  }
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
          NodeToNodeMap dummy1;
          NodeToNodeMap dummy2;
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

void FunAddMissingReturnStmts(Node fun) {
  CanonType result_ct = CanonType_result_type(Node_x_type(fun));
  CanonType unwrapped_ct = CanonType_get_unwrapped(result_ct);
  if (!CanonType_is_void(unwrapped_ct)) {
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

void FunCanonicalizeRemoveStmtCond(Node fun) {
  auto replacer = [](Node node, Node parent) -> Node {
    if (node.kind() != NT::StmtCond) return node;
    std::vector<Node> cases;
    for (Node c = Node_cases(node); !c.isnull(); c = Node_next(c)) {
      cases.push_back(c);
    }
    if (cases.empty()) return kNodeInvalid;

    Node out = kNodeInvalid;
    for (auto it = cases.rbegin(); it != cases.rend(); ++it) {
      if (CondIsAlwaysTrue(Node_cond(*it))) {
        ASSERT(out == kNodeInvalid,
               "'case true' shold be the last case in a cond statement");
        out = Node_body(*it);
        NodeFree(Node_cond(*it));
        NodeFree(*it);
      } else {
        Node t = NodeNew(NT::StmtIf);
        NodeInitStmtIf(t, Node_cond(*it), Node_body(*it), out, kStrInvalid,
                       Node_srcloc(*it));
        NodeFree(*it);
        out = t;
      }
    }
    NodeFree(node);
    return out;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

}  // namespace cwerg::fe