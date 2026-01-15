#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

extern void MakeAndRegisterLargeArgReplacements(TypeCorpus* tc);

extern void FunRewriteLargeArgsCallsites(Node fun, TypeCorpus* tc);

extern void FunRewriteLargeArgsParameter(Node fun, CanonType old_sig,
                                         CanonType new_sig, TypeCorpus* tc);

}  // namespace cwerg::fe