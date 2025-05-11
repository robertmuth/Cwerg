#include "FE/type_corpus.h"

#include <array>
#include <map>

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

inline bool& CanonType_mut(CanonType n) { return gCanonTypeCore[n].mut; }

inline int& CanonType_dim(CanonType n) { return gCanonTypeCore[n].dim; }

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
void TypeCorpus::Insert(CanonType ct) {
  ASSERT(corpus_.find(CanonType_name(ct)) == corpus_.end(), "");
  corpus_[CanonType_name(ct)] = ct;
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

void TypeCorpus::InsertPtrType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "mut_ptr" : "ptr",
                                NameData(CanonType_name(child)));
  CanonType out = CanonTypeNewPtrType(name, mut, child);
  Insert(out);
}

void TypeCorpus::InsertSpanType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "mut_span" : "span",
                                NameData(CanonType_name(child)));
  CanonType out = CanonTypeNewSpanType(name, mut, child);
  Insert(out);
}

void TypeCorpus::InsertWrappedType(CanonType child) {
  // TODO uid update
  Name name = MakeCanonTypeName("wrapped", NameData(CanonType_name(child)));
  CanonType out = CanonTypeNewWrappedType(name, child);
  Insert(out);
}

void TypeCorpus::InsertVecType(int dim, CanonType child) {
  Name name = MakeCanonTypeName("vec", std::to_string(dim),
                                NameData(CanonType_name(child)));
  CanonType out = CanonTypeNewVecType(name, dim, child);
  Insert(out);
}

void TypeCorpus::InsertRecType(std::string_view name, Node ast_node) {
  Name n = MakeCanonTypeName("rec", name);
  CanonType out = CanonTypeNewRecType(n, ast_node);
  Insert(out);
}

void TypeCorpus::InsertEnumType(std::string_view  name, BASE_TYPE_KIND base_type,
                                Node ast_node) {
  Name n = MakeCanonTypeName("enum", name);
  CanonType out = CanonTypeNewEnumType(n, base_type, ast_node);
  Insert(out);
}

void TypeCorpus::InsertUnionType(
    bool untagged, const std::vector<CanonType>& sorted_children) {}

void TypeCorpus::InsertFunType(const std::vector<CanonType>& params_result) {}

}  // namespace cwerg::fe