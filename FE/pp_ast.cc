#include "FE/pp_ast.h"

#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include "FE/cwast_gen.h"
#include "Util/assert.h"

namespace cwerg::fe {

std::string MakeLabel(std::string_view c,
                      const std::vector<std::string_view>& prefix) {
  std::string out;
  out.reserve(prefix.size() * 2 + c.size());
  std::string_view sep = c;
  for (const auto& p : prefix) {
    out += sep;
    sep = ".";
    out += p;
  }
  return out;
}

class Prefix {
  std::vector<std::string_view> prefix_;
  std::vector<std::string> cache_;
  std::string empty_;

 public:
  Prefix() {}

  void PushLevel() { prefix_.push_back(empty_); }

  void PopLevel() { prefix_.pop_back(); }

  void SetCurrent(int i) {
    if (cache_.size() < i) {
      prefix_.back() = cache_[i];
    } else {
      ASSERT(i == cache_.size(), "");
      cache_.push_back(std::to_string(i));
      prefix_.back() = cache_[i];
    }
  }

  std::string GetLabel(std::string_view c) const {
    return MakeLabel(c, prefix_);
  }
};

std::string_view GetLabelTag(NT kind) {
  switch (kind) {
    case NT::DefMod:
      return "m";
    case NT::DefFun:
      return "f";
    case NT::DefRec:
      return "r";
    case NT::DefEnum:
      return "e";
    case NT::DefMacro:
      return "x";
    case NT::DefType:
      return "t";
    case NT::DefGlobal:
      return "g";
    case NT::DefVar:
      return "v";
    case NT::FunParam:
      return "p";
    case NT::RecField:
      return "F";
    default:
      return "";
  }
}

void LabelDefs(Node node, Prefix* prefix, std::map<Node, std::string>* labels) {
  std::string_view tag = GetLabelTag(node.kind());
  if (!tag.empty()) {
    (*labels)[node] = prefix->GetLabel(tag);
  }

  const NodeDesc& nd = GlobalNodeDescs[int(node.kind())];
  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    NFD_SLOT kind = nd.node_fields[i];
    if (GlobalNodeFieldDescs[int(kind)].kind == NFD_KIND::LIST) {
      prefix->PushLevel();
      Node child = Node_child(node, i);
      for (int i = 0; !child.isnull(); ++i, child = Node_next(node)) {
        prefix->SetCurrent(i);
        LabelDefs(child, prefix, labels);
      }
    }

    prefix->PopLevel();
  }
}

void ExtractSymDefLabels(const std::vector<Node>& mods,
                         std::map<Node, std::string>* labels) {
  Prefix prefix;
  prefix.PushLevel();
  for (int i = 0; i < mods.size(); ++i) {
    Node mod = mods[i];
    prefix.SetCurrent(i);
    LabelDefs(mod, &prefix, labels);
  }
}

void ExtractTargetLabels(const std::vector<Node>& mods,
                         std::map<Node, std::string>* labels) {
  Prefix prefix;
  prefix.PushLevel();

  for (int i = 0; i < mods.size(); ++i) {
    Node mod = mods[i];
    prefix.SetCurrent(i);
    prefix.PushLevel();
    int block_counter = 0;
    int expr_counter = 0;

    auto visitor = [&labels, &prefix, &block_counter, &expr_counter](
                       Node node, Node parent) {
      switch (node.kind()) {
        case NT::StmtBlock:
          prefix.SetCurrent(block_counter++);
          (*labels)[node] = prefix.GetLabel("b");
          break;
        case NT::ExprStmt:
          prefix.SetCurrent(expr_counter++);
          (*labels)[node] = prefix.GetLabel("e");
        default:
          break;
      }
    };

    VisitAstRecursivelyPost(mod, visitor, kNodeInvalid);
    prefix.PopLevel();
  }
}

void DumpMods(const std::vector<Node>& mods) {
  std::map<Node, std::string> labels;
  ExtractSymDefLabels(mods, &labels);
  ExtractTargetLabels(mods, &labels);
}

}  // namespace cwerg::fe