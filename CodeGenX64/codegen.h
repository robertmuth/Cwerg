#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "CpuX64/assembler.h"
#include <iostream>

namespace cwerg::code_gen_x64 {
using namespace cwerg;

extern void EmitUnitAsText(base::Unit unit, std::ostream* output);

extern x64::A64Unit EmitUnitAsBinary(base::Unit unit, bool add_startup_code);

}  // namespace cwerg::code_gen_x64
