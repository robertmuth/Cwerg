#!/usr/bin/python3

import sys

from CpuA32 import symbolic
import CpuA32.opcode_tab as a32


def disass(data):
    ins = a32.Disassemble(data)
    if ins.opcode is None:
        print(f"could not disassemble {data:x}")
        return
    enum_name, operands_str = symbolic.InsSymbolize(ins)

    print(f"{data:08x} {enum_name} {', '.join(operands_str)}")
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, operands_str):
        print(f"    {f.name:19s} {o_str} ({o})")
    print(f"flags: {ins.opcode.classes}")
    print()
    data2 = a32.Assemble(ins)
    assert data == data2
    ins2 = symbolic.InsFromSymbolized(enum_name, operands_str)
    assert tuple(ins.operands) == tuple(

        ins2.operands), f"{ins.operands} vs {ins2.operands}"

    # opcode.AssembleOperands(operands2)


for arg_hex_number in sys.argv[1:]:
    disass(int(arg_hex_number, 16))
