#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <cstdint>

namespace cwerg::fe {

/* @AUTOGEN-START@ */

enum class TK_KIND : uint8_t {
    INVALID = 0,
    KW = 1,
    COMPOUND_ASSIGN = 2,
    OTHER_OP = 3,
    PREFIX_OP = 4,
    ANNOTATION = 5,
    ASSIGN = 6,
    COLON = 7,
    COMMA = 8,
    PAREN_OPEN = 9,
    PAREN_CLOSED = 10,
    CURLY_OPEN = 11,
    CURLY_CLOSED = 12,
    SQUARE_OPEN = 13,
    SQUARE_OPEN_EXCL = 14,
    SQUARE_CLOSED = 15,
    COMMENT = 16,
    GENERIC_ANNOTATION = 17,
    CHAR = 18,
    STR = 19,
    BASE_TYPE = 20,
    NUM = 21,
    ID = 22,
    SPECIAL_EOF = 23,
};
/* @AUTOGEN-END@ */

extern const char* EnumToString(TK_KIND x);

}  // namespace cwerg::fe