// (c) Robert Muth - see LICENSE for more info

/*
 Miscellaneous parsing helpers - this is quite adhoc and needs more work
 Part of the problem is that we are trying to avoid pulling a regex lib.
*/
#include "Util/parse.h"
#include "Util/assert.h"

namespace cwerg {
namespace {

char MapEscape(char c) {
  switch (c) {
    // case 'a': return '\a';
    case 'b':
      return '\b';
    case 'f':
      return '\f';
    case 'n':
      return '\n';
    case 'r':
      return '\r';
    case 't':
      return '\t';
    default:
      return c;
  }
}

const constexpr unsigned char IdFirstChars[] =
    "_%$"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

const constexpr unsigned char IdRestChars[] =
    ":0123456789"
    "_%$w/<>,"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

// Note '"' is treated as whitespace
const constexpr unsigned char SpaceChars[] = " \t\r\n\f=";

const constexpr unsigned char HexChars[] = "0123456789abcdefABCDEF";

const constexpr unsigned char NumFirstChars[] = "0123456789-.+";

const constexpr unsigned char OtherChars[] = "#[]\"";

enum CTYPE {
  CTYPE_SPACE = 1 << 1,
  CTYPE_HEX = 1 << 2,
  CTYPE_ID_FIRST = 1 << 3,
  CTYPE_ID_REST = 1 << 4,
  CTYPE_NUM_FIRST = 1 << 5,
  CTYPE_OTHER = 1 << 6,

  CTYPE_LEGIT = CTYPE_SPACE | CTYPE_ID_REST | CTYPE_NUM_FIRST | CTYPE_ID_FIRST |
                CTYPE_OTHER,
};

struct CharTable {
  uint16_t array[256];

  constexpr CharTable() : array() {
    for (int i = 0; i < 256; i++) array[i] = 0;

    for (auto c : IdFirstChars) array[c] |= CTYPE_ID_FIRST;
    for (auto c : IdRestChars) array[c] |= CTYPE_ID_REST;

    for (auto c : NumFirstChars) array[c] |= CTYPE_NUM_FIRST;

    for (auto c : SpaceChars) array[c] |= CTYPE_SPACE;
    for (auto c : HexChars) array[c] |= CTYPE_HEX;
    for (auto c : OtherChars) array[c] |= CTYPE_OTHER;
  }

  bool is(uint8_t c, uint16_t mask) const { return (array[c] & mask) != 0; }
  bool isspace(uint8_t c) const { return is(c, CTYPE_SPACE); }
  bool isidornumstart(uint8_t c) const {
    return is(c, CTYPE_ID_FIRST | CTYPE_NUM_FIRST);
  }
  bool isnumfirst(uint8_t c) const { return is(c, CTYPE_NUM_FIRST); }
  bool ishex(uint8_t c) const { return is(c, CTYPE_HEX); }
  bool isother(uint8_t c) const { return is(c, CTYPE_OTHER); }
  bool islegit(uint8_t c) const { return is(c, CTYPE_LEGIT); }
};

constexpr CharTable Ctype{};

size_t AddOct(std::string_view s, size_t i, char* out) {
  size_t n = std::min(i + 3, s.size());
  char c = 0;
  for (; i < n; ++i) {
    if ('0' > s[i] || s[i] > '7') break;
    c = c * 8 + (s[i] - '0');
  }
  *out = c;
  return i - 1;
}

// Parse two hex digits at position i as a byte and append that byte to out
size_t AddHex(std::string_view s, size_t i, char* out) {
  int a = HexDigit(s[i]);
  if (s[i] == 0 || a < -1) return 0;
  int b = HexDigit(s[i + 1]);
  if (s[i + 1] == 0 || b < -1) return 0;
  *out = a * 16 + b;
  return i + 1;
}

enum Mode {
  BETWEEN_TOKENS,
  IN_TOKEN,
  IN_STRING,
  IN_STRING_AFTER_BS,
  COMMENT,
  ENTER_LIST,
  EXIT_LIST
};

}  // namespace

size_t EscapedStringToBytes(std::string_view s, char* out) {
  size_t n = 0;
  bool escaped = false;
  for (size_t i = 0; i < s.size() && s[i] != 0; ++i) {
    const char c = s[i];
    if (!escaped) {
      if (c == '\\') {
        escaped = true;
      } else {
        out[n++] = c;
      }
      continue;
    }

    escaped = false;
    if ('0' <= c && c <= '7') {
      i = AddOct(s, i, out + n);
      if (i == 0) return 0;
      n++;
    } else if (c == 'x') {
      i = AddHex(s, i + 1, out + n);
      if (i == 0) return 0;
      n++;
    } else {
      out[n++] = MapEscape(c);
    }
  }
  return n;
}

size_t BytesToEscapedString(std::string_view s, char* out) {
  size_t n = 0;
  for (size_t i = 0; i < s.size(); ++i) {
    char c = s[i];
    if (c == '"') {
      out[n++] = '\\';
      out[n++] = '\"';
    } else if (c == '\\') {
      out[n++] = '\\';
      out[n++] = '\\';
    } else if (c == '\n') {
      out[n++] = '\\';
      out[n++] = 'n';
    } else if (' ' <= c && c <= 126) {
      out[n++] = c;
    } else {
      out[n++] = '\\';
      out[n++] = 'x';
      char d = c >> 4;
      out[n++] = HexChars[d & 0xf];
      out[n++] = HexChars[c & 0xf];
    }
  }
  return n;
}

void string_view_inc(std::string_view& s) { s = {s.data(), s.size() + 1}; }

Mode HandleOneChar(Mode mode,
                   const char* cp,
                   std::vector<std::string_view>* out) {
  char c = *cp;
  switch (mode) {
    case EXIT_LIST:
    case ENTER_LIST:
      ASSERT(false, "unreachable");
      return COMMENT;  // unreachable
    case COMMENT:
      string_view_inc(out->back());
      return COMMENT;
    case BETWEEN_TOKENS:
      if (Ctype.isspace(c))
        return BETWEEN_TOKENS;
      else if (Ctype.isidornumstart(c)) {
        out->emplace_back(std::string_view{cp, 0});
      }
      // fallthrough
    case IN_TOKEN:
      if (Ctype.isspace(c)) {
        return BETWEEN_TOKENS;
      } else if (c == '#') {
        out->emplace_back(std::string_view{cp, 1});
        return COMMENT;
      } else if (c == '"') {
        out->emplace_back(std::string_view{cp, 1});
        return IN_STRING;
      } else if (c == '[' || c == ']') {
        out->emplace_back(std::string_view{cp, 1});
        return c == '[' ? ENTER_LIST : EXIT_LIST;
      } else {
        string_view_inc(out->back());
        return IN_TOKEN;
      }
    case IN_STRING:
      string_view_inc(out->back());
      if (c == '"')
        return BETWEEN_TOKENS;
      else if (c == '\\')
        return IN_STRING_AFTER_BS;
      return IN_STRING;
    case IN_STRING_AFTER_BS:
      string_view_inc(out->back());
      return IN_STRING;
  }
  // unreachable - gcc complains
  return IN_STRING;
}

bool ParseLineWithStrings(std::string_view s,
                          bool allow_lists,
                          std::vector<std::string_view>* out) {
  const char* cp = s.data();
  const char* end = cp + s.size();
  Mode mode = BETWEEN_TOKENS;
  bool in_list = false;
  for (; cp < end; ++cp) {
    if (mode == IN_TOKEN || mode == BETWEEN_TOKENS) {
      if (!Ctype.islegit(*cp)) {
        return false;
      }
    }
    mode = HandleOneChar(mode, cp, out);
    if (mode == ENTER_LIST) {
      if (in_list) return false;
      in_list = true;
      mode = BETWEEN_TOKENS;
    } else if (mode == EXIT_LIST) {
      if (!in_list) return false;
      in_list = false;
      mode = BETWEEN_TOKENS;
    }
  }
  if (in_list) return false;
  if (mode != BETWEEN_TOKENS && mode != IN_TOKEN && mode != COMMENT)
    return false;
  return true;
}

bool IsLikelyNum(std::string_view s) {
  ASSERT(s.size() > 0, "");
  return Ctype.isnumfirst(s[0]);
}

static bool IsHex(std::string_view s) {
  return s.size() > 1 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X');
}

std::optional<double> ParseFlt64(std::string_view s) {
  if (IsHex(s)) {
    auto val = ParseInt<uint64_t>(s);
    if (!val) return val;
    union {
      uint64_t val_u;
      double val_d;
    } u = {val.value()};
    return u.val_d;
  }
  ASSERT(s.size() < 63, "");
  char buf[64];
  s.copy(buf, s.size());
  buf[s.size()] = 0;
  char* end;
  double out = strtod(buf, &end);
  if (end != buf + s.size()) return std::nullopt;
  return out;
}

std::optional<int64_t> ParseInt64(std::string_view s) {
  if (IsHex(s)) {
    // ParseInt<int64_t> does not support hex
    return ParseInt<uint64_t>(s);
  }
  return ParseInt<int64_t>(s);
}

std::optional<uint64_t> ParseUint64(std::string_view s) {
  return ParseInt<uint64_t>(s);
}

std::string_view ToDecString(uint64_t v, char buf[32]) {
  size_t i = 0;
  do {
    buf[i++] = '0' + v % 10;
    v = v / 10;
  } while (v != 0);
  buf[i] = 0;
  // reverse
  int start = 0;
  int end = i - 1;
  while (start < end) std::swap(buf[start++], buf[end--]);
  return {buf, i};
}

std::string_view ToDecSignedString(int64_t v, char buf[32]) {
  unsigned offset = 0;
  if (v < 0) {
    buf[0] = '-';
    offset = 1;
    v = -v;  // this also works for -(1 << 63)
  }
  return {buf, ToDecString(v, buf + offset).size() + offset};
}

std::string_view ToHexString(uint64_t v, char buf[32]) {
  size_t i = 0;
  for (int n = 60; n >= 0; n -= 4) {
    int nibble = (v >> n) & 15;
    if (i > 0 || nibble != 0) {
      buf[i++] = nibble <= 9 ? nibble + '0' : nibble + 'a' - 10;
    }
  }
  if (i == 0) {
    buf[i++] = '0';
  }
  buf[i] = 0;
  return {buf, i};
}

std::string_view ToFltString(double val, char buf[32]) {
  // TODO: deal with potential overflow
  auto len = snprintf(buf, 32, "%g", val);
  ASSERT(len < 32, "");
  return {buf, (size_t)len};
}

std::string_view ToFltHexString(double v, char buf[32]) {
  union {
    double val_d;
    uint64_t val_u;
  } u = {v};
  return ToHexString(u.val_u, buf);
}

std::string_view ToHexDataStringWithSep(std::string_view data,
                                        char sep,
                                        char* buf,
                                        size_t max_len) {
  ASSERT(data.size() * 3 <= max_len, "");
  const char* kHexChars = "0123456789abcdef";
  char* cp = buf;
  for (const auto b : data) {
    if (cp != buf) *cp++ = sep;
    *cp++ = kHexChars[(b >> 4) & 0xf];
    *cp++ = kHexChars[b & 0xf];
  }
  *cp = '\0';
  return {buf, size_t(cp - buf)};
}

namespace {
char* append(char* buf, std::string_view s) {
  s.copy(buf, s.size());
  return buf + s.size();
}

template <typename T, typename... Args>
char* append(char* buf, T first, Args... args) {
  return append(append(buf, first), args...);
}

}  // namespace

std::string_view StrCat(char* buf,
                        size_t max_len,
                        std::string_view s0,
                        std::string_view s1,
                        std::string_view s2) {
  size_t len = s0.size() + s1.size() + s2.size();
  ASSERT(len < max_len, "");
  *append(buf, s0, s1, s2) = '\0';
  return {buf, len};
}

std::string_view StrCat(char* buf,
                        size_t max_len,
                        std::string_view s0,
                        std::string_view s1,
                        std::string_view s2,
                        std::string_view s3) {
  size_t len = s0.size() + s1.size() + s2.size() + s3.size();
  ASSERT(len < max_len, "");
  *append(buf, s0, s1, s2, s3) = '\0';
  return {buf, len};
}

std::string_view StrCat(char* buf,
                        size_t max_len,
                        std::string_view s0,
                        std::string_view s1,
                        std::string_view s2,
                        std::string_view s3,
                        std::string_view s4) {
  size_t len = s0.size() + s1.size() + s2.size() + s3.size() + s4.size();
  ASSERT(len < max_len, "");
  *append(buf, s0, s1, s2, s3, s4) = '\0';
  return {buf, len};
}

std::string_view StrCat(char* buf,
                        size_t max_len,
                        std::string_view s0,
                        std::string_view s1,
                        std::string_view s2,
                        std::string_view s3,
                        std::string_view s4,
                        std::string_view s5) {
  size_t len =
      s0.size() + s1.size() + s2.size() + s3.size() + s4.size() + s5.size();
  ASSERT(len < max_len, "");
  *append(buf, s0, s1, s2, s3, s4, s5) = '\0';
  return {buf, len};
}

std::vector<char> SlurpDataFromStream(std::istream* fin) {
  size_t num_bytes_per_read = 1024 * 1024;
  size_t current_offset = 0U;
  std::vector<char> out(num_bytes_per_read);
  auto rdbuf = fin->rdbuf();
  while (true) {
    size_t count =
        rdbuf->sgetn(out.data() + current_offset, num_bytes_per_read);
    if (count == 0) break;
    current_offset += count;
    out.resize(current_offset + num_bytes_per_read);
  }
  out.resize(current_offset);
  return out;
}

double Flt64FromBits(uint64_t i) {
  union {
    uint64_t i;
    double d;
  } u = {i};
  return u.d;
}

uint64_t Flt64ToBits(double d) {
  union {
    double d;
    uint64_t i;
  } u = {d};
  return u.i;
}

bool IsWhiteSpace(char c) { return Ctype.isspace(c); }

int HexDigit(char c) {
  if ('0' <= c && c <= '9') return c - '0';
  if ('a' <= c && c <= 'f') return 10 + c - 'a';
  if ('A' <= c && c <= 'F') return 10 + c - 'A';
  return -1;
}

std::optional<ExpressionOp> ParseExpressionOp(std::string_view expr) {
  const size_t colon_sym = expr.find(':');
  if (colon_sym == std::string_view::npos) return std::nullopt;
  const std::string_view reloc_name = expr.substr(0, colon_sym);
  const std::string_view rest = expr.substr(colon_sym + 1);
  const size_t colon_addend = rest.find(':');
  const std::string_view symbol_name = rest.substr(
      0, colon_addend == std::string_view ::npos ? rest.size() : colon_addend);
  int32_t offset = 0;
  if (colon_addend != std::string_view::npos) {
    auto val = ParseInt<int32_t>(rest.substr(colon_addend + 1));
    if (!val.has_value()) return std::nullopt;
    offset = val.value();
  }
  return ExpressionOp{reloc_name, symbol_name, offset};
}

}  // namespace cwerg
