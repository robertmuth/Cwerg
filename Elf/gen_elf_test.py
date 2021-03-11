#!/usr/bin/python3

"""
Tests the creation of ELF executables for both x64 and a32
"""
import io
import sys

from Elf import elfhelper
from Elf.enum_tab import SH_FLAGS, EI_CLASS

RODATA_X64 = b"Hello, world (x64)\n"

TEXT_X64 = [
    0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00,  # mov  $0x1,%rax
    0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00,  # mov  $0x1,%rdi
    0x48, 0xc7, 0xc6, 0x00, 0x20, 0x40, 0x00,  # mov  $0x402000,%rsi
    0x48, 0xc7, 0xc2, 0x13, 0x00, 0x00, 0x00,  # mov  $0x13,%rdx
    0x0f, 0x05,  # syscall
    0x48, 0xc7, 0xc0, 0x3c, 0x00, 0x00, 0x00,  # mov  $0x3c,%rax
    0x48, 0x31, 0xff,  # xor    %rdi,%rdi
    0x0f, 0x05,  # syscall
]


def GenBareBonesX64() -> elfhelper.Executable:
    sec_rodata = elfhelper.Section.MakeSectionRodata(1)
    sec_rodata.data = RODATA_X64
    sec_rodata.sh_size = len(sec_rodata.data)

    sec_text = elfhelper.Section.MakeSectionText(1)
    sec_text.data = bytes(TEXT_X64)
    sec_text.sh_size = len(sec_text.data)

    sec_shstrtab = elfhelper.Section.MakeSectionStrTab(".shstrtab")
    sec_shstrtab.data = elfhelper.MakeSecStrTabContents([sec_rodata, sec_text, sec_shstrtab])
    sec_shstrtab.sh_size = len(sec_shstrtab.data)

    seg_ro = elfhelper.Segment.MakeROSegment(4096)
    seg_exe = elfhelper.Segment.MakeExeSegment(4096)
    seg_pseudo = elfhelper.Segment.MakePseudoSegment()

    seg_ro.sections.append(sec_rodata)
    seg_exe.sections.append(sec_text)
    seg_pseudo.sections.append(sec_shstrtab)

    exe = elfhelper.Executable.MakeExecutableX64(0x400000,
                                                 [sec_rodata, sec_text, sec_shstrtab],
                                                 [seg_ro, seg_exe, seg_pseudo])
    exe.update_vaddrs_and_offset()

    print(f"PATCH ENTRY: {sec_text.sh_addr:x}")
    exe.ehdr.e_entry = sec_text.sh_addr

    print(f"PATCH MSG: {sec_rodata.sh_addr:x}")
    # string address is at offset 14
    sec_text.data = (bytes(TEXT_X64[:17]) +
                     sec_rodata.sh_addr.to_bytes(4, "little") +
                     bytes(TEXT_X64[21:]))
    return exe


ALL_A64 = b"".join(x.to_bytes(4, byteorder='little') for x in [
    # 9 instruction
    0xd2800020,  # mov	x0, #0x1
    0x90000001,  # adrp	x1, 400000 <_start-0xb0>
    0x91035021,  # add	x1, x1, #0xd4
    0xd2800242,  # mov	x2, #0x12
    0xd2800808,  # mov	x8, #0x40
    0xd4000001,  # svc	#0x0
    0xd2800000,  # mov	x0, #0x0
    0xd2800ba8,  # mov	x8, #0x5d
    0xd4000001,  # svc	#0x0
    #  "hello world...."
    0x6c6c6548,  # .word	0x6c6c6548
    0x6f77206f,  # .word	0x6f77206f
    0x20646c72,  # .word	0x20646c72
    0x34366128,  # .word	0x64666128
    0x00000a29,  # .short	0x0a29
])


def GenBareBonesA64():
    sec_text = elfhelper.Section.MakeSectionText(1)
    sec_text.data = bytes(ALL_A64)
    sec_text.sh_size = len(sec_text.data)

    sec_shstrtab = elfhelper.Section.MakeSectionStrTab(".shstrtab")
    sec_shstrtab.data = elfhelper.MakeSecStrTabContents([sec_text, sec_shstrtab])
    sec_shstrtab.sh_size = len(sec_shstrtab.data)

    seg_exe = elfhelper.Segment.MakeExeSegment(65536)
    seg_exe.sections.append(sec_text)

    seg_pseudo = elfhelper.Segment.MakePseudoSegment()
    seg_pseudo.sections.append(sec_shstrtab)

    exe = elfhelper.Executable.MakeExecutableA64(0x400000, [sec_text, sec_shstrtab],
                                                 [seg_exe, seg_pseudo])
    exe.update_vaddrs_and_offset()
    print(f"PATCH ENTRY: {sec_text.sh_addr:x}")
    exe.ehdr.e_entry = sec_text.sh_addr
    print(f"PATCH INSTRUCTIONS: {sec_text.sh_addr:x}")
    # simplifying assumption - we stay on the same page so adrp
    # does not need patching only the add instruction following it
    msg_adr = sec_text.sh_addr + 9 * 4
    add_ins = 0x91035021 & 0xff0003ff | ((msg_adr & 0xfff) << 10)
    sec_text.data = (ALL_A64[:8] +
                     add_ins.to_bytes(4, "little") +
                     ALL_A64[12:])
    return exe


ALL_A32 = b"".join(x.to_bytes(4, byteorder='little') for x in [
    0xe3a00001,  # mov	r0, #1
    0xe28f1014,  # add	r1, pc, #20
    0xe3a02012,  # mov	r2, #18
    0xe3a07004,  # mov	r7, #4
    0xef000000,  # svc	0x00000000
    0xe3a00000,  # mov	r0, #0
    0xe3a07001,  # mov	r7, #1
    0xef000000,  # svc	0x00000000
    #
    0x6c6c6548,  # .word	0x6c6c6548
    0x6f77206f,  # .word	0x6f77206f
    0x20646c72,  # .word	0x20646c72
    0x32336128,  # .word	0x32336128
    0x00000a29,  # .short	0x0a29
])


def GenBareBonesA32():
    sec_text = elfhelper.Section.MakeSectionText(1)
    sec_text.data = bytes(ALL_A32)
    sec_text.sh_size = len(sec_text.data)

    sec_shstrtab = elfhelper.Section.MakeSectionStrTab(".shstrtab")
    sec_shstrtab.data = elfhelper.MakeSecStrTabContents([sec_text, sec_shstrtab])
    sec_shstrtab.sh_size = len(sec_shstrtab.data)

    seg_exe = elfhelper.Segment.MakeExeSegment(65536)
    seg_exe.sections.append(sec_text)

    seg_pseudo = elfhelper.Segment.MakePseudoSegment()
    seg_pseudo.sections.append(sec_shstrtab)

    exe = elfhelper.Executable.MakeExecutableA32(0x20000, [sec_text, sec_shstrtab],
                                                 [seg_exe, seg_pseudo])
    exe.update_vaddrs_and_offset()
    print(f"PATCH ENTRY: {sec_text.sh_addr:x}")
    exe.ehdr.e_entry = sec_text.sh_addr
    return exe


if __name__ == "__main__":
    assert len(sys.argv) > 2
    sys.argv.pop(0)
    mode = sys.argv.pop(0)
    if mode == "genx64":
        exe = GenBareBonesX64()
    elif mode == "gena32":
        exe = GenBareBonesA32()
    elif mode == "gena64":
        exe = GenBareBonesA64()
    else:
        assert False, f"unknown mode {mode}"

    for phdr in exe.segments:
        print(phdr)
        for shdr in phdr.sections:
            print(shdr)

    print("WRITING EXE")
    fout = open(sys.argv.pop(0), "wb")
    exe.save(fout)
