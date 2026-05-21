#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <iostream>

#include "BE/Base/ir.h"
#include "BE/CodeGenA32/regs.h"

namespace cwerg::code_gen_a32 {
using namespace cwerg;

extern void LegalizeAll(base::Unit unit, bool verbose, std::ostream* fout);

extern void RegAllocGlobal(base::Unit unit, bool verbose, std::ostream* fout);

extern void RegAllocLocal(base::Unit unit, bool verbose, std::ostream* fout);

}  // namespace cwerg::code_gen_a32
