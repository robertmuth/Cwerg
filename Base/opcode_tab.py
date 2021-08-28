#!/usr/bin/python3
# (c) Robert Muth - see LICENSE for more info

from typing import List, Dict

import enum
from Util import cgen

# maximum number of operands in an instruction
MAX_OPERANDS = 5
# maximum number of function parameters (or results)
MAX_PARAMETERS = 64


############################################################
# Opcode Families [OF.]
#
# Each Opcode belongs to one of the families below.
# Within each family the order and kind of the operands is similar
############################################################
@enum.unique
class OPC_KIND(enum.Enum):
    INVALID = 0
    ALU = 1
    ALU1 = 2
    MOV = 3
    LEA = 4
    LEA1 = 5

    COND_BRA = 6
    BRA = 7
    BSR = 8
    JSR = 9
    SWITCH = 10
    RET = 11
    SYSCALL = 12

    ST = 13
    LD = 14

    PUSHARG = 15
    POPARG = 16

    NOP = 17
    NOP1 = 18

    CONV = 19
    CMP = 20

    BCOPY = 21
    BZERO = 22

    DIRECTIVE = 23  # not a real instruction


_OF_TO_PURPOSE = {
    OPC_KIND.ALU: ["dst", "src1", "src2"],
    OPC_KIND.ALU1: ["dst", "src"],
    OPC_KIND.COND_BRA: ["op1", "op2", "target_bbl"],
    OPC_KIND.SWITCH: ["index", "table"],
    OPC_KIND.BRA: ["target_bbl"],
    OPC_KIND.RET: [],
    OPC_KIND.BSR: ["target_fun"],
    OPC_KIND.JSR: ["target_fun_addr", "target_fun_sig"],
    OPC_KIND.SYSCALL: ["target_fun_sig", "syscall_no"],
    OPC_KIND.LEA: ["dst", "base", "offset"],
    OPC_KIND.LEA1: ["dst", "base"],
    OPC_KIND.LD: ["dst", "base", "offset"],
    OPC_KIND.ST: ["base", "offset", "src"],
    OPC_KIND.NOP: [],
    OPC_KIND.NOP1: ["src_and_dst"],
    OPC_KIND.BZERO: ["dst_addr", "width"],
    OPC_KIND.BCOPY: ["dst_addr", "src_addr", "width"],
    OPC_KIND.POPARG: ["dst"],
    OPC_KIND.PUSHARG: ["src"],
    OPC_KIND.CONV: ["dst", "src"],
    OPC_KIND.MOV: ["dst", "src"],
    OPC_KIND.CMP: ["dst", "src1", "src2", "cmp1", "cmp2"],
}

_OFS_CFG = {OPC_KIND.BSR, OPC_KIND.JSR, OPC_KIND.SYSCALL, OPC_KIND.SWITCH,
            OPC_KIND.BRA, OPC_KIND.COND_BRA, OPC_KIND.RET}

# These instructions do not have a written register
_OFS_NO_DEF = _OFS_CFG | {OPC_KIND.ST, OPC_KIND.BCOPY, OPC_KIND.BZERO,
                          OPC_KIND.PUSHARG, OPC_KIND.NOP}

# These instructions have a written register
_OFS_WRITING_REGS = {
    OPC_KIND.LEA, OPC_KIND.LEA1, OPC_KIND.ALU, OPC_KIND.ALU1, OPC_KIND.CMP,
    OPC_KIND.MOV, OPC_KIND.CONV, OPC_KIND.LD,
    OPC_KIND.POPARG, OPC_KIND.NOP1}


@enum.unique
class OA(enum.Flag):
    """Opcode Attributes"""
    BBL_TERMINATOR = 1 << 0
    NO_FALL_THROUGH = 1 << 1
    CALL = 1 << 2
    COMMUTATIVE = 1 << 3
    MEM_RD = 1 << 4
    MEM_WR = 1 << 5
    SPECIAL = 1 << 6


OAS_CFG = OA.CALL | OA.BBL_TERMINATOR
OAS_SIDE_EFFECT = OA.CALL | OA.BBL_TERMINATOR | OA.MEM_RD | OA.MEM_WR | OA.SPECIAL


############################################################
# Operand Kinds [OK.]
#
# Each instruction operates on a list of operands. Since we mimic a
# three address machine, ALU instructions usually have 3 operands,
# the destination being the first one.
# There is a large variety of operands denoting registers or immediates
# which enable some basic typing on a per operand basis.
# Additional typing constraints across the operands are enforced by "rules".
############################################################
@enum.unique
class OP_KIND(enum.Enum):
    INVALID = 0
    REG = 1
    CONST = 2
    REG_OR_CONST = 3

    # bbl immediates ref to a bbl in the current function
    # Note: bbls can be referred to before they are defined
    BBL = 4
    # mem immediates refer to a global memory or stack region
    MEM = 5
    # stk immediates refer to a stack region in the current function
    STK = 6

    # fun immediates ref to a function in global function table
    # Note: funs can be referred to before they are defined
    FUN = 7

    JTB = 8

    TYPE_LIST = 20

    DATA_KIND = 21  # one of the RK_
    MEM_KIND = 23  # one of the MK_
    FUN_KIND = 24  # one of the FK_

    FIELD = 25

    NAME = 26
    NAME_LIST = 27
    VALUE = 28
    BBL_TAB = 29
    BYTES = 30


############################################################
# Type Constraints
############################################################
@enum.unique
class TC(enum.Enum):
    INVALID = 0
    ANY = 1
    ADDR_NUM = 2
    ADDR_INT = 3
    NUM = 4
    FLT = 5
    INT = 6
    ADDR = 7
    CODE = 8
    UINT = 9
    SINT = 10
    OFFSET = 11
    #
    SAME_AS_PREV = 20
    # for bitcast
    SAME_SIZE_AS_PREV = 22


############################################################
# DataType Flavors
############################################################

DK_FLAVOR_S = 0x20  # signed int
DK_FLAVOR_U = 0x40  # unsigned int
DK_FLAVOR_F = 0x60  # ieee floating point
DK_FLAVOR_A = 0x80  # data address
DK_FLAVOR_C = 0xa0  # code address

_DK_WIDTH_8 = 0
_DK_WIDTH_16 = 1
_DK_WIDTH_32 = 2
_DK_WIDTH_64 = 3
_DK_WIDTH_128 = 4


class DK(enum.Enum):
    """Data Kind - primarily used to associate a type with Const and Reg"""

    INVALID = 0

    # signed
    S8 = DK_FLAVOR_S + _DK_WIDTH_8
    S16 = DK_FLAVOR_S + _DK_WIDTH_16
    S32 = DK_FLAVOR_S + _DK_WIDTH_32
    S64 = DK_FLAVOR_S + _DK_WIDTH_64
    # S128 = _RK_S + _RK_128
    # unsigned
    U8 = DK_FLAVOR_U + _DK_WIDTH_8
    U16 = DK_FLAVOR_U + _DK_WIDTH_16
    U32 = DK_FLAVOR_U + _DK_WIDTH_32
    U64 = DK_FLAVOR_U + _DK_WIDTH_64
    # U128 = _RK_U + _RK_128
    # float
    F8 = DK_FLAVOR_F + _DK_WIDTH_8
    F16 = DK_FLAVOR_F + _DK_WIDTH_16
    F32 = DK_FLAVOR_F + _DK_WIDTH_32
    F64 = DK_FLAVOR_F + _DK_WIDTH_64
    # F128 = _RK_F + _RK_128
    # data address
    A32 = DK_FLAVOR_A + _DK_WIDTH_32
    A64 = DK_FLAVOR_A + _DK_WIDTH_64
    # code address
    C32 = DK_FLAVOR_C + _DK_WIDTH_32
    C64 = DK_FLAVOR_C + _DK_WIDTH_64

    def flavor(self) -> int:
        return self.value & 0xe0

    def bitwidth(self) -> int:
        return 8 << (self.value & 0x7)


SHORT_STR_TO_RK = {x.name: x for x in DK}  # this does contain the aliases


def RegIsAddrInt(rk: DK):
    return (DK.A32.value <= rk.value <= DK.A64.value or
            DK.S8.value <= rk.value <= DK.U64.value)


def RegIsInt(rk: DK):
    return DK.S8.value <= rk.value <= DK.U64.value


TC_TO_CHECKER = {
    TC.ANY: lambda x: True,
    TC.ADDR_NUM: lambda x: x.flavor() != DK_FLAVOR_C,
    TC.NUM: lambda x: x.flavor() in {DK_FLAVOR_U, DK_FLAVOR_S, DK_FLAVOR_F},
    TC.INT: lambda x: x.flavor() in {DK_FLAVOR_U, DK_FLAVOR_S},
    TC.ADDR: lambda x: x.flavor() == DK_FLAVOR_A,
    TC.CODE: lambda x: x.flavor() == DK_FLAVOR_C,
    TC.SINT: lambda x: x.flavor() == DK_FLAVOR_S,
    TC.UINT: lambda x: x.flavor() == DK_FLAVOR_U,
    TC.ADDR_INT: RegIsAddrInt,
    TC.FLT: lambda x: x.flavor() == DK_FLAVOR_F,
    TC.OFFSET: lambda x: x.flavor() in {DK_FLAVOR_U, DK_FLAVOR_S},
    # maybe change this to just U or S
}


def CheckTypeConstraint(last_type: DK, constraint: TC, this_type: DK) -> bool:
    checker = TC_TO_CHECKER.get(constraint)
    if checker:
        return checker(this_type)
    if constraint == TC.SAME_AS_PREV:
        return last_type == this_type
    elif constraint == TC.SAME_SIZE_AS_PREV:
        return last_type.bitwidth() == this_type.bitwidth()
    else:
        assert False, f"unknown contraint {constraint.name}"


@enum.unique
class MEM_KIND(enum.Enum):
    """Represents Allocation Type of Global Memory """
    INVALID = 0
    RO = 1
    RW = 2
    TLS = 3
    FIX = 4  # a fixed address provide via
    EXTERN = 5  # forward declaration must be defined before code emission
    BUILTIN = 6  # linker defined


SHORT_STR_TO_MK = {x.name: x for x in MEM_KIND}


@enum.unique
class FUN_KIND(enum.Enum):
    """Function Kinds"""
    INVALID = 0
    BUILTIN = 1  # linker defined
    EXTERN = 2  # forward declaration must be defined before code emission
    NORMAL = 3
    SIGNATURE = 4


SHORT_STR_TO_FK = {x.name: x for x in FUN_KIND}

############################################################
# Operand Value Kind Sets
############################################################

OKS_LIST = {OP_KIND.BYTES, OP_KIND.NAME_LIST, OP_KIND.BBL_TAB,
            OP_KIND.TYPE_LIST}

OKS_ALLOWED_FOR_INSTRUCTIONS = {OP_KIND.REG, OP_KIND.CONST,
                                OP_KIND.REG_OR_CONST,
                                OP_KIND.FUN, OP_KIND.BBL, OP_KIND.JTB,
                                OP_KIND.MEM, OP_KIND.STK, OP_KIND.FIELD}

# we do not want non-scalar operands in instructions as they
# increase memory usage and complicate the code
assert not (OKS_LIST & OKS_ALLOWED_FOR_INSTRUCTIONS)

OKS_ALLOWED_FOR_DIRECTIVES = {OP_KIND.CONST,
                              OP_KIND.VALUE, OP_KIND.MEM_KIND, OP_KIND.BYTES,
                              OP_KIND.NAME, OP_KIND.BBL_TAB,
                              OP_KIND.FUN_KIND, OP_KIND.TYPE_LIST,
                              OP_KIND.NAME_LIST, OP_KIND.DATA_KIND, OP_KIND.FUN,
                              OP_KIND.MEM, OP_KIND.BBL
                              }

OKS_ALL = OKS_ALLOWED_FOR_INSTRUCTIONS | OKS_ALLOWED_FOR_DIRECTIVES


############################################################
# Opcode Groups
############################################################
@enum.unique
class OPC_GENUS(enum.Enum):
    INVALID = 0
    BASE = 1
    MISC = 2
    STRUCT = 3
    TBD = 4


_DIR_TO_PURPOSE = {
    ".mem": ["name", "alignment", "mem_kind"],
    ".data": ["repeat", "data"],
    ".addr.fun": ["width", "fun"],
    ".addr.mem": ["width", "mem", "offset"],
    ".fun": ["name", "fun_kind", "out_params", "in_params"],
    ".bbl": ["name"],
    ".reg": ["reg_kind", "names"],
    ".stk": ["name", "alignment", "size"],
    ".jtb": ["name", "size", "default_bbl", "map"],
    ".struct": ["name"],
    ".field": ["name", "alignment", "size"],
    ".endstruct": [],
    ".stk.s": ["name", "name"],
}


############################################################
# Opcode
############################################################
class Opcode:
    """Opcodes are templates for instructions similar to what you would
    find in assembly language manual for a processor.

    Note, the main purpose of instantiating an opcode instance is to
    populate the Table/TableByNo class member
    """
    Table: Dict[str, "Opcode"] = {}
    TableByNo: Dict[int, "Opcode"] = {}

    def __init__(self, no, name: str, kind: OPC_KIND,
                 operand_kinds: List[OP_KIND],
                 constraints: List[TC], group: OPC_GENUS, desc,
                 attributes=OA(0)):
        assert name not in Opcode.Table, f"duplicate opcode {name}"
        assert len(operand_kinds) <= MAX_OPERANDS, name
        Opcode.Table[name] = self
        assert no not in Opcode.TableByNo, f"duplicate no: {no} {name}"
        Opcode.TableByNo[no] = self
        self.no = no
        self.name = name
        self.kind: OPC_KIND = kind
        self.operand_kinds: List[OP_KIND] = operand_kinds
        self.constraints: List[TC] = constraints
        self.group = group
        self.desc = desc
        self.attributes = attributes

        assert kind != OPC_KIND.INVALID, f"unknown {kind}"
        is_directive = kind == OPC_KIND.DIRECTIVE
        if is_directive:
            assert name.startswith(".")
            self.purpose = _DIR_TO_PURPOSE[name]
        else:
            self.purpose = _OF_TO_PURPOSE[kind]
        assert len(self.purpose) == len(
            operand_kinds), f"{name} {operand_kinds}"

        assert len(operand_kinds) == len(constraints), f"{no} {name}"
        for ok, tc in zip(operand_kinds, constraints):
            # self.operands_tab[o] = op
            assert ok in OKS_ALL, f"unexpected operand: {ok}"
            if ok in {OP_KIND.REG, OP_KIND.CONST, OP_KIND.REG_OR_CONST}:
                assert tc != TC.INVALID, f"{no} {name}"
            else:
                assert tc == TC.INVALID, f"{no} {name}"
            if is_directive:
                assert ok in OKS_ALLOWED_FOR_DIRECTIVES, f"bad ins op [{ok}]"
            else:
                assert ok in OKS_ALLOWED_FOR_INSTRUCTIONS, f"bad ins op [{ok}]"

    def is_call(self):
        return OA.CALL in self.attributes

    def is_bbl_terminator(self):
        return OA.BBL_TERMINATOR in self.attributes

    def has_fallthrough(self):
        return OA.NO_FALL_THROUGH not in self.attributes

    def has_side_effect(self):
        return OAS_SIDE_EFFECT & self.attributes

    def def_ops_count(self):
        """How many of the leading operands write are register writes"""
        if self.kind in {OPC_KIND.INVALID,
                         OPC_KIND.DIRECTIVE} or self.kind in _OFS_NO_DEF:
            return 0
        else:
            return 1

    @classmethod
    def Lookup(cls, name: str) -> "Opcode":
        return cls.Table[name]

    def __str__(self):
        return f"[OPCODE: {self.name}]"


############################################################
# ARITHMETIC ALU 0x10
# FLOAT + INT

# note: limited address arithmetic allowed
ADD = Opcode(0x10, "add", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.NUM, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Addition: dst := src1 + src2",
             OA.COMMUTATIVE)

# note: limited address arithmetic allowed
SUB = Opcode(0x11, "sub", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.NUM, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Subtraction: dst := src1 - src2")

# needs more work  wrt to size
MUL = Opcode(0x12, "mul", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.NUM, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Multiplication: dst := src1 \\* src2",
             OA.COMMUTATIVE)

DIV = Opcode(0x13, "div", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.NUM, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             """Division: dst := src1 / src2 
             
             Some day the operation might be more strictly defined as: 
             
             dst := 0 if src2 == 0 else src1 / src2""")

# cf.:
# https://www.gingerbill.org/article/2020/01/25/a-reply-to-lets-stop-copying-c/
REM = Opcode(0x14, "rem", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             """Modulo: dst := a % b
              
              Some day the sign of the result might be more strictly defined.
              Note: does not apply to floating point numbers""")

############################################################
# LOGIC ALU 0x30
# INT ONLY (all regs are treated as unsigned except for shr/rshr
XOR = Opcode(0x18, "xor", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Bitwise exclusive or: dst := src1 ^ src2",
             OA.COMMUTATIVE)

# note: limited address arithmetic allowed
AND = Opcode(0x19, "and", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Bitwise and: dst := src1 & src2",
             OA.COMMUTATIVE)

# note: limited address arithmetic allowed
OR = Opcode(0x1a, "or", OPC_KIND.ALU,
            [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
            [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
            "Bitwise or: dst := src1 | src2",
            OA.COMMUTATIVE)

# shift amount is determined as follows:
# use the log2(width(dst)) low order bits of src2
# e.g. for a dst of kind s8 the low order 3 bits of
# src2 will be used.
# src2 is treated as an unsigned register
SHL = Opcode(0x1b, "shl", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             """Shift left: dst := src1 << src2
              
              Some day the operation might more strictly defined as:
             
             dst: = src1 << (src2 mod bitwidth(src2))""")

SHR = Opcode(0x1c, "shr", OPC_KIND.ALU,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             """Shift right: dst := src1 >> src2
             
             Some day the operation might more strictly defined as:
             
             dst: = src1 >> (src2 mod bitwidth(src2))""")

CNTLZ = Opcode(0x1d, "cntlz", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
               [TC.INT, TC.SAME_AS_PREV], OPC_GENUS.BASE,
               "Count leading zeros.")

CNTTZ = Opcode(0x1e, "cnttz", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
               [TC.INT, TC.SAME_AS_PREV], OPC_GENUS.BASE,
               "Count trailing zeros.")

# do we need both directions, do we need a reverse version?
# should we rather use a funnel shift?
# ROTL = Opcode(0x1d, "rotl", OPC_KIND.ALU,
#               [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
#               [TC.INT, TC.SAME_AS_PREV, TC.SAME_AS_PREV], OPC_GENUS.TBD,
#               "Rotation Left")

############################################################
# CONDITIONAL BRANCHES 0x20
# do we need unordered variants for floating point?

# not beq/bne is the only operation for c_regs
BEQ = Opcode(0x20, "beq", OPC_KIND.COND_BRA,
             [OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST, OP_KIND.BBL],
             [TC.ANY, TC.SAME_AS_PREV, TC.INVALID], OPC_GENUS.BASE,
             "Conditional branch if equal.",
             OA.COMMUTATIVE | OA.BBL_TERMINATOR)

BNE = Opcode(0x21, "bne", OPC_KIND.COND_BRA,
             [OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST, OP_KIND.BBL],
             [TC.ANY, TC.SAME_AS_PREV, TC.INVALID], OPC_GENUS.BASE,
             "Conditional branch if not equal.",
             OA.COMMUTATIVE | OA.BBL_TERMINATOR)

BLT = Opcode(0x22, "blt", OPC_KIND.COND_BRA,
             [OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST, OP_KIND.BBL],
             [TC.ADDR_NUM, TC.SAME_AS_PREV, TC.INVALID], OPC_GENUS.BASE,
             "Conditional branch if greater than.",
             OA.BBL_TERMINATOR)

BLE = Opcode(0x23, "ble", OPC_KIND.COND_BRA,
             [OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST, OP_KIND.BBL],
             [TC.ADDR_NUM, TC.SAME_AS_PREV, TC.INVALID], OPC_GENUS.BASE,
             "Conditional branch if less or equal.",
             OA.BBL_TERMINATOR)

############################################################
# More Control Flow 0x28

SWITCH = Opcode(0x28, "switch", OPC_KIND.SWITCH, [OP_KIND.REG, OP_KIND.JTB],
                [TC.UINT, TC.INVALID], OPC_GENUS.BASE,
                """Multi target computed jump. 
                
                The register argument must be less than the jtb `size`.
                
                The jtb symbol must have been previously defined with the `.jtb` directive.
                """,
                OA.BBL_TERMINATOR | OA.NO_FALL_THROUGH)
BRA = Opcode(0x29, "bra", OPC_KIND.BRA, [OP_KIND.BBL],
             [TC.INVALID], OPC_GENUS.BASE,
             "Unconditional branch.",
             OA.BBL_TERMINATOR | OA.NO_FALL_THROUGH)
RET = Opcode(0x2a, "ret", OPC_KIND.RET, [],
             [], OPC_GENUS.BASE,
             "Return from subroutine.",
             OA.BBL_TERMINATOR | OA.NO_FALL_THROUGH)
BSR = Opcode(0x2b, "bsr", OPC_KIND.BSR, [OP_KIND.FUN],
             [TC.INVALID], OPC_GENUS.BASE,
             "Branch to subroutine fun",
             OA.CALL)
JSR = Opcode(0x2c, "jsr", OPC_KIND.JSR, [OP_KIND.REG, OP_KIND.FUN],
             [TC.CODE, TC.INVALID], OPC_GENUS.BASE,
             "Jump indirectly to subroutine through register (fun describes the signature). "
             "The signature must have been previously defined with the `.fun` directive.",
             OA.CALL)

SYSCALL = Opcode(0x2d, "syscall", OPC_KIND.SYSCALL,
                 [OP_KIND.FUN, OP_KIND.CONST],
                 [TC.INVALID, TC.UINT], OPC_GENUS.BASE,
                 "Syscall to `syscall_no`. (fun describes the signature). "
                 "The signature must have been previously defined with the `.fun` directive.",
                 OA.CALL)

TRAP = Opcode(0x2e, "trap", OPC_KIND.RET, [],
              [], OPC_GENUS.BASE,
              "Abort program.",
              OA.BBL_TERMINATOR | OA.NO_FALL_THROUGH)

############################################################
# Misc 0x30

PUSHARG = Opcode(0x30, "pusharg", OPC_KIND.PUSHARG, [OP_KIND.REG_OR_CONST],
                 [TC.ANY], OPC_GENUS.BASE,
                 "push call or return arg - must immediately precede bsr/jsr or ret",
                 OA.SPECIAL)

POPARG = Opcode(0x31, "poparg", OPC_KIND.POPARG, [OP_KIND.REG],
                [TC.ANY], OPC_GENUS.BASE,
                "pop call or return arg - must immediately follow fun entry or bsr/jsr",
                OA.SPECIAL)

CONV = Opcode(0x32, "conv", OPC_KIND.CONV, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
              [TC.NUM, TC.NUM], OPC_GENUS.BASE,
              # TODO: specify rounding and overflow for float <-> int conversions
              "Conversion of numerical regs which do not have to be of same size. "
              "Bits may change. Note: Use mov if both regs have the same kind. "
              "Note: This is not completely stable/well-defined yet for case that involve "
              "a widening change from signed -> unsigned.")

BITCAST = Opcode(0x33, "bitcast", OPC_KIND.CONV,
                 [OP_KIND.REG, OP_KIND.REG_OR_CONST],
                 [TC.ANY, TC.SAME_SIZE_AS_PREV], OPC_GENUS.BASE,
                 "Cast between regs of same size. "
                 "Bits will be re-interpreted but do not change. This can be used to "
                 "manipulated addresses im unusual ways.")

MOV = Opcode(0x34, "mov", OPC_KIND.MOV, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
             [TC.ANY, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Move between registers. While a mov can be emulated via a `zero add`, "
             "having a dedicated instruction make some optimizations easier to "
             "implement when combined with a canonicalization.")

CMPEQ = Opcode(0x35, "cmpeq", OPC_KIND.CMP,
               [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST,
                OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
               [TC.ANY, TC.SAME_AS_PREV, TC.SAME_AS_PREV, TC.ANY,
                TC.SAME_AS_PREV],
               OPC_GENUS.BASE,
               "Conditional move (compare equal). dst := (cmp1 == cmp2) ? src1 : src2 "
               "\nNote: dst/cmp1/cmp2 may be of a different type than src1/src2.",
               OA.COMMUTATIVE)

CMPLT = Opcode(0x36, "cmplt", OPC_KIND.CMP,
               [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST,
                OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
               [TC.ANY, TC.SAME_AS_PREV, TC.SAME_AS_PREV, TC.ADDR_NUM,
                TC.SAME_AS_PREV],
               OPC_GENUS.BASE,
               "Conditional move (compare less than). dst := (cmp1 < cmp2) ? src1 : src2 "
               "\nNote: dst/cmp1/cmp2 may be of a different type than src1/src2.")

# materialize addresses in a register
LEA = Opcode(0x38, "lea", OPC_KIND.LEA,
             [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
             [TC.ADDR, TC.SAME_AS_PREV, TC.OFFSET], OPC_GENUS.BASE,
             """Load effective Address. dst  := base + offset  
             
             (note: dst and base are addresses but offset is not))""")

LEA_MEM = Opcode(0x39, "lea.mem", OPC_KIND.LEA,
                 [OP_KIND.REG, OP_KIND.MEM, OP_KIND.REG_OR_CONST],
                 [TC.ADDR, TC.INVALID, TC.OFFSET], OPC_GENUS.BASE,
                 "Load effective memory address with offset, dst := base + offset")
LEA_STK = Opcode(0x3a, "lea.stk", OPC_KIND.LEA,
                 [OP_KIND.REG, OP_KIND.STK, OP_KIND.REG_OR_CONST],
                 [TC.ADDR, TC.INVALID, TC.OFFSET], OPC_GENUS.BASE,
                 "Load effective stack address with offset. dst := base + offset")
LEA_FUN = Opcode(0x3b, "lea.fun", OPC_KIND.LEA1, [OP_KIND.REG, OP_KIND.FUN],
                 [TC.CODE, TC.INVALID], OPC_GENUS.BASE,
                 "Load effective function address: dst := base (note: no offset).")

############################################################
# LOAD STORE 0x60
# ld/st base address  is in register, offset is immediate

# ld/st base address is register
LD = Opcode(0x40, "ld", OPC_KIND.LD,
            [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
            [TC.ANY, TC.ADDR, TC.OFFSET], OPC_GENUS.BASE,
            "Load from register base with offset.  dst := RAM[base + offset]",
            OA.MEM_RD)

# note: signedness of offset may matter here
LD_MEM = Opcode(0x41, "ld.mem", OPC_KIND.LD,
                [OP_KIND.REG, OP_KIND.MEM, OP_KIND.REG_OR_CONST],
                [TC.ANY, TC.INVALID, TC.OFFSET], OPC_GENUS.BASE,
                "Load from memory base with offset. dst := RAM[base + offset] ",
                OA.MEM_RD)

LD_STK = Opcode(0x42, "ld.stk", OPC_KIND.LD,
                [OP_KIND.REG, OP_KIND.STK, OP_KIND.REG_OR_CONST],
                [TC.ANY, TC.INVALID, TC.OFFSET], OPC_GENUS.BASE,
                "Load from stack base with offset. dst := RAM[base + offset]",
                OA.MEM_RD)

ST = Opcode(0x48, "st", OPC_KIND.ST,
            [OP_KIND.REG, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
            [TC.ADDR, TC.OFFSET, TC.ANY], OPC_GENUS.BASE,
            "Store to register base with offset. RAM[base + offset] := src",
            OA.MEM_WR)

ST_MEM = Opcode(0x49, "st.mem", OPC_KIND.ST,
                [OP_KIND.MEM, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
                [TC.INVALID, TC.OFFSET, TC.ANY], OPC_GENUS.BASE,
                "Store to memory base with offset. RAM[base + offset] := src",
                OA.MEM_WR)

ST_STK = Opcode(0x4a, "st.stk", OPC_KIND.ST,
                [OP_KIND.STK, OP_KIND.REG_OR_CONST, OP_KIND.REG_OR_CONST],
                [TC.INVALID, TC.OFFSET, TC.ANY], OPC_GENUS.BASE,
                "Store to stack base with offset. RAM[base + offset] := src",
                OA.MEM_WR)

############################################################
# FLOAT ALU OPERAND: 0x70, 0x80
SQRT = Opcode(0x60, "sqrt", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
              [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.BASE,
              "Compute the sqrt of floating point value")
ABS = Opcode(0x61, "abs", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
             [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.BASE,
             "Compute the absolute value of floating point value")
SIGN = Opcode(0x62, "sign", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
              [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
              "TBD")
# round towards positive infinity
CEIL = Opcode(0x63, "ceil", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
              [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
              "TBD")
# round towards negative infinity
FLOOR = Opcode(0x64, "floor", OPC_KIND.ALU1,
               [OP_KIND.REG, OP_KIND.REG_OR_CONST],
               [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
               "TBD")
# removes fractional part -> round to zero../
TRUNC = Opcode(0x65, "trunc", OPC_KIND.ALU1,
               [OP_KIND.REG, OP_KIND.REG_OR_CONST],
               [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
               "TBD")
# round to nearest - needed?
ROUND = Opcode(0x66, "round", OPC_KIND.ALU1,
               [OP_KIND.REG, OP_KIND.REG_OR_CONST],
               [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
               "TBD")

# do we need all these?
Opcode(0x67, "sin", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x68, "cos", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x69, "tan", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x6a, "asin", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x6b, "acos", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x6c, "atan", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x6d, "exp", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")
Opcode(0x6e, "log", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.FLT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")

############################################################
# Struct Stuff (experimental) 0xc0
############################################################

Opcode(0xc0, "st.stks", OPC_KIND.ST, [OP_KIND.STK, OP_KIND.FIELD, OP_KIND.REG],
       [TC.INVALID, TC.INVALID, TC.ANY], OPC_GENUS.STRUCT,
       "Store to stack base and immediate offset.")

Opcode(0xc1, "ld.stks", OPC_KIND.LD, [OP_KIND.REG, OP_KIND.STK, OP_KIND.FIELD],
       [TC.ANY, TC.INVALID, TC.INVALID], OPC_GENUS.STRUCT,
       "Load from stack base and immediate offset.")

Opcode(0xc2, "lea.stks", OPC_KIND.LEA1, [OP_KIND.REG, OP_KIND.FIELD],
       [TC.ADDR, TC.INVALID], OPC_GENUS.STRUCT,
       "Load effective stack address with field offset")

# ld/st base address is in register, offset is struct field
Opcode(0xc3, "lds", OPC_KIND.LD, [OP_KIND.REG, OP_KIND.REG, OP_KIND.FIELD],
       [TC.ANY, TC.ADDR, TC.INVALID], OPC_GENUS.STRUCT,
       "Load from register base and immediate offset.")

Opcode(0xc4, "sts", OPC_KIND.ST, [OP_KIND.REG, OP_KIND.FIELD, OP_KIND.REG],
       [TC.ADDR, TC.INVALID, TC.ANY], OPC_GENUS.STRUCT,
       "Store from register base and immediate offset.")

Opcode(0xc5, "adds", OPC_KIND.ALU, [OP_KIND.REG, OP_KIND.REG, OP_KIND.FIELD],
       [TC.ADDR, TC.SAME_AS_PREV, TC.INVALID], OPC_GENUS.STRUCT,
       "Addition with field offset. The first two regs must be address regs ")

############################################################
# Misc Experimental
############################################################
# INT SINGLE OPERAND 0xb0
# the src reg is treated as an unsigned reg
Opcode(0xb0, "cntpop", OPC_KIND.ALU1, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.INT, TC.SAME_AS_PREV], OPC_GENUS.TBD,
       "TBD")

# Note, negative lengths copy downwards
Opcode(0xb8, "bcopy", OPC_KIND.BCOPY,
       [OP_KIND.REG, OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.ADDR, TC.SAME_AS_PREV, TC.OFFSET], OPC_GENUS.TBD,
       "TBD",
       OA.MEM_WR | OA.MEM_RD)

# Note, negative lengths copy downwards
Opcode(0xba, "bzero", OPC_KIND.BZERO, [OP_KIND.REG, OP_KIND.REG_OR_CONST],
       [TC.ADDR, TC.OFFSET], OPC_GENUS.TBD,
       "TBD",
       OA.MEM_WR)

############################################################
# Internal USe
############################################################
NOP = Opcode(0xf1, "nop", OPC_KIND.NOP, [],
             [], OPC_GENUS.BASE,
             "nop - internal use.")

NOP1 = Opcode(0xf2, "nop1", OPC_KIND.NOP1, [OP_KIND.REG],
              [TC.ANY], OPC_GENUS.BASE,
              "nop with one reg - internal use. can be used to `reserve` a reg for code generation",
              OA.SPECIAL)


############################################################
# Directives 0xd
#
# do not correspond to instructions
############################################################


def Directive(no: int, name: str, operands, constraints, desc,
              group=OPC_GENUS.BASE):
    return Opcode(no, name, OPC_KIND.DIRECTIVE, operands, constraints,
                  desc=desc, group=group)


Directive(0x01, ".mem", [OP_KIND.NAME, OP_KIND.CONST, OP_KIND.MEM_KIND],
          [TC.INVALID, TC.UINT, TC.INVALID],
          "Add new memory region to unit")

Directive(0x02, ".data", [OP_KIND.CONST, OP_KIND.BYTES],
          [TC.UINT, TC.INVALID],
          "Add content to current memory region: multiple bytes")

Directive(0x03, ".addr.fun", [OP_KIND.CONST, OP_KIND.FUN],
          [TC.UINT, TC.INVALID],
          "Add content to current memory region: code address")

Directive(0x04, ".addr.mem", [OP_KIND.CONST, OP_KIND.MEM, OP_KIND.CONST],
          [TC.UINT, TC.INVALID, TC.OFFSET],
          "Add content to current memory region: "
          "memory address with offset")

Directive(0x05, ".fun", [OP_KIND.NAME, OP_KIND.FUN_KIND, OP_KIND.TYPE_LIST,
                         OP_KIND.TYPE_LIST],
          [TC.INVALID, TC.INVALID, TC.INVALID, TC.INVALID],
          "Add new function to unit")

Directive(0x06, ".bbl", [OP_KIND.NAME],
          [TC.INVALID],
          "Add new basic block to current function")

Directive(0x07, ".reg", [OP_KIND.DATA_KIND, OP_KIND.NAME_LIST],
          [TC.INVALID, TC.INVALID],
          "Add new registers to current function")

Directive(0x08, ".stk", [OP_KIND.NAME, OP_KIND.CONST, OP_KIND.CONST],
          [TC.INVALID, TC.UINT, TC.UINT],
          "Add stack region to current function")

Directive(0x09, ".jtb",
          [OP_KIND.NAME, OP_KIND.CONST, OP_KIND.BBL, OP_KIND.BBL_TAB],
          [TC.INVALID, TC.OFFSET, TC.INVALID, TC.INVALID],
          "bbl jump table: <name> <size> <default-bbl> <sparse-table>")

# experimental
Directive(0xe0, ".struct", [OP_KIND.NAME],
          [TC.INVALID],
          "Add new struct to unit", OPC_GENUS.STRUCT)

Directive(0xe1, ".field", [OP_KIND.NAME, OP_KIND.CONST, OP_KIND.CONST],
          [TC.INVALID, TC.UINT, TC.UINT],
          "Add field to current struct", OPC_GENUS.STRUCT)

Directive(0xe2, ".endstruct", [], [],
          "End current struct. Generates alignment and sizeof entries",
          OPC_GENUS.STRUCT)

Directive(0xe3, ".stk.s", [OP_KIND.NAME, OP_KIND.NAME],
          [TC.INVALID, TC.INVALID],
          "Add struct stack region to current function", OPC_GENUS.STRUCT)

############################################################
# experimental/unimplemented
############################################################

# add/sub/rotate with carry for legalizing say 64bit regs into pairs of 32bit regs
# unreachable
# swap
# unordered comparison
# https://stackoverflow.com/questions/8627331/what-does-ordered-unordered-comparison-mean
# conv int - flt  (urgent)
# conv int - int  (urgent)
# extract (urgent)
# insert (urgent)
# ld_l, st_C, cmpxch, cmpswp
# pow, pow2 powi
# log
# crc32c (supported by x86-64 and arm64 - using 0x1EDC6F41)
# aes ???
#  ld.scaled /st.scaled: base_reg + index_reg * scale imm + offset_imm
# copysign
# prefetch
# other built-ins: cf.:
# https://github.com/llvm-mirror/compiler-rt/tree/master/lib/builtins


_GROUPS = {
    0x01: "## Directives\n",
    0x10: "## Basic ALU\n",
    0x20: "## Conditional Branches\n",
    0x28: "## Other Control Flow\n",
    0x30: "## Move/Conversion\n",
    0x38: "## Address Arithmetic\n",
    0x40: "## Load\n",
    0x48: "## Store\n",
    0xf1: "## Misc\n",
}


def _render_operand_desc(purpose: str, kind: OP_KIND, constraint: TC, mod1="",
                         mod2="") -> str:
    kind_str = kind.name.replace("REG_OR_CONST", "REG/CONST")
    if constraint == TC.INVALID:
        return f"*{purpose}* {mod1}{kind_str}{mod2}"
    else:
        return f"*{purpose}* {mod1}{kind_str}:{constraint.name}{mod2}"


def _render_directive_doc(o: Opcode, fout):
    print_ops = [_render_operand_desc(*t, mod1="<sub>[", mod2="]</sub>")
                 for t in zip(o.purpose, o.operand_kinds, o.constraints)]
    print(f"#### [{o.no:02x}] {o.name} {' '.join(print_ops)}", file=fout)
    print(o.desc, file=fout)


def _render_opcode_doc(o: Opcode, fout):
    print_ops = [_render_operand_desc(*t, mod1="<sub>[", mod2="]</sub>")
                 for t in zip(o.purpose, o.operand_kinds, o.constraints)]

    if o.kind in _OFS_WRITING_REGS:
        print_ops.insert(1, "=")
    if o.kind in {OPC_KIND.ST}:
        print_ops.insert(-1, "=")
    print(f"#### [{o.no:02x}] {o.name} {' '.join(print_ops)}", file=fout)
    print(o.desc, file=fout)
    # print("* constraints:", ' '.join(ops))
    # print(f"{name:15.15},  // {' '.join(ops)} [{'
    # '.join(cons)}]"


def _render_documentation(fout):
    for opc in Opcode.Table.values():
        if opc.group != OPC_GENUS.BASE:
            continue
        if opc.no in _GROUPS:
            print(_GROUPS[opc.no], file=fout)
        if opc.kind == OPC_KIND.DIRECTIVE:
            _render_directive_doc(opc, fout)
        else:
            _render_opcode_doc(opc, fout)
        print()


def _render_h(fout):
    print("enum class OPC : uint8_t {", file=fout)
    last = 0
    print(f"    INVALID = 0x00,", file=fout)
    for opc in Opcode.Table.values():
        if opc.group != OPC_GENUS.BASE:
            continue
        if (opc.no & 0xff0) != last & 0xff0:
            print("", file=fout)
            last = opc.no

        name = opc.name.upper().replace(".", "_")
        if opc.kind == OPC_KIND.DIRECTIVE:
            name = "DIR_" + name[1:]
        print(f"    {name} = 0x{opc.no:02x},", file=fout)
    print("};", file=fout)

    # _render_enum("OpcodeFamily", ["OF.INVALID", "OF.DIRECTIVE"] +
    #             list(OFS_ALL))
    # _render_enum("OperandKind", ["OK.INVALID"] +
    #             [x.upper() for x in OKS_ALL])
    for cls in [OPC_GENUS, FUN_KIND, MEM_KIND, TC, OPC_KIND, DK, OP_KIND]:
        cgen.RenderEnum(cgen.NameValues(cls), f"class {cls.__name__} : uint8_t",
                        fout)
    cgen.RenderEnum(cgen.NameValues(OA), f"{OA.__name__} : uint16_t", fout)


def _render_c(fout):
    def render(cls, both_ways=True):
        cgen.RenderEnumToStringMap(cgen.NameValues(cls), cls.__name__, fout)
        cgen.RenderEnumToStringFun(cls.__name__, fout)
        if both_ways:
            cgen.RenderStringToEnumMap(cgen.NameValues(cls),
                                       cls.__name__ + "FromStringMap",
                                       cls.__name__ + "Jumper", fout)

    render(OPC_GENUS)
    render(FUN_KIND)
    render(MEM_KIND)
    render(TC)
    render(DK)
    render(OP_KIND, False)

    alpha = [(opc.name, opc.no) for opc in Opcode.Table.values()]
    cgen.RenderStringToEnumMap(alpha, "OPCFromStringMap", "OPCJumper", fout)

    print("const Opcode GlobalOpcodes[256] = {")
    opcodes = sorted([(o.no, o) for o in Opcode.Table.values()])
    last = -1

    dummy_opc = Opcode(0, "", OPC_KIND.RET, [], [], OPC_GENUS.INVALID, "")
    dummy_opc.name = ""
    dummy_opc.kind = OPC_KIND.INVALID

    def emit_one(opc: Opcode):
        kinds_str = [f"OP_KIND::{x.name}" for x in opc.operand_kinds]
        constraints_str = [f"TC::{x.name}" for x in opc.constraints]
        attributes = [f"OA::{x.name}" for x in OA if x in opc.attributes]
        if not attributes:
            attributes = ["0"]
        print("     {  // %2x %s" % (opc.no, opc.name))
        print('       {%s}, ' % ", ".join(kinds_str))
        print('       OPC_KIND::%s, OPC_GENUS::%s, %d, %d,' %
              (opc.kind.name, opc.group.name, len(opc.operand_kinds),
               opc.def_ops_count()))
        print('       {%s}, ' % ", ".join(constraints_str))
        print('       "%s", %s },' % (opc.name, '|'.join(attributes)))

    for n, o in opcodes:
        if o.group != OPC_GENUS.BASE:
            continue
        last += 1
        while last < n:
            dummy_opc.no = last
            emit_one(dummy_opc)
            last += 1
        emit_one(o)
    print("};\n")


def Dump():
    last = None
    for opc in Opcode.Table.values():
        if opc.kind != last:
            print()
            last = opc.kind
        ops = [_render_operand_desc(a, b, c) for a, b, c in
               zip(opc.purpose, opc.operand_kinds, opc.constraints)]

        print(f"{opc.kind.name} {opc.name} {' '.join(ops)}")
    print("total opcodes: %d" % len(Opcode.Table))


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "documentation":
            cgen.ReplaceContent(_render_documentation, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_h":
            cgen.ReplaceContent(_render_h, sys.stdin, sys.stdout)
        elif sys.argv[1] == "gen_c":
            cgen.ReplaceContent(_render_c, sys.stdin, sys.stdout)
    else:
        Dump()
