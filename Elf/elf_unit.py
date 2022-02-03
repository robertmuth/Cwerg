from typing import List, Dict, Optional, Any
import Elf.elfhelper as elf

ZERO_BYTE = bytes([0])


class Unit:
    """Hold a collection of Elf Section comprising an Elf Exe

     It is aimed at Cwerg code generation.
     """

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

    def AddReloc(self, reloc_kind, sec: elf.Section, symbol: elf.Symbol,
                 extra: int, reloc_offset_addend=0):
        self.relocations.append(
            elf.Reloc.Init(reloc_kind.value, sec,
                           len(sec.data) + reloc_offset_addend, symbol, extra))

    def FunStart(self, name: str, alignment: int, padding_or_padder: Any):
        self.sec_text.PadData(alignment, padding_or_padder)
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

    def AddFunAddr(self, reloc_type, size: int, fun_name: str):
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(fun_name, False)
        self.AddReloc(reloc_type, self.mem_sec, symbol, 0)
        self.mem_sec.AddData(b"\0" * size)

    def AddBblAddr(self, reloc_type, size: int, bbl_name: str):
        assert self.current_fun is not None
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(bbl_name, True)
        self.AddReloc(reloc_type, self.mem_sec, symbol, 0)
        self.mem_sec.AddData(b"\0" * size)

    def AddMemAddr(self, reloc_type, size: int, mem_name: str, addend: int):
        assert self.mem_sec is not None
        symbol = self.FindOrAddSymbol(mem_name, False)
        self.AddReloc(reloc_type, self.mem_sec, symbol, addend)
        self.mem_sec.AddData(b"\0" * size)

    def AddLabel(self, name: str, alignment: int, padding_or_padder: Any):
        self.sec_text.PadData(alignment, padding_or_padder)
        assert self.current_fun is not None
        self.AddSymbol(name, self.sec_text, True)

    def AddLinkerDefs(self):
        """must be called last - do we really need linkerdefs?"""
        if self.sec_bss.sh_size > 0:
            self.sec_bss.PadData(16, ZERO_BYTE)
            self.AddSymbol("$$rw_data_end", self.sec_bss, False)
        elif self.sec_data.sh_size > 0:
            self.sec_data.PadData(16, ZERO_BYTE)
            self.AddSymbol("$$rw_data_end", self.sec_data, False)

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
