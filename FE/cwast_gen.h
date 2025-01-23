#include <cstdint>
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
    TypeUnionDelta = 1,
    RecField = 2,
    ValSpan = 3,
    StmtBreak = 4,
    DefGlobal = 5,
    ExprStmt = 6,
    MacroFor = 7,
    ValVoid = 8,
    FunParam = 9,
    DefFun = 10,
    Id = 11,
    ExprNarrow = 12,
    TypeOf = 13,
    ExprPointer = 14,
    StmtReturn = 15,
    DefEnum = 16,
    ValNum = 17,
    StmtDefer = 18,
    TypePtr = 19,
    ExprParen = 20,
    ExprUnionTag = 21,
    StmtExpr = 22,
    ExprLen = 23,
    ExprUnionUntagged = 24,
    MacroInvoke = 25,
    TypeFun = 26,
    ExprWrap = 27,
    ExprBitCast = 28,
    TypeBase = 29,
    ExprStringify = 30,
    ValAuto = 31,
    ValString = 32,
    StmtContinue = 33,
    Expr2 = 34,
    StmtIf = 35,
    StmtBlock = 36,
    ExprWiden = 37,
    DefType = 38,
    DefMacro = 39,
    DefMod = 40,
    TypeUnion = 41,
    StmtStaticAssert = 42,
    ValPoint = 43,
    TypeSpan = 44,
    ExprField = 45,
    ExprSizeof = 46,
    ValTrue = 47,
    ExprDeref = 48,
    StmtCompoundAssignment = 49,
    Expr3 = 50,
    Import = 51,
    ExprUnwrap = 52,
    Case = 53,
    TypeAuto = 54,
    ExprFront = 55,
    DefVar = 56,
    MacroParam = 57,
    StmtTrap = 58,
    ValCompound = 59,
    EphemeralList = 60,
    ExprUnsafeCast = 61,
    ExprOffsetof = 62,
    StmtAssignment = 63,
    DefRec = 64,
    Expr1 = 65,
    StmtCond = 66,
    ModParam = 67,
    MacroId = 68,
    ValUndef = 69,
    ExprAddrOf = 70,
    ExprCall = 71,
    ExprIndex = 72,
    ExprAs = 73,
    TypeVec = 74,
    ExprTypeId = 75,
    EnumVal = 76,
    ExprSrcLoc = 77,
    ValFalse = 78,
    MacroVar = 79,
    ExprIs = 80,
};
struct NodeDesc{
    uint64_t node_field_bits;
    uint64_t string_field_bits;
 }
extern NodeDesc GlobalNodeDescs[];
struct Node {
    NT kind kind;
    uint8_t other_kind;
    uint16_t bits;
    Handle children[4];
    NodeHandle next;
}
// NFK.NAME
inline NameHandle& Node_name(Node& n) { return n.children[0]; }
inline NameHandle& Node_mod_name(Node& n) { return n.children[0]; }
inline NameHandle& Node_base_name(Node& n) { return n.children[1]; }
inline NameHandle& Node_enum_name(Node& n) { return n.children[2]; }
// NFK.STR
inline StrHandle& Node_number(Node& n) { return n.children[0]; }
inline StrHandle& Node_name_list(Node& n) { return n.children[1]; }
inline StrHandle& Node_string(Node& n) { return n.children[0]; }
inline StrHandle& Node_message(Node& n) { return n.children[0]; }
inline StrHandle& Node_label(Node& n) { return n.children[0]; }
inline StrHandle& Node_target(Node& n) { return n.children[0]; }
inline StrHandle& Node_path(Node& n) { return n.children[1]; }
// NFK.LIST
inline NodeHandle& Node_params(Node& n) { return n.children[1]; }
inline NodeHandle& Node_params_mod(Node& n) { return n.children[0]; }
inline NodeHandle& Node_params_macro(Node& n) { return n.children[1]; }
inline NodeHandle& Node_args(Node& n) { return n.children[1]; }
inline NodeHandle& Node_args_mod(Node& n) { return n.children[2]; }
inline NodeHandle& Node_items(Node& n) { return n.children[1]; }
inline NodeHandle& Node_fields(Node& n) { return n.children[1]; }
inline NodeHandle& Node_types(Node& n) { return n.children[0]; }
inline NodeHandle& Node_inits(Node& n) { return n.children[0]; }
inline NodeHandle& Node_gen_ids(Node& n) { return n.children[2]; }
inline NodeHandle& Node_body_mod(Node& n) { return n.children[1]; }
inline NodeHandle& Node_body(Node& n) { return n.children[3]; }
inline NodeHandle& Node_body_t(Node& n) { return n.children[0]; }
inline NodeHandle& Node_body_f(Node& n) { return n.children[2]; }
inline NodeHandle& Node_body_for(Node& n) { return n.children[2]; }
inline NodeHandle& Node_body_macro(Node& n) { return n.children[3]; }
inline NodeHandle& Node_cases(Node& n) { return n.children[0]; }
// NFK.NODE
inline NodeHandle& Node_field(Node& n) { return n.children[2]; }
inline NodeHandle& Node_point(Node& n) { return n.children[1]; }
inline NodeHandle& Node_type(Node& n) { return n.children[1]; }
inline NodeHandle& Node_subtrahend(Node& n) { return n.children[0]; }
inline NodeHandle& Node_type_or_auto(Node& n) { return n.children[1]; }
inline NodeHandle& Node_result(Node& n) { return n.children[2]; }
inline NodeHandle& Node_size(Node& n) { return n.children[0]; }
inline NodeHandle& Node_expr_size(Node& n) { return n.children[1]; }
inline NodeHandle& Node_expr_index(Node& n) { return n.children[1]; }
inline NodeHandle& Node_expr(Node& n) { return n.children[0]; }
inline NodeHandle& Node_cond(Node& n) { return n.children[1]; }
inline NodeHandle& Node_expr_t(Node& n) { return n.children[0]; }
inline NodeHandle& Node_expr_f(Node& n) { return n.children[2]; }
inline NodeHandle& Node_expr1(Node& n) { return n.children[0]; }
inline NodeHandle& Node_expr2(Node& n) { return n.children[1]; }
inline NodeHandle& Node_expr_bound_or_undef(Node& n) { return n.children[2]; }
inline NodeHandle& Node_expr_rhs(Node& n) { return n.children[1]; }
inline NodeHandle& Node_expr_ret(Node& n) { return n.children[0]; }
inline NodeHandle& Node_pointer(Node& n) { return n.children[0]; }
inline NodeHandle& Node_container(Node& n) { return n.children[0]; }
inline NodeHandle& Node_callee(Node& n) { return n.children[0]; }
inline NodeHandle& Node_value_or_auto(Node& n) { return n.children[1]; }
inline NodeHandle& Node_value_or_undef(Node& n) { return n.children[0]; }
inline NodeHandle& Node_lhs(Node& n) { return n.children[0]; }
inline NodeHandle& Node_expr_lhs(Node& n) { return n.children[0]; }
inline NodeHandle& Node_initial_or_undef_or_auto(Node& n) { return n.children[2]; }
inline void InitTypeUnionDelta(Node& node, NodeHandle type, NodeHandle subtrahend) {
   node.kind = NT::TypeUnionDelta;
   node.children = {subtrahend, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitRecField(Node& node, NameHandle name, NodeHandle type) {
   node.kind = NT::RecField;
   node.children = {name, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValSpan(Node& node, NodeHandle pointer, NodeHandle expr_size) {
   node.kind = NT::ValSpan;
   node.children = {pointer, expr_size, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtBreak(Node& node, StrHandle target) {
   node.kind = NT::StmtBreak;
   node.children = {target, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefGlobal(Node& node, NameHandle name, NodeHandle type_or_auto, NodeHandle initial_or_undef_or_auto) {
   node.kind = NT::DefGlobal;
   node.children = {name, type_or_auto, initial_or_undef_or_auto, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprStmt(Node& node, NodeHandle body) {
   node.kind = NT::ExprStmt;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, body};
   node.next = INVALID_HANDLE;
}

inline void InitMacroFor(Node& node, NameHandle name, StrHandle name_list, NodeHandle body_for) {
   node.kind = NT::MacroFor;
   node.children = {name, name_list, body_for, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValVoid(Node& node) {
   node.kind = NT::ValVoid;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitFunParam(Node& node, NameHandle name, NodeHandle type) {
   node.kind = NT::FunParam;
   node.children = {name, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefFun(Node& node, NameHandle name, NodeHandle params, NodeHandle result, NodeHandle body) {
   node.kind = NT::DefFun;
   node.children = {name, params, result, body};
   node.next = INVALID_HANDLE;
}

inline void InitId(Node& node, NameHandle mod_name, NameHandle base_name, NameHandle enum_name) {
   node.kind = NT::Id;
   node.children = {mod_name, base_name, enum_name, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprNarrow(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprNarrow;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeOf(Node& node, NodeHandle expr) {
   node.kind = NT::TypeOf;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprPointer(Node& node, POINTER_EXPR_KIND pointer_expr_kind, NodeHandle expr1, NodeHandle expr2, NodeHandle expr_bound_or_undef) {
   node.kind = NT::ExprPointer;
   node.other_kind = pointer_expr_kind;
   node.children = {expr1, expr2, expr_bound_or_undef, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtReturn(Node& node, NodeHandle expr_ret) {
   node.kind = NT::StmtReturn;
   node.children = {expr_ret, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefEnum(Node& node, NameHandle name, BASE_TYPE_KIND base_type_kind, NodeHandle items) {
   node.kind = NT::DefEnum;
   node.other_kind = base_type_kind;
   node.children = {name, items, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValNum(Node& node, StrHandle number) {
   node.kind = NT::ValNum;
   node.children = {number, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtDefer(Node& node, NodeHandle body) {
   node.kind = NT::StmtDefer;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, body};
   node.next = INVALID_HANDLE;
}

inline void InitTypePtr(Node& node, NodeHandle type) {
   node.kind = NT::TypePtr;
   node.children = {INVALID_HANDLE, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprParen(Node& node, NodeHandle expr) {
   node.kind = NT::ExprParen;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprUnionTag(Node& node, NodeHandle expr) {
   node.kind = NT::ExprUnionTag;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtExpr(Node& node, NodeHandle expr) {
   node.kind = NT::StmtExpr;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprLen(Node& node, NodeHandle container) {
   node.kind = NT::ExprLen;
   node.children = {container, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprUnionUntagged(Node& node, NodeHandle expr) {
   node.kind = NT::ExprUnionUntagged;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitMacroInvoke(Node& node, NameHandle name, NodeHandle args) {
   node.kind = NT::MacroInvoke;
   node.children = {name, args, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeFun(Node& node, NodeHandle params, NodeHandle result) {
   node.kind = NT::TypeFun;
   node.children = {INVALID_HANDLE, params, result, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprWrap(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprWrap;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprBitCast(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprBitCast;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeBase(Node& node, BASE_TYPE_KIND base_type_kind) {
   node.kind = NT::TypeBase;
   node.other_kind = base_type_kind;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprStringify(Node& node, NodeHandle expr) {
   node.kind = NT::ExprStringify;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValAuto(Node& node) {
   node.kind = NT::ValAuto;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValString(Node& node, StrHandle string, STR_KIND str_kind) {
   node.kind = NT::ValString;
   node.other_kind = str_kind;
   node.children = {string, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtContinue(Node& node, StrHandle target) {
   node.kind = NT::StmtContinue;
   node.children = {target, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExpr2(Node& node, BINARY_EXPR_KIND binary_expr_kind, NodeHandle expr1, NodeHandle expr2) {
   node.kind = NT::Expr2;
   node.other_kind = binary_expr_kind;
   node.children = {expr1, expr2, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtIf(Node& node, NodeHandle cond, NodeHandle body_t, NodeHandle body_f) {
   node.kind = NT::StmtIf;
   node.children = {body_t, cond, body_f, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtBlock(Node& node, StrHandle label, NodeHandle body) {
   node.kind = NT::StmtBlock;
   node.children = {label, INVALID_HANDLE, INVALID_HANDLE, body};
   node.next = INVALID_HANDLE;
}

inline void InitExprWiden(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprWiden;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefType(Node& node, NameHandle name, NodeHandle type) {
   node.kind = NT::DefType;
   node.children = {name, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefMacro(Node& node, NameHandle name, MACRO_PARAM_KIND macro_result_kind, NodeHandle params_macro, NodeHandle gen_ids, NodeHandle body_macro) {
   node.kind = NT::DefMacro;
   node.other_kind = macro_result_kind;
   node.children = {name, params_macro, gen_ids, body_macro};
   node.next = INVALID_HANDLE;
}

inline void InitDefMod(Node& node, NodeHandle params_mod, NodeHandle body_mod) {
   node.kind = NT::DefMod;
   node.children = {params_mod, body_mod, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeUnion(Node& node, NodeHandle types) {
   node.kind = NT::TypeUnion;
   node.children = {types, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtStaticAssert(Node& node, NodeHandle cond, StrHandle message) {
   node.kind = NT::StmtStaticAssert;
   node.children = {message, cond, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValPoint(Node& node, NodeHandle value_or_undef, NodeHandle point) {
   node.kind = NT::ValPoint;
   node.children = {value_or_undef, point, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeSpan(Node& node, NodeHandle type) {
   node.kind = NT::TypeSpan;
   node.children = {INVALID_HANDLE, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprField(Node& node, NodeHandle container, NodeHandle field) {
   node.kind = NT::ExprField;
   node.children = {container, INVALID_HANDLE, field, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprSizeof(Node& node, NodeHandle type) {
   node.kind = NT::ExprSizeof;
   node.children = {INVALID_HANDLE, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValTrue(Node& node) {
   node.kind = NT::ValTrue;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprDeref(Node& node, NodeHandle expr) {
   node.kind = NT::ExprDeref;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtCompoundAssignment(Node& node, ASSIGNMENT_KIND assignment_kind, NodeHandle lhs, NodeHandle expr_rhs) {
   node.kind = NT::StmtCompoundAssignment;
   node.other_kind = assignment_kind;
   node.children = {lhs, expr_rhs, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExpr3(Node& node, NodeHandle cond, NodeHandle expr_t, NodeHandle expr_f) {
   node.kind = NT::Expr3;
   node.children = {expr_t, cond, expr_f, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitImport(Node& node, NameHandle name, StrHandle path, NodeHandle args_mod) {
   node.kind = NT::Import;
   node.children = {name, path, args_mod, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprUnwrap(Node& node, NodeHandle expr) {
   node.kind = NT::ExprUnwrap;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitCase(Node& node, NodeHandle cond, NodeHandle body) {
   node.kind = NT::Case;
   node.children = {INVALID_HANDLE, cond, INVALID_HANDLE, body};
   node.next = INVALID_HANDLE;
}

inline void InitTypeAuto(Node& node) {
   node.kind = NT::TypeAuto;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprFront(Node& node, NodeHandle container) {
   node.kind = NT::ExprFront;
   node.children = {container, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefVar(Node& node, NameHandle name, NodeHandle type_or_auto, NodeHandle initial_or_undef_or_auto) {
   node.kind = NT::DefVar;
   node.children = {name, type_or_auto, initial_or_undef_or_auto, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitMacroParam(Node& node, NameHandle name, MACRO_PARAM_KIND macro_param_kind) {
   node.kind = NT::MacroParam;
   node.other_kind = macro_param_kind;
   node.children = {name, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtTrap(Node& node) {
   node.kind = NT::StmtTrap;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValCompound(Node& node, NodeHandle type_or_auto, NodeHandle inits) {
   node.kind = NT::ValCompound;
   node.children = {inits, type_or_auto, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitEphemeralList(Node& node, NodeHandle args) {
   node.kind = NT::EphemeralList;
   node.children = {INVALID_HANDLE, args, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprUnsafeCast(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprUnsafeCast;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprOffsetof(Node& node, NodeHandle type, NodeHandle field) {
   node.kind = NT::ExprOffsetof;
   node.children = {INVALID_HANDLE, type, field, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtAssignment(Node& node, NodeHandle lhs, NodeHandle expr_rhs) {
   node.kind = NT::StmtAssignment;
   node.children = {lhs, expr_rhs, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitDefRec(Node& node, NameHandle name, NodeHandle fields) {
   node.kind = NT::DefRec;
   node.children = {name, fields, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExpr1(Node& node, UNARY_EXPR_KIND unary_expr_kind, NodeHandle expr) {
   node.kind = NT::Expr1;
   node.other_kind = unary_expr_kind;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitStmtCond(Node& node, NodeHandle cases) {
   node.kind = NT::StmtCond;
   node.children = {cases, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitModParam(Node& node, NameHandle name, MOD_PARAM_KIND mod_param_kind) {
   node.kind = NT::ModParam;
   node.other_kind = mod_param_kind;
   node.children = {name, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitMacroId(Node& node, NameHandle name) {
   node.kind = NT::MacroId;
   node.children = {name, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValUndef(Node& node) {
   node.kind = NT::ValUndef;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprAddrOf(Node& node, NodeHandle expr_lhs) {
   node.kind = NT::ExprAddrOf;
   node.children = {expr_lhs, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprCall(Node& node, NodeHandle callee, NodeHandle args) {
   node.kind = NT::ExprCall;
   node.children = {callee, args, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprIndex(Node& node, NodeHandle container, NodeHandle expr_index) {
   node.kind = NT::ExprIndex;
   node.children = {container, expr_index, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprAs(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprAs;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitTypeVec(Node& node, NodeHandle size, NodeHandle type) {
   node.kind = NT::TypeVec;
   node.children = {size, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprTypeId(Node& node, NodeHandle type) {
   node.kind = NT::ExprTypeId;
   node.children = {INVALID_HANDLE, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitEnumVal(Node& node, NameHandle name, NodeHandle value_or_auto) {
   node.kind = NT::EnumVal;
   node.children = {name, value_or_auto, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprSrcLoc(Node& node, NodeHandle expr) {
   node.kind = NT::ExprSrcLoc;
   node.children = {expr, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitValFalse(Node& node) {
   node.kind = NT::ValFalse;
   node.children = {INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitMacroVar(Node& node, NameHandle name, NodeHandle type_or_auto, NodeHandle initial_or_undef_or_auto) {
   node.kind = NT::MacroVar;
   node.children = {name, type_or_auto, initial_or_undef_or_auto, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

inline void InitExprIs(Node& node, NodeHandle expr, NodeHandle type) {
   node.kind = NT::ExprIs;
   node.children = {expr, type, INVALID_HANDLE, INVALID_HANDLE};
   node.next = INVALID_HANDLE;
}

