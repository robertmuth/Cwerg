#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Elf/enum_gen.h"
#include "Util/assert.h"

#include <cstdint>
#include <cstdlib>

#include <memory>
#include <string_view>
#include <vector>

#include <iostream>

namespace cwerg::elf {

extern size_t Align(size_t x, size_t align);

const constexpr char EHDR_MAGIC[4] = {'\x7f', 'E', 'L', 'F'};

// ===========================================================
// Chunk (fraction of an Elf file, e.g. content of a Sections)
// ===========================================================

struct Chunk {
 public:
  Chunk(std::string_view bytes, bool is_read_only)
      : is_read_only_(is_read_only) {
    if (is_read_only_) {
      storage_ro_ = bytes;
    } else {
      storage_rw_ = std::string(bytes);
    }
  }

  const void* data() const {
    return is_read_only_ ? storage_ro_.data() : storage_rw_.data();
  }

  void* rwdata() {
    ASSERT(!is_read_only_, "");
    return storage_rw_.data();
  }

  size_t size() const {
    return is_read_only_ ? storage_ro_.size() : storage_rw_.size();
  }

  void AddData(std::string_view bytes) {
    ASSERT(!is_read_only_, "");
    storage_rw_.append(bytes);
  }

  void PadData(size_t alignment, std::string_view padding) {
    ASSERT(!is_read_only_, "");
    if (alignment <= 1) return;
    ASSERT(alignment % padding.size() == 0, "");
    ASSERT(storage_rw_.size() % padding.size() == 0, "");
    const size_t new_size = Align(storage_rw_.size(), alignment);
    while (storage_rw_.size() < new_size) {
      storage_rw_.append(padding);
    }
    ASSERT(storage_rw_.size() == new_size, "");
  }

 private:
  const bool is_read_only_;
  std::string_view storage_ro_;
  std::string storage_rw_;
};

struct Elf_EhdrIdent {
  char ei_magic[4] = {'\x7f', 'E', 'L', 'F'};
  EI_CLASS ei_class;
  EI_DATA ei_data;
  EI_VERSION ei_version;
  EI_OSABI ei_osabi;
  uint8_t ei_abiversion;
  uint8_t reserved[7] = {0};  // This will be all zeros

  bool IsValid() const;

  void InitX64() {
    ei_class = EI_CLASS::X_64;
    ei_data = EI_DATA::LSB2;
    ei_version = EI_VERSION::CURRENT;
    ei_osabi = EI_OSABI::SYSV;
    ei_abiversion = 0;
  }

  void InitA32() {
    ei_class = EI_CLASS::X_32;
    ei_data = EI_DATA::LSB2;
    ei_version = EI_VERSION::CURRENT;
    ei_osabi = EI_OSABI::SYSV;
    ei_abiversion = 0;
  }

  void InitA64() {
    ei_class = EI_CLASS::X_64;
    ei_data = EI_DATA::LSB2;
    ei_version = EI_VERSION::CURRENT;
    ei_osabi = EI_OSABI::SYSV;
    ei_abiversion = 0;
  }
};

// ===========================================================
// Section (explicit specializations for uint32_t and uint64_t)
// ===========================================================

template <typename elfsize_t>
struct Elf_Shdr {
  uint32_t sh_name = ~0;
  SH_TYPE sh_type;
  elfsize_t sh_flags = 0;
  elfsize_t sh_addr = ~elfsize_t(0);
  elfsize_t sh_offset = ~elfsize_t(0);
  elfsize_t sh_size = 0;
  uint32_t sh_link = 0;
  uint32_t sh_info = 0;
  elfsize_t sh_addralign = 0;
  elfsize_t sh_entsize = 0;
};

template <typename elfsize_t>
struct Section {
  Elf_Shdr<elfsize_t> shdr;
  std::unique_ptr<Chunk> data;
  std::string_view name;
  uint16_t index = ~0;

  void InitProg(std::string_view sec_name,
                elfsize_t alignment,
                elfsize_t flags) {
    name = sec_name;
    shdr.sh_flags = flags;
    shdr.sh_type = SH_TYPE::PROGBITS;
    ASSERT(alignment > 0, "");
    shdr.sh_addralign = alignment;
    data = std::make_unique<Chunk>(std::string_view("", 0), false);
  }

  void InitText(elfsize_t alignment) {
    InitProg(".text", alignment,
             uint32_t(SH_FLAGS::ALLOC) | uint32_t(SH_FLAGS::EXECINSTR));
  }

  void InitData(elfsize_t alignment) {
    InitProg(".data", alignment,
             uint32_t(SH_FLAGS::ALLOC) | uint32_t(SH_FLAGS::WRITE));
  }

  void InitRodata(elfsize_t alignment) {
    InitProg(".rodata", alignment, uint32_t(SH_FLAGS::ALLOC));
  }

  void InitBss(elfsize_t alignment) {
    name = ".bss";
    shdr.sh_flags = uint32_t(SH_FLAGS::ALLOC) | uint32_t(SH_FLAGS::WRITE);
    shdr.sh_type = SH_TYPE::NOBITS;
    ASSERT(alignment > 0, "");
    shdr.sh_addralign = alignment;
    data = std::make_unique<Chunk>(std::string_view("", 0), false);
  }

  void InitStrTab(std::string_view sec_name) {
    name = sec_name;
    shdr.sh_type = SH_TYPE::STRTAB;
    shdr.sh_addralign = 1;
  }

  void InitSymTab(std::string_view sec_name, size_t entsize, unsigned strtab_ndx) {
    name = sec_name;
    shdr.sh_type = SH_TYPE::SYMTAB;
    shdr.sh_addralign = 4;
    shdr.sh_link = strtab_ndx;
    shdr.sh_entsize = entsize;  // circular dep, ow: sizeof(Elf_Sym<elfsize_t>)
  }

  void InitNull() {
    name = "";
    shdr.sh_type = SH_TYPE::X_NULL;
    shdr.sh_addralign = 0;
  }

  void InitArmAttributes() {
    name = ".ARM.attributes";
    shdr.sh_type = SH_TYPE::ARM_ATTRIBUTES;
    shdr.sh_addralign = 1;
  }

  void PadData(size_t alignment, std::string_view padding) {
    data->PadData(alignment, padding);
    if (alignment > shdr.sh_addralign) shdr.sh_addralign = alignment;
    shdr.sh_size = data->size();
  }

  void AddData(std::string_view bytes) {
    ASSERT(bytes.size() > 0, "");
    data->AddData(bytes);
    shdr.sh_size = data->size();
  }

  void SetData(Chunk* chunk) {
    data.reset(chunk);
    shdr.sh_size = data->size();
  }
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Section<elfsize_t>& s);

// ===========================================================
// Symbol (explicit specializations for uint32_t and uint64_t)
// ===========================================================

template <typename elfsize_t>
struct Elf_Sym {};

template <>
struct Elf_Sym<uint32_t> {
  uint32_t st_name;
  uint32_t st_value = uint32_t(~0);
  uint32_t st_size;
  uint8_t st_type : 4;
  uint8_t st_bind : 4;
  uint8_t st_other;
  uint16_t st_shndx;
};

template <>
struct Elf_Sym<uint64_t> {
  uint32_t st_name;
  uint8_t st_type : 4;
  uint8_t st_bind : 4;
  uint8_t st_other;
  uint16_t st_shndx;
  uint64_t st_value = uint64_t(~0);
  uint64_t st_size;
};

template <typename elfsize_t>
struct Symbol {
  Elf_Sym<elfsize_t> sym;
  std::string_view name;
  const Section<elfsize_t>* section = nullptr;  // owned by enclosing executable

  void Init(std::string_view sym_name,
            bool is_local,
            Section<elfsize_t>* sec,
            elfsize_t val) {
    name = sym_name;
    sym.st_bind =
        uint32_t(is_local ? ST_INFO_BIND::LOCAL : ST_INFO_BIND::GLOBAL);
    sym.st_value = val;
    sym.st_type = uint32_t(ST_INFO_TYPE::NOTYPE);
    section = sec;
  }
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Symbol<elfsize_t>& s);

// ===========================================================
// Reloc (explicit specializations for uint32_t and uint64_t)
// ===========================================================
template <typename elfsize_t>
struct Elf_Rel {};

template <>
struct Elf_Rel<uint32_t> {
  uint32_t r_offset;
  uint32_t r_type : 8;
  uint32_t r_sym : 24;
  int32_t r_addend;
};

template <>
struct Elf_Rel<uint64_t> {
  uint64_t r_offset;
  uint32_t r_type;
  uint32_t r_sym;
  int64_t r_addend;
};

template <typename elfsize_t>
struct Reloc {
  Elf_Rel<elfsize_t> rel;
  elfsize_t addend = 0;
  const Section<elfsize_t>* section = nullptr;
  const Symbol<elfsize_t>* symbol = nullptr;

  void Init(RELOC_TYPE_ARM reloc_type,
            const Section<elfsize_t>* sec,
            elfsize_t offset,
            const Symbol<elfsize_t>* sym,
            typename std::make_signed<elfsize_t>::type addend) {
    rel.r_type = uint32_t(reloc_type);
    section = sec;
    rel.r_offset = offset;
    rel.r_addend = addend;
    symbol = sym;
  }
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Reloc<elfsize_t>& r);

// ===========================================================
// Segment (explicit specializations for uint32_t and uint64_t)
// ===========================================================
template <typename elfsize_t>
struct Elf_Phdr {};

template <>
struct Elf_Phdr<uint32_t> {
  P_TYPE p_type = P_TYPE::X_NULL;
  uint32_t p_offset = ~uint32_t(0);
  uint32_t p_vaddr = ~uint32_t(0);
  uint32_t p_paddr = ~~uint32_t(0);
  uint32_t p_filesz = ~uint32_t(0);
  uint32_t p_memsz = ~uint32_t(0);
  uint32_t p_flags = ~uint32_t(0);
  uint32_t p_align = UINT32_MAX;
};

template <>
struct Elf_Phdr<uint64_t> {
  P_TYPE p_type = P_TYPE::X_NULL;
  uint32_t p_flags = ~uint32_t(0);
  uint64_t p_offset = ~uint64_t(0);
  uint64_t p_vaddr = ~uint64_t(0);
  uint64_t p_paddr = ~uint64_t(0);
  uint64_t p_filesz = ~uint64_t(0);
  uint64_t p_memsz = ~uint64_t(0);
  uint64_t p_align = ~uint64_t(0);
};

template <typename elfsize_t>
struct Segment {
  Elf_Phdr<elfsize_t> phdr;
  std::vector<Section<elfsize_t>*> sections;  // owner is enclosing exe
  bool hard_align = false;
  bool is_pseudo = false;
  bool is_auxiliary = false;

  void InitPseudo() {
    is_pseudo = true;
    phdr.p_type = P_TYPE::X_NULL;
    phdr.p_flags = 0;
    phdr.p_align = 0;
    is_pseudo = true;
  }

  void InitExe(elfsize_t alignment) {
    phdr.p_type = P_TYPE::LOAD;
    phdr.p_flags = uint32_t(P_FLAGS::R) | uint32_t(P_FLAGS::X);
    phdr.p_align = alignment;
  }

  void InitRW(elfsize_t alignment) {
    phdr.p_type = P_TYPE::LOAD;
    phdr.p_flags = uint32_t(P_FLAGS::R) | uint32_t(P_FLAGS::W);
    phdr.p_align = alignment;
  }

  void InitRO(elfsize_t alignment) {
    phdr.p_type = P_TYPE::LOAD;
    phdr.p_flags = uint32_t(P_FLAGS::R);
    phdr.p_align = alignment;
  }
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Segment<elfsize_t>& s);

// ===========================================================
//
// ===========================================================

template <typename elfsize_t>
struct Elf_Ehdr {
  E_TYPE e_type;
  E_MACHINE e_machine;
  uint32_t e_version;
  elfsize_t e_entry = ~0;
  elfsize_t e_phoff = ~0;
  elfsize_t e_shoff = ~0;
  uint32_t e_flags = 0;
  uint16_t e_ehsize = sizeof(Elf_EhdrIdent) + sizeof(Elf_Ehdr<elfsize_t>);
  uint16_t e_phentsize = sizeof(Elf_Phdr<elfsize_t>);
  uint16_t e_phnum = ~0;
  uint16_t e_shentsize = sizeof(Elf_Shdr<elfsize_t>);
  uint16_t e_shnum = ~0;
  uint16_t e_shstrndx = ~0;

  void InitX64Exec(uint16_t shnum, uint16_t phnum, uint16_t shstrndx) {
    e_type = E_TYPE::EXEC;
    e_machine = E_MACHINE::X86_64;
    e_version = 1;
    e_shnum = shnum;
    e_phnum = phnum;
    e_shstrndx = shstrndx;
  }

  void InitA32Exec(uint16_t shnum, uint16_t phnum, uint16_t shstrndx) {
    e_type = E_TYPE::EXEC;
    e_machine = E_MACHINE::ARM;
    e_version = 1;
    e_flags =
        uint32_t(E_FLAGS_ARM::EABI_VER1) | uint32_t(E_FLAGS_ARM::EABI_VER4);
    e_shnum = shnum;
    e_phnum = phnum;
    e_shstrndx = shstrndx;
  }

  void InitA64Exec(uint16_t shnum, uint16_t phnum, uint16_t shstrndx) {
    e_type = E_TYPE::EXEC;
    e_machine = E_MACHINE::AARCH64;
    e_version = 1;
    e_shnum = shnum;
    e_phnum = phnum;
    e_shstrndx = shstrndx;
  }
};

// ===========================================================
// Executable
// ===========================================================

// Give the data of an Elf executable determine its class
extern EI_CLASS ElfDetermineClass(std::string_view data);

template <typename elfsize_t>
struct Executable {
  Elf_EhdrIdent ident;
  Elf_Ehdr<elfsize_t> ehdr;
  std::vector<std::unique_ptr<Section<elfsize_t>>> sections;
  std::vector<std::unique_ptr<Segment<elfsize_t>>>
      segments;                            // contains Section pointers
  std::vector<Symbol<elfsize_t>> symbols;  // contains Section pointers
  elfsize_t start_vaddr;

  std::vector<Segment<elfsize_t>*> FindContainingSegs(
      const Section<elfsize_t>* s);
  // Used for padding so we do not have to explicitly allocated memory
  // there is no partial initialization!
  const char zero_padding[4096] = {0};  // this will be all zeros

  // The memory referred to by `data` must outlive the Executable object.
  // This function can only be called once - it acts like a ctor (that can
  // fail).
  bool Load(std::string_view data);

  size_t CombinedHeaderSize() const {
    unsigned n = segments.size() - (segments.back()->is_pseudo);
    return sizeof(ident) + sizeof(ehdr) + n * sizeof(Elf_Phdr<elfsize_t>);
  }

  void InitWithSectionsAndSegments(elfsize_t start_address,
      std::vector<Section<elfsize_t>*>& all_sections,
      std::vector<Segment<elfsize_t>*>& all_segments);

  std::vector<std::string_view> Save() const;

  void VerifyVaddrsAndOffsets() const;

  void UpdateVaddrsAndOffsets();
};

template <typename elfsize_t>
std::ostream& operator<<(std::ostream& os, const Executable<elfsize_t>& e);

// takes ownership of Sections and Segments
extern Executable<uint64_t> MakeExecutableX64(
    uint64_t start_vaddr,
    std::vector<Section<uint64_t>*>& sections,
    std::vector<Segment<uint64_t>*>& segments);

// takes ownership of Sections and Segments
extern Executable<uint32_t> MakeExecutableA32(
    uint32_t start_vaddr,
    std::vector<Section<uint32_t>*>& all_sections,
    std::vector<Segment<uint32_t>*>& all_segments);

// takes ownership of Sections and Segments
extern Executable<uint64_t> MakeExecutableA64(
    uint64_t start_vaddr,
    std::vector<Section<uint64_t>*>& sections,
    std::vector<Segment<uint64_t>*>& segments);

template <typename elfsize_t>
Chunk* MakeShStrTabContents(const std::vector<Section<elfsize_t>*>& sections);

}  // namespace cwerg::elf
