#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <array>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <vector>

#include "Util/assert.h"
#include "Util/handle.h"
#include "Util/immutable.h"
#include "Util/stripe.h"

namespace cwerg::fe {

// These must be larger than the last element of the NT enum
uint8_t constexpr kKindStr = 100;
uint8_t constexpr kKindName = 101;
uint8_t constexpr kKindCanonType = 102;

// some forward declarations
enum class NT : uint8_t;  // "node type"
enum class BF : uint8_t;  // "bit flag"

enum class BINARY_EXPR_KIND : uint8_t;
enum class UNARY_EXPR_KIND : uint8_t;
enum class POINTER_EXPR_KIND : uint8_t;
enum class BASE_TYPE_KIND : uint8_t;
enum class STR_KIND : uint8_t;
enum class MACRO_PARAM_KIND : uint8_t;
enum class MACRO_RESULT_KIND : uint8_t;
enum class MOD_PARAM_KIND : uint8_t;
enum class ASSIGNMENT_KIND : uint8_t;

extern const std::array<uint16_t, 17> BF2MASK;

inline uint16_t Mask(BF val) { return BF2MASK[int(val)]; }

struct Node : public Handle {
  explicit constexpr Node(NT kind = NT(0), uint32_t index = 0)
      : Handle(index, uint8_t(kind)) {}

  explicit constexpr Node(Handle ref) : Handle(ref.value) {}
  NT kind() { return NT(raw_kind()); }
};

extern ImmutablePool gStringPool;

struct Str : public Handle {
  explicit constexpr Str(uint32_t index = 0) : Handle(index, kKindStr) {}
  explicit Str(Handle ref) : Handle(ref.value) {}

  bool operator<(const Str& other) const {
    if (index() == other.index()) return false;
    return strcmp(gStringPool.Data(index()), gStringPool.Data(other.index())) <
           0;
  }
};

extern ImmutablePool gNamePool;

struct Name : public Handle {
  explicit constexpr Name(uint32_t index = 0) : Handle(index, kKindName) {}

  explicit constexpr Name(Handle ref) : Handle(ref.value) {}

  bool operator<(const Name& other) const {
    if (index() == other.index()) return false;
    return strcmp(gNamePool.Data(index()), gNamePool.Data(other.index())) < 0;
  }
};

struct CanonType : public Handle {
  explicit constexpr CanonType(uint32_t index = 0)
      : Handle(index, kKindCanonType) {}

  explicit constexpr CanonType(Handle ref) : Handle(ref.value) {}
};

constexpr const Str kStrInvalid(0);
constexpr const Name kNameInvalid(0);
constexpr const Node kNodeInvalid(kHandleInvalid);
constexpr const CanonType kCanonTypeInvalid(kHandleInvalid);

// =======================================
// Node API
// =======================================
struct SrcLoc {
  uint32_t line;
  uint32_t col;
  Name file;
};

constexpr SrcLoc kSrcLocInvalid(0, 0, kNameInvalid);
constexpr int MAX_NODE_CHILDREN = 4;

struct NodeCore {
  NT kind;
  union {
    uint8_t other_kind;
    BINARY_EXPR_KIND binary_expr_kind;
    UNARY_EXPR_KIND unary_expr_kind;
    MACRO_PARAM_KIND macro_param_kind;
    MACRO_RESULT_KIND macro_result_kind;
    MOD_PARAM_KIND mod_param_kind;
    ASSIGNMENT_KIND assignment_kind;
    BASE_TYPE_KIND base_type_kind;
    POINTER_EXPR_KIND pointer_expr_kind;
    STR_KIND str_kind;
  };
  uint16_t compressed_flags;
  union {
    Handle children_handle[MAX_NODE_CHILDREN];
    Node children_node[MAX_NODE_CHILDREN];
    Str children_str[MAX_NODE_CHILDREN];
    Name children_name[MAX_NODE_CHILDREN];
  };
  Handle next;
};

struct NodeExtra {
  Str comment;
  SrcLoc x_srcloc;
  CanonType x_type;
  union {
    Node x_symbol;
    Node x_target;
    Node x_poly_mod;
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

struct NodeValidation {
  uint32_t dummy;
  bool ref_count;
};

extern struct Stripe<NodeCore, Node> gNodeCore;
extern struct Stripe<NodeExtra, Node> gNodeExtra;
extern struct Stripe<NodeAuxTyping, Node> gNodeAuxTyping;
extern struct Stripe<NodeValidation, Node> gNodeValidation;

extern struct StripeGroup gStripeGroupNode;

inline NT Node_kind(Node node) { return gNodeCore[node].kind; }
inline Node& Node_next(Node node) { return (Node&)gNodeCore[node].next; }

inline int NodeNumSiblings(Node node) {
  int n = 0;
  for (; !node.isnull(); node = Node_next(node)) {
    ++n;
  }
  return n;
}

inline Node NodeLastSiblings(Node node) {
  if (node.isnull()) return node;

  while (!Node_next(node).isnull()) {
    node = Node_next(node);
  }
  return node;
}

//
inline Str& Node_comment(Node node) { return gNodeExtra[node].comment; }
inline SrcLoc& Node_srcloc(Node node) { return gNodeExtra[node].x_srcloc; }
inline Node& Node_x_symbol(Node node) { return gNodeExtra[node].x_symbol; }
inline Node& Node_x_poly_mod(Node node) { return gNodeExtra[node].x_poly_mod; }
inline Node& Node_x_target(Node node) { return gNodeExtra[node].x_target; }
inline uint32_t& Node_x_offset(Node node) { return gNodeExtra[node].x_offset; }
inline CanonType& Node_x_type(Node node) { return gNodeExtra[node].x_type; }

inline Node& Node_x_import(Node node) { return gNodeAuxTyping[node].x_import; }
inline Node& Node_x_module(Node node) { return gNodeAuxTyping[node].x_import; }
inline SymTab*& Node_x_symtab(Node node) {
  return gNodeAuxTyping[node].x_symtab;
}

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
  // ASSERT(out.index() != xxx, "");
  return out;
}

inline bool NodeIsNode(Node node) {
  return node.raw_kind() < kKindStr && !node.isnull();
}

inline void NodeInit(Node node, NT kind, Handle child0, Handle child1,
                     Handle child2, Handle child3, uint8_t other_kind,
                     uint16_t bits, Str doc, const SrcLoc& srcloc) {
  NodeCore& core = gNodeCore[node];
  core.kind = kind;
  core.other_kind = other_kind;
  core.children_handle[0] = child0;
  core.children_handle[1] = child1;
  core.children_handle[2] = child2;
  core.children_handle[3] = child3;
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

inline Name NameNew(std::string_view s) {
  // we want a null byte at the end
  return Name(gNamePool.Intern(s, 1));
}

// TODO: this does not include the the seq
inline const char* NameData(Name name) { return gNamePool.Data(name.index()); }

inline bool NameIsEmpty(Name name) {
  return gNamePool.Data(name.index())[0] == '\0';
}

inline bool NameIsMacro(Name name) {
  return gNamePool.Data(name.index())[0] == '$';
}

inline std::ostream& operator<<(std::ostream& os, Name name) {
  if (name.isnull()) {
    os << "@NULL@";
  } else {
    os << NameData(name);
  }
  return os;
}

inline int NameCmp(Name a, Name b) {
  if (a == b) return 0;
  return strcmp(gNamePool.Data(a.index()), gNamePool.Data(b.index()));
}

inline std::ostream& operator<<(std::ostream& os, const SrcLoc& sl) {
  os << sl.file << ":" << sl.line;
  return os;
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

inline bool StrCmpLt(Str a, Str b) {
  if (a == b) return 0;
  return strcmp(gStringPool.Data(a.index()), gStringPool.Data(b.index())) < 0;
}

extern std::string ExpandStringConstant(Str s);

inline std::ostream& operator<<(std::ostream& os, Str str) {
  os << StrData(str);
  return os;
}

// clang-format off
/* @AUTOGEN-START@ */
enum class NFD_NODE_FIELD : uint8_t {
    invalid = 0,
    args = 1,  // slot: 1
    args_mod = 2,  // slot: 2
    body = 3,  // slot: 3
    body_f = 4,  // slot: 3
    body_for = 5,  // slot: 2
    body_macro = 6,  // slot: 3
    body_mod = 7,  // slot: 3
    body_t = 8,  // slot: 2
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
    enum_name = 1,  // slot: 1
    label = 2,  // slot: 0
    message = 3,  // slot: 0
    name = 4,  // slot: 0
    name_list = 5,  // slot: 1
    number = 6,  // slot: 0
    path = 7,  // slot: 1
    string = 8,  // slot: 0
    target = 9,  // slot: 0
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
    EXPR = 2,
    FIELD = 3,
    TYPE = 4,
    ID_DEF = 5,
    STMT_LIST = 6,
    EXPR_LIST_REST = 7,
};

enum class MACRO_RESULT_KIND : uint8_t {
    INVALID = 0,
    STMT = 1,
    STMT_LIST = 2,
    EXPR = 3,
    EXPR_LIST = 4,
    TYPE = 5,
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

constexpr int SLOT_BODY = 3;

constexpr int SLOT_BODY_T = 2;

// NFK.NAME
inline Name& Node_name(Node n) { return gNodeCore[n].children_name[0]; }
inline Name& Node_enum_name(Node n) { return gNodeCore[n].children_name[1]; }
inline Name& Node_name_list(Node n) { return gNodeCore[n].children_name[1]; }
inline Name& Node_label(Node n) { return gNodeCore[n].children_name[0]; }
inline Name& Node_target(Node n) { return gNodeCore[n].children_name[0]; }

// NFK.STR
inline Str& Node_number(Node n) { return gNodeCore[n].children_str[0]; }
inline Str& Node_string(Node n) { return gNodeCore[n].children_str[0]; }
inline Str& Node_message(Node n) { return gNodeCore[n].children_str[0]; }
inline Str& Node_path(Node n) { return gNodeCore[n].children_str[1]; }

// NFK.LIST
inline Node& Node_params(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_params_mod(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_params_macro(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_args(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_args_mod(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_items(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_fields(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_types(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_inits(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_gen_ids(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_body_mod(Node n) { return gNodeCore[n].children_node[3]; }
inline Node& Node_body(Node n) { return gNodeCore[n].children_node[3]; }
inline Node& Node_body_t(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_body_f(Node n) { return gNodeCore[n].children_node[3]; }
inline Node& Node_body_for(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_body_macro(Node n) { return gNodeCore[n].children_node[3]; }
inline Node& Node_cases(Node n) { return gNodeCore[n].children_node[0]; }

// NFK.NODE
inline Node& Node_field(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_point(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_type(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_subtrahend(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_type_or_auto(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_result(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_size(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_expr_size(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_index(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_cond(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_t(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_expr_f(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_expr1(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_expr2(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_bound_or_undef(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_expr_rhs(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_ret(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_pointer(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_container(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_callee(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_value_or_auto(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_value_or_undef(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_lhs(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_expr_lhs(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_initial_or_undef_or_auto(Node n) { return gNodeCore[n].children_node[2]; }
inline void NodeInitCase(Node node, Node cond, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Case, kHandleInvalid, cond, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void NodeInitDefEnum(Node node, Name name, BASE_TYPE_KIND base_type_kind, Node items, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefEnum, name, items, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), bits, doc, srcloc);
}

inline void NodeInitDefFun(Node node, Name name, Node params, Node result, Node body, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefFun, name, params, result, body, 0, bits, doc, srcloc);
}

inline void NodeInitDefGlobal(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefGlobal, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitDefMacro(Node node, Name name, MACRO_RESULT_KIND macro_result_kind, Node params_macro, Node gen_ids, Node body_macro, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMacro, name, params_macro, gen_ids, body_macro, uint8_t(macro_result_kind), bits, doc, srcloc);
}

inline void NodeInitDefMod(Node node, Name name, Node params_mod, Node body_mod, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMod, name, params_mod, kHandleInvalid, body_mod, 0, bits, doc, srcloc);
}

inline void NodeInitDefRec(Node node, Name name, Node fields, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefRec, name, fields, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitDefType(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefType, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitDefVar(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefVar, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitEnumVal(Node node, Name name, Node value_or_auto, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::EnumVal, name, value_or_auto, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitEphemeralList(Node node, Node args, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::EphemeralList, kHandleInvalid, args, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExpr1(Node node, UNARY_EXPR_KIND unary_expr_kind, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr1, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(unary_expr_kind), 0, doc, srcloc);
}

inline void NodeInitExpr2(Node node, BINARY_EXPR_KIND binary_expr_kind, Node expr1, Node expr2, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr2, expr1, expr2, kHandleInvalid, kHandleInvalid, uint8_t(binary_expr_kind), 0, doc, srcloc);
}

inline void NodeInitExpr3(Node node, Node cond, Node expr_t, Node expr_f, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Expr3, expr_t, cond, expr_f, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprAddrOf(Node node, Node expr_lhs, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprAddrOf, expr_lhs, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExprAs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprAs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprBitCast(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprBitCast, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprCall(Node node, Node callee, Node args, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprCall, callee, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprDeref(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprDeref, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprField(Node node, Node container, Node field, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprField, container, kHandleInvalid, field, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprFront(Node node, Node container, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprFront, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExprIndex(Node node, Node container, Node expr_index, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprIndex, container, expr_index, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExprIs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprIs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprLen(Node node, Node container, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprLen, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprNarrow(Node node, Node expr, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprNarrow, expr, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExprOffsetof(Node node, Node type, Node field, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprOffsetof, kHandleInvalid, type, field, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprParen(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprParen, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprPointer(Node node, POINTER_EXPR_KIND pointer_expr_kind, Node expr1, Node expr2, Node expr_bound_or_undef, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprPointer, expr1, expr2, expr_bound_or_undef, kHandleInvalid, uint8_t(pointer_expr_kind), 0, doc, srcloc);
}

inline void NodeInitExprSizeof(Node node, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprSizeof, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprSrcLoc(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprSrcLoc, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprStmt(Node node, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprStmt, kHandleInvalid, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void NodeInitExprStringify(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprStringify, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprTypeId(Node node, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprTypeId, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprUnionTag(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnionTag, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprUnionUntagged(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnionUntagged, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprUnsafeCast(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnsafeCast, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprUnwrap(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprUnwrap, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprWiden(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprWiden, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprWrap(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprWrap, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitFunParam(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::FunParam, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitId(Node node, Name name, Name enum_name, Str doc, const SrcLoc& srcloc) {
  NodeInit(node, NT::Id, name, enum_name, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitImport(Node node, Name name, Str path, Node args_mod, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::Import, name, path, args_mod, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitMacroFor(Node node, Name name, Name name_list, Node body_for, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroFor, name, name_list, body_for, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitMacroId(Node node, Name name, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroId, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitMacroInvoke(Node node, Name name, Node args, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroInvoke, name, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitMacroParam(Node node, Name name, MACRO_PARAM_KIND macro_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(macro_param_kind), 0, doc, srcloc);
}

inline void NodeInitModParam(Node node, Name name, MOD_PARAM_KIND mod_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ModParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(mod_param_kind), 0, doc, srcloc);
}

inline void NodeInitRecField(Node node, Name name, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::RecField, name, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtAssignment(Node node, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtBlock(Node node, Name label, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtBlock, label, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void NodeInitStmtBreak(Node node, Name target, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtBreak, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtCompoundAssignment(Node node, ASSIGNMENT_KIND assignment_kind, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCompoundAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, uint8_t(assignment_kind), 0, doc, srcloc);
}

inline void NodeInitStmtCond(Node node, Node cases, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCond, cases, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtContinue(Node node, Name target, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtContinue, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtDefer(Node node, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtDefer, kHandleInvalid, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void NodeInitStmtExpr(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtExpr, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtIf(Node node, Node cond, Node body_t, Node body_f, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtIf, kHandleInvalid, cond, body_t, body_f, 0, 0, doc, srcloc);
}

inline void NodeInitStmtReturn(Node node, Node expr_ret, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtReturn, expr_ret, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtStaticAssert(Node node, Node cond, Str message, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtStaticAssert, message, cond, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtTrap(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtTrap, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypeAuto(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypeBase(Node node, BASE_TYPE_KIND base_type_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeBase, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), 0, doc, srcloc);
}

inline void NodeInitTypeFun(Node node, Node params, Node result, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeFun, kHandleInvalid, params, result, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypeOf(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeOf, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypePtr(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypePtr, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitTypeSpan(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeSpan, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitTypeUnion(Node node, Node types, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeUnion, types, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitTypeUnionDelta(Node node, Node type, Node subtrahend, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeUnionDelta, subtrahend, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypeVec(Node node, Node size, Node type, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::TypeVec, size, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValAuto(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValCompound(Node node, Node type_or_auto, Node inits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValCompound, inits, type_or_auto, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValFalse(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValFalse, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValNum(Node node, Str number, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValNum, number, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValPoint(Node node, Node value_or_undef, Node point, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValPoint, value_or_undef, point, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValSpan(Node node, Node pointer, Node expr_size, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValSpan, pointer, expr_size, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValString(Node node, Str string, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValString, string, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValTrue(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValTrue, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValUndef(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValUndef, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValVoid(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValVoid, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

/* @AUTOGEN-END@ */
// clang-format on

// =======================================
// =======================================
inline bool IsFieldNode(Node node, Node parent) {
  return Node_field(parent) == node && (Node_kind(parent) == NT::ExprOffsetof ||
                                        Node_kind(parent) == NT::ExprField);
}

inline bool IsPointNode(Node node, Node parent) {
  return Node_point(parent) == node && Node_kind(parent) == NT::ValPoint;
}

inline MOD_PARAM_KIND& Node_mod_param_kind(Node n) {
  return gNodeCore[n].mod_param_kind;
}

inline MACRO_PARAM_KIND& Node_macro_param_kind(Node n) {
  return gNodeCore[n].macro_param_kind;
}

inline MACRO_RESULT_KIND& Node_macro_result_kind(Node n) {
  return gNodeCore[n].macro_result_kind;
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

inline bool IsNumber(BASE_TYPE_KIND x) {
  return int(BASE_TYPE_KIND::SINT) <= int(x) &&
         int(x) <= int(BASE_TYPE_KIND::R64);
}

inline bool IsInt(BASE_TYPE_KIND x) {
  return int(BASE_TYPE_KIND::SINT) <= int(x) &&
         int(x) <= int(BASE_TYPE_KIND::U64);
}

inline bool ResultIsBool(BINARY_EXPR_KIND x) {
  return int(BINARY_EXPR_KIND::EQ) <= int(x) &&
         int(x) <= int(BINARY_EXPR_KIND::ORSC);
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

// default is MACRO_RESULT_KIND::INVALID
MACRO_RESULT_KIND MACRO_RESULT_KIND_FromString(std::string_view name);

// default is MOD_PARAM_KIND::INVALID
MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name);

// default is BASE_TYPE_KIND::INVALID
BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name);

ASSIGNMENT_KIND ASSIGNMENT_KIND_FromString(std::string_view name);

BF BF_FromString(std::string_view name);

NT KeywordToNT(std::string_view kw);

inline void VisitAstRecursivelyPost(Node node,
                                    std::function<void(Node)> visitor) {
  const auto& core = gNodeCore[node];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;
    do {
      VisitAstRecursivelyPost(child, visitor);
      child = Node_next(child);
    } while (!child.isnull());
  }
  visitor(node);
}

inline void VisitAstRecursivelyPre(Node node,
                                   std::function<bool(Node, Node)> visitor,
                                   Node parent) {
  if (visitor(node, parent)) return;

  const auto& core = gNodeCore[node];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;
    do {
      VisitAstRecursivelyPre(child, visitor, node);
      child = Node_next(child);
    } while (!child.isnull());
  }
}

inline void VisitAstRecursivelyPost(Node node,
                                    std::function<void(Node, Node)> visitor,
                                    Node parent) {
  const auto& core = gNodeCore[node];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;

    do {
      // allow the visitor to update the next field
      // (used by NodeFreeRecursively)
      Node next = Node_next(child);
      VisitAstRecursivelyPost(child, visitor, node);
      child = next;
    } while (!child.isnull());
  }
  visitor(node, parent);
}

inline void VisitAstRecursivelyPreAndPost(
    Node node, std::function<void(Node, Node)> pre_visitor,
    std::function<void(Node, Node)> post_visitor, Node parent) {
  const auto& core = gNodeCore[node];
  pre_visitor(node, parent);

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;
    do {
      VisitAstRecursivelyPreAndPost(child, pre_visitor, post_visitor, node);
      child = Node_next(child);
    } while (!child.isnull());
  }
  post_visitor(node, parent);
}

inline void VisitAstRecursivelyWithScopeTracking(
    Node node, std::function<void(Node, Node)> pre_visitor,
    std::function<void(Node)> scope_enter, std::function<void(Node)> scope_exit,
    Node parent) {
  const auto& core = gNodeCore[node];

  pre_visitor(node, parent);

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;
    bool is_new_scope =
        (i == SLOT_BODY) || (Node_kind(node) == NT::StmtIf && i == SLOT_BODY_T);
    if (is_new_scope) {
      scope_enter(node);
    }

    do {
      VisitAstRecursivelyWithScopeTracking(child, pre_visitor, scope_enter,
                                           scope_exit, node);
      child = Node_next(child);
    } while (!child.isnull());
    if (is_new_scope) {
      scope_exit(node);
    }
  }
}

class NodeChain {
  Node first_ = kNodeInvalid;
  Node last_ = kNodeInvalid;

 public:
  NodeChain() = default;

  void Append(Node node) {
    if (node.isnull()) {
      return;
    }
    if (first_.isnull()) {
      first_ = node;
      last_ = node;
    } else {
      Node_next(last_) = node;
      last_ = node;
    }

    while (!Node_next(last_).isnull()) {
      last_ = Node_next(last_);
    }
  }

  Node First() { return first_; }
};

inline void MaybeReplaceAstRecursively(
    Node node, std::function<Node(Node, Node)> replacer) {
  // std::cout << "<<< MaybeReplaceAstRecursivelyPost " <<
  // EnumToString(Node_kind(node)) << "\n";
  auto& core = gNodeCore[node];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) continue;

    NodeChain new_children;
    do {
      Node next = Node_next(child);
      Node_next(child) = kNodeInvalid;
      Node new_child = replacer(child, node);
      if (child == new_child) {
        MaybeReplaceAstRecursively(child, replacer);
      }
      new_children.Append(new_child);
      child = next;
    } while (!child.isnull());
    core.children_node[i] = new_children.First();
  }
}

inline void MaybeReplaceAstRecursivelyPost(
    Node node, std::function<Node(Node, Node)> replacer, Node parent) {
  // std::cout << "<<< MaybeReplaceAstRecursivelyPost " <<
  // EnumToString(Node_kind(node)) << "\n";
  auto& core = gNodeCore[node];

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    Node child = core.children_node[i];
    if (!NodeIsNode(child)) {
      core.children_node[i] = child;
      continue;
    }
    NodeChain new_children;

    do {
      Node next = Node_next(child);
      Node_next(child) = kNodeInvalid;
      MaybeReplaceAstRecursivelyPost(child, replacer, node);

      Node new_child = replacer(child, node);
      new_children.Append(new_child);
      child = next;
    } while (!child.isnull());
    core.children_node[i] = new_children.First();
  }
  // std::cout << ">>> MaybeReplaceAstRecursivelyPost " <<
  // EnumToString(Node_kind(node)) << "\n";
}

inline Node GetWithDefault(const std::map<Node, Node>& m, Node node) {
  auto it = m.find(node);
  return (it == m.end()) ? node : it->second;
}

void RemoveNodesOfType(Node node, NT kind);

inline Node NodeCloneBasics(Node node) {
  Node clone = NodeNew(Node_kind(node));
  gNodeCore[clone] = gNodeCore[node];
  Node_next(clone) = kNodeInvalid;

  gNodeExtra[clone] = gNodeExtra[node];
  gNodeAuxTyping[clone] = gNodeAuxTyping[node];
  return clone;
}

// Note: Node_next(result) will be set to kNodeInvalid
Node NodeCloneRecursively(Node node, std::map<Node, Node>* symbol_map,
                          std::map<Node, Node>* target_map);

// TODO: move this to a helper lib
struct CompilerError : public std::ostream, private std::streambuf {
  CompilerError(const SrcLoc& srcloc) : std::ostream(this) {
    std::cerr << "Error " << srcloc.file << ":" << srcloc.line << ": ";
  }

  ~CompilerError() {
    std::cerr.put('\n');
    exit(1);
  }

 private:
  int overflow(int c) override {
    std::cerr.put(c);
    return 0;
  }
};

inline void NodeFree(Node node) {
  gNodeCore[node].kind = NT::invalid;
  gNodeCore[node].next = kNodeInvalid;

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    gNodeCore[node].children_handle[i] = kHandleInvalid;
  }
}

inline void NodeFreeRecursively(Node node) {
  VisitAstRecursivelyPost(
      node, [](Node node, Node parent) { NodeFree(node); }, kNodeInvalid);
}

inline Name Node_name_or_invalid(Node node) {
  switch (Node_kind(node)) {
    case NT::Id:
    case NT::DefGlobal:
    case NT::DefFun:
    case NT::DefVar:
    case NT::DefType:
    case NT::DefRec:
    case NT::DefEnum:
    case NT::DefMacro:
    //
    case NT::FunParam:
    case NT::MacroId:
    case NT::MacroFor:
    case NT::MacroInvoke:
    case NT::MacroParam:
    case NT::ModParam:
      return Node_name(node);
    default:
      return kNameInvalid;
  }
}
inline std::ostream& operator<<(std::ostream& os, Node node) {
  if (node.isnull()) {
    os << "@NULL@";
  } else {
    os << EnumToString(node.kind()) << "(" << node.index() << ")";
  }
  return os;
}

}  // namespace cwerg::fe
