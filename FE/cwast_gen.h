#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <array>
#include <cstdint>
#include <cstring>
#include <unordered_map>
#include <map>

#include "Util/handle.h"
#include "Util/immutable.h"
#include "Util/stripe.h"

namespace cwerg::fe {

uint8_t constexpr kKindStr = 100;
uint8_t constexpr kKindName = 101;

enum class NT : uint8_t;  // "node type"
enum class BF : uint8_t;  // "bit flag"

enum class BINARY_EXPR_KIND : uint8_t;
enum class UNARY_EXPR_KIND : uint8_t;
enum class POINTER_EXPR_KIND : uint8_t;
enum class BASE_TYPE_KIND : uint8_t;
enum class STR_KIND : uint8_t;
enum class MACRO_PARAM_KIND : uint8_t;
enum class MOD_PARAM_KIND : uint8_t;
enum class ASSIGNMENT_KIND : uint8_t;

extern const std::array<uint16_t, 17> BF2MASK;

inline uint16_t Mask(BF val) { return BF2MASK[int(val)]; }

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

constexpr const Str StrInvalid(0);
constexpr const Node NodeInvalid(kHandleInvalid);

extern ImmutablePool gNamePool;

// =======================================
// Node API
// =======================================
struct SrcLoc {
  uint32_t line;
  uint32_t col;
  uint32_t file;
};

const SrcLoc SrcLocInvalid(0, 0, 0);

struct NodeCore {
  NT kind;
  union {
    uint8_t other_kind;
    BINARY_EXPR_KIND binary_expr_kind;
    UNARY_EXPR_KIND unary_expr_kind;
    MACRO_PARAM_KIND macro_param_kind;
    MOD_PARAM_KIND mod_param_kind;
    ASSIGNMENT_KIND assignment_kind;
    BASE_TYPE_KIND base_type_kind;
    POINTER_EXPR_KIND pointer_expr_kind;
    STR_KIND str_kind;
  };
  uint16_t compressed_flags;
  Handle children[4];
  Handle next;
};

struct NodeExtra {
  Str comment;
  SrcLoc x_srcloc;
  // TODO: add typeninfo
  union {
    Node x_symbol;
    Node x_target;
    uint32_t x_offset;
  };
};

using SymTab = std::map<Name, Node>;

struct NodeAuxTyping {
  union {
    Node x_import;
    Node x_module;
    SymTab* x_symtab;
  };
};

extern struct Stripe<NodeCore, Node> gNodeCore;
extern struct Stripe<NodeExtra, Node> gNodeExtra;
extern struct Stripe<NodeAuxTyping, Node> gNodeAuxTyping;

extern struct StripeGroup gStripeGroupNode;

inline NT Node_kind(Node node) { return gNodeCore[node].kind; }
inline Node& Node_next(Node node) { return (Node&)gNodeCore[node].next; }
//
inline Str& Node_comment(Node node) { return gNodeExtra[node].comment; }
inline SrcLoc& Node_srcloc(Node node) { return gNodeExtra[node].x_srcloc; }
inline Node& Node_x_symbol(Node node) { return gNodeExtra[node].x_symbol; }
inline Node& Node_x_target(Node node) { return gNodeExtra[node].x_target; }
inline uint32_t& Node_x_offset(Node node) { return gNodeExtra[node].x_offset; }

inline Node& Node_x_import(Node node) { return gNodeAuxTyping[node].x_import; }
inline Node& Node_x_module(Node node) { return gNodeAuxTyping[node].x_import; }
inline SymTab*& Node_x_symtab(Node node) { return gNodeAuxTyping[node].x_symtab; }

inline bool Node_has_flag(Node node, BF bf) {
  return gNodeCore[node].compressed_flags & Mask(bf);
}
inline void Node_set_flag(Node node, BF bf) {
  gNodeCore[node].compressed_flags |= Mask(bf);
}
inline void Node_clr_flag(Node node, BF bf) {
  gNodeCore[node].compressed_flags &= ~Mask(bf);
}
inline uint16_t& Node_compressed_flags(Node node) {
  return gNodeCore[node].compressed_flags;
}

inline Node NodeNew(NT kind) {
  Node out = Node(kind, gStripeGroupNode.New().index());
  return out;
}

inline void NodeInit(Node node, NT kind, Handle child0, Handle child1,
                     Handle child2, Handle child3, uint8_t other_kind,
                     uint16_t bits, Str doc, const SrcLoc& srcloc) {
  NodeCore& core = gNodeCore[node];
  core.kind = kind;
  core.other_kind = other_kind;
  core.children[0] = child0;
  core.children[1] = child1;
  core.children[2] = child2;
  core.children[3] = child3;
  core.next = kHandleInvalid;
  core.compressed_flags = bits;
  //
  NodeExtra& extra = gNodeExtra[node];
  extra.comment = doc;
  extra.x_srcloc = srcloc;
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

inline bool NameIsEmpty(Name name) {
  return gNamePool.Data(gNameCore[name].name)[0] == '\0';
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

inline bool StrIsEmpty(Str str) {
  return gStringPool.Data(str.index())[0] == '\0';
}

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
    body_mod = 7,  // slot: 2
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
    params_mod = 33,  // slot: 1
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

enum class BF : uint8_t {
    invalid = 0,
    BUILTIN = 1,
    INIT = 2,
    FINI = 3,
    EXTERN = 4,
    CDECL = 5,
    POLY = 6,
    PUB = 7,
    MUT = 8,
    PRESERVE_MUT = 9,
    REF = 10,
    COLON = 11,
    WRAPPED = 12,
    UNCHECKED = 13,
    UNTAGGED = 14,
    ARG_REF = 15,
    RES_REF = 16,
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
inline Node Node_params_mod(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_params_macro(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_args(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_args_mod(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_items(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_fields(Node n) { return Node(gNodeCore[n].children[1]); }
inline Node Node_types(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_inits(Node n) { return Node(gNodeCore[n].children[0]); }
inline Node Node_gen_ids(Node n) { return Node(gNodeCore[n].children[2]); }
inline Node Node_body_mod(Node n) { return Node(gNodeCore[n].children[2]); }
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
inline void InitCase(Node node, Node cond, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Case, kHandleInvalid, cond, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void InitDefEnum(Node node, Name name, BASE_TYPE_KIND base_type_kind, Node items, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefEnum, name, items, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), bits, doc, srcloc);
}

inline void InitDefFun(Node node, Name name, Node params, Node result, Node body, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefFun, name, params, result, body, 0, bits, doc, srcloc);
}

inline void InitDefGlobal(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefGlobal, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitDefMacro(Node node, Name name, MACRO_PARAM_KIND macro_result_kind, Node params_macro, Node gen_ids, Node body_macro, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMacro, name, params_macro, gen_ids, body_macro, uint8_t(macro_result_kind), bits, doc, srcloc);
}

inline void InitDefMod(Node node, Name name, Node params_mod, Node body_mod, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMod, name, params_mod, body_mod, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitDefRec(Node node, Name name, Node fields, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefRec, name, fields, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitDefType(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefType, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitDefVar(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefVar, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitEnumVal(Node node, Name name, Node value_or_auto, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::EnumVal, name, value_or_auto, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitEphemeralList(Node node, Node args, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::EphemeralList, kHandleInvalid, args, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitExpr1(Node node, UNARY_EXPR_KIND unary_expr_kind, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr1, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(unary_expr_kind), 0, doc, srcloc);
}

inline void InitExpr2(Node node, BINARY_EXPR_KIND binary_expr_kind, Node expr1, Node expr2, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr2, expr1, expr2, kHandleInvalid, kHandleInvalid, uint8_t(binary_expr_kind), 0, doc, srcloc);
}

inline void InitExpr3(Node node, Node cond, Node expr_t, Node expr_f, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr3, expr_t, cond, expr_f, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprAddrOf(Node node, Node expr_lhs, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprAddrOf, expr_lhs, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitExprAs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprAs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprBitCast(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprBitCast, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprCall(Node node, Node callee, Node args, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprCall, callee, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprDeref(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprDeref, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprField(Node node, Node container, Node field, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprField, container, kHandleInvalid, field, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprFront(Node node, Node container, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprFront, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitExprIndex(Node node, Node container, Node expr_index, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprIndex, container, expr_index, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitExprIs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprIs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprLen(Node node, Node container, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprLen, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprNarrow(Node node, Node expr, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprNarrow, expr, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitExprOffsetof(Node node, Node type, Node field, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprOffsetof, kHandleInvalid, type, field, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprParen(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprParen, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprPointer(Node node, POINTER_EXPR_KIND pointer_expr_kind, Node expr1, Node expr2, Node expr_bound_or_undef, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprPointer, expr1, expr2, expr_bound_or_undef, kHandleInvalid, uint8_t(pointer_expr_kind), 0, doc, srcloc);
}

inline void InitExprSizeof(Node node, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprSizeof, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprSrcLoc(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprSrcLoc, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprStmt(Node node, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprStmt, kHandleInvalid, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void InitExprStringify(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprStringify, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprTypeId(Node node, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprTypeId, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprUnionTag(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnionTag, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprUnionUntagged(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnionUntagged, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprUnsafeCast(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnsafeCast, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprUnwrap(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnwrap, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprWiden(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprWiden, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitExprWrap(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprWrap, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitFunParam(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::FunParam, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitId(Node node, Name mod_name, Name base_name, Name enum_name, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Id, mod_name, base_name, enum_name, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitImport(Node node, Name name, Str path, Node args_mod, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Import, name, path, args_mod, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitMacroFor(Node node, Name name, Name name_list, Node body_for, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroFor, name, name_list, body_for, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitMacroId(Node node, Name name, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroId, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitMacroInvoke(Node node, Name name, Node args, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroInvoke, name, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitMacroParam(Node node, Name name, MACRO_PARAM_KIND macro_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(macro_param_kind), 0, doc, srcloc);
}

inline void InitModParam(Node node, Name name, MOD_PARAM_KIND mod_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ModParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(mod_param_kind), 0, doc, srcloc);
}

inline void InitRecField(Node node, Name name, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::RecField, name, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtAssignment(Node node, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtBlock(Node node, Name label, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtBlock, label, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void InitStmtBreak(Node node, Name target, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtBreak, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtCompoundAssignment(Node node, ASSIGNMENT_KIND assignment_kind, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCompoundAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, uint8_t(assignment_kind), 0, doc, srcloc);
}

inline void InitStmtCond(Node node, Node cases, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCond, cases, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtContinue(Node node, Name target, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtContinue, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtDefer(Node node, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtDefer, kHandleInvalid, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void InitStmtExpr(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtExpr, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtIf(Node node, Node cond, Node body_t, Node body_f, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtIf, body_t, cond, body_f, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtReturn(Node node, Node expr_ret, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtReturn, expr_ret, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtStaticAssert(Node node, Node cond, Str message, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtStaticAssert, message, cond, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitStmtTrap(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtTrap, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitTypeAuto(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitTypeBase(Node node, BASE_TYPE_KIND base_type_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeBase, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), 0, doc, srcloc);
}

inline void InitTypeFun(Node node, Node params, Node result, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeFun, kHandleInvalid, params, result, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitTypeOf(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeOf, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitTypePtr(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypePtr, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitTypeSpan(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeSpan, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitTypeUnion(Node node, Node types, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeUnion, types, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void InitTypeUnionDelta(Node node, Node type, Node subtrahend, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeUnionDelta, subtrahend, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitTypeVec(Node node, Node size, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeVec, size, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValAuto(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValCompound(Node node, Node type_or_auto, Node inits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValCompound, inits, type_or_auto, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValFalse(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValFalse, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValNum(Node node, Str number, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValNum, number, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValPoint(Node node, Node value_or_undef, Node point, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValPoint, value_or_undef, point, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValSpan(Node node, Node pointer, Node expr_size, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValSpan, pointer, expr_size, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValString(Node node, Str string, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValString, string, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValTrue(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValTrue, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValUndef(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValUndef, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void InitValVoid(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValVoid, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

/* @AUTOGEN-END@ */
// clang-format on

inline MOD_PARAM_KIND& Node_mod_param_kind(Node n) {
  return gNodeCore[n].mod_param_kind;
}

inline MACRO_PARAM_KIND& Node_macro_param_kind(Node n) {
  return gNodeCore[n].macro_param_kind;
}

inline MACRO_PARAM_KIND& Node_macro_result_kind(Node n) {
  return gNodeCore[n].macro_param_kind;
}

inline ASSIGNMENT_KIND Node_assignment_kind(Node n) {
  return gNodeCore[n].assignment_kind;
}

inline BASE_TYPE_KIND Node_base_type_kind(Node n) {
  return gNodeCore[n].base_type_kind;
}

inline POINTER_EXPR_KIND Node_pointer_expr_kind(Node n) {
  return gNodeCore[n].pointer_expr_kind;
}

inline UNARY_EXPR_KIND Node_unary_expr_kind(Node n) {
  return gNodeCore[n].unary_expr_kind;
}

inline BINARY_EXPR_KIND Node_binary_expr_kind(Node n) {
  return gNodeCore[n].binary_expr_kind;
}

inline STR_KIND Node_str_kind(Node n) { return gNodeCore[n].str_kind; }

struct NodeDesc {
  uint64_t node_field_bits;
  uint64_t string_field_bits;
  uint32_t bool_field_bits;
};

// For each NT described which fields (regular / bool) are present
// We have aboutr 45 regular and very few bool fields. So there is headroom in
// the biy vec
extern const NodeDesc GlobalNodeDescs[];

const char* EnumToString(MOD_PARAM_KIND x);
const char* EnumToString(MACRO_PARAM_KIND x);
const char* EnumToString(STR_KIND x);
const char* EnumToString(BASE_TYPE_KIND x);
const char* EnumToString(BF x);
const char* EnumToString(NT x);
const char* EnumToString(POINTER_EXPR_KIND x);
const char* EnumToString(BINARY_EXPR_KIND x);
const char* EnumToString(ASSIGNMENT_KIND x);

// default is MACRO_PARAM_KIND::INVALID
MACRO_PARAM_KIND MACRO_PARAM_KIND_FromString(std::string_view name);

// default is MOD_PARAM_KIND::INVALID
MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name);

// default is BASE_TYPE_KIND::INVALID
BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name);

ASSIGNMENT_KIND ASSIGNMENT_KIND_FromString(std::string_view name);

BF BF_FromString(std::string_view name);

NT KeywordToNT(std::string_view kw);

}  // namespace cwerg::fe
