#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <iostream>
#include <map>
#include <string_view>
#include <vector>
#include "Elf/elfhelper.h"
#include "Util/assert.h"

namespace cwerg::elf {

template <typename elfsize_t>
struct Unit {


  Section<elfsize_t>* const sec_text;
  Section<elfsize_t>* const sec_rodata;
  Section<elfsize_t>* const sec_data;
  Section<elfsize_t>* const sec_bss;

  std::vector<Reloc<elfsize_t>> relocations;
  std::vector<std::unique_ptr<Symbol<elfsize_t>>> symbols;
  std::map<std::string_view, Symbol<elfsize_t>*> global_symbol_map;
  std::map<std::string_view, Symbol<elfsize_t>*> local_symbol_map;

  std::map<std::string_view, std::unique_ptr<std::string>> string_table;

  Unit()
      : sec_rodata(new Section<elfsize_t>()),
        sec_text(new Section<elfsize_t>()),
        sec_data(new Section<elfsize_t>()),
        sec_bss(new Section<elfsize_t>()) {
    sec_rodata->InitRodata(1);

    sec_text->InitText(1);

    sec_data->InitData(1);

    sec_bss->InitBss(1);
  }

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

  void AddFunAddr(unsigned size, uint32_t reloc_kind, std::string_view fun_name) {
    ASSERT(current_mem_sec != nullptr, "");
    auto* sym = FindOrAddSymbol(fun_name, false);
    AddReloc(reloc_kind, current_mem_sec, sym, 0);
    current_mem_sec->AddDataRepeatedBytes(size, 0);
  }

  void AddBblAddr(unsigned size, uint32_t reloc_kind, std::string_view bbl_name) {
    ASSERT(current_mem_sec != nullptr, "add bbl addr outside a mem directive");
    auto* sym = FindOrAddSymbol(bbl_name, true);
    AddReloc(reloc_kind, current_mem_sec, sym, 0);
    current_mem_sec->AddDataRepeatedBytes(size, 0);
  }

  void AddMemAddr(unsigned size, uint32_t reloc_kind, std::string_view mem_name, uint32_t addend) {  ASSERT(current_mem_sec != nullptr, "memaddr outside of mem");
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
  Symbol<elfsize_t>* AddSymbol(std::string_view name,
                                   Section<elfsize_t>* sec,
                                   bool is_local) {
    name = InternString(name);
    auto* the_map = is_local ? &local_symbol_map : &global_symbol_map;
    auto it = the_map->find(name);
    Symbol<elfsize_t>* sym = it == the_map->end() ? nullptr : it->second;
    if (sym == nullptr) {
      sym = new Symbol<elfsize_t>();
      sym->Init(name, is_local, sec, sec == nullptr ? ~0U : sec->data->size());
      symbols.emplace_back(std::unique_ptr<Symbol<elfsize_t>>(sym));
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

  Symbol<elfsize_t>* FindOrAddSymbol(std::string_view name, bool is_local) {
    auto* the_map = is_local ? &local_symbol_map : &global_symbol_map;
    auto it = the_map->find(name);
    if (it != the_map->end()) {
      return it->second;
    } else {
      return AddSymbol(name, nullptr, is_local);
    }
  }

  // Add a Reloc for Section sec at the current offset
  void AddReloc(uint32_t reloc_kind,
                const Section<elfsize_t>* sec,
                const Symbol<elfsize_t>* sym,
                uint32_t addend) {
    relocations.emplace_back(Reloc<elfsize_t>());
    relocations.back().Init(reloc_kind, sec, sec->data->size(), sym, addend);
  }

  void AddLinkerDefs() {
    if (sec_bss->shdr.sh_size > 0) {
      sec_bss->PadData(16, {"\0", 1});
      AddSymbol("$$rw_data_end", sec_bss, false);
    } else if (sec_data->shdr.sh_size > 0) {
      sec_data->PadData(16, {"\0", 1});
      AddSymbol("$$rw_data_end", sec_data, false);
    }
  }

 private:
  std::string_view current_fun_name = "";
  Section<elfsize_t>* current_mem_sec = nullptr;
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Unit<elfsize_t>& s) {
  os << *s.sec_text << "\n"
     << *s.sec_rodata << "\n"
     << *s.sec_data << "\n"
     << *s.sec_bss << "\n";

  os << "String Table\n";
  for (const auto& sym : s.symbols) {
    os << *sym << "\n";
  }
  os << "Reloc Table\n";
  for (const auto& rel : s.relocations) {
    os << rel << "\n";
  }
  return os;
}

}  // namespace
