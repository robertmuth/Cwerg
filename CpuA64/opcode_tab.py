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

MAX_OPERANDS = 5

MAX_BIT_RANGES = 2

CONDITION_CODES = ["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
                   "hi", "ls", "ge", "lt", "gt", "le"]

CONDITION_CODES_INV_MAP = {code: CONDITION_CODES[n ^ 1] for
                           n, code in enumerate(CONDITION_CODES)}


def Decode8BitFlt(x):
    mantissa = (x & 0xf) + 16
    x >>= 4
    exponent = (x & 7) ^ 4
    sign = (x >> 3) * -2 + 1
    return ((0.125 * mantissa) / 16) * (1 << exponent) * sign


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


def ror(x: int, bit_size: int, amount: int) -> int:
    mask = (1 << amount) - 1
    return (x >> amount) | ((x & mask) << (bit_size - amount))


# https://stackoverflow.com/questions/30904718/range-of-immediate-values-in-armv8-a64-assembly/33265035#33265035
# table: https://gist.github.com/dinfuehr/51a01ac58c0b23e4de9aac313ed6a06a
def DecodeLogicalImmediate(x, reg_size) -> int:
    n = x >> 12
    r = (x >> 6) & 0x3f
    s = x & 0x3f
    # print(f"@@ {n:x} {r:x}  {s:x}")
    if n == 1:
        size = 64
        ones = s + 1
    else:
        size = 32
        while (size & s) != 0:
            size >>= 1
        ones = 1 + (s & (size - 1))
        assert ones != size

    pattern = (1 << ones) - 1
    # print (f"@@ pattern: {pattern:x} {size}")
    # Note: pattern is of the form 0+1+

    # spread pattern to reg_size
    while size < reg_size:
        pattern |= pattern << size
        size *= 2
    return ror(pattern, reg_size, r)


def Encode_10_15_16_22_X(x) -> Optional[int]:
    if x == 0 or x == ((1 << 64) - 1):
        return None
    # determine pattern width
    for size, sm in [(64, 0), (32, 0), (16, 0x20), (8, 0x30), (4, 0x38), (2 , 0x3c)]:
        shift = size >> 1
        a = x & ((1 << shift) - 1)
        b = x >> shift
        if a == b:
            x = a
        else:
            break
    else:
        assert False
    n = 1 if size == 64 else 0
    # determine ones
    ones = bin(x).count('1')
    ones_mask = (1 << ones) - 1
    for r in range(size):
        if x == ror(ones_mask, size, r):
            s = sm | (ones - 1)
            # print (f"{n} {r:06b} {s:06b}")
            return (n << 12) | (r << 6) | s

    return None


def EncodeShifted_10_21_22(x) -> Optional[int]:
    for i in range(2):
        if (x & 0xfff) == x:
            return x | (i << 12)
        x >>= 12
    return None


def EncodeShifted_5_20_21_22(x) -> Optional[int]:
    for i in range(4):
        if (x & 0xffff) == x:
            return x | (i << 16)
        x >>= 16
    return None


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

    WREG_0_4_SP = 29
    WREG_5_9_SP = 30

    XREG_0_4_SP = 31
    XREG_5_9_SP = 32
    REG_LINK = 33

    # shifts
    SHIFT_22_23 = 60
    SHIFT_22_23_NO_ROR = 61
    SHIFT_15_W = 62
    SHIFT_15_X = 63

    # signed immeditate
    SIMM_PCREL_0_25 = 70
    SIMM_12_20 = 71
    SIMM_15_21_TIMES16 = 72
    SIMM_15_21_TIMES4 = 73
    SIMM_15_21_TIMES8 = 74
    SIMM_PCREL_5_18 = 75
    SIMM_PCREL_5_23 = 76
    SIMM_PCREL_5_23_29_30 = 77

    # unsigned immediates
    IMM_10_12_LIMIT4 = 100
    IMM_10_15 = 101
    IMM_10_15_16_22_W = 102
    IMM_10_15_16_22_X = 103
    IMM_10_21 = 104
    IMM_SHIFTED_10_21_22 = 105
    IMM_10_21_times_16 = 106
    IMM_10_21_times_2 = 107
    IMM_10_21_times_4 = 108
    IMM_10_21_times_8 = 109
    IMM_12_MAYBE_SHIFT_0 = 110
    IMM_12_MAYBE_SHIFT_1 = 111
    IMM_12_MAYBE_SHIFT_2 = 112
    IMM_12_MAYBE_SHIFT_3 = 113
    IMM_12_MAYBE_SHIFT_4 = 114
    IMM_16_20 = 116
    IMM_16_21 = 117
    IMM_19_23_31 = 118
    IMM_5_20 = 119
    IMM_COND_0_3 = 121
    IMM_FLT_ZERO = 123
    IMM_SHIFTED_5_20_21_22 = 124
    #
    FLT_13_20 = 115


############################################################
# effects of an opcode wrt the status registers
# Note, the for instructions with the fCC_UPDATE_20 the effect
# is gated on the "s" bit
############################################################
@enum.unique
class SR_UPDATE(enum.Enum):
    NONE = 0
    NZCV = 1


############################################################
# bit ranges are the building blocks of fields
# Each bit range specifies one or more consecutive bits
############################################################
BIT_RANGE = Tuple[int, int]

FIELDS_REG: Dict[OK, List[BIT_RANGE]] = {
    OK.WREG_0_4: [(5, 0)],
    OK.WREG_5_9: [(5, 5)],
    OK.WREG_10_14: [(5, 10)],
    OK.WREG_16_20: [(5, 16)],
    OK.WREG_0_4_SP: [(5, 0)],
    OK.WREG_5_9_SP: [(5, 5)],

    #
    OK.XREG_0_4: [(5, 0)],
    OK.XREG_5_9: [(5, 5)],
    OK.XREG_10_14: [(5, 10)],
    OK.XREG_16_20: [(5, 16)],
    OK.XREG_0_4_SP: [(5, 0)],
    OK.XREG_5_9_SP: [(5, 5)],
    #
    OK.SREG_0_4: [(5, 0)],
    OK.SREG_5_9: [(5, 5)],
    OK.SREG_10_14: [(5, 10)],
    OK.SREG_16_20: [(5, 16)],
    #
    OK.DREG_0_4: [(5, 0)],
    OK.DREG_5_9: [(5, 5)],
    OK.DREG_10_14: [(5, 10)],
    OK.DREG_16_20: [(5, 16)],
    #
    OK.BREG_0_4: [(5, 0)],
    OK.BREG_5_9: [(5, 5)],
    OK.BREG_10_14: [(5, 10)],
    OK.BREG_16_20: [(5, 16)],
    #
    OK.HREG_0_4: [(5, 0)],
    OK.HREG_5_9: [(5, 5)],
    OK.HREG_10_14: [(5, 10)],
    OK.HREG_16_20: [(5, 16)],
    #
    OK.QREG_0_4: [(5, 0)],
    OK.QREG_5_9: [(5, 5)],
    OK.QREG_10_14: [(5, 10)],
    OK.QREG_16_20: [(5, 16)],
    OK.REG_LINK: [],

}

FIELDS_IMM: Dict[OK, List[BIT_RANGE]] = {
    OK.IMM_10_15: [(6, 10)],
    OK.IMM_10_21: [(12, 10)],
    OK.IMM_10_21_times_2: [(12, 10)],
    OK.IMM_10_21_times_4: [(12, 10)],
    OK.IMM_10_21_times_8: [(12, 10)],
    OK.IMM_10_21_times_16: [(12, 10)],
    OK.IMM_10_15_16_22_W: [(13, 10)],
    OK.IMM_10_15_16_22_X: [(13, 10)],
    OK.IMM_19_23_31: [(1, 31), (5, 19)],
    OK.IMM_5_20: [(16, 5)],
    OK.IMM_16_21: [(6, 16)],

    OK.SIMM_PCREL_5_23: [(19, 5)],
    OK.IMM_SHIFTED_10_21_22: [(13, 10)],
    OK.SIMM_12_20: [(9, 12)],
    OK.SIMM_PCREL_0_25: [(26, 0)],
    OK.SIMM_PCREL_5_18: [(14, 5)],
    OK.SIMM_15_21_TIMES4: [(7, 15)],
    OK.SIMM_15_21_TIMES8: [(7, 15)],
    OK.SIMM_15_21_TIMES16: [(7, 15)],
    OK.SIMM_PCREL_5_23_29_30: [(19, 5), (2, 29)],
    OK.IMM_COND_0_3: [(4, 0)],
    OK.IMM_16_20: [(5, 16)],
    OK.FLT_13_20: [(8, 13)],
    OK.IMM_FLT_ZERO: [],
    OK.IMM_10_12_LIMIT4: [(3, 10)],
    OK.IMM_12_MAYBE_SHIFT_0: [(1, 12)],
    OK.IMM_12_MAYBE_SHIFT_1: [(1, 12)],
    OK.IMM_12_MAYBE_SHIFT_2: [(1, 12)],
    OK.IMM_12_MAYBE_SHIFT_3: [(1, 12)],
    OK.IMM_12_MAYBE_SHIFT_4: [(1, 12)],
    OK.IMM_SHIFTED_5_20_21_22: [(18, 5)],
}

FIELDS_SHIFT: Dict[OK, List[BIT_RANGE]] = {
    OK.SHIFT_22_23: [(2, 22)],
    OK.SHIFT_22_23_NO_ROR: [(2, 22)],
    OK.SHIFT_15_W: [(1, 15)],
    OK.SHIFT_15_X: [(1, 15)],
}

# merge all dicts from above
FIELD_DETAILS: Dict[OK, List[BIT_RANGE]] = {
    **FIELDS_REG,
    **FIELDS_SHIFT,
    **FIELDS_IMM,
}


def DecodeOperand(operand_kind: OK, value: int) -> int:
    """ Decodes an operand into an int."""
    tmp = 0
    for width, pos in FIELD_DETAILS[operand_kind]:
        mask = (1 << width) - 1
        x = (value >> pos) & mask
        tmp = tmp << width | x
    return tmp


def EncodeOperand(operand_kind, val) -> List[Tuple[int, int, int]]:
    """ Encodes an int into a list of bit-fields"""
    bits: List[Tuple[int, int, int]] = []
    # Note: going reverse is crucial to make Hi/Lo and P/U/W work
    for width, pos in reversed(FIELD_DETAILS[operand_kind]):
        mask = (1 << width) - 1
        bits.append((mask, val & mask, pos))
        val = val >> width
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
    ATOMIC_WITH_STATUS = 1 << 9

    COND_BRANCH = 1 << 11
    BRANCH = 1 << 12
    BRANCH_INDIRECT = 1 << 13
    CALL = 1 << 15
    CALL_INDIRECT = 1 << 20
    MOVEFROMSR = 1 << 16
    TEST = 1 << 17
    PREFETCH = 1 << 18
    MULTIPLE = 1 << 19
    SYSCALL = 1 << 21
    BYTEREORDER = 1 << 22
    MISC = 1 << 23
    REG_PAIR = 1 << 25
    COND_PARAM = 1 << 26  # csel, etc which have a condition-code as a parameter
    DOMAIN_PARAM = 1 << 27  # dmb, etc which have a sharable domain as a parameter
    EXTENSION_PARAM = 1 << 28
    STACK_OPS = 1 << 29
    # do not go above 31 as we want these to fit into a 32 bit word


# number of bytes accessed by a memory opcode (ld/st)
@enum.unique
class MEM_WIDTH(enum.Enum):
    NA = 0
    W1 = 1
    W2 = 2
    W4 = 3
    W8 = 4
    W16 = 5


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
            all_bits += [((1 << width) - 1, 0, pos)
                         for width, pos in FIELD_DETAILS[f]]
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


def _CheckOpcodeSeparability():
    """Make sure we completely understand the case where the
     bit_mask and bit_value are not uniquely specifying an opcode.
     In this case the more specific one pattern must precede the
     less specific.
     """
    for bucket_no, bucket in enumerate(Opcode.ordered_opcodes):
        # if bucket:
        #    print (f"0x{bucket_no:02x}: {len(bucket):2} {[b.name for b in bucket]}")
        for n, o1 in enumerate(bucket):
            for o2 in bucket[n + 1:]:
                m = o1.bit_mask & o2.bit_mask
                if o1.bit_value & m != o2.bit_value & m:
                    continue

                print(f"potential conflict: {o1.name} vs {o2.name}")
                assert False
    return True


########################################
root010 = (7, 2, 26)
########################################

for ext, w_bit in [("w", (1, 0, 31)), ("x", (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    dst_reg_sp = OK.XREG_0_4_SP if ext == "x" else OK.WREG_0_4_SP

    src1_reg = OK.XREG_5_9 if ext == "x" else OK.WREG_5_9
    src1_reg_sp = OK.XREG_5_9_SP if ext == "x" else OK.WREG_5_9_SP

    src2_reg = OK.XREG_16_20 if ext == "x" else OK.WREG_16_20
    dst2_reg = OK.XREG_10_14 if ext == "x" else OK.WREG_10_14

    for name, bits in [("add", [(3, 0, 29), (3, 3, 24), (1, 0, 21)]),
                       ("and", [(3, 0, 29), (3, 2, 24), (1, 0, 21)]),
                       ("bic", [(3, 0, 29), (3, 2, 24), (1, 1, 21)]),
                       ("sub", [(3, 2, 29), (3, 3, 24), (1, 0, 21)]),
                       ("orr", [(3, 1, 29), (3, 2, 24), (1, 0, 21)]),
                       ("orn", [(3, 1, 29), (3, 2, 24), (1, 1, 21)]),
                       ("eor", [(3, 2, 29), (3, 2, 24), (1, 0, 21)]),
                       ("eon", [(3, 2, 29), (3, 2, 24), (1, 1, 21)])]:
        Opcode(name, ext + "_reg", [root010, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg, OK.SHIFT_22_23, OK.IMM_10_15],
               OPC_FLAG(0))

    for name, bits in [("ands", [(3, 3, 29), (3, 2, 24), (1, 0, 21)]),
                       ("bics", [(3, 3, 29), (3, 2, 24), (1, 1, 21)])]:
        Opcode(name, ext + "_reg", [root010, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg, OK.SHIFT_22_23, OK.IMM_10_15],
               OPC_FLAG(0), sr_update=SR_UPDATE.NZCV)

    for name, bits in [("adds", [(3, 1, 29), (3, 3, 24), (1, 0, 21)]),
                       ("subs", [(3, 3, 29), (3, 3, 24), (1, 0, 21)])]:
        Opcode(name, ext + "_reg", [root010, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg, OK.SHIFT_22_23_NO_ROR, OK.IMM_10_15],
               OPC_FLAG(0), sr_update=SR_UPDATE.NZCV)

    for ext2, option in [("uxtb", (7, 0, 13)), ("uxth", (7, 1, 13)),
                         ("uxtw", (7, 2, 13)), ("uxtx", (7, 3, 13)),
                         ("sxtb", (7, 4, 13)), ("sxth", (7, 5, 13)),
                         ("sxtw", (7, 6, 13)), ("sxtx", (7, 7, 13))]:
        src2_ext_reg = OK.XREG_16_20 if ext2[-1] == "x" else OK.WREG_16_20
        for name, bits in [("add", [(3, 0, 29), (0x1f, 0x19, 21)]),
                           ("sub", [(3, 2, 29), (0x1f, 0x19, 21)])]:
            Opcode(name, ext + "_reg_" + ext2, [root010, w_bit, option] + bits,
                   [dst_reg_sp, src1_reg_sp, src2_ext_reg, OK.IMM_10_12_LIMIT4],
                   OPC_FLAG.STACK_OPS | OPC_FLAG.EXTENSION_PARAM)
        for name, bits in [("adds", [(3, 1, 29), (0x1f, 0x19, 21)]),
                           ("subs", [(3, 3, 29), (0x1f, 0x19, 21)])]:
            Opcode(name, ext + "_reg_" + ext2, [root010, w_bit, option] + bits,
                   [dst_reg, src1_reg_sp, src2_ext_reg, OK.IMM_10_12_LIMIT4],
                   OPC_FLAG.EXTENSION_PARAM, sr_update=SR_UPDATE.NZCV)

for ext, w_bit in [("x", (7, 6, 29)), ("w", (7, 4, 29)), ("h", (7, 2, 29)), ("b", (7, 0, 29))]:
    reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    Opcode("ldxr", ext, [w_bit, root010, (0xffff, 0x17df, 10)],
           [reg, OK.XREG_5_9], OPC_FLAG.LOAD | OPC_FLAG.ATOMIC)
    Opcode("ldaxr", ext, [w_bit, root010, (0xffff, 0x17ff, 10)],
           [reg, OK.XREG_5_9], OPC_FLAG.LOAD | OPC_FLAG.ATOMIC)
    Opcode("ldar", ext, [w_bit, root010, (0xffff, 0x37ff, 10)],
           [reg, OK.XREG_5_9], OPC_FLAG.LOAD | OPC_FLAG.ATOMIC)
    Opcode("stxr", ext, [w_bit, root010, (0x1f, 0, 21), (0x3f, 0x1f, 10)],
           [OK.WREG_16_20, OK.XREG_5_9, reg], OPC_FLAG.STORE | OPC_FLAG.ATOMIC_WITH_STATUS)
    Opcode("stlxr", ext, [w_bit, root010, (0x1f, 0, 21), (0x3f, 0x3f, 10)],
           [OK.WREG_16_20, OK.XREG_5_9, reg], OPC_FLAG.STORE | OPC_FLAG.ATOMIC_WITH_STATUS)
    Opcode("stlr", ext, [w_bit, root010, (0xffff, 0x27ff, 10)],
           [OK.XREG_5_9, reg], OPC_FLAG.STORE | OPC_FLAG.ATOMIC)

for ext, w_bit, imm in [("x", (7, 5, 29), OK.SIMM_15_21_TIMES8),
                        ("w", (7, 1, 29), OK.SIMM_15_21_TIMES4),
                        ("sw", (7, 3, 29), OK.SIMM_15_21_TIMES4)]:
    dst1 = OK.XREG_0_4 if ext != "w" else OK.WREG_0_4
    dst2 = OK.XREG_10_14 if ext != "w" else OK.WREG_10_14
    Opcode("ldp", ext + "_imm_post", [w_bit, root010, (0xf, 3, 22)],
           [dst1, dst2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)
    Opcode("ldp", ext + "_imm_pre", [w_bit, root010, (0xf, 7, 22)],
           [dst1, dst2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)
    Opcode("ldp", ext + "_imm", [w_bit, root010, (0xf, 5, 22)],
           [dst1, dst2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)

for ext, w_bit, imm_scaled in [("x", (7, 5, 29), OK.SIMM_15_21_TIMES8),
                               ("w", (7, 1, 29), OK.SIMM_15_21_TIMES4)]:
    src1 = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    src2 = OK.XREG_10_14 if ext == "x" else OK.WREG_10_14
    Opcode("stp", ext + "_imm_post", [w_bit, root010, (0xf, 2, 22)],
           [OK.XREG_5_9_SP, imm_scaled, src1, src2], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)

    Opcode("stp", ext + "_imm_pre", [w_bit, root010, (0xf, 6, 22)],
           [OK.XREG_5_9_SP, imm_scaled, src1, src2], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)
    Opcode("stp", ext + "_imm", [w_bit, root010, (0xf, 4, 22)],
           [OK.XREG_5_9_SP, imm_scaled, src1, src2], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)

########################################
root011 = (7, 3, 26)
########################################
for ext, reg1, reg2, imm, bits in [
    ("s", OK.SREG_0_4, OK.SREG_10_14, OK.SIMM_15_21_TIMES4, (7, 1, 29)),
    ("d", OK.DREG_0_4, OK.DREG_10_14, OK.SIMM_15_21_TIMES8, (7, 3, 29)),
    ("q", OK.QREG_0_4, OK.QREG_10_14, OK.SIMM_15_21_TIMES16, (7, 5, 29))]:
    Opcode("fstp", ext + "_imm_post", [bits, root011, (0xf, 2, 22)],
           [OK.XREG_5_9_SP, imm, reg1, reg2, ], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)
    Opcode("fstp", ext + "_imm_pre", [bits, root011, (0xf, 6, 22)],
           [OK.XREG_5_9_SP, imm, reg1, reg2], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)
    Opcode("fstp", ext + "_imm", [bits, root011, (0xf, 4, 22)],
           [OK.XREG_5_9_SP, imm, reg1, reg2], OPC_FLAG.STORE | OPC_FLAG.REG_PAIR)
    Opcode("fldp", ext + "_imm_post", [bits, root011, (0xf, 3, 22)],
           [reg1, reg2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)
    Opcode("fldp", ext + "_imm_pre", [bits, root011, (0xf, 7, 22)],
           [reg1, reg2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)
    Opcode("fldp", ext + "_imm", [bits, root011, (0xf, 5, 22)],
           [reg1, reg2, OK.XREG_5_9_SP, imm], OPC_FLAG.LOAD | OPC_FLAG.REG_PAIR)

########################################
root100 = (7, 4, 26)
########################################
for ext, w_bit, w_bit2 in [("w", (1, 0, 31), (1, 0, 22)),
                           ("x", (1, 1, 31), (1, 1, 22))]:
    dst_reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    dst_reg_sp = OK.XREG_0_4_SP if ext == "x" else OK.WREG_0_4_SP
    src1_reg = OK.XREG_5_9 if ext == "x" else OK.WREG_5_9
    src1_reg_sp = OK.XREG_5_9_SP if ext == "x" else OK.WREG_5_9_SP
    src2_reg = OK.XREG_16_20 if ext == "x" else OK.WREG_16_20

    for name, bits in [("add", [(3, 0, 29), (3, 1, 24)]),
                       ("sub", [(3, 2, 29), (3, 1, 24)])]:
        Opcode(name, "imm_" + ext, [root100, w_bit, (1, 0, 23)] + bits,
               [dst_reg_sp, src1_reg_sp, OK.IMM_SHIFTED_10_21_22], OPC_FLAG.STACK_OPS)

    for name, bits in [("adds", [(3, 1, 29), (3, 1, 24)]),
                       ("subs", [(3, 3, 29), (3, 1, 24)])]:
        Opcode(name, "imm_" + ext, [root100, w_bit, (1, 0, 23)] + bits,
               [dst_reg, src1_reg, OK.IMM_SHIFTED_10_21_22], OPC_FLAG(0),
               sr_update=SR_UPDATE.NZCV)

    imm = OK.IMM_10_15_16_22_X if ext == "x" else OK.IMM_10_15_16_22_W
    for name, bits in [("and", [(3, 0, 29), (7, 4, 23)]),
                       ("eor", [(3, 2, 29), (7, 4, 23)]),
                       ("orr", [(3, 1, 29), (7, 4, 23)])]:
        Opcode(name, "imm_" + ext, [root100, w_bit] + bits,
               [dst_reg_sp, src1_reg, imm], OPC_FLAG.STACK_OPS)

    for name, bits in [("ands", [(3, 3, 29), (7, 4, 23)])]:
        Opcode(name, "imm_" + ext, [root100, w_bit] + bits,
               [dst_reg, src1_reg, imm], OPC_FLAG(0), sr_update=SR_UPDATE.NZCV)

    for name, bits in [("bfm", [(3, 1, 29), (7, 6, 23)]),
                       ("ubfm", [(3, 2, 29), (7, 6, 23)]),
                       ("sbfm", [(3, 0, 29), (7, 6, 23)])]:
        Opcode(name, ext, [root100, w_bit, w_bit2] + bits,
               [dst_reg, src1_reg, OK.IMM_16_21, OK.IMM_10_15], OPC_FLAG(0))
    Opcode("extr", ext, [w_bit, (3, 0, 29), root100, (7, 7, 23), (1, ext == "x", 22), (1, 0, 21)],
           [dst_reg, src1_reg, src2_reg, OK.IMM_10_15], OPC_FLAG(0))

    Opcode("movk", ext, [w_bit, (3, 3, 29), root100, (7, 5, 23)],
           [dst_reg, OK.IMM_SHIFTED_5_20_21_22], OPC_FLAG(0))

    Opcode("movz", ext + "_imm", [w_bit, (3, 2, 29), root100, (7, 5, 23)],
           [dst_reg, OK.IMM_SHIFTED_5_20_21_22], OPC_FLAG(0))
    Opcode("movn", ext + "_imm_", [w_bit, (3, 0, 29), root100, (7, 5, 23)],
           [dst_reg, OK.IMM_SHIFTED_5_20_21_22], OPC_FLAG(0))

Opcode("adr", "", [root100, (1, 0, 31), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_PCREL_5_23_29_30], OPC_FLAG(0))
Opcode("adrp", "", [root100, (1, 1, 31), (3, 0, 24)],
       [OK.XREG_0_4, OK.SIMM_PCREL_5_23_29_30], OPC_FLAG(0))

########################################
root101 = (7, 5, 26)
########################################

Opcode("b", "", [root101, (7, 0, 29)],
       [OK.SIMM_PCREL_0_25], OPC_FLAG.BRANCH)

Opcode("bl", "", [root101, (7, 4, 29)],
       [OK.REG_LINK, OK.SIMM_PCREL_0_25], OPC_FLAG.CALL)

Opcode("ret", "", [root101, (7, 6, 29), (0xffff, 0x97c0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG.BRANCH_INDIRECT)
Opcode("br", "", [root101, (7, 6, 29), (0xffff, 0x87c0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG(0))
Opcode("blr", "", [root101, (7, 6, 29), (0xffff, 0x8fc0, 10), (0x1f, 0, 0)],
       [OK.XREG_5_9], OPC_FLAG.CALL_INDIRECT)

for cond_val, cond_name in enumerate(CONDITION_CODES):
    Opcode("b." + cond_name, "", [root101, (7, 2, 29), (3, 0, 24), (0x1f, cond_val, 0)],
           [OK.SIMM_PCREL_5_23], OPC_FLAG.COND_BRANCH)

for ext, w_bit in [("w", (1, 0, 31)), ("x", (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    Opcode("cbnz", ext, [w_bit, root101, (3, 1, 29), (3, 1, 24)],
           [dst_reg, OK.SIMM_PCREL_5_23], OPC_FLAG.COND_BRANCH)
    Opcode("cbz", ext, [w_bit, root101, (3, 1, 29), (3, 0, 24)],
           [dst_reg, OK.SIMM_PCREL_5_23], OPC_FLAG.COND_BRANCH)

Opcode("tbz", "", [root101, (3, 1, 29), (3, 2, 24)],
       [OK.XREG_0_4, OK.IMM_19_23_31, OK.SIMM_PCREL_5_18], OPC_FLAG.COND_BRANCH)
Opcode("tbnz", "", [root101, (3, 1, 29), (3, 3, 24)],
       [OK.XREG_0_4, OK.IMM_19_23_31, OK.SIMM_PCREL_5_18], OPC_FLAG.COND_BRANCH)

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
       [], OPC_FLAG.DOMAIN_PARAM)
Opcode("dmb", "ishld", [root101, (7, 6, 29), (0x3ffffff, 0x10339bf, 0)],
       [], OPC_FLAG.DOMAIN_PARAM)
Opcode("dmb", "ishst", [root101, (7, 6, 29), (0x3ffffff, 0x1033abf, 0)],
       [], OPC_FLAG.DOMAIN_PARAM)
Opcode("dsb", "ish", [root101, (7, 6, 29), (0x3ffffff, 0x1033b9f, 0)],
       [], OPC_FLAG.DOMAIN_PARAM)
Opcode("dsb", "ishld", [root101, (7, 6, 29), (0x3ffffff, 0x103399f, 0)],
       [], OPC_FLAG.DOMAIN_PARAM)
Opcode("dsb", "ishst", [root101, (7, 6, 29), (0x3ffffff, 0x1033a9f, 0)],
       [], OPC_FLAG.DOMAIN_PARAM)

########################################
root110 = (7, 6, 26)
########################################
for ext, w_bit in [("w", (1, 0, 31)), ("x", (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if ext == "x" else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if ext == "x" else OK.WREG_16_20
    src3_reg = OK.XREG_10_14 if ext == "x" else OK.WREG_10_14

    for name, bits in [("madd", [(3, 0, 29), (1, 0, 15)]),
                       ("msub", [(3, 0, 29), (1, 1, 15)])]:
        Opcode(name, ext, [root110, w_bit, (3, 3, 24), (7, 0, 21)] + bits,
               [dst_reg, src1_reg, src2_reg, src3_reg], OPC_FLAG(0))

    for name, bits in [("udiv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 2, 10)]),
                       ("sdiv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 3, 10)]),
                       ("lslv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 8, 10)]),
                       ("lsrv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 9, 10)]),
                       ("asrv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 0xa, 10)]),
                       ("rorv", [(3, 0, 29), (0x1f, 0x16, 21), (0x3f, 0xb, 10)]),
                       ("adc", [(3, 0, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)]),
                       ("sbc", [(3, 2, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)])]:
        Opcode(name, ext, [root110, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg], OPC_FLAG(0))

    for name, bits, in [
        ("adcs", [(3, 1, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)]),
        ("sbcs", [(3, 3, 29), (0x1f, 0x10, 21), (0x3f, 0, 10)])]:
        Opcode(name, ext, [root110, w_bit] + bits,
               [dst_reg, src1_reg, src2_reg], OPC_FLAG(0), sr_update=SR_UPDATE.NZCV)

for name, bits in [("smaddl", [(3, 0, 29), (7, 1, 21), (1, 0, 15)]),
                   ("smsubl", [(3, 0, 29), (7, 1, 21), (1, 1, 15)]),
                   ("umaddl", [(3, 0, 29), (7, 5, 21), (1, 0, 15)]),
                   ("umsubl", [(3, 0, 29), (7, 5, 21), (1, 1, 15)])]:
    Opcode(name, "", [root110, (1, 1, 31), (3, 3, 24)] + bits,
           [OK.XREG_0_4, OK.WREG_5_9, OK.WREG_16_20, OK.XREG_10_14], OPC_FLAG(0))

for name, bits in [("smulh", [(3, 0, 29), (7, 2, 21), (1, 0, 15)]),
                   ("umulh", [(3, 0, 29), (7, 6, 21), (1, 0, 15)])]:
    Opcode(name, "", [root110, (1, 1, 31), (3, 3, 24), (0x1f, 0x1f, 10)] + bits,
           [OK.XREG_0_4, OK.XREG_5_9, OK.XREG_16_20], OPC_FLAG(0))

for ext, scaled_offset, w_bits, shift in [
    ("x", OK.IMM_10_21_times_8, (7, 7, 29), OK.IMM_12_MAYBE_SHIFT_3),
    ("w", OK.IMM_10_21_times_4, (7, 5, 29), OK.IMM_12_MAYBE_SHIFT_2),
    ("h", OK.IMM_10_21_times_2, (7, 3, 29), OK.IMM_12_MAYBE_SHIFT_1),
    ("b", OK.IMM_10_21, (7, 1, 29), OK.IMM_12_MAYBE_SHIFT_0)]:
    src = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    dst = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4

    Opcode("ldr", ext + "_imm", [root110, w_bits, (0xf, 5, 22)],
           [dst, OK.XREG_5_9_SP, scaled_offset], OPC_FLAG.LOAD)
    Opcode("ldr", ext + "_imm_pre", [root110, w_bits, (0x1f, 2, 21), (3, 3, 10)],
           [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
    Opcode("ldr", ext + "_imm_post", [root110, w_bits, (0x1f, 2, 21), (3, 1, 10)],
           [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
    Opcode("ldur", ext + "_imm", [root110, w_bits, (0x1f, 2, 21), (3, 0, 10)],
           [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)

    Opcode("ldr", ext + "_reg_w", [root110, w_bits, (0x1f, 3, 21), (3, 2, 13), (3, 2, 10)],
           [dst, OK.XREG_5_9_SP, OK.WREG_16_20, OK.SHIFT_15_W, shift], OPC_FLAG.LOAD)
    Opcode("ldr", ext + "_reg_x", [root110, w_bits, (0x1f, 3, 21), (3, 3, 13), (3, 2, 10)],
           [dst, OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift], OPC_FLAG.LOAD)

    Opcode("str", ext + "_reg_w", [root110, w_bits, (0x1f, 1, 21), (3, 2, 13), (3, 2, 10)],
           [OK.XREG_5_9_SP, OK.WREG_16_20, OK.SHIFT_15_W, shift, src], OPC_FLAG.STORE)
    Opcode("str", ext + "_reg_x", [root110, w_bits, (0x1f, 1, 21), (3, 3, 13), (3, 2, 10)],
           [OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift, src], OPC_FLAG.STORE)

    Opcode("str", ext + "_imm", [root110, w_bits, (0xf, 4, 22)],
           [OK.XREG_5_9_SP, scaled_offset, src], OPC_FLAG.STORE)
    Opcode("str", ext + "_imm_pre", [root110, w_bits, (0x1f, 0, 21), (3, 3, 10)],
           [OK.XREG_5_9_SP, OK.SIMM_12_20, src], OPC_FLAG.STORE)
    Opcode("str", ext + "_imm_post", [root110, w_bits, (0x1f, 0, 21), (3, 1, 10)],
           [OK.XREG_5_9_SP, OK.SIMM_12_20, src], OPC_FLAG.STORE)
    Opcode("stur", ext + "_imm", [root110, w_bits, (0x1f, 0, 21), (3, 0, 10)],
           [OK.XREG_5_9_SP, OK.SIMM_12_20, src], OPC_FLAG.STORE)

    if ext == "w":
        Opcode("ldrs" + ext, "imm", [root110, w_bits, (0xf, 6, 22)],
               [OK.XREG_0_4, OK.XREG_5_9_SP, scaled_offset], OPC_FLAG.LOAD)
        Opcode("ldrs" + ext, "imm_pre", [root110, w_bits, (0x1f, 4, 21), (3, 3, 10)],
               [OK.XREG_0_4, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
        Opcode("ldrs" + ext, "imm_post", [root110, w_bits, (0x1f, 4, 21), (3, 1, 10)],
               [OK.XREG_0_4, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
        Opcode("ldurs" + ext, "imm_post", [root110, w_bits, (0x1f, 4, 21), (3, 0, 10)],
               [OK.XREG_0_4, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
        Opcode("ldrs" + ext, "reg_w", [root110, w_bits, (0x1f, 5, 21), (3, 2, 13), (3, 2, 10)],
               [OK.XREG_0_4, OK.XREG_5_9, OK.WREG_16_20, OK.SHIFT_15_W, shift], OPC_FLAG(0))
        Opcode("ldrs" + ext, "reg_x", [root110, w_bits, (0x1f, 5, 21), (3, 3, 13), (3, 2, 10)],
               [OK.XREG_0_4, OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift], OPC_FLAG.LOAD)

    if ext == "b" or ext == "h":
        for ext2, w2_bits, dst in [("w", (1, 1, 22), OK.WREG_0_4), ("x", (1, 0, 22), OK.XREG_0_4)]:
            # scaled
            Opcode(f"ldrs" + ext, ext2 + "_imm", [root110, w_bits, (7, 3, 23), w2_bits],
                   [dst, OK.XREG_5_9_SP, scaled_offset], OPC_FLAG.LOAD)
            # pre/post
            Opcode("ldrs" + ext, ext2 + "_imm_pre", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 3, 10)],
                   [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
            Opcode("ldrs" + ext, ext2 + "_imm_post", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 1, 10)],
                   [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
            # unscaled
            Opcode("ldurs" + ext, ext2 + "_imm", [root110, w_bits, (7, 1, 23), w2_bits, (1, 0, 21), (3, 0, 10)],
                   [dst, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
            Opcode(f"ldrs" + ext, ext2 + "_reg_w",
                   [root110, w_bits, (7, 1, 23), w2_bits, (1, 1, 21), (3, 2, 13), (3, 2, 10)],
                   [dst, OK.XREG_5_9_SP, OK.WREG_16_20, OK.SHIFT_15_W, shift], OPC_FLAG.LOAD)
            Opcode(f"ldrs" + ext, ext2 + "_reg_x",
                   [root110, w_bits, (7, 1, 23), w2_bits, (1, 1, 21), (3, 3, 13), (3, 2, 10)],
                   [dst, OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift], OPC_FLAG.LOAD)

for ext, w_bits in [("w", (1, 0, 31)), ("x", (1, 1, 31))]:
    dst_reg = OK.XREG_0_4 if ext == "x" else OK.WREG_0_4
    src1_reg = OK.XREG_5_9 if ext == "x" else OK.WREG_5_9
    src2_reg = OK.XREG_16_20 if ext == "x" else OK.WREG_16_20
    for cond_val, cond_name in enumerate(CONDITION_CODES):
        for name, bits in [("csel", [(3, 0, 29), (3, 0, 10)]),
                           ("csneg", [(3, 2, 29), (3, 1, 10)]),
                           ("csinc", [(3, 0, 29), (3, 1, 10)]),
                           ("csinv", [(3, 2, 29), (3, 0, 10)])]:
            Opcode(name, f"{ext}_{cond_name}",
                   [w_bits, root110, (0x1f, 0x14, 21), (0xf, cond_val, 12)] + bits,
                   [dst_reg, src1_reg, src2_reg], OPC_FLAG.COND_PARAM)

        for name, bits in [("ccmp", (3, 3, 29)),
                           ("ccmn", (3, 1, 29))]:
            common = [w_bits, root110, (0x1f, 0x12, 21), (0xf, cond_val, 12), (1, 0, 4)]
            Opcode(name, f"{ext}_reg_{cond_name}",
                   common + [bits, (3, 0, 10)],
                   [src1_reg, src2_reg, OK.IMM_COND_0_3], OPC_FLAG.COND_PARAM)
            Opcode(name, f"{ext}_imm_{cond_name}",
                   common + [bits, (3, 2, 10)],
                   [src1_reg, OK.IMM_16_20, OK.IMM_COND_0_3], OPC_FLAG.COND_PARAM)

for name, ext, bits in [("rbit", "x", [(7, 6, 29), (7, 0, 10)]),
                        ("rbit", "w", [(7, 2, 29), (7, 0, 10)]),
                        ("clz", "x", [(7, 6, 29), (7, 4, 10)]),
                        ("clz", "w", [(7, 2, 29), (7, 4, 10)]),
                        ("cls", "x", [(7, 6, 29), (7, 5, 10)]),
                        ("cls", "w", [(7, 2, 29), (7, 5, 10)]),
                        ("rev", "x", [(7, 6, 29), (7, 3, 10)]),
                        ("rev", "w", [(7, 2, 29), (7, 2, 10)]),
                        ("rev32", "", [(7, 6, 29), (7, 2, 10)]),
                        ("rev16", "x", [(7, 6, 29), (7, 1, 10)]),
                        ("rev16", "w", [(7, 2, 29), (7, 1, 10)])]:
    dst = OK.XREG_0_4 if ext != "w" else OK.WREG_0_4
    src = OK.XREG_5_9 if ext != "w" else OK.WREG_5_9

    Opcode(name, ext, [root110, (0x1fff, 0x1600, 13)] + bits,
           [dst, src], OPC_FLAG(0))

########################################
root111 = (7, 7, 26)
########################################

for ext, w_bit in [("s", (1, 0, 22)),
                   ("d", (1, 1, 22))]:
    dst_reg = OK.DREG_0_4 if ext == "d" else OK.SREG_0_4
    src1_reg = OK.DREG_5_9 if ext == "d" else OK.SREG_5_9
    src2_reg = OK.DREG_16_20 if ext == "d" else OK.SREG_16_20
    src3_reg = OK.DREG_10_14 if ext == "d" else OK.SREG_10_14

    Opcode("fmov", ext + "_imm", [(7, 0, 29), root111, (7, 4, 23), w_bit, (1, 1, 21), (0xff, 0x80, 5)],
           [dst_reg, OK.FLT_13_20], OPC_FLAG(0))

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
        Opcode(name, ext, [(7, 0, 29), root111, (7, 4, 23), w_bit, (1, 1, 21), bits],
               [dst_reg, src1_reg, src2_reg], OPC_FLAG(0))

    for name, bits in [
        ("fmadd", [(7, 6, 23), (1, 0, 21), (1, 0, 15)]),
        ("fmsub", [(7, 6, 23), (1, 0, 21), (1, 1, 15)]),
        ("fnmadd", [(7, 6, 23), (1, 1, 21), (1, 0, 15)]),
        ("fnmsub", [(7, 6, 23), (1, 1, 21), (1, 1, 15)]),
    ]:
        Opcode(name, ext, [root111, (7, 0, 29), w_bit] + bits,
               [dst_reg, src1_reg, src2_reg, src3_reg], OPC_FLAG(0))

    for name, bits in [
        ("fabd", [(7, 5, 23), (0x3f, 0x35, 10)]),
        ("fcmge", [(7, 4, 23), (0x3f, 0x39, 10)]),
        ("fcmgt", [(7, 5, 23), (0x3f, 0x39, 10)]),
    ]:
        Opcode(name, ext, [root111, (7, 3, 29), w_bit, (1, 1, 21)] + bits,
               [dst_reg, src1_reg, src2_reg], OPC_FLAG(0))

    Opcode("fcmp", ext + "_zero", [root111, (7, 0, 29), w_bit, (1, 1, 21)] +
           [(7, 4, 23), (0x1f, 0, 16), (0x3f, 8, 10), (0x1f, 8, 0)],
           [src1_reg, OK.IMM_FLT_ZERO], OPC_FLAG(0))
    Opcode("fcmp", ext, [root111, (7, 0, 29), w_bit, (1, 1, 21)] + [(7, 4, 23), (0x3f, 8, 10), (0x1f, 0, 0)],
           [src1_reg, src2_reg], OPC_FLAG(0))

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
               [dst_reg, src1_reg], OPC_FLAG(0))

    for cond_val, cond_name in enumerate(["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc",
                                          "hi", "ls", "ge", "lt", "gt", "le"]):
        Opcode(f"fcsel", f"{ext}_{cond_name}",
               [(7, 0, 29), root111, (7, 4, 23), w_bit, (1, 1, 21), (0xf, cond_val, 12), (3, 3, 10)],
               [dst_reg, src1_reg, src2_reg], OPC_FLAG.COND_PARAM)
        Opcode("fccmp", f"{ext}_{cond_name}",
               [(7, 0, 29), root111, (7, 4, 23), w_bit, (1, 1, 21), (0xf, cond_val, 12), (3, 1, 10), (1, 0, 4)],
               [src1_reg, src2_reg, OK.IMM_COND_0_3], OPC_FLAG.COND_PARAM)

for ext, dst, src, bits in [
    ("s_from_w", OK.SREG_0_4, OK.WREG_5_9, [(1, 0, 31), (3, 0, 22), (1, 0, 19), (1, 1, 16)]),
    ("w_from_s", OK.WREG_0_4, OK.SREG_5_9, [(1, 0, 31), (3, 0, 22), (1, 0, 19), (1, 0, 16)]),
    ("d_from_x", OK.DREG_0_4, OK.XREG_5_9, [(1, 1, 31), (3, 1, 22), (1, 0, 19), (1, 1, 16)]),
    ("x_from_d", OK.XREG_0_4, OK.DREG_5_9, [(1, 1, 31), (3, 1, 22), (1, 0, 19), (1, 0, 16)]),
]:
    Opcode("fmov", ext, [(3, 0, 29), root111, (3, 6, 24), (3, 2, 20), (3, 3, 17), (0x3f, 0, 10)] +
           bits, [dst, src], OPC_FLAG(0))

for ext, reg, bits, scaled_imm, shift in [
    ("b", OK.BREG_0_4, [(3, 0, 30), (1, 0, 23)], OK.IMM_10_21, OK.IMM_12_MAYBE_SHIFT_0),
    ("h", OK.HREG_0_4, [(3, 1, 30), (1, 0, 23)], OK.IMM_10_21_times_2, OK.IMM_12_MAYBE_SHIFT_1),
    ("s", OK.SREG_0_4, [(3, 2, 30), (1, 0, 23)], OK.IMM_10_21_times_4, OK.IMM_12_MAYBE_SHIFT_2),
    ("d", OK.DREG_0_4, [(3, 3, 30), (1, 0, 23)], OK.IMM_10_21_times_8, OK.IMM_12_MAYBE_SHIFT_3),
    ("q", OK.QREG_0_4, [(3, 0, 30), (1, 1, 23)], OK.IMM_10_21_times_16, OK.IMM_12_MAYBE_SHIFT_4)]:
    ld_bits = [(1, 1, 29), root111, (1, 1, 22)] + bits
    Opcode("fldr", ext + "_imm_post", [(3, 0, 24), (1, 0, 21), (3, 1, 10)] + ld_bits,
           [reg, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
    Opcode("fldr", ext + "_imm_pre", [(3, 0, 24), (1, 0, 21), (3, 3, 10)] + ld_bits,
           [reg, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)
    Opcode("fldr", ext + "_imm", [(3, 1, 24)] + ld_bits,
           [reg, OK.XREG_5_9_SP, scaled_imm], OPC_FLAG.LOAD)

    Opcode("fldr", ext + "_reg_w", [(3, 0, 24), (3, 2, 13), (1, 1, 21), (3, 2, 10)] + ld_bits,
           [reg, OK.XREG_5_9_SP, OK.WREG_16_20, OK.SHIFT_15_W, shift], OPC_FLAG.LOAD)
    Opcode("fldr", ext + "_reg_x", [(3, 0, 24), (3, 3, 13), (1, 1, 21), (3, 2, 10)] + ld_bits,
           [reg, OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift], OPC_FLAG.LOAD)

    Opcode("fldur", ext + "_imm", [(3, 0, 24), (1, 0, 21), (3, 0, 10)] + ld_bits,
           [reg, OK.XREG_5_9_SP, OK.SIMM_12_20], OPC_FLAG.LOAD)

    st_bits = [(1, 1, 29), root111, (1, 0, 22)] + bits
    Opcode("fstr", ext + "_imm_post", [(3, 0, 24), (1, 0, 21), (3, 1, 10)] + st_bits,
           [OK.XREG_5_9_SP, OK.SIMM_12_20, reg], OPC_FLAG.STORE)
    Opcode("fstr", ext + "_imm_pre", [(3, 0, 24), (1, 0, 21), (3, 3, 10)] + st_bits,
           [OK.XREG_5_9_SP, OK.SIMM_12_20, reg], OPC_FLAG.STORE)
    Opcode("fstr", ext + "_imm", [(3, 1, 24)] + st_bits,
           [OK.XREG_5_9_SP, scaled_imm, reg], OPC_FLAG.STORE)
    Opcode("fstr", ext + "_reg_w", [(3, 0, 24), (1, 0, 13), (1, 1, 21), (1, 1, 14), (3, 2, 10)] + st_bits,
           [OK.XREG_5_9_SP, OK.WREG_16_20, OK.SHIFT_15_W, shift, reg], OPC_FLAG.STORE)
    Opcode("fstr", ext + "_reg_x", [(3, 0, 24), (1, 1, 13), (1, 1, 21), (1, 1, 14), (3, 2, 10)] + st_bits,
           [OK.XREG_5_9_SP, OK.XREG_16_20, OK.SHIFT_15_X, shift, reg], OPC_FLAG.STORE)
    Opcode("fstur", ext + "_imm", [(3, 0, 24), (1, 0, 21), (3, 0, 10)] + st_bits,
           [OK.XREG_5_9_SP, OK.SIMM_12_20, reg], OPC_FLAG.STORE)

for dst_ext, dst_reg, dst_bits in [("h", OK.HREG_0_4, (3, 3, 15)),
                                   ("s", OK.SREG_0_4, (3, 0, 15)),
                                   ("d", OK.DREG_0_4, (3, 1, 15))]:
    for src_ext, src_reg, src_bits in [("h", OK.HREG_5_9, (3, 3, 22)),
                                       ("s", OK.SREG_5_9, (3, 0, 22)),
                                       ("d", OK.DREG_5_9, (3, 1, 22))]:
        if src_ext != dst_ext:
            Opcode("fcvt", dst_ext + "_" + src_ext,
                   [(7, 0, 29), root111, (3, 2, 24), src_bits, (0x1f, 0x11, 17), dst_bits,
                    (0x1f, 0x10, 10)],
                   [dst_reg, src_reg], OPC_FLAG(0))

for dst_ext, dst_reg, dst_bits in [("w", OK.WREG_0_4, (1, 0, 31)),
                                   ("x", OK.XREG_0_4, (1, 1, 31))]:
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

for src_ext, src_reg, src_bits in [("w", OK.WREG_5_9, (1, 0, 31)),
                                   ("x", OK.XREG_5_9, (1, 1, 31))]:
    for dst_ext, dst_reg, dst_bits in [("s", OK.SREG_0_4, (1, 0, 22)),
                                       ("d", OK.DREG_0_4, (1, 1, 22))]:
        Opcode("scvtf", dst_ext + "_from_" + src_ext,
               [src_bits, (3, 0, 29), root111, (7, 4, 23), dst_bits, (0xfff, 0x880, 10)],
               [dst_reg, src_reg], OPC_FLAG(0))
        Opcode("ucvtf", dst_ext + "_from_" + src_ext,
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
        print ("Check Separability")
        _CheckOpcodeSeparability()
        print ("Check Logical Immediate Encoding")
        count = 0
        for size, sm in [(2, 0x3c), (4, 0x38), (8, 0x30), (16, 0x20), (32, 0), (64, 0)]:
            for ones in range (1, size):
                for r in range(size):
                    count += 1
                    n = (size == 64)
                    s = sm | (ones - 1)
                    i = (n << 12) | (r << 6) | s
                    x = DecodeLogicalImmediate(i, 64)
                    # print (f"{size:2d} {ones:2d} r={r:06b} s={s:06b} {x:016x}")
                    i2 = Encode_10_15_16_22_X(x)
                    assert i == i2, f"mismatch {i:x} {i2:x}"
        print(f"checked {count} immediates")
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
