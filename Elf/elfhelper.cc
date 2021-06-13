// (c) Robert Muth - see LICENSE for more info

#include "Elf/elfhelper.h"
#include "Elf/enum_gen.h"
#include "Util/assert.h"

#include <iomanip>
#include <iostream>
#include <string_view>

namespace cwerg::elf {

size_t Align(size_t x, size_t align) {
  if (align <= 1) return x;
  return ((x + align - 1) / align) * align;
}

template <typename elfsize_t>
bool is_inside(elfsize_t src_off,
               elfsize_t src_sz,
               elfsize_t dst_off,
               elfsize_t dst_sz) {
  return dst_off <= src_off && src_off <= dst_off + dst_sz &&
         dst_off <= src_off + src_sz && src_off + src_sz <= dst_off + dst_sz;
}

bool Elf_EhdrIdent::IsValid() const {
  return std::string_view(ei_magic, sizeof(EHDR_MAGIC)) ==
         std::string_view(EHDR_MAGIC, sizeof(EHDR_MAGIC));
}

EI_CLASS ElfDetermineClass(std::string_view data) {
  const Elf_EhdrIdent* ident =
      reinterpret_cast<const Elf_EhdrIdent*>(data.data());
  if (data.size() < sizeof(Elf_EhdrIdent) || !ident->IsValid() ||
      ident->ei_data != EI_DATA::LSB2) {
    return EI_CLASS::NONE;
  }

  return ident->ei_class;
}

template <typename Flag>
std::string_view FirstCharFlagString(uint32_t flag, char buf[64]) {
  size_t pos = 0;
  for (unsigned i = 0; i < 32; ++i) {
    if ((flag & (1 << i)) != 0) buf[pos++] = EnumToString<Flag>(Flag(i))[0];
  }
  return {buf, pos};
}

// Section Helpers

bool IsAuxiliaryPhdr(P_TYPE p_type) {
  switch (p_type) {
    case P_TYPE::GNU_STACK:
    case P_TYPE::GNU_PROPERTY:
    case P_TYPE::GNU_RELRO:
    case P_TYPE::GNU_EH_FRAME:
    case P_TYPE::DYNAMIC:
    case P_TYPE::TLS:
    case P_TYPE::NOTE:
    case P_TYPE::INTERP:

      return true;
    default:
      return false;
  }
}

// ===========================================================
// Section
// ===========================================================

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Section<elfsize_t>& s) {
  char buf[64];
  os << std::setw(20) << std::left << s.name << " " << std::setw(12)
     << EnumToString(s.shdr.sh_type) << " "  //
     << std::setw(5) << FirstCharFlagString<SH_FLAGS>(s.shdr.sh_flags, buf)
     << " "         //
     << std::right  //
     // flags << std::setw(7) << std::hex << s.phdr.p_offset << " "      //
     << std::setw(7) << std::hex << s.shdr.sh_addr << " "       //
     << std::setw(7) << std::hex << s.shdr.sh_offset << " "     //
     << std::setw(7) << std::hex << s.shdr.sh_size << " "       //
     << std::setw(2) << std::hex << s.shdr.sh_link << " "       //
     << std::setw(4) << std::hex << s.shdr.sh_info << " "       //
     << std::setw(3) << std::hex << s.shdr.sh_addralign << " "  //
     << std::setw(2) << std::hex << s.shdr.sh_entsize;

  return os;
}

// force instantiation of operator<<
template std::ostream& operator<<(std::ostream& os, const Section<uint32_t>& s);
template std::ostream& operator<<(std::ostream& os, const Section<uint64_t>& s);

// ===========================================================
// Symbol
// ===========================================================

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Symbol<elfsize_t>& s) {
  os << std::setw(12) << std::hex << s.sym.st_value << " "         //
     << std::dec << std::setw(2) << s.sym.st_shndx << " "          //
     << std::setw(30) << std::left << s.name << std::right << " "  //
     << EnumToString(ST_INFO_BIND(s.sym.st_bind)) << " "           //
     << EnumToString(ST_INFO_TYPE(s.sym.st_type));
  return os;
}

// force instantiation of operator<<
template std::ostream& operator<<(std::ostream& os, const Symbol<uint32_t>& s);
template std::ostream& operator<<(std::ostream& os, const Symbol<uint64_t>& s);

// ===========================================================
// Reloc
// ===========================================================

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Reloc<elfsize_t>& r) {
  os << std::setw(8) << r.section->name << " " << r.rel.r_offset << " "
     << EnumToString(RELOC_TYPE_ARM(r.rel.r_type)) << " " << r.symbol->name;
  return os;
}

// force instantiation of operator<<
template std::ostream& operator<<(std::ostream& os, const Reloc<uint32_t>& s);
template std::ostream& operator<<(std::ostream& os, const Reloc<uint64_t>& s);
// ===========================================================
// Segment
// ===========================================================

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Segment<elfsize_t>& s) {
  char buf[64];
  os << std::setw(12) << std::left << EnumToString(s.phdr.p_type) << " "  //
     << std::setw(3) << FirstCharFlagString<P_FLAGS>(s.phdr.p_flags, buf)
     << " "                                                 //
     << std::right                                          //
     << std::setw(7) << std::hex << s.phdr.p_offset << " "  //
     << std::setw(7) << std::hex << s.phdr.p_vaddr << " "   //
     << std::setw(7) << std::hex << s.phdr.p_paddr << " "   //
     << std::setw(7) << std::hex << s.phdr.p_filesz << " "  //
     << std::setw(7) << std::hex << s.phdr.p_memsz << " "   //
     << std::setw(4) << std::hex << s.phdr.p_align;

  return os;
}

// force instantiation of operator<<
template std::ostream& operator<<(std::ostream& os, const Segment<uint32_t>& s);
template std::ostream& operator<<(std::ostream& os, const Segment<uint64_t>& s);

// ===========================================================
// Executable
// ===========================================================

template <typename elfsize_t>
std::vector<Segment<elfsize_t>*> Executable<elfsize_t>::FindContainingSegs(
    const Section<elfsize_t>* s) {
  const elfsize_t filesz =
      s->shdr.sh_type == SH_TYPE::NOBITS ? 0 : s->shdr.sh_size;
  std::vector<Segment<elfsize_t>*> out;
  for (const auto& seg : segments) {
    if (!is_inside(s->shdr.sh_offset, filesz, seg->phdr.p_offset,
                   seg->phdr.p_filesz))
      continue;
    if (s->shdr.sh_addr != 0 and
        !is_inside(s->shdr.sh_addr, s->shdr.sh_size, seg->phdr.p_vaddr,
                   seg->phdr.p_memsz))
      continue;
    out.push_back(seg.get());
  }
  return out;
}

template <typename elfsize_t>
bool Executable<elfsize_t>::Load(std::string_view data) {
  ASSERT(segments.empty() && sections.empty(), "Load must be called only once");
  elfsize_t offset = 0;
  data.copy((char*)&ident, sizeof(ident), offset);
  ASSERT(ident.IsValid(), "");

  offset += sizeof((ident));
  data.copy((char*)&ehdr, sizeof(ehdr), offset);

  // std::cout << "Processing " << ehdr.e_phnum << " Segments\n";
  ASSERT(sizeof(Elf_Phdr<elfsize_t>) == ehdr.e_phentsize, "");
  offset = ehdr.e_phoff;
  segments.reserve(ehdr.e_phnum);
  start_vaddr = 0;

  for (unsigned i = 0; i < ehdr.e_phnum; ++i, offset += ehdr.e_phentsize) {
    segments.push_back(std::make_unique<Segment<elfsize_t>>());
    Segment<elfsize_t>* seg = segments.back().get();
    data.copy((char*)&seg->phdr, ehdr.e_phentsize, offset);
    seg->hard_align = seg->phdr.p_vaddr % seg->phdr.p_align == 0;
    seg->is_auxiliary = IsAuxiliaryPhdr(seg->phdr.p_type);
    if (start_vaddr == 0 && seg->phdr.p_type == P_TYPE::LOAD) {
      start_vaddr = seg->phdr.p_vaddr;
    }
  }

  // for (auto& s : segments) std::cout << s << "\n";

  // std::cout << "processing " << ehdr.e_shnum << " shdrs\n";
  ASSERT(sizeof(Elf_Shdr<elfsize_t>) == ehdr.e_shentsize, "");
  offset = ehdr.e_shoff;
  for (unsigned i = 0; i < ehdr.e_shnum; ++i, offset += ehdr.e_shentsize) {
    sections.emplace_back(std::make_unique<Section<elfsize_t>>());
    Section<elfsize_t>* s = sections.back().get();
    data.copy((char*)&s->shdr, ehdr.e_shentsize, offset);
  }
  // set section data
  for (const auto& s : sections) {
    if (s->shdr.sh_type != SH_TYPE::NOBITS) {
      s->SetData(
          new Chunk(data.substr(s->shdr.sh_offset, s->shdr.sh_size), true));
    }
  }
  // set section name
  const Chunk* names = sections[ehdr.e_shstrndx]->data.get();
  for (auto& sec : sections) {
    sec->name = {(const char*)names->data() + sec->shdr.sh_name};
  }

  // symbols
  const Section<elfsize_t>* symtab = nullptr;
  for (const auto& sec : sections) {
    if (sec->shdr.sh_type == SH_TYPE::SYMTAB && sec->name == ".symtab") {
      ASSERT(symtab == nullptr, "");
      symtab = sec.get();
    }
  }

  if (symtab != nullptr) {
    const char* names_str =
        (const char*)sections[symtab->shdr.sh_link]->data->data();
    const unsigned sym_size = sizeof(Elf_Sym<elfsize_t>);
    const unsigned num_syms = symtab->shdr.sh_size / sym_size;
    ASSERT(num_syms * sym_size == symtab->shdr.sh_size, "");
    offset = symtab->shdr.sh_offset;
    for (unsigned i = 0; i < num_syms; ++i, offset += sym_size) {
      symbols.emplace_back(Symbol<elfsize_t>());
      Symbol<elfsize_t>& s = symbols.back();
      data.copy((char*)&s.sym, sym_size, offset);
      if (s.sym.st_shndx < sections.size()) {
        s.section = sections[s.sym.st_shndx].get();
      }
      s.name = {names_str + s.sym.st_name};
    }
  }
  // for (auto& sec : sections) std::cout << sec << "\n";

  // assign sections to segments
  Segment<elfsize_t>* pseudo_seg = nullptr;
  for (const auto& sec : sections) {
    std::vector<Segment<elfsize_t>*> seg_containers =
        FindContainingSegs(sec.get());
    if (!seg_containers.empty()) {
      ASSERT(pseudo_seg == nullptr, "");
      if (seg_containers.size() > 1) {
        for (auto* seg : seg_containers) {
          ASSERT(seg->phdr.p_type == P_TYPE::LOAD || seg->is_auxiliary,
                 "bad seg " << EnumToString(seg->phdr.p_type) << " "
                            << seg_containers.size() << " " << sec->name);
        }
      }
      for (auto* seg : seg_containers) seg->sections.push_back(sec.get());
    } else {
      ASSERT(sec->shdr.sh_type != SH_TYPE::X_NULL, "");
      if (pseudo_seg == nullptr) {
        segments.push_back(std::make_unique<Segment<elfsize_t>>());
        pseudo_seg = segments.back().get();
        pseudo_seg->InitPseudo();
      }
      pseudo_seg->sections.push_back(sec.get());
    }
  }
  return true;
}

// force instantiation of Load()
template bool Executable<uint32_t>::Load(std::string_view data);

template bool Executable<uint64_t>::Load(std::string_view data);

template <typename elfsize_t>
std::vector<std::string_view> Executable<elfsize_t>::Save() const {
  std::vector<std::string_view> out;
  auto add_string_view = [&out](const void* data, size_t size) {
    out.emplace_back(std::string_view((const char*)data, size));
  };
  size_t offset = 0;
  add_string_view(&ident, sizeof(ident));
  offset += out.back().size();
  add_string_view(&ehdr, sizeof(ehdr));
  offset += out.back().size();
  // Write Segment headers
  ASSERT(offset == ehdr.e_phoff, "");
  for (const auto& seg : segments) {
    if (seg->is_pseudo) continue;
    add_string_view(&seg->phdr, sizeof(seg->phdr));
    offset += out.back().size();
  }
  // Write section content
  for (const auto& seg : segments) {
    if (seg->is_auxiliary) continue;
    for (const auto& sec : seg->sections) {
      if (sec->shdr.sh_size == 0 || sec->shdr.sh_type == SH_TYPE::NOBITS)
        continue;
      const size_t new_offset = sec->shdr.sh_offset;
      ASSERT(offset <= new_offset, "");
      if (new_offset != offset) {
        const size_t padding_size = new_offset - offset;
        ASSERT(padding_size < sizeof(zero_padding), "");
        add_string_view(zero_padding, padding_size);
        offset += padding_size;
      }
      ASSERT(sec->shdr.sh_size == sec->data->size(), "");
      add_string_view(sec->data->data(), sec->data->size());
      offset += out.back().size();
    }
  } /**/

  // Write Section headers
  const size_t new_offset = Align(offset, sizeof(elfsize_t) == 8 ? 16 : 4);

  if (new_offset != offset) {
    const size_t padding_size = new_offset - offset;
    ASSERT(padding_size < sizeof(zero_padding), "");
    add_string_view(zero_padding, padding_size);
    offset += padding_size;
  }
  ASSERT(offset == ehdr.e_shoff, offset << " vs " << ehdr.e_shoff);
  for (const auto& seg : segments) {
    if (seg->is_auxiliary) continue;
    for (const auto& sec : seg->sections) {
      add_string_view(&sec->shdr, sizeof(sec->shdr));
      offset += out.back().size();
    }
  }

  return out;
}

// force instantiation of Save()
template std::vector<std::string_view> Executable<uint32_t>::Save() const;

template std::vector<std::string_view> Executable<uint64_t>::Save() const;

template <typename elfsize_t>
void SectionVerifVaddrAndOffset(const Section<elfsize_t>* sec,
                                elfsize_t* vaddr,
                                size_t* offset) {
  if (sec->shdr.sh_type == SH_TYPE::X_NULL) {
    ASSERT(sec->shdr.sh_addr == 0, "");
    ASSERT(sec->shdr.sh_offset == 0, "");
  } else if (sec->shdr.sh_type == SH_TYPE::NOBITS) {
    if (sec->name != ".tbss") {
      *vaddr = Align(*vaddr, sec->shdr.sh_addralign);
      ASSERT(sec->shdr.sh_addr == *vaddr, "");
      ASSERT(sec->shdr.sh_offset == *offset, "");
      *vaddr += sec->shdr.sh_size;
    }
  } else {
    *vaddr = Align(*vaddr, sec->shdr.sh_addralign);
    *offset = Align(*offset, sec->shdr.sh_addralign);
    ASSERT(sec->shdr.sh_offset == *offset,
           std::hex << sec->shdr.sh_offset << " vs " << *offset);
    if ((uint32_t(sec->shdr.sh_flags) & uint32_t(SH_FLAGS::ALLOC)) != 0) {
      ASSERT(sec->shdr.sh_addr == *vaddr,
             std::hex << sec->shdr.sh_addr << " vs " << *vaddr);
    } else {
      ASSERT(sec->shdr.sh_addr == 0, "");
    }
    *vaddr += sec->shdr.sh_size;
    *offset += sec->shdr.sh_size;
  }
}

template <typename elfsize_t>
void Executable<elfsize_t>::VerifyVaddrsAndOffsets(
    elfsize_t header_size,
    elfsize_t start_vaddr) const {
  size_t offset = 0;
  elfsize_t vaddr = 0;
  for (const auto& seg : segments) {
    if (seg->is_auxiliary) continue;
    if (offset == 0) {
      offset += header_size;
      vaddr += header_size + start_vaddr;
    } else if (seg->hard_align) {
      vaddr = Align(vaddr + 1, seg->phdr.p_align);
      offset = Align(offset + 1, seg->phdr.p_align);
    } else {
      vaddr += seg->phdr.p_align;
    }
    for (const auto& sec : seg->sections) {
      SectionVerifVaddrAndOffset<elfsize_t>(sec, &vaddr, &offset);
    }
  }
  offset = Align(offset, sizeof(elfsize_t) == 8 ? 16 : 4);
  ASSERT(ehdr.e_shoff == offset, "");
  ASSERT(ehdr.e_phoff == sizeof(ident) + sizeof(ehdr), "");

  bool is_first_load = true;
  for (const auto& seg : segments) {
    if (seg->is_pseudo) continue;
    const auto& first_shdr = seg->sections[0]->shdr;
    if (seg->phdr.p_type == P_TYPE::LOAD and is_first_load) {
      ASSERT(seg->phdr.p_offset == 0, "");
      ASSERT(seg->phdr.p_vaddr == start_vaddr, "");
      is_first_load = false;
    } else {
      ASSERT(seg->phdr.p_offset == first_shdr.sh_offset, "");
      ASSERT(seg->phdr.p_vaddr == first_shdr.sh_addr, "");
    }
    const auto& last_shdr = seg->sections.back()->shdr;
    const elfsize_t filesz =
        last_shdr.sh_type == SH_TYPE::NOBITS ? 0 : last_shdr.sh_size;
    ASSERT(
        seg->phdr.p_filesz == last_shdr.sh_offset + filesz - seg->phdr.p_offset,
        "");
    ASSERT(seg->phdr.p_memsz ==
               last_shdr.sh_addr + last_shdr.sh_size - seg->phdr.p_vaddr,
           "");
  }
}

// force instantiation of VerifyVaddrsAndOffsets()
template void Executable<uint32_t>::VerifyVaddrsAndOffsets(
    uint32_t header_size,
    uint32_t start_vaddr) const;

template void Executable<uint64_t>::VerifyVaddrsAndOffsets(
    uint64_t header_size,
    uint64_t start_vaddr) const;

template <typename elfsize_t>
void SectionUpdateVaddrAndOffset(Section<elfsize_t>* sec,
                                 elfsize_t* vaddr,
                                 size_t* offset) {
  if (sec->shdr.sh_type == SH_TYPE::X_NULL) {
    sec->shdr.sh_addr = 0;
    sec->shdr.sh_offset = 0;
  } else if (sec->shdr.sh_type == SH_TYPE::NOBITS) {
    if (sec->name != ".tbss") {
      *vaddr = Align(*vaddr, sec->shdr.sh_addralign);
      sec->shdr.sh_addr = *vaddr;
      sec->shdr.sh_offset = *offset;
      *vaddr += sec->shdr.sh_size;
    }
  } else {
    ASSERT(sec->shdr.sh_size == sec->data->size(),
           "bad sec size " << *sec << " " << sec->data->size());
    ASSERT(sec->shdr.sh_addralign != 0, *sec);
    *vaddr = Align(*vaddr, sec->shdr.sh_addralign);
    *offset = Align(*offset, sec->shdr.sh_addralign);
    sec->shdr.sh_offset = *offset;
    if ((uint32_t(sec->shdr.sh_flags) & uint32_t(SH_FLAGS::ALLOC)) != 0) {
      sec->shdr.sh_addr = *vaddr;
    } else {
      sec->shdr.sh_addr = 0;
    }
    *vaddr += sec->shdr.sh_size;
    *offset += sec->shdr.sh_size;
  }
}

template <typename elfsize_t>
void Executable<elfsize_t>::UpdateVaddrsAndOffsets(elfsize_t header_size,
                                                   elfsize_t start_vaddr) {
  size_t offset = 0;
  elfsize_t vaddr = 0;
  for (auto& seg : segments) {
    if (seg->is_auxiliary) continue;
    if (offset == 0) {
      offset = header_size;
      vaddr = header_size + start_vaddr;
    } else if (seg->hard_align) {
      vaddr = Align(vaddr + 1, seg->phdr.p_align);
      offset = Align(offset + 1, seg->phdr.p_align);
    } else {
      vaddr += seg->phdr.p_align;
    }
    for (auto* sec : seg->sections) {
      SectionUpdateVaddrAndOffset<elfsize_t>(sec, &vaddr, &offset);
    }
  }

  offset = Align(offset, sizeof(elfsize_t) == 8 ? 16 : 4);
  ehdr.e_shoff = offset;
  ehdr.e_phoff = sizeof(ident) + sizeof(ehdr);

  bool is_first_load = true;
  for (auto& seg : segments) {
    if (seg->is_pseudo) continue;
    const auto& first_shdr = seg->sections[0]->shdr;
    if (seg->phdr.p_type == P_TYPE::LOAD and is_first_load) {
      seg->phdr.p_offset = 0;
      seg->phdr.p_vaddr = start_vaddr;
      is_first_load = false;
    } else {
      seg->phdr.p_offset = first_shdr.sh_offset;
      seg->phdr.p_vaddr = first_shdr.sh_addr;
    }
    seg->phdr.p_paddr = seg->phdr.p_vaddr;
    const auto& last_shdr = seg->sections.back()->shdr;
    const elfsize_t filesz =
        last_shdr.sh_type == SH_TYPE::NOBITS ? 0 : last_shdr.sh_size;

    seg->phdr.p_filesz = last_shdr.sh_offset + filesz - seg->phdr.p_offset;
    seg->phdr.p_memsz =
        last_shdr.sh_addr + last_shdr.sh_size - seg->phdr.p_vaddr;
  }
}

// force instantiation of UpdateVaddrsAndOffsets()
template void Executable<uint32_t>::UpdateVaddrsAndOffsets(
    uint32_t header_size,
    uint32_t start_vaddr);

template void Executable<uint64_t>::UpdateVaddrsAndOffsets(
    uint64_t header_size,
    uint64_t start_vaddr);

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Executable<elfsize_t>& e) {
  unsigned n = 0;
  for (const auto& seg : e.segments) {
    os << std::dec << "[" << std::setw(2) << n++ << "] " << *seg << "\n";
  }
  os << "\n";
  n = 0;
  for (const auto& seg : e.segments) {
    for (const auto* sec : seg->sections) {
      os << std::dec << "[" << std::setw(2) << n++ << "] " << *sec << "\n";
    }
  }
  os << "\n";

  n = 0;
  for (const auto& sym : e.symbols) {
    os << std::dec << "[" << std::setw(3) << n++ << "] " << sym << "\n";
  }
  return os;
}
// force instantiation of operator<<
template std::ostream& operator<<(std::ostream& os,
                                  const Executable<uint32_t>& e);
template std::ostream& operator<<(std::ostream& os,
                                  const Executable<uint64_t>& e);

template <typename elfsize_t>
void Executable<elfsize_t>::InitWithSectionsAndSegments(
    elfsize_t start_address,
    std::vector<Section<elfsize_t>*>& all_sections,
    std::vector<Segment<elfsize_t>*>& all_segments) {
  ASSERT(sections.empty() && !all_sections.empty(), "");
  ASSERT(segments.empty() && !all_segments.empty(), "");
  // TODO: check that sections referenced by segments are in all_sections
  ASSERT(all_sections.back()->shdr.sh_type == SH_TYPE::STRTAB,
         "bad sec: " << *all_sections.back());
  ASSERT(all_sections.back()->name == ".shstrtab", *all_sections.back());
  start_vaddr = start_address;
  unsigned n = 0;
  for (auto* sec : all_sections) {
    sec->index = n++;
    sections.push_back(std::unique_ptr<Section<elfsize_t>>(sec));
  }
  bool seen_pseudo = false;
  for (auto* seg : all_segments) {
    ASSERT(!seen_pseudo, "pseudo segment must be last");
    segments.push_back(std::unique_ptr<Segment<elfsize_t>>(seg));
    seen_pseudo = seg->is_pseudo;
  }
}

Executable<uint64_t> MakeExecutableX64(
    uint64_t start_vaddr,
    std::vector<Section<uint64_t>*>& all_sections,
    std::vector<Segment<uint64_t>*>& all_segments) {
  Executable<uint64_t> exe;
  exe.InitWithSectionsAndSegments(start_vaddr, all_sections, all_segments);
  exe.ident.InitX64();
  exe.ehdr.InitX64Exec(all_sections.size(),
                       all_segments.size() - (all_segments.back()->is_pseudo),
                       all_sections.size() - 1);
  return exe;
}

// takes ownership of Sections and Segments
Executable<uint32_t> MakeExecutableA32(
    uint32_t start_vaddr,
    std::vector<Section<uint32_t>*>& all_sections,
    std::vector<Segment<uint32_t>*>& all_segments) {
  Executable<uint32_t> exe;
  exe.InitWithSectionsAndSegments(start_vaddr, all_sections, all_segments);
  exe.ident.InitA32();
  exe.ehdr.InitA32Exec(all_sections.size(),
                       all_segments.size() - (all_segments.back()->is_pseudo),
                       all_sections.size() - 1);
  return exe;
}

// takes ownership of Sections and Segments
Executable<uint64_t> MakeExecutableA64(
    uint64_t start_vaddr,
    std::vector<Section<uint64_t>*>& all_sections,
    std::vector<Segment<uint64_t>*>& all_segments) {
  Executable<uint64_t> exe;
  exe.InitWithSectionsAndSegments(start_vaddr, all_sections, all_segments);
  exe.ident.InitA64();
  exe.ehdr.InitA64Exec(all_sections.size(),
                       all_segments.size() - (all_segments.back()->is_pseudo),
                       all_sections.size() - 1);
  return exe;
}

std::string_view null_byte = std::string_view("\0", 1);

template <typename elfsize_t>
Chunk* MakeShStrTabContents(const std::vector<Section<elfsize_t>*>& sections) {
  // strtab starts and endsw with null byte
  auto out = new Chunk(null_byte, false);
  for (auto* sec : sections) {
    if (sec->name.empty()) {
      sec->shdr.sh_name = 0;
    } else {
      sec->shdr.sh_name = out->size();
      out->AddData(sec->name);
      out->AddData(null_byte);
    }
  }
  return out;
}

// force instantiation of operator<<
template Chunk* MakeShStrTabContents(
    const std::vector<Section<uint32_t>*>& sections);
template Chunk* MakeShStrTabContents(
    const std::vector<Section<uint64_t>*>& sections);

}  // namespace cwerg::elf
