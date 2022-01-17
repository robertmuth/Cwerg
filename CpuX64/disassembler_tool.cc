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
        out.push_back((nibble << 4) | unsigned(hex_digit));
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

void batch(std::string_view data, const std::string& line) {
  Ins ins;
  if (!Disassemble(&ins, data)) {
    std::cout << "could not find opcode for: " << line << "\n";
    return;
  }
  std::vector<std::string> ops;
  std::string_view enum_name = InsSymbolize(ins, false, false, &ops);
  std::cout << std::setw(30) << data << std::dec << " " << enum_name;
  std::string_view sep = " ";
  for (const std::string& op : ops) {
    std::cout << sep << op;
    sep = ", ";
  }
  std::cout << "\n";
}

void disass(std::string_view data, const std::string& line) {
  Ins ins;
  if (!Disassemble(&ins, data)) {
    std::cout << "could not disassemble " << line << std::dec << "\n";
    return;
  }
  std::vector<std::string> ops;
  std::string_view enum_name = InsSymbolize(ins, true, true, &ops);
  std::cout << line << " " << enum_name;
  std::string_view sep = " ";
  for (const std::string& op : ops) {
    std::cout << sep << op;
    sep = " ";
  }
  std::cout << "\n";

  ops.clear();
  enum_name = InsSymbolize(ins, false, false, &ops);
  std::cout << "    " << enum_name << "\n";
  for (unsigned x = 0; x < ins.opcode->num_fields; ++x) {
    std::cout << "    " << std::left << std::setw(35)
              << EnumToString(ins.opcode->fields[x]) << " " << std::setw(10)
              << ops[x] << " (" << "0x" << std::hex << int64_t (ins.operands[x]) << std::dec << ")\n";
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

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cout << "no command specified\n";
    return 1;
  }
  if (std::string_view("batch") == argv[1]) {
    for (std::string line; getline(std::cin, line);) {
      if (line[0] == '#') continue;
      const std::string data = ExtractData(line);
      batch(data, line);
    }
  } else {
    std::string out;
    out.reserve(argc);
    for (unsigned i = 1; i < argc; ++i) {
      const std::string data = ExtractData(argv[i]);
      disass(data, argv[i]);
    }

    return 0;
  }
}
