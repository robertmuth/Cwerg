#include "FE/emit_ir.h"

#include <span>
#include <tuple>

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/symbolize.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::fe {

std::ostream& operator<<(std::ostream& os, DK dk) {
  os << EnumToString(dk);
  return os;
}

std::string_view DO_NOT_USE = "@DO_NOT_USE@";

//
class IterateValVec {
 public:
  IterateValVec(Node point, SizeOrDim dim, const SrcLoc& sl)
      : next_point_(point), dim_(dim), sl_(sl) {}

  Node next() {
    if (next_point_.isnull()) {
      ASSERT(curr_index_ < dim_, "");

      if (curr_index_ < dim_) {
        ++curr_index_;
        return kNodeInvalid;
      }
    }
    if (Node_point_or_undef(next_point_).kind() == NT::ValUndef) {
      ++curr_index_;
      Node out = next_point_;
      next_point_ = Node_next(next_point_);
      return out;
    }
    SizeOrDim target_index =
        ConstGetUnsigned(Node_x_eval(Node_point_or_undef(next_point_)));
    if (curr_index_ < target_index) {
      ++curr_index_;
      return kNodeInvalid;
    }
    ++curr_index_;
    Node out = next_point_;
    next_point_ = Node_next(next_point_);
    return out;
  }

 private:
  Node next_point_;
  SizeOrDim dim_;
  SizeOrDim curr_index_ = 0;
  const SrcLoc& sl_;
};

enum class STORAGE_KIND {
  INVALID,
  REGISTER,
  STACK,
  DATA,
};

bool IsDefOnStack(Node node) {
  if (Node_has_flag(node, BF::REF)) return true;
  return CanonType_ir_regs(Node_x_type(node)) == DK::MEM;
}

STORAGE_KIND StorageKindForId(Node node) {
  ASSERT(node.kind() == NT::Id, "");
  Node def_node = Node_x_symbol(node);
  switch (def_node.kind()) {
    case NT::DefGlobal:
      return STORAGE_KIND::DATA;
    case NT::FunParam:
      return STORAGE_KIND::REGISTER;
    case NT::DefVar:
      return IsDefOnStack(def_node) ? STORAGE_KIND::STACK
                                    : STORAGE_KIND::REGISTER;
    default:
      UNREACHABLE("bad node type " << def_node);
      return STORAGE_KIND::INVALID;
  }
}

void FunMachineTypes(CanonType ct, std::vector<std::string>* res_types,
                     std::vector<std::string>* arg_types) {
  ASSERT(CanonType_is_fun(ct), "");

  std::span<CanonType> children = CanonType_children(ct);
  DK rt = CanonType_ir_regs(children[children.size() - 1]);
  if (rt != DK::NONE) {
    res_types->push_back(EnumToString(rt));
  }

  for (CanonType at_ct : children.subspan(0, children.size() - 1)) {
    DK at = CanonType_ir_regs(at_ct);
    ASSERT(at != DK::NONE && at != DK::MEM, "");
    arg_types->push_back(EnumToString(at));
  }
}

std::string MakeFunSigName(CanonType ct) {
  std::vector<std::string> res_types;
  std::vector<std::string> arg_types;
  FunMachineTypes(ct, &res_types, &arg_types);
  if (res_types.empty()) res_types.push_back("void");
  if (arg_types.empty()) arg_types.push_back("void");

  std::string sig_name = "$sig";
  std::string sep = "/";
  for (const std::string& rt : res_types) {
    sig_name += sep;
    sig_name += rt;
    sep = "_";
  }
  for (const std::string& rt : arg_types) {
    sig_name += sep;
    sig_name += rt;
    sep = "_";
  }
  return sig_name;
}

void EmitFunctionHeader(std::string_view sig_name, std::string_view kind,
                        CanonType ct) {
  std::vector<std::string> res_types;
  std::vector<std::string> arg_types;
  FunMachineTypes(ct, &res_types, &arg_types);
  std::cout << "\n\n.fun " << sig_name << " " << kind << " [";
  std::string sep = "";
  for (const std::string& rt : res_types) {
    std::cout << sep << rt;
    sep = " ";
  }
  std::cout << "] = [";
  sep = "";
  for (const std::string& rt : arg_types) {
    std::cout << sep << rt;
    sep = " ";
  }
  std::cout << "]\n";
}

constexpr std::string_view kTAB("  ");

void EmitFunctionProlog(Node node, IdGenIR* id_gen) {
  std::cout << ".bbl " << id_gen->NameNewNext(NameNew("entry")) << "\n";
  for (Node p = Node_params(node); !p.isnull(); p = Node_next(p)) {
    std::string new_name = id_gen->NameNewNext(Node_name(p));
    Node_name(p) = NameNew(new_name);
    std::cout << kTAB << "poparg " << new_name << ":"
              << CanonType_ir_regs(Node_x_type(p)) << "\n";
  }
}

// forward decls
std::string EmitExpr(Node node, const TargetArchConfig& ta, IdGenIR* id_gen);

struct BaseOffset {
  std::string base;
  SizeOrDim offset = 0;

  BaseOffset AddScaledOffset(Node offset_expr, SizeOrDim scale,
                             const TargetArchConfig& ta, IdGenIR* id_gen) {
    if (offset_expr.kind() == NT::ValNum) {
      // TODO is this safe?
      Const val = Node_x_eval(offset_expr);
      if (IsSint(val.kind())) {
        return {base, SizeOrDim(offset + scale * ConstGetSigned(val))};
      } else {
        ASSERT(IsUint(val.kind()), "");
        return {base, SizeOrDim(offset + scale * ConstGetUnsigned(val))};
      }
    }
    std::string offset = EmitExpr(offset_expr, ta, id_gen);
    if (scale != 1) {
      std::string scaled = id_gen->NameNewNext(NameNew("scaled"));
      std::cout << kTAB << "conv " << scaled << ":" << ta.get_sint_kind_ir()
                << " = " << offset << "\n";
      std::cout << kTAB << "mul " << scaled << " = " << scaled << " " << scale
                << "\n";
      offset = scaled;
    }
    std::string new_base = id_gen->NameNewNext(NameNew("new_base"));
    std::cout << kTAB << "lea " << new_base << ":" << ta.get_data_addr_kind_ir()
              << " = " << base << " " << offset << "\n";
    return {new_base, 0};
  }

  BaseOffset AddOffset(SizeOrDim offset) const {
    return {base, this->offset + offset};
  }

  std::string MaterializeBase(const TargetArchConfig& ta,
                              IdGenIR* id_gen) const {
    if (offset == 0) return base;
    std::string out = id_gen->NameNewNext(NameNew("at"));
    std::cout << kTAB << "lea " << out << ":" << ta.get_data_addr_kind_ir()
              << " = " << base << " " << offset << "\n";
    return out;
  }
};

std::ostream& operator<<(std::ostream& os, const BaseOffset& bo) {
  os << "BaseOffset(" << bo.base << ", " << bo.offset << ")";
  return os;
}

struct ReturnResultLocation {
  std::string dst_reg;
  BaseOffset dst_mem;
  std::string end_label;
};

std::ostream& operator<<(std::ostream& os, const ReturnResultLocation& rrl) {
  os << "ReturnResultLocation(" << rrl.dst_reg << ", " << rrl.dst_mem << ", "
     << rrl.end_label << ")";
  return os;
}


// forward decls
void EmitConditional(Node node, bool invert, std::string_view label_f,
                     const TargetArchConfig& ta, IdGenIR* id_gen);

void EmitExprToMemory(Node node, const BaseOffset& dst,
                      const TargetArchConfig& ta, IdGenIR* id_gen);

SizeOrDim EmitInitializerRecursively(Node node, CanonType ct, SizeOrDim offset,
                                     const TargetArchConfig& ta);
void EmitStmt(Node node, const ReturnResultLocation& result,
              const TargetArchConfig& ta, IdGenIR* id_gen);

std::string_view GetSuffixForStorage(STORAGE_KIND kind) {
  switch (kind) {
    case STORAGE_KIND::STACK:
      return "stk";
    case STORAGE_KIND::DATA:
      return "mem";
    default:
      UNREACHABLE("bad storage kind " << int(kind));
      return "";
  }
}

BaseOffset GetLValueAddress(Node node, const TargetArchConfig& ta,
                            IdGenIR* id_gen) {
  switch (node.kind()) {
    case NT::ExprDeref:
      return {EmitExpr(Node_expr(node), ta, id_gen)};
    case NT::ExprField: {
      BaseOffset base = GetLValueAddress(Node_container(node), ta, id_gen);
      return base.AddOffset(Node_x_offset(Node_x_symbol(Node_field(node))));
    }
    case NT::Id: {
      Name name = Node_name(Node_x_symbol(node));
      std::string base = id_gen->NameNewNext(NameNew("lhsaddr"));
      std::cout << kTAB << "lea." << GetSuffixForStorage(StorageKindForId(node))
                << " " << base << ":" << ta.get_data_addr_kind_ir() << " = "
                << name << " 0\n";
      return {base};
    }

    case NT::ExprNarrow:
      return GetLValueAddress(Node_expr(node), ta, id_gen);
    case NT::ExprStmt: {
      CanonType ct = Node_x_type(node);
      std::string name = id_gen->NameNewNext(NameNew("expr_stk_var"));
      std::cout << kTAB << ".stk " << name << " " << CanonType_size(ct) << " "
                << CanonType_alignment(ct) << "\n";
      std::string base = id_gen->NameNewNext(NameNew("stmt_stk_base"));
      std::cout << kTAB << "lea.stk " << base << ":"
                << ta.get_data_addr_kind_ir() << " " << name << " 0\n";
      EmitExprToMemory(node, BaseOffset(base), ta, id_gen);
      return {base};
    }
    default:
      UNREACHABLE("");
      return {""};
  }
}

std::string EmitId(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  CanonType ct = Node_x_type(node);
  if (CanonType_size(ct) == 0) {
    return "@_BAD_DO_NOT_USE@";
  }
  Node def_node = Node_x_symbol(node);
  switch (def_node.kind()) {
    case NT::DefGlobal: {
      std::string out = id_gen->NameNewNext(NameNew("globread"));
      std::cout << kTAB << "ld.mem " << out << ":" << CanonType_ir_regs(ct)
                << " = " << NameData(Node_name(def_node)) << " 0\n";
      return out;
    }
    case NT::FunParam:
      return NameData(Node_name(def_node));
    case NT::DefFun: {
      std::string out = id_gen->NameNewNext(NameNew("funaddr"));
      std::cout << kTAB << "lea.fun " << out << ":" << CanonType_ir_regs(ct)
                << " = " << NameData(Node_name(def_node)) << "\n";
      return out;
    }
    case NT::DefVar:
      if (IsDefOnStack(node)) {
        std::string out = id_gen->NameNewNext(NameNew("stkread"));
        std::cout << kTAB << "ld.stk " << out << ":" << CanonType_ir_regs(ct)
                  << " = " << NameData(Node_name(def_node)) << " 0\n";
        return out;
      } else {
        return NameData(Node_name(def_node));
      }
    default:
      ASSERT(false, "unexpected node " << node);
      return "";
  }
}

std::string FormatNumber(Node node) {
  std::string out;
  CanonType ct = Node_x_type(node);
  Const val = Node_x_eval(node);
  switch (val.kind()) {
    case BASE_TYPE_KIND::BOOL:
    case BASE_TYPE_KIND::U8:
    case BASE_TYPE_KIND::U16:
    case BASE_TYPE_KIND::U32:
    case BASE_TYPE_KIND::U64:
      out = std::to_string(ConstGetUnsigned(val));

      break;
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
      out = std::to_string(ConstGetSigned(val));
      break;
    case BASE_TYPE_KIND::R32:
    case BASE_TYPE_KIND::R64:
      out = std::to_string(ConstGetFloat(val));
      break;
    default:
      ASSERT(false, "UNREACHABLE");
      break;
  }
  out += ":";
  out += EnumToString(CanonType_ir_regs(ct));
  return out;
}

void EmitZero(BaseOffset dst, SizeOrDim length, SizeOrDim alignment,
              IdGenIR* id_gen) {
  SizeOrDim width = alignment;
  SizeOrDim curr = 0;
  while (curr < length) {
    while (width > length - curr) width >>= 1;
    std::cout << kTAB << "st " << dst.base << " " << dst.offset + curr
              << " = 0:U" << width * 8 << "\n";
    curr += width;
  }
}

void EmitCopy(BaseOffset dst, BaseOffset src, SizeOrDim length,
              SizeOrDim alignment, IdGenIR* id_gen) {
  SizeOrDim width = alignment;
  SizeOrDim curr = 0;
  while (curr < length) {
    while (width > length - curr) width >>= 1;
    std::string tmp = id_gen->NameNewNext(NameNew("copy"));
    std::cout << kTAB << ".reg U" << width * 8 << " [" << tmp << "]\n";
    while (curr + width <= length) {
      std::cout << kTAB << "ld " << tmp << " = " << src.base << " "
                << src.offset + curr << "\n";
      std::cout << kTAB << "st " << dst.base << " " << dst.offset + curr
                << " = " << tmp << "\n";
      curr += width;
    }
  }
}

void EmitValCompoundRecToMemory(Node val, const BaseOffset& dst,
                                const TargetArchConfig& ta, IdGenIR* id_gen) {
  CanonType ct = Node_x_type(val);
  if (Node_inits(val).isnull()) {
    EmitZero(dst, CanonType_size(ct), CanonType_alignment(ct), id_gen);
  }

  IterateValRec it(Node_inits(val), Node_fields(CanonType_ast_node(ct)));
  for (Node point = it.next(); !it.curr_field.isnull(); point = it.next()) {
    CanonType field_ct = Node_x_type(it.curr_field);
    BaseOffset bo = dst.AddOffset(Node_x_offset(it.curr_field));
    if (point.isnull()) {
      EmitZero(bo, CanonType_size(field_ct), CanonType_alignment(field_ct),
               id_gen);
    } else if (Node_value_or_undef(point).kind() != NT::ValUndef) {
      EmitExprToMemory(Node_value_or_undef(point), bo, ta, id_gen);
    }
  }
}

void EmitValCompoundVecToMemory(Node val, BaseOffset dst,
                                const TargetArchConfig& ta, IdGenIR* id_gen) {
  CanonType ct = Node_x_type(val);
  SizeOrDim dim = CanonType_vec_dim(ct);
  SizeOrDim element_size = CanonType_size(ct) / dim;
  SizeOrDim alignment = CanonType_alignment(ct);
  Node last = kNodeInvalid;

  IterateValVec it(Node_inits(val), dim, Node_srcloc(val));
  for (SizeOrDim i = 0; i < dim; ++i) {
    Node point = it.next();
    if (!point.isnull()) {
      last = Node_value_or_undef(point);
    }
    if (last.isnull()) {
      EmitZero(dst, element_size, alignment, id_gen);
    } else if (last.kind() != NT::ValUndef) {
      EmitExprToMemory(last, dst, ta, id_gen);
    }
    dst = dst.AddOffset(element_size);
  }
}

void EmitExprToMemory(Node node, const BaseOffset& dst,
                      const TargetArchConfig& ta, IdGenIR* id_gen) {
  switch (node.kind()) {
    case NT::ExprCall:
    case NT::ValNum:
    case NT::ExprAddrOf:
    case NT::ExprAs:
    case NT::Expr1:
    case NT::Expr2:
    case NT::ExprBitCast:
    case NT::ExprPointer:
    case NT::ExprFront: {
      std::string op = EmitExpr(node, ta, id_gen);
      std::cout << kTAB << "st " << dst.base << " " << dst.offset << " = " << op
                << "\n";
      break;
    }
    case NT::ExprNarrow: {
      CanonType ct = Node_x_type(node);
      if (CanonType_size(ct) != 0) {
        BaseOffset src = GetLValueAddress(node, ta, id_gen);
        EmitCopy(dst, src, CanonType_size(ct), CanonType_alignment(ct), id_gen);
      }
      break;
    }
    //
    case NT::ExprWrap:
    case NT::ExprUnwrap:
      return EmitExprToMemory(Node_expr(node), dst, ta, id_gen);
    case NT::ExprWiden:
      if (CanonType_size(Node_x_type(node)) != 0) {
        return EmitExprToMemory(Node_expr(node), dst, ta, id_gen);
      }
    case NT::Id:
      if (StorageKindForId(node) == STORAGE_KIND::REGISTER) {
        std::string res = EmitId(node, ta, id_gen);
        std::cout << kTAB << "st " << dst.base << " " << dst.offset << " = "
                  << res << "\n";
        break;
      }
    // FALLTHROUGH
    case NT::ExprField:
    case NT::ExprDeref: {
      CanonType ct = Node_x_type(node);
      BaseOffset src = GetLValueAddress(node, ta, id_gen);
      EmitCopy(dst, src, CanonType_size(ct), CanonType_alignment(ct), id_gen);
      break;
    }
    case NT::ExprStmt: {
      std::string end_label = id_gen->NameNewNext(NameNew("end_expr"));
      ReturnResultLocation rrl("", dst, end_label);
      for (Node s = Node_body(node); !s.isnull(); s = Node_next(s)) {
        EmitStmt(s, rrl, ta, id_gen);
      }
      std::cout << ".bbl " << end_label << "\n";
      break;
    }
    case NT::ValCompound: {
      CanonType ct = Node_x_type(node);
      if (CanonType_is_rec(ct)) {
        EmitValCompoundRecToMemory(node, dst, ta, id_gen);
      } else {
        ASSERT(CanonType_is_vec(ct), "");
        EmitValCompoundVecToMemory(node, dst, ta, id_gen);
      }
      break;
    }
    default:
      break;
  }
}

uint64_t AllBitsSet(uint64_t n) {
  if (n == 64) return ~uint64_t(0);
  return (1 << n) - 1;
}

std::string EmitExpr1(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  CanonType ct = Node_x_type(node);
  std::string op = EmitExpr(Node_expr(node), ta, id_gen);
  std::string res = id_gen->NameNewNext(NameNew("expr1"));
  switch (Node_unary_expr_kind(node)) {
    case UNARY_EXPR_KIND::NEG: {
      auto ff =
          AllBitsSet(8 * BaseTypeKindByteSize(CanonType_base_type_kind(ct)));
      std::cout << kTAB << "sub " << res << ":" << CanonType_ir_regs(ct)
                << " = 0x" << std::hex << ff << " " << op << "\n";
      break;
    }
    case UNARY_EXPR_KIND::NOT: {
      std::cout << kTAB << "xor " << res << ":" << CanonType_ir_regs(ct)
                << " = 0 " << op << "\n";
      break;
    }
    case UNARY_EXPR_KIND::ABS:
      std::cout << kTAB << "sub " << res << ":" << CanonType_ir_regs(ct)
                << " = 0 " << op << "\n";
      std::cout << kTAB << "cmplt " << res << " = " << res << " " << op << " "
                << op << " 0\n";
      break;
    case UNARY_EXPR_KIND::SQRT:
      std::cout << kTAB << "sqrt " << res << ":" << CanonType_ir_regs(ct)
                << " = " << op << "\n";
      break;
    default:
      UNREACHABLE("");
      break;
  }
  return res;
}

std::string EmitExpr2(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  std::string op1 = EmitExpr(Node_expr1(node), ta, id_gen);
  std::string op2 = EmitExpr(Node_expr2(node), ta, id_gen);
  std::string res = id_gen->NameNewNext(NameNew("expr2"));
  DK res_dk = CanonType_ir_regs(Node_x_type(node));

  auto emit_simple = [&op1, &op2, &res, &res_dk](std::string_view operation) {
    std::cout << kTAB << operation << res << ":" << res_dk << " = " << op1
              << " " << op2 << "\n";
  };
  switch (Node_binary_expr_kind(node)) {
    case BINARY_EXPR_KIND::ADD:
      emit_simple("add ");
      break;
    case BINARY_EXPR_KIND::SUB:
      emit_simple("sub ");
      break;
    case BINARY_EXPR_KIND::MUL:
      emit_simple("mul ");
      break;
    case BINARY_EXPR_KIND::DIV:
      emit_simple("div ");
      break;
    case BINARY_EXPR_KIND::MOD:
      emit_simple("rem ");
      break;
    case BINARY_EXPR_KIND::AND:
      emit_simple("and ");
      break;
    case BINARY_EXPR_KIND::OR:
      emit_simple("or ");
      break;
    case BINARY_EXPR_KIND::XOR:
      emit_simple("xor ");
      break;
    case BINARY_EXPR_KIND::SHL:
      emit_simple("shl ");
      break;
    case BINARY_EXPR_KIND::SHR:
      emit_simple("shr ");
      break;

    case BINARY_EXPR_KIND::MAX:
      std::cout << kTAB << "cmplt " << res << ":" << res_dk << " = " << op1
                << " " << op2 << " " << op2 << " " << op1 << "\n";
      break;
    case BINARY_EXPR_KIND::MIN:
      std::cout << kTAB << "cmplt " << res << ":" << res_dk << " = " << op1
                << " " << op2 << " " << op1 << " " << op2 << "\n";
      break;
    case BINARY_EXPR_KIND::PDELTA: {
      std::string conv_op1 = id_gen->NameNewNext(NameNew("pdelta1"));
      std::string conv_op2 = id_gen->NameNewNext(NameNew("pdelta2"));
      std::cout << kTAB << "bitcast " << conv_op1 << ":" << res_dk << " = "
                << op1 << "\n";
      std::cout << kTAB << "bitcast " << conv_op2 << ":" << res_dk << " = "
                << op2 << "\n";
      std::cout << kTAB << "sub " << res << ":" << res_dk << " = " << conv_op1
                << " " << conv_op2 << "\n";
      SizeOrDim width = CanonType_aligned_size(
          CanonType_underlying_type(Node_x_type(Node_expr1(node))));
      std::cout << kTAB << "div " << res << " = " << res << " " << width
                << "\n";
      break;
    }
    default:
      UNREACHABLE("");
      break;
  }
  return res;
}

std::string EmitExprCall(Node node, const TargetArchConfig& ta,
                         IdGenIR* id_gen) {
  Node callee = Node_callee(node);
  CanonType fun_ct = Node_x_type(callee);
  std::vector<std::string> arg_ops;
  for (Node arg = Node_args(node); !arg.isnull(); arg = Node_next(arg)) {
    arg_ops.push_back(EmitExpr(arg, ta, id_gen));
  }
  for (auto it = arg_ops.rbegin(); it != arg_ops.rend(); ++it) {
    std::cout << kTAB << "pusharg " << *it << "\n";
  }
  if (callee.kind() == NT::Id && Node_x_symbol(callee).kind() == NT::DefFun) {
    std::cout << kTAB << "bsr " << NameData(Node_name(Node_x_symbol(callee)))
              << "\n";
  } else {
    std::string op = EmitExpr(callee, ta, id_gen);
    std::cout << kTAB << "jsr " << op << " " << MakeFunSigName(fun_ct) << "\n";
  }
  CanonType res_ct = CanonType_result_type(fun_ct);
  if (CanonType_size(res_ct) == 0) {
    return "@DO_NOT_USE@";
  }
  std::string out = id_gen->NameNewNext(NameNew("call"));
  std::cout << kTAB << "poparg " << out << ":" << CanonType_ir_regs(res_ct)
            << "\n";
  return out;
}

std::string EmitExpr(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  // CanonType ct = Node_x_type(node);
  switch (node.kind()) {
    case NT::ExprCall:
      return EmitExprCall(node, ta, id_gen);
    case NT::ValNum:
      return FormatNumber(node);
    case NT::Id:
      return EmitId(node, ta, id_gen);
    case NT::ExprAddrOf:
      return GetLValueAddress(Node_expr_lhs(node), ta, id_gen)
          .MaterializeBase(ta, id_gen);
    case NT::Expr1:
      return EmitExpr1(node, ta, id_gen);
    case NT::Expr2:
      return EmitExpr2(node, ta, id_gen);
    case NT::ExprPointer: {
      ASSERT(Node_pointer_expr_kind(node) == POINTER_EXPR_KIND::INCP, "");
      SizeOrDim width = CanonType_aligned_size(
          CanonType_underlying_type(Node_x_type(Node_expr1(node))));
      BaseOffset bo(EmitExpr(Node_expr1(node), ta, id_gen));
      return bo.AddScaledOffset(Node_expr2(node), width, ta, id_gen)
          .MaterializeBase(ta, id_gen);
    }
    case NT::ExprAs: {
      CanonType ct_dst = CanonType_get_unwrapped(Node_x_type(node));
      CanonType ct_src = CanonType_get_unwrapped(Node_x_type(Node_expr(node)));
      if (CanonType_is_base_type(ct_dst) && CanonType_is_base_type(ct_src)) {
        std::string src = EmitExpr(Node_expr(node), ta, id_gen);
        std::string res = id_gen->NameNewNext(NameNew("as"));
        std::cout << kTAB << "conv " << res << ":" << CanonType_ir_regs(ct_dst)
                  << " = " << src << "\n";
        return res;
      } else if (CanonType_is_ptr(ct_dst) && CanonType_is_ptr(ct_src)) {
        return EmitExpr(Node_expr(node), ta, id_gen);
      } else {
        UNREACHABLE("");
        return std::string(DO_NOT_USE);
      }
    }

    case NT::ExprUnwrap:
    case NT::ExprWrap:
      return EmitExpr(Node_expr(node), ta, id_gen);
    case NT::ExprDeref: {
      CanonType ct = Node_x_type(node);
      if (CanonType_size(ct) == 0) {
        return std::string(DO_NOT_USE);
      } else {
        std::string addr = EmitExpr(Node_expr(node), ta, id_gen);
        std::string res = id_gen->NameNewNext(NameNew("deref"));
        std::cout << kTAB << "ld " << res << ":" << CanonType_ir_regs(ct)
                  << " = " << addr << " 0\n";
        return res;
      }
    }
    case NT::ExprStmt: {
      CanonType ct = Node_x_type(node);
      ReturnResultLocation rrl;

      if (CanonType_size(ct) == 0) {
        rrl.dst_reg = std::string(DO_NOT_USE);
      } else {
        rrl.dst_reg = id_gen->NameNewNext(NameNew("expr"));
        std::cout << kTAB << ".reg " << CanonType_ir_regs(ct) << " ["
                  << rrl.dst_reg << "]\n";
      }
      rrl.end_label = id_gen->NameNewNext(NameNew("end_expr"));
      for (Node s = Node_body(node); !s.isnull(); s = Node_next(s)) {
        EmitStmt(s, rrl, ta, id_gen);
      }

      std::cout << ".bbl " << rrl.end_label << "\n";
      return rrl.dst_reg;
    }
    case NT::ExprFront:
      return GetLValueAddress(Node_container(node), ta, id_gen)
          .MaterializeBase(ta, id_gen);
    case NT::ExprField: {
      CanonType ct = Node_x_type(node);
      Node rec_field = Node_x_symbol(Node_field(node));
      std::string addr = GetLValueAddress(Node_container(node), ta, id_gen)
                             .MaterializeBase(ta, id_gen);
      if (CanonType_size(ct) == 0) {
        return std::string(DO_NOT_USE);
      }
      std::string res = id_gen->NameNewNext(Node_name(rec_field));
      std::cout << kTAB << "ld " << res << ":" << CanonType_ir_regs(ct) << " = "
                << addr << " " << Node_x_offset(rec_field) << "\n";
      return res;
    }

    default:
      return "";
  }
}

BINARY_EXPR_KIND InvertBranch(BINARY_EXPR_KIND kind) {
  switch (kind) {
    case BINARY_EXPR_KIND::EQ:
      return BINARY_EXPR_KIND::NE;
    case BINARY_EXPR_KIND::NE:
      return BINARY_EXPR_KIND::EQ;
    case BINARY_EXPR_KIND::LT:
      return BINARY_EXPR_KIND::GE;
    case BINARY_EXPR_KIND::LE:
      return BINARY_EXPR_KIND::GT;
    case BINARY_EXPR_KIND::GT:
      return BINARY_EXPR_KIND::LE;
    case BINARY_EXPR_KIND::GE:
      return BINARY_EXPR_KIND::LT;
    default:
      CHECK(false, "UNREACHABLE");
      return BINARY_EXPR_KIND::INVALID;
  }
}

std::tuple<std::string_view, bool> GetBranchOpcode(BINARY_EXPR_KIND kind,
                                                   bool invert) {
  bool swap = false;
  if (invert) {
    kind = InvertBranch(kind);
  }
  if (kind == BINARY_EXPR_KIND::GT) {
    kind = BINARY_EXPR_KIND::LT;
    swap = true;
  } else if (kind == BINARY_EXPR_KIND::GE) {
    kind = BINARY_EXPR_KIND::LE;
    swap = true;
  }

  switch (kind) {
    case BINARY_EXPR_KIND::EQ:
      return std::make_tuple("beq", swap);
    case BINARY_EXPR_KIND::NE:
      return std::make_tuple("bne", swap);
    case BINARY_EXPR_KIND::LT:
      return std::make_tuple("blt", swap);
    case BINARY_EXPR_KIND::LE:
      return std::make_tuple("ble", swap);
    default:
      CHECK(false, "UNREACHABLE");
      return std::make_tuple("@bad@", false);
  }
}

void EmitConditionalExpr2(Node cond, bool invert, std::string_view label_f,
                          const TargetArchConfig& ta, IdGenIR* id_gen) {
  switch (Node_binary_expr_kind(cond)) {
    case BINARY_EXPR_KIND::ANDSC:
      if (invert) {
        EmitConditional(Node_expr1(cond), true, label_f, ta, id_gen);
        EmitConditional(Node_expr2(cond), true, label_f, ta, id_gen);
      } else {
        std::string failed = id_gen->NameNewNext(NameNew("br_failed_and"));
        EmitConditional(Node_expr1(cond), true, failed, ta, id_gen);
        EmitConditional(Node_expr2(cond), false, label_f, ta, id_gen);
        std::cout << ".bbl " << failed << "\n";
      }
      break;
    case BINARY_EXPR_KIND::ORSC:
      if (invert) {
        std::string failed = id_gen->NameNewNext(NameNew("br_failed_or"));
        EmitConditional(Node_expr1(cond), false, failed, ta, id_gen);
        EmitConditional(Node_expr2(cond), true, label_f, ta, id_gen);
        std::cout << ".bbl " << failed << "\n";
      } else {
        EmitConditional(Node_expr1(cond), false, label_f, ta, id_gen);
        EmitConditional(Node_expr2(cond), false, label_f, ta, id_gen);
      }
      break;
    case BINARY_EXPR_KIND::XOR:
    case BINARY_EXPR_KIND::AND:
    case BINARY_EXPR_KIND::OR: {
      std::string op = EmitExpr(cond, ta, id_gen);
      std::cout << kTAB << (invert ? "beq " : "bne ") << op << " 0 " << label_f
                << "\n";
      break;
    }
    default: {
      std::string op1 = EmitExpr(Node_expr1(cond), ta, id_gen);
      std::string op2 = EmitExpr(Node_expr2(cond), ta, id_gen);
      auto const [branch, swap] =
          GetBranchOpcode(Node_binary_expr_kind(cond), invert);
      if (swap) {
        std::swap(op1, op2);
      }
      std::cout << kTAB << branch << " " << op1 << " " << op2 << " " << label_f
                << "\n";
      break;
    }
  }
}

void EmitConditional(Node node, bool invert, std::string_view label_f,
                     const TargetArchConfig& ta, IdGenIR* id_gen) {
  if (Node_x_eval(node) != kConstInvalid) {
    if (ConstGetUnsigned(Node_x_eval(node)) != invert) {
      std::cout << kTAB << ".bra " << label_f << "\n";
    }
    return;
  }

  switch (node.kind()) {
    case NT::Expr1:
      ASSERT(Node_unary_expr_kind(node) == UNARY_EXPR_KIND::NOT, "");
      EmitConditional(Node_expr(node), !invert, label_f, ta, id_gen);
      break;
    case NT::Expr2:
      EmitConditionalExpr2(node, invert, label_f, ta, id_gen);
      break;
    case NT::ExprCall:
    case NT::ExprStmt:
    case NT::ExprField:
    case NT::ExprDeref: {
      std::string op = EmitExpr(Node_expr(node), ta, id_gen);
      std::cout << kTAB << (invert ? "beq " : "bne ") << op << " 0 " << label_f
                << "\n";
      break;
    }
    case NT::Id: {
      std::string op = EmitId(node, ta, id_gen);
      std::cout << kTAB << (invert ? "beq " : "bne ") << op << " 0 " << label_f
                << "\n";
      break;
    }
    default:
      ASSERT(false, "NYI");
      break;
  }
}

bool ChangesControlFlow(Node node) {
  switch (node.kind()) {
    case NT::StmtBreak:
    case NT::StmtContinue:
    case NT::StmtReturn:
      return true;
    default:
      return false;
  }
}

void EmitStmt(Node node, const ReturnResultLocation& rrl,
              const TargetArchConfig& ta, IdGenIR* id_gen) {
  switch (node.kind()) {
    case NT::DefVar: {
      std::string name = id_gen->NameNewNext(Node_name(node));
      Node_name(node) = NameNew(name);
      CanonType ct = Node_x_type(node);
      Node init = Node_initial_or_undef_or_auto(node);
      if (CanonType_size(ct) == 0) {
        if (init.kind() != NT::ValUndef) {
          EmitExpr(init, ta, id_gen);
        }
      } else if (IsDefOnStack(node)) {
        std::cout << kTAB << ".stk " << NameData(Node_name(node)) << " "
                  << CanonType_alignment(ct) << " " << CanonType_size(ct)
                  << "\n";
        if (init.kind() != NT::ValUndef) {
          std::string base = id_gen->NameNewNext(NameNew("var_stk_base"));
          std::cout << kTAB << "lea.stk " << base << ":"
                    << ta.get_data_addr_kind_ir() << " "
                    << NameData(Node_name(node)) << " 0\n";
          EmitExprToMemory(init, BaseOffset(base), ta, id_gen);
        }
      } else {
        if (init.kind() == NT::ValUndef) {
          std::cout << kTAB << ".reg " << CanonType_ir_regs(ct) << " " << name
                    << "\n";
        } else {
          std::string out = EmitExpr(init, ta, id_gen);
          std::cout << kTAB << "mov " << name << ":" << CanonType_ir_regs(ct)
                    << " = " << out << "\n";
        }
      }
      break;
    }
    case NT::StmtBlock: {
      Name name = Node_label(node);
      if (name.isnull()) {
        name = NameNew("_");
      }
      Node_name(node) = NameNew(id_gen->NameNewNext(name));
      std::cout << ".bbl " << NameData(Node_label(node)) << "\n";
      for (Node s = Node_body(node); !s.isnull(); s = Node_next(s)) {
        EmitStmt(s, rrl, ta, id_gen);
      }
      std::cout << ".bbl " << NameData(Node_name(node)) << ".end" << "\n";
      break;
    }
    case NT::StmtReturn:
      if (Node_x_target(node).kind() == NT::ExprStmt) {
        Node ret = Node_expr_ret(node);
        if (CanonType_size(Node_x_type(ret)) != 0) {
          if (!rrl.dst_reg.empty()) {
            std::string op = EmitExpr(ret, ta, id_gen);
            std::cout << kTAB << "mov " << rrl.dst_reg << " = " << op
                      << "\n";
          } else {
            EmitExprToMemory(ret, rrl.dst_mem, ta, id_gen);
          }
        } else {
          EmitExpr(ret, ta, id_gen);
        }
        std::cout << kTAB << "bra " << rrl.end_label << "\n";
      } else {
        Node ret = Node_expr_ret(node);
        std::string out = EmitExpr(ret, ta, id_gen);
        if (CanonType_size(Node_x_type(ret)) != 0) {
          std::cout << kTAB << "pusharg " << out << "\n";
        }
        std::cout << kTAB << "ret\n";
      }
      break;
    case NT::StmtBreak:
      std::cout << kTAB << ".bra " << NameData(Node_label(Node_x_target(node)))
                << ".end  # break\n";
      break;
    case NT::StmtContinue:
      std::cout << kTAB << ".bra " << NameData(Node_label(Node_x_target(node)))
                << "  # break\n";
      break;
    case NT::StmtExpr: {
      CanonType ct = Node_x_type(Node_expr(node));
      if (CanonType_ir_regs(ct) != DK::MEM) {
        EmitExpr(Node_expr(node), ta, id_gen);
      } else {
        std::string name = id_gen->NameNewNext(NameNew("stmt_stk_var"));
        std::cout << kTAB << ".stk " << name << " " << CanonType_alignment(ct)
                  << " " << CanonType_size(ct) << "\n";
        std::string name_addr =
            id_gen->NameNewNext(NameNew("stmt_stk_var_addr"));
        std::cout << kTAB << "lea.stk " << name_addr << ":" << name << " 0\n";
        EmitExpr(Node_expr(node), ta, id_gen);
        EmitExprToMemory(Node_expr(node), BaseOffset(name_addr, 0), ta, id_gen);
      }
      break;
    }
    case NT::StmtIf: {
      std::string label_join = id_gen->NameNewNext(NameNew("br_join"));
      if (!Node_body_t(node).isnull() && !Node_body_f(node).isnull()) {
        std::string label_f = id_gen->NameNewNext(NameNew("br_f"));
        EmitConditional(Node_cond(node), true, label_f, ta, id_gen);
        Node last_s = kNodeInvalid;
        for (Node s = Node_body_t(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, rrl, ta, id_gen);
          last_s = s;
        }
        if (!ChangesControlFlow(last_s)) {
          std::cout << kTAB << ".bra " << label_join << "\n";
        }

        std::cout << ".bbl " << label_f << "\n";
        for (Node s = Node_body_f(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, rrl, ta, id_gen);
        }
      } else if (!Node_body_t(node).isnull()) {
        EmitConditional(Node_cond(node), true, label_join, ta, id_gen);
        for (Node s = Node_body_t(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, rrl, ta, id_gen);
        }
      } else {
        EmitConditional(Node_cond(node), false, label_join, ta, id_gen);
        for (Node s = Node_body_f(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, rrl, ta, id_gen);
        }
      }
      std::cout << ".bbl " << label_join << "\n";
      break;
    }
    case NT::StmtAssignment: {
      Node lhs = Node_lhs(node);
      if (lhs.kind() == NT::Id &&
          StorageKindForId(lhs) == STORAGE_KIND::REGISTER) {
        std::string op = EmitExpr(Node_expr_rhs(node), ta, id_gen);
        std::cout << kTAB << "mov " << NameData(Node_name(Node_x_symbol(lhs)))
                  << " = " << op << "\n";
      } else {
        BaseOffset bo = GetLValueAddress(lhs, ta, id_gen);
        EmitExprToMemory(Node_expr_rhs(node), bo, ta, id_gen);
      }
      break;
    }
    case NT::StmtTrap:
      std::cout << kTAB << "trap\n";
      break;

    default:
      break;
  }
}

void EmitDefFun(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  if (!Node_has_flag(node, BF::EXTERN)) {
    EmitFunctionHeader(NameData(Node_name(node)), "NORMAL", Node_x_type(node));
    EmitFunctionProlog(node, id_gen);
    for (Node s = Node_body(node); !s.isnull(); s = Node_next(s)) {
      EmitStmt(s, ReturnResultLocation(), ta, id_gen);
    }
  }
}

bool is_repeated_single_char(std::string_view data) {
  auto first_char = data[0];
  for (auto c : data) {
    if (c != first_char) {
      return false;
    }
  }
  return true;
}

class RLE {
 public:
  RLE(std::string_view data) : data_(data) {}

  struct Run {
    uint8_t byte;
    size_t length;
  };

  Run next() {
    if (data_.empty()) return {0, 0};
    uint8_t current_byte = data_[0];
    for (size_t i = 1; i < data_.size(); ++i) {
      if (uint8_t(data_[i]) != current_byte) {
        data_ = data_.substr(i);
        return {current_byte, i};
      }
    }
    auto out = data_;
    data_ = "";
    return {current_byte, out.size()};
  }

 private:
  std::string_view data_;
};

uint32_t EmitMemRepeatedByte(uint8_t data, SizeOrDim count, SizeOrDim offset,
                             std::string_view purpose,
                             std::string_view purpose2 = "") {
  std::cout << ".data ";
  std::cout << count << " [" << int(data) << "]";
  std::cout << " # " << offset << " " << count << " " << purpose << purpose2
            << "\n";
  return count;
}

uint32_t EmitMem(std::string_view data, SizeOrDim offset,
                 std::string_view comment) {
  if (data.size() == 0) {
    std::cout << ".data ";
    std::cout << " 0 []";
    std::cout << " # " << offset << " 0 " << comment << "\n";
  } else if (is_repeated_single_char(data)) {
    return EmitMemRepeatedByte(data[0], data.size(), offset, comment);
  } else {
    if (data.size() < 100) {
      std::string buf(data.size() * 4,
                      0);  // worst case is every byte become \xXX
      size_t length = BytesToEscapedString(data, buf.data());
      buf.resize(length);
      std::cout << ".data ";
      std::cout << 1 << " \"" << buf << "\"";
      std::cout << " # " << offset << " " << data.size() << " " << comment
                << "\n";

    } else {
      RLE rle(data);
      std::string sep = "";
      auto run = rle.next();
      while (run.length != 0) {
        std::cout << ".data " << run.length << " [" << int(run.byte) << "]";
        std::cout << " # " << offset << " " << run.length << " " << comment
                  << "\n";
        offset += run.length;
        run = rle.next();
      }
    }
  }

  return data.size();
}

const uint8_t BYTE_ZERO = '\0';
const uint8_t BYTE_UNDEF = '\0';
const uint8_t BYTE_PADDING = 'o';  // intentionally not zero?

SizeOrDim EmitInitializerVec(Node node, CanonType ct, SizeOrDim offset,
                             const TargetArchConfig& ta) {
  if (node.kind() == NT::ValAuto) {
    return EmitMemRepeatedByte(BYTE_ZERO, CanonType_size(ct), offset, "auto ",
                               NameData(CanonType_name(ct)));
  }

  if (node.kind() == NT::ValString) {
    Const val = Node_x_eval(node);
    return EmitMem(ConstBytesData(val), offset, NameData(CanonType_name(ct)));
  }

  ASSERT(node.kind() == NT::ValCompound, "");
  SizeOrDim dim = CanonType_vec_dim(ct);
  CanonType et = CanonType_get_unwrapped(CanonType_underlying_type(ct));
  if (CanonType_kind(et) == NT::TypeBase) {
    IterateValVec iv(Node_inits(node), dim, Node_srcloc(node));
    std::string buf;
    buf.reserve(CanonType_size(ct));

    std::string last = ConstBaseTypeSerialize(
        GetDefaultForBaseType(CanonType_base_type_kind(et)));
    for (SizeOrDim i = 0; i < dim; ++i) {
      Node point = iv.next();
      if (!point.isnull()) {
        if (Node_value_or_undef(point).kind() == NT::ValUndef) {
          last = std::string(CanonType_size(et), BYTE_UNDEF);
        } else {
          last = ConstBaseTypeSerialize(Node_x_eval(point));
        }
      }

      buf += last;
    }
    return EmitMem(buf, offset, NameData(CanonType_name(ct)));
  }
  std::cout << "# vec: " << NameData(CanonType_name(ct)) << "\n";
  Node last = Node(NT::ValUndef, 666);  // hack
  IterateValVec iv(Node_inits(node), dim, Node_srcloc(node));
  SizeOrDim stride = CanonType_size(ct) / dim;
  for (SizeOrDim i = 0; i < dim; ++i) {
    Node point = iv.next();
    if (!point.isnull()) {
      last = Node_value_or_undef(point);
    }
    SizeOrDim count =
        EmitInitializerRecursively(last, et, offset + i * stride, ta);
    if (count != stride) {
      EmitMemRepeatedByte(BYTE_PADDING, stride - count, offset + stride - count,
                          "padding");
    }
  }

  return CanonType_size(ct);
}

SizeOrDim EmitInitializerRec(Node node, CanonType ct, SizeOrDim offset,
                             const TargetArchConfig& ta) {
  std::cout << "# rec: " << NameData(CanonType_name(ct)) << "\n";
  if (node.kind() == NT::ValAuto) {
    return EmitMemRepeatedByte(BYTE_ZERO, CanonType_size(ct), offset, "auto");
  }
  ASSERT(node.kind() == NT::ValCompound, "");
  auto it =
      IterateValRec(Node_inits(node), Node_fields(CanonType_ast_node(ct)));
  SizeOrDim reloff = 0;
  while (true) {
    Node point = it.next();
    Node field = it.curr_field;
    CanonType field_ct = Node_x_type(field);

    if (field.isnull()) {
      ASSERT(reloff == CanonType_size(ct), "");
      return reloff;
    }

    if (Node_x_offset(field) > reloff) {
      reloff += EmitMemRepeatedByte(BYTE_PADDING, Node_x_offset(field) - reloff,
                                    offset + reloff, "padding");
    }

    Node val = point.isnull() ? kNodeInvalid : Node_value_or_undef(point);
    if (val.isnull()) {
      reloff += EmitMemRepeatedByte(BYTE_ZERO, CanonType_size(field_ct),
                                    offset + reloff,
                                    NameData(CanonType_name(field_ct)));
    } else {
      reloff += EmitInitializerRecursively(val, field_ct, offset + reloff, ta);
    }
  }
}

SizeOrDim EmitDataAddress(Node node, SizeOrDim offset,
                          const TargetArchConfig& ta) {
  ASSERT(node.kind() == NT::Id, "");
  Name name = Node_name(Node_x_symbol(node));
  std::cout << ".addr.mem " << ta.data_addr_bitwidth / 8 << " "
            << NameData(name) << " " << 0 << "\n";
  return ta.data_addr_bitwidth / 8;
}

SizeOrDim EmitCodeAddress(Node node, SizeOrDim offset,
                          const TargetArchConfig& ta) {
  ASSERT(node.kind() == NT::DefFun, "");
  std::cout << ".addr.fun " << ta.code_addr_bitwidth / 8 << " "
            << NameData(Node_name(node)) << "\n";
  return ta.code_addr_bitwidth / 8;
}

SizeOrDim EmitInitializerRecursively(Node node, CanonType ct, SizeOrDim offset,
                                     const TargetArchConfig& ta) {
  if (CanonType_size(ct) == 0) {
    return 0;
  }
  ASSERT(offset == align(offset, CanonType_alignment(ct)), "");
  switch (node.kind()) {
    case NT::ValUndef:
      return EmitMemRepeatedByte(BYTE_UNDEF, CanonType_size(ct), offset,
                                 "undef ", NameData(CanonType_name(ct)));
    case NT::Id: {
      Node sym = Node_x_symbol(node);
      if (sym.kind() == NT::DefFun) {
        return EmitCodeAddress(sym, offset, ta);
      }
      ASSERT(sym.kind() == NT::DefGlobal, "");
      return EmitInitializerRecursively(Node_initial_or_undef_or_auto(sym), ct,
                                        offset, ta);
    }
    case NT::ExprFront:
      return EmitDataAddress(Node_container(node), offset, ta);
    case NT::ExprAddrOf:
      return EmitDataAddress(Node_expr_lhs(node), offset, ta);
    case NT::ExprWiden: {
      uint32_t target = CanonType_size(ct);
      uint32_t count = EmitInitializerRecursively(
          Node_expr(node), Node_x_type(Node_expr(node)), offset, ta);
      if (count != target) {
        EmitMemRepeatedByte(BYTE_PADDING, target - count, offset + count,
                            "widen_padding");
      }
      return target;
    }
    case NT::ValNum:
      return EmitMem(ConstBaseTypeSerialize(Node_x_eval(node)), offset,
                     NameData(CanonType_name(ct)));

    default:
      break;
  }
  switch (CanonType_kind(ct)) {
    case NT::DefType:
      return EmitInitializerRecursively(
          Node_expr(node), Node_x_type(Node_expr(node)), offset, ta);
    case NT::TypeVec:
      return EmitInitializerVec(node, ct, offset, ta);
    case NT::DefRec:
      return EmitInitializerRec(node, ct, offset, ta);
    default:
      break;
  }

  return 0;
}

uint32_t EmitDefGlobal(Node node, const TargetArchConfig& ta) {
  CanonType def_type = Node_x_type(Node_type_or_auto(node));
  if (CanonType_is_void(CanonType_get_unwrapped(def_type))) {
    return 0;
  }
  std::cout << "\n.mem " << Node_name(node) << " "
            << CanonType_alignment(def_type) << " "
            << (Node_has_flag(node, BF::MUT) ? "RW" : "RO") << "\n";
  return EmitInitializerRecursively(Node_initial_or_undef_or_auto(node),
                                    def_type, 0, ta);
}

}  // namespace cwerg::fe