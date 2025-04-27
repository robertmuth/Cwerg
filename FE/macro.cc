
#include "FE/macro.h"

namespace cwerg::fe {

class MacroContext {
 private:
  IdGen* id_gen_;

 public:
  MacroContext(IdGen* id_gen) : id_gen_(id_gen) {}
};

Node ExpandMacroInvokeIteratively(Node node, int nesting, const SymTab* builtin_symtab,
                                 MacroContext* ctx) {
  return kNodeInvalid;
}

void ExpandMacrosAndMacroLikeRecursively(Node fun, int nesting,
                                         const SymTab* builtin_symtab,
                                         MacroContext* ctx) {
  auto replacer = [nesting, builtin_symtab, ctx](Node node, Node parent) -> Node {
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