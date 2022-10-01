#!/usr/bin/python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend

Highlights

* Comments are nodes and cannot occur in arbitrary places
* wrapped types
* variables are non-mutable by default
* pointees are non-mutable by default
* sum type with emphasis on error and optional handling
* init/fini function order defined by module dependencies
* templated module system
* visibilty identifier is non-public by default
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
# TypeNode
############################################################


TypeNode = Union["TypeId", "TypeBase", "TypeEnum", "TypeRec",
                 "TypeSum", "TypeSlice", "TypeArray", "TypeFunSig"]


@dataclasses.dataclass()
class FunArg:
    type: TypeNode
    name: str      # empty str means no var specified (fun proto type)


@dataclasses.dataclass()
class VarTypeDef:  #
    name: str
    type: TypeNode
    default: "ExprNode"    # must be const


@dataclasses.dataclass()
class NameVal:    # for enum elemenets
    name: str
    value: Optional[str]  # TODO: wrong


@dataclasses.dataclass()
class TypeId:
    name: str


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
    fields: List[Union[VarTypeDef, Comment]]


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
class DefType:
    name: str
    public:  bool
    wrapped: bool
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
    expr: ExprNode


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
    values: List[FieldVal]

############################################################
# StmtNode
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
class FunDef:
    name: str
    type: TypeNode
    body: List[StmtNode]

# @dataclasses.dataclass()
# class Mod:
#    mod_param: List[ModParam]
#    body: List[TopLevelItems]


# Partitioning of all the field names in the nodes above
TERMINAL_FIELDS = {"name", "string", "field",
                   # int
                   "size", "number",
                   # bools
                   "public", "mutable", "wrapped", "discard"}

LIST_FIELDS = {"params", "args", "path", "items", "fields", "types",
               "values",
               #
               "body", "body_t", "body_f"}

NODE_FIELDS = {"type", "result",
               # expr
               "expr", "cond", "expr_t", "expr_f", "container",
               "callee", "index", "length", "start", "end", "step",
               "value", "lhs", "rhs", "default"}

KIND_FIELDS = {"unary_expr_kind", "binary_expr_kind", "base_type_kind",
               "mod_type_kind"}

# Note: we rely on the matching being done greedily
TOKEN_STR = r'["][^\\"]*(?:[\\].[^\\"]*)*(?:["]|$)'
TOKEN_NAMENUM = r'[^\[\]\(\)\' \r\n\t]+'
TOKEN_OP = r'[\[\]\(\)]'
RE_COMBINED = re.compile("|".join(["(?:" + x + ")" for x in [
    TOKEN_STR, TOKEN_OP, TOKEN_NAMENUM]]))


NODES = {}
ENUMS = set()


for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        if obj.__base__ is object:
            NODES[obj.__name__] = obj
            for field, type in obj.__annotations__.items():
                if field in TERMINAL_FIELDS:
                    pass
                elif field in KIND_FIELDS:
                    pass
                elif field in NODE_FIELDS:
                    pass
                elif field in LIST_FIELDS:
                    pass
                else:
                    assert False, f"unexpected field {obj.__name__} {field}"
        elif obj.__base__ is enum.Enum:
            ENUMS.add(obj)


def DumpFields(node_class):
    for tag, val in node_class.__annotations__.items():
        print(f"    {tag}: {val}")


def ReadTokens(fp):
    for line in fp:
        tokens = re.findall(RE_COMBINED, line)
        for t in tokens:
            yield t


SHORT_HAND_NODES = {
    "s8": TypeBase(BASE_TYPE_KIND.S8),
    "s16": TypeBase(BASE_TYPE_KIND.S16),
    "s32": TypeBase(BASE_TYPE_KIND.S32),
    "s64": TypeBase(BASE_TYPE_KIND.S64),

    "u8": TypeBase(BASE_TYPE_KIND.U8),
    "u16":  TypeBase(BASE_TYPE_KIND.U16),
    "u32":  TypeBase(BASE_TYPE_KIND.U32),
    "u64":  TypeBase(BASE_TYPE_KIND.U64),

    "f32": TypeBase(BASE_TYPE_KIND.F32),
    "f64": TypeBase(BASE_TYPE_KIND.F64),

    "void": TypeBase(BASE_TYPE_KIND.VOID),
    "auto": TypeBase(BASE_TYPE_KIND.AUTO),
    "noret": TypeBase(BASE_TYPE_KIND.NORET),
    "bool": TypeBase(BASE_TYPE_KIND.BOOL),
}


def ShortHandExpr(field, field_type, t) -> Any:
    x = SHORT_HAND_NODES.get(t)
    assert x is not None, f"{t}"
    return x


def ReadPiece(field, field_type, stream) -> Any:
    t = next(stream)
    if field in TERMINAL_FIELDS:
        return t
    elif field in KIND_FIELDS:
        return t
    elif field in NODE_FIELDS:
        if t == "(":
            return ReadSExpr(stream)
        return ShortHandExpr(field, field_type, t)
    elif field in LIST_FIELDS:
        assert t == "["
        out = []
        while True:
            t = next(stream)
            if t == "]":
                break
            assert t == "("
            out.append(ReadSExpr(stream))
        return out
    else:
        assert False


def ReadSExpr(stream) -> Any:
    """The leading '(' has already been consumed"""
    tag = next(stream)
    cls = NODES.get(tag)
    print("@@ TAG", tag)
    assert cls is not None
    pieces = []
    for field, field_type in cls.__annotations__.items():
        pieces.append(ReadPiece(field, field_type, stream))
    t = next(stream)
    assert t == ")", f"{pieces}  {t}"
    return cls(*pieces)


if __name__ == "__main__":
    stream = ReadTokens(sys.stdin)
    t = next(stream)
    assert t == "("
    print(ReadSExpr(stream))
