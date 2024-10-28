// (c) Robert Muth - see LICENSE for more info

#include "BE/CpuX64/assembler.h"

#include <fstream>

using namespace cwerg;

bool Assemble(std::string_view input, std::string_view output) {
  std::ifstream finFile;
  std::istream* fin = &std::cin;
  if (input != "-") {
    finFile.open(input.data());
    fin = &finFile;
  }

  x64::X64Unit unit;
  if (!x64::UnitParse(fin, &unit)) {
    std::cerr << "cannot parse input file " << input << "\n";
    return false;
  }
  auto exe = x64::MakeExe(&unit, true);
  std::cout << exe;

  std::ofstream foutFile;
  std::ostream* fout = &std::cout;
  if (output != "-") {
    foutFile.open(output.data());
    fout = &foutFile;
  }

  std::vector<std::string_view> chunks = exe.Save();

  for (const auto& c : chunks) {
    fout->write((const char*)c.data(), c.size());
  }
  return true;
}

int main(int argc, char* argv[]) {
  if (argc <= 1) {
    std::cerr << "no command specified\n";
    return 1;
  }

  if (argv[1] == std::string_view("lint")) {
    x64::X64Unit unit;
    x64::UnitParse(&std::cin, &unit);
    std::cout << unit << "\n";
  } else if (argv[1] == std::string_view("assemble")) {
    if (argc <= 3) {
      std::cerr << "need src and dst args\n";
      return 1;
    }
    if (!Assemble(argv[2], argv[3])) {
      return 1;
    }
  }
  return 0;
}
