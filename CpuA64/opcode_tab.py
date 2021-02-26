#!/usr/bin/python3

"""
ARM 64bit assembler + disassembler + side-effects table



"""
from Util import cgen

from typing import List, Dict, Tuple, Optional, Set

import collections
import dataclasses
import enum
import re
import sys

_DEBUG = False

# ldr_reg requires 7 operands:  [PRED, DST, ADD_MODE, BASE, SHIFT_MODE, INDEX, OFFSET]
MAX_OPERANDS = 7

MAX_BIT_RANGES = 4


def Bits(*patterns) -> Tuple[int, int]:
    """
    combines are list of triples into a single triple
    """
    m = 0
    v = 0
    # print("")
    for mask, val, pos in patterns:
        # print(f"@@ {v:x}/{m:x}   - ({mask}, {val}, {pos})")
        mask <<= pos
        val <<= pos
        assert m & mask == 0, f"mask overlap {m:x} {mask:x}"
        m |= mask
        v |= val
    # print ("<- %x %x" % (m, v))
    return m, v


def ExtractBits(data, mask) -> int:
    out = 0
    pos = 1
    # print ("@@ %x %x" % (data, mask))
    while mask:
        new_mask = mask & (mask - 1)
        bit = mask ^ new_mask
        if bit & data:
            out |= pos
        pos <<= 1
        mask = new_mask
    # print ("@@ %x" % out)
    return out


def SignedIntFromBits(data, n_bits) -> int:
    mask = (1 << n_bits) - 1
    data &= mask
    if data & (1 << (n_bits - 1)):
        return data - (1 << n_bits)
    else:
        return data


def BitsFromSignedInt(n_bits, x) -> int:
    if x < 0:
        x = (1 << n_bits) + x
    assert x < (1 << n_bits)
    return x


# P/p: pre/post
# U/u: add/sub
# W/w: wb/-
# Note: post+wb no allowed
@enum.unique
class ADDR_MODE(enum.IntEnum):
    puw = 0
    puW = 1
    pUw = 2
    pUW = 3
    Puw = 4
    PuW = 5
    PUw = 6
    PUW = 7


@enum.unique
class SHIFT(enum.IntEnum):
    lsl = 0
    lsr = 1
    asr = 2
    ror_rrx = 3


############################################################
# OK (operand kind) denotes a set of bit in an instruction
# word the constitute an operand. The bits are not necessarily contiguous
# OK maybe further split up in bit ranges which are contiguous.
############################################################
@enum.unique
class OK(enum.Enum):
    Invalid = 0
    # registers
    WREG_0_4 = 1
    WREG_5_9 = 2
    WREG_10_14 = 3
    WREG_16_20 = 4

    XREG_0_4 = 5
    XREG_5_9 = 6
    XREG_10_14 = 7
    XREG_16_20 = 8

    SREG_0_4 = 9
    SREG_5_9 = 10
    SREG_10_14 = 11
    SREG_16_20 = 12

    DREG_0_4 = 13
    DREG_5_9 = 14
    DREG_10_14 = 15
    DREG_16_20 = 16

    BREG_0_4 = 17
    BREG_5_9 = 18
    BREG_10_14 = 19
    BREG_16_20 = 20

    HREG_0_4 = 21
    HREG_5_9 = 22
    HREG_10_14 = 23
    HREG_16_20 = 24

    QREG_0_4 = 25
    QREG_5_9 = 26
    QREG_10_14 = 27
    QREG_16_20 = 28

    # unsigned immediates
    IMM_5_23 = 30
    IMM_10_21 = 31
    IMM_10_21_22_23 = 32
    IMM_10_15 = 33
    IMM_12_20 = 34
    IMM_10_15_16_22 = 35

    IMM_10_21_times_2 = 36
    IMM_10_21_times_4 = 37
    IMM_10_21_times_8 = 38
    IMM_19_23_31 = 39
    IMM_5_20 = 40
    IMM_16_22 = 41

    # signed immeditate
    SIMM_0_25 = 50
    SIMM_12_20 = 51
    SIMM_5_23 = 52
    SIMM_5_18 = 53
    SIMM_15_21_TIMES4 = 54
    SIMM_15_21_TIMES8 = 55
    SIMM_15_21_TIMES16 = 56
    SIMM_5_23_29_30 = 57

    # shifts
    SHIFT_22_23 = 60
    SHIFT_12_14_15_W = 61
    SHIFT_12_14_15_X = 62
    SHIFT_10_12_LIMIT4 = 63


############################################################
# effects of an opcode wrt the status registers
# Note, the for instructions with the fCC_UPDATE_20 the effect
# is gated on the "s" bit
############################################################
@enum.unique
class SR_UPDATE(enum.Enum):
    NONE = 0
    NZ = 1
    NCZ_PSR = 2
    NCZ = 4
    NCZV = 5


############################################################
# bit ranges are the building blocks of fields
# Each bit range specifies one or more consecutive bits
############################################################
@enum.unique
class BRK(enum.Enum):  # bit range kind

    Verbatim = 0
    Hi = 1
    Lo = 2
    Rotated = 3
    Signed = 4
    Times8 = 5
    Times4 = 6
    Times2 = 7
    Times2Plus4 = 8
    Force0 = 9
    Force1 = 10
    Force3 = 11
    Force6 = 12
    Force14 = 13
    U = 14
    W = 15
    P = 16


BIT_RANGE_MODIFIER_SINGLE: Set[BRK] = {
    BRK.Verbatim,
    BRK.Rotated,
    BRK.Signed,
    BRK.Times8,
    BRK.Times4,
    BRK.Times2,
    BRK.Times2Plus4,
    BRK.Force0,
    BRK.Force1,
    BRK.Force3,
    BRK.Force6,
    BRK.Force14,
}

BIT_RANGE_MODIFIER_HILO: Set[BRK] = {BRK.Hi, BRK.Lo}
BIT_RANGE_MODIFIER_ADDR: Set[BRK] = {BRK.P, BRK.U, BRK.W}
BIT_RANGE_MODIFIER = BIT_RANGE_MODIFIER_SINGLE | BIT_RANGE_MODIFIER_HILO | BIT_RANGE_MODIFIER_ADDR
BIT_RANGE = Tuple[BRK, int, int]

FIELDS_REG: Dict[OK, List[BIT_RANGE]] = {
    OK.WREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.WREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.WREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.WREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.XREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.XREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.XREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.XREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.SREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.SREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.SREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.SREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.DREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.DREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.DREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.DREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.BREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.BREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.BREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.BREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.HREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.HREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.HREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.HREG_16_20: [(BRK.Verbatim, 5, 16)],
    #
    OK.QREG_0_4: [(BRK.Verbatim, 5, 0)],
    OK.QREG_5_9: [(BRK.Verbatim, 5, 5)],
    OK.QREG_10_14: [(BRK.Verbatim, 5, 10)],
    OK.QREG_16_20: [(BRK.Verbatim, 5, 16)],
}

FIELDS_IMM: Dict[OK, List[BIT_RANGE]] = {
    OK.IMM_5_23: [(BRK.Verbatim, 19, 5)],
    OK.IMM_10_15: [(BRK.Verbatim, 6, 10)],
    OK.IMM_10_21: [(BRK.Verbatim, 12, 10)],
    OK.IMM_10_21_times_2: [(BRK.Verbatim, 12, 10)],
    OK.IMM_10_21_times_4: [(BRK.Verbatim, 12, 10)],
    OK.IMM_10_21_times_8: [(BRK.Verbatim, 12, 10)],
    OK.IMM_10_15_16_22: [(BRK.Verbatim, 13, 10)],
    OK.IMM_19_23_31: [(BRK.Lo, 5, 19), (BRK.Hi, 1, 31)],
    OK.IMM_5_20: [(BRK.Verbatim, 16, 5)],
    OK.IMM_16_22: [(BRK.Verbatim, 7, 16)],

    OK.SIMM_5_23: [(BRK.Verbatim, 19, 5)],
    OK.IMM_10_21_22_23: [(BRK.Verbatim, 14, 10)],
    OK.IMM_12_20: [(BRK.Verbatim, 9, 12)],
    OK.SIMM_12_20: [(BRK.Verbatim, 9, 12)],
    OK.SIMM_0_25: [(BRK.Verbatim, 26, 0)],
    OK.SIMM_5_18: [(BRK.Verbatim, 14, 5)],
    OK.SIMM_15_21_TIMES4: [(BRK.Verbatim, 7, 15)],
    OK.SIMM_15_21_TIMES8: [(BRK.Verbatim, 7, 15)],
    OK.SIMM_15_21_TIMES16: [(BRK.Verbatim, 7, 15)],
    OK.SIMM_5_23_29_30: [(BRK.Hi, 19, 5), (BRK.Lo, 2, 29)],
}

FIELDS_SHIFT: Dict[OK, List[BIT_RANGE]] = {
    OK.SHIFT_22_23: [(BRK.Verbatim, 2, 22)],
    OK.SHIFT_12_14_15_W: [(BRK.Hi, 2, 14), (BRK.Lo, 1, 12)],
    OK.SHIFT_12_14_15_X: [(BRK.Hi, 2, 14), (BRK.Lo, 1, 12)],
    OK.SHIFT_10_12_LIMIT4: [(BRK.Verbatim, 3, 10)]
}

# merge all dicts from above
FIELD_DETAILS: Dict[OK, List[BIT_RANGE]] = {
    **FIELDS_REG,
    **FIELDS_SHIFT,
    **FIELDS_IMM,
}

for details in FIELD_DETAILS.values():
    if len(details) == 1:
        assert details[0][0] in BIT_RANGE_MODIFIER_SINGLE
    elif len(details) == 2:
        assert details[0][0] in BIT_RANGE_MODIFIER_HILO
        assert details[1][0] in BIT_RANGE_MODIFIER_HILO
    elif len(details) == 3:
        assert details[0][0] in BIT_RANGE_MODIFIER_ADDR
        assert details[1][0] in BIT_RANGE_MODIFIER_ADDR
        assert details[2][0] in BIT_RANGE_MODIFIER_ADDR
    else:
        assert False

assert len(FIELD_DETAILS) <= 256


def DecodeOperand(operand_kind: OK, value: int) -> int:
    """ Decodes an operand into an int."""
    tmp = 0
    # hi before lo
    # p  before u before w
    for modifier, width, pos in FIELD_DETAILS[operand_kind]:
        mask = (1 << width) - 1
        x = (value >> pos) & mask
        if modifier is BRK.Verbatim:
            return x
        elif modifier is BRK.Hi or modifier is BRK.P:
            tmp = x
        elif modifier is BRK.Times8:
            return x * 8
        elif modifier is BRK.Times4:
            return x * 4
        elif modifier is BRK.Times2:
            return x * 2
        elif modifier is BRK.Times2Plus4:
            return x * 2 + 4
        elif modifier is BRK.U:
            tmp = (tmp << width) | x
        elif modifier is BRK.Lo or modifier is BRK.W:
            return (tmp << width) | x
        elif modifier is BRK.Force1:
            return 1
        elif modifier is BRK.Force0:
            return 0
        elif modifier is BRK.Force3:
            return 3
        elif modifier is BRK.Force6:
            return 6
        elif modifier is BRK.Force14:
            return 14
        elif modifier is BRK.Signed:
            return SignedIntFromBits(x, width)
        else:
            assert False, f"{modifier}"
    # occurs for operands with empty field lists, e.g. OK.REG_LINK
    return 0


def EncodeOperand(operand_kind, val) -> List[Tuple[int, int, int]]:
    """ Encodes an int into a list of bit-fields"""
    bits: List[Tuple[int, int, int]] = []
    # Note: going reverse is crucial to make Hi/Lo and P/U/W work
    for modifier, width, pos in reversed(FIELD_DETAILS[operand_kind]):
        mask = (1 << width) - 1
        if modifier is BRK.Verbatim:
            assert mask & val == val
            bits.append((mask, val, pos))
        elif modifier is BRK.Times8:
            assert val % 8 == 0
            bits.append((mask, val >> 3, pos))
        elif modifier is BRK.Times2:
            assert val % 2 == 0
            bits.append((mask, val >> 1, pos))
        elif modifier is BRK.Times2Plus4:
            assert val & 4 == 4
            assert val % 2 == 0
            bits.append((mask, (val - 4) >> 1, pos))
        elif modifier is BRK.Times4:
            assert val % 4 == 0
            bits.append((mask, val >> 2, pos))
        elif modifier is BRK.Lo or modifier is BRK.W:
            bits.append((mask, val & mask, pos))
            val = val >> width
        elif modifier is BRK.U:
            bits.append((mask, val & mask, pos))
            val = val >> width
        elif modifier is BRK.Hi or modifier is BRK.P:
            assert mask & val == val, f"{operand_kind} {val} {modifier} {mask:x}"
            bits.append((mask, val, pos))
        elif modifier in {BRK.Force0, BRK.Force1, BRK.Force3, BRK.Force6,
                          BRK.Force14}:
            pass
        elif modifier is BRK.Signed:
            bits.append((mask, BitsFromSignedInt(width, val), pos))
        else:
            assert False, f"unknown modifier {modifier}"
    return bits


############################################################
# opcode classes
# an opcode may belong to multiple classes
# TODO: these need a lot of love especially wrt side-effects
############################################################
@enum.unique
class OPC_FLAG(enum.Flag):
    RESULT_64BIT = 1 << 0
    SRC_DST_0_1 = 1 << 1
    DST_0_1 = 1 << 2

    DIV = 1 << 3
    MUL = 1 << 4
    MULACC = 1 << 5
    LOAD = 1 << 6
    STORE = 1 << 7
    ATOMIC = 1 << 8

    ALU = 1 << 9
    ALU1 = 1 << 10

    SIGNEXTEND = 1 << 11
    JUMP = 1 << 12
    LINK = 1 << 13
    THUMB = 1 << 14
    MOVETOSR = 1 << 15
    MOVEFROMSR = 1 << 16
    TEST = 1 << 17
    PREFETCH = 1 << 18
    MULTIPLE = 1 << 19
    VFP = 1 << 20
    SYSCALL = 1 << 21
    BYTEREORDER = 1 << 22
    MISC = 1 << 23
    X = 1 << 24
    W = 1 << 25
    # do not go above 31 as we want these to fit into a 32 bit word


# number of bytes accessed by a memory opcode (ld/st)
@enum.unique
class MEM_WIDTH(enum.Enum):
    NA = 0
    W1 = 1
    W2 = 2
    W4 = 3
    W8 = 4
    W12 = 5
    Variable = 6


_RE_OPCODE_NAME = re.compile(r"[a-z.0-9]+")

# We use the notion of variant to disambiguate opcodes with the same mnemonic
_VARIANTS = {
    "",
    "imm",
    "imm_8",
    "imm_16",
    "imm_32",
    "imm_64",
    "imm_128",
    #
    "reg_32",
    "reg_64",
    #
    "reg_32_8",
    "reg_32_16",
    "reg_32_32",
    "reg_32_64",
    "reg_32_128",
    "reg_64_8",
    "reg_64_16",
    "reg_64_32",
    "reg_64_64",
    "reg_64_128",
    #
    "imm_post",
    "imm_post_8",
    "imm_post_16",
    "imm_post_32",
    "imm_post_64",
    "imm_post_128",
    "imm_pre",
    "imm_pre_8",
    "imm_pre_16",
    "imm_pre_32",
    "imm_pre_64",
    "imm_pre_128",
    "32",
    "64",
    "reg",
}


class Opcode:
    """The primary purpose of of instantiating an Opcode is to register it with
    the class variable `name_to_opcode`
    """
    name_to_opcode: Dict[str, "Opcode"] = {}

    # the key in this map is what you get when you "and" and opcode with
    # _INS_CLASSIFIER
    # For FindOpcode to work the more specific patterns must precede
    # the less specific ones
    ordered_opcodes: List[List['Opcode']] = [[] for i in range(256)]

    def __init__(self, name: str, variant: str,
                 bits: List[Tuple[int, int, int]],
                 fields: List[OK],
                 classes: OPC_FLAG,
                 mem_width: MEM_WIDTH = MEM_WIDTH.NA,
                 sr_update: SR_UPDATE = SR_UPDATE.NONE):
        if _DEBUG:
            print(name)
        # assert variant in _VARIANTS, f"bad variant [{variant}]"
        assert _RE_OPCODE_NAME.match(name)
        for f in fields:
            assert f in FIELD_DETAILS, f"miss field to mask entry {f}"

        assert len(fields) <= MAX_OPERANDS

        bit_mask, bit_value = Bits(*bits)
        self.bit_mask = bit_mask
        self.bit_value = bit_value

        all_bits = bits[:]
        for f in fields:
            all_bits += [((1 << t[1]) - 1, 0, t[2])
                         for t in FIELD_DETAILS[f]]
        mask = Bits(*all_bits)[0]
        # make sure all 32bits are accounted for
        assert 0xffffffff == mask, f"instruction word not entirely covered {mask:08x}  {name}"

        self.name = name
        self.variant = variant

        enum_name = self.NameForEnum()
        assert enum_name not in Opcode.name_to_opcode, f"duplicate opcode {enum_name}"
        Opcode.name_to_opcode[enum_name] = self

        mask, value = Bits(*bits)

        if (bit_mask >> 24) == 0xff:
            Opcode.ordered_opcodes[bit_value >> 24].append(self)
        else:
            b = bit_value >> 24
            m_inv = ~(bit_mask >> 24)
            dont_care = set((m_inv & x) for x in range(256))
            for dc in dont_care:
                Opcode.ordered_opcodes[b | dc].append(self)

        self.fields: List[OK] = fields
        self.classes: OPC_FLAG = classes
        self.sr_update = sr_update
        self.mem_width = mem_width

    def __lt__(self, other):
        return (self.name, self.variant) < (other.name, other.variant)

    def NameForEnum(self):
        name = self.name
        if self.variant:
            name += "_" + self.variant
        return name.replace(".", "_")

    def AssembleOperands(self, operands: List[int]):
        assert len(operands) == len(
            self.fields), f"not enough operands for {self.NameForEnum()}"
        bits = [(self.bit_mask, self.bit_value, 0)]
        for f, o in zip(self.fields, operands):
            bits += EncodeOperand(f, o)
        bit_mask, bit_value = Bits(*bits)
        assert bit_mask == 0xffffffff, f"{self.name} BAD MASK {bit_mask:08x}"
        return bit_value

    def DisassembleOperands(self, data: int) -> List[int]:
        assert data & self.bit_mask == self.bit_value
        return [DecodeOperand(f, data)
                for f in self.fields]

    @classmethod
    def FindOpcode(cls, data: int) -> Optional["Opcode"]:
        for opcode in Opcode.ordered_opcodes[data >> 24]:
            if data & opcode.bit_mask == opcode.bit_value:
                return opcode
        return None


########################################
root010 = (7, 2, 26)
########################################
for ext, w_flag, w_bit in [("w", OPC_FLAG.W, (1, 0, 31)), ("q", OPC_FLAG.X, (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if ext == "q" else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if ext == "q" else OK.WREG_16_20
    dst2_reg = OK.XREG_10_14 if ext == "q" else OK.WREG_10_14

    for name, bits in [("add", [(3, 0, 29), (3, 3, 24), (1, 0, 21)]),
                       ("and", [(3, 0, 29), (3, 2, 24), (1, 0, 21)]),
                       ("bic", [(3, 0, 29), (3, 2, 24), (1, 1, 21)]),
                       ("sub", [(3, 2, 29), (3, 3, 24), (1, 0, 21)]),
                       ("orr", [(3, 1, 29), (3, 2, 24), (1, 0, 21)]),
                       ("orn", [(3, 1, 29), (3, 2, 24), (1, 1, 21)]),
                       ("eor", [(3, 2, 29), (3, 2, 24), (1, 0, 21)]),
                       ("eon", [(3, 2, 29), (3, 2, 24), (1, 1, 21)])]:
        Opcode(name, ext + "_reg", [root010, w_bit] + bits,
               [dst_reg, src1_reg, OK.SHIFT_22_23, src2_reg, OK.IMM_10_15], w_flag)

    for name, bits in [("adds", [(3, 1, 29), (3, 3, 24), (1, 0, 21)]),
                       ("ands", [(3, 3, 29), (3, 2, 24), (1, 0, 21)]),
                       ("bics", [(3, 3, 29), (3, 2, 24), (1, 1, 21)]),
                       ("subs", [(3, 3, 29), (3, 3, 24), (1, 0, 21)])]:
        Opcode(name, ext + "_reg", [root010, w_bit] + bits,
               [dst_reg, src1_reg, OK.SHIFT_22_23, src2_reg, OK.IMM_10_15], w_flag, SR_UPDATE.NZ)

    for ext2, option in [("b", (7, 0, 13)), ("h", (7, 1, 13)), ("w", (7, 2, 13)), ("q", (7, 3, 13)),
                         ("sb", (7, 4, 13)), ("sh", (7, 5, 13)), ("sw", (7, 6, 13)), ("sq", (7, 7, 13))]:
        for name, bits in [
            ("add", [(3, 0, 29), (0x1f, 0x19, 21)]),
            ("sub", [(3, 2, 29), (0x1f, 0x19, 21)]),
        ]:
            Opcode(name, ext + "_reg_" + ext2, [root010, w_bit, option] + bits,
                   [dst_reg, src1_reg, OK.SHIFT_10_12_LIMIT4, src2_reg], w_flag)
        for name, bits in [
            ("adds", [(3, 1, 29), (0x1f, 0x19, 21)]),
            ("subs", [(3, 3, 29), (0x1f, 0x19, 21)]),
        ]:
            Opcode(name, ext + "_reg_" + ext2, [root010, w_bit, option] + bits,
                   [dst_reg, src1_reg, OK.SHIFT_10_12_LIMIT4, src2_reg], w_flag, SR_UPDATE.NZ)

for ext, w_bit in [("q", (7, 6, 29)), ("w", (7, 4, 29)), ("h", (7, 2, 29)), ("b", (7, 0, 29))]:
    reg = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    Opcode("ldxr" + ext, "", [w_bit, root010, (0xffff, 0x17df, 10)],
           [reg, OK.XREG_5_9], w_flag, SR_UPDATE.NONE)
    Opcode("ldaxr" + ext, "", [w_bit, root010, (0xffff, 0x17ff, 10)],
           [reg, OK.XREG_5_9], OPC_FLAG(0), SR_UPDATE.NONE)
    Opcode("ldar" + ext, "", [w_bit, root010, (0xffff, 0x37ff, 10)],
           [reg, OK.XREG_5_9], OPC_FLAG(0), SR_UPDATE.NONE)
    Opcode("stxr" + ext, "", [w_bit, root010, (0x1f, 0, 21), (0x3f, 0x1f, 10)],
           [OK.WREG_16_20, OK.XREG_5_9, reg], w_flag, SR_UPDATE.NONE)
    Opcode("stlxr" + ext, "", [w_bit, root010, (0x1f, 0, 21), (0x3f, 0x3f, 10)],
           [OK.WREG_16_20, OK.XREG_5_9, reg], w_flag, SR_UPDATE.NONE)
    Opcode("stlr" + ext, "", [w_bit, root010, (0xffff, 0x27ff, 10)],
           [OK.XREG_5_9, reg], w_flag, SR_UPDATE.NONE)

for ext, w_bit, imm in [("q", (7, 5, 29), OK.SIMM_15_21_TIMES8),
                        ("w", (7, 1, 29), OK.SIMM_15_21_TIMES4),
                        ("sw", (7, 3, 29), OK.SIMM_15_21_TIMES4)]:
    dst1 = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    dst2 = OK.XREG_10_14 if ext == "q" else OK.WREG_10_14
    Opcode("ldp" + ext, "imm_post", [w_bit, root010, (0xf, 3, 22)],
           [dst1, dst2, OK.XREG_5_9, imm], w_flag)
    Opcode("ldp" + ext, "imm_pre", [w_bit, root010, (0xf, 7, 22)],
           [dst1, dst2, OK.XREG_5_9, imm], w_flag)
    Opcode("ldp" + ext, "imm", [w_bit, root010, (0xf, 5, 22)],
           [dst1, dst2, OK.XREG_5_9, imm], w_flag)

for ext, w_bit, imm in [("q", (7, 4, 29), OK.SIMM_15_21_TIMES8),
                        ("w", (7, 0, 29), OK.SIMM_15_21_TIMES4),
                        ]:
    src1 = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    src2 = OK.XREG_10_14 if ext == "q" else OK.WREG_10_14
    Opcode("stp" + ext, "imm_post", [w_bit, root010, (0xf, 2, 22)],
           [OK.XREG_5_9, imm, src1, src2], w_flag)

    Opcode("stp" + ext, "imm_pre", [w_bit, root010, (0xf, 6, 22)],
           [OK.XREG_5_9, imm, src1, src2], w_flag)
    Opcode("stp" + ext, "imm", [w_bit, root010, (0xf, 4, 22)],
           [OK.XREG_5_9, imm, src1, src2], w_flag)

########################################
root011 = (7, 3, 26)
########################################
for ext, reg1, reg2, imm, bits in [
    ("s", OK.SREG_0_4, OK.SREG_10_14, OK.SIMM_15_21_TIMES4, (7, 1, 29)),
    ("d", OK.DREG_0_4, OK.DREG_10_14, OK.SIMM_15_21_TIMES8, (7, 3, 29)),
    ("q", OK.QREG_0_4, OK.QREG_10_14, OK.SIMM_15_21_TIMES16, (7, 5, 29))]:
    Opcode("fstp" + ext, "imm_post", [bits, root011, (0xf, 2, 22)],
           [OK.XREG_5_9, imm, reg1, reg2, ], OPC_FLAG(0))
    Opcode("fstp" + ext, "imm_pre", [bits, root011, (0xf, 6, 22)],
           [OK.XREG_5_9, imm, reg1, reg2], OPC_FLAG(0))
    Opcode("fstp" + ext, "imm", [bits, root011, (0xf, 4, 22)],
           [OK.XREG_5_9, imm, reg1, reg2], OPC_FLAG(0))
    Opcode("fldp" + ext, "imm_post", [bits, root011, (0xf, 3, 22)],
           [reg1, reg2, OK.XREG_5_9, imm], OPC_FLAG(0))
    Opcode("fldp" + ext, "imm_pre", [bits, root011, (0xf, 7, 22)],
           [reg1, reg2, OK.XREG_5_9, imm], OPC_FLAG(0))
    Opcode("fldp" + ext, "imm", [bits, root011, (0xf, 5, 22)],
           [reg1, reg2, OK.XREG_5_9, imm], OPC_FLAG(0))

########################################
root100 = (7, 4, 26)
########################################
for ext, w_flag, w_bit in [("b", OPC_FLAG.W, (1, 0, 31)), ("q", OPC_FLAG.X, (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if ext == "q" else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if ext == "q" else OK.WREG_16_20
    shift_filler = (0x3f, 0x3f, 10) if ext == "q" else (0x3f, 0x1f, 10)

    for name, bits, sr_update in [
        ("add", [(3, 0, 29), (3, 1, 24)], SR_UPDATE.NONE),
        ("adds", [(3, 1, 29), (3, 1, 24)], SR_UPDATE.NZ),
        ("sub", [(3, 2, 29), (3, 1, 24)], SR_UPDATE.NONE),
        ("subs", [(3, 3, 29), (3, 1, 24)], SR_UPDATE.NZ),

    ]:
        Opcode(name, "imm_" + ext, [root100, w_bit] + bits,
               [dst_reg, src1_reg, OK.IMM_10_21_22_23], w_flag, sr_update=sr_update)

    for name, bits, sr_update in [
        ("and", [(3, 0, 29), (7, 4, 23)], SR_UPDATE.NONE),
        ("ands", [(3, 3, 29), (7, 4, 23)], SR_UPDATE.NZ),
        ("eor", [(3, 2, 29), (7, 4, 23)], SR_UPDATE.NONE),
        ("orr", [(3, 1, 29), (7, 4, 23)], SR_UPDATE.NONE),
        # ("ubfx", [(3, 2, 29), (7, 6, 23)], SR_UPDATE.NONE),
        # ("bics", [(3, 3, 29), (7, 4, 23)], SR_UPDATE.NZ)
    ]:
        Opcode(name, "imm_" + ext, [root100, w_bit] + bits,
               [dst_reg, src1_reg, OK.IMM_10_15_16_22], w_flag, sr_update=sr_update)

    for name, bits in [
        # ("lsl", [(3, 2, 29), (7, 6, 23)]),
        ("lsr", [(3, 2, 29), (7, 6, 23)]),
        ("asr", [(3, 0, 29), (7, 6, 23)]),
        # ("ubfx", [(3, 2, 29), (7, 6, 23)], SR_UPDATE.NONE),
        # ("bics", [(3, 3, 29), (7, 4, 23)], SR_UPDATE.NZ),
    ]:
        Opcode(name, "imm_" + ext, [root100, w_bit, shift_filler] + bits,
               [dst_reg, src1_reg, OK.IMM_16_22], w_flag, sr_update=SR_UPDATE.NONE)

Opcode("adr", "", [root100, (1, 0, 31), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23_29_30], OPC_FLAG(0))
Opcode("adrp", "", [root100, (1, 1, 31), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23_29_30], OPC_FLAG(0))
########################################
root101 = (7, 5, 26)
########################################

Opcode("b", "", [root101, (7, 0, 29)],
       [OK.SIMM_0_25], OPC_FLAG(0))

Opcode("bl", "", [root101, (7, 4, 29)],
       [OK.SIMM_0_25], OPC_FLAG(0))

Opcode("ret", "", [root101, (7, 6, 29), (0xffff, 0x97c0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG(0))
Opcode("br", "", [root101, (7, 6, 29), (0xffff, 0x87c0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG(0))
Opcode("blr", "", [root101, (7, 6, 29), (0xffff, 0x8fc0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG(0))

for cond_val, cond_name in enumerate(["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
                                      "hi", "ls", "ge", "lt", "gt", "le"]):
    Opcode("b." + cond_name, "", [root101, (7, 2, 29), (3, 0, 24), (0x1f, cond_val, 0)],
           [OK.SIMM_5_23], OPC_FLAG(0))

Opcode("cbnz", "64", [root101, (7, 5, 29), (3, 1, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23], OPC_FLAG(0))
Opcode("cbnz", "32", [root101, (7, 1, 29), (3, 1, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23], OPC_FLAG(0))
Opcode("cbz", "64", [root101, (7, 5, 29), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23], OPC_FLAG(0))
Opcode("cbz", "32", [root101, (7, 1, 29), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_5_23], OPC_FLAG(0))

Opcode("tbz", "", [root101, (3, 1, 29), (3, 2, 24)],
       [OK.XREG_0_4, OK.IMM_19_23_31, OK.SIMM_5_18], OPC_FLAG(0))
Opcode("tbnz", "", [root101, (3, 1, 29), (3, 3, 24)],
       [OK.XREG_0_4, OK.IMM_19_23_31, OK.SIMM_5_18], OPC_FLAG(0))

Opcode("hlt", "", [root101, (7, 6, 29), (0x1f, 2, 21), (0x1f, 0, 0)],
       [OK.IMM_5_20], OPC_FLAG(0))
Opcode("brk", "", [root101, (7, 6, 29), (0x1f, 1, 21), (0x1f, 0, 0)],
       [OK.IMM_5_20], OPC_FLAG(0))
Opcode("svc", "", [root101, (7, 6, 29), (0x1f, 0, 21), (0x1f, 1, 0)],
       [OK.IMM_5_20], OPC_FLAG(0))
Opcode("yield", "", [root101, (7, 6, 29), (0x3ffffff, 0x103203f, 0)],
       [], OPC_FLAG(0))
Opcode("nop", "", [root101, (7, 6, 29), (0x3ffffff, 0x103201f, 0)],
       [], OPC_FLAG(0))
Opcode("eret", "", [root101, (7, 6, 29), (0x3ffffff, 0x29f03e0, 0)],
       [], OPC_FLAG(0))
# atomic
Opcode("isb", "", [root101, (7, 6, 29), (0x3ffffff, 0x1033fdf, 0)],
       [], OPC_FLAG(0))
Opcode("clrex", "", [root101, (7, 6, 29), (0x3ffffff, 0x1033f5f, 0)],
       [], OPC_FLAG(0))
Opcode("dmb", "ish", [root101, (7, 6, 29), (0x3ffffff, 0x1033bbf, 0)],
       [], OPC_FLAG(0))
Opcode("dmb", "ishld", [root101, (7, 6, 29), (0x3ffffff, 0x10339bf, 0)],
       [], OPC_FLAG(0))
Opcode("dmb", "ishst", [root101, (7, 6, 29), (0x3ffffff, 0x1033abf, 0)],
       [], OPC_FLAG(0))
Opcode("dsb", "ish", [root101, (7, 6, 29), (0x3ffffff, 0x1033b9f, 0)],
       [], OPC_FLAG(0))
Opcode("dsb", "ishld", [root101, (7, 6, 29), (0x3ffffff, 0x103399f, 0)],
       [], OPC_FLAG(0))
Opcode("dsb", "ishst", [root101, (7, 6, 29), (0x3ffffff, 0x1033a9f, 0)],
       [], OPC_FLAG(0))
########################################
root110 = (7, 6, 26)
########################################
for ext, w_flag, w_bit in [("32", OPC_FLAG.W, (1, 0, 31)), ("64", OPC_FLAG.X, (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if w_bit else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if w_bit else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if w_bit else OK.WREG_16_20
    src3_reg = OK.XREG_10_14 if w_bit else OK.WREG_10_14

    for name, bits in [
        ("madd", [(3, 0, 29), (1, 0, 15)]),
        ("msub", [(3, 0, 29), (1, 1, 15)]),
    ]:
        Opcode(name, ext, [root110, w_bit, (3, 3, 24), (7, 0, 21)] + bits,
               [dst_reg, src1_reg, src3_reg, src2_reg], w_flag)

    for name, bits in [("udiv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 2, 10)]),
                       ("sdiv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 3, 10)]),
                       ("lslv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 8, 10)]),
                       ("lsrv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 9, 10)]),
                       ("asrv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 0xa, 10)]),
                       ("rorv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 0xb, 10)]),
                       ("adc", [(3, 0, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)]),
                       ("sbc", [(3, 2, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)])]:
        Opcode(name, ext, [root110, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg], w_flag)

    for name, bits, in [
        ("adcs", [(3, 1, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)]),
        ("sbcs", [(3, 3, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)])]:
        Opcode(name, ext, [root110, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg], w_flag, SR_UPDATE.NZ)

    if ext == "64":
        for name, bits in [
            ("smaddl", [(3, 0, 29), (7, 1, 21), (1, 0, 15)]),
            ("smsubl", [(3, 0, 29), (7, 1, 21), (1, 1, 15)]),
            ("smulh", [(3, 0, 29), (7, 2, 21), (1, 0, 15)]),
            ("umaddl", [(3, 0, 29), (7, 5, 21), (1, 0, 15)]),
            ("umsubl", [(3, 0, 29), (7, 5, 21), (1, 1, 15)]),
            ("umulh", [(3, 0, 29), (7, 6, 21), (1, 0, 15)]),
        ]:
            Opcode(name, "", [root110, (1, 1, 31), (3, 3, 24)] + bits,
                   [dst_reg, src1_reg, src3_reg, src2_reg], w_flag)

for ext, scaled_offset, w_bits in [
    ("q", OK.IMM_10_21_times_8, (7, 7, 29)),
    ("w", OK.IMM_10_21_times_4, (7, 5, 29)),
    ("h", OK.IMM_10_21_times_2, (7, 3, 29)),
    ("b", OK.IMM_10_21, (7, 1, 29)),
]:
    src = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    dst = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4

    Opcode("ldr" + ext, "imm", [root110, w_bits, (0xf, 5, 22)],
           [dst, OK.XREG_5_9, scaled_offset], OPC_FLAG(0))
    Opcode("ldr" + ext, "imm_pre", [root110, w_bits, (0x1f, 2, 21), (3, 3, 10)],
           [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
    Opcode("ldr" + ext, "imm_post", [root110, w_bits, (0x1f, 2, 21), (3, 1, 10)],
           [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
    Opcode("ldur" + ext, "imm", [root110, w_bits, (0x1f, 2, 21), (3, 0, 10)],
           [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))

    Opcode("ldr" + ext, "reg_32", [root110, w_bits, (0x1f, 3, 21), (1, 0, 13), (3, 2, 10)],
           [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_W, OK.WREG_16_20], OPC_FLAG(0))
    Opcode("ldr" + ext, "reg_64", [root110, w_bits, (0x1f, 3, 21), (1, 1, 13), (3, 2, 10)],
           [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_X, OK.XREG_16_20], OPC_FLAG(0))

    Opcode("str" + ext, "reg_32", [root110, w_bits, (0x1f, 1, 21), (1, 0, 13), (3, 2, 10)],
           [OK.XREG_5_9, OK.SHIFT_12_14_15_W, OK.WREG_16_20, src], OPC_FLAG(0))
    Opcode("str" + ext, "reg_64", [root110, w_bits, (0x1f, 1, 21), (1, 1, 13), (3, 2, 10)],
           [OK.XREG_5_9, OK.SHIFT_12_14_15_X, OK.XREG_16_20, src], OPC_FLAG(0))

    Opcode("str" + ext, "imm", [root110, w_bits, (0xf, 4, 22)],
           [OK.XREG_5_9, scaled_offset, src], OPC_FLAG(0))
    Opcode("str" + ext, "imm_pre", [root110, w_bits, (0x1f, 0, 21), (3, 3, 10)],
           [OK.XREG_5_9, OK.SIMM_12_20, src], OPC_FLAG(0))
    Opcode("str" + ext, "imm_post", [root110, w_bits, (0x1f, 0, 21), (3, 1, 10)],
           [OK.XREG_5_9, OK.SIMM_12_20, src], OPC_FLAG(0))
    Opcode("stur" + ext, "imm", [root110, w_bits, (0x1f, 0, 21), (3, 0, 10)],
           [OK.XREG_5_9, OK.SIMM_12_20, src], OPC_FLAG(0))

    if ext == "w":
        Opcode("ldrs" + ext, "imm", [root110, w_bits, (0xf, 6, 22)],
               [OK.XREG_0_4, OK.XREG_5_9, scaled_offset], OPC_FLAG(0))
        Opcode("ldrs" + ext, "imm_pre", [root110, w_bits, (0x1f, 4, 21), (3, 3, 10)],
               [OK.XREG_0_4, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
        Opcode("ldrs" + ext, "imm_post", [root110, w_bits, (0x1f, 4, 21), (3, 1, 10)],
               [OK.XREG_0_4, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
        Opcode("ldurs" + ext, "imm_post", [root110, w_bits, (0x1f, 4, 21), (3, 0, 10)],
               [OK.XREG_0_4, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
        Opcode("ldrs" + ext, "reg_32", [root110, w_bits, (0x1f, 5, 21), (1, 0, 13), (3, 2, 10)],
               [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_W, OK.WREG_16_20], OPC_FLAG(0))
        Opcode("ldrs" + ext, "reg_64", [root110, w_bits, (0x1f, 5, 21), (1, 1, 13), (3, 2, 10)],
               [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_X, OK.XREG_16_20], OPC_FLAG(0))

    if ext == "b" or ext == "h":
        for ext2, w2_bits, dst in [("w", (1, 1, 22), OK.WREG_0_4), ("q", (1, 0, 22), OK.XREG_0_4)]:
            # scaled
            Opcode(f"ldrs{ext}{ext2}", "imm", [root110, w_bits, (7, 3, 23), w2_bits],
                   [dst, OK.XREG_5_9, OK.IMM_10_21_times_2], OPC_FLAG(0))
            # pre/post
            Opcode(f"ldrs{ext}{ext2}", "imm_pre", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 3, 10)],
                   [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
            Opcode(f"ldrs{ext}{ext2}", "imm_post", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 1, 10)],
                   [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
            # unscaled
            Opcode(f"ldurs{ext}{ext2}", "imm", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 0, 10)],
                   [dst, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
            Opcode(f"ldrs{ext}{ext2}", "reg_32",
                   [root110, w_bits, (7, 1, 23), w2_bits, (1, 1, 21), (1, 0, 13), (3, 2, 10)],
                   [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_W, OK.WREG_16_20], OPC_FLAG(0))
            Opcode(f"ldrs{ext}{ext2}", "reg_64",
                   [root110, w_bits, (7, 1, 23), w2_bits, (1, 1, 21), (1, 1, 13), (3, 2, 10)],
                   [dst, OK.XREG_5_9, OK.SHIFT_12_14_15_X, OK.XREG_16_20], OPC_FLAG(0))

for ext, w_bits in [("b", (1, 0, 31)), ("q", (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "q" else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if ext == "q" else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if ext == "q" else OK.WREG_16_20
    for cond_val, cond_name in enumerate(["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
                                          "hi", "ls", "ge", "lt", "gt", "le"]):
        for name, bits in [("csel", [(3, 0, 29), (3, 0, 10)]),
                           ("csneg", [(3, 2, 29), (3, 1, 10)]),
                           ("csinc", [(3, 0, 29), (3, 1, 10)]),
                           ("csinv", [(3, 2, 29), (3, 0, 10)]),
                           ]:
            Opcode(name, f"{ext}_{cond_name}",
                   [w_bits, root110, (0x1f, 0x14, 21), (0xf, cond_val, 12)] + bits,
                   [dst_reg, src1_reg, src2_reg], OPC_FLAG(0))

########################################
root111 = (7, 7, 26)
########################################

for ext, w_flag, w_bit in [("s", OPC_FLAG.W, (1, 0, 22)),
                           ("d", OPC_FLAG.X, (1, 1, 22))]:
    dst_reg = OK.DREG_0_4 if w_bit else OK.SREG_0_4
    src1_reg = OK.DREG_5_9 if w_bit else OK.SREG_5_9
    src2_reg = OK.DREG_16_20 if w_bit else OK.SREG_16_20
    src3_reg = OK.DREG_10_14 if w_bit else OK.SREG_10_14

    for name, bits in [
        ("fmul", (0x3f, 2, 10)),
        ("fdiv", (0x3f, 6, 10)),
        ("fadd", (0x3f, 0xa, 10)),
        ("fsub", (0x3f, 0xe, 10)),
        ("fmax", (0x3f, 0x12, 10)),
        ("fmaxnm", (0x3f, 0x1a, 10)),
        ("fmin", (0x3f, 0x16, 10)),
        ("fminnm", (0x3f, 0x1e, 10)),
        ("fnmul", (0x3f, 0x22, 10)),
    ]:
        Opcode(name, ext, [root111, (7, 0, 29), (7, 4, 23), w_bit, (1, 1, 21), bits],
               [dst_reg, src1_reg, src2_reg], w_flag)

    for name, bits in [
        ("fmadd", [(7, 6, 23), (1, 0, 21), (1, 0, 15)]),
        ("fmsub", [(7, 6, 23), (1, 0, 21), (1, 1, 15)]),
        ("fnmadd", [(7, 6, 23), (1, 1, 21), (1, 0, 15)]),
        ("fnmsub", [(7, 6, 23), (1, 1, 21), (1, 1, 15)]),
    ]:
        Opcode(name, ext, [root111, (7, 0, 29), w_bit] + bits,
               [dst_reg, src1_reg, src2_reg, src3_reg], w_flag)

    for name, bits in [
        ("fabd", [(7, 5, 23), (0x3f, 0x35, 10)]),
        ("fcmge", [(7, 4, 23), (0x3f, 0x39, 10)]),
        ("fcmgt", [(7, 5, 23), (0x3f, 0x39, 10)]),
    ]:
        Opcode(name, ext, [root111, (7, 3, 29), w_bit, (1, 1, 21)] + bits,
               [dst_reg, src1_reg, src2_reg], w_flag)

    for name, bits in [
        ("fabs", [(7, 4, 23), (0x7ff, 0x30, 10)]),
        ("fneg", [(7, 4, 23), (0x7ff, 0x50, 10)]),
        ("fsqrt", [(7, 4, 23), (0x7ff, 0x70, 10)]),
        ("frinta", [(7, 4, 23), (0x7ff, 0x190, 10)]),
        ("frinti", [(7, 4, 23), (0x7ff, 0x1f0, 10)]),
        ("frintm", [(7, 4, 23), (0x7ff, 0x150, 10)]),
        ("frintn", [(7, 4, 23), (0x7ff, 0x110, 10)]),
        ("frintp", [(7, 4, 23), (0x7ff, 0x130, 10)]),
        ("frintx", [(7, 4, 23), (0x7ff, 0x1d0, 10)]),
        ("frintz", [(7, 4, 23), (0x7ff, 0x170, 10)]),
    ]:
        Opcode(name, ext, [root111, (7, 0, 29), w_bit, (1, 1, 21)] + bits,
               [dst_reg, src1_reg], w_flag)

    for cond_val, cond_name in enumerate(["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
                                          "hi", "ls", "ge", "lt", "gt", "le"]):
        Opcode(f"fcsel", f"{ext}_{cond_name}",
               [(7, 0, 29), root111, (7, 4, 23), w_bit, (1, 1, 21), (0xf, cond_val, 12), (3, 3, 10)],
               [dst_reg, src1_reg, src2_reg], OPC_FLAG(0))

for ext, dst_reg, bits in [
    ("b", OK.BREG_0_4, [(3, 0, 30), (3, 1, 22)]),
    ("h", OK.HREG_0_4, [(3, 1, 30), (3, 1, 22)]),
    ("s", OK.SREG_0_4, [(3, 2, 30), (3, 1, 22)]),
    ("d", OK.DREG_0_4, [(3, 3, 30), (3, 1, 22)]),
    ("q", OK.QREG_0_4, [(3, 0, 30), (3, 3, 22)]),
]:
    Opcode("fldr" + ext, "imm_post", [root111, (1, 1, 29), (3, 0, 24), (1, 0, 21), (3, 1, 10)] + bits,
           [dst_reg, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
    Opcode("fldr" + ext, "imm_pre", [root111, (1, 1, 29), (3, 0, 24), (1, 0, 21), (3, 3, 10)] + bits,
           [dst_reg, OK.XREG_5_9, OK.SIMM_12_20], OPC_FLAG(0))
    Opcode("fldr" + ext, "imm", [root111, (1, 1, 29), (3, 1, 24)] + bits,
           [dst_reg, OK.XREG_5_9, OK.IMM_10_21], OPC_FLAG(0))
    Opcode("fldr" + ext, "reg_32", [root111, (1, 1, 29), (3, 0, 24), (1, 0, 13), (1, 1, 21), (3, 2, 10)] + bits,
           [dst_reg, OK.XREG_5_9, OK.SHIFT_12_14_15_W, OK.WREG_16_20], OPC_FLAG(0))
    Opcode("fldr" + ext, "reg_64", [root111, (1, 1, 29), (3, 0, 24), (1, 1, 13), (1, 1, 21), (3, 2, 10)] + bits,
           [dst_reg, OK.XREG_5_9, OK.SHIFT_12_14_15_X, OK.XREG_16_20], OPC_FLAG(0))

for dst_ext, dst_reg, dst_bits in [
    ("h", OK.HREG_0_4, (3, 3, 15)),
    ("s", OK.SREG_0_4, (3, 0, 15)),
    ("d", OK.DREG_0_4, (3, 1, 15))]:
    for src_ext, src_reg, src_bits in [
        ("h", OK.HREG_5_9, (3, 3, 22)),
        ("s", OK.SREG_5_9, (3, 0, 22)),
        ("d", OK.DREG_5_9, (3, 1, 22))]:
        if src_ext != dst_ext:
            Opcode("fcvt", dst_ext + "_" + src_ext,
                   [(7, 0, 29), root111, (3, 2, 24), src_bits, (0x1f, 0x11, 17), dst_bits,
                    (0x1f, 0x10, 10)],
                   [dst_reg, src_reg], OPC_FLAG(0))

for dst_ext, dst_reg, dst_bits in [("w", OK.WREG_0_4, (1, 0, 31)),
                                   ("q", OK.XREG_0_4, (1, 1, 31))]:
    for type_ext, bits in [("as", (0xfff, 0x900, 10)),
                           ("au", (0xfff, 0x940, 10)),
                           ("ms", (0xfff, 0xc00, 10)),
                           ("mu", (0xfff, 0xc40, 10)),
                           ("ns", (0xfff, 0x800, 10)),
                           ("nu", (0xfff, 0x840, 10)),
                           ("ps", (0xfff, 0xa00, 10)),
                           ("pu", (0xfff, 0xa40, 10)),
                           ("zs", (0xfff, 0xe00, 10)),
                           ("zu", (0xfff, 0xe40, 10))]:
        for src_ext, src_reg, src_bits in [("s", OK.SREG_5_9, (1, 0, 22)),
                                           ("d", OK.DREG_5_9, (1, 1, 22))]:
            Opcode("fcvt" + type_ext, dst_ext + "_" + src_ext,
                   [dst_bits, (3, 0, 29), root111, (7, 4, 23), src_bits, bits],
                   [dst_reg, src_reg], OPC_FLAG(0))

for src_ext, src_reg, src_bits in [("w", OK.WREG_0_4, (1, 0, 31)),
                                   ("q", OK.XREG_0_4, (1, 1, 31))]:
    for dst_ext, dst_reg, dst_bits in [("s", OK.SREG_5_9, (1, 0, 22)),
                                       ("d", OK.DREG_5_9, (1, 1, 22))]:
        Opcode("scvtf", dst_ext + "_" + src_ext,
               [src_bits, (3, 0, 29), root111, (7, 4, 23), dst_bits, (0xfff, 0x880, 10)],
               [dst_reg, src_reg], OPC_FLAG(0))
        Opcode("ucvtf", dst_ext + "_" + src_ext,
               [src_bits, (3, 0, 29), root111, (7, 4, 23), dst_bits, (0xfff, 0x8c0, 10)],
               [dst_reg, src_reg], OPC_FLAG(0))


class Ins:
    """Arm flavor of an Instruction

    There can be at most one relocation associated with an Ins
    """
    opcode: Opcode
    operands: List[int] = dataclasses.field(default_factory=list)
    #
    # Note the addend is store in `operands[reloc_pos]
    reloc_symbol: str = ""
    reloc_kind: int = 0
    reloc_pos = 0
    is_local_sym = False


def Disassemble(data: int) -> Optional[Ins]:
    opcode = Opcode.FindOpcode(data)
    if opcode is None:
        return None
    operands = opcode.DisassembleOperands(data)
    if operands is None:
        return None
    return Ins(opcode, operands)


def Assemble(ins: Ins) -> int:
    assert ins.reloc_kind == 0, "reloc has not been resolved"
    return ins.opcode.AssembleOperands(ins.operands)


############################################################
# code below is only used if this file is run as an executable
############################################################
def Query(opcode: str):
    count = 0
    for opc_list in Opcode.ordered_opcodes.values():
        for opc in opc_list:
            if opc.name != opcode:
                continue
            print(f"name={opc.name} variant={opc.variant}")
            print(f"mask={opc.bit_mask:08x} value={opc.bit_value:08x}")
            print("fields with bit ranges:")
            for f in opc.fields:
                print("\t", f.name, FIELD_DETAILS[f])
                count += 1
            print()
    if count:
        print("bit range tuples have the form (modifier, bit-width, start-pos)")


def _get_grouped_opcodes(mask: int) -> List[Opcode]:
    """Preserves the order of the Opcode.ordered_opcodes"""
    d = collections.defaultdict(list)
    for lst in Opcode.ordered_opcodes.values():
        for opc in lst:
            d[opc.bit_value & mask].append(opc)
    out = []
    for k, v in sorted(d.items()):
        out += v
    return out


def _find_mask_matches(mask: int, val: int, opcodes: List[Opcode]) -> Tuple[int, int]:
    first = -1
    last = -1
    for n, opc in enumerate(opcodes):
        if (opc.bit_value & mask) == val & opc.bit_mask:
            if first == -1: first = n
            last = n
    return first, last


def _render_enum_simple(symbols, name):
    print("\n%s {" % name)
    for sym in symbols:
        print(f"    {sym},")
    print("};")


def hash_djb2(x: str):
    """ Simple string hash function for mnemonics

     see http://www.cse.yorku.ca/~oz/hash.html"""
    h = 5381
    for c in x:
        h = (h << 5) + h + ord(c)
    return h & 0xffff


def _EmitCodeH(fout):
    cgen.RenderEnum(cgen.NameValues(OK), "class OK : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(SR_UPDATE), "class SR_UPDATE : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(BRK), "class BitRangeKind : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(MEM_WIDTH), "class MEM_WIDTH : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(OPC_FLAG), "OPC_FLAG", fout)
    # cgen.RenderEnum(cgen.NameValues(PRED), "class PRED : uint8_t", fout)
    # cgen.RenderEnum(cgen.NameValues(REG), "class REG : uint8_t", fout)
    # cgen.RenderEnum(cgen.NameValues(SREG), "class SREG : uint8_t", fout)
    # cgen.RenderEnum(cgen.NameValues(DREG), "class DREG : uint8_t", fout)
    # cgen.RenderEnum(cgen.NameValues(ADDR_MODE), "class ADDR_MODE : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(SHIFT), "class SHIFT : uint8_t", fout)
    opcodes = [opc.NameForEnum() for opc in _get_grouped_opcodes(_INS_CLASSIFIER)]
    # note we sneak in an invalid first entry
    _render_enum_simple(["invalid"] + opcodes, "enum class OPC : uint16_t")


def _RenderOpcodeTable():
    """Note: we sneak in an invalid first entry"""
    out = [
        '{"invalid", "invalid", 0, 0, 0, {}, 0, MEM_WIDTH::NA, SR_UPDATE::NONE},'
    ]
    opcodes = _get_grouped_opcodes(_INS_CLASSIFIER)
    last = ~0
    for opc in opcodes:
        key = opc.bit_value & _INS_CLASSIFIER
        if key != last:
            out += [
                f"/* {'=' * 60}*/",
                f"/* BLOCK {key:08x} */",
                f"/* {'=' * 60}*/",
            ]
            last = key
        flags = " | ".join([f.name for f in OPC_FLAG if opc.classes & f])
        assert len(opc.fields) <= MAX_OPERANDS
        fields = "{" + ", ".join(["OK::" + f.name for f in opc.fields]) + "}"
        out += [
            "{" +
            f'"{opc.name}", "{opc.NameForEnum()}", 0x{opc.bit_mask:08x}, 0x{opc.bit_value:08x},',
            f' {len(opc.fields)}, {fields},',
            f' {flags}, MEM_WIDTH::{opc.mem_width.name}, SR_UPDATE::{opc.sr_update.name}',
            '},']
    return out


def _RenderOpcodeTableJumper() -> List[str]:
    out = []
    opcodes = _get_grouped_opcodes(_INS_CLASSIFIER)
    for i in range(8):
        first, last = _find_mask_matches(_INS_CLASSIFIER, i * 0x2000000, opcodes)
        # the +1 compensates for the invalid first entry we have snuck in
        out.append(f"{first + 1}, {last + 1}")
    return out


def _RenderFieldTable():
    out = []
    for n, ok in enumerate(OK):
        assert n == ok.value
        if ok is OK.Invalid:
            bit_ranges = []
        else:
            bit_ranges = FIELD_DETAILS[ok]
        assert len(bit_ranges) <= MAX_BIT_RANGES
        out += ["{" + f"   // {ok.name} = {ok.value}"]
        out += [f"    {len(bit_ranges)}," + " {"]
        out += ["    {BitRangeKind::%s, %d, %d}," % (brk.name, a, b)
                for (brk, a, b) in bit_ranges]
        out += ["}}, "]
    return out


_MNEMONIC_HASH_LOOKUP_SIZE = 512


def _RenderMnemonicHashLookup():
    table = ["invalid"] * _MNEMONIC_HASH_LOOKUP_SIZE
    for name, opc in Opcode.name_to_opcode.items():
        h = hash_djb2(name)
        for d in range(64):
            hh = (h + d) % _MNEMONIC_HASH_LOOKUP_SIZE
            if table[hh] == "invalid":
                table[hh] = name
                break
        else:
            assert False, f"probing distance exceeded {name}"
    items = [f"OPC::{t}," for t in table]
    return ["   " + " ".join(items[i:i + 4]) for i in range(0, len(items), 4)]


def _EmitCodeC(fout):
    print("// Indexed by OPC which in turn are organize to help with disassembly", file=fout)
    print("const Opcode OpcodeTable[] = {", file=fout)
    print("\n".join(_RenderOpcodeTable()), file=fout)
    print("};\n", file=fout)

    print("const int16_t OpcodeTableJumper[] = {", file=fout)
    print(",\n".join(_RenderOpcodeTableJumper()), file=fout)
    print("};\n", file=fout)

    print("// Indexed by FieldKind", file=fout)
    print("static const Field FieldTable[] = {", file=fout)
    print("\n".join(_RenderFieldTable()), file=fout)
    print("};\n", file=fout)

    print("// Indexed by djb2 hash of mnemonic. Collisions are resolved via linear probing",
          file=fout)
    print("static const OPC MnemonicHashTable[512] = {", file=fout)
    print("\n".join(_RenderMnemonicHashLookup()), file=fout)
    print("};\n", file=fout)

    # what about REG/SREG/DREG
    cgen.RenderEnumToStringMap(cgen.NameValues(PRED), "PRED", fout)
    cgen.RenderEnumToStringFun("PRED", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(ADDR_MODE), "ADDR_MODE", fout)
    cgen.RenderEnumToStringFun("ADDR_MODE", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(SHIFT), "SHIFT", fout)
    cgen.RenderEnumToStringFun("SHIFT", fout)


def _OpcodeDisassemblerExperiments():
    """Some failed experiments for making the disassembler even faster"""
    print("opcode distribution")
    for k, v in Opcode.ordered_opcodes.items():
        submask = ~0
        for x in v:
            submask &= x.bit_mask
        print(f"{k:08x} {len(v):2}  {submask:08x}")
        d = collections.defaultdict(list)
        for x in v:
            d[x.bit_value & submask].append(x)
        for k2, v2 in sorted(d.items()):
            print(f"  {k2:08x} {len(v2):2}")
    # print(f"magic mask {_INS_MAGIC_CLASSIFIER:08x}")
    # d = collections.defaultdict(list)
    # for x in Opcode.name_to_opcode.values():
    #     d[x.bit_value & _INS_MAGIC_CLASSIFIER].append(x)
    # for k, v in sorted(d.items()):
    #     print(f"  {k:08x} {len(v):2}")
    # print("")
    for opc in sorted(Opcode.name_to_opcode.values()):
        print(f"{opc.name:12s} {opc.variant:6s} {opc.fields}")
    print("OK")


def _MnemonicHashingExperiments():
    # experiment for near perfect hashing
    buckets = [[] for _ in range(_MNEMONIC_HASH_LOOKUP_SIZE)]
    table = [""] * _MNEMONIC_HASH_LOOKUP_SIZE
    distance = [0] * 128
    for opc in Opcode.name_to_opcode.values():
        s = opc.NameForEnum()
        h = hash_djb2(s)
        print(f"{s}: {h:x}")
        buckets[h % _MNEMONIC_HASH_LOOKUP_SIZE].append(s)
        for d in range(len(distance)):
            hh = (h + d) % _MNEMONIC_HASH_LOOKUP_SIZE
            if table[hh] == "":
                table[hh] = s
                distance[d] += 1
                break
        else:
            assert False, f"probing distance exceeded {s}"
    print("hash collisions")
    for n, opcodes in enumerate(buckets):
        if opcodes:
            print(f"{n:2x} {len(opcodes)}  {opcodes}")
    print("linear probing distances")
    for n, count in enumerate(distance):
        if count > 0:
            print(f"{n} {count}")


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("no argument provided")
        sys.exit(1)
    if sys.argv[1] == "dist":
        _OpcodeDisassemblerExperiments()
    elif sys.argv[1] == "hash":
        _MnemonicHashingExperiments()
    elif sys.argv[1] == "gen_c":
        cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)
    elif sys.argv[1] == "gen_h":
        cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
    else:
        Query(sys.argv[1])
