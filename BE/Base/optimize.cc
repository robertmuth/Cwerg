// (c) Robert Muth - see LICENSE for more info
#include "BE/Base/optimize.h"

#include "BE/Base/canonicalize.h"
#include "BE/Base/cfg.h"
#include "BE/Base/liveness.h"
#include "BE/Base/lowering.h"
#include "BE/Base/opcode_gen.h"
#include "BE/Base/reaching_defs.h"
#include "BE/Base/reg_stats.h"
#include "BE/Base/sanity.h"
#include "BE/Base/serialize.h"

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
