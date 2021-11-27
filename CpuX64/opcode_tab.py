#!/usr/bin/python3

"""
X64 64bit assembler + disassembler + side-effects table

This depends on x86data.js from https://github.com/asmjit/asmdb

We intend to only support a small subset of the opcode space.
Enough for code generation.
"""

from typing import List, Dict, Tuple, Optional

import collections
import dataclasses
import enum
import re
import json
import itertools

# list of opcodes we expect to use during X64 code generation
# plus some extra ones.
# coverage is > 95% of all opcodes commonly found in x86-64 executable.
SUPPORTED_OPCODES = {
    "add", "addss", "addsd",  #
    "sub", "subss", "subsd",  #

    "imul", "mulss", "mulsd",  #
    "div", "idiv", "divss", "divsd",  #
    "or", "and", "xor",  #
    "sar", "shr", "shl", "ror", "rol",  #
    #
    "mov",  # includes movabs
    "movsx",  #
    "movzx",  #
    "movq",
    "movsxd", "movsx",
    "movaps", "movapd", "movups", "movdqu", "movdqa",  #
    #
    "minss", "minsd",
    "maxss", "maxsd",
    "sqrtss", "sqrtsd",
    # "movsd", # may require additional work
    # "movss", # may require additional work
    ""
    "neg",  #
    "pxor",  #
    "cvtss2sd", "cvtss2si",  #
    "cvtsd2ss", "cvtsd2si",  #
    "cvtsi2ss", "cvtsi2sd",  #
    "cvttss2si", "cvttsd2si",
    #
    "test",  "cmp",  #
    "lea",  #
    "xchg",
    "popcnt", "tzcnt", "lzcnt",  #
    "pop", "push",  #
    "ucomiss", "ucomisd", "comiss",
    #
    "call", "ret", "syscall", "endbr64",
    "jmp",
    "js",
    "jns",
    "jle",  # "/jng",
    "jne",  # "/jnz",
    "jge",  # "/jnl",
    "jbe",  # "/jna",
    "jb",  # "/jnae/jc",
    "jae",  # "/jnb/jnc"
    "je",  # "/jz",
    "ja",  # "/jnbe",
    "jl",  # "/jnge",
    "jp",  # "/jpe",
    "jnp",  # "/jpo",
    "jge",  # "/jnl",
    "jg",  # "/jnle",
    #
    "cmovb",  # "/cmovnae/cmovc"
    "cmovae",  # /cmovnb/cmovnc"
    "cmove",  # "/cmovz"
    "cmovo",
    "cmovno",
    "cmovs",
    "cmovns",
    "cmovne",  # "/cmovnz"
    "cmovbe",  # "/cmovna"
    "cmova",  # "/cmovnbe"
    "cmovs",
    "cmovns",
    "cmovp",  # "/cmovpe"
    "cmovnp",  # "/cmovpo"
    "cmovl",  # "/cmovnge"
    "cmovge",  # "/cmovnl"
    "cmovle",  # "/cmovng"
    "cmovle",  # "/cmovng"

}

_OPCODES_WITH_MULTIPLE_REG_WRITE = {
    "div", "idiv", "imul", "mul", "mulx",
    "cmpxchg8b", "cmpxchg16b", "cmpxchg32b",
    "xadd", "xchg",
    "cpuid", "rdtsc", "rdtscp",
    "rdpkru", "rdpru", "rdpmc", "rdmsr",
    "xgetbv",
    "vgatherdpd", "vgatherdps", "vgatherqpd", "vgatherqps",
    "vpgatherdd", "vpgatherdq", "vpgatherqd", "vpgatherqq",
    "vp2intersectd", "vp2intersectq",
}

# opcode extension/flavors we do not support for now
_DISALLOWED_EXTENSIONS = {
    "Deprecated",
    "MMX",
    "MMX2",
    "X86",
    "_Rep",
}


def IsDisallowExtension(ext):
    for m in ext.split():
        if m in _DISALLOWED_EXTENSIONS:
            return True
    return False


_IMPLICIT_OPERANDS = {
    "al", "ax", "eax", "rax",
    "dx", "edx", "rdx",  #
    "cl",  #
    "1",
}

# not used yet
_M_BUT_NOT_MEM = {
    "r64", "xmm[63:0]",
}

# not used yet
_M_BUT_NOT_REG = {
    "m32", "m64",
}

_OP_MAP = {
    "I": {
        "ib/ub", "iw/uw", "id/ud", "iq/uq",  #
        "ib", "iw", "id", "uw", "ud",
    },
    "R": {
        "r8", "r16", "r32", "r64",
        "sreg", "creg", "dreg",
        "xmm[31:0]", "xmm[63:0]",
        "xmm",
    },
    "M": {
        "r8/m8", "r16/m16", "r32/m32", "r64/m64",
        "r32/m16", "r64/m16",
        "mem",  #
        "r64[63:0]/m64",
        "xmm[31:0]/m32", "xmm[63:0]/m64", "xmm/m128",
        # non address
        # "r64", "xmm[63:0]", "xmm[31:0]",
        # non register
        # "m64", "m32",
    },
    "D": {"rel8", "rel32"},  # displacement
    "O": {"r8", "r16", "r32", "r64"},  # byte_with_reg
    "x": _IMPLICIT_OPERANDS,
    # "r": {"r8", "r16", "r32", "r64"},
}

_SUPPORTED_OPERANDS = set.union(*[x for x in _OP_MAP.values()])

_UNSUPPORTED_OPERANDS = {
    "moff8", "moff16", "moff32", "moff64",  #
    "fs", "gs",
    "creg", "dreg",  # problems with M encoding of r64
}

_OPCODES_WITH_IMMEDIATE_SIGN_EXTENSION = {
    "and", "or", "sub", "cmp", "add", "xor", "imul", "mov",
}


def ContainsUnsupportedOperands(ops):
    for o in ops:
        if o in _UNSUPPORTED_OPERANDS:
            return True
    return False


_OPERAND_MODIFIERS = {
    "x:",  # read/write
    "X:",  # read/write, zero extend
    "w:",  # write only
    "W:",  # write only, zero extend
    "R:",  # read only
}

_SUPPORTED_FORMATS = {
    "MI",
    "MR",
    "RM",
    "D",
    "M",
    "I",
    "O",
    "RMI",
    "",
    # custom formats:
    "OI",  # mov ['w:r8', 'ib/ub'] I ['B0+r', 'ib'] etc
    "xM",  # div ['ax', 'r8/m8'] xM ['F6', '/6']
    "xxM",  # div ['dx', 'ax', 'r16/m16'] xxM
    "Mx",  # sar ['r8/m8', 'cl'] Mx
    "xI",
    "Ox",  # xchg
    "xO",  # xchg
}

_REG_NAMES = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]

_REG_NAMES_8R = [r.replace("x", "") + "l" for r in _REG_NAMES] + [f"r{i}b" for i in range(8, 16)]

_REG_NAMES = {
    8: _REG_NAMES_8R,  # note: this is wrong when there is no rex bytes
    16: [r for r in _REG_NAMES] + [f"r{i}w" for i in range(8, 16)],
    32: [f"e{r}" for r in _REG_NAMES] + [f"r{i}d" for i in range(8, 16)],
    64: [f"r{r}" for r in _REG_NAMES] + [f"r{i}" for i in range(8, 16)],
}

_XREG_NAMES = [f"xmm{r}" for r in range(16)]


def GetSInt(data, byte_width, bit_width):
    x = int.from_bytes(data[:byte_width], "little", signed=True)
    if bit_width:
        return x & (1 << bit_width) - 1
    return x


def Hexify(data) -> str:
    return " ".join(f"{b:02x}" for b in data)


def IsOpXmm(c: str, ops: List, format: str) -> bool:
    pos = format.find(c)
    assert pos >= 0
    return "xmm" in ops[pos]


def GetOpWidth(op):
    if op in {"al"}:
        return 8
    elif op in {"eax"}:
        return 32
    elif op in {"rax"}:
        return 64
    elif op.endswith("128"):
        return 128
    elif op.endswith("8"):
        return 8
    elif op.endswith("16"):
        return 16
    elif op.endswith("32"):
        return 32
    elif op.endswith("64"):
        return 64
    else:
        assert False, f"{op}"


def FindOpWidth(c: str, ops: List, format: str) -> bool:
    pos = format.find(c)
    assert pos >= 0
    return GetOpWidth(ops[pos])


@enum.unique
class OK(enum.Enum):
    """Operand Kind"""
    MODRM_RM_REG = 1
    MODRM_RM_BASE = 2
    OFFABS8 = 3
    OFFABS32 = 4
    SIB_SCALE = 5
    SIB_INDEX = 6
    SIB_BASE = 7
    IMM8 = 8
    IMM16 = 9
    IMM32 = 10
    OFFPCREL8 = 11
    OFFPCREL32 = 12
    BYTE_WITH_REG = 13
    MODRM_REG = 14
    MODRM_XREG = 15
    MODRM_RM_XREG = 16
    IMM8_16 = 17
    IMM8_32 = 18
    IMM8_64 = 19
    IMM32_64 = 20
    IMM64 = 21
    SIB_INDEX_AS_BASE = 22


def GetRegBits(data: int, data_bit_pos, rex: int, rex_bit_pos: int) -> int:
    r = (data >> data_bit_pos) & 0x7
    if rex:
        r |= ((rex >> rex_bit_pos) & 1) << 3
    return r


@enum.unique
class SIB_MODE(enum.Enum):
    NO = 1
    YES = 2
    BP_DISP = 3


class Opcode:
    """
    An opcode represent an x86-64 instruction.
    We create separate Opcodes for each structurally different flavor of the
    instruction. For example `add reg, memory-access` will become six different
    opcodes (no-offset, offset8, offset32) X (sib, no-sib)
    The presence or absence of the REX.W and 0x66 (Operand override) prefixes also
    forces new Opcodes.
    """

    Opcodes = []

    def __init__(self, name: str, variant: str, operands: List, format: str):
        Opcode.Opcodes.append(self)
        self.name: str = name
        self.variant: str = variant
        self.operands = operands
        self.format = format

        self.discriminant_mask: int = 0
        self.discriminant_data: int = 0
        #
        self.rexw = False
        self.modrm_pos = -1
        self.sib_pos = -1
        self.offset_pos = -1
        self.imm_pos = -1
        self.byte_with_reg_pos = -1
        #
        self.fields: List = []
        self.mask: List = []
        self.data: List = []

    def __str__(self):
        return f"{self.name}.{self.variant}  [{' '.join(self.operands)}] {self.format}   {self.fields} sib:{self.sib_pos}  off:{self.offset_pos} "

    def Finalize(self):
        self.discriminant_mask = int.from_bytes(self.mask[0:5], "little")
        self.discriminant_data = self.discriminant_mask & int.from_bytes(self.data[0:5], "little")
        expected_len = len(self.operands)
        if self.modrm_pos >= 0:
            if OK.OFFABS8 in self.fields or OK.OFFABS32 in self.fields:
                expected_len += 1
            if self.sib_pos >= 0:
                expected_len += 2

            # assert len(self.fields) == expected_len, f"{self.fields} vs {self.operands}"

    def AddRexW(self):
        self.rexw = True
        self.variant += "_w"

    def AddByte(self, b: int):
        self.data.append(b)
        self.mask.append(0xff)

    def AddByteWithReg(self, b: int):
        self.byte_with_reg_pos = len(self.data)
        self.fields.append(OK.BYTE_WITH_REG)
        self.data.append(b)
        self.mask.append(0xf8)
        assert (b & 0xf8) == b

    def AddReg(self):
        is_xmm = IsOpXmm("R", self.operands, self.format)
        self.fields.append(OK.MODRM_XREG if is_xmm else OK.MODRM_REG)

    def AddRegOpExt(self, ext: int):
        self.modrm_pos = len(self.data)
        mask = 0xf8
        data = (3 << 6) | (ext << 3)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OK.MODRM_RM_REG)

    def AddRegOpReg(self):
        is_xmm = IsOpXmm("M", self.operands, self.format)
        self.modrm_pos = len(self.data)
        mask = 0xc0
        data = (3 << 6)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OK.MODRM_RM_XREG if is_xmm else OK.MODRM_RM_REG)

    def AddMemOpCommonTail(self, mod: int):
        if mod == 0:
            pass
        elif mod == 1:
            self.variant += "_off8"
            self.offset_pos = len(self.data)
            self.fields.append(OK.OFFABS8)
            self.mask += [0]
            self.data += [0]
        elif mod == 2:
            self.variant += "_off32"
            self.offset_pos = len(self.data)
            self.fields.append(OK.OFFABS32)
            self.mask += [0, 0, 0, 0]
            self.data += [0, 0, 0, 0]

    def AddMemOp(self, sib_mode: SIB_MODE, mod: int, ext: int = -1):
        self.modrm_pos = len(self.data)
        assert mod <= 2
        data = mod << 6
        mask = 0xc0

        if ext >= 0:
            assert ext <= 7
            mask |= 0x38
            data |= ext << 3
        if sib_mode == SIB_MODE.YES or sib_mode == SIB_MODE.BP_DISP:
            mask |= 0x7
            data |= 0x4
            self.mask.append(mask)
            self.data.append(data)
            self.sib_pos = len(self.data)
            if sib_mode == SIB_MODE.YES:
                self.variant += "_sib"
                self.mask.append(0)
                self.data.append(0)
                self.fields += [OK.SIB_BASE, OK.SIB_INDEX, OK.SIB_SCALE]
            else:
                self.variant += "_sib_bp_disp"
                self.mask.append(0x07)
                self.data.append(0x05)
                self.fields += [OK.SIB_INDEX_AS_BASE, OK.SIB_SCALE]
                assert mod == 0
                mod = 2
        else:
            self.mask.append(mask)
            self.data.append(data)
            self.fields.append(OK.MODRM_RM_BASE)
        self.AddMemOpCommonTail(mod)

    def AddImmOp(self, op):
        self.imm_pos = len(self.data)
        size = 0
        if op == "ib":
            if self.name == "push" and self.format == "I":
                self.fields.append(OK.IMM8_64)
            elif self.name in _OPCODES_WITH_IMMEDIATE_SIGN_EXTENSION:
                bw = GetOpWidth(self.operands[0])
                self.fields.append({8: OK.IMM8, 16: OK.IMM8_16,
                                    32: OK.IMM8_32, 64: OK.IMM8_64}[bw])
            else:
                self.fields.append(OK.IMM8)
            size = 1
        elif op == "iw":
            self.fields.append(OK.IMM16)
            size = 2
        elif op == "id":
            if self.name == "push" and self.format == "I":
                self.fields.append(OK.IMM32_64)
            elif self.name in _OPCODES_WITH_IMMEDIATE_SIGN_EXTENSION:
                bw = GetOpWidth(self.operands[0])
                self.fields.append({32: OK.IMM32, 64: OK.IMM32_64}[bw])
            else:
                self.fields.append(OK.IMM32)
            size = 4
        elif op == "iq":
            self.fields.append(OK.IMM64)
            size = 8
        else:
            assert False
        self.mask += [0] * size
        self.data += [0] * size

    def AddOffsetPCREL(self, op):
        self.offset_pos = len(self.data)
        if op == "cb":
            self.fields.append(OK.OFFPCREL8)
            self.mask += [0]
            self.data += [0]
        elif op == "cd":
            self.fields.append(OK.OFFPCREL32)
            self.mask += [0, 0, 0, 0]
            self.data += [0, 0, 0, 0]
        else:
            assert False

    def RenderOps(self, data, skip_implicit):
        is_lea = self.name.startswith("lea")
        rex = 0
        if (data[0] & 0xf0) == 0x40:
            rex = data[0]
            data = data[1:]
        out = []
        for o in self.fields:
            if isinstance(o, str):
                if not skip_implicit:
                    out.append(o)
                continue
            assert isinstance(o, OK), f"unexpected {o} {type(o)}"

            if o is OK.MODRM_RM_REG or o is OK.MODRM_RM_XREG:
                r = GetRegBits(data[self.modrm_pos], 0, rex, 0)
                if o is OK.MODRM_RM_REG:
                    bw = FindOpWidth("M", self.operands, self.format)
                    out.append(_REG_NAMES[bw][r])
                else:
                    out.append(_XREG_NAMES[r])
            elif o is OK.MODRM_RM_BASE:
                if not is_lea:
                    bw = FindOpWidth("M", self.operands, self.format)
                    out.append(f"MEM{bw}")
                r = GetRegBits(data[self.modrm_pos], 0, rex, 0)
                out.append(_REG_NAMES[64][r])  # assumes no add override
            elif o is OK.MODRM_REG or o is OK.MODRM_XREG:
                r = GetRegBits(data[self.modrm_pos], 3, rex, 2)
                if o is OK.MODRM_REG:
                    bw = FindOpWidth("R", self.operands, self.format)
                    out.append(_REG_NAMES[bw][r])
                else:
                    out.append(_XREG_NAMES[r])
            elif o is OK.SIB_BASE:
                if not is_lea:
                    bw = FindOpWidth("M", self.operands, self.format)
                    out.append(f"MEM{bw}")
                rbase = GetRegBits(data[self.sib_pos], 0, rex, 0)
                rindex = GetRegBits(data[self.sib_pos], 3, rex, 1)
                scale = data[self.sib_pos] >> 6
                if rindex == 4:
                    out.append(_REG_NAMES[64][rbase])  # assumes no add override
                else:
                    out.append(_REG_NAMES[64][rbase])  # assumes no add override
                    out.append(_REG_NAMES[64][rindex])  # assumes no add override
                    out.append(str(1 << scale))
            elif o is OK.SIB_INDEX_AS_BASE:
                if not is_lea:
                    bw = FindOpWidth("M", self.operands, self.format)
                    out.append(f"MEM{bw}")
                rindex = GetRegBits(data[self.sib_pos], 3, rex, 1)
                scale = data[self.sib_pos] >> 6
                out.append(_REG_NAMES[64][rindex])  # assumes no add override
                out.append(str(1 << scale))
            elif o is OK.SIB_INDEX:
                pass
            elif o is OK.SIB_SCALE:
                pass
            elif o is OK.BYTE_WITH_REG:
                r = GetRegBits(data[self.byte_with_reg_pos], 0, rex, 0)
                bw = FindOpWidth("O", self.operands, self.format)
                out.append(_REG_NAMES[bw][r])
            elif o is OK.IMM8:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 1, 8):x}")
            elif o is OK.IMM8_16:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 1, 16):x}")
            elif o is OK.IMM8_32:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 1, 32):x}")
            elif o is OK.IMM8_64:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 1, 64):x}")
            elif o is OK.IMM32_64:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 4, 64):x}")
            elif o is OK.IMM16:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 2, 16):x}")
            elif o is OK.IMM32:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 4, 32):x}")
            elif o is OK.IMM64:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 8, 64):x}")
            elif o is OK.OFFABS8:
                out.append(f"0x{GetSInt(data[self.offset_pos:], 1, None):x}")
            elif o is OK.OFFABS32:
                out.append(f"0x{GetSInt(data[self.offset_pos:], 4, None):x}")
        return out


_SUPPORTED_ENCODING_PARAMS = {
    "/0", "/1", "/2", "/3", "/4", "/5", "/6", "/7",  #
    "/r",  #
    "REX.W",
    "ib", "iw", "id", "iq",  #
    "cd", "cb",
}

_RE_BYTE_VARIATIONS = re.compile("^[0-9A-F][0-9A-F]([+]r)?$")

_RE_BYTE = re.compile("^[0-9A-F][0-9A-F]$")
_RE_BYTE_WITH_REG = re.compile("^[0-9A-F][0-9A-F][+]r?$")

_SIB_MOD_COMBOS = [
    (0, SIB_MODE.BP_DISP),
    (0, SIB_MODE.YES), (0, SIB_MODE.NO),
    (1, SIB_MODE.YES), (1, SIB_MODE.NO),
    (2, SIB_MODE.YES), (2, SIB_MODE.NO),
]


def HandlePatternMR(name: str, ops, format, encoding, inv: bool):
    opc = Opcode(name, "", ops, format)
    for x in encoding:
        if x == "REX.W":
            opc.AddRexW()
        elif _RE_BYTE.match(x):
            opc.AddByte(int(x, 16))
        elif x == "/r":
            if inv:
                opc.AddReg()
                opc.AddRegOpReg()
            else:
                opc.AddRegOpReg()
                opc.AddReg()
        elif x in {"ib", "iw", "id", "iq"}:
            opc.AddImmOp(x)
        else:
            assert False

    for mod, sib_mode in _SIB_MOD_COMBOS:
        opc = Opcode(name, "", ops, format)
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x == "/r":
                if inv:
                    opc.AddReg()
                    opc.AddMemOp(sib_mode, mod)
                else:
                    opc.AddMemOp(sib_mode, mod)
                    opc.AddReg()
            elif x in {"ib", "iw", "id", "iq"}:
                opc.AddImmOp(x)
            else:
                assert False


def HandlePatternMI(name: str, ops, format, encoding, before, after):
    opc = Opcode(name, "", ops, format)
    for x in encoding:
        if x == "REX.W":
            opc.AddRexW()
        elif _RE_BYTE.match(x):
            opc.AddByte(int(x, 16))
        elif x.startswith("/"):
            ext = int(x[1:])
            opc.fields += before
            opc.AddRegOpExt(ext)
            opc.fields += after
        elif x in {"ib", "iw", "id", "iq"}:
            opc.AddImmOp(x)
        else:
            assert False

    # 81 7c 24 28 ff 0f 00    cmp    DWORD PTR [rsp+0x28],0xfff
    for mod, sib_mode in _SIB_MOD_COMBOS:
        opc = Opcode(name, "", ops, format)
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x.startswith("/"):
                ext = int(x[1:])
                opc.fields += before
                opc.AddMemOp(sib_mode, mod, ext=ext)
                opc.fields += after
            elif x in {"ib", "iw", "id", "iq"}:
                opc.AddImmOp(x)
            else:
                assert False


def HandlePattern(name: str, ops: List[str], format: str, encoding: List[str], meta: List[str]):
    assert format in _SUPPORTED_FORMATS, f"bad format [{format}]"
    for f in encoding:
        assert f in _SUPPORTED_ENCODING_PARAMS or _RE_BYTE_VARIATIONS.match(f), f"bad parameter [{repr(f)}]"
    for o in ops:
        assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"

    assert len(format) == len(ops)
    for op, kind in zip(ops, format):
        assert op in _OP_MAP[kind], f"{op} not allowed for {kind}"

    if format in {"MI", "M", "xM", "xxM", "Mx"}:
        before = []
        after = []
        seen_non_X = False
        for i, c in enumerate(format):
            if c != "x":
                seen_non_X = True
            elif seen_non_X:
                after.append(ops[i])
            else:
                before.append(ops[i])
        HandlePatternMI(name, ops, format, encoding, before, after)
    elif format == "MR":
        HandlePatternMR(name, ops, format, encoding, inv=False)
    elif format == "RM" or format == "RMI":
        HandlePatternMR(name, ops, format, encoding, inv=True)
    elif format == "":
        opc = Opcode(name, "", ops, format)
        for x in encoding:
            if _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            else:
                assert False
    elif format in {"I", "O", "OI", "xI", "xO", "Ox"}:
        opc = Opcode(name, "", ops, format)
        before = []
        after = []
        seen_non_X = False
        for i, c in enumerate(format):
            if c != "x":
                seen_non_X = True
            elif seen_non_X:
                after.append(ops[i])
            else:
                before.append(ops[i])
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE_WITH_REG.match(x):
                opc.fields += before
                opc.AddByteWithReg(int(x[0:2], 16))
                opc.fields += after
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x in {"ib", "iw", "id", "iq"}:
                opc.fields += before
                opc.AddImmOp(x)
                opc.fields += after
            else:
                assert False
    elif format == "D":
        opc = Opcode(name, "", ops, format)
        for x in encoding:
            if _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x in {"cb", "cd"}:
                opc.AddOffsetPCREL(x)
            else:
                assert False
    else:
        assert False, "bad format {format}"


def ExtractOps(s):
    def clean(o):
        if o[0:2] in _OPERAND_MODIFIERS:
            o = o[2:]
        if o[0] == "~":  # indicates commutativity
            o = o[1:]
        return o

    return [clean(x) for x in s.split(",") if x]


def OpcodeSanityCheck(opcodes: List[Opcode]):
    patterns = collections.defaultdict(list)
    for opcode in Opcode.Opcodes:
        patterns[(opcode.rexw, opcode.discriminant_mask, opcode.discriminant_data)].append(opcode)


    print(f"Checkin Opcodes for conflicts")
    for k, opcodes in patterns.items():
        if len(opcodes) == 1: continue
        for o in opcodes:
            print(o)
        print()

    print(f"Checkin Opcodes for overlap")
    for a, b in itertools.combinations(opcodes, 2):
        if a.rexw == b.rexw:
            c = a.discriminant_mask & b.discriminant_mask
            assert (a.discriminant_data & c) != (b.discriminant_data & c)


def FixupFormat(format: str, ops: List, encoding) -> str:
    if format == "I" and ("B8+r" in encoding or "B0+r" in encoding):
        return "OI"
    if format == "NONE":
        return ""

    if len(format) == len(ops):
        return format

    assert len(format) == 1

    def tr(f):
        if f in _IMPLICIT_OPERANDS or f == "1":
            return "x"
        else:
            return format

    return "".join(tr(o) for o in ops)


# this excludes:
# "and", "X:r64, ud", "MI"      , "81 /4 id"
# "X:rax, ud", "I"       , "25 id"
def SkipInstruction(name, format, ops):
    if format == "MI" and ops[0] == "r64":
        return True

    if format == "I" and ops[0] == "rax" and ops[1] == "ud":
        return True

    # the decision which one of these to skip is somewhat arbitrary but
    # we followed what objdump does
    if name == "xchg" and (format == "RM" or ops[0].endswith("ax")):
        return True
    return False


def CreateOpcodes(instructions: List, verbose: bool):
    count = collections.defaultdict(int)
    for name, ops, format, encoding, metadata in instructions:
        if IsDisallowExtension(metadata):
            continue
        ops = ops.replace("<", "").replace(">", "").replace(", ", ",")
        ops_orig = [x for x in ops.split(",") if x]
        written_ops = [x for x in ops_orig if x[0:2] in {"X:", "x:", "W:", "w:"}]
        assert name in _OPCODES_WITH_MULTIPLE_REG_WRITE or len(written_ops) <= 1, f"{name}"
        ops = ExtractOps(ops)
        name = name.split("/")[0]
        if name not in SUPPORTED_OPCODES or ContainsUnsupportedOperands(ops):
            continue
        if SkipInstruction(name, format, ops):
            continue

        count[name] += 1
        metadata = metadata.split()
        encoding = encoding.split()
        # hack
        format = FixupFormat(format, ops, encoding)
        assert format in _SUPPORTED_FORMATS, f"{format}"
        if verbose:
            print(name, ops, format, encoding, metadata)
        HandlePattern(name, ops, format, encoding, metadata)
    for k in SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
    for opcode in Opcode.Opcodes:
        opcode.Finalize()


def FingerPrintRawInstructions(data) -> int:
    fp = []
    i = 0
    if (data[i] & 0xf0) == 0x40:
        if (data[i] & 0xf8) == 0x48:
            fp.append(0x48)
        i += 1
    if data[i] == 0x66:
        fp.append(data[i])
        i += 1
    if data[i] == 0xf2 or data[i] == 0xf3:
        fp.append(data[i])
        i += 1
    if data[i] == 0x0f:
        fp.append(data[i])
        i += 1
    fp.append(data[i])
    return int.from_bytes(fp, "little")


def LoadOpcodes(filename: str):
    # This file is file https://github.com/asmjit/asmdb (see file comment)
    _START_MARKER = "// ${JSON:BEGIN}"
    _END_MARKER = "// ${JSON:END}"
    data = open(filename).read()
    start = data.find(_START_MARKER) + len(_START_MARKER)
    end = data.find(_END_MARKER)

    tables = json.loads(data[start:end])

    CreateOpcodes(tables["instructions"], False)


def MakeFingerPrintLookupTable():
    out = collections.defaultdict(list)
    for opc in Opcode.Opcodes:
        assert isinstance(opc, Opcode)
        fp = []
        data = opc.data
        mask = opc.mask
        i = 0
        if opc.rexw:
            fp.append(0x48)
        if data[i] == 0x66:
            fp.append(0x66)
            assert mask[i] == 0xff
            i += 1
        if data[i] == 0xf2 or data[i] == 0xf3:
            fp.append(data[i])
            assert mask[i] == 0xff
            i += 1
        if data[i] == 0x0f:
            fp.append(data[i])
            assert mask[i] == 0xff
            i += 1

        if mask[i] == 0xff:
            fp.append(data[i])
            out[int.from_bytes(fp, "little")].append(opc)
        else:
            assert mask[i] == 0xf8 and i == opc.byte_with_reg_pos, f"{opc.name} {data} {mask} {fp}"
            fp.append(0)
            assert mask[i] == 0xf8
            for r in range(8):
                fp[-1] = data[i] + r
                out[int.from_bytes(fp, "little")].append(opc)
    return out


_OPCODES_BY_FP = None


def FindMatchingOpcode(data) -> Optional[Opcode]:
    rules = _OPCODES_BY_FP[FingerPrintRawInstructions(data)]
    if (data[0] & 0xf0) == 0x40:
        data = data[1:]
    discriminant = int.from_bytes(data, "little")
    for r in rules:
        if (r.discriminant_mask & discriminant) == r.discriminant_data:
            return r
    return None


LoadOpcodes("x86data.js")
print(f"TOTAL instruction templates: {len(Opcode.Opcodes)}")

_OPCODES_BY_FP = MakeFingerPrintLookupTable()

if __name__ == "__main__":
    OpcodeSanityCheck(Opcode.Opcodes)
    if False:
        for k, v in _OPCODES_BY_FP.items():
            if v:
                print(f"{k:10x} {len(v)}")
