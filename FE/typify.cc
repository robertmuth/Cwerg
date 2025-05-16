#include "FE/typify.h"

#include <array>
#include <cstdint>
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

struct ValAndKind {
  union {
    bool b;
    uint32_t u32;
    uint64_t u64;
    int32_t s32;
    int64_t s64;
    float f32;
    double f64;
  };
  std::string_view cleaned;
  BASE_TYPE_KIND kind;
};

ValAndKind NumCleanupAndTypeExtraction(std::string_view num,
                                       BASE_TYPE_KIND target_kind) {
  ValAndKind out = {.u32 = 0, .cleaned = num, .kind = target_kind};

  for (int i = 2; i <= 4 && i <= num.size(); i++) {
    // std::cout << "@@@ Trying " << num.substr(num.size() - i, i) << "\n" <<
    // std::flush;
    BASE_TYPE_KIND kind =
        BASE_TYPE_KIND_FromString(num.substr(num.size() - i, i));
    if (kind != BASE_TYPE_KIND::INVALID) {
      out.cleaned.remove_suffix(i);
      out.kind = kind;
      return out;
    }
  }
  return out;
}

#if 0
ValAndKind ParseNumRaw(Node num_val, BASE_TYPE_KIND target_kind) {
  std::string_view num = StrData(Node_number(num_val));
  if (num[0] == '\'') {
    ASSERT(false, num);
    return {.u32 = 0, .kind = target_kind};
  }
}
#endif

CanonType TypifyNodeRecursively(Node node, TypeCorpus* tc, CanonType ct_target,
                                PolyMap* pm);

CanonType TypifyDefGlobalOrDefVar(Node node, TypeCorpus* tc, PolyMap* pm) {
  Node initial = Node_initial_or_undef_or_auto(node);
  Node type = Node_type_or_auto(node);

  CanonType ct;
  if (Node_kind(type) == NT::TypeAuto) {
    ASSERT(Node_kind(initial) != NT::ValUndef, "");
    ct = TypifyNodeRecursively(initial, tc, kCanonTypeInvalid, pm);
    TypifyNodeRecursively(type, tc, ct, pm);
  } else {
    ct = TypifyNodeRecursively(type, tc, kCanonTypeInvalid, pm);
    if (Node_kind(initial) != NT::ValUndef) {
      TypifyNodeRecursively(initial, tc, ct, pm);
    }
  }
  return AnnotateType(node, ct);
}

CanonType TypifyId(Node id, TypeCorpus* tc, CanonType ct_target, PolyMap* pm) {
  Node def_node = Node_x_symbol(id);
  CanonType ct = Node_x_type(def_node);

  if (ct.isnull()) {
    switch (Node_kind(def_node)) {
      case NT::DefVar:
      case NT::DefGlobal:
        TypifyDefGlobalOrDefVar(def_node, tc, pm);
        break;
      case NT::DefFun:
        ASSERT(false, "");
        break;
      default:
        ASSERT(false, "");
        break;
    }
  }
  return AnnotateType(id, ct);
}

CanonType TypifyNodeRecursively(Node node, TypeCorpus* tc, CanonType ct_target,
                                PolyMap* pm) {
  std::cout << "@@ TYPIFY: " << EnumToString(Node_kind(node)) << "\n";

  switch (Node_kind(node)) {
    case NT::Id:
      return TypifyId(node, tc, ct_target, pm);

    case NT::TypeBase:
      return AnnotateType(node,
                          tc->get_base_canon_type(Node_base_type_kind(node)));
    case NT::ValAuto:
      ASSERT(!ct_target.isnull(), "");
      return AnnotateType(node, ct_target);

    case NT::ValNum: {
      BASE_TYPE_KIND target = ct_target.isnull()
                                  ? BASE_TYPE_KIND::INVALID
                                  : CanonType_base_type_kind(ct_target);
      BASE_TYPE_KIND actual =
          NumCleanupAndTypeExtraction(StrData(Node_number(node)), target).kind;
      ASSERT(actual != BASE_TYPE_KIND::INVALID,
             "cannot parse " << Node_number(node));
      return AnnotateType(node, tc->get_base_canon_type(actual));
    }
    case NT::TypeSpan: {
      CanonType ct =
          TypifyNodeRecursively(Node_type(node), tc, kCanonTypeInvalid, pm);
      return AnnotateType(node,
                          tc->InsertSpanType(Node_has_flag(node, BF::MUT), ct));
    }
    case NT::Expr2: {
      BINARY_EXPR_KIND kind = Node_binary_expr_kind(node);

      CanonType ct;
      if (ResultIsBool(kind)) {
        ct_target = kCanonTypeInvalid;
      }
      CanonType ct_left =
          TypifyNodeRecursively(Node_expr1(node), tc, ct_target, pm);
      TypifyNodeRecursively(
          Node_expr2(node), tc,
          CanonType_IsNumber(ct_left) ? ct_left : kCanonTypeInvalid, pm);
      if (ResultIsBool(kind)) {
        ct = tc->get_bool_canon_type();
      } else if (kind == BINARY_EXPR_KIND::PDELTA) {
        ct = tc->get_sint_canon_type();
      } else {
        ct = ct_left;
      }
      return AnnotateType(node, ct);
    }
    default:
      ASSERT(false, "unsupported node " << EnumToString(Node_kind(node)));
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
      std::cout << "@@ Phase 2: " << EnumToString(Node_kind(child)) << "\n";

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
            TypifyNodeRecursively(
                Node_value_or_auto(field), tc,
                tc->get_base_canon_type(CanonType_base_type_kind(ct)),
                &poly_map);
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
  //  phase 3
  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      std::cout << "@@ Phase 3: " << EnumToString(Node_kind(child)) << "\n";

      switch (Node_kind(child)) {
        case NT::DefRec:
        case NT::DefEnum:
        case NT::DefType:
        case NT::Import:
          continue;
        case NT::StmtStaticAssert:
          std::cout << "@@" << EnumToString(Node_kind(child)) << " "
                    << EnumToString(Node_kind(Node_cond(child))) << "\n";

          TypifyNodeRecursively(Node_cond(child), tc, tc->get_bool_canon_type(),
                                &poly_map);
          break;

        default:
          break;
      }
    }
  }
}

}  // namespace cwerg::fe