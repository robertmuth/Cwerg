// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

// may insert new untagged union type
extern NodeChain MakeAndRegisterSpanTypeReplacements(TypeCorpus* tc);

extern void ReplaceSpans(Node mod);

}  // namespace cwerg::fe