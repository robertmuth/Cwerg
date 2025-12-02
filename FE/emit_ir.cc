
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <set>
#include <vector>

#include "FE/canonicalize.h"
#include "FE/checker.h"
#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/lexer.h"
#include "FE/macro.h"
#include "FE/mod_pool.h"
#include "FE/parse.h"
#include "FE/pp.h"
#include "FE/pp_ast.h"
#include "FE/typify.h"
#include "Util/assert.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

SwitchString sw_stdlib("stdlib", "path to stdlib directory", "./Lib");

SwitchString sw_dump_ast("dump_ast", "dump AST after stage and stop", "");

SwitchString sw_dump_types("dump_types", "dump types after stage and stop", "");

SwitchBool sw_dump_stats("dump_stats", "dump stats before exiting");

void SanityCheckMods(std::string_view phase, const std::vector<Node>& mods,
                     const std::set<NT>& eliminated_nodes, COMPILE_STAGE stage,
                     TypeCorpus* tc) {
  ValidateAST(mods, stage);
  if (tc != nullptr) {
    TypeCheckAst(mods, tc, false);
    if (sw_dump_types.Value() == phase) {
      for (Node mod : mods) {
        std::cout << Node_name(mod) << "\n";
      }
      tc->Dump();
      exit(0);
    }
  }

  if (sw_dump_ast.Value() == phase) {
    DumpAstMods(mods);
    exit(0);
  }
}

void PhaseInitialLowering(const std::vector<Node>& mods_in_topo_order, TypeCorpus* tc) {
  for (Node mod : mods_in_topo_order) {
    for (Node fun = Node_body_mod(mod); !fun.isnull(); fun = Node_next(fun)) {
      FunReplaceTypeOfAndTypeUnionDelta(fun);
      FunReplaceConstExpr(fun, *tc);
      FunMakeImplicitConversionsExplicit(fun, tc);
      FunReplaceExprIndex(fun, tc);
      if (fun.kind() != NT::DefFun) continue;
    }
  }
}

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
  std::set<NT> eliminated_nodes = {NT::Import, NT::ModParam};
  SanityCheckMods("after_parsing", mp.mods_in_topo_order, eliminated_nodes,
                  COMPILE_STAGE::AFTER_PARSING, nullptr);
  //
  for (Node mod : mp.mods_in_topo_order) {
    FunRemoveParentheses(mod);
  }
  eliminated_nodes.insert(NT::ExprParen);

  ExpandMacrosAndMacroLike(mp.mods_in_topo_order);
  eliminated_nodes.insert(NT::DefMacro);
  eliminated_nodes.insert(NT::MacroInvoke);
  eliminated_nodes.insert(NT::MacroId);
  eliminated_nodes.insert(NT::MacroFor);
  eliminated_nodes.insert(NT::ExprSrcLoc);
  eliminated_nodes.insert(NT::ExprStringify);
  eliminated_nodes.insert(NT::EphemeralList);

  SetTargetFields(mp.mods_in_topo_order);
  ResolveSymbolsInsideFunctions(mp.mods_in_topo_order, mp.builtin_symtab);
  SanityCheckMods("after_symbolizing", mp.mods_in_topo_order, eliminated_nodes,
                  COMPILE_STAGE::AFTER_SYMBOLIZE, nullptr);

  TypeCorpus tc(STD_TARGET_X64);
  AddTypesToAst(mp.mods_in_topo_order, &tc);
  SanityCheckMods("after_typing", mp.mods_in_topo_order, eliminated_nodes,
                  COMPILE_STAGE::AFTER_TYPIFY, &tc);
  ValidateAST(mp.mods_in_topo_order, COMPILE_STAGE::AFTER_TYPIFY);
  //
  DecorateASTWithPartialEvaluation(mp.mods_in_topo_order);
  for (Node mod : mp.mods_in_topo_order) {
    RemoveNodesOfType(mod, NT::StmtStaticAssert);
  }
  SanityCheckMods("after_partial_eval", mp.mods_in_topo_order,
                  eliminated_nodes, COMPILE_STAGE::AFTER_EVAL, &tc);


  PhaseInitialLowering(mp.mods_in_topo_order, &tc);
  eliminated_nodes.insert(NT::TypeOf);
  eliminated_nodes.insert(NT::TypeUnionDelta);
  SanityCheckMods("after_initial_lowering", mp.mods_in_topo_order,
                  eliminated_nodes, COMPILE_STAGE::AFTER_DESUGAR, &tc);
  //
  if (sw_dump_stats.Value()) {
    std::cout << "Stats:  files=" << LexerRaw::stats.num_files
              << " lines=" << LexerRaw::stats.num_lines
              << " nodes=" << gStripeGroupNode.NextAvailable() << "\n";
  }
  return 0;
}