"""
This module contains code for (un-)symbolizing the X64 ISA operands
"""

from typing import List, Tuple

from BE.Elf import enum_tab
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


def SymbolizeReloc(ins: x64.Ins, addend: int) -> str:
    if ins.reloc_kind == enum_tab.RELOC_TYPE_X86_64.PC32:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if addend == 0 else f":{addend}"
        return f"expr:{loc}pcrel32:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_X86_64.X_64:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if addend == 0 else f":{addend}"
        return f"expr:{loc}abs64:{ins.reloc_symbol}{offset}"
    else:
        assert False


def SymbolizeOperand(ok: OK, val: int, show_implicits: bool, objdump_compat) -> str:
    if ok in x64.OK_TO_IMPLICIT:
        if show_implicits:
            return x64.OK_TO_IMPLICIT[ok]
        else:
            return None
    elif ok in x64.OK_REG_TO_INFO:
        bw, kind = x64.OK_REG_TO_INFO[ok]
        if kind == "r":
            return x64.REG_NAMES[bw][val]
        else:
            return x64.XREG_NAMES[val]
    elif ok is OK.MODRM_RM_BASE:
        return x64.REG_NAMES[64][val]  # assumes no address override
    elif ok is OK.RIP_BASE:
        return "rip"
    elif ok is OK.SIB_BASE:
        return x64.REG_NAMES[64][val]  # assumes no address override
    elif ok is OK.SIB_INDEX_AS_BASE:
        if val == 4:
            return "nobase"
        else:
            return x64.REG_NAMES[64][val]  # assumes no add override
    elif ok is OK.SIB_INDEX:
        if val == 4:
            return "noindex"
        else:
            return x64.REG_NAMES[64][val]  # assumes no address override
    elif ok is OK.SIB_SCALE:
        if objdump_compat:
            return str(1 << val)
        return str(val)
    elif ok in x64.OK_IMM_TO_SIZE:
        if val >= 1 << 63:
            val = -((1 << 64) - val)
        if val >= 0:
            return f"0x{val:x}"
        else:
            return f"-0x{-val:x}"
        #return f"0x{val:x}"
    elif ok in x64.OK_OFF_TO_SIZE:
        if objdump_compat:
            if val >= 0:
                return f"0x{val:x}"
            else:
                return f"-0x{-val:x}"
        return str(val)
    else:
        assert False, f"Unsupported field {ok}"


def InsSymbolize(ins: x64.Ins, show_implicits: bool, objdump_compat: bool = False) -> Tuple[str, List[str]]:
    assert len(ins.operands) == len(ins.opcode.fields)
    skip_next = 0
    out = []
    for n, ok in enumerate(ins.opcode.fields):
        if skip_next:
            skip_next = False
            continue

        if objdump_compat and ok is OK.SIB_INDEX and ins.operands[n] == 4:
            skip_next = True
            continue

        if objdump_compat and ok in {OK.MODRM_RM_BASE, OK.RIP_BASE, OK.SIB_BASE, OK.SIB_INDEX_AS_BASE}:
            if ins.opcode.mem_width:
                out.append(f"MEM{ins.opcode.mem_width}")

        if ins.has_reloc() and ins.reloc_pos == n:
            out.append(SymbolizeReloc(ins, ins.operands[n]))
            continue
        s = SymbolizeOperand(ok, ins.operands[n], show_implicits, objdump_compat)
        if s is not None:
            out.append(s)

    if objdump_compat:
        return ins.opcode.name, out
    return ins.opcode.EnumName(), out


def UnsymbolizeOperand(ok: x64.OK, op: str) -> int:
    """

    """

    assert isinstance(ok, x64.OK)
    if ok in x64.OK_REG_TO_INFO or ok in x64.OK_ADDR_REG:
        return SYMBOLIC_OPERAND_TO_INT[op]
    elif ok in x64.OK_TO_IMPLICIT:
        return 0
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
    opcode = x64.Opcode.name_to_opcode[mnemonic]
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
