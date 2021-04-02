#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import re
import sys
from typing import List

from  CpuA32 import symbolic
import CpuA32.opcode_tab as a32


def FixupAliases(opcode: a32.Opcode, name: str, ops: List[str]) -> str:
    if name[:3] in ["lsl", "lsr", "asr", "ror"]:
        # lsrs	r3, r3, #7  -> movs  r3, r3, lsr #7
        ops.insert(-1, name[:3])
        return "mov" + name[3:]

    if a32.OPC_FLAG.MULTIPLE in opcode.classes:
        # unsplit '{r0', 'r1}'
        while not ops[-1].startswith("{"):
            end = ops.pop(-1)
            ops[-1] = ops[-1] + "," + end

        if "push" in name:
            ops.insert(0, "sp")
            return name.replace("push", "stmdb")
        elif "pop" in name:
            ops.append("sp")
            return name.replace("pop", "ldmia")

        start = 1 if name[0] == "v" else 0
        if name[start + 3: start + 5] not in {"ia", "ib", "da", "db"}:
            name = name[:start + 3] + "ia" + name[start + 3:]
        if name.startswith("ldm") or name.startswith("vldm"):
            loadee = ops.pop(0)
            ops.append(loadee)
        return name

    if name.startswith("strex"):
        storee = ops.pop(1)
        ops.append(storee)
    elif name.startswith("str") or name.startswith("vstr"):
        storee = ops.pop(0)
        ops.append(storee)
    return name


# range looks like: {d8-d10} or  {d1}
def _GetFirstRegFromRange(range):
    token = range[1:-1].split("-")
    assert len(token) <= 2, f"{token}"
    return token[0]


def _GetWidthFromRange(range):
    token = range[1:-1].split("-")
    if len(token) == 1:
        return 1
    assert len(token) == 2
    return 1 + int(token[1][1:]) - int(token[0][1:])


def OperandsMatch(opcode: a32.Opcode, objdump_name: str,
                  objdump_ops: List[str], std_ops: List[str]) -> bool:
    j = 0
    for i, (ok, op) in enumerate(zip(opcode.fields, std_ops)):
        if j < len(objdump_ops) and op == objdump_ops[j]:
            j += 1
        elif (ok is a32.OK.PRED_28_31 and
              op == "al" or objdump_name.endswith(op)):
            continue
        elif ok in {a32.OK.IMM_0_7_TIMES_4, a32.OK.IMM_7_11,
                    a32.OK.IMM_0_11, a32.OK.IMM_0_3_8_11,
                    a32.OK.IMM_10_11_TIMES_8} and op == "#0":
            continue
        elif op == "#0" and j < len(objdump_ops) and "#0.0" == objdump_ops[j]:
            continue
        elif ok is a32.OK.SHIFT_MODE_5_6 and op == "lsl":
            continue
        elif ok is a32.OK.REG_LINK:
            continue
        elif (a32.OPC_FLAG.MULTIPLE in opcode.classes and
              a32.OPC_FLAG.VFP in opcode.classes):
            if ok in {a32.OK.DREG_12_15_22, a32.OK.SREG_12_15_22}:
                if _GetFirstRegFromRange(objdump_ops[j]) == op:
                    continue
            elif ok in {a32.OK.REG_RANGE_0_7, a32.OK.REG_RANGE_1_7}:
                if f"#{_GetWidthFromRange(objdump_ops[j])}" == op:
                    j += 1
                    continue

            return False

        else:
            return False
    return True


def HandleOneInstruction(count: int, line: str,
                         data: int,
                         actual_name: str, actual_ops: List):
    ins = a32.Disassemble(data)
    assert ins is not None, f"cannot disassemble [{count}]: {line}"
    assert ins.opcode is not None and ins.operands is not None, f"unknown opcode {line}"
    data2 = a32.Assemble(ins)
    assert data == data2, f"disass mismatch [{ins.opcode.NameForEnum()}] {data:x} vs {data2:x}"
    actual_name = FixupAliases(ins.opcode, actual_name, actual_ops)
    if not actual_name.startswith(ins.opcode.name):
        print("BAD NAME", ins.opcode.name, actual_name, line, end="")

    expected_ops = [symbolic.SymbolizeOperandOfficial(ins.opcode, op, ok)
                    for ok, op in zip(ins.opcode.fields, ins.operands)]
    if not OperandsMatch(ins.opcode, actual_name, actual_ops, expected_ops):
        print(f"OPERANDS differ {expected_ops} {actual_ops} in line  {line}", end="")

    name, operands_str = symbolic.InsSymbolize(ins)
    ins2 = symbolic.InsFromSymbolized(name, operands_str)
    assert tuple(ins.operands) == tuple(ins2.operands), f"{ins.operands} vs {ins2.operands}"


def main(argv):
    for fn in argv:
        with open(fn) as fp:
            # actual_XXX: derived from the text assembler listing
            # expected_XXX: derived from decoding the `data`
            count = 0
            for line in fp:
                count += 1
                token = line.split(None, 2)
                data = int(token[0], 16)
                actual_name = token[1]
                actual_ops = []
                if len(token) == 3:
                    # Note this removes all the address mode syntax
                    # so we lose a bit of fidelity
                    actual_ops = [x for x in re.split("[, \t\n\[\]!]+", token[2]) if x]
                HandleOneInstruction(
                    count, line, data, actual_name, actual_ops)


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("main(sys.argv[1:])")
    main(sys.argv[1:])
