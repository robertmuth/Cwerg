#!/usr/bin/python3

import sys

from CpuA32 import symbolic
from CpuA32 import opcode_tab as a32


def disass(data):
    ins = a32.Disassemble(data)
    if ins.opcode is None:
        print(f"could not disassemble {data:x}")
        return
    enum_name, operands_str = symbolic.InsSymbolize(ins)

    print(f"{data:08x} {enum_name} {', '.join(operands_str)}")
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, operands_str):
        print(f"    {f.name:25} {o_str:15} ({o})")
    print()
    data2 = a32.Assemble(ins)
    assert data == data2
    ins2 = symbolic.InsFromSymbolized(enum_name, operands_str)
    assert tuple(ins.operands) == tuple(
        ins2.operands), f"{ins.operands} vs {ins2.operands}"


def batch():
    for line in sys.stdin:
        if not line or line.startswith("#"): continue
        data = int(line.split()[0], 16)
        ins = a32.Disassemble(data)
        if ins.opcode is None:
            print(f"could not disassemble {data:x}")
            continue
        enum_name, ops_str = symbolic.InsSymbolize(ins)
        print(f"{data:08x} {enum_name}{' ' if ops_str else ''}{', '.join(ops_str)}")
        data2 = a32.Assemble(ins)
        assert data == data2
        ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
        assert tuple(ins.operands) == tuple(
            ins2.operands), f"{ins.operands} vs {ins2.operands}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            batch()
        else:
            for arg_hex_number in sys.argv[1:]:
                disass(int(arg_hex_number, 16))
