#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"

namespace cwerg::fe {

enum class CompileStage : uint8_t {
  AfterParsing,
  AfterSymbolization,
  AfterTyping
};

extern void ValidateAST(const std::vector<Node>& mods, CompileStage stage);
}  // namespace cwerg::fe
