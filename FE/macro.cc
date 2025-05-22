
#include "FE/macro.h"

#include <set>
#include <sstream>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"

namespace cwerg::fe {

class MacroContext {
 private:
  Node invoke_;
  IdGen* id_gen_;
  SrcLoc srcloc_;
  std::map<Name, Node> symtab_;
  std::map<Name, Node> symtab_not_owned_;

 public:
  MacroContext(Node invoke, IdGen* id_gen, const SrcLoc& srcloc)
      : invoke_(invoke), id_gen_(id_gen), srcloc_(srcloc) {}

  ~MacroContext() {
    for (const auto& [name, node] : symtab_) {
      if (!symtab_not_owned_.contains(name)) NodeFreeRecursively(node);
    }
  }

  void SetSymbol(Name name, Node value) {
    // std::cout << "@@ SetSymbol " << Node_name(invoke_) << " " << name << " "
    //          << EnumToString(Node_kind(value)) << " " << value.index() <<
    //          "\n";
    ASSERT(NameIsMacro(name), "");
    symtab_not_owned_[name] = value;
  }

  Node GetSymbol(Name name) {
    auto it = symtab_.find(name);
    if (it != symtab_.end()) {
      return it->second;
    }
    it = symtab_not_owned_.find(name);
    if (it != symtab_not_owned_.end()) {
      return it->second;
    }
    ASSERT(false, "unknown name " << name);
    return kNodeInvalid;
  }

  void RegisterSymbolWithOwnership(Name name, Node value) {
    // std::cout << "@@ SetSymbol WO " << Node_name(invoke_) << " " << name << "
    // "
    //          << EnumToString(Node_kind(value)) << " " << value.index() <<
    //          "\n";
    ASSERT(!symtab_.contains(name), "");
    ASSERT(NameIsMacro(name), "");
    symtab_[name] = value;
  }

  void GenerateNewSymbol(Name name, const SrcLoc& srcloc) {
    Name new_name = id_gen_->NameNewNext(NameNew(NameData(name) + 1));
    Node id = NodeNew(NT::Id);
    NodeInitId(id, new_name, kNameInvalid, kStrInvalid, srcloc);

    RegisterSymbolWithOwnership(name, id);
  }
};

Node FixUpArgsForExprListRest(Node params, Node args) {
  int num_params = NodeNumSiblings(params);
  Node last_param = NodeLastSiblings(params);
  if (Node_macro_param_kind(last_param) != MACRO_PARAM_KIND::EXPR_LIST_REST ||
      args.isnull()) {
    return args;
  }

  Node rest = NodeNew(NT::EphemeralList);
  if (num_params == 1) {
    NodeInitEphemeralList(rest, args, 0, kStrInvalid, Node_srcloc(args));
    return rest;
  }

  Node head = args;
  // advance args to the one before the "rest"
  for (int i = 0; i < num_params - 2; ++i) {
    if (args.isnull()) {
      CompilerError(Node_srcloc(args)) << "too few arguments";
    }
    args = Node_next(args);
  }

  NodeInitEphemeralList(rest, Node_next(args), 0, kStrInvalid,
                        Node_srcloc(args));
  Node_next(args) = rest;
  return head;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting, IdGen* id_gen);

Node ExpandMacroBodyNodeRecursively(Node node, MacroContext* ctx) {
  // std::cout << "@@   Expand body node " << EnumToString(Node_kind(node))
  //          << "\n";
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
        NodeInitDefVar(out, Node_name(new_name), type, initial,
                       Node_compressed_flags(node), kStrInvalid,
                       Node_srcloc(node));
        return out;
      }

      break;
    case NT::MacroId: {
      Node arg = ctx->GetSymbol(Node_name(node));

      Node replacement = NodeCloneRecursively(arg, &dummy1, &dummy2);
      // std::cout << "@@ expanding " << Node_name(node) << " "
      //          << EnumToString(Node_kind(arg)) << " " << arg.index() << " ->
      //          "
      //          << replacement.index() << "\n";

      if (Node_kind(replacement) == NT::EphemeralList) {
        Node args = Node_args(replacement);
        NodeFree(replacement);
        replacement = args;
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
  const NodeCore& core = gNodeCore[node];
  auto& core_clone = gNodeCore[clone];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (child.raw_kind() == kKindStr || child.raw_kind() == kKindName ||
        child.isnull()) {
      core_clone.children_node[i] = child;
      continue;
    }
    NodeChain new_children;

    do {
      Node exp = ExpandMacroBodyNodeRecursively(child, ctx);
      new_children.Append(exp);
      child = Node_next(child);
    } while (!child.isnull());

    core_clone.children_node[i] = new_children.First();
  }

  return clone;
}

constexpr int MAX_MACRO_NESTING = 8;

Node ExpandMacroInvocation(Node macro_invoke, int nesting, IdGen* id_gen) {
  // std::cout << "@@ Expand invoke of " << Node_name(macro_invoke)
  //           << " nesting=" << nesting << "\n";
  if (nesting >= MAX_MACRO_NESTING) {
    CompilerError(Node_srcloc(macro_invoke)) << "too many nested macros";
  }
  Node def_macro = Node_x_symbol(macro_invoke);
  if (Node_kind(def_macro) != NT::DefMacro) {
    CompilerError(Node_srcloc(macro_invoke)) << "not a macro";
  }
  Node params = Node_params_macro(def_macro);
  Node args = Node_args(macro_invoke);
  args = FixUpArgsForExprListRest(params, args);
  if (NodeNumSiblings(params) != NodeNumSiblings(args)) {
    CompilerError(Node_srcloc(macro_invoke))
        << "wrong number of macro arguments for " << Node_name(macro_invoke)
        << ": " << NodeNumSiblings(params) << " vs " << NodeNumSiblings(args);
  }

  MacroContext ctx(macro_invoke, id_gen, Node_srcloc(macro_invoke));

  for (Node p = params, a = args; !p.isnull();
       p = Node_next(p), a = Node_next(a)) {
    ctx.RegisterSymbolWithOwnership(Node_name(p), a);
  }

  // The ctx now "owns" the arg nodes so
  // we unlink them from each other and the invocation
  Node_args(macro_invoke) = kNodeInvalid;
  while (!args.isnull()) {
    Node next = Node_next(args);
    Node_next(args) = kNodeInvalid;
    args = next;
  }

  for (Node x = Node_gen_ids(def_macro); !x.isnull(); x = Node_next(x)) {
    ctx.GenerateNewSymbol(Node_name(x), Node_srcloc(macro_invoke));
  }

  NodeChain body_clone;
  for (Node body = Node_body_macro(def_macro); !body.isnull();
       body = Node_next(body)) {
    Node exp = ExpandMacroBodyNodeRecursively(body, &ctx);
    body_clone.Append(exp);
  }

  Node list = NodeNew(NT::EphemeralList);
  NodeInitEphemeralList(list, body_clone.First(), 0, kStrInvalid,
                        kSrcLocInvalid);
  ExpandMacrosAndMacroLikeRecursively(list, nesting + 1, id_gen);
  NodeFreeRecursively(macro_invoke);
  Node out = Node_args(list);
  NodeFree(list);
  return out;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting, IdGen* id_gen) {
  auto replacer = [nesting, id_gen](Node node, Node parent) -> Node {
    switch (Node_kind(node)) {
      case NT::MacroInvoke:
        return ExpandMacroInvocation(node, nesting, id_gen);
      case NT::ExprSrcLoc: {
        std::stringstream ss;
        ss << Node_srcloc(Node_expr(node));
        Node out = NodeNew(NT::ValString);
        NodeInitValString(out, StrNew(ss.str()), kStrInvalid,
                          Node_srcloc(node));
        NodeFreeRecursively(node);
        return out;
      }
      case NT::ExprStringify: {
        std::stringstream ss;
        ss << EnumToString(Node_kind(Node_expr(node)));
        Node out = NodeNew(NT::ValString);
        NodeInitValString(out, StrNew(ss.str()), kStrInvalid,
                          Node_srcloc(node));
        NodeFreeRecursively(node);
        return out;
      }

      default:
        return node;
    }
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

  for (Node mod : mods) {
    RemoveNodesOfType(mod, NT::DefMacro);
  }
}
}  // namespace cwerg::fe