#!/usr/bin/python3


import ctypes
import mmap
import platform
import struct
import sys

from CpuA32 import symbolic as dis
from CpuA32 import opcode_tab as a32


class TestBuffer:

    def __init__(self):
        self.instructions = []

    def write(self, bs):
        self.instructions.append(bs)

    def dump(self):
        for i, bs in enumerate(self.instructions):
            print(f"{i:2d} {bs}")

    def dump_fancy(self):
        for i, bs in enumerate(self.instructions):
            data = struct.unpack("<I", bs)[0]
            ins = a32.Disassemble(data)
            _, ops = dis.InsSymbolize(ins)
            if ops and ops[0] == "al":
                ops.pop(0)
            print(
                f"{i:2d} {[f'{b:02x}' for b in bs]} {data:08x} {ins.opcode.name} {' '.join(ops)}")


def MakeBuffer(size, prot):
    buf = mmap.mmap(-1, size, prot=prot)
    void_pointer = ctypes.c_void_p.from_buffer(buf)
    return buf, ctypes.addressof(void_pointer)


def EmitNull(code_buf):
    for ins in [
        # "al" predicate is optional
        dis.InsFromSymbolized("add_imm", ["r0", "r0", "1"]),
        dis.InsFromSymbolized("mov_regimm", ["pc", "lr", "lsl", "0"])
    ]:
        code_buf.write(a32.Assemble(ins).to_bytes(4, "little"))


def EmitMul(code_buf):
    for ins in [
        # "al" predicate is optional
        dis.InsFromSymbolized("mul", ["r0", "r1", "r0"]),
        dis.InsFromSymbolized("mov_regimm", ["pc", "lr", "lsl", "0"])
    ]:
        code_buf.write(a32.Assemble(ins).to_bytes(4, "little"))


def EmitFib(code_buf):
    for ins in [
        # e92d4030 stm sp!, {r4,r5,lr}
        dis.InsFromSymbolized("stmdb_update", ["al", "sp", "reglist:16432"]),
        dis.InsFromSymbolized("cmp_imm", ["al", "r0", "1"]),
        dis.InsFromSymbolized("b", ["le", "7"]),
        dis.InsFromSymbolized("mov_imm", ["al", "r4", "0"]),
        dis.InsFromSymbolized("mov_regimm", ["al", "r5", "r0", "lsl", "0"]),
        #
        dis.InsFromSymbolized("sub_imm", ["al", "r0", "r5", "1"]),
        dis.InsFromSymbolized("bl", ["al", "-8"]),
        dis.InsFromSymbolized(
            "add_regimm", ["al", "r4", "r4", "r0", "lsl", "0"]),
        # #
        dis.InsFromSymbolized("sub_imm", ["al", "r0", "r5", "2"]),
        dis.InsFromSymbolized("bl", ["al", "-11"]),
        dis.InsFromSymbolized(
            "add_regimm", ["al", "r0", "r4", "r0", "lsl", "0"]),
        # e8bd4030 ldm sp!, {r4,r5,pc}
        dis.InsFromSymbolized("ldmia_update", ["al", "reglist:32816", "sp"]),
    ]:
        code_buf.write(a32.Assemble(ins).to_bytes(4, "little"))


def gen_code(x):
    isa = platform.machine()
    if isa != "armv7l":
        print(f"\nIncompatible machine architecture {isa}: no execution")
        return

    code_buf, code_addr = MakeBuffer(
        mmap.PAGESIZE,
        mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)

    data_buf, data_addr = MakeBuffer(
        mmap.PAGESIZE,
        mmap.PROT_READ | mmap.PROT_WRITE)

    # print(f"CODE-BUFFER: {code_buf} {code_addr:08x}")
    ftype = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
    f = ftype(code_addr)

    EmitFib(code_buf)
    print("Running Code")
    r = f(x)
    print(r)

    # del fpointer
    code_buf.close()


if len(sys.argv) > 1:
    gen_code(int(sys.argv[1]))
else:
    print("Code generator dry run - no execution")
    for snippet in [EmitNull, EmitMul, EmitFib]:
        print(f"\n{snippet.__name__}")
        test_buffer = TestBuffer()
        snippet(test_buffer)
        test_buffer.dump_fancy()
