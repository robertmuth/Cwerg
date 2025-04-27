
#include "FE/macro.h"

#include "FE/symbolize.h"

namespace cwerg::fe {

class MacroContext {
 private:
  IdGen* id_gen_;

 public:
  MacroContext(IdGen* id_gen) : id_gen_(id_gen) {}
};

Node ExpandMacroInvokation(Node macro_invoke, Node def_macro,
                           MacroContext* ctx) {
  return kNodeInvalid;
}
void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting,
                                         const SymTab* builtin_symtab,
                                         MacroContext* ctx);

constexpr int MAX_MACRO_NESTING = 8;

Node ExpandMacroInvokeIteratively(Node macro_invoke, int nesting,
                                  const SymTab* builtin_symtab,
                                  MacroContext* ctx) {
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
    macro_invoke = ExpandMacroInvokation(macro_invoke, def_macro, ctx);
    ++nesting;
  } while (Node_kind(macro_invoke) == NT::MacroInvoke);
  ExpandMacrosAndMacroLikeRecursively(macro_invoke, nesting + 1, builtin_symtab,
                                      ctx);
  return kNodeInvalid;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting,
                                         const SymTab* builtin_symtab,
                                         MacroContext* ctx) {
  auto replacer = [nesting, builtin_symtab, ctx](Node node,
                                                 Node parent) -> Node {
    Node orig_node = node;
    if (Node_kind(node) == NT::MacroInvoke) {
      node = ExpandMacroInvokeIteratively(node, nesting, builtin_symtab, ctx);
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
        MacroContext ctx =
            MacroContext(id_gen_cache->Get(child, builtin_symtab));
        ExpandMacrosAndMacroLikeRecursively(child, 0, builtin_symtab, &ctx);
      }
    }
  }
}
}  // namespace cwerg::fe