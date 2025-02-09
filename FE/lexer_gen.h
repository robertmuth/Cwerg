#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>

#include "FE/cwast_gen.h"

namespace cwerg::fe {

/* @AUTOGEN-START@ */

enum class TK_KIND : uint8_t {
  INVALID = 0,
  COMPARISON_OP = 1,
  SHIFT_OP = 2,
  ADD_OP = 3,
  MUL_OP = 4,
  OR_SC_OP = 5,
  AND_SC_OP = 6,
  DEREF_OR_POINTER_OP = 7,
  ADDR_OF_OP = 8,
  PREFIX_OP = 9,
  BASE_TYPE = 10,
  KW = 11,
  KW_SIMPLE_VAL = 12,
  ANNOTATION = 13,
  ASSIGN = 14,
  SQUARE_OPEN = 15,
  CURLY_OPEN = 16,
  GENERIC_ANNOTATION = 17,
  TERNARY_OP = 18,
  DOT_OP = 19,
  COMPOUND_ASSIGN = 20,
  COLON = 21,
  COMMA = 22,
  PAREN_OPEN = 23,
  PAREN_CLOSED = 24,
  CURLY_CLOSED = 25,
  SQUARE_CLOSED = 26,
  COMMENT = 27,
  CHAR = 28,
  STR = 29,
  NUM = 30,
  ID = 31,
  SPECIAL_EOF = 32,
};
/* @AUTOGEN-END@ */

extern const char* EnumToString(TK_KIND x);

extern BINARY_EXPR_KIND BINARY_EXPR_KIND_FromString(std::string_view s,
                                                    TK_KIND kind);

struct Result {
  TK_KIND kind = TK_KIND::INVALID;
  uint32_t size = 0;
};

Result FindInTrie(std::string_view needle);

}  // namespace cwerg::fe