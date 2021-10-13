#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA64/opcode_gen.h"
#include "Elf/elfhelper.h"
#include "Elf/elf_unit.h"


namespace cwerg::a64 {
using namespace cwerg;

using A64Unit = elf::Unit<uint64_t>;

// Initialize a pristine A64Unit from a textual assembly content
extern bool UnitParse(std::istream* input, bool add_startup_code, A64Unit* unit);

extern void AddIns(A64Unit* unit, Ins* ins);

extern void AddStartupCode(A64Unit* unit);

extern elf::Executable<uint64_t> MakeExe(A64Unit* unit, bool create_sym_tab);

extern std::ostream& operator<<(std::ostream& os, const A64Unit& s);

extern void ApplyRelocation(const elf::Reloc<uint64_t>& rel);

}  // namespace cwerg::a32
