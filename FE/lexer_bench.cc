
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

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

#if 0
std::string_view ReadFile(const char* filename) {
  std::ifstream finFile;
  std::istream* fin;
  if (filename == std::string_view("-")) {
    fin = &std::cin;
  } else {
    finFile.open(filename);
    fin = &finFile;
  }

  std::vector<char>* data = SlurpDataFromStream(fin);
  return std::string_view(reinterpret_cast<const char*>(data->data()),
                          data->size());
}

#else

std::string_view ReadFile(const char* filename) {
  int fd = open(filename, O_RDONLY, 0);
  if (fd < 0) {
    std::cerr << "Cannot open input file [" << filename << "] err=" << fd
              << "\n";
    return std::string_view();
  }
  struct stat sb;
  fstat(fd, &sb);

  // map an extra terminator byte
  void* data_bytes = mmap(NULL, sb.st_size + 1, PROT_WRITE, MAP_PRIVATE, fd, 0);
  if (data_bytes == MAP_FAILED) {
    std::cerr << "Cannot mmap input file " << filename << "\n";
    return std::string_view();
  }
  close(fd);

  return std::string_view(reinterpret_cast<char*>(data_bytes), sb.st_size);
}

#endif

void RunLexer(Lexer* lexer) {
  while (true) {
    auto tk = lexer->Next();
    // std::cout << tk << "\n";
    if (tk.kind == TK_KIND::SPECIAL_EOF) {
      break;
    }
  }
}

void RunParser(Lexer* lexer, Name name) { ParseDefMod(lexer, name); }

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
    auto data = ReadFile(argv[i]);
    total_bytes += data.size();

    std::cout << "processing: " << argv[i] << " bytes=" << data.size() << "\n";
    Lexer lexer(data, kNameInvalid);

    std::string_view mode = sw_mode.Value();
    if (mode == "lexer") {
      RunLexer(&lexer);
    } else if (mode == "parser") {
      RunParser(&lexer, NameNew(argv[i]));
    } else {
      std::cerr << "unknown mode " << mode << "\n";
      return 1;
    }
    total_lines += lexer.LinesProcessed();
  }
  std::cout << "Processed: bytes=" << total_bytes << " lines=" << total_lines
            << "\n";
}
