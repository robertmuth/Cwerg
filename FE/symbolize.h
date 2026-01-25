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

// Return value for each field of the Rec.
// If we have a ValPoint for a field thay ValkPoint is
// returned otherwise kNodeInvalid.
// The field can be retrieved using the curr_field member.
// If curr_field is null the iteration is done.
class IterateValRec {
 public:
  IterateValRec(Node points, Node fields)
      : point_next_(points), field_next_(fields) {}

  Node next() {
    curr_field = field_next_;
    if (curr_field.isnull()) return kNodeInvalid;
    field_next_ = Node_next(field_next_);
    if (point_next_.isnull()) {
      return kNodeInvalid;
    }
    if (Node_point_or_undef(point_next_).kind() == NT::ValUndef) {
      Node out = point_next_;
      point_next_ = Node_next(point_next_);
      return out;
    }
    ASSERT(Node_point_or_undef(point_next_).kind() == NT::Id, "");

    if (Node_name(curr_field) == Node_name(Node_point_or_undef(point_next_))) {
      Node out = point_next_;
      point_next_ = Node_next(point_next_);
      return out;
    }
    return kNodeInvalid;
  }

  Node curr_field = kNodeInvalid;

 private:
  Node point_next_;
  Node field_next_;
};


}  // namespace cwerg::fe
