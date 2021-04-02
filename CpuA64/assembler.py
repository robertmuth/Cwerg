#!/usr/bin/python3

"""
This files contains ELF like abstraction to help build an a64 assembler.
"""
from typing import List, Dict, Optional, Any

import CpuA64.opcode_tab as a64
from CpuA64 import symbolic
import Elf.elfhelper as elf
import Elf.enum_tab as elf_enum
from Util import parse
from Elf import elf_unit

NOP_BYTES = bytes([0x1f, 0x20, 0x03, 0xd5])


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


def HandleOpcode(mnemonic, token: List[str], unit: elf_unit.Unit):
    ins = symbolic.InsFromSymbolized(mnemonic, token)
    if ins.reloc_kind != elf_enum.RELOC_TYPE_AARCH64.NONE:
        sym = unit.FindOrAddSymbol(ins.reloc_symbol, ins.is_local_sym)
        unit.AddReloc(ins.reloc_kind, unit.sec_text, sym, ins.operands[ins.reloc_pos])
        # clear reloc info before proceeding
        ins.reloc_kind = elf_enum.RELOC_TYPE_AARCH64.NONE
        ins.operands[ins.reloc_pos] = 0
    unit.sec_text.AddData(a64.Assemble(ins).to_bytes(4, byteorder='little'))


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
    assert False
    self.FunStart("_start", 16, NOP_BYTES)
    for mnemonic, ops in [
        ("ldr_imm_add", "al r0 sp 0"),
        ("add_imm", "al r1 sp 4"),
        ("bl", "al expr:call:main"),
        ("movw", "al r7 1"),
        ("svc", "al 0"),
        ("ud2", "al")]:
        HandleOpcode(mnemonic, ops.split(), unit)
    self.FunEnd()


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


# sample 90000440
_OPCODE_ADRP: a64.Opcode = a64.Opcode.name_to_opcode["adrp"]
# sample 9126c000
_OPCODE_ADD_X_IMM: a64.Opcode = a64.Opcode.name_to_opcode["add_x_imm"]
# sample 14014192
_OPCODE_B: a64.Opcode = a64.Opcode.name_to_opcode["b"]
# sample 97fffcf7
_OPCODE_BL: a64.Opcode = a64.Opcode.name_to_opcode["bl"]
# sample 54000140
_OPCODE_COND_BR = [a64.Opcode.name_to_opcode[f"b_{cond}"] for cond in a64.CONDITION_CODES]


def _patch_ins(ins_old: int, opcode: a64.Opcode, pos: int, value: int):
    ops = opcode.DisassembleOperands(ins_old)
    ops[pos] = value
    return opcode.AssembleOperands(ops)


def _branch_offset(rel: elf.Reloc, sym_val: int) -> int:
    return (sym_val - (rel.section.sh_addr + rel.r_offset)) >> 2


def _adrp_offset(rel: elf.Reloc, sym_val: int) -> int:
    return (sym_val >> 12) - ((rel.section.sh_addr + rel.r_offset) >> 12)


def _ApplyRelocation(rel: elf.Reloc):
    sec_data = rel.section.data
    sym_val = rel.symbol.st_value + rel.r_addend
    assert rel.r_offset + 4 <= len(sec_data)
    old_data = int.from_bytes(sec_data[rel.r_offset:rel.r_offset + 4], "little")

    if rel.r_type == elf_enum.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21.value:
        new_data = _patch_ins(old_data, _OPCODE_ADRP, 1, _adrp_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC.value:
        new_data = _patch_ins(old_data, _OPCODE_ADD_X_IMM, 2, sym_val & 0xfff)
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.CONDBR19.value:
        new_data = _patch_ins(old_data, _OPCODE_COND_BR[old_data & 0xf], 0, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.JUMP26.value:
        new_data = _patch_ins(old_data, _OPCODE_B, 0, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.CALL26.value:
        new_data = _patch_ins(old_data, _OPCODE_BL, 1, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.ABS32.value:
        new_data = sym_val
    elif rel.r_type == elf_enum.RELOC_TYPE_AARCH64.ABS64.value:
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

    if create_sym_tab:
        # we do not create the content here since we cannot really do this until
        # the section addresses are finalized
        which = elf_enum.EI_CLASS.X_64
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

    exe = elf.Executable.MakeExecutableA64(0x400000, sections, segments)
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
