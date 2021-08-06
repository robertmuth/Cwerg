#!/usr/bin/python3

"""
ARM 32bit assembler + disassembler + side-effects table

Based on: https://static.docs.arm.com/ddi0406/c/DDI0406C_C_arm_architecture_reference_manual.pdf

The table is will be initialized when the module is loaded and is
`const` afterwards. It can be searched via `Opcode.FindOpcode()`

Supported opcodes are those occurring in the *.dis files
which also serve as tests.
opcode are uniquely identified by a name and a variant. The variant
may be empty. The name adhere as much as possible to the manual above
and the elftool `objdump`.

Only ARM32 instructions are  supported (we target Raspberry PI3 and up)

Each opcode is accompanied by a list of fields which specified where
operands are located within an instruction word.
The field follow roughly the order of operands in the standard ARM assembler
notation with the following exceptions:
* written registers come first (mostly affects load opcodes)
* the shift direction comes before the shiftee and shift amount
* the address mode comes before the base register and offset operands

This file can also be run stand-alone to query opcode information, e.g.
`./arm_table.py mov` will show information for all opcodes with name `mov`.
Without any arguments the entire list of opcodes are shown

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
MAX_OPERANDS = 6

MAX_BIT_RANGES = 2


def Bits(*patterns) -> Tuple[int, int]:
    """
    combines are list of triples into a single triple
    """
    m = 0
    v = 0
    for mask, val, pos in patterns:
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


def BitsFromSignedInt(x, n_bits) -> Optional[int]:
    if x < 0:
        x = (1 << n_bits) + x
    assert x < (1 << n_bits), f"signed value out of range: {x}  bits:{n_bits}"
    return x


def BitsFromScaledInt(x, scale) -> Optional[int]:
    return x // scale


def DecodeRotatedImm(data) -> int:
    x = data & 0xff
    x += x << 32
    rot = (data & 0xf00) >> 7
    x >>= rot
    return x & 0xffffffff


def EncodeRotatedImm(x) -> Optional[int]:
    """Tries to convert the given integer into a 12bit arm rotated immediate

     return None if that os is not possible
     """
    if x < 0:
        x += (1 << 32)
    assert x >= 0
    x += x << 32  # duplicate the bit pattern
    for r in range(16):
        y = x >> (32 - r * 2)
        if y & 0xff == y & 0xffffffff:
            return (r << 8) | (y & 0xff)
    else:
        return None


def DecodeFloatZero(x) -> int:
    """Returns the integer representation of 32 bit float zero"""
    assert x == 0
    return 0


def EncodeFloatZero(x: int) -> Optional[int]:
    """Expects a 32 bit float in integer representation"""
    return 0 if x == 0 else None


############################################################
#
############################################################


@enum.unique
class PRED(enum.IntEnum):
    eq = 0
    ne = 1
    cs = 2
    cc = 3
    mi = 4
    pl = 5
    vs = 6
    vc = 7
    hi = 8
    ls = 9
    ge = 10
    lt = 11
    gt = 12
    le = 13
    al = 14
    invalid_pred = 15


@enum.unique
class REG(enum.IntEnum):
    r0 = 0
    r1 = 1
    r2 = 2
    r3 = 3
    r4 = 4
    r5 = 5
    r6 = 6
    r7 = 7
    r8 = 8
    r9 = 9
    sl = 10
    fp = 11
    ip = 12
    sp = 13
    lr = 14
    pc = 15


@enum.unique
class SREG(enum.IntEnum):
    s0 = 0
    s1 = 1
    s2 = 2
    s3 = 3
    s4 = 4
    s5 = 5
    s6 = 6
    s7 = 7
    s8 = 8
    s9 = 9
    s10 = 10
    s11 = 11
    s12 = 12
    s13 = 13
    s14 = 14
    s15 = 15
    s16 = 16
    s17 = 17
    s18 = 18
    s19 = 19
    s20 = 20
    s21 = 21
    s22 = 22
    s23 = 23
    s24 = 24
    s25 = 25
    s26 = 26
    s27 = 27
    s28 = 28
    s29 = 29
    s30 = 30
    s31 = 31


@enum.unique
class DREG(enum.IntEnum):
    d0 = 0
    d1 = 1
    d2 = 2
    d3 = 3
    d4 = 4
    d5 = 5
    d6 = 6
    d7 = 7
    d8 = 8
    d9 = 9
    d10 = 10
    d11 = 11
    d12 = 12
    d13 = 13
    d14 = 14
    d15 = 15


@enum.unique
class SHIFT(enum.IntEnum):
    lsl = 0
    lsr = 1
    asr = 2
    ror = 3  # also includes rrx


############################################################
# A field is a lists of bitranges which represent an operand
############################################################
@enum.unique
class OK(enum.Enum):
    Invalid = 0
    # arm register
    REG_0_3 = 1
    REG_8_11 = 2
    REG_12_15 = 3
    REG_16_19 = 4

    # arm register misc
    REG_PAIR_12_15 = 5  # {reg , reg+1}
    # d registers
    DREG_0_3_5 = 6
    DREG_12_15_22 = 7
    DREG_16_19_7 = 8
    # s registers
    SREG_0_3_5 = 9
    SREG_12_15_22 = 10
    SREG_16_19_7 = 11

    SHIFT_MODE_5_6 = 12

    # reglist
    REGLIST_0_15 = 13
    REG_RANGE_0_7 = 14
    REG_RANGE_1_7 = 15

    # misc
    PRED_28_31 = 16

    # immediates
    IMM_0_7_TIMES_4 = 17
    IMM_0_11 = 18
    IMM_0_3_8_11 = 19
    IMM_7_11 = 20
    IMM_10_11_TIMES_8 = 21
    IMM_0_23 = 22
    IMM_0_7_8_11 = 23
    IMM_FLT_ZERO = 24  # implicit 0.0 immediate
    IMM_0_11_16_19 = 25
    SIMM_0_23 = 26


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


BIT_RANGE = Tuple[int, int]


@enum.unique
class FK(enum.Enum):
    NONE = 0
    LIST = 1
    INT = 2
    INT_HEX = 3
    INT_SIGNED = 4
    INT_SIGNED_CUSTOM = 5
    FLT_CUSTOM = 6


class FieldInfo:

    def __init__(self, ranges, kind, enum_class=None, scale=1, prefix="", decoder=None, encoder=None):
        self.ranges: List[BIT_RANGE] = ranges
        self.bitwidth: int = sum([r[0] for r in ranges])
        self.kind: FK = kind
        self.enum_class = enum_class
        self.names: List[str] = [p.name for p in enum_class] if enum_class else []
        self.prefix: str = prefix
        self.scale: int = scale
        self.decoder = decoder
        self.encoder = encoder
        assert scale == 1 or kind in {FK.INT, FK.INT_HEX}
        assert not prefix or kind in {FK.INT, FK.INT_HEX}


FIELD_DETAILS: Dict[OK, FieldInfo] = {
    OK.Invalid: FieldInfo([], FK.NONE),
    OK.REG_0_3: FieldInfo([(4, 0)], FK.LIST, enum_class=REG),
    OK.REG_8_11: FieldInfo([(4, 8)], FK.LIST, enum_class=REG),
    OK.REG_12_15: FieldInfo([(4, 12)], FK.LIST, enum_class=REG),
    OK.REG_16_19: FieldInfo([(4, 16)], FK.LIST, enum_class=REG),
    OK.REG_PAIR_12_15: FieldInfo([(4, 12)], FK.LIST, enum_class=REG),
    #
    OK.DREG_0_3_5: FieldInfo([(1, 5), (4, 0)], FK.LIST, enum_class=DREG),
    OK.DREG_12_15_22: FieldInfo([(1, 22), (4, 12)], FK.LIST, enum_class=DREG),
    OK.DREG_16_19_7: FieldInfo([(1, 7), (4, 16)], FK.LIST, enum_class=DREG),
    #
    OK.SREG_0_3_5: FieldInfo([(4, 0), (1, 5)], FK.LIST, enum_class=SREG),
    OK.SREG_12_15_22: FieldInfo([(4, 12), (1, 22)], FK.LIST, enum_class=SREG),
    OK.SREG_16_19_7: FieldInfo([(4, 16), (1, 7)], FK.LIST, enum_class=SREG),
    #
    OK.SHIFT_MODE_5_6: FieldInfo([(2, 5)], FK.LIST, enum_class=SHIFT),
    OK.PRED_28_31: FieldInfo([(4, 28)], FK.LIST, enum_class=PRED),
    #
    OK.IMM_7_11: FieldInfo([(5, 7)], FK.INT),
    OK.IMM_0_23: FieldInfo([(24, 0)], FK.INT),
    OK.IMM_0_11_16_19: FieldInfo([(4, 16), (12, 0)], FK.INT),
    OK.IMM_0_11: FieldInfo([(12, 0)], FK.INT),
    OK.IMM_0_3_8_11: FieldInfo([(4, 8), (4, 0)], FK.INT),
    #
    OK.SIMM_0_23: FieldInfo([(24, 0)], FK.INT_SIGNED),
    OK.IMM_FLT_ZERO: FieldInfo([], FK.FLT_CUSTOM,
                               encoder=EncodeFloatZero, decoder=DecodeFloatZero),
    OK.IMM_0_7_8_11: FieldInfo([(12, 0)], FK.INT_SIGNED_CUSTOM,
                               encoder=EncodeRotatedImm, decoder=DecodeRotatedImm),

    OK.IMM_10_11_TIMES_8: FieldInfo([(2, 10)], FK.INT, scale=8),
    OK.IMM_0_7_TIMES_4: FieldInfo([(8, 0)], FK.INT, scale=4),

    # register set
    OK.REGLIST_0_15: FieldInfo([(16, 0)], FK.INT_HEX, prefix="reglist:"),
    OK.REG_RANGE_0_7: FieldInfo([(8, 0)], FK.INT, prefix="regrange:"),
    OK.REG_RANGE_1_7: FieldInfo([(7, 1)], FK.INT, prefix="regrange:"),
}

for ok in OK:
    assert ok in FIELD_DETAILS


def EncodeOperand(ok: OK, val: int) -> int:
    """Expects an unsigned 32 bit integer and emit it raw encoded equivalent
       to be insert into an a32 instruction as an operand

    The val can be interpreted as 32 bit signed ot even a 32bit float depending
    on t.kind.
    """
    assert val >= 0
    t = FIELD_DETAILS[ok]
    if t.kind == FK.INT_SIGNED_CUSTOM or t.kind == FK.FLT_CUSTOM:
        return t.encoder(val)
    elif t.kind == FK.LIST:
        assert val < len(t.names)
        return val
    elif t.kind == FK.INT_SIGNED:
        rest = val >> (t.bitwidth - 1)
        assert rest == 0 or rest + 1 == (1 << (32 - t.bitwidth + 1))
        return val & ((1 << t.bitwidth) - 1)
    if t.scale != 1:
        assert val % t.scale == 0
        val //= t.scale

    assert (val >> t.bitwidth) == 0
    return val


def DecodeOperand(ok: OK, val: int) -> int:
    """Convert a raw operand into something more human friendly

    Most operands are just passed through only a handful of OKs need this
    """
    t = FIELD_DETAILS[ok]
    if t.kind == FK.INT_SIGNED_CUSTOM or t.kind == FK.FLT_CUSTOM:
        return t.decoder(val)
    elif t.kind == FK.INT_SIGNED:
        return SignedIntFromBits(val, t.bitwidth) & 0xffffffff
    if t.scale != 1:
        val *= t.scale
    return val


def ExtractOperand(ok: OK, value: int) -> int:
    """ Decodes an operand into an int.

    This essentially shifts all the relevant bits to the right
    """
    tmp = 0
    for width, pos in FIELD_DETAILS[ok].ranges:
        mask = (1 << width) - 1
        x = (value >> pos) & mask
        tmp = tmp << width | x
    return tmp


def InsertOperand(ok: OK, val) -> List[Tuple[int, int, int]]:
    """ Encodes an int into a list of bit-fields

    This is essentially the inverse of ExtractOperand
    """
    bits: List[Tuple[int, int, int]] = []
    # Note: going reverse is crucial to make Hi/Lo and P/U/W work
    for width, pos in reversed(FIELD_DETAILS[ok].ranges):
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
    ADDR_PRE = (1 << 24)
    ADDR_POST = (1 << 25)
    ADDR_INC = (1 << 26)
    ADDR_DEC = (1 << 27)
    ADDR_UPDATE = (1 << 28)


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


# W[21],  # 1: write base reg
# U[23],  # 0: sub, 1: add
# P[24],  # 0: post 1:pre
STANDARD_ADDR_MODES = [
    #  post with out a write back is not allowed or a different kind of instruction
    ("sub_post", [(3, 0, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_DEC | OPC_FLAG.ADDR_UPDATE),
    ("add_post", [(3, 1, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_INC | OPC_FLAG.ADDR_UPDATE),
    ("sub", [(3, 2, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_DEC),
    ("add", [(3, 3, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_INC),
    ("sub_pre", [(3, 2, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_DEC | OPC_FLAG.ADDR_UPDATE),
    ("add_pre", [(3, 3, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_INC | OPC_FLAG.ADDR_UPDATE),
]

LIMITED_ADDR_MODES = [
    #  post with out a write back is not allowed or a different kind of instuction
    ("sub", [(1, 0, 23)], OPC_FLAG.ADDR_DEC | OPC_FLAG.ADDR_PRE),
    ("add", [(1, 1, 23)], OPC_FLAG.ADDR_INC | OPC_FLAG.ADDR_PRE),
]

MULTI_ADDR_MODES = [
    ("da", "", [(3, 0, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_DEC),
    ("ia", "", [(3, 1, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_INC),
    ("db", "", [(3, 2, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_DEC),
    ("ib", "", [(3, 3, 23), (1, 0, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_INC),
    ("da", "update", [(3, 0, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_DEC | OPC_FLAG.ADDR_UPDATE),
    ("ia", "update", [(3, 1, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_POST | OPC_FLAG.ADDR_INC | OPC_FLAG.ADDR_UPDATE),
    ("db", "update", [(3, 2, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_DEC | OPC_FLAG.ADDR_UPDATE),
    ("ib", "update", [(3, 3, 23), (1, 1, 21)],
     OPC_FLAG.ADDR_PRE | OPC_FLAG.ADDR_INC | OPC_FLAG.ADDR_UPDATE),
]

# _INS_MAGIC_CLASSIFIER: int = 0x0ff00000  # needs more work

_RE_OPCODE_NAME = re.compile(r"[a-z.0-9]+")

# We use the notion of variant to disambiguate opcodes with the same mnemonic
_VARIANTS: Set[str] = {
    "", "imm", "reg", "regreg", "regimm",
    "f32", "f64",
    "atof", "ftoa", "atos", "stoa",
    "zero", "s", "f",
    "APSR_nzcv_fpscr",
    "update",
    "f_update", "s_update"
}

_VARIANTS.update([t[0] for t in STANDARD_ADDR_MODES])
_VARIANTS.update(["f32_" + t[0] for t in STANDARD_ADDR_MODES])
_VARIANTS.update(["f64_" + t[0] for t in STANDARD_ADDR_MODES])
_VARIANTS.update(["imm_" + t[0] for t in STANDARD_ADDR_MODES])
_VARIANTS.update(["reg_" + t[0] for t in STANDARD_ADDR_MODES])

# All instruction contain this discriminant in their mask so we can use
# it to partition the instructions.
# Bit 0x00100000 is another candidate bit we would need an exception
# for svc, b, bl
_INS_CLASSIFIER: int = 0xff << 20


def _OpcodeDiscriminant(data: int) -> int:
    return (data >> 20) & 0xff


def _NameForEnum(base_name: str, variant: str) -> str:
    name = base_name
    if variant:
        name += "_" + variant
    return name.replace(".", "_")


class Opcode:
    """The primary purpose of of instantiating an Opcode is to register it with
    the class variable `name_to_opcode`
    """
    name_to_opcode: Dict[str, "Opcode"] = {}

    # the key in this map is what you get when you "and" and opcode with
    # _INS_CLASSIFIER
    # For FindOpcode to work the more specific patterns must precede
    # the less specific ones
    ordered_opcodes: Dict[int, List['Opcode']] = collections.defaultdict(list)

    def __init__(self, name: str, variant: str,
                 bits: List[Tuple[int, int, int]],
                 fields: List[OK],
                 classes: OPC_FLAG, has_pred=True,
                 mem_width: MEM_WIDTH = MEM_WIDTH.NA,
                 sr_update: SR_UPDATE = SR_UPDATE.NONE):
        if _DEBUG:
            print(name)
        assert variant in _VARIANTS, f"bad variant [{variant}]"
        assert _RE_OPCODE_NAME.match(name)
        for f in fields:
            assert f in FIELD_DETAILS

        if has_pred:
            fields.insert(0, OK.PRED_28_31)
        assert len(fields) <= MAX_OPERANDS

        all_bits = bits[:]
        for f in fields:
            all_bits += [((1 << bitwidth) - 1, 0, pos)
                         for bitwidth, pos in FIELD_DETAILS[f].ranges]
        mask = Bits(*all_bits)[0]
        # make sure all 32bits are accounted for
        assert 0xffffffff == mask, "%08x" % mask

        self.name = _NameForEnum(name, variant)
        self.official_name = name
        assert self.name not in Opcode.name_to_opcode, f"duplicate {self.name}"
        Opcode.name_to_opcode[self.name] = self

        # Discriminant on fixed bits
        bit_mask, bit_value = Bits(*bits)
        if bit_mask & _INS_CLASSIFIER == _INS_CLASSIFIER:
            Opcode.ordered_opcodes[_OpcodeDiscriminant(bit_value)].append(self)
        else:
            b = _OpcodeDiscriminant(bit_value)
            m_inv = ~_OpcodeDiscriminant(bit_mask)
            # needs to go through all bit patterns for the bit sin m_inv
            dont_care = set((m_inv & x) for x in range(256))
            for dc in dont_care:
                Opcode.ordered_opcodes[b | dc].append(self)

        self.bit_mask = bit_mask
        self.bit_value = bit_value
        self.fields: List[OK] = fields
        self.classes: OPC_FLAG = classes
        self.sr_update = sr_update
        self.mem_width = mem_width

    def __lt__(self, other):
        return self.name < other.name

    def HasPred(self):
        return self.fields[0] == OK.PRED_28_31

    def AssembleOperandsRaw(self, operands: List[int]):
        assert len(operands) == len(
            self.fields), f"not enough operands for {self.name}"
        bits = [(self.bit_mask, self.bit_value, 0)]
        for f, o in zip(self.fields, operands):
            bits += InsertOperand(f, o)
        bit_mask, bit_value = Bits(*bits)
        assert bit_mask == 0xffffffff, f"{self.name} BAD MASK {bit_mask:08x}"
        return bit_value

    def DisassembleOperandsRaw(self, data: int) -> List[int]:
        assert data & self.bit_mask == self.bit_value
        return [ExtractOperand(f, data)
                for f in self.fields]

    @classmethod
    def FindOpcode(cls, data: int) -> Optional["Opcode"]:
        for opcode in Opcode.ordered_opcodes[_OpcodeDiscriminant(data)]:
            if data & opcode.bit_mask == opcode.bit_value:
                return opcode
        return None


def _CheckDiscriminantSeparability():
    """Make sure we completely understand the case where the
     bit_mask and bit_value are not uniquely specifying an opcode.
     In this case the more specific one pattern must precede the
     less specific.
     """
    for opcodes in Opcode.ordered_opcodes.values():
        for n, o1 in enumerate(opcodes):
            for o2 in opcodes[n + 1:]:
                m = o1.bit_mask & o2.bit_mask
                if o1.bit_value & m != o2.bit_value & m:
                    continue

                if OK.PRED_28_31 not in o1.fields and OK.PRED_28_31 in o2.fields:
                    assert o1.bit_value >> 28 == 0xf
                    continue

                if o1.name.startswith("uxt") and o2.name.startswith("uxta"):
                    assert OK.REG_16_19 in o2.fields
                    assert (o1.bit_value >> 16) & 0xf == 0xf
                    continue
                if o1.name.startswith("sxt") and o2.name.startswith("sxta"):
                    assert OK.REG_16_19 in o2.fields
                    assert (o1.bit_value >> 16) & 0xf == 0xf
                    continue

                if OPC_FLAG.MULTIPLE & o2.classes and OPC_FLAG.VFP & o2.classes and OPC_FLAG.VFP & o1.classes:
                    if (OPC_FLAG.LOAD & o2.classes and OPC_FLAG.LOAD & o1.classes or
                            OPC_FLAG.STORE & o2.classes and OPC_FLAG.STORE & o1.classes):
                        mask = (1 << 24) | (1 << 21)
                        assert o1.bit_mask & mask == mask, o1.name
                        assert ExtractBits(o1.bit_value, mask) == 2, o1.name
                        continue
                    if o1.name.startswith("vmov"):
                        mask = (1 << 24) | (1 << 23) | (1 << 21)
                        assert o1.bit_mask & mask == mask, o1.name
                        assert ExtractBits(o1.bit_value, mask) == 0, o1.name
                        continue
                print(f"potential conflict: [{o1.name}]  [{o2.name}]")
                assert False


########################################
root00 = (3, 0, 26)
########################################

for ext, sr_update, s_bit in [("", SR_UPDATE.NONE, (1, 0, 20)),
                              ("s", SR_UPDATE.NZ, (1, 1, 20))]:
    Opcode("mul" + ext, "",
           [root00, s_bit, (0xf, 0x0, 21), (1, 0, 25), (0xf, 0x0, 12), (0xf, 0x9, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.MUL, sr_update=sr_update)

    Opcode("mla" + ext, "",
           [root00, s_bit, (0xf, 0x1, 21), (1, 0, 25), (0xf, 0x9, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11, OK.REG_12_15],
           OPC_FLAG.MULACC, sr_update=sr_update)

    Opcode("umull" + ext, "",
           [root00, s_bit, (0xf, 0x4, 21), (1, 0, 25), (0xf, 0x9, 4)],
           [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.DST_0_1 | OPC_FLAG.MUL, sr_update=sr_update)

    Opcode("umlal" + ext, "",
           [root00, s_bit, (0xf, 0x5, 21), (1, 0, 25), (0xf, 0x9, 4)],
           [OK.REG_16_19, OK.REG_12_15, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.DST_0_1 | OPC_FLAG.MULACC, sr_update=sr_update)

    Opcode("smull" + ext, "",
           [root00, s_bit, (0xf, 0x6, 21), (1, 0, 25), (0xf, 0x9, 4)],
           [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.RESULT_64BIT | OPC_FLAG.SRC_DST_0_1 | OPC_FLAG.MUL, sr_update=sr_update)

    Opcode("smlal" + ext, "",
           [root00, s_bit, (0xf, 0x7, 21), (1, 0, 25), (0xf, 0x9, 4)],
           [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.DST_0_1 | OPC_FLAG.MULACC, sr_update=sr_update)

Opcode("mls", "",
       [root00, (0xf, 0x3, 21), (1, 0, 20), (1, 0, 25), (0xf, 0x9, 4)],
       [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11, OK.REG_12_15],
       OPC_FLAG.MULACC)

for ext, n in [("bb", 8), ("tb", 10), ("bt", 12), ("tt", 14)]:
    Opcode("smla" + ext, "",
           [root00, (0x3f, 0x10, 20), (0xf, n, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11, OK.REG_12_15],
           OPC_FLAG.MULACC)

    Opcode("smul" + ext, "",
           [root00, (0x3f, 0x16, 20), (0xf, 0, 12), (0xf, n, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
           OPC_FLAG.MUL)

Opcode("strex", "",
       # TODO: OK.REG_0_3 should move to the end
       [root00, (0x3f, 0x18, 20), (0xf, 0xf, 8), (0xf, 0x9, 4)],
       [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3],
       OPC_FLAG.ATOMIC | OPC_FLAG.STORE, mem_width=MEM_WIDTH.W4)

Opcode("ldrex", "",
       [root00, (0x3f, 0x19, 20), (0xf, 0xf, 8), (0xf, 0x9, 4),
        (0xf, 0xf, 0)],
       [OK.REG_12_15, OK.REG_16_19],
       OPC_FLAG.ATOMIC | OPC_FLAG.LOAD, mem_width=MEM_WIDTH.W4)

for addr_mode, addr_bits, flag in STANDARD_ADDR_MODES:
    for variant, bits, fields in [
        ("imm_" + addr_mode, [(1, 1, 22)] + addr_bits,
         [OK.REG_16_19, OK.IMM_0_3_8_11]),
        ("reg_" + addr_mode, [(1, 0, 22), (0xf, 0, 8)] + addr_bits,
         [OK.REG_16_19, OK.REG_0_3])]:
        for ext, width, n in [("h", MEM_WIDTH.W2, 0xb), ("sb", MEM_WIDTH.W1, 0xd),
                              ("sh", MEM_WIDTH.W2, 0xf)]:
            Opcode("ldr" + ext, variant,
                   bits + [root00, (1, 0, 25), (1, 1, 20), (0xf, n, 4)],
                   [OK.REG_12_15] + fields,
                   OPC_FLAG.LOAD | flag, mem_width=width)

        Opcode("strh", variant,
               bits + [root00, (1, 0, 25), (1, 0, 20), (0xf, 0xb, 4)],
               fields + [OK.REG_12_15],
               OPC_FLAG.STORE | flag, mem_width=MEM_WIDTH.W2)

        Opcode("ldrd", variant,
               bits + [root00, (1, 0, 25), (1, 0, 20), (0xf, 0xd, 4)],
               [OK.REG_PAIR_12_15] + fields,
               OPC_FLAG.LOAD | flag, mem_width=MEM_WIDTH.W8)

        Opcode("strd", variant,
               bits + [root00, (1, 0, 25), (1, 0, 20), (0xf, 0xf, 4)],
               fields + [OK.REG_PAIR_12_15],
               OPC_FLAG.STORE | flag, mem_width=MEM_WIDTH.W8)

for opcode, n in [("and", 0), ("eor", 1), ("sub", 2), ("rsb", 3),
                  ("add", 4), ("adc", 5), ("sbc", 6), ("rsc", 7),
                  ("orr", 12), ("bic", 14)]:
    for ext, sr_update, s_bit in [("", SR_UPDATE.NONE, (1, 0, 20)),
                                  ("s", SR_UPDATE.NCZ_PSR, (1, 1, 20))]:
        Opcode(opcode + ext, "regreg",
               [root00, s_bit, (0xf, n, 21), (1, 0, 25), (1, 0, 7), (1, 1, 4)],
               [OK.REG_12_15, OK.REG_16_19,
                OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.REG_8_11],
               OPC_FLAG.ALU, sr_update=sr_update)
        Opcode(opcode + ext, "regimm",
               [root00, s_bit, (0xf, n, 21), (1, 0, 25), (1, 0, 4)],
               [OK.REG_12_15, OK.REG_16_19,
                OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.IMM_7_11],
               OPC_FLAG.ALU, sr_update=sr_update)
        Opcode(opcode + ext, "imm",
               [root00, s_bit, (0xf, n, 21), (1, 1, 25)],
               [OK.REG_12_15, OK.REG_16_19, OK.IMM_0_7_8_11],
               OPC_FLAG.ALU, sr_update=sr_update)

for ext, width, n in [("", MEM_WIDTH.W4, 8), ("b", MEM_WIDTH.W1, 0xa)]:
    Opcode("swp" + ext, "",
           [root00, (0xf, n, 21), (1, 0, 25), (1, 0, 20), (0xf, 0x0, 8), (0xf, 0x9, 4)],
           [OK.REG_12_15, OK.REG_0_3, OK.REG_16_19],
           OPC_FLAG.ATOMIC, mem_width=width)

Opcode("bx", "",
       [root00, (0xf, 0x9, 21), (1, 0, 25), (1, 0, 20),
        (0xfff, 0xfff, 8), (0xf, 1, 4)],
       [OK.REG_0_3],
       OPC_FLAG.JUMP | OPC_FLAG.THUMB)

Opcode("blx", "reg",
       [root00, (0xf, 0x9, 21), (1, 0, 25), (1, 0, 20),
        (0xfff, 0xfff, 8), (0xf, 3, 4)],
       [OK.REG_0_3],
       OPC_FLAG.JUMP | OPC_FLAG.LINK | OPC_FLAG.THUMB)

Opcode("clz", "",
       [root00, (0xf, 0xb, 21), (1, 0, 25), (1, 0, 20),
        (0xf, 0xf, 8), (0xf, 0xf, 16), (0xf, 1, 4)],
       [OK.REG_12_15, OK.REG_0_3],
       OPC_FLAG.ALU1)

for opcode, n in [("tst", 8), ("teq", 9), ("cmp", 10), ("cmn", 11)]:
    Opcode(opcode, "regreg",
           [root00, (0xf, n, 21), (1, 1, 20), (0xf, 0, 12), (1, 0, 25),
            (1, 0, 7), (1, 1, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.REG_8_11],
           OPC_FLAG.TEST, sr_update=SR_UPDATE.NCZ)
    Opcode(opcode, "regimm",
           [root00, (0xf, n, 21), (1, 1, 20), (0xf, 0, 12),
            (1, 0, 25), (1, 0, 4)],
           [OK.REG_16_19, OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.IMM_7_11],
           OPC_FLAG.TEST, sr_update=SR_UPDATE.NCZ)
    Opcode(opcode, "imm",
           [root00, (0xf, n, 21), (1, 1, 20), (0xf, 0, 12), (1, 1, 25)],
           [OK.REG_16_19, OK.IMM_0_7_8_11],
           OPC_FLAG.TEST, sr_update=SR_UPDATE.NCZ)

for opcode, n in [("mov", 0xd), ("mvn", 0xf)]:
    for ext, sr_update, s_bit in [("", SR_UPDATE.NONE, (1, 0, 20)),
                                  ("s", SR_UPDATE.NCZ_PSR, (1, 1, 20))]:
        bits = [root00, s_bit, (0xf, n, 21), (0xf, 0, 16)]
        Opcode(opcode + ext, "regreg",
               bits + [(1, 0, 25), (1, 0, 7), (1, 1, 4)],
               [OK.REG_12_15, OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.REG_8_11],
               OPC_FLAG.ALU1, sr_update=sr_update)
        Opcode(opcode + ext, "regimm",
               bits + [(1, 0, 25), (1, 0, 4)],
               [OK.REG_12_15, OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.IMM_7_11],
               OPC_FLAG.ALU1, sr_update=sr_update)
        Opcode(opcode + ext, "imm",
               bits + [(1, 1, 25)],
               [OK.REG_12_15, OK.IMM_0_7_8_11],
               OPC_FLAG.ALU1, sr_update=sr_update)

Opcode("movw", "",
       [root00, (0x3f, 0x30, 20)],
       [OK.REG_12_15, OK.IMM_0_11_16_19],
       OPC_FLAG.ALU1)

Opcode("movt", "",
       [root00, (0x3f, 0x34, 20)],
       [OK.REG_12_15, OK.IMM_0_11_16_19],
       OPC_FLAG.ALU1)

########################################
root01 = (3, 1, 26)
########################################
Opcode("sdiv", "",
       [root01, (0x3f, 0x31, 20), (0xf, 0xf, 12), (0xf, 1, 4)],
       [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
       OPC_FLAG.DIV)

Opcode("udiv", "",
       [root01, (0x3f, 0x33, 20), (0xf, 0xf, 12), (0xf, 1, 4)],
       [OK.REG_16_19, OK.REG_0_3, OK.REG_8_11],
       OPC_FLAG.DIV)

for ext, n in [("b", 2), ("b16", 0), ("h", 3)]:
    # "uxt has  (0xf, 0xf, 16) while uxta has OK.REG_16_19,
    bits = [root01, (0x3f, 0x7, 4), (0x3, n, 20)]
    Opcode("uxt" + ext, "",
           bits + [(0xf, 0xb, 22), (0xf, 0xf, 16)],
           [OK.REG_12_15, OK.REG_0_3, OK.IMM_10_11_TIMES_8],
           OPC_FLAG.SIGNEXTEND)

    Opcode("sxt" + ext, "",
           bits + [(0xf, 0xa, 22), (0xf, 0xf, 16)],
           [OK.REG_12_15, OK.REG_0_3, OK.IMM_10_11_TIMES_8],
           OPC_FLAG.SIGNEXTEND)

    Opcode("uxta" + ext, "",
           bits + [(0xf, 0xb, 22)],
           [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3, OK.IMM_10_11_TIMES_8],
           OPC_FLAG.SIGNEXTEND)

    Opcode("sxta" + ext, "",
           bits + [(0xf, 0xa, 22)],
           [OK.REG_12_15, OK.REG_16_19, OK.REG_0_3, OK.IMM_10_11_TIMES_8],
           OPC_FLAG.SIGNEXTEND)

for ext, n in [("", 3), ("16", 11)]:
    Opcode("rev" + ext, "",
           [root01, (0x3ff, 0x2bf, 16), (0xf, 0xf, 8), (0xf, n, 4)],
           [OK.REG_12_15, OK.REG_0_3],
           OPC_FLAG.BYTEREORDER)
# prefetch must precede ldrb as it is similar

for addr_mode, addr_bits, flag in STANDARD_ADDR_MODES:
    for variant, bits, fields in [
        ("reg_" + addr_mode, [(1, 1, 25), (1, 0, 4)] + addr_bits,
         [OK.REG_16_19, OK.REG_0_3, OK.SHIFT_MODE_5_6, OK.IMM_7_11]),
        ("imm_" + addr_mode, [(1, 0, 25)] + addr_bits,
         [OK.REG_16_19, OK.IMM_0_11])]:
        Opcode("ldp", variant,
               bits + [root01, (1, 1, 22), (1, 1, 20), (0xf, 0xf, 12), (0xf, 0xf, 28)],
               fields,
               OPC_FLAG.PREFETCH | flag, has_pred=False)

        for ext, width, n in [("", MEM_WIDTH.W4, 0), ("b", MEM_WIDTH.W1, 1)]:
            Opcode("ldr" + ext, variant,
                   bits + [root01, (1, n, 22), (1, 1, 20)],
                   [OK.REG_12_15] + fields,
                   OPC_FLAG.LOAD | flag, mem_width=width)

            Opcode("str" + ext, variant,
                   bits + [root01, (1, n, 22), (1, 0, 20)],
                   fields + [OK.REG_12_15],
                   OPC_FLAG.STORE | flag, mem_width=width)

Opcode("ud2", "",
       [root01, (0x3ffffff, 0x3f000f0, 0)],
       [],
       OPC_FLAG.MISC)
########################################
root10 = (3, 2, 26)
########################################
# Opcode("blx",
#       [root10, (1, 1, 25), (0xf, 0xf, 28)],
#       [oSIMM_0_23_24],
#       [cJump, cLink, cThumb], has_pred=False)


for mode, update, addr_bits, flag in MULTI_ADDR_MODES:
    Opcode("stm" + mode, update,
           [root10, (1, 0, 25), (1, 0, 20), (1, 0, 22)] + addr_bits,
           [OK.REG_16_19, OK.REGLIST_0_15],
           OPC_FLAG.STORE | OPC_FLAG.MULTIPLE | flag)

    Opcode("ldm" + mode, update,
           [root10, (1, 0, 25), (1, 1, 20), (1, 0, 22)] + addr_bits,
           [OK.REGLIST_0_15, OK.REG_16_19],
           OPC_FLAG.LOAD | OPC_FLAG.MULTIPLE | flag)

Opcode("b", "",
       [root10, (1, 1, 25), (1, 0, 24)],
       [OK.SIMM_0_23],
       OPC_FLAG.JUMP)

Opcode("bl", "",
       [root10, (1, 1, 25), (1, 1, 24)],
       [OK.SIMM_0_23],
       OPC_FLAG.JUMP | OPC_FLAG.LINK)

########################################
root11 = (3, 3, 26)
########################################
Opcode("svc", "",
       [root11, (3, 3, 24)],
       [OK.IMM_0_23],
       OPC_FLAG.SYSCALL)

for addr_mode, addr_bits, flag in LIMITED_ADDR_MODES:
    Opcode("vldr", "f32_" + addr_mode,
           [root11, (0x3, 1, 24), (0x3, 1, 20), (0xf, 0xa, 8)] + addr_bits,
           [OK.SREG_12_15_22, OK.REG_16_19, OK.IMM_0_7_TIMES_4],
           OPC_FLAG.VFP | OPC_FLAG.LOAD | flag)

    Opcode("vldr", "f64_" + addr_mode,
           [root11, (0x3, 1, 24), (0x3, 1, 20), (0xf, 0xb, 8)] + addr_bits,
           [OK.DREG_12_15_22, OK.REG_16_19, OK.IMM_0_7_TIMES_4],
           OPC_FLAG.VFP | OPC_FLAG.LOAD | flag)

    Opcode("vstr", "f32_" + addr_mode,
           [root11, (0x3, 1, 24), (0x3, 0, 20), (0xf, 0xa, 8)] + addr_bits,
           [OK.REG_16_19, OK.IMM_0_7_TIMES_4, OK.SREG_12_15_22],
           OPC_FLAG.VFP | OPC_FLAG.STORE | flag)

    Opcode("vstr", "f64_" + addr_mode,
           [root11, (0x3, 1, 24), (0x3, 0, 20), (0xf, 0xb, 8)] + addr_bits,
           [OK.REG_16_19, OK.IMM_0_7_TIMES_4, OK.DREG_12_15_22],
           OPC_FLAG.VFP | OPC_FLAG.STORE | flag)

Opcode("vmov", "atof",
       [root11, (0x3f, 4, 20), (0xfd, 0xb1, 4)],
       [OK.DREG_0_3_5, OK.REG_12_15, OK.REG_16_19],
       OPC_FLAG.VFP)

Opcode("vmov", "ftoa",
       [root11, (0x3f, 5, 20), (0xfd, 0xb1, 4)],
       [OK.REG_12_15, OK.REG_16_19, OK.DREG_0_3_5],
       OPC_FLAG.VFP)

Opcode("vmov", "atos",
       [root11, (0x3f, 0x20, 20), (0xf, 0xa, 8), (0x7f, 0x10, 0)],
       [OK.SREG_16_19_7, OK.REG_12_15],
       OPC_FLAG.VFP)

Opcode("vmov", "stoa",
       [root11, (0x3f, 0x21, 20), (0xf, 0xa, 8), (0x7f, 0x10, 0)],
       [OK.REG_12_15, OK.SREG_16_19_7],
       OPC_FLAG.VFP)

VCVT_DST = {"f32": OK.SREG_12_15_22, "f64": OK.DREG_12_15_22,
            "s32": OK.SREG_12_15_22, "u32": OK.SREG_12_15_22}

VCVT_SRC = {"f32": OK.SREG_0_3_5, "f64": OK.DREG_0_3_5,
            "s32": OK.SREG_0_3_5, "u32": OK.SREG_0_3_5}

for dst, src, a, b in [("f32", "f64", 0x37, 0xbc),
                       ("f64", "f32", 0x37, 0xac),
                       ("s32", "f64", 0x3d, 0xbc),
                       ("s32", "f32", 0x3d, 0xac),
                       ("u32", "f64", 0x3c, 0xbc),
                       ("u32", "f32", 0x3c, 0xac),
                       ("f64", "s32", 0x38, 0xbc),
                       ("f32", "s32", 0x38, 0xac),
                       ("f64", "u32", 0x38, 0xb4),
                       ("f32", "u32", 0x38, 0xa4)]:
    Opcode("vcvt.%s.%s" % (dst, src), "",
           [root11, (7, 5, 23), (0x3f, a, 16), (0xfd, b, 4)],
           [VCVT_DST[dst], VCVT_SRC[src]],
           OPC_FLAG.VFP)

for name, a, c in [("vcmp", 5, 4), ("vcmpe", 5, 0xc)]:
    bits = [root11, (3, 3, 20), (7, a, 23), (0xd, c, 4)]
    Opcode(name + ".f32", "",
           bits + [(0xf, 4, 16), (0xf, 0xa, 8)],
           [OK.SREG_12_15_22, OK.SREG_0_3_5],
           OPC_FLAG.VFP)

    Opcode(name + ".f64", "",
           bits + [(0xf, 4, 16), (0xf, 0xb, 8)],
           [OK.DREG_12_15_22, OK.DREG_0_3_5],
           OPC_FLAG.VFP)

    Opcode(name + ".f32", "zero",
           bits + [(0xf, 5, 16), (0xf, 0xa, 8), (0x2f, 0, 0)],
           [OK.SREG_12_15_22, OK.IMM_FLT_ZERO],
           OPC_FLAG.VFP)

    Opcode(name + ".f64", "zero",
           bits + [(0xf, 5, 16), (0xf, 0xb, 8), (0x2f, 0, 0)],
           [OK.DREG_12_15_22, OK.IMM_FLT_ZERO],
           OPC_FLAG.VFP)

for name, a, b, c in [("vabs", 5, 0, 0xc),
                      ("vmov", 5, 0, 4),
                      ("vsqrt", 5, 1, 0xc),
                      ("vneg", 5, 1, 4)]:
    bits = [root11, (7, a, 23), (0xf, b, 16), (0xd, c, 4)]
    Opcode(name + ".f32", "",
           bits + [(3, 3, 20), (0xf, 0xa, 8)],
           [OK.SREG_12_15_22, OK.SREG_0_3_5],
           OPC_FLAG.VFP)
    Opcode(name + ".f64", "",
           bits + [(3, 3, 20), (0xf, 0xb, 8)],
           [OK.DREG_12_15_22, OK.DREG_0_3_5],
           OPC_FLAG.VFP)

for name, a, b, c in [("vdiv", 5, 0, 0),
                      ("vmul", 4, 2, 0),
                      ("vadd", 4, 3, 0),
                      ("vsub", 4, 3, 4)]:
    bits = [root11, (7, a, 23), (3, b, 20), (5, c, 4)]
    Opcode(name + ".f32", "",
           bits + [(0xf, 0xa, 8)],
           [OK.SREG_12_15_22, OK.SREG_16_19_7, OK.SREG_0_3_5],
           OPC_FLAG.VFP)
    Opcode(name + ".f64", "",
           bits + [(0xf, 0xb, 8)],
           [OK.DREG_12_15_22, OK.DREG_16_19_7, OK.DREG_0_3_5],
           OPC_FLAG.VFP)

for name, a, b, c in [("vnmul", 4, 2, 4),
                      ("vnmls", 4, 1, 0),
                      ("vnmla", 4, 1, 4),
                      ("vmls", 4, 0, 4),
                      ("vmla", 4, 0, 0)]:
    bits = [root11, (7, a, 23), (3, b, 20), (5, c, 4)]
    Opcode(name + ".f32", "",
           bits + [(0xf, 0xa, 8)],
           [OK.SREG_12_15_22, OK.SREG_16_19_7, OK.SREG_0_3_5],
           OPC_FLAG.VFP)
    Opcode(name + ".f64", "",
           bits + [(0xf, 0xb, 8)],
           [OK.DREG_12_15_22, OK.DREG_16_19_7, OK.DREG_0_3_5],
           OPC_FLAG.VFP)

for mode, update, addr_bits, flag in MULTI_ADDR_MODES:
    Opcode("vldm" + mode, "s_" + update if update else "s",
           [root11, (1, 0, 25), (1, 1, 20), (0xf, 0xa, 8)] + addr_bits,
           [OK.SREG_12_15_22, OK.REG_RANGE_0_7, OK.REG_16_19],
           OPC_FLAG.LOAD | OPC_FLAG.MULTIPLE | OPC_FLAG.VFP | flag)

    Opcode("vldm" + mode, "f_" + update if update else "f",
           [root11, (1, 0, 25), (1, 1, 20), (0xf, 0xb, 8), (1, 0, 0)] + addr_bits,
           [OK.DREG_12_15_22, OK.REG_RANGE_1_7, OK.REG_16_19],
           OPC_FLAG.LOAD | OPC_FLAG.MULTIPLE | OPC_FLAG.VFP | flag)

    Opcode("vstm" + mode, "s_" + update if update else "s",
           [root11, (1, 0, 25), (1, 0, 20), (0xf, 0xa, 8)] + addr_bits,
           [OK.REG_16_19, OK.SREG_12_15_22, OK.REG_RANGE_0_7],
           OPC_FLAG.STORE | OPC_FLAG.MULTIPLE | OPC_FLAG.VFP | flag)

    Opcode("vstm" + mode, "f_" + update if update else "f",
           [root11, (1, 0, 25), (1, 0, 20), (0xf, 0xb, 8), (1, 0, 0)] + addr_bits,
           [OK.REG_16_19, OK.DREG_12_15_22, OK.REG_RANGE_1_7],
           OPC_FLAG.STORE | OPC_FLAG.MULTIPLE | OPC_FLAG.VFP | flag)

Opcode("vmrs", "APSR_nzcv_fpscr",
       [root11, (0x3ffffff, 0x2f1fa10, 0)],
       [],
       OPC_FLAG.VFP, sr_update=SR_UPDATE.NCZV)

_CheckDiscriminantSeparability()


############################################################
#
############################################################
@dataclasses.dataclass
class Ins:
    """Arm flavor of an Instruction

    There can be at most one relocation associated with an Ins
    """
    opcode: Opcode
    operands: List[int] = dataclasses.field(default_factory=list)
    #
    # Note the addend is store in `operands[reloc_pos]
    reloc_symbol: str = ""
    # this is really of type elf_enum.RELOC_TYPE_ARM but it does not seem
    # worthy it to create a dependency on the Elf package for it
    reloc_kind: int = 0
    reloc_pos = 0
    is_local_sym = False


def Disassemble(data: int) -> Optional[Ins]:
    opcode = Opcode.FindOpcode(data)
    if opcode is None:
        return None
    ops = opcode.DisassembleOperandsRaw(data)
    if ops is None:
        return None

    return Ins(opcode, ops)


def Assemble(ins: Ins) -> int:
    assert ins.reloc_kind == 0, "reloc has not been resolved"
    return ins.opcode.AssembleOperandsRaw(ins.operands)


def Patch(data: int, opcode: Opcode, pos: int, value: int):
    """For relocation patching - note that the value is not run through the Encoder.
    But there will still be some range checking."""
    ops = opcode.DisassembleOperandsRaw(data)
    ops[pos] = value
    return opcode.AssembleOperandsRaw(ops)


############################################################
# code below is only used if this file is run as an executable
############################################################
def Query(opcode: str):
    count = 0
    for opc_list in Opcode.ordered_opcodes.values():
        for opc in opc_list:
            if opc.name != opcode:
                continue
            print(f"name={opc.name}")
            print(f"mask={opc.bit_mask:08x} value={opc.bit_value:08x}")
            print("fields with bit ranges:")
            for f in opc.fields:
                print("\t", f.name, FIELD_DETAILS[f])
                count += 1
            print()
    if count:
        print("bit range tuples have the form (modifier, bit-width, start-pos)")


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
    print(f"constexpr const unsigned MAX_OPERANDS = {MAX_OPERANDS};", file=fout)
    print(f"constexpr const unsigned MAX_BIT_RANGES = {MAX_BIT_RANGES};", file=fout)
    cgen.RenderEnum(cgen.NameValues(FK), "class FK : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(OK), "class OK : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(SR_UPDATE), "class SR_UPDATE : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(MEM_WIDTH), "class MEM_WIDTH : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(OPC_FLAG), "OPC_FLAG", fout)
    cgen.RenderEnum(cgen.NameValues(PRED), "class PRED : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(REG), "class REG : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(SREG), "class SREG : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(DREG), "class DREG : uint8_t", fout)
    cgen.RenderEnum(cgen.NameValues(SHIFT), "class SHIFT : uint8_t", fout)
    opcodes = list(sorted(Opcode.name_to_opcode.keys()))
    # note we sneak in an invalid first entry
    _render_enum_simple(["invalid"] + opcodes, "enum class OPC : uint16_t")


def _RenderOpcodeTable() -> List[str]:
    """Note: we sneak in an invalid first entry"""
    out = [
        '{"invalid", "invalid", 0, 0, 0, {}, 0, MEM_WIDTH::NA, SR_UPDATE::NONE},'
    ]
    for name, opc in sorted(Opcode.name_to_opcode.items()):
        flags = " | ".join([f.name for f in OPC_FLAG if opc.classes & f])
        assert len(opc.fields) <= MAX_OPERANDS
        fields = "{" + ", ".join(["OK::" + f.name for f in opc.fields]) + "}"
        out += [
            "{" +
            f'"{opc.official_name}", "{name}", 0x{opc.bit_mask:08x}, 0x{opc.bit_value:08x},',
            f' {len(opc.fields)}, {fields},',
            f' {flags}, MEM_WIDTH::{opc.mem_width.name}, SR_UPDATE::{opc.sr_update.name}',
            '},']
    return out


def _RenderClusteredOpcodeTable() -> List[str]:
    out = []
    for i in range(256):
        cluster = Opcode.ordered_opcodes[i]
        out += [f"  // cluster {i}  size:{len(cluster)}"]
        if cluster:
            enums = [f"OPC::{opc.name}" for opc in cluster]
            out += ["  " + ", ".join(enums)]
    return out


def _RenderOpcodeTableJumper() -> List[str]:
    out = []
    current_offset = 0  # compensate for invalid first entry
    for i in range(256):
        cluster = Opcode.ordered_opcodes[i]
        out.append(f"{current_offset}")
        current_offset += len(cluster)
    out.append(f"{current_offset}")
    return out


def _RenderFieldInfoTable():
    out = []
    for n, ok in enumerate(OK):
        assert n == ok.value
        fd = FIELD_DETAILS[ok]
        ranges = ', '.join(["{%d, %d}" % (a, b) for a, b in fd.ranges])
        names = f"{fd.enum_class.__name__}_ToStringMap" if fd.enum_class else "nullptr"
        decoder = fd.decoder.__name__ if fd.decoder else 'nullptr'
        encoder = fd.encoder.__name__ if fd.encoder else 'nullptr'

        out += ['  {  // %s = %d' % (ok.name, ok.value)]
        out += ['    {%s}, %s, "%s",' % (ranges, names, fd.prefix)]
        out += ['    %s, %s, %d, FK::%s, %d, %d},' %
                (decoder, encoder, fd.bitwidth, fd.kind.name, fd.scale, len(fd.names))]
    return out


_MNEMONIC_HASH_TABLE_SIZE = 512


def _RenderMnemonicHashLookup():
    table = ["invalid"] * _MNEMONIC_HASH_TABLE_SIZE
    for name, opc in Opcode.name_to_opcode.items():
        h = hash_djb2(name)
        for d in range(64):
            hh = (h + d) % _MNEMONIC_HASH_TABLE_SIZE
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

    print("const OPC ClusteredOpcodeTable[] = {", file=fout)
    print(",\n".join(_RenderClusteredOpcodeTable()), file=fout)
    print("};\n", file=fout)

    print("const int16_t OpcodeTableJumper[] = {", file=fout)
    print(",\n".join(_RenderOpcodeTableJumper()), file=fout)
    print("};\n", file=fout)



    print(f"constexpr const unsigned MNEMONIC_HASH_TABLE_SIZE = {_MNEMONIC_HASH_TABLE_SIZE};", file=fout)

    print("// Indexed by djb2 hash of mnemonic. Collisions are resolved via linear probing",
          file=fout)
    print(f"static const OPC MnemonicHashTable[MNEMONIC_HASH_TABLE_SIZE] = {{", file=fout)
    print("\n".join(_RenderMnemonicHashLookup()), file=fout)
    print("};\n", file=fout)

    cgen.RenderEnumToStringMap(cgen.NameValues(REG), "REG", fout)
    cgen.RenderEnumToStringFun("REG", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(DREG), "DREG", fout)
    cgen.RenderEnumToStringFun("DREG", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(SREG), "SREG", fout)
    cgen.RenderEnumToStringFun("SREG", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(PRED), "PRED", fout)
    cgen.RenderEnumToStringFun("PRED", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(SHIFT), "SHIFT", fout)
    cgen.RenderEnumToStringFun("SHIFT", fout)
    cgen.RenderEnumToStringMap(cgen.NameValues(OK), "OK", fout)
    cgen.RenderEnumToStringFun("OK", fout)

    # Note this also uses the string tables from the enums above
    print("// Indexed by OK", file=fout)
    print("const FieldInfo FieldInfoTable[] = {", file=fout)
    print("\n".join(_RenderFieldInfoTable()), file=fout)
    print("};\n", file=fout)


def _OpcodeDiscriminantExperiments():
    """Some failed experiments for making the disassembler even faster"""
    print("opcode distribution")
    for k, cluster in Opcode.ordered_opcodes.items():
        submask = ~0
        for x in cluster:
            submask &= x.bit_mask
        print(f"{k:08x} {len(cluster):3}  {submask:08x}")
    print("OK")


def _MnemonicHashingExperiments():
    # experiment for near perfect hashing
    buckets = [[] for _ in range(_MNEMONIC_HASH_TABLE_SIZE)]
    table = [""] * _MNEMONIC_HASH_TABLE_SIZE
    distance = [0] * 128
    for opc in Opcode.name_to_opcode.values():
        s = opc.name
        h = hash_djb2(s)
        print(f"{s}: {h:x}")
        buckets[h % _MNEMONIC_HASH_TABLE_SIZE].append(s)
        for d in range(len(distance)):
            hh = (h + d) % _MNEMONIC_HASH_TABLE_SIZE
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
        for name, opcode in sorted(Opcode.name_to_opcode.items()):
            fields = [ok.name for ok in opcode.fields]
            print(f"{name:20} {' '.join(fields)}")
        sys.exit(1)
    if sys.argv[1] == "discriminant":
        _OpcodeDiscriminantExperiments()
    elif sys.argv[1] == "hash":
        _MnemonicHashingExperiments()
    elif sys.argv[1] == "gen_c":
        cgen.ReplaceContent(_EmitCodeC, sys.stdin, sys.stdout)
    elif sys.argv[1] == "gen_h":
        cgen.ReplaceContent(_EmitCodeH, sys.stdin, sys.stdout)
    else:
        Query(sys.argv[1])
