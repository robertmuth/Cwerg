// (c) Robert Muth - see LICENSE for more info

#include "CpuA32/assembler.h"
#include "CpuA32/opcode_gen.h"
#include "Util/parse.h"

#include <map>

namespace cwerg::a32 {
using namespace cwerg::elf;

// clang-format off
// @formatter:off
std::map<std::string_view, uint32_t> operand_symbols = {
    {"eq", 0}, {"ne", 1}, {"cs", 2}, {"cc", 3},
    {"mi", 4}, {"pl", 5}, {"vs", 6}, {"vc", 7},
    {"hi", 8},   {"ls", 9}, {"ge", 10}, {"lt", 11},
    {"gt", 12}, {"le", 13},  {"al", 14},
     //
    {"r0", 0},  {"r1", 1}, {"r2", 2}, {"r3", 3},
    {"r4", 4}, {"r5", 5}, {"r6", 6}, {"r7", 7},
    {"r8", 8}, {"r9", 9}, {"r10", 10}, {"r11", 11},
    {"r12", 12}, {"r13", 13}, {"r14", 14}, {"r15", 15},
    //
    {"sl", 10}, {"fp", 11},
    {"ip", 12}, {"sp", 13}, {"lr", 14}, {"pc", 15},
    //
    {"s0", 0}, {"s1", 1}, {"s2", 2}, {"s3", 3},
    {"s4", 4}, {"s5", 5}, {"s6", 6}, {"s7", 7},
    {"s8", 8}, {"s9", 9}, {"s10", 10}, {"s11", 11},
    {"s12", 12}, {"s13", 13}, {"s14", 14}, {"s15", 15},
    //
    {"s16", 16}, {"s17", 17}, {"s18", 18}, {"s19", 19},
    {"s20", 20}, {"s21", 21}, {"s22", 22}, {"s23", 23},
    {"s24", 24}, {"s25", 25}, {"s26", 26}, {"s27", 27},
    {"s28", 28}, {"s29", 29}, {"s30", 30}, {"s31", 31},
    //
    {"d0", 0}, {"d1", 1}, {"d2", 2}, {"d3", 3},
    {"d4", 4}, {"d5", 5}, {"d6", 6}, {"d7", 7},
    {"d8", 8}, {"d9", 9}, {"d10", 10}, {"d11", 11},
    {"d12", 12}, {"d13", 13}, {"d14", 14}, {"d15", 15},
    //
    {"puw", 0}, {"puW", 1}, {"pUw", 2}, {"pUW", 3},
    {"Puw", 4}, {"PuW", 5}, {"PUw", 6}, {"PUW", 7},
    //
    {"lsl",  0}, {"lsr", 1}, {"asr", 2}, {"ror_rrx", 3},
};
// @formatter:on
// clang-format on

std::string_view padding_four_zero("\0\0\0\0", 4);
std::string_view padding_zero("\0", 1);
std::string_view padding_nop("\x00\xf0\x20\xe3", 4);

const char ARM_ATTRIBUTES[] = {0x41, 0x11, 0, 0, 0, 0x61, 0x65, 0x61, 0x62,
                               0x69, 0,    1, 7, 0, 0,    0,    8,    1};

Symbol<uint32_t>* Unit::AddSymbol(std::string_view name,
                                  Section<uint32_t>* sec,
                                  bool is_local) {
  name = InternString(name);
  auto* the_map = is_local ? &local_symbol_map : &global_symbol_map;
  auto it = the_map->find(name);
  Symbol<uint32_t>* sym = it == the_map->end() ? nullptr : it->second;
  if (sym == nullptr) {
    sym = new Symbol<uint32_t>();
    sym->Init(name, is_local, sec, sec == nullptr ? ~0 : sec->data->size());
    symbols.emplace_back(std::unique_ptr<Symbol<uint32_t>>(sym));
    (*the_map)[name] = sym;
    return sym;
  }
  ASSERT(sec != nullptr && sym->section == nullptr, "");
  sym->section = sec;
  sym->sym.st_value = sec->data->size();
  return sym;
}

void Unit::FunStart(std::string_view name, unsigned alignment) {
  ASSERT(current_fun_name.empty(), "");
  current_fun_name = name;
  sec_text->PadData(alignment, padding_nop);
  AddSymbol(name, sec_text, false);
}

void Unit::FunEnd() {
  ASSERT(!current_fun_name.empty(), "");
  current_fun_name = "";
  local_symbol_map.clear();
}

void Unit::MemStart(std::string_view name,
                    unsigned alignment,
                    std::string_view kind) {
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
  current_mem_sec->PadData(alignment, padding_zero);
  AddSymbol(name, current_mem_sec, false);
}

void Unit::MemEnd() {
  ASSERT(current_mem_sec != nullptr, "");
  current_mem_sec = nullptr;
}

void Unit::AddData(unsigned repeats, const void* data, size_t len) {
  ASSERT(current_mem_sec != nullptr, "");
  for (unsigned i = 0; i < repeats; ++i) {
    current_mem_sec->AddData({(const char*)data, len});
  }
}

void Unit::AddFunAddr(unsigned size, std::string_view fun_name) {
  ASSERT(current_mem_sec != nullptr, "");
  ASSERT(size == 4, "");
  auto* sym = FindOrAddSymbol(fun_name, false);
  AddReloc(RELOC_TYPE_ARM::ABS32, current_mem_sec, sym, 0);
  current_mem_sec->AddData(padding_four_zero);
}

void Unit::AddBblAddr(unsigned size, std::string_view bbl_name) {
  ASSERT(current_mem_sec != nullptr, "");
  ASSERT(size == 4, "");
  auto* sym = FindOrAddSymbol(bbl_name, true);
  AddReloc(RELOC_TYPE_ARM::ABS32, current_mem_sec, sym, 0);
  current_mem_sec->AddData(padding_four_zero);
}

void Unit::AddMemAddr(unsigned size,
                      std::string_view mem_name,
                      uint32_t addend) {
  ASSERT(current_mem_sec != nullptr, "memaddr outside of mem");
  ASSERT(size == 4, "");
  ASSERT(addend == 0, "NYI");
  auto* sym = FindOrAddSymbol(mem_name, false);
  AddReloc(RELOC_TYPE_ARM::ABS32, current_mem_sec, sym, 0);
  current_mem_sec->AddData(padding_four_zero);
}

void Unit::AddLabel(std::string_view name, unsigned alignment) {
  sec_text->PadData(alignment, padding_nop);
  ASSERT(!current_fun_name.empty(), "");
  AddSymbol(name, sec_text, true);
}

void Unit::AddIns(Ins* ins) {
  if (ins->has_reloc()) {
    const elf::Symbol<uint32_t>* sym = FindOrAddSymbol(
        ins->reloc_symbol, ins->reloc_kind == elf::RELOC_TYPE_ARM::JUMP24);
    AddReloc(ins->reloc_kind, sec_text, sym, ins->operands[ins->reloc_pos]);
    ins->clear_reloc();
  }
  uint32_t data = EncodeIns(*ins);
  sec_text->AddData({(const char*)&data, 4});
}

std::array<std::string_view, 6> kStartupCode = {  //
    "ldr_imm al r0 PUw sp 0",                     //
    "add_imm al r1 sp 4",                         //
    "bl al expr:call:main",                       //
    "movw al r7 1",                               //
    "svc al 0",                                   //
    "ud2 al"};

void Unit::AddStartupCode() {
  FunStart("_start", 16);
  std::vector<std::string_view> token;
  for (const auto line : kStartupCode) {
    token.clear();
    if (!ParseLineWithStrings(line, false, &token)) {
      ASSERT(false, "bad internal code template " << line);
    }
    Ins ins;
    if (!InsParse(token, &ins)) {
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
    unit->FunStart(token[1], ParseInt<uint32_t>(token[2]).value());
  } else if (mnemonic == ".endfun") {
    unit->FunEnd();
  } else if (mnemonic == ".mem") {
    ASSERT(token.size() == 4, "");
    unit->MemStart(token[1], ParseInt<uint32_t>(token[2]).value(), token[3]);
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
    unit->AddMemAddr(ParseInt<uint32_t>(token[1]).value(), token[2],
                     ParseInt<uint32_t>(token[3]).value());
  } else if (mnemonic == ".addr.fun") {
    ASSERT(token.size() == 3, "");
    unit->AddFunAddr(ParseInt<uint32_t>(token[1]).value(), token[2]);
  } else if (mnemonic == ".addr.bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddBblAddr(ParseInt<uint32_t>(token[1]).value(), token[2]);
  } else if (mnemonic == ".bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddLabel(token[1], ParseInt<uint32_t>(token[2]).value());
  } else {
    std::cerr << "unknown directive " << mnemonic << "\n";
    return false;
  }
  return true;
}

std::optional<uint32_t> UnsymbolizeOperand(std::string_view s) {
  size_t colon_pos = s.find(':');
  if (colon_pos == std::string_view::npos) {
    auto it = operand_symbols.find(s);
    if (it != operand_symbols.end()) {
      return it->second;
    }
    return ParseInt<uint32_t>(s);
  }
  std::string_view num({s.data() + colon_pos + 1, s.size() - colon_pos - 1});
  return ParseInt<uint32_t>(num);
}

bool HandleRelocation(std::string_view expr, unsigned pos, Ins* ins) {
  ins->reloc_pos = pos;
  const size_t colon_sym = expr.find(':');
  if (colon_sym == std::string_view::npos) return false;
  const std::string_view kind_name = expr.substr(0, colon_sym);
  RELOC_TYPE_ARM rel_type;
  if (kind_name == "abs32") {
    ins->reloc_kind = RELOC_TYPE_ARM::ABS32;
  } else if (kind_name == "jump24") {
    ins->reloc_kind = RELOC_TYPE_ARM::JUMP24;
  } else if (kind_name == "call") {
    ins->reloc_kind = RELOC_TYPE_ARM::CALL;
  } else if (kind_name == "movw_abs_nc") {
    ins->reloc_kind = RELOC_TYPE_ARM::MOVW_ABS_NC;
  } else if (kind_name == "movt_abs") {
    ins->reloc_kind = RELOC_TYPE_ARM::MOVT_ABS;
  } else {
    return false;
  }
  //
  std::string_view rest = expr.substr(colon_sym + 1);
  const size_t colon_addend = rest.find(':');
  ins->reloc_symbol = rest.substr(0, colon_addend);

  ins->operands[pos] = 0;
  if (colon_addend != std::string_view::npos) {
    auto val = ParseInt<int32_t>(rest.substr(colon_addend + 1));
    if (!val.has_value()) return false;
    ins->operands[pos] = val.value();
  }
  return true;
}

bool InsParse(const std::vector<std::string_view>& token, Ins* ins) {
  ins->opcode = FindArmOpcodeForMnemonic(token[0]);
  if (ins->opcode == nullptr) {
    std::cerr << "unknown opcode " << token[0] << "\n";
    return false;
  }
  uint32_t operand_count = 0;
  if (token.size() == ins->opcode->num_fields) {
    ins->operands[operand_count++] = 14;  // predicate 'al'
  }
  ASSERT(token.size() - 1 + operand_count == ins->opcode->num_fields, "");
  for (unsigned i = 1; i < token.size(); ++i, ++operand_count) {
    if (token[i].substr(0, 5) == "expr:") {
      if (!HandleRelocation(token[i].substr(5), operand_count, ins)) {
        std::cerr << "malformed relocation expression " << token[i] << "\n";
        return false;
      }
    } else {
      auto val = UnsymbolizeOperand(token[i]);
      if (!val.has_value()) return false;
      ins->operands[operand_count] = val.value();
    }
  }
  return true;
}

bool HandleOpcode(Unit* unit, const std::vector<std::string_view>& token) {
  Ins ins;
  if (!InsParse(token, &ins)) {
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

uint32_t PatchA32Ins(uint32_t ins_old, unsigned pos, int32_t value) {
  Ins ins;
  CHECK(DecodeIns(&ins, ins_old), "");
  ins.operands[pos] = value;
  return EncodeIns(ins);
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
      new_data = PatchA32Ins(old_data, 1, BranchOffset(rel, sym_val));
      break;
    case RELOC_TYPE_ARM::CALL:
      new_data = PatchA32Ins(old_data, 2, BranchOffset(rel, sym_val));
      break;
    case RELOC_TYPE_ARM::MOVW_ABS_NC:
      new_data = PatchA32Ins(old_data, 2, sym_val & 0xffff);
      break;
    case RELOC_TYPE_ARM::MOVT_ABS:
      new_data = PatchA32Ins(old_data, 2, (sym_val >> 16) & 0xffff);
      break;
    default:
      ASSERT(false, "unknown relocation type " << rel.rel.r_type);
      return;
  }
  std::cout << "PATCH INS " << rel.rel.r_type
            << " " << std::hex << rel.rel.r_offset << " "
            << sym_val << " " << old_data << " "
            << new_data << std::dec << " " << rel.symbol->name << "\n";
  *(uint32_t*)patch_addr = new_data;
}

Executable<uint32_t> Unit::Assemble(bool create_sym_tab) {
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
      Chunk* sym_data = new Chunk(dummy, false);
      sec_symtab->SetData(sym_data);
      sections.push_back(sec_symtab);
      seg_pseudo->sections.push_back(sec_symtab);

      Chunk* names = new Chunk(padding_zero, false);
      for (auto& sym : symbols) {
        if (!sym->name.empty()) {
          sym->sym.st_name = names->size();
          names->AddData(sym->name);
          names->AddData(padding_zero);
        } else {
          sym->sym.st_name = 0;
        }
      }
      Section<uint32_t>* sec_strtab = new Section<uint32_t>();
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

    Chunk* sym_data = new Chunk("", false);
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
