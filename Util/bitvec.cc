// (c) Robert Muth - see LICENSE for more info

#include "Util/bitvec.h"
#include "Util/assert.h"
#include "Util/list.h"
#include "Util/mem_pool.h"

#include <memory.h>

namespace cwerg {
namespace {

MemPool<8> GlobalBitVecStorage;

}  // namespace

BitVec BitVec::New(unsigned num_bits) {
  ASSERT(num_bits <= BITVEC_MAX_BITS, "too many bits requested " << num_bits);
  // granularity is uint64_t (8 bytes) which can hold 64bits
  const unsigned raw_width = (num_bits + 63) / 64;
  const uint32_t offset = GlobalBitVecStorage.New(raw_width);
  memset(GlobalBitVecStorage.BackingStorage(offset), 0, raw_width * 8);
  BitVec out = {offset << 8 | raw_width};
  out.Clear();
  return out;
}

/*
void BitVec::Realloc(BitVec* bv, unsigned num_bits) {
  if (bv->bit_width() < num_bits) {
    BitVec::Del(*bv);
    *bv = BitVec::New(num_bits);
  }
  bv->Clear();
}
 */

void BitVec::Del(BitVec bv) {
  if (bv.raw_width() == 0) return;
  GlobalBitVecStorage.Del(bv.index >> 8, bv.index & 0xff);
}

uint64_t* BitVec::BackingStorage() const {
  return static_cast<uint64_t*>(GlobalBitVecStorage.BackingStorage(index >> 8));
}

void BitVec::BitSet(unsigned bit) {
  ASSERT(bit < bit_width(), "");
  const uint64_t mask = 1ull << (bit % 64);
  BackingStorage()[bit / 64] |= mask;
}

void BitVec::BitVec::BitClear(unsigned bit) {
  ASSERT(bit < bit_width(), "");
  const uint64_t mask = 1ull << (bit % 64);
  BackingStorage()[bit / 64] &= ~mask;
}

bool BitVec::BitGet(unsigned bit) const {
  ASSERT(bit < bit_width(), "");
  const uint64_t mask = 1ull << (bit % 64);
  return (BackingStorage()[bit / 64] & mask) != 0;
}

void BitVec::AndWith(BitVec other) {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) data1[i] &= data2[i];
}

void BitVec::AndNotWith(BitVec other) {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) data1[i] &= ~data2[i];
}

void BitVec::OrWith(BitVec other) {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) data1[i] |= data2[i];
}
void BitVec::OrNotWith(BitVec other) {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) data1[i] |= ~data2[i];
}

void BitVec::CopyFrom(BitVec other) {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "size mismatch " << width << " vs "
         <<  other.raw_width());
  for (unsigned i = 0; i < width; ++i) data1[i] = data2[i];
}

void BitVec::Clear() {
  uint64_t* data = BackingStorage();
  const unsigned width = raw_width();
  for (unsigned i = 0; i < width; ++i) data[i] = 0;
}

bool BitVec::Equal(BitVec other) const {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) {
    if (data1[i] != data2[i]) return false;
  }
  return true;
}

bool BitVec::Intersects(BitVec other) const {
  uint64_t* data1 = BackingStorage();
  uint64_t* data2 = other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width; ++i) {
    if (data1[i] & data2[i]) return true;
  }
  return false;
}

unsigned BitVec::Popcnt() const {
  uint64_t* data = BackingStorage();
  unsigned n = 0;
  const unsigned width = raw_width();
  for (unsigned i = 0; i < width; ++i) n += __builtin_popcountll(data[i]);
  return n;
}

std::ostream& operator<<(std::ostream& os, const BitVec& bv) {
  os << "BitVec[" << std::hex << bv.index << "]";
  return os;
}

}  // namespace cwerg
