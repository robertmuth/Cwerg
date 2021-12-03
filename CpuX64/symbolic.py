"""
This module contains code for (un-)symbolizing the X64 ISA operands
"""

from typing import List, Tuple
import struct

from Elf import enum_tab
from CpuX64 import opcode_tab as x64
from Util import parse

OK = x64.OK

SYMBOLIC_OPERAND_TO_INT = {
    "nobase": 4,
    "noindex": 4,
    "rip": 0,
}

for i, reg in enumerate(x64.XREG_NAMES):
    SYMBOLIC_OPERAND_TO_INT[reg] = i

for reglist in x64.REG_NAMES.values():
    for i, reg in enumerate(reglist):
        SYMBOLIC_OPERAND_TO_INT[reg] = i


def InsSymbolize(ins: x64.Ins) -> Tuple[str, List[str]]:
    assert len(ins.operands) == len(ins.opcode.fields)
    out = []
    for n, o in enumerate(ins.opcode.fields):
        if isinstance(o, str):
            out.append(o)
            continue

        val = ins.operands[n]
        assert isinstance(o, OK), f"unexpected {o} {type(o)}"
        if o in x64.OK_REG_TO_INFO:
            bw, kind = x64.OK_REG_TO_INFO[o]
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
            out.append(str(val))
        elif o in x64.OK_IMM_TO_SIZE:
            out.append(f"0x{val:x}")
        elif o in x64.OK_OFF_TO_SIZE:
            out.append(f"{val}")
        else:
            assert False, f"Unsupport field {o}"
    return ins.opcode.EnumName(), out


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
        if o in x64.OK_REG_TO_INFO:
            bw, kind = x64.OK_REG_TO_INFO[o]
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
        elif o in x64.OK_IMM_TO_SIZE:
            _, bw = x64.OK_IMM_TO_SIZE[o]
            mask = (1 << bw) - 1
            out.append(f"0x{val & mask:x}")
        elif o in x64.OK_OFF_TO_SIZE:
            out.append(f"0x{val:x}")
        else:
            assert False, f"Unsupported field {o}"
    return ins.opcode.name, out


def UnsymbolizeOperand(ok: x64.OK, op: str) -> int:
    """

    """

    if isinstance(ok, str):
        assert op == ok
        return 0
    assert isinstance(ok, x64.OK)
    if ok in x64.OK_REG_TO_INFO or ok in x64.OK_ADDR_REG:
        return SYMBOLIC_OPERAND_TO_INT[op]
    else:
        return int(op, 0)


_RELOC_KIND_MAP = {
    "pcrel8": (enum_tab.RELOC_TYPE_X86_64.PC8, False),
    "pcrel32": (enum_tab.RELOC_TYPE_X86_64.PC32, False),
    "loc_pcrel8": (enum_tab.RELOC_TYPE_X86_64.PC8, True),
    "loc_pcrel32": (enum_tab.RELOC_TYPE_X86_64.PC32, True),
    "abs32": (enum_tab.RELOC_TYPE_X86_64.X_32, False),
    "abs64": (enum_tab.RELOC_TYPE_X86_64.X_64, False),
}


def InsFromSymbolized(mnemonic: str, ops_str: List[str]) -> x64.Ins:
    opcode = x64.Opcode.OpcodesByName[mnemonic]
    ins = x64.Ins(opcode)
    for pos, (t, ok) in enumerate(zip(ops_str, opcode.fields)):
        if t.startswith("expr:"):
            # expr strings have the form expr:<rel-kind>:<symbol>:<addend>, e.g.:
            #   expr:movw_abs_nc:string_pointers:5
            #   expr:call:putchar
            rel_token = t.split(":")

            assert rel_token[1] in _RELOC_KIND_MAP, f"unknown reloc kind {rel_token}"
            ins.set_reloc(*_RELOC_KIND_MAP[rel_token[1]], pos, rel_token[2])

            addend = 0 if len(rel_token) == 3 else int(rel_token[3], 0)
            ins.operands.append(addend)
        else:
            ins.operands.append(UnsymbolizeOperand(ok, t))
    return ins
