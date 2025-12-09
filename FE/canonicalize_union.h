// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

// may insert new untagged union type
extern void FunSimplifyTaggedExprNarrow(Node fun, TypeCorpus* tc);

}  // namespace cwerg::fe