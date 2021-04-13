#!/usr/bin/python3

"""
Convert A64 instructions into human readable form suitable to
be processed by an assembler.
"""

import CpuA64.opcode_tab as a64
from CpuA64 import symbolic


def handle_opcode(data):
    ins = a64.Disassemble(data)
    if ins is None:
        print(f"could not disassemble {data:x}")
        return

    enum_name, ops_str = symbolic.InsSymbolize(ins)
    print(f"{data:08x}", f"{ins.opcode.NameForEnum()} {' '.join(ops_str)}")
    print("OPCODE", ins.opcode.name, ins.opcode.variant)
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, ops_str):
        print(f"    {f.name:35s} {o_str:10} ({o})")
    print(f"flags: {ins.opcode.classes}")
    print()
    data2 = a64.Assemble(ins)
    assert data == data2
    ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
    assert tuple(ins.operands) == tuple(ins2.operands), f"{ins.operands} vs {ins2.operands}"


if __name__ == "__main__":
    import sys

    for arg_hex_number in sys.argv[1:]:
        handle_opcode(int(arg_hex_number, 16))
