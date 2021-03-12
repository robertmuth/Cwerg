#!/usr/bin/python3

"""
Convert A64 instructions into human readable form suitable to
be processed by an assembler.
"""

import CpuA64.opcode_tab as a64
from CpuA64 import disass


def handle_opcode(data):
    ins = a64.Disassemble(data)
    if ins.opcode is None:
        print(f"could not disassemble {data:x}")
        return
    ops_str = [disass.DecodeOperand(f, op) for op, f in
               zip(ins.operands, ins.opcode.fields)]
    print(f"{data:08x}", f"{ins.opcode.NameForEnum()} {' '.join(ops_str)}")
    print("OPCODE", ins.opcode.name, ins.opcode.variant)
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, ops_str):
        print(f"    {f.name:35s} {o_str:10} ({o})")
    print()
    data2 = a64.Assemble(ins)
    assert data == data2
    operands2 = [disass.EncodeOperand(ok, op) for ok, op in
                 zip(ins.opcode.fields, ops_str)]
    assert tuple(ins.operands) == tuple(
        operands2), f"{ins.operands} vs {operands2}"


if __name__ == "__main__":
    import sys

    for arg_hex_number in sys.argv[1:]:
        handle_opcode(int(arg_hex_number, 16))
