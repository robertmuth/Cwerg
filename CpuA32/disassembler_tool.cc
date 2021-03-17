// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/disassembler.h"
#include "Util/assert.h"

#include <cstdlib>
#include <iostream>
#include <string_view>

using namespace cwerg::a32;

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cout << "no command specified\n";
    return 1;
  }
  if (std::string_view("disass") == argv[1]) {
    for (unsigned i = 2; i < argc; ++i) {
      const uint32_t data = strtoul(argv[i], 0, 16);
      Ins ins;
      if (!DecodeIns(&ins, data)) {
        std::cout << "could not find opcode for: " << std::hex << data << "\n";
        continue;
      }
      char buffer[128];
      std::cout << argv[i] << " " << ins.opcode->enum_name;
      std::string_view sep = " ";
      for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
        RenderOperandStd(buffer, *ins.opcode, ins.operands[i],
                         ins.opcode->fields[i]);
        std::cout << sep << buffer;
        sep = ", ";
      }
      std::cout << "\n";
      // check that the assembler works - this is not strictly
      // necessary but useful for debuggging the assembler
      const uint32_t data2 = EncodeIns(ins);
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
    for (uint32_t data = 0; data < (1 << 28); ++data) {
      Ins ins;
      if (DecodeIns(&ins, data)) {
        const uint32_t data2 = EncodeIns(ins);
        if (data != data2) {
          if (ins.opcode->fields[2] != OK::IMM_0_7_8_11 &&
              ins.opcode->fields[3] != OK::IMM_0_7_8_11) {
            std::cout << "Disassembler failure " << std::hex << data << " vs "
                      << data2 << ": ";
            char buffer[128];
            std::cout << ins.opcode->enum_name;
            std::string_view sep = " ";
            for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
              RenderOperandStd(buffer, *ins.opcode, ins.operands[i],
                               ins.opcode->fields[i]);
              std::cout << sep << buffer;
              sep = ", ";
            }
            std::cout << "\n";

            return 1;
          }
          continue;
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
