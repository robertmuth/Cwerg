#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <vector>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {
extern void TypeCheckAst(const std::vector<Node>& mods, TypeCorpus* tc,
                         bool strict);

extern void AddTypesToAst(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus);

extern void ModStripTypeNodesRecursively(Node node);

}  // namespace cwerg::fe
