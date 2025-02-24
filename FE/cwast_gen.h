#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>
#include <cstring>

#include "Util/handle.h"
#include "Util/immutable.h"
#include "Util/stripe.h"

namespace cwerg::fe {

uint8_t constexpr kKindStr = 100;
uint8_t constexpr kKindName = 101;

enum class NT : uint8_t;

struct Node : public Handle {
  explicit constexpr Node(NT kind, uint32_t index = 0)
      : Handle(index, uint8_t(kind)) {}

  explicit constexpr Node(Handle ref) : Handle(ref.value) {}
  NT kind() { return NT(raw_kind()); }
};

struct Str : public Handle {
  explicit constexpr Str(uint32_t index = 0) : Handle(index, kKindStr) {}
  explicit Str(Handle ref) : Handle(ref.value) {}
};

struct Name : public Handle {
  explicit constexpr Name(uint32_t index = 0) : Handle(index, kKindName) {}

  explicit constexpr Name(Handle ref) : Handle(ref.value) {}
};

constexpr const Handle HandleInvalid(0, 0);
constexpr const Str StrInvalid(0);

extern ImmutablePool gNamePool;

// =======================================
// Node API
// =======================================

struct NodeCore {
  NT kind;
  uint8_t other_kind;
  uint16_t bits;
  Handle children[4];
  Handle next;
};

struct NodeExtra {
  Str comment;
};

extern struct Stripe<NodeCore, Node> gNodeCore;
extern struct Stripe<NodeExtra, Node> gNodeExtra;
extern struct StripeGroup gStripeGroupNode;

inline NT& Node_kind(Node node) { return gNodeCore[node].kind; }
inline Node& Node_next(Node node) { return (Node&)gNodeCore[node].next; }
inline Str& Node_comment(Node node) { return gNodeExtra[node].comment; }

inline Node NodeNew(NT kind) {
  Node out = Node(kind, gStripeGroupNode.New().index());
  return out;
}

inline void NodeInit(Node node, NT kind, Handle child0, Handle child1,
                     Handle child2, Handle child3, uint8_t other_kind,
                     uint16_t bits, Str doc) {
  NodeCore& core = gNodeCore[node];
  core.kind = kind;
  core.other_kind = other_kind;
  core.children[0] = child0;
  core.children[1] = child1;
  core.children[2] = child2;
  core.children[3] = child3;
  core.next = HandleInvalid;
  core.bits = bits;
  Node_comment(node) = doc;
}

// =======================================
// Name API
// =======================================


struct NameCore {
  uint32_t name;  // offset from ImmutablePool.
  uint32_t seq;
};

extern struct Stripe<NameCore, Name> gNameCore;
extern struct StripeGroup gStripeGroupName;

inline Name NameNew(uint32_t offset, uint32_t seq) {
  Name out = Name(gStripeGroupName.New().index());
  gNameCore[out] = {offset, seq};
  return out;
}

inline Name NameNew(std::string_view s) {
  // we want a null byte at the end
  uint32_t offset = gNamePool.Intern(s, 1);
  // TODO: extract seq from string
  return NameNew(offset, 0);
}

inline const char* NameData(Name name) {
  return gNamePool.Data(gNameCore[name].name);
}

// =======================================
// Str API
//
// Note: Str is immutable. Handler index is pointing into
// an ImmutablePool.
// =======================================
extern ImmutablePool gStringPool;

inline Str StrNew(std::string_view s) {
  // we want a null byte at the end
  return Str(gStringPool.Intern(s, 1));
}

// Pointer returned by StrData is only valid until another string is interned.
inline const char* StrData(Str str) { return gStringPool.Data(str.index()); }

inline int StrCmp(Str a, Str b) {
  if (a == b) return 0;
  return strcmp(gStringPool.Data(a.index()), gStringPool.Data(b.index()));
}

inline bool StrCmpLt(Str a, Str b) {
  if (a == b) return 0;
  return strcmp(gStringPool.Data(a.index()), gStringPool.Data(b.index())) < 0;
}

// clang-format off
/* @AUTOGEN-START@ */
enum class NFD_NODE_FIELD : uint8_t {
    invalid = 0,
    args = 1,  // slot: 1
    args_mod = 2,  // slot: 2
    body = 3,  // slot: 3
    body_f = 4,  // slot: 2
    body_for = 5,  // slot: 2
    body_macro = 6,  // slot: 3
    body_mod = 7,  // slot: 1
    body_t = 8,  // slot: 0
    callee = 9,  // slot: 0
    cases = 10,  // slot: 0
    cond = 11,  // slot: 1
    container = 12,  // slot: 0
    expr = 13,  // slot: 0
    expr1 = 14,  // slot: 0
    expr2 = 15,  // slot: 1
    expr_bound_or_undef = 16,  // slot: 2
    expr_f = 17,  // slot: 2
    expr_index = 18,  // slot: 1
    expr_lhs = 19,  // slot: 0
    expr_ret = 20,  // slot: 0
    expr_rhs = 21,  // slot: 1
    expr_size = 22,  // slot: 1
    expr_t = 23,  // slot: 0
    field = 24,  // slot: 2
    fields = 25,  // slot: 1
    gen_ids = 26,  // slot: 2
    initial_or_undef_or_auto = 27,  // slot: 2
    inits = 28,  // slot: 0
    items = 29,  // slot: 1
    lhs = 30,  // slot: 0
    params = 31,  // slot: 1
    params_macro = 32,  // slot: 1
    params_mod = 33,  // slot: 0
    point = 34,  // slot: 1
    pointer = 35,  // slot: 0
    result = 36,  // slot: 2
    size = 37,  // slot: 0
    subtrahend = 38,  // slot: 0
    type = 39,  // slot: 1
    type_or_auto = 40,  // slot: 1
    types = 41,  // slot: 0
    value_or_auto = 42,  // slot: 1
    value_or_undef = 43,  // slot: 0
};
enum class NFD_STRING_FIELD : uint8_t {
    invalid = 0,
    base_name = 1,  // slot: 1
    enum_name = 2,  // slot: 2
    label = 3,  // slot: 0
    message = 4,  // slot: 0
    mod_name = 5,  // slot: 0
    name = 6,  // slot: 0
    name_list = 7,  // slot: 1
    number = 8,  // slot: 0
    path = 9,  // slot: 1
    string = 10,  // slot: 0
    target = 11,  // slot: 0
};
enum class NFD_BOOL_FIELD : uint8_t {
    invalid = 0,
    arg_ref = 1,
    builtin = 2,
    cdecl = 3,
    colon = 4,
    externx = 5,
    fini = 6,
    init = 7,
    mut = 8,
    poly = 9,
    preserve_mut = 10,
    pub = 11,
    ref = 12,
    res_ref = 13,
    unchecked = 14,
    untagged = 15,
    wrapped = 16,
};
enum class NT : uint8_t {
    invalid = 0,
    Case = 1,
    DefEnum = 2,
    DefFun = 3,
    DefGlobal = 4,
    DefMacro = 5,
    DefMod = 6,
    DefRec = 7,
    DefType = 8,
    DefVar = 9,
    EnumVal = 10,
    EphemeralList = 11,
    Expr1 = 12,
    Expr2 = 13,
    Expr3 = 14,
    ExprAddrOf = 15,
    ExprAs = 16,
    ExprBitCast = 17,
    ExprCall = 18,
    ExprDeref = 19,
    ExprField = 20,
    ExprFront = 21,
    ExprIndex = 22,
    ExprIs = 23,
    ExprLen = 24,
    ExprNarrow = 25,
    ExprOffsetof = 26,
    ExprParen = 27,
    ExprPointer = 28,
    ExprSizeof = 29,
    ExprSrcLoc = 30,
    ExprStmt = 31,
    ExprStringify = 32,
    ExprTypeId = 33,
    ExprUnionTag = 34,
    ExprUnionUntagged = 35,
    ExprUnsafeCast = 36,
    ExprUnwrap = 37,
    ExprWiden = 38,
    ExprWrap = 39,
    FunParam = 40,
    Id = 41,
    Import = 42,
    MacroFor = 43,
    MacroId = 44,
    MacroInvoke = 45,
    MacroParam = 46,
    ModParam = 47,
    RecField = 48,
    StmtAssignment = 49,
    StmtBlock = 50,
    StmtBreak = 51,
    StmtCompoundAssignment = 52,
    StmtCond = 53,
    StmtContinue = 54,
    StmtDefer = 55,
    StmtExpr = 56,
    StmtIf = 57,
    StmtReturn = 58,
    StmtStaticAssert = 59,
    StmtTrap = 60,
    TypeAuto = 61,
    TypeBase = 62,
    TypeFun = 63,
    TypeOf = 64,
    TypePtr = 65,
    TypeSpan = 66,
    TypeUnion = 67,
    TypeUnionDelta = 68,
    TypeVec = 69,
    ValAuto = 70,
    ValCompound = 71,
    ValFalse = 72,
    ValNum = 73,
    ValPoint = 74,
    ValSpan = 75,
    ValString = 76,
    ValTrue = 77,
    ValUndef = 78,
    ValVoid = 79,
};

enum class BINARY_EXPR_KIND : uint8_t {
    INVALID = 0,
    ADD = 1,
    SUB = 2,
    DIV = 3,
    MUL = 4,
    MOD = 5,
    MIN = 6,
    MAX = 7,
    AND = 10,
    OR = 11,
    XOR = 12,
    EQ = 20,
    NE = 21,
    LT = 22,
    LE = 23,
    GT = 24,
    GE = 25,
    ANDSC = 30,
    ORSC = 31,
    SHR = 40,
    SHL = 41,
    ROTR = 42,
    ROTL = 43,
    PDELTA = 52,
};

enum class UNARY_EXPR_KIND : uint8_t {
    INVALID = 0,
    NOT = 1,
    NEG = 2,
    ABS = 3,
    SQRT = 4,
};

enum class POINTER_EXPR_KIND : uint8_t {
    INVALID = 0,
    INCP = 1,
    DECP = 2,
};

enum class BASE_TYPE_KIND : uint8_t {
    INVALID = 0,
    SINT = 10,
    S8 = 11,
    S16 = 12,
    S32 = 13,
    S64 = 14,
    UINT = 20,
    U8 = 21,
    U16 = 22,
    U32 = 23,
    U64 = 24,
    R32 = 30,
    R64 = 31,
    VOID = 40,
    NORET = 41,
    BOOL = 42,
    TYPEID = 43,
};

enum class STR_KIND : uint8_t {
    NORMAL = 0,
    NORMAL_TRIPLE = 1,
    RAW = 2,
    RAW_TRIPLE = 3,
    HEX = 4,
    HEX_TRIPLE = 5,
};

enum class MACRO_PARAM_KIND : uint8_t {
    INVALID = 0,
    ID = 1,
    STMT_LIST = 2,
    EXPR_LIST = 3,
    EXPR = 4,
    STMT = 5,
    FIELD = 6,
    TYPE = 7,
    EXPR_LIST_REST = 8,
};

enum class MOD_PARAM_KIND : uint8_t {
    INVALID = 0,
    CONST_EXPR = 1,
    TYPE = 2,
};

enum class ASSIGNMENT_KIND : uint8_t {
    INVALID = 0,
    ADD = 1,
    SUB = 2,
    DIV = 3,
    MUL = 4,
    MOD = 5,
    MIN = 6,
    MAX = 7,
    AND = 10,
    OR = 11,
    XOR = 12,
    SHR = 40,
    SHL = 41,
    ROTR = 42,
    ROTL = 43,
};
// NFK.NAME
inline Name Node_name(Node n) { return Name(gNodeCore[n].children[0]); }
inline Name Node_mod_name(Node n) { return Name(gNodeCore[n].children[0]); }
inline Name Node_base_name(Node n) { return Name(gNodeCore[n].children[1]); }
inline Name Node_enum_name(Node n) { return Name(gNodeCore[n].children[2]); }
inline Name Node_name_list(Node n) { return Name(gNodeCore[n].children[1]); }
inline Name Node_label(Node n) { return Name(gNodeCore[n].children[0]); }
inline Name Node_target(Node n) { return Name(gNodeCore[n].children[0]); }
// NFK.STR
inline Str Node_number(Node n) { return Str(gNodeCore[n].children[0]); }
inline Str Node_string(Node n) { return Str(gNodeCore[n].children[0]); }
inline Str Node_message(Node n) { return Str(gNodeCore[n].children[0]); }
inline Str Node_path(Node n) { return Str(gNodeCore[n].children[1]); }
// NFK.LIST
inline Node Node_params(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_params_mod(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_params_macro(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_args(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_args_mod(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_items(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_fields(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_types(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_inits(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_gen_ids(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_body_mod(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_body(Node n) { return Node(gNodeCore[n].children[3]); }
inline Node Node_body_t(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_body_f(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_body_for(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_body_macro(Node n) { return Node(gNodeCore[n].children[3]); }
inline Node Node_cases(Node n) { return Node(gNodeCore[n].children[0]); }
// NFK.NODE
inline Node Node_field(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_point(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_type(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_subtrahend(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_type_or_auto(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_result(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_size(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_expr_size(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_expr_index(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_expr(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_cond(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_expr_t(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_expr_f(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_expr1(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_expr2(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_expr_bound_or_undef(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_expr_rhs(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_expr_ret(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_pointer(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_container(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_callee(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_value_or_auto(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_value_or_undef(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_lhs(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_expr_lhs(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_initial_or_undef_or_auto(Node n) { return Node(gNodeCore[n].children[2]); }
inline void InitCase(Node node, Node cond, Node body, Str doc) {
    NodeInit(node, NT::Case, HandleInvalid, cond, HandleInvalid, body, 0, 0, doc);
}

inline void InitDefEnum(Node node, Name name, BASE_TYPE_KIND base_type_kind, Node items, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefEnum, name, items, HandleInvalid, HandleInvalid, uint8_t(base_type_kind), bits, doc);
}

inline void InitDefFun(Node node, Name name, Node params, Node result, Node body, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefFun, name, params, result, body, 0, bits, doc);
}

inline void InitDefGlobal(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefGlobal, name, type_or_auto, initial_or_undef_or_auto, HandleInvalid, 0, bits, doc);
}

inline void InitDefMacro(Node node, Name name, MACRO_PARAM_KIND macro_result_kind, Node params_macro, Node gen_ids, Node body_macro, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefMacro, name, params_macro, gen_ids, body_macro, uint8_t(macro_result_kind), bits, doc);
}

inline void InitDefMod(Node node, Node params_mod, Node body_mod, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefMod, params_mod, body_mod, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitDefRec(Node node, Name name, Node fields, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefRec, name, fields, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitDefType(Node node, Name name, Node type, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefType, name, type, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitDefVar(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc) {
    NodeInit(node, NT::DefVar, name, type_or_auto, initial_or_undef_or_auto, HandleInvalid, 0, bits, doc);
}

inline void InitEnumVal(Node node, Name name, Node value_or_auto, Str doc) {
    NodeInit(node, NT::EnumVal, name, value_or_auto, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitEphemeralList(Node node, Node args, uint16_t bits, Str doc) {
    NodeInit(node, NT::EphemeralList, HandleInvalid, args, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitExpr1(Node node, UNARY_EXPR_KIND unary_expr_kind, Node expr, Str doc) {
    NodeInit(node, NT::Expr1, expr, HandleInvalid, HandleInvalid, HandleInvalid, uint8_t(unary_expr_kind), 0, doc);
}

inline void InitExpr2(Node node, BINARY_EXPR_KIND binary_expr_kind, Node expr1, Node expr2, Str doc) {
    NodeInit(node, NT::Expr2, expr1, expr2, HandleInvalid, HandleInvalid, uint8_t(binary_expr_kind), 0, doc);
}

inline void InitExpr3(Node node, Node cond, Node expr_t, Node expr_f, Str doc) {
    NodeInit(node, NT::Expr3, expr_t, cond, expr_f, HandleInvalid, 0, 0, doc);
}

inline void InitExprAddrOf(Node node, Node expr_lhs, uint16_t bits, Str doc) {
    NodeInit(node, NT::ExprAddrOf, expr_lhs, HandleInvalid, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitExprAs(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprAs, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprBitCast(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprBitCast, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprCall(Node node, Node callee, Node args, Str doc) {
    NodeInit(node, NT::ExprCall, callee, args, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprDeref(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprDeref, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprField(Node node, Node container, Node field, Str doc) {
    NodeInit(node, NT::ExprField, container, HandleInvalid, field, HandleInvalid, 0, 0, doc);
}

inline void InitExprFront(Node node, Node container, uint16_t bits, Str doc) {
    NodeInit(node, NT::ExprFront, container, HandleInvalid, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitExprIndex(Node node, Node container, Node expr_index, uint16_t bits, Str doc) {
    NodeInit(node, NT::ExprIndex, container, expr_index, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitExprIs(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprIs, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprLen(Node node, Node container, Str doc) {
    NodeInit(node, NT::ExprLen, container, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprNarrow(Node node, Node expr, Node type, uint16_t bits, Str doc) {
    NodeInit(node, NT::ExprNarrow, expr, type, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitExprOffsetof(Node node, Node type, Node field, Str doc) {
    NodeInit(node, NT::ExprOffsetof, HandleInvalid, type, field, HandleInvalid, 0, 0, doc);
}

inline void InitExprParen(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprParen, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprPointer(Node node, POINTER_EXPR_KIND pointer_expr_kind, Node expr1, Node expr2, Node expr_bound_or_undef, Str doc) {
    NodeInit(node, NT::ExprPointer, expr1, expr2, expr_bound_or_undef, HandleInvalid, uint8_t(pointer_expr_kind), 0, doc);
}

inline void InitExprSizeof(Node node, Node type, Str doc) {
    NodeInit(node, NT::ExprSizeof, HandleInvalid, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprSrcLoc(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprSrcLoc, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprStmt(Node node, Node body, Str doc) {
    NodeInit(node, NT::ExprStmt, HandleInvalid, HandleInvalid, HandleInvalid, body, 0, 0, doc);
}

inline void InitExprStringify(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprStringify, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprTypeId(Node node, Node type, Str doc) {
    NodeInit(node, NT::ExprTypeId, HandleInvalid, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprUnionTag(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprUnionTag, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprUnionUntagged(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprUnionUntagged, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprUnsafeCast(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprUnsafeCast, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprUnwrap(Node node, Node expr, Str doc) {
    NodeInit(node, NT::ExprUnwrap, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprWiden(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprWiden, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitExprWrap(Node node, Node expr, Node type, Str doc) {
    NodeInit(node, NT::ExprWrap, expr, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitFunParam(Node node, Name name, Node type, uint16_t bits, Str doc) {
    NodeInit(node, NT::FunParam, name, type, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitId(Node node, Name mod_name, Name base_name, Name enum_name, Str doc) {
    NodeInit(node, NT::Id, mod_name, base_name, enum_name, HandleInvalid, 0, 0, doc);
}

inline void InitImport(Node node, Name name, Str path, Node args_mod, Str doc) {
    NodeInit(node, NT::Import, name, path, args_mod, HandleInvalid, 0, 0, doc);
}

inline void InitMacroFor(Node node, Name name, Name name_list, Node body_for, Str doc) {
    NodeInit(node, NT::MacroFor, name, name_list, body_for, HandleInvalid, 0, 0, doc);
}

inline void InitMacroId(Node node, Name name, Str doc) {
    NodeInit(node, NT::MacroId, name, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitMacroInvoke(Node node, Name name, Node args, Str doc) {
    NodeInit(node, NT::MacroInvoke, name, args, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitMacroParam(Node node, Name name, MACRO_PARAM_KIND macro_param_kind, Str doc) {
    NodeInit(node, NT::MacroParam, name, HandleInvalid, HandleInvalid, HandleInvalid, uint8_t(macro_param_kind), 0, doc);
}

inline void InitModParam(Node node, Name name, MOD_PARAM_KIND mod_param_kind, Str doc) {
    NodeInit(node, NT::ModParam, name, HandleInvalid, HandleInvalid, HandleInvalid, uint8_t(mod_param_kind), 0, doc);
}

inline void InitRecField(Node node, Name name, Node type, Str doc) {
    NodeInit(node, NT::RecField, name, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtAssignment(Node node, Node lhs, Node expr_rhs, Str doc) {
    NodeInit(node, NT::StmtAssignment, lhs, expr_rhs, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtBlock(Node node, Name label, Node body, Str doc) {
    NodeInit(node, NT::StmtBlock, label, HandleInvalid, HandleInvalid, body, 0, 0, doc);
}

inline void InitStmtBreak(Node node, Name target, Str doc) {
    NodeInit(node, NT::StmtBreak, target, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtCompoundAssignment(Node node, ASSIGNMENT_KIND assignment_kind, Node lhs, Node expr_rhs, Str doc) {
    NodeInit(node, NT::StmtCompoundAssignment, lhs, expr_rhs, HandleInvalid, HandleInvalid, uint8_t(assignment_kind), 0, doc);
}

inline void InitStmtCond(Node node, Node cases, Str doc) {
    NodeInit(node, NT::StmtCond, cases, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtContinue(Node node, Name target, Str doc) {
    NodeInit(node, NT::StmtContinue, target, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtDefer(Node node, Node body, Str doc) {
    NodeInit(node, NT::StmtDefer, HandleInvalid, HandleInvalid, HandleInvalid, body, 0, 0, doc);
}

inline void InitStmtExpr(Node node, Node expr, Str doc) {
    NodeInit(node, NT::StmtExpr, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtIf(Node node, Node cond, Node body_t, Node body_f, Str doc) {
    NodeInit(node, NT::StmtIf, body_t, cond, body_f, HandleInvalid, 0, 0, doc);
}

inline void InitStmtReturn(Node node, Node expr_ret, Str doc) {
    NodeInit(node, NT::StmtReturn, expr_ret, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtStaticAssert(Node node, Node cond, Str message, Str doc) {
    NodeInit(node, NT::StmtStaticAssert, message, cond, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitStmtTrap(Node node, Str doc) {
    NodeInit(node, NT::StmtTrap, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitTypeAuto(Node node, Str doc) {
    NodeInit(node, NT::TypeAuto, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitTypeBase(Node node, BASE_TYPE_KIND base_type_kind, Str doc) {
    NodeInit(node, NT::TypeBase, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, uint8_t(base_type_kind), 0, doc);
}

inline void InitTypeFun(Node node, Node params, Node result, Str doc) {
    NodeInit(node, NT::TypeFun, HandleInvalid, params, result, HandleInvalid, 0, 0, doc);
}

inline void InitTypeOf(Node node, Node expr, Str doc) {
    NodeInit(node, NT::TypeOf, expr, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitTypePtr(Node node, Node type, uint16_t bits, Str doc) {
    NodeInit(node, NT::TypePtr, HandleInvalid, type, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitTypeSpan(Node node, Node type, uint16_t bits, Str doc) {
    NodeInit(node, NT::TypeSpan, HandleInvalid, type, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitTypeUnion(Node node, Node types, uint16_t bits, Str doc) {
    NodeInit(node, NT::TypeUnion, types, HandleInvalid, HandleInvalid, HandleInvalid, 0, bits, doc);
}

inline void InitTypeUnionDelta(Node node, Node type, Node subtrahend, Str doc) {
    NodeInit(node, NT::TypeUnionDelta, subtrahend, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitTypeVec(Node node, Node size, Node type, Str doc) {
    NodeInit(node, NT::TypeVec, size, type, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValAuto(Node node, Str doc) {
    NodeInit(node, NT::ValAuto, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValCompound(Node node, Node type_or_auto, Node inits, Str doc) {
    NodeInit(node, NT::ValCompound, inits, type_or_auto, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValFalse(Node node, Str doc) {
    NodeInit(node, NT::ValFalse, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValNum(Node node, Str number, Str doc) {
    NodeInit(node, NT::ValNum, number, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValPoint(Node node, Node value_or_undef, Node point, Str doc) {
    NodeInit(node, NT::ValPoint, value_or_undef, point, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValSpan(Node node, Node pointer, Node expr_size, Str doc) {
    NodeInit(node, NT::ValSpan, pointer, expr_size, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValString(Node node, Str string, STR_KIND str_kind, Str doc) {
    NodeInit(node, NT::ValString, string, HandleInvalid, HandleInvalid, HandleInvalid, uint8_t(str_kind), 0, doc);
}

inline void InitValTrue(Node node, Str doc) {
    NodeInit(node, NT::ValTrue, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValUndef(Node node, Str doc) {
    NodeInit(node, NT::ValUndef, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

inline void InitValVoid(Node node, Str doc) {
    NodeInit(node, NT::ValVoid, HandleInvalid, HandleInvalid, HandleInvalid, HandleInvalid, 0, 0, doc);
}

/* @AUTOGEN-END@ */
// clang-format on

struct NodeDesc {
  uint64_t node_field_bits;
  uint64_t string_field_bits;
  uint64_t bool_field_bits;
};

// For each NT described which fields (regular / bool) are present
// We have aboutr 45 regular and very few bool fields. So there is headroom in
// the biy vec
extern NodeDesc GlobalNodeDescs[];

const char* EnumToString(MOD_PARAM_KIND x);
const char* EnumToString(MACRO_PARAM_KIND x);
const char* EnumToString(STR_KIND x);
const char* EnumToString(BASE_TYPE_KIND x);

// default is MACRO_PARAM_KIND::INVALID
MACRO_PARAM_KIND MACRO_PARAM_KIND_FromString(std::string_view name);

// default is MOD_PARAM_KIND::INVALID
MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name);

// default is BASE_TYPE_KIND::INVALID
BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name);

ASSIGNMENT_KIND ASSIGNMENT_KIND_FromString(std::string_view name);

NT KeywordToNT(std::string_view kw);

}  // namespace cwerg::fe
