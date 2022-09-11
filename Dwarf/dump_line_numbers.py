#!/usr/bin/python3
"""
Tool for dumping dwarf line number info
"""

from ctypes.wintypes import SIZE
import dataclasses
import struct
import io
import enum
from typing import List, Dict, Optional, Set, Tuple, Any, BinaryIO


from Elf.elfhelper import Executable
from Elf.enum_tab import EI_CLASS
from Util import parse



@enum.unique
class DW_LNCT(enum.IntEnum):
    path = 1
    directory_index = 2
    timestamp = 3
    size = 4
    MD5 = 5
    LLVM_source = 8193
    lo_user = 8192
    hi_user = 16383


@enum.unique
class DW_FORM(enum.IntEnum):
    addr = 0x01
    block2 = 0x03
    block4 = 0x04
    data2 = 0x05
    data4 = 0x06
    data8 = 0x07
    string = 0x08
    block = 0x09
    block1 = 0x0a
    data1 = 0x0b
    flag = 0x0c
    sdata = 0x0d
    strp = 0x0e
    udata = 0x0f
    ref_addr = 0x10
    ref1 = 0x11
    ref2 = 0x12
    ref4 = 0x13
    ref8 = 0x14
    ref_udata = 0x15
    indirect = 0x16
    sec_offset = 0x17
    exprloc = 0x18
    flag_present = 0x19
    strx = 0x1a
    addrx = 0x1b
    ref_sup4 = 0x1c
    strp_sup = 0x1d
    data16 = 0x1e
    line_strp = 0x1f
    ref_sig8 = 0x20
    implicit_const = 0x21
    loclistx = 0x22
    rnglistx = 0x23
    ref_sup8 = 0x24
    strx1 = 0x25
    strx2 = 0x26
    strx3 = 0x27
    strx4 = 0x28
    addrx1 = 0x29
    addrx2 = 0x2a
    addrx3 = 0x2b
    addrx4 = 0x2c


@enum.unique
class DW_LNS(enum.IntEnum):
    copy = 1
    advance_pc = 2
    advance_line = 3
    set_file = 4
    set_column = 5
    negate_stmt = 6
    set_basic_block = 7
    const_add_pc = 8
    fixed_advance_pc = 9
    set_prologue_end = 10
    set_epilogue_begin = 11
    set_isa = 12


@enum.unique
class DW_LNE(enum.IntEnum):
    end_sequence = 1
    set_address = 2
    set_file = 3
    set_discriminator = 4
    lo_user = 0x80
    hi_user = 0xff


def ReadEntryList(data) -> Tuple[List, List]:
    format_count = ord(data.read(1))
    format = []
    for _ in range(format_count):
        a = parse.read_leb128(data)
        b = parse.read_leb128(data)
        format.append((DW_LNCT(a), DW_FORM(b)))
    entry_count = parse.read_leb128(data)
    entries = []
    for _ in range(entry_count):
        d = []
        entries.append(d)
        for lnct, form in format:
            if form is DW_FORM.line_strp:
                d.append(int.from_bytes(data.read(4), 'little'))
            elif form is DW_FORM.udata:
                d.append(parse.read_leb128(data))
            elif form is DW_FORM.data1:
                d.append(int.from_bytes(data.read(1), 'little'))
            elif form is DW_FORM.data2:
                d.append(int.from_bytes(data.read(2), 'little'))
            elif form is DW_FORM.data4:
                d.append(int.from_bytes(data.read(4), 'little'))
            elif form is DW_FORM.data8:
                d.append(int.from_bytes(data.read(8), 'little'))
            else:
                assert False, f"{str(lnct)}, {str(form)}"
    return format, entries


class DeltaEncoder:

    def __init__(self, opcode_base, line_base, line_range, min_instruction_length):
        self._opcode_base = opcode_base
        self._line_base = line_base
        self._line_range = line_range
        self._min_instruction_length = min_instruction_length
        self._max_ad_normalized = (
            255 - opcode_base) // line_range * line_range
        self.max_ad = self._max_ad_normalized // line_range * min_instruction_length

    def ld_within_range(self, ld):
        return ld >= self._line_base and ld < self._line_base + self._line_range

    def code_from_delta(self, ad, ld) -> Tuple[int, bool]:
        if not self.ld_within_range(ld):
            return None, None
        assert ad % self._min_instruction_length == 0
        a = ld - self._line_base
        b = ad // self._min_instruction_length * self._line_range
        out = a + b + self._opcode_base
        if out <= 255:
            return out, False
        out -= self._max_ad_normalized  # pretend we have a DW_LNS_const_add_pc
        if out <= 255:
            return out, True
        return None, None

    def deltas_from_code(self, x):
        xx = x - self._opcode_base
        ad = xx // self._line_range * self._min_instruction_length
        ld = self._line_base + xx % self._line_range
        assert self.code_from_delta(ad, ld)[0] == x, f"{x} {ad} {ld}"
        return ad, ld


@ dataclasses.dataclass
class StateMachine:
    address: int = 0
    # op_index:int  = 0  # irrelevant for our purposes- vliw only
    file: int = 1
    line: int = 1
    column: int = 0
    is_stmt: bool = True
    basic_block:  bool = False
    end_sequence: bool = False
    prologue_end: bool = False
    epilogue_begin: bool = False
    isa: int = 0
    discriminator: int = 0

    def clear(self):
        self.discriminator = 0
        self.basic_block = False
        self.prologue_end = False
        self.epilogue_begin = False

    @ staticmethod
    def New(default_is_stmt: bool):
        out = StateMachine()
        out.is_stmt = default_is_stmt
        return out


def ReadCommands(end, data: io.BytesIO, delta_enc, default_is_stmt: bool,
                 opcode_base: int) -> List[StateMachine]:
    sm = StateMachine.New(default_is_stmt)
    out: List[StateMachine] = []

    while data.tell() < end:
        print(f"[0x{data.tell():08x}]  ", end="")
        op = ord(data.read(1))
        if op == 0:
            # extended
            size = parse.read_leb128(data)
            op = ord(data.read(1))
            x = DW_LNE(op)
            if x is DW_LNE.set_address:
                sm.address = int.from_bytes(data.read(size - 1), "little")
                print(f"Extended opcode {op}: set Address to 0x{sm.address:x}")
            elif x is DW_LNE.end_sequence:
                print(f"Extended opcode {op}: End of Sequence\n")
                sm.end_sequence = True
                out.append(dataclasses.replace(sm))
                sm = StateMachine.New(default_is_stmt)
                # if data.tell() > 900: return out  # HACK
                # return out
            elif x is DW_LNE.set_discriminator:
                sm.discriminator = parse.read_leb128(data)
                print(
                    f"Extended opcode {op}: set Discriminator to {sm.discriminator}")
            else:
                assert False, x
        elif op < opcode_base:
            # standard
            x = DW_LNS(op)
            if x is DW_LNS.set_column:
                sm.column = parse.read_leb128(data)
                print(f"Set column to {sm.column}")
            elif x is DW_LNS.advance_pc:
                v = parse.read_leb128(data)
                sm.address += v
                print(f"Advance PC by {v} to 0x{sm.address:x}")
            elif x is DW_LNS.advance_line:
                v = parse.read_leb128(data, True)
                sm.line += v
                print(f"Advance Line by {v} to {sm.line}")
            elif x is DW_LNS.copy:
                print(f"Copy")
                out.append(dataclasses.replace(sm))
                assert out[-1].is_stmt == sm.is_stmt, f"{sm}"
                sm.clear()

            elif x is DW_LNS.negate_stmt:
                sm.is_stmt = not sm.is_stmt
                print(f"Set is_stmt to {int(sm.is_stmt)}")
            elif x is DW_LNS.set_file:
                sm.file = parse.read_leb128(data)
                print(
                    f"Set File Name to entry {sm.file} in the File Name Table")
            elif x is DW_LNS.const_add_pc:
                ad, _ = delta_enc.deltas_from_code(255)
                sm.address += ad
                print(f"Advance PC by constant {ad} to 0x{sm.address:x}")
            else:
                assert False, x
        else:
            # special
            ad, ld = delta_enc.deltas_from_code(op)
            sm.address += ad
            sm.line += ld
            out.append(dataclasses.replace(sm))
            sm.clear()
            print(f"Special opcode {op - opcode_base}: advance Address by {ad} to 0x{sm.address:x} "
                  f"and Line by {ld} to {sm.line}")

    return out


def GenerateCommands(matrix: List[StateMachine], de: DeltaEncoder, default_is_stmt: bool,
                     opcode_base: int) -> bytes:
    out = []
    # max_line
    curr = StateMachine.New(default_is_stmt)
    while matrix:
        next = matrix.pop(0)
        if next.file != curr.file:
            curr.file = next.file
            print(
                f"@@@ Set File Name to entry {curr.file} in the File Name Table")
        
        if next.column != curr.column:
            print(f"@@@ Set column to {next.column}")
            curr.column = next.column
        if next.discriminator != curr.discriminator:
            curr.discriminator = next.discriminator
            print(
                f"@@@ Extended opcode 4: set Discriminator to {curr.discriminator}")

        if next.is_stmt != curr.is_stmt:
            curr.is_stmt = not curr.is_stmt
            print(f"@@@ Set is_stmt to {int(curr.is_stmt)}")

        if curr.address == 0:
            print(
                f"@@@ Extended opcode {DW_LNE.set_address}: set Address to 0x{next.address:x}")
            ld = next.line - curr.line
            print(f"@@@ Advance Line by {ld} to {next.line}")
            print(f"@@@ Copy")
            curr.address = next.address
            curr.line = next.line
            assert curr == next
            curr.clear()
            continue

        ad = next.address - curr.address
        ld = next.line - curr.line
        if not next.end_sequence:
            if not de.ld_within_range(ld):
                print(f"@@@ Advance Line by {ld} to {next.line}")
                curr.line += ld
                ld = 0
            if ad == 0 and ld == 0:
                print(f"@@@ Copy")
                assert curr == next
                curr.clear()
                continue

            opc, const_add_pc = de.code_from_delta(ad, ld)

            if opc is None:
                curr.address += ad
                print(f"@@@ Advance PC by {ad} to 0x{curr.address:x}")
                ad = 0
                opc, const_add_pc = de.code_from_delta(ad, ld)

            if const_add_pc:
                curr.address += de.max_ad
                ad -= de.max_ad
                print(
                    f"@@@ Advance PC by constant {de.max_ad} to 0x{curr.address:x}")
            print(
                f"@@@ Special opcode {opc - opcode_base}: advance Address by {ad} to 0x{next.address:x} and Line by {ld} to {next.line}")
            curr.address += ad
            curr.line += ld
            assert curr == next
            curr.clear()
            continue

        if ad != 0:
            print(f"@@@ Advance PC by {ad} to 0x{next.address:x}")
            curr.address += ad

        if ld != 0:
            print(f"@@@ Advance Line by {ld} to {next.line}")
            curr.line += ld

        curr.end_sequence = True
        assert curr == next
        print("@@@ Extended opcode 1: End of Sequence")
        curr = StateMachine.New(default_is_stmt)
        print()


@ dataclasses.dataclass
class LineNumberProgram:
    """An Elf Symbol"""
    length: int = 0
    version: int = 0
    address_size: int = 0
    segment_selector_size: int = 0
    header_length: int = 0
    min_instruction_length: int = 0
    maximum_operations_per_instruction: int = 0
    default_is_stmt: int = 0
    line_base: int = 0
    line_range: int = 0
    #
    opcode_base: int = 0
    std_opcode_lengths: List[int] = dataclasses.field(default_factory=list)
    #
    directory_entry_format: List[Tuple[DW_LNCT, DW_FORM]
                                 ] = dataclasses.field(default_factory=list)
    directories: List[List[int]] = dataclasses.field(
        default_factory=list)
    file_name_entry_format: List[Tuple[DW_LNCT, DW_FORM]
                                 ] = dataclasses.field(default_factory=list)
    file_names: List[List[int]] = dataclasses.field(
        default_factory=list)

    commands: List = dataclasses.field(
        default_factory=list)

    FORMAT = "<IHBBIBBBbB"
    SIZE = struct.calcsize(FORMAT)

    def unpack(self, data: BinaryIO):
        start = data.tell()
        (self.length,
         self.version,
         self.address_size,
         self.segment_selector_size,
         self.header_length,
         self.min_instruction_length,
         self.maximum_operations_per_instruction,
         self.default_is_stmt,
         self.line_base, self.line_range,) = struct.unpack(
            LineNumberProgram.FORMAT, data.read(LineNumberProgram.SIZE))
        assert self.maximum_operations_per_instruction == 1, "VLIW not supported"
        assert self.version == 5, f"unknown version {self.version}"
        self.opcode_base = ord(data.read(1))
        self.std_opcode_lengths = list(data.read(self.opcode_base - 1))
        #
        self.directory_entry_format, self.directories = ReadEntryList(data)
        self.file_name_entry_format, self.file_names = ReadEntryList(data)
        de = DeltaEncoder(self.opcode_base, self.line_base,
                          self.line_range, self.min_instruction_length)
        print(f"# opcode_base={self.opcode_base} min_instruction_length={self.min_instruction_length} "
              f"line_base={self.line_base} line_range={self.line_range} default_is_stmt={self.default_is_stmt}")
        self.commands = ReadCommands(start + 4 + self.length,
                                     data, de, bool(self.default_is_stmt), self.opcode_base)
        GenerateCommands(self.commands, de,
                         bool(self.default_is_stmt), self.opcode_base)

        # print(orig_size, len(data))


if __name__ == "__main__":
    import sys
    assert len(sys.argv) > 1
    sys.argv.pop(0)
    exe = sys.argv.pop(0)
    fin = open(exe, "rb")
    obj = Executable()
    obj.load(fin)
    sec_line = None
    sec_line_str = None
    for sec in obj.sections:
        if sec.name == ".debug_line":
            sec_line = sec
        elif sec.name == ".debug_line_str":
            sec_line_str = sec
    if sec_line is None or sec_line_str is None:
        print(f"could not find line number info in {exe}")
        exit(1)
    # print(len(sec_line.data))
    data = io.BytesIO(sec_line.data)

    units = []
    while data.tell() < len(sec_line.data):
        # print ("@@@@@@@@")
        lnp = LineNumberProgram()
        lnp.unpack(data)
        units.append(lnp)
        break
    # print(header)
