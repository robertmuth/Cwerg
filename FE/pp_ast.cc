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
  // assume each prefix element is size 1
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
      for (int i = 0; !child.isnull(); ++i, child = Node_next(child)) {
        prefix->SetCurrent(i);
        LabelDefs(child, prefix, labels);
      }
      prefix->PopLevel();
    }
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
constexpr int INDENTATION = 4;

void _EmitLine(const std::vector<std::string>& line, int indent,
               const std::vector<int>* active_columns, bool is_last) {
  if (indent >= 0) {
    std::vector<std::string_view> spaces(indent * INDENTATION + 1, " ");
    for (int pos : *active_columns) {
      spaces[pos * INDENTATION] = "┃";
    }
    spaces.back() = is_last ? "┗" : "┣";
    for (const auto& s : spaces) {
      std::cout << s;
    }
  }
  //
  std::string_view sep;
  for (const auto& s : line) {
    std::cout << sep << s;
    sep = " ";
  }
  std::cout << "\n";
}

// forward decl
void DumpNode(Node node, int indent, std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last);

void DumpList(std::string_view name, Node node, int indent,
              std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last) {
  std::vector<std::string> line = {std::string(name)};

  if (node.isnull()) {
    line.push_back("[Empty]");
    _EmitLine(line, indent + 1, active_columns, is_last);
  } else {
    _EmitLine(line, indent + 1, active_columns, is_last);
    active_columns->push_back(indent + 2);
    do {
      Node next = Node_next(node);
      if (next.isnull()) {
        active_columns->pop_back();
      }
      DumpNode(node, indent + 2, labels, active_columns, next.isnull());
      node = next;
    } while (!node.isnull());
  }
}

int LastNodeSlot(const NodeDesc& desc) {
  int out = -1;
  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    NFD_SLOT slot = desc.node_fields[i];
    NFD_KIND kind = GlobalNodeFieldDescs[int(slot)].kind;
    if (kind == NFD_KIND::LIST || kind == NFD_KIND::NODE) {
      out = i;
    }
  }
  return out;
}

void DumpNode(Node node, int indent, std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last) {
  std::vector<std::string> line;
  line.push_back(std::string(EnumToString(node.kind())));
  // uint16_t compressed_flags = Node_compressed_flags(node);
  _EmitLine(line, indent, active_columns, is_last);

  const NodeDesc& desc = GlobalNodeDescs[int(node.kind())];
  int last_slot = LastNodeSlot(desc);
  if (last_slot == -1) return;

  active_columns->push_back(indent + 1);
  for (int i = 0; i <= last_slot; ++i) {
    if (i == last_slot) {
      active_columns->pop_back();
    }
    NFD_SLOT slot = desc.node_fields[i];
    NFD_KIND kind = GlobalNodeFieldDescs[int(slot)].kind;
    Node child = Node_child(node, i);

    switch (kind) {
      case NFD_KIND::NODE:
        DumpNode(child, indent + 1, labels, active_columns, i == last_slot);
        break;
      case NFD_KIND::LIST:
        DumpList(std::string(EnumToString(slot)), child, indent, labels,
                 active_columns, i == last_slot);
        break;
      default:
        break;
    }
  }
}

void DumpAstMods(const std::vector<Node>& mods) {
  std::map<Node, std::string> labels;
  ExtractSymDefLabels(mods, &labels);
  ExtractTargetLabels(mods, &labels);
  std::vector<int> active_columns;
  for (Node mod : mods) {
    active_columns.clear();
    DumpNode(mod, -1, &labels, &active_columns, true);
  }
}

}  // namespace cwerg::fe