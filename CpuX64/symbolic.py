"""
This module contains code for (un-)symbolizing the X64 ISA operands
"""

from typing import List, Tuple
import struct

from Elf import enum_tab
from CpuX64 import opcode_tab as x64
from Util import parse

OK = x64.OK


def InsSymbolizeObjdumpCompat(ins: x64.Ins, skip_implicit) -> Tuple[str, List[str]]:
    assert len(ins.operands) == len(ins.opcode.fields)
    is_lea = ins.opcode.name.startswith("lea")

    def EmitMemSize():
        if not is_lea:
            w = x64.FindSpecificOpWidth("M", ins.opcode.operands, ins.opcode.format)
            out.append(f"MEM{w}")

    out = []
    for n, o in enumerate(ins.opcode.fields):
        if isinstance(o, str):
            if not skip_implicit:
                out.append(o)
            continue

        val = ins.operands[n]
        assert isinstance(o, OK), f"unexpected {o} {type(o)}"
        if o in {OK.MODRM_RM_REG8, OK.MODRM_RM_REG16, OK.MODRM_RM_REG32, OK.MODRM_RM_REG64}:
            bw = 8 << (o - OK.MODRM_RM_REG8)
            out.append(x64.REG_NAMES[bw][val])
        elif o in {OK.MODRM_RM_XREG32, OK.MODRM_RM_XREG64, OK.MODRM_RM_XREG128}:
            out.append(x64.XREG_NAMES[val])
        elif o is OK.MODRM_RM_BASE:
            EmitMemSize()
            out.append(x64.REG_NAMES[64][val])  # assumes no add override
        elif o in {OK.MODRM_REG8, OK.MODRM_REG16, OK.MODRM_REG32, OK.MODRM_REG64}:
            bw = 8 << (o - OK.MODRM_REG8)
            out.append(x64.REG_NAMES[bw][val])
        elif o in {OK.MODRM_XREG32, OK.MODRM_XREG64, OK.MODRM_XREG128}:
            out.append(x64.XREG_NAMES[val])
        elif o is OK.RIP_BASE:
            EmitMemSize()
            out.append("rip")
        elif o is OK.SIB_BASE:
            EmitMemSize()
            rindex = ins.operands[n + 1]
            if rindex == 4:
                out.append(x64.REG_NAMES[64][val])  # assumes no add override
            else:
                out.append(x64.REG_NAMES[64][val])  # assumes no add override
                out.append(x64.REG_NAMES[64][rindex])  # assumes no add override
                out.append(str(1 << ins.operands[n + 2]))
        elif o is OK.SIB_INDEX_AS_BASE:
            EmitMemSize()
            # TODO: handle special case where rindex == sp
            out.append(x64.REG_NAMES[64][val])  # assumes no add override
            out.append(str(1 << ins.operands[n + 1]))
        elif o is OK.SIB_INDEX:
            pass
        elif o is OK.SIB_SCALE:
            pass
        elif o in {OK.BYTE_WITH_REG8, OK.BYTE_WITH_REG16, OK.BYTE_WITH_REG32,
                   OK.BYTE_WITH_REG64}:
            bw = 8 << (o - OK.BYTE_WITH_REG8)
            out.append(x64.REG_NAMES[bw][val])
        elif o in x64.IMM_TO_SIZE:
            _, bw = x64.IMM_TO_SIZE[o]
            mask = (1 << bw) - 1
            out.append(f"0x{val & mask:x}")
        elif o in x64.OFF_TO_SIZE:
            out.append(f"0x{val:x}")
        else:
            assert False, f"Unsupported field {o}"
    return ins.opcode.name, out
