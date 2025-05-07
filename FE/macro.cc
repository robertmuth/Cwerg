
#include "FE/macro.h"

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"

namespace cwerg::fe {

class MacroContext {
 private:
  IdGen* id_gen_;
  SrcLoc srcloc_;
  std::map<Name, Node> symtab_;

 public:
  MacroContext(IdGen* id_gen, const SrcLoc& srcloc)
      : id_gen_(id_gen), srcloc_(srcloc) {}

  void SetSymbol(Name name, Node value) {
    ASSERT(NameIsMacro(name), "");
    symtab_[name] = value;
  }

  Node GetSymbol(Name name) {
    auto it = symtab_.find(name);
    if (it == symtab_.end()) {
      return kNodeInvalid;
    }
    return it->second;
  }

  void RegisterSymbol(Name name, Node value) {
    ASSERT(GetSymbol(name).isnull(), "");
    SetSymbol(name, value);
  }

  void GenerateNewSymbol(Name name, const SrcLoc& srcloc) {
    Name new_name = id_gen_->NameNewNext(NameNew(NameData(name) + 1));
    Node id = NodeNew(NT::Id);
    InitId(id, new_name, kNameInvalid, kStrInvalid, srcloc);

    RegisterSymbol(name, id);
  }
};

void FixUpExprListRest(Node params, Node args) {
  int num_params = NodeNumSiblings(params);
  Node last_param = NodeLastSiblings(params);
  if (Node_macro_param_kind(last_param) != MACRO_PARAM_KIND::EXPR_LIST_REST) {
    return;
  }

  for (int i = 0; i < num_params - 1; ++i) {
    if (args.isnull()) {
      CompilerError(Node_srcloc(args)) << "too few arguments";
    }
    args = Node_next(args);
  }

  Node rest = NodeNew(NT::EphemeralList);
  InitEphemeralList(rest, Node_next(args), 0, kStrInvalid, Node_srcloc(args));
  Node_next(args) = kNodeInvalid;
  Node_next(last_param) = rest;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting, IdGen* id_gen);

Node ExpandMacroBodyNodeRecursively(Node node, MacroContext* ctx) {
  // Note these may be written.
  std::map<Node, Node> dummy1;
  std::map<Node, Node> dummy2;
  switch (Node_kind(node)) {
    case NT::DefVar:
      if (NameIsMacro(Node_name(node))) {
        Node new_name = ctx->GetSymbol(Node_name(node));
        ASSERT(Node_kind(new_name) == NT::Id, "");
        Node type =
            ExpandMacroBodyNodeRecursively(Node_type_or_auto(node), ctx);
        Node initial = ExpandMacroBodyNodeRecursively(
            Node_initial_or_undef_or_auto(node), ctx);
        Node out = NodeNew(NT::DefVar);
        InitDefVar(out, Node_name(new_name), type, initial,
                   Node_compressed_flags(node), kStrInvalid, Node_srcloc(node));
        return out;
      }

      break;
    case NT::MacroId: {
      Node arg = ctx->GetSymbol(Node_name(node));

      Node replacement = NodeCloneRecursively(arg, &dummy1, &dummy2);
      if (Node_kind(replacement) == NT::EphemeralList) {
        replacement = Node_args(replacement);
      }
      return replacement;
    }
    case NT::MacroFor: {
      Name loop_var = Node_name(node);
      ASSERT(NameIsMacro(loop_var), "");
      Node args = ctx->GetSymbol(Node_name_list(node));
      ASSERT(Node_kind(args) == NT::EphemeralList, "");
      args = Node_args(node);
      NodeChain out;
      for (Node arg = args; !arg.isnull(); arg = Node_next(arg)) {
        ctx->SetSymbol(loop_var, arg);
        for (Node body = Node_body_for(node); !body.isnull();
             body = Node_next(body)) {
          Node exp = ExpandMacroBodyNodeRecursively(body, ctx);
          out.Append(exp);
         }
      }
      return out.First();
    }

    default:
      break;
  }

  Node clone = NodeCloneBasics(node);
  auto& core = gNodeCore[clone];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Handle handle = core.children[i];
    if (handle.raw_kind() == kKindStr || handle.raw_kind() == kKindName ||
        handle.isnull()) {
      core.children[i] = handle;
      continue;
    }

    Node child = Node(handle);
    core.children[i] = ExpandMacroBodyNodeRecursively(Node(child), ctx);

    while (!Node_next(child).isnull()) {
      Node_next(child) = ExpandMacroBodyNodeRecursively(Node_next(child), ctx);
      child = Node_next(child);
    }
  }

  return clone;
}

constexpr int MAX_MACRO_NESTING = 8;

Node ExpandMacroInvocation(Node macro_invoke, int nesting, IdGen* id_gen) {
  if (nesting >= MAX_MACRO_NESTING) {
    CompilerError(Node_srcloc(macro_invoke)) << "too many nested macros";
  }
  Node def_macro = Node_x_symbol(macro_invoke);
  if (Node_kind(def_macro) != NT::DefMacro) {
    CompilerError(Node_srcloc(macro_invoke)) << "not a macro";
  }
  Node params = Node_params_macro(def_macro);
  Node args = Node_args(macro_invoke);
  FixUpExprListRest(params, args);
  if (NodeNumSiblings(params) != NodeNumSiblings(args)) {
    CompilerError(Node_srcloc(macro_invoke))
        << "wrong number of macro arguments";
  }

  MacroContext ctx(id_gen, Node_srcloc(macro_invoke));

  for (Node p = params, a = args; !p.isnull();
       p = Node_next(p), a = Node_next(a)) {
    ctx.RegisterSymbol(Node_name(p), a);
  }

  for (Node x = Node_gen_ids(def_macro); !x.isnull(); x = Node_next(x)) {
    ctx.GenerateNewSymbol(Node_name(x), Node_srcloc(macro_invoke));
  }

  for (Node body = Node_body_macro(def_macro); !body.isnull();
       body = Node_next(body)) {
    // Node exp = ExpandMacroBodyNodeRecursively(body, &ctx);
  }
  return kNodeInvalid;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting, IdGen* id_gen) {
  auto replacer = [nesting, id_gen](Node node, Node parent) -> Node {
    NT kind = Node_kind(node);

    if (kind == NT::MacroInvoke) {
      return ExpandMacroInvocation(node, nesting, id_gen);
    } else if (kind == NT::ExprSrcLoc) {
      ASSERT(false, "");
      return kNodeInvalid;
    } else if (kind == NT::ExprStringify) {
      ASSERT(false, "");
      return kNodeInvalid;
    }
    return node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void ExpandMacrosAndMacroLike(const std::vector<Node>& mods) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        IdGen idgen;
        ExpandMacrosAndMacroLikeRecursively(child, 0, &idgen);
      }
    }
  }
}
}  // namespace cwerg::fe