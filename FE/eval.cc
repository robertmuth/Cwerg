#include "FE/eval.h"

#include <set>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"
#include "Util/handle.h"

namespace cwerg::fe {
namespace {
}  // namespace

struct Stripe<ConstCore, Const> gConstCore("ConstCore");

StripeBase* const gAllStripesConst[] = {&gConstCore, nullptr};
struct StripeGroup gStripeGroupConst("Const", gAllStripesConst, 256 * 1024);
}  // namespace cwerg::fe