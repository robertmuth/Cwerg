// (c) Robert Muth - see LICENSE for more info

#include "CpuX64/opcode_gen.h"
#include "CpuX64/symbolic.h"
#include "Util/assert.h"
#include "Util/parse.h"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string_view>

using namespace cwerg::x64;

std::string ExtractData(std::string_view line) {
  std::string out;
  out.reserve(line.size());
  unsigned nibble;
  bool have_nibble = false;
  for (char c : line) {
    if (cwerg::IsWhiteSpace(c)) {
      if (have_nibble) {
        out.push_back(nibble);
        have_nibble = false;
      }
    } else {
      const int hex_digit = cwerg::HexDigit(c);
      ASSERT(hex_digit >= 0, "");
      if (have_nibble) {
        out.push_back((nibble << 4) | unsigned (hex_digit));
        have_nibble = false;
      } else {
        nibble = hex_digit;
        have_nibble = true;
      }
    }
  }
  if (have_nibble) {
    out.push_back(nibble);
    have_nibble = false;
  }
  return out;
}

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cout << "no command specified\n";
    return 1;
  }
  if (std::string_view("batch") == argv[1]) {
    for (std::string line; getline(std::cin, line);) {
      if (line[0] == '#') continue;
      const std::string data = ExtractData(line);
      Ins ins;
      if (!Disassemble(&ins, data)) {
        std::cout << "could not find opcode for: " << line << "\n";
        continue;
      }
      std::vector<std::string> ops;
      std::string_view enum_name = InsSymbolize(ins, false, &ops);
      std::cout << std::setw(30) << data << std::dec << " " << enum_name;
      std::string_view sep = " ";
      for (const std::string& op : ops) {
        std::cout << sep << op;
        sep = ", ";
      }
      std::cout << "\n";
    }
#if 0
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
#endif
  } else {
    std::string out;
    out.reserve(argc);
    for (unsigned i = 1; i < argc; ++i) {
      const std::string data = ExtractData(argv[i]);
      Ins ins;
      if (!Disassemble(&ins, data)) {
        std::cout << "could not disassemble " << std::hex << data << std::dec
                  << "\n";
        continue;
      }
      std::vector<std::string> ops;
      std::string_view enum_name = InsSymbolize(ins, true, &ops);
      std::cout << argv[i] << " " << enum_name;
      std::string_view sep = " ";
      for (const std::string& op : ops) {
        std::cout << sep << op;
        sep = " ";
      }
      std::cout << "\n";
      for (unsigned x = 0; x < ins.opcode->num_fields; ++x) {
        std::cout << "    " << std::left << std::setw(35)
                  << EnumToString(ins.opcode->fields[x]) << " " << std::setw(10)
                  << ops[x] << " (" << ins.operands[x] << ")\n";
      }
      std::cout << "\n";
#if 0
      // check that the assembler works - this is not strictly
      // necessary but useful for debugging the assembler
      const uint32_t data2 = Assemble(ins);
      if (data != data2) {
        std::cout << "Disassembler failure " << std::hex << data << " vs "
                  << data2 << "\n";
        return 1;
      }
      ASSERT(data == data2, "");
#endif
    }

    return 0;
  }
}
