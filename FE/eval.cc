#include "FE/eval.h"

#include <bit>  // For std::bit_cast
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
ImmutablePoolWithSizeInfo ConstPoolForString(alignof(uint64_t));

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
        BASE_TYPE_KIND_LOWER_FromString(num.substr(num.size() - i, i));
    if (kind != BASE_TYPE_KIND::INVALID) {
      num.remove_suffix(i);
      break;
    }
  }

  if (num[0] == '\'') {
    auto val = ParseChar(num);
    if (!val) return kConstInvalid;
    return ConstNewUnsigned(val.value(), target_kind);
  }

  if (IsSint(target_kind)) {
    auto val = ParseInt<int64_t>(num);
    if (!val) return kConstInvalid;
    int64_t v = val.value();
    if (target_kind == BASE_TYPE_KIND::S8) {
      v = (v << 56) >> 56;
    } else if (target_kind == BASE_TYPE_KIND::S16) {
      v = (v << 48) >> 48;
    } else if (target_kind == BASE_TYPE_KIND::S32) {
      v = (v << 32) >> 32;
    }

    return ConstNewSigned(v, target_kind);
  } else if (IsUint(target_kind)) {
    auto val = ParseInt<uint64_t>(num);
    if (!val) return kConstInvalid;
    return ConstNewUnsigned(val.value(), target_kind);
  }
  ASSERT(IsReal(target_kind), "");
  auto val = ParseFlt64(num);
  if (!val) return kConstInvalid;
  return ConstNewReal(val.value(), target_kind);
}

namespace {

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
    }
    ASSERT(src_value.kind() == BASE_TYPE_KIND::COMPOUND ||
               src_value.kind() == BASE_TYPE_KIND::BYTES,
           "unxpected kind " << int(src_value.kind()));
    Node pointer =
        src_node.kind() == NT::Id ? Node_x_symbol(src_node) : kNodeInvalid;

    return ConstNewSpan({pointer, CanonType_dim(src_type), src_value});
  }
  return src_value;
}

void AssignValue(Node node, Const val) { Node_x_eval(node) = val; }

Const GetDefaultForBaseType(BASE_TYPE_KIND bt) {
  if (IsUint(bt))
    return ConstNewUnsigned(0, bt);
  else if (IsSint(bt))
    return ConstNewSigned(0, bt);
  else if (IsReal(bt))
    return ConstNewReal(0.0, bt);
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
      if (CanonType_is_unwrapped_complex(ct))
        return ConstNewCompoundEmpty();
      else
        return kConstInvalid;
  }
}

Const GetValForVecAtPos(Const container_val, uint64_t index, CanonType ct) {
  if (container_val.kind() == BASE_TYPE_KIND::SPAN) {
    container_val = ConstGetSpan(container_val).content;
    if (container_val.isnull()) return kConstInvalid;
  }
  if (container_val.kind() == BASE_TYPE_KIND::BYTES) {
    std::string_view data = ConstBytesData(container_val);
    ASSERT(CanonType_kind(ct) == NT::TypeBase &&
               CanonType_get_unwrapped_base_type_kind(ct) == BASE_TYPE_KIND::U8,
           "");
    ASSERT(index < data.size(), "");
    return ConstNewU8(data[index]);
  }

  ASSERT(container_val.kind() == BASE_TYPE_KIND::COMPOUND,
         "" << int(container_val.kind()));
  Node init_node = ConstGetCompound(container_val);
  if (init_node.isnull()) {
    return GetDefaultForType(ct);
  }

  size_t dim = CanonType_size(Node_x_type(init_node));
  ASSERT(index < dim, "");
  if (init_node.kind() == NT::ValString) {
    char* buffer = new char[dim];
    size_t size = StringLiteralToBytes(StrData(Node_string(init_node)), buffer);
    CHECK(size != STRING_LITERAL_PARSE_ERROR, "");
    CHECK(index < size, "");
    Const out = ConstNewU8(uint8_t(buffer[index]));
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
  ASSERT(container.kind() == BASE_TYPE_KIND::COMPOUND, "");
  ASSERT(target_field.kind() == NT::RecField, "");
  Node compound = ConstGetCompound(container);
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
        return ConstNewUnsigned(~ConstGetUnsigned(e), bt);
      }
    case UNARY_EXPR_KIND::NEG:
      if (IsSint(bt)) {
        return ConstNewSigned(-ConstGetSigned(e), bt);
      } else if (IsUint(bt)) {
        return ConstNewUnsigned(-ConstGetUnsigned(e), bt);
      } else {
        ASSERT(IsReal(bt), "");
        return ConstNewReal(-ConstGetFloat(e), bt);
      }
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

Const CombineSigned(BINARY_EXPR_KIND op, int64_t e1, int64_t e2,
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
      return ConstNewSigned(e1 + e2, bt);
    case BINARY_EXPR_KIND::SUB:
      return ConstNewSigned(e1 - e2, bt);
    case BINARY_EXPR_KIND::MUL:
      return ConstNewSigned(e1 * e2, bt);
    case BINARY_EXPR_KIND::DIV:
      return ConstNewSigned(e1 / e2, bt);
    case BINARY_EXPR_KIND::MOD:
      return ConstNewSigned(e1 % e2, bt);

    case BINARY_EXPR_KIND::SHL:
      return ConstNewSigned(e1 << e2, bt);
    case BINARY_EXPR_KIND::SHR:
      return ConstNewSigned(e1 >> e2, bt);
      // not supported for signed ints
#if 0
    case BINARY_EXPR_KIND::AND:
      return ConstNewSigned(e1 & e2, bt);
    case BINARY_EXPR_KIND::OR:
      return ConstNewSigned(e1 | e2, bt);
    case BINARY_EXPR_KIND::XOR:
      return ConstNewSigned(e1 ^ e2, bt);
#endif
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

Const CombineUnsigned(BINARY_EXPR_KIND op, uint64_t e1, uint64_t e2,
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
      return ConstNewUnsigned(e1 + e2, bt);
    case BINARY_EXPR_KIND::SUB:
      return ConstNewUnsigned(e1 - e2, bt);
    case BINARY_EXPR_KIND::MUL:
      return ConstNewUnsigned(e1 * e2, bt);
    case BINARY_EXPR_KIND::DIV:
      return ConstNewUnsigned(e1 / e2, bt);
    case BINARY_EXPR_KIND::MOD:
      return ConstNewUnsigned(e1 % e2, bt);
    case BINARY_EXPR_KIND::SHL:
      return ConstNewUnsigned(e1 << e2, bt);
    case BINARY_EXPR_KIND::SHR:
      return ConstNewUnsigned(e1 >> e2, bt);
    case BINARY_EXPR_KIND::AND:
      return ConstNewUnsigned(e1 & e2, bt);
    case BINARY_EXPR_KIND::OR:
      return ConstNewUnsigned(e1 | e2, bt);
    case BINARY_EXPR_KIND::XOR:
      return ConstNewUnsigned(e1 ^ e2, bt);
    default:
      ASSERT(false, "UNREACHABLE");
      return kConstInvalid;
  }
}

Const CombineBool(BINARY_EXPR_KIND op, bool e1, bool e2, BASE_TYPE_KIND bt) {
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

Const CombineReal(BINARY_EXPR_KIND op, double e1, double e2,
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
      return ConstNewReal(e1 + e2, bt);
    case BINARY_EXPR_KIND::SUB:
      return ConstNewReal(e1 - e2, bt);
    case BINARY_EXPR_KIND::MUL:
      return ConstNewReal(e1 * e2, bt);
    case BINARY_EXPR_KIND::DIV:
      return ConstNewReal(e1 / e2, bt);
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
    return CombineSigned(op, ConstGetSigned(e1), ConstGetSigned(e2), bt);
  } else if (IsUint(bt)) {
    return CombineUnsigned(op, ConstGetUnsigned(e1), ConstGetUnsigned(e2), bt);
  } else if (IsReal(bt)) {
    return CombineReal(op, ConstGetFloat(e1), ConstGetFloat(e2), bt);
  } else if (bt == BASE_TYPE_KIND::BOOL) {
    return CombineBool(op, ConstGetUnsigned(e1), ConstGetUnsigned(e2), bt);
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
    }
    return kConstInvalid;
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
      return kConstVoid;
    case NT::ValUndef:
      return kConstUndef;
    case NT::ValNum: {
      ASSERT(CanonType_kind(Node_x_type(node)) == NT::TypeBase, "");
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
      return ConstNewCompound(node);
    case NT::ValString: {
      std::string_view str = StrData(Node_string(node));
      std::string buf(str.size(), 0);
      size_t len = StringLiteralToBytes(str, buf.data());
      buf.resize(len);
      return ConstNewBytes(buf);
    }
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
      return ConstNewUnsigned(
          CanonType_get_original_typeid(Node_x_type(Node_type(node))),
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
      } else if (IsReal(val.kind())) {
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
          return ConstNewSymbolAddr(Node_x_symbol(cont));
        }
      } else {
        ASSERT(CanonType_kind(Node_x_type(cont)) == NT::TypeSpan,
               "unexpected " << Node_x_type(cont));
        Const val_cont = Node_x_eval(cont);
        if (!val_cont.isnull() && !ConstGetSpan(val_cont).pointer.isnull()) {
          return ConstNewSymbolAddr(ConstGetSpan(val_cont).pointer);
        }
      }
      return kConstInvalid;
    }
    case NT::ExprLen: {
      Node cont = Node_container(node);
      BASE_TYPE_KIND bt =
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node));
      if (CanonType_kind(Node_x_type(cont)) == NT::TypeVec) {
        return ConstNewUnsigned(CanonType_dim(Node_x_type(cont)), bt);
      } else {
        Const val_cont = Node_x_eval(cont);
        ASSERT(CanonType_kind(Node_x_type(cont)) == NT::TypeSpan,
               "unexpected " << Node_x_type(cont));
        if (!val_cont.isnull() && ConstGetSpan(val_cont).size != -1) {
          return ConstNewUnsigned(ConstGetSpan(val_cont).size, bt);
        }
      }
      return kConstInvalid;
    }
    case NT::ExprAddrOf:
      if (Node_kind(Node_expr_lhs(node)) == NT::Id) {
        return ConstNewSymbolAddr(Node_x_symbol(Node_expr_lhs(node)));
      }
      return kConstInvalid;
    case NT::ExprOffsetof:
      return ConstNewUnsigned(
          Node_x_offset(Node_x_symbol(Node_field(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ExprSizeof:
      return ConstNewUnsigned(
          CanonType_size(Node_x_type(Node_type(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ValSpan: {
      Node sym = kNodeInvalid;
      SizeOrDim size = kSizeOrDimInvalid;
      Const p = Node_x_eval(Node_pointer(node));
      Const s = Node_x_eval(Node_expr_size(node));
      if (p.isnull() && s.isnull()) return kConstInvalid;
      if (!p.isnull()) {
        ASSERT(p.kind() == BASE_TYPE_KIND::VAR_ADDR ||
                   p.kind() == BASE_TYPE_KIND::GLOBAL_ADDR,
               " " << Node_srcloc(node) << " " << p);
        sym = ConstGetSymbolAddr(p);
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
      for (Node c = Node_items(node); !c.isnull(); c = Node_next(c)) {
        if (!Node_x_eval(c).isnull()) break;
        Node v = Node_value_or_auto(c);
        if (v.kind() == NT::ValAuto) {
          if (val.isnull()) {
            val = IsSint(bt) ? ConstNewSigned(0, bt) : ConstNewUnsigned(0, bt);
          } else {
            val = IsSint(bt) ? ConstNewSigned(ConstGetSigned(val) + 1, bt)
                             : ConstNewUnsigned(ConstGetUnsigned(val) + 1, bt);
          }
          AssignValue(v, val);
        } else {
          val = Node_x_eval(v);
        }
        ASSERT(!val.isnull(), "bad val for ");
        AssignValue(c, val);
      }
      return kConstInvalid;
    }
    case NT::ExprBitCast: {
      Const val = Node_x_eval(Node_expr(node));
      if (val.isnull()) return kConstInvalid;
      if (val.kind() == BASE_TYPE_KIND::VAR_ADDR ||
          val.kind() == BASE_TYPE_KIND::GLOBAL_ADDR) {
        return val;
      }
      CanonType dst_ct = Node_x_type(node);
      uint64_t data = ConstGetBitcastUnsigned(val);
      auto tmp =
          ConstNewBitcastUnsigned(data, CanonType_base_type_kind(dst_ct));
      uint64_t data2 = ConstGetBitcastUnsigned(tmp);
      ASSERT(data == data2, std::hex << data << " " << data2 << " " << dst_ct);
      return ConstNewBitcastUnsigned(data, CanonType_base_type_kind(dst_ct));
    }
    case NT::ExprCall:
    case NT::ExprStmt:
    case NT::ExprUnionUntagged:
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

Const ConstNewUnsigned(uint64_t val, BASE_TYPE_KIND kind) {
  ASSERT(IsUint(kind), "bad base type kind " << EnumToString(kind));
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, kind);
  }
  switch (kind) {
    case BASE_TYPE_KIND::U32: {
      uint32_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    case BASE_TYPE_KIND::U64: {
      uint64_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    default:
      ASSERT(false, "");
      return kConstInvalid;
  }
}

Const ConstNewSigned(int64_t val, BASE_TYPE_KIND kind) {
  ASSERT(IsSint(kind), "");
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, kind);
  }
  switch (kind) {
    case BASE_TYPE_KIND::S32: {
      int32_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    case BASE_TYPE_KIND::S64: {
      int64_t v = val;
      return Const(ConstPool.Intern(std::string_view((char*)&v, sizeof(v))),
                   kind);
    }
    default:
      ASSERT(false, "bad sint " << EnumToString(kind) << " for " << val);
      return kConstInvalid;
  }
}

int64_t ConstGetSigned(Const c) {
  if (c.IsShort()) {
    return ConstShortGetSigned(c);
  }
  if (c.kind() == BASE_TYPE_KIND::S32) {
    return *(int32_t*)ConstPool.Data(c.index());
  }
  ASSERT(c.kind() == BASE_TYPE_KIND::S64, "");
  return *(int64_t*)ConstPool.Data(c.index());
}

uint64_t ConstGetUnsigned(Const c) {
  if (c.IsShort()) {
    return ConstShortGetUnsigned(c);
  }
  if (c.kind() == BASE_TYPE_KIND::U32) {
    return *(uint32_t*)ConstPool.Data(c.index());
  }
  ASSERT(c.kind() == BASE_TYPE_KIND::U64, "bad size " << int(c.kind()));
  return *(uint64_t*)ConstPool.Data(c.index());
}

uint64_t ConstGetBitcastUnsigned(Const c) {
  switch (c.kind()) {
    case BASE_TYPE_KIND::U8:
    case BASE_TYPE_KIND::U16:
    case BASE_TYPE_KIND::U32:
    case BASE_TYPE_KIND::U64:
    case BASE_TYPE_KIND::BOOL:
      return ConstGetUnsigned(c);
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
      return ConstGetSigned(c);
    case BASE_TYPE_KIND::R32:
      return std::bit_cast<uint32_t, float>(float(ConstGetFloat(c)));
    case BASE_TYPE_KIND::R64:
      return std::bit_cast<uint64_t, double>(ConstGetFloat(c));
    default:
      ASSERT(false, "bad Const kind " << EnumToString(c.kind()));
      return 0;
  }
}

Const ConstNewBitcastUnsigned(uint64_t val, BASE_TYPE_KIND bt) {
  switch (bt) {
    case BASE_TYPE_KIND::U8:
    case BASE_TYPE_KIND::U16:
    case BASE_TYPE_KIND::U32:
    case BASE_TYPE_KIND::U64:
    case BASE_TYPE_KIND::BOOL:
      return ConstNewUnsigned(val, bt);
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
      return ConstNewUnsigned(int64_t(val), bt);
    case BASE_TYPE_KIND::R32:
      return ConstNewReal(std::bit_cast<float, uint32_t>(uint32_t(val)), bt);
    case BASE_TYPE_KIND::R64:
      return ConstNewReal(std::bit_cast<double, uint64_t>(val), bt);

    default:
      ASSERT(false, "bad Const kind " << EnumToString(bt));
      return kConstInvalid;
  }
}

double ConstGetFloat(Const c) {
  if (c.kind() == BASE_TYPE_KIND::R32) {
    return *(float*)ConstPool.Data(c.index());
  } else {
    ASSERT(c.kind() == BASE_TYPE_KIND::R64, "");
    return *(double*)ConstPool.Data(c.index());
  }
}

std::ostream& operator<<(std::ostream& os, Const c) {
  if (c.isnull()) return os << "EvalNull";
  switch (c.kind()) {
    case BASE_TYPE_KIND::VOID:
      return os << "EvalVoid";
    case BASE_TYPE_KIND::UNDEF:
      return os << "EvalUndef";
    case BASE_TYPE_KIND::U8:
    case BASE_TYPE_KIND::U16:
    case BASE_TYPE_KIND::U32:
    case BASE_TYPE_KIND::U64:
    case BASE_TYPE_KIND::BOOL:
      return os << "EvalNum[" << ConstGetUnsigned(c) << "_"
                << EnumToString_BASE_TYPE_KIND_LOWER(c.kind()) << "]";
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
      return os << "EvalNum[" << ConstGetSigned(c) << "_"
                << EnumToString_BASE_TYPE_KIND_LOWER(c.kind()) << "]";
    case BASE_TYPE_KIND::R32:
    case BASE_TYPE_KIND::R64:
      // we want %e format
      return os << "EvalNum[" << std::scientific << ConstGetFloat(c) << "_"
                << EnumToString_BASE_TYPE_KIND_LOWER(c.kind()) << "]";
    case BASE_TYPE_KIND::VAR_ADDR:
      return os << "EvalVarAddr[" << Node_name(ConstGetVarAddr(c)) << "]";
    case BASE_TYPE_KIND::GLOBAL_ADDR:
      return os << "EvalGlobalAddr[" << Node_name(ConstGetGlobalAddr(c)) << "]";
    case BASE_TYPE_KIND::FUN_ADDR:
      return os << "EvalFunAddr[" << Node_name(ConstGetFunAddr(c)) << "]";
    case BASE_TYPE_KIND::COMPOUND: {
      Node ec = ConstGetCompound(c);
      return os << "EvalCompound[" << ec << "]";
    }
    case BASE_TYPE_KIND::SPAN: {
      EvalSpan es = ConstGetSpan(c);
      return os << "EvalSpan[" << es.pointer << ", " << es.size << ", "
                << es.content << "]{" << c.index() << "}";
    }
    default:
      ASSERT(false, "unknown eval " << int(c.kind()));
      return os << " unknown eval " << int(c.kind());
  }
}

std::string to_string(Const c, const std::map<Node, std::string>* labels) {
  if (c.isnull()) return "null";

  std::stringstream ss;
  switch (c.kind()) {
    case BASE_TYPE_KIND::VOID:
    case BASE_TYPE_KIND::UNDEF:
    case BASE_TYPE_KIND::U8:
    case BASE_TYPE_KIND::U16:
    case BASE_TYPE_KIND::U32:
    case BASE_TYPE_KIND::U64:
    case BASE_TYPE_KIND::BOOL:
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
    case BASE_TYPE_KIND::R32:
    case BASE_TYPE_KIND::R64:
      ss << c;
      break;
    case BASE_TYPE_KIND::VAR_ADDR:
      if (labels->contains(ConstGetVarAddr(c))) {
        ss << "EvalVarAddr[" << labels->at(ConstGetVarAddr(c)) << "]";
      } else {
        ss << "EvalVarAddr[DANGLING:" << Node_name(ConstGetVarAddr(c)) << "]";
      }
      break;
    case BASE_TYPE_KIND::GLOBAL_ADDR:
      if (labels->contains(ConstGetGlobalAddr(c))) {
        ss << "EvalGlobalAddr[" << labels->at(ConstGetGlobalAddr(c)) << "]";
      } else {
        ss << "EvalGlobalAddr[DANGLING:" << Node_name(ConstGetGlobalAddr(c))
           << "]";
      }
      break;
    case BASE_TYPE_KIND::FUN_ADDR:
      ss << "EvalFunAddr[" << labels->at(ConstGetFunAddr(c)) << "]";
      break;
    case BASE_TYPE_KIND::BYTES: {
      std::string_view str = ConstBytesData(c);

      std::string buf(str.size() * 4,
                      0);  // worst case is every byte become \xXX
      size_t length = BytesToEscapedString(str, buf.data());
      buf.resize(length);
      ss << "EvalBytes[" << buf << "]";
      break;
    }
    case BASE_TYPE_KIND::COMPOUND: {
      Node ec = ConstGetCompound(c);
      ss << "EvalCompound[";
      if (!ec.isnull()) {
        ss << labels->at(ec);
      }
      ss << "]";
      break;
    }
    case BASE_TYPE_KIND::SPAN: {
      EvalSpan es = ConstGetSpan(c);
      ss << "EvalSpan[";
      if (es.pointer.isnull()) {
        ss << "null";
      } else {
        ss << labels->at(es.pointer);
      }
      ss << ", " << es.size << ", ";
      ss << to_string(es.content, labels);

      ss << "]";
      break;
    }
    default:
      ASSERT(false, "unknown eval " << int(c.kind()));
      break;
  }
  return ss.str();
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

  auto static_assert_checker = [](Node node, Node parent) {
    if (Node_kind(node) == NT::StmtStaticAssert) {
      Node cond = Node_cond(node);
      Const val = Node_x_eval(cond);
      if (val.kind() != BASE_TYPE_KIND::BOOL || ConstGetUnsigned(val) == 0) {
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
}

CONSTANT_KIND AddressConstKind(Node node) {
  switch (node.kind()) {
    case NT::Id: {
      Node def = Node_x_symbol(node);
      if (def.kind() == NT::DefGlobal) {
        return CONSTANT_KIND::WITH_GLOBAL_ADDRESS;
      } else
        return CONSTANT_KIND::NOT;
    }
    case NT::ExprIndex:
      if (Node_expr_index(node).kind() != NT::ValNum) {
        return CONSTANT_KIND::NOT;
      }
      return AddressConstKind(Node_container(node));

    default:
      return CONSTANT_KIND::NOT;
  }
}

CONSTANT_KIND ValueConstKind(Node node) {
  switch (node.kind()) {
    case NT::ValString:
    case NT::ValVoid:
    case NT::ValUndef:
    case NT::ValNum:
      return CONSTANT_KIND::PURE;
    case NT::ExprAddrOf:
      return AddressConstKind(Node_expr_lhs(node));
    case NT::ExprFront:
      return AddressConstKind(Node_container(node));
    case NT::ValSpan:
      if (Node_expr_index(node).kind() != NT::ValNum) {
        return CONSTANT_KIND::NOT;
      }
      return ValueConstKind(Node_pointer(node));
    case NT::ValCompound: {
      CONSTANT_KIND out = CONSTANT_KIND::PURE;
      const bool is_vec = CanonType_is_vec(Node_x_type(node));
      for (Node point = Node_inits(node); !point.isnull();
           point = Node_next(point)) {
        if (is_vec) {
          Node p = Node_point_or_undef(point);
          if (p.kind() != NT::ValNum && p.kind() != NT::ValUndef) {
            return CONSTANT_KIND::NOT;
          }
          switch (ValueConstKind(Node_value_or_undef(point))) {
            case CONSTANT_KIND::NOT:
              return CONSTANT_KIND::NOT;
            case CONSTANT_KIND::WITH_GLOBAL_ADDRESS:
              out = CONSTANT_KIND::WITH_GLOBAL_ADDRESS;
            case CONSTANT_KIND::PURE:
              break;
          }
        }
      }
      return out;
    }
    default:
      return CONSTANT_KIND::NOT;
  }
}

Node GlobalConstantPool::add_def_global(Node node) {
  ++current_no_;
  const SrcLoc& sl = Node_srcloc(node);
  CanonType ct = Node_x_type(node);
  ASSERT(!ct.isnull(), "");
  Node out = NodeNew(NT::DefGlobal);
  NodeInitDefGlobal(out, NameNew("global_val_", current_no_),
                    MakeTypeAuto(ct, sl), node, Mask(BF::PUB), kStrInvalid, sl,
                    ct);
  all_globals_.push_back(out);
  return out;
}

Node GlobalConstantPool::add_val_string(Node node) {
  ASSERT(node.kind() == NT::ValString, "");
  Const eval = Node_x_eval(node);
  ASSERT(eval.kind() == BASE_TYPE_KIND::BYTES, "");
  Node def_node = GetWithDefault(val_string_pool_, eval.index(), kNodeInvalid);
  if (def_node.isnull()) {
    def_node = add_def_global(node);
    val_string_pool_[eval.index()] = def_node;
  } else {
    NodeFreeRecursively(node);
  }
  return def_node;
}

void GlobalConstantPool::EliminateValStringAndValCompoundOutsideOfDefGlobal(
    Node node) {
  auto replacer = [this](Node node, Node parent) {
    if (parent.kind() == NT::DefGlobal) return node;
    switch (node.kind()) {
      case NT::ValString: {
        const SrcLoc& sl = Node_srcloc(node);
        // add_val_string may delete node
        return IdNodeFromDef(add_val_string(node), sl);
      }
      case NT::ValCompound: {
        if (CanonType_is_vec(Node_x_type(node)) &&
            parent.kind() != NT::DefVar &&
            ValueConstKind(node) != CONSTANT_KIND::NOT) {
          return IdNodeFromDef(add_def_global(node), Node_srcloc(node));
        } else {
          return node;
        }
      }
      default:
        return node;
    }
  };
  MaybeReplaceAstRecursively(node, replacer);
}

}  // namespace cwerg::fe