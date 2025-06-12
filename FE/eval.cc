#include "FE/eval.h"

#include <set>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"
#include "FE/type_corpus.h"
#include "Util/handle.h"
#include "Util/immutable.h"

namespace cwerg::fe {

ImmutablePool ConstPool(alignof(uint64_t));

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

Const EvalNode(Node node) {
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
    case NT::ValNum:
    case NT::ValPoint:
      // TODO
      return kConstInvalid;
    case NT::ValCompound:
      return ConstNewCompound(node);
    case NT::ValString:
    case NT::DefVar:
    case NT::DefGlobal:
    case NT::ExprIndex:
    case NT::ExprField:
    case NT::Expr1:
    case NT::Expr2:
    case NT::Expr3:
      // TODO
      return kConstInvalid;
    case NT::ExprTypeId:
      return ConstNewUnsigned(
          CanonType_get_original_typeid(Node_x_type(node)),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ExprAs:
    case NT::ExprNarrow:
    case NT::ExprWiden:
    case NT::ExprWrap:
    case NT::ExprUnwrap:
      // TODO
      return kConstInvalid;
    case NT::ExprIs:
      // TODO
      return kConstInvalid;

    case NT::ExprFront:
    case NT::ExprLen:
      // TODO
      return kConstInvalid;
    case NT::ExprAddrOf:
      if (Node_kind(Node_expr_lhs(node)) == NT::Id) {
        return ConstNewSymAddr(Node_x_symbol(Node_expr_lhs(node)));
      }
      return kConstInvalid;
    case NT::ExprOffsetof:
      return ConstNewUnsigned(
          CanonType_size(Node_x_type(Node_type(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ExprSizeof:
      return ConstNewUnsigned(
          Node_x_offset(Node_x_symbol(Node_field(node))),
          CanonType_get_unwrapped_base_type_kind(Node_x_type(node)));
    case NT::ValSpan:
      // TODO
      return kConstInvalid;
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
            val = IsSint(bt) ? ConstNewSigned(0, bt) : ConstNewUnsigned(0, bt);
          } else {
            val = IsSint(bt) ? ConstNewSigned(ConstGetSigned(val) + 1, bt)
                             : ConstNewUnsigned(ConstGetUnsigned(val) + 1, bt);
          }
        } else {
          val = Node_x_eval(v);
        }
        Node_x_eval(c) = val;
        Node_x_eval(v) = val;
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

Const ConstNewUnsigned(uint64_t val, BASE_TYPE_KIND bt) {
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

Const ConstNewSigned(int64_t val, BASE_TYPE_KIND bt) {
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
      ASSERT(false, "");
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
  ASSERT(c.kind() == CONST_KIND::U64, "");
  return *(uint64_t*)ConstPool.Data(c.index());
}

void DecorateASTWithPartialEvaluation(const std::vector<Node>& mods) {
  int iteration = 0;
  while (true) {
    ++iteration;
    std::cout << "Eval Iteration " << iteration << "\n";
    bool seen_change = false;
    for (Node mod : mods) {
      for (Node node = Node_body_mod(mod); !node.isnull();
           node = Node_next(node)) {
        seen_change |= _EvalRecursively(node);
      }
    }
    if (!seen_change) break;
  }
}

}  // namespace cwerg::fe