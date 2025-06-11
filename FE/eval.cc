#include "FE/eval.h"

#include <set>

#include "FE/cwast_gen.h"
#include "FE/symbolize.h"
#include "FE/type_corpus.h"
#include "Util/handle.h"

namespace cwerg::fe {
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
    case NT::ExprParen:
    case NT::DefEnum:
      // TODO
      return kConstInvalid;

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

struct Stripe<ConstCore, Const> gConstCore("ConstCore");

StripeBase* const gAllStripesConst[] = {&gConstCore, nullptr};
struct StripeGroup gStripeGroupConst("Const", gAllStripesConst, 256 * 1024);

Const ConstNewUnsigned(uint64_t val, BASE_TYPE_KIND bt) {
  CONST_KIND kind = gBaseTypeToConstType[int(bt)];
  ASSERT(kind != CONST_KIND::INVALID,
         "bad base type kind " << EnumToString(bt));
  if (ValIsShortConstUnsigned(val)) {
    return ConstNewShortUnsigned(val, kind);
  }
  Const out = ConstNewLong(kind);
  switch (kind) {
    case CONST_KIND::U32:
      ConstGetCore(out).val_u32 = val;
      break;
    case CONST_KIND::U64:
      ConstGetCore(out).val_u64 = val;
      break;
    default:
      ASSERT(false, "");
  }
  return out;
}

Const ConstNewSigned(int64_t val, BASE_TYPE_KIND bt) {
  CONST_KIND kind = gBaseTypeToConstType[int(bt)];
  ASSERT(kind != CONST_KIND::INVALID, "");
  if (ValIsShortConstSigned(val)) {
    return ConstNewShortSigned(val, kind);
  }
  Const out = ConstNewLong(kind);
  switch (kind) {
    case CONST_KIND::S32:
      ConstGetCore(out).val_s32 = val;
      break;
    case CONST_KIND::S64:
      ConstGetCore(out).val_s64 = val;
      break;
    default:
      ASSERT(false, "");
  }
  return out;
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