#include "Util/bitvec.h"
#include "Util/assert.h"

#include <iostream>
#include <vector>

using namespace std;

namespace cwerg {

void Test() {
  BitVec bv1 = BitVec::New(256);
  ASSERT(bv1.Popcnt() == 0, "");
  BitVec bv2 = BitVec::New(256);
  ASSERT(bv2.Popcnt() == 0, "");
  BitVec bv3 = BitVec::New(256);
  ASSERT(bv3.Popcnt() == 0, "");

  bv1.AndWith(bv2);
  ASSERT(bv1.Popcnt() == 0, "");
  bv1.OrWith(bv2);
  ASSERT(bv1.Popcnt() == 0, "expected 0 got " << bv1.Popcnt());
  bv1.AndNotWith(bv2);
  ASSERT(bv1.Popcnt() == 0, "expected 0 got " << bv1.Popcnt());

  // set all odd bits in bv1
  for (unsigned i = 1; i < 256; i += 2) {
    ASSERT(!bv1.BitGet(i), "");
    bv1.BitSet(i);
    ASSERT(bv1.BitGet(i), "");
    ASSERT(bv1.Popcnt() == (i / 2) + 1,
           "expected " << (i / 2) + 1 << " got " << bv1.Popcnt());
  }
  bv1.AndWith(bv1);
  ASSERT(bv1.Popcnt() == 128, "");
  bv1.OrWith(bv1);
  ASSERT(bv1.Popcnt() == 128, "");

  // set all even bits in bv2
  for (unsigned i = 0; i < 256; i += 2) {
    bv2.BitSet(i);
    ASSERT(bv2.Popcnt() == (i / 2) + 1,
           "expected " << (i / 2) + 1 << " got " << bv1.Popcnt());
  }
  bv2.AndWith(bv2);
  ASSERT(bv2.Popcnt() == 128, "");
  bv2.OrWith(bv2);
  ASSERT(bv2.Popcnt() == 128, "");

  ASSERT(!bv1.Intersects(bv2), "");

  // bv3 will have all bits set
  bv3.CopyFrom(bv1);
  bv3.OrWith(bv2);
  ASSERT(bv3.Popcnt() == 256, "");

  ASSERT(bv1.Intersects(bv3), "");
  ASSERT(bv2.Intersects(bv3), "");


  bv3.CopyFrom(bv1);
  bv3.AndWith(bv2);
  ASSERT(bv3.Popcnt() == 0, "");

  bv3.CopyFrom(bv1);
  bv3.AndNotWith(bv2);
  ASSERT(bv3.Popcnt() == 128, "");

  ASSERT(bv1.Equal(bv1), "");
  ASSERT(!bv1.Equal(bv2), "");

}

}  // namespace cwerg

int main() { cwerg::Test(); }
