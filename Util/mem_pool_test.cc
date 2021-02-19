
#include "Util/mem_pool.h"
#include "Util/assert.h"
#include <memory.h>
#include <iostream>

using namespace std;

namespace cwerg {

void BasicTest() {
  MemPool<32> pool;

  const uint32_t offset1 = pool.New(4);
  ASSERT(offset1 == 1, "");

  const uint32_t offset2 = pool.New(4);
  ASSERT(offset2 == 5, "");

  const uint32_t offset3 = pool.New(4);
  ASSERT(offset3 == 9, "");

  const uint32_t offset4 = pool.New(4);
  ASSERT(offset4 == 13, "");

  memset(pool.BackingStorage(offset1), 11, 4 * pool.byte_granularity());
  memset(pool.BackingStorage(offset2), 22, 4 * pool.byte_granularity());
  memset(pool.BackingStorage(offset3), 33, 4 * pool.byte_granularity());
  memset(pool.BackingStorage(offset4), 44, 4 * pool.byte_granularity());

  ASSERT(*(char*) pool.BackingStorage(offset1) == 11, "");
  ASSERT(*(char*) pool.BackingStorage(offset2) == 22, "");
  ASSERT(*(char*) pool.BackingStorage(offset3) == 33, "");
  ASSERT(*(char*) pool.BackingStorage(offset4) == 44, "");
}

}  // namespace cwerg

int main() {
  cwerg::BasicTest();
  return 0;
}
