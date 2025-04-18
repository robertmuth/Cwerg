#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

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

namespace cwerg::fe {

using namespace cwerg;
using namespace cwerg::fe;

const Path PATH_INVALID;

struct ImportInfo {
  Node import_node;
  std::vector<Node> normalized_args;

  ImportInfo(Node a_import_node) : import_node(a_import_node) {
    ASSERT(Node_kind(a_import_node) == NT::Import, "");
    // TODO:)
    for (Node child = Node_args_mod(a_import_node); !child.isnull();
         child = Node_next(Node(child))) {
      normalized_args.push_back(kNodeInvalid);
    }
  }

  int NumArgs() const {
    int n = 0;
    for (Node child = Node_args_mod(import_node); !child.isnull();
         child = Node_next(Node(child))) {
      ++n;
    }
    return n;
  }

  void ResolveImport(Node imported_mod) {
    ASSERT(Node_kind(imported_mod) == NT::DefMod, "");
    Node_x_module(import_node) = imported_mod;
  }
};

struct ModInfo {
  ModId mid;
  Node mod = kNodeInvalid;
  SymTab* symtab = nullptr;
  std::vector<ImportInfo> imports;

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

Node ReadMod(const Path& path) {
  std::cout << "ReadMod [" << path << "] as [" << path.filename() << "]\n";

  Path filename = path.filename();
  Path with_suffix = path;
  with_suffix.replace_extension(".cw");
  auto data = ReadFile(with_suffix.c_str());
  std::cout << "ReadMod [" << path << "] size=" << data.size() << "\n";

  // TODO: fix magic number
  Lexer lexer(data, 666);
  return ParseDefMod(&lexer, NameNew(filename.c_str()));
}

void Dump(Node node) {
  std::vector<Node> stack;
  int indent = -4;
  auto pre_visitor = [&stack, &indent](Node node, Node parent) {
    if (stack.empty() || stack.back() != parent) {
      stack.push_back(parent);
      indent += 4;
    }

    std::cout << std::setw(indent) << " " << EnumToString(Node_kind(node))
              << "\n";
  };
  auto post_visitor = [&stack, &indent](Node node, Node parent) {
    if (stack.back() != parent) {
      stack.pop_back();
      indent -= 4;
    }
  };
  VisitNodesRecursivelyPreAndPost(node, pre_visitor, post_visitor,
                                  kNodeInvalid);
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
      return NameNew(str + pos + 1);
    }
  }
  return kNameInvalid;
}

void ResolveImportsForQualifers(Node mod) {
  std::map<StrAndSeq, Node> imports;

  Node dummy_import = NodeNew(NT::Import);
  InitImport(dummy_import, NameNew("$$self", MAGIC_SELF_IMPORT_SEQ),
             kStrInvalid, kNodeInvalid, kStrInvalid, kSrcLocInvalid);
  Node_x_module(dummy_import) = mod;

  auto visitor = [&dummy_import, &imports](Node node, Node parent) {
    auto annotate = [&dummy_import, &imports](Node node, Name name) -> bool {
      if (name == kNameInvalid) {
        Node_x_import(node) = dummy_import;
        return false;
      } else {
        auto it = imports.find(NameStrAndSeq(name));
        if (it == imports.end()) {
          CompilerError(Node_srcloc(node))
              << "cannot resolve qualifier [" << NameData(name) << "] "
              << name.index();
        }
        Node_x_import(node) = it->second;
        return true;
      }
    };

    switch (Node_kind(node)) {
      case NT::Import: {
        auto name = NameStrAndSeq(Node_name(node));
        if (imports.contains(name)) {
          CompilerError(Node_srcloc(node)) << "duplicate import";
        }
        imports[name] = node;
      } break;
      case NT::DefFun:
      case NT::MacroInvoke:
      case NT::Id:
        if (annotate(node, GetQualifierIfPresent(Node_name(node)))) {
          Node_name(node) = StripQualifier(Node_name(node));
        }
        break;

      default:
        break;
    }
  };
  VisitNodesRecursivelyPost(mod, visitor, kNodeInvalid);
}

void ExtractSymTabPopulatedWithGlobals(Node mod, SymTab* symtab) {
  for (Node child = Node_body_mod(mod); !child.isnull();
       child = Node_next(Node(child))) {
    switch (Node_kind(child)) {
      case NT::DefFun:
        if (Node_has_flag(child, BF::POLY)) {
          if (HasImportedSymbolReference(child) ||
              symtab->contains(NameStrAndSeq(Node_name(child)))) {
            continue;
          }
        }
      // fall through
      case NT::DefType:
      case NT::DefEnum:
      case NT::DefGlobal:
      case NT::DefMacro:
      case NT::DefRec: {
        auto name = NameStrAndSeq(Node_name(child));
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

void Dump(const SymTab* symtab) {
  std::cout << "SYMTAB " << symtab << "\n";
  for (auto& kv : *symtab) {
    std::cout << kv.first << " -> " << EnumToString(Node_kind(kv.second))
              << "\n";
  }
  std::cout << "\n";
}

class ModPoolState {
  std::vector<SymTab*> symtabs;
  std::map<ModId, ModInfo> all_mods;

 public:
  // TODO: add args argument support
  ModInfo AddModInfoCommon(const Path& path, Node mod, SymTab* symtab) {
    ASSERT(Node_kind(mod) == NT::DefMod, "");
    ModId mid = ModId(path);
    ModInfo mod_info(mid, mod, symtab);
    all_mods.insert({mid, mod_info});
    symtabs.push_back(symtab);
    Node_x_symtab(mod) = symtab;
    return mod_info;
  }

  ModInfo GetModInfo(const ModId& mid) const {
    auto it = all_mods.find(mid);
    return it->second;
  }

  bool HasModInfo(const ModId& mid) const {
    return all_mods.find(mid) != all_mods.end();
    ;
  }

  std::vector<Node> AllMods() {
    std::vector<Node> out;
    for (auto& kv : all_mods) {
      out.push_back(kv.second.mod);
    }
    return out;
  }

  ModInfo AddModInfoSimple(const Path& path, SymTab* symtab) {
    Node mod = ReadMod(path);

    ResolveImportsForQualifers(mod);
    ExtractSymTabPopulatedWithGlobals(mod, symtab);
    // Dump(mod);
    Dump(symtab);
    return AddModInfoCommon(path, mod, symtab);
  }
};

ModPool ReadModulesRecursively(Path root_path,
                               const std::vector<Path>& seed_modules,
                               bool add_builtin) {
  ModPoolState state;
  ModPool out;
  std::vector<ModInfo> active;
  if (add_builtin) {
    Path path = ModUniquePathName(root_path, PATH_INVALID, "builtin");
    SymTab* symtab = new SymTab();

    ModInfo mi = state.AddModInfoSimple(path, symtab);
    active.push_back(mi);
    out.builtin_symtab = symtab;
  }
  for (const auto& filename : seed_modules) {
    Path path = ModUniquePathName(root_path, PATH_INVALID, filename.c_str());

    SymTab* symtab = new SymTab();
    ModInfo mi = state.AddModInfoSimple(path, symtab);
    active.push_back(mi);
  }

  std::cout << "Fixpoint For Imports\n" << std::flush;
  std::vector<ModInfo> new_active;
  while (!active.empty()) {
    ResolveSymbolsRecursivelyOutsideFunctionsAndMacros(
        state.AllMods(), out.builtin_symtab, false);
    new_active.clear();
    for (ModInfo& mi : active) {
      std::cout << "Handle Imports for Mod: " << mi.mid.path << "\n";
      for (auto& import : mi.imports) {
        std::cout << "Imports [" << Node_path(import.import_node) << "] ["
                  << Node_name(import.import_node) << "]\n";

        if (!Node_x_module(import.import_node).isnull()) {
          continue;
        }

        std::string pathname;
        if (Node_path(import.import_node) == kStrInvalid) {
          pathname = Name_String(Node_name(import.import_node));
        } else {
          pathname = StrData(Node_path(import.import_node));
          if (pathname[0] == '"') {
            pathname = pathname.substr(1, pathname.size() - 2);
          }
        }
        if (import.NumArgs() == 0) {
          Path path = ModUniquePathName(root_path, mi.mid.path, pathname);
          ModId mid(path);
          if (!state.HasModInfo(mid)) {
            SymTab* symtab = new SymTab();
            ModInfo mi = state.AddModInfoSimple(path, symtab);
            new_active.push_back(mi);
          }
          ModInfo mi = state.GetModInfo(mid);
          std::cout << "Resolve import " << mi.mid << " "
                    << EnumToString(Node_kind(mi.mod)) << "\n";
          import.ResolveImport(mi.mod);
        } else {
          ASSERT(false, "");
        }
      }
    }
    active.swap(new_active);
  }

  return out;
}

}  // namespace cwerg::fe