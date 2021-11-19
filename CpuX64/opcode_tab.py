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
import json

X86_DATA = None
SUPPORTED_OPCODES2 = {
    "sar",
}

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
    "neg", #
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
    "jle/jng", "jne/jnz", "jge/jnl",   # many missing
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

_OPERAND_MODIFIERS = {
    "x:",
    "X:",
    "w:",
    "W:",
    "R:"
}


def HandlePattern(name, ops: List[str], format, encoding: List[str], meta: List[str]):
    for o in ops:
        if o[0:2] in _OPERAND_MODIFIERS:
            assert o[2:] in _SUPPORTED_OPERANDS
        else:
            assert o in _SUPPORTED_OPERANDS, f"unexpected operand: [{o}]"


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
        ops = ops.replace(", ", ",").split(",")
        ops = [o for o in ops if o]
        print(name, ops, format, encoding.split(), metadata.split())
        HandlePattern(name, ops, format, encoding.split(), metadata.split())
    for k in _SUPPORTED_OPCODES:
        assert count[k], f"unknown opcode [{k}]"
