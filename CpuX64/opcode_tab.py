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
    # "jmp", # waiting for bug fix in asmdb
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
    "OI",  # mov ['w:r8', 'ib/ub'] I ['B0+r', 'ib'] etc
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
    BYTE_REG = 13


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

    def __init__(self, name: str, variant: str, operands: List, bit_width: int):
        Opcode.Opcodes.append(self)
        self.name: str = name
        self.variant: str = variant
        self.operands = operands
        self.bit_width: int = bit_width

        self.discriminant_mask: int = 0
        self.discriminant_data: int = 0
        #
        self.rex_pos = -1
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
        hex_str = " ".join(f"{b:02x}" for b in self.data)
        return f"{self.name}.{self.variant} [' '.join({self.operands})] {hex_str}"

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
        self.rex_pos = len(self.data)
        self.data.append(0x48)
        self.mask.append(0xf8)

    def AddByte(self, b: int):
        self.data.append(b)
        self.mask.append(0xff)

    def AddByteWithReg(self, b: int):
        self.byte_with_reg_pos = len(self.data)
        self.fields.append(OP.BYTE_REG)
        self.data.append(b)
        self.mask.append(0xf8)
        assert (b & 0xf8) == b

    def AddReg(self):
        self.fields.append(OP.MODRM_RM_REG)

    def AddRegOpExt(self, ext: int):
        self.modrm_pos = len(self.data)
        mask = 0xf8
        data = (3 << 6) | (ext << 3)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OP.MODRM_RM_REG)

    def AddRegOpReg(self):
        self.modrm_pos = len(self.data)
        mask = 0xc0
        data = (3 << 6)
        self.mask.append(mask)
        self.data.append(data)
        self.fields.append(OP.MODRM_RM_REG)

    def AddMemOpCommonTail(self, mod: int):
        if mod == 0:
            pass
        elif mod == 1:
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFABS8)
            self.mask += [0]
            self.data += [0]
        elif mod == 2:
            self.offset_pos = len(self.data)
            self.fields.append(OP.OFFABS32)
            self.mask += [0, 0, 0, 0]
            self.data += [0, 0, 0, 0]

    def AddMemOpExt(self, use_sib: bool, mod: int, ext: int):
        self.modrm_pos = len(self.data)
        assert mod <= 2
        assert ext <= 7
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
            self.mask.append(mask)
            self.data.append(data)
            self.fields.append(OP.MODRM_RM_BASE)
        self.AddMemOpCommonTail(mod)

    def AddMemOpReg(self, use_sib: bool, mod: int):
        self.modrm_pos = len(self.data)
        mask = 0xc0
        data = (mod << 6)
        if use_sib:
            mask |= 0x7
            data |= 0x4
            self.mask.append(mask)
            self.data.append(data)
            self.sib_pos = len(self.data)
            self.fields += [OP.SIB_BASE, OP.SIB_INDEX, OP.SIB_SCALE]
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
    },
    "D": {"rel8", "rel32"},
    "O": {"r8", "r16", "r32", "r64"},
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

_RE_BYTE_VARIATIONS = re.compile("^[0-9A-F][0-9A-F]([+]r)?$")

_RE_BYTE = re.compile("^[0-9A-F][0-9A-F]$")
_RE_BYTE_WITH_REG = re.compile("^[0-9A-F][0-9A-F][+]r?$")


def HandlePatternMR(name: str, ops, bit_width: int, inv: bool):
    opc = Opcode(name, "reg", ops, bit_width)
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

    for use_sib in [True, False]:
        for mod in range(3):
            variant = "sib_" if use_sib else ""
            if mod == 1:
                variant += "off8"
            if mod == 2:
                variant += "off32"
            opc = Opcode(name, variant, ops, bit_width)
            for x in encoding:
                if x == "REX.W":
                    opc.AddRexW()
                elif _RE_BYTE.match(x):
                    opc.AddByte(int(x, 16))
                elif x == "/r":
                    if inv:
                        opc.AddReg()
                        opc.AddMemOpReg(use_sib, mod)
                    else:
                        opc.AddMemOpReg(use_sib, mod)
                        opc.AddReg()
                elif x in {"ib", "iw", "id", "iq"}:
                    opc.AddImmOp(x)
                else:
                    assert False


def HandlePatternMI(name: str, ops, bit_width: int, before, after):
    opc = Opcode(name, "reg", ops, bit_width)
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
    for use_sib in [True, False]:
        for mod in range(3):
            variant = "sib_" if use_sib else ""
            if mod == 1:
                variant += "off8"
            if mod == 2:
                variant += "off32"
            opc = Opcode(name, variant, ops, bit_width)
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
        assert f in _SUPPORTED_PARAMS or _RE_BYTE_VARIATIONS.match(f), f"bad parameter [{repr(f)}]"
    for o in ops:
        assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"

    bit_width = GetBitwidth(ops)
    assert len(format) == len(ops)
    for op, kind in zip(ops, format):
        assert op in _OP_MAP[kind], f"{op} {kind}"

    if format in {"MI", "M", "xM", "xxM", "Mx"}:
        before = []
        after  = []
        seen_M = False
        for i, c in enumerate(format):
           if c == "M": seen_M = True
        if c == "x":
            if seen_M:
                after.append(ops[i])
            else:
                before.append(ops[i])
        HandlePatternMI(name, ops, bit_width, before, after)
    elif format == "MR":
        HandlePatternMR(name, ops, bit_width, inv=False)
    elif format == "RM" or format == "RMI":
        HandlePatternMR(name, ops, bit_width, inv=True)
    elif format == "":
        opc = Opcode(name, "", ops, bit_width)
        for x in encoding:
            if _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            else:
                assert False
    elif format in {"I", "O", "OI"}:
        opc = Opcode(name, "", ops, bit_width)
        for x in encoding:
            if x == "REX.W":
                opc.AddRexW()
            elif _RE_BYTE_WITH_REG.match(x):
                opc.AddByteWithReg(int(x[0:2], 16))
            elif _RE_BYTE.match(x):
                opc.AddByte(int(x, 16))
            elif x in {"ib", "iw", "id", "iq"}:
                opc.AddImmOp(x)
            else:
                assert False
    elif format == "D":
        opc = Opcode(name, "", ops, bit_width)
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
        patterns[(opcode.discriminant_mask, opcode.discriminant_data)].append(opcode)
    print (f"Checkin Opcodes for conflicts")
    for k, opcodes in patterns.items():
        if len(opcodes) == 1: continue
        for o in opcodes:
            print (o)
        print ()

    print (f"Checkin Opcodes for overlap")
    for a, b in itertools.combinations(opcodes, 2):
        c = a.discriminant_mask & b.discriminant_mask
        assert (a.discriminant_data & c) != (b.discriminant_data & c)

# _SUPPORTED_OPCODES = {"add"}

if __name__ == "__main__":
    # This file is file https://github.com/asmjit/asmdb (see file comment)
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
        if format == "MI" and ops[0] == "r64":
            # this excludes:
            # "and", "X:r64, ud", "MI"      , "81 /4 id"
            continue
        count[name] += 1
        metadata = metadata.split()
        encoding = encoding.split()
        # hack
        if format == "I" and ("B8+r" in encoding or "B0+r" in encoding):
            format = "OI"
        if format == "NONE":
            format = ""

        if len(format) != len(ops):
            assert len(format) == 1
            format = "".join([("x" if o in _IMPLICIT_OPERANDS else format)
                              for o in ops])
            print(format, name)
        assert format in _SUPPORTED_FORMATS

        print(name, ops, format, encoding, metadata)
        HandlePattern(name, ops, format, encoding, metadata)
    for k in _SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
    print(f"TOTAL instruction templates: {len(Opcode.Opcodes)}")
    for opcode in Opcode.Opcodes:
        opcode.Finalize()
    OpcodeSanityCheck(Opcode.Opcodes)
    HashTab = collections.defaultdict(list)
    for opc in Opcode.Opcodes:
        assert isinstance(opc, Opcode)
        name = ""
        data = opc.data
        mask = opc.data
        i = 0
        if opc.rex_pos >= 0:
            name += ".rex"
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

        if i == opc.byte_with_reg_pos:
            for r in range(8):
                HashTab[name + f".{data[i] + r:02x}"].append(opcode)
        else:
            HashTab[name +  f".{data[i]:02x}"].append(opcode)


    # for k, v in HashTab.items():
    #    if v:
    #        print (f"{k:10} {len(v)}")

