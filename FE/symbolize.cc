
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

Node SymTabResolveSym(const SymTab* symtab, Node node,
                      const SymTab* builtin_symtab, bool must_be_public) {
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
  if (out == kNodeInvalid) {
    out = SymTabResolveNameWithVisibilityCheck(
        builtin_symtab, name, must_be_public, Node_srcloc(node));
  }
  return out;
}

void AnnotateNodeSymbol(Node node, Node def_node) {
  ASSERT(Node_kind(node) == NT::Id, "");
  ASSERT(Node_x_symbol(node) == kNodeInvalid, "");
  Node_x_symbol(node) = def_node;
}

void HelperResolveSymbolsOutsideFunctionsAndMacros(
    Node node, const SymTab* builtin_symtab, bool must_resolve_all) {
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
    Node def_node = SymTabResolveSym(ref_symtab, node, builtin_symtab,
                                     HasImportedSymbolReference(node));
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
        HelperResolveSymbolsOutsideFunctionsAndMacros(
            child, builtin_symtab, must_resolve_all);
      }
    }
  }
}

void ResolveSymbolsInsideFunctions(const std::vector<Node>& mods,
                                   const SymTab* builtin_symtab) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        //
      }
    }
  }
}

void SetTargetFields(const std::vector<Node>& mods) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefFun) {
        //
      }
    }
  }
}

void VerifySymbols(Node node) {}

}  // namespace cwerg::fe