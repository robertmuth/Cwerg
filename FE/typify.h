#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <vector>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {

void DecorateASTWithTypes(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus);

}  // namespace cwerg::fe
