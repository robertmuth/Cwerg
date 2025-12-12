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

extern BASE_TYPE_KIND MakeSint(int bitwidth);
extern BASE_TYPE_KIND MakeUint(int bitwidth);

// TODO: change this to int64_t or uint64_t
typedef int SizeOrDim;

constexpr const SizeOrDim kSizeOrDimInvalid = -1;

extern SizeOrDim BaseTypeKindByteSize(BASE_TYPE_KIND kind);

extern const std::array<uint16_t, 17> BF2MASK;

inline uint16_t Mask(BF val) { return BF2MASK[int(val)]; }

struct Node : public Handle {
  constexpr Node(NT kind, uint32_t index) : Handle(index, uint8_t(kind)) {}
  constexpr Node() : Handle(0, 0) {}
  explicit constexpr Node(Handle ref) : Handle(ref.value) {}
  NT kind() const { return NT(raw_kind()); }
};

extern ImmutablePool gStringPool;

struct Str : public Handle {
  explicit constexpr Str(uint32_t index) : Handle(index, kKindStr) {}
  explicit Str(Handle ref) : Handle(ref.value) {}

  bool operator<(const Str& other) const {
    if (index() == other.index()) return false;
    return strcmp(gStringPool.Data(index()), gStringPool.Data(other.index())) <
           0;
  }
};

extern ImmutablePool gNamePool;

struct Name : public Handle {
  explicit constexpr Name(uint32_t index) : Handle(index, kKindName) {}

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

struct Const : public Handle {
  explicit constexpr Const(uint32_t index, BASE_TYPE_KIND kind)
      : Handle(index, uint8_t(kind)) {}
  // only used for kConstInvalid
  explicit constexpr Const(uint32_t index) : Handle(index, 0) {}
  explicit constexpr Const(Handle ref) : Handle(ref.value) {}

  BASE_TYPE_KIND kind() const { return BASE_TYPE_KIND(raw_kind()); }
  bool IsShort() const { return int32_t(value) < 0; }

  // 0 is a perfectly good value for the "index"
  // so we have to redefine what it means to be null
  bool isnull() const { return raw_kind() == 0; }
};

constexpr const Str kStrInvalid(0);
constexpr const Name kNameInvalid(0);
constexpr const Node kNodeInvalid(kHandleInvalid);
constexpr const CanonType kCanonTypeInvalid(kHandleInvalid);

constexpr const Const kConstInvalid(0);

// =======================================
// Node API
// =======================================
struct SrcLoc {
  uint32_t line;
  uint32_t col;
  Name file = kNameInvalid;
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
  Const x_eval;
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
inline Node& Node_child_node(Node node, int slot) {
  return gNodeCore[node].children_node[slot];
}
inline Name& Node_child_name(Node node, int slot) {
  return gNodeCore[node].children_name[slot];
}
inline Str& Node_child_str(Node node, int slot) {
  return gNodeCore[node].children_str[slot];
}

inline int NodeNumSiblings(Node node) {
  int n = 0;
  for (; !node.isnull(); node = Node_next(node)) {
    ++n;
  }
  return n;
}

inline Node NodeLastSibling(Node node) {
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
inline Const& Node_x_eval(Node node) { return gNodeExtra[node].x_eval; }
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
  ASSERT(node.kind() == kind, node);
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

enum class NFD_X_FIELD : uint8_t {
  invalid = 0,
  type = 1,
  symbol = 2,
  eval = 3,
  target = 4,
  poly_mod = 5,
  offset = 6,
};

enum class NFD_KIND : uint8_t {
  INVALID = 0,
  STR,
  NAME,
  NODE,
  LIST,
};

// clang-format off
/* @AUTOGEN-START@ */
enum class NFD_SLOT : uint8_t {
    invalid = 0,
    args = 1,  // slot: 1 LIST
    args_mod = 2,  // slot: 2 LIST
    body = 3,  // slot: 3 LIST
    body_f = 4,  // slot: 3 LIST
    body_for = 5,  // slot: 2 LIST
    body_macro = 6,  // slot: 3 LIST
    body_mod = 7,  // slot: 3 LIST
    body_t = 8,  // slot: 2 LIST
    callee = 9,  // slot: 0 NODE
    cases = 10,  // slot: 0 LIST
    cond = 11,  // slot: 1 NODE
    container = 12,  // slot: 0 NODE
    enum_name = 13,  // slot: 1 NAME
    expr = 14,  // slot: 0 NODE
    expr1 = 15,  // slot: 0 NODE
    expr2 = 16,  // slot: 1 NODE
    expr_bound_or_undef = 17,  // slot: 2 NODE
    expr_f = 18,  // slot: 3 NODE
    expr_index = 19,  // slot: 1 NODE
    expr_lhs = 20,  // slot: 0 NODE
    expr_ret = 21,  // slot: 0 NODE
    expr_rhs = 22,  // slot: 1 NODE
    expr_size = 23,  // slot: 1 NODE
    expr_t = 24,  // slot: 2 NODE
    field = 25,  // slot: 2 NODE
    fields = 26,  // slot: 1 LIST
    gen_ids = 27,  // slot: 2 LIST
    initial_or_undef_or_auto = 28,  // slot: 2 NODE
    inits = 29,  // slot: 2 LIST
    items = 30,  // slot: 1 LIST
    label = 31,  // slot: 0 NAME
    lhs = 32,  // slot: 0 NODE
    message = 33,  // slot: 2 STR
    name = 34,  // slot: 0 NAME
    name_list = 35,  // slot: 1 NAME
    number = 36,  // slot: 0 STR
    params = 37,  // slot: 1 LIST
    params_macro = 38,  // slot: 1 LIST
    params_mod = 39,  // slot: 1 LIST
    path = 40,  // slot: 1 STR
    point_or_undef = 41,  // slot: 1 NODE
    pointer = 42,  // slot: 0 NODE
    result = 43,  // slot: 2 NODE
    size = 44,  // slot: 0 NODE
    string = 45,  // slot: 0 STR
    subtrahend = 46,  // slot: 2 NODE
    target = 47,  // slot: 0 NAME
    type = 48,  // slot: 1 NODE
    type_or_auto = 49,  // slot: 1 NODE
    types = 50,  // slot: 0 LIST
    value_or_auto = 51,  // slot: 1 NODE
    value_or_undef = 52,  // slot: 0 NODE
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
    ExprUnwrap = 36,
    ExprWiden = 37,
    ExprWrap = 38,
    FunParam = 39,
    Id = 40,
    Import = 41,
    MacroFor = 42,
    MacroId = 43,
    MacroInvoke = 44,
    MacroParam = 45,
    ModParam = 46,
    RecField = 47,
    StmtAssignment = 48,
    StmtBlock = 49,
    StmtBreak = 50,
    StmtCompoundAssignment = 51,
    StmtCond = 52,
    StmtContinue = 53,
    StmtDefer = 54,
    StmtExpr = 55,
    StmtIf = 56,
    StmtReturn = 57,
    StmtStaticAssert = 58,
    StmtTrap = 59,
    TypeAuto = 60,
    TypeBase = 61,
    TypeFun = 62,
    TypeOf = 63,
    TypePtr = 64,
    TypeSpan = 65,
    TypeUnion = 66,
    TypeUnionDelta = 67,
    TypeVec = 68,
    ValAuto = 69,
    ValCompound = 70,
    ValNum = 71,
    ValPoint = 72,
    ValSpan = 73,
    ValString = 74,
    ValUndef = 75,
    ValVoid = 76,
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
    SHR = 8,
    SHL = 9,
    ROTR = 10,
    ROTL = 11,
    AND = 12,
    OR = 13,
    XOR = 14,
    EQ = 15,
    NE = 16,
    LT = 17,
    LE = 18,
    GT = 19,
    GE = 20,
    ANDSC = 21,
    ORSC = 22,
    PDELTA = 23,
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
    SINT = 16,
    S8 = 17,
    S16 = 18,
    S32 = 19,
    S64 = 20,
    UINT = 32,
    U8 = 33,
    U16 = 34,
    U32 = 35,
    U64 = 36,
    R32 = 51,
    R64 = 52,
    BOOL = 65,
    TYPEID = 80,
    VOID = 96,
    NORET = 97,
    UNDEF = 112,
    SYM_ADDR = 113,
    FUN_ADDR = 114,
    COMPOUND = 115,
    SPAN = 116,
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
inline Str& Node_message(Node n) { return gNodeCore[n].children_str[2]; }
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
inline Node& Node_inits(Node n) { return gNodeCore[n].children_node[2]; }
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
inline Node& Node_point_or_undef(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_type(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_subtrahend(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_type_or_auto(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_result(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_size(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_expr_size(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_index(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr(Node n) { return gNodeCore[n].children_node[0]; }
inline Node& Node_cond(Node n) { return gNodeCore[n].children_node[1]; }
inline Node& Node_expr_t(Node n) { return gNodeCore[n].children_node[2]; }
inline Node& Node_expr_f(Node n) { return gNodeCore[n].children_node[3]; }
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

inline void NodeInitDefEnum(Node node, Name name, BASE_TYPE_KIND base_type_kind, Node items, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefEnum, name, items, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitDefFun(Node node, Name name, Node params, Node result, Node body, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefFun, name, params, result, body, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitDefGlobal(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefGlobal, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitDefMacro(Node node, Name name, MACRO_RESULT_KIND macro_result_kind, Node params_macro, Node gen_ids, Node body_macro, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMacro, name, params_macro, gen_ids, body_macro, uint8_t(macro_result_kind), bits, doc, srcloc);
}

inline void NodeInitDefMod(Node node, Name name, Node params_mod, Node body_mod, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::DefMod, name, params_mod, kHandleInvalid, body_mod, 0, bits, doc, srcloc);
}

inline void NodeInitDefRec(Node node, Name name, Node fields, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefRec, name, fields, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitDefType(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefType, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitDefVar(Node node, Name name, Node type_or_auto, Node initial_or_undef_or_auto, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::DefVar, name, type_or_auto, initial_or_undef_or_auto, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitEnumVal(Node node, Name name, Node value_or_auto, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::EnumVal, name, value_or_auto, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitEphemeralList(Node node, Node args, uint16_t bits, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::EphemeralList, kHandleInvalid, args, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
}

inline void NodeInitExpr1(Node node, UNARY_EXPR_KIND unary_expr_kind, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::Expr1, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(unary_expr_kind), 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExpr2(Node node, BINARY_EXPR_KIND binary_expr_kind, Node expr1, Node expr2, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::Expr2, expr1, expr2, kHandleInvalid, kHandleInvalid, uint8_t(binary_expr_kind), 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExpr3(Node node, Node cond, Node expr_t, Node expr_f, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::Expr3, kHandleInvalid, cond, expr_t, expr_f, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprAddrOf(Node node, Node expr_lhs, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprAddrOf, expr_lhs, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprAs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprAs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprBitCast(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprBitCast, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprCall(Node node, Node callee, Node args, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprCall, callee, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprDeref(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprDeref, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprField(Node node, Node container, Node field, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprField, container, kHandleInvalid, field, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprFront(Node node, Node container, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprFront, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprIndex(Node node, Node container, Node expr_index, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprIndex, container, expr_index, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprIs(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprIs, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprLen(Node node, Node container, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprLen, container, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprNarrow(Node node, Node expr, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprNarrow, expr, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprOffsetof(Node node, Node type, Node field, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprOffsetof, kHandleInvalid, type, field, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprParen(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprParen, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprPointer(Node node, POINTER_EXPR_KIND pointer_expr_kind, Node expr1, Node expr2, Node expr_bound_or_undef, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprPointer, expr1, expr2, expr_bound_or_undef, kHandleInvalid, uint8_t(pointer_expr_kind), 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprSizeof(Node node, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprSizeof, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprSrcLoc(Node node, Node expr, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ExprSrcLoc, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitExprStmt(Node node, Node body, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprStmt, kHandleInvalid, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprStringify(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprStringify, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprTypeId(Node node, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprTypeId, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprUnionTag(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprUnionTag, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprUnionUntagged(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprUnionUntagged, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprUnwrap(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprUnwrap, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprWiden(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprWiden, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitExprWrap(Node node, Node expr, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ExprWrap, expr, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitFunParam(Node node, Name name, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::FunParam, name, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitId(Node node, Name name, Name enum_name, Str doc, const SrcLoc& srcloc, Node x_symbol, CanonType x_type) {
    NodeInit(node, NT::Id, name, enum_name, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_symbol(node) = x_symbol;
    Node_x_type(node) = x_type;
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

inline void NodeInitMacroInvoke(Node node, Name name, Node args, Str doc, const SrcLoc& srcloc, Node x_symbol) {
    NodeInit(node, NT::MacroInvoke, name, args, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_symbol(node) = x_symbol;
}

inline void NodeInitMacroParam(Node node, Name name, MACRO_PARAM_KIND macro_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::MacroParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(macro_param_kind), 0, doc, srcloc);
}

inline void NodeInitModParam(Node node, Name name, MOD_PARAM_KIND mod_param_kind, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ModParam, name, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(mod_param_kind), 0, doc, srcloc);
}

inline void NodeInitRecField(Node node, Name name, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::RecField, name, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitStmtAssignment(Node node, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtBlock(Node node, Name label, Node body, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtBlock, label, kHandleInvalid, kHandleInvalid, body, 0, 0, doc, srcloc);
}

inline void NodeInitStmtBreak(Node node, Name target, Str doc, const SrcLoc& srcloc, Node x_target) {
    NodeInit(node, NT::StmtBreak, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_target(node) = x_target;
}

inline void NodeInitStmtCompoundAssignment(Node node, BINARY_EXPR_KIND binary_expr_kind, Node lhs, Node expr_rhs, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCompoundAssignment, lhs, expr_rhs, kHandleInvalid, kHandleInvalid, uint8_t(binary_expr_kind), 0, doc, srcloc);
}

inline void NodeInitStmtCond(Node node, Node cases, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtCond, cases, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtContinue(Node node, Name target, Str doc, const SrcLoc& srcloc, Node x_target) {
    NodeInit(node, NT::StmtContinue, target, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_target(node) = x_target;
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

inline void NodeInitStmtReturn(Node node, Node expr_ret, Str doc, const SrcLoc& srcloc, Node x_target) {
    NodeInit(node, NT::StmtReturn, expr_ret, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_target(node) = x_target;
}

inline void NodeInitStmtStaticAssert(Node node, Node cond, Str message, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtStaticAssert, kHandleInvalid, cond, message, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitStmtTrap(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::StmtTrap, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitTypeAuto(Node node, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeBase(Node node, BASE_TYPE_KIND base_type_kind, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeBase, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, uint8_t(base_type_kind), 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeFun(Node node, Node params, Node result, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeFun, kHandleInvalid, params, result, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeOf(Node node, Node expr, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeOf, expr, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypePtr(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypePtr, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeSpan(Node node, Node type, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeSpan, kHandleInvalid, type, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeUnion(Node node, Node types, uint16_t bits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeUnion, types, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, bits, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeUnionDelta(Node node, Node type, Node subtrahend, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeUnionDelta, kHandleInvalid, type, subtrahend, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitTypeVec(Node node, Node size, Node type, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::TypeVec, size, type, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValAuto(Node node, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValAuto, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValCompound(Node node, Node type_or_auto, Node inits, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValCompound, kHandleInvalid, type_or_auto, inits, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValNum(Node node, Str number, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValNum, number, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValPoint(Node node, Node value_or_undef, Node point_or_undef, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValPoint, value_or_undef, point_or_undef, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValSpan(Node node, Node pointer, Node expr_size, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValSpan, pointer, expr_size, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValString(Node node, Str string, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValString, string, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
}

inline void NodeInitValUndef(Node node, Str doc, const SrcLoc& srcloc) {
    NodeInit(node, NT::ValUndef, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
}

inline void NodeInitValVoid(Node node, Str doc, const SrcLoc& srcloc, CanonType x_type) {
    NodeInit(node, NT::ValVoid, kHandleInvalid, kHandleInvalid, kHandleInvalid, kHandleInvalid, 0, 0, doc, srcloc);
    Node_x_type(node) = x_type;
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
  return Node_point_or_undef(parent) == node &&
         Node_kind(parent) == NT::ValPoint;
}

inline uint8_t Node_other_kind(Node n) { return gNodeCore[n].other_kind; }

inline MOD_PARAM_KIND& Node_mod_param_kind(Node n) {
  return gNodeCore[n].mod_param_kind;
}

inline MACRO_PARAM_KIND& Node_macro_param_kind(Node n) {
  return gNodeCore[n].macro_param_kind;
}

inline MACRO_RESULT_KIND& Node_macro_result_kind(Node n) {
  return gNodeCore[n].macro_result_kind;
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
  return BASE_TYPE_KIND::SINT <= x && x <= BASE_TYPE_KIND::BOOL;
}

inline bool IsInt(BASE_TYPE_KIND x) {
  return BASE_TYPE_KIND::SINT <= x && x <= BASE_TYPE_KIND::U64;
}

inline bool IsSint(BASE_TYPE_KIND x) {
  return BASE_TYPE_KIND::SINT <= x && x <= BASE_TYPE_KIND::S64;
}

inline bool IsReal(BASE_TYPE_KIND x) {
  return BASE_TYPE_KIND::R32 <= x && x <= BASE_TYPE_KIND::R64;
}

inline bool IsUint(BASE_TYPE_KIND x) {
  return BASE_TYPE_KIND::UINT <= x && x <= BASE_TYPE_KIND::U64;
}

inline bool IsArithmetic(BINARY_EXPR_KIND x) {
  return BINARY_EXPR_KIND::ADD <= x && x <= BINARY_EXPR_KIND::XOR;
}

inline bool IsComparison(BINARY_EXPR_KIND x) {
  return BINARY_EXPR_KIND::EQ <= x && x <= BINARY_EXPR_KIND::GE;
}

inline bool IsShortCircuit(BINARY_EXPR_KIND x) {
  return BINARY_EXPR_KIND::ANDSC <= x && x <= BINARY_EXPR_KIND::ORSC;
}

inline STR_KIND Node_str_kind(Node n) { return gNodeCore[n].str_kind; }

struct NodeFieldDesc {
  uint8_t slot;
  NFD_KIND kind;
};

extern const NodeFieldDesc GlobalNodeFieldDescs[];

struct NodeDesc {
  NFD_SLOT node_fields[MAX_NODE_CHILDREN];  // Node fields in their slots
  uint32_t bool_field_bits;                 // which flags are present
  uint32_t x_field_bits;                    // which x_fields are present

  bool has(BF bf) const { return (bool_field_bits >> uint32_t(bf)) & 1; }

  bool has(NFD_X_FIELD x_field) const {
    return (x_field_bits >> uint32_t(x_field)) & 1;
  }
};

// For each NT described which fields (regular / bool) are present
// We have aboutr 45 regular and very few bool fields. So there is headroom in
// the biy vec
extern const NodeDesc GlobalNodeDescs[];

inline bool NodeHasField(Node node, NFD_X_FIELD x_field) {
  return (GlobalNodeDescs[int(node.kind())].x_field_bits >> uint32_t(x_field)) &
         1;
}

const char* EnumToString(MOD_PARAM_KIND x);
const char* EnumToString(MACRO_PARAM_KIND x);
const char* EnumToString(MACRO_RESULT_KIND x);
const char* EnumToString(STR_KIND x);
const char* EnumToString(BF x);
const char* EnumToString_CURLY(BF x);
const char* EnumToString(NT x);
const char* EnumToString(NFD_SLOT x);
const char* EnumToString(UNARY_EXPR_KIND x);
// 2 Variants for POINTER_EXPR_KIND
const char* EnumToString(POINTER_EXPR_KIND x);
const char* EnumToString_POINTER_EXPR_OP(POINTER_EXPR_KIND x);
// 3 Variants for BINARY_EXPR_KIND
const char* EnumToString(BINARY_EXPR_KIND x);                 // ADD
const char* EnumToString_BINARY_EXPR_OP(BINARY_EXPR_KIND x);  // +
const char* EnumToString_ASSIGNMENT_OP(BINARY_EXPR_KIND x);   // +=
//
const char* EnumToString(BASE_TYPE_KIND x);
const char* EnumToString_BASE_TYPE_KIND_LOWER(BASE_TYPE_KIND x);

// default is MACRO_PARAM_KIND::INVALID
MACRO_PARAM_KIND MACRO_PARAM_KIND_FromString(std::string_view name);

// default is MACRO_RESULT_KIND::INVALID
MACRO_RESULT_KIND MACRO_RESULT_KIND_FromString(std::string_view name);

// default is MOD_PARAM_KIND::INVALID
MOD_PARAM_KIND MOD_PARAM_KIND_FromString(std::string_view name);

// default is BASE_TYPE_KIND::INVALID
BASE_TYPE_KIND BASE_TYPE_KIND_LOWER_FromString(std::string_view name);
// BASE_TYPE_KIND BASE_TYPE_KIND_FromString(std::string_view name);

BINARY_EXPR_KIND ASSIGNMENT_OP_FromString(std::string_view name);

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
  Node Last() { return last_; }
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

// Clones gNodeCore, gNodeExtra, gNodeAuxTyping
inline Node NodeCloneBasics(Node node) {
  Node clone = NodeNew(Node_kind(node));
  gNodeCore[clone] = gNodeCore[node];
  Node_next(clone) = kNodeInvalid;

  gNodeExtra[clone] = gNodeExtra[node];
  gNodeAuxTyping[clone] = gNodeAuxTyping[node];
  return clone;
}

// Note:
// * Node_next(result) will be set to kNodeInvalid
// * symbol_map/target_map may be updated
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
    ASSERT(node.kind() == Node_kind(node),
           "mismatched node " << int(node.kind()) << " vs "
                              << EnumToString(Node_kind(node)));
    os << EnumToString(node.kind()) << "(" << node.index() << ")";
  }
  return os;
}

}  // namespace cwerg::fe
