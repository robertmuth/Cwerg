"""
This module contains code for (un-)symbolizing the a64 ISA operands
"""
from typing import Any, Dict, List, Tuple
import struct

from Elf import enum_tab
from CpuA64 import opcode_tab as a64
from Util import  parse


def SymbolizeOperand(ok: a64.OK, data: int) -> str:
    t = a64.FIELD_DETAILS.get(ok)
    assert t is not None, f"NYI: {ok}"
    data = a64.DecodeOperand(ok, data)
    if t.kind == a64.FK.LIST:
        return t.names[data]
    elif t.kind == a64.FK.FLT_CUSTOM:
        # we only care about the float aspect
        data = parse.Flt64FromBits(data)
        return str(data)
    elif t.kind == a64.FK.INT_SIGNED:
        # we only care about the signed aspect
        if data >= 1 << 63:
            data -= (1 << 64)
        return str(data)
    elif t.kind == a64.FK.INT_HEX or t.kind == a64.FK.INT_HEX_CUSTOM:
        return hex(data)
    else:
        return str(data)


def _FloatTo64BitRepresentation(num: float) -> int:
    b = struct.pack('<d', num)
    assert len(b) == 8
    return int.from_bytes(b, "little")


def UnsymbolizeOperand(ok: a64.OK, op: str) -> int:
    """
    Converts a string into and int suitable for the provided `ok`
    E.g.
    #66 -> 65
    x0 -> 0
    asr -> 2
    """
    t = a64.FIELD_DETAILS.get(ok)
    assert t is not None, f"NYI: {ok}"

    if t.kind == a64.FK.LIST:
        # assert op in t, f"{op} not in {t}"
        data = t.names.index(op)
    elif t.kind == a64.FK.FLT_CUSTOM:
        # we only care about the float aspect
        data = parse.Flt64ToBits(float(op))
    else:
        data = int(op, 0)  # skip "#", must handle "0x" prefix
        # note we intentionally allow negative numbers here
    return a64.EncodeOperand(ok, data)


_RELOC_KIND_MAP = {
    # these relocations imply that the symbol is local
    "jump26": enum_tab.RELOC_TYPE_AARCH64.JUMP26,
    "condbr19": enum_tab.RELOC_TYPE_AARCH64.CONDBR19,
    # these relocations imply that the symbol is local
    # unless prefixed with `loc_`
    "call26": enum_tab.RELOC_TYPE_AARCH64.CALL26,
    "abs32": enum_tab.RELOC_TYPE_AARCH64.ABS32,
    "abs64": enum_tab.RELOC_TYPE_AARCH64.ABS64,

    "adr_prel_pg_hi21": enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21,
    "add_abs_lo12_nc": enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC,
}

_RELOC_OK = set([
    a64.OK.SIMM_PCREL_0_25, a64.OK.SIMM_PCREL_5_23, a64.OK.SIMM_PCREL_5_23_29_30
])


def _EmitReloc(ins: a64.Ins, pos: int) -> str:
    assert False, "NYI"


def InsSymbolize(ins: a64.Ins) -> Tuple[str, List[str]]:
    """Convert all the operands in an arm.Ins to strings including relocs
    """
    ops = []
    for pos, (ok, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if (ok in _RELOC_OK and
                ins.reloc_kind != enum_tab.RELOC_TYPE_AARCH64.NONE and
                ins.reloc_pos == pos):
            ops.append(_EmitReloc(ins, pos))
        else:
            ops.append(SymbolizeOperand(ok, value))

    return ins.opcode.NameForEnum(), ops


def InsFromSymbolized(mnemonic: str, ops_str: List[str]) -> a64.Ins:
    opcode = a64.Opcode.name_to_opcode[mnemonic]
    ins = a64.Ins(opcode)
    for pos, (t, ok) in enumerate(zip(ops_str, opcode.fields)):
        if t.startswith("expr:"):
            # expr strings have the form expr:<rel-kind>:<symbol>:<addend>, e.g.:
            #   expr:movw_abs_nc:string_pointers:5
            #   expr:call:putchar
            rel_token = t.split(":")
            if len(rel_token) == 3:
                rel_token.append("0")
            assert rel_token[1] in _RELOC_KIND_MAP, f"unknown reloc kind {rel_token}"
            if rel_token[1] == "condbr19" or rel_token[1] == "jump26":
                ins.is_local_sym = True
            if rel_token[1].startswith("loc_"):
                ins.is_local_sym = True
                rel_token[1] = rel_token[1][4:]
            ins.reloc_kind = _RELOC_KIND_MAP[rel_token[1]]
            ins.reloc_pos = pos
            ins.reloc_symbol = rel_token[2]
            ins.operands.append(int(rel_token[3], 0))
        else:
            ins.operands.append(UnsymbolizeOperand(ok, t))
    return ins
