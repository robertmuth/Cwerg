#!/usr/bin/python3

import sys

from CpuA64 import symbolic
from CpuA64 import opcode_tab as a64


def disass(data):
    ins = a64.Disassemble(data)
    if ins is None:
        print(f"could not disassemble {data:x}")
        return

    enum_name, ops_str = symbolic.InsSymbolize(ins)
    print(f"{data:08x}", f"{ins.opcode.NameForEnum()} {' '.join(ops_str)}")
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, ops_str):
        print(f"    {f.name:35s} {o_str:10} ({o})")
    # print(f"flags: {ins.opcode.classes}")
    print()
    data2 = a64.Assemble(ins)
    assert data == data2
    ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
    assert tuple(ins.operands) == tuple(
        ins2.operands), f"{ins.operands} vs {ins2.operands}"


def batch():
    for line in sys.stdin:
        if not line or line.startswith("#"): continue
        data = int(line.split()[0], 16)
        ins = a64.Disassemble(data)
        if ins.opcode is None:
            print(f"could not disassemble {data:x}")
            continue
        enum_name, ops_str = symbolic.InsSymbolize(ins)
        print(f"{data:08x} {enum_name}{' ' if ops_str else ''}{', '.join(ops_str)}")
        data2 = a64.Assemble(ins)
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
