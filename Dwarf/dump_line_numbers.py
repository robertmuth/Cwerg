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


def read_leb128(r: BinaryIO, signed: bool = False) -> int:
    """
    cf. http://en.wikipedia.org/wiki/LEB128
    """
    out = 0
    shift = 0
    while True:
        b = ord(r.read(1))
        out |= (b & 0x7f) << shift
        shift += 7
        if (b & 0x80) == 0:
            if signed and b & 0x40:
                out -= (1 << shift)
            return out


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
        a = read_leb128(data)
        b = read_leb128(data)
        format.append((DW_LNCT(a), DW_FORM(b)))
    entry_count = read_leb128(data)
    entries = []
    for _ in range(entry_count):
        d = []
        entries.append(d)
        for lnct, form in format:
            if form is DW_FORM.line_strp:
                d.append(int.from_bytes(data.read(4), 'little'))
            elif form is DW_FORM.udata:
                d.append(read_leb128(data))
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


@dataclasses.dataclass
class StateMachine:
    address: int = 0
    # op_index:int  = 0  # irrelevant for our purposes- vliw only
    file: int = 1
    line: int = 1
    column: int = 0
    is_stmt = True
    basic_block = False
    end_sequence = False
    prologue_end = False
    epilogue_begin = False
    isa = 0
    discriminator = 0

    def clear(self):
        self.discriminator = 0
        self.basic_block = False
        self.prologue_end = False
        self.epilogue_begin = False

    @staticmethod
    def New(default_is_stmt):
        out = StateMachine()
        out.is_stmt = default_is_stmt
        return out


def ReadCommands(end, data: io.BytesIO, default_is_stmt, opcode_base, line_base, line_range,
                 min_instruction_length, maximum_operations_per_instruction):
    sm = StateMachine.New(default_is_stmt)
    matrix = []

    def addr_delta(x):
        return ((x - opcode_base) // line_range) * min_instruction_length // maximum_operations_per_instruction

    while data.tell() < end:
        print(f"[0x{data.tell():08x}]  ", end="")
        op = ord(data.read(1))
        if op == 0:
            # extended
            size = read_leb128(data)
            op = ord(data.read(1))
            x = DW_LNE(op)
            if x is DW_LNE.set_address:
                sm.address = int.from_bytes(data.read(size - 1), "little")
                print(f"Extended opcode {op}: set Address to 0x{sm.address:x}")
            elif x is DW_LNE.end_sequence:
                print(f"Extended opcode {op}: End of Sequence\n")
                sm.end_sequence = True
                sm = StateMachine.New(default_is_stmt)
            elif x is DW_LNE.set_discriminator:
                sm.discriminator = read_leb128(data)
                print(
                    f"Extended opcode {op}: set Discriminator to {sm.discriminator}")
            else:
                assert False, x
        elif op < opcode_base:
            # standard
            x = DW_LNS(op)
            if x is DW_LNS.set_column:
                sm.column = read_leb128(data)
                print(f"Set column to {sm.column}")
            elif x is DW_LNS.advance_pc:
                v = read_leb128(data)
                sm.address += v
                print(f"Advance PC by {v} to 0x{sm.address:x}")
            elif x is DW_LNS.advance_line:
                v = read_leb128(data, True)
                sm.line += v
                print(f"Advance Line by {v} to {sm.line}")
            elif x is DW_LNS.copy:
                print(f"Copy")
                sm.clear()
            elif x is DW_LNS.negate_stmt:
                sm.is_stmt = not sm.is_stmt
                print(f"Set is_stmt to {int(sm.is_stmt)}")
            elif x is DW_LNS.set_file:
                sm.file = read_leb128(data)
                print(
                    f"Set File Name to entry {sm.file} in the File Name Table")
            elif x is DW_LNS.const_add_pc:
                x = 255 - opcode_base
                delta = addr_delta(255)
                sm.address += delta
                sm.clear()
                print(f"Advance PC by constant {delta} to 0x{sm.address:x}")
            else:
                assert False, x
        else:
            # special
            ad = addr_delta(op)
            sm.address += ad
            ld = line_base + (op - opcode_base) % line_range
            sm.line += ld
            sm.clear()
            print(f"Special opcode {op - opcode_base}: advance Address by {ad} to 0x{sm.address:x} "
                  f"and Line by {ld} to {sm.line}")


@dataclasses.dataclass
class DebugLineHeader:
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
            DebugLineHeader.FORMAT, data.read(DebugLineHeader.SIZE))

        self.opcode_base = ord(data.read(1))
        self.std_opcode_lengths = list(data.read(self.opcode_base - 1))
        #
        self.directory_entry_format, self.directories = ReadEntryList(data)
        self.file_name_entry_format, self.file_names = ReadEntryList(data)
        self.commands = ReadCommands(start + 4 + self.length,
                                     data, self.default_is_stmt, self.opcode_base, self.line_base, self.line_range,
                                     self.min_instruction_length, self.maximum_operations_per_instruction)
        #print(orig_size, len(data))


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
    header = DebugLineHeader()
    data = io.BytesIO(sec_line.data)
    while data.tell() < len(sec_line.data):
        # print ("@@@@@@@@")
        header.unpack(data)
    # print(header)
