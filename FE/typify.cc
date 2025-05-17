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
  // std::cout << "@@ ID: " << NameData(Node_name(id))
  //           << " t=" << CanonType_name(ct) << "\n";
  if (ct.isnull()) {
    switch (Node_kind(def_node)) {
      case NT::DefVar:
      case NT::DefGlobal:
        ct = TypifyDefGlobalOrDefVar(def_node, tc, pm);
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

Node RecAdvanceField(Node field, Node point) {
  ASSERT(Node_kind(field) == NT::RecField, "");
  ASSERT(Node_kind(point) == NT::ValPoint, "");
  Node field_name = Node_point(point);
  if (Node_kind(field_name) != NT::ValAuto) {
    ASSERT(Node_kind(field_name) == NT::Id, "");
    while (Node_name(field_name) != Node_name(field)) {
      field = Node_next(field);
      ASSERT(!field.isnull(), "");
    }
  }
  return field;
}

void AnnotateFieldWithTypeAndSymbol(Node id, Node field) {
  ASSERT(Node_kind(id) == NT::Id, "");
  ASSERT(Node_kind(field) == NT::RecField, "");
  AnnotateType(id, Node_x_type(field));
  Node_x_symbol(id) = field;
}

CanonType TypifyValCompound(Node node, TypeCorpus* tc, CanonType ct_target,
                            PolyMap* pm) {
  std::cout << "@@ VALCOMP\n";
  CanonType ct =
      TypifyNodeRecursively(Node_type_or_auto(node), tc, ct_target, pm);
  if (CanonType_kind(ct) == NT::TypeVec) {
    CanonType element_type = CanonType_underlying_vec_type(ct);

    for (Node point = Node_inits(node); !point.isnull();
         point = Node_next(point)) {
      ASSERT(Node_kind(point) == NT::ValPoint, "");
      AnnotateType(point, element_type);
      //
      Node val = Node_value_or_undef(point);
      if (Node_kind(val) != NT::ValUndef) {
        TypifyNodeRecursively(val, tc, element_type, pm);
      }
      //
      Node index = Node_point(point);
      CanonType uint_type = tc->get_uint_canon_type();
      if (Node_kind(index) == NT::ValAuto) {
        AnnotateType(index, uint_type);
      } else {
        TypifyNodeRecursively(index, tc, uint_type, pm);
      }
    }
  } else {
    ASSERT(CanonType_kind(ct) == NT::DefRec, "");
    Node defrec = CanonType_ast_node(ct);
    ASSERT(Node_kind(defrec) == NT::DefRec, "");
    Node field = Node_fields(defrec);
    for (Node point = Node_inits(node); !point.isnull();
         point = Node_next(point)) {
      field = RecAdvanceField(field, point);

      CanonType ct_field = Node_x_type(field);
      AnnotateType(point, ct_field);
      if (Node_kind(Node_point(point)) == NT::Id) {
        AnnotateFieldWithTypeAndSymbol(Node_point(point), field);
      }
      if (Node_kind(Node_value_or_undef(point)) != NT::ValUndef) {
        TypifyNodeRecursively(Node_value_or_undef(point), tc, ct_field, pm);
      }
    }
  }
  return AnnotateType(node, ct);
}

CanonType TypifyNodeRecursively(Node node, TypeCorpus* tc, CanonType ct_target,
                                PolyMap* pm) {
  std::cout << "@@ TYPIFY: " << EnumToString(Node_kind(node))
            << " target: " << CanonType_name(ct_target) << "\n";
  if (!Node_x_type(node).isnull()) {
    return Node_x_type(node);
  }
  switch (Node_kind(node)) {
    case NT::Id:
      return TypifyId(node, tc, ct_target, pm);

    case NT::TypeBase:
      return AnnotateType(node,
                          tc->get_base_canon_type(Node_base_type_kind(node)));
    case NT::ValAuto:
    case NT::TypeAuto:
      ASSERT(!ct_target.isnull(), "" << Node_srcloc(node));
      return AnnotateType(node, ct_target);

    case NT::ValTrue:
    case NT::ValFalse:
      return AnnotateType(node, tc->get_bool_canon_type());

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
    case NT::ExprField: {
      CanonType ct =
          TypifyNodeRecursively(Node_container(node), tc, ct_target, pm);
      if (CanonType_kind(ct) != NT::DefRec) {
        CompilerError(Node_srcloc(node)) << "Container is not of type rec";
      }
      Node field_name = Node_field(node);
      Node field_node = CanonType_lookup_rec_field(ct, Node_name(field_name));
      if (field_node.isnull()) {
        CompilerError(Node_srcloc(node))
            << "unknown field name " << Node_name(field_name);
      }
      AnnotateFieldWithTypeAndSymbol(field_name, field_node);
      return AnnotateType(node, Node_x_type(field_node));
    }
    case NT::ValCompound:
      return TypifyValCompound(node, tc, ct_target, pm);

    default:
      ASSERT(false, "unsupported node " << Node_srcloc(node) << " "
                                        << EnumToString(Node_kind(node)));
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