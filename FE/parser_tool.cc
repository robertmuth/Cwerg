#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"
#include "Util/stripe.h"
#include "Util/switch.h"

using namespace cwerg::fe;
using namespace cwerg;

SwitchInt32 sw_multiplier("multiplier", "adjust multiplies for item pool sizes",
                          4);

bool ends_with(std::string_view str, std::string_view suffix) {
  return str.size() >= suffix.size() &&
         str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}

bool starts_with(std::string_view str, std::string_view prefix) {
  return str.size() >= prefix.size() &&
         str.compare(0, prefix.size(), prefix) == 0;
}
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

uint16_t BitsFromAnnotation(const TK& tk) { return 0; }





Node PrattParseKW(Lexer* lexer, const TK& tk, uint32_t precedence) {
  ASSERT(false, "");
  return Node(HandleInvalid);
}

Node PrattParsePrefix(Lexer* lexer, const TK& tk, uint32_t precedence) {
  ASSERT(false, "");
  return Node(HandleInvalid);
}

Node MakeNodeId(std::string_view s) {
  Node out = NodeNew(NT::Id);
  std::string_view mod_name = std::string_view();
  std::string_view enum_name = std::string_view();

  size_t pos = s.find("::");
  if (pos != std::string_view::npos) {
    mod_name = s.substr(0, pos);
    s = s.substr(pos + 2);
  }
  pos = s.find(":");
  if (pos != std::string_view::npos) {
    enum_name = s.substr(pos + 1);
    s = s.substr(0, pos);
  }
  InitId(out, NameNew(mod_name), NameNew(s), NameNew(enum_name));
  return out;
}

Node PrattParseId(Lexer* lexer, const TK& tk, uint32_t precedence) {
  if (starts_with(tk.text, "$")) {
    Node out = NodeNew(NT::MacroId);
    InitMacroId(out, NameNew(tk.text));
    return out;
  } else {
    return MakeNodeId(tk.text);
  }
}

Node PrattParseNum(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ValNum);
  InitValNum(out, StrNew(tk.text));
  return out;
}

Node PrattParseChar(Lexer* lexer, const TK& tk, uint32_t precedence) {
  ASSERT(false, "");
  return Node(HandleInvalid);
}

Node PrattParseValCompound(Lexer* lexer, const TK& tk, uint32_t precedence) {
  ASSERT(false, "");
  return Node(HandleInvalid);
}

Node PrattParseParenGroup(Lexer* lexer, const TK& tk, uint32_t precedence) {
  ASSERT(false, "");
  return Node(HandleInvalid);
}

Node PrattParseStr(Lexer* lexer, const TK& tk, uint32_t precedence) {
  std::string_view s = tk.text;
  STR_KIND sk = STR_KIND::NORMAL;
  uint32_t offset = 0;
  if (s[0] == '"') {
    sk = STR_KIND::NORMAL;
    offset = 0;
  } else if (s[0] == 'r') {
    sk = STR_KIND::RAW;
    offset = 1;
  } else if (s[0] == 'x') {
    sk = STR_KIND::HEX;
    offset = 1;
  } else {
    ASSERT(false, "");
  }

  if (starts_with(s.substr(1), "\"\"\"")) {
    s = s.substr(offset + 3, s.size() - offset - 6);
    sk = STR_KIND(1 + uint8_t(sk));
  } else {
    s = s.substr(offset + 1, s.size() - offset - 2);
  }

  Node out = NodeNew(NT::ValString);
  InitValString(out, StrNew(s), sk);
  return out;
}

struct PrattHandlerPrefix {
  std::function<Node(Lexer*, const TK&, uint32_t)> handler = nullptr;
  uint32_t precedence = 0;
};

struct PrattHandlerInfix {
  std::function<Node(Lexer*, Node, const TK&, uint32_t)> handler = nullptr;
  uint32_t precedence = 0;
};

constexpr int MAX_TK_KIND = int(TK_KIND::SPECIAL_EOF) + 1;

std::array<PrattHandlerPrefix, MAX_TK_KIND> PREFIX_EXPR_PARSERS;
std::array<PrattHandlerInfix, MAX_TK_KIND> INFIX_EXPR_PARSERS;

// Could probably done with C++20 designated array initializers
// But going for C++17 to C++20 is a major step.
void PREFIX_EXPR_PARSERS_Init() {
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::KW)] = {PrattParseKW, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::PREFIX_OP)] = {PrattParsePrefix, 13};
  // only used for '-'
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::ADD_OP)] = {PrattParsePrefix, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::ID)] = {PrattParseId, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::NUM)] = {PrattParseNum, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::STR)] = {PrattParseStr, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::CHAR)] = {PrattParseChar, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::PAREN_OPEN)] = {PrattParseParenGroup,
                                                        10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::CURLY_OPEN)] = {PrattParseValCompound,
                                                        10};
  //

  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::COMPARISON_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::ADD_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::MUL_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::OR_SC_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::AND_SC_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::SHIFT_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::PAREN_OPEN)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::SQUARE_OPEN)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::DEREF_OR_POINTER_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::DOT_OP)] = {nullptr, 0};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::TERNARY_OP)] = {nullptr, 0};
}

Node PrattParseExpr(Lexer* lexer, uint32_t precdence = 0);

Node ParseTypeExpr(Lexer* lexer) {
  const TK tk = lexer->Next();

  if (tk.kind == TK_KIND::BASE_TYPE) {
    Node out = NodeNew(NT::TypeBase);
    InitTypeBase(out, BASE_TYPE_KIND_FromString(tk.text));
    return out;
  } else if (tk.kind == TK_KIND::PREFIX_OP) {
    ASSERT(tk.text == "^" || tk.text == "^!", "");
    Node out = NodeNew(NT::TypePtr);
    Node pointee = ParseTypeExpr(lexer);
    uint16_t bits = tk.text.size() == 1 ? 0 : 1 << int(NFD_BOOL_FIELD::mut);
    InitTypePtr(out, pointee, bits);
    return out;
  } else if (tk.kind == TK_KIND::SQUARE_OPEN) {
    Node dim = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::SQUARE_CLOSED);
    Node type = ParseTypeExpr(lexer);
    Node out = NodeNew(NT::TypeVec);
    InitTypeVec(out, dim, type);
    return out;
  }
  std::cout << "### " << tk.text << "\n";
  ASSERT(false, "NYI TypeExpr");
  return Node(HandleInvalid);
}

Node PrattParseExpr(Lexer* lexer, uint32_t precedence) {
  const TK& tk = lexer->Next();
  const PrattHandlerPrefix& prefix_handler = PREFIX_EXPR_PARSERS[uint8_t(tk.kind)];
  ASSERT(prefix_handler.handler != nullptr, "");
  Node lhs = prefix_handler.handler(lexer, tk, prefix_handler.precedence);
  while (true) {
    const TK& tk = lexer->Peek();
    const PrattHandlerInfix& infix_handler = INFIX_EXPR_PARSERS[uint8_t(tk.kind)];
    if (precedence >=infix_handler.precedence) {
      break;
    }

    lhs = infix_handler.handler(lexer, lhs, lexer->Next(),
                                infix_handler.precedence);
  }
  return lhs;
}

bool MaybeTypeExprStart(const TK& tk) {
  switch (tk.kind) {
    case TK_KIND::BASE_TYPE:
      return true;
    case TK_KIND::PREFIX_OP:
      return tk.text == "^" || tk.text == "^!";
    case TK_KIND::SQUARE_OPEN:
      return true;
    case TK_KIND::KW:
      return tk.text == "auto" || tk.text == "funtype" ||
             tk.text == "type_of" || tk.text == "union" ||
             tk.text == "union_delta";
    default:
      return false;
  }
}

Node ParseTypeExprOrExpr(Lexer* lexer) {
  const TK& tk = lexer->Peek();
  if (MaybeTypeExprStart(tk)) {
    return ParseTypeExpr(lexer);
  } else {
    return PrattParseExpr(lexer);
  }
  return Node(HandleInvalid);
}

Node ParseMacroArgList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return Node(HandleInvalid);
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = ParseTypeExprOrExpr(lexer);

  Node next = ParseMacroArgList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseModParamList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return Node(HandleInvalid);
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchOrDie(TK_KIND::ID);
  TK kind = lexer->MatchOrDie(TK_KIND::ID);
  Node out = NodeNew(NT::ModParam);
  InitModParam(out, NameNew(name.text), MOD_PARAM_KIND_FromString(kind.text));
  Node next = ParseModParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseFunParamList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return Node(HandleInvalid);
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchOrDie(TK_KIND::ID);
  Node type = ParseTypeExpr(lexer);
  Node out = NodeNew(NT::ModParam);

  InitFunParam(out, NameNew(name.text), type, BitsFromAnnotation(name));
  Node next = ParseFunParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseStmt(Lexer* lexer) {
  const TK tk = lexer->Next();
  if (tk.text == "return") {
    Node expr = PrattParseExpr(lexer);
    Node out = NodeNew(NT::StmtReturn);
    InitStmtReturn(out, expr);
    return out;
  } else {
    ASSERT(false, "STMT");
    return Node(HandleInvalid);
  }
}

Node ParseStmtBodyList(Lexer* lexer, uint32_t column) {
  const TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.sl.col < column) {
    return Node(HandleInvalid);
  }
  std::cout << "@@ BODY " << tk.text << "\n";
  Node out = Node(HandleInvalid);
  if (tk.kind == TK_KIND::ID) {
    lexer->Next();
    ASSERT(ends_with(tk.text, "#"), "");
    Node args = Node(HandleInvalid);
    if (lexer->Match(TK_KIND::PAREN_OPEN)) {
      args = ParseMacroArgList(lexer, false);
    } else {
      ASSERT(false, "NYI StmtBodyList");
    }

    out = NodeNew(NT::MacroInvoke);
    InitMacroInvoke(out, NameNew(tk.text), args);
  } else {
    ASSERT(tk.kind == TK_KIND::KW, "NYI");
    out = ParseStmt(lexer);
  }
  Node next = ParseStmtBodyList(lexer, column);
  Node_next(out) = next;
  return out;
}

Node ParseRecFieldList(Lexer* lexer, uint32_t column) {
  TK name = lexer->Next();
  std::cout << "@@ rec field " << name.text << "\n";
  if (name.kind == TK_KIND::SPECIAL_EOF || name.sl.col < column) {
    return Node(HandleInvalid);
  }

  Node type = ParseTypeExpr(lexer);
  Node out = NodeNew(NT::RecField);
  InitRecField(out, NameNew(name.text), type);
  Node_next(out) = ParseRecFieldList(lexer, column);
  return out;
}

Node ParseTopLevel(Lexer* lexer) {
  const TK& tk = lexer->Next();
  ASSERT(tk.kind == TK_KIND::KW, "expected top level kw");
  if (tk.text == "fun") {
    Node out = NodeNew(NT::DefFun);
    TK name = lexer->MatchOrDie(TK_KIND::ID);
    lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
    Node params = ParseFunParamList(lexer, false);
    Node result = Node(HandleInvalid);
    if (lexer->Match(TK_KIND::COLON)) {
      ASSERT(false, "");
    } else {
      result = ParseTypeExpr(lexer);
      lexer->MatchOrDie(TK_KIND::COLON);
    }
    const TK& tk = lexer->Peek();
    Node body = ParseStmtBodyList(lexer, tk.sl.col);
    InitDefFun(out, NameNew(name.text), params, result, body,
               BitsFromAnnotation(name));
    return out;
  } else if (starts_with(tk.text, "global")) {
    const TK name = lexer->MatchOrDie(TK_KIND::ID);
    Node type = Node(HandleInvalid);
    Node init = Node(HandleInvalid);
    if (lexer->Match(TK_KIND::ASSIGN)) {
      type = NodeNew(NT::TypeAuto);
      InitTypeAuto(type);
      init = PrattParseExpr(lexer);
    } else {
      type = ParseTypeExpr(lexer);
      if (lexer->Match(TK_KIND::ASSIGN)) {
        init = PrattParseExpr(lexer);
      } else {
        init = NodeNew(NT::ValAuto);
        InitValAuto(init);
      }
    }
    Node out = NodeNew(NT::DefGlobal);
    // TODO: mut
    uint16_t bits = 0;
    InitDefGlobal(out, NameNew(name.text), type, init, bits);
    return out;
  } else if (tk.text == "rec") {
    TK name = lexer->MatchOrDie(TK_KIND::ID);
    lexer->MatchOrDie(TK_KIND::COLON);
    Node fields = ParseRecFieldList(lexer, lexer->Peek().sl.col);
    Node out = NodeNew(NT::DefRec);
    InitDefRec(out, NameNew(name.text), fields, BitsFromAnnotation(tk));
    return out;
  } else if (tk.text == "import") {
    TK name = lexer->MatchOrDie(TK_KIND::ID);
    Node args = Node(HandleInvalid);
    std::string_view path = std::string_view();
    if (lexer->Match(TK_KIND::ASSIGN)) {
      const TK& tk = lexer->Next();
      path = tk.text;
    }
    if (lexer->Match(TK_KIND::PAREN_OPEN)) {
      ASSERT(false, "NYI Import With Params");
    }
    Node out = NodeNew(NT::Import);
    InitImport(out, NameNew(name.text), StrNew(path), args);
    return out;

  } else if (tk.text == "type") {
    ASSERT(false, "NYI DefType");
  } else {
    std::cout << "#### " << tk.text << "\n";
    ASSERT(false, "");
  }
  return Node(HandleInvalid);
}

Node ParseModBodyList(Lexer* lexer, uint32_t column) {
  const TK& tk = lexer->Peek();
  std::cout << "@@@@ TOP " << tk.text << " " << EnumToString(tk.kind) << "\n";
  if (tk.kind == TK_KIND::SPECIAL_EOF) {
    return Node(HandleInvalid);
  }

  Node top = ParseTopLevel(lexer);
  Node next = ParseModBodyList(lexer, column);
  Node_next(top) = next;
  return top;
}

Node ParseDefMod(Lexer* lexer) {
  const TK& tk = lexer->MatchOrDie(TK_KIND::KW, "module");
  //
  Node def_mod = NodeNew(NT::DefMod);
  Node params = Node(HandleInvalid);
  if (lexer->Match(TK_KIND::PAREN_OPEN)) {
    params = ParseModParamList(lexer, false);
  }
  lexer->MatchOrDie(TK_KIND::COLON);
  Node body = ParseModBodyList(lexer, 0);
  InitDefMod(def_mod, params, body, BitsFromAnnotation(tk));
  return def_mod;
}

int main(int argc, const char* argv[]) {
  InitLexer();
  InitStripes(sw_multiplier.Value());
  PREFIX_EXPR_PARSERS_Init();

  // If the synchronization is turned off, the C++ standard streams are allowed
  // to buffer their I/O independently from their stdio counterparts, which may
  // be considerably faster in some cases.
  std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::vector<char> data = SlurpDataFromStream(fin);
  Lexer lexer(
      std::string_view(reinterpret_cast<char*>(data.data()), data.size()), 555);
  // std::cout << "loaded " << data.size() << " bytes\n";

  ParseDefMod(&lexer);
  return 0;
}