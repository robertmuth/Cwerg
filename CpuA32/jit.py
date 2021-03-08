#!/usr/bin/python3


import ctypes
import mmap
import platform
import struct
import sys

import CpuA32.disassembler as dis
import CpuA32.opcode_tab as arm


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
            ins = arm.Disassemble(data)
            disass = dis.RenderInstructionStd(ins)
            print(f"{i:2d} {[f'{b:02x}' for b in bs]} {data:08x} {disass}")


def MakeBuffer(size, prot):
    buf = mmap.mmap(-1, size, prot=prot)
    void_pointer = ctypes.c_void_p.from_buffer(buf)
    return buf, ctypes.addressof(void_pointer)


def EmitX86(code_buf):
    code_buf.write(b'\x8b\xc7')  # mov eax, edi
    code_buf.write(b'\x83\xc0\x01')  # add eax, 1
    code_buf.write(b'\xc3')  # ret


def EmitARM32(code_buf):
    for ins in [
        dis.InsParse("add_imm", ["r0", "r0", "1"]),
        dis.InsParse("mov_regimm", ["r15", "lsl", "r14", "0"])
    ]:
        code_buf.write(arm.Assemble(ins).to_bytes(4, "little"))


def EmitARM32Mul(code_buf):
    for ins in [
        dis.InsParse("mul", ["r0", "r1", "r0"]),
        dis.InsParse("mov_regimm", ["r15", "lsl", "r14", "0"])
    ]:
        code_buf.write(arm.Assemble(ins).to_bytes(4, "little"))


def EmitARM32Fib(code_buf):
    for ins in [
        # e92d4030 stm sp!, {r4,r5,lr}
        dis.InsParse("stmdb_update", ["sp", "reglist:16432"]),
        dis.InsParse("cmp_imm", ["r0", "1"]),
        dis.InsParse("b", ["le", "7"]),
        dis.InsParse("mov_imm", ["r4", "0"]),
        dis.InsParse("mov_regimm", ["r5", "lsl", "r0", "0"]),
        #
        dis.InsParse("sub_imm", ["r0", "r5", "1"]),
        dis.InsParse("bl", ["lr", "-8"]),
        dis.InsParse("add_regimm", ["r4", "r4", "lsl", "r0", "0"]),
        # #
        dis.InsParse("sub_imm", ["r0", "r5", "2"]),
        dis.InsParse("bl", ["lr", "-11"]),
        dis.InsParse("add_regimm", ["r0", "r4", "lsl", "r0", "0"]),
        # e8bd4030 ldm sp!, {r4,r5,pc}
        dis.InsParse("ldmia_update", ["reglist:32816", "sp"]),
    ]:
        code_buf.write(arm.Assemble(ins).to_bytes(4, "little"))


def TestCodeGen():
    print("Ensure code generators work in principle - no executation")
    for snippet in [EmitX86]:
        print(f"\n{snippet.__name__}")
        test_buffer = TestBuffer()
        snippet(test_buffer)
        test_buffer.dump()
    for snippet in [EmitARM32, EmitARM32Mul, EmitARM32Fib]:
        print(f"\n{snippet.__name__}")
        test_buffer = TestBuffer()
        snippet(test_buffer)
        test_buffer.dump_fancy()


def gen_code(x):
    TestCodeGen()

    code_buf, code_addr = MakeBuffer(
        mmap.PAGESIZE,
        mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)

    data_buf, data_addr = MakeBuffer(
        mmap.PAGESIZE,
        mmap.PROT_READ | mmap.PROT_WRITE)

    # print(f"CODE-BUFFER: {code_buf} {code_addr:08x}")
    ftype = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
    f = ftype(code_addr)

    isa = platform.machine()
    print(f"ISA: {isa}")
    if isa == "x86_64":
        EmitX86(code_buf)
    elif isa == "armv7l":
        # EmitARM32(code_buf)
        EmitARM32Fib(code_buf)
    else:
        assert False, f"unexpected isa {isa}"

    print("Running Code")
    r = f(x)
    print(r)

    # del fpointer
    code_buf.close()


if len(sys.argv) > 1:
    gen_code(int(sys.argv[1]))
else:
    gen_code(42)
