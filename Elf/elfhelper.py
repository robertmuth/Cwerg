#!/usr/bin/python3

"""Simple ELF Helper for Little-Endian Architectures

basic parsing and assembling of ELF executable linked with:
`-static -Wl,-z,norelro`

More work is needed ro make this compatible with
 * shared/dynamic code
 * situations where  text and data segment live in different memory
   regions - currently only the (text) start address can chosen.

References:
https://linuxhint.com/understanding_elf_file_format/
https://github.com/torvalds/linux/blob/master/include/uapi/linux/elf.h

Type mappings
u32	Elf32_Addr
u16	Elf32_Half
u32	Elf32_Off
s32	Elf32_Sword
u32	Elf32_Word

u64	Elf64_Addr
u16	Elf64_Half
s16	Elf64_SHalf
u64	Elf64_Off
s32	Elf64_Sword
u32	Elf64_Word
u64	Elf64_Xword
s64	Elf64_Sxword

Python struct
u8  -> B
s8  -> b
u16 -> H  ("half word")
s16 -> h
u32 -> I
s32 -> i
u64 -> Q ("quad word")
s64 -> q

"""

import dataclasses
import io
import struct
from typing import List, Dict, Optional, Set, Tuple, Any

from Elf.enum_tab import E_MACHINE, EI_CLASS, EI_DATA, E_TYPE, E_FLAGS_ARM, ST_INFO_BIND, \
    ST_INFO_TYPE
from Elf.enum_tab import P_TYPE, P_FLAGS
from Elf.enum_tab import SH_TYPE, SH_FLAGS


def Align(x, align):
    if align <= 1:
        return x
    return (x + align - 1) // align * align


def Pad(data: bytearray, alignment: int, padding_or_padder: Any):
    if alignment <= 0:
        return
    old_len = len(data)
    new_len = Align(old_len, alignment)
    delta = new_len - old_len
    if isinstance(padding_or_padder, bytes):
        assert old_len % len(padding_or_padder) == 0
        assert alignment % len(padding_or_padder) == 0
        data += padding_or_padder * (delta // len(padding_or_padder))
    else:
        data += padding_or_padder(delta)
    assert len(data) == new_len


def _FirstCharFlags(x: int, flag_map: Dict[int, str]):
    out = []
    while x:
        y = x & (x - 1)
        bit = x - y
        x = y
        out.append(flag_map[bit][0])
    return "".join(out)


EHDR_MAGIC = b'\x7fELF'
TO_BE_FILLED_IN_LATER = -1


@dataclasses.dataclass
class EHdrIdent:
    ei_magic: bytes = EHDR_MAGIC
    ei_class: int = 0
    ei_data: int = 0
    ei_version: int = 0
    ei_osabi: int = 0
    ei_abiversion: int = 0

    # https://docs.python.org/2/library/struct.html
    FORMAT = "<4sbbbbb7s"
    SIZE = struct.calcsize(FORMAT)

    def InitX64(self):
        self.ei_class = EI_CLASS.X_64.value
        self.ei_data = EI_DATA.LSB2.value
        self.ei_version = 1
        self.ei_osabi = 0
        self.ei_abiversion = 0

    def InitA64(self):
        self.ei_class = EI_CLASS.X_64.value
        self.ei_data = EI_DATA.LSB2.value
        self.ei_version = 1
        self.ei_osabi = 0
        self.ei_abiversion = 0

    def InitA32(self):
        self.ei_class = EI_CLASS.X_32.value
        self.ei_data = EI_DATA.LSB2.value
        self.ei_version = 1
        self.ei_osabi = 0
        self.ei_abiversion = 0

    def unpack(self, data: bytes):
        assert EHdrIdent.SIZE == 16
        (self.ei_magic,
         self.ei_class,
         self.ei_data,
         self.ei_version,
         self.ei_osabi,
         self.ei_abiversion,
         _) = struct.unpack(EHdrIdent.FORMAT,
                            data)

    def pack(self):
        assert EHdrIdent.SIZE == 16
        return struct.pack(
            EHdrIdent.FORMAT,
            self.ei_magic,
            self.ei_class,
            self.ei_data,
            self.ei_version,
            self.ei_osabi,
            self.ei_abiversion,
            b"")

    def is_valid(self):
        return (self.ei_magic == EHDR_MAGIC and
                self.ei_class in {EI_CLASS.X_32, EI_CLASS.X_64} and
                self.ei_data in {EI_DATA.LSB2, EI_DATA.MSB2})


@dataclasses.dataclass
class EHdr:
    e_type: int = 0
    e_machine: int = 0
    e_version: int = 0
    e_entry: int = TO_BE_FILLED_IN_LATER
    e_phoff: int = TO_BE_FILLED_IN_LATER
    e_shoff: int = TO_BE_FILLED_IN_LATER
    e_flags: int = 0
    e_ehsize: int = 0
    e_phentsize: int = 0
    e_phnum: int = TO_BE_FILLED_IN_LATER
    e_shentsize: int = 0
    e_shnum: int = TO_BE_FILLED_IN_LATER
    e_shstrndx: int = TO_BE_FILLED_IN_LATER
    FORMAT = {EI_CLASS.X_32: "<2H5I6H", EI_CLASS.X_64: "<2HI3QI6H"}
    SIZE = {k: struct.calcsize(v) for k, v in FORMAT.items()}

    def InitX64Exec(self, shnum, phnum, shstrndx):
        self.e_type = E_TYPE.EXEC.value
        self.e_machine = E_MACHINE.X86_64.value
        self.e_version = 1
        self.e_ehsize = EHdrIdent.SIZE + EHdr.SIZE[EI_CLASS.X_64]
        self.e_phentsize = Segment.SIZE[EI_CLASS.X_64]
        self.e_shentsize = Section.SIZE[EI_CLASS.X_64]
        self.e_shnum = shnum
        self.e_phnum = phnum
        self.e_shstrndx = shstrndx

    def InitA64Exec(self, shnum, phnum, shstrndx):
        self.e_type = E_TYPE.EXEC.value
        self.e_machine = E_MACHINE.AARCH64.value
        self.e_version = 1
        # should we use HARD?
        self.e_flags = 0
        self.e_ehsize = EHdrIdent.SIZE + EHdr.SIZE[EI_CLASS.X_64]
        self.e_phentsize = Segment.SIZE[EI_CLASS.X_64]
        self.e_shentsize = Section.SIZE[EI_CLASS.X_64]
        self.e_shnum = shnum
        self.e_phnum = phnum
        self.e_shstrndx = shstrndx

    def InitA32Exec(self, shnum, phnum, shstrndx):
        self.e_type = E_TYPE.EXEC.value
        self.e_machine = E_MACHINE.ARM.value
        self.e_version = 1
        # should we use HARD?
        self.e_flags = (E_FLAGS_ARM.EABI_VER1 | E_FLAGS_ARM.EABI_VER4).value
        self.e_ehsize = EHdrIdent.SIZE + EHdr.SIZE[EI_CLASS.X_32]
        self.e_phentsize = Segment.SIZE[EI_CLASS.X_32]
        self.e_shentsize = Section.SIZE[EI_CLASS.X_32]
        self.e_shnum = shnum
        self.e_phnum = phnum
        self.e_shstrndx = shstrndx

    def unpack(self, which, data: bytes):
        fmt = EHdr.FORMAT[which]
        (self.e_type, self.e_machine, self.e_version, self.e_entry, self.e_phoff,
         self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, self.e_phnum,
         self.e_shentsize, self.e_shnum, self.e_shstrndx) = struct.unpack(fmt, data)

    def pack(self, which):
        fmt = EHdr.FORMAT[which]
        return struct.pack(
            fmt,
            self.e_type,
            self.e_machine,
            self.e_version,
            self.e_entry,
            self.e_phoff,
            self.e_shoff,
            self.e_flags,
            self.e_ehsize,
            self.e_phentsize,
            self.e_phnum,
            self.e_shentsize,
            self.e_shnum,
            self.e_shstrndx)


# More info in ELF for the ARM Architecture ABI r2.10
# https://developer.arm.com/documentation/ihi0044/f/
ARM_ATTRIBUTES = bytes([0x41, 0x11, 0, 0,
                        0, 0x61, 0x65, 0x61,
                        0x62, 0x69, 0, 1,
                        7, 0, 0, 0,
                        8, 1])


@dataclasses.dataclass
class Section:
    """An Elf Section (glorified Shdr)"""
    sh_name: int = TO_BE_FILLED_IN_LATER
    sh_type: int = 0
    sh_flags: int = 0
    sh_addr: int = TO_BE_FILLED_IN_LATER
    sh_offset: int = TO_BE_FILLED_IN_LATER
    sh_size: int = 0
    sh_link: int = 0
    sh_info: int = 0
    sh_addralign: int = 0
    sh_entsize: int = 0
    # non-elf extras
    name: str = ""  # maybe switch to bytes and propagate to Section in CodeGenXXX
    data: bytearray = dataclasses.field(default_factory=bytearray)
    index: int = TO_BE_FILLED_IN_LATER

    FORMAT = {EI_CLASS.X_32: "10I", EI_CLASS.X_64: "2I4Q2I2Q"}
    SIZE = {k: struct.calcsize(v) for k, v in FORMAT.items()}

    def PadData(self, n: int, padding_or_padder: Any):
        if self.sh_addralign < n:
            self.sh_addralign = n
        Pad(self.data, n, padding_or_padder)
        self.sh_size = len(self.data)

    def AddData(self, data: bytes):
        self.data += data
        self.sh_size = len(self.data)

    def SetData(self, data: bytes):
        self.data = data
        self.sh_size = len(self.data)

    @classmethod
    def MakeSection(cls, name: str, alignment: int, kind: SH_TYPE, flags: SH_FLAGS) -> "Section":
        self = Section()
        self.name = name
        self.sh_flags = flags.value
        self.sh_type = kind.value
        self.sh_addralign = alignment
        return self

    @classmethod
    def MakeSectionNull(cls) -> "Section":
        return Section.MakeSection("", 0, SH_TYPE.X_NULL, SH_FLAGS(0))

    @classmethod
    def MakeSectionText(cls, alignment: int) -> "Section":
        return Section.MakeSection(
            ".text", alignment, SH_TYPE.PROGBITS, SH_FLAGS.ALLOC | SH_FLAGS.EXECINSTR)

    @classmethod
    def MakeSectionRodata(cls, alignment: int) -> "Section":
        return Section.MakeSection(".rodata", alignment, SH_TYPE.PROGBITS, SH_FLAGS.ALLOC)

    @classmethod
    def MakeSectionData(cls, alignment: int) -> "Section":
        return Section.MakeSection(
            ".data", alignment, SH_TYPE.PROGBITS, SH_FLAGS.ALLOC | SH_FLAGS.WRITE)

    @classmethod
    def MakeSectionBss(cls, alignment: int) -> "Section":
        return Section.MakeSection(
            ".bss", alignment, SH_TYPE.NOBITS, SH_FLAGS.ALLOC | SH_FLAGS.WRITE)

    @classmethod
    def MakeSectionStrTab(cls, name: str) -> "Section":
        return Section.MakeSection(name, 1, SH_TYPE.STRTAB, SH_FLAGS(0))

    @classmethod
    def MakeSectionSymTab(cls, name: str, which, strtab_ndx: int) -> "Section":
        # TODO: is the alignment different for 64bit?
        sec = Section.MakeSection(name, 4, SH_TYPE.SYMTAB, SH_FLAGS(0))
        sec.sh_link = strtab_ndx
        sec.sh_info = TO_BE_FILLED_IN_LATER
        sec.sh_entsize = Symbol.SIZE[which]
        return sec

    @classmethod
    def MakeSectionArmAttributes(cls) -> "Section":
        return Section.MakeSection(".ARM.attributes", 1, SH_TYPE.ARM_ATTRIBUTES, SH_FLAGS(0))

    def unpack(self, which, data: bytes):
        fmt = Section.FORMAT[which]
        (self.sh_name,
         self.sh_type,
         self.sh_flags,
         self.sh_addr,
         self.sh_offset,
         self.sh_size,
         self.sh_link,
         self.sh_info,
         self.sh_addralign,
         self.sh_entsize) = struct.unpack(fmt,
                                          data)

    def pack(self, which):
        fmt = Section.FORMAT[which]
        return struct.pack(
            fmt,
            self.sh_name,
            self.sh_type,
            self.sh_flags,
            self.sh_addr,
            self.sh_offset,
            self.sh_size,
            self.sh_link,
            self.sh_info,
            self.sh_addralign,
            self.sh_entsize)

    def verify_vaddr_and_offset(self, vaddr, offset) -> Tuple[int, int]:
        """Checks sh_addr and sh_offset."""
        if self.sh_type == SH_TYPE.X_NULL:  # usually NULL
            assert self.sh_addr == 0
            assert self.sh_offset == 0
            return vaddr, offset
        if self.sh_type == SH_TYPE.NOBITS:
            if self.name != ".tbss":
                # we have other ways to get that space via the TLS segments
                vaddr = Align(vaddr, self.sh_addralign)
                assert self.sh_offset == offset
                assert self.sh_addr == vaddr
                vaddr += self.sh_size
            return vaddr, offset

        offset = Align(offset, self.sh_addralign)
        vaddr = Align(vaddr, self.sh_addralign)
        assert self.sh_offset == offset, f"bad offset {offset:x} vs {self.sh_offset:x}"
        if SH_FLAGS(self.sh_flags) & SH_FLAGS.ALLOC:
            assert self.sh_addr == vaddr, f"bad addr {vaddr:x} vs {self.sh_addr:x}"
        else:
            assert self.sh_addr == 0
        return vaddr + self.sh_size, offset + self.sh_size

    def update_vaddr_and_offset(self, vaddr, offset) -> Tuple[int, int]:
        """Fills in sh_addr and sh_offset."""
        if self.sh_type == SH_TYPE.X_NULL:  # usually NULL
            self.sh_addr = 0
            self.sh_offset = 0
            return vaddr, offset
        if self.sh_type == SH_TYPE.NOBITS:
            if self.name != ".tbss":
                # we have other ways to get that space via the TLS segments
                vaddr = Align(vaddr, self.sh_addralign)
                self.sh_offset = offset
                self.sh_addr = vaddr
                vaddr += self.sh_size
            return vaddr, offset

        assert self.sh_size == len(self.data), f"{self}"
        offset = Align(offset, self.sh_addralign)
        vaddr = Align(vaddr, self.sh_addralign)
        self.sh_offset = offset
        if SH_FLAGS(self.sh_flags) & SH_FLAGS.ALLOC:
            self.sh_addr = vaddr
        else:
            self.sh_addr = 0
        return vaddr + self.sh_size, offset + self.sh_size

    def type_str(self) -> str:
        return SH_TYPE(self.sh_type).name

    def flag_str(self):
        sh_flags = SH_FLAGS(self.sh_flags)
        flags = [f for f in SH_FLAGS if f & sh_flags]
        return "".join([f.name[0] for f in flags])

    def __str__(self):
        return (
            f"{self.name:20s} {self.type_str():12s} "
            f"{self.flag_str():5} {self.sh_addr:7x} "
            f"{self.sh_offset:7x} {self.sh_size:7x} {self.sh_link:2x} {self.sh_info:4x} "
            f"{self.sh_addralign:3x} {self.sh_entsize:2x}")


@dataclasses.dataclass
class Segment:
    """An Elf Segment (glorified phdr) - also includes Elf Sections"""
    p_type: int = TO_BE_FILLED_IN_LATER
    p_offset: int = TO_BE_FILLED_IN_LATER
    p_vaddr: int = TO_BE_FILLED_IN_LATER
    p_paddr: int = TO_BE_FILLED_IN_LATER
    p_filesz: int = TO_BE_FILLED_IN_LATER
    p_memsz: int = TO_BE_FILLED_IN_LATER
    p_flags: int = TO_BE_FILLED_IN_LATER
    p_align: int = TO_BE_FILLED_IN_LATER
    # non-elf extras
    is_pseudo: bool = False
    is_auxiliary: bool = False
    hard_align: bool = False
    sections: List[Section] = dataclasses.field(default_factory=list)

    FORMAT = {EI_CLASS.X_32: "<8I", EI_CLASS.X_64: "<2I6Q"}
    SIZE = {k: struct.calcsize(v) for k, v in FORMAT.items()}

    @classmethod
    def MakePseudoSegment(cls):
        self = Segment()
        self.is_pseudo = True
        self.p_type = P_TYPE.X_NULL.value
        self.p_align = 0
        self.p_flags = 0
        return self

    @classmethod
    def MakeExeSegment(cls, align: int):
        self = Segment()
        self.p_type = P_TYPE.LOAD
        self.p_flags = (P_FLAGS.R | P_FLAGS.X).value
        self.p_align = align
        return self

    @classmethod
    def MakeRWSegment(cls, align: int):
        self = Segment()
        self.p_type = P_TYPE.LOAD.value
        self.p_flags = (P_FLAGS.R | P_FLAGS.W).value
        self.p_align = align
        return self

    @classmethod
    def MakeROSegment(cls, align: int):
        self = Segment()
        self.p_type = P_TYPE.LOAD.value
        self.p_flags = P_FLAGS.R.value
        self.p_align = align
        return self

    def unpack(self, which, data: bytes):
        fmt = Segment.FORMAT[which]
        if which == EI_CLASS.X_32:
            (self.p_type,
             self.p_offset,
             self.p_vaddr,
             self.p_paddr,
             self.p_filesz,
             self.p_memsz,
             self.p_flags,
             self.p_align) = struct.unpack(fmt,
                                           data)
        else:
            assert which == EI_CLASS.X_64
            (self.p_type, self.p_flags, self.p_offset, self.p_vaddr, self.p_paddr,
             self.p_filesz, self.p_memsz, self.p_align) = struct.unpack(fmt, data)

    def pack(self, which):
        fmt = Segment.FORMAT[which]
        if which == EI_CLASS.X_32:
            return struct.pack(
                fmt,
                self.p_type,
                self.p_offset,
                self.p_vaddr,
                self.p_paddr,
                self.p_filesz,
                self.p_memsz,
                self.p_flags,
                self.p_align)
        else:
            assert which == EI_CLASS.X_64
            return struct.pack(
                fmt,
                self.p_type,
                self.p_flags,
                self.p_offset,
                self.p_vaddr,
                self.p_paddr,
                self.p_filesz,
                self.p_memsz,
                self.p_align)

    def flag_str(self):
        p_flags = P_FLAGS(self.p_flags)
        flags = [f for f in P_FLAGS if f & p_flags]
        return "".join([f.name[0] for f in flags])

    def type_str(self):
        return P_TYPE(self.p_type).name

    # sadly. this is NOT unique, e.g. there might be multiple (LOAD, "R") phdrs
    def flavor(self):
        return self.p_type, self.flag_str()

    def contains_vaddr(self, vaddr: int):
        assert self.p_type == P_TYPE.LOAD
        return self.p_vaddr <= vaddr < self.p_vaddr + self.p_memsz

    def __str__(self):
        return (
            f"{self.type_str():12} {self.flag_str():3} "
            f"{self.p_offset:7x} {self.p_vaddr:7x} {self.p_paddr:7x} {self.p_filesz:7x} "
            f"{self.p_memsz:7x} {self.p_align:4x}")

    def __repr__(self):
        return str(self)


@dataclasses.dataclass
class Symbol:
    """An Elf Symbol"""
    st_name: int = 0
    st_value: int = 0
    st_size: int = 0
    st_bind: int = 0
    st_type: int = 0
    st_other: int = 0
    st_shndx: int = 0
    # non-elf extras
    name: str = ""
    section: Optional[Section] = None

    FORMAT = {EI_CLASS.X_32: "3IBBH", EI_CLASS.X_64: "IBBHQQ"}
    SIZE = {k: struct.calcsize(v) for k, v in FORMAT.items()}

    @classmethod
    def Init(cls, name, is_local, sec=None, value=0) -> "Symbol":
        self = Symbol()
        self.name = name
        self.st_bind = ST_INFO_BIND.LOCAL if is_local else ST_INFO_BIND.GLOBAL
        self.st_value = value
        self.st_type = ST_INFO_TYPE.NOTYPE
        self.section = sec
        return self

    def is_undefined(self):
        return self.section is None

    def unpack(self, which, data: bytes):
        fmt = Symbol.FORMAT[which]
        if which == EI_CLASS.X_32:
            (self.st_name,
             self.st_value,
             self.st_size,
             st_info,
             self.st_other,
             self.st_shndx) = struct.unpack(fmt, data)
        else:
            assert which == EI_CLASS.X_64
            (self.st_name, st_info, self.st_other, self.st_shndx,
             self.st_value, self.st_size) = struct.unpack(fmt, data)
        self.st_bind = st_info >> 4
        self.st_type = st_info & 0xf

    def pack(self, which):
        st_info = (self.st_bind << 4) | self.st_type
        fmt = Symbol.FORMAT[which]
        assert self.st_value != -1, f"undefined sym {self.name}"
        if which == EI_CLASS.X_32:
            return struct.pack(
                fmt, self.st_name,
                self.st_value,
                self.st_size,
                st_info,
                self.st_other,
                self.st_shndx
            )
        else:
            assert which == EI_CLASS.X_64
            return struct.pack(
                fmt, self.st_name, st_info, self.st_other, self.st_shndx,
                self.st_value, self.st_size)

    def __str__(self):
        return (
            f"{self.name:20s} {self.st_value:7x} {self.st_shndx} "
            f"{ST_INFO_BIND(self.st_bind).name:10}"
            f"{ST_INFO_TYPE(self.st_type).name:10}")


@dataclasses.dataclass
class Reloc:
    """An Elf Relocation with addend"""
    r_offset: int = 0
    r_type: int = 0
    r_sym: int = 0
    r_addend: int = 0
    # non-elf extras
    symbol: Symbol = None
    section: Optional[Section] = None

    FORMAT = {EI_CLASS.X_32: "IIi", EI_CLASS.X_64: "QIIq"}
    SIZE = {k: struct.calcsize(v) for k, v in FORMAT.items()}

    @classmethod
    def Init(cls, kind: int, sec: Section, offset: int, sym: Symbol, addend: int) -> "Reloc":
        out = Reloc()
        out.r_offset = offset
        out.section = sec
        out.r_type = kind
        out.r_addend = addend
        out.symbol = sym
        return out

    def unpack(self, which, data: bytes):
        if which == EI_CLASS.X_64:
            self.r_offset, self.r_type, self.r_sym, self.r_addend = struct.unpack(
                Reloc.FORMAT[which], data)
        else:
            self.r_offset, r_info, self.r_addend = struct.unpack(Reloc.FORMAT[which], data)
            self.r_type = r_info & 0xff
            self.r_sym = r_info >> 8

    def pack(self, which):
        if which == EI_CLASS.X_64:
            return struct.pack(Reloc.FORMAT[which], self.r_offset, self.r_type, self.r_sym,
                               self.r_addend)
        else:
            return struct.pack(Reloc.FORMAT[which], self.r_offset,
                               self.r_type | (self.r_sym << 8, self.r_addend))


# These Segment types are overlapping with LOAD Segments and the Sections they
# contain a are duplicates of those in the LOAD Segment.
_AUXILIARY_PHDR_TYPE: Set[int] = {
    P_TYPE.GNU_STACK,
    P_TYPE.GNU_PROPERTY,
    P_TYPE.GNU_RELRO,
    P_TYPE.GNU_EH_FRAME,
    P_TYPE.DYNAMIC,
    P_TYPE.TLS,
    P_TYPE.NOTE,
    P_TYPE.INTERP,
}


def is_inside(src, dst):
    return (dst[0] <= src[0] <= dst[0] + dst[1] and
            dst[0] <= src[0] + src[1] <= dst[0] + dst[1])


def str_offset_to_name(offset, sec_symtab: Section):
    data = sec_symtab.data
    name = bytearray()
    while data[offset] != 0:
        name.append(data[offset])
        offset += 1
    return name.decode("utf-8")


def MakeSecStrTabContents(sections: List[Section]):
    out = bytearray()
    out += b"\0"
    for sec in sections:
        if sec.name:
            sec.sh_name = len(out)
            out += bytes(sec.name, "utf-8") + b"\0"
        else:
            sec.sh_name = 0
    return out


class Executable:
    """An ELF Executable"""

    def __init__(self):
        self.ehdr_ident = EHdrIdent()
        self.ehdr = EHdr()
        self.sections: List[Section] = []
        self.segments: List[Segment] = []
        self.start_vaddr = 0
        self.symbols: List[Symbol] = []

    def InitWithSectionsAndSegments(self, start_vaddr: int,
                                    sections: List[Section],
                                    segments: List[Segment]):
        assert not self.sections and not self.segments
        assert sections[-1].sh_type == SH_TYPE.STRTAB.value
        assert sections[-1].name == ".shstrtab"

        for n, sec in enumerate(sections):
            sec.index = n

        self.start_vaddr = start_vaddr
        self.sections = sections
        self.segments = segments

    @classmethod
    def MakeExecutableA32(cls, start_vaddr: int,
                          sections: List[Section],
                          segments: List[Segment]):
        exe = Executable()
        exe.ehdr_ident.InitA32()
        exe.ehdr.InitA32Exec(len(sections),
                             len([p for p in segments
                                  if not p.is_pseudo]),
                             len(sections) - 1)
        exe.InitWithSectionsAndSegments(start_vaddr, sections, segments)
        return exe

    @classmethod
    def MakeExecutableA64(cls, start_vaddr: int,
                          sections: List[Section],
                          segments: List[Segment]):
        exe = Executable()
        exe.ehdr_ident.InitA64()
        exe.ehdr.InitA64Exec(len(sections),
                             len([p for p in segments
                                  if not p.is_pseudo]),
                             len(sections) - 1)
        exe.InitWithSectionsAndSegments(start_vaddr, sections, segments)
        return exe

    @classmethod
    def MakeExecutableX64(cls, start_vaddr: int,
                          sections: List[Section],
                          segments: List[Segment]):
        exe = Executable()
        exe.ehdr_ident.InitX64()
        exe.ehdr.InitX64Exec(len(sections),
                             len([p for p in segments
                                  if not p.is_pseudo]),
                             len(sections) - 1)
        exe.InitWithSectionsAndSegments(start_vaddr, sections, segments)
        return exe

    def phdrs_containing_shdr(self, shdr: Section):
        filesz = 0 if shdr.sh_type == SH_TYPE.NOBITS else shdr.sh_size
        out = []
        for phdr in self.segments:
            # check containment in file
            if not is_inside((shdr.sh_offset, filesz),
                             (phdr.p_offset, phdr.p_filesz)):
                continue
            # check containment in address space
            if (shdr.sh_addr != 0 and
                    not is_inside((shdr.sh_addr, shdr.sh_size),
                                  (phdr.p_vaddr, phdr.p_memsz))):
                continue
            out.append(phdr)
        return out

    def save(self, stream: io.BytesIO):
        """ Save"""
        which = self.ehdr_ident.ei_class

        offset = 0
        data = self.ehdr_ident.pack()
        offset += len(data)
        stream.write(data)
        data = self.ehdr.pack(which)
        offset += len(data)
        stream.write(data)
        assert offset == self.ehdr.e_phoff
        for phdr in self.segments:
            if phdr.is_pseudo:
                continue
            data = phdr.pack(which)
            offset += len(data)
            stream.write(data)

        # Note pseudo segment will be last
        for phdr in self.segments:
            if phdr.is_auxiliary:
                continue
            for shdr in phdr.sections:
                print(
                    f"writing {shdr.name:20s} offset is {offset:5x} "
                    f"want{shdr.sh_offset:5x} "
                    f"align {shdr.sh_addralign:5x} "
                    f"size {shdr.sh_size:5x}")
                if shdr.sh_size == 0 or shdr.sh_type == SH_TYPE.NOBITS:
                    continue

                new_offset = shdr.sh_offset
                if new_offset != offset:
                    assert new_offset > offset, f"offset corruption"
                    padding = (new_offset - offset) * b"\0"
                    print(f"adding {len(padding)} byte padding")
                    offset += len(padding)
                    stream.write(padding)

                assert shdr.sh_size == len(
                    shdr.data), f"size mismatch {shdr.sh_size:x} vs {len(shdr.data):x}"
                offset += len(shdr.data)
                stream.write(shdr.data)

        # hack
        new_offset = Align(offset, 16 if which == EI_CLASS.X_64 else 4)
        padding = (new_offset - offset) * b"\0"
        offset += len(padding)
        stream.write(padding)

        assert offset == self.ehdr.e_shoff, f"e_shoff mismatch {offset:x} vs {self.ehdr.e_shoff:x}"
        for phdr in self.segments:
            if phdr.is_auxiliary:
                continue
            for shdr in phdr.sections:
                data = shdr.pack(which)
                offset += len(data)
                stream.write(data)

    def _load_segements(self, fin: io.BytesIO, which) -> Tuple[int, List[Segment]]:
        size = Segment.SIZE[which]
        assert size == self.ehdr.e_phentsize
        fin.seek(self.ehdr.e_phoff)
        start_vaddr = 0
        segments = []
        for i in range(self.ehdr.e_phnum):
            phdr = Segment()
            segments.append(phdr)
            phdr.unpack(which, fin.read(size))
            phdr.hard_align = phdr.p_vaddr % phdr.p_align == 0
            if start_vaddr == 0 and phdr.p_type == P_TYPE.LOAD:
                start_vaddr = phdr.p_vaddr
            phdr.is_auxiliary = (phdr.p_type in _AUXILIARY_PHDR_TYPE)
        return start_vaddr, segments

    def _load_sections(self, fin: io.BytesIO, which) -> List[Section]:
        size = Section.SIZE[which]
        assert size == self.ehdr.e_shentsize
        fin.seek(self.ehdr.e_shoff)
        shdrs: List[Section] = []
        for i in range(self.ehdr.e_shnum):
            shdr = Section()
            shdrs.append(shdr)
            shdr.unpack(which, fin.read(size))
        # retrieve data
        for shdr in shdrs:
            if shdr.sh_type == SH_TYPE.NOBITS:
                continue
            else:
                fin.seek(shdr.sh_offset)
                shdr.data = fin.read(shdr.sh_size)
        # retrieve section names
        sh_strtab = shdrs[self.ehdr.e_shstrndx]
        for shdr in shdrs:
            shdr.name = str_offset_to_name(shdr.sh_name, sh_strtab)
        return shdrs

    def _load_symbols(self, fin: io.BytesIO, which, shdrs):
        symtab = None
        for shdr in shdrs:
            if shdr.sh_type == SH_TYPE.SYMTAB.value and shdr.name == ".symtab":
                assert symtab is None
                symtab = shdr
        if not symtab:
            return
        strtab = shdrs[symtab.sh_link]
        # note, sh_info is the index of the last local symbol + 1
        size = Symbol.SIZE[which]
        n = symtab.sh_size // size
        assert n * size == symtab.sh_size
        fin.seek(symtab.sh_offset)
        for i in range(n):
            sym = Symbol()
            self.symbols.append(sym)
            if len(shdrs) > sym.st_shndx > 0:
                sym.section = shdrs[sym.st_shndx]
            sym.unpack(which, fin.read(size))
            sym.name = str_offset_to_name(sym.st_name, strtab)

    def load(self, fin: io.BytesIO):
        """Initialize the object from the content of a file """
        assert not self.sections and not self.segments
        self.ehdr_ident.unpack(fin.read(EHdrIdent.SIZE))
        assert self.ehdr_ident.is_valid()
        assert self.ehdr_ident.ei_data == EI_DATA.LSB2

        which = self.ehdr_ident.ei_class

        self.ehdr.unpack(which, fin.read(EHdr.SIZE[which]))

        self.start_vaddr, self.segments = self._load_segements(fin, which)
        self.sections = self._load_sections(fin, which)
        self._load_symbols(fin, which, self.sections)

        # assign sections to segments
        # The null sections goes into the first segment
        # `pseudd_segment` holds all the unmapped sections
        pseudo_segment: Optional[Segment] = None
        for sec in self.sections:
            segments = self.phdrs_containing_shdr(sec)
            if segments:
                assert pseudo_segment is None, (
                    f"{sec} - all mapped sections must precede unmapped ones")
                if len(segments) > 1:
                    for phdr in segments:
                        assert phdr.p_type == P_TYPE.LOAD or phdr.is_auxiliary, f"{phdr}"
                for phdr in segments:
                    phdr.sections.append(sec)

            else:
                assert sec.sh_type != SH_TYPE.X_NULL, f"unexpected {sec}"
                if pseudo_segment is None:
                    pseudo_segment = Segment.MakePseudoSegment()
                    self.segments.append(pseudo_segment)
                pseudo_segment.sections.append(sec)

        print(self)

    def combined_header_size(self) -> int:
        """assumes a layout where the phdrs follow directly after the ehdr"""
        which = self.ehdr_ident.ei_class
        num_phdrs = len([phdr for phdr in self.segments if not phdr.is_pseudo])
        return EHdrIdent.SIZE + EHdr.SIZE[which] + num_phdrs * Segment.SIZE[which]

    def verify_vaddrs_and_offsets(self):
        """Compute the section addresses and offsets.

        Note, this assumes we already know how many segments there are which must be
        reflected in len(self.phdrs)
        """
        which = self.ehdr_ident.ei_class
        offset = 0
        vaddr = 0
        for phdr in self.segments:
            if phdr.is_auxiliary:
                continue
            if offset == 0:
                offset = self.combined_header_size()
                vaddr = self.combined_header_size() + self.start_vaddr
            elif phdr.hard_align:
                vaddr = Align(vaddr + 1, phdr.p_align)
                offset = Align(offset + 1, phdr.p_align)
            else:
                vaddr = vaddr + phdr.p_align
            print("NEW PHDR", phdr)
            for shdr in phdr.sections:
                print("SHDR", shdr)
                vaddr, offset = shdr.verify_vaddr_and_offset(vaddr, offset)

        # the section headers are written last
        offset = Align(offset, 16 if which == EI_CLASS.X_64 else 4)
        assert self.ehdr.e_shoff == offset, f"{offset:x}  {self.ehdr.e_shoff:x}"
        assert self.ehdr.e_phoff == EHdrIdent.SIZE + EHdr.SIZE[which]

        # check phdr
        is_first_load = True
        for phdr in self.segments:
            if phdr.is_pseudo:
                continue

            first_shdr = phdr.sections[0]
            if phdr.p_type == P_TYPE.LOAD and is_first_load:
                assert phdr.p_offset == 0, f"{phdr.p_offset:x}"
                assert phdr.p_vaddr == self.start_vaddr
                is_first_load = False
            else:
                assert phdr.p_offset == first_shdr.sh_offset
                assert phdr.p_vaddr == first_shdr.sh_addr
            assert phdr.p_paddr == phdr.p_vaddr

            last_shdr = phdr.sections[-1]
            filesz = 0 if last_shdr.sh_type == SH_TYPE.NOBITS else last_shdr.sh_size
            assert phdr.p_filesz == last_shdr.sh_offset + filesz - phdr.p_offset
            assert phdr.p_memsz == last_shdr.sh_addr + last_shdr.sh_size - phdr.p_vaddr

    def update_vaddrs_and_offset(self):
        """Compute the section addresses and offsets.

        Note, this assumes we already know how many segments there are which must be
        reflected in len(self.phdrs)
        """
        # print("COMPUTE VADDRS AND OFFSETS")
        which = self.ehdr_ident.ei_class
        # update shdr first
        offset = 0
        vaddr = 0
        for phdr in self.segments:
            if phdr.is_auxiliary:
                continue
            if offset == 0:
                offset = self.combined_header_size()
                vaddr = self.combined_header_size() + self.start_vaddr
            elif phdr.hard_align:
                vaddr = Align(vaddr + 1, phdr.p_align)
                offset = Align(offset + 1, phdr.p_align)
            else:
                vaddr += phdr.p_align
            for sec in phdr.sections:
                assert sec in self.sections
                vaddr, offset = sec.update_vaddr_and_offset(vaddr, offset)

        # update ehdr
        # the section headers are written last
        offset = Align(offset, 16 if which == EI_CLASS.X_64 else 4)
        self.ehdr.e_shoff = offset
        self.ehdr.e_phoff = EHdrIdent.SIZE + EHdr.SIZE[which]

        # now update phdr
        is_first_load = True
        for phdr in self.segments:
            if phdr.is_pseudo:
                continue

            first_shdr = phdr.sections[0]
            if phdr.p_type == P_TYPE.LOAD and is_first_load:
                phdr.p_offset = 0
                phdr.p_vaddr = self.start_vaddr
                is_first_load = False
            else:
                phdr.p_offset = first_shdr.sh_offset
                phdr.p_vaddr = first_shdr.sh_addr
            phdr.p_paddr = phdr.p_vaddr

            last_shdr = phdr.sections[-1]
            filesz = 0 if last_shdr.sh_type == SH_TYPE.NOBITS else last_shdr.sh_size
            phdr.p_filesz = last_shdr.sh_offset + filesz - phdr.p_offset
            phdr.p_memsz = last_shdr.sh_addr + last_shdr.sh_size - phdr.p_vaddr

    def __str__(self):
        out = [
            str(self.ehdr_ident),
            str(self.ehdr),
            "PHDR type      flags   offset    vaddr  paddr  filesz   memsz align"
        ]

        for i, phdr in enumerate(self.segments):
            out.append(f"[{i:2}] {phdr}")

        out.append("SHDR  name                  type      flags     addr  offset    size")

        for i, shdr in enumerate(self.sections):
            out.append(f"[{i:2}] {shdr}")

        # expected_phdrs = SHDR_TO_PHDRS[shdr.name]
        # actual_phdrs = [(p.p_type, p.flag_str()) for p in phdrs]
        # for ep in expected_phdrs:
        #     assert ep in actual_phdrs, f"{shdr.name} {ep} {actual_phdrs}"
        out.append(f"HEADER SIZE: {self.combined_header_size():x}")

        out.append("SYM  name                  type      flags     addr  offset    size")
        for i, sym in enumerate(self.symbols):
            out.append(f"[{i:3}] {sym}")
        return "\n".join(out)


TESTS = [
    "/bin/bash",
    "/usr/bin/gcc",
]

# /usr/lib/ld-linux.so.2
#
# /bin/Xwayland
# /usr/bin/qemu-aarch64_be-static
#  /usr/bin/gcc
#  /usr/bin/clang
#  /opt/google/chrome/chrome

if __name__ == "__main__":
    import sys
    assert len(sys.argv) > 1
    sys.argv.pop(0)
    mode = sys.argv.pop(0)


    def verify(exe: str):
        fin = open(exe, "rb")
        obj = Executable()
        obj.load(fin)
        obj.verify_vaddrs_and_offsets()


    def clone(exe: str, exe_clone: str):
        fin = open(exe, "rb")
        obj = Executable()
        obj.load(fin)
        obj.verify_vaddrs_and_offsets()
        fout = open(exe_clone, "wb")
        obj.save(fout)


    if mode == "verify":
        assert len(sys.argv) == 1
        verify(sys.argv[0])
    elif mode == "clone":
        assert len(sys.argv) == 2
        clone(sys.argv[0], sys.argv[1])
    else:
        assert False, f"unknown mode {mode}"
