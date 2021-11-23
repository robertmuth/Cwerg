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

X86_DATA = None

# list of opcodes we expect to use during X64 code generation
_SUPPORTED_OPCODES = {
    "add", "sub",  #
    "or", "and", "xor",  #
    "sar", "shr", "shl/sal",  #
    "imul", "mulss", "mulsd",  #
    "div", "idiv", "divss", "divsd",  #
    "mov",  #
    "movsx",  #
    "movzx",  #
    "movaps", "movapd",  #
    "neg",  #
    "cvtss2sd", "cvtss2si",  #
    "cvtsd2ss", "cvtsd2si",  #
    "cvtsi2ss", "cvtsi2sd",  #
    "cvttss2si", "cvttsd2si",  #
    "test",  #
    "cmp",  #
    "lea",  #
    "popcnt",  #
    "pop", "push",  #
    "ucomiss", "ucomisd",
    "call", "ret", "syscall",
    "jle/jng", "jne/jnz", "jge/jnl",  # many missing
}

# opcode extension/flavors we do not support for now
_DISALLOWED_EXTENSIONS = {
    "Deprecated",
    "AltForm",
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


_SUPPORTED_OPERANDS = {
    "1",  #
    "creg", "dreg", "sreg", "cl",  #
    "al", "ax", "eax", "rax",  #
    "dx", "edx", "rdx",  #
    "r8", "r16", "r32", "r64",  #
    "~r8", "~r16", "~r32", "~r64",  #
    "r8/m8", "r16/m16", "r32/m32", "r64/m64",  #
    "r32/m16", "r64/m16",  #
    "~r8/m8", "~r16/m16", "~r32/m32", "~r64/m64",  #
    "xmm[31:0]", "xmm[63:0]",  #
    "xmm[31:0]/m32", "xmm[63:0]/m64",  #
    "xmm/m128", "xmm",  #
    "ib/ub", "iw/uw", "id/ud", "iq/uq",  #
    "id", "ib", "ud", "iw", "uw",  #
    "rel8", "rel16", "rel32",  #
    "mem",  #
}

_UNSUPPORTED_OPERANDS = {
    "moff8", "moff16", "moff32", "moff64",  #
    "fs", "gs",
}


def ContainsUnsupportedOperands(ops):
    for o in ops:
        if o in _UNSUPPORTED_OPERANDS:
            return True
    return False


_IMPLICIT_OPERANDS = {
    "al", "ax", "eax", "rax",
    "dx", "edx", "rdx",  #
    "cl",
}


def GetBitwidth(ops):
    if not ops:
        return 0
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
        if ops[1].endswith("8"):
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
    "rI",  # mov ['w:r8', 'ib/ub'] I ['B0+r', 'ib'] etc
    "xM",  # div ['ax', 'r8/m8'] xM ['F6', '/6']
    "xxM",  # div ['dx', 'ax', 'r16/m16'] xxM
    "Mx",  # sar ['r8/m8', 'cl'] Mx
}


@enum.unique
class OP(enum.Enum):
    """
    """
    MODRM_RM_REG = 1
    MODRM_RM_BASE = 2
    OFFSET8 = 3
    OFFSET32 = 4
    SIB_SCALE = 5
    SIB_INDEX = 6
    SIB_BASE = 7
    IMM8 = 8
    IMM16 = 9
    IMM32 = 32


@dataclasses.dataclass()
class Opcode:
    name: str
    variant: str
    bit_width: int

    bit32_mask: int = 0
    bit32_value: int = 0
    #
    rex_pos = 0
    modrm_pos = 0
    sib_pos = 0
    offset_pos = 0
    imm_pos = 0
    #
    fields: List = dataclasses.field(default_factory=list)
    mask: List = dataclasses.field(default_factory=list)
    data: List = dataclasses.field(default_factory=list)

    def AddRexW(self):
        self.rex_pos = len(self.data)
        self.data.append(0x48)
        self.mask.append(0xf8)

    def AddByte(self, b: int):
        self.data.append(b)
        self.mask.append(0xff)

    def AddRegOpExt(self, ext: int):
        self.modrm_pos = len(self.data)
        mask = 0xf8
        data = (3 << 6) | (ext << 3)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OP.MODRM_RM_REG)


    def AddMemOpExt(self, use_sib: bool, mod: int, ext: int):
        self.modrm_pos = len(self.data)
        mask = 0xf8
        data = (mod << 6) | (ext << 3)
        if use_sib:
            mask |= 0x7
            data |= 0x4
            self.mask.append(mask)
            self.data.append(data)
            self.sib_pos = len(self.data)
            self.fields += [OP.SIB_BASE, OP.SIB_INDEX, OP.SIB_SCALE]
        else:
            self.fields.append(OP.MODRM_RM_BASE)

        if mod == 0:
            pass
        elif mod == 1:
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFSET8)
            self.mask += [0]
            self.data += [0]
        elif mod == 2:
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFSET32)
            self.mask += [0, 0, 0, 0]
            self.data += [0, 0, 0, 0]

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
        "r8/m8", "r16/m16", "r32/m32", "r64/m64", "r64",
        "~r8/m8", "~r16/m16", "~r32/m32", "~r64/m64",
        "r32/m16", "r64/m16",
        "mem",
        "xmm[31:0]/m32", "xmm[63:0]/m64", "xmm/m128",
        # "sreg", "creg", "dreg",
        # "xmm",
    },
    "D": {"rel8", "rel32"},
    "O": {"r16", "r32", "r64"},
    "x": _IMPLICIT_OPERANDS,
    "r": {"r8", "r16", "r32", "r64"},
}

_SUPPORTED_PARAMS = {
    "/0", "/1", "/2", "/3", "/4", "/5", "/6", "/7",  #
    "/r",  #
    "REX.W",
    "ib", "iw", "id", "iq",  #
    "cd", "cb",
}

_RE_BYTE = re.compile("^[0-9A-F][0-9A-F]([+]r)?$")



def HandlePatternMI(name: str, bit_width: int):
    opc = Opcode(name, "reg", bit_width)
    for x in encoding:
        if x == "REX.W":
            opc.AddRexW()
        elif _RE_BYTE.match(x):
            opc.AddByte(int(x, 16))
        elif x.startswith("/"):
            ext = int(x[1:])
            opc.AddRegOpExt(ext)
        elif x in {"ib", "iw", "id", "iq"}:
            opc.AddImmOp(x)
        else:
            assert False

    # 81 7c 24 28 ff 0f 00    cmp    DWORD PTR [rsp+0x28],0xfff
    for use_sib in [True, False]:
        for mod in range(3):
            variant = "sib_" if use_sib else ""
            if mod == 1:
                variant += "off8"
            if mod == 2:
                variant += "off32"
            opc = Opcode(name, variant, bit_width)
            for x in encoding:
                if x == "REX.W":
                    opc.AddRexW()
                elif _RE_BYTE.match(x):
                    opc.AddByte(int(x, 16))
                elif x.startswith("/"):
                    ext = int(x[1:])
                    opc.AddMemOpExt(use_sib, mod, ext)
                elif x in {"ib", "iw", "id", "iq"}:
                    opc.AddImmOp(x)
                else:
                    assert False

def HandlePattern(name: str, ops: List[str], format: str, encoding: List[str], meta: List[str]):
    assert format in _SUPPORTED_FORMATS, f"bad format [{format}]"
    for f in encoding:
        assert f in _SUPPORTED_PARAMS or _RE_BYTE.match(f), f"bad parameter [{repr(f)}]"
    for o in ops:
        assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"

    bit_width = GetBitwidth(ops)
    assert len(format) == len(ops)
    for op, kind in zip(ops, format):
        assert op in _OP_MAP[kind], f"{op} {kind}"

    if format == "MI":
        HandlePatternMI(name, bit_width)

    elif format == "I":
        opc = Opcode(name, "", bit_width)
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x in {"ib", "iw", "id", "iq"}:
                opc.AddImmOp(x)
            else:
                assert False
    else:
        pass
        #assert Falde


def ExtractOps(s):
    def clean(o):
        o = o.replace("<", "").replace(">", "")
        if o[0:2] in _OPERAND_MODIFIERS:
            return o[2:]
        return o

    return [clean(x) for x in s.replace(", ", ",").split(",") if x]


if __name__ == "__main__":
    _START_MARKER = "// ${JSON:BEGIN}"
    _END_MARKER = "// ${JSON:END}"
    data = open("x86data.js").read()
    start = data.find(_START_MARKER) + len(_START_MARKER)
    end = data.find(_END_MARKER)

    X86_DATA = json.loads(data[start:end])
    count = collections.defaultdict(int)
    for name, ops, format, encoding, metadata in X86_DATA["instructions"]:
        ops = ExtractOps(ops)
        if (name not in _SUPPORTED_OPCODES or IsDisallowExtension(metadata) or
                ContainsUnsupportedOperands(ops)):
            continue
        if format == "MI" and ops[0] == "X:r64":
            # this excludes:
            # "and", "X:r64, ud", "MI"      , "81 /4 id"
            continue
        count[name] += 1
        metadata = metadata.split()
        encoding = encoding.split()
        if format == "I" and ("B8+r" in encoding or "B0+r" in encoding):
            format = "rI"
        if format == "NONE":
            format = ""

        #if format not in  {"MI", "I"}:
        #    continue

        if len(format) != len(ops):
            assert len(format) == 1
            format = "".join([("x" if o in _IMPLICIT_OPERANDS else format)
                              for o in ops])
        print(name, ops, format, encoding, metadata)
        HandlePattern(name, ops, format, encoding, metadata)
    for k in _SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
