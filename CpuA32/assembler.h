#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Elf/elfhelper.h"
#include "CpuA32/opcode_gen.h"

#include <iostream>
#include <map>
#include <string_view>
#include <vector>

namespace cwerg::a32 {
using namespace cwerg;
// TODO: this needs a lot more work
// * improve memory management
// * maybe templatize it, so works for 64 bit
struct Unit {
  Unit();

  elf::Section<uint32_t>* const sec_text;
  elf::Section<uint32_t>* const sec_rodata;
  elf::Section<uint32_t>* const sec_data;
  elf::Section<uint32_t>* const sec_bss;

  std::vector<elf::Reloc<uint32_t>> relocations;
  std::vector<std::unique_ptr<elf::Symbol<uint32_t>>> symbols;
  std::map<std::string_view, elf::Symbol<uint32_t>*> global_symbol_map;
  std::map<std::string_view, elf::Symbol<uint32_t>*> local_symbol_map;

  std::map<std::string_view, std::unique_ptr<std::string>> string_table;

  // Alternatively, manually  populate it with the primitives below.
  // See  ParseFromAsm's implementation for inspiration.
  void FunStart(std::string_view name, unsigned alignment);
  void AddLabel(std::string_view name, unsigned alignment);
  void FunEnd();

  void MemStart(std::string_view name,
                unsigned alignment,
                std::string_view kind);
  void AddData(unsigned repeats, const void* data, size_t len);
  void AddFunAddr(unsigned size, std::string_view fun_name);
  void AddBblAddr(unsigned size, std::string_view bbl_name);
  void AddMemAddr(unsigned size, std::string_view mem_name, uint32_t addend);
  void MemEnd();

  std::string_view InternString(std::string_view s) {
    auto it = string_table.find(s);
    if (it != string_table.end()) return it->first;
    std::string* sp = new std::string(s.data(), s.size());
    std::string_view key(*sp);
    string_table[key] = std::unique_ptr<std::string>(sp);
    return key;
  }

  // Add a symbol for Section sec at the current offset
  elf::Symbol<uint32_t>* AddSymbol(std::string_view name,
                                   elf::Section<uint32_t>* sec,
                                   bool is_local);

  elf::Symbol<uint32_t>* FindOrAddSymbol(std::string_view name, bool is_local) {
    auto* the_map = is_local ? &local_symbol_map : &global_symbol_map;
    auto it = the_map->find(name);
    if (it != the_map->end()) {
      return it->second;
    } else {
      return AddSymbol(name, nullptr, is_local);
    }
  }

  // Add a Reloc for Section sec at the current offset
  void AddReloc(elf::RELOC_TYPE_ARM reloc_type,
                const elf::Section<uint32_t>* sec,
                const elf::Symbol<uint32_t>* sym,
                uint32_t addend) {
    relocations.emplace_back(elf::Reloc<uint32_t>());
    relocations.back().Init(reloc_type, sec, sec->data->size(), sym, addend);
  }

  void AddLinkerDefs();

  void AddIns(a32::Ins* ins);

  void AddStartupCode();

  elf::Executable<uint32_t> Assemble(bool create_sym_tab);

 private:
  std::string_view current_fun_name = "";
  elf::Section<uint32_t>* current_mem_sec = nullptr;
};

// Initialize a pristine A32Unit from a textual assembly content
extern bool UnitParse(std::istream* input, bool add_startup_code, Unit* unit);

extern std::ostream& operator<<(std::ostream& os, const Unit& s);

extern bool InsParse(const std::vector<std::string_view>& token, Ins* ins);

extern std::optional<uint32_t> UnsymbolizeOperand(std::string_view s);

}  // namespace cwerg::a32
