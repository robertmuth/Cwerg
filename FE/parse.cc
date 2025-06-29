#include <functional>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/lexer.h"

namespace cwerg::fe {
namespace {

Str MoveComment(Node n) {
  Str comment = Node_comment(n);
  if (comment != kStrInvalid) {
    Node_comment(n) = kStrInvalid;
  }
  return comment;
}

Node ParseTypeExpr(Lexer* lexer);
Node PrattParseExpr(Lexer* lexer, uint32_t precdence = 0);
Node ParseStmtBodyList(Lexer* lexer, uint32_t outer_column);
Node ParseMacroArgList(Lexer* lexer, bool want_comma);
Node ParseFunParamList(Lexer* lexer, bool want_comma);
Node ParseMacroInvocation(Lexer* lexer, TK name);

uint16_t BitsFromAnnotation(const TK& tk) {
  uint32_t uncompressed = tk.annotation_bits;
  if (uncompressed == 0) {
    return 0;
  }
  uint16_t out = 0;
  for (int i = 0; i < 32; i++) {
    if (((1 << i) & uncompressed) != 0) {
      out |= Mask(BF(i));
    }
  }
  return out;
}

void ParseFunLikeArgs(Lexer* lexer, std::string_view args_desc,
                      std::array<Node, 4>* args) {
  TK start = lexer->Peek();
  lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
  for (int i = 0; i < args_desc.size(); i++) {
    uint8_t kind = args_desc[i];
    if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
      // e is optional
      ASSERT(kind == 'e', "");
      Node undef = NodeNew(NT::ValUndef);
      NodeInitValUndef(undef, start.comments, start.srcloc);
      (*args)[i] = undef;
      return;
    }
    if (i != 0) {
      lexer->MatchOrDie(TK_KIND::COMMA);
    }
    switch (kind) {
      case 'e':
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
  std::array<Node, 4> args = {kNodeInvalid, kNodeInvalid,  //
                              kNodeInvalid, kNodeInvalid};
  uint16_t bits = BitsFromAnnotation(tk);
  switch (nt) {
    // TE
    case NT::ExprOffsetof:
      ParseFunLikeArgs(lexer, "TE", &args);
      NodeInitExprOffsetof(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    // EE
    case NT::ValSpan:
      ParseFunLikeArgs(lexer, "EE", &args);
      NodeInitValSpan(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    // TT
    case NT::TypeUnionDelta:
      ParseFunLikeArgs(lexer, "TT", &args);
      NodeInitTypeUnionDelta(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    // E
    case NT::ExprLen:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitExprLen(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::ExprUnwrap:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitExprUnwrap(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::ExprUnionTag:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitExprUnionTag(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::ExprStringify:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitExprStringify(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::ExprSrcLoc:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitExprSrcLoc(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::TypeOf:
      ParseFunLikeArgs(lexer, "E", &args);
      NodeInitTypeOf(out, args[0], tk.comments, tk.srcloc);
      return out;
    // E with bits
    case NT::ExprFront:
      ParseFunLikeArgs(lexer, "E", &args);
      bits |= tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
      NodeInitExprFront(out, args[0], bits, tk.comments, tk.srcloc);
      return out;
    // T
    case NT::ExprSizeof:
      ParseFunLikeArgs(lexer, "T", &args);
      NodeInitExprSizeof(out, args[0], tk.comments, tk.srcloc);
      return out;
    case NT::ExprTypeId:
      ParseFunLikeArgs(lexer, "T", &args);
      NodeInitExprTypeId(out, args[0], tk.comments, tk.srcloc);
      return out;
    // ET
    case NT::ExprAs:
      ParseFunLikeArgs(lexer, "ET", &args);
      NodeInitExprAs(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    case NT::ExprWrap:
      ParseFunLikeArgs(lexer, "ET", &args);
      NodeInitExprWrap(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    case NT::ExprIs:
      ParseFunLikeArgs(lexer, "ET", &args);
      NodeInitExprIs(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    case NT::ExprWiden:
      ParseFunLikeArgs(lexer, "ET", &args);
      NodeInitExprWiden(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    case NT::ExprBitCast:
      ParseFunLikeArgs(lexer, "ET", &args);
      NodeInitExprBitCast(out, args[0], args[1], tk.comments, tk.srcloc);
      return out;
    // ET with bits
    case NT::ExprNarrow:
      ParseFunLikeArgs(lexer, "ET", &args);
      bits |= tk.text.ends_with("!") ? Mask(BF::UNCHECKED) : 0;
      NodeInitExprNarrow(out, args[0], args[1], bits, tk.comments, tk.srcloc);
      return out;
      //
    default:
      ASSERT(false, tk);
      return kNodeInvalid;
  }
}

Node ParseFunLikeSpecial(Lexer* lexer, const TK& tk) {
  std::array<Node, 4> args = {kNodeInvalid, kNodeInvalid,  //
                              kNodeInvalid, kNodeInvalid};
  if (tk.text == "ptr_inc" || tk.text == "ptr_dec") {
    Node out = NodeNew(NT::ExprPointer);
    ParseFunLikeArgs(lexer, "EEe", &args);
    NodeInitExprPointer(out,
                        tk.text == "ptr_inc" ? POINTER_EXPR_KIND::INCP
                                             : POINTER_EXPR_KIND::DECP,
                        args[0], args[1], args[2], tk.comments, tk.srcloc);
    return out;
  } else if (tk.text == "abs") {
    Node out = NodeNew(NT::Expr1);
    ParseFunLikeArgs(lexer, "E", &args);
    NodeInitExpr1(out, UNARY_EXPR_KIND::ABS, args[0], tk.comments, tk.srcloc);
    return out;
  } else if (tk.text == "sqrt") {
    Node out = NodeNew(NT::Expr1);
    ParseFunLikeArgs(lexer, "E", &args);
    NodeInitExpr1(out, UNARY_EXPR_KIND::SQRT, args[0], tk.comments, tk.srcloc);
    return out;
  } else if (tk.text == "ptr_diff") {
    Node out = NodeNew(NT::Expr2);
    ParseFunLikeArgs(lexer, "EE", &args);
    NodeInitExpr2(out, BINARY_EXPR_KIND::PDELTA, args[0], args[1], tk.comments,
                  tk.srcloc);
    return out;
  } else if (tk.text == "max") {
    Node out = NodeNew(NT::Expr2);
    ParseFunLikeArgs(lexer, "EE", &args);
    NodeInitExpr2(out, BINARY_EXPR_KIND::MAX, args[0], args[1], tk.comments,
                  tk.srcloc);
    return out;
  } else if (tk.text == "min") {
    Node out = NodeNew(NT::Expr2);
    ParseFunLikeArgs(lexer, "EE", &args);
    NodeInitExpr2(out, BINARY_EXPR_KIND::MIN, args[0], args[1], tk.comments,
                  tk.srcloc);
    return out;
  } else {
    ASSERT(false, tk);
    return kNodeInvalid;
  }
}

Node PrattParseKW(Lexer* lexer, const TK& tk, uint32_t precedence) {
  const NT nt = KeywordToNT(tk.text);
  if (nt == NT::invalid) {
    return ParseFunLikeSpecial(lexer, tk);
  }
  if (nt == NT::ExprStmt) {
    lexer->MatchOrDie(TK_KIND::COLON);
    Node body = ParseStmtBodyList(lexer, 0);
    Node out = NodeNew(NT::ExprStmt);
    NodeInitExprStmt(out, body, tk.comments, tk.srcloc);
    return out;
  } else {
    return ParseFunLike(lexer, nt, tk);
  }
}

Node PrattParseSimpleVal(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = kNodeInvalid;
  switch (tk.text[0]) {
    case 'a':
      out = NodeNew(NT::ValAuto);
      NodeInitValAuto(out, tk.comments, tk.srcloc);
      return out;
    case 't':
      out = NodeNew(NT::ValNum);
      NodeInitValNum(out, StrNew("true"), tk.comments, tk.srcloc);
      return out;
    case 'f':
      out = NodeNew(NT::ValNum);
      NodeInitValNum(out, StrNew("false"), tk.comments, tk.srcloc);
      return out;
    case 'u':
      out = NodeNew(NT::ValUndef);
      NodeInitValUndef(out, tk.comments, tk.srcloc);
      return out;
    case 'v':
      out = NodeNew(NT::ValVoid);
      NodeInitValVoid(out, tk.comments, tk.srcloc);
      return out;
    default:
      ASSERT(false, tk);
      return out;
  }
}

Node PrattParsePrefix(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node rhs = PrattParseExpr(lexer, precedence);
  if (tk.text == "-") {
    Node out = NodeNew(NT::Expr1);
    NodeInitExpr1(out, UNARY_EXPR_KIND::NEG, rhs, tk.comments, tk.srcloc);
    return out;
  } else if (tk.text == "!") {
    Node out = NodeNew(NT::Expr1);
    NodeInitExpr1(out, UNARY_EXPR_KIND::NOT, rhs, tk.comments, tk.srcloc);
    return out;
  } else {
    ASSERT(false, "unknown unary " << tk);
    return kNodeInvalid;
  }
}

Node MakeNodeId(const TK& tk) {
  auto s = tk.text;
  ASSERT(s[0] != '$', s);
  Node out = NodeNew(NT::Id);
  std::string_view enum_name = std::string_view();

  size_t pos = s.rfind(":");
  if (pos != std::string_view::npos && s[pos - 1] != ':') {
    enum_name = s.substr(pos + 1);
    s = s.substr(0, pos);
  }
  NodeInitId(out, NameNew(s),
             enum_name.empty() ? kNameInvalid : NameNew(enum_name), tk.comments,
             tk.srcloc);
  return out;
}

Node MakeNodeMacroId(const TK& tk) {
  std::string_view s = tk.text;
  ASSERT(s[0] == '$', s);
  Node out = NodeNew(NT::MacroId);
  NodeInitMacroId(out, NameNew(s), tk.comments, tk.srcloc);
  return out;
}

Node PrattParseId(Lexer* lexer, const TK& tk, uint32_t precedence) {
  return tk.text.starts_with("$") ? MakeNodeMacroId(tk) : MakeNodeId(tk);
}

Node PrattParseNum(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ValNum);
  NodeInitValNum(out, StrNew(tk.text), tk.comments, tk.srcloc);
  return out;
}

Node ParseValPointList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::CURLY_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = NodeNew(NT::ValPoint);

  Node val = PrattParseExpr(lexer);
  Node pos = kNodeInvalid;
  if (lexer->Match(TK_KIND::ASSIGN)) {
    pos = val;
    val = PrattParseExpr(lexer);
  } else {
    pos = NodeNew(NT::ValUndef);
    NodeInitValUndef(pos, kStrInvalid, Node_srcloc(val));
  }
  Str comment = MoveComment(pos);
  if (comment == kStrInvalid) {
    comment = MoveComment(val);
  }
  NodeInitValPoint(out, val, pos, comment, Node_srcloc(val));
  Node_next(out) = ParseValPointList(lexer, true);
  return out;
}

Node PrattParseValCompound(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ValCompound);
  Node type = kNodeInvalid;
  if (lexer->Match(TK_KIND::COLON)) {
    type = NodeNew(NT::TypeAuto);
    NodeInitTypeAuto(type, kStrInvalid, kSrcLocInvalid);
  } else {
    type = ParseTypeExpr(lexer);
    lexer->MatchOrDie(TK_KIND::COLON);
  }
  Node inits = ParseValPointList(lexer, false);
  NodeInitValCompound(out, type, inits, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseParenGroup(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ExprParen);
  Node expr = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::PAREN_CLOSED);
  NodeInitExprParen(out, expr, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseStr(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ValString);
  NodeInitValString(out, StrNew(tk.text), tk.comments, tk.srcloc);
  return out;
}

Node PrattParseAddrOf(Lexer* lexer, const TK& tk, uint32_t precedence) {
  Node out = NodeNew(NT::ExprAddrOf);
  Node expr = PrattParseExpr(lexer, precedence);
  uint16_t bits = tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
  NodeInitExprAddrOf(out, expr, bits, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseExpr2(Lexer* lexer, Node lhs, const TK& tk,
                     uint32_t precedence) {
  BINARY_EXPR_KIND kind = BINARY_EXPR_KIND_FromString(tk.text, tk.kind);
  Node rhs = PrattParseExpr(lexer, precedence);
  Node out = NodeNew(NT::Expr2);
  NodeInitExpr2(out, kind, lhs, rhs, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseExpr3(Lexer* lexer, Node lhs, const TK& tk,
                     uint32_t precedence) {
  Node out = NodeNew(NT::Expr3);
  Node expr_t = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::COLON);
  Node expr_f = PrattParseExpr(lexer);
  NodeInitExpr3(out, lhs, expr_t, expr_f, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseExprDeref(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  Node out = NodeNew(NT::ExprDeref);
  NodeInitExprDeref(out, lhs, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseExprIndex(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  Node out = NodeNew(NT::ExprIndex);
  Node index = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::SQUARE_CLOSED);
  uint16_t bits = tk.text.ends_with("!") ? Mask(BF::UNCHECKED) : 0;
  NodeInitExprIndex(out, lhs, index, bits, tk.comments, tk.srcloc);
  return out;
}

Node PrattParseExprField(Lexer* lexer, Node lhs, const TK& tk,
                         uint32_t precedence) {
  TK field = lexer->MatchIdOrDie();
  Node out = NodeNew(NT::ExprField);
  NodeInitExprField(out, lhs, MakeNodeId(field), tk.comments, tk.srcloc);
  return out;
}

Node ParseFunArgsList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = PrattParseExpr(lexer);
  Node_next(out) = ParseFunArgsList(lexer, true);
  return out;
}

std::string FullName(Node node) {
  ASSERT(node.kind() == NT::Id, "");
  std::string out = NameData(Node_name(node));
  if (!NameIsEmpty(Node_enum_name(node))) {
    out += ":";
  }
  return out;
}

bool IsMacroExpression(Node lhs) {
  if (lhs.kind() == NT::Id) {
    std::string_view name = NameData(Node_name(lhs));
    return name.ends_with("#") || name == "span_inc" || name == "span_dec" ||
           name == "span_diff";
  }
  return false;
}

Node PrattParseExprCall(Lexer* lexer, Node lhs, const TK& tk,
                        uint32_t precedence) {
  if (IsMacroExpression(lhs)) {
    Node out = NodeNew(NT::MacroInvoke);
    Node args = ParseMacroArgList(lexer, false);
    NodeInitMacroInvoke(out, NameNew(FullName(lhs)), args, tk.comments,
                        tk.srcloc);
    NodeFree(lhs);  // we are not using the Id node anymore
    return out;
  }
  Node out = NodeNew(NT::ExprCall);

  ASSERT(tk.kind == TK_KIND::PAREN_OPEN, "");
  Node args = ParseFunArgsList(lexer, false);
  NodeInitExprCall(out, lhs, args, tk.comments, tk.srcloc);
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

Node ParseTypeList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = ParseTypeExpr(lexer);
  Node_next(out) = ParseTypeList(lexer, true);
  return out;
}

Node ParseTypeExpr(Lexer* lexer) {
  const TK tk = lexer->Next();

  if (tk.kind == TK_KIND::BASE_TYPE) {
    Node out = NodeNew(NT::TypeBase);
    NodeInitTypeBase(out, BASE_TYPE_KIND_FromString(tk.text), tk.comments,
                     tk.srcloc);
    return out;
  } else if (tk.kind == TK_KIND::DEREF_OR_POINTER_OP) {
    Node out = NodeNew(NT::TypePtr);
    Node pointee = ParseTypeExpr(lexer);
    uint16_t bits = tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
    NodeInitTypePtr(out, pointee, bits, tk.comments, tk.srcloc);
    return out;
  } else if (tk.kind == TK_KIND::SQUARE_OPEN) {
    Node out = NodeNew(NT::TypeVec);
    Node dim = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::SQUARE_CLOSED);
    Node type = ParseTypeExpr(lexer);
    NodeInitTypeVec(out, dim, type, tk.comments, tk.srcloc);
    return out;
  } else if (tk.text.starts_with("span")) {
    Node out = NodeNew(NT::TypeSpan);
    lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
    Node type = ParseTypeExpr(lexer);
    lexer->MatchOrDie(TK_KIND::PAREN_CLOSED);
    uint16_t bits = tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
    NodeInitTypeSpan(out, type, bits, tk.comments, tk.srcloc);
    return out;
  } else if (tk.kind == TK_KIND::ID) {
    return tk.text.starts_with("$") ? MakeNodeMacroId(tk) : MakeNodeId(tk);
  } else if (tk.kind == TK_KIND::KW) {
    NT nt = KeywordToNT(tk.text);
    ASSERT(nt != NT::invalid, tk);
    switch (nt) {
      case NT::TypeUnion: {
        Node out = NodeNew(NT::TypeUnion);
        lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
        uint16_t bits = tk.text.ends_with("!") ? Mask(BF::UNTAGGED) : 0;
        Node types = ParseTypeList(lexer, false);
        NodeInitTypeUnion(out, types, bits, tk.comments, tk.srcloc);
        return out;
      }
      case NT::TypeFun: {
        Node out = NodeNew(NT::TypeFun);
        lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
        Node params = ParseFunParamList(lexer, false);
        Node result = ParseTypeExpr(lexer);
        NodeInitTypeFun(out, params, result, tk.comments, tk.srcloc);
        return out;
      }
      case NT::TypeUnionDelta: {
        std::array<Node, 4> args = {kNodeInvalid,
                                    kNodeInvalid,  //
                                    kNodeInvalid, kNodeInvalid};
        Node out = NodeNew(NT::TypeUnionDelta);
        ParseFunLikeArgs(lexer, "TT", &args);
        NodeInitTypeUnionDelta(out, args[0], args[1], tk.comments, tk.srcloc);
        return out;
      }
      case NT::TypeOf: {
        std::array<Node, 4> args = {kNodeInvalid,
                                    kNodeInvalid,  //
                                    kNodeInvalid, kNodeInvalid};
        Node out = NodeNew(NT::TypeOf);
        ParseFunLikeArgs(lexer, "E", &args);
        NodeInitTypeOf(out, args[0], tk.comments, tk.srcloc);
        return out;
      }
      default:
        ASSERT(false, tk);
        return kNodeInvalid;
    }
  } else {
    ASSERT(false, "NYI TypeExpr " << tk);
    return kNodeInvalid;
  }
}

Node PrattParseExpr(Lexer* lexer, uint32_t precedence) {
  const TK tk = lexer->Next();
  // std::cout << "@@PRATT START " << tk << "\n";
  const PrattHandlerPrefix& prefix_handler =
      PREFIX_EXPR_PARSERS[uint8_t(tk.kind)];
  ASSERT(prefix_handler.handler != nullptr, "No handler for " << tk);
  Node lhs = prefix_handler.handler(lexer, tk, prefix_handler.precedence);
  while (true) {
    TK tk = lexer->Peek();

    const PrattHandlerInfix& infix_handler =
        INFIX_EXPR_PARSERS[uint8_t(tk.kind)];
    // std::cout << "@@PRATT LOOP prec=" << precedence << " " << tk
    //            << infix_handler.precedence << "\n";
    if (precedence >= infix_handler.precedence) {
      // std::cout << "@@PRATT DONE\n";
      break;
    }

    lexer->Skip();
    lhs = infix_handler.handler(lexer, lhs, tk, infix_handler.precedence);
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
  const TK tk = lexer->Peek();
  if (MaybeTypeExprStart(tk)) {
    return ParseTypeExpr(lexer);
  } else {
    return PrattParseExpr(lexer);
  }
}

Node ParseMacroArgList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  Node out = ParseTypeExprOrExpr(lexer);

  Node next = ParseMacroArgList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseMacroArgListWithColon(Lexer* lexer, uint32_t outer_col,
                                bool want_comma) {
  if (lexer->Match(TK_KIND::COLON)) {
    Node stmts = ParseStmtBodyList(lexer, outer_col);
    Node body = NodeNew(NT::EphemeralList);
    NodeInitEphemeralList(body, stmts, Mask(BF::COLON), kStrInvalid,
                          kSrcLocInvalid);
    return body;
  }

  if (want_comma) {
    lexer->Match(TK_KIND::COMMA) || lexer->Match(TK_KIND::ASSIGN);
  }
  Node out = ParseTypeExprOrExpr(lexer);
  Node_next(out) = ParseMacroArgListWithColon(lexer, outer_col, true);
  return out;
}

Node ParseModParamList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchIdOrDie();
  TK kind = lexer->MatchIdOrDie();
  Node out = NodeNew(NT::ModParam);
  NodeInitModParam(out, NameNew(name.text),
                   MOD_PARAM_KIND_FromString(kind.text), name.comments,
                   name.srcloc);
  Node next = ParseModParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseFunParamList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchIdOrDie();
  Node type = ParseTypeExpr(lexer);
  Node out = NodeNew(NT::FunParam);

  NodeInitFunParam(out, NameNew(name.text), type, BitsFromAnnotation(name),
                   name.comments, name.srcloc);
  Node next = ParseFunParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseCaseList(Lexer* lexer, int cond_column) {
  TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.srcloc.col <= cond_column) {
    return kNodeInvalid;
  }
  ASSERT(tk.text == "case", "");
  lexer->Skip();
  uint32_t case_column = tk.srcloc.col;
  Node out = NodeNew(NT::Case);
  Node cond = PrattParseExpr(lexer);
  lexer->MatchOrDie(TK_KIND::COLON);
  Node body = ParseStmtBodyList(lexer, case_column);
  NodeInitCase(out, cond, body, tk.comments, tk.srcloc);
  Node_next(out) = ParseCaseList(lexer, cond_column);
  return out;
}

Node ParseStmtSpecial(Lexer* lexer, const TK& tk) {
  uint32_t outer_col = tk.srcloc.col;
  if (tk.text == "set") {
    Node lhs = PrattParseExpr(lexer);
    TK op = lexer->Next();
    Node rhs = PrattParseExpr(lexer);
    if (op.kind == TK_KIND::ASSIGN) {
      Node out = NodeNew(NT::StmtAssignment);
      NodeInitStmtAssignment(out, lhs, rhs, tk.comments, tk.srcloc);
      return out;
    } else {
      Node out = NodeNew(NT::StmtCompoundAssignment);
      BINARY_EXPR_KIND kind = ASSIGNMENT_KIND_FromString(op.text);
      NodeInitStmtCompoundAssignment(out, kind, lhs, rhs, tk.comments,
                                     tk.srcloc);
      return out;
    }
  } else if (tk.text == "tryset") {
    return ParseMacroInvocation(lexer, tk);
  } else if (tk.text == "while") {
    return ParseMacroInvocation(lexer, tk);
  } else if (tk.text == "for") {
    return ParseMacroInvocation(lexer, tk);
  } else if (tk.text.starts_with("trylet")) {
    Node out = NodeNew(NT::MacroInvoke);
    //
    const TK name = lexer->MatchIdOrDie();
    Node var = MakeNodeId(name);
    Node type = ParseTypeExpr(lexer);
    lexer->MatchOrDie(TK_KIND::ASSIGN);
    Node expr = PrattParseExpr(lexer);
    lexer->MatchOrDie(TK_KIND::COMMA);
    const TK name2 = lexer->MatchIdOrDie();
    Node var2 = MakeNodeId(name2);
    lexer->MatchOrDie(TK_KIND::COLON);
    Node stmts = ParseStmtBodyList(lexer, outer_col);
    Node body = NodeNew(NT::EphemeralList);
    NodeInitEphemeralList(body, stmts, Mask(BF::COLON), kStrInvalid,
                          kSrcLocInvalid);
    //
    Node_next(var) = type;
    Node_next(type) = expr;
    Node_next(expr) = var2;
    Node_next(var2) = body;
    NodeInitMacroInvoke(out, NameNew(tk.text), var, tk.comments, tk.srcloc);
    return out;
  } else {
    ASSERT(false, tk);
    return kNodeInvalid;
  }
}

Node ParseStmt(Lexer* lexer) {
  TK tk = lexer->Next();
  uint32_t outer_column = tk.srcloc.col;
  const NT nt = KeywordToNT(tk.text);
  switch (nt) {
    case NT::StmtReturn: {
      Node expr = kNodeInvalid;
      if (lexer->Peek().srcloc.line == tk.srcloc.line) {
        expr = PrattParseExpr(lexer);
      } else {
        expr = NodeNew(NT::ValVoid);
        NodeInitValVoid(expr, kStrInvalid, kSrcLocInvalid);
      }
      Node out = NodeNew(NT::StmtReturn);
      NodeInitStmtReturn(out, expr, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtCond: {
      lexer->MatchOrDie(TK_KIND::COLON);
      Node out = NodeNew(NT::StmtCond);
      Node cases = ParseCaseList(lexer, outer_column);
      NodeInitStmtCond(out, cases, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtAssignment: {
      Node lhs = PrattParseExpr(lexer);
      const TK op = lexer->Next();
      if (op.kind == TK_KIND::ASSIGN) {
        Node out = NodeNew(NT::StmtAssignment);
        Node rhs = PrattParseExpr(lexer);
        NodeInitStmtAssignment(out, lhs, rhs, tk.comments, tk.srcloc);
        return out;
      } else {
        ASSERT(op.kind == TK_KIND::COMPOUND_ASSIGN, "" << op);
        ASSERT(false, "NYI");
        return kNodeInvalid;
      }
    }
    case NT::DefVar: {
      Node out = NodeNew(NT::DefVar);
      const TK name = lexer->MatchIdOrDie();
      Node type = kNodeInvalid;
      Node init = kNodeInvalid;
      if (lexer->Match(TK_KIND::ASSIGN)) {
        type = NodeNew(NT::TypeAuto);
        NodeInitTypeAuto(type, kStrInvalid, kSrcLocInvalid);
        init = PrattParseExpr(lexer);
      } else {
        type = ParseTypeExpr(lexer);
        if (lexer->Match(TK_KIND::ASSIGN)) {
          init = PrattParseExpr(lexer);
        } else {
          init = NodeNew(NT::ValAuto);
          NodeInitValAuto(init, kStrInvalid, kSrcLocInvalid);
        }
      }

      uint16_t bits = BitsFromAnnotation(tk);
      bits |= tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
      NodeInitDefVar(out, NameNew(name.text), type, init, bits, tk.comments,
                     tk.srcloc);
      return out;
    }
    case NT::StmtIf: {
      Node out = NodeNew(NT::StmtIf);
      Node cond = PrattParseExpr(lexer);
      lexer->MatchOrDie(TK_KIND::COLON);
      Node body_t = ParseStmtBodyList(lexer, outer_column);
      Node body_f = kNodeInvalid;
      const TK else_tk = lexer->Peek();
      if (else_tk.text == "else" && else_tk.srcloc.col == outer_column) {
        lexer->Skip();
        lexer->MatchOrDie(TK_KIND::COLON);
        body_f = ParseStmtBodyList(lexer, outer_column);
      }
      NodeInitStmtIf(out, cond, body_t, body_f, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtDefer: {
      Node out = NodeNew(NT::StmtDefer);
      lexer->MatchOrDie(TK_KIND::COLON);
      Node body = ParseStmtBodyList(lexer, outer_column);
      NodeInitStmtDefer(out, body, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtBlock: {
      Node out = NodeNew(NT::StmtBlock);
      Name label = NameNew("");
      if (!lexer->Match(TK_KIND::COLON)) {
        label = NameNew(lexer->Next().text);
        lexer->MatchOrDie(TK_KIND::COLON);
      }
      Node body = ParseStmtBodyList(lexer, outer_column);
      NodeInitStmtBlock(out, label, body, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtBreak: {
      Node out = NodeNew(NT::StmtBreak);
      Name label = kNameInvalid;
      if (lexer->Peek().srcloc.line == tk.srcloc.line) {
        label = NameNew(lexer->Next().text);
      }
      NodeInitStmtBreak(out, label, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtContinue: {
      Node out = NodeNew(NT::StmtContinue);
      Name label = kNameInvalid;
      if (lexer->Peek().srcloc.line == tk.srcloc.line) {
        label = NameNew(lexer->Next().text);
      }
      NodeInitStmtContinue(out, label, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtExpr: {
      Node out = NodeNew(NT::StmtExpr);
      Node expr = PrattParseExpr(lexer);
      NodeInitStmtExpr(out, expr, tk.comments, tk.srcloc);
      return out;
    }
    case NT::StmtTrap: {
      Node out = NodeNew(NT::StmtTrap);
      NodeInitStmtTrap(out, tk.comments, tk.srcloc);
      return out;
    }
    case NT::MacroFor: {
      Node out = NodeNew(NT::MacroFor);
      TK name = lexer->MatchIdOrDie();
      TK container = lexer->MatchIdOrDie();
      lexer->MatchOrDie(TK_KIND::COLON);
      Node body = ParseStmtBodyList(lexer, outer_column);
      NodeInitMacroFor(out, NameNew(name.text), NameNew(container.text), body,
                       tk.comments, tk.srcloc);
      return out;
    }
    default:
      return ParseStmtSpecial(lexer, tk);
  }
}
Node ParseExprList(Lexer* lexer, uint32_t outer_column) {
  const TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.srcloc.col <= outer_column) {
    return kNodeInvalid;
  }
  Node out = PrattParseExpr(lexer);
  Node_next(out) = ParseExprList(lexer, true);
  return out;
}

Node ParseMacroInvocation(Lexer* lexer, TK name) {
  uint32_t outer_column = name.srcloc.col;
  Node args = kNodeInvalid;
  if (lexer->Match(TK_KIND::PAREN_OPEN)) {
    args = ParseMacroArgList(lexer, false);
  } else {
    args = ParseMacroArgListWithColon(lexer, outer_column, false);
  }

  Node out = NodeNew(NT::MacroInvoke);
  NodeInitMacroInvoke(out, NameNew(name.text), args, name.comments,
                      name.srcloc);
  return out;
}

Node ParseStmtList(Lexer* lexer, uint32_t column) {
  const TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.srcloc.col < column) {
    return kNodeInvalid;
  }
  Node out = kNodeInvalid;
  if (tk.kind == TK_KIND::ID) {
    lexer->Skip();
    if (tk.text.ends_with("#")) {
      out = ParseMacroInvocation(lexer, tk);

    } else {
      // This happens when the macro body contains macro parameter
      ASSERT(tk.text.starts_with("$"), tk);
      out = MakeNodeMacroId(tk);
    }
  } else {
    ASSERT(tk.kind == TK_KIND::KW, tk);
    // if (tk.comments != StrInvalid)
    //   std::cout << "@@ " << tk.text << " >>>>" << StrData(tk.comments);
    out = ParseStmt(lexer);
  }
  Node_next(out) = ParseStmtList(lexer, column);
  return out;
}

Node ParseStmtBodyList(Lexer* lexer, uint32_t outer_column) {
  const TK tk = lexer->Peek();
  if (tk.kind == TK_KIND::SPECIAL_EOF || tk.srcloc.col <= outer_column) {
    return kNodeInvalid;
  }

  return ParseStmtList(lexer, tk.srcloc.col);
}

Node ParseRecFieldList(Lexer* lexer, uint32_t column) {
  TK name = lexer->Peek();

  if (name.kind == TK_KIND::SPECIAL_EOF || name.srcloc.col <= column) {
    return kNodeInvalid;
  }
  name = lexer->MatchIdOrDie();
  Node type = ParseTypeExpr(lexer);
  Node out = NodeNew(NT::RecField);
  NodeInitRecField(out, NameNew(name.text), type, name.comments, name.srcloc);
  Node_next(out) = ParseRecFieldList(lexer, column);
  return out;
}

Node ParseEnumFieldList(Lexer* lexer, uint32_t column) {
  TK name = lexer->Peek();

  if (name.kind == TK_KIND::SPECIAL_EOF || name.srcloc.col <= column) {
    return kNodeInvalid;
  }
  name = lexer->MatchIdOrDie();
  Node val = PrattParseExpr(lexer);
  Node out = NodeNew(NT::EnumVal);
  NodeInitEnumVal(out, NameNew(name.text), val, name.comments, name.srcloc);
  Node_next(out) = ParseEnumFieldList(lexer, column);
  return out;
}

Node ParseMacroParamList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::PAREN_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchIdOrDie();
  TK kind = lexer->MatchIdOrDie();
  Node out = NodeNew(NT::MacroParam);
  NodeInitMacroParam(out, NameNew(name.text),
                     MACRO_PARAM_KIND_FromString(kind.text), name.comments,
                     name.srcloc);
  Node next = ParseMacroParamList(lexer, true);
  Node_next(out) = next;
  return out;
}

Node ParseMacroGenIdList(Lexer* lexer, bool want_comma) {
  if (lexer->Match(TK_KIND::SQUARE_CLOSED)) {
    return kNodeInvalid;
  }
  if (want_comma) {
    lexer->Match(TK_KIND::COMMA);
  }
  TK name = lexer->MatchIdOrDie();
  Node out = MakeNodeMacroId(name);
  Node_next(out) = ParseMacroGenIdList(lexer, true);
  return out;
}

Node ParseTopLevel(Lexer* lexer) {
  const TK tk = lexer->Next();
  ASSERT(tk.kind == TK_KIND::KW, "expected top level kw");
  NT nt = KeywordToNT(tk.text);
  uint32_t outer_column = tk.srcloc.col;
  uint16_t bits = BitsFromAnnotation(tk);
  switch (nt) {
    case NT::DefFun: {
      Node out = NodeNew(NT::DefFun);
      TK name = lexer->MatchIdOrDie();
      lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
      Node params = ParseFunParamList(lexer, false);
      Node result = kNodeInvalid;
      // the result type must not be omitted because
      // we do require it for `funtype` as well
      result = ParseTypeExpr(lexer);
      lexer->MatchOrDie(TK_KIND::COLON);
      Node body = ParseStmtBodyList(lexer, outer_column);
      NodeInitDefFun(out, NameNew(name.text), params, result, body,
                     BitsFromAnnotation(tk), tk.comments, tk.srcloc);
      return out;
    }
    case NT::DefGlobal: {
      Node out = NodeNew(NT::DefGlobal);
      const TK name = lexer->MatchIdOrDie();
      Node type = kNodeInvalid;
      Node init = kNodeInvalid;
      if (lexer->Match(TK_KIND::ASSIGN)) {
        type = NodeNew(NT::TypeAuto);
        NodeInitTypeAuto(type, kStrInvalid, kSrcLocInvalid);
        init = PrattParseExpr(lexer);
      } else {
        type = ParseTypeExpr(lexer);
        if (lexer->Match(TK_KIND::ASSIGN)) {
          init = PrattParseExpr(lexer);
        } else {
          init = NodeNew(NT::ValAuto);
          NodeInitValAuto(init, kStrInvalid, kSrcLocInvalid);
        }
      }
      bits |= tk.text.ends_with("!") ? Mask(BF::MUT) : 0;
      NodeInitDefGlobal(out, NameNew(name.text), type, init, bits, tk.comments,
                        tk.srcloc);
      return out;
    }
    case NT::DefRec: {
      Node out = NodeNew(NT::DefRec);
      TK name = lexer->MatchIdOrDie();
      lexer->MatchOrDie(TK_KIND::COLON);
      Node fields = ParseRecFieldList(lexer, outer_column);
      NodeInitDefRec(out, NameNew(name.text), fields, BitsFromAnnotation(tk),
                     tk.comments, tk.srcloc);
      return out;
    }

    case NT::Import: {
      TK name = lexer->MatchIdOrDie();
      Node args = kNodeInvalid;
      std::string_view path = std::string_view();
      if (lexer->Match(TK_KIND::ASSIGN)) {
        const TK tk = lexer->Next();
        path = tk.text;
      }
      if (lexer->Match(TK_KIND::PAREN_OPEN)) {
        args = ParseMacroArgList(lexer, false);
      }
      Node out = NodeNew(NT::Import);
      NodeInitImport(out, NameNew(name.text),
                     path.size() == 0 ? kStrInvalid : StrNew(path), args,
                     tk.comments, tk.srcloc);
      return out;
    }
    case NT::DefEnum: {
      Node out = NodeNew(NT::DefEnum);
      const TK name = lexer->MatchIdOrDie();
      const TK base_type = lexer->Peek();
      lexer->MatchOrDie(TK_KIND::BASE_TYPE);
      BASE_TYPE_KIND bt = BASE_TYPE_KIND_FromString(base_type.text);
      lexer->MatchOrDie(TK_KIND::COLON);
      Node items = ParseEnumFieldList(lexer, outer_column);
      NodeInitDefEnum(out, NameNew(name.text), bt, items, bits, tk.comments,
                      tk.srcloc);
      return out;
    }
    case NT::DefType: {
      Node out = NodeNew(NT::DefType);
      const TK name = lexer->MatchIdOrDie();
      lexer->MatchOrDie(TK_KIND::ASSIGN);
      Node type = ParseTypeExpr(lexer);
      NodeInitDefType(out, NameNew(name.text), type, bits, tk.comments,
                      tk.srcloc);
      return out;
    }
    case NT::StmtStaticAssert: {
      Node out = NodeNew(NT::StmtStaticAssert);
      Node cond = PrattParseExpr(lexer);
      NodeInitStmtStaticAssert(out, cond, StrNew(""), tk.comments, tk.srcloc);
      return out;
    }
    case NT::DefMacro: {
      Node out = NodeNew(NT::DefMacro);
      const TK name = lexer->Next();
      if (name.kind == TK_KIND::ID) {
        ASSERT(name.text.ends_with("#") || name.text == "span_inc" ||
                   name.text == "span_dec" || name.text == "span_diff",

               name);
      } else {
        ASSERT(name.kind == TK_KIND::KW, EnumToString(tk.kind) << " " << name);
        ASSERT(name.text == "for" || name.text == "while" ||
                   name.text == "tryset" || name.text == "trylet" ||
                   name.text == "trylet!" || name.text == "ptr_diff",
               name);
      }
      const TK kind = lexer->MatchIdOrDie();
      MACRO_RESULT_KIND mrk = MACRO_RESULT_KIND_FromString(kind.text);

      lexer->MatchOrDie(TK_KIND::PAREN_OPEN);
      Node params = ParseMacroParamList(lexer, false);
      lexer->MatchOrDie(TK_KIND::SQUARE_OPEN);
      Node gen_ids = ParseMacroGenIdList(lexer, false);
      lexer->MatchOrDie(TK_KIND::COLON);
      Node body = kNodeInvalid;
      if (mrk == MACRO_RESULT_KIND::TYPE || mrk == MACRO_RESULT_KIND::EXPR ||
          mrk == MACRO_RESULT_KIND::EXPR_LIST) {
        body = ParseExprList(lexer, outer_column);
      } else {
        body = ParseStmtBodyList(lexer, outer_column);
      }
      NodeInitDefMacro(out, NameNew(name.text), mrk, params, gen_ids, body,
                       bits, tk.comments, tk.srcloc);
      return out;
    }
    default:
      ASSERT(false, tk.text);
      return kNodeInvalid;
  }
}

Node ParseModBodyList(Lexer* lexer, uint32_t column) {
  if (lexer->Peek().kind == TK_KIND::SPECIAL_EOF) {
    return kNodeInvalid;
  }

  Node top = ParseTopLevel(lexer);
  Node next = ParseModBodyList(lexer, column);
  Node_next(top) = next;
  return top;
}
}  // namespace

// Could probably done with C++20 designated array initializers
void InitParser() {
  // NodeInit Prefix Table
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
  // NodeInit Infix/Postfix Table
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

Node ParseDefMod(Lexer* lexer, Name name) {
  const TK tk = lexer->Peek();
  ASSERT(tk.text == "module", "");
  lexer->Skip();
  //
  Node def_mod = NodeNew(NT::DefMod);
  Node params = kNodeInvalid;
  if (lexer->Match(TK_KIND::PAREN_OPEN)) {
    params = ParseModParamList(lexer, false);
  }
  lexer->MatchOrDie(TK_KIND::COLON);
  Node body = ParseModBodyList(lexer, 0);
  NodeInitDefMod(def_mod, name, params, body, BitsFromAnnotation(tk),
                 tk.comments, tk.srcloc);
  return def_mod;
}

}  // namespace cwerg::fe