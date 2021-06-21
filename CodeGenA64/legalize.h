#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "CodeGenA64/regs.h"

#include <iostream>

namespace cwerg::code_gen_a64 {
using namespace cwerg;

extern void PhaseLegalization(base::Fun fun,
                              base::Unit unit,
                              std::ostream* fout);

extern void PhaseGlobalRegAlloc(base::Fun fun,
                                base::Unit unit,
                                std::ostream* fout);

extern void PhaseFinalizeStackAndLocalRegAlloc(base::Fun fun,
                                               base::Unit unit,
                                               std::ostream* fout);

}  // namespace cwerg::code_gen_a32
