
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <set>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/macro.h"
#include "FE/typify.h"
#include "FE/mod_pool.h"
#include "FE/parse.h"
#include "FE/pp.h"
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

  ModPool mp = ReadModulesRecursively(sw_stdlib.Value(), seed_modules, true);
  ExpandMacrosAndMacroLike(mp.mods_in_topo_order);
  SetTargetFields(mp.mods_in_topo_order);
  ResolveSymbolsInsideFunctions(mp.mods_in_topo_order, mp.builtin_symtab);

  for (Node mod : mp.mods_in_topo_order) {
    std::cout << "\n\n\n";
    Prettify(mod);
  }

  std::set<NT> eliminated_nodes = {
      NT::Import,  NT::DefMacro, NT::MacroInvoke,
      NT::MacroId, NT::MacroFor, NT::ModParam,
  };

  TypeCorpus tc(STD_TARGET_X64);
  DecorateASTWithTypes(mp.mods_in_topo_order, &tc);
  return 0;
}