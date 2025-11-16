#include "FE/lexer.h"

#include <array>
#include <cstdint>
#include <iostream>
#include <string_view>
#include <vector>

#include "Util/assert.h"
#include "Util/immutable.h"

namespace cwerg::fe {
namespace {

const int kCTypeWhitespace = 1;
const int kCTypeOperator = 2;
const int kCTypeNumberStart = 4;
const int kCTypeNumberRest = 8;
const int kCTypeNameStart = 16;
const int kCTypeNameRest = 32;

std::array<uint8_t, 256> InitCType() {
  std::array<uint8_t, 256> out;
  for (uint8_t c : " \t\n") {
    out[c] |= kCTypeWhitespace;
  }
  //
  out['_'] |= kCTypeNameStart | kCTypeNameRest;

  for (uint8_t x = 0; x < 26; x++) {
    out['a' + x] |= kCTypeNameStart | kCTypeNameRest;
    out['A' + x] |= kCTypeNameStart | kCTypeNameRest;
  }
  for (uint8_t x = 0; x < 10; x++) {
    out['0' + x] |= kCTypeNameRest;
  }
  // Number
  for (uint8_t c : ".-+01234567890") {
    out[c] |= kCTypeNumberStart | kCTypeNumberRest;
  }
  for (uint8_t c : "xpabcdef_rstuin") {
    out[c] |= kCTypeNumberRest;
  }
  return out;
}

const std::array<uint8_t, 256> CType = InitCType();

bool IsWhitespace(uint8_t c) { return CType[c] & kCTypeWhitespace; }

// bool IsOperator(uint8_t c) { return CType[c] & kCTypeOperator; }

bool IsNumberStart(uint8_t c) { return CType[c] & kCTypeNumberStart; }

bool IsNumberRest(uint8_t c) { return CType[c] & kCTypeNumberRest; }

bool IsNameStart(uint8_t c) { return CType[c] & kCTypeNameStart; }

bool IsNameRest(uint8_t c) { return CType[c] & kCTypeNameRest; }

typedef std::array<uint8_t, 129> TrieNode;

}  // namespace

LexerStats LexerRaw::stats;

// Below is bunch of adhoc lexer helpers
// These are quite horrible and the only excuse for them
// is that they let us do without a depenency on a lexer library,
uint32_t LexerRaw::HandleNum() {
  uint32_t i = pos_;
  if (!IsNumberStart(input_[i])) return 0;
  i++;
  while (IsNumberRest(input_[i])) {
    i++;
  }
  return i - pos_;
}

#define HANDLE_ID_COMPONENT                  \
  if (!IsNameStart(c = input_[i])) return 0; \
  i++;                                       \
  while (IsNameRest(c = input_[i])) {        \
    i++;                                     \
  }

uint32_t LexerRaw::HandleMacroId() {
  uint32_t i = pos_;
  if (input_[i] != '$') return 0;
  i++;
  uint8_t c;
  HANDLE_ID_COMPONENT
  return i - pos_;
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
  uint8_t c;
  HANDLE_ID_COMPONENT
  if (c == '#') return i + 1 - pos_;
  if (c != ':') return i - pos_;
  // no out-of- bound access assuming zero or newline padding
  c = input_[i + 1];
  if (c == ':') {
    i += 2;
  } else if (IsNameStart(c)) {
    seen_single_colon = true;
    i += 1;
  } else {
    return i - pos_;
  }

  // middle component
  HANDLE_ID_COMPONENT

  if (c == '#') return i + 1 - pos_;
  if (c != ':') return i - pos_;
  if (seen_single_colon) return i - pos_;
  i++;
  if (!IsNameStart(input_[i])) return i - 1 - pos_;
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

uint32_t LexerRaw::HandleSimpleStr() {
  uint32_t i = pos_;
  uint8_t first = input_[i];
  i++;
  if (first == 'r' || first == 'x') {
    i++;
    while (input_[i] != '"') {
      i++;
    }
    return i + 1 - pos_;
  } else {
    bool skip_next = false;
    for (; i < end_; i++) {
      if (skip_next) {
        skip_next = false;
      } else {
        uint8_t c = input_[i];
        if (c == '\\') {
          skip_next = true;
        } else if (c == '"') {
          return i + 1 - pos_;
          break;
        }
        ASSERT(c != '\n', "");
      }
    }
  }
  ASSERT(false, "");
  return 0;
}

uint32_t LexerRaw::HandleGenericAnnotation() {
  uint32_t i = pos_ + 2;
  while (input_[i] != '}') {
    i++;
  }
  ASSERT(input_[i + 1] == '}', "");
  return i + 2 - pos_;
}

TK_RAW LexerRaw::HandleMultiStr() {
  uint32_t i = pos_;
  uint8_t first = input_[i];
  i += 3 + (first != '"');
  uint32_t quotes_in_row = 0;
  bool skip_next = false;
  while (i < end_) {
    uint8_t c = input_[i];
    i++;
    col_no_++;
    if (skip_next) {
      continue;
    }
    if (c == '\n') {
      quotes_in_row = 0;
      line_no_++;
      col_no_ = 0;
    } else if (c == '"') {
      quotes_in_row++;
      if (quotes_in_row == 3) {
        std::string_view token = input_.substr(pos_, i - pos_);
        pos_ = i;
        return TK_RAW{TK_KIND::STR, token};
      }
    } else {
      quotes_in_row = 0;
      if (first == '"' && c == '\\') {
        skip_next = true;
      }
    }
  }
  ASSERT(false, "");
  return TK_RAW{TK_KIND::INVALID};
}

TK_RAW LexerRaw::Next() {
  uint8_t c;
  while (IsWhitespace(c = input_[pos_])) {
    pos_++;
    if (pos_ >= input_.size()) {
      // fix issue with "return [eof]"
      line_no_++;
      srcloc_.col = col_no_;
      srcloc_.line = line_no_ + 1;
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
      uint8_t first = input_[pos_];
      uint32_t i = first == '"' ? pos_ : pos_ + 1;
      bool triple =
          input_[i] == '"' && input_[i + 1] == '"' && input_[i + 2] == '"';
      if (triple) {
        return HandleMultiStr();
      }
      result.size = HandleSimpleStr();
    } else if (result.kind == TK_KIND::CHAR) {
      result.size = HandleChar();
    } else if (result.kind == TK_KIND::GENERIC_ANNOTATION) {
      result.size = HandleGenericAnnotation();
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

std::ostream& operator<<(std::ostream& os, const TK& tk) {
  os << tk.srcloc << " " << EnumToString(tk.kind) << " [" << tk.text << "]";
  if (tk.annotation_bits != 0) {
    std::string_view sep = "";
    os << "{";
    for (int i = 0; i < 32; ++i) {
      if (((1 << i) & tk.annotation_bits) != 0) {
        BF bf = BF(i);
        os << sep << EnumToString(bf);
        sep = ", ";
      }
    }
    os << "}";
  }

  return os;
}

}  // namespace cwerg::fe
