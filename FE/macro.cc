
#include "FE/macro.h"

namespace cwerg::fe {

class MacroContext {
 private:
  IdGen* id_gen_;

 public:
  MacroContext(IdGen* id_gen) : id_gen_(id_gen) {}
};

void ExpandMacrosAndMacroLikeRecursively(Node fun, const SymTab* builtin_symtab,
                                         MacroContext* ctx) {
  auto replacer = [&ctx](Node node, Node parent) -> Node {
    return kNodeInvalid;
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
        ExpandMacrosAndMacroLikeRecursively(child, builtin_symtab, &ctx);
      }
    }
  }
}
}  // namespace cwerg::fe