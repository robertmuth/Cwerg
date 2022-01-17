#!/usr/bin/python3

import sys

from CpuX64 import symbolic
from CpuX64 import opcode_tab as x64


def disass(data):
    ins = x64.Disassemble(data)
    if ins is None:
        print(f"could not determine opcode {x64.Hexify(data)}")
        return

    enum_name, ops_str = symbolic.InsSymbolizeObjdumpCompat(ins, False)
    print(f"{x64.Hexify(data)}", f"{ins.opcode.name}_{ins.opcode.variant} {' '.join(ops_str)}")

    enum_name, ops_str = symbolic.InsSymbolize(ins)
    print("    " + enum_name)
    for f, o, o_str in zip(ins.opcode.fields, ins.operands, ops_str):
        if isinstance(f, x64.OK):
            f = f.name
        print(f"    {f:35s} {o_str:10} (0x{o:x})")
    print()
    data2 = x64.Assemble(ins)
    assert data == data2, f"{data} vs {data2}"
    ins2 = symbolic.InsFromSymbolized(enum_name, ops_str)
    assert tuple(ins.operands) == tuple(
        ins2.operands), f"{ins.operands} vs {ins2.operands}"


def HexToData(s: str):
    return [int(x, 16) for x in s.split()]


def batch():
    for line in sys.stdin:
        line = line.split("#")[0].strip()
        if not line.strip(): continue
        data = HexToData(line.strip())
        ins = x64.Disassemble(data)
        if ins.opcode is None:
            print(f"could not determine opcode [{x64.Hexify(data)}]")
            continue
        enum_name, ops_str = symbolic.InsSymbolize(ins)
        print(f"{x64.Hexify(data)}", f"{ins.opcode.name}_{ins.opcode.variant} {' '.join(ops_str)}")

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
            for seq in sys.argv[1:]:
                disass(HexToData(seq))
