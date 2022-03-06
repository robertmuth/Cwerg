#pragma once

#include <cstdint>
#include <string_view>
#include <unordered_set>

namespace cwerg {

// ImmutablePool is used to store immutable byte sequences. If the byte sequence has 
// been stored before it will not be stored again. 
// The Byte sequence are identified by a uint32_t offset which will never change.  
// The offset is guranteed to be aligned by `alignment`.
// An empty byte sequence is identified by offset zero.
// Once stored byte sequences cannot be deleted from the pool, so it keeps growing.  
// The accumulated size of unique byte sequences stored must not overflow 
// 32 bits (about 4GB). 
class ImmutablePool {
 public:
  ImmutablePool(size_t alignment)
      : data_(new char[16 * 1024 * 1024]),
        reserved_(16 * 1024 * 1024),
        alignment_(alignment) {
    // Make zero is never returned as a valid offset.
    AddData({"\0", 1}, alignment - 1);
  }

  // Insert the byte sequence `data` if it does not exist already.
  // Also append at least `padding` bytes of zeros. The actual number
  // can be higher to satify alignment requirements. The paddding is 
  // not considered for determining if the sequence exists already.
  uint32_t Intern(std::string_view data, uint32_t padding = 0);

  // Given a uint32_t returned by `Intern()` get a pointer to the actual data.
  // The pointer is valid until the next call to `Intern()`.
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
