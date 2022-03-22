// (c) Robert Muth - see LICENSE for more info
#include "Base/optimize.h"

#include "Base/canonicalize.h"
#include "Base/cfg.h"
#include "Base/liveness.h"
#include "Base/lowering.h"
#include "Base/opcode_gen.h"
#include "Base/reaching_defs.h"
#include "Base/reg_stats.h"
#include "Base/sanity.h"
#include "Base/serialize.h"

namespace cwerg::base {

void FunCfgInit(Fun fun) {
  FunSplitBbls(fun);
  FunInitCFG(fun);
  FunRemoveUnconditionalBranches(fun);
  FunRemoveEmptyBbls(fun);
}

void FunCfgExit(Fun fun) { FunAddUnconditionalBranches(fun); }

void FunOptBasic(Fun fun, bool allow_conv_conversions) {
  std::vector<Ins> inss;
  FunNumberReg(fun);
  FunMergeMoveWithSrcDef(fun, &inss);
  FunCanonicalize(fun);
  FunStrengthReduction(fun);  // generates more MOVs which help

  FunRemoveEmptyBbls(fun);
  FunRemoveUnreachableBbls(fun);  // remove unreachable code before reaching-def
  FunNumberReg(fun);
  FunComputeReachingDefs(fun);
  FunPropagateRegs(fun);
  FunPropagateConsts(fun);
  FunConstantFold(fun, allow_conv_conversions, &inss);

  FunCanonicalize(fun);
  FunStrengthReduction(fun);  // generates more MOVs which help

  FunLoadStoreSimplify(fun);
  FunMoveElimination(fun, &inss);

  FunComputeLivenessInfo(fun);
  FunRemoveUselessInstructions(fun, &inss);
  FunComputeRegStatsExceptLAC(fun);
  FunComputeRegStatsLAC(fun);
  FunDropUnreferencedRegs(fun);
  FunSeparateLocalRegUsage(fun);
}

void FunOpt(Fun fun, const DK_MAP& rk_map) {
  std::vector<Ins> inss;
  FunOptBasic(fun, true);

  FunRegWidthWidening(fun, DK::U8, DK::U32, &inss);
  FunRegWidthWidening(fun, DK::S8, DK::S32, &inss);
  FunRegWidthWidening(fun, DK::U16, DK::U32, &inss);
  FunRegWidthWidening(fun, DK::S16, DK::S32, &inss);

  FunOptBasic(fun, false);
}

}  // namespace cwerg::base
