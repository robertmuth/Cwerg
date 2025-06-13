#include "Util/parse.h"

#include <iostream>
#include <string>

#include "Util/assert.h"

using namespace cwerg;
using namespace std;

void EmitId(string_view s) { cout << "{" << s << "}"; }

void EmitString(string_view s) {
  if (s.size() == 2) {
    cout << s;
    return;
  }

  char buffer[4 * 1024];
  ASSERT(s.size() < sizeof(buffer), "string too large");

  uint32_t size = EscapedStringToBytes({s.data() + 1, s.size() - 2}, buffer);
  if (size == 0) {
    cout << "@FAILED@";
    return;
  }

  char buffer2[4 * 1024];
  size = BytesToEscapedString({buffer, size}, buffer2);
  buffer2[size] = 0;
  cout << "\"" << buffer2 << "\"";
}

std::vector<std::string_view> split(const std::string_view& s, char delim) {
  std::vector<std::string_view> out;
  int token_start = -1;
  for (int i = 0; i < s.size(); ++i) {
    char c = s[i];
    if (c == delim) {
      if (token_start >= 0) {
        out.push_back(s.substr(token_start, i - token_start));
        token_start = -1;
      }
    } else if (token_start < 0) {
      token_start = i;
    }
  }
  if (token_start >= 0) {
    out.push_back(s.substr(token_start, s.size() - token_start));
  }
  return out;
}

int main(int argc, char* argv[]) {
  std::string mode = argv[1];
  for (string line; getline(std::cin, line);) {
    cout << "\n" << line << "\n";
    std::vector<std::string_view> vec;
    if (mode == "lex") {
      if (!ParseLineWithStrings(line.c_str(), false, &vec)) {
        cout << "@FAILED@\n\n";
        continue;
      }
      const char* sep = "";
      for (const string_view& s : vec) {
        cout << sep;
        sep = " ";
        ASSERT(s.size() > 0, "");
        if (s[0] == '"') {
          EmitString(s);
        } else {
          EmitId(s);
        }
      }
      cout << "\n";
    } else {
      ASSERT(mode == "num", "");
      std::vector<std::string_view> vec = split(line, ' ');
      if (vec.size() == 2) {
        char buf[32];
        if (vec[0] == "int64") {
          cout << "[INT64] ";
          auto val = ParseInt<int64_t>(vec[1]);
          if (!val.has_value()) {
            cout << "@BAD VALUE@\n";
            continue;
          }
          cout << ToDecSignedString(val.value(), buf) << " "
               << ToHexString(val.value(), buf) << "\n";
        } else if (vec[0] == "uint64") {
          cout << "[UINT64] ";
          auto val = ParseInt<uint64_t>(vec[1]);
          if (!val.has_value()) {
            cout << "@BAD VALUE@\n";
            continue;
          }
          cout << ToDecString(val.value(), buf) << " "
               << ToHexString(val.value(), buf) << "\n";
        } else if (vec[0] == "flt64") {
          cout << "[FLT64] ";
          auto val = ParseFlt64(vec[1]);
          if (!val.has_value()) {
            cout << "@BAD VALUE@\n";
            continue;
          }
          cout << ToFltString(val.value(), buf) << " "
               << ToFltHexString(val.value(), buf) << "\n";
        } else if (vec[0] == "char") {
          cout << "[CHAR] ";
          auto val = ParseChar(vec[1]);
          if (!val.has_value()) {
            cout << "@BAD VALUE@\n";
            continue;
          }
          cout << val.value() << "\n";
        }
      }
    }
  }
  return 0;
}
