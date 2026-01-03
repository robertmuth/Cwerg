

#include "FE/canonicalize_large_args.h"

#include <array>

#include "FE/canonicalize.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/typify.h"

namespace cwerg::fe {

void FindFunSigsWithLargeArgs(TypeCorpus* tc) {}

void FunRewriteLargeArgsCallerSide(Node fun, TypeCorpus* tc) {}

void FunRewriteLargeArgsCalleeSide(Node fun, CanonType new_sig,
                                   TypeCorpus* tc) {}
}  // namespace cwerg::fe