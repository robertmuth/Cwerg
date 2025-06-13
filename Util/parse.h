#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <charconv>
#include <cstdint>
#include <iostream>
#include <optional>
#include <string_view>
#include <vector>

namespace cwerg {

// Note, if there is a comment it will always be the last token
extern bool ParseLineWithStrings(std::string_view s, bool allow_lists,
                                 std::vector<std::string_view>* out);

// returns 0 on error so avoid passing in len = 0 strings
extern size_t EscapedStringToBytes(std::string_view s, char* out);

extern size_t HexStringToBytes(std::string_view s, char* out);

// buf needs to be at least 4 * size
extern size_t BytesToEscapedString(std::string_view, char* out);

extern bool IsNum(std::string_view s);

extern bool IsLikelyNum(std::string_view s);  // just looks at first char

extern double Flt64FromBits(uint64_t i);
extern uint64_t Flt64ToBits(double d);

template <typename INT>
std::optional<INT> ParseInt(std::string_view s) {
  bool neg = s[0] == '-';
  if (neg) {
    s.remove_prefix(1);
  }

  unsigned base = 10;
  if (s.size() > 2 && s[0] == '0') {
    if (s[1] == 'b') {
      base = 2;
      s.remove_prefix(2);
    } else if (s[1] == 'x') {
      base = 16;
      s.remove_prefix(2);
    }
  }
  INT out = 0;
  for (char c : s) {
    INT digit;
    if (c >= '0' && c <= '9') {
      digit = c - '0';
    } else if (c >= 'a' && c <= 'f') {
      digit = c - 'a' + 10;
    } else if (c == '_') {
      continue;
    } else {
      return std::nullopt;
    }

    if (digit >= base) {
      return std::nullopt;
    }
    out = out * base + digit;
  }
  if (neg) {
    out = -out;
  }
  return out;
}

extern std::optional<double> ParseFlt64(std::string_view s);

extern std::optional<uint64_t> ParseChar(std::string_view s);

// =================================================================================
// Number To Canonical String
// =================================================================================
extern std::string_view ToHexString(uint64_t v, char buf[32]);
extern std::string_view ToDecString(uint64_t v, char buf[32]);
extern std::string_view ToDecSignedString(int64_t v, char buf[32]);

extern std::string_view ToFltString(double v, char buf[32]);
extern std::string_view ToFltHexString(double v, char buf[32]);

extern std::string_view ToHexDataStringWithSep(std::string_view data, char sep,
                                               char* buf, size_t max_len);

// =================================================================================
// Misc
// =================================================================================

extern std::string_view StrCat(char* buf, size_t max_len, std::string_view s0,
                               std::string_view s1, std::string_view s2);

extern std::string_view StrCat(char* buf, size_t max_len, std::string_view s0,
                               std::string_view s1, std::string_view s2,
                               std::string_view s3);

extern std::string_view StrCat(char* buf, size_t max_len, std::string_view s0,
                               std::string_view s1, std::string_view s2,
                               std::string_view s3);

extern std::string_view StrCat(char* buf, size_t max_len, std::string_view s0,
                               std::string_view s1, std::string_view s2,
                               std::string_view s3, std::string_view s4);

extern std::string_view StrCat(char* buf, size_t max_len, std::string_view s0,
                               std::string_view s1, std::string_view s2,
                               std::string_view s3, std::string_view s4,
                               std::string_view s5);

// This works well for std::cin
std::vector<char>* SlurpDataFromStream(std::istream* fin);

extern bool IsWhiteSpace(char c);

// returns -1 on failure
extern int HexDigit(char c);

struct ExpressionOp {
  std::string_view reloc_name;
  std::string_view symbol_name;
  int32_t offset;
};

// `expr` looks like
//  expr:call:putchar
//  expr:jump24:skip
//  expr:movw_abs_nc:fmt:0
extern std::optional<ExpressionOp> ParseExpressionOp(std::string_view expr);


}  // namespace cwerg
