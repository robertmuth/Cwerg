#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <cstdint>
#include <string_view>
#include <vector>

// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/lexer_gen.h"
#include "Util/assert.h"

namespace cwerg::fe {

void InitLexer();

struct SrcLoc {
  uint32_t line;
  uint32_t col;
  uint32_t file;
};

std::ostream& operator<<(std::ostream& os, const SrcLoc& sl);

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
  Str comments;
  std::vector<std::string_view> annotations;
};

std::ostream& operator<<(std::ostream& os, const TK& tk);

class Lexer {
 private:
  LexerRaw lexer_raw_;
  TK peek_cached_;
  TK current_;

 public:
  Lexer(std::string_view input, uint32_t file_id)
      : lexer_raw_(input, file_id) {}

  const TK& Peek() {
    if (peek_cached_.kind == TK_KIND::INVALID) {
      peek_cached_ = Next();
    }
    return peek_cached_;
  }

  bool Match(TK_KIND kind, std::string_view text = std::string_view()) {
    Peek();
    if (kind == peek_cached_.kind &&
        (text.empty() || text == peek_cached_.text)) {
      peek_cached_.kind = TK_KIND::INVALID;
      return true;
    }
    return false;
  }

  TK MatchOrDie(TK_KIND kind, std::string_view text = std::string_view()) {
    Peek();
    if (kind == peek_cached_.kind &&
        (text.empty() || text == peek_cached_.text)) {
      current_ = peek_cached_;
      peek_cached_.kind = TK_KIND::INVALID;
      return current_;
    }
    ASSERT(false, "expected: " << EnumToString(kind) << " " << text << " got "
                               << peek_cached_);
    return current_;
  }

  const TK& Next() {
    if (peek_cached_.kind != TK_KIND::INVALID) {
      current_ = peek_cached_;
      peek_cached_.kind = TK_KIND::INVALID;
    } else {
      std::vector<std::string_view> comments;
      current_.annotations.clear();
      TK_RAW tk = lexer_raw_.Next();
      while (tk.kind == TK_KIND::COMMENT) {
        comments.push_back(tk.text);
        tk = lexer_raw_.Next();
      }
      while (tk.kind == TK_KIND::ANNOTATION) {
        if (current_.annotations.empty()) {
          current_.sl = lexer_raw_.GetSrcLoc();
        }
        current_.annotations.push_back(tk.text);
        tk = lexer_raw_.Next();
      }
      if (current_.annotations.empty()) {
        current_.sl = lexer_raw_.GetSrcLoc();
      }
      current_.kind = tk.kind;
      current_.text = tk.text;
      if (comments.empty()) {
        current_.comments = Str(0);
      } else {
        std::string s;
        for (std::string_view sv : comments) {
          ASSERT(sv[0] == ';', "");
          s += sv;
        }
        current_.comments = StrNew(s);
      }
    }
    return current_;
  }
};

}  // namespace cwerg::fe
