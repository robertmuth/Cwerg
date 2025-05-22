#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <vector>

#include "FE/cwast_gen.h"

namespace cwerg::fe {
extern bool HasImportedSymbolReference(Node node);

extern void ResolveGlobalAndImportedSymbolsOutsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab);

extern void ResolveGlobalAndImportedSymbolsInsideFunctionsAndMacros(
    const std::vector<Node>& mods, const SymTab* builtin_symtab);

extern void ResolveSymbolsInsideFunctions(const std::vector<Node>& mods,
                                          const SymTab* builtin_symtab);

extern void SetTargetFields(const std::vector<Node>& mods);

extern void UpdateNodeSymbolForPolyCall(Node callee, Node called_fun);

extern void VerifySymbols(Node node);

extern bool IsFieldNode(Node node, Node parent);


extern bool IsPointNode(Node node, Node parent);

}  // namespace cwerg::fe
