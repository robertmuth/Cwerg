#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <cstdint>
#include <string_view>
#include <vector>

#include "Util/assert.h"

namespace cwerg::fe {

void InitLexer();

struct SrcLoc {
  uint32_t line;
  uint32_t col;
  uint32_t file;
};

enum class TK_KIND : uint8_t {
  INVALID = 0,
  KW,
  COMPOUND_ASSIGN,
  OTHER_OP,
  PREFIX_OP,
  ANNOTATION,
  ASSIGN,
  COLON,
  COMMA,
  PAREN_OPEN,
  PAREN_CLOSED,
  CURLY_OPEN,
  CURLY_CLOSED,
  SQUARE_OPEN,
  SQUARE_OPEN_EXCL,
  SQUARE_CLOSED,
  // These just match the prefix of the lexeme
  COMMENT,
  GENERIC_ANNOTATION,
  CHAR,
  STR,
  NUM,
  ID,
  SPECIAL_EOF,
};

extern const char* EnumToString(TK_KIND x);

struct TK_RAW {
  TK_KIND kind;
  std::string_view text = std::string_view();
};

class LexerRaw {
 private:
  SrcLoc srcloc_;
  std::string_view input_;
  uint32_t line_no_ = 0;
  uint32_t col_no_ = 0;
  uint32_t pos_ = 0;
  const uint32_t end_;

  uint32_t HandleId();
  uint32_t HandleMacroId();
  uint32_t HandleNum();
  uint32_t HandleSimpleStr();
  uint32_t HandleChar();
  uint32_t HandleGenericAnnotation();
  TK_RAW HandleMultiStr();

 public:
  LexerRaw(std::string_view input, uint32_t file_id);

  const SrcLoc& GetSrcLoc() { return srcloc_; }

  TK_RAW Next();
};

struct TK {
  TK_KIND kind = TK_KIND::INVALID;
  std::string_view text;
  SrcLoc sl;
  std::vector<std::string_view> comments;
  std::vector<std::string_view> annotations;
};

class Lexer {
 private:
  LexerRaw lexer_raw_;
  TK peek_cached_;
  TK current_;

 public:
  Lexer(std::string_view input, uint32_t file_id)
      : lexer_raw_(input, file_id) {}

  const TK& peek() {
    if (peek_cached_.kind == TK_KIND::INVALID) {
      peek_cached_ = next();
    }
    return peek_cached_;
  }

  bool match(TK_KIND kind, std::string_view text) {
    peek();
    if (kind == peek_cached_.kind &&
        (text.empty() || text == peek_cached_.text)) {
      peek_cached_.kind = TK_KIND::INVALID;
      return true;
    }
    return false;
  }

  bool match_or_die(TK_KIND kind, std::string_view text) {
    peek();
    if (kind == peek_cached_.kind &&
        (text.empty() || text == peek_cached_.text)) {
      peek_cached_.kind = TK_KIND::INVALID;
      return true;
    }
    ASSERT(false, "");
    return false;
  }

  const TK& next() {
    if (peek_cached_.kind != TK_KIND::INVALID) {
      current_ = peek_cached_;
      peek_cached_.kind = TK_KIND::INVALID;
    } else {
      current_.comments.clear();
      TK_RAW tk = lexer_raw_.Next();
      while (tk.kind == TK_KIND::COMMENT) {
        current_.comments.push_back(tk.text);
        tk = lexer_raw_.Next();
      }
      while (tk.kind == TK_KIND::ANNOTATION) {
        current_.annotations.push_back(tk.text);
        if (current_.annotations.empty()) {
          current_.sl = lexer_raw_.GetSrcLoc();
        }
        tk = lexer_raw_.Next();
      }
      if (current_.annotations.empty()) {
        current_.sl = lexer_raw_.GetSrcLoc();
      }
      current_.kind = tk.kind;
      current_.text = tk.text;
    }
    return current_;
  }
};

}  // namespace cwerg::fe
