#pragma once

#include <cstdint>
#include <string_view>
#include <unordered_set>

namespace cwerg {

// ImmutablePool is used to store immutable byte sequences. If the byte sequence has
// been stored before it will not be stored again.
// This makes it suitable got interning strings.
// The Byte sequence are identified by a uint32_t offset which will never change.
// The offset is guaranteed to be aligned by `alignment`.
// Once stored a byte sequences cannot be deleted from the pool, so the pool keeps growing.
// The accumulated size of unique byte sequences stored must not overflow
// 32 bits (about 4GB).
class ImmutablePool {
 public:
  ImmutablePool(size_t alignment)
      : data_(new char[16 * 1024 * 1024]),
        reserved_(16 * 1024 * 1024),
        alignment_(alignment) {
    // Fill first slot so that 0 is never returned as a valid offset.
    AddData({"\0", 1}, alignment - 1);
  }

  // Insert the byte sequence `data` if it does not exist already.
  // Also append at least `padding` bytes of zeros. The actual number
  // can be higher to satify alignment requirements. The paddding is
  // not considered for determining if the sequence exists already.
  // Note that Intern:
  // * will never return 0 so this value can be used to
  //   like a nullptr.
  // * does not store the length of `data` internally. So the caller has
  //   remember the size or encode it in the data.
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
