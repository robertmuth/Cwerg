#pragma once
// (c) Robert Muth - see LICENSE for more info

#include <charconv>
#include <iostream>
#include <optional>
#include <string_view>
#include <vector>

namespace cwerg {

// Note, if there is a comment it will always be the last token
extern bool ParseLineWithStrings(std::string_view s,
                                 bool allow_lists,
                                 std::vector<std::string_view>* out);

// returns 0 on error so avoid passing in len = 0 strings
extern size_t EscapedStringToBytes(std::string_view s, char* out);

// buf needs to be at least 4 * size
extern size_t BytesToEscapedString(std::string_view, char* out);

extern bool IsNum(std::string_view s);

extern bool IsLikelyNum(std::string_view s);  // just looks at first char

template <typename INT>
std::optional<INT> ParseInt(std::string_view s) {
  INT out;
  unsigned base = 10;
  if (s.size() > 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) {
    base = 16;
    s.remove_prefix(2);
  }
  const auto last = s.data() + s.size();
  auto result = std::from_chars(s.data(), last, out, base);
  if (result.ptr == last && result.ec == std::errc()) {
    return out;
  }

  return std::nullopt;
}

extern std::optional<double> ParseDouble(std::string_view s);

extern char HexDigit(char c);

// =================================================================================
// Number To Canonical String
// =================================================================================
extern std::string_view ToHexString(uint64_t v, char buf[32]);
extern std::string_view ToDecString(uint64_t v, char buf[32]);

extern std::string_view PosToHexString(uint64_t v, char buf[32]);
extern std::string_view NegToHexString(uint64_t v, char buf[32]);
extern std::string_view FltToHexString(double v, char buf[32]);

extern std::string_view ToHexDataStringWithSep(std::string_view data,
                                               char sep,
                                               char* buf,
                                               size_t max_len);

// =================================================================================
// Misc
// =================================================================================

extern std::string_view StrCat(char* buf,
                               size_t max_len,
                               std::string_view s0,
                               std::string_view s1,
                               std::string_view s2);

extern std::string_view StrCat(char* buf,
                               size_t max_len,
                               std::string_view s0,
                               std::string_view s1,
                               std::string_view s2,
                               std::string_view s3);

extern std::string_view StrCat(char* buf,
                               size_t max_len,
                               std::string_view s0,
                               std::string_view s1,
                               std::string_view s2,
                               std::string_view s3);

extern std::string_view StrCat(char* buf,
                               size_t max_len,
                               std::string_view s0,
                               std::string_view s1,
                               std::string_view s2,
                               std::string_view s3,
                               std::string_view s4);

extern std::string_view StrCat(char* buf,
                               size_t max_len,
                               std::string_view s0,
                               std::string_view s1,
                               std::string_view s2,
                               std::string_view s3,
                               std::string_view s4,
                               std::string_view s5);

// This works well for std::cin
std::vector<char> SlurpDataFromStream(std::istream* fin);

}  // namespace cwerg
