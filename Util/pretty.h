#pragma once
// (c) Robert Muth - see LICENSE for more info

// see pretty.py for documentation

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

namespace PP {

const size_t INFINITE_WIDTH = 1000000;

enum class BreakType {
  INVALID = 0,
  FITS,
  INCONSISTENT,
  CONSISTENT,
  FORCE_LINE_BREAK
};

enum class TokenType {
  INVALID,
  BEG,
  END,
  BRK,
  STR,
};

struct Token {
  TokenType type;

  union {
    std::string_view str;

    struct {
      ssize_t num_spaces;
      ssize_t offset;
      bool nobreak;
    } brk;

    struct {
      BreakType break_type;
      ssize_t offset;
    } beg;

    struct {
    } end;  // silly but avoids a warning
  };
};

inline Token Brk(ssize_t num_space = 1, ssize_t offset = 0,
                 bool nobreak = false) {
  return {.type = TokenType::BRK, .brk = {num_space, offset, nobreak}};
}

inline Token End() { return {.type = TokenType::END, .end = {}}; }

inline Token Str(std::string_view str) {
  return {.type = TokenType::STR, .str = str};
}

inline Token Beg(BreakType break_type, ssize_t offset) {
  return {.type = TokenType::BEG, .beg = {break_type, offset}};
}

inline Token NoBreak(size_t num_spaces) { return Brk(num_spaces, 0, true); }

inline Token LineBreak(size_t offset = 0) {
  return Brk(INFINITE_WIDTH, offset, false);
}

extern std::string PrettyPrint(const std::vector<Token>& tokens,
                               ssize_t line_width);

}  // namespace PP