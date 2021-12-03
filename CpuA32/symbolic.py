"""
Convert ARM32 instruction into human readable form suitable to
be processed by an assembler.
"""

from typing import List, Tuple, Set
import struct
import CpuA32.opcode_tab as a32
from Elf import enum_tab


def _EmitReloc(ins: a32.Ins, pos: int) -> str:
    if ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.JUMP24:
        assert ins.is_local_sym, f"expected local symbol"
        return f"expr:jump24:{ins.reloc_symbol}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.MOVT_ABS:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}movt_abs:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC:
        loc = "loc_" if ins.is_local_sym else ""
        offset = "" if ins.operands[pos] == 0 else f":{ins.operands[pos]}"
        return f"expr:{loc}movw_abs_nc:{ins.reloc_symbol}{offset}"
    elif ins.reloc_kind == enum_tab.RELOC_TYPE_ARM.CALL:
        return f"expr:call:{ins.reloc_symbol}"
    else:
        assert False


def _FloatFrom32BitRepresentation(data: int) -> float:
    return struct.unpack('<f', int.to_bytes(data, 4, "little"))[0]


def _SymbolizeOperand(ok: a32.OK, data: int) -> str:
    """Convert an operand in integer form as found in  arm.Ins to a string

    (This does not handle relocation expressions.)
    """
    data = a32.DecodeOperand(ok, data)
    assert data >= 0, f"expected unsigned for {ok}: {data}"
    t = a32.FIELD_DETAILS[ok]
    if t.kind == a32.FK.LIST:
        return t.names[data]
    elif t.kind == a32.FK.FLT_CUSTOM:
        # we only care about the float aspect
        data = _FloatFrom32BitRepresentation(data)
        return str(data)
    elif t.kind == a32.FK.INT_SIGNED_CUSTOM or t.kind == a32.FK.INT_SIGNED:
        # we only care about the signed aspect
        if data >= 1 << 31:
            data -= (1 << 32)
        return str(data)
    elif t.kind == a32.FK.INT_HEX:
        return t.prefix + hex(data)
    else:
        return t.prefix + str(data)


_REG_REWRITES = {
    "r10": "sl",
    "r11": "fp",
    "r12": "ip",
    "r14": "lr",
}


def _FloatTo32BitRepresentation(num: float) -> int:
    b = struct.pack('<f', num)
    assert len(b) == 4
    return int.from_bytes(b, "little")


def _UnsymbolizeOperand(ok: a32.OK, op: str) -> int:
    """Convert a symbolized operand  into an int suitable for arm.Ins

    This does not handle relocation expressions.
    """
    t = a32.FIELD_DETAILS[ok]
    if t.prefix and op.startswith(t.prefix):
        op = op[len(t.prefix):]
    if t.kind == a32.FK.LIST:
        op = _REG_REWRITES.get(op, op)
        data = t.names.index(op)
    elif t.kind == a32.FK.FLT_CUSTOM:
        # we only care about the float aspect
        data = _FloatTo32BitRepresentation(float(op))
    elif t.kind == a32.FK.INT_SIGNED_CUSTOM or t.kind == a32.FK.INT_SIGNED:
        # we only care about the signed aspect
        data = int(op, 0)
        if data < 0:
            data += 1 << 32
    else:
        data = int(op, 0)
    assert data is not None and data >= 0, f"bad data {ok}: {op}"
    return a32.EncodeOperand(ok, data)


_RELOC_KIND_MAP = {
    "jump24": (enum_tab.RELOC_TYPE_ARM.JUMP24, True), # always local
    #
    "abs32": (enum_tab.RELOC_TYPE_ARM.ABS32, False),
    "call": (enum_tab.RELOC_TYPE_ARM.CALL, False),
    "movw_abs_nc": (enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC, False),
    "movt_abs": (enum_tab.RELOC_TYPE_ARM.MOVT_ABS, False),
    #
    "loc_abs32": (enum_tab.RELOC_TYPE_ARM.ABS32, True),
    "loc_call": (enum_tab.RELOC_TYPE_ARM.CALL, True),
    "loc_movw_abs_nc": (enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC, True),
    "loc_movt_abs": (enum_tab.RELOC_TYPE_ARM.MOVT_ABS, True),
}

_RELOC_OK: Set[a32.OK] = {a32.OK.SIMM_0_23, a32.OK.IMM_0_11_16_19}


def InsSymbolize(ins: a32.Ins) -> Tuple[str, List[str]]:
    """Convert all the operands in an arm.Ins to strings including relocs
    """
    ops = []
    for pos, (ok, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if ok in _RELOC_OK and ins.has_reloc() and ins.reloc_pos == pos:
            # Note: we essentially store the "addend" here
            ops.append(_EmitReloc(ins, pos))
        else:
            ops.append(_SymbolizeOperand(ok, value))

    return ins.opcode.name, ops


def InsFromSymbolized(mnemonic, token: List[str]) -> a32.Ins:
    """Takes textual form of an A32 instruction (in systematic notation) and parses it into a Ins

     * Supports relocatable expressions
     * Adds missing "al" predicate if necessary
     Example input:
     "add_regimm", ["r4", "r4", "r0", "lsl", "0"]
     """
    opcode: a32.Opcode = a32.Opcode.name_to_opcode[mnemonic]
    # CodeGenA32 relies on this
    if opcode.HasPred() and len(token) == len(opcode.fields) - 1:
        token = ["al"] + token
    ins = a32.Ins(opcode)
    assert len(token) == len(opcode.fields), f"expected {len(opcode.fields)} operands in {mnemonic} {token}"
    for pos, (t, ok) in enumerate(zip(token, opcode.fields)):
        if t.startswith("expr:"):
            # expr strings have the form expr:<rel-kind>:<symbol>:<addend>, e.g.:
            #   expr:movw_abs_nc:string_pointers:5
            #   expr:call:putchar
            rel_token = t.split(":")

            ins.set_reloc(*_RELOC_KIND_MAP[rel_token[1]], pos, rel_token[2])
            addend = 0 if len(rel_token) ==3 else  int(rel_token[3], 0)
            ins.operands.append(addend)
        else:
            ins.operands.append(_UnsymbolizeOperand(ok, t))
    return ins
