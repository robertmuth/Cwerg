#include "FE/checker.h"

#include <array>
#include <map>
#include <set>

#include "Util/assert.h"

namespace cwerg::fe {

void ValidateAST(const std::vector<Node>& mods) {
  bool verbose = true;
  std::cout << "@@@ CHECKING ############\n";
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
  std::cout << "improperly unlinked nodes " << n << " " << total << "\n";
}

}  // namespace cwerg::fe