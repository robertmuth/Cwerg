#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
namespace cwerg::fe {

struct TargetArchConfig {
  int uint_bitwidth;
  int sint_bitwidth;
  int typeid_bitwidth;
  int data_addr_bitwidth;
  int code_addr_bitwidth;
};

constexpr TargetArchConfig STD_TARGET_X64 = {64, 64, 16, 64, 64};
constexpr TargetArchConfig STD_TARGET_A64 = {64, 64, 16, 64, 64};
constexpr TargetArchConfig STD_TARGET_A32 = {32, 32, 16, 32, 32};

extern Name CanonType_name(CanonType n);
extern NT CanonType_kind(CanonType n);

class TypeCorpus {
  std::map<Name, CanonType> corpus_;

  CanonType Insert(CanonType ct);

 public:
  TypeCorpus(const TargetArchConfig& arch);

  CanonType InsertPtrType(bool mut, CanonType child);
  CanonType InsertSpanType(bool mut, CanonType child);
  CanonType InsertWrappedType(CanonType child);
  CanonType InsertVecType(int dim, CanonType child);
  CanonType InsertRecType(std::string_view name, Node ast_node);
  CanonType InsertEnumType(std::string_view name, BASE_TYPE_KIND base_type,
                           Node ast_node);
  CanonType InsertUnionType(bool untagged,
                            const std::vector<CanonType>& components);
  CanonType InsertFunType(const std::vector<CanonType>& params_result);
};

}  // namespace cwerg::fe
