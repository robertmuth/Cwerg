#include "FE/lexer.h"

#include <array>
#include <cstdint>
#include <iostream>
#include <string_view>
#include <vector>

#include "Util/assert.h"
#include "Util/immutable.h"

namespace cwerg::fe {

const int kCTypeWhitespace = 1;
const int kCTypeOperator = 2;
const int kCTypeNumberStart = 4;
const int kCTypeNumberRest = 8;
const int kCTypeNameStart = 16;
const int kCTypeNameRest = 32;

const char* const TK_KIND_TO_STR[] = {
    "INVALID",
    "KW",
    "COMPOUND_ASSIGN",
    "OTHER_OP",
    "PREFIX_OP",
    "ANNOTATION",
    "ASSIGN",
    "COLON",
    "COMMA",
    "PAREN_OPEN",
    "PAREN_CLOSED",
    "CURLY_OPEN",
    "CURLY_CLOSED",
    "SQUARE_OPEN",
    "SQUARE_OPEN_EXCL",
    "SQUARE_CLOSED",
    // These just match the prefix of the lexeme
    "COMMENT",
    "GENERIC_ANNOTATION",
    "CHAR",
    "STR",
    "NUM",
    "ID",
    "SPECIAL_EOF",
};

const char* EnumToString(TK_KIND x) { return TK_KIND_TO_STR[int(x)]; }

uint8_t CType[256];

void InitLexer() {
  for (uint8_t c : " \t\n") {
    CType[c] |= kCTypeWhitespace;
  }
  //
  CType['_'] |= kCTypeNameStart | kCTypeNameRest;

  for (uint8_t x = 0; x < 26; x++) {
    CType['a' + x] |= kCTypeNameStart | kCTypeNameRest;
    CType['A' + x] |= kCTypeNameStart | kCTypeNameRest;
  }
  for (uint8_t x = 0; x < 10; x++) {
    CType['0' + x] |= kCTypeNameRest;
  }
  // Number
  for (uint8_t c : ".-+01234567890") {
    CType[c] |= kCTypeNumberStart;
  }
  //
}

bool IsWhitespace(uint8_t c) { return CType[c] & kCTypeWhitespace; }

bool IsOperator(uint8_t c) { return CType[c] & kCTypeOperator; }

bool IsNumberStart(uint8_t c) { return CType[c] & kCTypeNumberStart; }

bool IsNumberRest(uint8_t c) { return CType[c] & kCTypeNumberRest; }

bool IsNameStart(uint8_t c) { return CType[c] & kCTypeNameStart; }

bool IsNameRest(uint8_t c) { return CType[c] & kCTypeNameRest; }

typedef std::array<uint8_t, 129> TrieNode;

struct Result {
  TK_KIND kind = TK_KIND::INVALID;
  uint32_t size = 0;
};

extern uint8_t TrieNodeCount;
extern uint8_t KeywordAndOpRecognizer[][128];

Result FindInTrie(std::string_view needle) {
  uint32_t node_no = 0;
  for (uint32_t i = 0; i < uint32_t(needle.size()); ++i) {
    uint8_t c = uint8_t(needle[i]);
    if (c > 127) {
      c = 127;
    }

    uint8_t x = KeywordAndOpRecognizer[node_no][c];

    // std::cout << "Find [" << i << "] [" << c << "] -> " << int(x) << "\n";

    if (x == 0) {
      return Result();
    } else if (x < TrieNodeCount) {
      node_no = x;
    } else {
      x -= TrieNodeCount;
      if (x & 1) {
        return Result{TK_KIND(x >> 1), i};
      } else {
        return Result{TK_KIND(x >> 1), i + 1};
      }
    }
  }
  return Result();
}

LexerRaw::LexerRaw(std::string_view input, uint32_t file)
    : input_(input), end_(input.size()) {
  srcloc_.file = file;
}

uint32_t LexerRaw::HandleNum() { return 0; }

#define HANDLE_ID_COMPONENT              \
  if (!IsNameStart(input_[i])) return 0; \
  i++;                                   \
  while (IsNameRest(input_[i])) {        \
    i++;                                 \
  }

uint32_t LexerRaw::HandleMacroId() {
  uint32_t i = pos_;
  if (input_[i] != '$') return 0;
  i++;
  HANDLE_ID_COMPONENT
  return i;
}

// examples
// a
// a#
// a::b
// a:b
// a::b:c
uint32_t LexerRaw::HandleId() {
  bool seen_single_colon = false;

  uint32_t i = pos_;

  HANDLE_ID_COMPONENT
  const uint8_t c = input_[i];
  if (c == '#') return i + 1 - pos_;
  if (c != ':') return i - pos_;
  // no out-of- bound access assuming zero or newline padding
  const uint8_t d = input_[i + 1];
  if (d == ':') {
    i += 2;
  } else if (IsNameStart(d)) {
    seen_single_colon = true;
    i += 1;
  } else {
    return i - pos_;
  }

  // middle component
  HANDLE_ID_COMPONENT

  if (c == '#') return i + 1 - pos_;
  if (c != ':') return i - pos_;
  if (seen_single_colon) return i;
  i++;
  HANDLE_ID_COMPONENT
  return i - pos_;
}

uint32_t LexerRaw::HandleChar() {
  bool skip_next = false;
  for (uint32_t i = pos_ + 1; i < end_; i++) {
    if (skip_next) {
      skip_next = false;
    } else {
      uint8_t c = input_[i];
      if (c == '\\') {
        skip_next = true;
      } else if (c == '\'') {
        return i + 1 - pos_;
        break;
      }
      ASSERT(c != '\n', "");
    }
  }
  ASSERT(false, "");
  return 0;
}

#if 0
      uint32_t i = pos_;
      uint8_t first = input_[i];
      i++;
      if (first == 'r' || first == 'x') {
        i++;
      }
      bool skip_next = false;
      for (; i < end_; i++) {
        if (skip_next) {
          skip_next = false;
        } else {
          uint8_t c = input_[i];
        }
#endif

TK_RAW LexerRaw::Next() {
  uint8_t c;
  while (IsWhitespace(c = input_[pos_])) {
    pos_++;
    if (pos_ >= input_.size()) {
      return TK_RAW{TK_KIND::SPECIAL_EOF};
    }
    col_no_++;
    if (c == '\n') {
      col_no_ = 0;
      line_no_++;
    }
  }
  // freeze SrcLoc
  srcloc_.col = col_no_;
  srcloc_.line = line_no_;
  //
  Result result = FindInTrie(input_.substr(pos_));
  // std::cout << "Trie search result " << result.size << "\n";

  if (result.size == 0) {
    uint8_t c = input_[pos_];
    if (IsNumberStart(c)) {
      ASSERT(false, "NYI NUM");
      result.kind = TK_KIND::NUM;
      result.size = HandleNum();
    } else {
      result.kind = TK_KIND::ID;
      result.size = (c == '$') ? HandleMacroId() : HandleId();
    }
  } else {
    if (result.kind == TK_KIND::COMMENT) {
      result.size = end_ - pos_;
      for (uint32_t i = pos_ + 1; i < end_; i++) {
        if (input_[i] == '\n') {
          result.size = i + 1 - pos_;
          break;
        }
      }
    } else if (result.kind == TK_KIND::STR) {
      ASSERT(false, "NYI STR");
    } else if (result.kind == TK_KIND::CHAR) {
      result.size = HandleChar();
    } else if (result.kind == TK_KIND::GENERIC_ANNOTATION) {
      for (uint32_t i = pos_ + 2; i < end_; i++) {
        uint8_t c = input_[i];
        if (c == '}') {
          ASSERT(input_[i + 1] != '}', "");
          result.size = i + 2 - pos_;
          break;
        }
        ASSERT(c != '\n', "");
      }
    }
  }
  std::string_view token = input_.substr(pos_, result.size);
  col_no_ += result.size;
  pos_ += result.size;
  if (result.kind == TK_KIND::COMMENT) {
    col_no_ = 0;
    line_no_++;
  } else if (result.kind == TK_KIND::GENERIC_ANNOTATION) {
    result.kind = TK_KIND::ANNOTATION;
    token = token.substr(2, token.size() - 4);
  }
  return TK_RAW{result.kind, token};
}

}  // namespace cwerg::fe
