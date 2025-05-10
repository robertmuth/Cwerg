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
 public:
  TypeCorpus(const TargetArchConfig& arch);
};

}  // namespace cwerg::fe
