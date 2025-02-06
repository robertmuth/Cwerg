#include <fstream>
#include <iomanip>
#include <iostream>

#include "Util/parse.h"
#include "Util/switch.h"

namespace {

using namespace cwerg;
using namespace cwerg::fe;

}  //  namespace

int main(int argc, const char* argv[]) {
  if (argc - 2 != cwerg::SwitchBase::ParseArgv(argc, argv, &std::cerr)) {
    std::cerr << "need exactly two positional arguments\n";
    return 1;
  }

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  std::ios_base::sync_with_stdio(false);

  // InitStripes(sw_multiplier.Value());

  std::ifstream finFile;
  std::istream* fin = &std::cin;
  if (argv[argc - 2] != std::string_view("-")) {
    finFile.open(argv[argc - 2]);
    fin = &finFile;
  }

  std::ofstream foutFile;
  std::ostream* fout = &std::cout;
  if (argv[argc - 1] != std::string_view("-")) {
    foutFile.open(argv[argc - 1]);
    fout = &foutFile;
  }

  std::vector<char> data = SlurpDataFromStream(fin);
}
