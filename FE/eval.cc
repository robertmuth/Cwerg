#include "FE/eval.h"

#include <set>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"
#include "Util/handle.h"

namespace cwerg::fe {
namespace {

Const EvalNode(Node node) {
  switch (Node_kind(node)) {
    case NT::DefVar:
      return kConstInvalid;

    default:
      return kConstInvalid;
  }
}

bool _EvalRecursively(Node mod) {
  bool seen_change = false;
  auto evaluator = [&seen_change](Node node, Node parent) {
    Const c = EvalNode(node);
    if (!c.isnull()) {
      Node_x_eval(node) = c;
      seen_change = true;
    }
  };

  VisitAstRecursivelyPost(mod, evaluator, kNodeInvalid);
  return seen_change;
}

}  // namespace

struct Stripe<ConstCore, Const> gConstCore("ConstCore");

StripeBase* const gAllStripesConst[] = {&gConstCore, nullptr};
struct StripeGroup gStripeGroupConst("Const", gAllStripesConst, 256 * 1024);

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods) {
  int iteration = 0;
  while (true) {
    ++iteration;
    bool seen_change = false;
    for (Node mod : mods) {
      for (Node node = Node_body_mod(mod); !node.isnull();
           node = Node_next(node)) {
        seen_change |= _EvalRecursively(node);
      }
    }
    if (!seen_change) break;
  }
}

}  // namespace cwerg::fe