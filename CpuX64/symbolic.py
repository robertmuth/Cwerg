"""
This module contains code for (un-)symbolizing the X64 ISA operands
"""

from typing import List, Tuple
import struct

from Elf import enum_tab
from CpuX64 import opcode_tab as x64
from Util import parse

OK = x64.OK

REG_MAP = {
    OK.MODRM_RM_XREG32: (32, "x"),
    OK.MODRM_RM_XREG64: (64, "x"),
    OK.MODRM_RM_XREG128: (128, "x"),
    #
    OK.MODRM_RM_REG8: (8, "r"),
    OK.MODRM_RM_REG16: (16, "r"),
    OK.MODRM_RM_REG32: (32, "r"),
    OK.MODRM_RM_REG64: (64, "r"),
    #
    OK.MODRM_XREG32: (32, "x"),
    OK.MODRM_XREG64: (64, "x"),
    OK.MODRM_XREG128: (128, "x"),
    #
    OK.MODRM_REG8: (8, "r"),
    OK.MODRM_REG16: (16, "r"),
    OK.MODRM_REG32: (32, "r"),
    OK.MODRM_REG64: (64, "r"),
    #
    OK.BYTE_WITH_REG8: (8, "r"),
    OK.BYTE_WITH_REG16: (16, "r"),
    OK.BYTE_WITH_REG32: (32, "r"),
    OK.BYTE_WITH_REG64: (64, "r"),
}


def InsSymbolize(ins: x64.Ins) -> Tuple[str, List[str]]:
    assert len(ins.operands) == len(ins.opcode.fields)
    out = []
    for n, o in enumerate(ins.opcode.fields):
        if isinstance(o, str):
            out.append(o)
            continue

        val = ins.operands[n]
        assert isinstance(o, OK), f"unexpected {o} {type(o)}"
        if o in REG_MAP:
            bw, kind = REG_MAP[o]
            if kind == "r":
                out.append(x64.REG_NAMES[bw][val])
            else:
                out.append(x64.XREG_NAMES[val])
        elif o is OK.MODRM_RM_BASE:
            out.append(x64.REG_NAMES[64][val])  # assumes no address override
        elif o is OK.RIP_BASE:
            out.append("rip")
        elif o is OK.SIB_BASE:
            out.append(x64.REG_NAMES[64][val])  # assumes no address override
        elif o is OK.SIB_INDEX_AS_BASE:
            if val == 4:
                out.append("nobase")
            else:
                out.append(x64.REG_NAMES[64][val])  # assumes no add override
        elif o is OK.SIB_INDEX:
            if val == 4:
                out.append("noindex")
            else:
                out.append(x64.REG_NAMES[64][val])  # assumes no address override
        elif o is OK.SIB_SCALE:
            out.append(str(1 << val))
        elif o in x64.IMM_TO_SIZE:
            out.append(f"0x{val:x}")
        elif o in x64.OFF_TO_SIZE:
            out.append(f"0x{val:x}")
        else:
            assert False, f"Unsupport field {o}"
    return ins.opcode.name, out

def InsSymbolizeObjdumpCompat(ins: x64.Ins, skip_implicit) -> Tuple[str, List[str]]:
    assert len(ins.operands) == len(ins.opcode.fields)
    is_lea = ins.opcode.name.startswith("lea")

    def EmitMemSize():
        if not is_lea:
            w = x64.FindSpecificOpWidth("M", ins.opcode.operands, ins.opcode.format)
            out.append(f"MEM{w}")

    out = []
    skip_next = 0
    for n, o in enumerate(ins.opcode.fields):
        if skip_next > 0:
            skip_next -= 1
            continue
        if isinstance(o, str):
            if not skip_implicit:
                out.append(o)
            continue

        val = ins.operands[n]
        assert isinstance(o, OK), f"unexpected {o} {type(o)}"
        if o in REG_MAP:
            bw, kind = REG_MAP[o]
            if kind == "r":
                out.append(x64.REG_NAMES[bw][val])
            else:
                out.append(x64.XREG_NAMES[val])
        elif o is OK.MODRM_RM_BASE:
            EmitMemSize()
            out.append(x64.REG_NAMES[64][val])  # assumes no address override
        elif o is OK.RIP_BASE:
            EmitMemSize()
            out.append("rip")
        elif o is OK.SIB_BASE:
            EmitMemSize()
            out.append(x64.REG_NAMES[64][val])  # assumes no address override
        elif o is OK.SIB_INDEX_AS_BASE:
            EmitMemSize()
            # TODO: handle special case where rindex == sp
            out.append(x64.REG_NAMES[64][val])  # assumes no add override
        elif o is OK.SIB_INDEX:
            if val == 4:
                skip_next = 1
            else:
                out.append(x64.REG_NAMES[64][val])  # assumes no add override
        elif o is OK.SIB_SCALE:
            out.append(str(1 << val))
        elif o in x64.IMM_TO_SIZE:
            _, bw = x64.IMM_TO_SIZE[o]
            mask = (1 << bw) - 1
            out.append(f"0x{val & mask:x}")
        elif o in x64.OFF_TO_SIZE:
            out.append(f"0x{val:x}")
        else:
            assert False, f"Unsupported field {o}"
    return ins.opcode.name, out


_RELOC_KIND_MAP = {
    # these relocations imply that the symbol is global
    # unless prefixed with `loc_`
    "pcrel8": enum_tab.RELOC_TYPE_X86_64.PC8,
    "pcrel32": enum_tab.RELOC_TYPE_X86_64.PC32,
    "abs32": enum_tab.RELOC_TYPE_X86_64.X_32,
    "abs64": enum_tab.RELOC_TYPE_X86_64.X_64,
}
