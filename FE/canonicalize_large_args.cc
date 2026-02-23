

#include "FE/canonicalize_large_args.h"

#include <array>

#include "FE/canonicalize.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/typify.h"

namespace cwerg::fe {

void MakeAndRegisterLargeArgReplacements(TypeCorpus* tc) {
  tc->ClearReplacementInfo();

  for (CanonType orig_fun_ct : tc->InTopoOrder()) {
    if (!CanonType_is_fun(orig_fun_ct)) continue;

    bool change = false;
    const std::span<CanonType> orig_children_ct =
        CanonType_children(orig_fun_ct);

    std::vector<CanonType> new_children_ct;

    for (CanonType child :
         orig_children_ct.first(orig_children_ct.size() - 1)) {
      DK ir_regs = CanonType_ir_regs(child);
      if (ir_regs == DK::MEM) {
        new_children_ct.push_back(tc->InsertPtrType(false, child));
        change = true;
      } else {
        new_children_ct.push_back(child);
      }
    }

    CanonType new_result_ct = orig_children_ct.back();
    if (CanonType_ir_regs(new_result_ct) == DK::MEM) {
      new_children_ct.push_back(tc->InsertPtrType(true, new_result_ct));
      new_result_ct = tc->get_void_canon_type();
      change = true;
    }
    new_children_ct.push_back(new_result_ct);

    if (change) {
      CanonType new_fun_ct = tc->InsertFunType(new_children_ct);
      CanonTypeLinkReplacementType(orig_fun_ct, new_fun_ct);
    }
  }
}

Node FixupFunctionSignature(Node fun, CanonType old_sig, CanonType new_sig,
                            TypeCorpus* tc) {
  Node result_param = kNodeInvalid;
  NodeChangeType(fun, new_sig);
  const std::span<CanonType> old_children_ct = CanonType_children(old_sig);
  const std::span<CanonType> new_children_ct = CanonType_children(new_sig);
  // fixup large result
  if (old_children_ct.size() != new_children_ct.size()) {
    NodeChangeType(Node_result(fun), tc->get_void_canon_type());
    //
    const SrcLoc& sl = Node_srcloc(fun);
    Node at = MakeTypeAuto(new_children_ct[new_children_ct.size() - 2], sl);
    result_param = NodeNew(NT::FunParam);
    NodeInitFunParam(result_param, NameNew("large_result"), at,
                     Mask(BF::RES_REF), kStrInvalid, sl, Node_x_type(at));
    if (Node_params(fun).isnull()) {
      Node_params(fun) = result_param;
    } else {
      Node p = Node_params(fun);
      while (!Node_next(p).isnull()) {
        p = Node_next(p);
      }
      Node_next(p) = result_param;
    }
  }
  // other param
  Node param = Node_args(fun);
  for (int i = 0; i < old_children_ct.size() - 1; ++i) {
    CanonType old_ct = old_children_ct[i];
    CanonType new_ct = new_children_ct[i];
    if (old_ct != new_ct) {
      NodeChangeType(param, new_ct);
      NodeChangeType(Node_type(param), new_ct);
      Node_set_flag(param, BF::ARG_REF);
    }
    param = Node_next(param);
  }
  return result_param;
}

void FunRewriteLargeArgsParameter(Node fun, CanonType old_sig,
                                  CanonType new_sig, TypeCorpus* tc) {
  Node result_param = FixupFunctionSignature(fun, old_sig, new_sig, tc);
  auto replacer = [fun, result_param, tc](Node node, Node parent) -> Node {
    if (node.kind() == NT::Id) {
      Node sym = Node_x_symbol(node);
      if (sym.kind() == NT::FunParam && Node_has_flag(sym, BF::ARG_REF)) {
        Node out = NodeNew(NT::ExprDeref);
        NodeInitExprDeref(out, node, kStrInvalid, Node_srcloc(node),
                          Node_x_type(node));
        NodeChangeType(node, Node_x_type(sym));
        return out;
      }
    } else if (node.kind() == NT::StmtReturn && !result_param.isnull() &&
               Node_x_target(node) == fun) {
      NodeChain out;
      CanonType result_ct = Node_x_type(result_param);
      const SrcLoc& sl = Node_srcloc(node);
      Node id = NodeNew(NT::Id);
      NodeInitId(id, Node_name(result_param), kStrInvalid, sl,
                 result_param, result_ct);
      Node lhs = NodeNew(NT::ExprDeref);
      NodeInitExprDeref(lhs, id, kStrInvalid, sl,
                        CanonType_underlying_type(result_ct));
      Node assign = NodeNew(NT::StmtAssignment);
      NodeInitStmtAssignment(assign, lhs, Node_expr_ret(node), kStrInvalid, sl);
      Node val_void = NodeNew(NT::ValVoid);
      NodeInitValVoid(val_void, kStrInvalid, sl, tc->get_void_canon_type());
      Node_x_eval(val_void) = kConstVoid;
      Node_expr_ret(node) = val_void;
      out.Append(assign);
      out.Append(node);
      return out.First();
    }

    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

struct DefAndArg {
  Node def;
  Node arg;
};

DefAndArg MakeDefVarAndAddrOfForParam(Name name, Node init, CanonType ct_old,
                                      CanonType ct_new, bool mut) {
  const SrcLoc& sl = Node_srcloc(init);
  Node at = MakeTypeAuto(ct_old, sl);
  Node def = NodeNew(NT::DefVar);
  uint16_t flags = Mask(BF::REF) | (mut ? Mask(BF::MUT) : 0);
  NodeInitDefVar(def, name, at, init, flags, kStrInvalid, sl, ct_old);
  Node sym = IdNodeFromDef(def, sl);
  Node addr_of = NodeNew(NT::ExprAddrOf);
  NodeInitExprAddrOf(addr_of, sym, 0, kStrInvalid, sl, ct_new);
  return {def, addr_of};
}

Node FixupCall(Node call, CanonType orig_fun_ct, CanonType new_fun_ct,
               TypeCorpus* tc) {
  const SrcLoc& sl = Node_srcloc(call);
  Node_next(call) = kNodeInvalid;  // unlink call before consuming it later

  NodeChain expr_body;
  NodeChain new_args;
  Node out = NodeNew(NT::ExprStmt);
  NodeInitExprStmt(out, kNodeInvalid, kStrInvalid, sl, Node_x_type(call));
  //
  NodeChangeType(Node_callee(call), new_fun_ct);
  const std::span<CanonType> orig_children_ct = CanonType_children(orig_fun_ct);
  const std::span<CanonType> new_children_ct = CanonType_children(new_fun_ct);

  Node arg = Node_args(call);
  for (int i = 0; i < orig_children_ct.size() - 1; ++i) {
    Node the_arg = arg;
    arg = Node_next(arg);
    Node_next(the_arg) = kNodeInvalid;
    ASSERT(!the_arg.isnull(), "");
    CanonType old_ct = orig_children_ct[i];
    CanonType new_ct = new_children_ct[i];
    if (old_ct != new_ct) {
      auto def_and_arg = MakeDefVarAndAddrOfForParam(NameNew("arg", i), the_arg,
                                                     old_ct, new_ct, false);
      expr_body.Append(def_and_arg.def);
      the_arg = def_and_arg.arg;
    }
    new_args.Append(the_arg);
  }
  //
  if (orig_children_ct.size() != new_children_ct.size()) {
    Node undef_init = NodeNew(NT::ValUndef);
    NodeInitValUndef(undef_init, kStrInvalid, Node_srcloc(call));
    Node_x_eval(undef_init) = kConstUndef;
    auto [new_def, the_arg] = MakeDefVarAndAddrOfForParam(
        NameNew("result"), undef_init, orig_children_ct.back(),
        new_children_ct[new_children_ct.size() - 2], true);
    new_args.Append(the_arg);
    expr_body.Append(new_def);
    Node call_stmt = NodeNew(NT::StmtExpr);
    NodeChangeType(call, tc->get_void_canon_type());
    expr_body.Append(NodeInitStmtExpr(call_stmt, call, kStrInvalid, sl));
    Node ret_stmt = NodeNew(NT::StmtReturn);
    NodeInitStmtReturn(ret_stmt, IdNodeFromDef(new_def, sl), kStrInvalid, sl,
                       out);
    expr_body.Append(ret_stmt);
  } else {
    Node ret_stmt = NodeNew(NT::StmtReturn);
    NodeInitStmtReturn(ret_stmt, call, kStrInvalid, sl, out);
    expr_body.Append(ret_stmt);
  }
  Node_body(out) = expr_body.First();
  Node_args(call) = new_args.First();
  return out;
}

void FunRewriteLargeArgsCallsites(Node fun, TypeCorpus* tc) {
  auto replacer = [tc](Node call, Node parent) -> Node {
    if (call.kind() != NT::ExprCall) return call;
    CanonType orig_fun_ct = Node_x_type(Node_callee(call));
    CanonType new_fun_ct = tc->MaybeGetReplacementType(orig_fun_ct);
    if (new_fun_ct.isnull()) return call;
    return FixupCall(call, orig_fun_ct, new_fun_ct, tc);
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

}  // namespace cwerg::fe