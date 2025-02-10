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

Node ParseTypeExpr(Lexer* lexer);
Node PrattParseExpr(Lexer* lexer, uint32_t precdence = 0);
Node ParseStmtBodyList(Lexer* lexer, uint32_t column);

uint16_t BitsFromAnnotation(const TK& tk) { return 0; }

void ParseFunLikeArgs(Lexer* lexer, std::string_view args_desc,
                      std::array<Node, 4>* args) {
  lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
  for (int i = 0; i < args_desc.size(); i++) {
    if (i != 0) {
      lexer->MatchOrDie(TK_KIND::COMMA);
    }
    switch (args_desc[i]) {
      case 'E':
        (*args)[i] = PrattParseExpr(lexer);
        break;
      case 'T':
        (*args)[i] = ParseTypeExpr(lexer);
        break;
      default:
        ASSERT(false, "");
        break;
    }
  }
  lexer->MatchOrDie(TK_KIND::PAREN_CLOSED);
}

Node ParseFunLike(Lexer* lexer, NT nt, const TK& tk) {
  Node out = NodeNew(nt);
  std::array<Node, 4> args = {Node(HandleInvalid), Node(HandleInvalid),  //
                              Node(HandleInvalid), Node(HandleInvalid)};
  uint16_t bits = 0;
  switch (nt) {
    // TE
    case NT::ExprOffsetof:
      ParseFunLikeArgs(lexer, "TE", &args);
      InitExprOffsetof(out, args[0], args[1]);
      return out;
    // EE
    case NT::ValSpan:
      ParseFunLikeArgs(lexer, "EE", &args);
      InitValSpan(out, args[0], args[1]);
      return out;
    // TT
    case NT::TypeUnionDelta:
      ParseFunLikeArgs(lexer, "TT", &args);
      InitTypeUnionDelta(out, args[0], args[1]);
      return out;
    // E
    case NT::ExprLen:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprLen(out, args[0]);
      return out;
    case NT::ExprUnwrap:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprUnwrap(out, args[0]);
      return out;
    case NT::ExprUnionTag:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprUnwrap(out, args[0]);
      return out;
    case NT::ExprStringify:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprStringify(out, args[0]);
      return out;
    case NT::ExprSrcLoc:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprSrcLoc(out, args[0]);
      return out;
    case NT::TypeOf:
      ParseFunLikeArgs(lexer, "E", &args);
      InitTypeOf(out, args[0]);
      return out;
    // E with bits
    case NT::ExprFront:
      ParseFunLikeArgs(lexer, "E", &args);
      InitExprFront(out, args[0], bits);
      return out;
    // T
    case NT::ExprSizeof:
      ParseFunLikeArgs(lexer, "T", &args);
      InitExprSizeof(out, args[0]);
      return out;
    case NT::ExprTypeId:
      ParseFunLikeArgs(lexer, "T", &args);
      InitExprTypeId(out, args[0]);
      return out;
    // ET
    case NT::ExprAs:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprAs(out, args[0], args[1]);
      return out;
    case NT::ExprWrap:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprWrap(out, args[0], args[1]);
      return out;
    case NT::ExprIs:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprIs(out, args[0], args[1]);
      return out;
    case NT::ExprWiden:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprWiden(out, args[0], args[1]);
      return out;
    case NT::ExprUnsafeCast:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprUnsafeCast(out, args[0], args[1]);
      return out;
    case NT::ExprBitCast:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprBitCast(out, args[0], args[1]);
      return out;
    // ET with bits
    case NT::ExprNarrow:
      ParseFunLikeArgs(lexer, "ET", &args);
      InitExprNarrow(out, args[0], args[1], bits);
      return out;
      //
    default:
      ASSERT(false, tk);
      return Node(HandleInvalid);
  }
}

Node PrattParseKW(Lexer* lexer, const TK& tk, uint32_t precedence) {
  const NT nt = KeywordToNT(tk.text);
  ASSERT(nt != NT::invalid, "");
  return ParseFunLike(lexer, nt, tk);
}

Node PrattParseSimpleVal(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = Node(HandleInvalid);
  switch (tk.text[0]) {
    case 'a':
      out = NodeNew(NT::ValAuto);
      InitValAuto(out);
      return out;
    case 't':
      out = NodeNew(NT::ValTrue);
      InitValTrue(out);
      return out;
    case 'f':
      out = NodeNew(NT::ValFalse);
      InitValFalse(out);
      return out;
    case 'u':
      out = NodeNew(NT::ValUndef);
      InitValUndef(out);
      return out;
    case 'v':
      out = NodeNew(NT::ValVoid);
      InitValVoid(out);
      return out;
    default:
      ASSERT(false, tk);
      return out;
  }
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

Node MakeNodeMacroId(std::string_view s) {
  Node out = NodeNew(NT::MacroId);
  InitMacroId(out, NameNew(s));
  return out;
}

Node PrattParseId(Lexer* lexer, const TK& tk, uint32_t precedence) {
  return starts_with(tk.text, "$") ? MakeNodeMacroId(tk.text)
                                   : MakeNodeId(tk.text);
}

Node PrattParseNum(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ValNum);
  InitValNum(out, StrNew(tk.text));
  return out;
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

Node PrattParseAddrOf(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ExprAddrOf);
  Node expr = PrattParseExpr(lexer, precedence);
  // TODO
  uint16_t bits = 0;
  InitExprAddrOf(out, expr, bits);
  return out;
}

Node PrattParseExpr2(Lexer* lexer, Node lhs, const TK& tk,
                     uint32_t precedence) {
  BINARY_EXPR_KIND kind = BINARY_EXPR_KIND_FromString(tk.text, tk.kind);
  Node rhs = PrattParseExpr(lexer, precedence);
  Node out = NodeNew(NT::Expr2);
  InitExpr2(out, kind, lhs, rhs);
  return out;
}

Node PrattParseExpr3(Lexer* lexer, Node lhs, const TK& tk,
                     uint32_t precedence) {
  Node out = NodeNew(NT::Expr3);
  Node expr_t = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::COLON);
  Node expr_f = PrattParseExpr(lexer);
  InitExpr3(out, lhs, expr_t, expr_f);
  return out;
}

Node PrattParseExprDeref(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  Node out = NodeNew(NT::ExprDeref);
  InitExprDeref(out, lhs);
  return out;
}

Node PrattParseExprIndex(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  Node out = NodeNew(NT::ExprIndex);
  Node index = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::SQUARE_CLOSED);
  // TODO
  uint16_t bits = 0;
  InitExprIndex(out, lhs, index, bits);
  return out;
}

Node PrattParseExprField(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  const TK& field = lexer->MatchOrDie(TK_KIND::ID);
  Node out = NodeNew(NT::ExprField);
  InitExprField(out, lhs, MakeNodeId(tk.text));
  return out;
}

Node ParseFunArgsList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return Node(HandleInvalid);
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = PrattParseExpr(lexer);
  Node_next(out) = ParseFunArgsList(lexer, true);
  return out;
}

Node PrattParseExprCall(Lexer* lexer, Node lhs, const TK& tk,
                        uint32_t precedence) {
  if (lhs.kind() == NT::Id) {
    ASSERT(!ends_with(NameData(Node_base_name(lhs)), "#"), "MACRO");
  }
  Node out = NodeNew(NT::ExprCall);

  ASSERT(tk.kind == TK_KIND::PAREN_OPEN, "");
  Node args = ParseFunArgsList(lexer, false);
  InitExprCall(out, lhs, args);
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
  // Init Prefix Table
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::KW)] = {PrattParseKW, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::KW_SIMPLE_VAL)] = {PrattParseSimpleVal,
                                                           10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::PREFIX_OP)] = {PrattParsePrefix, 13};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::ADDR_OF_OP)] = {PrattParseAddrOf, 13};

  // only used for '-'
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::ADD_OP)] = {PrattParsePrefix, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::ID)] = {PrattParseId, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::NUM)] = {PrattParseNum, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::STR)] = {PrattParseStr, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::CHAR)] = {PrattParseNum, 10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::PAREN_OPEN)] = {PrattParseParenGroup,
                                                        10};
  PREFIX_EXPR_PARSERS[uint32_t(TK_KIND::CURLY_OPEN)] = {PrattParseValCompound,
                                                        10};
  // Init Infix/Postfix Table
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::OR_SC_OP)] = {PrattParseExpr2, 5};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::AND_SC_OP)] = {PrattParseExpr2, 6};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::COMPARISON_OP)] = {PrattParseExpr2, 7};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::ADD_OP)] = {PrattParseExpr2, 10};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::MUL_OP)] = {PrattParseExpr2, 11};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::SHIFT_OP)] = {PrattParseExpr2, 12};
  //
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::PAREN_OPEN)] = {PrattParseExprCall, 20};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::SQUARE_OPEN)] = {PrattParseExprIndex,
                                                        14};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::DEREF_OR_POINTER_OP)] = {
      PrattParseExprDeref, 14};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::DOT_OP)] = {PrattParseExprField, 14};
  INFIX_EXPR_PARSERS[uint32_t(TK_KIND::TERNARY_OP)] = {PrattParseExpr3, 6};
}

Node ParseTypeExpr(Lexer* lexer) {
  const TK tk = lexer->Next();

  if (tk.kind == TK_KIND::BASE_TYPE) {
    Node out = NodeNew(NT::TypeBase);
    InitTypeBase(out, BASE_TYPE_KIND_FromString(tk.text));
    return out;
  } else if (tk.kind == TK_KIND::DEREF_OR_POINTER_OP) {
    Node out = NodeNew(NT::TypePtr);
    Node pointee = ParseTypeExpr(lexer);
    uint16_t bits = tk.text.size() == 1 ? 0 : 1 << int(NFD_BOOL_FIELD::mut);
    InitTypePtr(out, pointee, bits);
    return out;
  } else if (tk.kind == TK_KIND::SQUARE_OPEN) {
    Node out = NodeNew(NT::TypeVec);
    Node dim = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::SQUARE_CLOSED);
    Node type = ParseTypeExpr(lexer);
    InitTypeVec(out, dim, type);
    return out;
  } else if (starts_with(tk.text, "span")) {
    Node out = NodeNew(NT::TypeSpan);
    lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
    Node type = ParseTypeExpr(lexer);
    lexer->MatchOrDie(TK_KIND::PAREN_CLOSED);
    uint16_t bits = ends_with(tk.text, "!") ? 1 << int(NFD_BOOL_FIELD::mut) : 0;
    InitTypeSpan(out, type, bits);
    return out;
  } else if (tk.kind == TK_KIND::ID) {
    return MakeNodeId(tk.text);
  }
  ASSERT(false, "NYI TypeExpr " << tk);
  return Node(HandleInvalid);
}

Node PrattParseExpr(Lexer* lexer, uint32_t precedence) {
  const TK& tk = lexer->Next();
  std::cout << "@@PRATT START " << tk << "\n";
  const PrattHandlerPrefix& prefix_handler =
      PREFIX_EXPR_PARSERS[uint8_t(tk.kind)];
  ASSERT(prefix_handler.handler != nullptr, "No handler for " << tk);
  Node lhs = prefix_handler.handler(lexer, tk, prefix_handler.precedence);
  while (true) {
    const TK& tk = lexer->Peek();

    const PrattHandlerInfix& infix_handler =
        INFIX_EXPR_PARSERS[uint8_t(tk.kind)];
    std::cout << "@@PRATT LOOP prec=" << precedence << " " << tk
              << infix_handler.precedence << "\n";
    if (precedence >= infix_handler.precedence) {
      std::cout << "@@PRATT DONE\n";
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

Node ParseCaseList(Lexer* lexer, int column) {
  const TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.sl.col < column) {
    return Node(HandleInvalid);
  }
  lexer->Next();
  ASSERT(tk.kind == TK_KIND::KW && tk.text == "case", "");
  Node out = NodeNew(NT::Case);
  Node cond = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::COLON);
  Node body = ParseStmtBodyList(lexer, lexer->Peek().sl.col);
  InitCase(out, cond, body);
  Node_next(out) = ParseCaseList(lexer, column);
  return out;
}

Node ParseStmtSpecial(Lexer* lexer, const TK& tk) {
  if (tk.text == "set") {
    Node lhs = PrattParseExpr(lexer);
    TK op = lexer->Next();
    Node rhs = PrattParseExpr(lexer);
    if (op.kind == TK_KIND::ASSIGN) {
      Node out = NodeNew(NT::StmtAssignment);
      InitStmtAssignment(out, lhs, rhs);
      return out;
    } else {
      Node out = NodeNew(NT::StmtAssignment);
      ASSIGNMENT_KIND kind = ASSIGNMENT_KIND_FromString(op.text);
      InitStmtCompoundAssignment(out, kind, lhs, rhs);
      return out;
    }
  } else if (tk.text == "for") {
    Node out = NodeNew(NT::MacroInvoke);
    const TK& name = lexer->MatchOrDie(TK_KIND::ID);
    Node id = starts_with(name.text, "$") ? MakeNodeMacroId(tk.text)
                                          : MakeNodeId(name.text);
    lexer->MatchOrDie(TK_KIND::ASSIGN);
    Node start = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::COMMA);
    Node end = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::COMMA);
    Node step = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::COLON);

    Node stmts = ParseStmtBodyList(lexer, lexer->Peek().sl.col);
    Node body = NodeNew(NT::EphemeralList);
    uint16_t bits = 0;
    InitEphemeralList(body, stmts, bits);

    InitMacroInvoke(out, NameNew(tk.text), id);
    Node_next(id) = start;
    Node_next(start) = end;
    Node_next(end) = step;
    Node_next(step) = body;
    return out;
  } else {
    ASSERT(false, tk);
    return Node(HandleInvalid);
  }
}

Node ParseStmt(Lexer* lexer) {
  const TK tk = lexer->Next();
  const NT nt = KeywordToNT(tk.text);
  switch (nt) {
    case NT::StmtReturn: {
      Node expr = PrattParseExpr(lexer);
      Node out = NodeNew(NT::StmtReturn);
      InitStmtReturn(out, expr);
      return out;
    }
    case NT::StmtCond: {
      lexer->MatchOrDie(TK_KIND::COLON);
      Node out = NodeNew(NT::StmtCond);
      Node cases = ParseCaseList(lexer, lexer->Peek().sl.col);
      InitStmtCond(out, cases);
      return out;
    }
    case NT::StmtAssignment: {
      Node lhs = PrattParseExpr(lexer);
      const TK op = lexer->Next();
      if (op.kind == TK_KIND::ASSIGN) {
        Node out = NodeNew(NT::StmtAssignment);
        Node rhs = PrattParseExpr(lexer);
        InitStmtAssignment(out, lhs, rhs);
        return out;
      } else {
        ASSERT(op.kind == TK_KIND::COMPOUND_ASSIGN, "" << op);
        ASSERT(false, "NYI");
        return Node(HandleInvalid);
      }
    }
    case NT::DefVar: {
      Node out = NodeNew(NT::DefVar);
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
      // TODO: mut
      uint16_t bits = 0;
      InitDefVar(out, NameNew(name.text), type, init, bits);
      return out;
    }

    default:
      return ParseStmtSpecial(lexer, tk);
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
  TK name = lexer->Peek();

  if (name.kind == TK_KIND::SPECIAL_EOF || name.sl.col < column) {
    return Node(HandleInvalid);
  }
  name = lexer->Next();
  ASSERT(name.kind == TK_KIND::ID, "expected ID got " << name);
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
    Node out = NodeNew(NT::DefGlobal);
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
  // std::ios_base::sync_with_stdio(false);
  std::istream* fin = &std::cin;

  std::vector<char> data = SlurpDataFromStream(fin);
  Lexer lexer(
      std::string_view(reinterpret_cast<char*>(data.data()), data.size()), 555);
  // std::cout << "loaded " << data.size() << " bytes\n";

  ParseDefMod(&lexer);
  return 0;
}