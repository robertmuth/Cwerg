#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <vector>

#include "FE/cwast_gen.h"
#include "Util/assert.h"
namespace cwerg::fe {

struct TargetArchConfig {
  int uint_bitwidth;
  int sint_bitwidth;
  int typeid_bitwidth;
  int data_addr_bitwidth;
  int code_addr_bitwidth;

  inline int get_address_size() const { return data_addr_bitwidth / 8; }
};

constexpr TargetArchConfig STD_TARGET_X64 = {64, 64, 16, 64, 64};
constexpr TargetArchConfig STD_TARGET_A64 = {64, 64, 16, 64, 64};
constexpr TargetArchConfig STD_TARGET_A32 = {32, 32, 16, 32, 32};

extern Name CanonType_name(CanonType n);
extern NT CanonType_kind(CanonType n);
extern Node CanonType_ast_node(CanonType n);
extern bool CanonType_mut(CanonType n);
extern bool CanonType_untagged(CanonType ct);
extern int CanonType_alignment(CanonType n);
extern int CanonType_size(CanonType n);
extern std::vector<CanonType>& CanonType_children(CanonType n);

extern Node CanonType_lookup_rec_field(CanonType ct, Name field);

inline CanonType CanonType_underlying_type(CanonType n) {
  ASSERT(CanonType_children(n).size() == 1, "");
  return CanonType_children(n)[0];
}

extern BASE_TYPE_KIND CanonType_get_unwrapped_base_type_kind(CanonType n);

extern CanonType CanonType_get_unwrapped(CanonType n);

inline std::ostream& operator<<(std::ostream& os, CanonType ct) {
  return os << CanonType_name(ct);
}

inline bool IsTypeForCmp(CanonType ct) {
  CanonType unwrapped = CanonType_get_unwrapped(ct);
  return CanonType_kind(unwrapped) == NT::TypeBase ||
         CanonType_kind(unwrapped) == NT::TypePtr;
}

inline bool IsTypeForEq(CanonType ct) {
  CanonType unwrapped = CanonType_get_unwrapped(ct);
  return CanonType_kind(unwrapped) == NT::TypeFun ||
         CanonType_kind(unwrapped) == NT::TypeBase ||
         CanonType_kind(unwrapped) == NT::TypePtr;
}

extern bool IsCompatibleTypeForEq(CanonType op1, CanonType op2);
extern bool IsCompatibleTypeForCmp(CanonType op1, CanonType op2);
extern bool IsCompatibleTypeForAs(CanonType src, CanonType dst);
extern bool IsCompatibleTypeForBitcast(CanonType src, CanonType dst);
extern bool IsProperLhs(Node node);

class TypeCorpus {
  std::map<Name, CanonType> corpus_;

  std::map<BASE_TYPE_KIND, CanonType> base_type_map_;
  const TargetArchConfig& arch_;

  CanonType Insert(CanonType ct);
  CanonType InsertBaseType(BASE_TYPE_KIND kind);

 public:
  TypeCorpus(const TargetArchConfig& arch);

  CanonType get_base_canon_type(BASE_TYPE_KIND kind) {
    ASSERT(kind != BASE_TYPE_KIND::INVALID, "");
    return base_type_map_[kind];
  }

  CanonType get_void_canon_type() {
    return base_type_map_[BASE_TYPE_KIND::VOID];
  }
  CanonType get_bool_canon_type() {
    return base_type_map_[BASE_TYPE_KIND::BOOL];
  }

  CanonType get_sint_canon_type() {
    return base_type_map_[BASE_TYPE_KIND::SINT];
  }

  CanonType get_uint_canon_type() {
    return base_type_map_[BASE_TYPE_KIND::UINT];
  }

  CanonType get_typeid_canon_type() {
    return base_type_map_[BASE_TYPE_KIND::TYPEID];
  }

  CanonType InsertPtrType(bool mut, CanonType child);
  CanonType InsertSpanType(bool mut, CanonType child);
  CanonType InsertVecType(int dim, CanonType child);

  CanonType InsertRecType(std::string_view name, Node ast_node);
  CanonType InsertEnumType(std::string_view name, Node ast_node);
  CanonType InsertUnionType(bool untagged,
                            const std::vector<CanonType>& components);
  CanonType InsertFunType(const std::vector<CanonType>& params_result);
  CanonType InsertWrappedTypePre(std::string_view name);
  void InsertWrappedTypeFinalize(CanonType ct, CanonType wrapped_type);
  CanonType InsertUnionComplement(CanonType minuend, CanonType subtrahend);

  void Dump();
};

}  // namespace cwerg::fe
