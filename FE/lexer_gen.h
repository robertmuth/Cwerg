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
    ANNOTATION = 12,
    ASSIGN = 13,
    SQUARE_OPEN = 14,
    CURLY_OPEN = 15,
    GENERIC_ANNOTATION = 16,
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

extern BINARY_EXPR_KIND BINARY_EXPR_KIND_FromString(std::string_view s,
                                                    TK_KIND kind);

}  // namespace cwerg::fe