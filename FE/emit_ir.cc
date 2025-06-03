
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <set>
#include <vector>

#include "FE/checker.h"
#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/macro.h"
#include "FE/mod_pool.h"
#include "FE/parse.h"
#include "FE/pp.h"
#include "FE/typify.h"
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
  std::cout << "@@@ CHECKING BEFORE MACRO EXPANSION\n";
  ValidateAST(mp.mods_in_topo_order, CompileStage::AfterParsing);
  ExpandMacrosAndMacroLike(mp.mods_in_topo_order);
  std::cout << "@@@ CHECKING AFTER MACRO EXPANSION\n";
  ValidateAST(mp.mods_in_topo_order, CompileStage::AfterParsing);
#if 0
  for (Node mod : mp.mods_in_topo_order) {
    std::cout << "\n\n\n";
    Prettify(mod);
  }
#endif
  SetTargetFields(mp.mods_in_topo_order);
  ResolveSymbolsInsideFunctions(mp.mods_in_topo_order, mp.builtin_symtab);
  std::cout << "@@@ CHECKING AFTER SYMBOL RESOLUTION EXPANSION\n";
  ValidateAST(mp.mods_in_topo_order, CompileStage::AfterSymbolization);

#if 0
  for (Node mod : mp.mods_in_topo_order) {
    std::cout << "\n\n\n";
    Prettify(mod);
  }
#endif

  std::set<NT> eliminated_nodes = {
      NT::Import,  NT::DefMacro, NT::MacroInvoke,
      NT::MacroId, NT::MacroFor, NT::ModParam,
  };

  TypeCorpus tc(STD_TARGET_X64);

  AddTypesToAst(mp.mods_in_topo_order, &tc);
  std::cout << "@@@ CHECKING AFTER TYPING\n";
  ValidateAST(mp.mods_in_topo_order, CompileStage::AfterTyping);
  TypeCheckAst(mp.mods_in_topo_order, &tc, false);

  // tc.Dump();

  std::cout << "@@@ files=" << LexerRaw::stats.num_files
            << " lines=" << LexerRaw::stats.num_lines << "\n";

  return 0;
}