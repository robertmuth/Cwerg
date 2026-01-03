#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {
extern void FindFunSigsWithLargeArgs(TypeCorpus* tc);

extern void FunRewriteLargeArgsCallerSide(Node fun, TypeCorpus* tc);

extern void FunRewriteLargeArgsCalleeSide(Node fun, CanonType new_sig,
                                          TypeCorpus* tc);

}  // namespace cwerg::fe