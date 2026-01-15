

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
      if (CanonType_fits_in_register(child)) {
        new_children_ct.push_back(child);
      } else {
        new_children_ct.push_back(tc->InsertPtrType(false, child));
        change = true;
      }
    }

    CanonType new_result_ct = orig_children_ct.back();
    if (!CanonType_is_void(new_result_ct) &&
        !CanonType_fits_in_register(new_result_ct)) {
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

struct DefAndArg {
  Node def;
  Node arg;
};

DefAndArg MakeDefVarAndAddrOfForParam(Name name, Node init, CanonType ct_old,
                                      CanonType ct_new, bool mut) {
  const SrcLoc& sl = Node_srcloc(init);
  Node at = MakeTypeAuto(ct_old, sl);
  Node def = NodeNew(NT::DefVar);
  NodeInitDefVar(def, name, at, init, mut ? Mask(BF::MUT) : 0, kStrInvalid, sl,
                 ct_old);
  Node sym = IdNodeFromDef(def, sl);
  Node addr_of = NodeNew(NT::ExprAddrOf);
  NodeInitExprAddrOf(addr_of, sym, 0, kStrInvalid, sl, ct_new);
  return {def, addr_of};
}

void FunRewriteLargeArgsCallerSide(Node fun, TypeCorpus* tc) {
  auto replacer = [tc](Node call, Node parent) -> Node {
    if (call.kind() != NT::ExprCall) return call;
    CanonType orig_fun_ct = Node_x_type(Node_callee(call));
    CanonType new_fun_ct = tc->MaybeGetReplacementType(orig_fun_ct);
    if (new_fun_ct.isnull()) return call;
    //
    const SrcLoc& sl = Node_srcloc(call);
    Node_next(call) = kNodeInvalid;  // unlink call before consuming it later

    NodeChain expr_body;
    NodeChain new_args;
    Node out = NodeNew(NT::ExprStmt);
    NodeInitExprStmt(out, kNodeInvalid, kStrInvalid, sl, Node_x_type(call));
    //
    NodeChangeType(call, new_fun_ct);
    const std::span<CanonType> orig_children_ct =
        CanonType_children(orig_fun_ct);
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
        auto def_and_arg = MakeDefVarAndAddrOfForParam(
            NameNew("arg", i), the_arg, old_ct, new_ct, false);
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
    Node_args(out) = new_args.First();
    return out;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void FunRewriteLargeArgsCalleeSide(Node fun, CanonType new_sig,
                                   TypeCorpus* tc) {
  auto replacer = [](Node node, Node parent) -> Node { return node; };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}
}  // namespace cwerg::fe