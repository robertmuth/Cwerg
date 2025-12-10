

// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

extern void FunRemoveParentheses(Node fun);

extern void FunReplaceTypeOfAndTypeUnionDelta(Node node);

// May add ... type
extern void FunReplaceExprIndex(Node node, TypeCorpus* tc);

extern void FunReplaceConstExpr(Node node, const TypeCorpus& tc);

// May add ... type
extern void FunMakeImplicitConversionsExplicit(Node node, TypeCorpus* tc);

extern void FunDesugarTaggedUnionComparisons(Node fun);

// May add ... types
extern void FunReplaceSpanCastWithSpanVal(Node fun, TypeCorpus* tc);

extern bool IsNodeCopyableWithoutRiskOfSideEffects(Node node);

extern Node MakeNodeCopyableWithoutRiskOfSideEffects(Node lhs, NodeChain* stmts,
                                                     bool is_lhs);
extern void FunDesugarExprIs(Node fun, const TypeCorpus* tc);

extern void FunRemoveUselessCast(Node fun);

extern void FunEliminateDefer(Node fun);

extern void FunCanonicalizeBoolExpressionsNotUsedForConditionals(Node fun);

}  // namespace cwerg::fe