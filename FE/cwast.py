#!/bin/env python3

"""AST Nodes and SExpr reader/writer for the Cwerg frontend"""
from __future__ import annotations

import sys
import dataclasses
import logging
import enum
import re

from Util import cgen
from Util.parse import EscapedStringToBytes, HexStringToBytes

from typing import Optional, Union, Any, TypeAlias, NoReturn, Final, ClassVar

logger = logging.getLogger(__name__)


MACRO_CALL_SUFFIX = "#"
MUTABILITY_SUFFIX = "!"
MACRO_VAR_PREFIX = "$"
ANNOTATION_PREFIX = "@"
ID_PATH_SEPARATOR = "::"

BUILT_IN_STMT_MACROS = set([
    "while",
    "for",
    "trylet",
    "trylet!",
    "tryset",
])

BUILT_IN_EXPR_MACROS = set([
    "span_inc",
    "span_diff",
])

ALL_BUILT_IN_MACROS = BUILT_IN_STMT_MACROS | BUILT_IN_EXPR_MACROS


@dataclasses.dataclass(eq=True, frozen=True)
class NAME:
    name: str

    @staticmethod
    def Make(s) -> "NAME":
        return NAME(sys.intern(s))

    def IsMacroCall(self):
        return self.name.endswith(MACRO_CALL_SUFFIX)

    def IsMacroVar(self):
        return self.name.startswith(MACRO_VAR_PREFIX)

    def GetSymbolNameWithoutQualifier(self) -> NAME:
        pos = self.name.find(ID_PATH_SEPARATOR)
        if pos < 0:
            return self
        return NAME(self.name[pos + len(ID_PATH_SEPARATOR):])

    def __str__(self):
        return f"{self.name}"


EMPTY_NAME = NAME("")

############################################################
# Enums
############################################################


@enum.unique
class BASE_TYPE_KIND(enum.Enum):
    """basic scalar types"""
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
    TYPEID = 43

    def IsUint(self) -> bool:
        return BASE_TYPE_KIND.UINT.value <= self.value <= BASE_TYPE_KIND.U64.value

    def IsSint(self) -> bool:
        return BASE_TYPE_KIND.SINT.value <= self.value <= BASE_TYPE_KIND.S64.value

    def IsInt(self) -> bool:
        return BASE_TYPE_KIND.SINT.value <= self.value <= BASE_TYPE_KIND.U64.value

    def IsReal(self) -> bool:
        return self in (BASE_TYPE_KIND.R32, BASE_TYPE_KIND.R64)

    def IsNumber(self) -> bool:
        return BASE_TYPE_KIND.SINT.value <= self.value <= BASE_TYPE_KIND.R64.value

    @classmethod
    def MakeUint(cls, size: int) -> "BASE_TYPE_KIND":
        return {8: BASE_TYPE_KIND.U8, 16: BASE_TYPE_KIND.U16, 32: BASE_TYPE_KIND.U32, 64: BASE_TYPE_KIND.U64}[size]

    @classmethod
    def MakeSint(cls, size: int) -> "BASE_TYPE_KIND":
        return {8: BASE_TYPE_KIND.S8, 16: BASE_TYPE_KIND.S16, 32: BASE_TYPE_KIND.S32, 64: BASE_TYPE_KIND.S64}[size]


BASE_TYPE_KIND_TO_SIZE: dict[BASE_TYPE_KIND, int] = {
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
    BASE_TYPE_KIND.BOOL: 1,
    #
    BASE_TYPE_KIND.VOID: 0,
    BASE_TYPE_KIND.NORET: 0,

}


def KeywordToBaseTypeKind(s: str) -> BASE_TYPE_KIND:
    ss = s.lower()
    if ss != s:
        return BASE_TYPE_KIND.INVALID
    s = s.upper()
    try:
        return BASE_TYPE_KIND[s]
    except KeyError:
        return BASE_TYPE_KIND.INVALID


def BaseTypeKindToKeyword(kind: BASE_TYPE_KIND) -> str:
    return kind.name.lower()


@enum.unique
class NF(enum.Flag):
    """Node Flags"""
    NONE = 0

    TYPE_ANNOTATED = enum.auto()   # node has a type (x_type)
    VALUE_ANNOTATED = enum.auto()  # node may have a comptime value (x_value)
    SYMBOL_ANNOTATED = enum.auto()  # node reference a XXX_SYM_DEF node (x_symbol)
    # possibly uniquified name of module, use during code-gen
    SYMTAB_ANNOTATED = enum.auto()

    # Temporary annotations
    # node reference to the imported module (x_module)
    MODULE_ANNOTATED = enum.auto()
    # reference to the import node resolving the qualifier  (x_import)
    IMPORT_ANNOTATED = enum.auto()
    POLY_MOD_ANNOTATED = enum.auto()

    # Node families
    MAY_BE_LHS = enum.auto()
    TYPE_CORPUS = enum.auto()
    CONTROL_FLOW = enum.auto()
    GLOBAL_SYM_DEF = enum.auto()
    LOCAL_SYM_DEF = enum.auto()
    TOP_LEVEL = enum.auto()
    MACRO_BODY_ONLY = enum.auto()
    TO_BE_EXPANDED = enum.auto()
    # all non-core nodes will be stripped or converted to core nodes before code-gen
    NON_CORE = enum.auto()


NF_EXPR = NF.VALUE_ANNOTATED | NF.TYPE_ANNOTATED


@enum.unique
class GROUP(enum.IntEnum):
    """Node Family"""
    Misc = enum.auto()
    Type = enum.auto()
    Statement = enum.auto()
    Value = enum.auto()
    Expression = enum.auto()
    Macro = enum.auto()


@enum.unique
class BINARY_EXPR_KIND(enum.Enum):
    """same type two operand expressions"""
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    MOD = 5
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

    ROTR = 42    # >>>
    ROTL = 43    # <<<

    PDELTA = 52  # pointer delta result is sint

    def ResultIsBool(self) -> bool:
        return BINARY_EXPR_KIND.EQ.value <= self.value <= BINARY_EXPR_KIND.ORSC.value

    def OpsHaveSameType(self) -> bool:
        return self is not BINARY_EXPR_KIND.PDELTA


BINARY_EXPR_SHORTCUT = {
    #
    "<<": BINARY_EXPR_KIND.SHL,
    ">>": BINARY_EXPR_KIND.SHR,
    "<<<": BINARY_EXPR_KIND.ROTL,
    ">>>": BINARY_EXPR_KIND.ROTR,
    #
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
    "%": BINARY_EXPR_KIND.MOD,
    #
    "max": BINARY_EXPR_KIND.MAX,
    "min": BINARY_EXPR_KIND.MIN,
    #
    "&&": BINARY_EXPR_KIND.ANDSC,
    "||": BINARY_EXPR_KIND.ORSC,

    #
    "&": BINARY_EXPR_KIND.AND,
    "|": BINARY_EXPR_KIND.OR,
    "~": BINARY_EXPR_KIND.XOR,
    #
    "ptr_diff": BINARY_EXPR_KIND.PDELTA,
}

BINARY_EXPR_SHORTCUT_INV = {v: k for k, v in BINARY_EXPR_SHORTCUT.items()}


@enum.unique
class POINTER_EXPR_KIND(enum.Enum):
    """pointer and int two operand expressions"""
    INVALID = 0
    INCP = 1   # pointer add int
    DECP = 2   # pointer sub int


POINTER_EXPR_SHORTCUT = {
    #
    "ptr_inc": POINTER_EXPR_KIND.INCP,
    "ptr_dec": POINTER_EXPR_KIND.DECP,
}

POINTER_EXPR_SHORTCUT_INV = {v: k for k, v in POINTER_EXPR_SHORTCUT.items()}


@enum.unique
class ASSIGNMENT_KIND(enum.Enum):
    """Compound Assignment Kinds"""
    INVALID = 0
    ADD = 1
    SUB = 2
    DIV = 3
    MUL = 4
    MOD = 5
    #
    MIN = 6
    MAX = 7
    #
    AND = 10
    OR = 11
    XOR = 12
    #
    SHR = 40    # >>
    SHL = 41    # <<
    ROTR = 42    # >>
    ROTL = 43    # <<


ASSIGNMENT_SHORTCUT = {
    #
    "+=": ASSIGNMENT_KIND.ADD,
    "-=": ASSIGNMENT_KIND.SUB,
    "*=": ASSIGNMENT_KIND.MUL,
    "/=": ASSIGNMENT_KIND.DIV,
    "%=": ASSIGNMENT_KIND.MOD,
    "min=": ASSIGNMENT_KIND.MIN,
    "max=": ASSIGNMENT_KIND.MAX,
    #
    "&=": ASSIGNMENT_KIND.AND,
    "|=": ASSIGNMENT_KIND.OR,
    "~=": ASSIGNMENT_KIND.XOR,
    #
    "<<=": ASSIGNMENT_KIND.SHL,
    ">>=": ASSIGNMENT_KIND.SHR,
    "<<<=": ASSIGNMENT_KIND.ROTL,
    ">>>=": ASSIGNMENT_KIND.ROTR,
}

ASSIGNMENT_SHORTCUT_INV = {v: k for k, v in ASSIGNMENT_SHORTCUT.items()}

COMPOUND_KIND_TO_EXPR_KIND = {
    ASSIGNMENT_KIND.ADD: BINARY_EXPR_KIND.ADD,
    ASSIGNMENT_KIND.SUB: BINARY_EXPR_KIND.SUB,
    ASSIGNMENT_KIND.DIV: BINARY_EXPR_KIND.DIV,
    ASSIGNMENT_KIND.MUL: BINARY_EXPR_KIND.MUL,
    ASSIGNMENT_KIND.MOD: BINARY_EXPR_KIND.MOD,
    #
    ASSIGNMENT_KIND.AND: BINARY_EXPR_KIND.AND,
    ASSIGNMENT_KIND.OR: BINARY_EXPR_KIND.OR,
    ASSIGNMENT_KIND.XOR: BINARY_EXPR_KIND.XOR,
    #
    ASSIGNMENT_KIND.MAX: BINARY_EXPR_KIND.MAX,
    ASSIGNMENT_KIND.MIN: BINARY_EXPR_KIND.MIN,
    #
    ASSIGNMENT_KIND.SHR: BINARY_EXPR_KIND.SHR,
    ASSIGNMENT_KIND.SHL: BINARY_EXPR_KIND.SHL,
    ASSIGNMENT_KIND.ROTL: BINARY_EXPR_KIND.ROTL,
    ASSIGNMENT_KIND.ROTR: BINARY_EXPR_KIND.ROTR,
}


@enum.unique
class UNARY_EXPR_KIND(enum.Enum):
    """Unary Expression Kind for basic types"""
    INVALID = 0
    NOT = 1
    NEG = 2
    ABS = 3
    SQRT = 4


UNARY_EXPR_SHORTCUT_COMMON = {
    "!": UNARY_EXPR_KIND.NOT,
    "abs": UNARY_EXPR_KIND.ABS,
    "sqrt": UNARY_EXPR_KIND.SQRT,
}

# for sexpr we need to distinguish unary and binary minus
UNARY_EXPR_SHORTCUT_SEXPR = UNARY_EXPR_SHORTCUT_COMMON | {
    "neg": UNARY_EXPR_KIND.NEG}
UNARY_EXPR_SHORTCUT_CONCRETE = UNARY_EXPR_SHORTCUT_COMMON | {
    "-": UNARY_EXPR_KIND.NEG}

UNARY_EXPR_SHORTCUT_SEXPR_INV = {v: k for k,
                                 v in UNARY_EXPR_SHORTCUT_SEXPR.items()}

UNARY_EXPR_SHORTCUT_CONCRETE_INV = {
    v: k for k, v in UNARY_EXPR_SHORTCUT_CONCRETE.items()}


@enum.unique
class MOD_PARAM_KIND(enum.Enum):
    """Module Parameter Kind"""
    INVALID = 0
    CONST_EXPR = enum.auto()
    TYPE = enum.auto()


@enum.unique
class MACRO_PARAM_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = 0
    ID = enum.auto()
    EXPR = enum.auto()
    FIELD = enum.auto()
    TYPE = enum.auto()
    ID_DEF = enum.auto()      # an id the results in a DefVar being created inside the macro
    STMT_LIST = enum.auto()   # list of statements must be last
    EXPR_LIST_REST = enum.auto()   # must be last parameter


@enum.unique
class MACRO_RESULT_KIND(enum.Enum):
    """Macro Parameter Kinds"""
    INVALID = 0
    STMT = enum.auto()
    STMT_LIST = enum.auto()
    EXPR = enum.auto()
    EXPR_LIST = enum.auto()
    TYPE = enum.auto()

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
    """Node Field Descriptor Kind"""
    INVALID = 0
    STR = enum.auto()
    NAME = enum.auto()

    ATTR_BOOL = enum.auto()  # usually specified via @XXX
    ATTR_STR = enum.auto()  # usually specified via @XXX=YYY
    KIND = enum.auto()  # some enum
    NODE = enum.auto()
    LIST = enum.auto()


@dataclasses.dataclass(frozen=True)
class NFD:
    """Node Field Descriptor"""
    kind: NFK
    name: str
    doc: str
    enum_kind: Any = None
    node_type: Any = None


def NfdStr(name, doc):
    return NFD(NFK.STR, name, doc)


def NfdName(name, doc):
    return NFD(NFK.NAME, name, doc)


def NfdAttrBool(name, doc):
    return NFD(NFK.ATTR_BOOL, name, doc)


def NfdAttrStr(name, doc):
    return NFD(NFK.ATTR_STR, name, doc)


def NfdKind(name, doc, enum_kind):
    return NFD(NFK.KIND, name, doc, enum_kind=enum_kind)


def _ExtractTypes(t):
    """Extract the actual type"""
    if isinstance(t, str):
        return t
    # we cannot test isinstance(t, Union) because Union is a special form
    return tuple([x.__forward_arg__ for x in t.__args__])


def NfdNode(name, doc, node_type):
    return NFD(NFK.NODE, name, doc, node_type=_ExtractTypes(node_type))


def NfdNodeList(name, doc, node_type):
    return NFD(NFK.LIST, name, doc, node_type=_ExtractTypes(node_type))


NODES_INITS_T: TypeAlias = "ValPoint"
NODES_FIELDS_T: TypeAlias = "RecField"
NODES_CASES_T: TypeAlias = "Case"
NODES_ITEMS_T: TypeAlias = "EnumVal"
NODES_PARAMS_MOD_T: TypeAlias = "ModParam"
NODES_PARAMS_MACRO_T: TypeAlias = "MacroParam"
NODES_PARAMS_T: TypeAlias = "FunParam"
#
NODES_BODY_MOD_T = Union["DefFun", "DefRec", "DefEnum", "DefVar", "DefMacro", "DefType",
                         "DefGlobal", "StmtStaticAssert", "Import"]

NODES_BODY_T = Union["StmtDefer", "StmtIf", "StmtBreak", "StmtContinue", "StmtReturn",
                     "StmtExpr",
                     "StmtCompoundAssignment", "StmtBlock", "StmtCond", "DefVar",
                     "StmtAssignment", "StmtTrap"]


NODES_TYPES_T = Union["TypeBase", "TypeSpan", "TypeVec", "TypePtr", "TypeFun", "Id",
                      "TypeUnion", "TypeOf", "TypeUnionDelta"]

NODES_TYPES_OR_AUTO_T = Union[NODES_TYPES_T, "TypeAuto"]

NODES_VAL_T = Union["ValFalse", "ValTrue", "ValNum",
                    "ValVoid", "ValCompound", "ValString", "ValSpan"]

NODES_EXPR_T = Union[NODES_VAL_T,
                     #
                     "Id", "ExprAddrOf", "ExprDeref", "ExprIndex",
                     "ExprField", "ExprCall", "ExprParen",
                     "Expr1", "Expr2", "Expr3", "ExprPointer",
                     "ExprLen", "ExprFront",
                     "ExprTypeId", "ExprSizeof", "ExprOffsetof", "ExprStmt",
                     "ExprStringify",
                     "ExprUnionTag", "ExprUnionUntagged", "ExprUnsafeCast",
                     "ExprIs", "ExprAs", "ExprWrap", "ExprUnwrap", "ExprNarrow",
                     "ExprWiden", "ExprBitCast"]

NODES_EXPR_OR_AUTO_T = Union[NODES_EXPR_T, "ValAuto"]

NODES_EXPR_OR_UNDEF_T = Union[NODES_EXPR_T, "ValUndef"]

NODES_EXPR_OR_UNDEF_OR_AUTO_T = Union[NODES_EXPR_T, "ValUndef", "ValAuto"]

NODES_BODY_MACRO_T = Union[NODES_BODY_T, NODES_EXPR_T, "MacroFor", "MacroId"]


NODES_COND_T = Union["ValFalse", "ValTrue",
                     #
                     "Id", "ExprDeref", "ExprIndex",
                     "ExprField", "ExprCall", "ExprParen",
                     "Expr1", "Expr2", "Expr3",
                     "ExprStmt", "ExprIs", "ExprNarrow"]

NODES_LHS_T = Union["Id", "ExprDeref", "ExprIndex", "ExprField", "ExprParen"]

NODES_SYMBOLS_T = Union["DefEnum", "EnumVal", "DefType", "DefVar", "DefGlobal", "DefFun",
                        "FunParam", "ModParam",
                        "DefMod", "MacroParam", "DefMacro", "Import", "DefRec"]


def _EnumValues(enum_class):
    return ", ".join(x.name for x in enum_class if x.value != 0)


ALL_FIELDS = [
    NfdName("name", "name of the object"),
    NfdName("enum_name", "optional enum element name"),
    NfdName("name_list", "name of the object list"),
    NfdName("label", "block  name (if not empty)"),
    NfdName("target",
            "name of enclosing while/for/block to brach to (empty means nearest)"),

    NfdStr("number", "a number"),
    NfdStr("string", "string literal"),
    NfdStr("message", "message for assert failures"),

    NfdStr("path", "TBD"),
    #
    # order of the attribute should match the order in the node class definition
    # as we use it for pretty printing.
    #
    NfdAttrBool("builtin", "module is the builtin module"),
    NfdAttrBool("init", "run function at startup"),
    NfdAttrBool("fini", "run function at shutdown"),
    NfdAttrBool("extern", "is external function (empty body)"),
    NfdAttrBool("cdecl", "use c-linkage (no module prefix)"),
    NfdAttrBool("poly", "is polymorphic function"),
    #
    NfdAttrBool("pub", "has public visibility"),
    NfdAttrBool("mut", "is mutable"),
    NfdAttrBool("preserve_mut", "result type is mutable if underlying type is"),
    NfdAttrBool("ref", "address may be taken"),
    NfdAttrBool("colon", "colon style list"),
    NfdAttrBool("wrapped", "is wrapped type (forces type equivalence by name)"),

    NfdAttrBool("unchecked", "array acces is not checked"),
    NfdAttrBool("untagged", "union type is untagged"),
    NfdAttrBool("arg_ref", "in parameter was converted for by-val to pointer"),
    NfdAttrBool("res_ref", "in parameter was converted for by-val to pointer"),
    NfdAttrStr("doc", "possibly multi-line comment"),

    #
    NfdKind("unary_expr_kind",
            f"one of: [{_EnumValues(UNARY_EXPR_KIND)}](#expr1-kind)",
            UNARY_EXPR_KIND),
    NfdKind("binary_expr_kind",
            f"one of: [{_EnumValues(BINARY_EXPR_KIND)}](#expr2-kind)",
            BINARY_EXPR_KIND),
    NfdKind("base_type_kind",
            f"one of: [{_EnumValues(BASE_TYPE_KIND)}](#base-type-kind)",
            BASE_TYPE_KIND),
    NfdKind("mod_param_kind",
            f"one of: [{_EnumValues(MOD_PARAM_KIND)}](#modparam-kind)",
            MOD_PARAM_KIND),
    NfdKind("assignment_kind",
            f"one of: [{_EnumValues(ASSIGNMENT_KIND)
                        }](#stmtcompoundassignment-kind)",
            ASSIGNMENT_KIND),
    NfdKind("macro_param_kind",
            f"one of: [{_EnumValues(MACRO_PARAM_KIND)}](#macro-param-kind)",
            MACRO_PARAM_KIND),
    NfdKind("macro_result_kind",
            f"one of: [{_EnumValues(MACRO_RESULT_KIND)}](#macro-result-kind)",
            MACRO_RESULT_KIND),
    NfdKind("pointer_expr_kind",
            f"one of: [{_EnumValues(POINTER_EXPR_KIND)}](#pointerop-kind)",
            POINTER_EXPR_KIND),


    #
    # TODO: fix all the None below
    NfdNodeList("params", "function parameters and/or comments",
                NODES_PARAMS_T),
    NfdNodeList("params_mod", "module template parameters",
                NODES_PARAMS_MOD_T),
    NfdNodeList("params_macro", "macro parameters", NODES_PARAMS_MACRO_T),
    NfdNodeList("args", "function call arguments", NODES_EXPR_T),
    NfdNodeList("args_mod", "module arguments",
                Union[NODES_EXPR_T, NODES_TYPES_T]),
    NfdNodeList("items", "enum items and/or comments", NODES_ITEMS_T),
    NfdNodeList("fields", "record fields and/or comments", NODES_FIELDS_T),
    NfdNodeList("types", "union types", NODES_TYPES_T),
    NfdNodeList("inits", "rec initializers and/or comments", NODES_INITS_T),
    NfdNodeList("gen_ids",
                "name placeholder ids to be generated at macro instantiation time",
                "MacroId"),

    #
    NfdNodeList("body_mod",
                "toplevel module definitions and/or comments", NODES_BODY_MOD_T),
    NfdNodeList(
        "body", "new scope: statement list and/or comments", NODES_BODY_T),
    NfdNodeList("body_t",
                "new scope: statement list and/or comments for true branch", NODES_BODY_T),
    NfdNodeList("body_f",
                "new scope: statement list and/or comments for false branch", NODES_BODY_T),
    NfdNodeList("body_for", "statement list for macro_loop", NODES_BODY_T),
    NfdNodeList("body_macro",
                "new scope: macro statments/expression", NODES_BODY_MACRO_T),
    NfdNodeList("cases", "list of case statements", NODES_CASES_T),

    #
    NfdNode("field", "record field", "Id"),
    NfdNode("point",
            "compound initializer index/field or auto (meaning next pos)", NODES_EXPR_OR_AUTO_T),
    NfdNode("type", "type expression", NODES_TYPES_T),
    NfdNode("subtrahend", "type expression", NODES_TYPES_T),
    NfdNode("type_or_auto", "type expression", NODES_TYPES_OR_AUTO_T),
    NfdNode("result", "return type", NODES_TYPES_T),
    NfdNode("size", "compile-time constant size", NODES_EXPR_T),
    NfdNode("expr_size", "expression determining the size or auto",
            NODES_EXPR_OR_AUTO_T),
    NfdNode("expr_index",
            "expression determining the index to be accessed", NODES_EXPR_T),
    NfdNode("expr", "expression", NODES_EXPR_T),
    NfdNode("cond", "conditional expression must evaluate to a boolean", NODES_COND_T),
    NfdNode("expr_t",
            "expression (will only be evaluated if cond == true)", NODES_EXPR_T),
    NfdNode("expr_f",
            "expression (will only be evaluated if cond == false)", NODES_EXPR_T),
    NfdNode("expr1", "left operand expression", NODES_EXPR_T),
    NfdNode("expr2", "right operand expression", NODES_EXPR_T),
    NfdNode("expr_bound_or_undef", "", NODES_EXPR_OR_UNDEF_T),
    NfdNode("expr_rhs", "rhs of assignment", NODES_EXPR_T),
    NfdNode("expr_ret", "result expression (ValVoid means no result)", NODES_EXPR_T),
    NfdNode("pointer", "pointer component of span", NODES_EXPR_T),
    NfdNode("container", "vec and span", NODES_EXPR_T),
    NfdNode(
        "callee", "expression evaluating to the function to be called", NODES_EXPR_T),
    NfdNode("value_or_auto", "enum constant or auto", NODES_EXPR_OR_AUTO_T),
    NfdNode("value_or_undef", "", NODES_EXPR_OR_UNDEF_T),
    NfdNode("lhs", "l-value expression", NODES_LHS_T),
    NfdNode("expr_lhs", "l-value expression", NODES_LHS_T),
    NfdNode("initial_or_undef_or_auto", "initializer",
            NODES_EXPR_OR_UNDEF_OR_AUTO_T),
]

NEW_SCOPE_FIELDS = set(["body", "body_f", "body_t", "body_macro"])

TYPE_FIELDS = set(["type", "types", "result", "type_or_auto", "subtrahend"])


FIELD_NAME_FIELDS = set(["point", "field"])

ALL_FIELDS_MAP: dict[str, NFD] = {nfd.name: nfd for nfd in ALL_FIELDS}


# Optional fields must come last in a dataclass
_OPTIONAL_FIELDS = {
    "expr_ret": "@ValVoid",
    "value_or_auto": "@ValAuto",
    "target": "@EmptyName",
    "path": "",
    "message": "",
    "initial_or_undef_or_auto": "@ValAuto",
    "point": "@ValAuto",
    "inits": "@EmptyList",
    "expr_bound_or_undef": "@ValUndef",
    "args_mod": "@EmptyList",
}


def GetOptional(field: str, srcloc):
    e: Union[None, str] = _OPTIONAL_FIELDS.get(field)
    if e is None:
        return e

    assert isinstance(e, str)
    if e == "@EmptyList":
        return []
    elif e == "":
        return ""
    elif e == "@ValVoid":
        return ValVoid(x_srcloc=srcloc)
    elif e == "@ValAuto":
        return ValAuto(x_srcloc=srcloc)
    elif e == "@ValUndef":
        return ValUndef(x_srcloc=srcloc)
    elif e == "@EmptyName":
        return EMPTY_NAME
    else:
        assert False


def IsFieldWithDefaultValue(field, val):
    e = _OPTIONAL_FIELDS.get(field)
    if e is None:
        return False

    assert isinstance(e, str)
    if e == "@EmptyList":
        return len(val) == 0
    elif e == "":
        return val == ""
    elif e == "@ValVoid":
        return isinstance(val, ValVoid)
    elif e == "@ValAuto":
        return isinstance(val, ValAuto)
    elif e == "@ValUndef":
        return isinstance(val, ValUndef)
    elif e == "@EmptyName":
        return val.name == ""
    else:
        assert False


X_FIELDS = {

    ################################################
    # VeryCommon
    ################################################
    "x_srcloc": None,  # set by cwast.py
    # set by eval.py
    # ExprXXX ->
    "x_value": NF.VALUE_ANNOTATED,
    # set by typify.py
    "x_type": NF.TYPE_ANNOTATED,
    ################################################
    # Only used until typing is complete
    # set by mod_pool.py
    ################################################
    # Id, DefFun, MacroInvoke -> Import
    # (if name is qualified)
    "x_import": NF.IMPORT_ANNOTATED,
    "x_poly_mod": NF.POLY_MOD_ANNOTATED,
    # Import -> DefMod (imported module)
    "x_module": NF.MODULE_ANNOTATED,
    # DefMod -> (global) SymTab
    "x_symtab": NF.SYMTAB_ANNOTATED,
    ################################################
    # The x_XXX below point to other Nodes
    ################################################
    # set by symbolize.py
    # Id -> Node in GLOBAL_SYM_DEF/LOCAL_SYM_DEF group
    "x_symbol": NF.SYMBOL_ANNOTATED,
    # set by symbolize.py
    # linksbreak/continue/return -> nodes to enclosing node (DefFun, StmtBlock)
    "x_target": NF.CONTROL_FLOW,
    ################################################
    # Could live in the same union as last group
    ################################################
    # set by typify.py
    # RecField -> int
    "x_offset": NF.TYPE_CORPUS,   # oddball, should be moved into types

}


def NODE_NAME(node):
    if node.ALIAS:
        return "[" + node.ALIAS + "]"
    return "[" + node.__class__.__name__ + "]"


def _FLAGS(node):
    out = []
    for nfd in node.__class__.ATTRS:
        if getattr(node, nfd.name):
            out.append(ANNOTATION_PREFIX + nfd.name)
    outs = " ".join(out)
    return " " + outs if outs else outs


# maps node class name and aliases to class
NODES_ALIASES = {}

ALL_NODES = set()


def _CheckNodeFieldOrder(cls):
    """
    order is
    * regular
    * optional
    * flags
    * x_
    """
    optionals = 0
    regulars = 0
    flags = 0
    xs = 0
    for field, node_type in cls.__annotations__.items():
        if field in ('ALIAS', 'GROUP', 'FLAGS'):
            continue
        if field.startswith("x_"):
            assert field in X_FIELDS, f"unexpected x-field: {
                field} in node {node_type}"
            if field != "x_srcloc":
                flag_kind = X_FIELDS[field]
                assert flag_kind in cls.FLAGS, f"{cls}: {
                    field} missing flag {flag_kind}"
            xs += 1
            continue
        nfd = ALL_FIELDS_MAP[field]
        if field in _OPTIONAL_FIELDS:
            optionals += 1
            assert flags + xs == 0, f"{cls}: {field}"
        elif nfd.kind is NFK.ATTR_BOOL or nfd.kind is NFK.ATTR_STR:
            flags += 0
            assert xs == 0
        else:
            regulars += 1
            assert optionals + flags + xs == 0


def NodeCommon(cls: Any):
    cls.__eq__ = lambda a, b: id(a) == id(b)
    cls.__hash__ = lambda a: id(a)

    assert hasattr(cls, "ALIAS") and hasattr(
        cls, "FLAGS") and hasattr(cls, "GROUP")
    assert hasattr(cls, "x_srcloc"), f"class is missing x_srcloc {cls}"
    if cls.GROUP is GROUP.Statement:
        assert hasattr(cls, "doc"), f"mising doc {cls.__name__}"
    _CheckNodeFieldOrder(cls)

    ALL_NODES.add(cls)
    NODES_ALIASES[cls.__name__] = cls

    if cls.ALIAS is not None:
        NODES_ALIASES[cls.ALIAS] = cls
    cls.FIELDS = []
    cls.ATTRS = []
    cls.NODE_FIELDS = []
    for field, _ in cls.__annotations__.items():
        if field in ('ALIAS', 'GROUP', 'FLAGS'):
            continue
        if field.startswith("x_"):
            continue
        nfd: NFD = ALL_FIELDS_MAP[field]
        assert nfd.name == field

        kind = nfd.kind
        if kind is NFK.ATTR_BOOL or kind is NFK.ATTR_STR:
            cls.ATTRS.append(nfd)
        else:
            cls.FIELDS.append(nfd)
            if kind is NFK.NODE or kind is NFK.LIST:
                cls.NODE_FIELDS.append(nfd)
    return cls

############################################################
# Typing
############################################################


@enum.unique
class UnionKind(enum.Enum):
    """Union Kind"""
    INVALID = 0
    NORMAL = enum.auto()
    TAG_ONLY = enum.auto()
    POINTER = enum.auto()


def align(x, a):
    return (x + a - 1) // a * a


@dataclasses.dataclass()
class CanonType:
    """Canonical Type"""
    # type of node, e.g. DefRec, TypeBase, TypeUnion, TypeSpan, etc.
    node: Any
    name: str
    #
    mut: bool = False
    dim: int = -1
    untagged: bool = False
    base_type_kind: BASE_TYPE_KIND = BASE_TYPE_KIND.INVALID
    children: list["CanonType"] = dataclasses.field(default_factory=list)
    #
    ast_node: Optional[Union["DefRec", "DefEnum"]] = None
    # we may rewrite spans and unions into recs
    # this provides a way to access the original type (mostly its typeid)
    original_type: Optional["CanonType"] = None
    replacement_type: Optional["CanonType"] = None
    # The fields below are filled during finalization
    alignment: int = -1
    size: int = -1
    register_types: Optional[list[Any]] = None
    typeid: int = -1
    union_kind: UnionKind = UnionKind.INVALID

    def __hash__(self):
        return hash(self.name)

    def is_bool(self) -> bool:
        return self.base_type_kind is BASE_TYPE_KIND.BOOL

    def is_void(self) -> bool:
        return self.base_type_kind is BASE_TYPE_KIND.VOID

    def is_int(self) -> bool:
        return self.base_type_kind.IsInt()

    def is_uint(self) -> bool:
        return self.base_type_kind.IsUint()

    def is_sint(self) -> bool:
        return self.base_type_kind.IsSint()

    def is_real(self) -> bool:
        return self.base_type_kind.IsReal()

    def is_number(self) -> bool:
        return self.base_type_kind.IsNumber()

    def is_wrapped(self) -> bool:
        return self.node is DefType

    def underlying_wrapped_type(self) -> "CanonType":
        assert self.is_wrapped()
        return self.children[0]

    def is_fun(self) -> bool:
        return self.node is TypeFun

    def is_rec(self) -> bool:
        return self.node is DefRec

    def parameter_types(self) -> list["CanonType"]:
        assert self.is_fun()
        return self.children[:-1]

    def result_type(self) -> "CanonType":
        assert self.is_fun()
        return self.children[-1]

    def is_pointer(self) -> bool:
        return self.node is TypePtr

    def is_span(self) -> bool:
        return self.node is TypeSpan

    def is_enum(self) -> bool:
        return self.node is DefEnum

    def is_base_type(self) -> bool:
        return self.node is TypeBase

    def is_base_or_enum_type(self) -> bool:
        return self.node is TypeBase or self.node is DefEnum

    def is_union(self) -> bool:
        return self.node is TypeUnion

    def is_untagged_union(self) -> bool:
        return self.node is TypeUnion and self.untagged

    def is_tagged_union(self) -> bool:
        return self.node is TypeUnion and not self.untagged

    def union_member_types(self) -> list["CanonType"]:
        assert self.is_union()
        return self.children

    def is_vec(self) -> bool:
        return self.node is TypeVec

    def is_void_or_wrapped_void(self) -> bool:
        if self.node is DefType:
            return self.children[0].is_void()
        return self.is_void()

    def underlying_pointer_type(self) -> "CanonType":
        assert self.is_pointer()
        return self.children[0]

    def underlying_span_type(self) -> "CanonType":
        assert self.is_span()
        return self.children[0]

    def underlying_array_type(self) -> "CanonType":
        assert self.is_vec()
        return self.children[0]

    def is_vec_or_span(self) -> bool:
        return self.node is TypeVec or self.node is TypeSpan

    def underlying_vec_or_span_type(self) -> "CanonType":
        assert self.is_vec() or self.is_span()
        return self.children[0]

    def contained_type(self) -> "CanonType":
        if self.node is TypeVec or self.node is TypeSpan:
            return self.children[0]
        else:
            assert False, f"expected vec or span type: {self.name}"

    def aligned_size(self) -> int:
        # somtimes we need to round up. e.g. struct {int32, int8} needs 3 bytes padding
        return align(self.size, self.alignment)

    def array_dim(self):
        assert self.is_vec()
        return self.dim

    def array_element_size(self):
        assert self.is_vec()
        return self.size // self.dim

    def is_mutable(self) -> bool:
        return self.mut

    def fits_in_register(self) -> bool:
        reg_type = self.register_types
        return reg_type is not None and len(reg_type) == 1

    def get_single_register_type(self) -> str:
        reg_type = self.register_types
        assert reg_type is not None and len(reg_type) == 1, f"{
            self} {reg_type}"
        return reg_type[0]

    def get_original_typeid(self):
        if not self.original_type:
            return self.typeid
        else:
            return self.original_type.get_original_typeid()

    def set_union_kind(self):
        seen_pointer = False
        for t in self.union_member_types():
            if t.is_wrapped():
                t = t.children[0]
            if t.is_void():
                continue
            elif t.is_pointer():
                if seen_pointer:
                    return UnionKind.NORMAL
                seen_pointer = True
            else:
                return UnionKind.NORMAL
        if seen_pointer:
            return UnionKind.POINTER
        return UnionKind.TAG_ONLY

    def finalize(self, size: int, alignment: int, register_types):
        # self.typeid = typeid
        self.size = size
        self.alignment = alignment
        self.register_types = register_types

    def __str__(self):
        return self.name + ("☠" if self.replacement_type else " ")


NO_TYPE = CanonType(None, "@invali@d")


@dataclasses.dataclass(frozen=True)
class SrcLoc:
    filename: str
    lineno: int

    def __str__(self):
        return f"{self.filename}({self.lineno})"


INVALID_SRCLOC: Final[SrcLoc] = SrcLoc("@unknown@", 0)
SRCLOC_GENERATED: Final[SrcLoc] = SrcLoc("@generated@", 0)

############################################################
# Emphemeral
############################################################


@NodeCommon
@dataclasses.dataclass()
class EphemeralList:
    """Only exist in the context of macro parameters:
       STMT_LIST, EXPR_LIST, EXPR_LIST_REST
       and is not used after macro expansion


    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Macro
    FLAGS: ClassVar = NF.NON_CORE
    #
    args: list[Any]
    #
    colon: bool = False  # orignated from a STMT_LIST
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

############################################################
#
############################################################


@NodeCommon
@dataclasses.dataclass()
class ModParam:
    """Module Parameters"""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.GLOBAL_SYM_DEF | NF.NON_CORE
    #
    name: NAME
    mod_param_kind: MOD_PARAM_KIND
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name} {self.mod_param_kind.name}"


@NodeCommon
@dataclasses.dataclass()
class DefMod:
    """Module Definition

    The module is a template if `params` is non-empty

    ordering is used to put the modules in a deterministic order
    """
    ALIAS: ClassVar = "module"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.GLOBAL_SYM_DEF | NF.SYMTAB_ANNOTATED
    #
    name: NAME
    params_mod: list[NODES_PARAMS_MOD_T]
    body_mod: list[NODES_BODY_MOD_T]
    #
    doc: str = ""
    builtin: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_symtab: Any = None

    def __lt__(self, other):
        return self.name.name < other.name.name

    def __repr__(self):
        params = ', '.join(str(p) for p in self.params_mod)
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name} [{params}]"


INVALID_MOD = DefMod(NAME("INVALID_MOD"), [], [])
############################################################
#
############################################################


@NodeCommon
@dataclasses.dataclass()
class Import:
    """Import another Module from `path` as `name`"""
    ALIAS: ClassVar = "import"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.GLOBAL_SYM_DEF | NF.NON_CORE | NF.MODULE_ANNOTATED
    #
    name: NAME
    path: str
    args_mod: list[NODES_EXPR_T]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_module: DefMod = INVALID_MOD

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}  path={self.path}"


@NodeCommon
@dataclasses.dataclass()
class RecField:  #
    """Record field

    All fields must be explicitly initialized. Use `ValUndef` in performance
    sensitive situations.
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    name: NAME
    type: NODES_TYPES_T
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_offset: int = -1

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}: {self.type}"


@NodeCommon
@dataclasses.dataclass()
class DefRec:
    """Record definition"""
    ALIAS: ClassVar = "rec"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    name: NAME
    fields: list[NODES_FIELDS_T]
    #
    pub:  bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name}"


############################################################
# Identifier
############################################################


INVALID_SYMBOL = None  # forward declaration


@NodeCommon
@dataclasses.dataclass()
class Id:
    """Refers to a type, variable, constant, function, module by name.

    Ids may contain a path component indicating which modules they reference.
    If the path component is missing the Id refers to the current module.

    id or mod::id or enum::id or mod::enum:id
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Misc
    FLAGS: ClassVar = NF_EXPR | NF.SYMBOL_ANNOTATED | NF.MAY_BE_LHS | NF.IMPORT_ANNOTATED
    #
    name: NAME
    enum_name: Optional[NAME]
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None
    x_symbol: NODES_SYMBOLS_T = INVALID_SYMBOL
    x_import: Optional[Import] = None  # which import the id is qualified with

    def GetRecFieldRef(self) -> RecField:
        assert isinstance(self.x_symbol, RecField)
        return self.x_symbol

    def IsMacroCall(self):
        return self.name.IsMacroCall() or self.name.name in BUILT_IN_EXPR_MACROS

    def FullName(self):
        name = str(self.name)
        if self.enum_name:
            name += f":{self.enum_name}"
        return name

    def GetBaseNameStrict(self):
        assert self.enum_name is None
        return self.name

    @staticmethod
    def Make(name: str, **kwargs):
        assert not name.startswith(MACRO_VAR_PREFIX)
        enum_name = None
        pos = name.rfind(":")
        if pos > 0 and name[pos - 1] != ":":
            enum_name = NAME.Make(name[pos + 1:])
            name = name[:pos]
        return Id(NAME.Make(name), enum_name, **kwargs)

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.FullName()}"


@NodeCommon
@dataclasses.dataclass()
class TypeAuto:
    """Placeholder for an unspecified (auto derived) type

    My only occur where explicitly allowed.
    """
    ALIAS: ClassVar = "auto"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}"


############################################################
# TypeNodes
############################################################
@NodeCommon
@dataclasses.dataclass()
class FunParam:
    """Function parameter

    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF
    #
    name: NAME
    type: NODES_TYPES_T
    #
    arg_ref: bool = False
    res_ref: bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}: {self.type}"


@NodeCommon
@dataclasses.dataclass()
class TypeBase:
    """Base type

    One of: void, bool, r32, r64, u8, u16, u32, u64, s8, s16, s32, s64
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    base_type_kind: BASE_TYPE_KIND
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.base_type_kind.name}"


@NodeCommon
@dataclasses.dataclass()
class TypePtr:
    """Pointer type
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    type: NODES_TYPES_T
    #
    mut: bool = False  # pointee is mutable
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.type}"


@NodeCommon
@dataclasses.dataclass()
class TypeSpan:
    """A span (view) of a vec with compile-time unknown dimensions

    Internally, this is tuple of `start` and `length`
    (mutable/non-mutable)"union
    """
    ALIAS: ClassVar = "span"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.NON_CORE
    #
    type: NODES_TYPES_T
    #
    mut: bool = False  # span is mutable
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        mod = "-MUT" if self.mut else ""
        return f"{NODE_NAME(self)}{mod}({self.type})"


@NodeCommon
@dataclasses.dataclass()
class TypeVec:
    """An array of the given type and `size`

    """
    ALIAS: ClassVar = "vec"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    size: "NODES_EXPR_T"      # must be const and unsigned
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)} ({self.type}) {self.size}"


@NodeCommon
@dataclasses.dataclass()
class TypeFun:
    """A function signature

    The `FunParam.name` field is ignored and should be `_`
    """
    ALIAS: ClassVar = "funtype"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    params: list[NODES_PARAMS_T]
    result: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        t = [str(t) for t in self.params]
        return f"{NODE_NAME(self)} {' '.join(t)} -> {self.result}"


@NodeCommon
@dataclasses.dataclass()
class TypeUnion:
    """Union types (tagged unions)

    Unions are "auto flattening", e.g.
    union(a, union(b,c), union(a, d)) == union(a, b, c, d)

    union! indicates an untagged union
    """
    ALIAS: ClassVar = "union"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS
    #
    types: list[NODES_TYPES_T]
    #
    untagged: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        t = [str(t) for t in self.types]
        extra = "-untagged" if self.untagged else ""
        return f"{NODE_NAME(self)}{extra} {' '.join(t)}"


@NodeCommon
@dataclasses.dataclass()
class TypeUnionDelta:
    """Type resulting from the difference of TypeUnion and a non-empty subset sets of its members
    """
    ALIAS: ClassVar = "union_delta"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.NON_CORE
    #
    type: NODES_TYPES_T
    subtrahend: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{self.type} - {self.subtrahend}"


@NodeCommon
@dataclasses.dataclass()
class TypeOf:
    """(Static) type of the expression. Computed at compile-time.
    The underlying expression is not evaluated.
    """
    ALIAS: ClassVar = "type_of"
    GROUP: ClassVar = GROUP.Type
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.NON_CORE
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}"
############################################################
# Val Nodes
############################################################


@NodeCommon
@dataclasses.dataclass()
class ValAuto:
    """Placeholder for an unspecified (auto derived) value

    Used for: array dimensions, enum values, chap and range
    """
    ALIAS: ClassVar = "auto_val"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class ValTrue:
    """Bool constant `true`"""
    ALIAS: ClassVar = "true"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class ValFalse:
    """Bool constant `false`"""
    ALIAS: ClassVar = "false"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class ValNum:
    """Numeric constant (signed int, unsigned int, real

    Underscores in `number` are ignored. `number` can be explicitly typed via
    suffices like `_u64`, `_s16`, `_r32`.
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    number: str   # maybe a (unicode) character as well
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.number}"


@NodeCommon
@dataclasses.dataclass()
class ValUndef:
    """Special constant to indiciate *no default value*
    """
    ALIAS: ClassVar = "undef"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF.VALUE_ANNOTATED
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_value: Optional[Any] = None    # this is always a ValUndef() object

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class ValVoid:
    """Only value inhabiting the `TypeVoid` type

    It can be used to model *null* in nullable pointers via a union type.
     """
    ALIAS: ClassVar = "void_val"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class ValPoint:
    """Component of a ValCompound

    The `point` is optional and `ValAuto` if not used.
    It indicates which slot of the ValCompound is being initialized.
    For Recs it represents a field name  for Vecs an index which must be
    a compile-time constant
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    value_or_undef: NODES_EXPR_T
    point: NODES_EXPR_OR_AUTO_T  # compile time constant
    #
    doc: str = ""
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} [{self.point}] = {self.value_or_undef}"


@NodeCommon
@dataclasses.dataclass()
class ValCompound:
    """A compound (Rec or Vec) literal
    e.g.
    `{[10]int : 1 = 5, 2 = 6, 77}`
    or
    `{Point3 : x = 5, y = 8, z = 12}`
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    type_or_auto: NODES_TYPES_OR_AUTO_T
    inits: list[NODES_INITS_T]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} type={self.type_or_auto}"


@NodeCommon
@dataclasses.dataclass()
class ValSpan:
    """A span value comprised of a pointer and length

    type and mutability is defined by the pointer
    """
    ALIAS: ClassVar = "make_span"
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    pointer: "NODES_EXPR_T"
    expr_size: "NODES_EXPR_T"
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.pointer} {self.expr_size}"


@NodeCommon
@dataclasses.dataclass()
class ValString:
    """An vec_val encoded as a string

    type is `[strlen(string)]u8`. `string` may be escaped/raw
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Value
    FLAGS: ClassVar = NF_EXPR
    #
    string: str
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def kind(self) -> str:
        out = self.string[0]
        return "" if out == '"' else out

    def payload(self):
        offset = len(self.kind())
        if self.string.endswith('"""'):
            return self.string[offset+3:-3]
        return self.string[offset + 1:-1]

    def get_bytes(self):
        s = self.payload()
        k = self.kind()
        if not all(ord(c) < 128 for c in s):
            CompilerError(
                self, "non-ascii chars currently not supported")
        if k == "r":
            return bytes(s, encoding="ascii")
        elif k == "x":
            return HexStringToBytes(s)
        return EscapedStringToBytes(s)

    def render(self):
        return self.string

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.string}"


def IsWellFormedStringLiteral(t: str):
    if t.endswith('"""'):
        return (len(t) >= 6 and t.startswith('"""') or
                len(t) >= 7 and t.startswith('r"""') or
                len(t) >= 7 and t.startswith('x"""'))
    elif t.endswith('"'):
        return (len(t) >= 2 and t.startswith('"') or
                len(t) >= 3 and t.startswith('r"') or
                len(t) >= 3 and t.startswith('x"'))
    else:
        return False


############################################################
# ExprNode
############################################################


@NodeCommon
@dataclasses.dataclass()
class ExprDeref:
    """Dereference a pointer represented by `expr`"""
    ALIAS: ClassVar = "^"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.MAY_BE_LHS
    #
    expr: NODES_EXPR_T  # must be of type AddrOf
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprAddrOf:
    """Create a pointer to object represented by `expr`

    Pointer can optionally point to a mutable object if the
    pointee is mutable. This is indicated using `@!`.
    """
    ALIAS: ClassVar = "@"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr_lhs: NODES_EXPR_T
    #
    mut: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.expr_lhs}"


@NodeCommon
@dataclasses.dataclass()
class ExprCall:
    """Function call expression.
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    callee: NODES_EXPR_T
    args: list[NODES_EXPR_T]
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.callee}"


@NodeCommon
@dataclasses.dataclass()
class ExprParen:
    """Used for preserving parenthesis in the source
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprField:
    """Access field in expression representing a record.
    """
    ALIAS: ClassVar = "."
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.MAY_BE_LHS
    #
    container: NODES_EXPR_T  # must be of type rec
    field: Id
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.container}  field:{self.field}"


@NodeCommon
@dataclasses.dataclass()
class Expr1:
    """Unary expression."""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    unary_expr_kind: UNARY_EXPR_KIND
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.unary_expr_kind} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprPointer:
    """Pointer arithmetic expression - optionally bound checked.."""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    pointer_expr_kind: POINTER_EXPR_KIND
    expr1: NODES_EXPR_T
    expr2: NODES_EXPR_T
    expr_bound_or_undef: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{self.pointer_expr_kind.name}({self.expr1}, {self.expr2}, {self.expr_bound_or_undef})"


@NodeCommon
@dataclasses.dataclass()
class Expr2:
    """Binary expression."""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    binary_expr_kind: BINARY_EXPR_KIND
    expr1: NODES_EXPR_T
    expr2: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{self.binary_expr_kind.name}({self.expr1}, {self.expr2})"


@NodeCommon
@dataclasses.dataclass()
class Expr3:
    """Tertiary expression (like C's `? :`)
    """
    ALIAS: ClassVar = "?"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    cond: NODES_EXPR_T  # must be of type  bool
    expr_t: NODES_EXPR_T
    expr_f: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"? {self.cond} {self.expr_t} {self.expr_f}"

# Array/Slice Expressions


@NodeCommon
@dataclasses.dataclass()
class ExprIndex:
    """Optionally unchecked indexed access of vec or span
    """
    ALIAS: ClassVar = "at"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.MAY_BE_LHS | NF.NON_CORE
    #
    container: NODES_EXPR_T  # must be of type span or vec
    expr_index: NODES_EXPR_T  # must be of int type
    #
    unchecked: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"AT {self.container} {self.expr_index}"


@NodeCommon
@dataclasses.dataclass()
class ExprLen:
    """Length of vec or span

    Result type is `uint`.
    """
    ALIAS: ClassVar = "len"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    container: NODES_EXPR_T   # must be of type span or vec
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return self.__class__.__name__
# Cast Like Expressions


@NodeCommon
@dataclasses.dataclass()
class ExprFront:
    """Address of the first element of an vec or span

    Similar to `@container[0]` but will not fail if container has zero size
    If the underlying container is mutable, then `front!` can be  used to
    obtain a mutable pointer.
    """
    ALIAS: ClassVar = "front"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    container: NODES_EXPR_T   # must be of type span or vec
    #
    mut: bool = False
    preserve_mut: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return self.__class__.__name__


# Cast Like Expressions
@NodeCommon
@dataclasses.dataclass()
class ExprIs:
    """Test actual expression (run-time) type

    Typically used when `expr` is a tagged union type.
    Otherwise, the node can be constant folded.

    `type` can be a tagged union itself.
    """
    ALIAS: ClassVar = "is"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprWrap:
    """Cast: underlying type -> enum/wrapped
    """
    ALIAS: ClassVar = "wrap_as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{self.expr} WRAP {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprUnwrap:
    """Cast: enum/wrapped -> underlying type
    """
    ALIAS: ClassVar = "unwrap"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprAs:
    """Safe Cast (Conversion)

    Allowed:
    u8-u64, s8-s64 <-> u8-u64, s8-s64
    u8-u64, s8-s64 -> r32-r64  (note: one way only)
    """
    ALIAS: ClassVar = "as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} -> {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprNarrow:
    """Narrowing Cast (for unions)

    `narrow_as!` forces an unchecked narrowing
    """
    ALIAS: ClassVar = "narrow_as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    unchecked: bool = False
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} -> {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprWiden:
    """Widening Cast (for unions)

    Usually this is implicit
    """
    ALIAS: ClassVar = "widen_as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} {self.expr.x_type} -> {self.type.x_type}"


@NodeCommon
@dataclasses.dataclass()
class ExprUnsafeCast:
    """Unsafe Cast

    Allowed:
    ptr a <-> ptr b

    """
    ALIAS: ClassVar = "unsafe_as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} -> {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprBitCast:
    """Bit cast.

    Type must have same size and alignment as type of item

    s32,u32,f32 <-> s32,u32,f32
    s64,u64, f64 <-> s64,u64, f64
    sint, uint <-> ptr(x)
    ptr(a) <-> ptr(b)
    (Probably not true anymore: It is also ok to bitcast complex objects like recs
    """
    ALIAS: ClassVar = "bitwise_as"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    expr: NODES_EXPR_T
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr} {self.type.x_type}"


@NodeCommon
@dataclasses.dataclass()
class ExprTypeId:
    """TypeId of type

    Result has type is `typeid`"""
    ALIAS: ClassVar = "typeid_of"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprUnionTag:
    """Typetag of tagged union type

    result has type is `typeid`"""
    ALIAS: ClassVar = "union_tag"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprUnionUntagged:
    """Untagged union portion of tagged union type

    Result has type untagged union"""
    ALIAS: ClassVar = "union_untagged"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class ExprSizeof:
    """Byte size of type

    Result has type is `uint`"""
    ALIAS: ClassVar = "size_of"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    type: NODES_TYPES_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.type}"


@NodeCommon
@dataclasses.dataclass()
class ExprOffsetof:
    """Byte offset of field in record types

    Result has type `uint`"""
    ALIAS: ClassVar = "offset_of"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR | NF.NON_CORE
    #
    type: NODES_TYPES_T  # must be rec
    field: Id
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.type} {self.field}"


@NodeCommon
@dataclasses.dataclass()
class ExprStmt:
    """Expr with Statements

    The body statements must be terminated by a StmtReturn
    """
    ALIAS: ClassVar = "expr"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF_EXPR
    #
    body: list[NODES_BODY_T]  # new scope
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)}"


############################################################
# Stmt
############################################################
@NodeCommon
@dataclasses.dataclass()
class StmtBlock:
    """Block statement.

    if `label` is non-empty, nested break/continue statements can target this `block`.
    """
    ALIAS: ClassVar = "block"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF(0)
    #
    label: NAME
    body: list[NODES_BODY_T]  # new scope
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.label}"


@NodeCommon
@dataclasses.dataclass()
class StmtDefer:
    """Defer statement

    Note: defer body's containing return statments have
    non-straightforward semantics.
    """
    ALIAS: ClassVar = "defer"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NON_CORE
    #
    body:  list[NODES_BODY_T]  # new scope, must NOT contain RETURN
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class StmtIf:
    """If statement"""
    ALIAS: ClassVar = "if"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF(0)
    #
    cond: NODES_EXPR_T        # must be of type bool
    body_t: list[NODES_BODY_T]  # new scope
    body_f: list[NODES_BODY_T]  # new scope
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class Case:
    """Single case of a Cond statement"""
    ALIAS: ClassVar = "case"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NON_CORE
    #
    cond: NODES_EXPR_T        # must be of type bool
    body: list[NODES_BODY_T]  # new scope
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class StmtCond:
    """Multicase if-elif-else statement"""
    ALIAS: ClassVar = "cond"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NON_CORE
    #
    cases: list[NODES_CASES_T]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class StmtBreak:
    """Break statement

    use "" if the target is the nearest for/while/block """
    ALIAS: ClassVar = "break"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.CONTROL_FLOW
    #
    target: NAME  # use "" for no value
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_target: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.target}"


@NodeCommon
@dataclasses.dataclass()
class StmtContinue:
    """Continue statement

    use "" if the target is the nearest for/while/block """
    ALIAS: ClassVar = "continue"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.CONTROL_FLOW
    #
    target: NAME  # use "" for no value
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_target: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.target}"


@NodeCommon
@dataclasses.dataclass()
class StmtReturn:
    """Return statement

    Returns from the first enclosing ExprStmt node or the enclosing DefFun node.
    Uses void_val if the DefFun's return type is void
    """
    ALIAS: ClassVar = "return"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.CONTROL_FLOW
    #
    expr_ret: NODES_EXPR_T
    #
    doc: str = ""
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_target: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr_ret}"


@NodeCommon
@dataclasses.dataclass()
class StmtExpr:
    """Expression statement

    Turns an expression (typically a call) into a statement
    """
    ALIAS: ClassVar = "do"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NONE
    #
    expr: ExprCall
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.expr}"


@NodeCommon
@dataclasses.dataclass()
class StmtStaticAssert:
    """Static assert statement (must evaluate to true at compile-time"""
    ALIAS: ClassVar = "static_assert"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TOP_LEVEL | NF.NON_CORE
    #
    cond: NODES_EXPR_T  # must be of type bool
    message: str     # should this be an expression?
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.cond}"


@NodeCommon
@dataclasses.dataclass()
class StmtTrap:
    """Trap statement"""
    ALIAS: ClassVar = "trap"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NONE
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)}"


@NodeCommon
@dataclasses.dataclass()
class StmtCompoundAssignment:
    """Compound assignment statement

    Note: this does not support pointer inc/dec
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NON_CORE
    #
    assignment_kind: ASSIGNMENT_KIND
    lhs: NODES_LHS_T
    expr_rhs: NODES_EXPR_T
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} [{self.assignment_kind.name}] {self.lhs} = {self.expr_rhs}"


@NodeCommon
@dataclasses.dataclass()
class StmtAssignment:
    """Assignment statement"""
    ALIAS: ClassVar = "="
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.NONE
    #
    lhs: NODES_LHS_T
    expr_rhs: NODES_EXPR_T
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.lhs} = {self.expr_rhs}"


############################################################
# Definitions
############################################################


@NodeCommon
@dataclasses.dataclass()
class EnumVal:
    """ Enum element.

     `value: ValAuto` means previous value + 1"""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.VALUE_ANNOTATED | NF.GLOBAL_SYM_DEF
    #
    name: NAME
    value_or_auto: Union["ValNum", ValAuto]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}: {self.value_or_auto}"


@NodeCommon
@dataclasses.dataclass()
class DefEnum:
    """Enum definition"""
    ALIAS: ClassVar = "enum"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_CORPUS | NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL | NF.VALUE_ANNOTATED
    #
    name: NAME
    base_type_kind: BASE_TYPE_KIND   # must be integer
    items: list[NODES_ITEMS_T]
    #
    pub:  bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None  # used to guide the evaluation of EnumVal

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name}"


@NodeCommon
@dataclasses.dataclass()
class DefType:
    """Type definition

    A `wrapped` gives the underlying type a new name that is not type compatible.
    To convert between the two use an `as` cast expression.
    """
    ALIAS: ClassVar = "type"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.TYPE_CORPUS | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    name: NAME
    type: NODES_TYPES_T
    #
    pub:  bool = False
    wrapped: bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name} = {self.type}"


@NodeCommon
@dataclasses.dataclass()
class DefVar:
    """Variable definition at local scope (DefGlobal is used for global scope)

    Allocates space on stack (or in a register) and initializes it with `initial_or_undef_or_auto`.
    `let!` makes the allocated space read/write otherwise it is readonly.
    The attribute `ref` allows the address of the variable to be taken and prevents register allocation.

    """
    ALIAS: ClassVar = "let"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.LOCAL_SYM_DEF
    #
    name: NAME
    type_or_auto: NODES_TYPES_OR_AUTO_T
    initial_or_undef_or_auto: NODES_EXPR_OR_UNDEF_OR_AUTO_T
    #
    mut: bool = False
    ref: bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef_or_auto}"


@NodeCommon
@dataclasses.dataclass()
class DefGlobal:
    """Variable definition at global scope (DefVar is used for local scope)

    Allocates space in static memory and initializes it with `initial_or_undef`.
    `let!` makes the allocated space read/write otherwise it is readonly.
    The attribute `ref` allows the address of the variable to be taken and prevents register allocation.
    """
    ALIAS: ClassVar = "global"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL
    #
    name: NAME
    type_or_auto: NODES_TYPES_OR_AUTO_T
    initial_or_undef_or_auto: NODES_EXPR_T
    #
    pub: bool = False
    mut: bool = False
    ref: bool = False
    cdecl: bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE

    def __repr__(self):
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name} {self.type_or_auto} {self.initial_or_undef_or_auto}"


@NodeCommon
@dataclasses.dataclass()
class DefFun:
    """Function definition

    `init` and `fini` indicate module initializer/finalizers

    `extern` indicates a prototype and hence the function body must be empty.

    `cdecl` disables name mangling

    `ref`  fun may be assigned to a variable (i.e. its address may be taken)
     """
    ALIAS: ClassVar = "fun"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.TYPE_ANNOTATED | NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL | NF.IMPORT_ANNOTATED | NF.POLY_MOD_ANNOTATED
    #
    name: NAME   # may contain qualifier (in case of polymorphic funs)
    params: list[NODES_PARAMS_T]
    result: NODES_TYPES_T
    body: list[NODES_BODY_T]  # new scope
    #
    init: bool = False
    fini: bool = False
    extern: bool = False
    cdecl: bool = False
    poly: bool = False
    #
    pub: bool = False
    ref: bool = False

    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_type: CanonType = NO_TYPE
    x_import: Import = None  # only used for polymorphic function
    x_poly_mod: Optional[DefMod] = None  # only used for polymorphic function

    def __repr__(self):
        params = ', '.join(str(p) for p in self.params)
        return f"{NODE_NAME(self)}{_FLAGS(self)} {self.name} [{params}]->{self.result}"


############################################################
# Macro Like
############################################################


@NodeCommon
@dataclasses.dataclass()
class ExprSrcLoc:
    """Source Location encoded as string

    expr is not evaluated but just used for its x_srcloc
    """
    ALIAS: ClassVar = "srcloc"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF.TO_BE_EXPANDED | NF.NON_CORE | NF_EXPR
    #
    expr: NODES_EXPR_T
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC


@NodeCommon
@dataclasses.dataclass()
class ExprStringify:
    """Human readable representation of the expression

    This is useful to implement for assert like features
    """
    ALIAS: ClassVar = "stringify"
    GROUP: ClassVar = GROUP.Expression
    FLAGS: ClassVar = NF.TO_BE_EXPANDED | NF.NON_CORE | NF_EXPR
    #
    expr:  NODES_EXPR_T
    # the next two are not really used since node gets replaced with string
    x_type: CanonType = NO_TYPE
    x_value: Optional[Any] = None
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

############################################################
# Macro
############################################################


@NodeCommon
@dataclasses.dataclass()
class MacroId:
    """Placeholder for a parameter

    This node will be expanded with the actual argument
    """
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Macro
    FLAGS: ClassVar = NF.NON_CORE
    #
    name: NAME

    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    @staticmethod
    def Make(name: str, **kwargs):
        assert name.startswith(MACRO_VAR_PREFIX)
        return MacroId(NAME.Make(name), **kwargs)

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}"


@NodeCommon
@dataclasses.dataclass()
class MacroFor:
    """Macro for-loop like statement

    loops over the macro parameter `name_list` which must be a list and
    binds each list element to `name` while expanding the AST nodes in `body_for`.
    """
    ALIAS: ClassVar = "mfor"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.MACRO_BODY_ONLY | NF.NON_CORE
    #
    name: NAME
    name_list: NAME  # a macro variable holding a list
    body_for: list[Any]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC


@NodeCommon
@dataclasses.dataclass()
class MacroParam:
    """Macro Parameter"""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Macro
    FLAGS: ClassVar = NF.LOCAL_SYM_DEF | NF.NON_CORE
    #
    name: NAME
    macro_param_kind: MACRO_PARAM_KIND
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name} {self.macro_param_kind.name}"


@NodeCommon
@dataclasses.dataclass()
class MacroInvoke:
    """Macro Invocation"""
    ALIAS: ClassVar = None
    GROUP: ClassVar = GROUP.Macro
    FLAGS: ClassVar = NF.TO_BE_EXPANDED | NF.NON_CORE | NF.IMPORT_ANNOTATED | NF.SYMBOL_ANNOTATED
    #
    name: NAME   # may contain qualifiers
    args: list[NODES_EXPR_T]
    #
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC
    x_symbol: NODES_SYMBOLS_T = INVALID_SYMBOL
    x_import: Import = None

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}"


@NodeCommon
@dataclasses.dataclass()
class DefMacro:
    """Define a macro

    A macro consists of
    * a name
    * the type of AST node (list) it create
    * a parameter list. A parameter name must start with a '$'
    * a list of additional identifiers used by the macro (also starimg with '$')
    * a body containing both regular and macro specific AST node serving as a template
    """
    ALIAS: ClassVar = "macro"
    GROUP: ClassVar = GROUP.Statement
    FLAGS: ClassVar = NF.GLOBAL_SYM_DEF | NF.TOP_LEVEL | NF.NON_CORE
    #
    name: NAME
    macro_result_kind: MACRO_RESULT_KIND
    params_macro: list[NODES_PARAMS_MACRO_T]
    gen_ids: list[MacroId]
    body_macro: list[Any]  # new scope
    #
    builtin: bool = False  # only used by some macros from buildin.cw
    pub: bool = False
    doc: str = ""
    #
    x_srcloc: SrcLoc = INVALID_SRCLOC

    def __repr__(self):
        return f"{NODE_NAME(self)} {self.name}"


# NO_SYMBOL = DefType(NAME("", 0), TypeBase(BASE_TYPE_KIND.BOOL))
# parent is not also an expression
TOP_LEVEL_EXPRESSION_NODES = (ExprCall, StmtReturn, StmtCompoundAssignment, StmtAssignment,
                              DefVar, DefGlobal, ValPoint)
############################################################
#
############################################################


def VisitAstRecursively(node, visitor):
    if visitor(node):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursively(child, visitor)
        else:
            for child in getattr(node, f):
                VisitAstRecursively(child, visitor)


def VisitAstRecursivelyWithScopeTracking(node, visitor, scope_enter, scope_exit, parent=None):
    if visitor(node, parent):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyWithScopeTracking(
                child, visitor, scope_enter, scope_exit, node)
        else:
            if nfd.name in NEW_SCOPE_FIELDS:
                scope_enter(node)
            for child in getattr(node, f):
                VisitAstRecursivelyWithScopeTracking(
                    child, visitor, scope_enter, scope_exit, node)
            if nfd.name in NEW_SCOPE_FIELDS:
                scope_exit(node)


def VisitAstRecursivelyWithField(node, visitor, nfd=None):
    if visitor(node, nfd):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyWithField(child, visitor, nfd)
        else:
            for child in getattr(node, f):
                VisitAstRecursivelyWithField(child, visitor, nfd)


def VisitAstRecursivelyPreAndPost(node, visitor_pre, visitor_post):
    if visitor_pre(node):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyPreAndPost(child, visitor_pre, visitor_post)
        else:
            for child in getattr(node, f):
                VisitAstRecursivelyPreAndPost(
                    child, visitor_pre, visitor_post)

    visitor_post(node)


def _VisitAstRecursivelyWithParentAndField(node, visitor, parent, nfd=None):
    if visitor(node, parent, nfd):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            _VisitAstRecursivelyWithParentAndField(child, visitor, node, nfd)
        else:
            for child in getattr(node, f):
                _VisitAstRecursivelyWithParentAndField(
                    child, visitor, node, nfd)


def VisitAstRecursivelyWithParent(node, visitor, parent):
    if visitor(node, parent):
        return

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyWithParent(child, visitor, node)
        else:
            for child in getattr(node, f):
                VisitAstRecursivelyWithParent(
                    child, visitor, node)


def VisitAstRecursivelyPost(node, visitor):
    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyPost(child, visitor)
        else:
            for child in getattr(node, f):
                VisitAstRecursivelyPost(child, visitor)

    visitor(node)


def VisitAstRecursivelyWithParentPost(node, visitor, parent):

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            VisitAstRecursivelyWithParentPost(child, visitor, node)
        else:
            for child in getattr(node, f):
                VisitAstRecursivelyWithParentPost(
                    child, visitor, node)

    visitor(node, parent)


def MaybeReplaceAstRecursively(node, replacer):
    """Note: the root node will not be replaced

    If a node is being replace we do not recurse into its children.
    """
    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            new_child = replacer(child, node)
            if new_child:
                setattr(node, f, new_child)
            else:
                MaybeReplaceAstRecursively(child, replacer)
        else:
            children = getattr(node, f)
            new_children = []
            for n, child in enumerate(children):
                new_child = replacer(child, node)
                if isinstance(new_child, list):
                    new_children += new_child
                elif new_child is None:
                    new_children.append(child)
                    MaybeReplaceAstRecursively(child, replacer)
                else:
                    new_children.append(new_child)
            setattr(node, f, new_children)


def MaybeReplaceAstRecursivelyPost(node, replacer):
    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            MaybeReplaceAstRecursivelyPost(child, replacer)
            new_child = replacer(child)
            assert not isinstance(new_child, list)
            if new_child is not None:
                setattr(node, f, new_child)
        else:
            children = getattr(node, f)
            new_children = []
            for n, child in enumerate(children):
                MaybeReplaceAstRecursivelyPost(child, replacer)
                new_child = replacer(child)
                if new_child is None:
                    new_children.append(child)
                elif isinstance(new_child, list):
                    for x in new_child:
                        assert not isinstance(x, list)
                    new_children += new_child
                else:
                    new_children.append(new_child)
            setattr(node, f, new_children)


def MaybeReplaceAstRecursivelyWithParentPost(node, replacer):
    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            child = getattr(node, f)
            MaybeReplaceAstRecursivelyWithParentPost(child, replacer)
            new_child = replacer(child, node)
            assert not isinstance(new_child, list)
            if new_child is not None:
                setattr(node, f, new_child)
        else:
            children = getattr(node, f)
            new_children = []
            for n, child in enumerate(children):
                MaybeReplaceAstRecursivelyWithParentPost(child, replacer)
                new_child = replacer(child, node)
                if new_child is None:
                    new_children.append(child)
                elif isinstance(new_child, list):
                    for x in new_child.args:
                        assert not isinstance(x, list)
                    new_children += new_child.args
                else:
                    new_children.append(new_child)
            setattr(node, f, new_children)


def CloneNodeRecursively(node, symbol_map, target_map):
    clone = dataclasses.replace(node)
    if isinstance(clone, DefVar):
        symbol_map[node] = clone
    elif isinstance(clone, (StmtBlock, ExprStmt)):
        target_map[node] = clone

    if NF.SYMBOL_ANNOTATED in clone.FLAGS:
        old_symbol = clone.x_symbol
        clone.x_symbol = symbol_map.get(old_symbol, old_symbol)
    if NF.CONTROL_FLOW in clone.FLAGS:
        old_target = clone.x_target
        clone.x_target = target_map.get(old_target, old_target)

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            setattr(clone, f, CloneNodeRecursively(
                getattr(node, f), symbol_map, target_map))
        else:
            out = [CloneNodeRecursively(cc, symbol_map, target_map)
                   for cc in getattr(node, f)]
            setattr(clone, f, out)
    return clone


def UpdateSymbolAndTargetLinks(node, symbol_map, target_map):
    """Similar to CloneNodeRecursively if you do not need to clone but can update the AST in-place"""
    if NF.SYMBOL_ANNOTATED in node.FLAGS:
        node.x_symbol = symbol_map.get(node.x_symbol, node.x_symbol)
    if NF.CONTROL_FLOW in node.FLAGS:
        old_target = node.x_target
        new_target = target_map.get(old_target, old_target)
        node.x_target = new_target

    for nfd in node.__class__.NODE_FIELDS:
        f = nfd.name
        if nfd.kind is NFK.NODE:
            UpdateSymbolAndTargetLinks(
                getattr(node, f), symbol_map, target_map)
        else:
            for cc in getattr(node, f):
                UpdateSymbolAndTargetLinks(cc, symbol_map, target_map)
    return node


def NumberOfNodes(node) -> int:
    n = 0

    def visitor(_node: Any):
        nonlocal n
        n += 1

    VisitAstRecursively(node, visitor)
    return n

############################################################
# Helpers
############################################################


def RemoveNodesOfType(node, cls):
    def replacer(node, _):
        nonlocal cls
        if isinstance(node, cls):
            return []
        else:
            return None

    MaybeReplaceAstRecursively(node, replacer)


############################################################
# AST Checker
############################################################
ASSERT_AFTER_ERROR = True

# message format follows:
# https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-diagnostic-format-for-tasks


def CompilerError(srcloc, msg, kind='syntax') -> NoReturn:
    global ASSERT_AFTER_ERROR
    print(f"{srcloc}: error {kind}: {msg}", file=sys.stdout)
    if ASSERT_AFTER_ERROR:
        # this will emit a stack trace which is the main purpose
        assert False
    exit(1)


def _CheckMacroRecursively(node, seen_names: set[str]):
    def visitor(node):
        if isinstance(node, (MacroParam, MacroFor)):
            assert node.name.IsMacroVar()
            assert node.name not in seen_names, f"duplicate name: {node.name}"
            seen_names.add(node.name)
    VisitAstRecursively(node, visitor)


def _IsPermittedNode(node, permitted, parent, toplevel_node, node_mod: DefMod,
                     allow_type_auto: bool) -> bool:
    if node.__class__.__name__ in permitted:
        return True
    if isinstance(node, MacroInvoke):
        # this could be made stricter, i.e. only for exprs and stmts
        return True
    if isinstance(node, TypeAuto):
        return allow_type_auto
    if isinstance(node, MacroId):
        return isinstance(toplevel_node, DefMacro) or node_mod.params_mod

    if isinstance(parent, (MacroInvoke, EphemeralList)):
        return True  # refine
    if isinstance(toplevel_node, DefMacro):
        return True  # refine
    return False


def CheckAST(node_mod: DefMod, disallowed_nodes, allow_type_auto=False, pre_symbolize=False):
    """
    This check is run at various stages of compilation.

    `disallowed_nodes` contains a set of nodes that must not appear.

    `pre_symbolize` indicates that the check is running before symbolization so
    that the fields `x_symtab`, `x_target`, `x_symbol` are not yet set.


    """
    # this only works with pre-order traversal
    toplevel_node = None

    def visitor(node: Any, parent: Any, nfd: NFD):
        nonlocal disallowed_nodes
        nonlocal toplevel_node
        nonlocal node_mod
        nonlocal pre_symbolize

        if type(node) in disallowed_nodes:
            CompilerError(
                node.x_srcloc, f"Disallowed node: {type(node)} in {toplevel_node}")

        assert isinstance(
            node.x_srcloc, SrcLoc) and node.x_srcloc != INVALID_SRCLOC, f"Node without srcloc node {node} for parent={parent} field={nfd} {node.x_srcloc}"

        if NF.TOP_LEVEL in node.FLAGS:
            if not isinstance(parent, DefMod):
                CompilerError(
                    node.x_srcloc, f"only allowed at toplevel: {node}")
            toplevel_node = node
        if NF.MACRO_BODY_ONLY in node.FLAGS:
            assert isinstance(
                toplevel_node, DefMacro), f"only allowed in macros: {node}"

        if NF.LOCAL_SYM_DEF in node.FLAGS:
            assert isinstance(node.name, NAME), f"{node}"
        if NF.GLOBAL_SYM_DEF in node.FLAGS:
            if not isinstance(node, DefMod):
                assert isinstance(node.name, NAME), f"{node}"

        if isinstance(node, DefMacro):
            if not node.name.IsMacroCall() and node.name.name not in ALL_BUILT_IN_MACROS:
                CompilerError(
                    node.x_srcloc, f"macro name must end with `#`: {node.name}")
            for p in node.params_macro:
                if isinstance(p, MacroParam):
                    assert p.name.IsMacroVar()
            for i in node.gen_ids:
                assert isinstance(i, MacroId)
            _CheckMacroRecursively(node, set())
        elif isinstance(node, Id):
            assert isinstance(node.name, NAME), f"{node} {node.x_symbol}"
            if not pre_symbolize:
                assert node.x_symbol is not INVALID_SYMBOL, f"{
                    node} without valid x_symbol {node.x_srcloc}"
            if node.name.IsMacroVar():
                CompilerError(node.x_srcloc, f"{node} start with $")
        elif isinstance(node, MacroId):
            assert node.name.IsMacroVar()
        elif isinstance(node, StmtBlock):
            assert isinstance(node.label, NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, StmtBreak):
            assert isinstance(node.target, NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, StmtContinue):
            assert isinstance(node.target, NAME), f"{node} {node.x_srcloc}"
        elif isinstance(node, Import):
            if not pre_symbolize:
                assert node.x_module != INVALID_MOD
        elif isinstance(node, DefMod):
            if not pre_symbolize:
                assert node.x_symtab, f"missing x_symtab {node}"
        if nfd is not None:
            if not _IsPermittedNode(node, nfd.node_type, parent, toplevel_node,
                                    node_mod,
                                    allow_type_auto):
                CompilerError(
                    node.x_srcloc, f"unexpected node for field={nfd.name}: {node.__class__.__name__}")

    _VisitAstRecursivelyWithParentAndField(node_mod, visitor, None)


##########################################################################################
# Doc Generation
##########################################################################################
PROLOG = """## Abstract Syntax Tree (AST) Nodes used by Cwerg

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
    print("""
## Node Overview (Core)

Core nodes are the ones that are known to the code generator.
""",  file=fout)
    n = 0
    for name, cls in nodes:
        if NF.NON_CORE in cls.FLAGS:
            continue
        n += 1
        alias = ""
        if cls.ALIAS:
            alias = f"&nbsp;({cls.ALIAS})"
        anchor = MakeAnchor(name, cls.ALIAS)
        print(f"[{name}{alias}](#{anchor}) &ensp;", file=fout)
    print(f"({n} nodes)", file=fout)

    print("""
## Node Overview (Non-Core)

Non-core nodes are syntactic sugar and will be eliminated before
code generation.
""",  file=fout)
    n = 0
    for name, cls in nodes:
        if NF.NON_CORE not in cls.FLAGS:
            continue
        n += 1
        alias = ""
        if cls.ALIAS:
            alias = f"&nbsp;({cls.ALIAS})"
        anchor = MakeAnchor(name, cls.ALIAS)
        print(f"[{name}{alias}](#{anchor}) &ensp;", file=fout)
    print(f"({n} nodes)", file=fout)

    print("""
## Enum Overview

Misc enums used inside of nodes.
""",  file=fout)
    for cls in ["Expr1", "Expr2", "StmtCompoundAssignment", "Base Type",
                "ModParam", "MacroParam"]:
        name = cls + " Kind"
        anchor = MakeAnchor(name, None)
        print(f"[{name}](#{anchor}) &ensp;", file=fout)

    nodes = sorted((node.GROUP, node.__name__, node) for node in ALL_NODES)
    last_group = ""
    for group, name, cls in nodes:
        if last_group != group:
            print(f"\n## {group.name} Node Details",  file=fout)
            last_group = group
        print("", file=fout)
        alias = ""
        if cls.ALIAS:
            alias = f" ({cls.ALIAS})"
        print(f"### {name}{alias}", file=fout)

        print(cls.__doc__,  file=fout)

        if NF.TOP_LEVEL in cls.FLAGS:
            print("", file=fout)
            print("Allowed at top level only", file=fout)
        if len(cls.__annotations__):
            print("", file=fout)
            print("Fields:",  file=fout)

            for nfd in cls.FIELDS:
                field = nfd.name
                kind = nfd.kind
                extra = ""
                optional_val = GetOptional(field, 0)
                if optional_val is not None:
                    if optional_val == "":
                        extra = ' (default "")'
                    elif isinstance(optional_val, ValNum):
                        extra = f' (default {optional_val.number})'
                    else:
                        extra = f' (default {optional_val.__class__.__name__})'
                print(f"* {field} [{kind.name}]{extra}: {nfd.doc}", file=fout)
            if cls.ATTRS:
                print("", file=fout)
                print("Flags:",  file=fout)
                for field, nfd in cls.ATTRS:
                    print(f"* {field}: {nfd.doc}", file=fout)
            print("", file=fout)

    print("## Enum Details",  file=fout)

    _RenderKind(Expr1.__name__,  UNARY_EXPR_KIND,
                UNARY_EXPR_SHORTCUT_SEXPR_INV, fout)
    _RenderKind(Expr2.__name__,  BINARY_EXPR_KIND,
                BINARY_EXPR_SHORTCUT_INV, fout)
    _RenderKind(ExprPointer.__name__, POINTER_EXPR_KIND,
                POINTER_EXPR_SHORTCUT_INV, fout)
    _RenderKind(StmtCompoundAssignment.__name__,
                ASSIGNMENT_KIND, ASSIGNMENT_SHORTCUT_INV, fout)
    _RenderKindSimple("Base Type",
                      BASE_TYPE_KIND, fout)
    _RenderKindSimple("ModParam",
                      MOD_PARAM_KIND, fout)
    _RenderKindSimple("MacroParam",
                      MACRO_PARAM_KIND, fout)
    _RenderKindSimple("MacroResult",
                      MACRO_RESULT_KIND, fout)


_NFK_KIND_2_SIZE = {
    NFK.NAME: 32,
    NFK.NODE: 32,
    NFK.STR: 32,
    NFK.LIST: 32,
    NFK.KIND: 8,
    NFK.ATTR_BOOL: 1,
    NFK.ATTR_STR: 32,

}


# this covers all fields which occur more than once (and all the body_* fields)
_FIELD_2_SLOT = {
    "type": 1,
    "type_or_auto": 1,
    "name": 0,
    "expr": 0,
    "expr1": 0,
    "expr2": 1,
    "body": 3,
    "body_mod": 3,
    "body_f": 3,
    "body_t": 2,
    "cond": 1,
    "container": 0,
    "params": 1,
    "result": 2,
    "initial_or_undef_or_auto": 2,
    "lhs": 0,
    "expr_rhs": 1,
    "target": 0,
    "args": 1,
    "field": 2,
}


def GetSize(kind):
    return _NFK_KIND_2_SIZE.get(kind, -1)


MAX_SLOTS = 4


def _ComputeRemainingSlotsForFields():
    for cls in ALL_NODES:
        slots: list[Optional[NFD]] = [None] * MAX_SLOTS
        for nfd in cls.FIELDS:
            if nfd.kind not in (NFK.NODE, NFK.LIST, NFK.STR, NFK.NAME):
                continue
            field = nfd.name
            if field in _FIELD_2_SLOT:
                slot = _FIELD_2_SLOT[field]
                assert slots[slot] is None, f"[{cls.__name__}] slot {
                    slot} already used for [{slots[slot].name}] trying for [{field}]"
                slots[slot] = nfd
            else:
                for i in range(4):
                    if slots[i] is None:
                        slots[i] = nfd
                        _FIELD_2_SLOT[field] = i
                        break
                else:
                    assert False, "slot clash"


_KIND_TO_HANDLE = {
    NFK.NODE: "Node",
    NFK.LIST: "Node",
    NFK.NAME: "Name",
    NFK.STR: "Str",
}


def GenerateAccessors():
    last = None
    for nfd in ALL_FIELDS:
        k = nfd.kind
        if k not in _KIND_TO_HANDLE:
            continue
        if k != last:
            print(f"\n// {k}")
            last = k

        dst = _KIND_TO_HANDLE[k]
        print(f"inline {dst}& Node_{
            nfd.name}(Node n) {{ return gNodeCore[n].children_{dst.lower()}[{_FIELD_2_SLOT[nfd.name]}]; }}")


def GenerateInits():
    for cls in sorted(ALL_NODES, key=lambda x: x.__name__):

        other_kind = None
        nfds = []
        slots = [None] * MAX_SLOTS
        has_bits = False
        for nfd in cls.FIELDS:
            if nfd.kind in (NFK.NODE, NFK.LIST, NFK.NAME, NFK.STR):
                nfds.append(nfd)
                slots[_FIELD_2_SLOT[nfd.name]] = nfd
            elif nfd.kind == NFK.KIND:
                other_kind = nfd
                nfds.append(nfd)
        for nfd in cls.ATTRS:
            if nfd.kind == NFK.ATTR_BOOL:
                has_bits = True

        print(f"inline void NodeInit{cls.__name__}(Node node", end="")
        for nfd in nfds:
            k = nfd.kind
            if k == NFK.NODE or k == NFK.LIST:
                print(f", Node {nfd.name}", end="")
            elif k == NFK.NAME:
                print(f", Name {nfd.name}", end="")
            elif k == NFK.STR:
                print(f", Str {nfd.name}", end="")
            elif k == NFK.KIND:
                print(f", {other_kind.enum_kind.__name__} {nfd.name}", end="")
        if has_bits:
            print(", uint16_t bits", end="")
        print(", Str doc, const SrcLoc& srcloc", end="")
        print(") {")
        args = ["node", f"NT::{cls.__name__}"]
        for i in range(MAX_SLOTS):
            if slots[i] is None:
                args.append("kHandleInvalid")
            else:
                args.append(slots[i].name)
        if other_kind is None:
            args.append("0")
        else:
            args.append(f"uint8_t({other_kind.name})")
        if has_bits:
            args.append("bits")
        else:
            args.append("0")
        args.append("doc")
        args.append("srcloc")
        print(f"    NodeInit({', '.join(args)});")
        print("}\n")


def _NameValuesForNT():
    out = [("invalid", 0)]
    for n, cls in enumerate(sorted(ALL_NODES, key=lambda x: x.__name__)):
        out.append((cls.__name__, n+1))
    return out


def _MakeNameValues(names, to_upper=False):
    out = [("invalid", 0)]
    for n, name in enumerate(names):
        if to_upper:
            name = name.upper()
        out.append((name, n+1))
    return out


def _FieldNamesForKind(nfk: NFK) -> list[str]:
    out = []
    for nfd in ALL_FIELDS:
        if nfd.kind is nfk:
            out.append(nfd.name)
    return out


def GenerateCodeH(fout: Any):
    _ComputeRemainingSlotsForFields()

    print("enum class NFD_NODE_FIELD : uint8_t {")
    print("    invalid = 0,")
    fields = sorted(_FieldNamesForKind(NFK.NODE) +
                    _FieldNamesForKind(NFK.LIST))
    for n, name in enumerate(fields):
        print(f"    {name} = {n+1},  // slot: {_FIELD_2_SLOT[name]}")
    print("};")

    print("enum class NFD_STRING_FIELD : uint8_t {")
    print("    invalid = 0,")
    fields = sorted(_FieldNamesForKind(NFK.NAME) +
                    _FieldNamesForKind(NFK.STR))
    for n, name in enumerate(fields):
        print(f"    {name} = {n+1},  // slot: {_FIELD_2_SLOT[name]}")
    print("};")

    #  intentionally not sorted
    cgen.RenderEnumClass(_MakeNameValues(
        _FieldNamesForKind(NFK.ATTR_BOOL), to_upper=True), "BF", fout)

    cgen.RenderEnumClass(_NameValuesForNT(), "NT", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        BINARY_EXPR_KIND), "BINARY_EXPR_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        UNARY_EXPR_KIND), "UNARY_EXPR_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        POINTER_EXPR_KIND), "POINTER_EXPR_KIND", fout)

    cgen.RenderEnumClass(cgen.NameValues(
        BASE_TYPE_KIND), "BASE_TYPE_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        MACRO_PARAM_KIND), "MACRO_PARAM_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        MACRO_RESULT_KIND), "MACRO_RESULT_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        MOD_PARAM_KIND), "MOD_PARAM_KIND", fout)
    cgen.RenderEnumClass(cgen.NameValues(
        ASSIGNMENT_KIND), "ASSIGNMENT_KIND", fout)

    print(f"\nconstexpr int SLOT_BODY = {_FIELD_2_SLOT['body']};")
    print(f"\nconstexpr int SLOT_BODY_T = {_FIELD_2_SLOT['body_t']};")
    GenerateAccessors()
    GenerateInits()


def EnumStringConversions(fout: Any):
    def render(name: str, name_vals: list, both_ways=True):
        cgen.RenderEnumToStringMap(name_vals, name, fout)
        cgen.RenderEnumToStringFun(name, fout)
        if both_ways:
            cgen.RenderStringToEnumMap(name_vals,
                                       name + "_FromStringMap",
                                       name + "_Jumper", fout)

    def std_render(cls):
        render(cls.__name__, cgen.NameValues(cls))

    std_render(MOD_PARAM_KIND)
    std_render(MACRO_PARAM_KIND)
    std_render(MACRO_RESULT_KIND)

    render(BASE_TYPE_KIND.__name__,  cgen.NameValuesLower(BASE_TYPE_KIND))

    render(ASSIGNMENT_KIND.__name__,
           [(k, v.value) for k, v in ASSIGNMENT_SHORTCUT.items()])

    render(POINTER_EXPR_KIND.__name__,
           [(k, v.value) for k, v in POINTER_EXPR_SHORTCUT.items()], both_ways=False)

    render(BINARY_EXPR_KIND.__name__,
           [(k, v.value) for k, v in BINARY_EXPR_SHORTCUT.items()], both_ways=False)
    render("NT",  _NameValuesForNT(), both_ways=False)
    # intentionally not sorted - order is "print-order"
    render("BF", _MakeNameValues(
        _FieldNamesForKind(NFK.ATTR_BOOL), to_upper=False),
        both_ways=True)


def NodeAliasStringConversion(fout: Any):
    print(
        "\nconst std::map<std::string_view, NT> KeywordToNodeTypeMap = {", file=fout)
    for node in sorted(ALL_NODES, key=lambda x: x.__name__):
        alias = node.ALIAS
        if alias and _NAMED_OP_RE.fullmatch(alias):
            print(f'    {{"{alias}", NT::{node.__name__}}},', file=fout)
            for f in node.ATTRS:
                if f.name in ("mut", "untagged", "unchecked"):
                    print(
                        f'    {{"{alias + MUTABILITY_SUFFIX}", NT::{node.__name__}}},', file=fout)
                    break
    print("};", file=fout)


def EmitNodeDesc(fout: Any):
    print("const NodeDesc GlobalNodeDescs[] = {")
    print("    {}, // invalid")

    for cls in sorted(ALL_NODES, key=lambda n: n.__name__):
        node_fields = []
        string_fields = []
        bool_fields = []
        for nfd in cls.FIELDS:
            k = nfd.kind
            if k == NFK.NODE or k == NFK.LIST:
                node_fields.append(f"BIT_N({nfd.name})")
            if k == NFK.NAME or k == NFK.STR:
                string_fields.append(f"BIT_S({nfd.name})")
        for nfd in cls.ATTRS:
            k = nfd.kind
            if k == NFK.ATTR_BOOL:
                bool_fields.append(f"BIT_B({nfd.name.upper()})")
        if node_fields:
            node_fields = '| '.join(node_fields)
        else:
            node_fields = "0"
        #
        if string_fields:
            string_fields = '| '.join(string_fields)
        else:
            string_fields = "0"
        #
        if bool_fields:
            bool_fields = '| '.join(bool_fields)
        else:
            bool_fields = "0"

        print(f"    {{ {node_fields}, {string_fields}, {
              bool_fields} }}, // {cls.__name__}")
    print("};")


def GenerateCodeCC(fout: Any):
    EmitNodeDesc(fout)
    EnumStringConversions(fout)
    NodeAliasStringConversion(fout)


_NAMED_OP_RE = re.compile(r"[_a-zA-Z]+")


_SIMPLE_VAL = set([ValTrue, ValFalse, ValAuto, ValUndef, ValVoid])


def KeyWordsForConcreteSyntax():
    out = []
    for x in ALL_NODES:
        if x in _SIMPLE_VAL:
            continue
        alias = x.ALIAS
        if alias and alias not in "^.?=@at":
            out.append(alias)
            for f in x.ATTRS:
                if f.name in ("mut", "untagged", "unchecked"):
                    out.append(alias + MUTABILITY_SUFFIX)
                    break
    for k in POINTER_EXPR_SHORTCUT:
        if _NAMED_OP_RE.fullmatch(k):
            out.append(k)
    for k in BINARY_EXPR_SHORTCUT:
        if _NAMED_OP_RE.fullmatch(k):
            out.append(k)
    for k in UNARY_EXPR_SHORTCUT_CONCRETE:
        if _NAMED_OP_RE.fullmatch(k):
            out.append(k)
    return out


def KeyWordsSimpleVal():
    return [x.ALIAS for x in _SIMPLE_VAL]


def KeywordsBaseTypes():
    out = []
    for k in BASE_TYPE_KIND:
        if k != BASE_TYPE_KIND.INVALID:
            out.append(BaseTypeKindToKeyword(k))
    return out


def UnaryOpsForConcreteSyntax():
    # note, this excludes the "-" operator.
    # The lexer will treat it as a BinaryOp and
    # the parse will figure out what it really is
    return [x for x in UNARY_EXPR_SHORTCUT_COMMON
            if not _NAMED_OP_RE.fullmatch(x)]


def BinaryOpsForConcreteSyntax():
    return [x for x in BINARY_EXPR_SHORTCUT
            if not _NAMED_OP_RE.fullmatch(x)]


##########################################################################################
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    logger.setLevel(logging.INFO)
    if len(sys.argv) <= 1:
        print("no mode given")
        exit(1)
    mode = sys.argv[1]
    if mode == "doc":
        GenerateDocumentation(sys.stdout)
    elif mode == "gen_h":
        cgen.ReplaceContent(GenerateCodeH, sys.stdin, sys.stdout)
    elif mode == "gen_cc":
        cgen.ReplaceContent(GenerateCodeCC, sys.stdin, sys.stdout)
    elif mode == "kw":
        for kw in sorted(KeyWordsForConcreteSyntax()):
            print(kw)
    elif mode == "op":
        print("UNARY")
        for kw in sorted(UnaryOpsForConcreteSyntax()):
            print(kw)
        print("BINARY")
        for kw in sorted(BinaryOpsForConcreteSyntax()):
            print(kw)
        print("COMPOUND")
        for kw in sorted(ASSIGNMENT_SHORTCUT.keys()):
            print(kw)
    else:
        print(f"unknown mode: {mode}")
        exit(1)
