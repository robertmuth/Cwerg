"""
This module contains code for (un-)symbolizing the a64 ISA operands
"""
from typing import List, Tuple
import struct

from BE.Elf import enum_tab
from BE.CpuA64 import opcode_tab as a64


def _FloatTo64BitRepresentation(num: float) -> int:
    b = struct.pack('<d', num)
    assert len(b) == 8
    return int.from_bytes(b, "little")


def _Flt64FromBits(data: int) -> float:
    return struct.unpack('<d', int.to_bytes(data, 8, "little"))[0]


def SymbolizeOperand(ok: a64.OK, data: int) -> str:
    t = a64.FIELD_DETAILS.get(ok)
    assert t is not None, f"NYI: {ok}"
    data = a64.DecodeOperand(ok, data)
    if t.kind == a64.FK.LIST:
        return t.names[data]
    elif t.kind == a64.FK.FLT_CUSTOM:
        # we only care about the float aspect
        data = _Flt64FromBits(data)
        return f"{data:g}"
    elif t.kind == a64.FK.INT_SIGNED:
        # we only care about the signed aspect
        if data >= 1 << 63:
            data -= (1 << 64)
        return str(data)
    elif t.kind == a64.FK.INT_HEX or t.kind == a64.FK.INT_HEX_CUSTOM:
        return hex(data)
    else:
        return str(data)


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
        data = _FloatTo64BitRepresentation(float(op))
    else:
        data = int(op, 0)  # skip "#", must handle "0x" prefix
        # note we intentionally allow negative numbers here
    return a64.EncodeOperand(ok, data)


_RELOC_KIND_MAP = {
    # these relocations imply that the symbol is local
    "jump26": (enum_tab.RELOC_TYPE_AARCH64.JUMP26, True),
    "condbr19": (enum_tab.RELOC_TYPE_AARCH64.CONDBR19, True),
    #
    "call26": (enum_tab.RELOC_TYPE_AARCH64.CALL26, False),
    "abs32": (enum_tab.RELOC_TYPE_AARCH64.ABS32, False),
    "abs64": (enum_tab.RELOC_TYPE_AARCH64.ABS64, False),
    "adr_prel_pg_hi21": (enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21, False),
    "add_abs_lo12_nc": (enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC, False),
    #
    "loc_call26": (enum_tab.RELOC_TYPE_AARCH64.CALL26, True),
    "loc_abs32": (enum_tab.RELOC_TYPE_AARCH64.ABS32, True),
    "loc_abs64": (enum_tab.RELOC_TYPE_AARCH64.ABS64, True),
    "loc_adr_prel_pg_hi21": (enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21, True),
    "loc_add_abs_lo12_nc": (enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC, True),
}

_RELOC_OK = {
    a64.OK.SIMM_PCREL_0_25,  # RELOC_TYPE_AARCH64.JUMP26
    a64.OK.SIMM_PCREL_5_23,
    a64.OK.SIMM_PCREL_5_23_29_30,
    a64.OK.IMM_SHIFTED_10_21_22,  # RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC
}


def _EmitReloc(ins: a64.Ins, pos: int) -> str:
    if ins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.JUMP26:
        assert ins.is_local_sym, f"expected local symbol"
        return f"expr:jump26:{ins.reloc_symbol}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.ADR_PREL_PG_HI21:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}adr_prel_pg_hi21:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.ADD_ABS_LO12_NC:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}add_abs_lo12_nc:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.CALL26:
        return f"expr:call26:{ins.reloc_symbol}"
    if ins.reloc_kind == enum_tab.RELOC_TYPE_AARCH64.CONDBR19:
        assert ins.is_local_sym, f"expected local symbol"
        return f"expr:condbr19:{ins.reloc_symbol}"
    else:
        assert False


def InsSymbolize(ins: a64.Ins) -> Tuple[str, List[str]]:
    """Convert all the operands in an arm.Ins to strings including relocs
    """
    ops = []
    for pos, (ok, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if ins.has_reloc() and ins.reloc_pos == pos:
            assert ok in _RELOC_OK
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
            assert rel_token[1] in _RELOC_KIND_MAP, f"unknown reloc kind {rel_token}"
            ins.set_reloc(*_RELOC_KIND_MAP[rel_token[1]], pos, rel_token[2])
            addend = 0 if len(rel_token) == 3 else int(rel_token[3], 0)
            ins.operands.append(addend)
        else:
            ins.operands.append(UnsymbolizeOperand(ok, t))
    return ins
