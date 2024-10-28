#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <iostream>
#include "Base/ir.h"
#include "BE/CpuX64/assembler.h"

namespace cwerg::code_gen_x64 {
using namespace cwerg;

extern void EmitUnitAsText(base::Unit unit, std::ostream* output);

extern x64::X64Unit EmitUnitAsBinary(base::Unit unit);

}  // namespace cwerg::code_gen_x64
