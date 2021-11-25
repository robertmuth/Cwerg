#!/usr/bin/python3

"""
X64 64bit assembler + disassembler + side-effects table

This depends on x86data.js from https://github.com/asmjit/asmdb

We intend to only support a small subset of the opcode space.
Enough for code generation.
"""
from ast import Num
from typing import List, Dict, Tuple, Optional

import collections
import dataclasses
import enum
import sys
import re
import json
import itertools

X86_DATA = None

# list of opcodes we expect to use during X64 code generation
_SUPPORTED_OPCODES = {
    "add", "addss", "addsd",  #
    "sub", "subss", "subsd",  #
    "or", "and", "xor",  #
    "sar", "shr", "shl/sal",  #
    "imul", "mulss", "mulsd",  #
    "div", "idiv", "divss", "divsd",  #
    "mov",  #
    "movsx",  #
    "movzx",  #
    "movq",
    "movsxd", "movsx",
    # "movsd",
    # "movss",
    ""
    "movaps", "movapd", "movups", "movdqu", "movdqa",  #
    "neg",  #
    # "pxor",
    "cvtss2sd", "cvtss2si",  #
    "cvtsd2ss", "cvtsd2si",  #
    "cvtsi2ss", "cvtsi2sd",  #
    "cvttss2si", "cvttsd2si",  #
    "test",  #
    "cmp",  #
    "lea",  #
    "popcnt",  #
    "pop", "push",  #
    "ucomiss", "ucomisd", "comiss",
    "call", "ret", "syscall", "endbr64",
    # "jmp", # waiting for bug fix in asmdb
    "jle/jng", "jne/jnz", "jge/jnl", "jbe/jna",
    "jb/jnae/jc", "je/jz", "ja/jnbe", "jl/jnge",
    "jp/jpe", "jnp/jpo", "jge/jnl", "jg/jnle",
}

# opcode extension/flavors we do not support for now
_DISALLOWED_EXTENSIONS = {
    "Deprecated",
    # "AltForm",
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

_M_BUT_NOT_MEM = {
    "r64", "xmm[63:0]",
}

_M_BUT_NOT_REG = {
    "m32", "m64",
}

_OP_MAP = {
    "I": {
        "ib/ub", "iw/uw", "id/ud", "iq/uq",  #
        "ib", "iw", "id", "uw", "ud",
    },
    "R": {
        "~r8", "~r16", "~r32", "~r64",
        "r8", "r16", "r32", "r64",
        "sreg", "creg", "dreg",
        "xmm[31:0]", "xmm[63:0]",
        "xmm",
    },
    "M": {
        "r8/m8", "r16/m16", "r32/m32", "r64/m64",
        "~r8/m8", "~r16/m16", "~r32/m32", "~r64/m64",
        "r32/m16", "r64/m16",
        "mem", #
        "r64[63:0]/m64",
        "xmm[31:0]/m32", "xmm[63:0]/m64", "xmm/m128",
        # non address
        # "r64", "xmm[63:0]", "xmm[31:0]",
        # non register
        # "m64", "m32",
    },
    "D": {"rel8", "rel32"},     # displacement
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


def ContainsUnsupportedOperands(ops):
    for o in ops:
        if o in _UNSUPPORTED_OPERANDS:
            return True
    return False


def GetBitwidth(ops):
    if not ops:
        return 0
    elif ops[0].endswith("128"):
        return 128
    elif ops[0].endswith("8"):
        return 8
    elif ops[0].endswith("16"):
        return 16
    elif ops[0].endswith("32"):
        return 32
    elif ops[0].endswith("64"):
        return 64
    elif ops[0] == "xmm[31:0]":
        return 32
    elif ops[0] == "xmm[63:0]":
        return 64
    elif ops[0] in {"al"}:
        return 16
    elif ops[0] in {"ax", "dx"}:
        return 16
    elif ops[0] in {"eax", "edx"}:
        return 32
    elif ops[0] in {"rax", "rdx"}:
        return 64
    elif ops[0] in {"sreg", "creg", "dreg", "xmm"}:
        if ops[1].endswith("128"):
            return 128
        elif ops[1].endswith("8"):
            return 8
        elif ops[1].endswith("16"):
            return 16
        elif ops[1].endswith("32"):
            return 32
        elif ops[1].endswith("64"):
            return 64
        elif ops[1].endswith("128"):
            return 18
        assert False, f"cannot determine width for {ops}"
    elif ops[0] == "ib":
        return 8
    elif ops[0] == "iw":
        return 16
    elif ops[0] == "uw":
        return 16
    elif ops[0] == "id":
        return 32
    assert False, f"cannot determine width for {ops}"


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
}

_REG_NAMES = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]

_REG_NAMES_8R = [r.replace("x", "") + "l" for r in _REG_NAMES] + [f"r{i}b" for i in range(8, 16)]
_REG_NAMES_16 = [r for r in _REG_NAMES] + [f"r{i}w" for i in range(8, 16)]
_REG_NAMES_32 = [f"e{r}" for r in _REG_NAMES] + [f"r{i}d" for i in range(8, 16)]
_REG_NAMES_64 = [f"r{r}" for r in _REG_NAMES] + [f"r{i}" for i in range(8, 16)]

_REG_NAMES = {
    8: _REG_NAMES_8R,
    16: _REG_NAMES_16,
    32: _REG_NAMES_32,
    64: _REG_NAMES_64,
}

_XREG_NAMES = [f"xmm{r}" for r in range(16)]


def GetSInt(data, byte_width, bit_width):
    x = int.from_bytes(data[:byte_width], "little", signed=True)
    if bit_width:
        return x & (1 << bit_width) - 1
    return x


def GetUInt(data, byte_width):
    return int.from_bytes(data[:byte_width], "little")


def Hexify(data) -> str:
    return " ".join(f"{b:02x}" for b in data)


def IsXmm(c:str, ops: List, format: str) -> bool:
    pos = format.find(c)
    assert pos >= 0
    return "xmm" in ops[pos]


@enum.unique
class OP(enum.Enum):
    """
    """
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


@enum.unique
class SIB_MODE(enum.Enum):
    NONE = 1
    STD = 2
    SIMPLE = 3


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
        self.bit_width: int = GetBitwidth(operands)

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
        return f"{self.name}.{self.variant}  [{' '.join(self.operands)}]   {self.fields}  w:{self.bit_width}  sib:{self.sib_pos}  off:{self.offset_pos} "

    def Finalize(self):
        self.discriminant_mask = int.from_bytes(self.mask[0:5], "little")
        self.discriminant_data = self.discriminant_mask & int.from_bytes(self.data[0:5], "little")
        expected_len = len(self.operands)
        if self.modrm_pos >= 0:
            if OP.OFFABS8 in self.fields or OP.OFFABS32 in self.fields:
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
        self.fields.append(OP.BYTE_WITH_REG)
        self.data.append(b)
        self.mask.append(0xf8)
        assert (b & 0xf8) == b

    def AddReg(self):
        is_xmm = IsXmm("R", self.operands, self.format)
        self.fields.append(OP.MODRM_XREG if is_xmm else OP.MODRM_REG)

    def AddRegOpExt(self, ext: int):
        self.modrm_pos = len(self.data)
        mask = 0xf8
        data = (3 << 6) | (ext << 3)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OP.MODRM_RM_REG)

    def AddRegOpReg(self):
        is_xmm = IsXmm("M", self.operands, self.format)
        self.modrm_pos = len(self.data)
        mask = 0xc0
        data = (3 << 6)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OP.MODRM_RM_XREG if is_xmm else OP.MODRM_RM_REG)

    def AddMemOpCommonTail(self, mod: int):
        if mod == 0:
            pass
        elif mod == 1:
            self.variant += "_off8"
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFABS8)
            self.mask += [0]
            self.data += [0]
        elif mod == 2:
            self.variant += "_off32"
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFABS32)
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
        if sib_mode != SIB_MODE.NONE:
            mask |= 0x7
            data |= 0x4
            self.mask.append(mask)
            self.data.append(data)
            self.sib_pos = len(self.data)
            if sib_mode == SIB_MODE.STD:
                self.variant += "_sib"
                self.mask.append(0)
                self.data.append(0)
                self.fields += [OP.SIB_BASE, OP.SIB_INDEX, OP.SIB_SCALE]
            else:
                assert sib_mode == SIB_MODE.SIMPLE
                self.variant += "_stk"
                self.mask.append(0x38)
                self.data.append(0x20)
                self.fields += [OP.SIB_BASE]
        else:
            self.mask.append(mask)
            self.data.append(data)
            self.fields.append(OP.MODRM_RM_BASE)
        self.AddMemOpCommonTail(mod)

    def AddImmOp(self, op):
        self.imm_pos = len(self.data)
        size = 0
        if op == "ib":
            self.fields.append(OP.IMM8)
            size = 1
        elif op == "iw":
            self.fields.append(OP.IMM16)
            size = 2
        elif op == "id":
            self.fields.append(OP.IMM32)
            size = 4
        elif op == "iq":
            self.fields.append(OP.IMM32)
            size = 8
        else:
            assert False
        self.mask += [0] * size
        self.data += [0] * size

    def AddOffsetPCREL(self, op):
        self.offset_pos = len(self.data)
        if op == "cb":
            self.fields.append(OP.OFFPCREL8)
            self.mask += [0]
            self.data += [0]
        elif op == "cd":
            self.fields.append(OP.OFFPCREL32)
            self.mask += [0, 0, 0, 0]
            self.data += [0, 0, 0, 0]
        else:
            assert False

    def RenderOps(self, data):
        is_lea = self.name.startswith("lea")
        rex = 0
        if (data[0] & 0xf0) == 0x40:
            rex = data[0]
            data = data[1:]
        out = []
        for o in self.fields:
            if isinstance(o, str):
                out.append(o)
                continue
            assert isinstance(o, OP), f"unexpected {o} {type(o)}"

            if o is OP.MODRM_RM_REG or o is OP.MODRM_RM_XREG:
                r = data[self.modrm_pos] & 0x7
                if rex:
                    r |= (rex & 1) << 3
                if o is OP.MODRM_RM_REG:
                    out.append(_REG_NAMES[self.bit_width][r])
                else:
                     out.append(_XREG_NAMES[r])
            elif o is OP.MODRM_RM_BASE:
                if not is_lea:
                    out.append(f"MEM{self.bit_width}")
                r = data[self.modrm_pos] & 0x7
                if rex:
                    r |= (rex & 1) << 3
                out.append(_REG_NAMES_64[r])
            elif o is OP.MODRM_REG or o is OP.MODRM_XREG:
                r = (data[self.modrm_pos] >> 3) & 0x7
                if rex:
                    r |= (rex & 4) << 1
                if o is OP.MODRM_REG:
                    out.append(_REG_NAMES[self.bit_width][r])
                else:
                    out.append(_XREG_NAMES[r])
            elif o is OP.SIB_BASE:
                if not is_lea:
                    out.append(f"MEM{self.bit_width}")
                r = data[self.sib_pos] & 0x7
                if rex:
                    r |= (rex & 1) << 3
                out.append(_REG_NAMES_64[r])
            elif o is OP.SIB_INDEX:
                r = (data[self.sib_pos] >> 3) & 0x7
                if rex:
                    r |= (rex & 2) << 2
                out.append(_REG_NAMES_64[r])
            elif o is OP.SIB_SCALE:
                s = data[self.sib_pos] >> 6
                out.append(str(1 << s))
            elif o is OP.BYTE_WITH_REG:
                r = data[self.byte_with_reg_pos] & 0x7
                if rex:
                    r |= (rex & 1) << 3
                out.append(_REG_NAMES[self.bit_width][r])
            elif o is OP.IMM8:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 1, self.bit_width):x}")
            elif o is OP.IMM16:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 2, self.bit_width):x}")
            elif o is OP.IMM32:
                out.append(f"0x{GetSInt(data[self.imm_pos:], 4, self.bit_width):x}")
            elif o is OP.OFFABS8:
                out.append(f"0x{GetSInt(data[self.offset_pos:], 1, None):x}")
            elif o is OP.OFFABS32:
                out.append(f"0x{GetSInt(data[self.offset_pos:], 4, None):x}")
        return out


_SUPPORTED_PARAMS = {
    "/0", "/1", "/2", "/3", "/4", "/5", "/6", "/7",  #
    "/r",  #
    "REX.W",
    "ib", "iw", "id", "iq",  #
    "cd", "cb",
}

_RE_BYTE_VARIATIONS = re.compile("^[0-9A-F][0-9A-F]([+]r)?$")

_RE_BYTE = re.compile("^[0-9A-F][0-9A-F]$")
_RE_BYTE_WITH_REG = re.compile("^[0-9A-F][0-9A-F][+]r?$")


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

    for sib_mode in [SIB_MODE.SIMPLE, SIB_MODE.STD, SIB_MODE.NONE]:
        for mod in range(3):
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
    for sib_mode in [SIB_MODE.SIMPLE, SIB_MODE.STD, SIB_MODE.NONE]:
        for mod in range(3):
            opc = Opcode(name, "", ops, format)
            for x in encoding:
                if x == "REX.W":
                    opc.AddRexW()
                elif _RE_BYTE.match(x):
                    opc.AddByte(int(x, 16))
                elif x.startswith("/"):
                    ext = int(x[1:])
                    opc.AddMemOp(sib_mode, mod, ext=ext)
                elif x in {"ib", "iw", "id", "iq"}:
                    opc.AddImmOp(x)
                else:
                    assert False


def HandlePattern(name: str, ops: List[str], format: str, encoding: List[str], meta: List[str]):
    assert format in _SUPPORTED_FORMATS, f"bad format [{format}]"
    for f in encoding:
        assert f in _SUPPORTED_PARAMS or _RE_BYTE_VARIATIONS.match(f), f"bad parameter [{repr(f)}]"
    for o in ops:
        assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"

    assert len(format) == len(ops)
    for op, kind in zip(ops, format):
        assert op in _OP_MAP[kind], f"{op} {kind}"

    if format in {"MI", "M", "xM", "xxM", "Mx"}:
        before = []
        after = []
        seen_M = False
        for i, c in enumerate(format):
            if c == "M": seen_M = True
        if c == "x":
            if seen_M:
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
    elif format in {"I", "O", "OI", "xI"}:
        opc = Opcode(name, "", ops, format)
        before = []
        for i, c in enumerate(format):
            if c == "x":
                before.append(ops[i])
            else:
                break
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE_WITH_REG.match(x):
                opc.AddByteWithReg(int(x[0:2], 16))
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x in {"ib", "iw", "id", "iq"}:
                opc.fields += before
                opc.AddImmOp(x)
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
        assert False


def ExtractOps(s):
    def clean(o):
        o = o.replace("<", "").replace(">", "")
        if o[0:2] in _OPERAND_MODIFIERS:
            return o[2:]
        return o

    return [clean(x) for x in s.replace(", ", ",").split(",") if x]


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


def FixupFormat(format: str, ops: List, encoding):
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

def SkipInstruction(format, ops):
    if format == "MI" and ops[0] == "r64":
        return True

    if format == "I" and ops[0] == "rax" and ops[1] == "ud":
        return True
    return False


def CreateOpcodes(instructions: List):
    count = collections.defaultdict(int)
    for name, ops, format, encoding, metadata in instructions:
        ops = ExtractOps(ops)
        if (name not in _SUPPORTED_OPCODES or IsDisallowExtension(metadata) or
                ContainsUnsupportedOperands(ops)):
            continue
        if SkipInstruction(format, ops):
            continue
        count[name] += 1
        metadata = metadata.split()
        encoding = encoding.split()
        # hack
        format = FixupFormat(format, ops, encoding)
        assert format in _SUPPORTED_FORMATS

        print(name, ops, format, encoding, metadata)
        HandlePattern(name, ops, format, encoding, metadata)
    for k in _SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
    for opcode in Opcode.Opcodes:
        opcode.Finalize()
    OpcodeSanityCheck(Opcode.Opcodes)


def FindMatchingRule(data, rules: List[Opcode]) -> Optional[Opcode]:
    if (data[0] & 0xf0) == 0x40:
        data = data[1:]
    discriminant = int.from_bytes(data, "little")
    for r in rules:
        if (r.discriminant_mask & discriminant) == r.discriminant_data:
            return r
    return None


def ExtractObjdumpOps(ops_str):
    ops_str = ops_str.split("<")[0]
    ops_str = ops_str.replace("-0x", "+0x-")
    ops_str = ops_str.replace("XMMWORD PTR ", "MEM128,")
    ops_str = ops_str.replace("QWORD PTR ", "MEM64,")
    ops_str = ops_str.replace("DWORD PTR ", "MEM32,")
    ops_str = ops_str.replace("BYTE PTR ", "MEM8,")
    ops_str = ops_str.replace("WORD PTR ", "MEM16,")
    ops_str = ops_str.strip().replace("[", "").replace("]", "")
    return [o for o in re.split("[,+*]", ops_str) if o]


# _SUPPORTED_OPCODES = {"mov"}


if __name__ == "__main__":
    # This file is file https://github.com/asmjit/asmdb (see file comment)
    _START_MARKER = "// ${JSON:BEGIN}"
    _END_MARKER = "// ${JSON:END}"
    data = open("x86data.js").read()
    start = data.find(_START_MARKER) + len(_START_MARKER)
    end = data.find(_END_MARKER)

    X86_DATA = json.loads(data[start:end])

    CreateOpcodes(X86_DATA["instructions"])
    print(f"TOTAL instruction templates: {len(Opcode.Opcodes)}")
    HashTab = collections.defaultdict(list)

    def MakeHashName(data):
        i = 0
        name = ""
        if (data[0] & 0xf0) == 0x40:
            if (data[0] & 8) == 8:
                name += ".rexw"
            i += 1
        if data[i] == 0x66:
            name += ".66"
            i += 1
        if data[i] == 0xf2 or data[i] == 0xf3:
            name += f".{data[i]:02x}"
            i += 1
        if data[i] == 0x0f:
            name += ".0f"
            i += 1
        return name + f".{data[i]:02x}"


    for opc in Opcode.Opcodes:
        assert isinstance(opc, Opcode)
        name = ""
        data = opc.data
        mask = opc.data
        i = 0
        if opc.rexw:
            name += ".rexw"
        if data[i] == 0x66:
            name += ".66"
            i += 1
        if data[i] == 0xf2 or data[i] == 0xf3:
            name += f".{data[i]:02x}"
            i += 1
        if data[i] == 0x0f:
            name += ".0f"
            i += 1

        if i == opc.byte_with_reg_pos:
            for r in range(8):
                HashTab[name + f".{data[i] + r:02x}"].append(opc)
        else:
            HashTab[name + f".{data[i]:02x}"].append(opc)

    if False:
        for k, v in HashTab.items():
            if v:
                print(f"{k:10} {len(v)}")

    # data must be generated with: objdump -d  -M intel  --insn-width=10
    # and looks like:
    # 6f03b9:	4c 03 7e e8                   	add    r15,QWORD PTR [rsi-0x18]
    n = 0
    bad = 0
    skipped = 0
    mismatch = 0
    for line in sys.stdin:
        try:
            addr_str, data_str, ins_str = line.strip().split("\t")
        except:
            continue
        name = ins_str.split()[0]
        if name not in _SUPPORTED_OPCODES:
            skipped += 1
            continue
        if "fs:" in ins_str or "dh," in ins_str or "ch," in ins_str:
            skipped += 1
            continue

        data = [int(d, 16) for d in data_str.split()]
        if data[0] in {0x66, 0xf2, 0xf3} and (data[1] & 0xf0) == 0x40:
            data[0], data[1] = data[1], data[0]
        candidates = HashTab[MakeHashName(data)]
        # print (addr_str, data_str, ins_str)
        if not candidates:
            print(f"BAD [{MakeHashName(data)}]  {line}", end="")
            bad += 1
            continue
        opc = FindMatchingRule(data, candidates)
        if not opc:
            print(f"BAD [{MakeHashName(data)}]  {line}", end="")
            bad += 1
            continue

        if "[rip+" in line:
            continue

        assert name == opc.name
        if opc.fields == [OP.OFFPCREL32] or opc.fields == [OP.OFFPCREL8]:
            continue
        expected_ops = ExtractObjdumpOps(ins_str[len(name):])
        actual_ops = opc.RenderOps(data)
        if expected_ops != actual_ops:
            if True:
                # print (addr_str, data_str, ins_str)
                # print(f"EXPECTED: {expected_ops}")
                # print(f"ACTUAL:   {actual_ops}")
                mismatch += 1
            else:
                print(line)
                print(f"EXPECTED: {expected_ops}")
                print(f"ACTUAL:   {actual_ops}")
                print(f"OPCODE: {opc}")
                print(Hexify(opc.data))
                print(Hexify(opc.mask))
                exit()
        else:
            pass
            # print(line, end="")

        n += 1
    print(f"CHECKED: {n}   BAD: {bad}   SKIPPED: {skipped}  MISMATCHED: {mismatch}")
