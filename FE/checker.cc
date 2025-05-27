#include "FE/checker.h"

#include <array>
#include <map>
#include <set>

#include "Util/assert.h"

namespace cwerg::fe {
namespace {
bool NodeIsPossibleSymbol(Node symbol) {
  switch (Node_kind(symbol)) {
    case NT::DefMacro:
    case NT::DefFun:
    case NT::FunParam:
    case NT::DefType:
    case NT::DefGlobal:
    case NT::DefVar:
    case NT::DefRec:
    case NT::RecField:
    case NT::DefEnum:
    case NT::EnumVal:

      return true;

    default:
      return false;
  }
}
bool NodeIsPossibleTarget(Node target) {
  switch (Node_kind(target)) {
    case NT::DefFun:
    case NT::StmtBlock:
    case NT::ExprStmt:
      return true;

    default:
      return false;
  }
}

bool NodeValidateSymbols(Node node, Node parent) {
  switch (Node_kind(node)) {
    // x_symbol
    case NT::MacroInvoke:
    case NT::Id: {
      if (!IsPointNode(node, parent) && !IsFieldNode(node, parent)) {
        Node symbol = Node_x_symbol(node);
        ASSERT(!symbol.isnull(), "no symbol for "
                                     << EnumToString(Node_kind(node)) << " "
                                     << Node_name_or_invalid(node) << " "
                                     << Node_srcloc(node));
        ASSERT(NodeIsPossibleSymbol(symbol),
               "no symbol but " << EnumToString(Node_kind(symbol)));
      }
      break;
    }
    // x_target
    case NT::StmtBreak:
    case NT::StmtContinue:
    case NT::StmtReturn: {
      Node target = Node_x_target(node);
      ASSERT(NodeIsPossibleTarget(target), "");
      break;
    }
    case NT::DefFun:
      if (Node_has_flag(node, BF::POLY)) {
        ASSERT(!Node_x_poly_mod(node).isnull(),
               "poly DefMod must have valid x_poly_mod " << Node_name(node));
      }
      break;
    default:
      break;
  }
  return false;
}

}  // namespace

void ValidateAST(const std::vector<Node>& mods, bool symbolized) {
  bool verbose = true;
  for (int i = kStripeGroupFirstAlloc; i < gStripeGroupNode.NextAvailable();
       ++i) {
    gNodeValidation[i].ref_count = 0;
  }

  // mark
  auto mark = [](Node node, Node parent) -> bool {
    if (Node_kind(node) == NT::invalid) {
      ASSERT(false, "freed node " << node.index() << "still reference was "
                                  << EnumToString(node.kind()));
    }
    if (gNodeValidation[node].ref_count) {
      ASSERT(false, "duplicate linked node");
    }
    gNodeValidation[node].ref_count = true;
    return false;
  };

  for (Node mod : mods) {
    std::cout << "@@ VALIDATE: " << Node_name(mod) << "\n";
    VisitNodesRecursivelyPre(mod, mark, kNodeInvalid);
  }

  int n = 0;
  int total = 0;
  for (int i = kStripeGroupFirstAlloc; i < gStripeGroupNode.NextAvailable();
       ++i) {
    Node node(NT::invalid, i);
#if 0
    std::cout << i << " " << gNodeValidation[i].ref_count << " "
              << EnumToString(gNodeCore[i].kind) << " "
              << Node_name_or_invalid(node) << "\n";
#endif
    if (!gNodeValidation[i].ref_count) {
      auto& core = gNodeCore[i];
      if (core.kind != NT::invalid) {
        if (verbose) {
          std::cout << "orphaned node " << i << " " << EnumToString(core.kind)
                    << " " << Node_name_or_invalid(node) << " "
                    << Node_srcloc(node) << "\n";
        }
        ++n;
      }
    } else {
      ++total;
    }
  }
  if (symbolized) {
    for (Node mod : mods) {
      VisitNodesRecursivelyPre(mod, NodeValidateSymbols, kNodeInvalid);
    }
  }

  std::cout << "improperly unlinked nodes " << n << " " << total << "\n";
}

}  // namespace cwerg::fe