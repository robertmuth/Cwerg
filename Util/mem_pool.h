#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Util/assert.h"

#include <cstdint>
#include <memory.h>
#include <iostream>

namespace cwerg {

// Memory pool for variable size entities whose size must be a multiple
// of `BYTE_GRANULARITY`.
// The result of an allocation is not a pointer but an index into the pool.
// Use `BackingStorage` to get a pointer to the actual memory.
//
// The pool currently uses realloc when it runs out of memory,
// which may invalidate the pointer returned by `BackingStorage()`

template <int BYTE_GRANULARITY>
struct MemPool {
  uint8_t* data = nullptr;
  uint8_t* alloc_bitmap = nullptr;
  uint32_t allocated_size = 0;
  uint32_t first_free = 0;

  void UpdateBitmap(uint32_t start, uint32_t size, bool allocated) {
    for (unsigned i = 0; i < size; ++i) {
      unsigned pos = (start + i) / 8;
      unsigned bit = (start + i) % 8;
      if (allocated) {
        // TODO: this only holds if never use `Del`
        // ASSERT((alloc_bitmap[pos] & (1ull << bit)) == 0, "");
        alloc_bitmap[pos] |= (1ull << bit);
      } else {
        ASSERT((alloc_bitmap[pos] & (1ull << bit)), "");
        alloc_bitmap[pos] &= ~(1ull << bit);
      }
    }
  }

  // Allocate Storage
  // Size is in multiples of granularity
  uint32_t New(uint32_t size) {
    if (data == nullptr || first_free + size > allocated_size) {
      const bool first_alloc = (data == nullptr);
      uint32_t old_size = allocated_size;
      allocated_size += 1024 * 1024;
      data = (uint8_t*)realloc(data, allocated_size * BYTE_GRANULARITY);
      // 1 bit per element in data
      alloc_bitmap = (uint8_t*)realloc(alloc_bitmap, allocated_size / 8);
      memset(alloc_bitmap + old_size / 8, 0, (allocated_size - old_size) / 8);
      if (first_alloc) {
        // Make sure we never return a zero offset
        UpdateBitmap(0, 1, true);
        first_free = 1;
      }
    }

    uint32_t start = first_free;
    first_free += size;
    UpdateBitmap(start, size, true);
    return start;
  }

  // Free Storage, size must be the value or smaller that was used
  // as the parameter to `New()`
  void Del(uint32_t start, uint32_t size) {
    UpdateBitmap(start, size, false);
  }

  void* BackingStorage(uint32_t start) const {
    return data + start * BYTE_GRANULARITY;
  }

  uint32_t byte_granularity() const { return  BYTE_GRANULARITY; }
};

}  // namespace cwerg
