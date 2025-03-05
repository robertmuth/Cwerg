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
 // input is assumed to have a trailing zero byte
  LexerRaw(std::string_view input, uint32_t file_id)
      : input_(input), end_(input.size()) {
    srcloc_.file = file_id;
  }

  const SrcLoc& GetSrcLoc() { return srcloc_; }

  int LinesProcessed() { return line_no_; }

  TK_RAW Next();
};

struct TK {
  TK_KIND kind = TK_KIND::INVALID;
  std::string_view text;
  SrcLoc srcloc;
  Str comments;
  uint32_t annotation_bits;
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

  TK Peek() {
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

  // Use after Peek
  void Skip() {
    ASSERT(peek_cached_.kind != TK_KIND::INVALID, "");
    peek_cached_.kind = TK_KIND::INVALID;
  }

  TK Next() {
    if (peek_cached_.kind != TK_KIND::INVALID) {
      current_ = peek_cached_;
      peek_cached_.kind = TK_KIND::INVALID;
    } else {
      std::string comments;
      current_.annotation_bits = 0;

      TK_RAW tk = lexer_raw_.Next();
      while (tk.kind == TK_KIND::COMMENT) {
        ASSERT(tk.text[0] == ';', "");
        comments += tk.text;
        tk = lexer_raw_.Next();
      }
      while (tk.kind == TK_KIND::ANNOTATION) {
        if (current_.annotation_bits == 0) {
          current_.srcloc = lexer_raw_.GetSrcLoc();
        }

        current_.annotation_bits |= 1 << uint32_t(BF_FromString(tk.text));
        tk = lexer_raw_.Next();
      }
      if (current_.annotation_bits == 0) {
        current_.srcloc = lexer_raw_.GetSrcLoc();
      }
      current_.kind = tk.kind;
      current_.text = tk.text;
      if (comments.empty()) {
        current_.comments = Str(0);
      } else {
        current_.comments = StrNew(comments);
      }
    }
    return current_;
  }

  int LinesProcessed() { return lexer_raw_.LinesProcessed(); }
};

}  // namespace cwerg::fe
