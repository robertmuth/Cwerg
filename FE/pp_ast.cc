#include "FE/pp_ast.h"

#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include "FE/cwast_gen.h"
#include "FE/eval.h"
#include "FE/type_corpus.h"
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

// Helper for label generation
class Prefix {
  std::vector<int> prefix_;
  // Avoids creating the same strings over and over again
  std::vector<std::string> digits_cache_;
  std::string tmp_;

 public:
  Prefix() {}

  void PushLevel() { prefix_.push_back(-1); }

  void PopLevel() { prefix_.pop_back(); }

  void SetCurrent(int i) { prefix_.back() = i; }

  std::string GetLabel(std::string_view c) {
    tmp_.clear();
    std::string_view sep = c;
    for (const auto& p : prefix_) {
      while (digits_cache_.size() <= p) {
        digits_cache_.push_back(std::to_string(digits_cache_.size()));
      }
      tmp_ += sep;
      sep = ".";
      tmp_ += digits_cache_[p];
    }
    return tmp_;
  }
};

std::string_view GetLabelTag(NT kind) {
  switch (kind) {
    case NT::DefMod:
      return "M";
    case NT::DefFun:
      return "F";
    case NT::DefRec:
      return "R";
    case NT::DefEnum:
      return "E";
    case NT::EnumVal:
      return "e";
    case NT::DefMacro:
      return "X";
    case NT::DefType:
      return "T";
    case NT::DefGlobal:
      return "G";
    case NT::DefVar:
      return "v";
    case NT::FunParam:
      return "p";
    case NT::RecField:
      return "f";
    case NT::ValString:
      return "S";
    case NT::ValCompound:
      return "C";
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
    Node child = Node_child_node(node, i);
    switch (GlobalNodeFieldDescs[int(kind)].kind) {
      case NFD_KIND::NODE:
        LabelDefs(child, prefix, labels);
        break;
      case NFD_KIND::LIST:
        prefix->PushLevel();
        for (int i = 0; !child.isnull(); ++i, child = Node_next(child)) {
          prefix->SetCurrent(i);
          LabelDefs(child, prefix, labels);
        }
        prefix->PopLevel();
        break;
      default:
        break;
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
                       Node node, Node parent) -> bool {
      switch (node.kind()) {
        case NT::StmtBlock:
          prefix.SetCurrent(block_counter++);
          (*labels)[node] = prefix.GetLabel("b");
          break;
        case NT::ExprStmt:
          prefix.SetCurrent(expr_counter++);
          (*labels)[node] = prefix.GetLabel("s");
        default:
          break;
      }
      return false;
    };

    VisitAstRecursivelyPre(mod, visitor, kNodeInvalid);
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
void DumpNode(Node node, int indent, const std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last, bool dump_handles);

void DumpList(std::string_view name, Node node, int indent,
              const std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last, bool dump_handles) {
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
      DumpNode(node, indent + 2, labels, active_columns, next.isnull(), dump_handles);
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

std::string RenderFlags(uint16_t compressed_flags, uint32_t desc_flag_bits) {
  if (compressed_flags == 0) {
    return "[]";
  }
  std::vector<std::string> flags;
  for (int i = 0; desc_flag_bits != 0; ++i, desc_flag_bits >>= 1) {
    if (desc_flag_bits & 1) {
      if (compressed_flags & Mask(BF(i))) {
        flags.push_back(std::string(EnumToString(BF(i))));
      }
    }
  }
  std::sort(flags.begin(), flags.end());
  std::string out;
  out.reserve(flags.size() * 15);  // basically we will stay below 16 only if
                                   // there is just on flag set
  std::string_view sep = "[";
  for (const auto& f : flags) {
    out += sep;
    out += f;
    sep = ", ";
  }
  out += "]";
  return out;
}

std::string RenderKind(Node node) {
  switch (node.kind()) {
    case NT::Expr1:
      return EnumToString(Node_unary_expr_kind(node));
    case NT::Expr2:
    case NT::StmtCompoundAssignment:
      return EnumToString(Node_binary_expr_kind(node));
    case NT::TypeBase:
      return EnumToString(Node_base_type_kind(node));
    case NT::ExprPointer:
      return EnumToString(Node_pointer_expr_kind(node));
    case NT::ModParam:
      return EnumToString(Node_mod_param_kind(node));
    case NT::MacroParam:
      return EnumToString(Node_macro_param_kind(node));
    case NT::DefMacro:
      return EnumToString(Node_macro_result_kind(node));
    case NT::DefEnum:
      return EnumToString(Node_base_type_kind(node));
    default:
      return "";
  }
}

void DumpNode(Node node, int indent, const std::map<Node, std::string>* labels,
              std::vector<int>* active_columns, bool is_last, bool dump_handles) {
  const NodeDesc& desc = GlobalNodeDescs[int(node.kind())];
  std::vector<std::string> line;

  auto add_tag_value = [&line](std::string_view tag, std::string_view value) {
    std::string out;
    out.reserve(tag.size() + value.size() + 1);
    out += tag;
    out += "=";
    out += value;
    line.push_back(out);
  };

  line.push_back(std::string(EnumToString(node.kind())));
  if (dump_handles) {
    line.push_back("[");
    line.push_back(std::to_string(node.index()));
    line.push_back("]");
  }
  if (desc.bool_field_bits != 0) {
    line.push_back(
        RenderFlags(Node_compressed_flags(node), desc.bool_field_bits));
  }

  if (Node_other_kind(node) != 0) {
    line.push_back(RenderKind(node));
  }

  for (int i = 0; i < MAX_NODE_CHILDREN; ++i) {
    NFD_SLOT slot = desc.node_fields[i];
    NFD_KIND kind = GlobalNodeFieldDescs[int(slot)].kind;
    switch (kind) {
      case NFD_KIND::STR: {
        Str str = Node_child_str(node, i);
        if (!str.isnull() && StrData(str)[0] != 0) {
          add_tag_value(EnumToString(slot), StrData(str));
        }
        break;
      }
      case NFD_KIND::NAME: {
        Name name = Node_child_name(node, i);
        if (!name.isnull()) {
          auto val = NameData(name);
          if (val[0] != 0) {
            if (slot == NFD_SLOT::name) {
              line.push_back(std::string(val));
            } else {
              add_tag_value(EnumToString(slot), val);
            }
          }
        }
        break;
      }

      default:
        break;
    }
  }

  if (labels->contains(node)) {
    add_tag_value("label", labels->at(node));
  }

  if (desc.has(NFD_X_FIELD::type)) {
    CanonType ct = Node_x_type(node);
    if (!ct.isnull()) {
      auto name = NameData(CanonType_name(ct));
      auto no = "[" + std::to_string(CanonType_get_original_typeid(ct)) + "]";
      if (strlen(name) < 16) {
        add_tag_value("x_type", std::string(name) + no);
      } else {
        add_tag_value("x_type", no);
      }
    }
  }

  if (desc.has(NFD_X_FIELD::eval)) {
    Const eval = Node_x_eval(node);
    if (!eval.isnull()) {
      add_tag_value("x_eval", to_string(eval, labels));
    }
  }

  if (desc.has(NFD_X_FIELD::symbol)) {
    Node def_sym = Node_x_symbol(node);
    ASSERT(labels->contains(def_sym), "" << Node_name(def_sym));
    if (!def_sym.isnull()) add_tag_value("x_symbol", labels->at(def_sym));
  }

  if (desc.has(NFD_X_FIELD::target)) {
    Node def_sym = Node_x_target(node);
    if (!def_sym.isnull()) add_tag_value("x_target", labels->at(def_sym));
  }

  if (desc.has(NFD_X_FIELD::poly_mod)) {
    Node def_sym = Node_x_poly_mod(node);
    if (!def_sym.isnull()) add_tag_value("x_poly_mod", labels->at(def_sym));
  }

  if (desc.has(NFD_X_FIELD::offset)) {
    add_tag_value("x_offset", std::to_string(Node_x_offset(node)));
  }

  _EmitLine(line, indent, active_columns, is_last);

  int last_slot = LastNodeSlot(desc);
  if (last_slot == -1) return;

  active_columns->push_back(indent + 1);
  for (int i = 0; i <= last_slot; ++i) {
    if (i == last_slot) {
      active_columns->pop_back();
    }
    NFD_SLOT slot = desc.node_fields[i];
    NFD_KIND kind = GlobalNodeFieldDescs[int(slot)].kind;
    Node child = Node_child_node(node, i);

    switch (kind) {
      case NFD_KIND::NODE:
        DumpNode(child, indent + 1, labels, active_columns, i == last_slot, dump_handles);
        break;
      case NFD_KIND::LIST:
        DumpList(std::string(EnumToString(slot)), child, indent, labels,
                 active_columns, i == last_slot, dump_handles);
        break;
      default:
        break;
    }
  }
}

void DumpAstMods(const std::vector<Node>& mods, bool dump_handles) {
  std::map<Node, std::string> labels;
  ExtractSymDefLabels(mods, &labels);
  ExtractTargetLabels(mods, &labels);
  std::vector<int> active_columns;
  for (Node mod : mods) {
    std::cout << "\n";
    active_columns.clear();
    DumpNode(mod, -1, &labels, &active_columns, true, dump_handles);
  }
}

}  // namespace cwerg::fe