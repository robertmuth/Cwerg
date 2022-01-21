#!/usr/bin/python3

"""
This files contains ELF like abstraction to help build an a64 assembler.
"""
from typing import List, Dict, Any

from CpuX64 import opcode_tab as x64
from CpuX64 import symbolic
from Elf import elf_unit
from Elf import elfhelper as elf
from Elf import enum_tab
from Util import parse

# TODO: improve this by using multiple byte nop instructions where possible
NOP_BYTES = bytes([0x90])


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


def _RelocFieldOffsetFromEndOfIns(opcode: x64.Opcode):
    """We measure from the end for two reasons
    1) the instruction may have additional prefixes
    2) for pc relative addressing, the pc will point this many bytes further ahead

    Note, we probably should take the reloc operand pos into account
    """
    if opcode.offset_pos > 0:
        # if the ins has an offset we assume that is gets relocated.
        return len(opcode.data) - opcode.offset_pos
    else:
        assert opcode.imm_pos > 0
        return len(opcode.data) - opcode.imm_pos


def AddIns(unit: elf_unit.Unit, ins: x64.Ins):
    if ins.has_reloc():
        sym = unit.FindOrAddSymbol(ins.reloc_symbol, ins.is_local_sym)
        kind = ins.reloc_kind
        addend = ins.operands[ins.reloc_pos]
        ins.clear_reloc()  # we need to clear the reloc info BEFORE assembling
        ins_data = bytes(x64.Assemble(ins))  # note we do not know the exact length because of prefixes
        distance_to_ins_end = _RelocFieldOffsetFromEndOfIns(ins.opcode)
        if kind in {enum_tab.RELOC_TYPE_X86_64.PC32}:
            addend -= distance_to_ins_end
        unit.AddReloc(kind, unit.sec_text, sym, addend, len(ins_data) - distance_to_ins_end)
    else:
        ins_data = bytes(x64.Assemble(ins))
    unit.sec_text.AddData(ins_data)


def HandleOpcode(mnemonic, token: List[str], unit: elf_unit.Unit):
    AddIns(unit, symbolic.InsFromSymbolized(mnemonic, token))


def AddStartUpCode(unit: elf_unit.Unit):
    """Add code for `_start` wrapper which calls main(()

    When Linux transfers control to a new A32 program is does not follow any calling
    convention so we need this shim.
    The initial execution env looks like this:
    0(sp)			    argc
    8(sp)			    argv[0] # argv start
    16(sp)               argv[1]
    ...
    (8*argc)(sp)        NULL    # argv sentinel

    (8*(argc+1))(sp)    envp[0] # envp start
    (8*(argc+2))(sp)    envp[1]
    ...
                        NULL    # envp sentinel

    This feature is needed by CodeGenA64/
    """
    unit.FunStart("_start", 16, NOP_BYTES)
    for mnemonic, ops in [
        ("mov_64_r_mbis8", "rdi rsp noindex 0 0"),  # argc
        ("lea_64_r_mbis8", "rsi rsp noindex 0 8"),  # argv
        ("lea_64_r_mbis8", "rdx rsp rdi 3 16"),  # envp
        # default mxcsr is 0x1f80
        # description: https://wiki.osdev.org/SSE
        # force "rounding down"
        ("stmxcsr_32_mbis8", "rsp noindex 0 -4"),
        ("and_32_mbis8_imm32", "rsp noindex 0 -4 0xffff9fff"),
        ("or_32_mbis8_imm32", "rsp noindex 0 -4 0x2000"),
        ("ldmxcsr_32_mbis8", "rsp noindex 0 -4"),
        ("call_32", "expr:pcrel32:main"),
        # edi contains result from main
        ("mov_32_r_imm32", "edi 0x0"),
        ("mov_64_mr_imm32", "rax 0x3c"),
        ("syscall", ""),
        # unreachable
        ("int3", "")]:
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
        ".addr.fun": lambda x, y: unit.AddFunAddr(enum_tab.RELOC_TYPE_X86_64.X_64, int(x, 0), y),
        ".addr.bbl": lambda x, y: unit.AddBblAddr(enum_tab.RELOC_TYPE_X86_64.X_64, int(x, 0), y),
        ".addr.mem": lambda x, y, z: unit.AddMemAddr(enum_tab.RELOC_TYPE_X86_64.X_64, int(x, 0), y, int(z, 0)),
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


def _pc_offset(rel: elf.Reloc, sym_val: int) -> int:
    return sym_val - (rel.section.sh_addr + rel.r_offset)


def _RelWidth(rel_type: int):
    return 8 if rel_type == enum_tab.RELOC_TYPE_X86_64.X_64.value else 4


def _ApplyRelocation(rel: elf.Reloc):
    sec_data = rel.section.data
    sym_val = rel.symbol.st_value + rel.r_addend
    width = _RelWidth( rel.r_type)
    if rel.r_type == enum_tab.RELOC_TYPE_X86_64.PC32.value:
        assert rel.r_offset + width <= len(sec_data)
        new_data = _pc_offset(rel, sym_val)
        assert -(1 << 31) <= new_data < (1 << 31), f"out of range reloc {rel.symbol.name} {new_data}"
        sec_data[rel.r_offset:rel.r_offset + width] = new_data.to_bytes(width, "little", signed=True)
    elif rel.r_type == enum_tab.RELOC_TYPE_X86_64.X_64.value:
        sec_data[rel.r_offset:rel.r_offset + width] = sym_val.to_bytes(width, "little")
    else:
        assert False, f"unknown kind reloc {rel}"


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
        which = enum_tab.EI_CLASS.X_64
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

    exe = elf.Executable.MakeExecutableX64(0x400000, sections, segments)
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
