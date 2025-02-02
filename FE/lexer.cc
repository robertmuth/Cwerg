#include "FE/lexer.h"

#include <array>
#include <cstdint>
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

uint8_t CType[256];

void InitLexer() {
  for (uint8_t c : " \t\n") {
    CType[c] |= kCTypeWhitespace;
  }
  for (uint8_t c : "<>=!*/+-%&|~:.?,") {
    CType[c] |= kCTypeOperator;
  }
  CType['_'] |= kCTypeNameStart | kCTypeNameRest;
  for (uint8_t x = 0; x < 26; x++) {
    CType['a' + x] |= kCTypeNameStart | kCTypeNameRest;
    CType['A' + x] |= kCTypeNameStart | kCTypeNameRest;
  }
  for (uint8_t x = 0; x < 10; x++) {
    CType['0' + x] |= kCTypeNameRest;
  }
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

class Trie {
 public:
  std::vector<TrieNode> nodes_;

  Trie() {}

  Result Find(std::string_view needle) {
    uint32_t node_no = 0;
    for (uint32_t i = 0; i < static_cast<uint32_t>(needle.size()); ++i) {
      uint8_t x = nodes_[node_no][static_cast<uint8_t>(needle[i])];
      if (x == 0) {
        return Result();
      } else if (x < nodes_.size()) {
        node_no = x;
      } else {
        x -= nodes_.size();
        if (x & 1) {
          return Result{TK_KIND(x >> 1), i};
        } else {
          return Result{TK_KIND(x >> 1), i + 1};
        }
      }
    }
    return Result();
  }
};

LexerRaw::LexerRaw(std::string_view input, uint32_t file)
    : input_(input), end_(input.size()) {
  srcloc_.file = file;
}

#if 0
TK_RAW HandleComment(uint32_t start_pos) {
  while (input_[pos_] != '\n' && input_[pos_] != '\0') {
    pos_++;
    col_++;
  }
  if (input_[pos_] != '\n') {
    pos_++;
    col_ = 0;
    line_++;
  }
  return {TK_KIND::COMMENT, start_pos, pos_ - start_pos};
}

TK_RAW HandleNumber(uint32_t start_pos) {
  while (IsNumberRest(input_[pos_])) {
    pos_++;
    col_++;
  }
  return {TK_KIND::NUM, start_pos, pos_ - start_pos};
}

TK_RAW HandleName(uint32_t start_pos) {
  bool seen_single_colon = false;
  bool seen_double_colon = false;
  uint8_t c;
  while (IsNameRest(c = input_[pos_])) {
    pos_++;
    col_++;
  }
  if (c != ':') {
    return {TK_KIND::ID, start_pos, pos_ - start_pos};
  }
}

TK_RAW HandleCharConstant(uint32_t start_pos) {}

TK_RAW HandleStringConstant(uint32_t start_pos) {}

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
  srcloc_.col = col_no_;
  srcloc_.line = line_no_;
  const uint32_t start_pos = pos_;
  Result result = trie_->Find(input_.substr(pos_));
  if (result.size == 0) {
    ASSERT(false, "");
  }
  if (result.kind == TK_KIND::COMMENT) {
    result.size = end_ - pos_;
    for (uint32_t i = pos_ + 1; i < end_; i++) {
      if (input_[i] == '\n') {
        result.size = i + 1 - pos_;
        break;
      }
    }
  } else if (result.kind == TK_KIND::CHAR) {
    bool skip_next = false;
    for (uint32_t i = pos_ + 1; i < end_; i++) {
      if (skip_next) {
        skip_next = false;
      } else {
        uint8_t c = input_[i];
        if (c == '\\') {
          skip_next = true;
        } else if (c == '\'') {
          result.size = i + 1 - pos_;
          break;
        }
        ASSERT(c != '\n', "");
      }
    }
  }

  return TK_RAW{TK_KIND::SPECIAL_EOF};

#if 0
  if (c == '\0') {
    return {TK_KIND::SPECIAL_EOF, std::string_view()};
  }

  if (c == '\'') {
    return HandleCharConstant(start_pos);
  }

  if (c == '-' && input_[pos_ + 1] == '-') {
    return HandleComment(start_pos);
  }
  if (c == '-' || c == '+') {
    if (IsNumberStart(input_[pos_ + 1])) {
      pos_ += 2;
      col_ += 2;
      return HandleNumber(start_pos);
    }
  }
  if (IsNumberStart(c)) {
    pos_++;
    col_++;
    return HandleNumber(start_pos);
  }

  if (IsNameStart(c)) {
    pos_++;
    col_++;
    return HandleName(start_pos);
  }

  if (IsOperator(c)) {
  }
#endif
}

}  // namespace cwerg::fe
