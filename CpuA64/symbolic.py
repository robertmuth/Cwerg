"""
This module contains code for (un-)symbolizing the a64 ISA operands
"""
from typing import Any, Dict, List, Tuple

from Elf import enum_tab
from CpuA64 import opcode_tab as a64

_STRINGIFIER: Dict[a64.OK, Any] = {
    a64.OK.IMM_10_15_16_22_W: lambda x: hex(a64.DecodeLogicImmediate(x, 32)),
    a64.OK.IMM_10_15_16_22_X: lambda x: hex(a64.DecodeLogicImmediate(x, 64)),
    a64.OK.IMM_SHIFTED_5_20_21_22: lambda x: hex((x & 0xffff) << (16 * (x >> 16))),
    a64.OK.IMM_SHIFTED_10_21_22: lambda x: hex((x & 0xfff) << (12 * (x >> 12))),
    #
    a64.OK.FLT_13_20: lambda x: f"{a64.Decode8BitFlt(x):e}",
    #
    a64.OK.IMM_FLT_ZERO: lambda x: "0.0",
    a64.OK.REG_LINK: lambda x: f"lr",
    #
    a64.OK.SHIFT_15_W: ["uxtw", "sxtw"],
    a64.OK.SHIFT_15_X: ["lsl", "sxtx"],
    a64.OK.SHIFT_22_23: ["lsl", "lsr", "asr", "ror"],
    a64.OK.SHIFT_22_23_NO_ROR: ["lsl", "lsr", "asr"],
    #
    # Format: is dec/hex, sign-bits, scale
    a64.OK.IMM_5_20: (True, 0, 1),
    a64.OK.IMM_16_20: (True, 0, 1),
    a64.OK.IMM_COND_0_3: (True, 0, 1),
    a64.OK.IMM_16_21: (False, 0, 1),
    a64.OK.IMM_10_15: (False, 0, 1),
    a64.OK.IMM_10_21: (False, 0, 1),
    a64.OK.IMM_19_23_31: (False, 0, 1),
    a64.OK.IMM_10_12_LIMIT4: (False, 0, 1),
    #
    a64.OK.IMM_10_21_times_2: (False, 0, 2),
    a64.OK.IMM_10_21_times_4: (False, 0, 4),
    a64.OK.IMM_10_21_times_8: (False, 0, 8),
    a64.OK.IMM_10_21_times_16: (False, 0, 16),
    #
    a64.OK.IMM_12_MAYBE_SHIFT_0: (False, 0, 0),
    a64.OK.IMM_12_MAYBE_SHIFT_1: (False, 0, 1),
    a64.OK.IMM_12_MAYBE_SHIFT_2: (False, 0, 2),
    a64.OK.IMM_12_MAYBE_SHIFT_3: (False, 0, 3),
    a64.OK.IMM_12_MAYBE_SHIFT_4: (False, 0, 4),
    #
    a64.OK.SIMM_15_21_TIMES4: (False, 7, 4),
    a64.OK.SIMM_15_21_TIMES8: (False, 7, 8),
    a64.OK.SIMM_15_21_TIMES16: (False, 7, 16),
    a64.OK.SIMM_12_20: (False, 9, 1),
    #
    a64.OK.SIMM_PCREL_0_25: (False, 26, 1),
    a64.OK.SIMM_PCREL_5_23: (False, 19, 1),
    a64.OK.SIMM_PCREL_5_18: (False, 14, 1),
    a64.OK.SIMM_PCREL_5_23_29_30: (False, 21, 1),
}

for i in range(32):
    for ok in [a64.OK.WREG_0_4_SP, a64.OK.WREG_5_9_SP]:
        _STRINGIFIER[ok] = ["sp" if i == 31 else f"w{i}" for i in range(32)]
    for ok in [a64.OK.WREG_0_4, a64.OK.WREG_5_9, a64.OK.WREG_10_14, a64.OK.WREG_16_20]:
        _STRINGIFIER[ok] = ["wzr" if i == 31 else f"w{i}" for i in range(32)]
    for ok in [a64.OK.XREG_0_4_SP, a64.OK.XREG_5_9_SP]:
        _STRINGIFIER[ok] = ["sp" if i == 31 else f"x{i}" for i in range(32)]
    for ok in [a64.OK.XREG_0_4, a64.OK.XREG_5_9, a64.OK.XREG_10_14, a64.OK.XREG_16_20]:
        _STRINGIFIER[ok] = ["xzr" if i == 31 else f"x{i}" for i in range(32)]
    #
    for ok in [a64.OK.BREG_0_4, a64.OK.BREG_5_9, a64.OK.BREG_10_14, a64.OK.BREG_16_20]:
        _STRINGIFIER[ok] = [f"b{i}" for i in range(32)]
    for ok in [a64.OK.HREG_0_4, a64.OK.HREG_5_9, a64.OK.HREG_10_14, a64.OK.HREG_16_20]:
        _STRINGIFIER[ok] = [f"h{i}" for i in range(32)]
    for ok in [a64.OK.SREG_0_4, a64.OK.SREG_5_9, a64.OK.SREG_10_14, a64.OK.SREG_16_20]:
        _STRINGIFIER[ok] = [f"s{i}" for i in range(32)]
    for ok in [a64.OK.DREG_0_4, a64.OK.DREG_5_9, a64.OK.DREG_10_14, a64.OK.DREG_16_20]:
        _STRINGIFIER[ok] = [f"d{i}" for i in range(32)]
    for ok in [a64.OK.QREG_0_4, a64.OK.QREG_5_9, a64.OK.QREG_10_14, a64.OK.QREG_16_20]:
        _STRINGIFIER[ok] = [f"q{i}" for i in range(32)]


def SymbolizeOperand(ok: a64.OK, data: int) -> str:
    t = _STRINGIFIER.get(ok)
    if isinstance(t, list):
        return t[data]
    elif isinstance(t, tuple):
        if t[1]:
            data = a64.SignedIntFromBits(data, t[1])
        if t[0]:
            return hex(data * t[2])
        else:
            return str(data * t[2])
    else:
        return t(data)


_UNSTRINGIFIER_SYMBOL: Dict[str, int] = {}

for ok, t in _STRINGIFIER.items():
    if isinstance(t, list):
        for val, name in enumerate(t):
            val2 = _UNSTRINGIFIER_SYMBOL.get(name)
            if val2 is None:
                _UNSTRINGIFIER_SYMBOL[name] = val
            else:
                assert val == val2, f"{name}: {val} vs  {val2}"

_UNSTRINGIFIER_SYMBOL["lr"] = 30

_UNSTRINGIFIER_INT: Dict[a64.OK, Any] = {
    a64.OK.IMM_10_15_16_22_W: a64.Encode_10_15_16_22_W,
    a64.OK.IMM_10_15_16_22_X: a64.Encode_10_15_16_22_X,
    a64.OK.IMM_SHIFTED_5_20_21_22: a64.EncodeShifted_5_20_21_22,
    a64.OK.IMM_SHIFTED_10_21_22: a64.EncodeShifted_10_21_22,
}

_UNSTRINGIFIER_FLT: Dict[a64.OK, Any] = {
    a64.OK.IMM_FLT_ZERO: lambda x: 0,
    a64.OK.FLT_13_20: a64.Encode8BitFlt,
}


def UnsymbolizeOperand(ok: a64.OK, op: str) -> int:
    """
    Converts a string into and int suitable for the provided `ok`
    E.g.
    #66 -> 65
    x0 -> 0
    asr -> 2

    """
    t = _UNSTRINGIFIER_SYMBOL.get(op)
    if t is not None:
        return t

    # systematic int encodings first
    t = _STRINGIFIER.get(ok)
    if isinstance(t, tuple):
        i = int(op, 0)  # skip "#", must handle "0x" prefix
        if t[2] > 1:
            # handle scaling
            x = i // t[2]
            assert x * t[2] == i
            i = x
        if t[1] == 0:
            return i  # unsigned
        return i & ((1 << t[1]) - 1)

    # handle custom in encodings
    t = _UNSTRINGIFIER_INT.get(ok)
    if t:
        return t(int(op, 0))
    assert ok in _UNSTRINGIFIER_FLT, f"unknown operand: {ok.name} {op}"
    return _UNSTRINGIFIER_FLT[ok](float(op))


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
