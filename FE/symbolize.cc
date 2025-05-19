
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
  return !Node_x_import(node).isnull();
}

Node SymTabFindWithDefault(const SymTab* symtab, Name name) {
  auto it = symtab->find(name);

  if (it == symtab->end()) {
    return kNodeInvalid;
  }
  return it->second;
}

Node SymTabResolveImported(const SymTab* symtab, Node node) {
  Node def_node = SymTabFindWithDefault(symtab, Node_name(node));
  if (!def_node.isnull()) {
    if (!Node_has_flag(def_node, BF::PUB)) {
      CompilerError(Node_srcloc(node)) << "not public " << Node_name(node);
    }
  }
  return def_node;
}

Node SymTabResolveWithFallback(const SymTab* symtab, Node node,
                               const SymTab* builtin_symtab) {
  Node def = SymTabFindWithDefault(symtab, Node_name(node));
  if (def.isnull()) {
    def = SymTabResolveImported(builtin_symtab, node);
  }
  return def;
}

Node ResolveEnum(Node enum_id, Node enum_type) {
  ASSERT(Node_kind(enum_type) == NT::DefEnum, "");
  ASSERT(Node_kind(enum_id) == NT::Id, "");
  Name enum_name = Node_enum_name(enum_id);
  for (Node child = Node_items(enum_type); !child.isnull();
       child = Node_next(Node(child))) {
    ASSERT(Node_kind(child) == NT::EnumVal, "");
    if (Node_name(child) == enum_name) {
      return child;
    }
  }
  CompilerError(Node_srcloc(enum_id)) << "enum value not found " << enum_name;
  return kNodeInvalid;
}
void UpdateNodeSymbolForPolyCall(Node id, Node new_def) {
  ASSERT(!new_def.isnull(), "");
  Node old_def = Node_x_symbol(id);
  ASSERT(Node_kind(old_def) == NT::DefFun, "");
  ASSERT(Node_has_flag(old_def, BF::POLY), "");
  Node_x_symbol(id) = new_def;
}

void AnnotateNodeSymbol(Node node, Node def_node) {
  ASSERT(!def_node.isnull(), "");
  // std::cout << "@@@ AnnotateNodeSymbol: " << Node_srcloc(node) << " "
  //          << node.index() << " " << Node_name(node) << " -> "
  //          << EnumToString(Node_kind(def_node)) << "\n";
  ASSERT(Node_kind(node) == NT::Id || Node_kind(node) == NT::MacroInvoke, "");
  ASSERT(Node_x_symbol(node).isnull(), "");
  Node_x_symbol(node) = def_node;
}

void ResolveGlobalAndImportedSymbols(Node node, const SymTab* symtab,
                                     const SymTab* builtin_symtab,
                                     bool runs_outside_fun) {
  auto visitor = [symtab, builtin_symtab, runs_outside_fun](
                     Node node, Node parent) -> bool {
    NT kind = Node_kind(node);
    if (kind != NT::Id && kind != NT::MacroInvoke) return false;
    if (!Node_x_symbol(node).isnull()) return false;
    if (IsFieldNode(node, parent)) return false;
    Node def_node;
    if (!Node_x_import(node).isnull()) {
      Node def_mod = Node_x_module(Node_x_import(node));
      if (def_mod.isnull()) {
        if (!runs_outside_fun) {
          CompilerError(Node_srcloc(node))
              << "module import unresolved for " << Node_name(node);
        }
        return false;
      }
      const SymTab* symtab = Node_x_symtab(def_mod);
      def_node = SymTabResolveImported(symtab, node);
      if (def_node.isnull()) {
        CompilerError(Node_srcloc(node))
            << "unknown imported symbol " << Node_name(node);
      }
    } else {
      def_node = SymTabResolveWithFallback(symtab, node, builtin_symtab);
      if (def_node.isnull()) {
        if (kind == NT::MacroInvoke) {
          CompilerError(Node_srcloc(node))
              << "invocation of unknown macro " << Node_name(node);
        } else {
          if (runs_outside_fun && !IsPointNode(node, parent)) {
            CompilerError(Node_srcloc(node))
                << "unknown global symbol " << Node_name(node);
          }
          return false;
        }
      }
    }

    if (kind == NT::Id && !Node_enum_name(node).isnull()) {
      def_node = ResolveEnum(node, def_node);
    }
    // std::cout << "SymTabResolved: " << Node_name(node) << "\n";
    AnnotateNodeSymbol(node, def_node);
    return false;
  };
  VisitNodesRecursivelyPre(node, visitor, kNodeInvalid);
}

void ResolveGlobalAndImportedSymbolsOutsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab) {
  for (Node mod : mods) {
    // std::cout << "ResolveGlobalAndImportedSymbolsOutsideFunctionsAndMacros "
    //           << Node_name(mod) << "\n";
    const SymTab* symtab = Node_x_symtab(mod);
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(Node(child))) {
      if (Node_kind(child) != NT::DefFun && Node_kind(child) != NT::DefMacro) {
        ResolveGlobalAndImportedSymbols(child, symtab, builtin_symtab, true);
      }
    }
  }
}

void ResolveGlobalAndImportedSymbolsInsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab) {
  for (Node mod : mods) {
    // std::cout << "ResolveGlobalAndImportedSymbolsInsideFunctionsAndMacros "
    //           << Node_name(mod) << "\n";
    const SymTab* symtab = Node_x_symtab(mod);
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(Node(child))) {
      if (Node_kind(child) == NT::DefFun || Node_kind(child) == NT::DefMacro) {
        ResolveGlobalAndImportedSymbols(child, symtab, builtin_symtab, false);
      }
    }
  }
}

void ResolveSymbolInsideFunction(Node node, const SymTab* builtin_symtab,
                                 std::vector<SymTab>* scopes) {
  ASSERT(Node_kind(node) == NT::Id, "");
  if (!Node_x_symbol(node).isnull()) return;
  Name name = Node_name(node);
  for (auto it = scopes->rbegin(); it != scopes->rend(); ++it) {
    auto def_node = it->find(name);
    if (def_node != it->end()) {
      AnnotateNodeSymbol(node, def_node->second);
      return;
    }
  }
  CompilerError(Node_srcloc(node))
      << "unknown local symbol " << name << " " << node.index() << " "
      << EnumToString(Node_kind(Node_x_symbol(node)));
  return;
}

void FunResolveSymbolsInsideFunctions(Node fun, const SymTab* builtin_symtab,
                                      std::vector<SymTab>* scopes) {
  auto visitor = [builtin_symtab, scopes](Node node, Node parent) {
    if (Node_kind(node) == NT::Id) {
      if (!IsFieldNode(node, parent)) {
        ResolveSymbolInsideFunction(node, builtin_symtab, scopes);
      }
    } else if (Node_kind(node) == NT::DefVar) {
      auto ss = Node_name(node);
      if (scopes->back().contains(ss)) {
        CompilerError(Node_srcloc(node)) << "duplicate symbol " << ss;
      }
      scopes->back()[ss] = node;
    }
  };

  auto scope_enter = [scopes](Node node) {
    scopes->push_back(SymTab());
    if (Node_kind(node) == NT::DefFun) {
      for (Node p = Node_params(node); !p.isnull(); p = Node_next(p)) {
        // td::cout << "Adding param " << Node_name(p) << "\n";
        auto ss = Node_name(p);
        if (scopes->back().contains(ss)) {
          CompilerError(Node_srcloc(node)) << "duplicate symbol " << ss;
        }
        scopes->back()[ss] = p;
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
    for (Node fun = Node_body_mod(mod); !fun.isnull(); fun = Node_next(fun)) {
      if (Node_kind(fun) == NT::DefFun) {
        scopes.clear();
        FunResolveSymbolsInsideFunctions(fun, builtin_symtab, &scopes);
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
          if (Node_label(node).isnull() ||
              Node_label(node) == Node_label(*it)) {
            Node_x_target(node) = *it;
            return;
          }
        }
      }
      CompilerError(Node_srcloc(node))
          << "cannot find target for " << EnumToString(Node_kind(node));
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