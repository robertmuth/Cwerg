#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <map>

#include "FE/cwast_gen.h"
#include "Util/assert.h"

namespace cwerg::fe {
class IdGen {
 private:
  std::map<uint32_t, uint32_t> last_used_seq_;

  void RegistereStrAndSeq(const StrAndSeq& ss) {
    if (ss.seq > last_used_seq_[ss.name]) {
      last_used_seq_[ss.name] = ss.seq;
    }
  }

 public:
  Name NameNewNext(uint32_t offset) {
    auto it = last_used_seq_.find(offset);
    ASSERT(it != last_used_seq_.end(), "");
    ++it->second;
    return NameNew(offset, it->second);
  }

  Name NameNewNext(Name name) {
    const auto& ss = NameStrAndSeq(name);
    return NameNewNext(ss.name);
  }

  Name NameNewNext(std::string_view name) {
    uint32_t offset = gNamePool.Intern(name, 1);
    return NameNewNext(offset);
  }

  IdGen() {}

  IdGen(Node fun, const SymTab* symtab) {
    for (const auto& kv : *symtab) {
      RegistereStrAndSeq(kv.first);
    }

    auto visitor = [this, symtab](Node node, Node parent) {
      switch (Node_kind(node)) {
        case NT::DefVar:
        case NT::Id:
          RegistereStrAndSeq(NameStrAndSeq(Node_name(node)));
          break;
        default:
          break;
      }
    };

    VisitNodesRecursivelyPost(fun, visitor, kNodeInvalid);
  }
};

class IdGenCache {
 private:
  std::map<Node, IdGen*> cache_;

 public:
  IdGenCache() {}

  IdGen* Get(Node fun, const SymTab* symtab) {
    auto it = cache_.find(fun);
    if (it != cache_.end()) {
      return it->second;
    }
    IdGen* id_gen = new IdGen(fun, symtab);
    cache_[fun] = id_gen;
    return id_gen;
  }
};

}  // namespace cwerg::fe
