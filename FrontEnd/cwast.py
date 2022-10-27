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
    TYPE_ANNOTATED = enum.auto()
    TYPE_CORPUS = enum.auto()
    CONTROL_FLOW = enum.auto()
    GLOBAL_SYM_DEF = enum.auto()
    LOCAL_SYM_DEF = enum.auto()

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
    FLAGS = NF.NONE

    comment: str

    def __str__(self):
        return "# " + self.comment

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

    They may contain a path component indicating which modules they reference.
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED
    name: str          # last component of mod1::mod2:id: id
    path: str          # first components of mod1::mod2:id: mod1::mod2

    def __str__(self):
        joiner = "::" if self.path else ""
        return f"{self.path}{joiner}{self.name}"


class Auto:
    """Placeholder for an unspecified value or type

    My only occur where explicitly allowed.
    """
    ALIAS = "auto"
    FLAGS = NF.NONE

    def __str__(self):
        return "AUTO"


############################################################
# TypeNodes
############################################################
TypeNode = Union["Id", "TypeBase",
                 "TypeSum", "TypeSlice", "TypeArray", "TypeFun"]


@dataclasses.dataclass()
class FunParam:
    """Function parameter

    """
    ALIAS = "param"
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF

    name: str      # empty str means no var specified (fun proto type)
    type: TypeNode

    def __str__(self):
        return f"{self.name}: {self.type}"


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


@dataclasses.dataclass()
class TypeBase:
    """Base type 

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64    
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    base_type_kind: BASE_TYPE_KIND

    def __str__(self):
        return self.base_type_kind.name


@dataclasses.dataclass()
class TypePtr:
    """Pointer type (mutable/non-mutable)
    """
    ALIAS = "ptr"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    mut: bool   # pointee is mutable
    type: TypeNode

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"PTR{mod}({self.type})"


@dataclasses.dataclass()
class TypeSlice:
    """A view/slice of an array with compile time unknown dimentions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    mut: bool  # slice is mutable
    type: TypeNode


@dataclasses.dataclass()
class TypeArray:
    """An array of the given type and `size`

    Size must be evaluatable as a compile time constant"""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    size: "ExprNode"      # must be const and unsigned
    type: TypeNode


PARAMS_NODES = Union[Comment, FunParam]


@dataclasses.dataclass()
class TypeFun:
    """A function signature

    The `FunParam.name` field is ignored and should be `_`
    """
    ALIAS = "sig"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    params: List[PARAMS_NODES]
    result: TypeNode


TYPES_NODES = Union[Comment, TypeBase, TypeSlice, TypeArray, TypePtr, TypeFun]


@dataclasses.dataclass()
class TypeSum:
    """Sum types (tagged unions)

    Sums are "auto flattening", e.g.
    Sum(a, Sum(b,c), Sum(a, d)) = Sum(a, b, c, d)
    """
    ALIAS = "union"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    types: List[TYPES_NODES]


############################################################
# Val Nodes
############################################################
ValNode = Union["ValFalse", "ValTrue", "ValNum", "ValUndef",
                "ValVoid", "ValArray", "ValArrayString",
                "ValRec"]


@dataclasses.dataclass()
class ValTrue:
    """Bool constant `true`"""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self):
        return "TRUE"


@dataclasses.dataclass()
class ValFalse:
    """Bool constant `false`"""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self):
        return "FALSE"


@dataclasses.dataclass()
class ValNum:
    """Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    number: str   # maybe a (unicode) character as well

    def __str__(self): return self.number


@dataclasses.dataclass()
class ValUndef:
    """Special constant to indiciate *no default value*
    """
    ALIAS = None
    FLAGS = NF(0)

    def __str__(self): return f"UNDEF"


@dataclasses.dataclass()
class ValVoid:
    """Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a sum type.
     """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self): return "VOID"


@dataclasses.dataclass()
class IndexVal:
    "Used for array initialization, e.g. `.1 = 5`"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    value: "ExprNode"
    index: str


@dataclasses.dataclass()
class FieldVal:
    """Used for rec initialization, e.g. `.imag = 5`"""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    field: str
    value: "ExprNode"


INITS_ARRAY_NODES = Union[Comment, IndexVal]


@dataclasses.dataclass()
class ValArray:
    """An array literal

    `[10]int{.1 = 5, .2 = 6}`
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    expr_size: Union["ExprNode", Auto]  # must be constant
    inits_array: List[INITS_ARRAY_NODES]


@dataclasses.dataclass()
class ValArrayString:
    """An array value encoded as a string

    type is `u8[strlen(string)]`. `string` may be escaped/raw
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    raw: bool
    string: str

    def __str__(self): return f"STRING({self.string})"


INITS_REC_NODES = Union[Comment, FieldVal]


@dataclasses.dataclass()
class ValRec:
    """A record literal

    `E.g.: complex{.imag = 5, .real = 1}`
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    inits_rec: List[INITS_REC_NODES]


############################################################
# ExprNode
############################################################
ExprNode = Union[ValNode, "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                 "ExprField", "ExprCall", "ExprParen",
                 "Expr1", "Expr2", "Expr3",
                 "ExprChop",
                 "ExprLen", "ExprSizeof"]


@dataclasses.dataclass()
class ExprDeref:
    """Dereference a pointer represented by `expr`"""
    ALIAS = "^"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode  # must be of type AddrOf


@dataclasses.dataclass()
class ExprAddrOf:
    """Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable.
    """
    ALIAS = "&"
    FLAGS = NF.TYPE_ANNOTATED
    mut: bool
    expr: ExprNode


@dataclasses.dataclass()
class ExprCall:
    """Function call expression.
    """
    ALIAS = "call"
    FLAGS = NF.TYPE_ANNOTATED

    callee: ExprNode
    args: List[ExprNode]


@dataclasses.dataclass()
class ExprParen:
    """Used for preserving parenthesis in the source
    """
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode


@dataclasses.dataclass()
class ExprField:
    """Access field in expression representing a record.
    """
    ALIAS = "."
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type rec
    field: str


@enum.unique
class UNARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    NOT = 1
    MINUS = 2
    NEG = 3


@dataclasses.dataclass()
class Expr1:
    """Unary expression."""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    unary_expr_kind: UNARY_EXPR_KIND
    expr: ExprNode


@enum.unique
class BINARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    REM = 5

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
    PADD = 50   # pointer add int
    PSUB = 51   # pointer sub int
    PDELTA = 52  # pointer delta result is sint


@dataclasses.dataclass()
class Expr2:
    """Binary expression."""
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    binary_expr_kind: BINARY_EXPR_KIND
    expr1: ExprNode
    expr2: ExprNode

    def __str__(self):
        return f"{self.binary_expr_kind.name}({self.expr1}, {self.expr2})"


@dataclasses.dataclass()
class Expr3:
    """Tertiary expression (like C's `? :`) 
    """
    ALIAS = "?"
    FLAGS = NF.TYPE_ANNOTATED

    cond: ExprNode  # must be of type  bool
    expr_t: ExprNode
    expr_f: ExprNode


# Array/Slice Expressions


@dataclasses.dataclass()
class ExprIndex:
    """Checked indexed access of array or slice 
    """
    ALIAS = "at"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type slice or array
    expr_index: ExprNode  # must be of int type


@dataclasses.dataclass()
class ExprChop:
    """Slicing expression of array or slice
    """
    ALIAS = "chop"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type slice or array
    start: Union[ExprNode, "Auto"]  # must be of int type
    width: Union[ExprNode, "Auto"]  # must be of int type


@dataclasses.dataclass()
class ExprLen:
    """Length of array or slice"""
    ALIAS = "len"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode   # must be of type slice or array


# Cast Like Expressions

@dataclasses.dataclass()
class ExprIs:
    """Test actual expression type within a Sum Type

    """
    ALIAS = "is"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode
    type: TypeNode


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
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode
    type: TypeNode


@dataclasses.dataclass()
class ExprUnsafeCast:
    """Unsafe Cast

    Allowed:
    ptr a <-> ptr b

    """
    ALIAS = "cast"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode
    type: TypeNode


@dataclasses.dataclass()
class ExprBitCast:
    """Bit cast.

    Type must have same size as type of item

    s32,u32 <-> f32
    s64,u64 <-> f64
    sint, uint <-> ptr
    uX <-> sX
    """
    ALIAS = "bitcast"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode
    type: TypeNode


# Const Expression


@dataclasses.dataclass()
class ExprSizeof:
    """Byte size of type

    Type is `uint`"""
    ALIAS = "sizeof"
    FLAGS = NF.TYPE_ANNOTATED

    expr: TypeNode


@dataclasses.dataclass()
class ExprOffsetof:
    """Byte offset of field in record types

    Type is `uint`"""
    ALIAS = "offsetof"
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode  # must be rec
    field: str


@dataclasses.dataclass()
class ExprRange:
    """Range expression for simple for-loops

    Modelled after Python's `range`, e.g.
    Range(end=5) = [0, 1, 2, 3, 4]
    Range(end=5, start=2) = [2, 3, 4]
    Range(end=5, start=1, step=2) = [1, 3]
    Range(end=1, start=5, step=-2) = [5, 3]
    """
    ALIAS = "range"
    FLAGS = NF.TYPE_ANNOTATED

    end: ExprNode   # start, end ,step work like range(start, end, step)
    begin_or_auto: Union[Auto, ExprNode]
    step_or_auto: Union[Auto, ExprNode]

    def __str__(self):
        return f"RANGE({self.end}, {self.begin_or_auto}, {self.step_or_auto})"


############################################################
# Stmt
############################################################
BODY_NODES = Union["Comment", "StmtWhile", "StmtDefer", "StmtIf", "StmtBreak",
                   "StmtContinue", "StmtReturn", "StmtExpr", "StmtAssert",
                   "StmtBlock"]

EXPR_LHS = Union["Id", "ExprDeref", "ExprIndex", "ExprField",
                 "ExprCall"]


@dataclasses.dataclass()
class StmtWhile:
    """While statement.
    """
    ALIAS = "while"
    FLAGS = NF.NEW_SCOPE

    cond: ExprNode
    body: List[BODY_NODES]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"WHILE {self.cond}:\n{body}"


@dataclasses.dataclass()
class StmtBlock:
    """Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    """
    ALIAS = "block"
    FLAGS = NF.NEW_SCOPE

    label: str
    body: List[BODY_NODES]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"BLOCK {self.label}:\n{body}"


@dataclasses.dataclass()
class StmtFor:
    """For statement.

    Defines the non-mut variable `name`.
    """
    ALIAS = "for"
    FLAGS = NF.NEW_SCOPE | NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF

    name: str
    type_or_auto: Union[TypeNode, Auto]
    range: ExprNode
    body: List[BODY_NODES]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"FOR  {self.name}: {self.type_or_auto} = {self.range}:\n{body}"


@dataclasses.dataclass()
class StmtDefer:
    """Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    """
    ALIAS = "defer"
    FLAGS = NF.NEW_SCOPE

    body: List[BODY_NODES]  # must NOT contain RETURN

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"DEFER:\n{body}"


@dataclasses.dataclass()
class StmtIf:
    """If statement"""
    ALIAS = "if"
    FLAGS = NF.NEW_SCOPE

    cond: ExprNode        # must be of type bool
    body_t: List[BODY_NODES]
    body_f: List[BODY_NODES]

    def __str__(self):
        body_t = '\n'.join(str(s) for s in self.body_t)
        body_f = '\n'.join(str(s) for s in self.body_f)
        return f"IF {self.cond}:\n{body_t}\nELSE:\n{body_f}"


# @dataclasses.dataclass()
# class StmtWhen:
#    "compile time conditional"
#    ALIAS = "when"
#    cond: ExprNode        # must be of type bool
#    body_t: List[StmtNode]
#    body_f: List[StmtNode]


@dataclasses.dataclass()
class StmtBreak:
    """Break statement

    use "" if the target is the nearest for/while/block """
    ALIAS = "break"
    FLAGS = NF.CONTROL_FLOW

    target: str  # use "" for no value

    def __str__(self):
        return f"BREAK {self.target}"


@dataclasses.dataclass()
class StmtContinue:
    """Continue statement

    use "" if the target is the nearest for/while/block """
    ALIAS = "continue"
    FLAGS = NF.CONTROL_FLOW
    target: str  # use "" for no value

    def __str__(self):
        return f"CONTINUE {self.target}"


@dataclasses.dataclass()
class StmtReturn:
    """Return statement

    Use `void` value if the function's return type is `void`
    """
    ALIAS = "return"
    FLAGS = NF.CONTROL_FLOW
    expr_ret: ExprNode

    def __str__(self):
        return f"RETURN {self.expr_ret}"


@dataclasses.dataclass()
class StmtExpr:
    """Expression statement

    If expression does not have type void, `discard` must be `true`
    """
    ALIAS = "expr"
    FLAGS = NF.NONE

    discard: bool
    expr: ExprCall


@dataclasses.dataclass()
class StmtAssert:
    """Assert statement"""
    ALIAS = "assert"
    FLAGS = NF.NONE

    cond: ExprNode  # must be of type bool
    message: str     # should this be an expression?


@enum.unique
class ASSIGNMENT_KIND(enum.Enum):
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    REM = 5

    AND = 10
    OR = 11
    XOR = 12

    SHR = 20    # >>
    SHL = 31    # <<


@dataclasses.dataclass()
class StmtCompoundAssignment:
    """Compound assignment statement"""
    ALIAS = None
    FLAGS = NF.NONE

    assignment_kind: ASSIGNMENT_KIND
    lhs: EXPR_LHS
    expr: ExprNode


@dataclasses.dataclass()
class StmtAssignment:
    """Assignment statement"""
    ALIAS = "="
    FLAGS = NF.NONE

    lhs: EXPR_LHS
    expr: ExprNode


############################################################
# Definitions
############################################################
@dataclasses.dataclass()
class RecField:  #
    """Record field

    `initial` must be a compile-time constant or `ValUndef`"""
    ALIAS = "field"
    FLAGS = NF.TYPE_ANNOTATED

    name: str
    type: TypeNode
    initial_or_undef: Union["ExprNode", ValUndef]    # must be const

    def __str__(self):
        return f"{self.name}: {self.type} = {self.initial_or_undef}"


FIELDS_NODES = Union[Comment, RecField]


@dataclasses.dataclass()
class DefRec:
    """Record definition (only allowed at top-level)"""
    ALIAS = "rec"
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    fields: List[FIELDS_NODES]

    def __str__(self):
        fields = '\n'.join(str(s) for s in self.fields)
        return f"REC {self.name}:\n{fields}"


@dataclasses.dataclass()
class EnumVal:
    """ Enum element.

     `value: ValAuto` means previous value + 1"""
    ALIAS = "entry"
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    name: str
    value: Union["ValNum", "Auto"]

    def __str__(self):
        return f"{self.name}: {self.value}"


ITEMS_NODES = Union[Comment, EnumVal]


@dataclasses.dataclass()
class DefEnum:
    """Enum definition (only allowed at top-level)"""
    ALIAS = "enum"
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    base_type_kind: BASE_TYPE_KIND   # must be integer
    items: List[ITEMS_NODES]

    def __str__(self):
        items = '\n'.join(str(s) for s in self.items)
        return f"ENUM {self.name}:\n{items}"


@dataclasses.dataclass()
class DefType:
    """Type definition (only allowed at top-level)

    """
    ALIAS = "type"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.GLOBAL_SYM_DEF

    pub:  bool
    wrapped: bool
    name: str
    type: TypeNode

    def __str__(self):
        return f"TYPE {self.name} = {self.type}"


CONST_NODE = Union[Id, ValFalse, ValTrue, ValNum,
                   ValVoid, ValRec, ValArray, ValArrayString]


@dataclasses.dataclass()
class DefConst:
    """Constant definition (only allowed at top-level)"""
    ALIAS = "const"
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    type_or_auto: Union[TypeNode, Auto]
    value: CONST_NODE

    def __str__(self):
        return f"CONST {self.name}: {self.type_or_auto} = {self.value}"


@dataclasses.dataclass()
class DefVar:
    """Variable definition (at module level and inside functions)


    public visibily only makes sense for module level definitions.
    """
    ALIAS = "let"
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF | NF.GLOBAL_SYM_DEF

    pub: bool
    mut: bool
    name: str
    type_or_auto: Union[TypeNode, Auto]
    initial_or_undef: ExprNode

    def __str__(self):
        return f"LET {self.name}: {self.type_or_auto} = {self.initial_or_undef}"


@dataclasses.dataclass()
class DefFun:
    """Function definition (only allowed at top-level)"""
    ALIAS = "fun"
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.NEW_SCOPE

    init: bool
    fini: bool
    pub: bool
    extern: bool
    name: str
    params: List[PARAMS_NODES]
    result: TypeNode
    body: List[BODY_NODES]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        params = ', '.join(str(p) for p in self.params)
        return f"FUN {self.name} [{params}]->{self.result}:\n{body}"


@enum.unique
class MOD_PARAM_KIND(enum.Enum):
    INVALID = 0
    CONST = 1
    MOD = 2
    TYPE = 3


@dataclasses.dataclass()
class ModParam:
    """Module Parameters"""
    ALIAS = "None"
    FLAGS = NF.GLOBAL_SYM_DEF

    name: str
    mod_param_kind: MOD_PARAM_KIND

    def __str__(self):
        return f"{self.name}: {self.mod_param_kind.name}"


BODY_MOD_NODES = Union[Comment, DefFun, DefRec, DefConst, DefEnum, DefVar]

PARAMS_MOD_NODES = Union[Comment, ModParam]


@dataclasses.dataclass()
class DefMod:
    """Module Definition

    The module is a template if `params` is non-empty"""
    ALIAS = "mod"
    FLAGS = NF.GLOBAL_SYM_DEF

    pub: bool
    name: str
    params_mod: List[PARAMS_MOD_NODES]
    body_mod: List[BODY_MOD_NODES]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body_mod)
        params = ', '.join(str(p) for p in self.params_mod)
        return f"MOD {self.name} [{params}]:\n{body}"


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
    NFD(NFK.STR, "string", "string literal"),
    NFD(NFK.STR, "comment", "comment"),
    NFD(NFK.STR, "message", "message for assert failures"),
    NFD(NFK.STR, "field", "record field"),
    NFD(NFK.STR, "label", "block  name (if not empty)"),
    NFD(NFK.STR, "target",
        "name of enclosing while/for/block to brach to (empty means nearest)"),
    NFD(NFK.STR, "index", "initializer index or empty"),
    NFD(NFK.STR, "path", "TBD"),
    #
    NFD(NFK.FLAG, "pub", "has public visibility"),
    NFD(NFK.FLAG, "extern", "is external function (empty body)"),
    NFD(NFK.FLAG, "mut", "is mutable"),
    NFD(NFK.FLAG, "wrapped", "is wrapped type (forces type equivalence by name)"),
    NFD(NFK.FLAG, "discard", "ignore non-void expression"),
    NFD(NFK.FLAG, "init", "run function at startup"),
    NFD(NFK.FLAG, "fini", "run function at shutdown"),
    NFD(NFK.FLAG, "raw", "ignore escape sequences in string"),
    #
    NFD(NFK.KIND, "unary_expr_kind", "TBD", UNARY_EXPR_KIND),
    NFD(NFK.KIND, "binary_expr_kind", "TBD", BINARY_EXPR_KIND),
    NFD(NFK.KIND, "base_type_kind", "TBD", BASE_TYPE_KIND),
    NFD(NFK.KIND, "mod_param_kind", "TBD",  MOD_PARAM_KIND),
    NFD(NFK.KIND, "assignment_kind", "TBD", ASSIGNMENT_KIND),
    #
    NFD(NFK.LIST, "params", "function parameters and/or comments", PARAMS_NODES),
    NFD(NFK.LIST, "params_mod", "module template parameters", PARAMS_MOD_NODES),
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
    NFD(NFK.LIST, "body_t", "statement list and/or comments", BODY_NODES),
    NFD(NFK.LIST, "body_f", "statement list and/or comments", BODY_NODES),
    #
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
    NFD(NFK.NODE, "range", "range expression"),
    NFD(NFK.NODE, "container", "array and slice"),
    NFD(NFK.NODE, "callee", "expression evaluating to the function to be called"),
    NFD(NFK.NODE, "start", "desired start of slice"),
    NFD(NFK.NODE, "begin_or_auto", "range begin: `Auto` => 0"),
    NFD(NFK.NODE, "end", "range end"),
    NFD(NFK.NODE, "step_or_auto", "range step, `Auto` => 1"),
    NFD(NFK.NODE, "width", "desired width of slice"),
    NFD(NFK.NODE, "value", ""),
    NFD(NFK.NODE, "lhs", "l-value expression"),
    NFD(NFK.NODE, "initial_or_undef",
        "initializer (must be compile-time constant)"),
]

ALL_FIELDS_MAP: Dict[str, NFD] = {nfd.name: nfd for nfd in ALL_FIELDS}

# must come last in a dataclass
OPTIONAL_FIELDS = {
    "expr_ret":  ValVoid(),
    "width":  Auto(),
    "start":   Auto(),
    "begin_or_auto":   Auto(),
    "step_or_auto":   Auto(),
    "target": "",
    "path": "",
    "index": "",
}

# Note: we rely on the matching being done greedily
_TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
_TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
_TOKEN_OP = r'[\[\]\(\)]'
_TOKENS_ALL = re.compile("|".join(["(?:" + x + ")" for x in [
    _TOKEN_STR, _TOKEN_OP, _TOKEN_NAMENUM]]))

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


TYPED_ANNOTATED_NODES = tuple(
    n for n in ALL_NODES if NF.TYPE_ANNOTATED in n.FLAGS)

TYPE_CORPUS_NODES = tuple(n for n in ALL_NODES if NF.TYPE_CORPUS in n.FLAGS)

LOCAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.LOCAL_SYM_DEF in n.FLAGS)

GLOBAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.GLOBAL_SYM_DEF in n.FLAGS)

SCOPING_NODES = tuple(
    [n for n in ALL_NODES if NF.NEW_SCOPE in n.FLAGS])

##########################################################################################
PROLOG = """## Abstract Syntax Tree (AST) Nodes used by Cwerg

WIP 
"""


def GenerateDocumentation(fout):
    print(PROLOG, file=fout)
    nodes = sorted((node.__name__, node) for node in ALL_NODES)
    for name, cls in nodes:
        print(f"", file=fout)
        alias = ""
        if cls.ALIAS:
            alias = f" ({cls.ALIAS})"
        print(f"### {name}{alias}", file=fout)

        print(cls.__doc__,  file=fout)

        if NF.NEW_SCOPE in cls.FLAGS:
            print(f"", file=fout)
            print(f"Creates a new scope", file=fout)
        if len(cls.__annotations__):
            print(f"", file=fout)
            print("Fields:",  file=fout)

            for field, type in cls.__annotations__.items():
                nfd = ALL_FIELDS_MAP[field]
                kind = nfd.kind
                print(f"* {field} [{kind.name}]: {nfd.doc}", file=fout)


##########################################################################################
def DumpFields(node_class):
    for tag, val in node_class.__annotations__.items():
        print(f"    {tag}: {val}")


def ReadTokens(fp):
    for line in fp:
        tokens = re.findall(_TOKENS_ALL, line)
        for t in tokens:
            yield t


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

# maps "atoms" to the nodes they will be expanded to
_SHORT_HAND_NODES = {
    "auto": Auto(),
    "noret": TypeBase(BASE_TYPE_KIND.NORET),
    "bool": TypeBase(BASE_TYPE_KIND.BOOL),

    "undef": ValUndef(),
    "true": ValTrue(),
    "false": ValFalse(),
}

for t in _SCALAR_TYPES:
    name = t.name.lower()
    _SHORT_HAND_NODES[name] = TypeBase(t)


def ExpandShortHand(field, t) -> Any:
    """Expands atoms, ids, and numbers to proper nodes"""
    if field == "index":
        return int(t)
    elif field == "field":
        return t
    elif t == "void":
        if field == "type":
            return TypeBase(BASE_TYPE_KIND.VOID)
        else:
            return ValVoid()
    elif t[0] == '"':
        # TODO: r"
        return ValArrayString(False, t)

    x = _SHORT_HAND_NODES.get(t)
    if x is not None:
        assert x is not None, f"{t}"
        return x
    elif _TOKEN_ID.match(t):
        parts = t.rsplit("::", 1)
        return Id(parts[-1], "" if len(parts) == 1 else parts[0])
    elif _TOKEN_NUM.match(t):
        return ValNum(t)
    else:
        assert False, f"cannot expand short hand: {field} {t}"


def ReadPiece(field, token, stream) -> Any:
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
            return ReadSExpr(stream)
        return ExpandShortHand(field, token)
    elif nfd.kind is NFK.LIST:
        assert token == "[", f"expected list start for: {field} {token}"
        out = []
        while True:
            token = next(stream)
            if token == "]":
                break
            if token == "(":
                out.append(ReadSExpr(stream))
            else:
                out.append(ExpandShortHand(field, token))
        return out
    else:
        assert False


UNARY_SHORTCUT = {
    "!": UNARY_EXPR_KIND.NOT,
    "neg": UNARY_EXPR_KIND.NEG,
    "~": UNARY_EXPR_KIND.MINUS,
}

UNARY_SHORTCUT_INV = {v: k for k, v in UNARY_SHORTCUT.items()}


BINOP_SHORTCUT = {
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
    #
    "and": BINARY_EXPR_KIND.AND,
    "or": BINARY_EXPR_KIND.OR,
    "xor": BINARY_EXPR_KIND.XOR,
    #
    "padd": BINARY_EXPR_KIND.PADD,
    "psub": BINARY_EXPR_KIND.PSUB,
    "pdelta": BINARY_EXPR_KIND.PDELTA,
}

BINOP_BOOL = {
    BINARY_EXPR_KIND.GE,
    BINARY_EXPR_KIND.GT,
    BINARY_EXPR_KIND.LE,
    BINARY_EXPR_KIND.LT,
    BINARY_EXPR_KIND.EQ,
    BINARY_EXPR_KIND.NE,
}

BINOP_SHORTCUT_INV = {v: k for k, v in BINOP_SHORTCUT.items()}


_ASSIGNMENT_SHORTCUT = {
    #
    "+=": ASSIGNMENT_KIND.ADD,
    "-=": ASSIGNMENT_KIND.SUB,
    "*=": ASSIGNMENT_KIND.MUL,
    "/=": ASSIGNMENT_KIND.DIV,
    "%=": ASSIGNMENT_KIND.REM,
    #
    "and=": ASSIGNMENT_KIND.AND,
    "or=": ASSIGNMENT_KIND.OR,
    "xor=": ASSIGNMENT_KIND.XOR,
    #
}


def ReadRestAndMakeNode(cls, pieces: List[Any], fields: List[str], stream):
    """Read the remaining componts of an SExpr (after the tag).

    Can handle optional bools at the beginning and an optional 'tail'
    """
    token = next(stream)
    for field in fields:
        nfd = ALL_FIELDS_MAP[field]
        if token == ")":
            # we have reached the end before all the fields were processed
            # fill in default values
            assert field in OPTIONAL_FIELDS, f"unknown optional: {field}"
            pieces.append(OPTIONAL_FIELDS[field])
        elif nfd.kind is NFK.FLAG:
            if token == field:
                pieces.append(True)
                token = next(stream)
            else:
                pieces.append(False)
        else:
            pieces.append(ReadPiece(field, token, stream))
            token = next(stream)
    assert token == ")", f"while parsing {cls.__name__}  expected node-end but got {token}"
    return cls(*pieces)


def ReadSExpr(stream) -> Any:
    """The leading '(' has already been consumed"""
    tag = next(stream)
    logger.info("Readding TAG %s", tag)
    if tag in UNARY_SHORTCUT:
        return ReadRestAndMakeNode(Expr1, [UNARY_SHORTCUT[tag]],
                                   ["expr"], stream)
    elif tag in BINOP_SHORTCUT:
        return ReadRestAndMakeNode(Expr2, [BINOP_SHORTCUT[tag]],
                                   ["expr1", "expr2"], stream)
    elif tag in _ASSIGNMENT_SHORTCUT:
        return ReadRestAndMakeNode(StmtCompoundAssignment, [_ASSIGNMENT_SHORTCUT[tag]],
                                   ["lhs", "expr"], stream)
    else:
        cls = _NODES_ALIASES.get(tag)
        assert cls is not None, f"Non node: {tag}"
        fields = [f for f, _ in cls.__annotations__.items()]
        return ReadRestAndMakeNode(cls, [], fields, stream)


VALUE_NODES = (ValTrue, ValFalse, ValNum, IndexVal,
               ValUndef, ValVoid, FieldVal, ValArray,
               ValArrayString, ValRec)

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    if len(sys.argv) > 1 and sys.argv[1] == "gendoc":
        GenerateDocumentation(sys.stdout)
    else:
        stream = ReadTokens(sys.stdin)
        try:
            while True:
                t = next(stream)
                assert t == "("
                sexpr = ReadSExpr(stream)
                print(sexpr)
                print()
        except StopIteration:
            pass
