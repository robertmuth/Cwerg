#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import re
import sys
import collections
from typing import List, Dict

# import CpuA64.disassembler as dis
from CpuA64.opcode_tab import OK, Opcode, DecodeLogicalImmediate, SignedIntFromBits, OPC_FLAG, DecodeOperand

count_found = 0
count_total = 0
ok_histogram: Dict[OK, int] = collections.defaultdict(int)

ALIASES = {
    "cmn": {"adds"},
    "cmp": {"subs"},
    "neg": {"sub"},
    "negs": {"subs"},
    "ngcs": {"sbcs"},
    #
    "cneg": {"csneg"},
    "cinc": {"csinc"},
    "cset": {"csinc"},
    "cinv": {"csinv"},
    "csetm": {"csinv"},
    #
    "tst": {"ands"},
    "mov": {"orr", "add", "movz", "movn"},
    "mvn": {"orn"},
    "mul": {"madd"},
    "mneg": {"msub"},
    #
    "lsl": {"lslv", "lsl", "ubfm"},
    "lsr": {"lsrv", "lsr", "ubfm"},
    "asr": {"asrv", "asr", "sbfm"},
    "ror": {"rorv", "ror", "extr"},
    "ubfiz": {"ubfm"},
    "ubfx": {"ubfm"},
    "sbfx": {"sbfm"},
    "sxtb": {"sbfm"},
    "sxth": {"sbfm"},
    "sxtw": {"sbfm"},
    "sbfiz": {"sbfm"},
    "bfxil": {"bfm"},
    "bfi": {"bfm"},
    "bfc": {"bfm"},
    #
    "smull": {"smaddl"},
    "umull": {"umaddl"},
    #
    "ldr": {"ldr", "fldr"},
    "ldp": {"ldp", "fldp"},
    "ldur": {"ldur", "fldur"},
    #
    "ldurb": {"ldur"},
    "ldurh": {"ldur"},
    "ldrb": {"ldr"},
    "ldrb": {"ldr"},
    "ldrh": {"ldr"},
    "ldarb": {"ldar"},
    "ldarh": {"ldar"},
    "ldxrb": {"ldxr"},
    "ldxrh": {"ldxr"},
    "ldaxrb": {"ldaxr"},
    "ldaxrh": {"ldaxr"},
    "ldpsw": {"ldp"},

    #
    "sturb": {"stur"},
    "sturh": {"stur"},
    "strb": {"str"},
    "strh": {"str"},
    "stlxrb": {"stlxr"},
    "stlxrh": {"stlxr"},
    "stxrb": {"stxr"},
    "stxrh": {"stxr"},
    "stlrb": {"stlr"},
    "stlrh": {"stlr"},
    "stpw": {"stp"},
    #
    "str": {"str", "fstr"},
    "stp": {"stp", "fstp"},
    "stur": {"stur", "fstur"},
}

MISSED = collections.defaultdict(int)
EXAMPLE = {}


def MaybeLsl(n):
    return [] if n == 0 else ["lsl", f"#{n}"]


COND_INV = ["ne" "eq", "cc", "cs", "pl", "mi", "vc", "vs",
            "ls", "hi", "lt", "ge", "le", "gt"]


SHIFT_OPS = set(["lsl", "lsr", "asr", "ror", "uxtw", "sxtw",  "sxtx"])

SHIFT_MAP_22_23 = ["lsl", "lsr", "asr", "ror"]
SHIFT_MAP_15_W = ["uxtw", "sxtw"]
SHIFT_MAP_15_X = ["lsl", "sxtx"]

MAYBE_SHIFT_0 = [[], []]
MAYBE_SHIFT_1 = [[], "#1"]
MAYBE_SHIFT_2 = [[], "#2"]
MAYBE_SHIFT_3 = [[], "#3"]
MAYBE_SHIFT_4 = [[], "#4"]

STRIGIFIER = {
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
    #
    OK.IMM_FLT_ZERO: lambda x: "#0.0",
    OK.IMM_10_21_22: lambda x: [f"#0x{x & 0xfff:x}", "lsl", "#12"] if (x & (1 << 12)) else f"#0x{x:x}",
    OK.IMM_5_20: lambda x: f"#0x{x:x}",
    OK.IMM_16_20: lambda x: f"#0x{x:x}",
    OK.IMM_16_21: lambda x: f"#{x}",
    OK.IMM_10_15: lambda x: [] if x == 0 else f"#{x}",
    OK.IMM_10_15_16_22_W: lambda x: f"#0x{DecodeLogicalImmediate(x, 32):x}",
    OK.IMM_10_15_16_22_X: lambda x: f"#0x{DecodeLogicalImmediate(x, 64):x}",
    OK.IMM_10_12_LIMIT4: lambda x: [] if x == 0 else f"#{x}",
    OK.IMM_SHIFTED_5_20_21_22: lambda x: f"#0x{(x & 0xffff)  << ((x >> 16) * 16):x}",
    # OK.IMM_SHIFTED_5_20_21_22_NOT: lambda x: [f"#0x{x&0xffff:x}"] + MaybeLsl((x >> 16) * 16),
    OK.IMM_COND_0_3: lambda x: f"#0x{x:x}",
    #
    OK.SIMM_15_21_TIMES4: lambda x: [] if x == 0 else f"#{SignedIntFromBits(x, 7) * 4}",
    OK.SIMM_15_21_TIMES8: lambda x: [] if x == 0 else f"#{SignedIntFromBits(x, 7) * 8}",
    OK.SIMM_15_21_TIMES16: lambda x: [] if x == 0 else f"#{SignedIntFromBits(x, 7) * 16}",
    OK.IMM_10_21: lambda x: [] if x == 0 else f"#{x}",
    OK.IMM_10_21_times_2: lambda x: [] if x == 0 else f"#{x * 2}",
    OK.IMM_10_21_times_4: lambda x: [] if x == 0 else f"#{x * 4}",
    OK.IMM_10_21_times_8: lambda x: [] if x == 0 else f"#{x * 8}",
    OK.IMM_10_21_times_16: lambda x: [] if x == 0 else f"#{x * 16}",
    OK.SIMM_12_20: lambda x: [] if x == 0 else f"#{SignedIntFromBits(x, 9)}",
    #
    OK.IMM_12_MAYBE_SHIFT_0: lambda x: MAYBE_SHIFT_0[x],
    OK.IMM_12_MAYBE_SHIFT_1: lambda x: MAYBE_SHIFT_1[x],
    OK.IMM_12_MAYBE_SHIFT_2: lambda x: MAYBE_SHIFT_2[x],
    OK.IMM_12_MAYBE_SHIFT_3: lambda x: MAYBE_SHIFT_3[x],
    OK.IMM_12_MAYBE_SHIFT_4: lambda x: MAYBE_SHIFT_4[x],
    #
    OK.SHIFT_22_23: lambda x: SHIFT_MAP_22_23[x],
    OK.SHIFT_22_23_NO_ROR: lambda x: SHIFT_MAP_22_23[x],
    OK.SHIFT_15_W: lambda x: SHIFT_MAP_15_W[x],
    OK.SHIFT_15_X: lambda x: SHIFT_MAP_15_X[x],
}


def OperandsMatch(opcode: Opcode, std_ops: List[str], objdump_ops: List[str]) -> bool:
    return std_ops == objdump_ops


def HandleOneInstruction(count: int, line: str,
                         data: int, opcode: Opcode,
                         actual_name: str, actual_ops: List[str]) -> int:
    global count_found, count_total, count_mismatch
    count_total += 1
    opcode = Opcode.FindOpcode(data)
    aliases = ALIASES.get(actual_name, {actual_name})
    count_found += 1
    for f in opcode.fields:
        ok_histogram[f] += 1
    assert opcode.name in aliases, f"[{opcode.name}#{opcode.variant}] vs [{actual_name}]: {line}"
    # print (line, end="")
    if (OPC_FLAG.BRANCH in opcode.classes or
            OPC_FLAG.COND_BRANCH in opcode.classes or
            OPC_FLAG.CALL in opcode.classes or
            opcode.name in {"csinc", "csneg", "csinv", "adr", "adrp",
                            "movn", "fmov", "movk", "movz"}):
        MISSED[opcode.name] += 1
        EXAMPLE[opcode.name] = line
        return 0
    # print(line, end="")

    ops = []
    for f in opcode.fields:
        op = STRIGIFIER[f](DecodeOperand(f, data))
        if isinstance(op, str):
            ops.append(op)
        elif isinstance(op, list):
            ops += op
        else:
            assert False
    assert OperandsMatch(opcode, ops, actual_ops), f"[{opcode.name} {opcode.variant}] mismatch in [{count}]:  {ops} vs {actual_ops}: {line}"
    return 1


def HandleAliasMassaging(name, opcode, operands):
    """A bunch of a hacks to deal with the ton of alias that arm64 defines"""
    if name == "sxtb" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#7"]
        return opcode.name
    if name == "sxth" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#15"]
        return opcode.name
    if name == "sxtw" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#31"]
        return opcode.name
    if name == "bfc" and opcode.name == "bfm":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        width = int(operands[3][1:])
        if width - 1:
            operands[3] = f"#{width - 1}"
        else:
            operands.pop(3)
        return opcode.name
    if ((name == "bfi" and opcode.name == "bfm") or
            (name == "sbfiz" and opcode.name == "sbfm")):
        lsb = int(operands[2][1:])
        width = int(operands[3][1:])
        bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
        operands[2] = f"#{bits - lsb}"
        if width - 1:
            operands[3] = f"#{width - 1}"
        else:
            operands.pop(3)
        return opcode.name
    if ((name == "bfxil" and opcode.name == "bfm") or
            (name == "sbfx" and opcode.name == "sbfm")):
        lsb = int(operands[2][1:])
        width = int(operands[3][1:])
        if lsb + width - 1:
            operands[3] = f"#{lsb + width - 1}"
        else:
            operands.pop(3)
        return opcode.name
    if name == "ubfiz" and opcode.name == "ubfm":
        lsb = int(operands[2][1:])
        width = int(operands[3][1:])
        bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
        operands[2] = f"#{bits - lsb}"
        if width - 1:
            operands[3] = f"#{width - 1}"
        else:
            operands.pop(3)
        return opcode.name
    if name == "ubfx" and opcode.name == "ubfm":
        x = int(operands[2][1:]) + int(operands[3][1:]) - 1
        operands[3] = f"#{x}"
        return opcode.name
    if name == "lsl" and opcode.name == "ubfm":
        lsb = int(operands[2][1:])
        bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
        operands[2] = f"#{bits - lsb}"
        if bits - lsb - 1:
            operands.append(f"#{bits - lsb - 1}")
        return opcode.name
    if name == "tst" and opcode.name == "ands":
        operands.insert(0, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "cmp" and opcode.name == "subs":
        operands.insert(0, "xzr" if opcode.fields[0] in {OK.XREG_0_4, OK.XREG_0_4_SP} else "wzr")
        return opcode.name
    if name == "cmn" and opcode.name == "adds":
        operands.insert(0, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "neg" and opcode.name == "sub":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "negs" and opcode.name == "subs":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "ngcs" and opcode.name == "sbcs":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "mul" and opcode.name == "madd":
        operands.append("xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "mneg" and opcode.name == "msub":
        operands.append("xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "asr" and opcode.name == "sbfm":
        operands.append("#63" if opcode.fields[0] == OK.XREG_0_4 else "#31")
        return opcode.name
    if name == "lsr" and opcode.name == "ubfm":
        operands.append("#63" if opcode.fields[0] == OK.XREG_0_4 else "#31")
        return opcode.name
    # if name == "lsl" and opcode.name == "ubfm":
    #        operands.append("#63" if opcode.fields[0] == OK.XREG_0_4 else "#31")
    #    return opcode.name
    if name == "umull" and opcode.name == "umaddl":
        operands.append("xzr")
        return opcode.name
    if name == "smull" and opcode.name == "smaddl":
        operands.append("xzr")
        return opcode.name
    if name == "asr" and opcode.name == "asrv":
        return opcode.name
    if name == "lsr" and opcode.name == "lsrv":
        return opcode.name
    if name == "lsl" and opcode.name == "lslv":
        return opcode.name
    if name == "ror" and opcode.name == "rorv":
        return opcode.name
    if name == "ror" and opcode.name == "extr":
        operands.insert(1, operands[1])
        return opcode.name
    if name == "mov" and opcode.name == "add":
        operands.append("#0x0")
        return opcode.name
    if name == "mov" and opcode.name == "orr":
        operands.insert(1, "xzr" if opcode.fields[1] == OK.XREG_5_9 else "wzr")
        return opcode.name
    if name == "mvn" and opcode.name == "orn":
        operands.insert(1, "xzr" if opcode.fields[1] == OK.XREG_5_9 else "wzr")
    if name == "mov" and opcode.name == "movz":
        return opcode.name
    return opcode.name
    return name


def MassageOperands(name, opcode, operands):
    """Deal with aliases and case were we deviate from std notation"""
    if OPC_FLAG.STORE in opcode.classes:
        if OPC_FLAG.ATOMIC_WITH_STATUS in opcode.classes:
            operands.append(operands.pop(1))
        else:
            operands.append(operands.pop(0))
        if OPC_FLAG.REG_PAIR in opcode.classes:
            operands.append(operands.pop(0))

    if name in ALIASES:
        name = HandleAliasMassaging(name, opcode, operands)
    if len(operands) + 2 == len(opcode.fields):
        if (len(opcode.fields) > 3 and
                opcode.fields[3] in {OK.SHIFT_22_23, OK.SHIFT_22_23_NO_ROR,
                                     OK.SHIFT_15_W, OK.SHIFT_15_X}):
            operands.insert(3, "lsl")
        if (len(opcode.fields) > 2 and
                opcode.fields[2] in {OK.SHIFT_15_W, OK.SHIFT_15_X}):
            operands.insert(2, "lsl")
    if name == "ret" and not operands:
        operands.append("x30")
        return name
    if OPC_FLAG.DOMAIN_PARAM in opcode.classes:
        if operands[-1] == opcode.variant:
            operands.pop(-1)
            return name
    if OPC_FLAG.COND_PARAM in opcode.classes:
        if opcode.variant.endswith(operands[-1]):
            operands.pop(-1)
            return name
    if OPC_FLAG.EXTENSION_PARAM in opcode.classes:
        if len(operands) == 3:
            pass
        elif opcode.variant.endswith(operands[3]) or operands[3] == "lsl":
            operands.pop(3)
            return name
    return name


def main(argv):
    for fn in argv:
        with open(fn) as fp:
            # actual_XXX: derived from the text assembler listing
            # expected_XXX: derived from decoding the `data`
            count = 0
            good = 0
            for line in fp:
                count += 1
                token = line.split(None, 2)
                if not token or token[0].startswith("#"):
                    continue
                data = int(token[0], 16)
                opcode = Opcode.FindOpcode(data)
                assert opcode, f"cannot find opcode: {line}"
                actual_name = token[1]
                actual_ops = []
                if len(token) == 3:
                    ops_str = token[2]
                    ops_str = ops_str.split("//")[0]
                    actual_ops = [x for x in re.split("[, \t\n\[\]!]+", ops_str) if x]
                actual_name = MassageOperands(actual_name, opcode, actual_ops)
                # print (actual_name, actual_ops)
                good += HandleOneInstruction(
                    count, line, data, opcode, actual_name, actual_ops)
    for k, v in sorted(MISSED.items()):
        print(f"{k:10}: {v:5}     {EXAMPLE[k]}", end="")
    print(f"found {count_found}/{count_total}   {100 * count_found / count_total:3.1f}%")
    for k in OK:
        if k not in STRIGIFIER:
            print(f"{k.name}  {ok_histogram[k]}")

    print(f"good: {good}/{count_total}   {100 * good / count_total:3.1f}% ")


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("main(sys.argv[1:])")
    main(sys.argv[1:])
