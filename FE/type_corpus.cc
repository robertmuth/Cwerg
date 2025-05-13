#include "FE/type_corpus.h"

#include <array>
#include <map>
#include <set>

#include "Util/assert.h"

namespace cwerg::fe {

// =======================================
// CanonType API
// =======================================

struct CanonTypeCore {
  NT node;
  Name name;
  std::vector<CanonType> children;
  bool mut = false;
  bool untagged = false;
  int dim = -1;
  BASE_TYPE_KIND base_type_kind = BASE_TYPE_KIND::INVALID;
  Node ast_node = kNodeInvalid;
};

struct Stripe<CanonTypeCore, CanonType> gCanonTypeCore("CanonTypeCore");

StripeBase* const gAllStripesCanonType[] = {&gCanonTypeCore, nullptr};

struct StripeGroup gStripeGroupCanonType("CanonType", &gAllStripesCanonType[0],
                                         128 * 1024);

Name CanonType_name(CanonType n) { return gCanonTypeCore[n].name; }

bool CanonType_mut(CanonType n) { return gCanonTypeCore[n].mut; }

int CanonType_dim(CanonType n) { return gCanonTypeCore[n].dim; }

NT CanonType_kind(CanonType n) { return gCanonTypeCore[n].node; }

bool CanonType_untagged(CanonType n) { return gCanonTypeCore[n].untagged; }

const std::vector<CanonType>& CanonType_children(CanonType n) {
  return gCanonTypeCore[n].children;
}

CanonType CanonTypeNew() {
  CanonType out = CanonType(gStripeGroupCanonType.New().index());
  return out;
}

CanonType CanonTypeNewBaseType(Name name, BASE_TYPE_KIND base_type) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypePtr, .name = name, .base_type_kind = base_type};
  return out;
}

CanonType CanonTypeNewPtrType(Name name, bool mut, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypePtr, .name = name, .children = {child}, .mut = mut};
  return out;
}

CanonType CanonTypeNewSpanType(Name name, bool mut, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypeSpan, .name = name, .children = {child}, .mut = mut};
  return out;
}

CanonType CanonTypeNewWrappedType(Name name, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::DefType, .name = name, .children = {child}};
  return out;
}

CanonType CanonTypeNewVecType(Name name, int dim, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypeVec, .name = name, .children = {child}, .dim = dim};
  return out;
}

CanonType CanonTypeNewRecType(Name name, Node ast_node) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::DefRec, .name = name, .ast_node = ast_node};
  return out;
}

CanonType CanonTypeNewEnumType(Name name, BASE_TYPE_KIND base_type,
                               Node ast_node) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::DefRec,
                         .name = name,
                         .base_type_kind = base_type,
                         .ast_node = ast_node};

  return out;
}

CanonType CanonTypeNewUnionType(Name name, bool untagged,
                                const std::vector<CanonType>& sorted_children) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::TypeVec,
                         .name = name,
                         .children = sorted_children,
                         .untagged = untagged};

  return out;
}

CanonType CanonTypeNewFunType(Name name,
                              const std::vector<CanonType>& params_result) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypeFun, .name = name, .children = params_result};
  return out;
}
CanonType TypeCorpus::Insert(CanonType ct) {
  ASSERT(corpus_.find(CanonType_name(ct)) == corpus_.end(), "");
  corpus_[CanonType_name(ct)] = ct;
  return ct;
}

Name MakeCanonTypeName(std::string_view main, std::string_view arg1,
                       std::string_view arg2 = std::string_view()) {
  std::string buf;
  buf.append(main);
  buf.append("<");
  buf.append(arg1);
  if (!arg2.empty()) {
    buf.append(",");
    buf.append(arg2);
  }
  buf.append(">");
  return NameNew(buf);
}
Name MakeCanonTypeName(std::string_view main,
                       const std::vector<CanonType> args) {
  std::string buf;
  buf.append(main);
  buf.append("<");

  for (int i = 0; i < args.size(); ++i) {
    buf.append(NameData(CanonType_name(args[i])));
    if (i != args.size() - 1) {
      buf.append(",");
    }
  }
  buf.append(">");
  return NameNew(buf);
}

CanonType TypeCorpus::InsertPtrType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "mut_ptr" : "ptr",
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end(), "") return it->second;
  CanonType out = CanonTypeNewPtrType(name, mut, child);
  return (out);
}

CanonType TypeCorpus::InsertSpanType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "mut_span" : "span",
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end(), "") return it->second;
  CanonType out = CanonTypeNewSpanType(name, mut, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertWrappedType(CanonType child) {
  // TODO uid update
  Name name = MakeCanonTypeName("wrapped", NameData(CanonType_name(child)));
  CanonType out = CanonTypeNewWrappedType(name, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertVecType(int dim, CanonType child) {
  Name name = MakeCanonTypeName("vec", std::to_string(dim),
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end(), "") return it->second;
  CanonType out = CanonTypeNewVecType(name, dim, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertRecType(std::string_view name, Node ast_node) {
  Name n = MakeCanonTypeName("rec", name);
  CanonType out = CanonTypeNewRecType(n, ast_node);
  return Insert(out);
}

CanonType TypeCorpus::InsertEnumType(std::string_view name,
                                     BASE_TYPE_KIND base_type, Node ast_node) {
  Name n = MakeCanonTypeName("enum", name);
  CanonType out = CanonTypeNewEnumType(n, base_type, ast_node);
  return Insert(out);
}

CanonType TypeCorpus::InsertUnionType(
    bool untagged, const std::vector<CanonType>& components) {
  ASSERT(!components.empty(), "");
  auto cmp = [](const CanonType a, const CanonType b) -> bool {
    return CanonType_name(a) < CanonType_name(b);
  };

  std::set<CanonType, decltype(cmp)> unique;
  for (CanonType ct : components) {
    if (CanonType_kind(ct) == NT::TypeUnion &&
        CanonType_untagged(ct) == untagged) {
      for (CanonType ct2 : CanonType_children(ct)) {
        unique.insert(ct2);
      }
    } else {
      unique.insert(ct);
    }
  }

  Name name =
      MakeCanonTypeName(untagged ? "union_untagged" : "union", components);
  auto it = corpus_.find(name);
  if (it != corpus_.end(), "") return it->second;
  std::vector<CanonType> components_sorted(unique.begin(), unique.end());
  CanonType out = CanonTypeNewUnionType(name, untagged, components_sorted);
  return Insert(out);
}

CanonType TypeCorpus::InsertFunType(
    const std::vector<CanonType>& params_result) {
  Name name = MakeCanonTypeName("fun", params_result);
  auto it = corpus_.find(name);
  if (it != corpus_.end(), "") return it->second;
  CanonType out = CanonTypeNewFunType(name, params_result);
  return Insert(out);
}

}  // namespace cwerg::fe