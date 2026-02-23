#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <map>
#include <set>
#include <string>
#include <string_view>
#include <vector>

// only used for interning comment strings
#include "FE/lexer.h"
#include "FE/mod_pool.h"
#include "FE/parse.h"
#include "Util/switch.h"

namespace cwerg::fe {

using namespace cwerg;

const Path PATH_INVALID;

namespace {

SwitchBool sw_verbose("verbose_read", "make reading more verbose");

Node NormalizeModParamOneStep(Node node) {
  switch (Node_kind(node)) {
    case NT::Id:
      return Node_x_symbol(node);
    case NT::DefType:
      return Node_has_flag(node, BF::WRAPPED) ? node : Node_type(node);

    case NT::DefFun:
    case NT::DefRec:
    //
    case NT::TypeUnion:
    case NT::TypeBase:
    case NT::TypePtr:
    case NT::TypeSpan:
    //
    case NT::EnumVal:
    case NT::ValNum:
    case NT::ValVoid:
      return node;

    default:
      ASSERT(false, "");
      return kNodeInvalid;
  }
}

struct ImportInfo {
  Node import_node;
  std::vector<Node> normalized_args;

  ImportInfo(Node a_import_node) : import_node(a_import_node) {
    ASSERT(Node_kind(a_import_node) == NT::Import, "");
    for (Node child = Node_args_mod(a_import_node); !child.isnull();
         child = Node_next(Node(child))) {
      normalized_args.push_back(child);
    }
  }

  bool HasBeenResolved() { return !Node_x_module(import_node).isnull(); }

  size_t NumArgs() const { return normalized_args.size(); }
  bool IsParameterized() const { return NumArgs() > 0; }

  void ResolveImport(Node imported_mod) {
    ASSERT(Node_kind(imported_mod) == NT::DefMod, "");
    Node_x_module(import_node) = imported_mod;
  }

  bool TryNormalizeModArg() {
    for (size_t i = 0; i < normalized_args.size(); ++i) {
      Node n = normalized_args[i];
      while (true) {
        Node x = NormalizeModParamOneStep(n);
        if (x.isnull()) {
          return false;
        } else if (x == n) {
          break;
        } else {
          normalized_args[i] = x;
          n = x;
        }
      }
    }
    return true;
  }
};

struct ModInfo {
  ModId mid;
  Node mod;
  SymTab* symtab;
  std::vector<ImportInfo> imports;

  ModInfo() : ModInfo(ModId(), kNodeInvalid, nullptr) {}

  ModInfo(ModId a_mid, Node a_mod, SymTab* a_symtab)
      : mid(a_mid), mod(a_mod), symtab(a_symtab) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(child)) {
      if (Node_kind(child) == NT::Import) {
        imports.push_back(ImportInfo(child));
      }
    }
  }

  bool IsValid() { return mod.raw_kind() != kKindInvalid; }
};

std::string_view ReadFile(const char* filename) {
  int fd = open(filename, O_RDONLY, 0);
  if (fd < 0) {
    std::cerr << "Cannot open input file [" << filename << "] err=" << fd
              << "\n";
    return std::string_view();
  }
  struct stat sb;
  fstat(fd, &sb);

  // map an extra terminator byte
  void* data_bytes = mmap(NULL, sb.st_size + 1, PROT_WRITE, MAP_PRIVATE, fd, 0);
  if (data_bytes == MAP_FAILED) {
    std::cerr << "Cannot mmap input file " << filename << "\n";
    return std::string_view();
  }
  close(fd);

  return std::string_view(reinterpret_cast<char*>(data_bytes), sb.st_size);
}

Name GetQualifierIfPresent(Name name) {
  const char* str = NameData(name);
  for (size_t pos = 0; str[pos] != 0; ++pos) {
    if (str[pos] == ':' && str[pos + 1] == ':') {
      return NameNew({str, pos});
    }
  }
  return kNameInvalid;
}

Name StripQualifier(Name name) {
  const char* str = NameData(name);
  for (size_t pos = 0; str[pos] != 0; ++pos) {
    if (str[pos] == ':' && str[pos + 1] == ':') {
      return NameNew(str + pos + 2);
    }
  }
  return kNameInvalid;
}

void ResolveImportsForQualifers(Node mod) {
  std::unordered_map<Name, Node> imports;

  auto visitor = [&imports](Node node, Node parent) {
    switch (Node_kind(node)) {
      case NT::Import: {
        auto name = Node_name(node);
        if (imports.contains(name)) {
          CompilerError(Node_srcloc(node)) << "duplicate import";
        }
        imports[name] = node;
      } break;
      case NT::DefFun:
      case NT::MacroInvoke:
      case NT::Id: {
        Name name = Node_name(node);
        Name q = GetQualifierIfPresent(name);
        if (!q.isnull()) {
          auto it = imports.find(q);
          if (it == imports.end()) {
            CompilerError(Node_srcloc(node))
                << "cannot resolve qualifier [" << q << "] " << name.index();
          }
          Node_x_import(node) = it->second;
          auto s = StripQualifier(name);
          Node_name(node) = s;
          // std::cout << "ResolveImportsForQualifers " << name << " -> " << s
          //          << "\n";
        }
      } break;

      default:
        break;
    }
  };
  VisitAstRecursivelyPost(mod, visitor, kNodeInvalid);
}

void ExtractSymTabPopulatedWithGlobals(Node mod, SymTab* symtab) {
  for (Node child = Node_body_mod(mod); !child.isnull();
       child = Node_next(Node(child))) {
    switch (Node_kind(child)) {
      case NT::DefFun:
        if (Node_has_flag(child, BF::POLY)) {
          if (HasImportedSymbolReference(child) ||
              symtab->contains(Node_name(child))) {
            continue;
          }
        }
      // fall through
      case NT::DefType:
      case NT::DefEnum:
      case NT::DefGlobal:
      case NT::DefMacro:
      case NT::DefRec: {
        auto name = Node_name(child);
        if (symtab->contains(name)) {
          CompilerError(Node_srcloc(child))
              << "duplicate symbol " << Node_name(child);
        } else {
          symtab->insert({name, child});
        }
        break;
      }
      default:
        break;
    }
  }
}

#if 0
void Dump(const SymTab* symtab) {
  std::cout << "SYMTAB " << symtab << "\n";
  for (auto& kv : *symtab) {
    std::cout << kv.first << " -> " << EnumToString(Node_kind(kv.second))
              << "\n";
  }
  std::cout << "\n";
}
#endif

class ModPoolState {
  std::vector<SymTab*> symtabs_;
  std::map<ModId, ModInfo> all_mods_;
  std::map<Path, Node> raw_generic_;
  int gen_mod_uid = 0;

 public:
  ModInfo GetModInfo(const ModId& mid) const {
    auto it = all_mods_.find(mid);
    return it->second;
  }

  ~ModPoolState() {
    for (SymTab* symtab : symtabs_) {
      delete symtab;
    }
    for (auto& kv : raw_generic_) {
      NodeFreeRecursively(kv.second);
    }
  }

  bool HasModInfo(const ModId& mid) const {
    return all_mods_.find(mid) != all_mods_.end();
  }

  std::vector<Node> AllMods() {
    std::vector<Node> out;
    for (auto& kv : all_mods_) {
      out.push_back(kv.second.mod);
    }
    return out;
  }

  ModInfo AddModInfo(const Path& path, const std::vector<Node>& args,
                     Node mod) {
    SymTab* symtab = new SymTab();
    ExtractSymTabPopulatedWithGlobals(mod, symtab);
    ResolveImportsForQualifers(mod);
    if (sw_verbose.Value()) {
      std::cout << "AddModInfoCommon [" << path << "] " << Node_name(mod)
                << "\n";
    }
    ASSERT(Node_kind(mod) == NT::DefMod, "");
    ModId mid = ModId(path, args);
    ASSERT(!all_mods_.contains(mid), "duplicate module " << mid.path);
    ModInfo mod_info(mid, mod, symtab);
    all_mods_.insert({mid, mod_info});
    symtabs_.push_back(symtab);
    Node_x_symtab(mod) = symtab;
    return mod_info;
  }

  Node GetCloneOfGenericMod(const Path& path,
                            std::function<Node(Path)> read_mod_fun) {
    Node generic_mod;
    if (raw_generic_.contains(path)) {
      generic_mod = raw_generic_[path];
    } else {
      generic_mod = read_mod_fun(path);
      raw_generic_[path] = generic_mod;
    }
    ++gen_mod_uid;
    NodeToNodeMap dummy1;
    NodeToNodeMap dummy2;

    Node mod = NodeCloneRecursively(generic_mod, &dummy1, &dummy2);
    std::string s = NameData(Node_name(generic_mod));
    s += "/";
    s += std::to_string(gen_mod_uid);
    Node_name(mod) = NameNew(s);
    return mod;
  }
};

struct Candidate {
  Name name;
  Node mod;

  // Note unlike python which uses a min heap, c++ uses a max heap so we invert
  // the order
  bool operator<(const Candidate& other) const { return other.name < name; }
};

std::vector<Node> ModulesInTopologicalOrder(const std::vector<Node>& mods) {
  std::map<Node, std::set<Node>> deps_in;
  std::map<Node, std::set<Node>> deps_out;

  for (Node mod : mods) {
    for (Node child = Node_body_mod(mod); !child.isnull();
         child = Node_next(Node(child))) {
      if (Node_kind(child) == NT::Import) {
        Node importee = Node_x_module(child);
        ASSERT(Node_kind(importee) == NT::DefMod,
               "in " << Node_name(mod) << " :: " << Node_name(child)
                     << " expected DefMod got "
                     << EnumToString(Node_kind(importee)));
        deps_in[mod].insert(importee);
        deps_out[importee].insert(mod);
      }
    }
  }

  std::vector<Candidate> candidates;
  for (Node mod : mods) {
    if (deps_in[mod].empty()) {
      candidates.push_back({Node_name(mod), mod});
      std::push_heap(candidates.begin(), candidates.end());
    }
  }

  std::vector<Node> out;
  while (out.size() != mods.size()) {
    std::pop_heap(candidates.begin(), candidates.end());
    Node mod = candidates.back().mod;
    candidates.pop_back();
    out.push_back(mod);
    for (Node importer : deps_out[mod]) {
      deps_in[importer].erase(mod);
      if (deps_in[importer].empty()) {
        candidates.push_back({Node_name(importer), importer});
        std::push_heap(candidates.begin(), candidates.end());
      }
    }
  }
  return out;
}
void ResolvePolyMods(const std::vector<Node>& mods_in_topo_order) {
  for (Node mod : mods_in_topo_order) {
    for (Node fun = Node_body_mod(mod); !fun.isnull(); fun = Node_next(fun)) {
      if (Node_kind(fun) == NT::DefFun && Node_has_flag(fun, BF::POLY)) {
        Node ref_mod = Node_x_import(fun).isnull()
                           ? mod
                           : Node_x_module(Node_x_import(fun));
        ASSERT(!ref_mod.isnull(), "");
#if 0
        std::cout << "@@ ResolvPhePolyMods " << Node_name(ref_mod)
                  << " "<<  Node_name(fun) << "\n";
#endif
        Node_x_poly_mod(fun) = ref_mod;
      }
    }
  }
}

void SpecializeGenericModule(Node mod, const std::vector<Node>& args) {
  ASSERT(Node_kind(mod) == NT::DefMod, "");
  ASSERT(NodeNumSiblings(Node_params_mod(mod)) == args.size(), "");
  std::unordered_map<Name, Node> arg_map;
  int i = 0;
  for (Node p = Node_params_mod(mod); !p.isnull(); p = Node_next(p), ++i) {
    ASSERT(Node_kind(p) == NT::ModParam, "");
    Node a = args[i];
    switch (Node_kind(a)) {
      case NT::DefFun:
      case NT::DefRec:
      case NT::DefType:
      case NT::DefEnum: {
        Node id = NodeNew(NT::Id);
        NodeInitId(id, Node_name(a), kStrInvalid, Node_srcloc(p), a,
                   kCanonTypeInvalid);
        arg_map[Node_name(p)] = id;
        break;
      }
      case NT::ValVoid:
      case NT::ValNum:
      // fallthrough
      default:
        arg_map[Node_name(p)] = a;
        break;
    }
  }
  Node child = Node_params_mod(mod);
  while (!child.isnull()) {
    Node next = Node_next(child);
    NodeFreeRecursively(child);
    child = next;
  }
  Node_params_mod(mod) = kNodeInvalid;
  NodeToNodeMap dummy1;
  NodeToNodeMap dummy2;
  auto replacer = [&dummy1, &dummy2, &arg_map](Node node, Node parent) {
    if (Node_kind(node) == NT::MacroId) {
      auto it = arg_map.find(Node_name(node));
      ASSERT(it != arg_map.end(), "");
      NodeFreeRecursively(node);
      return NodeCloneRecursively(it->second, &dummy1, &dummy2);
    } else {
      return node;
    }
  };
  MaybeReplaceAstRecursivelyPost(mod, replacer, kNodeInvalid);
  for (auto& kv : arg_map) {
    if (Node_kind(kv.second) == NT::Id) {
      NodeFreeRecursively(kv.second);
    }
  }
}

}  // namespace

Node ReadMod(const Path& path) {
  Path with_suffix = path;
  with_suffix.replace_extension(".cw");
  Path absolute = std::filesystem::absolute(with_suffix.lexically_normal());
  // std::cout << "ReadMod [" << absolute << "] as [" << path.filename() <<
  // "]\n";
  auto data = ReadFile(with_suffix.c_str());

  Path filename = path.stem();
  Name name = NameNew(filename.c_str());
  Lexer lexer(data, NameNew(absolute.string()));
  int before = gStripeGroupNode.NextAvailable();
  Node mod = ParseDefMod(&lexer, name);
  if (sw_verbose.Value()) {
    std::cout << "ReadMod [" << path << "] bytes=" << data.size()
              << " lines=" << lexer.LinesProcessed()
              << " nodes=" << gStripeGroupNode.NextAvailable() - before << "\n";
  }
  return mod;
}

Node FindFun(Node mod, Name name) {
  for (Node child = Node_body_mod(mod); !child.isnull();
       child = Node_next(Node(child))) {
    if (Node_kind(child) == NT::DefFun && Node_name(child) == name) {
      return child;
    }
  }
  return kNodeInvalid;
}

ModPool ReadModulesRecursively(Path root_path,
                               const std::vector<Path>& seed_modules,
                               bool add_builtin,
                               std::function<Node(Path)> read_mod_fun) {
  Name name_main = NameNew("main");
  ModPoolState state;
  ModPool out;
  std::vector<ModInfo> active;
  if (add_builtin) {
    Path path = ModUniquePathName(root_path, PATH_INVALID, "builtin");
    Node mod = read_mod_fun(path);
    ModInfo mi = state.AddModInfo(path, {}, mod);
    active.push_back(mi);
    out.builtin_symtab = mi.symtab;
  }
  for (const auto& filename : seed_modules) {
    Path path = ModUniquePathName(root_path, PATH_INVALID, filename.c_str());
    Node mod = read_mod_fun(path);
    ModInfo mi = state.AddModInfo(path, {}, mod);
    if (out.main_fun.isnull()) {
      out.main_fun = FindFun(mod, name_main);
    }
    active.push_back(mi);
  }

  std::vector<ModInfo> new_active;
  while (!active.empty()) {
    ResolveGlobalAndImportedSymbolsOutsideFunctionsAndMacros(
        state.AllMods(), out.builtin_symtab);
    new_active.clear();
    for (ModInfo& mi_importer : active) {
      // std::cout << "\nHandle Imports for Mod: " << mi_importer.mid.path <<
      // "\n";
      size_t num_unresolved_imports = 0;
      for (auto& import_info : mi_importer.imports) {
        if (import_info.HasBeenResolved()) {
          continue;
        }
        if (import_info.IsParameterized() &&
            !import_info.TryNormalizeModArg()) {
          ++num_unresolved_imports;
          continue;
        }

        std::string pathname;
        if (Node_path(import_info.import_node) == kStrInvalid) {
          pathname = NameData(Node_name(import_info.import_node));
        } else {
          pathname = StrData(Node_path(import_info.import_node));
          if (pathname[0] == '"') {
            pathname = pathname.substr(1, pathname.size() - 2);
          }
        }
        Path path =
            ModUniquePathName(root_path, mi_importer.mid.path, pathname);
        ModInfo mi;
        if (import_info.NumArgs() == 0) {
          ModId mid(path);
          if (state.HasModInfo(mid)) {
            mi = state.GetModInfo(mid);
          } else {
            Node mod = read_mod_fun(path);
            mi = state.AddModInfo(path, {}, mod);
            new_active.push_back(mi);
          }
        } else {
          if (sw_verbose.Value()) {
            std::cout << "SpecialGenericMod [" << path << "] " << "\n";
          }
          Node mod = state.GetCloneOfGenericMod(path, read_mod_fun);
          SpecializeGenericModule(mod, import_info.normalized_args);
          mi = state.AddModInfo(path, import_info.normalized_args, mod);
          new_active.push_back(mi);
        }

        import_info.ResolveImport(mi.mod);
      }
      if (num_unresolved_imports > 0) {
        new_active.push_back(mi_importer);
      }
    }
    active.swap(new_active);
  }
  const auto all_mods = state.AllMods();
  out.mods_in_topo_order = ModulesInTopologicalOrder(all_mods);
  ASSERT(out.mods_in_topo_order.size() == all_mods.size(), "");
  ResolvePolyMods(out.mods_in_topo_order);
  ResolveGlobalAndImportedSymbolsInsideFunctionsAndMacros(
      out.mods_in_topo_order, out.builtin_symtab);
  for (Node mod : out.mods_in_topo_order) {
    RemoveNodesOfType(mod, NT::Import);
  }
  return out;
}

}  // namespace cwerg::fe