#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
namespace cwerg::fe {
class TypeCorpus {
 public:
  TypeCorpus () {}
};
void DecorateASTWithTypes(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus);

}  // namespace cwerg::fe
