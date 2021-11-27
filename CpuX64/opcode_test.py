#!/usr/bin/python3

"""
This test checks that we can assemble and disassemble all the instructions
found in `..TestData/objdump.dis` and similar dumps obtained via `objdump`
"""

import re
import sys
import collections

from typing import List

# from CpuA32 import symbolic
import CpuX64.opcode_tab as x64


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
        opc = x64.FindMatchingOpcode(data)
        if not opc:
            print(f"BAD {line}", end="")
            bad[name] += 1
            continue

        if "[rip+" in line:
            continue

        assert name == opc.name
        if opc.fields == [x64.OK.OFFPCREL32] or opc.fields == [x64.OK.OFFPCREL8]:
            continue
        expected_ops = ExtractObjdumpOps(ops_str)
        actual_ops = opc.RenderOps(data, name in {"div", "idiv", "imul"})
        if expected_ops != actual_ops:
            if True:
                print(line)
                print(f"EXPECTED: {expected_ops}")
                print(f"ACTUAL:   {actual_ops}")
                print(f"OPCODE: {opc}")
                print(Hexify(opc.data))
                print(Hexify(opc.mask))
            mismatched[name] += 1
            # exit()

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
    assert len(sys.argv) == 2, "must specify a single input file"
    ProcessObjdumpFile(open(sys.argv[1]))
