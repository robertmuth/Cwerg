#pragma once

#include <cstdint>
#include <string_view>
#include <unordered_set>

namespace cwerg {

class ImmutablePool {
 public:
  ImmutablePool(size_t alignment)
      : data_(new char[16 * 1024 * 1024]),
        reserved_(16 * 1024 * 1024),
        alignment_(alignment) {
    AddData({"\0", 1}, alignment - 1);
  }

  uint32_t Intern(std::string_view data, uint32_t padding = 0);

  const char* Data(uint32_t pos) { return data_ + pos; }

 private:
  char* const data_;
  size_t reserved_ = 0;
  size_t used_ = 0;
  const size_t alignment_;

  std::unordered_set<std::string_view> views_;

  char* AddData(std::string_view data, uint32_t padding);
};

}  // namespace cwerg
