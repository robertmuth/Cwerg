#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "FE/parse.h"
#include "Util/assert.h"
#include "Util/pretty.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

const PP::Token PP_BEG_STD = PP::Beg(PP::BreakType::INCONSISTENT, 2);
const PP::Token PP_BEG_NEST = PP::Beg(PP::BreakType::FORCE_LINE_BREAK, 4);

std::vector<char> SlurpDataFromStream(std::istream* fin) {
  size_t num_bytes_per_read = 1024 * 1024;
  size_t current_offset = 0U;
  std::vector<char> out(num_bytes_per_read);
  auto rdbuf = fin->rdbuf();
  while (true) {
    size_t count =
        rdbuf->sgetn(out.data() + current_offset, num_bytes_per_read);
    if (count == 0) break;
    current_offset += count;
    out.resize(current_offset + num_bytes_per_read);
  }
  out.resize(current_offset);
  return out;
}

void MaybeEmitDoc(std::vector<PP::Token>* out, Node node) {
  Str doc = Node_comment(node);
  if (doc == StrInvalid) return;
  const char* data = StrData(doc);
  size_t start = 0;
  size_t end = 0;
  while (data[start] != '\0') {
    for (end = start; data[end] != '\n'; ++end);
    out->push_back(PP::Str(std::string_view(data + start, end - start)));
    out->push_back(PP::LineBreak());
    start = end + 1;
  }
}

#define BIT_B(x) 1ull << uint32_t(BF::x)

const uint32_t EXCLAMATION_FLAGS =
    BIT_B(MUT) | BIT_B(UNCHECKED) | BIT_B(UNTAGGED);
const uint32_t KW_FLAGS =
    BIT_B(PUB) | BIT_B(WRAPPED) | BIT_B(REF) | BIT_B(POLY);

void MaybeEmitAnnotations(std::vector<PP::Token>* out, Node node) {
  uint16_t compressed = Node_compressed_flags(node);

  if (compressed == 0) return;
  uint32_t available = GlobalNodeDescs[int(Node_kind(node))].bool_field_bits &
                       ~EXCLAMATION_FLAGS;
  if (available == 0) return;

  for (int i = 0; i < 32; i++) {
    uint32_t mask = 1 << i;
    if ((mask & available) == 0) continue;
    BF bf = BF(i);
    if ((Mask(bf) & compressed) == 0) continue;
    if ((mask & KW_FLAGS) != 0) {
      out->push_back(PP::Str(EnumToString(bf)));
      out->push_back(PP::Brk());
    } else {
      out->push_back(PP::Str("{{"));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str(EnumToString(bf)));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str("}}"));
      out->push_back(PP::Brk());
    }
  }
}

void MaybeAddCommaAndHandleComment(std::vector<PP::Token>* out, bool first,
                                   Node node, const PP::Token& first_break) {
  Str doc = Node_comment(node);
  if (!first) {
    out->push_back(PP::NoBreak(0));
    out->push_back(PP::Str(","));
  }
  if (doc != StrInvalid) {
    out->push_back(PP::LineBreak());
    MaybeEmitDoc(out, node);
  } else {
    out->push_back(first ? first_break : PP::Brk());
  }
}

void EmitFullName(std::vector<PP::Token>* out, Node node) {
  ASSERT(Node_kind(node) == NT::Id, "");
  if (!NameIsEmpty(Node_mod_name(node))) {
    out->push_back(PP::Str(NameData(Node_mod_name(node))));
    out->push_back(PP::NoBreak(0));

    out->push_back(PP::Str("::"));
    out->push_back(PP::NoBreak(0));
  }
  out->push_back(PP::Str(NameData(Node_base_name(node))));

  if (!NameIsEmpty(Node_enum_name(node))) {
    out->push_back(PP::NoBreak(0));
    out->push_back(PP::Str(":"));
    out->push_back(PP::NoBreak(0));
    out->push_back(PP::Str(NameData(Node_enum_name(node))));
  }
}

// forward decls

void EmitExprOrType(std::vector<PP::Token>* out, Node node);
void EmitStatement(std::vector<PP::Token>* out, Node node);
void EmitStatementsSpecial(std::vector<PP::Token>* out, Node node);
void EmitParameterList(std::vector<PP::Token>* out, Node node);

void EmitArg(std::vector<PP::Token>* out, Node node, bool first) {
  if (first) {
    if (Node_comment(node) != StrInvalid) {
      out->push_back(PP::Brk(0));

    } else {
      out->push_back(PP::NoBreak(0));
    }
  } else {
    out->push_back(PP::NoBreak(0));
    out->push_back(PP::Str(","));
    out->push_back(PP::Brk());
  }
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  EmitExprOrType(out, node);
  out->push_back(PP::End());
}

void EmitParenList(std::vector<PP::Token>* out, Node node) {
  out->push_back(PP::Str("("));
  if (node != HandleInvalid) {
    EmitArg(out, node, true);
    for (Node child = Node_next(node); child != HandleInvalid;
         child = Node_next(child)) {
      EmitArg(out, child, false);
    }
  }
  out->push_back(PP::NoBreak(0));
  out->push_back(PP::Str(")"));
}

void EmitFunctional(std::vector<PP::Token>* out, Node node,
                    std::string_view name, Node arg0, Node arg1 = NodeInvalid,
                    Node arg2 = NodeInvalid) {
  out->push_back(PP_BEG_STD);
  MaybeEmitAnnotations(out, node);
  out->push_back(PP::Str(name));
  out->push_back(PP::NoBreak(0));
  out->push_back(PP::Str("("));
  EmitArg(out, arg0, true);
  if (arg1 != NodeInvalid) {
    EmitArg(out, arg1, false);
  }
  if (arg2 != NodeInvalid) {
    EmitArg(out, arg2, false);
  }
  out->push_back(PP::NoBreak(0));
  out->push_back(PP::Str(")"));
  out->push_back(PP::End());
}

bool IsComplexValCompound(Node inits) {
  int num_inits = 0;
  for (Node child = inits; child != HandleInvalid; child = Node_next(child)) {
    ++num_inits;
  }
  if (num_inits > 10) {
    return true;
  }
  return inits != HandleInvalid &&
         Node_kind(Node_value_or_undef(inits)) == NT::ValCompound;
}

void EmitValCompound(std::vector<PP::Token>* out, Node node) {
  out->push_back(PP::Beg(PP::BreakType::INCONSISTENT, 1));
  Node type = Node_type_or_auto(node);
  out->push_back(PP::Str("{"));
  out->push_back(PP::NoBreak(0));
  if (Node_kind(type) != NT::TypeAuto) {
    EmitExprOrType(out, type);
    out->push_back(PP::NoBreak(0));
  }
  out->push_back(PP::Str(":"));
  bool first = true;
  PP::Token first_break =
      IsComplexValCompound(Node_inits(node)) ? PP::LineBreak() : PP::NoBreak(1);
  for (Node child = Node_inits(node); child != HandleInvalid;
       child = Node_next(child)) {
    MaybeAddCommaAndHandleComment(out, first, child, first_break);
    first = false;
    ASSERT(Node_kind(child) == NT::ValPoint, "");
    out->push_back(PP_BEG_STD);
    if (Node_kind(Node_point(child)) != NT::ValAuto) {
      EmitExprOrType(out, Node_point(child));
      out->push_back(PP::NoBreak(1));
      out->push_back(PP::Str("="));
      out->push_back(PP::Brk());
    }
    EmitExprOrType(out, Node_value_or_undef(child));
    out->push_back(PP::End());
  }
  out->push_back(PP::Brk(0));
  out->push_back(PP::Str("}"));
  out->push_back(PP::End());
}

void EmitExprOrType(std::vector<PP::Token>* out, Node node) {
  // std::cout << "EXPR " << EnumToString(Node_kind(node)) << "\n";
  switch (Node_kind(node)) {
    case NT::Id:
      EmitFullName(out, node);
      break;
    case NT::MacroId:
      out->push_back(PP::Str(NameData(Node_name(node))));
      break;
    case NT::ValTrue:
      out->push_back(PP::Str("true"));
      break;
    case NT::ValFalse:
      out->push_back(PP::Str("false"));
      break;
    case NT::ValUndef:
      out->push_back(PP::Str("undef"));
      break;
    case NT::ValVoid:
      out->push_back(PP::Str("void_val"));
      break;
    case NT::ValAuto:
      out->push_back(PP::Str("auto_val"));
      break;
    case NT::TypeAuto:
      out->push_back(PP::Str("auto"));
      break;
    case NT::ValNum:
      out->push_back(PP::Str(StrData(Node_number(node))));
      break;
    case NT::TypeBase:
      out->push_back(PP::Str(EnumToString(Node_base_type_kind(node))));
      break;
    case NT::ExprFront:
      EmitFunctional(out, node,
                     Node_has_flag(node, BF::MUT) ? "front!" : "front",
                     Node_container(node));
      break;
    case NT::ExprLen:
      EmitFunctional(out, node, "len", Node_container(node));
      break;
      //
    case NT::ExprOffsetof:
      EmitFunctional(out, node, "offset_of", Node_type(node), Node_field(node));
      break;
    case NT::TypeUnionDelta:
      EmitFunctional(out, node, "union_delta", Node_type(node),
                     Node_subtrahend(node));
      break;
    case NT::ValSpan:
      EmitFunctional(out, node, "make_span", Node_pointer(node),
                     Node_expr_size(node));
      break;
      //

    case NT::ExprAs:
      EmitFunctional(out, node, "as", Node_expr(node), Node_type(node));
      break;
    case NT::ExprIs:
      EmitFunctional(out, node, "is", Node_expr(node), Node_type(node));
      break;
    case NT::ExprUnsafeCast:
      EmitFunctional(out, node, "unsafe_as", Node_expr(node), Node_type(node));
      break;
    case NT::ExprWiden:
      EmitFunctional(out, node, "widen_as", Node_expr(node), Node_type(node));
      break;
    case NT::ExprWrap:
      EmitFunctional(out, node, "wrap_as", Node_expr(node), Node_type(node));
      break;
    case NT::ExprBitCast:
      EmitFunctional(out, node, "bitwise_as", Node_expr(node), Node_type(node));
      break;
    case NT::ExprNarrow:
      EmitFunctional(
          out, node,
          Node_has_flag(node, BF::UNCHECKED) ? "narrow_as!" : "narrow_as",
          Node_expr(node), Node_type(node));
      break;
    case NT::ExprSizeof:
      EmitFunctional(out, node, "size_of", Node_type(node));
      break;
    case NT::ExprTypeId:
      EmitFunctional(out, node, "typeid_of", Node_type(node));
      break;
    case NT::TypeSpan:
      EmitFunctional(out, node, Node_has_flag(node, BF::MUT) ? "span!" : "span",
                     Node_type(node));
      break;
    case NT::ExprUnionTag:
      EmitFunctional(out, node, "union_tag", Node_expr(node));
      break;
    case NT::ExprUnwrap:
      EmitFunctional(out, node, "unwrap", Node_expr(node));
      break;
    case NT::ExprStringify:
      EmitFunctional(out, node, "stringify", Node_expr(node));
      break;
    case NT::ExprSrcLoc:
      EmitFunctional(out, node, "srcloc", Node_expr(node));
      break;
    case NT::TypeOf:
      EmitFunctional(out, node, "type_of", Node_expr(node));
      break;
      //
    case NT::ExprCall:
      out->push_back(PP_BEG_STD);
      EmitExprOrType(out, Node_callee(node));
      out->push_back(PP::NoBreak(0));
      EmitParenList(out, Node_args(node));
      out->push_back(PP::End());
      break;
    case NT::MacroInvoke:
      out->push_back(PP_BEG_STD);
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::NoBreak(0));
      EmitParenList(out, Node_args(node));
      out->push_back(PP::End());
      break;
    case NT::TypeUnion:
      out->push_back(PP_BEG_STD);
      out->push_back(
          PP::Str(Node_has_flag(node, BF::UNTAGGED) ? "union!" : "union"));
      out->push_back(PP::NoBreak(0));
      EmitParenList(out, Node_types(node));
      out->push_back(PP::End());
      break;
    //
    case NT::ExprPointer:
      if (Node_kind(Node_expr_bound_or_undef(node)) == NT::ValUndef) {
        EmitFunctional(out, node, EnumToString(Node_pointer_expr_kind(node)),
                       Node_expr1(node), Node_expr2(node));
      } else {
        EmitFunctional(out, node, EnumToString(Node_pointer_expr_kind(node)),
                       Node_expr1(node), Node_expr2(node),
                       Node_expr_bound_or_undef(node));
      }
      break;
    case NT::Expr1:
      switch (Node_unary_expr_kind(node)) {
        case UNARY_EXPR_KIND::ABS:
          EmitFunctional(out, node, "abs", Node_expr(node));
          break;
        case UNARY_EXPR_KIND::SQRT:
          EmitFunctional(out, node, "sqrt", Node_expr(node));
          break;
        case UNARY_EXPR_KIND::NOT:
          out->push_back(PP::Str("!"));
          out->push_back(PP::Brk(0));
          EmitExprOrType(out, Node_expr(node));
          break;
        case UNARY_EXPR_KIND::NEG:
          out->push_back(PP::Str("-"));
          out->push_back(PP::Brk(0));
          EmitExprOrType(out, Node_expr(node));
          break;
        case UNARY_EXPR_KIND::INVALID:
          ASSERT(false, "");
          break;
      }
      break;
    case NT::Expr2:
      switch (Node_binary_expr_kind(node)) {
        case BINARY_EXPR_KIND::PDELTA:
          EmitFunctional(out, node, "ptr_diff", Node_expr1(node), Node_expr2(node));
          break;
        case BINARY_EXPR_KIND::MIN:
          EmitFunctional(out, node, "min", Node_expr1(node), Node_expr2(node));
          break;
        case BINARY_EXPR_KIND::MAX:
          EmitFunctional(out, node, "max", Node_expr1(node), Node_expr2(node));
          break;
        default:
          EmitExprOrType(out, Node_expr1(node));
          out->push_back(PP::NoBreak(1));
          out->push_back(PP::Str(EnumToString(Node_binary_expr_kind(node))));
          out->push_back(PP::Brk());
          EmitExprOrType(out, Node_expr2(node));
          break;
      }
      break;
    case NT::Expr3:
      EmitExprOrType(out, Node_cond(node));
      out->push_back(PP::NoBreak(1));
      out->push_back(PP::Str("?"));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_expr_t(node));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(":"));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_expr_f(node));
      break;
    case NT::ExprDeref:
      EmitExprOrType(out, Node_expr(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str("^"));
      break;
    case NT::ExprAddrOf:
      out->push_back(PP::Str(Node_has_flag(node, BF::MUT) ? "@!" : "@"));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_expr(node));
      break;
    case NT::TypePtr:
      out->push_back(PP::Str(Node_has_flag(node, BF::MUT) ? "^!" : "^"));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_type(node));
      break;
    case NT::ExprField:
      EmitExprOrType(out, Node_container(node));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str("."));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_field(node));
      break;
    case NT::ExprIndex:
      out->push_back(PP_BEG_STD);
      EmitExprOrType(out, Node_container(node));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str(Node_has_flag(node, BF::UNCHECKED) ? "[!" : "["));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_expr_index(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str("]"));
      out->push_back(PP::End());
      break;
    case NT::TypeVec:
      out->push_back(PP_BEG_STD);
      out->push_back(PP::Str("["));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_size(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str("]"));
      EmitExprOrType(out, Node_type(node));
      out->push_back(PP::End());
      break;
    case NT::TypeFun:
      out->push_back(PP::Beg(PP::BreakType::CONSISTENT, 2));
      out->push_back(PP::Str("funtype"));
      out->push_back(PP::NoBreak(0));
      EmitParameterList(out, Node_params(node));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_result(node));
      out->push_back(PP::End());
      break;
    case NT::ExprParen:
      out->push_back(PP_BEG_STD);
      out->push_back(PP::Str("("));
      out->push_back(PP::Brk(0));
      EmitExprOrType(out, Node_expr(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str(")"));
      out->push_back(PP::End());
      break;
    case NT::ValCompound:
      EmitValCompound(out, node);
      break;

    case NT::ExprStmt:
      out->push_back(PP::Str("expr"));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str(":"));
      EmitStatementsSpecial(out, Node_body(node));
      break;
    case NT::ValString:
      out->push_back(PP::Str(StrData(Node_string(node))));
      break;
    default:
      // out->push_back(PP::Str("TODO-UNEXPECTED"));
      ASSERT(false, EnumToString(Node_kind(node)));
      break;
  }
}

void EmitParameterList(std::vector<PP::Token>* out, Node node) {
  out->push_back(PP::Beg(PP::BreakType::INCONSISTENT, 1));
  out->push_back(PP ::Str("("));
  bool first = true;
  for (Node child = node; child != HandleInvalid; child = Node_next(child)) {
    MaybeAddCommaAndHandleComment(out, first, child, PP::NoBreak(0));
    first = false;
    out->push_back(PP_BEG_STD);
    out->push_back(PP::Str(NameData(Node_name(child))));
    out->push_back(PP::Brk());
    switch (Node_kind(child)) {
      case NT::FunParam:
        EmitExprOrType(out, Node_type(child));
        break;
      case NT::ModParam:
        out->push_back(PP::Str(EnumToString(Node_mod_param_kind(child))));
        break;
      case NT::MacroParam:
        out->push_back(PP::Str(EnumToString(Node_macro_param_kind(child))));
        break;
      default:
        ASSERT(false, "");
    }
    out->push_back(PP::End());
  }
  out->push_back(PP::Brk(0));
  out->push_back(PP ::Str(")"));
  out->push_back(PP::End());
}

void EmitStatementsSpecial(std::vector<PP::Token>* out, Node node) {
  if (node == HandleInvalid) {
    return;
  }
  out->push_back(PP::End());
  out->push_back(PP_BEG_NEST);
  bool first = true;
  for (Node child = node; child != HandleInvalid; child = Node_next(child)) {
    if (!first) {
      out->push_back(PP::Brk());
    }
    first = false;
    EmitStatement(out, child);
  }
}

void EmitStmtSet(std::vector<PP::Token>* out, std::string_view op, Node lhs,
                 Node rhs) {
  out->push_back(PP ::Str("set"));
  out->push_back(PP::Brk());
  EmitExprOrType(out, lhs);
  out->push_back(PP::Brk());
  out->push_back(PP ::Str(op));
  out->push_back(PP::Brk());
  EmitExprOrType(out, rhs);
}

void EmitStmtLetOrGlobal(std::vector<PP::Token>* out, std::string_view kw,
                         Name name, Node type_or_auto,
                         Node initial_or_undef_or_auto) {
  out->push_back(PP ::Str(kw));
  out->push_back(PP::NoBreak(1));
  out->push_back(PP ::Str(NameData(name)));

  if (Node_kind(type_or_auto) != NT::TypeAuto) {
    out->push_back(PP::NoBreak(1));
    EmitExprOrType(out, type_or_auto);
  }
  if (Node_kind(initial_or_undef_or_auto) != NT::ValAuto) {
    out->push_back(PP::NoBreak(1));
    out->push_back(PP ::Str("="));
    out->push_back(PP::NoBreak(1));
    EmitExprOrType(out, initial_or_undef_or_auto);
  }
}
bool IsBuiltInStmtMacro(std::string_view name) {
  return name == "while" || name == "for" || name == "trylet" ||
         name == "trylet!" || name == "tryset";
}

bool IsMacroWitBlock(Node node) {
  for (Node arg = Node_args(node); arg != HandleInvalid; arg = Node_next(arg)) {
    if (Node_kind(arg) == NT::EphemeralList && Node_has_flag(arg, BF::COLON))
      return true;
  }
  return false;
}

void EmitStmtMacroInvoke(std::vector<PP::Token>* out, Node node) {
  std::string_view name = NameData(Node_name(node));
  out->push_back(PP::Str(name));
  bool is_block_like = IsBuiltInStmtMacro(name) || IsMacroWitBlock(node);
  if (!is_block_like) {
    out->push_back(PP::NoBreak(0));
    out->push_back(PP::Beg(PP::BreakType::INCONSISTENT, 1));
    out->push_back(PP ::Str("("));
  }
  Node arg = Node_args(node);
  if (name == "for" || name == "tryset") {
    out->push_back(PP::Brk());
    EmitExprOrType(out, arg);
    arg = Node_next(arg);
    out->push_back(PP::Brk());
    out->push_back(PP ::Str("="));
  } else if (name == "trylet" || name == "trylet!") {
    out->push_back(PP::Brk());
    EmitExprOrType(out, arg);
    arg = Node_next(arg);
    out->push_back(PP::Brk());
    EmitExprOrType(out, arg);
    arg = Node_next(arg);
    out->push_back(PP::Brk());
    out->push_back(PP ::Str("="));
  }
  bool first = true;
  for (; arg != HandleInvalid; arg = Node_next(arg)) {
    if (Node_kind(arg) == NT::EphemeralList && Node_has_flag(arg, BF::COLON)) {
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_args(arg));
      continue;
    }
    if (first) {
      out->push_back(PP::Brk(is_block_like ? 1 : 0));
    } else {
      out->push_back(PP::NoBreak(0));
      out->push_back(PP ::Str(","));
      out->push_back(PP::Brk());
    }
    first = false;
    EmitExprOrType(out, arg);
  }
  if (!is_block_like) {
    out->push_back(PP::Brk(0));
    out->push_back(PP ::Str(")"));
    out->push_back(PP::End());
  }
}

void EmitStatement(std::vector<PP::Token>* out, Node node) {
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  MaybeEmitAnnotations(out, node);

  switch (Node_kind(node)) {
    case NT::StmtContinue:
      out->push_back(PP ::Str("continue"));
      if (!NameIsEmpty(Node_target(node))) {
        out->push_back(PP::NoBreak(1));
        out->push_back(PP::Str(NameData(Node_target(node))));
      }
      break;
    case NT::StmtBreak:
      out->push_back(PP ::Str("break"));
      if (!NameIsEmpty(Node_target(node))) {
        out->push_back(PP::NoBreak(1));
        out->push_back(PP::Str(NameData(Node_target(node))));
      }
      break;
    case NT::StmtReturn:
      out->push_back(PP ::Str("return"));
      if (Node_kind(Node_expr_ret(node)) != NT::ValVoid) {
        out->push_back(PP::NoBreak(1));
        EmitExprOrType(out, Node_expr_ret(node));
      }
      break;
    case NT::StmtTrap:
      out->push_back(PP ::Str("trap"));
      break;
    case NT::StmtAssignment:
      EmitStmtSet(out, "=", Node_lhs(node), Node_expr_rhs(node));
      break;
    case NT::StmtCompoundAssignment:
      EmitStmtSet(out, EnumToString(Node_assignment_kind(node)), Node_lhs(node),
                  Node_expr_rhs(node));
      break;
    case NT::DefVar:
      EmitStmtLetOrGlobal(out, Node_has_flag(node, BF::MUT) ? "let!" : "let",
                          Node_name(node), Node_type_or_auto(node),
                          Node_initial_or_undef_or_auto(node));
      break;
    case NT::StmtExpr:
      out->push_back(PP ::Str("do"));
      out->push_back(PP::NoBreak(1));
      EmitExprOrType(out, Node_expr(node));
      break;
    case NT::StmtDefer:
      out->push_back(PP ::Str("defer"));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_body(node));
      break;
    case NT::StmtCond:
      out->push_back(PP ::Str("cond"));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_cases(node));
      break;
    case NT::Case:
      out->push_back(PP ::Str("case"));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_cond(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_body(node));
      break;
    case NT::MacroInvoke:
      EmitStmtMacroInvoke(out, node);
      break;
    case NT::MacroId:
      out->push_back(PP ::Str(NameData(Node_name(node))));
      break;
    case NT::StmtBlock:
      out->push_back(PP ::Str("block"));
      out->push_back(PP::Brk());
      out->push_back(PP ::Str(NameData(Node_label(node))));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_body(node));
      break;
    case NT::StmtIf:
      out->push_back(PP ::Str("if"));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_cond(node));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_body_t(node));
      if (Node_body_f(node) != HandleInvalid) {
        out->push_back(PP::End());
        out->push_back(PP::Brk());
        out->push_back(PP_BEG_STD);
        out->push_back(PP ::Str("else"));
        out->push_back(PP::Brk(0));
        out->push_back(PP ::Str(":"));
        EmitStatementsSpecial(out, Node_body_f(node));
      }
      break;
    case NT::MacroFor:
      out->push_back(PP ::Str("mfor"));
      out->push_back(PP::Brk());
      out->push_back(PP ::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk());
      out->push_back(PP ::Str(NameData(Node_name_list(node))));
      out->push_back(PP::Brk(0));
      out->push_back(PP ::Str(":"));
      EmitStatementsSpecial(out, Node_body_for(node));

      break;
    default:
      ASSERT(false, EnumToString(Node_kind(node)));
      break;
  }
  out->push_back(PP::End());
}

void EmitExprMacroBlockSpecial(std::vector<PP::Token>* out, Node node) {
  out->push_back(PP::End());
  out->push_back(PP_BEG_NEST);
  bool first = true;
  for (Node child = node; child != HandleInvalid; child = Node_next(child)) {
    if (!first) {
      out->push_back(PP::Brk());
    }
    first = false;
    MaybeEmitDoc(out, child);
    out->push_back(PP_BEG_STD);
    EmitExprOrType(out, child);
    out->push_back(PP::End());
  }
}

void EmitIdList(std::vector<PP::Token>* out, Node node) {
  out->push_back(PP::Beg(PP::BreakType::CONSISTENT, 2));
  out->push_back(PP::Str("["));
  bool first = true;
  for (Node child = node; child != HandleInvalid; child = Node_next(child)) {
    if (first) {
      out->push_back(PP::Brk(0));
    } else {
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str(","));
      out->push_back(PP::Brk());
    }
    first = false;
    out->push_back(PP::Str(NameData(Node_name(child))));
  }
  out->push_back(PP::Brk(0));
  out->push_back(PP::Str("]"));
  out->push_back(PP::End());
}

void EmitTopLevel(std::vector<PP::Token>* out, Node node) {
  // std::cout << "TOPLEVEL " << EnumToString(Node_kind(node)) << "\n";
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  MaybeEmitAnnotations(out, node);
  bool emit_break;
  switch (Node_kind(node)) {
    case NT::DefGlobal:
      EmitStmtLetOrGlobal(out,
                          Node_has_flag(node, BF::MUT) ? "global!" : "global",
                          Node_name(node), Node_type_or_auto(node),
                          Node_initial_or_undef_or_auto(node));
      break;

    case NT::Import:
      out->push_back(PP::Str("import"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      if (Node_path(node) != StrInvalid) {
        out->push_back(PP::NoBreak(1));
        out->push_back(PP::Str("="));
        out->push_back(PP::Brk());
        out->push_back(PP::Str(StrData(Node_path(node))));
      }
      if (Node_args_mod(node) != HandleInvalid) {
        out->push_back(PP::NoBreak(1));
        EmitParenList(out, Node_args_mod(node));
      }
      break;
    case NT::DefType:
      out->push_back(PP::Str("type"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk());
      out->push_back(PP::Str("="));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_type(node));
      break;
    case NT::DefRec:
      out->push_back(PP::Str("rec"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str(":"));
      out->push_back(PP::End());
      out->push_back(PP_BEG_NEST);
      emit_break = false;
      for (Node child = Node_items(node); child != HandleInvalid;
           child = Node_next(child)) {
        if (emit_break) {
          out->push_back(PP::Brk());
        }
        emit_break = true;
        MaybeEmitDoc(out, child);
        out->push_back(PP_BEG_STD);
        out->push_back(PP::Str(NameData(Node_name(child))));
        out->push_back(PP::Brk());
        EmitExprOrType(out, Node_type(child));
        out->push_back(PP::End());
      }
      break;
    case NT::StmtStaticAssert:
      out->push_back(PP::Str("static_assert"));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_cond(node));
      break;
    case NT::DefEnum:
      out->push_back(PP::Str("enum"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(EnumToString(Node_base_type_kind(node))));
      out->push_back(PP::Brk(0));
      out->push_back(PP::Str(":"));
      out->push_back(PP::End());
      out->push_back(PP_BEG_NEST);
      emit_break = false;
      for (Node child = Node_items(node); child != HandleInvalid;
           child = Node_next(child)) {
        if (emit_break) {
          out->push_back(PP::Brk());
        }
        emit_break = true;
        MaybeEmitDoc(out, child);
        out->push_back(PP_BEG_STD);
        out->push_back(PP::Str(NameData(Node_name(child))));
        out->push_back(PP::Brk());
        EmitExprOrType(out, Node_value_or_auto(child));
        out->push_back(PP::End());
      }
      break;
    case NT::DefFun:
      out->push_back(PP::Str("fun"));
      out->push_back(PP::NoBreak(1));
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::NoBreak(0));
      EmitParameterList(out, Node_params(node));
      out->push_back(PP::Brk());
      EmitExprOrType(out, Node_result(node));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str(":"));
      EmitStatementsSpecial(out, Node_body(node));
      break;
    case NT::DefMacro:
      out->push_back(PP::Str("macro"));
      out->push_back(PP::NoBreak(1));
      out->push_back(PP::Str(NameData(Node_name(node))));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(EnumToString(Node_macro_param_kind(node))));
      out->push_back(PP::NoBreak(1));
      EmitParameterList(out, Node_params(node));
      out->push_back(PP::Brk());
      EmitIdList(out, Node_gen_ids(node));
      out->push_back(PP::NoBreak(0));
      out->push_back(PP::Str(":"));
      if (Node_macro_param_kind(node) == MACRO_PARAM_KIND::STMT ||
          Node_macro_param_kind(node) == MACRO_PARAM_KIND::STMT_LIST) {
        EmitStatementsSpecial(out, Node_body_macro(node));
      } else {
        EmitExprMacroBlockSpecial(out, Node_body_macro(node));
      }
      break;
    default:
      ASSERT(false, EnumToString(Node_kind(node)));
      break;
  }
  out->push_back(PP::End());
}

void EmitModule(std::vector<PP::Token>* out, Node node) {
  ASSERT(Node_kind(node) == NT::DefMod, "");
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  MaybeEmitAnnotations(out, node);
  out->push_back(PP::Str("module"));
  if (Node_params_mod(node) != HandleInvalid) {
    out->push_back(PP::NoBreak(0));
    EmitParameterList(out, Node_params_mod(node));
  }
  out->push_back(PP::Brk(0));
  out->push_back(PP::Str(":"));
  out->push_back(PP::End());
  if (Node_body_mod(node) != HandleInvalid) {
    out->push_back(PP::Beg(PP::BreakType::FORCE_LINE_BREAK, 0));
    bool emit_break = false;
    for (Node child = Node_body_mod(node); child != HandleInvalid;
         child = Node_next(child)) {
      out->push_back(PP::LineBreak());
      if (emit_break) {
        out->push_back(PP::LineBreak());
      }
      emit_break = true;
      EmitTopLevel(out, child);
    }
    out->push_back(PP::End());
  }
}

void Prettify(Node mod) {
  std::vector<PP::Token> tokens;
  tokens.push_back(PP::Beg(PP::BreakType::CONSISTENT, 0));
  EmitModule(&tokens, mod);
  tokens.push_back(PP::End());
  std::cout << PP::PrettyPrint(tokens, 80) << "\n";
}

int main(int argc, const char* argv[]) {
  InitStripes(sw_multiplier.Value());
  InitParser();

  // If the synchronization is turned off, the C++ standard streams are
  // allowed to buffer their I/O independently from their stdio
  // counterparts, which may be considerably faster in some cases.
  // std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::vector<char> data = SlurpDataFromStream(fin);
  Lexer lexer(
      std::string_view(reinterpret_cast<char*>(data.data()), data.size()), 555);
  // std::cout << "loaded " << data.size() << " bytes\n";

  Node mod = ParseDefMod(&lexer);
  Prettify(mod);
  return 0;
}