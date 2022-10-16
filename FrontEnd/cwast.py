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
    NEW_SCOPE = 1
    TYPE_ANNOTATED = 2
    TYPE_CORPUS = 3
    CONTROL_FLOW = 4
    GLOBAL_SYM_DEF = 5
    LOCAL_SYM_DEF = 6

############################################################
# Comment
############################################################


@dataclasses.dataclass()
class Comment:
    ALIAS = "#"
    FLAGS = NF.NONE

    string: str

    def __str__(self):
        return "# " + self.string

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
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED
    path: List[str]  # first components of mod1::mod2:id
    name: str          # last component of mod1::mod2:id
    # id_kind = ID_KIND  # may be filled in later

    def __str__(self):
        path = '/'.join(self.path) + "/" if self.path else ""
        return f"{path}{self.name}"


class Auto:
    """placeholder for an unspecified value or type

    Note: it is not part of the ValNode Union or TypeUnion"""
    ALIAS = None
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
    """Function argument"""
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
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    base_type_kind: BASE_TYPE_KIND

    def __str__(self):
        return self.base_type_kind.name


@dataclasses.dataclass()
class TypeSum:
    ALIAS = "|"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    types: List[Union[TypeNode, Comment]]


@dataclasses.dataclass()
class TypePtr:
    ALIAS = "ptr"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    mut: bool   # pointee is mutable
    type: TypeNode

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"PTR{mod}({self.type})"


@dataclasses.dataclass()
class TypeSlice:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    mut: bool  # slice is mutable
    type: TypeNode


@dataclasses.dataclass()
class TypeArray:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    size: "ExprNode"      # must be const and unsigned
    type: TypeNode


@dataclasses.dataclass()
class TypeFun:
    ALIAS = "sig"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS

    params: List[FunParam]
    result: TypeNode


############################################################
# Val Nodes
############################################################
ValNode = Union["ValFalse", "ValTrue", "ValNum", "ValUndef",
                "ValVoid", "ValArray", "ValArrayString",
                "ValRec"]


@dataclasses.dataclass()
class ValTrue:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self):
        return "TRUE"


@dataclasses.dataclass()
class ValFalse:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self):
        return "FALSE"


@dataclasses.dataclass()
class ValNum:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    number: str   # maybe a (unicode) character as well

    def __str__(self): return self.number


@dataclasses.dataclass()
class ValUndef:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self): return f"UNDEF"


@dataclasses.dataclass()
class ValVoid:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    def __str__(self): return "VOID"


@dataclasses.dataclass()
class IndexVal:
    "for array initialization {.1 = 5, .2 = 6}"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    index: str
    value: "ExprNode"


@dataclasses.dataclass()
class FieldVal:
    "for rec initialization {.imag = 5, .real = 1}"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    field: str
    value: "ExprNode"


@dataclasses.dataclass()
class ValArray:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    size: Union["ExprNode", Auto]  # must be constant
    values: List[IndexVal]


@dataclasses.dataclass()
class ValArrayString:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    noesc: bool
    # type: u8, size: strlen(value)
    string: str

    def __str__(self): return f"STRING({self.string})"


@dataclasses.dataclass()
class ValRec:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    values: List[Union[FieldVal, Comment]]


############################################################
# ExprNode
############################################################
ExprNode = Union[ValNode, "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                 "ExprField", "ExprCall", "ExprParen",
                 "Expr1", "Expr2", "Expr3",
                 "ExprUnwrap", "ExprChop",
                 "ExprLen", "ExprSizeof"]


@dataclasses.dataclass()
class ExprDeref:
    ALIAS = "^"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode  # must be of type AddrOf


@dataclasses.dataclass()
class ExprAddrOf:
    ALIAS = "&"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode


@dataclasses.dataclass()
class ExprCall:
    ALIAS = "call"
    FLAGS = NF.TYPE_ANNOTATED

    callee: ExprNode  # must of type fun
    args: List[ExprNode]


@dataclasses.dataclass()
class ExprParen:
    "used for preserving parenthesis in the source"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode


@dataclasses.dataclass()
class ExprField:
    ALIAS = "."
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type rec
    field: str


@enum.unique
class UNARY_EXPR_KIND(enum.Enum):
    INVALID = 0
    NOT = '!'
    MINUS = '~'
    NEG = 'not'


@dataclasses.dataclass()
class Expr1:
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


@dataclasses.dataclass()
class Expr2:
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    binary_expr_kind: BINARY_EXPR_KIND
    expr1: ExprNode
    expr2: ExprNode

    def __str__(self):
        return f"{self.binary_expr_kind.name}({self.expr1}, {self.expr2})"


@dataclasses.dataclass()
class Expr3:
    ALIAS = "?"
    FLAGS = NF.TYPE_ANNOTATED

    cond: ExprNode  # must be of type  bool
    expr_t: ExprNode
    expr_f: ExprNode


# Array/Slice Expressions


@dataclasses.dataclass()
class ExprIndex:
    ALIAS = "at"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type slice or array
    expr_index: ExprNode  # must be of int type


@dataclasses.dataclass()
class ExprChop:
    ALIAS = "chop"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode  # must be of type slice or array
    start: Union[ExprNode, "Auto"]  # must be of int type
    width: Union[ExprNode, "Auto"]  # must be of int type


@dataclasses.dataclass()
class ExprLen:
    ALIAS = "len"
    FLAGS = NF.TYPE_ANNOTATED

    container: ExprNode   # must be of type slice or array


# Cast Like Expressions


@dataclasses.dataclass()
class ExprUnwrap:
    "converts from wrapped/enum type to underlying type"
    ALIAS = "unwrap"
    FLAGS = NF.TYPE_ANNOTATED

    expr: ExprNode


class ExprCastAs:
    "number <-> number, number -> enum,  val -> wrapped val"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    expr: ExprNode


class ExprBitCastAs:
    "type must have saame size as type of item"
    ALIAS = None
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode
    expr: ExprNode


# Const Expression


@dataclasses.dataclass()
class ExprSizeof:
    ALIAS = "sizeof"
    FLAGS = NF.TYPE_ANNOTATED

    expr: TypeNode


@dataclasses.dataclass()
class ExprOffsetof:
    ALIAS = "offsetof"
    FLAGS = NF.TYPE_ANNOTATED

    type: TypeNode  # must be rec
    field: str


@dataclasses.dataclass()
class ExprRange:
    ALIAS = "range"
    FLAGS = NF.TYPE_ANNOTATED

    end: ExprNode   # start, end ,step work like range(start, end, step)
    start: Union["Auto", ExprNode]
    step: Union["Auto", ExprNode]

    def __str__(self):
        return f"RANGE({self.end}, {self.start}, {self.step})"


############################################################
# Stmt
############################################################
StmtNode = Union["StmtWhile", "StmtDefer", "StmtIf", "StmtBreak",
                 "StmtContinue", "StmtReturn", "StmtExpr", "StmtAssert",
                 "StmtBlock"]

ExprLHS = Union["Id", "ExprDeref", "ExprIndex", "ExprField",
                "ExprCall"]


@dataclasses.dataclass()
class StmtWhile:
    ALIAS = "while"
    FLAGS = NF.NEW_SCOPE

    cond: ExprNode       # must be of type bool
    body: List[StmtNode]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"WHILE {self.cond}:\n{body}"


@dataclasses.dataclass()
class StmtBlock:
    ALIAS = "block"
    FLAGS = NF.NEW_SCOPE

    label: str
    body: List[StmtNode]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"BLOCK {self.label}:\n{body}"


@dataclasses.dataclass()
class StmtFor:
    ALIAS = "for"
    FLAGS = NF.NEW_SCOPE | NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF

    name: str
    type: TypeNode
    range: ExprNode
    body: List[StmtNode]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"FOR  {self.name}: {self.type} = {self.range}:\n{body}"


@dataclasses.dataclass()
class StmtDefer:
    ALIAS = "defer"
    FLAGS = NF.NEW_SCOPE

    body: List[StmtNode]  # must NOT contain RETURN

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        return f"DEFER:\n{body}"


@dataclasses.dataclass()
class StmtIf:
    ALIAS = "if"
    FLAGS = NF.NEW_SCOPE

    cond: ExprNode        # must be of type bool
    body_t: List[StmtNode]
    body_f: List[StmtNode]

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
    ALIAS = "break"
    FLAGS = NF.CONTROL_FLOW

    target: str  # use "" for no value

    def __str__(self):
        return f"BREAK {self.target}"


@dataclasses.dataclass()
class StmtContinue:
    ALIAS = "continue"
    FLAGS = NF.CONTROL_FLOW
    target: str  # use "" for no value

    def __str__(self):
        return f"CONTINUE {self.target}"


@dataclasses.dataclass()
class StmtReturn:
    ALIAS = "return"
    FLAGS = NF.CONTROL_FLOW
    expr_ret: ExprNode  # use void for no value

    def __str__(self):
        return f"RETURN {self.expr_ret}"


@dataclasses.dataclass()
class StmtExpr:
    ALIAS = "expr"
    FLAGS = NF.NONE

    discard: bool
    expr: ExprCall


@dataclasses.dataclass()
class StmtAssert:
    ALIAS = "assert"
    FLAGS = NF.NONE

    cond: ExprNode  # must be of type bool
    string: str     # should this be an expression?


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
    ALIAS = None
    FLAGS = NF.NONE

    assignment_kind: ASSIGNMENT_KIND
    lhs: ExprLHS
    expr: ExprNode


@dataclasses.dataclass()
class StmtAssignment:
    ALIAS = "="
    FLAGS = NF.NONE

    assignment_kind: ASSIGNMENT_KIND
    lhs: ExprLHS
    expr: ExprNode


############################################################
# Definitions
############################################################
DefNode = Union["DefType", "DefConst", "DefVar", "DefFun", "DefMod"]


@dataclasses.dataclass()
class RecField:  #
    ALIAS = "field"
    FLAGS = NF.TYPE_ANNOTATED

    name: str
    type: TypeNode
    initial: "ExprNode"    # must be const

    def __str__(self):
        return f"{self.name}: {self.type} = {self.initial}"


@dataclasses.dataclass()
class DefRec:
    ALIAS = "rec"
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    fields: List[Union[RecField, Comment]]

    def __str__(self):
        fields = '\n'.join(str(s) for s in self.fields)
        return f"REC {self.name}:\n{fields}"


@dataclasses.dataclass()
class EnumEntry:
    """ Enum element - `value: auto` means previous value + 1"""
    ALIAS = "entry"
    FLAGS = NF.TYPE_ANNOTATED  | NF.GLOBAL_SYM_DEF

    name: str
    value: Union["ValNum", "Auto"]

    def __str__(self):
        return f"{self.name}: {self.value}"


@dataclasses.dataclass()
class DefEnum:
    ALIAS = "enum"
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED  | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    base_type_kind: BASE_TYPE_KIND   # must be integer
    items: List[Union[EnumEntry, Comment]]

    def __str__(self):
        items = '\n'.join(str(s) for s in self.items)
        return f"ENUM {self.name}:\n{items}"


@dataclasses.dataclass()
class DefType:
    """Type Definition"""
    ALIAS = "type"
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.GLOBAL_SYM_DEF

    pub:  bool
    wrapped: bool
    name: str
    type: TypeNode

    def __str__(self):
        return f"TYPE {self.name} = {self.type}"


@dataclasses.dataclass()
class DefConst:
    """Const Definition"""
    ALIAS = "const"
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    pub:  bool
    name: str
    type: Union[TypeNode, Auto]
    value: ValNode

    def __str__(self):
        return f"CONST {self.name}: {self.type} = {self.value}"


@dataclasses.dataclass()
class DefVar:
    """Function Definition"""
    ALIAS = "let"
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF | NF.GLOBAL_SYM_DEF

    pub: bool
    mut: bool
    name: str
    type: Union[TypeNode, Auto]
    initial: ExprNode

    def __str__(self):
        return f"LET {self.name}: {self.type} = {self.initial}"


@dataclasses.dataclass()
class DefFun:
    """Function Definition"""
    ALIAS = "fun"
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF

    init: bool
    fini: bool
    pub: bool
    extern: bool
    name: str
    params: List[FunParam]
    result: TypeNode
    body: List[StmtNode]

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
    """Module argument"""
    ALIAS = "None"
    FLAGS = NF.GLOBAL_SYM_DEF

    name: str
    mod_param_kind: MOD_PARAM_KIND

    def __str__(self):
        return f"{self.name}: {self.mod_param_kind.name}"


@dataclasses.dataclass()
class DefMod:
    """Module Definition"""
    ALIAS = "mod"
    FLAGS = NF.GLOBAL_SYM_DEF

    pub: bool
    name: str
    params: List[ModParam]
    body: List[StmtNode]

    def __str__(self):
        body = '\n'.join(str(s) for s in self.body)
        params = ', '.join(str(p) for p in self.params)
        return f"MOD {self.name} [{params}]:\n{body}"


############################################################
# S-Expression Serialization (Introspection driven)
############################################################
# Partitioning of all the field names in the node classes above.
# Atom fields do NOT contain other node instances
INT_FIELDS = {"number"}
STR_FIELDS = {"name", "string", "field", "label", "target", "index"}
# BOOLs are optional and must come first in a dataclass
FLAG_FIELDS = {"pub", "extern", "mut", "wrapped", "discard", "init", "fini",
               "noesc"}

# Fields containing an enum. Mapped to the enum class
KIND_FIELDS = {
    "unary_expr_kind": UNARY_EXPR_KIND,
    "binary_expr_kind": BINARY_EXPR_KIND,
    "base_type_kind": BASE_TYPE_KIND,
    "mod_param_kind": MOD_PARAM_KIND,
    "assignment_kind": ASSIGNMENT_KIND,
}

# Fields contains list of nodes
LIST_FIELDS = {"params", "args", "path", "items", "fields", "types",
               "values",
               #
               "body", "body_t", "body_f"}

# Fields containing one node
NODE_FIELDS = {"type", "result",
               "size",
               "expr_index",
               # expr
               "expr", "cond", "expr_t", "expr_f", "expr1", "expr2",
               "expr_ret",  "range",
               "container",
               "callee", "length", "start", "end", "step", "width",
               "value", "lhs", "rhs", "initial"}


ALL_FIELDS = FLAG_FIELDS | INT_FIELDS | STR_FIELDS | KIND_FIELDS.keys(
) | NODE_FIELDS | LIST_FIELDS

# check disjointness
assert len(ALL_FIELDS) == (len(FLAG_FIELDS) + len(STR_FIELDS) + len(INT_FIELDS) + len(KIND_FIELDS) +
                           len(NODE_FIELDS) + len(LIST_FIELDS))

# must come last in a dataclass
OPTIONAL_FIELDS = {
    "expr_ret":  ValVoid(),
    "width":  Auto(),
    "start":   Auto(),
    "step":   Auto(),
    "target": "",
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
_NODES_ALIASES = {

    "expr": StmtExpr,
    #
    "type": DefType,
    #
    "fun": DefFun,

    "mod":  DefMod,
    "let": DefVar,
}

ALL_NODES = set()

for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        if obj.__base__ is object:
            ALL_NODES.add(obj)
            _NODES_ALIASES[obj.__name__] = obj
            if obj.ALIAS is not None:
                _NODES_ALIASES[obj.ALIAS] = obj

            flags = []
            other = []
            for field, type in obj.__annotations__.items():
                if field in FLAG_FIELDS:
                    assert not other, "bools must come first"
                    flags.append(field)
                elif field in STR_FIELDS or field in INT_FIELDS or field in KIND_FIELDS:
                    other.append(field)
                elif field in NODE_FIELDS:
                    other.append(field)
                elif field in LIST_FIELDS:
                    other.append(field)
                else:
                    assert False, f"unexpected field {obj.__name__} {field}"
            seen_optional = False
            for x in other:
                if x in OPTIONAL_FIELDS:
                    seen_optional = True
                else:
                    assert not seen_optional, f"in {obj.__name__} optional fields must come last: {other}: {x}"
            obj.FIELDS = flags + other


TYPED_ANNOTATED_NODES = tuple(
    n for n in ALL_NODES if NF.TYPE_ANNOTATED in n.FLAGS)
TYPE_CORPUS_NODES = tuple(n for n in ALL_NODES if NF.TYPE_CORPUS in n.FLAGS)
LOCAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.LOCAL_SYM_DEF in n.FLAGS)
GLOBAL_SYM_DEF_NODES = tuple(
    n for n in ALL_NODES if NF.GLOBAL_SYM_DEF in n.FLAGS)


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
    "false": ValTrue(),
    "true": ValFalse(),
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
        parts = t.split("::")
        return Id(parts[:-1], parts[-1])
    elif _TOKEN_NUM.match(t):
        return ValNum(t)
    else:
        assert False, f"cannot expand short hand: {field} {t}"


def ReadPiece(field, token, stream) -> Any:
    """Read a single component of an SExpr including lists."""
    if field in FLAG_FIELDS:
        return bool(token)
    elif field in STR_FIELDS:
        return token
    elif field in INT_FIELDS:
        return token
    elif field in KIND_FIELDS:
        enum = KIND_FIELDS.get(field)
        assert enum is not None, f"{field} {token}"
        return enum[token]
    elif field in NODE_FIELDS:
        if token == "(":
            return ReadSExpr(stream)
        return ExpandShortHand(field, token)
    elif field in LIST_FIELDS:
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
        if token == ")":
            # we have reached the end before all the fields were processed
            # fill in default values
            assert field in OPTIONAL_FIELDS, f"unknown optional: {field}"
            pieces.append(OPTIONAL_FIELDS[field])
        elif field in FLAG_FIELDS:
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
    if tag in BINOP_SHORTCUT:
        return ReadRestAndMakeNode(Expr2, [BINOP_SHORTCUT[tag]],
                                   ["expr1", "expr2"], stream)
    elif tag in _ASSIGNMENT_SHORTCUT:
        return ReadRestAndMakeNode(StmtAssignment2, [_ASSIGNMENT_SHORTCUT[tag]],
                                   ["lhs", "rhs"], stream)
    else:
        cls = _NODES_ALIASES.get(tag)
        assert cls is not None, f"Non node: {tag}"
        fields = [f for f, _ in cls.__annotations__.items()]
        return ReadRestAndMakeNode(cls, [], fields, stream)


SCOPING_NODES = (StmtBlock, StmtWhile, StmtFor, StmtDefer,
                 StmtIf, DefFun)

VALUE_NODES = (ValTrue, ValFalse, ValNum, IndexVal,
               ValUndef, ValVoid, FieldVal, ValArray,
               ValArrayString, ValRec)

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
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
