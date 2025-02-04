#pragma once
// (c) Robert Muth - see LICENSE for more info

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
  explicit constexpr Name(uint32_t index = 0) : Handle(index, kKindName) {}

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

inline void InitNode(NodeCore& node, NT kind, Handle child0, Handle child1,
                     Handle child2, Handle child3, uint8_t other_kind) {
  node.kind = kind;
  node.other_kind = other_kind;
  node.children[0] = child0;
  node.children[1] = child1;
  node.children[2] = child2;
  node.children[3] = child3;
  node.next = HandleInvalid;
}

/* @AUTOGEN-START@ */
enum class NFD_NODE_FIELD : uint8_t {
  invalid = 0,
  field = 1,                      // slot: 2
  point = 2,                      // slot: 1
  type = 3,                       // slot: 1
  subtrahend = 4,                 // slot: 0
  type_or_auto = 5,               // slot: 1
  result = 6,                     // slot: 2
  size = 7,                       // slot: 0
  expr_size = 8,                  // slot: 1
  expr_index = 9,                 // slot: 1
  expr = 10,                      // slot: 0
  cond = 11,                      // slot: 1
  expr_t = 12,                    // slot: 0
  expr_f = 13,                    // slot: 2
  expr1 = 14,                     // slot: 0
  expr2 = 15,                     // slot: 1
  expr_bound_or_undef = 16,       // slot: 2
  expr_rhs = 17,                  // slot: 1
  expr_ret = 18,                  // slot: 0
  pointer = 19,                   // slot: 0
  container = 20,                 // slot: 0
  callee = 21,                    // slot: 0
  value_or_auto = 22,             // slot: 1
  value_or_undef = 23,            // slot: 0
  lhs = 24,                       // slot: 0
  expr_lhs = 25,                  // slot: 0
  initial_or_undef_or_auto = 26,  // slot: 2
  params = 27,                    // slot: 1
  params_mod = 28,                // slot: 0
  params_macro = 29,              // slot: 1
  args = 30,                      // slot: 1
  args_mod = 31,                  // slot: 2
  items = 32,                     // slot: 1
  fields = 33,                    // slot: 1
  types = 34,                     // slot: 0
  inits = 35,                     // slot: 0
  gen_ids = 36,                   // slot: 2
  body_mod = 37,                  // slot: 1
  body = 38,                      // slot: 3
  body_t = 39,                    // slot: 0
  body_f = 40,                    // slot: 2
  body_for = 41,                  // slot: 2
  body_macro = 42,                // slot: 3
  cases = 43,                     // slot: 0
};
enum class NFD_STRING_FIELD : uint8_t {
  invalid = 0,
  name = 1,       // slot: 0
  mod_name = 2,   // slot: 0
  base_name = 3,  // slot: 1
  enum_name = 4,  // slot: 2
  number = 5,     // slot: 0
  name_list = 6,  // slot: 1
  string = 7,     // slot: 0
  message = 8,    // slot: 0
  label = 9,      // slot: 0
  target = 10,    // slot: 0
  path = 11,      // slot: 1
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
inline Node Node_expr_bound_or_undef(NodeCore& n) {
  return Node(n.children[2]);
}
inline Node Node_expr_rhs(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_expr_ret(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_pointer(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_container(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_callee(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_value_or_auto(NodeCore& n) { return Node(n.children[1]); }
inline Node Node_value_or_undef(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_lhs(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_expr_lhs(NodeCore& n) { return Node(n.children[0]); }
inline Node Node_initial_or_undef_or_auto(NodeCore& n) {
  return Node(n.children[2]);
}
inline void InitCase(NodeCore& node, Node cond, Node body) {
  InitNode(node, NT::Case, HandleInvalid, cond, HandleInvalid, body, 0);
}

inline void InitDefEnum(NodeCore& node, Name name,
                        BASE_TYPE_KIND base_type_kind, Node items) {
  InitNode(node, NT::DefEnum, name, items, HandleInvalid, HandleInvalid,
           uint8_t(base_type_kind));
}

inline void InitDefFun(NodeCore& node, Name name, Node params, Node result,
                       Node body) {
  InitNode(node, NT::DefFun, name, params, result, body, 0);
}

inline void InitDefGlobal(NodeCore& node, Name name, Node type_or_auto,
                          Node initial_or_undef_or_auto) {
  InitNode(node, NT::DefGlobal, name, type_or_auto, initial_or_undef_or_auto,
           HandleInvalid, 0);
}

inline void InitDefMacro(NodeCore& node, Name name,
                         MACRO_PARAM_KIND macro_result_kind, Node params_macro,
                         Node gen_ids, Node body_macro) {
  InitNode(node, NT::DefMacro, name, params_macro, gen_ids, body_macro,
           uint8_t(macro_result_kind));
}

inline void InitDefMod(NodeCore& node, Node params_mod, Node body_mod) {
  InitNode(node, NT::DefMod, params_mod, body_mod, HandleInvalid, HandleInvalid,
           0);
}

inline void InitDefRec(NodeCore& node, Name name, Node fields) {
  InitNode(node, NT::DefRec, name, fields, HandleInvalid, HandleInvalid, 0);
}

inline void InitDefType(NodeCore& node, Name name, Node type) {
  InitNode(node, NT::DefType, name, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitDefVar(NodeCore& node, Name name, Node type_or_auto,
                       Node initial_or_undef_or_auto) {
  InitNode(node, NT::DefVar, name, type_or_auto, initial_or_undef_or_auto,
           HandleInvalid, 0);
}

inline void InitEnumVal(NodeCore& node, Name name, Node value_or_auto) {
  InitNode(node, NT::EnumVal, name, value_or_auto, HandleInvalid, HandleInvalid,
           0);
}

inline void InitEphemeralList(NodeCore& node, Node args) {
  InitNode(node, NT::EphemeralList, HandleInvalid, args, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExpr1(NodeCore& node, UNARY_EXPR_KIND unary_expr_kind,
                      Node expr) {
  InitNode(node, NT::Expr1, expr, HandleInvalid, HandleInvalid, HandleInvalid,
           uint8_t(unary_expr_kind));
}

inline void InitExpr2(NodeCore& node, BINARY_EXPR_KIND binary_expr_kind,
                      Node expr1, Node expr2) {
  InitNode(node, NT::Expr2, expr1, expr2, HandleInvalid, HandleInvalid,
           uint8_t(binary_expr_kind));
}

inline void InitExpr3(NodeCore& node, Node cond, Node expr_t, Node expr_f) {
  InitNode(node, NT::Expr3, expr_t, cond, expr_f, HandleInvalid, 0);
}

inline void InitExprAddrOf(NodeCore& node, Node expr_lhs) {
  InitNode(node, NT::ExprAddrOf, expr_lhs, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprAs(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprAs, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprBitCast(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprBitCast, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprCall(NodeCore& node, Node callee, Node args) {
  InitNode(node, NT::ExprCall, callee, args, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprDeref(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprDeref, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprField(NodeCore& node, Node container, Node field) {
  InitNode(node, NT::ExprField, container, HandleInvalid, field, HandleInvalid,
           0);
}

inline void InitExprFront(NodeCore& node, Node container) {
  InitNode(node, NT::ExprFront, container, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprIndex(NodeCore& node, Node container, Node expr_index) {
  InitNode(node, NT::ExprIndex, container, expr_index, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprIs(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprIs, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprLen(NodeCore& node, Node container) {
  InitNode(node, NT::ExprLen, container, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprNarrow(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprNarrow, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprOffsetof(NodeCore& node, Node type, Node field) {
  InitNode(node, NT::ExprOffsetof, HandleInvalid, type, field, HandleInvalid,
           0);
}

inline void InitExprParen(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprParen, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprPointer(NodeCore& node, POINTER_EXPR_KIND pointer_expr_kind,
                            Node expr1, Node expr2, Node expr_bound_or_undef) {
  InitNode(node, NT::ExprPointer, expr1, expr2, expr_bound_or_undef,
           HandleInvalid, uint8_t(pointer_expr_kind));
}

inline void InitExprSizeof(NodeCore& node, Node type) {
  InitNode(node, NT::ExprSizeof, HandleInvalid, type, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprSrcLoc(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprSrcLoc, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprStmt(NodeCore& node, Node body) {
  InitNode(node, NT::ExprStmt, HandleInvalid, HandleInvalid, HandleInvalid,
           body, 0);
}

inline void InitExprStringify(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprStringify, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprTypeId(NodeCore& node, Node type) {
  InitNode(node, NT::ExprTypeId, HandleInvalid, type, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprUnionTag(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprUnionTag, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprUnionUntagged(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprUnionUntagged, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprUnsafeCast(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprUnsafeCast, expr, type, HandleInvalid, HandleInvalid,
           0);
}

inline void InitExprUnwrap(NodeCore& node, Node expr) {
  InitNode(node, NT::ExprUnwrap, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitExprWiden(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprWiden, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitExprWrap(NodeCore& node, Node expr, Node type) {
  InitNode(node, NT::ExprWrap, expr, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitFunParam(NodeCore& node, Name name, Node type) {
  InitNode(node, NT::FunParam, name, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitId(NodeCore& node, Name mod_name, Name base_name,
                   Name enum_name) {
  InitNode(node, NT::Id, mod_name, base_name, enum_name, HandleInvalid, 0);
}

inline void InitImport(NodeCore& node, Name name, Str path, Node args_mod) {
  InitNode(node, NT::Import, name, path, args_mod, HandleInvalid, 0);
}

inline void InitMacroFor(NodeCore& node, Name name, Str name_list,
                         Node body_for) {
  InitNode(node, NT::MacroFor, name, name_list, body_for, HandleInvalid, 0);
}

inline void InitMacroId(NodeCore& node, Name name) {
  InitNode(node, NT::MacroId, name, HandleInvalid, HandleInvalid, HandleInvalid,
           0);
}

inline void InitMacroInvoke(NodeCore& node, Name name, Node args) {
  InitNode(node, NT::MacroInvoke, name, args, HandleInvalid, HandleInvalid, 0);
}

inline void InitMacroParam(NodeCore& node, Name name,
                           MACRO_PARAM_KIND macro_param_kind) {
  InitNode(node, NT::MacroParam, name, HandleInvalid, HandleInvalid,
           HandleInvalid, uint8_t(macro_param_kind));
}

inline void InitMacroVar(NodeCore& node, Name name, Node type_or_auto,
                         Node initial_or_undef_or_auto) {
  InitNode(node, NT::MacroVar, name, type_or_auto, initial_or_undef_or_auto,
           HandleInvalid, 0);
}

inline void InitModParam(NodeCore& node, Name name,
                         MOD_PARAM_KIND mod_param_kind) {
  InitNode(node, NT::ModParam, name, HandleInvalid, HandleInvalid,
           HandleInvalid, uint8_t(mod_param_kind));
}

inline void InitRecField(NodeCore& node, Name name, Node type) {
  InitNode(node, NT::RecField, name, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitStmtAssignment(NodeCore& node, Node lhs, Node expr_rhs) {
  InitNode(node, NT::StmtAssignment, lhs, expr_rhs, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtBlock(NodeCore& node, Str label, Node body) {
  InitNode(node, NT::StmtBlock, label, HandleInvalid, HandleInvalid, body, 0);
}

inline void InitStmtBreak(NodeCore& node, Str target) {
  InitNode(node, NT::StmtBreak, target, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtCompoundAssignment(NodeCore& node,
                                       ASSIGNMENT_KIND assignment_kind,
                                       Node lhs, Node expr_rhs) {
  InitNode(node, NT::StmtCompoundAssignment, lhs, expr_rhs, HandleInvalid,
           HandleInvalid, uint8_t(assignment_kind));
}

inline void InitStmtCond(NodeCore& node, Node cases) {
  InitNode(node, NT::StmtCond, cases, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtContinue(NodeCore& node, Str target) {
  InitNode(node, NT::StmtContinue, target, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtDefer(NodeCore& node, Node body) {
  InitNode(node, NT::StmtDefer, HandleInvalid, HandleInvalid, HandleInvalid,
           body, 0);
}

inline void InitStmtExpr(NodeCore& node, Node expr) {
  InitNode(node, NT::StmtExpr, expr, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtIf(NodeCore& node, Node cond, Node body_t, Node body_f) {
  InitNode(node, NT::StmtIf, body_t, cond, body_f, HandleInvalid, 0);
}

inline void InitStmtReturn(NodeCore& node, Node expr_ret) {
  InitNode(node, NT::StmtReturn, expr_ret, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtStaticAssert(NodeCore& node, Node cond, Str message) {
  InitNode(node, NT::StmtStaticAssert, message, cond, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitStmtTrap(NodeCore& node) {
  InitNode(node, NT::StmtTrap, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitTypeAuto(NodeCore& node) {
  InitNode(node, NT::TypeAuto, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitTypeBase(NodeCore& node, BASE_TYPE_KIND base_type_kind) {
  InitNode(node, NT::TypeBase, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, uint8_t(base_type_kind));
}

inline void InitTypeFun(NodeCore& node, Node params, Node result) {
  InitNode(node, NT::TypeFun, HandleInvalid, params, result, HandleInvalid, 0);
}

inline void InitTypeOf(NodeCore& node, Node expr) {
  InitNode(node, NT::TypeOf, expr, HandleInvalid, HandleInvalid, HandleInvalid,
           0);
}

inline void InitTypePtr(NodeCore& node, Node type) {
  InitNode(node, NT::TypePtr, HandleInvalid, type, HandleInvalid, HandleInvalid,
           0);
}

inline void InitTypeSpan(NodeCore& node, Node type) {
  InitNode(node, NT::TypeSpan, HandleInvalid, type, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitTypeUnion(NodeCore& node, Node types) {
  InitNode(node, NT::TypeUnion, types, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitTypeUnionDelta(NodeCore& node, Node type, Node subtrahend) {
  InitNode(node, NT::TypeUnionDelta, subtrahend, type, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitTypeVec(NodeCore& node, Node size, Node type) {
  InitNode(node, NT::TypeVec, size, type, HandleInvalid, HandleInvalid, 0);
}

inline void InitValAuto(NodeCore& node) {
  InitNode(node, NT::ValAuto, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValCompound(NodeCore& node, Node type_or_auto, Node inits) {
  InitNode(node, NT::ValCompound, inits, type_or_auto, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValFalse(NodeCore& node) {
  InitNode(node, NT::ValFalse, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValNum(NodeCore& node, Str number) {
  InitNode(node, NT::ValNum, number, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValPoint(NodeCore& node, Node value_or_undef, Node point) {
  InitNode(node, NT::ValPoint, value_or_undef, point, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValSpan(NodeCore& node, Node pointer, Node expr_size) {
  InitNode(node, NT::ValSpan, pointer, expr_size, HandleInvalid, HandleInvalid,
           0);
}

inline void InitValString(NodeCore& node, Str string, STR_KIND str_kind) {
  InitNode(node, NT::ValString, string, HandleInvalid, HandleInvalid,
           HandleInvalid, uint8_t(str_kind));
}

inline void InitValTrue(NodeCore& node) {
  InitNode(node, NT::ValTrue, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValUndef(NodeCore& node) {
  InitNode(node, NT::ValUndef, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

inline void InitValVoid(NodeCore& node) {
  InitNode(node, NT::ValVoid, HandleInvalid, HandleInvalid, HandleInvalid,
           HandleInvalid, 0);
}

/* @AUTOGEN-END@ */

struct NodeDesc {
  uint64_t node_field_bits;
  uint64_t string_field_bits;
};

// For each NT described which fields (regular / bool) are present
// We have aboutr 45 regular and very few bool fields. So there is headroom in
// the biy vec
extern NodeDesc GlobalNodeDescs[];

}  // namespace cwerg::fe
