#include <fstream>
#include <iomanip>
#include <iostream>

#include "FE/lexer.h"
#include "FE/parse.h"
#include "Util/parse.h"
#include "Util/switch.h"

namespace {

using namespace cwerg;
using namespace cwerg::fe;

void RunLexer(Lexer* lexer) {
  while (true) {
    auto tk = lexer->Next();
    std::cout << tk << "\n";
    if (tk.kind == TK_KIND::SPECIAL_EOF) {
      break;
    }
  }
}

void RunParser(Lexer* lexer) {
  ParseDefMod(lexer);
}

}  //  namespace

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          16);
SwitchString sw_mode("m", "benchmark mode: `lexer`, `paser`", "lexer");

int main(int argc, const char* argv[]) {
  int start_positional = SwitchBase::ParseArgv(argc, argv, &std::cerr);
  if (start_positional >= argc) {
    std::cerr << "need at least one input file\n";
    return 1;
  }

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  std::ios_base::sync_with_stdio(false);

  InitStripes(sw_multiplier.Value());
  InitParser();

  int total_bytes = 0;
  int total_lines = 0;

  for (int i = start_positional; i < argc; ++i) {
    std::ifstream finFile;
    std::istream* fin;
    if (argv[i] == std::string_view("-")) {
      fin = &std::cin;
    } else {
      finFile.open(argv[i]);
      fin = &finFile;
    }

    std::vector<char> data = SlurpDataFromStream(fin);
    total_bytes += data.size();
    std::cout << "processing: " << argv[i] << " bytes=" << data.size() << "\n";
    Lexer lexer(std::string_view(reinterpret_cast<const char*>(data.data()),
                                 data.size()),
                i);


    std::string_view mode = sw_mode.Value();
    if (mode == "lexer") {
      RunLexer(&lexer);
    } else if (mode == "parser") {
      RunParser(&lexer);
    } else {
      std::cerr << "unknown mode " << mode << "\n";
      return 1;
    }
    total_lines += lexer.LinesProcessed();
  }
  std::cout << "Processed: bytes=" << total_bytes << " lines=" << total_lines
            << "\n";
}
