/*
    This test is NOT equivalent to opcode_test.py
    It only checks the encoding of certain immediate fields.
*/

#include <cstdint>

#include "BE/CpuA64/opcode_gen.h"
#include "Util/assert.h"

namespace {
using namespace cwerg;

void CheckEncodeDecode() {
  uint32_t count = 0;
  uint32_t sm = 0;
  for (uint32_t size = 64; size >= 2; size >>= 1U) {
    for (uint32_t ones = 1; ones < size; ++ones) {
      for (uint32_t r = 0; r < size; ++r) {
        ++count;
        const uint32_t n = size == 64;
        const uint32_t s = sm | (ones - 1);
        const uint32_t i = (n << 12U) | (r << 6U) | s;
        uint64_t x = a64::Decode_10_15_16_22_X(i);
        // std::cout << std::hex << i << " " << x << std::dec << "\n";
        // std::cout << std::hex << n << " " << r << " " << s << " pattern " <<
        // x
        //          << "\n";
        uint32_t j = a64::Encode_10_15_16_22_X(x);
        CHECK(i == j,
              "bad logic imm " << i << " vs " << j << " decoded was " << x);
      }
    }

    if (size <= 32) {
      sm += size;
    }
  }

  CHECK(count == 5334, "total number of codes is not 5334: " << count);
}

void CheckEncodeDecodeFloat() {
  for (uint32_t i = 0; i < 256; ++i) {
    const double d = a64::Decode8BitFlt(i);
    // std::cout << std::hex << i << " " << d << "\n";
    uint32_t j = a64::Encode8BitFlt(d);
    CHECK(i == j, "bad flt imm " << i << " vs " << j << "  val " << d);
  }
}

}  // namespace

int main(int argc, char* argv[]) {
  CheckEncodeDecode();
  CheckEncodeDecodeFloat();
  return 0;
}
