#include "Util/parse.h"
#include "Util/assert.h"

#include <iostream>
#include <string>

using namespace cwerg;
using namespace std;

void EmitId(string_view s) { cout << "{" << s << "}"; }

void EmitString(string_view s) {
  if (s.size() == 2) {
    cout << s;
    return;
  }


  char buffer[4* 1024];
  ASSERT(s.size() < sizeof(buffer), "string too large");

  uint32_t size = EscapedStringToBytes({s.data() + 1,  s.size() - 2}, buffer);
  if (size == 0) {
    cout << "@FAILED@";
    return;
  }

  char buffer2[4* 1024];
  size = BytesToEscapedString({buffer, size}, buffer2);
  buffer2[size] = 0;
  cout << "\"" << buffer2 << "\"";
}

void EmitNum(string_view s) {
  char buf[64];
  if (s[0] == '-') {
    auto neg = ParseInt<uint64_t>({s.data()+1, s.size() - 1});
    if (neg.has_value()) {
      auto v = neg.value();
      cout << (v == 0 ? PosToHexString(v, buf) : NegToHexString(v, buf)) << "#";
      return;
    }
    auto flt = ParseDouble(s);
    if (flt.has_value()) {
      cout << FltToHexString(flt.value(), buf) << "#";
      return;
    }
  } else {
    auto pos = ParseInt<uint64_t>(s);
    if (pos.has_value()) {
      cout << PosToHexString(pos.value(), buf) << "#";
      return;
    }
    auto flt = ParseDouble(s);
    if (flt.has_value()) {
      cout << FltToHexString(flt.value(), buf) << "#";
      return;
    }
  }

  cout << "@FAILED@";
}

int main() {
  std::vector<string_view> vec;
  for (string line; getline(std::cin, line);) {
    cout << "\n" << line << "\n";
    vec.clear();
    if (!ParseLineWithStrings(line.c_str(), false, &vec)) {
      cout << "@FAILED@\n";
      continue;
    }
    const char* sep = "";
    for (const string_view& s : vec) {
      cout << sep;
      sep = " ";
      ASSERT(s.size() > 0, "");
      if (s[0] == '"') {
        EmitString(s);
      } else if (IsLikelyNum(s)) {
        EmitNum(s);
      } else {
        EmitId(s);
      }
    }
    cout << "\n";
  }
  return 0;
}
