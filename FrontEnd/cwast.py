#!/usr/bin/python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend


"""

import sys
import re
import dataclasses
import logging
import enum
from typing import List, Dict, Set, Optional, Union, Any

logger = logging.getLogger(__name__)


############################################################
# Enums
############################################################
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


@enum.unique
class NF(enum.Flag):
    """Node Flags"""
    NONE = 0
    TYPE_ANNOTATED = enum.auto()   # node has a type (x_type)
    VALUE_ANNOTATED = enum.auto()  # node may have a comptime value (x_value)
    MUST_HAVE_VALUE = enum.auto()
    FIELD_ANNOTATED = enum.auto()  # node reference a struct field (x_field)
    SYMBOL_ANNOTATED = enum.auto()  # node reference a XXX_SYM_DEF node (x_symbol)
    TYPE_CORPUS = enum.auto()
    CONTROL_FLOW = enum.auto()
    GLOBAL_SYM_DEF = enum.auto()
    LOCAL_SYM_DEF = enum.auto()
    TOP_LEVEL = enum.auto()
    MACRO_BODY_ONLY = enum.auto()
    TO_BE_EXPANDED = enum.auto()


@enum.unique
class GROUP(enum.IntEnum):
    """Node Family"""
    Misc = enum.auto()
    Type = enum.auto()
    Statement = enum.auto()
    Value = enum.auto()
    Expression = enum.auto()
    Macro = enum.auto()
    Ephemeral = enum.auto()  # should only exist during intermediate steps and in macros


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


@enum.unique
class MOD_PARAM_KIND(enum.Enum):
    INVALID = 0
    CONST = 1
    MOD = 2
    TYPE = 3


@enum.unique
class MACRO_PARAM_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = 0
    ID = 1
    STMT_LIST = 2
    EXPR = 3
    FIELD = 4
    TYPE = 5

############################################################
# Field attributes of Nodes
#
# the fields of nodes are subject to a lot of invariants which must be enforced
#
# There are two kinds of fields:
# * regular fields - typically populated directly from source
# * x-fields - typically populated by later analyses
#
# Regular fields follow these rules
#
# All fields belong to one of these categories:
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


NODES_PARAMS = ("Comment", "FunParam")
NODES_PARAMS_T = Union[NODES_PARAMS]

NODES_BODY_MOD = ("Comment", "DefFun", "DefRec", "DefEnum", "DefVar", "DefMacro", "DefType", "DefGlobal",
                  "StmtStaticAssert", "Import")
NODES_BODY_MOD_T = Union[NODES_BODY_MOD]

NODES_PARAMS_MOD = ("Comment", "ModParam")
NODES_PARAMS_MOD_T = Union[NODES_PARAMS_MOD]

NODES_PARAMS_MACRO = ("Comment", "MacroParam")
NODES_PARAMS_MACRO_T = Union[NODES_PARAMS_MACRO]

NODES_BODY = ("Comment", "StmtDefer", "StmtIf", "StmtBreak",
              "StmtContinue", "StmtReturn", "StmtExpr", "StmtCompoundAssignment",
              "StmtBlock", "StmtCond", "DefVar", "MacroInvoke", "StmtAssignment", "StmtTrap")
NODES_BODY_T = Union[NODES_BODY]

NODES_BODY_MACRO = ("Comment", "StmtDefer", "StmtIf", "StmtBreak",
                    "StmtContinue", "StmtReturn", "StmtExpr",
                    "StmtBlock", "StmtCond")
NODES_BODY_MACRO_T = Union[NODES_BODY_MACRO]

NODES_TYPES = ("Comment", "TypeBase",
               "TypeSlice", "TypeArray", "TypePtr", "TypeFun", "Id", "TypeSum")
NODES_TYPES_T = Union[NODES_TYPES]

NODES_TYPES_OR_AUTO = ("Comment", "TypeBase",
                       "TypeSlice", "TypeArray", "TypePtr", "TypeFun", "Id", "TypeSum", "TypeAuto")
NODES_TYPES_OR_AUTO_T = Union[NODES_TYPES_OR_AUTO]

NODES_ITEMS = ("Comment", "EnumVal")
NODES_ITEMS_T = Union[NODES_ITEMS]

NODES_INITS_ARRAY = ("Comment", "IndexVal")
NODES_INITS_ARRAY_T = Union[NODES_INITS_ARRAY]

NODES_INITS_REC = ("Comment", "FieldVal")
NODES_INITS_REC_T = Union[NODES_INITS_REC]

NODES_FIELDS = ("Comment", "RecField")
NODES_FIELDS_T = Union[NODES_FIELDS]

NODES_CASES = ("Comment", "Case")
NODES_CASES_T = Union[NODES_CASES]

NODES_EXPR = ("ValFalse", "ValTrue", "ValNum", "ValUndef",
              "ValVoid", "ValArray", "ValString", "ValRec",
              #
              "MacroInvoke",
              #
              "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
              "ExprField", "ExprCall", "ExprParen",
              "Expr1", "Expr2", "Expr3",
              "ExprLen", "ExprSizeof", "ExprOffsetof", "ExprStmt",
              "ExprIs", "ExprAs", "ExprAsNot")
NODES_EXPR_T = Union[NODES_EXPR]

NODES_COND = ("ValFalse", "ValTrue",
              #
              "Id", "ExprDeref", "ExprIndex",
              "ExprField", "ExprCall", "ExprParen",
              "Expr1", "Expr2", "Expr3",
              "ExprStmt", "ExprIs")
NODES_COND_T = Union[NODES_COND]

NODES_LHS = ("Id", "ExprDeref", "ExprIndex", "ExprField", "ExprCall")
NODES_LHS_T = Union[NODES_LHS]

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
    # TODO: fix all the None below
    NFD(NFK.LIST, "params", "function parameters and/or comments", NODES_PARAMS),
    NFD(NFK.LIST, "params_mod", "module template parameters", NODES_PARAMS_MOD),
    NFD(NFK.LIST, "params_macro", "macro parameters", NODES_PARAMS_MACRO),
    NFD(NFK.LIST, "args", "function call arguments", None),
    NFD(NFK.LIST, "items", "enum items and/or comments", NODES_ITEMS),
    NFD(NFK.LIST, "fields", "record fields and/or comments", NODES_FIELDS),
    NFD(NFK.LIST, "types", "union types", NODES_TYPES),
    NFD(NFK.LIST, "inits_array",
        "array initializers and/or comments", NODES_INITS_ARRAY),
    NFD(NFK.LIST, "inits_rec", "record initializers and/or comments", NODES_INITS_REC),
    #
    NFD(NFK.LIST, "body_mod",
        "toplevel module definitions and/or comments", NODES_BODY_MOD),
    NFD(NFK.LIST, "body", "new scope: statement list and/or comments", NODES_BODY),
    NFD(NFK.LIST, "body_t",
        "new scope: statement list and/or comments for true branch", NODES_BODY),
    NFD(NFK.LIST, "body_f",
        "new scope: statement list and/or comments for false branch", NODES_BODY),
    NFD(NFK.LIST, "body_for", "statement list for macro_loop", NODES_BODY),
    NFD(NFK.LIST, "body_macro",
        "new scope: macro statments/expression", None),
    NFD(NFK.LIST, "cases", "list of case statements", NODES_CASES),

    #
    NFD(NFK.NODE, "init_index",
        "initializer index or empty (empty mean next index)", None),
    NFD(NFK.NODE, "type", "type expression", NODES_TYPES),
    NFD(NFK.NODE, "type_or_auto", "type expression", NODES_TYPES_OR_AUTO),
    NFD(NFK.NODE, "result", "return type", None),
    NFD(NFK.NODE, "size", "compile-time constant size", None),
    NFD(NFK.NODE, "expr_size", "expression determining the size or auto", None),
    NFD(NFK.NODE, "expr_index",
        "expression determining the index to be accessed", None),
    NFD(NFK.NODE, "expr", "expression", NODES_EXPR),
    NFD(NFK.NODE, "cond", "conditional expression must evaluate to a boolean", NODES_COND),
    NFD(NFK.NODE, "expr_t",
        "expression (will only be evaluated if cond == true)", NODES_EXPR),
    NFD(NFK.NODE, "expr_f",
        "expression (will only be evaluated if cond == false)", NODES_EXPR),
    NFD(NFK.NODE, "expr1", "left operand expression", NODES_EXPR),
    NFD(NFK.NODE, "expr2", "righ operand expression", NODES_EXPR),
    NFD(NFK.NODE, "expr_ret", "result expression (ValVoid means no result)", NODES_EXPR),
    NFD(NFK.NODE, "pointer", "pointer component of slice", None),
    NFD(NFK.NODE, "container", "array and slice", None),
    NFD(NFK.NODE, "callee", "expression evaluating to the function to be called", None),
    NFD(NFK.NODE, "width", "desired width of slice (default: length of container)", None),
    NFD(NFK.NODE, "value", "", NODES_EXPR),
    NFD(NFK.NODE, "value_or_auto", "enum constant or auto", None),
    NFD(NFK.NODE, "value_or_undef", "", None),
    NFD(NFK.NODE, "lhs", "l-value expression", NODES_LHS),
    NFD(NFK.NODE, "initial_or_undef", "initializer", None),
    NFD(NFK.NODE, "default_or_undef",
        "value if type narrowing fail or trap if undef", None),
]

NEW_SCOPE_FIELDS = set(["body", "body_f", "body_t", "body_macro"])

ALL_FIELDS_MAP: Dict[str, NFD] = {nfd.name: nfd for nfd in ALL_FIELDS}


# Optional fields must come last in a dataclass
OPTIONAL_FIELDS = {
    "expr_ret": lambda srcloc: ValVoid(x_srcloc=srcloc),
    "width": lambda srcloc: ValAuto(x_srcloc=srcloc),
    "start": lambda srcloc:  ValAuto(x_srcloc=srcloc),
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
    "x_srcloc": None,  # set by cwast.py
    #
    "x_symbol": NF.SYMBOL_ANNOTATED,  # set by symbolize.py
    "x_target": NF.CONTROL_FLOW,  # set by symbolize.py
    #
    "x_field": NF.FIELD_ANNOTATED,  # set by typify.py
    #
    "x_type": NF.TYPE_ANNOTATED,   # set by typify.py
    "x_alignment": NF.TYPE_ANNOTATED,  # set by typify.py
    "x_size": NF.TYPE_ANNOTATED,  # set by typify.py
    "x_offset": NF.TYPE_ANNOTATED,  # set by typify.py
    #
    "x_value": NF.VALUE_ANNOTATED,  # set by eval.py
}


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


# maps node class name and aliases to class
NODES_ALIASES = {}

ALL_NODES = set()


def _CheckNodeFieldOrder(obj):
    seen_optional = False
    seen_non_flag = False
    for field, type in obj.__annotations__.items():
        if field.startswith("x_"):
            assert field in X_FIELDS, f"unexpected x-field: {field} in node {type}"
            x = X_FIELDS[field]
            if x:
                assert x in obj.FLAGS
            continue
        nfd = ALL_FIELDS_MAP[field]
        if field in OPTIONAL_FIELDS:
            seen_optional = True
        else:
            assert not seen_optional, f"in {obj.__name__} optional fields must come last: {field}"

        if nfd.kind is NFK.FLAG:
            assert not seen_non_flag, "flags must come first"
        else:
            seen_non_flag = True


def NodeCommon(cls):
    cls.__eq__ = lambda a, b: id(a) == id(b)
    cls.__hash__ = lambda a: id(a)

    assert hasattr(cls, "ALIAS") and hasattr(
        cls, "FLAGS") and hasattr(cls, "GROUP")
    assert hasattr(cls, "x_srcloc")
    _CheckNodeFieldOrder(cls)

    ALL_NODES.add(cls)
    NODES_ALIASES[cls.__name__] = cls
    if cls.ALIAS is not None:
        NODES_ALIASES[cls.ALIAS] = cls
    cls.FIELDS = [field for field, type in cls.__annotations__.items()
                  if not field.startswith("x_")]
    return cls


############################################################
# Comment and Emphemeral
############################################################
@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class EphemeralList:
    """Only exist temporarily after a replacement strep

    will removed (flattened) in the next cleanup step
    """
    ALIAS = None
    GROUP = GROUP.Macro
    FLAGS = NF(0)
    #
    args: List[NODES_EXPR_T]
    #
    x_srcloc: Optional[Any] = None

############################################################
# Identifier
############################################################


@enum.unique
class ID_KIND(enum.Enum):
    INVALID = 0
    VAR = 1
    CONST = 2
    FUN = 3


@NodeCommon
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
        joiner = "/" if self.path else ""
        return f"{_NAME(self)} {self.path}{joiner}{self.name}"


@NodeCommon
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
@NodeCommon
@dataclasses.dataclass()
class FunParam:
    """Function parameter

    """
    ALIAS = "param"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF
    #
    name: str      # empty str means no var specified (fun proto type)
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}: {self.type}"


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


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class TypePtr:
    """Pointer type
    """
    ALIAS = "ptr"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    mut: bool   # pointee is mutable
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"{_NAME(self)}{_FLAGS(self)} {self.type}"


@NodeCommon
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
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        mod = "-MUT" if self.mut else ""
        return f"{_NAME(self)}{mod}({self.type})"


@NodeCommon
@dataclasses.dataclass()
class TypeArray:
    """An array of the given type and `size`

    """
    ALIAS = "array"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    size: "NODES_EXPR_T"      # must be const and unsigned
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)} ({self.type}) {self.size}"


@NodeCommon
@dataclasses.dataclass()
class TypeFun:
    """A function signature

    The `FunParam.name` field is ignored and should be `_`
    """
    ALIAS = "sig"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    params: List[NODES_PARAMS_T]
    result: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        t = [str(t) for t in self.params]
        return f"{_NAME(self)} {' '.join(t)} -> {self.result}"


@NodeCommon
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
    types: List[NODES_TYPES_T]
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
@NodeCommon
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


@NodeCommon
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


@NodeCommon
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


@NodeCommon
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


@NodeCommon
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


@NodeCommon
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


@NodeCommon
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
    value_or_undef: "NODES_EXPR_T"
    init_index: "NODES_EXPR_T"  # compile time constant
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.init_index}] = {self.value_or_undef}"


@NodeCommon
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
    value: "NODES_EXPR_T"
    init_field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.init_field}] = {self.value}"


@NodeCommon
@dataclasses.dataclass()
class ValArray:
    """An array literal

    `[10]int{.1 = 5, .2 = 6, 77}`
    """
    ALIAS = "array_val"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: NODES_TYPES_T
    expr_size: Union["NODES_EXPR_T", ValAuto]  # must be constant
    inits_array: List[NODES_INITS_ARRAY_T]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr_size}"


@NodeCommon
@dataclasses.dataclass()
class ValSlice:
    """A slice value comprised of a pointer and length

    type and mutability is defined by the pointer
    """
    ALIAS = "slice_val"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    pointer: "NODES_EXPR_T"
    expr_size: "NODES_EXPR_T"
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self): return f"{_NAME(self)} {self.string}"


NODES_INITS_REC_T = Union[Comment, FieldVal]


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class ValRec:
    """A record literal

    `E.g.: complex{.imag = 5, .real = 1}`
    """
    ALIAS = "rec"
    GROUP = GROUP.Value
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: NODES_TYPES_T
    inits_rec: List[NODES_INITS_REC_T]
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
@NodeCommon
@dataclasses.dataclass()
class ExprDeref:
    """Dereference a pointer represented by `expr`"""
    ALIAS = "^"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: NODES_EXPR_T  # must be of type AddrOf
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr}"


@NodeCommon
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
    expr: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprCall:
    """Function call expression.
    """
    ALIAS = "call"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    polymorphic: bool
    callee: NODES_EXPR_T
    args: List[NODES_EXPR_T]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.callee}"


@NodeCommon
@dataclasses.dataclass()
class ExprParen:
    """Used for preserving parenthesis in the source
    """
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None


@NodeCommon
@dataclasses.dataclass()
class ExprField:
    """Access field in expression representing a record.
    """
    ALIAS = "."
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.FIELD_ANNOTATED
    #
    container: NODES_EXPR_T  # must be of type rec
    field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} {self.container} . {self.field}"


@NodeCommon
@dataclasses.dataclass()
class Expr1:
    """Unary expression."""
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    unary_expr_kind: UNARY_EXPR_KIND
    expr: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.unary_expr_kind} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class Expr2:
    """Binary expression."""
    ALIAS = None
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    binary_expr_kind: BINARY_EXPR_KIND
    expr1: NODES_EXPR_T
    expr2: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.binary_expr_kind.name}({self.expr1}, {self.expr2})"


@NodeCommon
@dataclasses.dataclass()
class Expr3:
    """Tertiary expression (like C's `? :`)
    """
    ALIAS = "?"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    cond: NODES_EXPR_T  # must be of type  bool
    expr_t: NODES_EXPR_T
    expr_f: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"? {self.cond} {self.expr_t} {self.expr_f}"

# Array/Slice Expressions


@NodeCommon
@dataclasses.dataclass()
class ExprIndex:
    """Checked indexed access of array or slice
    """
    ALIAS = "at"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    container: NODES_EXPR_T  # must be of type slice or array
    expr_index: NODES_EXPR_T  # must be of int type
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"AT {self.container} {self.expr_index}"


@NodeCommon
@dataclasses.dataclass()
class ExprLen:
    """Length of array or slice"""
    ALIAS = "len"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    container: NODES_EXPR_T   # must be of type slice or array
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return self.__class__.__name__
# Cast Like Expressions


@NodeCommon
@dataclasses.dataclass()
class ExprIs:
    """Test actual expression type within a Sum Type

    """
    ALIAS = "is"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr} {self.type}"


@NodeCommon
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
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.expr} AS {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprAsNot:
    """Cast of Union to diff of the union and the given type

    """
    ALIAS = "asnot"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{self.expr} AS {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprTryAs:
    """Narrow a `expr` which is of Sum to `type`

    If the is not possible return `default_or_undef` if that is not undef
    or trap otherwise.

    """
    ALIAS = "tryas"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    default_or_undef: Union[NODES_EXPR_T, ValUndef]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr} {self.type} {self.default_or_undef}"


@NodeCommon
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
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None


@NodeCommon
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
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None


@NodeCommon
@dataclasses.dataclass()
class ExprSizeof:
    """Byte size of type

    Type is `uint`"""
    ALIAS = "sizeof"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprOffsetof:
    """Byte offset of field in record types

    Type is `uint`"""
    ALIAS = "offsetof"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.FIELD_ANNOTATED
    #
    type: NODES_TYPES_T  # must be rec
    field: str
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_field: Optional["RecField"] = None

    def __str__(self):
        return f"{_NAME(self)} {self.type} {self.field}"


@NodeCommon
@dataclasses.dataclass()
class ExprStmt:
    """Expr with Statements

    The body statements must be terminated by a StmtReturn
    """
    ALIAS = "expr"
    GROUP = GROUP.Expression
    FLAGS = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED
    #
    body: List[NODES_BODY_T]  # new scope
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


############################################################
# Stmt
############################################################
@NodeCommon
@dataclasses.dataclass()
class StmtBlock:
    """Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    """
    ALIAS = "block"
    GROUP = GROUP.Statement
    FLAGS = NF(0)
    #
    label: str
    body: List[NODES_BODY_T]  # new scope
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.label}"


@NodeCommon
@dataclasses.dataclass()
class StmtDefer:
    """Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    """
    ALIAS = "defer"
    GROUP = GROUP.Statement
    FLAGS = NF(0)
    #
    body:  List[NODES_BODY_T]  # new scope, must NOT contain RETURN
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class StmtIf:
    """If statement"""
    ALIAS = "if"
    GROUP = GROUP.Statement
    FLAGS = NF(0)
    #
    cond: NODES_EXPR_T        # must be of type bool
    body_t: List[NODES_BODY_T]  # new scope
    body_f: List[NODES_BODY_T]  # new scope
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class Case:
    """Single case of a Cond statement"""
    ALIAS = "case"
    GROUP = GROUP.Statement
    FLAGS = NF(0)
    #
    cond: NODES_EXPR_T        # must be of type bool
    body: List[NODES_BODY_T]  # new scope
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class StmtCond:
    """Multicase if-elif-else statement"""
    ALIAS = "cond"
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    cases: List[NODES_CASES_T]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@NodeCommon
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
    x_target: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.target}"


@NodeCommon
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
    x_target: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.target}"


@NodeCommon
@dataclasses.dataclass()
class StmtReturn:
    """Return statement

    Returns from the first enclosing ExprStmt node or the enclosing DefFun node.
    Uses void_val if the DefFun's return type is void
    """
    ALIAS = "return"
    GROUP = GROUP.Statement
    FLAGS = NF.CONTROL_FLOW
    #
    expr_ret: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_target: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.expr_ret}"


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class StmtStaticAssert:
    """Static assert statement (must evaluate to true at compile-time"""
    ALIAS = "static_assert"
    GROUP = GROUP.Statement
    FLAGS = NF.TOP_LEVEL
    #
    cond: NODES_EXPR_T  # must be of type bool
    message: str     # should this be an expression?
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class StmtTrap:
    """Trap statement"""
    ALIAS = "trap"
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class StmtCompoundAssignment:
    """Compound assignment statement"""
    ALIAS = None
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    assignment_kind: ASSIGNMENT_KIND
    lhs: NODES_LHS_T
    expr: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} [{self.assignment_kind.name}] {self.lhs} = {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class StmtAssignment:
    """Assignment statement"""
    ALIAS = "="
    GROUP = GROUP.Statement
    FLAGS = NF.NONE
    #
    lhs: NODES_LHS_T
    expr: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.lhs} = {self.expr}"


############################################################
# Definitions
############################################################
@NodeCommon
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
    type: NODES_TYPES_T
    initial_or_undef: Union["NODES_EXPR_T", ValUndef]    # must be const
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None
    x_offset: int = -1

    def __str__(self):
        return f"{_NAME(self)} {self.name}: {self.type} = {self.initial_or_undef}"


@NodeCommon
@dataclasses.dataclass()
class DefRec:
    """Record definition"""
    ALIAS = "defrec"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    pub:  bool
    name: str
    fields: List[NODES_FIELDS_T]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f" {_NAME(self)}{_FLAGS(self)}"


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class DefEnum:
    """Enum definition"""
    ALIAS = "enum"
    GROUP = GROUP.Type
    FLAGS = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL | NF.VALUE_ANNOTATED
    #
    pub:  bool
    name: str
    base_type_kind: BASE_TYPE_KIND   # must be integer
    items: List[NODES_ITEMS_T]
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None  # used to guide the evaluation of EnumVal
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name}"


@NodeCommon
@dataclasses.dataclass()
class DefType:
    """Type definition

    """
    ALIAS = "type"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    pub:  bool
    wrapped: bool
    name: str
    type: NODES_TYPES_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_alignment: int = -1
    x_size: int = -1

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} = {self.type}"


@NodeCommon
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
    type_or_auto: NODES_TYPES_OR_AUTO_T
    initial_or_undef: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef}"


@NodeCommon
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
    type_or_auto: NODES_TYPES_OR_AUTO_T
    initial_or_undef: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None
    x_value: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef}"


@NodeCommon
@dataclasses.dataclass()
class DefFun:
    """Function definition"""
    ALIAS = "fun"
    GROUP = GROUP.Statement
    FLAGS = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    init: bool
    fini: bool
    pub: bool
    extern: bool
    polymorphic: bool
    name: str
    params: List[NODES_PARAMS_T]
    result: NODES_TYPES_T
    body: List[NODES_BODY_T]  # new scope
    #
    x_srcloc: Optional[Any] = None
    x_type: Optional[Any] = None

    def __str__(self):
        params = ', '.join(str(p) for p in self.params)
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} [{params}]->{self.result}"


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class DefMod:
    """Module Definition

    The module is a template if `params` is non-empty"""
    ALIAS = "module"
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF
    #
    name: str
    params_mod: List[NODES_PARAMS_MOD_T]
    body_mod: List[NODES_BODY_MOD_T]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        params = ', '.join(str(p) for p in self.params_mod)
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} [{params}]"


@NodeCommon
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
@NodeCommon
@dataclasses.dataclass()
class ExprSrcLoc:
    """Source Location encoded as u32"""
    ALIAS = "src_loc"
    GROUP = GROUP.Expression
    FLAGS = NF.TO_BE_EXPANDED
    #
    x_srcloc: Optional[Any] = None


@NodeCommon
@dataclasses.dataclass()
class ExprStringify:
    """Human readable representation of the expression

    This is useful to implement for assert like features
    """
    ALIAS = "stringify"
    GROUP = GROUP.Expression
    FLAGS = NF.TO_BE_EXPANDED
    #
    expr:  NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None

############################################################
# Macro
############################################################


@NodeCommon
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


@NodeCommon
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
    type_or_auto: NODES_TYPES_OR_AUTO_T
    initial_or_undef: NODES_EXPR_T
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)}{_FLAGS(self)} {self.name} {self.initial_or_undef}"


@NodeCommon
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
    body_for: List[Any]
    #
    x_srcloc: Optional[Any] = None


@NodeCommon
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


@NodeCommon
@dataclasses.dataclass()
class MacroInvoke:
    """Macro Invocation"""
    ALIAS = "macro_invoke"
    GROUP = GROUP.Macro
    FLAGS = NF.TO_BE_EXPANDED
    #
    name: str
    args: List[NODES_EXPR_T]
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


@NodeCommon
@dataclasses.dataclass()
class DefMacro:
    """Define a macro


    A macro consists of parameters whose name starts with a '$'
    and a body. Macros that evaluate to expressions will typically
    have a single node body
    """
    ALIAS = "macro"
    GROUP = GROUP.Statement
    FLAGS = NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    pub: bool
    #
    name: str
    params_macro: List[NODES_PARAMS_MACRO_T]
    gen_ids: List[str]
    body_macro: List[Any]  # new scope
    #
    x_srcloc: Optional[Any] = None

    def __str__(self):
        return f"{_NAME(self)} {self.name}"


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


############################################################
#
############################################################
def VisitAstRecursively(node, visitor):
    if visitor(node):
        return
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            VisitAstRecursively(getattr(node, c), visitor)
        elif nfd.kind is NFK.LIST:
            for cc in getattr(node, c):
                VisitAstRecursively(cc, visitor)


def VisitAstRecursivelyWithParent(node, parent, visitor):
    if visitor(node, parent):
        return
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            VisitAstRecursivelyWithParent(getattr(node, c), node, visitor)
        elif nfd.kind is NFK.LIST:
            for cc in getattr(node, c):
                VisitAstRecursivelyWithParent(cc, node, visitor)


def VisitAstRecursivelyWithAllParents(node, parents: List[Any], visitor):
    if visitor(node, parents):
        return
    parents.append(node)
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            VisitAstRecursivelyWithAllParents(
                getattr(node, c), parents, visitor)
        elif nfd.kind is NFK.LIST:
            for cc in getattr(node, c):
                VisitAstRecursivelyWithAllParents(cc, parents, visitor)
    parents.pop(-1)


def MaybeReplaceAstRecursively(node, replacer):
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            child = getattr(node, c)
            new_child = replacer(child)
            if new_child:
                setattr(node, c, new_child)
            else:
                MaybeReplaceAstRecursively(child, replacer)
        elif nfd.kind is NFK.LIST:
            children = getattr(node, c)
            for n, child in enumerate(children):
                new_child = replacer(child)
                if new_child:
                    children[n] = new_child
                else:
                    MaybeReplaceAstRecursively(child, replacer)

def MaybeReplaceAstRecursivelyPost(node, replacer):
    for c in node.__class__.FIELDS:
        # print ("replace: ", node.__class__.__name__, c)
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            child = getattr(node, c)
            MaybeReplaceAstRecursivelyPost(child, replacer)
            new_child = replacer(child)
            if new_child:
                setattr(node, c, new_child)
        elif nfd.kind is NFK.LIST:
            children = getattr(node, c)
            for n, child in enumerate(children):
                MaybeReplaceAstRecursivelyPost(child, replacer)
                new_child = replacer(child)
                if new_child:
                    children[n] = new_child
                    

def _MaybeFlattenEphemeralList(nodes: List[Any]):
    has_ephemeral =  False
    for n in nodes:
        if isinstance(n, EphemeralList):
            has_ephemeral = True
            break
    if not has_ephemeral:
        return nodes
    out = []
    for c in nodes:
        if isinstance(c, EphemeralList):
            out += _MaybeFlattenEphemeralList(c.args)
        else:
            out.append(c)
    return out


def EliminateEphemeralsRecursively(node):
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            child = getattr(node, c)
            if isinstance(child, EphemeralList):
                new_child = _MaybeFlattenEphemeralList([child])
                assert len(new_child) == 1
                setattr(node, c, new_child[0])
            EliminateEphemeralsRecursively(child)
        elif nfd.kind is NFK.LIST:
            children = getattr(node, c)
            new_children = _MaybeFlattenEphemeralList(children)
            if new_children is not children:
                 setattr(node, c, new_children)
            for child in children:
                EliminateEphemeralsRecursively(child)


def CloneNodeRecursively(node):
    clone = dataclasses.replace(node)
    for c in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[c]
        if nfd.kind is NFK.NODE:
            setattr(clone, c, CloneNodeRecursively(getattr(node, c)))
        elif nfd.kind is NFK.LIST:
            out = [CloneNodeRecursively(cc) for cc in getattr(node, c)]
            setattr(clone, c, out)
    return clone


############################################################
# Helpers
############################################################

def StripNodes(node, cls):
    def replacer(n):
        if isinstance(n, cls):
            return EphemeralList([])
        else:
            return None
    MaybeReplaceAstRecursively(node, replacer)
    EliminateEphemeralsRecursively(node)

############################################################
# AST Checker
############################################################
def CompilerError(srcloc, msg):
    print(f"{srcloc} ERROR: {msg}", file=sys.stdout)
    assert False


class CheckASTContext:
    def __init__(self, allow_comments, allow_macros):
        self.allow_comments = allow_comments
        self.allow_macros = allow_macros
        self.toplevel = True
        self.in_fun = False
        self.in_macro = False


def _CheckMacroRecursively(node, seen_names: Set[str]):
    def visitor(node):
        if isinstance(node, (MacroParam, MacroFor)):
            assert node.name.startswith("$")
            assert node.name not in seen_names, f"duplicate name: {node.name}"
            seen_names.add(node.name)
    VisitAstRecursively(node, visitor)


def CheckAST(node, parent, ctx: CheckASTContext):
    assert node.x_srcloc, f"Node without srcloc {node}"
    if NF.TOP_LEVEL in node.FLAGS:
        assert ctx.toplevel, f"only allowed at toplevel: {node}"
    if NF.MACRO_BODY_ONLY in node.FLAGS:
        assert ctx.in_macro, f"only allowed in macros: {node}"
    if node.GROUP is GROUP.Ephemeral:
        assert ctx.in_macro, f"only allowed in macros: {node}"
    if isinstance(node, Comment):
        assert ctx.allow_comments
    if isinstance(node, DefMacro):
        assert ctx.allow_macros
        for p in node.params_macro:
            assert p.name.startswith("$")
        for i in node.gen_ids:
            assert i.startswith("$")
        _CheckMacroRecursively(node, set())

    for f in node.__class__.FIELDS:
        nfd = ALL_FIELDS_MAP[f]
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            permitted = nfd.extra
            if permitted and not ctx.in_macro:
                if child.__class__.__name__ not in permitted:
                    CompilerError(
                        node.x_srcloc, f"{_NAME(node)} [{f}]: bad child {child}")
            ctx.toplevel = isinstance(node, DefMod)
            ctx.in_fun |= isinstance(node, DefFun)
            ctx.in_macro |= isinstance(node, DefMacro)
            CheckAST(child, node, ctx)
        elif nfd.kind is NFK.LIST:
            permitted = nfd.extra
            for cc in getattr(node, f):
                if permitted and not ctx.in_macro:
                    assert cc.__class__.__name__ in permitted, f"{_NAME(node)} [{f}]: bad child {_NAME(cc)}"
                ctx.toplevel = isinstance(node, DefMod)
                ctx.in_fun |= isinstance(node, DefFun)
                ctx.in_macro |= isinstance(node, DefMacro)
                CheckAST(cc, node, ctx)


##########################################################################################
# Doc Generation
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

        if NF.TOP_LEVEL in cls.FLAGS:
            print(f"", file=fout)
            print(f"Allowed at top level only", file=fout)
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
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    GenerateDocumentation(sys.stdout)
