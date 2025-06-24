#include "FE/eval.h"

#include <set>
#include <string_view>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"
#include "FE/type_corpus.h"
#include "Util/handle.h"
#include "Util/immutable.h"
#include "Util/parse.h"
#include "Util/switch.h"

namespace cwerg::fe {
SwitchBool sw_verbose("verbose_eval", "make eval more verbose");

ImmutablePool ConstPool(alignof(uint64_t));

Const ParseNum(Node node) {
  ASSERT(Node_kind(node) == NT::ValNum, "");
  CanonType ct = Node_x_type(node);
  ASSERT(CanonType_kind(ct) == NT::TypeBase, "");

  std::string_view num = StrData(Node_number(node));
  if (num == "false") return ConstNewBool(false);
  if (num == "true") return ConstNewBool(true);

  BASE_TYPE_KIND target_kind = CanonType_get_unwrapped_base_type_kind(ct);
  ASSERT(target_kind != BASE_TYPE_KIND::UINT, "");

  for (int i = 2; i <= 4 && i <= num.size(); i++) {
    // std::cout << "@@@ Trying " << num.substr(num.size() - i, i) << "\n"
    //          << std::flush;
    BASE_TYPE_KIND kind =
        BASE_TYPE_KIND_FromString(num.substr(num.size() - i, i));
    if (kind != BASE_TYPE_KIND::INVALID) {
      num.remove_suffix(i);
      break;
    }
  }

  if (num[0] == '\'') {
    auto val = ParseChar(num);
    if (!val) return kConstInvalid;
    return ConstNew<uint64_t>(val.value(), target_kind);
  }

  if (IsSint(target_kind)) {
    auto val = ParseInt<int64_t>(num);
    if (!val) return kConstInvalid;
    return ConstNew<int64_t>(val.value(), target_kind);
  } else if (IsUint(target_kind)) {
    auto val = ParseInt<uint64_t>(num);
    if (!val) return kConstInvalid;
    return ConstNew<uint64_t>(val.value(), target_kind);
  }
  ASSERT(IsFlt(target_kind), "");
  auto val = ParseFlt64(num);
  if (!val) return kConstInvalid;
  return ConstNew<double>(val.value(), target_kind);
}

namespace {

constexpr std::array<CONST_KIND, 64> MakeBaseTypeToConstType() {
  std::array<CONST_KIND, 64> out;
  out[int(BASE_TYPE_KIND::VOID)] = CONST_KIND::VOID;
  out[int(BASE_TYPE_KIND::BOOL)] = CONST_KIND::BOOL;
  //
  out[int(BASE_TYPE_KIND::S8)] = CONST_KIND::S8;
  out[int(BASE_TYPE_KIND::S16)] = CONST_KIND::S16;
  out[int(BASE_TYPE_KIND::S32)] = CONST_KIND::S32;
  out[int(BASE_TYPE_KIND::S64)] = CONST_KIND::S64;
  //
  out[int(BASE_TYPE_KIND::U8)] = CONST_KIND::U8;
  out[int(BASE_TYPE_KIND::U16)] = CONST_KIND::U16;
  out[int(BASE_TYPE_KIND::U32)] = CONST_KIND::U32;
  out[int(BASE_TYPE_KIND::U64)] = CONST_KIND::U64;

  return out;
}

const std::array<CONST_KIND, 64> gBaseTypeToConstType =
    MakeBaseTypeToConstType();

Const EvalValWithPossibleImplicitConversion(CanonType dst_type, Node src_node) {
  Const src_value = Node_x_eval(src_node);
  if (Node_kind(src_node) == NT::ValUndef) return src_value;
  CanonType src_type = Node_x_type(src_node);
  if (src_type == dst_type || IsDropMutConversion(src_type, dst_type)) {
    return src_value;
  }
  if (IsVecToSpanConversion(src_type, dst_type)) {
    if (src_value.isnull()) {
      return ConstNewSpan(
          {kNodeInvalid, CanonType_dim(src_type), kConstInvalid});
    } else {
      ASSERT(src_value.kind() == CONST_KIND::COMPOUND,
             "unxpected kind " << int(src_value.kind()));
      return ConstNewSpan({ConstGetCompound(src_value).symbol,
                           CanonType_dim(src_type), src_value});
    }
  }
  return src_value;
}

void AssignValue(Node node, Const val) { Node_x_eval(node) = val; }

Const GetDefaultForBaseType(BASE_TYPE_KIND bt) {
  if (IsUint(bt))
    return ConstNew<uint64_t>(0, bt);
  else if (IsSint(bt))
    return ConstNew<int64_t>(0, bt);
  else if (IsFlt(bt))
    return ConstNew<double>(0.0, bt);
  else if (bt == BASE_TYPE_KIND::BOOL)
    return ConstNewBool(false);
  else {
    ASSERT(false, "");
    return kConstInvalid;
  }
}

Const GetDefaultForType(CanonType ct) {
  switch (CanonType_kind(ct)) {
    case NT::TypeBase:
      return GetDefaultForBaseType(CanonType_get_unwrapped_base_type_kind(ct));
    case NT::DefType:
      return GetDefaultForType(CanonType_underlying_type(ct));
    case NT::TypeSpan:
      return ConstNewSpan({kNodeInvalid, 0, kConstInvalid});
    default:
      if (CanonType_is_complex(ct))
        return ConstNewCompound({kNodeInvalid, kNodeInvalid});
      else
        return kConstInvalid;
  }
}

Const GetValForVecAtPos(Const container_val, uint64_t index, CanonType ct) {
  if (container_val.kind() == CONST_KIND::SPAN) {
    container_val = ConstGetSpan(container_val).content;
    if (container_val.isnull()) return kConstInvalid;
  }

  ASSERT(container_val.kind() == CONST_KIND::COMPOUND,
         "" << int(container_val.kind()));
  Node init_node = ConstGetCompound(container_val).init_node;
  if (init_node.isnull()) {
    return GetDefaultForType(ct);
  }

  size_t dim = CanonType_size(Node_x_type(init_node));
  ASSERT(index < dim, "");
  if (init_node.kind() == NT::ValString) {
    char* buffer = new char[dim];
    size_t size = StringLiteralToBytes(StrData(Node_string(init_node)), buffer);
    ASSERT(size != STRING_LITERAL_PARSE_ERROR, "");
    ASSERT(index < size, "");
    Const out = ConstNew<uint64_t>(uint8_t(buffer[index]), BASE_TYPE_KIND::U8);
    delete[] buffer;
    return out;
  }

  ASSERT(init_node.kind() == NT::ValCompound, "");
  uint64_t n = 0;
  for (Node point = Node_inits(init_node); !point.isnull();
       point = Node_next(point)) {
    ASSERT(point.kind() == NT::ValPoint, "");
    Node p = Node_point_or_undef(point);
    if (p.kind() != NT::ValUndef) {
      n = ConstGetUnsigned(Node_x_eval(p));
    }
    if (n == index) return Node_x_eval(Node_value_or_undef(point));
    if (n > index) return GetDefaultForType(ct);
    ++n;
  }
  return kConstInvalid;
}

Node MaybewAdvanceRecField(Node point, Node field) {
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

Const GetValForRecAtField(Const container, Node target_field) {
  ASSERT(container.kind() == CONST_KIND::COMPOUND, "");
  ASSERT(target_field.kind() == NT::RecField, "");
  Node compound = ConstGetCompound(container).init_node;
  if (compound.isnull()) {
    return GetDefaultForType(Node_x_type(target_field));
  }
  ASSERT(compound.kind() == NT::ValCompound,
         "expected compound val " << int(compound.kind()));
  Node defrec = CanonType_ast_node(Node_x_type(compound));
  ASSERT(defrec.kind() == NT::DefRec, "");
  Node field = Node_fields(defrec);
  for (Node point = Node_inits(compound); !point.isnull();
       point = Node_next(point), field = Node_next(field)) {
    field = MaybewAdvanceRecField(point, field);
    if (field == target_field) {
      return Node_x_eval(Node_value_or_undef(point));
    }
  }
  return GetDefaultForType(Node_x_type(target_field));
}

Const EvalExpr1(UNARY_EXPR_KIND op, Const e, CanonType ct) {
  BASE_TYPE_KIND bt = CanonType_get_unwrapped_base_type_kind(ct);
  switch (op) {
    case UNARY_EXPR_KIND::NOT:
      if (bt == BASE_TYPE_KIND::BOOL) {
        return ConstNewBool(!ConstGetUnsigned(e));
      } else {
        ASSERT(IsUint(bt), "");
        return ConstNew<uint64_t>(~ConstGetUnsigned(e), bt);
      }
    case UNARY_EXPR_KIND::NEG:
      if (IsSint(bt)) {
        return ConstNew<int64_t>(-ConstGetSigned(e), bt);
      } else if (IsUint(bt)) {
        return ConstNew<uint64_t>(-ConstGetUnsigned(e), bt);
      } else {
        ASSERT(IsFlt(bt), "");
        return ConstNew<double>(-ConstGetFloat(e), bt);
      }
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

template <typename T>
Const Combine(BINARY_EXPR_KIND op, T e1, T e2, BASE_TYPE_KIND bt) {
  switch (op) {
    case BINARY_EXPR_KIND::EQ:
      return ConstNewBool(e1 == e2);
    case BINARY_EXPR_KIND::NE:
      return ConstNewBool(e1 != e2);
    case BINARY_EXPR_KIND::LT:
      return ConstNewBool(e1 < e2);
    case BINARY_EXPR_KIND::LE:
      return ConstNewBool(e1 <= e2);
    case BINARY_EXPR_KIND::GT:
      return ConstNewBool(e1 > e2);
    case BINARY_EXPR_KIND::GE:
      return ConstNewBool(e1 >= e2);
    case BINARY_EXPR_KIND::ADD:
      return ConstNew<T>(e1 + e2, bt);
    case BINARY_EXPR_KIND::SUB:
      return ConstNew<T>(e1 - e2, bt);
    case BINARY_EXPR_KIND::MUL:
      return ConstNew<T>(e1 * e2, bt);
    case BINARY_EXPR_KIND::DIV:
      return ConstNew<T>(e1 / e2, bt);
    case BINARY_EXPR_KIND::MOD:
      return ConstNew<T>(e1 % e2, bt);
    case BINARY_EXPR_KIND::SHL:
      return ConstNew<T>(e1 << e2, bt);
    case BINARY_EXPR_KIND::SHR:
      return ConstNew<T>(e1 >> e2, bt);
    case BINARY_EXPR_KIND::AND:
      return ConstNew<T>(e1 & e2, bt);
    case BINARY_EXPR_KIND::OR:
      return ConstNew<T>(e1 | e2, bt);
    case BINARY_EXPR_KIND::XOR:
      return ConstNew<T>(e1 ^ e2, bt);
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

template <>
Const Combine<bool>(BINARY_EXPR_KIND op, bool e1, bool e2, BASE_TYPE_KIND bt) {
  ASSERT(bt == BASE_TYPE_KIND::BOOL, "");
  switch (op) {
    case BINARY_EXPR_KIND::EQ:
      return ConstNewBool(e1 == e2);
    case BINARY_EXPR_KIND::NE:
      return ConstNewBool(e1 != e2);
    case BINARY_EXPR_KIND::LT:
      return ConstNewBool(e1 < e2);
    case BINARY_EXPR_KIND::LE:
      return ConstNewBool(e1 <= e2);
    case BINARY_EXPR_KIND::GT:
      return ConstNewBool(e1 > e2);
    case BINARY_EXPR_KIND::GE:
      return ConstNewBool(e1 >= e2);
    case BINARY_EXPR_KIND::AND:
      return ConstNewBool(e1 & e2);
    case BINARY_EXPR_KIND::OR:
      return ConstNewBool(e1 | e2);
    case BINARY_EXPR_KIND::XOR:
      return ConstNewBool(e1 ^ e2);
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

template <>
Const Combine<double>(BINARY_EXPR_KIND op, double e1, double e2,
                      BASE_TYPE_KIND bt) {
  switch (op) {
    case BINARY_EXPR_KIND::EQ:
      return ConstNewBool(e1 == e2);
    case BINARY_EXPR_KIND::NE:
      return ConstNewBool(e1 != e2);
    case BINARY_EXPR_KIND::LT:
      return ConstNewBool(e1 < e2);
    case BINARY_EXPR_KIND::LE:
      return ConstNewBool(e1 <= e2);
    case BINARY_EXPR_KIND::GT:
      return ConstNewBool(e1 > e2);
    case BINARY_EXPR_KIND::GE:
      return ConstNewBool(e1 >= e2);
    case BINARY_EXPR_KIND::ADD:
      return ConstNew<double>(e1 + e2, bt);
    case BINARY_EXPR_KIND::SUB:
      return ConstNew<double>(e1 - e2, bt);
    case BINARY_EXPR_KIND::MUL:
      return ConstNew<double>(e1 * e2, bt);
    case BINARY_EXPR_KIND::DIV:
      return ConstNew<double>(e1 / e2, bt);
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

Const EvalExpr2(BINARY_EXPR_KIND op, Const e1, Const e2, CanonType ct,
                CanonType ct_operand) {
  if (CanonType_kind(ct_operand) == NT::TypeFun ||
      CanonType_kind(ct_operand) == NT::TypePtr) {
    if (op == BINARY_EXPR_KIND::EQ) {
      return ConstNewBool(e1 == e2);
    } else if (op == BINARY_EXPR_KIND::NE) {
      return ConstNewBool(e1 != e2);
    } else {
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
    }
  }

  BASE_TYPE_KIND bt = CanonType_get_unwrapped_base_type_kind(ct_operand);
  if (IsSint(bt)) {
    return Combine<int64_t>(op, ConstGetSigned(e1), ConstGetSigned(e2), bt);
  } else if (IsUint(bt)) {
    return Combine<uint64_t>(op, ConstGetUnsigned(e1), ConstGetUnsigned(e2),
                             bt);
  } else if (IsFlt(bt)) {
    return Combine<double>(op, ConstGetFloat(e1), ConstGetFloat(e2), bt);
  } else if (bt == BASE_TYPE_KIND::BOOL) {
    return Combine<bool>(op, ConstGetUnsigned(e1), ConstGetUnsigned(e2), bt);
  } else {
    ASSERT(false, "UNREACHABLE");
    return kConstInvalid;
  }
}

template <typename T>
Const Convert(T val, BASE_TYPE_KIND bt) {
  switch (bt) {
    case BASE_TYPE_KIND::S8:
      return ConstNewS8(int8_t(val));
    case BASE_TYPE_KIND::S16:
      return ConstNewS16(int16_t(val));
    case BASE_TYPE_KIND::S32:
      return ConstNewS32(int32_t(val));
    case BASE_TYPE_KIND::S64:
      return ConstNewS64(int64_t(val));
    case BASE_TYPE_KIND::U8:
      return ConstNewU8(uint8_t(val));
    case BASE_TYPE_KIND::U16:
      return ConstNewU16(uint16_t(val));
    case BASE_TYPE_KIND::U32:
      return ConstNewU32(uint32_t(val));
    case BASE_TYPE_KIND::U64:
      return ConstNewU64(uint64_t(val));
    case BASE_TYPE_KIND::R32:
      return ConstNewR32(float(val));
    case BASE_TYPE_KIND::R64:
      return ConstNewR64(double(val));
    default:
      ASSERT(false, "");
      return kConstInvalid;
  }
}

Const EvalExprIs(Node node) {
  CanonType expr_ct = Node_x_type(Node_expr(node));
  CanonType test_ct = Node_x_type(Node_type(node));
  if (CanonType_get_original_typeid(expr_ct) ==
      CanonType_get_original_typeid(test_ct)) {
    return ConstNewBool(true);
  }

  if (CanonType_kind(expr_ct) == NT::TypeUnion &&
      !CanonType_untagged(expr_ct)) {
    if (CanonType_kind(test_ct) == NT::TypeUnion &&
        !CanonType_untagged(test_ct)) {
      if (TypeListIsSuperSet(CanonType_children(test_ct),
                             CanonType_children(expr_ct))) {
        return ConstNewBool(true);
      }
      return kConstInvalid;
    }
  } else if (CanonType_kind(test_ct) == NT::TypeUnion &&
             !CanonType_untagged(test_ct)) {
    return ConstNewBool(CanonType_tagged_union_contains(test_ct, expr_ct));
  }
  return ConstNewBool(false);
}

Const EvalNode(Node node) {
  // std::cout << "@@@ " << Node_srcloc(node) << " " << node << " "
  //           << Node_name_or_invalid(node) << "\n";
  switch (Node_kind(node)) {
    case NT::Id: {
      Node def = Node_x_symbol(node);
      switch (Node_kind(def)) {
        case NT::DefVar:
        case NT::DefGlobal:
          return Node_x_eval(def);
        case NT::EnumVal:
          return Node_x_eval(Node_value_or_auto(def));
        case NT::DefFun:
          return ConstNewFunAddr(def);
        default:
          return kConstInvalid;
      }
    }
    case NT::ValVoid:
      return ConstNewVoid();
    case NT::ValUndef:
      return ConstNewUndef();
    case NT::ValNum: {
      CanonType ct = Node_x_type(node);
      ASSERT(CanonType_kind(ct) == NT::TypeBase, "");
      Const x = ParseNum(node);
      if (x.isnull()) {
        CompilerError(Node_srcloc(node))
            << "cannot parse " << Node_number(node);
      }
      return x;
    }
    case NT::ValPoint:
      return EvalValWithPossibleImplicitConversion(Node_x_type(node),
                                                   Node_value_or_undef(node));
    case NT::ValCompound:
    case NT::ValString:
      return ConstNewCompound({node, kNodeInvalid});
    case NT::DefVar:
    case NT::DefGlobal: {
      Node initial = Node_initial_or_undef_or_auto(node);
      if (Node_x_eval(initial).isnull() && Node_kind(initial) == NT::ValAuto) {
        AssignValue(initial, GetDefaultForType(Node_x_type(node)));
      }
      if (Node_has_flag(node, BF::MUT)) return kConstInvalid;
      return EvalValWithPossibleImplicitConversion(Node_x_type(node), initial);
    }
    case NT::ExprIndex: {
      Const index_val = Node_x_eval(Node_expr_index(node));
      if (index_val.isnull()) return kConstInvalid;
      Const container_val = Node_x_eval(Node_container(node));
      if (container_val.isnull()) return kConstInvalid;
      return GetValForVecAtPos(container_val, ConstGetUnsigned(index_val),
                               Node_x_type(node));
    }
      return kConstInvalid;

    case NT::ExprField: {
      Const container_val = Node_x_eval(Node_container(node));
      if (container_val.isnull()) return kConstInvalid;
      return GetValForRecAtField(container_val,
                                 Node_x_symbol(Node_field(node)));
    }

      return kConstInvalid;

    case NT::Expr1: {
      Const e = Node_x_eval(Node_expr(node));
      if (e.isnull()) return kConstInvalid;
      return EvalExpr1(Node_unary_expr_kind(node), e, Node_x_type(node));
    }
    case NT::Expr2: {
      Const e1 = Node_x_eval(Node_expr1(node));
      Const e2 = Node_x_eval(Node_expr2(node));

      if (e1.isnull() || e2.isnull()) return kConstInvalid;
      return EvalExpr2(Node_binary_expr_kind(node), e1, e2, Node_x_type(node),
                       Node_x_type(Node_expr1(node)));
    }
    case NT::Expr3:
      if (!Node_x_eval(Node_cond(node)).isnull()) {
        if (ConstGetUnsigned(Node_x_eval(Node_cond(node)))) {
          return Node_x_eval(Node_expr_t(node));
        } else {
          return Node_x_eval(Node_expr_f(node));
        }
      }
      return kConstInvalid;
    case NT::ExprTypeId:
      return ConstNew<uint64_t>(
          CanonType_get_original_typeid(Node_x_type(node)),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ExprAs: {
      Const val = Node_x_eval(Node_expr(node));
      if (val.isnull()) return kConstInvalid;
      BASE_TYPE_KIND bt_target =
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node));
      if (IsSint(val.kind())) {
        return Convert(ConstGetSigned(val), bt_target);
      } else if (IsUint(val.kind())) {
        return Convert(ConstGetUnsigned(val), bt_target);
      } else if (IsFlt(val.kind())) {
        return Convert(ConstGetFloat(val), bt_target);
      } else {
        ASSERT(false, "");
        return kConstInvalid;
      }
    }
    case NT::ExprNarrow:
    case NT::ExprWiden:
    case NT::ExprWrap:
    case NT::ExprUnwrap:
      return Node_x_eval(Node_expr(node));
    case NT::ExprIs:
      return EvalExprIs(node);
    case NT::ExprFront: {
      Node cont = Node_container(node);
      if (CanonType_kind(Node_x_type(cont)) == NT::TypeVec) {
        if (Node_kind(cont) == NT::Id) {
          return ConstNewSymAddr(Node_x_symbol(cont));
        }
      } else {
        ASSERT(CanonType_kind(Node_x_type(cont)) == NT::TypeSpan,
               "unexpected " << Node_x_type(cont));
        Const val_cont = Node_x_eval(cont);
        if (!val_cont.isnull() && !ConstGetSpan(val_cont).pointer.isnull()) {
          return ConstNewSymAddr(ConstGetSpan(val_cont).pointer);
        }
      }
      return kConstInvalid;
    }
    case NT::ExprLen: {
      Node cont = Node_container(node);
      BASE_TYPE_KIND bt =
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node));
      if (CanonType_kind(Node_x_type(cont)) == NT::TypeVec) {
        return ConstNew<uint64_t>(CanonType_dim(Node_x_type(cont)), bt);
      } else {
        Const val_cont = Node_x_eval(cont);
        ASSERT(CanonType_kind(Node_x_type(cont)) == NT::TypeSpan,
               "unexpected " << Node_x_type(cont));
        if (!val_cont.isnull() && ConstGetSpan(val_cont).size != -1) {
          return ConstNew<uint64_t>(ConstGetSpan(val_cont).size, bt);
        }
      }
      return kConstInvalid;
    }
    case NT::ExprAddrOf:
      if (Node_kind(Node_expr_lhs(node)) == NT::Id) {
        return ConstNewSymAddr(Node_x_symbol(Node_expr_lhs(node)));
      }
      return kConstInvalid;
    case NT::ExprOffsetof:
      return ConstNew<uint64_t>(
          Node_x_offset(Node_x_symbol(Node_field(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ExprSizeof:
      return ConstNew<uint64_t>(
          CanonType_size(Node_x_type(Node_type(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ValSpan: {
      Node sym = kNodeInvalid;
      int32_t size = -1;
      Const p = Node_x_eval(Node_pointer(node));
      Const s = Node_x_eval(Node_expr_size(node));
      if (p.isnull() && s.isnull()) return kConstInvalid;
      if (!p.isnull()) {
        ASSERT(p.kind() == CONST_KIND::SYM_ADDR,
               " " << Node_srcloc(node) << " " << p);
        sym = ConstGetSymbol(p);
      }
      if (!s.isnull()) {
        ASSERT(IsUint(s.kind()), Node_srcloc(node) << node);
        size = ConstGetUnsigned(s);
      }
      return ConstNewSpan({sym, size, kConstInvalid});
    }
    case NT::ExprParen:
      return Node_x_eval(Node_expr(node));
    case NT::DefEnum: {
      BASE_TYPE_KIND bt =
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node));
      Const val = kConstInvalid;
      for (Node c = Node_items(node); c.isnull(); c = Node_next(c)) {
        if (Node_x_eval(c).isnull()) break;
        Node v = Node_value_or_auto(c);
        if (Node_kind(v) == NT::ValAuto) {
          if (val.isnull()) {
            val = IsSint(bt) ? ConstNew<int64_t>(0, bt)
                             : ConstNew<uint64_t>(0, bt);
          } else {
            val = IsSint(bt)
                      ? ConstNew<int64_t>(ConstGetSigned(val) + 1, bt)
                      : ConstNew<uint64_t>(ConstGetUnsigned(val) + 1, bt);
          }
        } else {
          val = Node_x_eval(v);
        }
        AssignValue(c, val);
        AssignValue(v, val);
      }
      return kConstInvalid;
    }
    case NT::ExprCall:
    case NT::ExprStmt:
    case NT::ExprUnionUntagged:
    case NT::ExprBitCast:
    case NT::ExprUnionTag:
    case NT::ExprPointer:
      return kConstInvalid;
    case NT::EnumVal:
    case NT::ExprDeref:
    case NT::ValAuto:
      return kConstInvalid;
      // not evaluatable:
    case NT::TypeAuto:
    case NT::TypeBase:
    case NT::TypeFun:
    case NT::TypeOf:
    case NT::TypePtr:
    case NT::TypeSpan:
    case NT::TypeUnion:
    case NT::TypeUnionDelta:
    case NT::TypeVec:
    case NT::DefType:
    case NT::DefRec:
    case NT::RecField:
    case NT::DefMod:
    case NT::ModParam:
      return kConstInvalid;

    case NT::DefFun:
    case NT::FunParam:
    case NT::StmtAssignment:
    case NT::StmtBlock:
    case NT::StmtBreak:
    case NT::StmtCompoundAssignment:
    case NT::StmtCond:
    case NT::Case:
    case NT::StmtContinue:
    case NT::StmtDefer:
    case NT::StmtExpr:
    case NT::StmtIf:
    case NT::StmtReturn:
    case NT::StmtStaticAssert:
    case NT::StmtTrap:
      return kConstInvalid;
    default:
      ASSERT(false, "unexpected eval node: " << EnumToString(Node_kind(node))
                                             << " " << node);
      return kConstInvalid;
  }
}

bool _EvalRecursively(Node mod) {
  bool seen_change = false;
  auto evaluator = [&seen_change](Node node, Node parent) {
    if (!Node_x_eval(node).isnull()) return;
    Const c = EvalNode(node);
    if (!c.isnull()) {
      Node_x_eval(node) = c;
      seen_change = true;
    }
  };

  VisitAstRecursivelyPost(mod, evaluator, kNodeInvalid);
  return seen_change;
}

}  // namespace

template <>
Const ConstNew(uint64_t val, BASE_TYPE_KIND bt) {
  CONST_KIND kind = gBaseTypeToConstType[int(bt)];
  ASSERT(kind != CONST_KIND::INVALID,
         "bad base type kind " << EnumToString(bt));
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, kind);
  }
  switch (kind) {
    case CONST_KIND::U32: {
      uint32_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    case CONST_KIND::U64: {
      uint64_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    default:
      ASSERT(false, "");
      return kConstInvalid;
  }
}

template <>
Const ConstNew<int64_t>(int64_t val, BASE_TYPE_KIND bt) {
  CONST_KIND kind = gBaseTypeToConstType[int(bt)];
  ASSERT(kind != CONST_KIND::INVALID, "");
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, kind);
  }
  switch (kind) {
    case CONST_KIND::S32: {
      int32_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    case CONST_KIND::S64: {
      int64_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    default:
      ASSERT(false, "bad sint " << EnumToString(bt) << " for " << val);
      return kConstInvalid;
  }
}

int64_t ConstGetSigned(Const c) {
  if (c.IsShort()) {
    return ConstShortGetSigned(c);
  }
  if (c.kind() == CONST_KIND::S32) {
    return *(int32_t*)ConstPool.Data(c.index());
  }
  ASSERT(c.kind() == CONST_KIND::S64, "");
  return *(int64_t*)ConstPool.Data(c.index());
}

uint64_t ConstGetUnsigned(Const c) {
  if (c.IsShort()) {
    return ConstShortGetUnsigned(c);
  }
  if (c.kind() == CONST_KIND::U32) {
    return *(uint32_t*)ConstPool.Data(c.index());
  }
  ASSERT(c.kind() == CONST_KIND::U64, "bad size " << int(c.kind()));
  return *(uint64_t*)ConstPool.Data(c.index());
}

double ConstGetFloat(Const c) {
  if (c.kind() == CONST_KIND::R32) {
    return *(float*)ConstPool.Data(c.index());
  } else {
    ASSERT(c.kind() == CONST_KIND::R64, "");
    return *(double*)ConstPool.Data(c.index());
  }
}

std::ostream& operator<<(std::ostream& os, Const c) {
  if (c.isnull()) return os << "EvalNull";
  switch (c.kind()) {
    case CONST_KIND::VOID:
      return os << "EvalVoid";
    case CONST_KIND::U8:
    case CONST_KIND::U16:
    case CONST_KIND::U32:
    case CONST_KIND::U64:
    case CONST_KIND::BOOL:
      return os << "EvalNum(" << int(c.kind()) << ")[" << ConstGetUnsigned(c)
                << "]{" << c.index() << "}";
    case CONST_KIND::S8:
    case CONST_KIND::S16:
    case CONST_KIND::S32:
    case CONST_KIND::S64:
      return os << "EvalNum(" << int(c.kind()) << ")[" << ConstGetSigned(c)
                << "]{" << c.index() << "}";
    case CONST_KIND::R32:
    case CONST_KIND::R64:
      return os << "EvalNum[" << ConstGetFloat(c) << "]{" << c.index() << "}";
    case CONST_KIND::SYM_ADDR:
      return os << "SymAddr[" << Node_name(ConstGetSymbol(c)) << "]{"
                << c.index() << "}";
    case CONST_KIND::FUN_ADDR:
      return os << "FunAdd[" << Node_name(ConstGetSymbol(c)) << "]{"
                << c.index() << "}";
    case CONST_KIND::COMPOUND: {
      EvalCompound ec = ConstGetCompound(c);
      return os << "COMPOUND[" << ec.init_node << ", " << ec.symbol << "]{"
                << c.index() << "}";
    }
    case CONST_KIND::SPAN: {
      EvalSpan es = ConstGetSpan(c);
      return os << "SPAN[" << es.pointer << ", " << es.size << ", "
                << es.content << "]{" << c.index() << "}";
    }
    default:
      ASSERT(false, "unknown eval " << int(c.kind()));
      return os << " unknown eval " << int(c.kind());
  }
}

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods) {
  int iteration = 0;
  while (true) {
    ++iteration;
    if (sw_verbose.Value()) {
      std::cout << "Eval Iteration " << iteration << "\n";
    }
    bool seen_change = false;
    for (Node mod : mods) {
      for (Node node = Node_body_mod(mod); !node.isnull();
           node = Node_next(node)) {
        seen_change |= _EvalRecursively(node);
      }
    }
    if (!seen_change) break;
  }
#if 0
  auto static_assert_checker = [](Node node, Node parent) {
    if (Node_kind(node) == NT::StmtStaticAssert) {
      Node cond = Node_cond(node);
      Const val = Node_x_eval(cond);
      if (val.kind() != CONST_KIND::BOOL || ConstGetUnsigned(val) == 0) {
        if (cond.kind() == NT::Expr2) {
          std::cout << Node_expr1(cond) << " " << Node_x_eval(Node_expr1(cond))
                    << " " << Node_expr2(cond) << " "
                    << Node_x_eval(Node_expr2(cond)) << "\n";
        }

        CompilerError(Node_srcloc(node))
            << "static assert failed " << val << " " << cond;
      }
    }
  };

  for (Node mod : mods) {
    VisitAstRecursivelyPost(mod, static_assert_checker, kNodeInvalid);
  }
#endif
}

}  // namespace cwerg::fe