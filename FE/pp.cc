#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/parse.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

std::vector<char> SlurpDataFromStream(std::istream* fin) {
  size_t num_bytes_per_read = 1024 * 1024;
  size_t current_offset = 0U;
  std::vector<char> out(num_bytes_per_read);
  auto rdbuf = fin->rdbuf();
  while (true) {
    size_t count =
        rdbuf->sgetn(out.data() + current_offset, num_bytes_per_read);
    if (count == 0) break;
    current_offset += count;
    out.resize(current_offset + num_bytes_per_read);
  }
  out.resize(current_offset);
  return out;
}

int main(int argc, const char* argv[]) {
  InitLexer();
  InitStripes(sw_multiplier.Value());
  InitParser();

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  // std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::vector<char> data = SlurpDataFromStream(fin);
  Lexer lexer(
      std::string_view(reinterpret_cast<char*>(data.data()), data.size()), 555);
  // std::cout << "loaded " << data.size() << " bytes\n";

  Node mod = ParseDefMod(&lexer);
  mod = mod;
  return 0;
}