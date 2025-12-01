#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {

enum class COMPILE_STAGE : uint8_t {
  AFTER_PARSING,
  AFTER_SYMBOLIZE,
  AFTER_TYPIFY,
  AFTER_EVAL,
  AFTER_DESUGAR,
};

extern void ValidateAST(const std::vector<Node>& mods, COMPILE_STAGE stage);
}  // namespace cwerg::fe
