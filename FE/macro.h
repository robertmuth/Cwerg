#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <map>

#include "FE/cwast_gen.h"
#include "FE/identifier.h"
#include "Util/assert.h"

namespace cwerg::fe {

void ExpandMacrosAndMacroLike(const std::vector<Node>& mods,
                              const SymTab* builtin_symtab,
                              IdGenCache* id_gen_cache);
}  // namespace cwerg::fe
