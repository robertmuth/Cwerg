// (c) Robert Muth - see LICENSE for more info

#include "Util/immutable.h"
#include "Util/assert.h"

#include "memory.h"

namespace cwerg {
namespace {
uint32_t align(uint32_t x, uint32_t alignment) {
  if (alignment <= 1) return x;
  return (x + alignment - 1) / alignment * alignment;
}

}  // namespace

char* ImmutablePool::AddData(std::string_view data, uint32_t padding) {
  uint64_t total_size = data.size() + padding;
  ASSERT(reserved_ >= used_ + total_size, "realloc must have failed");
  uint32_t out = used_;
  data.copy(data_ + out, data.size());
  memset(data_ + out + data.size(), 0, padding);
  used_ += total_size;
  return data_ + out;
}

uint32_t ImmutablePool::Intern(std::string_view data, uint32_t padding) {
  auto it = views_.find(data);
  if (it != views_.end()) return it->data() - data_;
  const uint32_t total_size = align(data.size() + padding, alignment_);
  const char* pos = AddData(data, total_size - data.size());
  views_.insert({pos, data.size()});
  return pos - data_;
}

}  // namespace cwerg
