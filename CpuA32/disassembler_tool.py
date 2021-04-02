#!/usr/bin/python3

import sys

from CpuA32 import symbolic
import CpuA32.opcode_tab as a32


def disass(data):
    ins = a32.Disassemble(data)
    if ins.opcode is None:
        print(f"could not disassemble {data:x}")
        return
    std_name = ins.opcode.name
    std_ops = [symbolic.SymbolizeOperandOfficial(ins.opcode, op, ok)
               for ok, op in zip(ins.opcode.fields, ins.operands)]

    if std_ops and std_ops[0] == "al":
        std_ops.pop(0)
    print(f"{data:08x} {std_name} {', '.join(std_ops)}")
    print("OPCODE", ins.opcode.name, ins.opcode.variant)
    enum_name, operands_str = symbolic.InsSymbolize(ins)
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, operands_str):
        print(f"    {f.name:19s} {o_str} ({o})")
    print()
    data2 = a32.Assemble(ins)
    assert data == data2
    ins2 = symbolic.InsFromSymbolized(enum_name, operands_str)
    assert tuple(ins.operands) == tuple(

        ins2.operands), f"{ins.operands} vs {ins2.operands}"

    # opcode.AssembleOperands(operands2)


for arg_hex_number in sys.argv[1:]:
    disass(int(arg_hex_number, 16))
