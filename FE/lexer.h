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

struct TK_RAW {
  TK_KIND kind;
  std::string_view text = std::string_view();
};

struct LexerStats{
  uint32_t num_files = 0;
  uint32_t num_lines = 0;
};

class LexerRaw {
 private:
  SrcLoc srcloc_;
  std::string_view input_;
  uint32_t line_no_ = 1;
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
  // TODO: access to this should synchonized so we can "lex" in parallel
  static LexerStats stats;

  // input is assumed to have a trailing zero byte
  LexerRaw(std::string_view input, Name file_id)
      : input_(input), end_(input.size()) {
    srcloc_.file = file_id;
  }

  ~LexerRaw() {
    stats.num_files++;
    stats.num_lines += line_no_;
  }


  const SrcLoc& GetSrcLoc() { return srcloc_; }

  int LinesProcessed() { return line_no_; }

  TK_RAW Next();
};

struct TK {
  std::string_view text;
  TK_KIND kind = TK_KIND::INVALID;
  SrcLoc srcloc;
  Str comments = kStrInvalid;
  uint32_t annotation_bits;
};

extern std::ostream& operator<<(std::ostream& os, const TK& tk);

class Lexer {
 private:
  LexerRaw lexer_raw_;
  bool peek_valid_ = false;
  TK peek_cached_;

 public:
  Lexer(std::string_view input, Name file_id)
      : lexer_raw_(input, file_id) {}

  TK Peek() {
    if (!peek_valid_) {
      peek_cached_ = Next();
      peek_valid_ = true;
    }
    return peek_cached_;
  }

  int LinesProcessed() { return lexer_raw_.LinesProcessed(); }


  bool Match(TK_KIND kind, std::string_view text = std::string_view()) {
    Peek();
    if (kind == peek_cached_.kind &&
        (text.empty() || text == peek_cached_.text)) {
      peek_valid_ = false;
      return true;
    }
    return false;
  }

  void MatchOrDie(TK_KIND kind) {
    Peek();
    if (kind == peek_cached_.kind) {
      peek_valid_ = false;
      return;
    }
    ASSERT(false, "expected: " << EnumToString(kind) << " " << " got "
                               << peek_cached_);
    abort();
  }

  TK MatchIdOrDie() {
    Peek();
    if (TK_KIND::ID == peek_cached_.kind) {
      peek_valid_ = false;
      return peek_cached_;
    }
    ASSERT(false, "expected ID: " << " got " << peek_cached_);
    abort();
    return peek_cached_;
  }
  // Use after Peek
  void Skip() {
    ASSERT(peek_valid_, "");
    peek_valid_ = false;
  }

  TK Next() {
    if (peek_valid_) {
      peek_valid_ = false;
      return peek_cached_;
    } else {
      TK current;

      std::string comments;
      current.annotation_bits = 0;

      TK_RAW tk = lexer_raw_.Next();
      while (tk.kind == TK_KIND::COMMENT) {
        ASSERT(tk.text[0] == ';', "");
        comments += tk.text;
        tk = lexer_raw_.Next();
      }
      while (tk.kind == TK_KIND::ANNOTATION) {
        if (current.annotation_bits == 0) {
          current.srcloc = lexer_raw_.GetSrcLoc();
        }

        current.annotation_bits |= 1 << uint32_t(BF_FromString(tk.text));
        tk = lexer_raw_.Next();
      }
      if (current.annotation_bits == 0) {
        current.srcloc = lexer_raw_.GetSrcLoc();
      }
      current.kind = tk.kind;
      current.text = tk.text;

      if (comments.empty()) {
        current.comments = Str(0);
      } else {
        current.comments = StrNew(comments);
      }
      return current;
    }
  }
};

}  // namespace cwerg::fe
