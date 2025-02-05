#include <fstream>
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

Node ParseTypeExpr(Lexer* lexer) {
  const TK tk = lexer->Next();
  if (tk.kind == TK_KIND::BASE_TYPE) {
    Node out = NodeNew(NT::TypeBase);
    InitTypeBase(out, BASE_TYPE_KIND_FromString(tk.text));
    return out;
  }

  ASSERT(false, "NYI TypeExpr");
  return Node(HandleInvalid);
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
  Node next = ParseModParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseStmt(Lexer* lexer) {
  ASSERT(false, "STMT");
  return Node(HandleInvalid);
}

Node ParseStmtBodyList(Lexer* lexer, uint32_t column) {
  const TK& tk = lexer->Peek();
  if (tk.kind != TK_KIND::KW) {
    return Node(HandleInvalid);
  }

  Node stmt = ParseStmt(lexer);
  Node next = ParseStmtBodyList(lexer, column);
  Node_next(stmt) = next;
  return stmt;
}

Node ParseTopLevel(Lexer* lexer) {
  const TK& tk = lexer->Next();
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
  } else if (tk.text == "rec") {
    ASSERT(false, "NYI DefRec");
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
    ASSERT(false, "");
  }
  return Node(HandleInvalid);
}

Node ParseModBodyList(Lexer* lexer, uint32_t column) {
  const TK& tk = lexer->Peek();
  if (tk.kind != TK_KIND::KW) {
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