#!/usr/bin/python3

"""
This files contains ELF like abstraction to help build an assembler.
"""
from typing import List, Dict, Optional, Any

import CpuA32.opcode_tab as arm
import CpuA32.disassembler as dis
import Elf.elfhelper as elf
import Elf.enum_tab as elf_enum
from Util import parse

ZERO_BYTE = bytes([0])
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


class Unit:
    """Holds a low level binary version of an A32 executable """

    def __init__(self):
        self.sec_text = elf.Section.MakeSectionText(1)
        self.sec_rodata = elf.Section.MakeSectionRodata(1)
        self.sec_data = elf.Section.MakeSectionData(1)
        self.sec_bss = elf.Section.MakeSectionBss(1)
        #
        self.global_symbol_map: Dict[str, elf.Symbol] = {}
        self.symbols: List[elf.Symbol] = []
        self.relocations: List[elf.Reloc] = []

        # used while processing
        self.local_symbol_map: Dict[str, elf.Symbol] = {}
        self.mem_sec: Optional[elf.Section] = None
        self.current_fun: Optional[str] = None

    def AddSymbol(self, name, sec: Optional[elf.Section], is_local: bool) -> elf.Symbol:
        the_map = self.local_symbol_map if is_local else self.global_symbol_map
        sym = the_map.get(name)
        if sym is None:
            # ~0 is our undefined symbol marker. It is checked in
            val = ~0 if sec is None else len(sec.data)
            sym = elf.Symbol.Init(name, is_local, sec, val)
            self.symbols.append(sym)
            the_map[name] = sym
            return sym
        elif sec is not None:
            # the symbol was forward declared and now we are filling in the missing info
            assert sym.is_undefined(), f"{sym} already defined"
            sym.section = sec
            sym.st_value = len(sec.data)
        return sym

    def FindOrAddSymbol(self, name, is_local) -> elf.Symbol:
        the_map = self.local_symbol_map if is_local else self.global_symbol_map

        sym = the_map.get(name)
        if sym is None:
            return self.AddSymbol(name, None, is_local)
        return sym

    def AddReloc(self, kind: elf_enum.RELOC_TYPE_ARM, sec: elf.Section, symbol: elf.Symbol,
                 extra: int):
        self.relocations.append(
            elf.Reloc.Init(kind.value, sec, len(sec.data), symbol, extra))

    def FunStart(self, name: str, alignment: int):
        self.sec_text.PadData(alignment, NOP_BYTES)
        self.AddSymbol(name, self.sec_text, False)
        assert self.current_fun is None
        self.current_fun = name

    def FunEnd(self):
        assert self.current_fun is not None
        self.current_fun = None
        self.local_symbol_map.clear()

    def MemStart(self, name: str, alignment: int, kind: str, is_local_sym):
        assert self.mem_sec is None
        if kind == "rodata":
            self.mem_sec = self.sec_rodata
        elif kind == "data":
            self.mem_sec = self.sec_data
        elif kind == "bss":
            self.mem_sec = self.sec_bss
        else:
            assert False, f"bad mem kind {kind}"
        self.mem_sec.PadData(alignment, ZERO_BYTE)
        self.AddSymbol(name, self.mem_sec, is_local_sym)

    def MemEnd(self):
        assert self.mem_sec is not None
        self.mem_sec = None

    def AddData(self, repeats: int, data: bytes):
        assert self.mem_sec is not None
        self.mem_sec.AddData(data * repeats)

    def AddFunAddr(self, size: int, fun_name: str):
        assert size == 4
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(fun_name, False)
        self.AddReloc(elf_enum.RELOC_TYPE_ARM.ABS32, self.mem_sec, symbol, 0)
        self.mem_sec.AddData(b"\0" * size)

    def AddBblAddr(self, size: int, bbl_name: str):
        assert size == 4
        assert self.current_fun is not None
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(bbl_name, True)
        self.AddReloc(elf_enum.RELOC_TYPE_ARM.ABS32, self.mem_sec, symbol, 0)
        self.mem_sec.AddData(b"\0" * size)

    def AddMemAddr(self, size: int, mem_name: str, addend: int):
        assert size == 4
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(mem_name, False)
        self.AddReloc(elf_enum.RELOC_TYPE_ARM.ABS32, self.mem_sec, symbol, addend)
        self.mem_sec.AddData(b"\0" * size)

    def AddLabel(self, name: str, alignment: int):
        assert alignment % len(NOP_BYTES) == 0
        self.sec_text.PadData(alignment, NOP_BYTES)
        assert self.current_fun is not None
        self.AddSymbol(name, self.sec_text, True)

    def AddIns(self, ins: arm.Ins):
        if ins.reloc_kind != elf_enum.RELOC_TYPE_ARM.NONE:
            sym = self.FindOrAddSymbol(ins.reloc_symbol, ins.is_local_sym)
            self.AddReloc(ins.reloc_kind, self.sec_text, sym, ins.operands[ins.reloc_pos])
            # clear reloc info before proceeding
            ins.reloc_kind = elf_enum.RELOC_TYPE_ARM.NONE
            ins.operands[ins.reloc_pos] = 0
        self.sec_text.AddData(arm.Assemble(ins).to_bytes(4, byteorder='little'))

    def AddLinkerDefs(self):
        """must be called last"""
        if self.sec_bss.sh_size > 0:
            self.sec_bss.PadData(16, ZERO_BYTE)
            self.AddSymbol("$$rw_data_end", self.sec_bss, False)
        elif self.sec_data.sh_size > 0:
            self.sec_data.PadData(16, ZERO_BYTE)
            self.AddSymbol("$$rw_data_end", self.sec_data, False)

    def AddStartUpCode(self):
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
        self.FunStart("_start", 16)
        for mnemonic, ops in [
            ("ldr_imm_add", "al r0 sp 0"),
            ("add_imm", "al r1 sp 4"),
            ("bl", "al expr:call:main"),
            ("movw", "al r7 1"),
            ("svc", "al 0"),
            ("ud2", "al")]:
            self.AddIns(dis.InsParse(mnemonic, ops.split()))
        self.FunEnd()

    def __str__(self):
        syms = {}
        return f"""UNIT
SECTION[text] {len(self.sec_text.data)}
{DumpData(self.sec_text.data, 0, syms)}
SECTION[rodata] {len(self.sec_rodata.data)}
{DumpData(self.sec_rodata.data, 0, syms)}     
SECTION[data] {len(self.sec_data.data)}
{DumpData(self.sec_data.data, 0, syms)}    
SECTION[bss] {len(self.sec_bss.data)}
{DumpData(self.sec_bss.data, 0, syms)}    
"""


def HandleOpcode(mnemonic, token: List[str], unit: Unit):
    ins = dis.InsParse(mnemonic, token)
    unit.AddIns(ins)


class ParseError(Exception):
    pass


def UnitParse(fin, add_startup_code) -> Unit:
    unit = Unit()
    dir_handlers = {
        ".fun": lambda x, y: unit.FunStart(x, int(y, 0)),
        ".endfun": unit.FunEnd,
        ".mem": lambda x, y, z: unit.MemStart(x, int(y, 0), z, False),
        ".localmem": lambda x, y, z: unit.MemStart(x, int(y, 0), z, True),
        ".endmem": unit.MemEnd,
        ".data": lambda x, y: unit.AddData(int(x, 0),
                                           parse.QuotedEscapedStringToBytes(y)),
        ".addr.fun": lambda x, y: unit.AddFunAddr(int(x, 0), y),
        ".addr.bbl": lambda x, y: unit.AddBblAddr(int(x, 0), y),
        ".addr.mem": lambda x, y, z: unit.AddMemAddr(int(x, 0), y, int(z, 0)),
        ".bbl": lambda x, y: unit.AddLabel(x, int(y, 0)),
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
        unit.AddStartUpCode()
    return unit


_OPCODE_MOVW: arm.Opcode = arm.Opcode.name_to_opcode["movw"]
_OPCODE_MOVT: arm.Opcode = arm.Opcode.name_to_opcode["movt"]
_OPCODE_B: arm.Opcode = arm.Opcode.name_to_opcode["b"]
_OPCODE_BL: arm.Opcode = arm.Opcode.name_to_opcode["bl"]


def _patch_ins(ins_old: int, opcode: arm.Opcode, pos: int, value: int):
    ops = opcode.DisassembleOperands(ins_old)
    ops[pos] = value
    return opcode.AssembleOperands(ops)


def _branch_offset(rel: elf.Reloc, sym_val: int) -> int:
    return (sym_val - rel.section.sh_addr - rel.r_offset - 8) >> 2


def _ApplyRelocation(rel: elf.Reloc):
    sec_data = rel.section.data
    sym_val = rel.symbol.st_value + rel.r_addend
    assert rel.r_offset + 4 <= len(sec_data)
    old_data = int.from_bytes(sec_data[rel.r_offset:rel.r_offset + 4], "little")

    if rel.r_type == elf_enum.RELOC_TYPE_ARM.MOVW_ABS_NC.value:
        new_data = _patch_ins(old_data, _OPCODE_MOVW, 2, sym_val & 0xffff)
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.MOVT_ABS.value:
        new_data = _patch_ins(old_data, _OPCODE_MOVT, 2, (sym_val >> 16) & 0xffff)
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.JUMP24.value:
        new_data = _patch_ins(old_data, _OPCODE_B, 1, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.CALL.value:
        new_data = _patch_ins(old_data, _OPCODE_BL, 2, _branch_offset(rel, sym_val))
    elif rel.r_type == elf_enum.RELOC_TYPE_ARM.ABS32.value:
        new_data = sym_val
    else:
        assert False, f"unknown kind reloc {rel}"

    sec_data[rel.r_offset:rel.r_offset + 4] = new_data.to_bytes(4, "little")
    print(f"PATCH INS {rel.r_type} {rel.r_offset:x} {sym_val:x} {old_data:x} {new_data:x} {rel.symbol.name}")


def Assemble(unit: Unit, create_sym_tab: bool) -> elf.Executable:
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
