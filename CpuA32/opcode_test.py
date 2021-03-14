#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `arm_test.dis` and similar dumps obtained via `objdump`
"""

import sys
from typing import List

import CpuA32.disassembler as dis
import CpuA32.opcode_tab as arm


def FixupAliases(name: str, ops: List, is_multi):
    if name[:3] in ["lsl", "lsr", "asr", "ror"]:
        # lsrs	r3, r3, #7  -> movs  r3, r3, lsr #7
        ops[-1] = name[:3] + " " + ops[-1]
        return "mov" + name[3:]
    if name.startswith("vcmp") and "#0.0" in ops:
        ops[ops.index("#0.0")] = "#0"

    if is_multi:
        if "push" in name:
            name = name.replace("push", "stmdb")
            ops.insert(0, "sp!")
        elif "pop" in name:
            name = name.replace("pop", "ldmia")
            ops.insert(0, "sp!")

        start = 1 if name[0] == "v" else 0
        if name[start + 3: start + 5] not in {"ia", "ib", "da", "db"}:
            name = name[:start + 3] + "ia" + name[start + 3:]
    return name


def OperandsMatch(opcode: arm.Opcode, actual_ops: List[str], objdump_ops: List[str]) -> bool:
    return actual_ops == objdump_ops


def HandleOneInstruction(count: int, line: str,
                         data: int,
                         actual_name: str, actual_ops: List):
    ins = arm.Disassemble(data)
    assert ins is not None, f"cannot disassemble: {line}"
    assert ins.opcode is not None and ins.operands is not None, f"unknown opcode {line}"
    data2 = arm.Assemble(ins)
    assert data == data2, f"disass mismatch [{ins.opcode.NameForEnum()}] {data:x} vs {data2:x}"
    expected = dis.RenderInstructionStd(ins)
    token = expected.split(None, 1)
    expected_name = token[0]
    expected_ops = []
    if len(token) == 2:
        expected_ops = [o.strip() for o in token[1].split(",")]

    actual_name = FixupAliases(actual_name, actual_ops,
                               arm.OPC_FLAG.MULTIPLE in ins.opcode.classes)
    if actual_name != expected_name:
        print("BAD NAME", expected_name, actual_name, line, end="")

    if not OperandsMatch(ins.opcode, actual_ops, expected_ops):
        print("OPERANDS differ", str(expected_ops), line, end="")

    operands_str = dis.SymbolizeOperands(ins)
    operands2 = [dis.UnsymbolizeOperand(op) for op in operands_str]
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
