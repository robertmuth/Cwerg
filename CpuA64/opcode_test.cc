/*
    This test should be more or less identical to arm_test.py
    except that it is written in C.
    It checks that we can assemble and disassemble all the instructions
    found in `arm_test.dis`
*/

#include "CpuA64/opcode_gen.h"
#include "Util/assert.h"

#include <cstdint>


namespace {
using namespace cwerg;

void CheckEncodeDecode() {
  uint32_t count = 0;
  uint32_t sm = 0;
  for (uint32_t size = 64; size >= 2; size >>= 1) {
    for (uint32_t ones = 1; ones < size; ++ones) {
      for (uint32_t r = 0; r < size; ++r) {
        ++count;
        const uint32_t n = size == 64;
        const uint32_t s = sm | (ones - 1);
        const uint32_t i = (n << 12) | (r << 6) | s;
        uint64_t x = a64::Decode_10_15_16_22_X(i);
        // std::cout << std::hex << i << " " << x << std::dec << "\n";
        // std::cout << std::hex << n << " " << r << " " << s << " pattern " <<
        // x
        //          << "\n";
        uint32_t j = a64::Encode_10_15_16_22_X(x);
        ASSERT(i == j,
               "bad logic imm " << i << " vs " << j << " decoded was " << x);
      }
    }

    if (size <= 32) {
      sm += size;
    }
  }

  ASSERT(count == 5334, "total number of codes is not 5334: " << count);
}

void CheckEncodeDecodeFloat() {
  for (uint32_t i = 0; i < 256; ++i) {
    const double d = a64::Decode8BitFlt(i);
    // std::cout << std::hex << i << " " << d << "\n";
    uint32_t j = a64::Encode8BitFlt(d);
    ASSERT(i == j, "bad flt imm " << i << " vs " << j << "  val " << d);
  }
}

}  // namespace

int main(int argc, char* argv[]) {
  CheckEncodeDecode();
  CheckEncodeDecodeFloat();
  return 0;
}
