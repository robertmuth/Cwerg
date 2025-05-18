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

extern std::vector<CanonType>& CanonType_children(CanonType n);

extern Node CanonType_lookup_rec_field(CanonType ct, Name field);

inline CanonType CanonType_underlying_vec_type(CanonType n) {
  ASSERT(CanonType_kind(n) == NT::TypeVec, "");
  return CanonType_children(n)[0];
}

inline CanonType CanonType_underlying_span_type(CanonType n) {
  ASSERT(CanonType_kind(n) == NT::TypeSpan, "");
  return CanonType_children(n)[0];
}

extern BASE_TYPE_KIND CanonType_base_type_kind(CanonType n);

inline bool CanonType_IsNumber(CanonType n) {
  return IsNumber(CanonType_base_type_kind(n));
}

class TypeCorpus {
  std::map<Name, CanonType> corpus_;

  std::map<BASE_TYPE_KIND, CanonType> base_type_map_;
  const TargetArchConfig& arch_;

  CanonType Insert(CanonType ct);
  CanonType InsertBaseType(BASE_TYPE_KIND kind);

 public:
  TypeCorpus(const TargetArchConfig& arch);

  CanonType get_base_canon_type(BASE_TYPE_KIND kind) {
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
