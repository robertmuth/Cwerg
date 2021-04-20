// (c) Robert Muth - see LICENSE for more info

#include "CpuA64/symbolic.h"
#include "Util/assert.h"

#include <cstdlib>
#include <iostream>
#include <string_view>

using namespace cwerg::a64;

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cout << "no command specified\n";
    return 1;
  }
  if (std::string_view("disass") == argv[1]) {
    for (unsigned i = 2; i < argc; ++i) {
      const uint32_t data = strtoul(argv[i], nullptr, 16);
      Ins ins;
      if (!Disassemble(&ins, data)) {
        std::cout << "could not find opcode for: " << std::hex << data << "\n";
        continue;
      }
      std::vector<std::string> ops;
      std::string_view enum_name = InsSymbolize(ins, &ops);
      std::cout << argv[i] << " " << enum_name;
      std::string_view sep = " ";
      for (const std::string& op : ops) {
        std::cout << sep << op;
        sep = ", ";
      }
      std::cout << "\n";
      // check that the assembler works - this is not strictly
      // necessary but useful for debuggging the assembler
      const uint32_t data2 = Assemble(ins);
      if (data != data2) {
        std::cout << "Disassembler failure " << std::hex << data << " vs "
                  << data2 << "\n";
        return 1;
      }
      ASSERT(data == data2, "");
    }
  } else if (std::string_view("benchmark") == argv[1]) {
    // The first 1<<28 (256M) bit patterns exercise all opcodes with predicate
    // "eq"
    uint32_t num_bad = 0;
    std::vector<std::string> ops;
    for (uint32_t data = 0; data < (1U << 28U); ++data) {
      Ins ins;
      if (Disassemble(&ins, data)) {
        const uint32_t data2 = Assemble(ins);
        if (data != data2) {
          std::cout << "Disassembler failure " << std::hex << data << " vs "
                    << data2 << ": ";
          ops.clear();
          std::string_view enum_name = InsSymbolize(ins, &ops);
          std::cout << enum_name;
          std::string_view sep = " ";
          for (const std::string& op : ops) {
            std::cout << sep << op;
            sep = ", ";
          }
          std::cout << "\n";
          return 1;
        }
      } else {
        ++num_bad;
      }
      if (data % 10000000 == 0) {
        std::cout << num_bad << "/" << data << "\n";
      }
    }
    std::cout << "unsupported opcodes: " << std::dec << num_bad << "\n";
    return 0;
  } else {
    std::cout << "unknown command specified: " << argv[1] << "\n";
    return 1;
  }
}
