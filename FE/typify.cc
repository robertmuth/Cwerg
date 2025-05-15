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


void UpdateType(Node node, CanonType ct) { Node_x_type(node) = ct; }

CanonType AnnotateType(Node node, CanonType ct) {
  ASSERT(Node_x_type(node).isnull(), "");
  UpdateType(node, ct);
  return ct;
}

CanonType TypifyNodeRecursively(Node node, TypeCorpus* tc, CanonType ct_target,
                                PolyMap* poly_map) {
  switch (Node_kind(node)) {
    case NT::TypeBase: {
      return AnnotateType(node,
                          tc->get_base_canon_type(Node_base_type_kind(node)));
    }
    default:
      ASSERT(false, "unsupported node " << EnumToString(Node_kind(node)));
      node = node;
      tc = tc;
      ct_target = ct_target;
      poly_map = poly_map;  // NOLINT
      break;
  }
  return kCanonTypeInvalid;
}

void DecorateASTWithTypes(const std::vector<Node>& mods, TypeCorpus* tc) {
  //  phase 1
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      switch (Node_kind(child)) {
        case NT::DefRec: {
          std::string name;
          name.append(NameData(Node_name(mod)));
          name.append("/");
          name.append(NameData(Node_name(child)));
          CanonType ct = tc->InsertRecType(name, child);
          AnnotateType(child, ct);
          break;
        }
        case NT::DefEnum: {
          std::string name;
          name.append(NameData(Node_name(mod)));
          name.append("/");
          name.append(NameData(Node_name(child)));
          CanonType ct = tc->InsertEnumType(name, child);
          AnnotateType(child, ct);
          break;
        }
        case NT::DefType:
          if (Node_has_flag(child, BF::WRAPPED)) {
            std::string name;
            name.append(NameData(Node_name(mod)));
            name.append("/");
            name.append(NameData(Node_name(child)));
            CanonType ct = tc->InsertWrappedTypePre(name);
            AnnotateType(child, ct);
          }
          break;

        default:
          break;
      }
    }
  }

  //  phase 2
  PolyMap poly_map;

  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      switch (Node_kind(child)) {
        case NT::DefRec: {
          for (Node field = Node_fields(child); !field.isnull();
               field = Node_next(field)) {
            CanonType ct = TypifyNodeRecursively(Node_value_or_auto(field), tc,
                                                 kCanonTypeInvalid, &poly_map);
            AnnotateType(field, ct);
          }
          break;
        }
        case NT::DefEnum: {
          CanonType ct = Node_x_type(child);
          for (Node field = Node_items(child); !field.isnull();
               field = Node_next(field)) {
            TypifyNodeRecursively(Node_value_or_auto(field), tc,
                                  kCanonTypeInvalid, &poly_map);
            AnnotateType(field, ct);
          }
          break;
        }
        case NT::DefType: {
          CanonType ct = TypifyNodeRecursively(Node_type(child), tc,
                                               kCanonTypeInvalid, &poly_map);
          if (Node_has_flag(child, BF::WRAPPED)) {
            tc->InsertWrappedTypeFinalize(Node_x_type(child), ct);
          } else {
            AnnotateType(child, ct);
          }
          break;
        }
        default:
          break;
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