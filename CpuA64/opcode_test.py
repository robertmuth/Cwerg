#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import sys
import collections
from typing import List, Dict

# import CpuA64.disassembler as dis
import CpuA64.opcode_tab as a64

count_found = 0
count_total = 0
ok_histogram: Dict[a64.OK, int] = collections.defaultdict(int)

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

STRIGIFIER = {
    a64.OK.WREG_0_4_SP: lambda x: "sp" if x == 31 else f"w{x}",
    a64.OK.WREG_5_9_SP: lambda x: "sp" if x == 31 else f"w{x}",

    a64.OK.XREG_0_4_SP: lambda x: "sp" if x == 31 else f"x{x}",
    a64.OK.XREG_5_9_SP: lambda x: "sp" if x == 31 else f"x{x}",

    a64.OK.WREG_0_4: lambda x: "wzr" if x == 31 else f"w{x}",
    a64.OK.WREG_5_9: lambda x: "wzr" if x == 31 else f"w{x}",
    a64.OK.WREG_10_14: lambda x: "wzr" if x == 31 else f"w{x}",
    a64.OK.WREG_16_20: lambda x: "wzr" if x == 31 else f"w{x}",

    a64.OK.XREG_0_4: lambda x: "xzr" if x == 31 else f"x{x}",
    a64.OK.XREG_5_9: lambda x: "xzr" if x == 31 else f"x{x}",
    a64.OK.XREG_10_14: lambda x: "xzr" if x == 31 else f"x{x}",
    a64.OK.XREG_16_20: lambda x: "xzr" if x == 31 else f"x{x}",
    #
    a64.OK.SREG_0_4: lambda x: f"s{x}",
    a64.OK.SREG_5_9: lambda x: f"s{x}",
    a64.OK.SREG_10_14: lambda x: f"s{x}",
    a64.OK.SREG_16_20: lambda x: f"s{x}",

    a64.OK.DREG_0_4: lambda x: f"d{x}",
    a64.OK.DREG_5_9: lambda x: f"d{x}",
    a64.OK.DREG_10_14: lambda x: f"d{x}",
    a64.OK.DREG_16_20: lambda x: f"d{x}",

    a64.OK.BREG_0_4: lambda x: f"b{x}",
    a64.OK.BREG_5_9: lambda x: f"b{x}",
    a64.OK.BREG_10_14: lambda x: f"b{x}",
    a64.OK.BREG_16_20: lambda x: f"b{x}",

    a64.OK.HREG_0_4: lambda x: f"h{x}",
    a64.OK.HREG_5_9: lambda x: f"h{x}",
    a64.OK.HREG_10_14: lambda x: f"h{x}",
    a64.OK.HREG_16_20: lambda x: f"h{x}",

    a64.OK.QREG_0_4: lambda x: f"q{x}",
    a64.OK.QREG_5_9: lambda x: f"q{x}",
    a64.OK.QREG_10_14: lambda x: f"q{x}",
    a64.OK.QREG_16_20: lambda x: f"q{x}",
    #
    a64.OK.IMM_FLT_ZERO: lambda x: "#0.0",
    a64.OK.IMM_10_21_22: lambda x: [f"#0x{x & 0xfff:x}", "lsl", "#12"] if (x & (1 << 12)) else f"#0x{x:x}",
    a64.OK.IMM_5_20: lambda x: f"#0x{x:x}",
    a64.OK.IMM_16_21: lambda x: f"#{x}",
    a64.OK.IMM_10_15: lambda x: f"#{x}",

}


def IsRegOnly(opcode: a64.Opcode) -> bool:
    for f in opcode.fields:
        if f not in STRIGIFIER:
            return False
    return True


def HandleOneInstruction(count: int, line: str,
                         data: int, opcode: a64.Opcode,
                         actual_name: str, actual_ops: List[str]) -> int:
    global count_found, count_total, count_mismatch
    count_total += 1
    opcode = a64.Opcode.FindOpcode(data)
    aliases = ALIASES.get(actual_name, {actual_name})
    count_found += 1
    for f in opcode.fields:
        ok_histogram[f] += 1
    assert opcode.name in aliases, f"[{opcode.name}#{opcode.variant}] vs [{actual_name}]: {line}"
    # print (line, end="")
    if (not IsRegOnly(opcode) or
            actual_name in {"stlxr", "stxr", "stlr",
                            "stlxrb", "stlxrb", "stxrb", "stlrb",
                            "stlxrh", "stlxrh", "stxrh", "stlrh",
                            "sbfx", "sxtb", "sxth", "sxtw",
                            "sbfiz",
                            "cinc", "cset",	"bfxil", "bfi",
                            "ubfx", "ubfiz",
                            "cneg", "cinv", "csetm", "bfc",
                            "lsl"}):
        MISSED[opcode.name] += 1
        EXAMPLE[opcode.name] = line
        return 0
    # print(line, end="")

    ops = []
    for f in opcode.fields:
        op = STRIGIFIER[f](a64.DecodeOperand(f, data))
        if isinstance(op, str):
            ops.append(op)
        elif isinstance(op, list):
            ops += op
        else:
            assert False
    assert len(ops) == len(actual_ops), f"[{opcode.name}] num mismatch in {ops} vs {actual_ops}: {line}"
    assert ops == actual_ops, f"[{opcode.name}] mismatch in [{count}]:  {ops} vs {actual_ops}: {line}"
    return 1


def MassageOperands(name, opcode, operands):
    """Deal with aliases and case were we deviate from std notation"""
    if name == "ret" and not operands:
        operands.append("x30")
        return name
    if name == "cmp" and opcode.name == "subs":
        operands.insert(0, "xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "cmn" and opcode.name == "adds":
        operands.insert(0, "xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "neg" and opcode.name == "sub":
        operands.insert(1, "xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "ngcs" and opcode.name == "sbcs":
        operands.insert(1, "xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "mul" and opcode.name == "madd":
        operands.append("xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "mneg" and opcode.name == "msub":
        operands.append("xzr" if opcode.fields[0] == a64.OK.XREG_0_4 else "wzr")
        return opcode.name
    if name == "asr" and opcode.name == "sbfm":
        operands.append("#63" if opcode.fields[0] == a64.OK.XREG_0_4 else "#31")
        return opcode.name
    if name == "lsr" and opcode.name == "ubfm":
        operands.append("#63" if opcode.fields[0] == a64.OK.XREG_0_4 else "#31")
        return opcode.name
    # if name == "lsl" and opcode.name == "ubfm":
    #        operands.append("#63" if opcode.fields[0] == a64.OK.XREG_0_4 else "#31")
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
    if name == "mov":
        if opcode.name == "add":
            operands.append("#0x0")
            return "add"
    if a64.OPC_FLAG.DOMAIN_PARAM in opcode.classes:
        if operands[-1] == opcode.variant:
            operands.pop(-1)
            return name
    if a64.OPC_FLAG.COND_PARAM in opcode.classes:
        if opcode.variant.endswith(operands[-1]):
            operands.pop(-1)
            return name
    return name


def clean(op: str) -> str:
    op = op.strip()
    if op[0] == "[":
        op = op[1:]
    if op[-1] == "]":
        op = op[:-1]
    return op


def main(argv):
    for fn in argv:
        with open(fn) as fp:
            # actual_XXX: derived from the text assembler listing
            # expected_XXX: derived from decoding the `data`
            count = 0
            good = 0
            for line in fp:
                count += 1
                line = line.replace("lsl ", "lsl,")
                line = line.replace("asr ", "asr,")
                token = line.split(None, 2)
                if not token or token[0].startswith("#"):
                    continue
                data = int(token[0], 16)
                opcode = a64.Opcode.FindOpcode(data)
                assert opcode, f"cannot find opcode: {line}"
                actual_name = token[1]
                actual_ops = []
                if len(token) == 3:
                    ops_str = token[2]
                    ops_str = ops_str.split(" //")[0]
                    actual_ops = [clean(o) for o in ops_str.split(",")]
                actual_name = MassageOperands(actual_name, opcode, actual_ops)
                # print (actual_name, actual_ops)
                good += HandleOneInstruction(
                    count, line, data, opcode, actual_name, actual_ops)
    for k, v in sorted(MISSED.items()):
        print(f"{k:10}: {v:5}     {EXAMPLE[k]}", end="")
    print(f"found {count_found}/{count_total}   {100 * count_found / count_total:3.1f}%")
    for k in a64.OK:
        if k not in STRIGIFIER:
            print(f"{k.name}  {ok_histogram[k]}")

    print(f"good: {good}/{count_total}   {100 * good / count_total:3.1f}% ")


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("main(sys.argv[1:])")
    main(sys.argv[1:])
