#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <iostream>

#include "BE/Base/ir.h"
#include "BE/CodeGenA64/regs.h"

namespace cwerg::code_gen_a64 {
using namespace cwerg;

void LegalizeAll(base::Unit unit, bool verbose, std::ostream* fout);

void RegAllocGlobal(base::Unit unit, bool verbose, std::ostream* fout);

void RegAllocLocal(base::Unit unit, bool verbose, std::ostream* fout);

}  // namespace cwerg::code_gen_a64
