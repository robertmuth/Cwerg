#!/usr/bin/python3

"""
This files contains ELF like abstraction to help build an assembler.
"""
from typing import List, Dict, Any

import CpuA32.opcode_tab as a32
import CpuA32.symbolic as dis
import Elf.elfhelper as elf
import Elf.enum_tab as elf_enum
from Elf import elf_unit

from Util import parse

NOP_BYTES = bytes([0x00, 0xF0, 0x20, 0xE3])


def DumpData(data: bytes, addr: int, syms: Dict[int, Any]) -> str:
    out = []
    first_address = True
    for n, b in enumerate(data):
        if first_address or (addr + n) % 8 == 0 or (addr + n) in syms:
            out.append(f"{addr:06x}")
            first_address = False
            name = syms.get(addr + n)
            if name:
                out[-1] += f" [{name}]"
        out[-1] += f" {b:02x}"
    return "\n".join(out)


def AddIns(unit: elf_unit.Unit, ins: a32.Ins):
    if ins.reloc_kind != elf_enum.RELOC_TYPE_ARM.NONE:
        sym = unit.FindOrAddSymbol(ins.reloc_symbol, ins.is_local_sym)
        unit.AddReloc(ins.reloc_kind, unit.sec_text, sym, ins.operands[ins.reloc_pos])
        # clear reloc info before proceeding
        ins.reloc_kind = elf_enum.RELOC_TYPE_ARM.NONE
        ins.operands[ins.reloc_pos] = 0
    unit.sec_text.AddData(a32.Assemble(ins).to_bytes(4, byteorder='little'))


def HandleOpcode(mnemonic, token: List[str], unit: elf_unit.Unit):
    AddIns(unit, dis.InsFromSymbolized(mnemonic, token))


def AddStartUpCode(unit: elf_unit.Unit):
    """Add code for `_start` wrapper which calls main(()

    When Linux transfers control to a new A32 program is does not follow any calling
    convention so we need this shim.
    The initial execution env looks like this:
    0(sp)			argc

    4(sp)			    argv[0] # argv start
    8(sp)               argv[1]
    ...
    (4*argc)(sp)        NULL    # argv sentinel

    (4*(argc+1))(sp)    envp[0] # envp start
    (4*(argc+2))(sp)    envp[1]
    ...
                        NULL    # envp sentinel
    """
    unit.FunStart("_start", 16, NOP_BYTES)
    for mnemonic, ops in [
        ("ldr_imm_add", "al r0 sp 0"),
        ("add_imm", "al r1 sp 4"),
        ("bl", "al lr expr:call:main"),
        ("movw", "al r7 1"),
        ("svc", "al 0"),
        ("ud2", "al")]:
        HandleOpcode(mnemonic, ops.split(), unit)
    unit.FunEnd()


class ParseError(Exception):
    pass


def UnitParse(fin, add_startup_code) -> elf_unit.Unit:
    unit = elf_unit.Unit()
    dir_handlers = {
        ".fun": lambda x, y: unit.FunStart(x, int(y, 0), NOP_BYTES),
        ".endfun": unit.FunEnd,
        ".mem": lambda x, y, z: unit.MemStart(x, int(y, 0), z, False),
        ".localmem": lambda x, y, z: unit.MemStart(x, int(y, 0), z, True),
        ".endmem": unit.MemEnd,
        ".data": lambda x, y: unit.AddData(int(x, 0),
                                           parse.QuotedEscapedStringToBytes(y)),
        ".addr.fun": lambda x, y: unit.AddFunAddr(elf_enum.RELOC_TYPE_ARM.ABS32, int(x, 0), y),
        ".addr.bbl": lambda x, y: unit.AddBblAddr(elf_enum.RELOC_TYPE_ARM.ABS32, int(x, 0), y),
        ".addr.mem": lambda x, y, z: unit.AddMemAddr(elf_enum.RELOC_TYPE_ARM.ABS32, int(x, 0), y, int(z, 0)),
        ".bbl": lambda x, y: unit.AddLabel(x, int(y, 0), NOP_BYTES),
    }
    for line_num, line in enumerate(fin):
        token = parse.ParseLine(line)
        # print(line)
        if not token:
            continue
        mnemonic = token.pop(0)

        if mnemonic.startswith("#"):
            continue
        if mnemonic.startswith("."):
            handler = dir_handlers.get(mnemonic)
            assert handler is not None
            handler(*token)
            continue

        try:
            HandleOpcode(mnemonic, token, unit)
        except Exception as err:
            raise ParseError(
                f"UnitParseFromAsm error in line {line_num}:\n{line}\n{token}\n{err}")
    unit.AddLinkerDefs()
    if add_startup_code:
        AddStartUpCode(unit)
    return unit


_OPCODE_MOVW: a32.Opcode = a32.Opcode.name_to_opcode["movw"]
_OPCODE_MOVT: a32.Opcode = a32.Opcode.name_to_opcode["movt"]
_OPCODE_B: a32.Opcode = a32.Opcode.name_to_opcode["b"]
_OPCODE_BL: a32.Opcode = a32.Opcode.name_to_opcode["bl"]


def _branch_offset(rel: elf.Reloc, sym_val: int) -> int:
    return (sym_val - rel.section.sh_addr - rel.r_offset - 8) >> 2


def _ApplyRelocation(rel: elf.Reloc):
    sec_data = rel.section.data
    sym_val = rel.symbol.st_value + rel.r_addend
    assert rel.r_offset + 4 <= len(sec_data)
    old_data = int.from_bytes(sec_data[rel.r_offset:rel.r_offset + 4], "little")

    if rel.r_type == elf_enum.RELOC_TYPE_ARM.MOVW_ABS_NC.value:
        new_data = a32.Patch(old_data, _OPCODE_MOVW, 2, sym_val & 0xffff)
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.MOVT_ABS.value:
        new_data = a32.Patch(old_data, _OPCODE_MOVT, 2, (sym_val >> 16) & 0xffff)
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.JUMP24.value:
        new_data = a32.Patch(old_data, _OPCODE_B, 1, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.CALL.value:
        new_data = a32.Patch(old_data, _OPCODE_BL, 2, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.ABS32.value:
        new_data = sym_val
    else:
        assert False, f"unknown kind reloc {rel}"

    sec_data[rel.r_offset:rel.r_offset + 4] = new_data.to_bytes(4, "little")
    print(f"PATCH INS {rel.r_type} {rel.r_offset:x} {sym_val:x} {old_data:x} {new_data:x} {rel.symbol.name}")


def Assemble(unit: elf_unit.Unit, create_sym_tab: bool) -> elf.Executable:
    sections = []
    segments = []

    seg_exe = elf.Segment.MakeExeSegment(65536)
    segments.append(seg_exe)

    sec_null = elf.Section.MakeSectionNull()
    sections.append(sec_null)
    seg_exe.sections.append(sec_null)
    #
    sec_text = unit.sec_text
    assert len(sec_text.data) > 0
    sections.append(sec_text)
    seg_exe.sections.append(sec_text)

    sec_rodata = unit.sec_rodata
    if len(sec_rodata.data) > 0:
        seg_ro = elf.Segment.MakeROSegment(65536)
        segments.append(seg_ro)
        #
        sections.append(sec_rodata)
        seg_ro.sections.append(sec_rodata)

    if len(unit.sec_data.data) + len(unit.sec_bss.data) > 0:
        seg_rw = elf.Segment.MakeRWSegment(65536)
        segments.append(seg_rw)

    sec_data = unit.sec_data
    if len(sec_data.data) > 0:
        sections.append(sec_data)
        seg_rw.sections.append(sec_data)

    sec_bss = unit.sec_bss
    if len(sec_bss.data) > 0:
        sections.append(sec_bss)
        seg_rw.sections.append(sec_bss)

    seg_pseudo = elf.Segment.MakePseudoSegment()
    segments.append(seg_pseudo)
    #
    sec_attr = elf.Section.MakeSectionArmAttributes()
    sections.append(sec_attr)
    sec_attr.SetData(elf.ARM_ATTRIBUTES)
    seg_pseudo.sections.append(sec_attr)

    if create_sym_tab:
        # we do not create the content here since we cannot really do this until
        # the section addresses are finalized
        which = elf_enum.EI_CLASS.X_32
        sec_symtab = elf.Section.MakeSectionSymTab(".symtab", which, len(sections) + 1)
        sections.append(sec_symtab)
        sec_symtab.SetData(bytearray(len(unit.symbols) * elf.Symbol.SIZE[which]))
        seg_pseudo.sections.append(sec_symtab)
        # TODO: this is not quite right
        sec_symtab.sh_info = len(unit.symbols)

        sym_names = bytearray()
        sym_names += b"\0"
        for sym in unit.symbols:
            if sym.name:
                sym.st_name = len(sym_names)
                sym_names += (bytes(sym.name, "utf-8") + b"\0")
            else:
                sym.st_name = 0
        sec_symstrtab = elf.Section.MakeSectionStrTab(".strtab")
        sections.append(sec_symstrtab)
        sec_symstrtab.SetData(sym_names)
        seg_pseudo.sections.append(sec_symstrtab)

    sec_shstrtab = elf.Section.MakeSectionStrTab(".shstrtab")
    sections.append(sec_shstrtab)
    sec_shstrtab.SetData(elf.MakeSecStrTabContents(sections))
    seg_pseudo.sections.append(sec_shstrtab)

    exe = elf.Executable.MakeExecutableA32(0x20000, sections, segments)
    exe.update_vaddrs_and_offset()

    if False:
        for sym in unit.symbols:
            print("@@@SYMS", sym)
        for rel in unit.relocations:
            print("@@@REL", rel)

    for sym in unit.symbols:
        if sym.section:
            assert sym.section.sh_addr > 0
            assert sym.st_value != elf.TO_BE_FILLED_IN_LATER
            sym.st_value += sym.section.sh_addr
            sym.st_shndx = sym.section.index

    for rel in unit.relocations:
        _ApplyRelocation(rel)

    if create_sym_tab:
        # we only put dummiess in the symtable above - do it for real now
        sec_symtab.data = bytearray()
        for sym in unit.symbols:
            sec_symtab.AddData(sym.pack(which))

    sym_entry = unit.global_symbol_map["_start"]
    assert sym_entry and not sym_entry.is_undefined()
    entry_addr = sym_entry.st_value
    print(f"PATCH ENTRY: {entry_addr:x}")
    exe.ehdr.e_entry = entry_addr
    return exe
