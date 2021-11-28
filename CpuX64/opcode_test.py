#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `..TestData/objdump.dis` and similar dumps obtained via `objdump`
"""

import re
import sys
import collections

from typing import List

import CpuX64.opcode_tab as x64
from CpuX64 import symbolic


def Hexify(data) -> str:
    return " ".join(f"{b:02x}" for b in data)


# This applies some massaging to simplify checking
def ExtractObjdumpOps(ops_str: str) -> List[str]:
    ops_str = ops_str.split("<")[0]
    ops_str = ops_str.replace("-0x", "+0x-")
    ops_str = ops_str.replace("XMMWORD PTR ", "MEM128,")
    ops_str = ops_str.replace("QWORD PTR ", "MEM64,")
    ops_str = ops_str.replace("DWORD PTR ", "MEM32,")
    ops_str = ops_str.replace("BYTE PTR ", "MEM8,")
    ops_str = ops_str.replace("WORD PTR ", "MEM16,")
    ops_str = ops_str.strip().replace("[", "").replace("]", "")
    return [o for o in re.split("[,+*]", ops_str) if o]


NOP = {
    "90": "xchg eax,eax",
    "66 90": "xchg ax,ax",
    "0f 1f 00": "xchg",
    "0F 1F 40 00": "xchg",
    "0f 1f 44 00 00": "xchg",
    "66 0F 1F 44 00 00": "xchg",
    "0F 1F 80 00 00 00 00": "xchg",
    "0F 1F 84 00 00 00 00 00": "xchg",
    "66 0F 1F 84 00 00 00 00 00": "xchg",
    "66 2e 0f 1f 84 00 00 00 00 00": "xchg"
}


# data must be generated with: objdump -d  -M intel  --insn-width=12
# and looks like:
# 6f03b9:	4c 03 7e e8                   	add    r15,QWORD PTR [rsi-0x18]
def ProcessObjdumpFile(fin):
    n = 0
    bad = collections.defaultdict(int)
    skipped = collections.defaultdict(int)
    mismatched = collections.defaultdict(int)
    for line in fin:
        try:
            addr_str, data_str, ins_str = line.strip().split("\t")
        except Exception as err:
            continue
        data_str = data_str.strip()
        if data_str in NOP:
            continue
        name = ins_str.split()[0]
        ops_str = ins_str[len(name):]
        # objdump use movabs to refer to 64bit immediate mov's
        if name == "movabs":
            name = "mov"
        if name not in x64.SUPPORTED_OPCODES:
            skipped[name] += 1
            continue
        # skip instructions with segments or "high" registers
        if re.search("[df]s:|[abcd]h,|,[abcd]h", ins_str):
            skipped[name] += 1
            continue

        data = [int(d, 16) for d in data_str.split()]
        if data[0] in {0x66, 0xf2, 0xf3} and (data[1] & 0xf0) == 0x40:
            data[0], data[1] = data[1], data[0]
        ins = x64.Disassemble(data)
        if not ins:
            print(f"BAD {line}", end="")
            bad[name] += 1
            continue

        data2 = x64.Assemble(ins)
        assert data == data2, f"{line}: {Hexify(data)} vs {Hexify(data2)} {ins.opcode}"

        if ins.opcode.fields == [x64.OK.OFFPCREL32] or ins.opcode.fields == [x64.OK.OFFPCREL8]:
            continue

        expected_ops = ExtractObjdumpOps(ops_str)
        # for some reason objdump suppressed the implicit operands for these
        actual_name, actual_ops = symbolic.InsSymbolizeObjdumpCompat(ins, name in {"div", "idiv", "imul"})
        if actual_name == "movq2":
            actual_name = "movq"
        assert name == actual_name
        if name == "lea" and expected_ops[-1] != actual_ops[-1]:
            assert expected_ops[-1].startswith("0xffffffff")
            v = int(expected_ops[-1][2:], 16) - (1 << 64)
            expected_ops[-1] = f"0x{v:x}"
        if expected_ops != actual_ops:
            if True:
                print(line)
                print(f"EXPECTED: {expected_ops}")
                print(f"ACTUAL:   {actual_ops}")
                print(f"OPCODE: {ins.opcode}")
                print(Hexify(ins.opcode.data))
                print(Hexify(ins.opcode.mask))
            mismatched[name] += 1
            #exit()

        n += 1
    print(f"CHECKED: {n}   BAD: {sum(bad.values())}")
    print(f"SKIPPED-TOTAL: {sum(skipped.values())}")
    if False:
        for name, count in skipped.items():
            print(f"SKIPPED: {name} {count}")
    print(f"MISMATCHED-TOTAL: {sum(mismatched.values())}")
    for name, count in mismatched.items():
        print(f"MISMATCHED: {name} {count}")
    assert sum(mismatched.values()) + sum(bad.values()) == 0


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("main(sys.argv[1:])")
    ProcessObjdumpFile(sys.stdin)
