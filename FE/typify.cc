#include "FE/typify.h"

#include <array>
#include <cstdint>
#include <map>

#include "FE/symbolize.h"
#include "Util/assert.h"
#include "Util/parse.h"
#include "Util/switch.h"

namespace cwerg::fe {
namespace {

SwitchBool sw_verbose("verbose_typify", "make typify more verbose");

struct PolyMapKey {
  Node mod;
  Name fun_name;
  CanonType first_param_type;

  bool operator<(const PolyMapKey& other) const {
    if (mod != other.mod) {
      return mod < other.mod;
    }
    if (fun_name != other.fun_name) {
      return fun_name < other.fun_name;
    }
    return first_param_type < other.first_param_type;
  }
};

std::ostream& operator<<(std::ostream& os, const PolyMapKey& k) {
  os << Node_name(k.mod) << " " << k.fun_name << " "
     << CanonType_name(k.first_param_type);
  return os;
}

class PolyMap {
  TypeCorpus* tc_;
  std::map<PolyMapKey, Node> map_;

 public:
  PolyMap(TypeCorpus* tc) : tc_(tc) {}

  void Register(Node fun) {
    ASSERT(Node_has_flag(fun, BF::POLY), "");
    CanonType ct = Node_x_type(fun);
    ASSERT(Node_kind(fun) == NT::DefFun, "");
    ASSERT(Node_has_flag(fun, BF::POLY), "");
    ASSERT(CanonType_children(ct).size() >= 2, "");
    CanonType ct_first = CanonType_children(ct)[0];
    PolyMapKey key{Node_x_poly_mod(fun), Node_name(fun), ct_first};
    if (map_.find(key) != map_.end()) {
      CompilerError(Node_srcloc(fun))
          << "Duplicate poly fun for " << CanonType_name(ct_first);
    }
    map_[key] = fun;
  }

  Node Resolve(Node callee, CanonType ct_first) {
    PolyMapKey key{Node_x_poly_mod(Node_x_symbol(callee)), Node_name(callee),
                   ct_first};
    auto it = map_.find(key);
    if (it != map_.end()) {
      return it->second;
    }
    if (CanonType_kind(ct_first) == NT::TypeVec) {
      key.first_param_type =
          tc_->InsertSpanType(false, CanonType_underlying_type(ct_first));
    }
    it = map_.find(key);
    if (it != map_.end()) {
      return it->second;
    }
    CompilerError(Node_srcloc(callee))
        << "cannot resolve polymorphic call for " << key;
    return kNodeInvalid;
  }
};

// =======================================
// =======================================

class TypeContext {
  std::array<CanonType, 10> base_type_map_;

  std::map<Name, CanonType> corpus_;

  void insert(CanonType ct) {
    ASSERT(!corpus_.contains(CanonType_name(ct)), "");
    corpus_[CanonType_name(ct)] = ct;
  }

  void insert_base_type(BASE_TYPE_KIND kind) {}

 public:
  TypeContext() {}
};

CanonType NodeSetType(Node node, CanonType ct) {
  ASSERT(Node_x_type(node).isnull(),
         "attempt to overwrite type " << Node_srcloc(node) << " " << node);
  ASSERT(!ct.isnull(), "invalid type at " << Node_srcloc(node) << " for "
                                          << EnumToString(Node_kind(node)));
  NodeChangeType(node, ct);
  return ct;
}

struct ValAndKind {
  std::string_view cleaned;
  BASE_TYPE_KIND kind;
};

ValAndKind NumCleanupAndTypeExtraction(std::string_view num,
                                       BASE_TYPE_KIND target_kind) {
  if (num == "false") return {num, BASE_TYPE_KIND::BOOL};
  if (num == "true") return {num, BASE_TYPE_KIND::BOOL};

  ValAndKind out = {.cleaned = num, .kind = target_kind};
  for (int i = 2; i <= 4 && i <= num.size(); i++) {
    // std::cout << "@@@ Trying " << num.substr(num.size() - i, i) << "\n" <<
    // std::flush;
    BASE_TYPE_KIND kind =
        BASE_TYPE_KIND_LOWER_FromString(num.substr(num.size() - i, i));
    if (kind != BASE_TYPE_KIND::INVALID) {
      out.cleaned.remove_suffix(i);
      out.kind = kind;
      return out;
    }
  }
  if (num[0] == '\'') {
    ASSERT(target_kind != BASE_TYPE_KIND::INVALID, "");
  }
  return out;
}

CanonType TypifyExprOrType(Node node, TypeCorpus* tc, CanonType ct_target,
                           PolyMap* pm);

void TypifyStmt(Node node, TypeCorpus* tc, CanonType ct_target, PolyMap* pm);

void TypifyStmtSeq(Node stmt, TypeCorpus* tc, CanonType ct_target,
                   PolyMap* pm) {
  for (; !stmt.isnull(); stmt = Node_next(stmt)) {
    TypifyStmt(stmt, tc, ct_target, pm);
  }
}

CanonType TypifyDefGlobalOrDefVar(Node node, TypeCorpus* tc, PolyMap* pm) {
  Node initial = Node_initial_or_undef_or_auto(node);
  Node type = Node_type_or_auto(node);

  CanonType ct;
  if (Node_kind(type) == NT::TypeAuto) {
    ASSERT(Node_kind(initial) != NT::ValUndef, "");
    ct = TypifyExprOrType(initial, tc, kCanonTypeInvalid, pm);
    TypifyExprOrType(type, tc, ct, pm);
  } else {
    ct = TypifyExprOrType(type, tc, kCanonTypeInvalid, pm);
    if (Node_kind(initial) != NT::ValUndef) {
      TypifyExprOrType(initial, tc, ct, pm);
    }
  }
  return NodeSetType(node, ct);
}

CanonType TypifyTypeFunOrDefFun(Node node, TypeCorpus* tc, PolyMap* pm) {
  ASSERT(Node_kind(node) == NT::DefFun || Node_kind(node) == NT::TypeFun, "");
  std::vector<CanonType> params;
  for (Node p = Node_params(node); !p.isnull(); p = Node_next(p)) {
    ASSERT(Node_kind(p) == NT::FunParam, "");
    CanonType ct = TypifyExprOrType(Node_type(p), tc, kCanonTypeInvalid, pm);
    NodeSetType(p, ct);
    params.push_back(ct);
  }
  params.push_back(
      TypifyExprOrType(Node_result(node), tc, kCanonTypeInvalid, pm));

  return NodeSetType(node, tc->InsertFunType(params));
}

CanonType TypifyId(Node id, TypeCorpus* tc, CanonType ct_target, PolyMap* pm) {
  Node def_node = Node_x_symbol(id);
  ASSERT(!def_node.isnull(),
         "unsymbolized ID " << Node_srcloc(id) << " " << Node_name(id));

  CanonType ct = Node_x_type(def_node);
  if (ct.isnull()) {
    switch (Node_kind(def_node)) {
      case NT::DefVar:
      case NT::DefGlobal:
        ct = TypifyDefGlobalOrDefVar(def_node, tc, pm);
        break;
      case NT::DefFun:
        ct = TypifyTypeFunOrDefFun(def_node, tc, pm);
        break;
      default:
        ASSERT(false, "Id for unsupported "
                          << Node_name(id) << " -> "
                          << EnumToString(Node_kind(def_node)) << " "
                          << EnumToString(Node_kind(def_node)));
        break;
    }
  }
  return NodeSetType(id, ct);
}

Node MaybewAdvanceRecField(Node field, Node point) {
  ASSERT(Node_kind(field) == NT::RecField, "");
  ASSERT(Node_kind(point) == NT::ValPoint, "");
  Node field_name = Node_point_or_undef(point);
  if (Node_kind(field_name) != NT::ValUndef) {
    ASSERT(Node_kind(field_name) == NT::Id, "unexpected index " << field_name);
    while (Node_name(field_name) != Node_name(field)) {
      field = Node_next(field);
      ASSERT(!field.isnull(), "");
    }
  }
  return field;
}

void AnnotateFieldWithTypeAndSymbol(Node id, Node field) {
  // std::cout << "@@ FIELD ANNOTATION " << Node_srcloc(id) << " " <<
  // Node_name(id)
  //           << "\n";
  ASSERT(Node_kind(id) == NT::Id, "");
  ASSERT(Node_kind(field) == NT::RecField, "");
  NodeSetType(id, Node_x_type(field));
  Node_x_symbol(id) = field;
}

CanonType TypifyValCompound(Node node, TypeCorpus* tc, CanonType ct_target,
                            PolyMap* pm) {
  CanonType ct = TypifyExprOrType(Node_type_or_auto(node), tc, ct_target, pm);
  if (CanonType_kind(ct) == NT::TypeVec) {
    CanonType element_type = CanonType_underlying_type(ct);

    for (Node point = Node_inits(node); !point.isnull();
         point = Node_next(point)) {
      ASSERT(Node_kind(point) == NT::ValPoint, "");
      NodeSetType(point, element_type);
      //
      Node val = Node_value_or_undef(point);
      if (Node_kind(val) != NT::ValUndef) {
        TypifyExprOrType(val, tc, element_type, pm);
      }
      //
      Node index = Node_point_or_undef(point);
      CanonType uint_type = tc->get_uint_canon_type();
      if (Node_kind(index) != NT::ValUndef) {
        TypifyExprOrType(index, tc, uint_type, pm);
      }
    }
  } else {
    ASSERT(CanonType_kind(ct) == NT::DefRec,
           "expected DefRec " << Node_srcloc(node) << " "
                              << EnumToString(CanonType_kind(ct)));
    Node defrec = CanonType_ast_node(ct);
    ASSERT(Node_kind(defrec) == NT::DefRec, "");
    Node field = Node_fields(defrec);
    for (Node point = Node_inits(node); !point.isnull();
         point = Node_next(point), field = Node_next(field)) {
      field = MaybewAdvanceRecField(field, point);
      ASSERT(Node_kind(field) == NT::RecField, "");
      CanonType ct_field = Node_x_type(field);
      NodeSetType(point, ct_field);
      if (Node_kind(Node_point_or_undef(point)) == NT::Id) {
        AnnotateFieldWithTypeAndSymbol(Node_point_or_undef(point), field);
      } else {
        ASSERT(Node_kind(Node_point_or_undef(point)) == NT::ValUndef, "");
      }
      if (Node_kind(Node_value_or_undef(point)) != NT::ValUndef) {
        TypifyExprOrType(Node_value_or_undef(point), tc, ct_field, pm);
      }
    }
  }
  return NodeSetType(node, ct);
}

uint32_t ComputeArrayLength(Node node) {
  switch (Node_kind(node)) {
    case NT::ValNum: {
      ValAndKind val = NumCleanupAndTypeExtraction(StrData(Node_number(node)),
                                                   BASE_TYPE_KIND::UINT);
      ASSERT(IsInt(val.kind), "");
      // Needs more work
      auto num = ParseInt<uint32_t>(val.cleaned);
      ASSERT(num.has_value(), "");
      return num.value();
    }
    case NT::Id:
      return ComputeArrayLength(Node_x_symbol(node));
    case NT::DefGlobal:
    case NT::DefVar:
      ASSERT(!Node_has_flag(node, BF::MUT), "");
      return ComputeArrayLength(Node_initial_or_undef_or_auto(node));
    case NT::Expr2: {
      uint32_t op1 = ComputeArrayLength(Node_expr1(node));
      uint32_t op2 = ComputeArrayLength(Node_expr2(node));
      switch (Node_binary_expr_kind(node)) {
        case BINARY_EXPR_KIND::ADD:
          return op1 + op2;
        case BINARY_EXPR_KIND::SUB:
          return op1 - op2;
        case BINARY_EXPR_KIND::MUL:
          return op1 * op2;
        case BINARY_EXPR_KIND::DIV:
          return op1 / op2;
        default:
          ASSERT(false, "");
          return 0;
      }
    }
    default:
      CompilerError(Node_srcloc(node))
          << "Vec dim must be a compile time constant";
      return 0;
  }
}

bool IsPolymorphicCallee(Node callee) {
  if (Node_kind(callee) != NT::Id) {
    return false;
  }
  Node def_sum = Node_x_symbol(callee);
  if (Node_kind(def_sum) != NT::DefFun) {
    return false;
  }
  return Node_has_flag(def_sum, BF::POLY);
}

CanonType TypifyExprCall(Node node, TypeCorpus* tc, CanonType ct_target,
                         PolyMap* pm) {
  Node callee = Node_callee(node);
  CanonType ct_fun;
  if (IsPolymorphicCallee(callee)) {
    ASSERT(Node_kind(callee) == NT::Id, "");
    Node first_arg = Node_args(node);
    ASSERT(!first_arg.isnull(), "");
    CanonType ct = TypifyExprOrType(first_arg, tc, kCanonTypeInvalid, pm);
    Node called_fun = pm->Resolve(callee, ct);
    UpdateNodeSymbolForPolyCall(callee, called_fun);
    ct_fun = Node_x_type(called_fun);
    NodeSetType(callee, ct_fun);
  } else {
    ct_fun = TypifyExprOrType(callee, tc, kCanonTypeInvalid, pm);
  }
  int num_parameters = CanonType_children(ct_fun).size() - 1;
  int num_args = NodeNumSiblings(Node_args(node));
  if (num_parameters != num_args) {
    CompilerError(Node_srcloc(node)) << "call parameter count mismatch";
  }
  int i = 0;
  for (Node arg = Node_args(node); !arg.isnull(); arg = Node_next(arg), ++i) {
    TypifyExprOrType(arg, tc, CanonType_children(ct_fun)[i], pm);
  }
  return NodeSetType(node, CanonType_children(ct_fun).back());
}

CanonType GetExprStmtType(Node root) {
  CanonType result = kCanonTypeInvalid;

  auto visitor = [&result, root](Node node, Node parent) -> bool {
    if (root != node && Node_kind(node) == NT::ExprStmt) {
      return true;
    }
    if (Node_kind(node) != NT::StmtReturn) {
      return false;
    }
    if (result.isnull()) {
      result = Node_x_type(Node_expr_ret(node));
    } else {
      ASSERT(result == Node_x_type(Node_expr_ret(node)), "");
    }
    return false;
  };
  VisitAstRecursivelyPre(root, visitor, kNodeInvalid);
  return result;
}

CanonType TypifyExprOrType(Node node, TypeCorpus* tc, CanonType ct_target,
                           PolyMap* pm) {
#if 0
  std::cout << "@@ TYPIFY: " << Node_srcloc(node) << " "
            << EnumToString(Node_kind(node))
            << " target: " << CanonType_name(ct_target) << "\n";
#endif
  if (!Node_x_type(node).isnull()) {
    return Node_x_type(node);
  }
  CanonType ct;

  switch (Node_kind(node)) {
    case NT::Id:
      return TypifyId(node, tc, ct_target, pm);
    //
    case NT::ValAuto:
    case NT::TypeAuto:
      ASSERT(!ct_target.isnull(), "" << Node_srcloc(node));
      return NodeSetType(node, ct_target);
    case NT::ValVoid:
      return NodeSetType(node, tc->get_void_canon_type());
    case NT::ValSpan:
      TypifyExprOrType(Node_expr_size(node), tc, tc->get_uint_canon_type(), pm);
      if (ct_target.isnull()) {
        CanonType ct_ptr =
            TypifyExprOrType(Node_pointer(node), tc, kCanonTypeInvalid, pm);
        ct_target = tc->InsertSpanType(CanonType_mut(ct_ptr),
                                       CanonType_underlying_type(ct_ptr));
      } else {
        ASSERT(CanonType_kind(ct_target) == NT::TypeSpan, "");
        CanonType ct_ptr = tc->InsertPtrType(
            CanonType_mut(ct_target), CanonType_underlying_type(ct_target));
        TypifyExprOrType(Node_pointer(node), tc, ct_ptr, pm);
      }
      return NodeSetType(node, ct_target);
    case NT::ValNum: {
      BASE_TYPE_KIND target =
          ct_target.isnull()
              ? BASE_TYPE_KIND::INVALID
              : CanonType_get_unwrapped_base_type_kind(ct_target);
      BASE_TYPE_KIND actual =
          NumCleanupAndTypeExtraction(StrData(Node_number(node)), target).kind;
      // if (actual == BASE_TYPE_KIND::INVALID)
      ASSERT(
          actual != BASE_TYPE_KIND::INVALID,
          "cannot parse " << Node_number(node) << " at " << Node_srcloc(node));
      return NodeSetType(node, tc->get_base_canon_type(actual));
    }
    case NT::ValCompound:
      return TypifyValCompound(node, tc, ct_target, pm);
    case NT::ValString: {
      int dim = ComputeStringLiteralLength(StrData(Node_string(node)));
      ct = tc->InsertVecType(dim, tc->get_base_canon_type(BASE_TYPE_KIND::U8));
      return NodeSetType(node, ct);
    }

    //
    case NT::TypeBase:
      return NodeSetType(node,
                         tc->get_base_canon_type(Node_base_type_kind(node)));
    case NT::TypeVec:
      TypifyExprOrType(Node_size(node), tc, tc->get_uint_canon_type(), pm);
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(
          node, tc->InsertVecType(ComputeArrayLength(Node_size(node)), ct));
    case NT::TypePtr:
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node,
                         tc->InsertPtrType(Node_has_flag(node, BF::MUT), ct));
    case NT::TypeSpan:
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node,
                         tc->InsertSpanType(Node_has_flag(node, BF::MUT), ct));
    case NT::TypeUnion: {
      std::vector<CanonType> children;
      for (Node child = Node_types(node); !child.isnull();
           child = Node_next(child)) {
        children.push_back(TypifyExprOrType(child, tc, kCanonTypeInvalid, pm));
      }
      return NodeSetType(
          node,
          tc->InsertUnionType(Node_has_flag(node, BF::UNTAGGED), children));
    }
    case NT::TypeUnionDelta: {
      CanonType ct_minuend =
          TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      CanonType ct_subtrahend =
          TypifyExprOrType(Node_subtrahend(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node,
                         tc->InsertUnionComplement(ct_minuend, ct_subtrahend));
    }
    case NT::TypeOf:
      ct = TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, ct);
    case NT::TypeFun:
      return TypifyTypeFunOrDefFun(node, tc, pm);
      //
    case NT::ExprParen:
      ct = TypifyExprOrType(Node_expr(node), tc, ct_target, pm);
      return NodeSetType(node, ct);
    case NT::Expr1:
      ct = TypifyExprOrType(Node_expr(node), tc, ct_target, pm);
      return NodeSetType(node, ct);
    case NT::Expr2: {
      BINARY_EXPR_KIND kind = Node_binary_expr_kind(node);
      if (IsComparison(kind)) {
        ct_target = kCanonTypeInvalid;
      }

      CanonType ct_left = TypifyExprOrType(Node_expr1(node), tc, ct_target, pm);

      TypifyExprOrType(Node_expr2(node), tc, ct_left, pm);
      if (IsComparison(kind)) {
        ct = tc->get_bool_canon_type();
      } else if (kind == BINARY_EXPR_KIND::PDELTA) {
        ct = tc->get_sint_canon_type();
      } else {
        ct = ct_left;
      }
      return NodeSetType(node, ct);
    }
    case NT::Expr3:
      TypifyExprOrType(Node_cond(node), tc, tc->get_bool_canon_type(), pm);
      ct = TypifyExprOrType(Node_expr_t(node), tc, ct_target, pm);
      TypifyExprOrType(Node_expr_f(node), tc, ct, pm);
      return NodeSetType(node, ct);

    case NT::ExprAddrOf:
      ct = TypifyExprOrType(Node_expr_lhs(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node,
                         tc->InsertPtrType(Node_has_flag(node, BF::MUT), ct));
    case NT::ExprField: {
      ct = TypifyExprOrType(Node_container(node), tc, ct_target, pm);
      if (CanonType_kind(ct) != NT::DefRec) {
        CompilerError(Node_srcloc(node)) << "Container is not of type rec "
                                         << EnumToString(CanonType_kind(ct));
      }
      Node field_name = Node_field(node);
      Node field_node = CanonType_lookup_rec_field(ct, Node_name(field_name));
      if (field_node.isnull()) {
        CompilerError(Node_srcloc(node))
            << "unknown field name " << Node_name(field_name);
      }
      AnnotateFieldWithTypeAndSymbol(field_name, field_node);
      return NodeSetType(node, Node_x_type(field_node));
    }
    case NT::ExprIndex:
      TypifyExprOrType(Node_expr_index(node), tc, tc->get_uint_canon_type(),
                       pm);
      ct = TypifyExprOrType(Node_container(node), tc, kCanonTypeInvalid, pm);
      if (CanonType_kind(ct) == NT::TypeVec ||
          CanonType_kind(ct) == NT::TypeSpan) {
        return NodeSetType(node, CanonType_underlying_type(ct));
      } else {
        CompilerError(Node_srcloc(node)) << "Container is not of type vec";
        return kCanonTypeInvalid;
      }
    case NT::ExprLen:
      TypifyExprOrType(Node_container(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, tc->get_uint_canon_type());
    case NT::ExprIs:
      TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, tc->get_bool_canon_type());
    case NT::ExprAs:
    case NT::ExprBitCast:
    case NT::ExprNarrow:
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, ct);
    case NT::ExprCall:
      return TypifyExprCall(node, tc, ct_target, pm);
    case NT::ExprWrap: {
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      ASSERT(CanonType_kind(ct) == NT::DefEnum ||
                 CanonType_kind(ct) == NT::DefType,
             "");
      TypifyExprOrType(Node_expr(node), tc, CanonType_underlying_type(ct), pm);
      return NodeSetType(node, ct);
    }
    case NT::ExprUnwrap:
      ct = TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      if (CanonType_kind(ct) == NT::DefType) {
        return NodeSetType(node, CanonType_children(ct)[0]);
      } else if (CanonType_kind(ct) == NT::DefEnum) {
        return NodeSetType(node, CanonType_underlying_type(ct));
      } else {
        CompilerError(Node_srcloc(node))
            << "unexpected type to unwrap " << EnumToString(CanonType_kind(ct));
        return kCanonTypeInvalid;
      }
    case NT::ExprUnionTag:
      ct = TypifyExprOrType(Node_expr(node), tc, ct_target, pm);
      ASSERT(CanonType_kind(ct) == NT::TypeUnion && !CanonType_untagged(ct),
             "");
      return NodeSetType(node, tc->get_typeid_canon_type());
    case NT::ExprPointer:
      ct = TypifyExprOrType(Node_expr1(node), tc, ct_target, pm);
      TypifyExprOrType(Node_expr2(node), tc, tc->get_uint_canon_type(), pm);
      if (Node_kind(Node_expr_bound_or_undef(node)) != NT::ValUndef) {
        TypifyExprOrType(Node_expr_bound_or_undef(node), tc,
                         tc->get_uint_canon_type(), pm);
      }
      return NodeSetType(node, ct);
    case NT::ExprDeref:
      ct = TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      if (CanonType_kind(ct) != NT::TypePtr) {
        CompilerError(Node_srcloc(node)) << "expected pointer type";
      }
      return NodeSetType(node, CanonType_underlying_type(ct));
    case NT::ExprOffsetof: {
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      Node field_node =
          CanonType_lookup_rec_field(ct, Node_name(Node_field(node)));
      if (field_node.isnull()) {
        CompilerError(Node_srcloc(node))
            << "unknown field name " << Node_name(Node_field(node));
      }
      AnnotateFieldWithTypeAndSymbol(Node_field(node), field_node);
      return NodeSetType(node, tc->get_uint_canon_type());
    }
    case NT::ExprTypeId:
      TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, tc->get_typeid_canon_type());
    case NT::ExprSizeof:
      ct = TypifyExprOrType(Node_type(node), tc, kCanonTypeInvalid, pm);
      return NodeSetType(node, tc->get_uint_canon_type());
    case NT::ExprFront: {
      ct = TypifyExprOrType(Node_container(node), tc, kCanonTypeInvalid, pm);
      if (CanonType_kind(ct) != NT::TypeSpan &&
          CanonType_kind(ct) != NT::TypeVec) {
        CompilerError(Node_srcloc(node))
            << "expected container in front expression";
      }
      bool mut = Node_has_flag(node, BF::MUT) ||
                 (Node_has_flag(node, BF::PRESERVE_MUT) &&
                  CanonType_kind(ct) == NT::TypeSpan && CanonType_mut(ct));
      return NodeSetType(node,
                         tc->InsertPtrType(mut, CanonType_underlying_type(ct)));
    }

    case NT::ExprStmt:
      TypifyStmtSeq(Node_body(node), tc, ct_target, pm);
      if (ct_target.isnull()) {
        ct_target = GetExprStmtType(node);
      }
      return NodeSetType(node, ct_target);
    default:
      ASSERT(false, "unsupported node " << Node_srcloc(node) << " "
                                        << EnumToString(Node_kind(node)));
      return kCanonTypeInvalid;
  }
}

void TypifyStmt(Node node, TypeCorpus* tc, CanonType ct_target, PolyMap* pm) {
  CanonType ct;
  switch (Node_kind(node)) {
    case NT::StmtAssignment:
    case NT::StmtCompoundAssignment:
      ct = TypifyExprOrType(Node_expr_lhs(node), tc, kCanonTypeInvalid, pm);
      TypifyExprOrType(Node_expr_rhs(node), tc, ct, pm);
      break;
    case NT::DefVar:
      TypifyDefGlobalOrDefVar(node, tc, pm);
      break;
    case NT::StmtDefer:
      TypifyStmtSeq(Node_body(node), tc, ct_target, pm);
      break;
    case NT::StmtReturn:
      TypifyExprOrType(Node_expr(node), tc, ct_target, pm);
      break;
    case NT::StmtBlock:
      TypifyStmtSeq(Node_body(node), tc, ct_target, pm);
      break;
    case NT::StmtIf:
      TypifyExprOrType(Node_cond(node), tc, tc->get_bool_canon_type(), pm);
      TypifyStmtSeq(Node_body_t(node), tc, ct_target, pm);
      TypifyStmtSeq(Node_body_f(node), tc, ct_target, pm);
      break;
    case NT::StmtCond:
      TypifyStmtSeq(Node_cases(node), tc, ct_target, pm);
      break;
    case NT::Case:
      TypifyExprOrType(Node_cond(node), tc, tc->get_bool_canon_type(), pm);
      TypifyStmtSeq(Node_body(node), tc, ct_target, pm);
      break;
    case NT::StmtExpr:
      TypifyExprOrType(Node_expr(node), tc, kCanonTypeInvalid, pm);
      break;
    case NT::StmtBreak:
    case NT::StmtContinue:
    case NT::StmtTrap:
      break;
    default:
      ASSERT(false, "unsupported node " << Node_srcloc(node) << " "
                                        << EnumToString(Node_kind(node)));
  }
}

void CheckTypeIs(Node node, CanonType expected) {
  CanonType actual = Node_x_type(node);

  if (actual != expected) {
    CompilerError(Node_srcloc(node))
        << "type mismatch for " << EnumToString(Node_kind(node))
        << " actual: " << CanonType_name(actual)
        << " expected: " << CanonType_name(expected);
  }
}

void CheckUnderlyingTypeIs(Node node, CanonType expected) {
  CanonType actual = CanonType_underlying_type(Node_x_type(node));

  if (actual != expected) {
    CompilerError(Node_srcloc(node))
        << "type mismatch for " << EnumToString(Node_kind(node))
        << " actual: " << CanonType_name(actual)
        << " expected: " << CanonType_name(expected);
  }
}

void CheckDefFunTypeFun(Node node) {
  CanonType ct = Node_x_type(node);
  ASSERT(CanonType_kind(ct) == NT::TypeFun,
         "expected fun type " << EnumToString(CanonType_kind(ct)) << " for  "
                              << node);
  const auto& children = CanonType_children(ct);

  ASSERT(children.size() == 1 + NodeNumSiblings(Node_args(node)), "");
  int i = 0;
  for (Node arg = Node_args(node); !arg.isnull(); arg = Node_next(arg), ++i) {
    CheckTypeIs(arg, children[i]);
  }
  CheckTypeIs(Node_result(node), children.back());
}

void CheckTypeKind(Node node, NT kind) {
  CanonType ct = Node_x_type(node);
  CHECK(CanonType_kind(ct) == kind,
        "in " << node << " expected " << EnumToString(kind) << " got "
              << EnumToString(CanonType_kind(ct)) << " " << Node_srcloc(node));
}
void CheckExpr2TypesArithmetic(CanonType result, Node op1, Node op2) {
  CHECK(CanonType_kind(result) == NT::TypeBase, "");
  CheckTypeIs(op1, result);
  CheckTypeIs(op2, result);
}

void CheckValUndefOrTypeIsUint(Node node) {
  if (Node_kind(node) == NT::ValUndef) return;
  CanonType ct = Node_x_type(node);
  if (CanonType_kind(ct) != NT::TypeBase ||
      !IsUint(CanonType_get_unwrapped_base_type_kind(ct))) {
    CompilerError(Node_srcloc(node)) << "expected uint type";
  }
}

void CheckExpr2Types(Node node, Node op1, Node op2, BINARY_EXPR_KIND kind,
                     TypeCorpus* tc) {
  if (IsArithmetic(kind)) {
    CheckExpr2TypesArithmetic(Node_x_type(node), op1, op2);
  } else if (IsComparison(kind)) {
    CheckTypeIs(node, tc->get_bool_canon_type());
    if (kind == BINARY_EXPR_KIND::EQ || kind == BINARY_EXPR_KIND::NE) {
      if (!IsCompatibleTypeForEq(Node_x_type(op1), Node_x_type(op2))) {
        CompilerError(Node_srcloc(op1))
            << "incompatible types for comparison testing";
      }
    } else {
      if (!IsCompatibleTypeForCmp(Node_x_type(op1), Node_x_type(op2))) {
        CompilerError(Node_srcloc(op1))
            << "incompatible types for comparison testing";
      }
    }
  } else if (IsShortCircuit(kind)) {
    auto ct = tc->get_bool_canon_type();
    CheckTypeIs(node, ct);
    CheckTypeIs(op1, ct);
    CheckTypeIs(op2, ct);
  } else if (kind == BINARY_EXPR_KIND::PDELTA) {
    CheckTypeIs(node, tc->get_sint_canon_type());
    CheckTypeKind(op1, NT::TypePtr);
    CheckTypeKind(op2, NT::TypePtr);
    if (CanonType_underlying_type(Node_x_type(op1)) !=
        CanonType_underlying_type(Node_x_type(op2))) {
      CompilerError(Node_srcloc(node))
          << "pointers must have same underlying type";
    }
  } else {
    CHECK(false, "NYI " << EnumToString(kind));
  }
}

bool AddressCanBeTaken(Node node) {
  switch (Node_kind(node)) {
    case NT::Id: {
      Node sym = Node_x_symbol(node);
      return (Node_kind(sym) == NT::DefVar ||
              Node_kind(sym) == NT::DefGlobal) &&
             Node_has_flag(sym, BF::REF);
    }
    case NT::ExprField:
    case NT::ExprDeref:
      return true;
    case NT::ExprIndex:

      if (CanonType_kind(Node_x_type(Node_container(node))) == NT::TypeSpan) {
        return true;
      } else {
        CHECK(CanonType_kind(Node_x_type(Node_container(node))) == NT::TypeVec,
              "");
        return AddressCanBeTaken(Node_container(node));
      }
    default:
      return false;
  }
}

void CheckTypeCompatibleWithOptionalStrict(Node src_node, CanonType dst_ct,
                                           bool strict) {
  CanonType src_ct = Node_x_type(src_node);
  if (src_ct == dst_ct) return;

  if (strict) {
    if (IsDropMutConversion(src_ct, dst_ct)) {
      CompilerError(Node_srcloc(src_node)) << "drop conversion";
    }
  } else {
    bool writable =
        CanonType_kind(src_ct) == NT::TypeVec && IsProperLhs(src_node);
    if (!IsCompatibleType(src_ct, dst_ct, writable)) {
      CompilerError(Node_srcloc(src_node))
          << "type mismatch for " << src_node << ": " << src_ct << " -> "
          << dst_ct;
    }
  }
}

void TypeCheckRecursively(Node mod, TypeCorpus* tc, bool strict) {
  // std::cout << "@@ TYPECHECK: " << Node_name(mod) << "\n";

  auto type_checker = [&tc, &strict](Node node, Node parent) {
    CanonType ct = Node_x_type(node);

    switch (Node_kind(node)) {
      case NT::ExprIs:
        return CheckTypeIs(node, tc->get_bool_canon_type());
      case NT::ExprOffsetof:
      case NT::ExprSizeof:
      case NT::ExprLen:
        return CheckTypeIs(node, tc->get_uint_canon_type());
      case NT::StmtIf:
      case NT::Case:
      case NT::StmtStaticAssert:
        return CheckTypeIs(Node_cond(node), tc->get_bool_canon_type());
      case NT::ValVoid:
        return CheckTypeIs(node, tc->get_void_canon_type());
      case NT::ExprTypeId:
        return CheckTypeIs(node, tc->get_typeid_canon_type());
      case NT::Expr1:
        return CheckTypeIs(node, Node_x_type(Node_expr(node)));
      case NT::TypeOf:
        return CheckTypeIs(node, Node_x_type(Node_expr(node)));
      case NT::ExprParen:
        return CheckTypeIs(node, Node_x_type(Node_expr(node)));
      case NT::FunParam:
        // return CheckTypeIs(node, Node_x_type(Node_type(node)));
        return;
        //
      case NT::TypeBase:
        return CheckTypeKind(node, NT::TypeBase);
      case NT::TypeSpan:
        return CheckTypeKind(node, NT::TypeSpan);
      case NT::TypeVec:
        return CheckTypeKind(node, NT::TypeVec);
      case NT::TypePtr:
        return CheckTypeKind(node, NT::TypePtr);
      case NT::TypeUnion:
        return CheckTypeKind(node, NT::TypeUnion);
      case NT::ValNum:
        CHECK(CanonType_get_unwrapped_base_type_kind(Node_x_type(node)) !=
                  BASE_TYPE_KIND::INVALID,
              "");
        break;
      case NT::ValString:
        return CheckTypeKind(node, NT::TypeVec);
      case NT::ValSpan:
        // TODO: does not work after constant folding
        CheckTypeKind(node, NT::TypeSpan);
        // return CheckTypeIs(
        //     node, CanonType_underlying_type(Node_x_type(node)),
        //     CanonType_underlying_type(Node_x_type(Node_pointer(node))));
        return;
      case NT::ExprUnionTag:
        CheckTypeKind(Node_expr(node), NT::TypeUnion);
        CHECK(!CanonType_untagged(Node_x_type(Node_expr(node))), "");
        return CheckTypeIs(node, tc->get_typeid_canon_type());
        break;
      case NT::ExprDeref:
        CheckTypeKind(Node_expr(node), NT::TypePtr);
        return CheckTypeIs(
            node, CanonType_underlying_type(Node_x_type(Node_expr(node))));
      case NT::Expr3:
        CheckTypeIs(Node_expr_t(node), Node_x_type(node));
        CheckTypeIs(Node_expr_f(node), Node_x_type(node));
        return CheckTypeIs(Node_cond(node), tc->get_bool_canon_type());

      case NT::Id: {
        Node def_node = Node_x_symbol(node);
        switch (Node_kind(def_node)) {
          case NT::DefVar:
          case NT::DefGlobal:
            return CheckTypeIs(node, Node_x_type(Node_type_or_auto(def_node)));
          case NT::FunParam:
            return CheckTypeIs(node, Node_x_type(Node_type(def_node)));
          case NT::DefRec:
          case NT::DefFun:
          case NT::DefType:
          case NT::DefEnum:
          case NT::EnumVal:
          case NT::RecField:
            return CheckTypeIs(node, Node_x_type(def_node));
          default:
            CHECK(false, "unexpected " << EnumToString(Node_kind(def_node)));
            break;
        }
        return;
      }
      case NT::Expr2:
        return CheckExpr2Types(node, Node_expr1(node), Node_expr2(node),
                               Node_binary_expr_kind(node), tc);
      case NT::ExprField:
        CheckTypeKind(Node_container(node), NT::DefRec);
        return CheckTypeIs(node, Node_x_type(Node_x_symbol(Node_field(node))));
      case NT::ExprPointer:
        CheckValUndefOrTypeIsUint(Node_expr_bound_or_undef(node));
        CheckTypeKind(node, NT::TypePtr);
        return CheckTypeIs(Node_expr1(node), Node_x_type(node));
      case NT::DefType:
        if (Node_has_flag(node, BF::WRAPPED)) {
          return CheckTypeKind(node, NT::DefType);
        } else {
          return CheckTypeIs(Node_type(node), Node_x_type(node));
        }
      case NT::ExprAs:
        if (!IsCompatibleTypeForAs(Node_x_type(Node_expr(node)),
                                   Node_x_type(node))) {
          CompilerError(Node_srcloc(node))
              << "bad ExprAs conversion " << Node_x_type(node) << " <- "
              << Node_x_type(Node_expr(node));
        }
        return CheckTypeIs(Node_type(node), Node_x_type(node));

      case NT::ExprBitCast:
        if (!IsCompatibleTypeForBitcast(Node_x_type(node),
                                        Node_x_type(Node_expr(node)))) {
          CompilerError(Node_srcloc(node))
              << "bad ExprBitCast conversion " << Node_x_type(node) << " <- "
              << Node_x_type(Node_expr(node));
        }
        return CheckTypeIs(Node_type(node), Node_x_type(node));

      case NT::StmtCompoundAssignment:
        if (!IsProperLhs(Node_expr_lhs(node))) {
          CompilerError(Node_srcloc(node)) << "cannot assign to readonly data";
        }
        CHECK(IsArithmetic(Node_binary_expr_kind(node)), "");
        return CheckExpr2TypesArithmetic(Node_x_type(Node_expr_lhs(node)),
                                         Node_expr_lhs(node),
                                         Node_expr_rhs(node));
      case NT::ExprIndex: {
        NT kind = CanonType_kind(Node_x_type(Node_container(node)));
        CHECK(kind == NT::TypeVec || kind == NT::TypeSpan, "");
        return CheckUnderlyingTypeIs(Node_container(node), ct);
      }

      case NT::ExprFront: {
        CheckTypeKind(node, NT::TypePtr);
        Node container = Node_container(node);
        CanonType container_ct = Node_x_type(container);
        bool mut = CanonType_mut(Node_x_type(node));

        if (CanonType_kind(container_ct) == NT::TypeSpan) {
          if (mut && !CanonType_mut(container_ct)) {
            CompilerError(Node_srcloc(node)) << "span not mutable";
          }
        } else {
          CHECK(CanonType_kind(container_ct) == NT::TypeVec, "");
          if (mut && !IsProperLhs(container)) {
            CompilerError(Node_srcloc(node)) << "vec not mutable";
          }
          // TODO: check if address can be taken
        }

        return CheckUnderlyingTypeIs(node,
                                     CanonType_underlying_type(container_ct));
      }

      case NT::ExprAddrOf: {
        break;
        CheckTypeKind(node, NT::TypePtr);
        Node lhs = Node_expr_lhs(node);
        CanonType lhs_ct = Node_x_type(lhs);
        if (Node_has_flag(node, BF::MUT)) {
          if (!IsProperLhs(lhs)) {
            CompilerError(Node_srcloc(node))
                << "not mutable " << EnumToString(Node_kind(lhs));
          }
        }

        if (!AddressCanBeTaken(lhs))
          CompilerError(Node_srcloc(node)) << "address cannot be taken";
        return CheckUnderlyingTypeIs(node, lhs_ct);
      }
      case NT::ExprWiden:
        CheckTypeIs(node, Node_x_type(Node_type(node)));
        if (!IsSubtypeOfUnion(Node_x_type(Node_expr(node)),
                              Node_x_type(node))) {
          CompilerError(Node_srcloc(node)) << "incompatible typed for widening";
        }
        return;
      case NT::ExprUnionUntagged: {
        CanonType ct_expr = Node_x_type(Node_expr(node));
        CheckTypeKind(Node_expr(node), NT::TypeUnion);
        CheckTypeKind(node, NT::TypeUnion);
        if (CanonType_untagged(ct_expr) || !CanonType_untagged(ct)) {
          CompilerError(Node_srcloc(node))
              << "expected conversion from tagged to untagged";
        }
        if (!TypeListsAreTheSame(CanonType_children(ct_expr),
                                 CanonType_children(ct))) {
          CompilerError(Node_srcloc(node)) << "unions are not compatible";
        }
        return;
      }
      case NT::ExprUnwrap: {
        CanonType ct_expr = Node_x_type(Node_expr(node));
        if (CanonType_kind(ct_expr) != NT::DefType &&
            CanonType_kind(ct_expr) != NT::DefEnum) {
          CompilerError(Node_srcloc(node)) << "expected a type or enum";
        }
        return CheckUnderlyingTypeIs(Node_expr(node), ct);
      }
      case NT::ExprWrap: {
        CanonType ct_dst = Node_x_type(Node_type(node));
        CheckTypeIs(node, Node_x_type(Node_type(node)));
        CanonType ct_target = CanonType_underlying_type(ct_dst);
        CanonType ct_src = Node_x_type(Node_expr(node));
        if (ct_target == ct_src) return;

        if (CanonType_kind(ct_dst) == NT::DefType &&
            IsDropMutConversion(ct_src, ct_target))
          return;
        CompilerError(Node_srcloc(node)) << "unions are not compatible";
      }

      case NT::EnumVal:
        return CheckTypeKind(node, NT::DefEnum);
      case NT::DefRec:
      case NT::DefEnum:
        CHECK(node == CanonType_ast_node(ct), "");
        break;
      case NT::RecField:
        return CheckTypeIs(Node_type(node), Node_x_type(node));
      case NT::ValCompound:
        if (CanonType_kind(ct) == NT::TypeVec) {
          CanonType ct_underlying = CanonType_underlying_type(ct);
          for (Node field = Node_inits(node); !field.isnull();
               field = Node_next(field)) {
            CheckTypeIs(field, ct_underlying);
            CheckValUndefOrTypeIsUint(Node_point_or_undef(field));
          }
        } else {
          CHECK(CanonType_kind(ct) == NT::DefRec, "");
          Node defrec = CanonType_ast_node(ct);
          Node field = Node_fields(defrec);

          for (Node point = Node_inits(node); !point.isnull();
               point = Node_next(point), field = Node_next(field)) {
            field = MaybewAdvanceRecField(field, point);
            CHECK(Node_kind(field) == NT::RecField, "");
            CanonType ct_field = Node_x_type(field);
            CheckTypeIs(point, ct_field);
          }
        }
        return;
      case NT::TypeFun:
      case NT::DefFun:
        CheckDefFunTypeFun(node);
        return;
        // ========= behavior changes when "strict"

      case NT::ExprNarrow:
        if (strict) {
          // unchecked
          CanonType src_ct = Node_x_type(Node_expr(node));

          if (!CanonType_untagged(src_ct) &&
              !Node_has_flag(node, BF::UNCHECKED)) {
            CompilerError(Node_srcloc(node))
                << "incompatible typed for narrowing";
          }
        } else {
          // checked
          CheckTypeIs(node, Node_x_type(Node_type(node)));
          if (!IsSubtypeOfUnion(ct, Node_x_type(Node_expr(node)))) {
            CompilerError(Node_srcloc(node))
                << "incompatible typed for narrowing";
          }
        }
        return;
      case NT::ExprCall: {
        CanonType fun_sig = Node_x_type(Node_callee(node));
        CHECK(CanonType_kind(fun_sig) == NT::TypeFun, "");
        CheckTypeIs(node, CanonType_result_type(fun_sig));
        int num_parameters = CanonType_children(fun_sig).size() - 1;
        int num_args = NodeNumSiblings(Node_args(node));
        if (num_parameters != num_args) {
          CompilerError(Node_srcloc(node)) << "call parameter count mismatch";
        }
        int i = 0;
        for (Node arg = Node_args(node); !arg.isnull();
             arg = Node_next(arg), ++i) {
          CanonType ct_target = CanonType_children(fun_sig)[i];
          CheckTypeCompatibleWithOptionalStrict(arg, ct_target, strict);
        }
        return;
      }
      case NT::StmtAssignment:
        if (!IsProperLhs(Node_lhs(node))) {
          CompilerError(Node_srcloc(node)) << "cannot assign to readonly data";
        }
        return CheckTypeCompatibleWithOptionalStrict(
            Node_expr_rhs(node), Node_x_type(Node_lhs(node)), strict);

      case NT::StmtReturn: {
        Node target = Node_x_target(node);
        CanonType ct_target = Node_kind(target) == NT::DefFun
                                  ? Node_x_type(Node_result(target))
                                  : Node_x_type(target);
        return CheckTypeCompatibleWithOptionalStrict(Node_expr_ret(node),
                                                     ct_target, strict);
      }
      case NT::DefGlobal:
      case NT::DefVar: {
        Node initial = Node_initial_or_undef_or_auto(node);
        if (Node_kind(initial) != NT::ValUndef) {
          CheckTypeCompatibleWithOptionalStrict(initial, ct, strict);
        }
        return CheckTypeIs(node, Node_x_type(Node_type(node)));
      }
      case NT::ValPoint: {
        Node val = Node_value_or_undef(node);
        if (Node_kind(val) != NT::ValUndef) {
          CheckTypeCompatibleWithOptionalStrict(val, ct, strict);
        }
        return;
      }
        // ========= nothing to check yet
      case NT::ExprStmt:
      case NT::TypeAuto:
      case NT::ValAuto:
      case NT::TypeUnionDelta:
        return;
        //  ========= No type annotation
      case NT::ValUndef:
      case NT::DefMod:
      case NT::StmtExpr:
      case NT::StmtTrap:
      case NT::StmtBreak:
      case NT::StmtContinue:
      case NT::StmtDefer:
      case NT::StmtBlock:
      case NT::StmtCond:
        CHECK(ct.isnull(),
              "no type info expected for " << EnumToString(Node_kind(node)));
        // no type checking
        return;
      default:
        CHECK(false, "NYI " << EnumToString(Node_kind(node)));
        return;
    };
  };
  VisitAstRecursivelyPost(mod, type_checker, kNodeInvalid);
}

}  //  namespace

void NodeChangeType(Node node, CanonType ct) { Node_x_type(node) = ct; }

Node MakeDefRec(Name name, std::span<NameAndType> fields, TypeCorpus* tc) {
  NodeChain chain;
  for (const auto& nt : fields) {
    Node f = NodeNew(NT::RecField);
    NodeInitRecField(f, nt.name, MakeTypeAuto(nt.ct, kSrcLocInvalid),
                     kStrInvalid, kSrcLocInvalid, nt.ct);
    chain.Append(f);
  }

  Node out = NodeNew(NT::DefRec);
  NodeInitDefRec(out, name, chain.First(), 0, kStrInvalid, kSrcLocInvalid,
                 kCanonTypeInvalid);
  CanonType ct = tc->InsertRecType(NameData(name), out, true);
  NodeSetType(out, ct);
  return out;
}

void AddTypesToAst(const std::vector<Node>& mods, TypeCorpus* tc) {
  if (sw_verbose.Value()) std::cout << "Phase 1\n";

  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      switch (Node_kind(child)) {
        case NT::DefRec: {
          std::string name;
          name.append(NameData(Node_name(mod)));
          name.append("/");
          name.append(NameData(Node_name(child)));
          CanonType ct = tc->InsertRecType(name, child, false);
          NodeSetType(child, ct);
          break;
        }
        case NT::DefEnum: {
          std::string name;
          name.append(NameData(Node_name(mod)));
          name.append("/");
          name.append(NameData(Node_name(child)));
          CanonType ct = tc->InsertEnumType(name, child);
          NodeSetType(child, ct);
          break;
        }
        case NT::DefType:
          if (Node_has_flag(child, BF::WRAPPED)) {
            std::string name;
            name.append(NameData(Node_name(mod)));
            name.append("/");
            name.append(NameData(Node_name(child)));
            CanonType ct = tc->InsertWrappedTypePre(name);
            NodeSetType(child, ct);
          }
          break;

        default:
          break;
      }
    }
  }

  if (sw_verbose.Value()) std::cout << "Phase 2\n";

  PolyMap poly_map(tc);

  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      switch (Node_kind(child)) {
        case NT::DefRec: {
          std::vector<CanonType> children;
          for (Node field = Node_fields(child); !field.isnull();
               field = Node_next(field)) {
            CanonType ct = TypifyExprOrType(Node_value_or_auto(field), tc,
                                            kCanonTypeInvalid, &poly_map);
            children.push_back(ct);
            NodeSetType(field, ct);
          }
          CanonType_children(Node_x_type(child)) = children;
          break;
        }
        case NT::DefEnum: {
          CanonType ct = Node_x_type(child);
          CanonType underlying_ct = CanonType_underlying_type(ct);
          for (Node field = Node_items(child); !field.isnull();
               field = Node_next(field)) {
            TypifyExprOrType(Node_value_or_auto(field), tc, underlying_ct,
                             &poly_map);
            NodeSetType(field, ct);
          }
          break;
        }
        case NT::DefType: {
          CanonType ct = TypifyExprOrType(Node_type(child), tc,
                                          kCanonTypeInvalid, &poly_map);
          if (Node_has_flag(child, BF::WRAPPED)) {
            // was annotated in phase1
            tc->InsertWrappedTypeFinalize(Node_x_type(child), ct);
          } else {
            NodeSetType(child, ct);
          }
          break;
        }
        default:
          break;
      }
    }
  }

  if (sw_verbose.Value()) std::cout << "Phase 3\n";

  for (Node mod : mods) {
    for (Node node = Node_body_mod(mod); !node.isnull();
         node = Node_next(node)) {
      switch (Node_kind(node)) {
        case NT::DefRec:
        case NT::DefEnum:
        case NT::DefType:
        case NT::Import:
          continue;
        case NT::DefGlobal:
          if (Node_x_type(node).isnull()) {
            TypifyDefGlobalOrDefVar(node, tc, &poly_map);
          }
          break;
        case NT::StmtStaticAssert:
          TypifyExprOrType(Node_cond(node), tc, tc->get_bool_canon_type(),
                           &poly_map);
          break;
        case NT::DefFun:
          if (Node_x_type(node).isnull()) {
            TypifyTypeFunOrDefFun(node, tc, &poly_map);
          }
          if (Node_has_flag(node, BF::POLY)) {
            poly_map.Register(node);
          }

          break;
        default:
          CHECK(false, "unexpected top level node " << node);
          break;
      }
    }
  }

  if (sw_verbose.Value()) std::cout << "Phase 4\n";

  for (Node mod : mods) {
    for (Node fun = Node_body_mod(mod); !fun.isnull(); fun = Node_next(fun)) {
      if (Node_kind(fun) == NT::DefFun && !Node_has_flag(fun, BF::EXTERN)) {
        for (Node child = Node_body(fun); !child.isnull();
             child = Node_next(child)) {
          TypifyStmt(child, tc, Node_x_type(Node_result(fun)), &poly_map);
        }
      }
    }
  }

  tc->SetAbiInfoForAllTypes();
}

void TypeCheckAst(const std::vector<Node>& mods, TypeCorpus* tc, bool strict) {
  for (Node mod : mods) {
    TypeCheckRecursively(mod, tc, strict);
  }
}

void ModStripTypeNodesRecursively(Node node) {
  auto replacer = [](Node node, Node parent) -> Node {
    switch (node.kind()) {
      case NT::Id: {
        Node sym = Node_x_symbol(node);
        if (sym.kind() == NT::DefRec || sym.kind() == NT::DefEnum ||
            sym.kind() == NT::DefType) {
          const SrcLoc& sl = Node_srcloc(node);
          CanonType ct = Node_x_type(node);
          NodeFreeRecursively(node);
          return MakeTypeAuto(ct, sl);
        }

        return node;
      }

      case NT::TypeOf:
      case NT::TypeFun:
      case NT::TypeBase:
      case NT::TypeSpan:
      case NT::TypeVec:
      case NT::TypePtr:
      case NT::TypeUnion:
      case NT::TypeUnionDelta: {
        const SrcLoc& sl = Node_srcloc(node);
        CanonType ct = Node_x_type(node);
        NodeFreeRecursively(node);
        return MakeTypeAuto(ct, sl);
      }
      default:
        return node;
    }
  };

  MaybeReplaceAstRecursivelyPost(node, replacer, kNodeInvalid);
}

}  // namespace cwerg::fe