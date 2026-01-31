#include "FE/emit_ir.h"

#include <span>

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/symbolize.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"
#include "Util/parse.h"

namespace cwerg::fe {

//
class IterateValVec {
 public:
  IterateValVec(Node point, SizeOrDim dim, const SrcLoc& sl)
      : point_(point), dim_(dim), sl_(sl) {}

  Node next() {
    if (point_.isnull()) {
      ASSERT(curr_index_ < dim_, "");

      if (curr_index_ < dim_) {
        ++curr_index_;
        return kNodeInvalid;
      }
    }
    if (Node_point_or_undef(point_).kind() == NT::ValUndef) {
      ++curr_index_;
      Node out = point_;
      point_ = Node_next(point_);
      return out;
    }
    SizeOrDim target_index =
        ConstGetUnsigned(Node_x_eval(Node_point_or_undef(point_)));
    if (curr_index_ < target_index) {
      ++curr_index_;
      return kNodeInvalid;
    }
    ++curr_index_;
    Node out = point_;
    point_ = Node_next(point_);
    return out;
  }

 private:
  Node point_;
  SizeOrDim dim_;
  SizeOrDim curr_index_ = 0;
  const SrcLoc& sl_;
};

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
              << EnumToString(CanonType_ir_regs(Node_x_type(p))) << "\n";
  }
}

struct BaseOffset {
  std::string base;
  SizeOrDim offset;
};

struct ReturnResultLocation {};

bool IsDefOnStack(Node node) {
  if (Node_has_flag(node, BF::REF)) return true;
  return CanonType_ir_regs(Node_x_type(node)) == DK::MEM;
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
      std::cout << kTAB << "ld.mem " << out << ":"
                << EnumToString(CanonType_ir_regs(ct)) << " = "
                << NameData(Node_name(def_node)) << " 0 \n";
      return out;
    }
    case NT::FunParam:
      return NameData(Node_name(def_node));
    case NT::DefFun: {
      std::string out = id_gen->NameNewNext(NameNew("funaddr"));
      std::cout << kTAB << "lea.fun " << out << ":"
                << EnumToString(CanonType_ir_regs(ct)) << " = "
                << NameData(Node_name(def_node)) << "\n";
      return out;
    }
    case NT::DefVar:
      if (IsDefOnStack(node)) {
        std::string out = id_gen->NameNewNext(NameNew("stkread"));
        std::cout << kTAB << "ld.stk " << out << ":"
                  << EnumToString(CanonType_ir_regs(ct)) << " = "
                  << NameData(Node_name(def_node)) << " 0 \n";
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
      out += std::to_string(ConstGetUnsigned(val));
      break;
    case BASE_TYPE_KIND::S8:
    case BASE_TYPE_KIND::S16:
    case BASE_TYPE_KIND::S32:
    case BASE_TYPE_KIND::S64:
      out += std::to_string(ConstGetSigned(val));
      break;
    case BASE_TYPE_KIND::R32:
    case BASE_TYPE_KIND::R64:
      out += std::to_string(ConstGetFloat(val));
      break;
    default:
      ASSERT(false, "UNREACHABLE");
      break;
  }
  out += ":";
  out += EnumToString(CanonType_ir_regs(ct));
  return out;
}

void EmitExprToMemory(Node node, const BaseOffset& dst,
                      const TargetArchConfig& ta, IdGenIR* id_gen) {}

std::string EmitExpr(Node node, const TargetArchConfig& ta, IdGenIR* id_gen) {
  //CanonType ct = Node_x_type(node);
  switch (node.kind()) {
    case NT::ValNum:
      return FormatNumber(node);
    case NT::Id:
      return EmitId(node, ta, id_gen);
    case NT::FunParam:
      return NameData(Node_name(Node_x_symbol(node)));
    default:
      return "";
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
      break;
    case NT::ExprCall:
    case NT::ExprStmt:
    case NT::ExprField:
    case NT::ExprIndex:
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

void EmitStmt(Node node, const ReturnResultLocation* result,
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
          EmitExpr(init, ta, id_gen);
        }
      } else {
        if (init.kind() == NT::ValUndef) {
          std::cout << kTAB << ".reg " << EnumToString(CanonType_ir_regs(ct))
                    << " " << name << "\n";
        } else {
          EmitExpr(init, ta, id_gen);
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
        EmitStmt(s, result, ta, id_gen);
      }
      std::cout << ".bbl " << NameData(Node_name(node)) << ".end" << "\n";
      break;
    }
    case NT::StmtReturn:
      if (Node_x_target(node).kind() == NT::ExprStmt) {
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
        std::cout << kTAB << "lea.stk " << name_addr << ":" << name << " 0 \n";
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
          EmitStmt(s, result, ta, id_gen);
          last_s = s;
        }
        if (!ChangesControlFlow(last_s)) {
          std::cout << kTAB << ".bra " << label_join << "\n";
        }

        std::cout << ".bbl " << label_f << "\n";
        for (Node s = Node_body_f(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, result, ta, id_gen);
        }
      } else if (!Node_body_t(node).isnull()) {
        for (Node s = Node_body_t(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, result, ta, id_gen);
        }
      } else {
        for (Node s = Node_body_f(node); !s.isnull(); s = Node_next(s)) {
          EmitStmt(s, result, ta, id_gen);
        }
      }

      break;
    }
    case NT::StmtAssignment:
      break;
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
      EmitStmt(s, nullptr, ta, id_gen);
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

// forward decl
SizeOrDim EmitInitializerRecursively(Node node, CanonType ct, SizeOrDim offset,
                                     const TargetArchConfig& ta);

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
  SizeOrDim dim = CanonType_dim(ct);
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