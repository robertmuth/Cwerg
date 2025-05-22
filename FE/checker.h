#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {

extern void ValidateAST(const std::vector<Node>& mods, bool symbolized);
}  // namespace cwerg::fe
