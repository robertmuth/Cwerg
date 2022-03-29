#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/opcode_gen.h"
#include "Elf/elfhelper.h"
#include "Elf/elf_unit.h"


namespace cwerg::a32 {
using namespace cwerg;

using A32Unit = elf::Unit<uint32_t>;

// Initialize a pristine A32Unit from a textual assembly content
extern bool UnitParse(std::istream* input, bool add_startup_code, A32Unit* unit);

extern void AddIns(A32Unit* unit, Ins* ins);

extern void ApplyRelocation(const elf::Reloc<uint32_t>& rel);

extern elf::Executable<uint32_t> MakeExe(A32Unit* unit, bool create_sym_tab);

extern std::ostream& operator<<(std::ostream& os, const A32Unit& s);

}  // namespace cwerg::a32
