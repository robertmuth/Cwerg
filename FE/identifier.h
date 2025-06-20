#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <map>

#include "FE/cwast_gen.h"
#include "Util/assert.h"

namespace cwerg::fe {
class IdGen {
 private:
  std::map<Name, uint32_t> last_used_seq_;

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
