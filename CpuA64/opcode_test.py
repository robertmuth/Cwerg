#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import re
import sys
import collections
from typing import List, Dict

from CpuA64.opcode_tab import OK, Opcode, OPC_FLAG, CONDITION_CODES_INV_MAP

from CpuA64 import disass

SIMPLE_ALIASES = {
    ("asr", "asrv"),
    ("lsr", "lsrv"),
    ("lsl", "lslv"),
    ("ror", "rorv"),

    # will be handled by OperandsMatch(
    ("mov", "movn"),
    ("mov", "movz"),

    # cwerg specific aliases
    ("ldr", "fldr"),
    ("str", "fstr"),
    ("ldur", "fldur"),
    ("stur", "fstur"),
    ("ldp", "fldp"),
    ("stp", "fstp"),
    #
    ("ldrh", "ldr"),
    ("strh", "str"),
    ("ldurh", "ldur"),
    ("sturh", "stur"),
    ("ldpsw", "ldp"),
    ("ldarh", "ldar"),
    ("stlrh", "stlr"),
    ("ldaxrh", "ldaxr"),
    ("ldxrh", "ldxr"),
    ("stlxrh", "stlxr"),
    ("ldrb", "ldr"),
    ("strb", "str"),
    ("stxrh", "stxr"),
    ("ldurb", "ldur"),
    ("sturb", "stur"),
    ("ldarb", "ldar"),
    ("stlrb", "stlr"),
    ("ldaxrb", "ldaxr"),
    ("ldxrb", "ldxr"),
    ("stxrb", "stxr"),
    ("stlxrb", "stlxr"),
}

COMPLEX_ALIASES = {
    ("cmn", "adds"),
    ("cmp", "subs"),
    ("neg", "sub"),
    ("negs", "subs"),
    ("ngcs", "sbcs"),
    ("cneg", "csneg"),
    ("cinc", "csinc"),
    ("cset", "csinc"),
    ("cinv", "csinv"),
    ("csetm", "csinv"),
    #
    ("tst", "ands"),
    ("mov", "orr"),
    ("mov", "add"),
    ("mvn", "orn"),
    ("mul", "madd"),
    ("mneg", "msub"),
    #
    ("lsl", "ubfm"),
    ("lsr", "ubfm"),
    ("asr", "sbfm"),
    ("ror", "extr"),
    ("ubfiz", "ubfm"),
    ("ubfx", "ubfm"),
    ("sbfx", "sbfm"),
    ("sxtb", "sbfm"),
    ("sxth", "sbfm"),
    ("sxtw", "sbfm"),
    ("sbfiz", "sbfm"),
    ("bfxil", "bfm"),
    ("bfi", "bfm"),
    ("bfc", "bfm"),
    #
    ("smull", "smaddl"),
    ("umull", "umaddl"),
}


def OperandsMatch(opcode: Opcode, std_ops: List[str], objdump_ops: List[str]) -> bool:
    if std_ops == objdump_ops: return True
    j = 0
    for i, op in enumerate(std_ops):
        if j < len(objdump_ops) and op == objdump_ops[j]:
            j += 1
        elif opcode.fields[i] in {OK.SIMM_PCREL_0_25, OK.SIMM_PCREL_5_18,
                                  OK.SIMM_PCREL_5_23, OK.SIMM_PCREL_5_23_29_30}:
            j += 1
        elif op == "lsl" or op == "#0" or op == "lr":
            pass
        elif opcode.fields[i] == OK.FLT_13_20:
            return float(op[1:]) == float(objdump_ops[j][1:])
        elif opcode.fields[i] in {OK.IMM_SHIFTED_5_20_21_22, OK.IMM_10_21_22}:  # movz etc
            v = int(objdump_ops[j][1:], 0)
            if opcode.name == "movn":
                bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
                return int(op[1:], 0) ^ v == (1 << bits) - 1
            if objdump_ops[j + 1] != "lsl":
                return False
            shift = int(objdump_ops[j + 2][1:], 0)
            if v << shift != int(op[1:], 0):
                print(f"@@ {v:x}  {shift:x}")
                return False
            j += 3
        else:
            print(f"Operand mismatch {opcode.fields[i].name}: {op} vs  {objdump_ops[j]}")
            return False

    return j == len(objdump_ops) or opcode.fields[-1] == OK.IMM_SHIFTED_5_20_21_22


def HandleAliasMassaging(name, opcode, operands):
    """A bunch of a hacks to deal with the ton of alias that arm64 defines"""
    if ((name == "cneg" and opcode.name == "csneg") or
            (name == "cinv" and opcode.name == "csinv") or
            (name == "cinc" and opcode.name == "csinc")):
        operands.insert(1, operands[1])
        operands[3] = CONDITION_CODES_INV_MAP[operands[3]]
    elif ((name == "csetm" and opcode.name == "csinv") or
          (name == "cset" and opcode.name == "csinc")):
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        operands[3] = CONDITION_CODES_INV_MAP[operands[3]]
    elif name == "sxtb" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#7"]
    elif name == "sxth" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#15"]
    elif name == "sxtw" and opcode.name == "sbfm":
        operands[1] = operands[0][0] + operands[1][1:]
        operands += ["#0", "#31"]
    elif name == "bfc" and opcode.name == "bfm":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
        width = int(operands[3][1:])
        operands[3] = f"#{width - 1}"
    elif ((name == "bfi" and opcode.name == "bfm") or
          (name == "sbfiz" and opcode.name == "sbfm") or
          (name == "ubfiz" and opcode.name == "ubfm")):
        lsb = int(operands[2][1:])
        width = int(operands[3][1:])
        bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
        operands[2] = f"#{bits - lsb}"
        operands[3] = f"#{width - 1}"
    elif ((name == "bfxil" and opcode.name == "bfm") or
          (name == "ubfx" and opcode.name == "ubfm") or
          (name == "sbfx" and opcode.name == "sbfm")):
        lsb = int(operands[2][1:])
        width = int(operands[3][1:])
        operands[3] = f"#{lsb + width - 1}"
    elif name == "lsl" and opcode.name == "ubfm":
        lsb = int(operands[2][1:])
        bits = 64 if opcode.fields[0] == OK.XREG_0_4 else 32
        operands[2] = f"#{bits - lsb}"
        operands.append(f"#{bits - lsb - 1}")
    #
    elif name == "tst" and opcode.name == "ands":
        operands.insert(0, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    elif name == "cmp" and opcode.name == "subs":
        operands.insert(0, "xzr" if opcode.fields[0] in {OK.XREG_0_4, OK.XREG_0_4_SP} else "wzr")
    elif name == "cmn" and opcode.name == "adds":
        operands.insert(0, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    #
    elif name == "neg" and opcode.name == "sub":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    elif name == "negs" and opcode.name == "subs":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    elif name == "ngcs" and opcode.name == "sbcs":
        operands.insert(1, "xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    elif name == "mov" and opcode.name == "orr":
        operands.insert(1, "xzr" if opcode.fields[1] == OK.XREG_5_9 else "wzr")
    elif name == "mvn" and opcode.name == "orn":
        operands.insert(1, "xzr" if opcode.fields[1] == OK.XREG_5_9 else "wzr")
    #
    elif name == "mul" and opcode.name == "madd":
        operands.append("xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    elif name == "mneg" and opcode.name == "msub":
        operands.append("xzr" if opcode.fields[0] == OK.XREG_0_4 else "wzr")
    #
    elif name == "asr" and opcode.name == "sbfm":
        operands.append("#63" if opcode.fields[0] == OK.XREG_0_4 else "#31")
    elif name == "lsr" and opcode.name == "ubfm":
        operands.append("#63" if opcode.fields[0] == OK.XREG_0_4 else "#31")
    #
    elif name == "umull" and opcode.name == "umaddl":
        operands.append("xzr")
    elif name == "smull" and opcode.name == "smaddl":
        operands.append("xzr")
    elif name == "ror" and opcode.name == "extr":
        operands.insert(1, operands[1])
    elif name == "mov" and opcode.name == "add":
        operands.append("#0x0")
    else:
        assert False


def MassageOperands(name, opcode, operands):
    """Deal with aliases and case were we deviate from std notation"""
    if OPC_FLAG.STORE in opcode.classes:
        if OPC_FLAG.ATOMIC_WITH_STATUS in opcode.classes:
            operands.append(operands.pop(1))
        else:
            operands.append(operands.pop(0))
        if OPC_FLAG.REG_PAIR in opcode.classes:
            operands.append(operands.pop(0))

    if name != opcode.name:
        if (name, opcode.name) in SIMPLE_ALIASES:
            name = opcode.name
        elif (name, opcode.name) in COMPLEX_ALIASES:
            HandleAliasMassaging(name, opcode, operands)
            name = opcode.name
    assert name == opcode.name
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


def HandleOneInstruction(count: int, line: str,
                         data: int, opcode: Opcode,
                         actual_name: str, actual_ops: List[str]):
    actual_name = MassageOperands(actual_name, opcode, actual_ops)
    ops_raw = opcode.DisassembleOperands(data)
    ops = [disass.DecodeOperand(f, op) for op, f in zip(ops_raw, opcode.fields)]
    assert OperandsMatch(opcode, ops,
                         actual_ops), f"[{opcode.name} {opcode.variant}] mismatch in [{count}]:  {ops} vs {actual_ops}: {line}"
    data2 = opcode.AssembleOperands(ops_raw)
    assert data == data2


def main(argv):
    HISTOGRAM = {}

    for name in Opcode.name_to_opcode.keys():
        HISTOGRAM[name] = 0

    for fn in argv:
        with open(fn) as fp:
            # actual_XXX: derived from the text assembler listing
            # expected_XXX: derived from decoding the `data`
            count = 0
            for line in fp:
                count += 1
                token = line.split(None, 2)
                if not token or token[0].startswith("#"):
                    continue
                data = int(token[0], 16)
                opcode = Opcode.FindOpcode(data)
                assert opcode, f"cannot find opcode: {line}"
                HISTOGRAM[opcode.NameForEnum()] += 1
                actual_name = token[1]
                actual_ops = []
                if len(token) == 3:
                    ops_str = token[2]
                    ops_str = ops_str.split("//")[0]
                    actual_ops = [x for x in re.split("[, \t\n\[\]!]+", ops_str) if x]
                # print (actual_name, actual_ops)
                HandleOneInstruction(
                    count, line, data, opcode, actual_name, actual_ops)
    # for name, count in sorted(HISTOGRAM.items()):
    #    print (f"{name:20s} {count}")
    print("OK")


if __name__ == "__main__":
    if False:
        import cProfile
        import pstats

        cProfile.run("main(sys.argv[1:])", sort=pstats.SortKey.CUMULATIVE)
    else:
        main(sys.argv[1:])
