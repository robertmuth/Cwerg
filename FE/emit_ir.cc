
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
  InitStripes(sw_multiplier.Value());
  InitParser();
  ModPool mod_pool(sw_stdlib.Value());
  // TODO
  return 0;
}