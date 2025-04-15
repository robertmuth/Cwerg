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
  std::cout << "ReadMod " << path << " as " << path.filename() << "\n";

  Path filename = path.filename();
  Path with_suffix = path;
  with_suffix.replace_extension(".cw");
  auto data = ReadFile(with_suffix.c_str());
  std::cout << "ReadMod " << path << " size=" << data.size() << "\n";

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
  InitImport(dummy_import, NameNew("$self"), kStrInvalid, kNodeInvalid,
             kStrInvalid, kSrcLocInvalid);
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
      case NT::DefType:
      case NT::DefEnum:
      case NT::DefGlobal:
      case NT::DefMacro:
      case NT::DefRec: {
        auto name = NameStrAndSeq(Node_name(child));
        // std::cout << "@@@ " << EnumToString(Node_kind(child)) << " " << name
        // << "\n";
        // TODO: special handling of polymorphic functions
        if (symtab->contains(name)) {
          CompilerError(Node_srcloc(child)) << "duplicate symbol " << name;
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

void Dump(SymTab* symtab) {
  for (auto& kv : *symtab) {
    std::cout << kv.first << " -> " << EnumToString(Node_kind(kv.second))
              << "\n";
  }
}

struct ModPoolState {
  // ModInfo main_modinfo_ = ModInfoInvalid;
  // ModInfo builtin_modinfo_ = ModInfoInvalid;
  std::vector<SymTab*> symtabs;

  // TODO: add args argument
  ModInfo AddModInfoCommon(const Path& path, Node mod, SymTab* symtab) {
    // TODO
    return ModInfo();
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
    out.builtin_symtab = symtab;

    ModInfo mi = state.AddModInfoSimple(path, symtab);
    active.push_back(mi);
    // builtin_modinfo_ = mi;
  }
  for (const auto& filename : seed_modules) {
    Path path = ModUniquePathName(root_path, PATH_INVALID, filename.c_str());

    SymTab* symtab = new SymTab();
    ModInfo mi = state.AddModInfoSimple(path, symtab);
    active.push_back(mi);
  }
  return out;
}

}  // namespace cwerg::fe