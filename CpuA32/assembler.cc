// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/assembler.h"
#include "CpuA32/opcode_gen.h"
#include "CpuA32/symbolic.h"
#include "Util/parse.h"

#include <map>

namespace cwerg::a32 {
using namespace cwerg::elf;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

std::string_view padding_four_zero("\0\0\0\0", 4);
std::string_view padding_zero("\0", 1);
std::string_view padding_nop("\x00\xf0\x20\xe3", 4);

const char ARM_ATTRIBUTES[] = {0x41, 0x11, 0, 0, 0, 0x61, 0x65, 0x61, 0x62,
                               0x69, 0,    1, 7, 0, 0,    0,    8,    1};

void Unit::AddIns(Ins* ins) {
  if (ins->has_reloc()) {
    const elf::Symbol<uint32_t>* sym =
        FindOrAddSymbol(ins->reloc_symbol, ins->is_local_sym);
    AddReloc(+ins->reloc_kind, sec_text, sym, ins->operands[ins->reloc_pos]);
    ins->clear_reloc();
  }
  uint32_t data = Assemble(*ins);
  sec_text->AddData({(const char*)&data, 4});
}

std::array<std::string_view, 6> kStartupCode = {  //
    "ldr_imm_add al r0 sp 0",                     //
    "add_imm al r1 sp 4",                         //
    "bl expr:call:main",                       //
    "movw al r7 1",                               //
    "svc al 0",                                   //
    "ud2 al"};

void Unit::AddStartupCode() {
  FunStart("_start", 16, padding_nop);
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
    AddIns(&ins);
  }
  FunEnd();
}

void Unit::AddLinkerDefs() {
  if (sec_bss->shdr.sh_size > 0) {
    sec_bss->PadData(16, padding_zero);
    AddSymbol("$$rw_data_end", sec_bss, false);
  } else if (sec_data->shdr.sh_size > 0) {
    sec_data->PadData(16, padding_zero);
    AddSymbol("$$rw_data_end", sec_data, false);
  }
}

bool HandleDirective(Unit* unit, const std::vector<std::string_view>& token) {
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
    unit->AddMemAddr(ParseInt<uint32_t>(token[1]).value(), +RELOC_TYPE_ARM::ABS32, token[2],
                     ParseInt<uint32_t>(token[3]).value());
  } else if (mnemonic == ".addr.fun") {
    ASSERT(token.size() == 3, "");
    unit->AddFunAddr(ParseInt<uint32_t>(token[1]).value(), +RELOC_TYPE_ARM::ABS32, token[2]);
  } else if (mnemonic == ".addr.bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddBblAddr(ParseInt<uint32_t>(token[1]).value(), +RELOC_TYPE_ARM::ABS32, token[2]);
  } else if (mnemonic == ".bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddLabel(token[1], ParseInt<uint32_t>(token[2]).value(), padding_nop);
  } else {
    std::cerr << "unknown directive " << mnemonic << "\n";
    return false;
  }
  return true;
}




bool HandleOpcode(Unit* unit, const std::vector<std::string_view>& token) {
  Ins ins;
  if (!InsFromSymbolized(token, &ins)) {
    std::cerr << "parse error " << token[0] << "\n";
    return false;
  }
  unit->AddIns(&ins);
  return true;
}

Unit::Unit()
    : sec_rodata(new Section<uint32_t>()),
      sec_text(new Section<uint32_t>()),
      sec_data(new Section<uint32_t>()),
      sec_bss(new Section<uint32_t>()) {
  sec_rodata->InitRodata(1);

  sec_text->InitText(1);

  sec_data->InitData(1);

  sec_bss->InitBss(1);
}

bool UnitParse(std::istream* input, bool add_startup_code, Unit* unit) {
  Unit out;
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
    unit->AddStartupCode();
  }
  return true;
}



int32_t BranchOffset(const Reloc<uint32_t>& rel, int32_t sym_val) {
  return int32_t(sym_val - rel.section->shdr.sh_addr - rel.rel.r_offset - 8) >>
         2;
}

void ApplyRelocation(const Reloc<uint32_t>& rel) {
  void* patch_addr = (char*)rel.section->data->data() + rel.rel.r_offset;
  const uint32_t old_data = *(uint32_t*)patch_addr;
  const int32_t sym_val = rel.symbol->sym.st_value + rel.rel.r_addend;

  uint32_t new_data;
  switch (RELOC_TYPE_ARM(rel.rel.r_type)) {
    case RELOC_TYPE_ARM::ABS32:
      new_data = sym_val;
      break;
    case RELOC_TYPE_ARM::JUMP24:
      new_data = PatchIns(old_data, 1, BranchOffset(rel, sym_val));
      break;
    case RELOC_TYPE_ARM::CALL:
      new_data = PatchIns(old_data, 1, BranchOffset(rel, sym_val));
      break;
    case RELOC_TYPE_ARM::MOVW_ABS_NC:
      new_data = PatchIns(old_data, 2, sym_val & 0xffff);
      break;
    case RELOC_TYPE_ARM::MOVT_ABS:
      new_data = PatchIns(old_data, 2, (sym_val >> 16) & 0xffff);
      break;
    default:
      ASSERT(false, "unknown relocation type " << rel.rel.r_type);
      return;
  }
#if 0
  std::cout << "PATCH INS " << rel.rel.r_type << " " << std::hex
            << rel.rel.r_offset << " " << sym_val << " " << old_data << " "
            << new_data << std::dec << " " << rel.symbol->name << "\n";
#endif
  *(uint32_t*)patch_addr = new_data;
}

Executable<uint32_t> Unit::MakeExe(bool create_sym_tab) {
  std::vector<Section<uint32_t>*> sections;
  std::vector<Segment<uint32_t>*> segments;

  {
    auto seg_exe = new Segment<uint32_t>();
    seg_exe->InitExe(65536);
    segments.push_back(seg_exe);

    auto sec_null = new Section<uint32_t>();
    sec_null->InitNull();
    sections.push_back(sec_null);
    seg_exe->sections.push_back(sec_null);

    ASSERT(sec_text->data->size() > 0, "");
    sections.push_back(sec_text);
    seg_exe->sections.push_back(sec_text);
  }

  if (sec_rodata->data->size() > 0) {
    auto seg_ro = new Segment<uint32_t>();
    seg_ro->InitRO(65536);
    segments.push_back(seg_ro);

    sections.push_back(sec_rodata);
    seg_ro->sections.push_back(sec_rodata);
  }

  Segment<uint32_t>* seg_rw = nullptr;

  if (sec_data->data->size() + sec_bss->data->size() > 0) {
    seg_rw = new Segment<uint32_t>();
    seg_rw->InitRW(65536);
    segments.push_back(seg_rw);
  }

  if (sec_data->data->size() > 0) {
    sections.push_back(sec_data);
    seg_rw->sections.push_back(sec_data);
  }

  if (sec_bss->data->size() > 0) {
    sections.push_back(sec_bss);
    seg_rw->sections.push_back(sec_bss);
  }

  Section<uint32_t>* sec_symtab = nullptr;
  {
    auto seg_pseudo = new Segment<uint32_t>();
    seg_pseudo->InitPseudo();
    segments.push_back(seg_pseudo);
    auto sec_attr = new Section<uint32_t>();
    sec_attr->InitArmAttributes();
    sec_attr->SetData(
        new Chunk({ARM_ATTRIBUTES, sizeof(ARM_ATTRIBUTES)}, true));
    sections.push_back(sec_attr);
    seg_pseudo->sections.push_back(sec_attr);
    //
    if (create_sym_tab) {
      sec_symtab = new Section<uint32_t>();
      sec_symtab->InitSymTab(".symtab", sizeof(Elf_Sym<uint32_t>),
                             sections.size() + 1);
      sec_symtab->shdr.sh_info = symbols.size();
      std::string dummy(sizeof(Elf_Sym<uint32_t>) * symbols.size(), '\0');
      auto* sym_data = new Chunk(dummy, false);
      sec_symtab->SetData(sym_data);
      sections.push_back(sec_symtab);
      seg_pseudo->sections.push_back(sec_symtab);

      auto* names = new Chunk(padding_zero, false);
      for (auto& sym : symbols) {
        if (!sym->name.empty()) {
          sym->sym.st_name = names->size();
          names->AddData(sym->name);
          names->AddData(padding_zero);
        } else {
          sym->sym.st_name = 0;
        }
      }
      auto* sec_strtab = new Section<uint32_t>();
      sec_strtab->InitStrTab(".strtab");
      sec_strtab->SetData(names);
      sections.push_back(sec_strtab);
      seg_pseudo->sections.push_back(sec_strtab);
    }
    //
    auto sec_shstrtab = new Section<uint32_t>();
    sec_shstrtab->InitStrTab(".shstrtab");
    sections.push_back(sec_shstrtab);
    sec_shstrtab->SetData(MakeShStrTabContents(sections));
    seg_pseudo->sections.push_back(sec_shstrtab);
  }

  Executable<uint32_t> exe = MakeExecutableA32(0x20000, sections, segments);
  exe.UpdateVaddrsAndOffsets();
  for (auto& sym : symbols) {
    ASSERT(sym->sym.st_value != ~0, "undefined symbol " << sym->name);
    if (sym->section != nullptr) {
      ASSERT(sym->section->shdr.sh_addr != ~0,
             sym->name << "has bad sec " << *sym->section);
      sym->sym.st_value += sym->section->shdr.sh_addr;
      sym->sym.st_shndx = sym->section->index;
    }
  }

  for (auto& rel : relocations) {
    ApplyRelocation(rel);
  }

  if (create_sym_tab) {
    ASSERT(sec_symtab != nullptr, "");

    auto* sym_data = new Chunk("", false);
    for (auto& sym : symbols) {
      sym_data->AddData({(const char*)&sym->sym, sizeof(sym->sym)});
    }
    ASSERT(sec_symtab->shdr.sh_size == sym_data->size(), "");
    sec_symtab->SetData(sym_data);
  }

  auto* entry = global_symbol_map["_start"];
  ASSERT(entry != nullptr, "_start is not defined");
  exe.ehdr.e_entry = entry->sym.st_value;
  return exe;
}

std::ostream& operator<<(std::ostream& os, const Unit& s) {
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

}  // namespace cwerg::a32
