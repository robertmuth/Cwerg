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
  SizeOrDim dim = kSizeOrDimInvalid;
  BASE_TYPE_KIND base_type_kind = BASE_TYPE_KIND::INVALID;
  Node ast_node = kNodeInvalid;
  SizeOrDim alignment = -1;
  //  TODO: should probably be sint64_t
  SizeOrDim size = kSizeOrDimInvalid;
  int type_id = -1;
};

struct Stripe<CanonTypeCore, CanonType> gCanonTypeCore("CanonTypeCore");

StripeBase* const gAllStripesCanonType[] = {&gCanonTypeCore, nullptr};

struct StripeGroup gStripeGroupCanonType("CanonType", &gAllStripesCanonType[0],
                                         128 * 1024);

Name CanonType_name(CanonType ct) { return gCanonTypeCore[ct].name; }

bool CanonType_mut(CanonType ct) { return gCanonTypeCore[ct].mut; }

SizeOrDim CanonType_dim(CanonType ct) {
  ASSERT(CanonType_kind(ct) == NT::TypeVec, "");
  return gCanonTypeCore[ct].dim;
}

int align(int size, int alignment) {
  return (size + alignment - 1) / alignment * alignment;
}

SizeOrDim CanonType_alignment(CanonType ct) {
  return gCanonTypeCore[ct].alignment;
}
SizeOrDim CanonType_size(CanonType ct) { return gCanonTypeCore[ct].size; }
int CanonType_aligned_size(CanonType ct) {
  return align(gCanonTypeCore[ct].size, gCanonTypeCore[ct].alignment);
}

bool CanonType_union_contains(CanonType ct, CanonType member) {
  for (CanonType child : CanonType_children(ct)) {
    if (child == member) return true;
  }
  return false;
}

bool CanonType_is_finalized(CanonType ct) {
  return gCanonTypeCore[ct].alignment > 0;
}

void CanonType_Finalize(CanonType ct, SizeOrDim size, size_t alignment) {
  ASSERT(size >= 0 && alignment >= 0,
         "" << size << " " << alignment << " " << ct);
  ASSERT(gCanonTypeCore[ct].alignment < 0, "already finalized " << ct);
  gCanonTypeCore[ct].alignment = alignment;
  gCanonTypeCore[ct].size = size;
}

NT CanonType_kind(CanonType ct) { return gCanonTypeCore[ct].node; }

bool CanonType_untagged(CanonType ct) { return gCanonTypeCore[ct].untagged; }

Node CanonType_ast_node(CanonType ct) { return gCanonTypeCore[ct].ast_node; }

bool operator<(CanonType a, CanonType b) {
  return CanonType_name(a) < CanonType_name(b);
}

CanonType CanonType_get_unwrapped(CanonType ct) {
  while (CanonType_kind(ct) == NT::DefType) {
    ct = CanonType_children(ct)[0];
  }

  if (CanonType_kind(ct) == NT::DefEnum) {
    return CanonType_children(ct)[0];
  }

  return ct;
}

BASE_TYPE_KIND CanonType_get_unwrapped_base_type_kind(CanonType ct) {
  while (CanonType_kind(ct) == NT::DefType) {
    ct = CanonType_children(ct)[0];
  }

  if (CanonType_kind(ct) == NT::DefEnum) {
    ct = CanonType_children(ct)[0];
  }
  if (CanonType_kind(ct) == NT::TypeBase) {
    return gCanonTypeCore[ct].base_type_kind;
  }

  return BASE_TYPE_KIND::INVALID;
}

bool CanonType_is_unwrapped_complex(CanonType ct) {
  while (CanonType_kind(ct) == NT::DefType) {
    ct = CanonType_children(ct)[0];
  }
  switch (CanonType_kind(ct)) {
    case NT::TypeVec:
    case NT::DefRec:
    case NT::TypeUnion:
      return true;
    default:
      return false;
  }
}

BASE_TYPE_KIND CanonType_base_type_kind(CanonType ct) {
  ASSERT(CanonType_kind(ct) == NT::TypeBase, "");
  return gCanonTypeCore[ct].base_type_kind;
}

std::vector<CanonType>& CanonType_children(CanonType n) {
  return gCanonTypeCore[n].children;
}

int CanonType_get_original_typeid(CanonType n) {
  return gCanonTypeCore[n].type_id;
}
int& CanonType_typeid(CanonType n) { return gCanonTypeCore[n].type_id; }

Node CanonType_lookup_rec_field(CanonType ct, Name field_name) {
  ASSERT(CanonType_kind(ct) == NT::DefRec, "");
  Node defrec = CanonType_ast_node(ct);
  ASSERT(Node_kind(defrec) == NT::DefRec, "");
  for (Node field = Node_fields(defrec); !field.isnull();
       field = Node_next(field)) {
    if (Node_name(field) == field_name) {
      return field;
    }
  }
  return kNodeInvalid;
}

CanonType CanonTypeNew() {
  CanonType out = CanonType(gStripeGroupCanonType.New().index());
  return out;
}

CanonType CanonTypeNewBaseType(BASE_TYPE_KIND base_type) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypeBase,
      .name = NameNew(EnumToString_BASE_TYPE_KIND_LOWER(base_type)),
      .base_type_kind = base_type};
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

CanonType CanonTypeNewWrappedType(Name name) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::DefType, .name = name};
  return out;
}

CanonType CanonTypeNewVecType(Name name, SizeOrDim dim, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {
      .node = NT::TypeVec, .name = name, .children = {child}, .dim = dim};
  return out;
}

CanonType CanonTypeNewRecType(Name name, Node ast_node,
                              const std::vector<CanonType>& children) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::DefRec,
                         .name = name,
                         .children = children,
                         .ast_node = ast_node};
  return out;
}

CanonType CanonTypeNewEnumType(Name name, Node ast_node, CanonType child) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::DefEnum,
                         .name = name,
                         .children = {child},
                         .ast_node = ast_node};

  return out;
}

CanonType CanonTypeNewUnionType(Name name, bool untagged,
                                const std::vector<CanonType>& sorted_children) {
  CanonType out = CanonTypeNew();
  gCanonTypeCore[out] = {.node = NT::TypeUnion,
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

// ====================================================================

TypeCorpus::TypeCorpus(const TargetArchConfig& arch) : arch_config_(arch) {
  for (BASE_TYPE_KIND kind : {BASE_TYPE_KIND::VOID,
                              //
                              BASE_TYPE_KIND::S8, BASE_TYPE_KIND::S16,
                              BASE_TYPE_KIND::S32, BASE_TYPE_KIND::S64,
                              //
                              BASE_TYPE_KIND::U8, BASE_TYPE_KIND::U16,
                              BASE_TYPE_KIND::U32, BASE_TYPE_KIND::U64,
                              //
                              BASE_TYPE_KIND::R32, BASE_TYPE_KIND::R64,
                              //
                              BASE_TYPE_KIND::BOOL, BASE_TYPE_KIND::NORET}) {
    base_type_map_[kind] = InsertBaseType(kind);
  }
  base_type_map_[BASE_TYPE_KIND::SINT] = base_type_map_[arch.get_sint_kind()];
  base_type_map_[BASE_TYPE_KIND::UINT] = base_type_map_[arch.get_uint_kind()];
  base_type_map_[BASE_TYPE_KIND::TYPEID] =
      base_type_map_[arch.get_typeid_kind()];
}

void SetAbiInfoRecursively(CanonType ct, const TargetArchConfig& ta) {
  if (CanonType_alignment(ct) >= 0) return;
  if (CanonType_kind(ct) != NT::TypePtr && CanonType_kind(ct) != NT::TypeFun) {
    for (CanonType child : CanonType_children(ct)) {
      SetAbiInfoRecursively(child, ta);
    }
  }

  switch (CanonType_kind(ct)) {
    case NT::TypeBase: {
      auto size = BaseTypeKindByteSize(CanonType_base_type_kind(ct));
      return CanonType_Finalize(ct, size, size);
    }
    case NT::TypePtr: {
      size_t size = ta.data_addr_bitwidth / 8;
      return CanonType_Finalize(ct, SizeOrDim(size), size);
    }
    case NT::TypeSpan: {
      size_t ptr_size = ta.data_addr_bitwidth / 8;
      size_t len_size = ta.uint_bitwidth / 8;
      ASSERT(ptr_size == len_size, "TODO: needs more work");
      return CanonType_Finalize(ct, SizeOrDim(ptr_size + len_size), ptr_size);
    }
    case NT::TypeVec: {
      CanonType ct_dep = CanonType_underlying_type(ct);
      auto dim = CanonType_dim(ct);
      auto elem_size = CanonType_aligned_size(ct_dep);
      return CanonType_Finalize(ct, SizeOrDim(elem_size * dim),
                                CanonType_alignment(ct_dep));
    }
    case NT::TypeUnion: {
      int num_pointer = 0;
      int num_other = 0;
      SizeOrDim max_size = 0;
      SizeOrDim max_alignment = 1;
      SizeOrDim ptr_size = ta.code_addr_bitwidth / 8;
      for (CanonType child_ct : CanonType_children(ct)) {
        if (CanonType_size(child_ct) == 0) continue;
        while (CanonType_kind(child_ct) == NT::DefType) {
          child_ct = CanonType_children(child_ct)[0];
        }
        if (CanonType_kind(child_ct) == NT::TypePtr) {
          ++num_pointer;
          max_size = std::max(max_size, ptr_size);
          max_alignment = std::max(max_alignment, ptr_size);
        } else {
          ++num_other;
          max_size = std::max(max_size, CanonType_size(child_ct));
          max_alignment =
              std::max(max_alignment, CanonType_alignment(child_ct));
        }
      }
      if (CanonType_untagged(ct)) {
        return CanonType_Finalize(ct, max_size, max_alignment);
      }

      if (ta.optimize_union_tag && num_pointer == 1 && num_other == 0) {
        return CanonType_Finalize(ct, ptr_size, ptr_size);
      }
      SizeOrDim tag_size = ta.typeid_bitwidth / 8;
      max_alignment = std::max(max_alignment, tag_size);

      return CanonType_Finalize(ct, align(tag_size, max_alignment) + max_size,
                                max_alignment);
    }
    case NT::DefEnum: {
      int size = CanonType_size(CanonType_underlying_type(ct));
      return CanonType_Finalize(ct, size, size);
    }
    case NT::TypeFun: {
      size_t size = ta.code_addr_bitwidth / 8;
      return CanonType_Finalize(ct, size, size);
    }

    case NT::DefRec: {
      SizeOrDim size = 0;
      SizeOrDim alignment = 1;
      Node def_rec = CanonType_ast_node(ct);
      for (Node field = Node_fields(def_rec); !field.isnull();
           field = Node_next(field)) {
        CanonType field_ct = Node_x_type(field);
        size = align(size, CanonType_alignment(field_ct));
        Node_x_offset(field) = size;
        size += CanonType_size(field_ct);
        alignment = std::max(alignment, CanonType_alignment(field_ct));
      }
      return CanonType_Finalize(ct, size, alignment);
    }

    case NT::DefType: {
      CanonType ct_dep = CanonType_underlying_type(ct);
      return CanonType_Finalize(ct, CanonType_size(ct_dep),
                                CanonType_alignment(ct_dep));
    }
    default:
      ASSERT(false, "UNREACHABLE");
      break;
  }
}

CanonType TypeCorpus::Insert(CanonType ct) {
  ASSERT(!ct.isnull(), "");
  ASSERT(corpus_.find(CanonType_name(ct)) == corpus_.end(),
         "Duplicate type " << CanonType_name(ct));
  corpus_[CanonType_name(ct)] = ct;
  CanonType_typeid(ct) = typeid_curr_;
  ++typeid_curr_;
  corpus_in_order_.push_back(ct);
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

CanonType TypeCorpus::InsertBaseType(BASE_TYPE_KIND kind) {
  CanonType out = CanonTypeNewBaseType(kind);
  return Insert(out);
}

CanonType TypeCorpus::InsertPtrType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "ptr_mut" : "ptr",
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end()) return it->second;
  CanonType out = CanonTypeNewPtrType(name, mut, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertSpanType(bool mut, CanonType child) {
  Name name = MakeCanonTypeName(mut ? "span_mut" : "span",
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end()) {
    return it->second;
  }
  CanonType out = CanonTypeNewSpanType(name, mut, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertWrappedTypePre(std::string_view name) {
  // TODO uid update
  Name n = MakeCanonTypeName("wrapped", name);
  CanonType out = CanonTypeNewWrappedType(n);
  return Insert(out);
}

void TypeCorpus::InsertWrappedTypeFinalize(CanonType ct,
                                           CanonType wrapped_type) {
  CanonType_children(ct) = {wrapped_type};
}

CanonType TypeCorpus::InsertVecType(int dim, CanonType child) {
  Name name = MakeCanonTypeName("vec", std::to_string(dim),
                                NameData(CanonType_name(child)));
  auto it = corpus_.find(name);
  if (it != corpus_.end()) return it->second;
  CanonType out = CanonTypeNewVecType(name, dim, child);
  return Insert(out);
}

CanonType TypeCorpus::InsertRecType(std::string_view name, Node ast_node,
                                    bool process_children) {
  Name n = MakeCanonTypeName("rec", name);
  std::vector<CanonType> children;
  if (process_children) {
    for (Node field = Node_fields(ast_node); !field.isnull();
         field = Node_next(field)) {
      CanonType ct = Node_x_type(field);
      ASSERT(!ct.isnull(), "");
      children.push_back(ct);
    }
  }
  CanonType out = CanonTypeNewRecType(n, ast_node, children);
  return Insert(out);
}

CanonType TypeCorpus::InsertEnumType(std::string_view name, Node ast_node) {
  Name n = MakeCanonTypeName("enum", name);
  CanonType out = CanonTypeNewEnumType(
      n, ast_node, get_base_canon_type(Node_base_type_kind(ast_node)));
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

  Name name = MakeCanonTypeName(untagged ? "sum_untagged" : "sum", components);
  auto it = corpus_.find(name);
  if (it != corpus_.end()) return it->second;
  std::vector<CanonType> components_sorted(unique.begin(), unique.end());
  CanonType out = CanonTypeNewUnionType(name, untagged, components_sorted);
  return Insert(out);
}

CanonType TypeCorpus::InsertUnionComplement(CanonType all, CanonType part) {
  ASSERT(CanonType_kind(all) == NT::TypeUnion,
         "expected union type " << EnumToString(CanonType_kind(all)));
  std::vector<CanonType> part_children;
  if (CanonType_kind(part) == NT::TypeUnion) {
    part_children = CanonType_children(part);
  } else {
    part_children.push_back(part);
  }
  std::vector<CanonType> children;
  TypeListDelta(CanonType_children(all), part_children, &children);
  ASSERT(!children.empty(), "");
  if (children.size() == 1) {
    return children[0];
  }
  return InsertUnionType(CanonType_untagged(all), children);
}

CanonType TypeCorpus::InsertFunType(
    const std::vector<CanonType>& params_result) {
  Name name = MakeCanonTypeName("fun", params_result);
  auto it = corpus_.find(name);
  if (it != corpus_.end()) return it->second;
  CanonType out = CanonTypeNewFunType(name, params_result);
  return Insert(out);
}

void TypeCorpus::SetAbiInfoForAllTypes() {
  for (auto it = corpus_.begin(); it != corpus_.end(); ++it) {
    CanonType ct = it->second;
    SetAbiInfoRecursively(ct, arch_config_);
    ASSERT(CanonType_size(ct) >= 0, "" << ct);
  }
  initial_typing_ = false;
}

void TypeCorpus::Dump() {
  std::cout << "Dump of CanonTypes: (" << corpus_in_order_.size() << ")\n";
  for (CanonType ct : corpus_in_order_) {
    std::cout << CanonType_name(ct)
              // << " " << EnumToString(CanonType_kind(ct))
              << " id=" << CanonType_typeid(ct)
              << " size=" << CanonType_size(ct)
              << " align=" << CanonType_alignment(ct) << "\n";
  }
}

bool CanonType_tagged_union_contains(CanonType haystack, CanonType needle) {
  if (CanonType_kind(haystack) != NT::TypeUnion ||
      CanonType_untagged(haystack)) {
    return false;
  }
  for (const auto x : CanonType_children(haystack)) {
    if (x == needle) return true;
  }
  return false;
}

bool IsCompatibleTypeForEq(CanonType op1, CanonType op2) {
  if (IsTypeForEq(op1)) {
    if (op1 == op2) return true;

    if (CanonType_kind(op1) == NT::TypePtr &&
        CanonType_kind(op2) == NT::TypePtr) {
      return CanonType_underlying_type(op1) == CanonType_underlying_type(op2);
    }

    if (CanonType_tagged_union_contains(op2, op1)) {
      return true;
    }
  } else if (IsTypeForEq(op2)) {
    if (CanonType_tagged_union_contains(op1, op2)) {
      return true;
    }
  }
  return false;
}

bool IsCompatibleTypeForCmp(CanonType op1, CanonType op2) {
  if (IsTypeForCmp(op1)) {
    if (op1 == op2) return true;

    if (CanonType_kind(op1) == CanonType_kind(op2) &&
        CanonType_kind(op1) == NT::TypePtr) {
      return CanonType_underlying_type(op1) == CanonType_underlying_type(op2);
    }
  }
  return false;
}

bool IsCompatibleTypeForAs(CanonType src, CanonType dst) {
  return CanonType_kind(src) == NT::TypeBase &&
         CanonType_kind(dst) == NT::TypeBase &&
         IsNumber(CanonType_get_unwrapped_base_type_kind(src)) &&
         IsNumber(CanonType_get_unwrapped_base_type_kind(dst));
}

bool IsCompatibleTypeForBitcast(CanonType src, CanonType dst) {
  if (CanonType_kind(src) != NT::TypeBase && CanonType_kind(src) != NT::TypePtr)
    return false;
  if (CanonType_kind(dst) != NT::TypeBase && CanonType_kind(dst) != NT::TypePtr)
    return false;
  return CanonType_size(src) == CanonType_size(dst);
}

bool IsSubtypeOfUnion(CanonType src_ct, CanonType dst_ct) {
  if (CanonType_kind(dst_ct) != NT::TypeUnion) return false;
  if (CanonType_kind(src_ct) == NT::TypeUnion) {
    if (CanonType_untagged(src_ct) != CanonType_untagged(dst_ct)) return false;
    return TypeListIsSuperSet(CanonType_children(dst_ct),
                              CanonType_children(src_ct));
  } else {
    for (CanonType child : CanonType_children(dst_ct)) {
      if (child == src_ct) return true;
    }
    return false;
  }
}

bool IsDropMutConversion(CanonType src, CanonType dst) {
  if ((CanonType_kind(src) == NT::TypePtr &&
       CanonType_kind(dst) == NT::TypePtr) ||
      (CanonType_kind(src) == NT::TypeSpan &&
       CanonType_kind(dst) == NT::TypeSpan)) {
    return CanonType_underlying_type(src) == CanonType_underlying_type(dst) &&
           !CanonType_mut(dst);
  }
  return false;
}

bool IsCompatibleType(CanonType src, CanonType dst, bool src_is_writable) {
  if (IsDropMutConversion(src, dst)) return true;
  if (src_is_writable || !CanonType_mut(dst)) {
    if (IsVecToSpanConversion(src, dst)) return true;
  }

  return IsSubtypeOfUnion(src, dst);
}

bool IsVecToSpanConversion(CanonType src_ct, CanonType dst_src) {
  if (CanonType_kind(src_ct) != NT::TypeVec) return false;
  if (CanonType_kind(dst_src) != NT::TypeSpan) return false;
  return CanonType_underlying_type(src_ct) ==
         CanonType_underlying_type(dst_src);
}

bool IsProperLhs(Node node) {
  switch (Node_kind(node)) {
    case NT::Id: {
      Node def_node = Node_x_symbol(node);
      if (Node_kind(def_node) == NT::DefVar ||
          Node_kind(def_node) == NT::DefGlobal) {
        return Node_has_flag(def_node, BF::MUT);
      }
      return false;
    }
    case NT::ExprDeref:
      return CanonType_mut(Node_x_type(Node_expr(node)));
    case NT::ExprField:
      return IsProperLhs(Node_container(node));
    case NT::ExprIndex: {
      Node container = Node_container(node);
      NT kind = CanonType_kind(Node_x_type(container));
      if (kind == NT::TypeSpan) return CanonType_mut(Node_x_type(container));
      ASSERT(kind == NT::TypeVec, "");
      return IsProperLhs(container);
    }
    case NT::ExprNarrow:
      return IsProperLhs(Node_expr(node));
    default:
      return false;
  }
}

bool TypeListsAreTheSame(const std::vector<CanonType>& children1,
                         const std::vector<CanonType>& children2) {
  int size1 = children1.size();
  int size2 = children2.size();
  if (size1 != size2) return false;

  for (int i = 0; i < size1; i++) {
    if (children1[i] != children2[i]) return false;
  }
  return true;
}

bool TypeListIsSuperSet(const std::vector<CanonType>& children1,
                        const std::vector<CanonType>& children2) {
  int size1 = children1.size();
  int size2 = children2.size();
  if (size1 < size2) return false;

  for (int i2 = 0, i1 = 0; i2 < size2; ++i2, ++i1) {
    if (i1 == size1) return false;

    while (children1[i1] != children2[i2]) {
      i1++;
      if (i1 == size1) return false;
    }
  }
  return true;
}

void TypeListDelta(const std::vector<CanonType>& children1,
                   const std::vector<CanonType>& children2,
                   std::vector<CanonType>* out) {
  int size1 = children1.size();
  int size2 = children2.size();
  ASSERT(size1 >= size2, "");
  for (int i1 = 0, i2 = 0; i1 < size1; ++i1) {
    if (i2 < size2 && children1[i1] == children2[i2]) {
      ++i2;
      continue;
    }
    out->push_back(children1[i1]);
  }
}

}  // namespace cwerg::fe