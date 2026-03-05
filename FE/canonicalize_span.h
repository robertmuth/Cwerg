// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {

// may insert new untagged union type
extern void MakeAndRegisterSpanTypeReplacements(TypeCorpus* tc, NodeChain* out);

extern void ReplaceSpans(Node mod);

}  // namespace cwerg::fe