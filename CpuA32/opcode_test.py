#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import sys
from typing import List

import CpuA32.disassembler as dis
import CpuA32.opcode_tab as arm


def FixupAliases(actual_name: str, actual_ops: List, is_multi):
    if actual_name[:3] in ["lsl", "lsr", "asr", "ror"]:
        # lsrs	r3, r3, #7  -> movs  r3, r3, lsr #7
        actual_ops[-1] = actual_name[:3] + " " + actual_ops[-1]
        return "mov" + actual_name[3:]
    if actual_name.startswith("vcmp") and "#0.0" in actual_ops:
        actual_ops[actual_ops.index("#0.0")] = "#0"
    if is_multi:
        return (actual_name.replace("ia", "")
                .replace("ib", "").replace("db", "")
                .replace("push", "stm").replace("pop", "ldm"))
    return actual_name


def OperandsDiffer(actual_operands, expected_operands):
    if len(actual_operands) != len(expected_operands):
        return True
    for n, o in enumerate(expected_operands):
        if o != actual_operands[n]:
            return True
    return False


def HandleOneInstruction(count: int, line: str,
                         data: int,
                         actual_name: str, actual_ops: List):
    is_push_pop = "push" in actual_name or "pop" in actual_name
    ins = arm.Disassemble(data)
    assert ins.opcode is not None and ins.operands is not None, f"unknown opcode {line}"
    data2 = arm.Assemble(ins)
    assert data == data2
    expected = dis.RenderInstructionStd(ins)
    token = expected.split(None, 1)
    expected_name = token[0]
    expected_ops = []
    if len(token) == 2:
        expected_ops = [o.strip() for o in token[1].split(",")]

    actual_name = FixupAliases(actual_name, actual_ops,
                               arm.OPC_FLAG.MULTIPLE in ins.opcode.classes)
    if actual_name != expected_name:
        print("BAD NAME", expected_name, actual_name, line)

    if is_push_pop:
        expected_ops.pop(0)
    if OperandsDiffer(actual_ops, expected_ops):
        print("OPERANDS differ", str(expected_ops), line)

    operands_str = dis.SymbolizeOperands(ins)
    operands2 = [dis.UnsymbolizeOperand(o) for o in operands_str]
    assert tuple(ins.operands) == tuple(operands2), f"{ins.operands} vs {operands2}"


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
                    actual_ops = [o.strip() for o in token[2].split(",")]
                HandleOneInstruction(
                    count, line, data, actual_name, actual_ops)


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("main(sys.argv[1:])")
    main(sys.argv[1:])
