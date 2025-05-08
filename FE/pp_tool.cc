#include <memory>

#include "FE/parse.h"
#include "FE/pp.h"
#include "Util/parse.h"
#include "Util/switch.h"

cwerg::SwitchInt32 sw_multiplier("multiplier",
                                 "adjust multiplies for item pool sizes", 4);

int main(int argc, const char* argv[]) {
  cwerg::InitStripes(sw_multiplier.Value());
  cwerg::fe::InitParser();

  // If the synchronization is turned off, the C++ standard streams are
  // allowed to buffer their I/O independently from their stdio
  // counterparts, which may be considerably faster in some cases.
  // std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::unique_ptr<const std::vector<char>> data(
      cwerg::SlurpDataFromStream(fin));
  cwerg::fe::Lexer lexer({data->data(), data->size()},
                         cwerg::fe::NameNew("stdin"));
  // std::cout << "loaded " << data.size() << " bytes\n";

  cwerg::fe::Node mod =
      cwerg::fe::ParseDefMod(&lexer, cwerg::fe::kNameInvalid);
  cwerg::fe::Prettify(mod);
  return 0;
}