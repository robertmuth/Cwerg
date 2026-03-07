#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

void FunEliminateDefer(Node fun);

void FunAddMissingReturnStmts(Node fun);

void FunCanonicalizeRemoveStmtCond(Node fun);

void ModVerifyFunFallthrus(Node mod);

}  // namespace cwerg::fe