#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <vector>

#include "FE/cwast_gen.h"

namespace cwerg::fe {
bool HasImportedSymbolReference(Node node);

void ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab,
    bool must_resolve_all);

void ResolveSymbolsInsideFunctions(const std::vector<Node>& mods,
                                   const SymTab* builtin_symtab);

void SetTargetFields(const std::vector<Node>& mods);

void VerifySymbols(Node node);

}  // namespace cwerg::fe
