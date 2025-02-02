#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <cstdint>

#include <string_view>

namespace cwerg::fe {

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

struct TK_RAW {
  TK_KIND kind;
  std::string_view text = std::string_view();
};

class Trie;  // internal

class LexerRaw {
 private:
  SrcLoc srcloc_;
  std::string_view input_;
  uint32_t line_no_;
  uint32_t col_no_;
  uint32_t pos_;
  const uint32_t end_;
  // hide implementation
  Trie* const trie_;

  uint32 HandleId();
  uint32 HandleNum();

 public:
  LexerRaw(std::string_view input, uint32_t file_id);

  const SrcLoc& GetSrcLoc() { return srcloc_; }

  TK_RAW Next();
};

}  // namespace cwerg::fe
