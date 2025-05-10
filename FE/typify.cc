#include "FE/typify.h"

#include <array>
#include <map>

#include "Util/assert.h"

namespace cwerg::fe {

class PolyMap {
 public:
  PolyMap() {}
};



// =======================================
// =======================================

class TypeContext {
  std::array<CanonType, 10> base_type_map_;

  std::map<Name, CanonType> corpus_;

  void insert(CanonType ct) {
    auto it = corpus_.find(CanonType_name(ct));
    ASSERT(it == corpus_.end(), "");

    corpus_[CanonType_name(ct)] = ct;
  }
  void insert_base_type(BASE_TYPE_KIND kind) {}

 public:
  TypeContext() {}
};

TypeCorpus::TypeCorpus(const TargetArchConfig& arch) {}

void DecorateASTWithTypes(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus) {}

}  // namespace cwerg::fe