#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <cstdint>
#include <filesystem>
#include <set>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

// only used for interning comment strings
#include "FE/cwast_gen.h"

namespace cwerg::fe {
bool HasImportedSymbolReference(Node node);

void ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
    const std::vector<Node>& modules, const SymTab* builtin_symtab,
    bool must_resolve_all);

}  // namespace cwerg::fe
