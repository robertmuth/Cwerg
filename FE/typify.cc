#include "FE/typify.h"

#include <array>
#include <map>

#include "Util/assert.h"

namespace cwerg::fe {

class PolyMap {
 public:
  PolyMap() {}

  void Register(Node fun) { ASSERT(false, ""); }

  Node Resolve(Node callee, CanonType first_param_type) {
    ASSERT(false, "");
    return kNodeInvalid;
  }
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

void UpdateType(Node node, CanonType ct) { Node_x_type(node) = ct; }

CanonType AnnotateType(Node node, CanonType ct) {
  ASSERT(Node_x_type(node).isnull(), "");
  UpdateType(node, ct);
  return ct;
}

void DecorateASTWithTypes(const std::vector<Node>& mods,
                          TypeCorpus* type_corpus) {
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefRec) {
        std::string name;
        name.append(NameData(Node_name(mod)));
        name.append("/");
        name.append(NameData(Node_name(child)));
        CanonType ct = type_corpus->InsertRecType(name, child);
        AnnotateType(child, ct);
      }
    }
  }
//
#if 0
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::DefRec) {
        CanonType ct = Node_x_type(child);
        for (Node field = Node_fields(child); !child.isnull();
             field = Node_next(field)) {
        }
        // type_corpus->FinalizeRecType(ct);
      }
    }
  }
#endif
}

}  // namespace cwerg::fe