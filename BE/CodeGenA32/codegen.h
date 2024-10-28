#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "BE/CpuA32/assembler.h"
#include <iostream>

namespace cwerg::code_gen_a32 {
using namespace cwerg;

extern void EmitUnitAsText(base::Unit unit, std::ostream* output);

extern a32::A32Unit EmitUnitAsBinary(base::Unit unit);

extern void LegalizeAll(base::Unit unit, bool verbose, std::ostream* fout);

extern void RegAllocGlobal(base::Unit unit, bool verbose, std::ostream* fout);

extern void RegAllocLocal(base::Unit unit, bool verbose, std::ostream* fout);

}  // namespace cwerg::code_gen_a32
