#!/usr/bin/python3

import sys

from CpuX64 import symbolic
import CpuX64.opcode_tab as x64


def disass(data):
    ins = x64.Disassemble(data)
    if ins is None:
        print(f"could not disassemble {x64.Hexify(data)}")
        return

    enum_name, ops_str = symbolic.InsSymbolize(ins)
    print(f"{x64.Hexify(data)}", f"{ins.opcode.name}.{ins.opcode.variant} {' '.join(ops_str)}")
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, ops_str):
        print(f"    {f.name:35s} {o_str:10} ({o})")
    print()
    data2 = x64.Assemble(ins)
    assert data == data2
    #ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
    #assert tuple(ins.operands) == tuple(
    #    ins2.operands), f"{ins.operands} vs {ins2.operands}"


def HexToData(s: str):
    return [int(x, 16) for x in s.split()]


def batch():
    assert False
    for line in sys.stdin:
        if not line or line.startswith("#"): continue
        data = HexToData(line.strip())
        ins = x64.Disassemble(data)
        if ins.opcode is None:
            print(f"could not disassemble [{x64.Hexify(data)}]")
            continue
        enum_name, ops_str = symbolic.InsSymbolize(ins)
        print(f"{data:08x} {enum_name}{' ' if ops_str else ''}{', '.join(ops_str)}")
        data2 = x64.Assemble(ins)
        assert data == data2
        ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
        assert tuple(ins.operands) == tuple(
            ins2.operands), f"{ins.operands} vs {ins2.operands}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            batch()
        else:
            for seq in " ".join(sys.argv[1:]).split(","):
                disass(HexToData(seq))
