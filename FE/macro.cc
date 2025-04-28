
#include "FE/macro.h"

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"

namespace cwerg::fe {

class MacroContext {
 private:
  IdGen* id_gen_;
  SrcLoc srcloc_;
  SymTab symtabs_;

 public:
  MacroContext(IdGen* id_gen, const SrcLoc& srcloc)
      : id_gen_(id_gen), srcloc_(srcloc) {}
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

Node ExpandMacroInvokation(Node macro_invoke, Node def_macro, IdGen* id_gen) {
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
  }

  return kNodeInvalid;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting,
                                         const SymTab* builtin_symtab,
                                         IdGen* id_gen);

constexpr int MAX_MACRO_NESTING = 8;

Node ExpandMacroInvokeIteratively(Node macro_invoke, int nesting,
                                  const SymTab* builtin_symtab, IdGen* id_gen) {
  do {
    if (nesting >= MAX_MACRO_NESTING) {
      CompilerError(Node_srcloc(macro_invoke)) << "too many nested macros";
    }
    SymTab* symtab = Node_x_symtab(Node_x_module(Node_x_import(macro_invoke)));
    Node def_macro =
        SymTabResolveMacro(symtab, macro_invoke, builtin_symtab,
                           HasImportedSymbolReference(macro_invoke));
    if (def_macro.isnull()) {
      CompilerError(Node_srcloc(macro_invoke)) << "unknown macro";
    }
    macro_invoke = ExpandMacroInvokation(macro_invoke, def_macro, id_gen);
    ++nesting;
  } while (Node_kind(macro_invoke) == NT::MacroInvoke);
  ExpandMacrosAndMacroLikeRecursively(macro_invoke, nesting + 1, builtin_symtab,
                                      id_gen);
  return kNodeInvalid;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting,
                                         const SymTab* builtin_symtab,
                                         IdGen* id_gen) {
  auto replacer = [nesting, builtin_symtab, id_gen](Node node,
                                                    Node parent) -> Node {
    Node orig_node = node;
    if (Node_kind(node) == NT::MacroInvoke) {
      node =
          ExpandMacroInvokeIteratively(node, nesting, builtin_symtab, id_gen);
    }
    NT kind = Node_kind(node);
    if (kind == NT::ExprSrcLoc) {
      ASSERT(false, "");
      return kNodeInvalid;
    } else if (kind == NT::ExprStringify) {
      ASSERT(false, "");
      return kNodeInvalid;
    }
    return node == orig_node ? kNodeInvalid : node;
  };
  MaybeReplaceAstRecursivelyPost(fun, replacer, kNodeInvalid);
}

void ExpandMacrosAndMacroLike(const std::vector<Node>& mods,
                              const SymTab* builtin_symtab,
                              IdGenCache* id_gen_cache) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        ExpandMacrosAndMacroLikeRecursively(
            child, 0, builtin_symtab, id_gen_cache->Get(child, builtin_symtab));
      }
    }
  }
}
}  // namespace cwerg::fe