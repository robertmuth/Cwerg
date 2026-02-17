#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>

#include "Util/handle.h"

namespace cwerg {

// This is also the max number of registers a function can have if
// we want to run a reaching definitions analysis.
// There are way to work around this should this become an issue:
// * dedicate more bits to the width part of the index
// * only track registers that are not live across Bbls
//   (this is less desirable because sometimes we would like
//    to if a register is visible in another Bbl even currently
//    that register is local to its Bbl)
constexpr const unsigned HANDLEVEC_CHUNCK_BYTE_SIZE = 32;
constexpr const unsigned HANDLEVEC_NUM_CHUNK_BITS = 8;
constexpr const unsigned HANDLEVEC_HANDLES_PER_CHUNK =
    HANDLEVEC_CHUNCK_BYTE_SIZE / sizeof(Handle);

// Represents an array of Handles.
// Max size is HANDLEVEC_MAX_ENTRIES
struct HandleVec {
  // Note: if bv has zero length Del is a nop
  static HandleVec New(unsigned num_entries);

  static void Del(HandleVec hv);

  unsigned chunk_offset() const { return index >> HANDLEVEC_NUM_CHUNK_BITS; }
  unsigned num_chunks() const {
    return index & ((1 << HANDLEVEC_NUM_CHUNK_BITS) - 1);
  }
  unsigned num_bytes() const {
    return HANDLEVEC_CHUNCK_BYTE_SIZE * num_chunks();
  }
  unsigned num_handles() const {
    return HANDLEVEC_HANDLES_PER_CHUNK * num_chunks();
  }

  Handle* BackingStorage() const;

  void Set(unsigned pos, Handle handle);

  Handle Get(unsigned pos) const;

  void CopyFrom(HandleVec other);

  void ClearWith(Handle handle);

  bool Equal(HandleVec other) const;

  // encodes both the width and an offset into backing storage
  uint32_t index;
};

constexpr const HandleVec HandleVecInvalid{0};

}  // namespace cwerg
