#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>

namespace cwerg::fe {

/* @AUTOGEN-START@ */

enum class TK_KIND : uint8_t {
    INVALID = 0,
    KW = 1,
    ANNOTATION = 2,
    ASSIGN = 3,
    SQUARE_OPEN = 4,
    CURLY_OPEN = 5,
    GENERIC_ANNOTATION = 6,
    DEREF_OR_POINTER_OP = 7,
    ADDR_OF_OP = 8,
    COMPARISON_OP = 9,
    SHIFT_OP = 10,
    ADD_OP = 11,
    MUL_OP = 12,
    OR_SC_OP = 13,
    AND_SC_OP = 14,
    PREFIX_OP = 15,
    BASE_TYPE = 16,
    TERNARY_OP = 17,
    DOT_OP = 18,
    COMPOUND_ASSIGN = 19,
    COLON = 20,
    COMMA = 21,
    PAREN_OPEN = 22,
    PAREN_CLOSED = 23,
    CURLY_CLOSED = 24,
    SQUARE_CLOSED = 25,
    COMMENT = 26,
    CHAR = 27,
    STR = 28,
    NUM = 29,
    ID = 30,
    SPECIAL_EOF = 31,
};
/* @AUTOGEN-END@ */

extern const char* EnumToString(TK_KIND x);

}  // namespace cwerg::fe