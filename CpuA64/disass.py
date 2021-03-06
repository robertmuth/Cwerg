"""
This module contains code for (un-)symbolizing the a64 ISA operands
"""
from typing import Any, Dict

from CpuA64.opcode_tab import OK, DecodeLogicalImmediate, SignedIntFromBits, Decode8BitFlt, \
    EncodeShifted_10_21_22, EncodeShifted_5_20_21_22, Encode_10_15_16_22_X, Encode_10_15_16_22_W


def print_dec(x):
    return "#" + str(x)


def print_hex(x):
    return "#" + hex(x)


_STRINGIFIER: Dict[OK, Any] = {
    OK.IMM_10_15_16_22_W: lambda x: print_hex(DecodeLogicalImmediate(x, 32)),
    OK.IMM_10_15_16_22_X: lambda x: print_hex(DecodeLogicalImmediate(x, 64)),
    OK.IMM_SHIFTED_5_20_21_22: lambda x: print_hex((x & 0xffff) << (16 * (x >> 16))),
    OK.IMM_SHIFTED_10_21_22: lambda x: print_hex((x & 0xfff) << (12 * (x >> 12))),
    #
    OK.FLT_13_20: lambda x: f"#{Decode8BitFlt(x):e}",
    #
    OK.IMM_FLT_ZERO: lambda x: "#0.0",
    OK.REG_LINK: lambda x: f"lr",
    #
    OK.SHIFT_15_W: ["uxtw", "sxtw"],
    OK.SHIFT_15_X: ["lsl", "sxtx"],
    OK.SHIFT_22_23: ["lsl", "lsr", "asr", "ror"],
    OK.SHIFT_22_23_NO_ROR: ["lsl", "lsr", "asr"],
    #
    # Format: is dec/hex, sign-bits, scale
    OK.IMM_5_20: (True, 0, 1),
    OK.IMM_16_20: (True, 0, 1),
    OK.IMM_COND_0_3: (True, 0, 1),
    OK.IMM_16_21: (False, 0, 1),
    OK.IMM_10_15: (False, 0, 1),
    OK.IMM_10_21: (False, 0, 1),
    OK.IMM_19_23_31: (False, 0, 1),
    OK.IMM_10_12_LIMIT4: (False, 0, 1),
    #
    OK.IMM_10_21_times_2: (False, 0, 2),
    OK.IMM_10_21_times_4: (False, 0, 4),
    OK.IMM_10_21_times_8: (False, 0, 8),
    OK.IMM_10_21_times_16: (False, 0, 16),
    #
    OK.IMM_12_MAYBE_SHIFT_0: (False, 0, 0),
    OK.IMM_12_MAYBE_SHIFT_1: (False, 0, 1),
    OK.IMM_12_MAYBE_SHIFT_2: (False, 0, 2),
    OK.IMM_12_MAYBE_SHIFT_3: (False, 0, 3),
    OK.IMM_12_MAYBE_SHIFT_4: (False, 0, 4),
    #
    OK.SIMM_15_21_TIMES4: (False, 7, 4),
    OK.SIMM_15_21_TIMES8: (False, 7, 8),
    OK.SIMM_15_21_TIMES16: (False, 7, 16),
    OK.SIMM_12_20: (False, 9, 1),
    #
    OK.SIMM_PCREL_0_25: (False, 26, 1),
    OK.SIMM_PCREL_5_23: (False, 19, 1),
    OK.SIMM_PCREL_5_18: (False, 14, 1),
    OK.SIMM_PCREL_5_23_29_30: (False, 21, 1),
}

for i in range(32):
    for ok in [OK.WREG_0_4_SP, OK.WREG_5_9_SP]:
        _STRINGIFIER[ok] = ["sp" if i == 31 else f"w{i}" for i in range(32)]
    for ok in [OK.WREG_0_4, OK.WREG_5_9, OK.WREG_10_14, OK.WREG_16_20]:
        _STRINGIFIER[ok] = ["wzr" if i == 31 else f"w{i}" for i in range(32)]
    for ok in [OK.XREG_0_4_SP, OK.XREG_5_9_SP]:
        _STRINGIFIER[ok] = ["sp" if i == 31 else f"x{i}" for i in range(32)]
    for ok in [OK.XREG_0_4, OK.XREG_5_9, OK.XREG_10_14, OK.XREG_16_20]:
        _STRINGIFIER[ok] = ["xzr" if i == 31 else f"x{i}" for i in range(32)]
    #
    for ok in [OK.BREG_0_4, OK.BREG_5_9, OK.BREG_10_14, OK.BREG_16_20]:
        _STRINGIFIER[ok] = [f"b{i}" for i in range(32)]
    for ok in [OK.HREG_0_4, OK.HREG_5_9, OK.HREG_10_14, OK.HREG_16_20]:
        _STRINGIFIER[ok] = [f"h{i}" for i in range(32)]
    for ok in [OK.SREG_0_4, OK.SREG_5_9, OK.SREG_10_14, OK.SREG_16_20]:
        _STRINGIFIER[ok] = [f"s{i}" for i in range(32)]
    for ok in [OK.DREG_0_4, OK.DREG_5_9, OK.DREG_10_14, OK.DREG_16_20]:
        _STRINGIFIER[ok] = [f"d{i}" for i in range(32)]
    for ok in [OK.QREG_0_4, OK.QREG_5_9, OK.QREG_10_14, OK.QREG_16_20]:
        _STRINGIFIER[ok] = [f"q{i}" for i in range(32)]


def DecodeOperand(kind: OK, data: int) -> str:
    t = _STRINGIFIER.get(kind)
    if isinstance(t, list):
        return t[data]
    elif isinstance(t, tuple):
        if t[1]:
            data = SignedIntFromBits(data, t[1])
        if t[0]:
            return "#" + hex(data * t[2])
        else:
            return "#" + str(data * t[2])
    else:
        return t(data)


_UNSTRINGIFIER_CONST: Dict[str, int] = {}

for ok, t in _STRINGIFIER.items():
    if isinstance(t, list):
        for val, name in enumerate(t):
            val2 = _UNSTRINGIFIER_CONST.get(name)
            if val2 is None:
                _UNSTRINGIFIER_CONST[name] = val
            else:
                assert val == val2, f"{name}: {val} vs  {val2}"


_UNSTRINGIFIER: Dict[OK, Any] = {
    OK.IMM_FLT_ZERO: lambda x: 0,
    OK.REG_LINK: lambda x: 0,
    OK.IMM_10_15_16_22_W: lambda x: Encode_10_15_16_22_W(int(x[1:], 0)),
    OK.IMM_10_15_16_22_X: lambda x:  Encode_10_15_16_22_X(int(x[1:], 0)),
    OK.IMM_SHIFTED_5_20_21_22: lambda x: EncodeShifted_5_20_21_22(int(x[1:], 0)),
    OK.IMM_SHIFTED_10_21_22: lambda x: EncodeShifted_10_21_22(int(x[1:], 0)),
}


def EncodeOperand(ok: OK, op: str) -> int:
    t = _STRINGIFIER.get(ok)
    if isinstance(t, list):
        if t == 31:
            pass
        return _UNSTRINGIFIER_CONST[op]
    elif isinstance(t, tuple):
        if ok in {OK.SIMM_PCREL_5_23_29_30,
                  OK.SIMM_PCREL_5_23,
                  OK.SIMM_PCREL_5_18,
                  OK.SIMM_PCREL_0_25}:  # pc rel
            return None
        i = int(op[1:], 0)  # skip "#", must handle "0x" prefix
        if t[2] > 1:
            x = i // t[2]
            assert x * t[2] == i
            i = x
        if t[1] == 0:
            return i
        return i & ((1 << t[1]) - 1)
    else:
        t = _UNSTRINGIFIER.get(ok)
        if t is None:
            return None
        return t(op)
