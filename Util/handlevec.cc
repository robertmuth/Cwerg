
#include "Util/handlevec.h"
#include <memory.h>
#include "Util/assert.h"
#include "Util/mem_pool.h"

namespace cwerg {
namespace {

MemPool<32> GlobalHandleVecStorage;

}  // namespace

HandleVec HandleVec::New(unsigned num_entries) {
  ASSERT(num_entries <= HANDLEVEC_MAX_ENTRIES,
         "too many bits requested " << num_entries);
  // granularity is 8 entries = 32 bytes
  const unsigned raw_width = (num_entries + 7) / 8;
  const uint32_t offset = GlobalHandleVecStorage.New(raw_width);
  memset(GlobalHandleVecStorage.BackingStorage(offset), 0, raw_width * 32);
  HandleVec out = {offset << 8 | raw_width};
  return out;
}

void HandleVec::Del(HandleVec bv) {
  if (bv.raw_width() == 0) return;
  GlobalHandleVecStorage.Del(bv.index >> 8, bv.index & 0xff);
}

Handle* HandleVec::BackingStorage() const {
  return static_cast<Handle*>(
      GlobalHandleVecStorage.BackingStorage(index >> 8));
}

void HandleVec::Set(unsigned pos, Handle handle) {
  ASSERT(pos < entry_width(), "");
  BackingStorage()[pos] = handle;
}

Handle HandleVec::Get(unsigned pos) const {
  ASSERT(pos < entry_width(), "");
  return BackingStorage()[pos];
}

void HandleVec::ClearWith(Handle handle) {
  Handle* data = BackingStorage();
  const unsigned width = entry_width();
  for (unsigned i = 0; i < width; ++i) data[i] = handle;
}

void HandleVec::CopyFrom(HandleVec other) {
  uint64_t* data1 = (uint64_t*)BackingStorage();
  uint64_t* data2 = (uint64_t*)other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  // copy two handles at a time
  for (unsigned i = 0; i < width * 4; ++i) data1[i] = data2[i];
}

bool HandleVec::Equal(HandleVec other) const {
  uint64_t* data1 = (uint64_t*)BackingStorage();
  uint64_t* data2 = (uint64_t*)other.BackingStorage();
  const unsigned width = raw_width();
  ASSERT(width == other.raw_width(), "");
  for (unsigned i = 0; i < width * 4; ++i) {
    if (data1[i] != data2[i]) return false;
  }
  return true;
}

}  // namespace cwerg
