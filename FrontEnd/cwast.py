#!/usr/bin/python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend


"""

import sys
import re
import inspect
import dataclasses
import logging
import enum
import string
from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)

############################################################
# The AST Nodes and the fields they contain follow these rules
#
# All flields belong to one of these categories:
# * FLAG_FIELDS: bools
# * STR_FIELDS: strings
# * INT_FIELDS: ints
# * KIND_FIELDS: enums
# * NODE_FIELD: a single AST Node
# * LIST_FIELDS: zero or more AST Nodes
#
# The order of fields in the Node is:
#
# * fields from FLAG_FIELDS
# * fields from other categories
# If fields are in OPTIONAL_FIELDS they must come last


@enum.unique
class NF(enum.Flag):
    """Node Flags"""
    NONE = 0
    NEW_SCOPE = enum.auto()
    TYPE_ANNOTATED = enum.auto()   # node has a type (x_type)
    VALUE_ANNOTATED = enum.auto()  # node may have a comptime value (x_value)
    MUST_HAVE_VALUE = enum.auto()
    FIELD_ANNOTATED = enum.auto()  # node reference a struct field (x_field)
    SYMBOL_ANNOTATED = enum.auto()  # node reference a XXX_SYM_DEF node (x_symbol)
    TYPE_CORPUS = enum.auto()
    CONTROL_FLOW = enum.auto()
    GLOBAL_SYM_DEF = enum.auto()
    LOCAL_SYM_DEF = enum.auto()
    TOP_LEVEL_ONLY = enum.auto()
    TOP_LEVEL = enum.auto()
    MACRO_BODY_ONLY = enum.auto()
    TO_BE_EXPANDED = enum.auto()


@enum.unique
class GROUP(enum.IntEnum):
    Misc = enum.auto()
    Type = enum.auto()
    Statement = enum.auto()
    Value = enum.auto()
    Expression = enum.auto()
    Macro = enum.auto()


def _NAME(node):
    if node.ALIAS is not None:
        return "[" + node.ALIAS + "]"
    return "[" + node.__class__.__name__ + "]"


def _FLAGS(node):
    out = []
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.FLAG and getattr(node, c):
            out.append(c)
    outs = " ".join(out)
    return " " + outs if outs else outs

############################################################
# Comment
############################################################


@dataclasses.dataclass()
class Comment:
    """Comment

    Comments are proper AST nodes and may only occur where explicitly allowed.
    They refer to the next sibling in the tree.
    """
    ALIAS = "#"
    GROUP = GROUP.Misc
    FLAGS = NF.NONE
    #
    comment: str
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.comment}"

############################################################
# Identifier
############################################################


@enum.unique
class ID_KIND(enum.Enum):
    INVALID = 0
    VAR = 1
    CONST = 2
    FUN = 3


@dataclasses.dataclass()
class Id:
    """Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    """
    ALIAS = "id"
    GROUP = GROUP.Misc
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.SYMBOL_ANNOTATED
    #
    name: str          # last component of mod1::mod2:id: id
    path: str          # first components of mod1::mod2:id: mod1::mod2
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_symbol: Optional[Any] = None

    def __str__(self):
        joiner = "::" if self.path else ""
        return f"{_NAME(self)} {self.path}{joiner}{self.name}"


@dataclasses.dataclass()
class TypeAuto:
    """Placeholder for an unspecified (auto derived) type

    My only occur where explicitly allowed.
    """
    ALIAS = "auto"
    GROUP = GROUP.Type
    FLAGS = NF.NONE
    #
    x_srcloc: Optional[Any] = None

    # TODO
    # FLAGS = NF.TYPE_ANNOTATED
    # x_type: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


############################################################
# TypeNodes
############################################################
TYPE_NODE = Union["Id", "TypeBase",
                  "TypeSum", "TypeSlice", "TypeArray", "TypeFun"]


@dataclasses.dataclass()
class FunParam:
    """Function parameter

    """
    ALIAS = "param"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF
    #
    name: str      # empty str means no var specified (fun proto type)
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}: {self.type}"


@enum.unique
class BASE_TYPE_KIND(enum.Enum):
    INVALID = 0

    SINT = 10
    S8 = 11
    S16 = 12
    S32 = 13
    S64 = 14

    UINT = 20
    U8 = 21
    U16 = 22
    U32 = 23
    U64 = 24

    R32 = 30  # real
    R64 = 31  # real

    VOID = 40
    NORET = 41
    BOOL = 42


BASE_TYPE_KIND_UINT = set([
    BASE_TYPE_KIND.U8,
    BASE_TYPE_KIND.U16,
    BASE_TYPE_KIND.U32,
    BASE_TYPE_KIND.U64,
])

BASE_TYPE_KIND_SINT = set([
    BASE_TYPE_KIND.S8,
    BASE_TYPE_KIND.S16,
    BASE_TYPE_KIND.S32,
    BASE_TYPE_KIND.S64,
])

BASE_TYPE_KIND_INT = BASE_TYPE_KIND_UINT | BASE_TYPE_KIND_SINT

BASE_TYPE_KIND_REAL = set([
    BASE_TYPE_KIND.R32,
    BASE_TYPE_KIND.R64,
])


BASE_TYPE_KIND_TO_SIZE: Dict[BASE_TYPE_KIND, int] = {
    BASE_TYPE_KIND.U8: 1,
    BASE_TYPE_KIND.U16: 2,
    BASE_TYPE_KIND.U32: 4,
    BASE_TYPE_KIND.U64: 8,

    BASE_TYPE_KIND.S8: 1,
    BASE_TYPE_KIND.S16: 2,
    BASE_TYPE_KIND.S32: 4,
    BASE_TYPE_KIND.S64: 8,
    BASE_TYPE_KIND.R32: 4,
    BASE_TYPE_KIND.R64: 8,
    BASE_TYPE_KIND.VOID: 0,
    BASE_TYPE_KIND.NORET: 0,
    BASE_TYPE_KIND.BOOL: 1,
}


@dataclasses.dataclass()
class TypeBase:
    """Base type

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64
    """
    ALIAS = None
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    base_type_kind: BASE_TYPE_KIND
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)} {self.base_type_kind.name}"


@dataclasses.dataclass()
class TypePtr:
    """Pointer type
    """
    ALIAS = "ptr"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    mut: bool   # pointee is mutable
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"{_NAME(self)}{_FLAGS(self)} {self.type}"


@dataclasses.dataclass()
class TypeSlice:
    """A view/slice of an array with compile-time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    """
    ALIAS = "slice"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    mut: bool  # slice is mutable
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"{_NAME(self)}{mod}({self.type})"


@dataclasses.dataclass()
class TypeArray:
    """An array of the given type and `size`

    """
    ALIAS = "array"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    size: "EXPR_NODE"      # must be const and unsigned
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)} ({self.type}) {self.size}"


PARAMS_NODES = Union[Comment, FunParam]


@dataclasses.dataclass()
class TypeFun:
    """A function signature

    The `FunParam.name` field is ignored and should be `_`
    """
    ALIAS = "sig"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    params: List[PARAMS_NODES]
    result: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        t = [str(t) for t in self.params]
        return f"{_NAME(self)} {' '.join(t)} -> {self.result}"


TYPES_NODES = Union[Comment, TypeBase, TypeSlice, TypeArray, TypePtr, TypeFun]


@dataclasses.dataclass()
class TypeSum:
    """Sum types (tagged unions)

    Sums are "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    """
    ALIAS = "union"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    types: List[TYPES_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_size: int = -1
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        t = [str(t) for t in self.types]
        return f"{_NAME(self)} {' '.join(t)}"


############################################################
# Val Nodes
############################################################
ValNode = Union["ValFalse", "ValTrue", "ValNum", "ValUndef",
                "ValVoid", "ValArray", "ValString",
                "ValRec"]


@dataclasses.dataclass()
class ValAuto:
    """Placeholder for an unspecified (auto derived) value

    Used for: array dimensions, enum values, chap and range
    """
    ALIAS = "auto_val"
    GROUP = GROUP.Value
    FLAGS = NF.VALUE_ANNOTATED
    #
    x_srcloc: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class ValTrue:
    """Bool constant `true`"""
    ALIAS = "true"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class ValFalse:
    """Bool constant `false`"""
    ALIAS = "false"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class ValNum:
    """Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    """
    ALIAS = "num"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    number: str   # maybe a (unicode) character as well
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self): return f"{_NAME(self)} {self.number}"


@dataclasses.dataclass()
class ValUndef:
    """Special constant to indiciate *no default value*
    """
    ALIAS = "undef"
    GROUP = GROUP.Value
    FLAGS = NF.VALUE_ANNOTATED
    #
    x_srcloc: Optional[Any] = None
    x_value: Optional[Any] = None    # this is always a ValUndef() object

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class ValVoid:
    """Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type.
     """
    ALIAS = "void_val"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class IndexVal:
    """Part of an array literal

    e.g. `.1 = 5`
    If index is empty use `0` or `previous index + 1`.
    """
    ALIAS = None
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    value_or_undef: "EXPR_NODE"
    init_index: "EXPR_NODE"  # compile time constant
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.init_index}] = {self.value_or_undef}"


@dataclasses.dataclass()
class FieldVal:
    """Part of rec literal

    e.g. `.imag = 5`
    If field is empty use `first field` or `next field`.
    """
    ALIAS = None
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.FIELD_ANNOTATED
    #
    value: "EXPR_NODE"
    init_field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.init_field}] = {self.value}"


INITS_ARRAY_NODES = Union[Comment, IndexVal]


@dataclasses.dataclass()
class ValArray:
    """An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`
    """
    ALIAS = "array_val"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: TYPE_NODE
    expr_size: Union["EXPR_NODE", ValAuto]  # must be constant
    inits_array: List[INITS_ARRAY_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr_size}"


@dataclasses.dataclass()
class ValSlice:
    """A slice value comprised of a pointer and length

    type and mutability is defined by the pointer
    """
    ALIAS = "slice_val"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    pointer: "EXPR_NODE"
    expr_size: "EXPR_NODE"
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self): return f"{_NAME(self)} {self.string}"


INITS_REC_NODES = Union[Comment, FieldVal]


@dataclasses.dataclass()
class ValString:
    """An array value encoded as a string

    type is `[strlen(string)]u8`. `string` may be escaped/raw
    """
    ALIAS = None
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    raw: bool
    string: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self): return f"{_NAME(self)} {self.string}"


INITS_REC_NODES = Union[Comment, FieldVal]


@dataclasses.dataclass()
class ValRec:
    """A record literal

    `E.g.: complex{.imag = 5, .real = 1}`
    """
    ALIAS = "rec"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: TYPE_NODE
    inits_rec: List[INITS_REC_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        t = [str(i) for i in self.inits_rec]
        return f"{_NAME(self)} [{self.type}] {' '.join(t)}"


############################################################
# ExprNode
############################################################
EXPR_NODE = Union[ValNode, "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                  "ExprField", "ExprCall", "ExprParen",
                  "Expr1", "Expr2", "Expr3",
                  "ExprLen", "ExprSizeof"]


@dataclasses.dataclass()
class ExprDeref:
    """Dereference a pointer represented by `expr`"""
    ALIAS = "^"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE  # must be of type AddrOf
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr}"


@dataclasses.dataclass()
class ExprAddrOf:
    """Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable.
    """
    ALIAS = "&"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    mut: bool
    expr: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.expr}"


@dataclasses.dataclass()
class ExprCall:
    """Function call expression.
    """
    ALIAS = "call"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    polymorphic: bool
    callee: EXPR_NODE
    args: List[EXPR_NODE]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.callee}"


@dataclasses.dataclass()
class ExprParen:
    """Used for preserving parenthesis in the source
    """
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None


@dataclasses.dataclass()
class ExprField:
    """Access field in expression representing a record.
    """
    ALIAS = "."
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.FIELD_ANNOTATED
    #
    container: EXPR_NODE  # must be of type rec
    field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} {self.container} . {self.field}"


@enum.unique
class UNARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    NOT = 1
    MINUS = 2
    NEG = 3


UNARY_EXPR_SHORTCUT = {
    "!": UNARY_EXPR_KIND.NOT,     # boolean not
    "neg": UNARY_EXPR_KIND.NEG,   # bitwise not for unsigned
    "~": UNARY_EXPR_KIND.MINUS,
}

UNARY_EXPR_SHORTCUT_INV = {v: k for k, v in UNARY_EXPR_SHORTCUT.items()}


@dataclasses.dataclass()
class Expr1:
    """Unary expression."""
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    unary_expr_kind: UNARY_EXPR_KIND
    expr: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.unary_expr_kind} {self.expr}"


@enum.unique
class BINARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    REM = 5
    MIN = 6
    MAX = 7

    AND = 10
    OR = 11
    XOR = 12

    EQ = 20
    NE = 21
    LT = 22
    LE = 23
    GT = 24
    GE = 25

    ANDSC = 30  # && (SC = short circuit)
    ORSC = 31   # || (SC = short circuit)

    SHR = 40    # >>
    SHL = 41    # <<
    INCP = 50   # pointer add int
    DECP = 51   # pointer sub int
    PDELTA = 52  # pointer delta result is sint


BINARY_EXPR_SHORTCUT = {
    ">=": BINARY_EXPR_KIND.GE,
    ">": BINARY_EXPR_KIND.GT,
    "<=": BINARY_EXPR_KIND.LE,
    "<": BINARY_EXPR_KIND.LT,
    "==": BINARY_EXPR_KIND.EQ,
    "!=": BINARY_EXPR_KIND.NE,
    #
    "+": BINARY_EXPR_KIND.ADD,
    "-": BINARY_EXPR_KIND.SUB,
    "*": BINARY_EXPR_KIND.MUL,
    "/": BINARY_EXPR_KIND.DIV,
    "%": BINARY_EXPR_KIND.REM,
    "max": BINARY_EXPR_KIND.MAX,
    "min": BINARY_EXPR_KIND.MIN,
    #
    "&&": BINARY_EXPR_KIND.ANDSC,
    "||": BINARY_EXPR_KIND.ORSC,
    #
    "<<": BINARY_EXPR_KIND.SHL,
    ">>": BINARY_EXPR_KIND.SHR,
    #
    "and": BINARY_EXPR_KIND.AND,
    "or": BINARY_EXPR_KIND.OR,
    "xor": BINARY_EXPR_KIND.XOR,
    #
    "incp": BINARY_EXPR_KIND.INCP,
    "decp": BINARY_EXPR_KIND.DECP,
    "pdelta": BINARY_EXPR_KIND.PDELTA,
}

BINARY_EXPR_SHORTCUT_INV = {v: k for k, v in BINARY_EXPR_SHORTCUT.items()}


@dataclasses.dataclass()
class Expr2:
    """Binary expression."""
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    binary_expr_kind: BINARY_EXPR_KIND
    expr1: EXPR_NODE
    expr2: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.binary_expr_kind.name}({self.expr1}, {self.expr2})"


@dataclasses.dataclass()
class Expr3:
    """Tertiary expression (like C's `? :`)
    """
    ALIAS = "?"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    cond: EXPR_NODE  # must be of type  bool
    expr_t: EXPR_NODE
    expr_f: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"COND {self.cond} {self.expr_t} {self.expr_f}"

# Array/Slice Expressions


@dataclasses.dataclass()
class ExprIndex:
    """Checked indexed access of array or slice
    """
    ALIAS = "at"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    container: EXPR_NODE  # must be of type slice or array
    expr_index: EXPR_NODE  # must be of int type
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"AT {self.container} {self.expr_index}"


@dataclasses.dataclass()
class ExprLen:
    """Length of array or slice"""
    ALIAS = "len"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    container: EXPR_NODE   # must be of type slice or array
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return self.__class__.__name__
# Cast Like Expressions


@dataclasses.dataclass()
class ExprIs:
    """Test actual expression type within a Sum Type

    """
    ALIAS = "is"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr} {self.type}"


@dataclasses.dataclass()
class ExprAs:
    """Safe Cast (Conversion)

    Allowed:
    enum <-> undelying enum type
    wrapped type <-> undelying enum type
    u8-u64, s8-s64 <-> u8-u64, s8-s64
    u8-u64, s8-s64 -> r32-r64  (note: one way only)

    Possibly
    slice -> ptr
    ptr to rec -> ptr to first element of rec
    """
    ALIAS = "as"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.expr} AS {self.type}"


@dataclasses.dataclass()
class ExprAsNot:
    """Cast of Union to diff of the union and the given type

    """
    ALIAS = "asnot"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.expr} AS {self.type}"


@dataclasses.dataclass()
class ExprTryAs:
    """Narrow a `expr` which is of Sum to `type`

    If the is not possible return `default_or_undef` if that is not undef
    or trap otherwise.

    """
    ALIAS = "tryas"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    default_or_undef: Union[EXPR_NODE, ValUndef]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr} {self.type} {self.default_or_undef}"


@dataclasses.dataclass()
class ExprUnsafeCast:
    """Unsafe Cast

    Allowed:
    ptr a <-> ptr b

    """
    ALIAS = "cast"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None


@dataclasses.dataclass()
class ExprBitCast:
    """Bit cast.

    Type must have same size as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr
    """
    ALIAS = "bitcast"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: EXPR_NODE
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None


@dataclasses.dataclass()
class ExprSizeof:
    """Byte size of type

    Type is `uint`"""
    ALIAS = "sizeof"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.type}"


@dataclasses.dataclass()
class ExprOffsetof:
    """Byte offset of field in record types

    Type is `uint`"""
    ALIAS = "offsetof"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.FIELD_ANNOTATED
    #
    type: TYPE_NODE  # must be rec
    field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} {self.type} {self.field}"


############################################################
# Stmt
############################################################
BODY_NODES = Union["Comment", "StmtDefer", "StmtIf", "StmtBreak",
                   "StmtContinue", "StmtReturn", "StmtExpr",
                   "StmtBlock", "StmtCond"]

EXPR_LHS = Union["Id", "ExprDeref", "ExprIndex", "ExprField",
                 "ExprCall"]


@dataclasses.dataclass()
class StmtBlock:
    """Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    """
    ALIAS = "block"
    GROUP = GROUP.Statement
    FLAGS = NF.NEW_SCOPE
    #
    label: str
    body: List[BODY_NODES]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.label}"


@dataclasses.dataclass()
class StmtDefer:
    """Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    """
    ALIAS = "defer"
    GROUP = GROUP.Statement
    FLAGS = NF.NEW_SCOPE
    #
    body:  List[BODY_NODES]  # must NOT contain RETURN
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@dataclasses.dataclass()
class StmtIf:
    """If statement"""
    ALIAS = "if"
    GROUP = GROUP.Statement
    FLAGS = NF.NEW_SCOPE
    #
    cond: EXPR_NODE        # must be of type bool
    body_t: List[BODY_NODES]
    body_f: List[BODY_NODES]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@dataclasses.dataclass()
class Case:
    """Single case of a Cond statement"""
    ALIAS = "case"
    GROUP = GROUP.Statement
    FLAGS = NF.NEW_SCOPE
    #
    cond: EXPR_NODE        # must be of type bool
    body: List[BODY_NODES]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@dataclasses.dataclass()
class StmtCond:
    """Multicase if-elif-else statement"""
    ALIAS = "cond"
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    cases: List[Case]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"

# @dataclasses.dataclass()
# class StmtWhen:
#    "compile-time conditional"
#    ALIAS = "when"
#    cond: ExprNode        # must be of type bool
#    body_t: List[StmtNode]
#    body_f: List[StmtNode]


@dataclasses.dataclass()
class StmtBreak:
    """Break statement

    use "" if the target is the nearest for/while/block """
    ALIAS = "break"
    GROUP = GROUP.Statement
    FLAGS = NF.CONTROL_FLOW
    #
    target: str  # use "" for no value
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.target}"


@dataclasses.dataclass()
class StmtContinue:
    """Continue statement

    use "" if the target is the nearest for/while/block """
    ALIAS = "continue"
    GROUP = GROUP.Statement
    FLAGS = NF.CONTROL_FLOW
    #
    target: str  # use "" for no value
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.target}"


@dataclasses.dataclass()
class StmtReturn:
    """Return statement

    Uses void_val if the function's return type is void
    """
    ALIAS = "return"
    GROUP = GROUP.Statement
    FLAGS = NF.CONTROL_FLOW
    #
    expr_ret: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr_ret}"


@dataclasses.dataclass()
class StmtExpr:
    """Expression statement

    If expression does not have type void, `discard` must be `true`
    """
    ALIAS = "stmt"
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    discard: bool
    expr: ExprCall
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.discard} {self.expr}"


@dataclasses.dataclass()
class StmtStaticAssert:
    """Static assert statement (must evaluate to true at compile-time"""
    ALIAS = "static_assert"
    GROUP = GROUP.Statement
    FLAGS = NF.TOP_LEVEL
    #
    cond: EXPR_NODE  # must be of type bool
    message: str     # should this be an expression?
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@dataclasses.dataclass()
class StmtTrap:
    """Trap statement"""
    ALIAS = "trap"
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    x_srcloc: Optional[Any] = None


@enum.unique
class ASSIGNMENT_KIND(enum.Enum):
    """Compound Assignment Kinds"""
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    REM = 5
    #
    INCP = 6
    DECP = 7
    #
    AND = 10
    OR = 11
    XOR = 12
    #
    SHR = 20    # >>
    SHL = 31    # <<


ASSIGNMENT_SHORTCUT = {
    #
    "+=": ASSIGNMENT_KIND.ADD,
    "-=": ASSIGNMENT_KIND.SUB,
    "*=": ASSIGNMENT_KIND.MUL,
    "/=": ASSIGNMENT_KIND.DIV,
    "%=": ASSIGNMENT_KIND.REM,
    #
    "incp=": ASSIGNMENT_KIND.INCP,
    "decp=": ASSIGNMENT_KIND.DECP,
    #
    "and=": ASSIGNMENT_KIND.AND,
    "or=": ASSIGNMENT_KIND.OR,
    "xor=": ASSIGNMENT_KIND.XOR,
    #
    "<<=": ASSIGNMENT_KIND.SHL,
    ">>=": ASSIGNMENT_KIND.SHR,
}

ASSIGMENT_SHORTCUT_INV = {v: k for k, v in ASSIGNMENT_SHORTCUT.items()}


@dataclasses.dataclass()
class StmtCompoundAssignment:
    """Compound assignment statement"""
    ALIAS = None
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    assignment_kind: ASSIGNMENT_KIND
    lhs: EXPR_LHS
    expr: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.assignment_kind.name}] {self.lhs} = {self.expr}"


@dataclasses.dataclass()
class StmtAssignment:
    """Assignment statement"""
    ALIAS = "="
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    lhs: EXPR_LHS
    expr: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.lhs} = {self.expr}"

############################################################
# Definitions
############################################################


@dataclasses.dataclass()
class RecField:  #
    """Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    """
    ALIAS = "field"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    name: str
    type: TYPE_NODE
    initial_or_undef: Union["EXPR_NODE", ValUndef]    # must be const
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_offset: int = -1

    def __str__(self):
        return f"{_NAME(self)} {self.name}: {self.type} = {self.initial_or_undef}"


FIELDS_NODES = Union[Comment, RecField]


@dataclasses.dataclass()
class DefRec:
    """Record definition"""
    ALIAS = "defrec"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL_ONLY
    #
    pub:  bool
    name: str
    fields: List[FIELDS_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f" {_NAME(self)}{_FLAGS(self)}"


@dataclasses.dataclass()
class EnumVal:
    """ Enum element.

     `value: ValAuto` means previous value + 1"""
    ALIAS = "entry"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.VALUE_ANNOTATED
    #
    name: str
    value_or_auto: Union["ValNum", ValAuto]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}: {self.value_or_auto}"


ITEMS_NODES = Union[Comment, EnumVal]


@dataclasses.dataclass()
class DefEnum:
    """Enum definition"""
    ALIAS = "enum"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL_ONLY | NF.VALUE_ANNOTATED
    #
    pub:  bool
    name: str
    base_type_kind: BASE_TYPE_KIND   # must be integer
    items: List[ITEMS_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None  # used to guide the evaluation of EnumVal
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name}"


@dataclasses.dataclass()
class DefType:
    """Type definition

    """
    ALIAS = "type"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL_ONLY
    #
    pub:  bool
    wrapped: bool
    name: str
    type: TYPE_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} = {self.type}"


CONST_NODE = Union[Id, ValFalse, ValTrue, ValNum,
                   ValVoid, ValRec, ValArray, ValString]


@dataclasses.dataclass()
class DefVar:
    """Variable definition

    Allocates space on stack and initializes it with `initial_or_undef`.
    `mut` makes the allocated space read/write otherwise it is readonly.

    """
    ALIAS = "let"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF | NF.VALUE_ANNOTATED
    #
    mut: bool
    name: str
    type_or_auto: Union[TYPE_NODE, TypeAuto]
    initial_or_undef: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef}"


@dataclasses.dataclass()
class DefGlobal:
    """Variable definition

    Allocates space in static memory and initializes it with `initial_or_undef`.
    `mut` makes the allocated space read/write otherwise it is readonly.
    """
    ALIAS = "global"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL | NF.VALUE_ANNOTATED
    #
    pub: bool
    mut: bool
    name: str
    type_or_auto: Union[TYPE_NODE, TypeAuto]
    initial_or_undef: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef}"


@dataclasses.dataclass()
class DefFun:
    """Function definition"""
    ALIAS = "fun"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.NEW_SCOPE | NF.TOP_LEVEL_ONLY
    #
    init: bool
    fini: bool
    pub: bool
    extern: bool
    polymorphic: bool
    name: str
    params: List[PARAMS_NODES]
    result: TYPE_NODE
    body: List[BODY_NODES]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        params = ', '.join(str(p) for p in self.params)
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} [{params}]->{self.result}"


@enum.unique
class MOD_PARAM_KIND(enum.Enum):
    INVALID = 0
    CONST = 1
    MOD = 2
    TYPE = 3


@dataclasses.dataclass()
class ModParam:
    """Module Parameters"""
    ALIAS = None
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF
    #
    name: str
    mod_param_kind: MOD_PARAM_KIND
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name} {self.mod_param_kind.name}"


BODY_MOD_NODES = Union[Comment, DefFun, DefRec, DefEnum, DefVar]

PARAMS_MOD_NODES = Union[Comment, ModParam]


@dataclasses.dataclass()
class DefMod:
    """Module Definition

    The module is a template if `params` is non-empty"""
    ALIAS = "module"
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF
    #
    pub: bool
    name: str
    params_mod: List[PARAMS_MOD_NODES]
    body_mod: List[BODY_MOD_NODES]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        params = ', '.join(str(p) for p in self.params_mod)
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} [{params}]"


@dataclasses.dataclass()
class Import:
    """Import another Module"""
    ALIAS = "import"
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF
    #
    name: str
    alias: str
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


############################################################
# Macro Like
############################################################

@dataclasses.dataclass()
class ExprSrcLoc:
    """Source Location encoded as u32"""
    ALIAS = "src_loc"
    GROUP = GROUP.Expression
    FLAGS = NF.TO_BE_EXPANDED
    #
    x_srcloc: Optional[Any] = None


@dataclasses.dataclass()
class ExprStringify:
    """Human readable representation of the expression

    This is useful to implement for assert like features
    """
    ALIAS = "stringify"
    GROUP = GROUP.Expression
    FLAGS = NF.TO_BE_EXPANDED
    #
    expr:  EXPR_NODE
    #
    x_srcloc: Optional[Any] = None

############################################################
# Macro
############################################################


@enum.unique
class MACRO_PARAM_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = 0
    ID = 1
    STMT_LIST = 2
    EXPR = 3
    FIELD = 4
    TYPE = 5


@dataclasses.dataclass()
class MacroId:
    """Placeholder for a parameter

    This node will be expanded with the actual argument
    """
    ALIAS = "macro_id"
    GROUP = GROUP.Macro
    FLAGS = NF(0)
    #
    name: str
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


@dataclasses.dataclass()
class MacroVar:
    """Macro Variable definition whose name stems from a macro parameter or macro_gen_id"

    `name` must start with a `$`.

    """
    ALIAS = "macro_let"
    GROUP = GROUP.Macro
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF | NF.MACRO_BODY_ONLY
    #
    mut: bool
    name: str
    type_or_auto: Union[TYPE_NODE, TypeAuto]
    initial_or_undef: EXPR_NODE
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.initial_or_undef}"


@dataclasses.dataclass()
class MacroFor:
    """Macro for-loop like statement

    NYI
    """
    ALIAS = "macro_for"
    GROUP = GROUP.Macro
    FLAGS = NF.MACRO_BODY_ONLY
    #
    name: str
    name_list: str
    body: List[Any]
    #
    x_srcloc: Optional[Any] = None


@dataclasses.dataclass()
class MacroListArg:
    """Container for macro arguments that consists of multiple node (e.g. list of statements)

    """
    ALIAS = "macro_list_arg"
    GROUP = GROUP.Macro
    FLAGS = NF(0)
    #
    args: List[EXPR_NODE]
    #
    x_srcloc: Optional[Any] = None


@dataclasses.dataclass()
class MacroParam:
    """Macro Parameter"""
    ALIAS = "macro_param"
    GROUP = GROUP.Macro
    FLAGS = NF.LOCAL_SYM_DEF
    #
    name: str
    macro_param_kind: MACRO_PARAM_KIND
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name} {self.macro_param_kind.name}"


@dataclasses.dataclass()
class MacroInvoke:
    """Macro Invocation"""
    ALIAS = "macro_invoke"
    GROUP = GROUP.Macro
    FLAGS = NF.TO_BE_EXPANDED
    #
    name: str
    args: List[EXPR_NODE]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


PARAMS_MACRO_NODES = Union[Comment, MacroParam]


@dataclasses.dataclass()
class DefMacro:
    """Define a macro


    A macro consists of parameters whose name starts with a '$'
    and a body. Macros that evaluate to expressions will typically
    have a single node body
    """
    ALIAS = "macro"
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF | NF.NEW_SCOPE | NF.TOP_LEVEL_ONLY
    pub: bool
    #
    name: str
    params_macro: List[PARAMS_MACRO_NODES]
    gen_ids: List[str]
    body_macro: List[Any]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


############################################################
# S-Expression Serialization (Introspection driven)
############################################################


@enum.unique
class NFK(enum.Enum):
    INT = 1
    STR = 2
    FLAG = 3
    KIND = 4
    NODE = 5
    LIST = 6
    STR_LIST = 7


@dataclasses.dataclass()
class NFD:
    """Node Field Descriptor"""
    kind: NFK
    name: str
    doc: str
    extra: Any = None


ALL_FIELDS = [
    NFD(NFK.STR, "number", "a number"),
    NFD(NFK.STR, "name", "name of the object"),
    NFD(NFK.STR, "name_list", "name of the object list"),

    NFD(NFK.STR, "string", "string literal"),
    NFD(NFK.STR, "comment", "comment"),
    NFD(NFK.STR, "message", "message for assert failures"),
    NFD(NFK.STR, "field", "record field"),
    NFD(NFK.STR, "label", "block  name (if not empty)"),
    NFD(NFK.STR, "target",
        "name of enclosing while/for/block to brach to (empty means nearest)"),
    NFD(NFK.STR, "init_field", "initializer field or empty (empty means next field)"),
    NFD(NFK.STR, "path", "TBD"),
    NFD(NFK.STR, "alias", "name of imported module to be used instead of given name"),
    NFD(NFK.STR_LIST, "gen_ids",
        "name placeholder ids to be generated at macro instantiation time"),
    #
    NFD(NFK.FLAG, "pub", "has public visibility"),
    NFD(NFK.FLAG, "extern", "is external function (empty body)"),
    NFD(NFK.FLAG, "mut", "is mutable"),
    NFD(NFK.FLAG, "wrapped", "is wrapped type (forces type equivalence by name)"),
    NFD(NFK.FLAG, "discard", "ignore non-void expression"),
    NFD(NFK.FLAG, "init", "run function at startup"),
    NFD(NFK.FLAG, "fini", "run function at shutdown"),
    NFD(NFK.FLAG, "raw", "ignore escape sequences in string"),
    NFD(NFK.FLAG, "polymorphic", "function definition or call is polymorphic"),

    #
    NFD(NFK.KIND, "unary_expr_kind", "see Expr1 Kind below", UNARY_EXPR_KIND),
    NFD(NFK.KIND, "binary_expr_kind", "see Expr2 Kind below", BINARY_EXPR_KIND),
    NFD(NFK.KIND, "base_type_kind", "see Base Types below", BASE_TYPE_KIND),
    NFD(NFK.KIND, "mod_param_kind", "see ModParam Kind below",  MOD_PARAM_KIND),
    NFD(NFK.KIND, "assignment_kind",
        "see StmtCompoundAssignment Kind below", ASSIGNMENT_KIND),
    NFD(NFK.KIND,  "macro_param_kind",
        "see MacroParam Kind below",  MACRO_PARAM_KIND),
    #
    NFD(NFK.LIST, "params", "function parameters and/or comments", PARAMS_NODES),
    NFD(NFK.LIST, "params_mod", "module template parameters", PARAMS_MOD_NODES),
    NFD(NFK.LIST, "params_macro", "macro parameters", PARAMS_MACRO_NODES),
    NFD(NFK.LIST, "args", "function call arguments", "TBD"),
    NFD(NFK.LIST, "items", "enum items and/or comments", ITEMS_NODES),
    NFD(NFK.LIST, "fields", "record fields and/or comments", TYPES_NODES),
    NFD(NFK.LIST, "types", "union types", TYPES_NODES),
    NFD(NFK.LIST, "inits_array",
        "array initializers and/or comments", INITS_ARRAY_NODES),
    NFD(NFK.LIST, "inits_rec", "record initializers and/or comments", INITS_REC_NODES),
    #
    NFD(NFK.LIST, "body_mod",
        "toplevel module definitions and/or comments", BODY_MOD_NODES),
    NFD(NFK.LIST, "body", "statement list and/or comments", BODY_NODES),
    NFD(NFK.LIST, "body_t", "statement list and/or comments for true branch", BODY_NODES),
    NFD(NFK.LIST, "body_f", "statement list and/or comments for false branch", BODY_NODES),
    NFD(NFK.LIST, "body_except",
        "statement list and/or comments when type narrowing fails", BODY_NODES),
    NFD(NFK.LIST, "body_macro",
        "macro statments/expression", BODY_MOD_NODES),
    NFD(NFK.LIST, "cases", "list of case statements"),

    #
    NFD(NFK.NODE, "init_index", "initializer index or empty (empty mean next index)"),
    NFD(NFK.NODE, "type", "type expression"),
    NFD(NFK.NODE, "type_or_auto", "type expression"),
    NFD(NFK.NODE, "result", "return type"),
    NFD(NFK.NODE, "size", "compile-time constant size"),
    NFD(NFK.NODE, "expr_size", "expression determining the size or auto"),
    NFD(NFK.NODE, "expr_index", "expression determining the index to be accessed"),
    NFD(NFK.NODE, "expr", "expression"),
    NFD(NFK.NODE, "cond", "conditional expression must evaluate to a boolean"),
    NFD(NFK.NODE, "expr_t", "expression (will only be evaluated if cond == true)"),
    NFD(NFK.NODE, "expr_f", "expression (will only be evaluated if cond == false)"),
    NFD(NFK.NODE, "expr1", "left operand expression"),
    NFD(NFK.NODE, "expr2", "righ operand expression"),
    NFD(NFK.NODE, "expr_ret", "result expression (ValVoid means no result)"),
    NFD(NFK.NODE, "pointer", "pointer component of slice"),
    NFD(NFK.NODE, "range", "range expression"),
    NFD(NFK.NODE, "container", "array and slice"),
    NFD(NFK.NODE, "callee", "expression evaluating to the function to be called"),
    NFD(NFK.NODE, "start", "desired start of slice (default 0)"),
    NFD(NFK.NODE, "begin_or_auto", "range begin"),
    NFD(NFK.NODE, "end", "range end"),
    NFD(NFK.NODE, "step_or_auto", "range step"),
    NFD(NFK.NODE, "width", "desired width of slice (default: length of container)"),
    NFD(NFK.NODE, "value", ""),
    NFD(NFK.NODE, "value_or_auto", "enum constant or auto"),
    NFD(NFK.NODE, "value_or_undef", ""),
    NFD(NFK.NODE, "lhs", "l-value expression"),
    NFD(NFK.NODE, "initial_or_undef", "initializer"),
    NFD(NFK.NODE, "default_or_undef",
        "value if type narrowing fail or trap if undef"),
    NFD(NFK.NODE, "catch",
        "handler for type mismatch (implictly terminated by trap)"),

]

ALL_FIELDS_MAP: Dict[str, NFD] = {nfd.name: nfd for nfd in ALL_FIELDS}

# must come last in a dataclass
OPTIONAL_FIELDS = {
    "expr_ret": lambda srcloc: ValVoid(x_srcloc=srcloc),
    "width": lambda srcloc: ValAuto(x_srcloc=srcloc),
    "start": lambda srcloc:  ValAuto(x_srcloc=srcloc),
    "begin_or_auto": lambda srcloc:  ValNum("0", x_srcloc=srcloc),
    "step_or_auto": lambda srcloc:  ValNum("1", x_srcloc=srcloc),
    "value_or_auto": lambda srcloc: ValAuto(x_srcloc=srcloc),
    "target": lambda srcloc: "",
    "path": lambda srcloc: "",
    "alias": lambda srcloc: "",
    "message": lambda srcloc: "",
    "init_index": lambda srcloc: ValAuto(x_srcloc=srcloc),
    "init_field": lambda srcloc: "",
    "initial_or_undef": lambda srcloc: ValUndef(x_srcloc=srcloc),
    "inits_array": lambda srcloc: [],
}


X_FIELDS = {
    "x_type",   #
    "x_value",  #
    "x_field",
    "x_symbol",
    "x_alignment",
    "x_size",
    "x_offset",
    "x_srcloc",

}

# Note: we rely on the matching being done greedily
_TOKEN_CHAR = r"['][^\\']*(?:[\\].[^\\']*)*(?:[']|$)"
_TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
_TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
_TOKEN_OP = r'[\[\]\(\)]'
_TOKENS_ALL = re.compile("|".join(["(?:" + x + ")" for x in [
    _TOKEN_STR, _TOKEN_CHAR, _TOKEN_OP, _TOKEN_NAMENUM]]))

_TOKEN_ID = re.compile(r'[_A-Za-z$][_A-Za-z$0-9]*(::[_A-Za-z$][_A-Za-z$0-9])*')
_TOKEN_NUM = re.compile(r'[.0-9][_.a-z0-9]*')

# maps node class name and aliases to class
_NODES_ALIASES = {}

ALL_NODES = set()

for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and obj.__base__ is object and hasattr(obj, "ALIAS"):
        ALL_NODES.add(obj)
        _NODES_ALIASES[obj.__name__] = obj
        if obj.ALIAS is not None:
            _NODES_ALIASES[obj.ALIAS] = obj

        obj.FIELDS = []
        seen_optional = False
        seen_non_flag = False
        for field, type in obj.__annotations__.items():
            if field.startswith("x_"):
                assert field in X_FIELDS, f"unexpected x-field: {field} in node {type}"
                continue
            obj.FIELDS.append(field)
            nfd = ALL_FIELDS_MAP[field]
            if field in OPTIONAL_FIELDS:
                seen_optional = True
            else:
                assert not seen_optional, f"in {obj.__name__} optional fields must come last: {field}"

            if nfd.kind is NFK.FLAG:
                assert not seen_non_flag, "flags must come first"
            else:
                seen_non_flag = True


LOCAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.LOCAL_SYM_DEF in n.FLAGS)

GLOBAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.GLOBAL_SYM_DEF in n.FLAGS)

############################################################
#
############################################################


class _CheckASTContext:
    def __init__(self):
        self.toplevel = True
        self.in_fun = False
        self.in_macro = False


def _CheckMacroRecursively(node, seen_names: Set[str]):
    if isinstance(node, (MacroParam, MacroFor)):
        assert node.name.startswith("$")
        assert node.name not in seen_names, f"duplicate name: {node.name}"
        seen_names.add(node.name)
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            _CheckMacroRecursively(getattr(node, c), seen_names)
        elif nfd.kind is NFK.LIST:
            for cc in getattr(node, c):
                _CheckMacroRecursively(cc, seen_names)


def _CheckAST(node, ctx: _CheckASTContext):
    assert node.x_srcloc, f"Node without srcloc {node}"
    if NF.TOP_LEVEL_ONLY in node.FLAGS:
        assert ctx.toplevel, f"only allowed at toplevel: {node}"
    if NF.MACRO_BODY_ONLY in node.FLAGS:
        assert ctx.in_macro, f"only allowed in macros: {node}"
    if isinstance(node, DefMacro):
        for p in node.params_macro:
            assert p.name.startswith("$")
        for i in node.gen_ids:
            assert i.startswith("$")
        _CheckMacroRecursively(node, set())

    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            ctx.toplevel = isinstance(node, DefMod)
            ctx.in_fun |= isinstance(node, DefFun)
            ctx.in_macro |= isinstance(node, DefMacro)
            _CheckAST(getattr(node, c), ctx)
        elif nfd.kind is NFK.LIST:
            for cc in getattr(node, c):
                ctx.toplevel = isinstance(node, DefMod)
                ctx.in_fun |= isinstance(node, DefFun)
                ctx.in_macro |= isinstance(node, DefMacro)
                _CheckAST(cc, ctx)


##########################################################################################
PROLOG = """## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP
"""


def _RenderKindSimple(name, kind, fout):
    print(f"\n### {name} Kind\n", file=fout)
    print("|Kind|", file=fout)
    print("|----|", file=fout)
    for x in kind:
        if x is kind.INVALID:
            continue
        print(f"|{x.name:10}|", file=fout)


def _RenderKind(name, kind, inv, fout):
    print(f"\n### {name} Kind\n", file=fout)
    print("|Kind|Abbrev|", file=fout)
    print("|----|------|", file=fout)
    for x in kind:
        if x is kind.INVALID:
            continue
        assert x in inv, f"No custom name defined for emnum {x}"
        print(f"|{x.name:10}|{inv[x]}|", file=fout)


def MakeAnchor(name, alias):
    out = name.lower()
    if alias:
        out += "-" + alias
    tab = str.maketrans(" ", "-", "?,^&=@#$%")
    return out.lower().translate(tab)


def GenerateDocumentation(fout):
    print(PROLOG, file=fout)
    nodes = sorted((node.__name__, node) for node in ALL_NODES)
    print("\n## Node Overview",  file=fout)
    for name, cls in nodes:
        alias = ""
        if cls.ALIAS:
            alias = f"&nbsp;({cls.ALIAS})"
        anchor = MakeAnchor(name, cls.ALIAS)
        print(f"[{name}{alias}](#{anchor}) &ensp;", file=fout)

    print("\n## Enum Overview",  file=fout)
    for cls in ["Expr1", "Expr2", "StmtCompoundAssignment", "Base Types",
                "ModParam Types", "MacroParam Types"]:
        name = cls + " Kind"
        anchor = MakeAnchor(name, None)
        print(f"[{name}](#{anchor}) &ensp;", file=fout)

    nodes = sorted((node.GROUP, node.__name__, node) for node in ALL_NODES)
    last_group = ""
    for group, name, cls in nodes:
        if last_group != group:
            print(f"\n## {group.name} Node Details",  file=fout)
            last_group = group
        print(f"", file=fout)
        alias = ""
        if cls.ALIAS:
            alias = f" ({cls.ALIAS})"
        print(f"### {name}{alias}", file=fout)

        print(cls.__doc__,  file=fout)

        if NF.NEW_SCOPE in cls.FLAGS:
            print(f"", file=fout)
            print(f"Creates a new scope", file=fout)
        if NF.TOP_LEVEL_ONLY in cls.FLAGS:
            print(f"", file=fout)
            print(f"Allowed at top level only", file=fout)
        if NF.TOP_LEVEL in cls.FLAGS:
            print(f"", file=fout)
            print(f"Allowed at top level", file=fout)
        if len(cls.__annotations__):
            print(f"", file=fout)
            print("Fields:",  file=fout)

            for field, type in cls.__annotations__.items():
                if field in X_FIELDS:
                    continue
                nfd = ALL_FIELDS_MAP[field]
                kind = nfd.kind
                extra = ""
                optional_fun = OPTIONAL_FIELDS.get(field)
                if optional_fun is not None:
                    optional_val = optional_fun(0)
                    if optional_val == "":
                        extra = f' (default "")'
                    elif isinstance(optional_val, ValNum):
                        extra = f' (default {optional_val.number})'
                    elif optional_val is not None:
                        extra = f' (default {optional_val.__class__.__name__})'
                print(f"* {field} [{kind.name}]{extra}: {nfd.doc}", file=fout)

    print("## Enum Details",  file=fout)

    _RenderKind(Expr1.__name__,  UNARY_EXPR_KIND,
                UNARY_EXPR_SHORTCUT_INV, fout)
    _RenderKind(Expr2.__name__,  BINARY_EXPR_KIND,
                BINARY_EXPR_SHORTCUT_INV, fout)
    _RenderKind(StmtCompoundAssignment.__name__,
                ASSIGNMENT_KIND, ASSIGMENT_SHORTCUT_INV, fout)
    _RenderKindSimple("Base Types",
                      BASE_TYPE_KIND, fout)
    _RenderKindSimple("ModParam Types",
                      MOD_PARAM_KIND, fout)
    _RenderKindSimple("MacroParam Types",
                      MACRO_PARAM_KIND, fout)
##########################################################################################


def DumpFields(node_class):
    for tag, val in node_class.__annotations__.items():
        print(f"    {tag}: {val}")


class ReadTokens:
    def __init__(self, fp):
        self._fp = fp
        self.line_no = 0
        self._tokens = []

    def __iter__(self):
        return self

    def srcloc(self):
        # TODO: should also reflect the file once we support multiple input files
        return self.line_no

    def __next__(self):
        while not self._tokens:
            self._tokens = re.findall(_TOKENS_ALL, next(self._fp))
            self.line_no += 1
        return self._tokens.pop(0)


_SCALAR_TYPES = [
    #
    BASE_TYPE_KIND.SINT,
    BASE_TYPE_KIND.S8,
    BASE_TYPE_KIND.S16,
    BASE_TYPE_KIND.S32,
    BASE_TYPE_KIND.S64,
    #
    BASE_TYPE_KIND.UINT,
    BASE_TYPE_KIND.U8,
    BASE_TYPE_KIND.U16,
    BASE_TYPE_KIND.U32,
    BASE_TYPE_KIND.U64,
    #
    BASE_TYPE_KIND.R32,
    BASE_TYPE_KIND.R64,
]


def _MakeTypeBaseLambda(kind: BASE_TYPE_KIND):
    return lambda srcloc: TypeBase(kind, x_srcloc=srcloc)


# maps "atoms" to the nodes they will be expanded to
_SHORT_HAND_NODES = {
    "auto": lambda srcloc: TypeAuto(x_srcloc=srcloc),
    #
    "noret": _MakeTypeBaseLambda(BASE_TYPE_KIND.NORET),
    "bool": _MakeTypeBaseLambda(BASE_TYPE_KIND.BOOL),
    "void": _MakeTypeBaseLambda(BASE_TYPE_KIND.VOID),
    #
    "void_val": lambda srcloc: ValVoid(x_srcloc=srcloc),
    "undef": lambda srcloc: ValUndef(x_srcloc=srcloc),
    "true": lambda srcloc: ValTrue(x_srcloc=srcloc),
    "false": lambda srcloc: ValFalse(x_srcloc=srcloc),
}


for t in _SCALAR_TYPES:
    name = t.name.lower()
    _SHORT_HAND_NODES[name] = _MakeTypeBaseLambda(t)


def ExpandShortHand(t, srcloc) -> Any:
    """Expands atoms, ids, and numbers to proper nodes"""
    x = _SHORT_HAND_NODES.get(t)
    if x is not None:
        return x(srcloc)

    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        # TODO: r"
        return ValString(False, t, x_srcloc=srcloc)
    elif _TOKEN_ID.match(t):
        if t[0] == "$":
            return MacroId(t, x_srcloc=srcloc)
        parts = t.rsplit("::", 1)
        return Id(parts[-1], "" if len(parts) == 1 else parts[0], x_srcloc=srcloc)
    elif _TOKEN_NUM.match(t):
        return ValNum(t, x_srcloc=srcloc)
    elif len(t) >= 3 and t[0] == "'" and t[-1] == "'":
        return ValNum(t, x_srcloc=srcloc)
    else:
        return None


def ReadNodeList(stream: ReadTokens, parent_cls):
    out = []
    while True:
        token = next(stream)
        if token == "]":
            break
        if token == "(":
            out.append(ReadSExpr(stream, parent_cls))
        else:
            out.append(ExpandShortHand(token, stream.srcloc()))
    return out


def ReadStrList(stream) -> List[str]:
    out = []
    while True:
        token = next(stream)
        if token == "]":
            break
        else:
            out.append(token)
    return out


def ReadPiece(field, token, stream: ReadTokens, parent_cls) -> Any:
    """Read a single component of an SExpr including lists."""
    nfd = ALL_FIELDS_MAP[field]
    if nfd.kind is NFK.FLAG:
        return bool(token)
    elif nfd.kind is NFK.STR:
        return token
    elif nfd.kind is NFK.INT:
        return token
    elif nfd.kind is NFK.KIND:
        assert nfd.extra is not None, f"{field} {token}"
        return nfd.extra[token]
    elif nfd.kind is NFK.NODE:
        if token == "(":
            return ReadSExpr(stream, parent_cls)
        out = ExpandShortHand(token, stream.srcloc())
        assert out is not None, f"Cannot expand {token} for {field}"
        return out
    elif nfd.kind is NFK.STR_LIST:
        assert token == "[", f"expected list start for: {field} {token}"
        return ReadStrList(stream)
    elif nfd.kind is NFK.LIST:
        assert token == "[", f"expected list start for: {field} {token}"
        return ReadNodeList(stream, parent_cls)
    else:
        assert None


BINOP_BOOL = {
    BINARY_EXPR_KIND.GE,
    BINARY_EXPR_KIND.GT,
    BINARY_EXPR_KIND.LE,
    BINARY_EXPR_KIND.LT,
    BINARY_EXPR_KIND.EQ,
    BINARY_EXPR_KIND.NE,
    BINARY_EXPR_KIND.ANDSC,
    BINARY_EXPR_KIND.ORSC,
}

BINOP_OPS_HAVE_SAME_TYPE = {
    BINARY_EXPR_KIND.GE,
    BINARY_EXPR_KIND.GT,
    BINARY_EXPR_KIND.LE,
    BINARY_EXPR_KIND.LT,
    BINARY_EXPR_KIND.EQ,
    BINARY_EXPR_KIND.NE,
    #
    BINARY_EXPR_KIND.ADD,
    BINARY_EXPR_KIND.SUB,
    BINARY_EXPR_KIND.MUL,
    BINARY_EXPR_KIND.DIV,
    BINARY_EXPR_KIND.REM,
    BINARY_EXPR_KIND.MIN,
    BINARY_EXPR_KIND.MAX,
    #
    BINARY_EXPR_KIND.ANDSC,
    BINARY_EXPR_KIND.ORSC,
    # ???
    # BINARY_EXPR_KIND.SHL,
    # BINARY_EXPR_KIND.SHR,
    #
    BINARY_EXPR_KIND.AND,
    BINARY_EXPR_KIND.OR,
    BINARY_EXPR_KIND.XOR,
}


def ReadMacroInvocation(tag, stream: ReadTokens):
    parent_cls = MacroInvoke
    srcloc = stream.srcloc()
    logger.info("Readdng MACRO INVOCATION %s at %s", tag, srcloc)
    args = []
    while True:
        token = next(stream)
        if token == ")":
            return MacroInvoke(tag, args, x_srcloc=srcloc)
        elif token == "(":
            args.append(ReadSExpr(stream, parent_cls))
        elif token == "[":
            args.append(MacroListArg(ReadNodeList(
                stream, parent_cls), x_srcloc=srcloc))
        else:
            out = ExpandShortHand(token, stream.srcloc())
            assert out is not None, f"while processing {tag} unexpected macro arg: {token}"
            args.append(out)
    return args


def ReadRestAndMakeNode(cls, pieces: List[Any], fields: List[str], stream: ReadTokens):
    """Read the remaining componts of an SExpr (after the tag).

    Can handle optional bools at the beginning and an optional 'tail'
    """
    srcloc = stream.srcloc()
    logger.info("Readding TAG %s at %s", cls.__name__, srcloc)
    token = next(stream)
    for field in fields:
        nfd = ALL_FIELDS_MAP[field]
        if token == ")":
            # we have reached the end before all the fields were processed
            # fill in default values
            assert field in OPTIONAL_FIELDS, f"in {cls.__name__} unknown optional (or missing) field: {field}"
            pieces.append(OPTIONAL_FIELDS[field](srcloc))
        elif nfd.kind is NFK.FLAG:
            if token == field:
                pieces.append(True)
                token = next(stream)
            else:
                pieces.append(False)
        else:
            pieces.append(ReadPiece(field, token, stream, cls))
            token = next(stream)
    if token != ")":
        CompilerError(stream.srcloc(
        ), f"while parsing {cls.__name__} expected node-end but got {token}")
    return cls(*pieces, x_srcloc=srcloc)


def ReadSExpr(stream: ReadTokens, parent_cls) -> Any:
    """The leading '(' has already been consumed"""
    tag = next(stream)
    if tag in UNARY_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(Expr1, [UNARY_EXPR_SHORTCUT[tag]],
                                   ["expr"], stream)
    elif tag in BINARY_EXPR_SHORTCUT:
        return ReadRestAndMakeNode(Expr2, [BINARY_EXPR_SHORTCUT[tag]],
                                   ["expr1", "expr2"], stream)
    elif tag in ASSIGNMENT_SHORTCUT:
        return ReadRestAndMakeNode(StmtCompoundAssignment, [ASSIGNMENT_SHORTCUT[tag]],
                                   ["lhs", "expr"], stream)
    else:
        cls = _NODES_ALIASES.get(tag)
        if not cls:
            # unknown node name - assume it is a macro
            return ReadMacroInvocation(tag, stream)
        assert cls is not None, f"[{stream.line_no}] Non node: {tag}"

        # This helps catching missing closing braces early
        if NF.TOP_LEVEL_ONLY in cls.FLAGS:
            if parent_cls is not DefMod:
                CompilerError(stream.srcloc(
                ), f"toplevel node {cls.__name__} not allowed in {parent_cls.__name__}")

        fields = [f for f, _ in cls.__annotations__.items()
                  if not f.startswith("x_")]
        return ReadRestAndMakeNode(cls, [], fields, stream)


VALUE_NODES = (ValTrue, ValFalse, ValNum, IndexVal,
               ValUndef, ValVoid, FieldVal, ValArray,
               ValString, ValRec)


def ReadModsFromStream(fp) -> List[DefMod]:
    asts = []
    stream = ReadTokens(fp)
    try:
        failure = False
        while True:
            t = next(stream)
            failure = True
            assert t == "("
            sexpr = ReadSExpr(stream, None)
            assert isinstance(sexpr, DefMod)
            _CheckAST(sexpr, _CheckASTContext())
            asts.append(sexpr)
            failure = False
    except StopIteration:
        assert not failure, f"truncated file"
    return asts


def CompilerError(srcloc, msg):
    print(f"{srcloc} ERROR: {msg}", file=sys.stdout)
    assert False


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    if len(sys.argv) > 1 and sys.argv[1] == "gendoc":
        GenerateDocumentation(sys.stdout)
    else:
        ReadModsFromStream(sys.stdin)
