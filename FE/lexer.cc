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

uint32_t LexerRaw::HandleNum() { return 0; }

uint32_t LexerRaw::HandleId() { return 0; }

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
  Result result = trie_->Find(input_.substr(pos_));
  if (result.size == 0) {
    uint8_t c = input_[i];
    if (IsNumberStart(c)) {
      result.kind = TK_KIND::NUM;
      result.size = HandleNum();
    } else {
      result.kind = TK_KIND::ID;
      result.size = HandleId();
    }
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
  std::string_view token = input_.substr(result.size);
  col_no_ += result.size;
  pos_ += result.size;
  if (result.kind == TK_KIND::GENERIC_ANNOTATION) {
    result.kind = TK_KIND::ANNOTATION;
    token = token.substr(2, token.size() - 4);
  }
  return TK_RAW{result.kind, token};
}

}  // namespace cwerg::fe
