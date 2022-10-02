#!/usr/bin/python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend


"""

import sys
import re
import inspect
import dataclasses
import collections
import enum
import string
from typing import List, Dict, Set, Optional, Union, Any


############################################################
# Comment
############################################################


@dataclasses.dataclass()
class Comment:
    string: str

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
    path: List[str]  # first components of mod1::mod2:id
    name: str          # last component of mod1::mod2:id
    # id_kind = ID_KIND  # may be filled in later

############################################################
# TypeNode
############################################################


TypeNode = Union["Id", "TypeBase", "TypeEnum", "TypeRec",
                 "TypeSum", "TypeSlice", "TypeArray", "TypeFunSig"]


@dataclasses.dataclass()
class FunParam:
    """Function argument"""
    name: str      # empty str means no var specified (fun proto type)
    type: TypeNode


@dataclasses.dataclass()
class RecField:  #
    name: str
    type: TypeNode
    initial: "ExprNode"    # must be const


@dataclasses.dataclass()
class NameVal:
    """ Enum element - `value: auto` means previous value + 1"""
    name: str
    value: Union["ValNum", "ValAuto"]


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

    F32 = 30
    F64 = 31

    VOID = 40
    AUTO = 41
    NORET = 42
    BOOL = 43


@dataclasses.dataclass()
class TypeBase:
    base_type_kind: BASE_TYPE_KIND


@dataclasses.dataclass()
class TypeRec:
    fields: List[Union[RecField, Comment]]


@dataclasses.dataclass()
class TypeEnum:
    base_type_kind: BASE_TYPE_KIND
    items:  List[Union[NameVal, Comment]]


@dataclasses.dataclass()
class TypeSum:
    types: List[Union[TypeNode, Comment]]


@dataclasses.dataclass()
class TypePtr:
    mut: bool   # pointee is mutable
    type: TypeNode


@dataclasses.dataclass()
class TypeSlice:
    mut: bool  # slice is mutable
    type: TypeNode


@dataclasses.dataclass()
class TypeArray:
    size: int      # must be const and unsigned
    type: TypeNode


@dataclasses.dataclass()
class TypeFunSig:
    params: List[FunParam]
    result: TypeNode


############################################################
# Val (includes const)
############################################################
ValNode = Union["ValBool", "ValNum", "ValUndef",
                "ValVoid", "ValArray", "ValArrayString",
                "ValRec"]


@dataclasses.dataclass()
class ValBool:
    value: bool


@dataclasses.dataclass()
class ValNum:
    number: str   # maybe a (unicode) character as well
    base_type_kind: BASE_TYPE_KIND


class ValAuto:  # placeholder for unspecified val (note: not in ValNode)
    pass


@dataclasses.dataclass()
class ValUndef:
    base_type_kind: BASE_TYPE_KIND


@dataclasses.dataclass()
class ValVoid:
    pass


@dataclasses.dataclass()
class IndexVal:   # for array initialization {.1 = 5, .2 = 6}
    index: str
    value: ValNode


@dataclasses.dataclass()
class FieldVal:   # for rec initialization {.imag = 5, .real = 1}
    index: str
    value: ValNode


@dataclasses.dataclass()
class ValArray:
    type: TypeNode
    size: Union[ValNum, ValAuto]
    values: List[IndexVal]


@dataclasses.dataclass()
class ValArrayString:
    # type: u8, size: strlen(value)
    value: str


@dataclasses.dataclass()
class ValRec:
    type: TypeNode
    values: List[Union[FieldVal, Comment]]

############################################################
# ExprNode
############################################################


ExprLHS = Union["Id", "ExprDeref", "ExprIndex", "ExprField",
                "ExprCall"]


ExprNode = Union[ValNode, "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                 "ExprField", "ExprCall", "ExprParen",
                 "Expr1", "Expr2", "Expr3",
                 "ExprUnwrap", "ExprChop",
                 "ExprLen", "ExprSizeof"]


@dataclasses.dataclass()
class ExprDeref:
    expr: ExprNode  # must be of type AddrOf


@dataclasses.dataclass()
class ExprAddrOf:
    expr: ExprNode


@dataclasses.dataclass()
class ExprCall:
    callee: ExprNode  # must of type fun
    args: List[ExprNode]


@dataclasses.dataclass()
class ExprParen:      # used for preserving parenthesis in the source
    expr: ExprNode


@dataclasses.dataclass()
class ExprField:
    container: ExprNode  # must be of type rec
    field: str


@dataclasses.dataclass()
class Expr1:
    cond: ExprNode  # must be of type  bool
    expr_t: ExprNode
    expr_f: ExprNode


@enum.unique
class UNARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    NOT = '!'
    MINUS = '-'
    NEG = '~'


@dataclasses.dataclass()
class Expr1:
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

    ANDSC = 30  # &&
    ORSC = 31   # ||

    SHR = 40    # >>
    SHL = 41    # <<


@dataclasses.dataclass()
class Expr2:
    binary_expr_kind: BINARY_EXPR_KIND
    expr1: ExprNode
    expr2: ExprNode


@dataclasses.dataclass()
class Expr3:
    cond: ExprNode  # must be of type  bool
    expr_t: ExprNode
    expr_f: ExprNode


# Array/Slice Expressions


@dataclasses.dataclass()
class ExprIndex:
    container: ExprNode  # must be of type slice or array
    index: ExprNode  # must be of int type


@dataclasses.dataclass()
class ExprChop:
    container: ExprNode  # must be of type slice or array
    start: Union[ExprNode, "ValAuto"]  # must be of int type
    length: Union[ExprNode, "ValAuto"]  # must be of int type


@dataclasses.dataclass()
class ExprLen:
    container: ExprNode   # must be of type slice or array


# Cast Like Expressions

@dataclasses.dataclass()
class ExprUnwrap:  # converts from wrapped/enum type to underlying type
    expr: ExprNode


class ExprCastAs:  # number <-> number, number -> enum,  val -> wrapped val
    type: TypeNode
    expr: ExprNode


class ExprBitCastAs:  # type must have saame size as type of item
    type: TypeNode
    expr: ExprNode


# Const Expression

@dataclasses.dataclass()
class ExprSizeof:
    expr: TypeNode


@dataclasses.dataclass()
class ExprOffsetof:
    type: TypeNode  # must be rec
    field: str


@dataclasses.dataclass()
class ExprRange:
    end: ExprNode   # start, end ,step work like range(start, end, step)
    start: Union["ValAuto", ExprNode]
    step: Union["ValAuto", ExprNode]


############################################################
# Stmt
############################################################
StmtNode = Union["StmtWhile", "StmtDefer", "StmtIf", "StmtBreak",
                 "StmtContinue", "StmtReturn", "StmtExpr", "StmtAssert",
                 "StmtBlock"]


@dataclasses.dataclass()
class StmtWhile:
    cond: ExprNode       # must be of type bool
    body: List[StmtNode]


@dataclasses.dataclass()
class StmtBlock:
    label: str
    body: List[StmtNode]


@dataclasses.dataclass()
class StmtFor:
    name: str
    type: TypeNode
    range: ExprRange
    body: List[StmtNode]

@dataclasses.dataclass()
class StmtDefer:
    body: List[StmtNode]  # must NOT contain RETURN


@dataclasses.dataclass()
class StmtIf:
    cond: ExprNode        # must be of type bool
    body_t: List[StmtNode]
    body_f: List[StmtNode]


@dataclasses.dataclass()
class StmtBreak:
    target: str  # use "" for no value


@dataclasses.dataclass()
class StmtContinue:
    target: str  # use "" for no value


@dataclasses.dataclass()
class StmtReturn:
    expr_ret: ExprNode  # use void for no value


@dataclasses.dataclass()
class StmtExpr:
    discard: bool
    expr: ExprCall


@dataclasses.dataclass()
class StmtAssert:
    cond: ExprNode  # must be of type bool
    string: str


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
class StmtAssignment2:
    assignment_kind: ASSIGNMENT_KIND
    lhs: ExprLHS
    expr: ExprNode


@dataclasses.dataclass()
class StmtAssignment:
    assignment_kind: ASSIGNMENT_KIND
    lhs: ExprLHS
    expr: ExprNode

############################################################
# Definitions
############################################################


@dataclasses.dataclass()
class DefType:
    """Type Definition"""
    pub:  bool
    wrapped: bool
    name: str
    type: TypeNode


@dataclasses.dataclass()
class DefConst:
    """Const Definition"""
    name: str
    value: ValNode
    pub:  bool


@dataclasses.dataclass()
class DefVar:
    """Function Definition"""
    pub: bool
    mut: bool
    name: str
    type: TypeNode
    initial: ExprNode


@dataclasses.dataclass()
class DefFun:
    """Function Definition"""
    pub: bool
    extern: bool
    name: str
    type: TypeNode
    body: List[StmtNode]


@enum.unique
class MOD_PARAM_KIND(enum.Enum):
    INVALID = 0
    CONST = 1
    MOD = 2
    TYPE = 3


@dataclasses.dataclass()
class ModParam:
    """Module argument"""
    name: str
    mod_param_kind: MOD_PARAM_KIND


@dataclasses.dataclass()
class DefMod:
    """Module Definition"""
    pub: bool
    name: str
    params: List[ModParam]
    body: List[StmtNode]


############################################################
# S-Expression Serialization (Introspection driven)
############################################################
# Partitioning of all the field names in the node classes above
# Terminal fields do NOT contain other node instances
_TERMINAL_INT = {"size", "number"}
_TERMINAL_STR = {"name", "string", "field", "label", "target"}
# BOOLs are optional and must come first
_TERMINAL_BOOL = {"pub", "extern", "mut", "wrapped", "discard"}
_TERMINAL_FIELDS = _TERMINAL_BOOL | _TERMINAL_INT | _TERMINAL_STR

# terminal field containing an enum ampped to the enum class
_KIND_FIELDS = {
    "unary_expr_kind": UNARY_EXPR_KIND,
    "binary_expr_kind": BINARY_EXPR_KIND,
    "base_type_kind": BASE_TYPE_KIND,
    "mod_param_kind": MOD_PARAM_KIND,
    "assignment_kind": ASSIGNMENT_KIND,
}

# contain list of nodes
_LIST_FIELDS = {"params", "args", "path", "items", "fields", "types",
                "values",
                #
                "body", "body_t", "body_f"}

# contain one nodes
_NODE_FIELDS = {"type", "result",
                # expr
                "expr", "cond", "expr_t", "expr_f", "expr1", "expr2",
                "expr_ret",  "range",
                "container",
                "callee", "index", "length", "start", "end", "step",
                "value", "lhs", "rhs", "initial"}


# must come last
_OPTIONAL_FIELDS = {
    "expr_ret":  ValVoid(),
    "start":   ValAuto(),
    "step":   ValAuto(),
    "target": "",
    "result": TypeBase(BASE_TYPE_KIND.VOID)
}

# Note: we rely on the matching being done greedily
_TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
_TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
_TOKEN_OP = r'[\[\]\(\)]'
_TOKENS_ALL = re.compile("|".join(["(?:" + x + ")" for x in [
    _TOKEN_STR, _TOKEN_OP, _TOKEN_NAMENUM]]))

_TOKEN_ID = re.compile(r'[_A-Za-z$][_A-Za-z$0-9]*(::[_A-Za-z$][_A-Za-z$0-9])*')
_TOKEN_NUM = re.compile(r'[.0-9][_.a-z0-9]*')

# maps node class name to class
_NODES = {
    "#": Comment,
    "^": ExprDeref,
    "&": ExprAddrOf,
    ".": ExprField,
    "at": ExprIndex,
    "range": ExprRange,
    #
    "=": StmtAssignment,
    "return": StmtReturn,
    "continue": StmtContinue,
    "break": StmtBreak,
    "if": StmtIf,
    "for": StmtFor,
    "block": StmtBlock,
    #
    "field": RecField,
    "ptr": TypePtr,
    "param": FunParam,
    "type": DefType,
    "sig": TypeFunSig,
    #
    "fun": DefFun,

    "mod":  DefMod,
    "let": DefVar,
}


for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        if obj.__base__ is object:
            _NODES[obj.__name__] = obj
            for field, type in obj.__annotations__.items():
                if field in _TERMINAL_FIELDS:
                    pass
                elif field in _KIND_FIELDS:
                    pass
                elif field in _NODE_FIELDS:
                    pass
                elif field in _LIST_FIELDS:
                    pass
                else:
                    assert False, f"unexpected field {obj.__name__} {field}"


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
    BASE_TYPE_KIND.S8,
    BASE_TYPE_KIND.S16,
    BASE_TYPE_KIND.S32,
    BASE_TYPE_KIND.S64,
    #
    BASE_TYPE_KIND.U8,
    BASE_TYPE_KIND.U16,
    BASE_TYPE_KIND.U32,
    BASE_TYPE_KIND.U64,
    #
    BASE_TYPE_KIND.F32,
    BASE_TYPE_KIND.F64,
]

_SHORT_HAND_NODES = {
    "void": TypeBase(BASE_TYPE_KIND.VOID),
    "auto": TypeBase(BASE_TYPE_KIND.AUTO),
    "noret": TypeBase(BASE_TYPE_KIND.NORET),
    "bool": TypeBase(BASE_TYPE_KIND.BOOL),

    "undef": ValUndef(BASE_TYPE_KIND.AUTO),
    "false": ValBool(False),
    "true": ValBool(True),
}

for t in _SCALAR_TYPES:
    name = t.name.lower()
    _SHORT_HAND_NODES[name] = TypeBase(t)
    _SHORT_HAND_NODES[f"undef_{name}"] = ValUndef(t)


def ExpandShortHand(field, t) -> Any:
    x = _SHORT_HAND_NODES.get(t)
    if x is not None:
        assert x is not None, f"{t}"
        return x
    elif _TOKEN_ID.match(t):
        parts = t.split("::")
        return Id(parts[:-1], parts[-1])
    elif _TOKEN_NUM.match(t):
        return ValNum(t, BASE_TYPE_KIND.AUTO)
    else:
        assert False, f"cannot expand short hand: {field} {t}"


def ReadPiece(field, token, stream) -> Any:
    if field in _TERMINAL_FIELDS:
        if field in _TERMINAL_BOOL:
            return bool(token)
        return token
    elif field in _KIND_FIELDS:
        enum = _KIND_FIELDS.get(field)
        assert enum is not None, f"{field} {token}"
        return enum[token]
    elif field in _NODE_FIELDS:
        if token == "(":
            return ReadSExpr(stream)
        return ExpandShortHand(field, token)
    elif field in _LIST_FIELDS:
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


_BINOP_SHORTCUT = {
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
}

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


def ReadRestAndMakeNode(cls, pieces: List[Any], fields: List[str]):
    token = next(stream)
    for field in fields:
        if token == ")":
            assert field in _OPTIONAL_FIELDS, f"unknown optional: {field}"
            pieces.append(_OPTIONAL_FIELDS[field])
        elif field in _TERMINAL_BOOL:
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
    print("@@ TAG", tag)
    if tag in _BINOP_SHORTCUT:
        return ReadRestAndMakeNode(Expr2, [_BINOP_SHORTCUT[tag]],
                                   ["expr1", "expr2"])
    else:
        cls = _NODES.get(tag)
        assert cls is not None, f"Non node: {tag}"
        fields = [f for f, _ in cls.__annotations__.items()]
        return ReadRestAndMakeNode(cls, [], fields)


if __name__ == "__main__":
    stream = ReadTokens(sys.stdin)
    try:
        while True:
            t = next(stream)
            assert t == "("
            print(ReadSExpr(stream))
            print()
    except StopIteration:
        pass
