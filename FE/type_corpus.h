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

class TypeCorpus {
  std::map<Name, CanonType> corpus_;

  void Insert(CanonType ct);

  public:
  TypeCorpus(const TargetArchConfig& arch);

  void InsertPtrType(bool mut, CanonType child);
  void InsertSpanType(bool mut, CanonType child);
  void InsertWrappedType(CanonType child);
  void InsertVecType(int dim, CanonType child);
  void InsertRecType(std::string_view name, Node ast_node);
  void InsertEnumType(std::string_view name, BASE_TYPE_KIND base_type, Node ast_node);
  void InsertUnionType(bool untagged,
                       const std::vector<CanonType>& sorted_children);
  void InsertFunType(const std::vector<CanonType>& params_result);
};

}  // namespace cwerg::fe
