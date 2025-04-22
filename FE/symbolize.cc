
#include "FE/symbolize.h"

#include "Util/assert.h"

namespace cwerg::fe {

bool IsFieldNode(Node node, Node parent) {
  return (Node_kind(parent) == NT::ExprOffsetof ||
          Node_kind(parent) == NT::ExprField) &&
         Node_field(parent) == node;
}

bool IsPointNode(Node node, Node parent) {
  return (Node_kind(parent) == NT::ValPoint) && Node_point(parent) == node;
}

bool HasImportedSymbolReference(Node node) {
  if (Node_x_import(node).isnull()) {
    return false;
  }

  auto seq = NameStrAndSeq(Node_name(Node_x_import(node))).seq;
  return seq != MAGIC_SELF_IMPORT_SEQ;
}

Node SymTabFindWithDefault(const SymTab* symtab, Name name) {
  StrAndSeq ss = NameStrAndSeq(name);
  auto it = symtab->find(ss);

  // auto it = symtab->find(NameStrAndSeq(name));

  if (it == symtab->end()) {
    return kNodeInvalid;
  }
  return it->second;
}

Node SymTabResolveNameWithVisibilityCheck(const SymTab* symtab, Name name,
                                          bool must_be_public,
                                          const SrcLoc& srcloc) {
  Node def = SymTabFindWithDefault(symtab, name);
  if (def != kNodeInvalid) {
    if (must_be_public && !Node_has_flag(def, BF::PUB)) {
      CompilerError(srcloc) << "not public " << name;
    }
  }
  return def;
}

Node SymTabResolveSym(const SymTab* symtab, Node node, bool must_be_public) {
  ASSERT(Node_kind(node) == NT::Id, "");
  Name name = Node_name(node);
  Name enum_name = Node_enum_name(node);
  Node out = SymTabResolveNameWithVisibilityCheck(symtab, name, must_be_public,
                                                  Node_srcloc(node));
  if (enum_name != kNameInvalid) {
    if (out == kNodeInvalid) {
      CompilerError(Node_srcloc(node)) << "enum not found";
    }
    ASSERT(Node_kind(out) == NT::DefEnum, "");
    for (Node child = Node_items(out); !child.isnull();
         child = Node_next(Node(child))) {
      ASSERT(Node_kind(child) == NT::EnumVal, "");
      if (Node_name(child) == enum_name) {
        return child;
      }
    }
    CompilerError(Node_srcloc(node)) << "enum value not found";
  }
  return out;
}

void AnnotateNodeSymbol(Node node, Node def_node) {
  ASSERT(Node_kind(node) == NT::Id, "");
  ASSERT(Node_x_symbol(node) == kNodeInvalid, "");
  Node_x_symbol(node) = def_node;
}

void HelperResolveSymbolsOutsideFunctionsAndMacros(Node node,
                                                   const SymTab* builtin_symtab,
                                                   bool must_resolve_all) {
  auto visitor = [must_resolve_all, builtin_symtab](Node node, Node parent) {
    if (Node_kind(node) != NT::Id || !Node_x_symbol(node).isnull()) {
      return;
    }
    if (IsFieldNode(node, parent)) {
      return;
    }
    Node import_node = Node_x_import(node);
    ASSERT(!import_node.isnull(), "");
    ASSERT(Node_kind(import_node) == NT::Import, "");

    if (Node_x_module(import_node).isnull()) {
      if (must_resolve_all) {
        CompilerError(Node_srcloc(node)) << "module not resolved";
      }
      return;
    }
    const SymTab* ref_symtab = Node_x_symtab(Node_x_module(import_node));
    // std::cout << "@@@@@@ " << Node_name(import_node) << " " << " "
    //          << builtin_symtab << "\n";
    Node def_node =
        SymTabResolveSym(ref_symtab, node, HasImportedSymbolReference(node));
    if (def_node.isnull()) {
      def_node = SymTabResolveSym(builtin_symtab, node, true);
    }
    if (def_node == kNodeInvalid) {
      AnnotateNodeSymbol(node, def_node);
    } else {
      if (must_resolve_all && !IsPointNode(node, parent)) {
        CompilerError(Node_srcloc(node)) << "cannot resolve symbol";
      }
    }
  };
  VisitNodesRecursivelyPost(node, visitor, kNodeInvalid);
}

void ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab,
    bool must_resolve_all) {
  for (Node mod : mods) {
    ASSERT(Node_kind(mod) == NT::DefMod, "");
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(Node(child))) {
      if (Node_kind(child) != NT::DefFun && Node_kind(child) != NT::DefMacro) {
        HelperResolveSymbolsOutsideFunctionsAndMacros(child, builtin_symtab,
                                                      must_resolve_all);
      }
    }
  }
}
void ResolveSymbolInsideFunction(Node node, const SymTab* builtin_symtab,
                                 std::vector<SymTab>* scopes) {
  ASSERT(Node_kind(node) == NT::Id, "");
  // TODO
}

void FunResolveSymbolsInsideFunctions(Node fun, const SymTab* builtin_symtab,
                                      std::vector<SymTab>* scopes) {
  auto visitor = [builtin_symtab, scopes](Node node, Node parent) {
    if (Node_kind(node) == NT::Id) {
      if (!IsFieldNode(node, parent)) {
        ResolveSymbolInsideFunction(node, builtin_symtab, scopes);
      }
    } else if (Node_kind(node) == NT::DefVar) {
      auto& ss = NameStrAndSeq(Node_name(node));
      if (scopes->back().contains(ss)) {
        CompilerError(Node_srcloc(node)) << "duplicate symbol " << ss;
      }
      scopes->back()[ss] = node;
    }
  };

  auto scope_enter = [scopes](Node node) {
    scopes->push_back(SymTab());
    if (Node_kind(node) == NT::DefFun) {
      for (Node child = Node_params(node); !child.isnull();
           child = Node_next(child)) {
        auto& ss = NameStrAndSeq(Node_name(child));
        if (scopes->back().contains(ss)) {
          CompilerError(Node_srcloc(node)) << "duplicate symbol " << ss;
          scopes->back()[ss] = node;
        }
      }
    }
  };
  auto scope_exit = [scopes](Node node) { scopes->pop_back(); };
  VisitAstRecursivelyWithScopeTracking(fun, visitor, scope_enter, scope_exit,
                                       kNodeInvalid);
}

void ResolveSymbolsInsideFunctions(const std::vector<Node>& mods,
                                   const SymTab* builtin_symtab) {
  std::vector<SymTab> scopes;
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        scopes.clear();
        FunResolveSymbolsInsideFunctions(child, builtin_symtab, &scopes);
      }
    }
  }
}

void FunSetTargetField(Node fun) {
  std::vector<Node> stack;
  auto pre_visitor = [&stack](Node node, Node parent) {
    stack.push_back(node);
    const auto nt = Node_kind(node);
    if (nt == NT::StmtBreak || nt == NT::StmtContinue) {
      for (auto it = stack.rbegin(); it != stack.rend(); ++it) {
        if (Node_kind(*it) == NT::StmtBlock) {
          if (Node_label(node).isnull() || NameStrAndSeq(Node_label(node)) ==
                                               NameStrAndSeq(Node_label(*it))) {
            Node_x_target(node) = *it;
            return;
          }
        }
      }
      CompilerError(Node_srcloc(node)) << "cannot find target";
    } else if (nt == NT::StmtReturn) {
      for (auto it = stack.rbegin(); it != stack.rend(); ++it) {
        if (Node_kind(*it) == NT::DefFun || Node_kind(*it) == NT::ExprStmt) {
          Node_x_target(node) = *it;
          return;
        }
      }
      CompilerError(Node_srcloc(node)) << "cannot find target";
    }
  };
  auto post_visitor = [&stack](Node node, Node parent) { stack.pop_back(); };
  VisitNodesRecursivelyPreAndPost(fun, pre_visitor, post_visitor, kNodeInvalid);
}

void SetTargetFields(const std::vector<Node>& mods) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        FunSetTargetField(child);
      }
    }
  }
}

void VerifySymbols(Node node) {}

}  // namespace cwerg::fe