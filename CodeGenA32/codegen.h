#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "CpuA32/assembler.h"
#include <iostream>

namespace cwerg::code_gen_a32 {
using namespace cwerg;

extern void EmitUnitAsText(base::Unit unit, std::ostream* output);

extern a32::Unit EmitUnitAsBinary(base::Unit unit, bool add_startup_code);

}  // namespace cwerg::code_gen_a32
