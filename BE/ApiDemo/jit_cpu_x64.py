#!/usr/bin/python3


import ctypes
import mmap
import platform
import sys

from typing import List

from BE.CpuX64 import symbolic as dis
from BE.CpuX64 import opcode_tab as x64


class TestBuffer:

    def __init__(self):
        self.instructions = b""

    def write(self, bs: bytes):
        self.instructions += bs

    def dump(self):
        for i, bs in enumerate(self.instructions):
            print(f"{i:2d} {bs}")

    def dump_fancy(self):
        data = self.instructions
        off = 0
        while off < len(data):
            ins = x64.Disassemble(list(data[off:]))
            opcode_name, ops_str = dis.InsSymbolize(ins, True)
            print(f"0x{off:02x} {opcode_name} {' '.join(ops_str)}")
            off += x64.InsLength(ins)


def MakeBuffer(size, prot):
    buf = mmap.mmap(-1, size, prot=prot)
    void_pointer = ctypes.c_void_p.from_buffer(buf)
    return buf, ctypes.addressof(void_pointer)


def EmitNull(code_buf):
    for ins in [
        # "al" predicate is optional
        dis.InsFromSymbolized("ret", []),
    ]:
        code_buf.write(bytes(x64.Assemble(ins)))


def EmitFib(code_buf):
    INS: List[x64.Ins] = [
        # 0
        dis.InsFromSymbolized("push_64_r", ["r14"]),
        dis.InsFromSymbolized("push_64_r", ["rbx"]),
        dis.InsFromSymbolized("push_64_r", ["rbx"]),
        dis.InsFromSymbolized("cmp_64_mr_imm8", ["rdi", "2"]),
        dis.InsFromSymbolized("jb_8", ["0"]),  # patch me at 4
        #5
        dis.InsFromSymbolized("mov_64_mr_r", ["rbx", "rdi"]),
        dis.InsFromSymbolized("xor_32_mr_r", ["r14", "r14"]),
        dis.InsFromSymbolized("sub_64_mr_imm8", ["rdi", "1"]),
        dis.InsFromSymbolized("call_32", ["0"]),  # patch me at 8
        dis.InsFromSymbolized("add_64_mr_r", ["r14", "rax"]),
        #10
        dis.InsFromSymbolized("mov_64_mr_r", ["rdi", "rbx"]),
        dis.InsFromSymbolized("sub_64_mr_imm8", ["rdi", "2"]),
        dis.InsFromSymbolized("call_32", ["0"]), # patch me at 12
        dis.InsFromSymbolized("add_64_mr_r", ["r14", "rax"]),
        dis.InsFromSymbolized("mov_64_mr_r", ["rdi", "r14"]),
        #15
        dis.InsFromSymbolized("mov_64_mr_r", ["rax", "rdi"]),
        dis.InsFromSymbolized("pop_64_r", ["rbx"]),
        dis.InsFromSymbolized("pop_64_r", ["rbx"]),
        dis.InsFromSymbolized("pop_64_r", ["r14"]),
        dis.InsFromSymbolized("ret", []),
    ]

    LENGTH = [x64.InsLength(i) for  i in INS]

    def pcoffset(src: int, dst: int) -> int:
        out = 0;
        while src < dst:
            out += LENGTH[src]
            src += 1
        return out;

    # patching of branch offsets
    INS[4].operands[0] = pcoffset(5, 15)
    INS[8].operands[0] = -pcoffset(0, 9)
    INS[12].operands[0] = -pcoffset(0, 13)

    for ins in INS:
        code_buf.write(bytes(x64.Assemble(ins)))


def gen_code(x):
    isa = platform.machine()
    if isa != "x86_64":
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
    for snippet in [EmitNull, EmitFib]:
        print(f"\n{snippet.__name__}")
        test_buffer = TestBuffer()
        snippet(test_buffer)
        test_buffer.dump_fancy()
