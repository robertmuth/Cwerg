

// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

extern void FunRemoveParentheses(Node fun);

extern void FunReplaceTypeOfAndTypeUnionDelta(Node node);

extern void FunReplaceExprIndex(Node node, TypeCorpus* tc);

extern void FunReplaceConstExpr(Node node, const TypeCorpus& tc);

}  // namespace cwerg::fe