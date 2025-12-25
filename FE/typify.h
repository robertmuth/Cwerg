#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <span>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {
extern void TypeCheckAst(const std::vector<Node>& mods, TypeCorpus* tc,
                         bool strict);

extern void AddTypesToAst(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus);

extern void ModStripTypeNodesRecursively(Node node);

struct NameAndType {
  Name name;
  CanonType ct;
};

extern Node MakeDefRec(Name name, std::span<NameAndType> fields,
                       TypeCorpus* tc);

}  // namespace cwerg::fe
