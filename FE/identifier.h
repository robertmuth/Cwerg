#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <string>
#include <unordered_map>

#include "FE/cwast_gen.h"
#include "Util/assert.h"

namespace cwerg::fe {

// same as above but returs std::string
class IdGenIR {
 private:
  std::unordered_map<Name, uint32_t> last_used_seq_;

 public:
  std::string NameNewNext(Name name) {
    uint32_t n = last_used_seq_[name]++;

    std::string buf(NameData(name));
    if (n) {
      buf += ".";
      buf += std::to_string(n);
    }
    return std::string(buf);
  }

  IdGenIR() {}
};

class IdGen {
 private:
  std::unordered_map<Name, uint32_t> last_used_seq_;

 public:
  Name NameNewNext(Name name) {
    uint32_t& n = last_used_seq_[name];
    ++n;
    char buf[1024];
    strcpy(buf, NameData(name));
    sprintf(buf + strlen(buf), "%%%u", n);

    return NameNew(buf);
  }

  IdGen() {}
};

}  // namespace cwerg::fe
