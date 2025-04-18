
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/mod_pool.h"
#include "FE/parse.h"
#include "Util/assert.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

SwitchString sw_stdlib("stdlib", "path to stdlib directory", "./Lib");

int main(int argc, const char* argv[]) {
  const int arg_start = cwerg::SwitchBase::ParseArgv(argc, argv, &std::cerr);
  std::ios_base::sync_with_stdio(true);

  InitStripes(sw_multiplier.Value());
  InitParser();
  std::vector<Path> seed_modules;
  for (int i = arg_start; i < argc; ++i) {
    seed_modules.push_back(std::filesystem::absolute((argv[i])));
  }
  // ModPool mod_pool =
  ReadModulesRecursively(sw_stdlib.Value(), seed_modules, true);
  // TODO
  return 0;
}