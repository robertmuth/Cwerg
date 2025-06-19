#include "FE/checker.h"

#include <array>
#include <map>
#include <set>

#include "Util/assert.h"
#include "Util/switch.h"

namespace cwerg::fe {
namespace {
SwitchBool sw_verbose("verbose_checks", "make checking more verbose");

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

bool IsTyped(NT nt) {
  switch (nt) {
    case NT::Id:
    case NT::TypeAuto:
    case NT::FunParam:
    case NT::TypeBase:
    case NT::TypePtr:
    case NT::TypeSpan:
    case NT::TypeVec:
    case NT::TypeFun:
    case NT::TypeUnion:
    case NT::TypeUnionDelta:
    case NT::TypeOf:
    case NT::ValAuto:
    case NT::ValNum:
    case NT::ValVoid:
    case NT::ValPoint:
    case NT::ValCompound:
    case NT::ValSpan:
    case NT::ValString:
    case NT::Expr1:
    case NT::Expr2:
    case NT::Expr3:
    case NT::ExprDeref:
    case NT::ExprAddrOf:
    case NT::ExprCall:
    case NT::ExprParen:
    case NT::ExprField:
    case NT::ExprPointer:
    case NT::ExprIndex:
    case NT::ExprLen:
    case NT::ExprFront:
    case NT::ExprIs:
    case NT::ExprWrap:
    case NT::ExprUnwrap:
    case NT::ExprAs:
    case NT::ExprNarrow:
    case NT::ExprWiden:
    case NT::ExprBitCast:
    case NT::ExprTypeId:
    case NT::ExprUnionTag:
    case NT::ExprUnionUntagged:
    case NT::ExprSizeof:
    case NT::ExprOffsetof:
    case NT::ExprStmt:
    case NT::EnumVal:
    case NT::DefEnum:
    case NT::DefType:
    case NT::DefVar:
    case NT::DefGlobal:
    case NT::DefFun:
    case NT::ExprStringify:
    case NT::RecField:
    case NT::DefRec:
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
        ASSERT(!symbol.isnull(), "no symbol for " << node << " "
                                                  << Node_name_or_invalid(node)
                                                  << " " << Node_srcloc(node));
        ASSERT(NodeIsPossibleSymbol(symbol), "no symbol but " << symbol);
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

void ValidateAST(const std::vector<Node>& mods, COMPILE_STAGE stage) {
  for (int i = kStripeGroupFirstAlloc; i < gStripeGroupNode.NextAvailable();
       ++i) {
    gNodeValidation[i].ref_count = 0;
  }

  // mark
  auto mark = [](Node node, Node parent) -> bool {
    if (Node_kind(node) == NT::invalid) {
      ASSERT(false,
             "freed node " << node.index() << "still reference was " << node);
    }
    if (gNodeValidation[node].ref_count) {
      ASSERT(false, "duplicate linked node");
    }
    gNodeValidation[node].ref_count = true;
    return false;
  };

  for (Node mod : mods) {
    if (sw_verbose.Value())
      std::cout << "Validate Mod: " << Node_name(mod) << "\n";
    VisitAstRecursivelyPre(mod, mark, kNodeInvalid);
  }

  int live = 0;
  int freed = 0;
  for (int i = kStripeGroupFirstAlloc; i < gStripeGroupNode.NextAvailable();
       ++i) {
    Node node(NT::invalid, i);
#if 0
    std::cout << i << " " << gNodeValidation[i].ref_count << " "
              << EnumToString(gNodeCore[i].kind) << " "
              << Node_name_or_invalid(node) << "\n";
#endif
    auto& core = gNodeCore[i];
    if (!gNodeValidation[i].ref_count) {
      ++freed;
      ASSERT(core.kind == NT::invalid,
             "orphaned node " << i << " " << EnumToString(core.kind) << " "
                              << Node_name_or_invalid(node) << " "
                              << Node_srcloc(node) << "\n");
      continue;
    }
    for (int j = 0; j < MAX_NODE_CHILDREN; ++j) {
      Node child = core.children_node[j];
      if (!NodeIsNode(child)) continue;
      ASSERT(child.kind() == Node_kind(child),
             "node mismatch " << child << " vs "
                              << EnumToString(Node_kind(child))
                              << " kind=" << int(child.kind()) << " "
                              << int(Node_kind(child)));
    }
    ASSERT(core.kind != NT::invalid, "");
    ++live;

    node = Node(core.kind, i);
    CanonType ct = Node_x_type(node);
    if (stage >= COMPILE_STAGE::AFTER_TYPIFY) {
      if (IsTyped(core.kind)) {
        ASSERT(!ct.isnull(), "missing type for " << node << " "
                                                 << Node_srcloc(node)
                                                 << Node_name_or_invalid(node));
      }
    } else {
      ASSERT(ct.isnull(), "unexpected type for "
                              << node << " " << Node_srcloc(node) << " " << ct);
    }
  }

  if (stage >= COMPILE_STAGE::AFTER_SYMBOLIZE) {
    for (Node mod : mods) {
      VisitAstRecursivelyPre(mod, NodeValidateSymbols, kNodeInvalid);
    }
  }

  if (sw_verbose.Value()) {
    std::cout << "Node Stats: live=" << live << " freed=" << freed
              << " total=" << live + freed << "\n";
  }
}

}  // namespace cwerg::fe