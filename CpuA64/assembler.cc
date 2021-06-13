// (c) Robert Muth - see LICENSE for more info

#include "CpuA64/assembler.h"
#include "CpuA64/opcode_gen.h"
#include "CpuA64/symbolic.h"
#include "Util/parse.h"

#include <map>

namespace cwerg::a64 {
using namespace cwerg::elf;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

std::string_view padding_zero("\0", 1);
std::string_view padding_nop("\x1f\x20\x03\xd5", 4);

void AddIns(A64Unit* unit, Ins* ins) {
  if (ins->has_reloc()) {
    const elf::Symbol<uint64_t>* sym =
        unit->FindOrAddSymbol(ins->reloc_symbol, ins->is_local_sym);
    unit->AddReloc(+ins->reloc_kind, unit->sec_text, sym,
                   ins->operands[ins->reloc_pos]);
    ins->clear_reloc();
  }
  uint32_t data = Assemble(*ins);
  unit->sec_text->AddData({(const char*)&data, 4});
}

std::array<std::string_view, 6> kStartupCode = {"ldr_x_imm x0 sp 0",    //
                                                "add_x_imm x1 sp 8",    //
                                                "bl expr:call26:main",  //
                                                "movz_x_imm x8 0x5d",   //
                                                "svc 0",                //
                                                "brk 1"};

void AddStartupCode(A64Unit* unit) {
  unit->FunStart("_start", 16, padding_nop);
  std::vector<std::string_view> token;
  for (const auto line : kStartupCode) {
    token.clear();
    if (!ParseLineWithStrings(line, false, &token)) {
      ASSERT(false, "bad internal code template " << line);
    }
    Ins ins;
    if (!InsFromSymbolized(token, &ins)) {
      ASSERT(false, "internal parse error " << token[0]);
    }
    AddIns(unit, &ins);
  }
  unit->FunEnd();
}

bool HandleDirective(A64Unit* unit,
                     const std::vector<std::string_view>& token) {
  const auto mnemonic = token[0];
  if (mnemonic == ".fun") {
    ASSERT(token.size() == 3, "");
    unit->FunStart(token[1], ParseInt<uint32_t>(token[2]).value(), padding_nop);
  } else if (mnemonic == ".endfun") {
    unit->FunEnd();
  } else if (mnemonic == ".mem") {
    ASSERT(token.size() == 4, "");
    unit->MemStart(token[1], ParseInt<uint32_t>(token[2]).value(), token[3],
                   padding_zero, false);
  } else if (mnemonic == ".localmem") {
    ASSERT(token.size() == 4, "");
    unit->MemStart(token[1], ParseInt<uint32_t>(token[2]).value(), token[3],
                   padding_zero, true);
  } else if (mnemonic == ".endmem") {
    unit->MemEnd();
  } else if (mnemonic == ".data") {
    ASSERT(token.size() == 3, "");
    size_t len = token[2].size();
    if (token[2][0] != '"' || token[2][len - 1] != '"' || len <= 2) {
      std::cerr << "malformed .data directive\n";
      return false;
    }
    char buffer[1024];
    len = EscapedStringToBytes({token[2].data() + 1, len - 2}, buffer);
    if (len == 0) {
      std::cerr << "malformed .data directive cannot parse payload\n";
      return false;
    }
    unit->AddData(ParseInt<uint32_t>(token[1]).value(), buffer, len);
  } else if (mnemonic == ".addr.mem") {
    ASSERT(token.size() == 4, "");
    unit->AddMemAddr(ParseInt<uint32_t>(token[1]).value(),
                     +RELOC_TYPE_ARM::ABS32, token[2],
                     ParseInt<uint32_t>(token[3]).value());
  } else if (mnemonic == ".addr.fun") {
    ASSERT(token.size() == 3, "");
    unit->AddFunAddr(ParseInt<uint32_t>(token[1]).value(),
                     +RELOC_TYPE_ARM::ABS32, token[2]);
  } else if (mnemonic == ".addr.bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddBblAddr(ParseInt<uint32_t>(token[1]).value(),
                     +RELOC_TYPE_ARM::ABS32, token[2]);
  } else if (mnemonic == ".bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddLabel(token[1], ParseInt<uint32_t>(token[2]).value(), padding_nop);
  } else {
    std::cerr << "unknown directive " << mnemonic << "\n";
    return false;
  }
  return true;
}

bool HandleOpcode(A64Unit* unit, const std::vector<std::string_view>& token) {
  Ins ins;
  if (!InsFromSymbolized(token, &ins)) {
    std::cerr << "parse error " << token[0] << "\n";
    return false;
  }
  AddIns(unit, &ins);
  return true;
}

bool UnitParse(std::istream* input, bool add_startup_code, A64Unit* unit) {
  A64Unit out;
  int line_num = 0;
  std::vector<std::string_view> token;
  for (std::string line; getline(*input, line);) {
    ++line_num;
    token.clear();
    if (!ParseLineWithStrings(line.c_str(), false, &token)) {
      std::cerr << "Error while parsing line " << line_num << "\n" << line;
      return false;
    }

    // std::cerr << "@@reading: " << line << "\n";
    if (token.empty()) continue;
    if (token[0][0] == '#') continue;
    if (token.back()[0] == '#') token.pop_back();  // get rid of comment
    // Directives
    if (token[0][0] == '.') {
      if (!HandleDirective(unit, token)) return false;
    } else {
      if (!HandleOpcode(unit, token)) return false;
    }
  }
  unit->AddLinkerDefs();
  if (add_startup_code) {
    AddStartupCode(unit);
  }
  return true;
}

int64_t BranchOffset(const Reloc<uint64_t>& rel, int64_t sym_val) {
  return (sym_val - (rel.section->shdr.sh_addr + rel.rel.r_offset)) >> 2;
}

int64_t AdrpOffset(const Reloc<uint64_t>& rel, int64_t sym_val) {
  return (sym_val >> 12ULL) -
         ((rel.section->shdr.sh_addr + rel.rel.r_offset) >> 12ULL);
}

void ApplyInsReloc(uint32_t* patch_addr, unsigned pos, uint32_t val) {
  *patch_addr = a64::Patch(*patch_addr, pos, val);
}

void ApplyRelocation(const Reloc<uint64_t>& rel) {
  void* patch_addr = (char*)rel.section->data->data() + rel.rel.r_offset;
  const int64_t sym_val = rel.symbol->sym.st_value + rel.rel.r_addend;

  switch (RELOC_TYPE_AARCH64(rel.rel.r_type)) {
    case RELOC_TYPE_AARCH64::ADR_PREL_PG_HI21:
      ApplyInsReloc((uint32_t*)patch_addr, 1, AdrpOffset(rel, sym_val));
      return;
    case RELOC_TYPE_AARCH64::ADD_ABS_LO12_NC:
      ApplyInsReloc((uint32_t*)patch_addr, 2, sym_val & 0xfff);
      return;
    case RELOC_TYPE_AARCH64::CONDBR19:
      ApplyInsReloc((uint32_t*)patch_addr, 0, BranchOffset(rel, sym_val));
      return;
    case RELOC_TYPE_AARCH64::JUMP26:
      ApplyInsReloc((uint32_t*)patch_addr, 0, BranchOffset(rel, sym_val));
      return;
    case RELOC_TYPE_AARCH64::CALL26:
      ApplyInsReloc((uint32_t*)patch_addr, 0, BranchOffset(rel, sym_val));
      return;
    case RELOC_TYPE_AARCH64::ABS32:
      ASSERT(sym_val >> 32ULL == 0, "");
      *(uint32_t*)patch_addr = sym_val;
      return;
    case RELOC_TYPE_AARCH64::ABS64:
      *(uint64_t*)patch_addr = sym_val;
      return;
    default:
      ASSERT(false, "unknown relocation type " << rel.rel.r_type);
      return;
  }
}

Executable<uint64_t> MakeExe(A64Unit* unit, bool create_sym_tab) {
  std::vector<Section<uint64_t>*> sections;
  std::vector<Segment<uint64_t>*> segments;

  {
    auto seg_exe = new Segment<uint64_t>();
    seg_exe->InitExe(65536);
    segments.push_back(seg_exe);

    auto sec_null = new Section<uint64_t>();
    sec_null->InitNull();
    sections.push_back(sec_null);
    seg_exe->sections.push_back(sec_null);

    ASSERT(unit->sec_text->data->size() > 0, "");
    sections.push_back(unit->sec_text);
    seg_exe->sections.push_back(unit->sec_text);
  }

  if (unit->sec_rodata->data->size() > 0) {
    auto seg_ro = new Segment<uint64_t>();
    seg_ro->InitRO(65536);
    segments.push_back(seg_ro);

    sections.push_back(unit->sec_rodata);
    seg_ro->sections.push_back(unit->sec_rodata);
  }

  Segment<uint64_t>* seg_rw = nullptr;

  if (unit->sec_data->data->size() + unit->sec_bss->data->size() > 0) {
    seg_rw = new Segment<uint64_t>();
    seg_rw->InitRW(65536);
    segments.push_back(seg_rw);
  }

  if (unit->sec_data->data->size() > 0) {
    sections.push_back(unit->sec_data);
    seg_rw->sections.push_back(unit->sec_data);
  }

  if (unit->sec_bss->data->size() > 0) {
    sections.push_back(unit->sec_bss);
    seg_rw->sections.push_back(unit->sec_bss);
  }

  Section<uint64_t>* sec_symtab = nullptr;
  {
    auto seg_pseudo = new Segment<uint64_t>();
    seg_pseudo->InitPseudo();
    segments.push_back(seg_pseudo);
    //
    if (create_sym_tab) {
      sec_symtab = new Section<uint64_t>();
      sec_symtab->InitSymTab(".symtab", sizeof(Elf_Sym<uint64_t>),
                             sections.size() + 1);
      sec_symtab->shdr.sh_info = unit->symbols.size();
      std::string dummy(sizeof(Elf_Sym<uint64_t>) * unit->symbols.size(), '\0');
      auto* sym_data = new Chunk(dummy, false);
      sec_symtab->SetData(sym_data);
      sections.push_back(sec_symtab);
      seg_pseudo->sections.push_back(sec_symtab);

      auto* names = new Chunk(padding_zero, false);
      for (auto& sym : unit->symbols) {
        if (!sym->name.empty()) {
          sym->sym.st_name = names->size();
          names->AddData(sym->name);
          names->AddData(padding_zero);
        } else {
          sym->sym.st_name = 0;
        }
      }
      auto* sec_strtab = new Section<uint64_t>();
      sec_strtab->InitStrTab(".strtab");
      sec_strtab->SetData(names);
      sections.push_back(sec_strtab);
      seg_pseudo->sections.push_back(sec_strtab);
    }
    //
    auto sec_shstrtab = new Section<uint64_t>();
    sec_shstrtab->InitStrTab(".shstrtab");
    sections.push_back(sec_shstrtab);
    sec_shstrtab->SetData(MakeShStrTabContents(sections));
    seg_pseudo->sections.push_back(sec_shstrtab);
  }

  Executable<uint64_t> exe = MakeExecutableA64(0x400000, sections, segments);
  exe.ehdr.e_shoff = exe.UpdateVaddrsAndOffsets(
      CombinedElfHeaderSize<uint64_t>(exe.segments), exe.start_vaddr);
  exe.ehdr.e_phoff = sizeof(exe.ident) + sizeof(exe.ehdr);

  for (auto& sym : unit->symbols) {
    ASSERT(sym->sym.st_value != ~0, "undefined symbol " << sym->name);
    if (sym->section != nullptr) {
      ASSERT(sym->section->shdr.sh_addr != ~0,
             sym->name << "has bad sec " << *sym->section);
      sym->sym.st_value += sym->section->shdr.sh_addr;
      sym->sym.st_shndx = sym->section->index;
    }
  }

  for (auto& rel : unit->relocations) {
    ApplyRelocation(rel);
  }

  if (create_sym_tab) {
    ASSERT(sec_symtab != nullptr, "");

    auto* sym_data = new Chunk("", false);
    for (auto& sym : unit->symbols) {
      sym_data->AddData({(const char*)&sym->sym, sizeof(sym->sym)});
    }
    ASSERT(sec_symtab->shdr.sh_size == sym_data->size(), "");
    sec_symtab->SetData(sym_data);
  }

  auto* entry = unit->global_symbol_map["_start"];
  ASSERT(entry != nullptr, "_start is not defined");
  exe.ehdr.e_entry = entry->sym.st_value;
  return exe;
}

}  // namespace cwerg::a64
