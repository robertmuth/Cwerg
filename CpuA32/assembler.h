#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/opcode_gen.h"
#include "Elf/elfhelper.h"

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
  void FunStart(std::string_view name,
                unsigned alignment,
                std::string_view padding) {
    ASSERT(current_fun_name.empty(), "");
    current_fun_name = name;
    sec_text->PadData(alignment, padding);
    AddSymbol(name, sec_text, false);
  }

  void AddLabel(std::string_view name,
                unsigned alignment,
                std::string_view padding) {
    sec_text->PadData(alignment, padding);
    ASSERT(!current_fun_name.empty(), "");
    AddSymbol(name, sec_text, true);
  }

  void FunEnd() {
    ASSERT(!current_fun_name.empty(), "");
    current_fun_name = "";
    local_symbol_map.clear();
  }

  void MemStart(std::string_view name,
                unsigned alignment,
                std::string_view kind,
                std::string_view padding,
                bool is_local) {
    ASSERT(current_mem_sec == nullptr, "");
    if (kind == "rodata") {
      current_mem_sec = sec_rodata;
    } else if (kind == "data") {
      current_mem_sec = sec_data;
    } else if (kind == "bss") {
      current_mem_sec = sec_bss;
    } else {
      ASSERT(false, "bad mem kind " << kind);
    }
    current_mem_sec->PadData(alignment, padding);
    AddSymbol(name, current_mem_sec, is_local);
  }

  void AddData(unsigned repeats, const void* data, size_t len) {
    ASSERT(current_mem_sec != nullptr, "");
    for (unsigned i = 0; i < repeats; ++i) {
      current_mem_sec->AddData({(const char*)data, len});
    }
  }

  void AddFunAddr(unsigned size, uint8_t reloc_kind, std::string_view fun_name) {
    ASSERT(current_mem_sec != nullptr, "");
    ASSERT(size == 4, "");
    auto* sym = FindOrAddSymbol(fun_name, false);
    AddReloc(reloc_kind, current_mem_sec, sym, 0);
    current_mem_sec->AddDataRepeatedBytes(size, 0);
  }

  void AddBblAddr(unsigned size, uint8_t reloc_kind, std::string_view bbl_name) {
    ASSERT(current_mem_sec != nullptr, "add bbl addr outside a mem directive");
    ASSERT(size == 4, "");
    auto* sym = FindOrAddSymbol(bbl_name, true);
    AddReloc(reloc_kind, current_mem_sec, sym, 0);
    current_mem_sec->AddDataRepeatedBytes(size, 0);
  }

  void AddMemAddr(unsigned size, uint8_t reloc_kind, std::string_view mem_name, uint32_t addend) {  ASSERT(current_mem_sec != nullptr, "memaddr outside of mem");
    ASSERT(size == 4, "");
    ASSERT(addend == 0, "NYI");
    auto* sym = FindOrAddSymbol(mem_name, false);
    AddReloc(reloc_kind, current_mem_sec, sym, 0);
    current_mem_sec->AddDataRepeatedBytes(size, 0);
  }

  void MemEnd() {
    ASSERT(current_mem_sec != nullptr, "");
    current_mem_sec = nullptr;
  }

  std::string_view InternString(std::string_view s) {
    auto it = string_table.find(s);
    if (it != string_table.end()) return it->first;
    auto* sp = new std::string(s.data(), s.size());
    std::string_view key(*sp);
    string_table[key] = std::unique_ptr<std::string>(sp);
    return key;
  }

  // Add a symbol for Section sec at the current offset
  elf::Symbol<uint32_t>* AddSymbol(std::string_view name,
                                   elf::Section<uint32_t>* sec,
                                   bool is_local) {
    name = InternString(name);
    auto* the_map = is_local ? &local_symbol_map : &global_symbol_map;
    auto it = the_map->find(name);
    elf::Symbol<uint32_t>* sym = it == the_map->end() ? nullptr : it->second;
    if (sym == nullptr) {
      sym = new elf::Symbol<uint32_t>();
      sym->Init(name, is_local, sec, sec == nullptr ? ~0U : sec->data->size());
      symbols.emplace_back(std::unique_ptr<elf::Symbol<uint32_t>>(sym));
      (*the_map)[name] = sym;
      return sym;
    }
    if (sec != nullptr) {
      ASSERT(sym->section == nullptr,
             "Symbol " << name << " already has sec local:" << is_local);
      sym->section = sec;
      sym->sym.st_value = sec->data->size();
    }
    return sym;
  }

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
  void AddReloc(uint8_t reloc_kind,
                const elf::Section<uint32_t>* sec,
                const elf::Symbol<uint32_t>* sym,
                uint32_t addend) {
    relocations.emplace_back(elf::Reloc<uint32_t>());
    relocations.back().Init(reloc_kind, sec, sec->data->size(), sym, addend);
  }

  void AddLinkerDefs();


 private:
  std::string_view current_fun_name = "";
  elf::Section<uint32_t>* current_mem_sec = nullptr;
};

// Initialize a pristine A32Unit from a textual assembly content
extern bool UnitParse(std::istream* input, bool add_startup_code, Unit* unit);

extern void AddIns(Unit* unit, Ins* ins);

extern void AddStartupCode(Unit* unit);

extern elf::Executable<uint32_t> MakeExe(Unit* unit, bool create_sym_tab);

extern std::ostream& operator<<(std::ostream& os, const Unit& s);

}  // namespace cwerg::a32
