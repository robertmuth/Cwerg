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

# _SUPPORTED_OPCODES = { "add" }

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
    "fs", "gs",  #
    "al", "ax", "eax", "rax", "<ax>", "<eax>", "<rax>",  #
    "<dx>", "<edx>", "<rdx>",  #
    "r8", "r16", "r32", "r64",  #
    "~r8", "~r16", "~r32", "~r64",  #
    "r8/m8", "r16/m16", "r32/m32", "r64/m64",  #
    "r32/m16", "r64/m16",  #
    "~r8/m8", "~r16/m16", "~r32/m32", "~r64/m64",  #
    "xmm[31:0]", "xmm[63:0]",  #
    "xmm[31:0]/m32", "xmm[63:0]/m64",  #
    "xmm/m128", "xmm",  #
    "moff8", "moff16", "moff32", "moff64",  #
    "ib/ub", "iw/uw", "id/ud", "iq/uq",  #
    "id", "ib", "ud", "iw", "uw",  #
    "rel8", "rel16", "rel32",  #
    "mem",  #
}

_SUPPORTED_PARAMS = {
    "/0", "/1", "/2", "/3", "/4", "/5", "/6", "/7",  #
    "/r",  #
    "REX.W",
    "ib", "iw", "id", "iq",  #
    "cd", "cb",
}

_RE_BYTE = re.compile("[0-9A-F][0-9A-F]")

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
    "NONE",
}


@dataclasses.dataclass()
class Opcode:
    name: str
    bit_width: int
    len: int
    bit32_mask: int
    bit32_value: int
    fields: List


def HandlePattern(name, ops: List[str], format: str, encoding: List[str], meta: List[str]):
    assert format in _SUPPORTED_FORMATS, f"bad format [{format}]"
    for f in encoding:
        assert f in _SUPPORTED_PARAMS or _RE_BYTE.match(f), f"bad parameter [{repr(f)}]"
    for o in ops:
        if o[0:2] in _OPERAND_MODIFIERS:
            assert o[2:] in _SUPPORTED_OPERANDS
        else:
            assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"


def SplitStringComma(s):
    return [x for x in s.replace(", ", ",").split(",") if x]

if __name__ == "__main__":
    _START_MARKER = "// ${JSON:BEGIN}"
    _END_MARKER = "// ${JSON:END}"
    data = open("x86data.js").read()
    start = data.find(_START_MARKER) + len(_START_MARKER)
    end = data.find(_END_MARKER)

    X86_DATA = json.loads(data[start:end])
    count = collections.defaultdict(int)
    for name, ops, format, encoding, metadata in X86_DATA["instructions"]:
        if name not in _SUPPORTED_OPCODES or IsDisallowExtension(metadata):
            continue
        count[name] += 1
        ops = SplitStringComma(ops)
        metadata = metadata.split()
        encoding = encoding.split()
        print(name, ops, format, encoding, metadata)
        HandlePattern(name, ops, format, encoding, metadata)
    for k in _SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
