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


@dataclasses.dataclass()
class ModId:
    name: str


@enum.unique
class ID_KIND(enum.Enum):
    INVALID = 0
    VAR = 1
    CONST = 2
    FUN = 3


@dataclasses.dataclass()
class Id:
    path: List[ModId]  # first components of mod1::mod2:id
    name: str          # last component of mod1::mod2:id
    # id_kind = ID_KIND  # may be filled in later

############################################################
# TypeNode
############################################################


TypeNode = Union["Id", "TypeBase", "TypeEnum", "TypeRec",
                 "TypeSum", "TypeSlice", "TypeArray", "TypeFunSig"]


@dataclasses.dataclass()
class FunArg:
    """Function argument"""
    type: TypeNode
    name: str      # empty str means no var specified (fun proto type)


@dataclasses.dataclass()
class RecField:  #
    name: str
    type: TypeNode
    default: "ExprNode"    # must be const


@dataclasses.dataclass()
class NameVal:
    """ Enum element - `value: auto` means previous value + 1"""
    name: str
    value: Union["ValNum", "ValAuto"]


@enum.unique
class BASE_TYPE_KIND(enum.Enum):
    INVALID = 0

    S8 = 10
    S16 = 11
    S32 = 12
    S64 = 13

    U8 = 20
    U16 = 21
    U32 = 22
    U64 = 23

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
    type: TypeNode
    mutable: bool


@dataclasses.dataclass()
class TypeSlice:
    type: TypeNode
    mutable: bool


@dataclasses.dataclass()
class TypeArray:
    size: int      # must be const and unsigned
    type: TypeNode


@dataclasses.dataclass()
class TypeFunSig:
    params: List[FunArg]
    result: TypeNode


############################################################
# TypeMod
############################################################

@enum.unique
class MOD_TYPE_KIND(enum.Enum):
    INVALID = 0
    CONST = 1
    MOD = 2
    TYPE = 3


@dataclasses.dataclass()
class VarTypeMod:
    name: str
    mod_type_kind: MOD_TYPE_KIND
    type: Optional[TypeNode]     # if mod_type_kind == TYPE


@dataclasses.dataclass()
class TypeMod:
    params: List[VarTypeMod]


############################################################
# ExprNode (inlcudes const)
############################################################

ExprLHS = Union["Id", "ExprDeref", "ExprIndex", "ExprField",
                "ExprCall"]


ExprNode = Union["Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                 "ExprField", "ExprCall", "ExprParen",
                 "Expr1", "Expr2", "Expr3",
                 "ExprUnwrap",
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
    PLUS = 1
    MINUS = 2
    DIV = 3
    MUL = 4
    MOD = 5

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

    RSH = 40    # >>
    LSH = 41    # <<


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
class ExprSlice:
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


############################################################
# Val (includes const)
############################################################
Val = Union["ValBool", "ValNum", "ValUndef",
            "ValVoid", "ValArray", "ValArrayString",
            "ValRec"]


@dataclasses.dataclass()
class ValBool:
    value: bool


@dataclasses.dataclass()
class ValNum:
    number: str   # maybe a (unicode) character as well
    base_type_kind: BASE_TYPE_KIND


class ValAuto:  # placeholder for unspecified val
    pass


@dataclasses.dataclass()
class ValUndef:
    base_type_kind: BASE_TYPE_KIND


@dataclasses.dataclass()
class ValVoid:
    name: string  # void or wrapped void


@dataclasses.dataclass()
class IndexVal:   # for array initialization {.1 = 5, .2 = 6}
    index: str
    value: Val


@dataclasses.dataclass()
class FieldVal:   # for rec initialization {.imag = 5, .real = 1}
    index: str
    value: Val


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
# Stmt
############################################################
StmtNode = Union["StmtWhile", "StmtDefer", "StmtIf", "StmtBreak",
                 "StmtContinue", "StmtReturn", "StmtExpr", "StmtAssert"]


@dataclasses.dataclass()
class StmtWhile:
    cond: ExprNode       # must be of type bool
    body: List[StmtNode]


@dataclasses.dataclass()
class StmtFor:
    name: str
    base_type_kind: BASE_TYPE_KIND
    end: ExprNode   # start, end ,step work like range(start, end, step)
    start: Union["ValAuto", ExprNode]
    step: Union["ValAuto", ExprNode]


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
    pass


@dataclasses.dataclass()
class StmtContinue:
    pass


@dataclasses.dataclass()
class StmtReturn:
    expr: ExprNode  # use void for no value


@dataclasses.dataclass()
class StmtExpr:
    expr: ExprCall
    discard: bool


@dataclasses.dataclass()
class StmtAssert:
    cond: ExprNode  # must be of type bool
    string: str


@dataclasses.dataclass()
class StmtAssignment:
    lhs: ExprLHS
    expr: ExprNode

############################################################
#
############################################################


@dataclasses.dataclass()
class DefType:
    """Type Definition"""
    name: str
    type: TypeNode
    public:  bool
    wrapped: bool

@dataclasses.dataclass()
class DefConst:
    """Const Definition"""
    name: str
    value: Val
    public:  bool

@dataclasses.dataclass()
class DefFun:
    """Function Definition"""
    name: str
    public: bool
    type: TypeNode
    body: List[StmtNode]

# @dataclasses.dataclass()
# class Mod:
#    mod_param: List[ModParam]
#    body: List[TopLevelItems]


############################################################
# S-Expression Serialization (Introspection driven)
############################################################
# Partitioning of all the field names in the node classes above
# Terminal fields do NOT contain other node instances
_TERMINAL_BOOL = {"public", "mutable", "wrapped", "discard"}
_TERMINAL_INT = {"size", "number"}
_TERMINAL_STR = {"name", "string", "field"}
_TERMINAL_FIELDS = _TERMINAL_BOOL | _TERMINAL_INT | _TERMINAL_STR

# terminal field containing an enum ampped to the enum class
_KIND_FIELDS = {
    "unary_expr_kind": UNARY_EXPR_KIND,
    "binary_expr_kind": BINARY_EXPR_KIND,
    "base_type_kind": BASE_TYPE_KIND,
    "mod_type_kind": MOD_TYPE_KIND,
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
                "container",
                "callee", "index", "length", "start", "end", "step",
                "value", "lhs", "rhs", "default"}


# Note: we rely on the matching being done greedily
TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
TOKEN_OP = r'[\[\]\(\)]'
RE_COMBINED = re.compile("|".join(["(?:" + x + ")" for x in [
    TOKEN_STR, TOKEN_OP, TOKEN_NAMENUM]]))

TOKEN_ID = re.compile(r'[_A-Za-z$][_A-Za-z$0-9]*(::[_A-Za-z$][_A-Za-z$0-9])*')
TOKEN_NUM = re.compile(r'[.0-9][_.a-z0-9]')

# maps node class name to class
_NODES = {
    "#": Comment,
    "return": StmtReturn,
    "if": StmtIf,
    "type": DefType,
    "fun": DefFun,
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
        tokens = re.findall(RE_COMBINED, line)
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
    elif TOKEN_ID.match(t):
        parts = t.split("::")
        return Id(parts[:-1], parts[-1])
    elif TOKEN_NUM.match(t):
        return ValNum(t, BASE_TYPE_KIND.AUTO)
    else:
        assert False, f"cannot expand short hand: {field} {t}"


def ReadPiece(field, stream) -> Any:
    t = next(stream)
    if field in _TERMINAL_FIELDS:
        if field in _TERMINAL_BOOL:
            return bool(t)
        return t
    elif field in _KIND_FIELDS:
        enum = _KIND_FIELDS.get(field)
        assert enum is not None, f"{field} {t}"
        return enum[t]
    elif field in _NODE_FIELDS:
        if t == "(":
            return ReadSExpr(stream)
        return ExpandShortHand(field, t)
    elif field in _LIST_FIELDS:
        assert t == "[", f"expected list start for: {field} {t}"
        out = []
        while True:
            t = next(stream)
            if t == "]":
                break
            if t == "(":
                out.append(ReadSExpr(stream))
            else:
                out.append(ExpandShortHand(field, t))
        return out
    else:
        assert False


_BINOP_SHORTCUT = {
    "<=": BINARY_EXPR_KIND.LE,
    "<": BINARY_EXPR_KIND.LT,
    "==": BINARY_EXPR_KIND.EQ,
    "!=": BINARY_EXPR_KIND.NE,
    #
    "+": BINARY_EXPR_KIND.PLUS,
    "-": BINARY_EXPR_KIND.MINUS,

}


def ReadSExpr(stream) -> Any:
    """The leading '(' has already been consumed"""
    tag = next(stream)
    print("@@ TAG", tag)
    if tag in _BINOP_SHORTCUT:
        op1 = ReadPiece("expr1", stream)
        print()
        op2 = ReadPiece("expr2", stream)
        t = next(stream)
        assert t == ")", f"{pieces}  {t}"
        return Expr2(_BINOP_SHORTCUT[tag], op1, op2)
    else:
        cls = _NODES.get(tag)
        assert cls is not None, f"Non node: {tag}"
        pieces = []
        for field, _ in cls.__annotations__.items():
            pieces.append(ReadPiece(field, stream))
        t = next(stream)
        assert t == ")", f"{pieces}  {t}"
        return cls(*pieces)


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
