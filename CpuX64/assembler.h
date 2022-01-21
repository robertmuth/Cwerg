#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuX64/opcode_gen.h"
#include "Elf/elfhelper.h"
#include "Elf/elf_unit.h"


namespace cwerg::x64 {
using namespace cwerg;

using X64Unit = elf::Unit<uint64_t>;

// Initialize a pristine A64Unit from a textual assembly content
extern bool UnitParse(std::istream* input, bool add_startup_code, X64Unit* unit);

extern void AddIns(X64Unit* unit, Ins* ins);

extern void AddStartupCode(X64Unit* unit);

extern elf::Executable<uint64_t> MakeExe(X64Unit* unit, bool create_sym_tab);

extern std::ostream& operator<<(std::ostream& os, const X64Unit& s);

extern void ApplyRelocation(const elf::Reloc<uint64_t>& rel);

}  // namespace cwerg::x64
