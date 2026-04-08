#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

void FunEliminateDefer(Node fun);

void FunAddMissingReturnStmts(Node fun);

void FunCanonicalizeRemoveStmtCond(Node fun);

void ModVerifyFunFallthrus(Node mod);

Node MakeFiniFun(std::string_view name,
                 const std::vector<Node>& mod_in_topo_order, TypeCorpus* tc);

Node MakeInitFun(std::string_view name,
                 const std::vector<Node>& mod_in_topo_order, TypeCorpus* tc);
}  // namespace cwerg::fe