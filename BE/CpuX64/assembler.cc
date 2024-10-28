// (c) Robert Muth - see LICENSE for more info

#include "BE/CpuX64/assembler.h"

#include <map>

#include "BE/CpuX64/opcode_gen.h"
#include "BE/CpuX64/symbolic.h"
#include "Util/parse.h"

namespace cwerg::x64 {
using namespace cwerg::elf;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

std::string_view padding_zero("\0", 1);

const std::array<const std::string_view, 10> kCodePaddingSequences = {
    std::string_view{"", 0},
    std::string_view{"\x90", 1},
    std::string_view{"\x66\x90", 2},
    std::string_view{"\x0f\x1f\x00", 3},
    std::string_view{"\x0f\x1f\x40\x00", 4},
    std::string_view{"\x0f\x1f\x44\x00\x00", 5},
    std::string_view{"\x66\x0f\x1f\x44\x00\x00", 6},
    std::string_view{"\x0f\x1f\x08\x00\x00\x00\x00", 7},
    std::string_view{"\x0f\x1f\x84\x00\x00\x00\x00\x00", 8},
    std::string_view{"\x66\x0f\x1f\x84\x00\x00\x00\x00\x00", 9}};

void TextPadder(size_t len, std::string* s) {
  const std::string_view largest = kCodePaddingSequences.back();
  while (len > largest.size()) {
    s->append(largest);
    len -= largest.size();
  }
  s->append(kCodePaddingSequences[len]);
}

uint32_t RelocFieldOffsetFromEndOfIns(const x64::Opcode& opcode) {
  if (opcode.offset_pos != NA) {
    return opcode.num_bytes - opcode.offset_pos;
  } else {
    ASSERT(opcode.imm_pos != NA, "");
    return opcode.num_bytes - opcode.imm_pos;
  }
}

void AddIns(X64Unit* unit, Ins* ins) {
  char buffer[64];
  uint32_t len;
  if (ins->has_reloc()) {
    const elf::Symbol<uint64_t>* sym =
        unit->FindOrAddSymbol(ins->reloc_symbol, ins->is_local_sym);
    const elf::RELOC_TYPE_X86_64 kind = ins->reloc_kind;
    int64_t addend = ins->operands[ins->reloc_pos];
    ins->clear_reloc();
    len = Assemble(*ins, buffer);
    const uint32_t distance_to_ins_end =
        RelocFieldOffsetFromEndOfIns(*ins->opcode);
    if (kind == elf::RELOC_TYPE_X86_64::PC32) {
      addend -= distance_to_ins_end;
    }
    unit->AddReloc(+kind, unit->sec_text, sym, addend,
                   len - distance_to_ins_end);
  } else {
    len = Assemble(*ins, buffer);
  }
  unit->sec_text->AddData({buffer, len});
}

std::array<std::string_view, 12> kStartupCode = {
    "mov_64_r_mbis8 rdi rsp noindex 0 0", "lea_64_r_mbis8 rsi rsp noindex 0 8",
    "lea_64_r_mbis8 rdx rsp rdi 3 16",
    // default mxcsr is 0x1f80
    // description: https://wiki.osdev.org/SSE
    // force "rounding down"
    "stmxcsr_32_mbis8 rsp noindex 0 -4",
    "and_32_mbis8_imm32 rsp noindex 0 -4 0xffff9fff",
    "or_32_mbis8_imm32 rsp noindex 0 -4 0x2000",
    "ldmxcsr_32_mbis8 rsp noindex 0 -4", "call_32 expr:pcrel32:main",
    // edi contains result from main
    "mov_32_r_imm32 edi 0x0", "mov_64_mr_imm32 rax 0x3c", "syscall",
    // unreachable
    "int3"};

void AddStartupCode(X64Unit* unit) {
  unit->FunStart("main", 16, TextPadder);
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

bool HandleDirective(X64Unit* unit,
                     const std::vector<std::string_view>& token) {
  const auto mnemonic = token[0];
  if (mnemonic == ".fun") {
    ASSERT(token.size() == 3, "");
    unit->FunStart(token[1], ParseInt<uint32_t>(token[2]).value(), TextPadder);
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
                     +RELOC_TYPE_AARCH64::ABS64, token[2],
                     ParseInt<uint32_t>(token[3]).value());
  } else if (mnemonic == ".addr.fun") {
    ASSERT(token.size() == 3, "");
    unit->AddFunAddr(ParseInt<uint32_t>(token[1]).value(),
                     +RELOC_TYPE_AARCH64::ABS64, token[2]);
  } else if (mnemonic == ".addr.bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddBblAddr(ParseInt<uint32_t>(token[1]).value(),
                     +RELOC_TYPE_AARCH64::ABS64, token[2]);
  } else if (mnemonic == ".bbl") {
    ASSERT(token.size() == 3, "");
    unit->AddLabel(token[1], ParseInt<uint32_t>(token[2]).value(), TextPadder);
  } else {
    std::cerr << "unknown directive " << mnemonic << "\n";
    return false;
  }
  return true;
}

bool HandleOpcode(X64Unit* unit, const std::vector<std::string_view>& token) {
  Ins ins;
  if (!InsFromSymbolized(token, &ins)) {
    std::cerr << "parse error " << token[0] << "\n";
    return false;
  }
  AddIns(unit, &ins);
  return true;
}

bool UnitParse(std::istream* input, X64Unit* unit) {
  X64Unit out;
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
  return true;
}

int32_t PcOffset32(const Reloc<uint64_t>& rel, int64_t sym_val) {
  int64_t offset = sym_val - (rel.section->shdr.sh_addr + rel.rel.r_offset);
  ASSERT((-int64_t(1LL << 31) <= offset) && offset < int64_t(1LL << 31),
         "PcOffset overflow " << offset << " for symbol " << rel.symbol->name);
  return offset;
}

uint32_t RelWidth(RELOC_TYPE_X86_64 rel_type) {
  return rel_type == elf::RELOC_TYPE_X86_64::X_64 ? 8 : 4;
}

void ApplyRelocation(const Reloc<uint64_t>& rel) {
  void* patch_addr = (char*)rel.section->data->data() + rel.rel.r_offset;
  const int64_t sym_val = rel.symbol->sym.st_value + rel.rel.r_addend;
  const uint32_t width = RelWidth(RELOC_TYPE_X86_64(rel.rel.r_type));
  ASSERT(rel.rel.r_offset + width <= rel.section->data->size(), "Relocation out of bounds " <<
    rel.rel.r_offset + width << " " << rel.section->data->size() << " " << rel);
  switch (RELOC_TYPE_X86_64(rel.rel.r_type)) {
    case elf::RELOC_TYPE_X86_64::PC32:
      *((int32_t*)patch_addr) = PcOffset32(rel, sym_val);
      return;
    case elf::RELOC_TYPE_X86_64::X_64:
      *((int64_t*)patch_addr) = sym_val;
      return;
    default:
      ASSERT(false, "unknown relocation type " << rel.rel.r_type);
      return;
  }
}

Executable<uint64_t> MakeExe(X64Unit* unit, bool create_sym_tab) {
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

    ASSERT(unit->sec_text->data->size() > 0, "text sec has no data " << unit->sec_text->data->size());
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

  Executable<uint64_t> exe = MakeExecutableX64(0x400000, sections, segments);
  exe.ehdr.e_shoff = exe.UpdateVaddrsAndOffsets(
      CombinedElfHeaderSize<uint64_t>(exe.segments), exe.start_vaddr);
  exe.ehdr.e_phoff = sizeof(exe.ident) + sizeof(exe.ehdr);

  for (auto& sym : unit->symbols) {
    ASSERT(sym->sym.st_value != ~0U, "undefined symbol " << sym->name);
    if (sym->section != nullptr) {
      ASSERT(sym->section->shdr.sh_addr != ~0U,
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

}  // namespace cwerg::x64
