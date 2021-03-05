"""
This module contains code for (un-)symbolizing the a64 ISA encodings
"""
from CpuA64.opcode_tab import OK, Opcode, DecodeLogicalImmediate, SignedIntFromBits, Decode8BitFlt

_SHIFT_MAP_22_23 = ["lsl", "lsr", "asr", "ror"]
_SHIFT_MAP_15_W = ["uxtw", "sxtw"]
_SHIFT_MAP_15_X = ["lsl", "sxtx"]

_STRINGIFIER_REG = {
    OK.WREG_0_4_SP: lambda x: "sp" if x == 31 else f"w{x}",
    OK.WREG_5_9_SP: lambda x: "sp" if x == 31 else f"w{x}",

    OK.XREG_0_4_SP: lambda x: "sp" if x == 31 else f"x{x}",
    OK.XREG_5_9_SP: lambda x: "sp" if x == 31 else f"x{x}",

    OK.WREG_0_4: lambda x: "wzr" if x == 31 else f"w{x}",
    OK.WREG_5_9: lambda x: "wzr" if x == 31 else f"w{x}",
    OK.WREG_10_14: lambda x: "wzr" if x == 31 else f"w{x}",
    OK.WREG_16_20: lambda x: "wzr" if x == 31 else f"w{x}",

    OK.XREG_0_4: lambda x: "xzr" if x == 31 else f"x{x}",
    OK.XREG_5_9: lambda x: "xzr" if x == 31 else f"x{x}",
    OK.XREG_10_14: lambda x: "xzr" if x == 31 else f"x{x}",
    OK.XREG_16_20: lambda x: "xzr" if x == 31 else f"x{x}",
    #
    OK.SREG_0_4: lambda x: f"s{x}",
    OK.SREG_5_9: lambda x: f"s{x}",
    OK.SREG_10_14: lambda x: f"s{x}",
    OK.SREG_16_20: lambda x: f"s{x}",

    OK.DREG_0_4: lambda x: f"d{x}",
    OK.DREG_5_9: lambda x: f"d{x}",
    OK.DREG_10_14: lambda x: f"d{x}",
    OK.DREG_16_20: lambda x: f"d{x}",

    OK.BREG_0_4: lambda x: f"b{x}",
    OK.BREG_5_9: lambda x: f"b{x}",
    OK.BREG_10_14: lambda x: f"b{x}",
    OK.BREG_16_20: lambda x: f"b{x}",

    OK.HREG_0_4: lambda x: f"h{x}",
    OK.HREG_5_9: lambda x: f"h{x}",
    OK.HREG_10_14: lambda x: f"h{x}",
    OK.HREG_16_20: lambda x: f"h{x}",

    OK.QREG_0_4: lambda x: f"q{x}",
    OK.QREG_5_9: lambda x: f"q{x}",
    OK.QREG_10_14: lambda x: f"q{x}",
    OK.QREG_16_20: lambda x: f"q{x}",
}


def print_dec(x):
    return "#" + str(x)


def print_hex(x):
    return "#" + hex(x)


_STRINGIFIER_DEC = {x: print_dec for x in
                    [OK.IMM_16_21, OK.IMM_10_15, OK.IMM_10_21, OK.IMM_19_23_31, OK.IMM_10_12_LIMIT4]}


_STRINGIFIER_HEX = {x: print_hex for x in
                    [OK.IMM_5_20, OK.IMM_16_20, OK.IMM_16_20, OK.IMM_COND_0_3]}

STRINGIFIER_MISC = {
    OK.IMM_10_15_16_22_W: lambda x: print_hex(DecodeLogicalImmediate(x, 32)),
    OK.IMM_10_15_16_22_X: lambda x: print_hex(DecodeLogicalImmediate(x, 64)),
    OK.IMM_SHIFTED_5_20_21_22: lambda x: print_hex((x & 0xffff) << (16 * (x >> 16))),
    OK.IMM_10_21_22: lambda x: print_hex((x & 0xfff) << (12 * (x >> 12))),
    #
    OK.IMM_10_21_times_2: lambda x: print_dec(x * 2),
    OK.IMM_10_21_times_4: lambda x: print_dec(x * 4),
    OK.IMM_10_21_times_8: lambda x: print_dec(x * 8),
    OK.IMM_10_21_times_16: lambda x: print_dec(x * 16),
    #
    OK.IMM_12_MAYBE_SHIFT_0: lambda x: print_dec(x * 0),
    OK.IMM_12_MAYBE_SHIFT_1: lambda x: print_dec(x * 1),
    OK.IMM_12_MAYBE_SHIFT_2: lambda x: print_dec(x * 2),
    OK.IMM_12_MAYBE_SHIFT_3: lambda x: print_dec(x * 3),
    OK.IMM_12_MAYBE_SHIFT_4: lambda x: print_dec(x * 4),
    #
    OK.SHIFT_22_23: lambda x: _SHIFT_MAP_22_23[x],
    OK.SHIFT_22_23_NO_ROR: lambda x: _SHIFT_MAP_22_23[x],
    OK.SHIFT_15_W: lambda x: _SHIFT_MAP_15_W[x],
    OK.SHIFT_15_X: lambda x: _SHIFT_MAP_15_X[x],
    #
    OK.FLT_13_20: lambda x: f"#{Decode8BitFlt(x):e}",
    OK.IMM_FLT_ZERO: lambda x: "#0.0",
    #
    OK.SIMM_15_21_TIMES4: lambda x: print_dec(SignedIntFromBits(x, 7) * 4),
    OK.SIMM_15_21_TIMES8: lambda x: print_dec(SignedIntFromBits(x, 7) * 8),
    OK.SIMM_15_21_TIMES16: lambda x: print_dec(SignedIntFromBits(x, 7) * 16),
    OK.SIMM_12_20: lambda x: print_dec(SignedIntFromBits(x, 9)),
    #
    OK.SIMM_PCREL_0_25: lambda x: print_dec(SignedIntFromBits(x, 26)),
    OK.SIMM_PCREL_5_23: lambda x: print_dec(SignedIntFromBits(x, 19)),
    OK.SIMM_PCREL_5_18: lambda x: print_dec(SignedIntFromBits(x, 14)),
    OK.SIMM_PCREL_5_23_29_30: lambda x: print_dec(SignedIntFromBits(x, 21)),
    #
    OK.REG_LINK: lambda x: f"lr",
}

_STRINGIFIER = {
    **_STRINGIFIER_REG,
    **STRINGIFIER_MISC,
    **_STRINGIFIER_DEC,
    **_STRINGIFIER_HEX,
}


def DecodeOperand(kind: OK, data: int) -> str:
    return _STRINGIFIER[kind](data)
