"""
Convert ARM32 instruction into human readable form suitable to
be processed by an assembler.
"""

from typing import List, Tuple, Set, Dict, Any
import enum
import CpuA32.opcode_tab as a32
from Elf import enum_tab


@enum.unique
class VK(enum.Enum):
    NONE = 0
    STR = 1
    INT = 2
    INT_HEX = 3
    FLT = 4


_FORMAT_INFO: Dict[a32.OK, Any] = {
    a32.OK.Invalid: None,
    a32.OK.REG_0_3: [p.name for p in a32.REG],
    a32.OK.REG_8_11: [p.name for p in a32.REG],
    a32.OK.REG_12_15: [p.name for p in a32.REG],
    a32.OK.REG_16_19: [p.name for p in a32.REG],
    a32.OK.REG_PAIR_12_15: [p.name for p in a32.REG],
    #
    a32.OK.DREG_0_3_5: [p.name for p in a32.DREG],
    a32.OK.DREG_12_15_22: [p.name for p in a32.DREG],
    a32.OK.DREG_16_19_7: [p.name for p in a32.DREG],
    #
    a32.OK.SREG_0_3_5: [p.name for p in a32.SREG],
    a32.OK.SREG_12_15_22: [p.name for p in a32.SREG],
    a32.OK.SREG_16_19_7: [p.name for p in a32.SREG],
    #
    # Triple Format: is dec/hex, sign-bits, scale, prefix
    a32.OK.IMM_7_11: (VK.INT, ""),
    a32.OK.IMM_0_23: (VK.INT, ""),
    a32.OK.IMM_0_11_16_19: (VK.INT, ""),
    a32.OK.IMM_0_11: (VK.INT, ""),
    a32.OK.IMM_0_3_8_11: (VK.INT, ""),
    #
    a32.OK.IMM_10_11_TIMES_8: (VK.INT, ""),
    a32.OK.IMM_0_7_TIMES_4: (VK.INT, ""),
    #
    a32.OK.SIMM_0_23: (VK.INT, ""),
    #
    a32.OK.IMM_FLT_ZERO: (VK.FLT, ""),
    #
    a32.OK.IMM_0_7_8_11: (VK.INT, ""),

    #
    a32.OK.SHIFT_MODE_5_6: [p.name for p in a32.SHIFT],
    # register set
    a32.OK.REGLIST_0_15: (VK.INT_HEX, "reglist:"),
    a32.OK.REG_RANGE_0_7: (VK.INT, "regrange:"),
    a32.OK.REG_RANGE_1_7: (VK.INT, "regrange:"),
    # misc
    a32.OK.PRED_28_31: [p.name for p in a32.PRED],
}
for ok in a32.OK:
    assert ok in _FORMAT_INFO
    t = _FORMAT_INFO[ok]
    assert t is None or isinstance(t, (int, tuple, list)), f"{ok}"


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


def _SymbolizeOperand(ok: a32.OK, data: int) -> str:
    """Convert an operand in integer form as found in  arm.Ins to a string

    (This does not handle relocation expressions.)
    """
    data = a32.DecodeOperand(ok, data)
    t = _FORMAT_INFO.get(ok)
    assert t is not None, f"NYI: {ok}"
    if isinstance(t, list):
        return t[data]
    assert isinstance(t, tuple), f"{ok}: {data} {t}"
    if t[0] == VK.INT:
        return t[1] + str(data)
    elif t[0] == VK.INT_HEX:
        return t[1] + hex(data)
    elif t[0] == VK.FLT:
        return t[1] + str(data)
    else:
        assert False


_REG_REWRITES = {
    "r10": "sl",
    "r11": "fp",
    "r12": "ip",
    "r14": "lr",
}


def _UnsymbolizeOperand(ok: a32.OK, op: str) -> int:
    """Convert a symbolized operand  into an int suitable for arm.Ins

    This does not handle relocation expressions.
    """
    assert isinstance(op, str)
    t = _FORMAT_INFO.get(ok)
    assert t is not None, f"NYI: {ok}"
    if isinstance(t, list):
        op = _REG_REWRITES.get(op, op)
        return t.index(op)
    assert isinstance(t, tuple),  f"{ok} for {op} {t}"
    assert op.startswith(t[1]), f"bad prefix {op} for {ok}"
    op = op[len(t[1]):]
    if t[0] == VK.INT:
        data = int(op, 0)
    elif t[0] == VK.INT_HEX:
        data = int(op, 0)
    elif t[0] == VK.FLT:
        data = float(op)
    else:
        assert False
    return a32.EncodeOperand(ok, data)


_RELOC_KIND_MAP = {
    # these relocations imply that the symbol is local
    "jump24": enum_tab.RELOC_TYPE_ARM.JUMP24,
    # these relocations imply that the symbol is local
    # unless prefixed with `loc_`
    "abs32": enum_tab.RELOC_TYPE_ARM.ABS32,
    "call": enum_tab.RELOC_TYPE_ARM.CALL,
    "movw_abs_nc": enum_tab.RELOC_TYPE_ARM.MOVW_ABS_NC,
    "movt_abs": enum_tab.RELOC_TYPE_ARM.MOVT_ABS,
}

_RELOC_OK: Set[a32.OK] = {a32.OK.SIMM_0_23, a32.OK.IMM_0_11_16_19}


def InsSymbolize(ins: a32.Ins) -> Tuple[str, List[str]]:
    """Convert all the operands in an arm.Ins to strings including relocs
    """
    ops = []
    for pos, (ok, value) in enumerate(zip(ins.opcode.fields, ins.operands)):
        if ok in _RELOC_OK and ins.reloc_kind != 0 and ins.reloc_pos == pos:
            # Note: we essentially store the "addend" here
            ops.append(_EmitReloc(ins, pos))
        else:
            ops.append(_SymbolizeOperand(ok, value))

    return ins.opcode.NameForEnum(), ops


def InsFromSymbolized(mnemonic, token: List[str]) -> a32.Ins:
    """Takes textual form of an A32 instruction (in systematic notation) and parses it into a Ins

     * Supports relocatable expressions
     * Adds missing "al" predicate if necessary
     Example input:
     "add_regimm", ["r4", "r4", "r0", "lsl", "0"]
     """
    opcode: a32.Opcode = a32.Opcode.name_to_opcode[mnemonic]
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
            if len(rel_token) == 3:
                rel_token.append("0")
            if rel_token[1] == "jump24":
                ins.is_local_sym = True
            if rel_token[1].startswith("loc_"):
                ins.is_local_sym = True
                rel_token[1] = rel_token[1][4:]
            ins.reloc_kind = _RELOC_KIND_MAP[rel_token[1]]
            ins.reloc_pos = pos
            ins.reloc_symbol = rel_token[2]
            ins.operands.append(int(rel_token[3], 0))
        else:
            ins.operands.append(_UnsymbolizeOperand(ok, t))
    return ins
