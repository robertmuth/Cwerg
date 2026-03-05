#include "FE/controlflow.h"

#include "FE/eval.h"

namespace cwerg::fe {

bool CondIsAlwaysTrue(Node cond) {
  if (cond.kind() == NT::ValNum) {
    return Node_x_eval(cond) == kConstTrue;
  }
  return false;
}

bool CondIsAlwaysFalse(Node cond) {
  if (cond.kind() == NT::ValNum) {
    return Node_x_eval(cond) == kConstFalse;
  }
  return false;
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