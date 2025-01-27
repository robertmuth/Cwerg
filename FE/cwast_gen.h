#include <cstdint>

#include "Util/handle.h"
#include "Util/stripe.h"

namespace cwerg::fe {


uint8_t constexpr kKindStr = 100;
uint8_t constexpr kKindName = 101;

enum class NT : uint8_t;

struct Str : public Handle {
  explicit Str(uint32_t index = 0) : Handle(index, kKindStr) {}
  explicit Str(Handle ref) : Handle(ref.value) {}
};

struct Node : public Handle {
  explicit constexpr Node(NT kind, uint32_t index = 0)
      : Handle(index, uint8_t(kind)) {}

  explicit constexpr Node(Handle ref) : Handle(ref.value) {}
};

struct Name : public Handle {
  explicit constexpr Name(uint32_t index = 0)
      : Handle(index, kKindName) {}

  explicit constexpr Name(Handle ref) : Handle(ref.value) {}
};

constexpr const Handle HandleInvalid(0, 0);

struct NodeCore {
  NT kind;
  uint8_t other_kind;
  uint16_t bits;
  Handle children[4];
  Handle next;
};

/* @AUTOGEN-START@ */
enum class NFD_NODE_FIELD : uint8_t {
    invalid = 0,
    field = 1,  // slot: 2
    point = 2,  // slot: 1
    type = 3,  // slot: 1
    subtrahend = 4,  // slot: 0
    type_or_auto = 5,  // slot: 1
    result = 6,  // slot: 2
    size = 7,  // slot: 0
    expr_size = 8,  // slot: 1
    expr_index = 9,  // slot: 1
    expr = 10,  // slot: 0
    cond = 11,  // slot: 1
    expr_t = 12,  // slot: 0
    expr_f = 13,  // slot: 2
    expr1 = 14,  // slot: 0
    expr2 = 15,  // slot: 1
    expr_bound_or_undef = 16,  // slot: 2
    expr_rhs = 17,  // slot: 1
    expr_ret = 18,  // slot: 0
    pointer = 19,  // slot: 0
    container = 20,  // slot: 0
    callee = 21,  // slot: 0
    value_or_auto = 22,  // slot: 1
    value_or_undef = 23,  // slot: 0
    lhs = 24,  // slot: 0
    expr_lhs = 25,  // slot: 0
    initial_or_undef_or_auto = 26,  // slot: 2
    params = 27,  // slot: 1
    params_mod = 28,  // slot: 0
    params_macro = 29,  // slot: 1
    args = 30,  // slot: 1
    args_mod = 31,  // slot: 2
    items = 32,  // slot: 1
    fields = 33,  // slot: 1
    types = 34,  // slot: 0
    inits = 35,  // slot: 0
    gen_ids = 36,  // slot: 2
    body_mod = 37,  // slot: 1
    body = 38,  // slot: 3
    body_t = 39,  // slot: 0
    body_f = 40,  // slot: 2
    body_for = 41,  // slot: 2
    body_macro = 42,  // slot: 3
    cases = 43,  // slot: 0
};
enum class NFD_STRING_FIELD : uint8_t {
    invalid = 0,
    name = 1,  // slot: 0
    mod_name = 2,  // slot: 0
    base_name = 3,  // slot: 1
    enum_name = 4,  // slot: 2
    number = 5,  // slot: 0
    name_list = 6,  // slot: 1
    string = 7,  // slot: 0
    message = 8,  // slot: 0
    label = 9,  // slot: 0
    target = 10,  // slot: 0
    path = 11,  // slot: 1
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
    MacroVar = 47,
    ModParam = 48,
    RecField = 49,
    StmtAssignment = 50,
    StmtBlock = 51,
    StmtBreak = 52,
    StmtCompoundAssignment = 53,
    StmtCond = 54,
    StmtContinue = 55,
    StmtDefer = 56,
    StmtExpr = 57,
    StmtIf = 58,
    StmtReturn = 59,
    StmtStaticAssert = 60,
    StmtTrap = 61,
    TypeAuto = 62,
    TypeBase = 63,
    TypeFun = 64,
    TypeOf = 65,
    TypePtr = 66,
    TypeSpan = 67,
    TypeUnion = 68,
    TypeUnionDelta = 69,
    TypeVec = 70,
    ValAuto = 71,
    ValCompound = 72,
    ValFalse = 73,
    ValNum = 74,
    ValPoint = 75,
    ValSpan = 76,
    ValString = 77,
    ValTrue = 78,
    ValUndef = 79,
    ValVoid = 80,
};
// NFK.NAME
inline Name Node_name(NodeCore& n) { return Name(n.children[0]); }
inline Name Node_mod_name(NodeCore& n) { return Name(n.children[0]); }
inline Name Node_base_name(NodeCore& n) { return Name(n.children[1]); }
inline Name Node_enum_name(NodeCore& n) { return Name(n.children[2]); }
// NFK.STR
inline Str Node_number(NodeCore& n) { return Str(n.children[0]); }
inline Str Node_name_list(NodeCore& n) { return Str(n.children[1]); }
inline Str Node_string(NodeCore& n) { return Str(n.children[0]); }
inline Str Node_message(NodeCore& n) { return Str(n.children[0]); }
inline Str Node_label(NodeCore& n) { return Str(n.children[0]); }
inline Str Node_target(NodeCore& n) { return Str(n.children[0]); }
inline Str Node_path(NodeCore& n) { return Str(n.children[1]); }
// NFK.LIST
inline Node Node_params(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_params_mod(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_params_macro(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_args(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_args_mod(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_items(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_fields(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_types(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_inits(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_gen_ids(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_body_mod(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_body(NodeCore& n) { return Node(n.children[3]); }
inline Node Node_body_t(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_body_f(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_body_for(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_body_macro(NodeCore& n) { return Node(n.children[3]); }
inline Node Node_cases(NodeCore& n) { return Node(n.children[0]); }
// NFK.NODE
inline Node Node_field(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_point(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_type(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_subtrahend(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_type_or_auto(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_result(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_size(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_expr_size(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr_index(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_cond(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr_t(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_expr_f(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_expr1(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_expr2(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr_bound_or_undef(NodeCore& n) { return Node(n.children[2]); }
inline Node Node_expr_rhs(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr_ret(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_pointer(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_container(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_callee(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_value_or_auto(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_value_or_undef(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_lhs(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_expr_lhs(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_initial_or_undef_or_auto(NodeCore& n) { return Node(n.children[2]); }
inline void InitExprWiden(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprWiden;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeVec(NodeCore& node, Node size, Node type) {
   node.kind = NT::TypeVec;
   node.children[0] = size;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExpr1(NodeCore& node, UNARY_EXPR_KIND unary_expr_kind, Node expr) {
   node.kind = NT::Expr1;
   node.other_kind = unary_expr_kind;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitMacroInvoke(NodeCore& node, Name name, Node args) {
   node.kind = NT::MacroInvoke;
   node.children[0] = name;
   node.children[1] = args;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprCall(NodeCore& node, Node callee, Node args) {
   node.kind = NT::ExprCall;
   node.children[0] = callee;
   node.children[1] = args;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeSpan(NodeCore& node, Node type) {
   node.kind = NT::TypeSpan;
   node.children[0] = HandleInvalid;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprSrcLoc(NodeCore& node, Node expr) {
   node.kind = NT::ExprSrcLoc;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtReturn(NodeCore& node, Node expr_ret) {
   node.kind = NT::StmtReturn;
   node.children[0] = expr_ret;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValAuto(NodeCore& node) {
   node.kind = NT::ValAuto;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefGlobal(NodeCore& node, Name name, Node type_or_auto, Node initial_or_undef_or_auto) {
   node.kind = NT::DefGlobal;
   node.children[0] = name;
   node.children[1] = type_or_auto;
   node.children[2] = initial_or_undef_or_auto;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeOf(NodeCore& node, Node expr) {
   node.kind = NT::TypeOf;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExpr3(NodeCore& node, Node cond, Node expr_t, Node expr_f) {
   node.kind = NT::Expr3;
   node.children[0] = expr_t;
   node.children[1] = cond;
   node.children[2] = expr_f;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefEnum(NodeCore& node, Name name, BASE_TYPE_KIND base_type_kind, Node items) {
   node.kind = NT::DefEnum;
   node.other_kind = base_type_kind;
   node.children[0] = name;
   node.children[1] = items;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitMacroId(NodeCore& node, Name name) {
   node.kind = NT::MacroId;
   node.children[0] = name;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprUnwrap(NodeCore& node, Node expr) {
   node.kind = NT::ExprUnwrap;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtCond(NodeCore& node, Node cases) {
   node.kind = NT::StmtCond;
   node.children[0] = cases;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprStringify(NodeCore& node, Node expr) {
   node.kind = NT::ExprStringify;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefMod(NodeCore& node, Node params_mod, Node body_mod) {
   node.kind = NT::DefMod;
   node.children[0] = params_mod;
   node.children[1] = body_mod;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprUnionUntagged(NodeCore& node, Node expr) {
   node.kind = NT::ExprUnionUntagged;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtBlock(NodeCore& node, Str label, Node body) {
   node.kind = NT::StmtBlock;
   node.children[0] = label;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = body;
   node.next = HandleInvalid;
}

inline void InitExprPointer(NodeCore& node, POINTER_EXPR_KIND pointer_expr_kind, Node expr1, Node expr2, Node expr_bound_or_undef) {
   node.kind = NT::ExprPointer;
   node.other_kind = pointer_expr_kind;
   node.children[0] = expr1;
   node.children[1] = expr2;
   node.children[2] = expr_bound_or_undef;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefMacro(NodeCore& node, Name name, MACRO_PARAM_KIND macro_result_kind, Node params_macro, Node gen_ids, Node body_macro) {
   node.kind = NT::DefMacro;
   node.other_kind = macro_result_kind;
   node.children[0] = name;
   node.children[1] = params_macro;
   node.children[2] = gen_ids;
   node.children[3] = body_macro;
   node.next = HandleInvalid;
}

inline void InitValCompound(NodeCore& node, Node type_or_auto, Node inits) {
   node.kind = NT::ValCompound;
   node.children[0] = inits;
   node.children[1] = type_or_auto;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefRec(NodeCore& node, Name name, Node fields) {
   node.kind = NT::DefRec;
   node.children[0] = name;
   node.children[1] = fields;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprLen(NodeCore& node, Node container) {
   node.kind = NT::ExprLen;
   node.children[0] = container;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtTrap(NodeCore& node) {
   node.kind = NT::StmtTrap;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeUnion(NodeCore& node, Node types) {
   node.kind = NT::TypeUnion;
   node.children[0] = types;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitImport(NodeCore& node, Name name, Str path, Node args_mod) {
   node.kind = NT::Import;
   node.children[0] = name;
   node.children[1] = path;
   node.children[2] = args_mod;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprUnsafeCast(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprUnsafeCast;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValNum(NodeCore& node, Str number) {
   node.kind = NT::ValNum;
   node.children[0] = number;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprParen(NodeCore& node, Node expr) {
   node.kind = NT::ExprParen;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtExpr(NodeCore& node, Node expr) {
   node.kind = NT::StmtExpr;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtBreak(NodeCore& node, Str target) {
   node.kind = NT::StmtBreak;
   node.children[0] = target;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValFalse(NodeCore& node) {
   node.kind = NT::ValFalse;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefFun(NodeCore& node, Name name, Node params, Node result, Node body) {
   node.kind = NT::DefFun;
   node.children[0] = name;
   node.children[1] = params;
   node.children[2] = result;
   node.children[3] = body;
   node.next = HandleInvalid;
}

inline void InitExprIndex(NodeCore& node, Node container, Node expr_index) {
   node.kind = NT::ExprIndex;
   node.children[0] = container;
   node.children[1] = expr_index;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefType(NodeCore& node, Name name, Node type) {
   node.kind = NT::DefType;
   node.children[0] = name;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitEphemeralList(NodeCore& node, Node args) {
   node.kind = NT::EphemeralList;
   node.children[0] = HandleInvalid;
   node.children[1] = args;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtDefer(NodeCore& node, Node body) {
   node.kind = NT::StmtDefer;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = body;
   node.next = HandleInvalid;
}

inline void InitExprAs(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprAs;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprSizeof(NodeCore& node, Node type) {
   node.kind = NT::ExprSizeof;
   node.children[0] = HandleInvalid;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtCompoundAssignment(NodeCore& node, ASSIGNMENT_KIND assignment_kind, Node lhs, Node expr_rhs) {
   node.kind = NT::StmtCompoundAssignment;
   node.other_kind = assignment_kind;
   node.children[0] = lhs;
   node.children[1] = expr_rhs;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValString(NodeCore& node, Str string, STR_KIND str_kind) {
   node.kind = NT::ValString;
   node.other_kind = str_kind;
   node.children[0] = string;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitModParam(NodeCore& node, Name name, MOD_PARAM_KIND mod_param_kind) {
   node.kind = NT::ModParam;
   node.other_kind = mod_param_kind;
   node.children[0] = name;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitId(NodeCore& node, Name mod_name, Name base_name, Name enum_name) {
   node.kind = NT::Id;
   node.children[0] = mod_name;
   node.children[1] = base_name;
   node.children[2] = enum_name;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprFront(NodeCore& node, Node container) {
   node.kind = NT::ExprFront;
   node.children[0] = container;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtStaticAssert(NodeCore& node, Node cond, Str message) {
   node.kind = NT::StmtStaticAssert;
   node.children[0] = message;
   node.children[1] = cond;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeAuto(NodeCore& node) {
   node.kind = NT::TypeAuto;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprAddrOf(NodeCore& node, Node expr_lhs) {
   node.kind = NT::ExprAddrOf;
   node.children[0] = expr_lhs;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeBase(NodeCore& node, BASE_TYPE_KIND base_type_kind) {
   node.kind = NT::TypeBase;
   node.other_kind = base_type_kind;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExpr2(NodeCore& node, BINARY_EXPR_KIND binary_expr_kind, Node expr1, Node expr2) {
   node.kind = NT::Expr2;
   node.other_kind = binary_expr_kind;
   node.children[0] = expr1;
   node.children[1] = expr2;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValUndef(NodeCore& node) {
   node.kind = NT::ValUndef;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprField(NodeCore& node, Node container, Node field) {
   node.kind = NT::ExprField;
   node.children[0] = container;
   node.children[1] = HandleInvalid;
   node.children[2] = field;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprBitCast(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprBitCast;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprNarrow(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprNarrow;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValPoint(NodeCore& node, Node value_or_undef, Node point) {
   node.kind = NT::ValPoint;
   node.children[0] = value_or_undef;
   node.children[1] = point;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitFunParam(NodeCore& node, Name name, Node type) {
   node.kind = NT::FunParam;
   node.children[0] = name;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtIf(NodeCore& node, Node cond, Node body_t, Node body_f) {
   node.kind = NT::StmtIf;
   node.children[0] = body_t;
   node.children[1] = cond;
   node.children[2] = body_f;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitRecField(NodeCore& node, Name name, Node type) {
   node.kind = NT::RecField;
   node.children[0] = name;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeFun(NodeCore& node, Node params, Node result) {
   node.kind = NT::TypeFun;
   node.children[0] = HandleInvalid;
   node.children[1] = params;
   node.children[2] = result;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtContinue(NodeCore& node, Str target) {
   node.kind = NT::StmtContinue;
   node.children[0] = target;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypeUnionDelta(NodeCore& node, Node type, Node subtrahend) {
   node.kind = NT::TypeUnionDelta;
   node.children[0] = subtrahend;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValSpan(NodeCore& node, Node pointer, Node expr_size) {
   node.kind = NT::ValSpan;
   node.children[0] = pointer;
   node.children[1] = expr_size;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitMacroFor(NodeCore& node, Name name, Str name_list, Node body_for) {
   node.kind = NT::MacroFor;
   node.children[0] = name;
   node.children[1] = name_list;
   node.children[2] = body_for;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitEnumVal(NodeCore& node, Name name, Node value_or_auto) {
   node.kind = NT::EnumVal;
   node.children[0] = name;
   node.children[1] = value_or_auto;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprOffsetof(NodeCore& node, Node type, Node field) {
   node.kind = NT::ExprOffsetof;
   node.children[0] = HandleInvalid;
   node.children[1] = type;
   node.children[2] = field;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitStmtAssignment(NodeCore& node, Node lhs, Node expr_rhs) {
   node.kind = NT::StmtAssignment;
   node.children[0] = lhs;
   node.children[1] = expr_rhs;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitTypePtr(NodeCore& node, Node type) {
   node.kind = NT::TypePtr;
   node.children[0] = HandleInvalid;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprWrap(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprWrap;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValVoid(NodeCore& node) {
   node.kind = NT::ValVoid;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprDeref(NodeCore& node, Node expr) {
   node.kind = NT::ExprDeref;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprUnionTag(NodeCore& node, Node expr) {
   node.kind = NT::ExprUnionTag;
   node.children[0] = expr;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitDefVar(NodeCore& node, Name name, Node type_or_auto, Node initial_or_undef_or_auto) {
   node.kind = NT::DefVar;
   node.children[0] = name;
   node.children[1] = type_or_auto;
   node.children[2] = initial_or_undef_or_auto;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprIs(NodeCore& node, Node expr, Node type) {
   node.kind = NT::ExprIs;
   node.children[0] = expr;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitValTrue(NodeCore& node) {
   node.kind = NT::ValTrue;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitMacroVar(NodeCore& node, Name name, Node type_or_auto, Node initial_or_undef_or_auto) {
   node.kind = NT::MacroVar;
   node.children[0] = name;
   node.children[1] = type_or_auto;
   node.children[2] = initial_or_undef_or_auto;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitExprStmt(NodeCore& node, Node body) {
   node.kind = NT::ExprStmt;
   node.children[0] = HandleInvalid;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = body;
   node.next = HandleInvalid;
}

inline void InitExprTypeId(NodeCore& node, Node type) {
   node.kind = NT::ExprTypeId;
   node.children[0] = HandleInvalid;
   node.children[1] = type;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

inline void InitCase(NodeCore& node, Node cond, Node body) {
   node.kind = NT::Case;
   node.children[0] = HandleInvalid;
   node.children[1] = cond;
   node.children[2] = HandleInvalid;
   node.children[3] = body;
   node.next = HandleInvalid;
}

inline void InitMacroParam(NodeCore& node, Name name, MACRO_PARAM_KIND macro_param_kind) {
   node.kind = NT::MacroParam;
   node.other_kind = macro_param_kind;
   node.children[0] = name;
   node.children[1] = HandleInvalid;
   node.children[2] = HandleInvalid;
   node.children[3] = HandleInvalid;
   node.next = HandleInvalid;
}

/* @AUTOGEN-END@ */

struct NodeDesc {
  uint64_t node_field_bits;
  uint64_t string_field_bits;
};

extern NodeDesc GlobalNodeDescs[];



}  // namespace cwerg::fe
