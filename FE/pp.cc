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
    out->push_back(PP ::LineBreak());
    start = end + 1;
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
    out->push_back(PP::Str(NameData(Node_enum_name(node))));
  }
}

void EmitExprOrType(std::vector<PP::Token>* out, Node node) {
  switch (Node_kind(node)) {
    case NT::Id:
      EmitFullName(out, node);
      break;
    case NT::MacroId:
      out->push_back(PP::Str(NameData(Node_name(node))));
      break;
    default:
      out->push_back(PP::Str("EXPR_OR_TYPE"));
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

void EmitStatement(std::vector<PP::Token>* out, Node node);

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

void EmitStatement(std::vector<PP::Token>* out, Node node) {
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
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
        EmitExprOrType(out, Node_result(node));
      }
      break;
    case NT::StmtTrap:
      out->push_back(PP ::Str("trap"));
      break;
    case NT::StmtAssignment:
      EmitStmtSet(out, "=", Node_lhs(node), Node_expr_rhs(node));
      break;
    case NT::StmtCompoundAssignment:
      EmitStmtSet(out, GetOperatorString(Node_assignment_kind(node)),
                  Node_lhs(node), Node_expr_rhs(node));
      break;
    case NT::DefVar:
      EmitStmtLetOrGlobal(out, "let", Node_name(node), Node_type_or_auto(node),
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
      out->push_back(PP ::Str("TODO-MACRO_INVOKE"));
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

void EmitTokensExprMacroBlockSpecial(std::vector<PP::Token>* out, Node node) {}

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
    out->push_back(PP::Str(NameData(Node_name(node))));
  }
  out->push_back(PP::Brk(0));
  out->push_back(PP::Str("]"));
  out->push_back(PP::End());
}

void EmitTokensTopLevel(std::vector<PP::Token>* out, Node node) {
  std::cout << "TOPLEVEL " << EnumToString(Node_kind(node)) << "\n";
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  bool emit_break;
  switch (Node_kind(node)) {
    case NT::DefGlobal:
      EmitStmtLetOrGlobal(out, "global", Node_name(node),
                          Node_type_or_auto(node),
                          Node_initial_or_undef_or_auto(node));
      break;

    case NT::Import:
      out->push_back(PP::Str("import"));
      out->push_back(PP::Brk());
      out->push_back(PP::Str(NameData(Node_name(node))));
      if (Node_path(node) != StrInvalid) {
        ASSERT(false, "");
      }
      if (Node_args_mod(node) != HandleInvalid) {
        ASSERT(false, "");
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
      out->push_back(PP::Str("TODO-base-type-kind"));
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
        EmitStatementsSpecial(out, Node_body(node));
      } else {
        EmitTokensExprMacroBlockSpecial(out, Node_body_macro(node));
      }
      break;
    default:
      ASSERT(false, EnumToString(Node_kind(node)));
      break;
  }
  out->push_back(PP::End());
}

void EmitTokensModule(std::vector<PP::Token>* out, Node node) {
  ASSERT(Node_kind(node) == NT::DefMod, "");
  MaybeEmitDoc(out, node);
  out->push_back(PP_BEG_STD);
  out->push_back(PP::Str("module"));
  //
  if (Node_params_mod(node) != HandleInvalid) {
    ASSERT(false, "");
  }
  //
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
      EmitTokensTopLevel(out, child);
    }
    out->push_back(PP::End());
  }
}

void Prettify(Node mod) {
  std::vector<PP::Token> tokens;
  tokens.push_back(PP::Beg(PP::BreakType::CONSISTENT, 0));
  EmitTokensModule(&tokens, mod);
  tokens.push_back(PP::End());
  std::cout << PP::PrettyPrint(tokens, 80);
}

int main(int argc, const char* argv[]) {
  InitLexer();
  InitStripes(sw_multiplier.Value());
  InitParser();

  // If the synchronization is turned off, the C++ standard streams are
  // allowed to buffer their I/O independently from their stdio counterparts,
  // which may be considerably faster in some cases.
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