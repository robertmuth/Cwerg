#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Util/handle.h"
#include <cstdint>

namespace cwerg {

// This is also the max number of registers a function can have if
// we want to run a reaching definitions analysis.
// There are way to work around this should this become an issue:
// * dedicate more bits to the width part of the index
// * only track registers that are not live across Bbls
//   (this is less desirable because sometimes we would like
//    to if a register is visible in another Bbl even currently
//    that register is local to its Bbl)
constexpr const unsigned HANDLEVEC_MAX_ENTRIES = 8 * 255;

// Represents an array of Handles.
// Max size is HANDLEVEC_MAX_ENTRIES
struct HandleVec {
  // Note: if bv has zero length Del is a nop
  static HandleVec New(unsigned num_entries);

  static void Del(HandleVec hv);

  unsigned raw_width() const { return index & 0xff; }
  unsigned byte_width() const { return 32 * raw_width(); }
  unsigned entry_width() const { return 8 * raw_width(); }

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
