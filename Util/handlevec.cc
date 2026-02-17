
#include "Util/handlevec.h"

#include <memory.h>

#include "Util/assert.h"
#include "Util/mem_pool.h"

namespace cwerg {
namespace {

constexpr const unsigned HANDLEVEC_MAX_ENTRIES =
    HANDLEVEC_HANDLES_PER_CHUNK * ((1 << HANDLEVEC_NUM_CHUNK_BITS) - 1);

MemPool<HANDLEVEC_CHUNCK_BYTE_SIZE> GlobalHandleVecStorage;

}  // namespace

HandleVec HandleVec::New(unsigned num_entries) {
  ASSERT(num_entries <= HANDLEVEC_MAX_ENTRIES,
         "too many bits requested " << num_entries);
  const unsigned raw_width = (num_entries + HANDLEVEC_HANDLES_PER_CHUNK - 1) /
                             HANDLEVEC_HANDLES_PER_CHUNK;
  const uint32_t offset = GlobalHandleVecStorage.New(raw_width);
  HandleVec out = {offset << HANDLEVEC_NUM_CHUNK_BITS | raw_width};
  memset(GlobalHandleVecStorage.BackingStorage(offset), 0, out.num_bytes());
  return out;
}

void HandleVec::Del(HandleVec bv) {
  if (bv.num_chunks() == 0) return;
  GlobalHandleVecStorage.Del(bv.chunk_offset(), bv.num_chunks());
}

Handle* HandleVec::BackingStorage() const {
  return static_cast<Handle*>(
      GlobalHandleVecStorage.BackingStorage(chunk_offset()));
}

void HandleVec::Set(unsigned pos, Handle handle) {
  ASSERT(pos < num_handles(), "");
  BackingStorage()[pos] = handle;
}

Handle HandleVec::Get(unsigned pos) const {
  ASSERT(pos < num_handles(), "");
  return BackingStorage()[pos];
}

void HandleVec::ClearWith(Handle handle) {
  Handle* data = BackingStorage();
  const unsigned width = num_handles();
  for (unsigned i = 0; i < width; ++i) data[i] = handle;
}

void HandleVec::CopyFrom(HandleVec other) {
  uint64_t* data1 = (uint64_t*)BackingStorage();
  uint64_t* data2 = (uint64_t*)other.BackingStorage();
  ASSERT(num_chunks() == other.num_chunks(), "");
  memcpy(data1, data2, num_bytes());
}

bool HandleVec::Equal(HandleVec other) const {
  uint64_t* data1 = (uint64_t*)BackingStorage();
  uint64_t* data2 = (uint64_t*)other.BackingStorage();
  ASSERT(num_chunks() == other.num_chunks(), "");
  return memcmp(data1, data2, num_bytes()) == 0;
}

}  // namespace cwerg
