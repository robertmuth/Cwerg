#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>
#include <iostream>

namespace cwerg {

constexpr const unsigned BITVEC_MAX_BITS = 64 * 255;  // = 16320

struct BitVec {
  // BITVEC_MAX_BITS is the maximum number of bits in a bit vector.
  // Since we are using them for register liveness, this is also a limit
  // on the number of registers per Fun.
  static BitVec New(unsigned num_bits);

  // Note: if bv has zero length Del is a nop
  static void Del(BitVec bv);

  unsigned raw_width() const { return index & 0xff; }
  unsigned byte_width() const { return 8 * raw_width(); }
  unsigned bit_width() const { return 64 * raw_width(); }

  uint64_t* BackingStorage() const;

  void BitSet(unsigned bit);

  void BitClear(unsigned bit);

  bool BitGet(unsigned bit) const;

  void AndWith(BitVec other);

  void AndNotWith(BitVec other);

  void OrWith(BitVec other);

  void OrNotWith(BitVec other);

  void CopyFrom(BitVec other);

  void Clear();

  bool Equal(BitVec other) const;

  bool Intersects(BitVec other) const;

  bool operator==(const BitVec& other) const { return index == other.index; }
  bool operator!=(const BitVec& other) const { return index != other.index; }

  unsigned Popcnt() const;
  // Encodes both the width and an offset into backing storage
  // Currently see encoding is:
  // top 24 bits: MemPool index
  // low 8 bits: MemPool size
  // We can increase the width of the size field if necessary
  uint32_t index;
};

constexpr const BitVec BitVecInvalid{0};

extern std::ostream& operator<<(std::ostream& os, const BitVec& bv);

}  // namespace cwerg
