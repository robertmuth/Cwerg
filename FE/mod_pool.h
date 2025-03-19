#pragma once
// (c) Robert Muth - see LICENSE for more info
#include <cstdint>
#include <filesystem>
#include <set>
#include <string>
#include <string_view>
#include <vector>

// only used for interning comment strings
#include "FE/cwast_gen.h"
#include "FE/lexer_gen.h"
#include "FE/symbolize.h"
#include "Util/assert.h"

namespace cwerg::fe {

using Path = std::filesystem::path;

extern const Path PATH_INVALID;

inline Path ModUniquePathName(const Path& root_path, const Path& curr_path,
                              std::string_view pathname) {
  Path path(pathname);
  if (path.is_absolute()) {
    return std::filesystem::canonical(path);
  } else if (pathname.starts_with(".")) {
    return curr_path.parent_path() / path;
  } else {
    return root_path / path;
  }
}

struct ModId {
 public:
  Path path;
  std::vector<Node> args;  // for generic  modules
};


struct ModInfo {
  ModId mid;
  Node mod = Node(kHandleInvalid);
  SymTab* symtab = nullptr;

  bool IsValid() { return mod.raw_kind() != kKindInvalid; }
};


class ModPool {
  Path root_path_;
  // ModInfo main_modinfo_ = ModInfoInvalid;
  // ModInfo builtin_modinfo_ = ModInfoInvalid;
  std::vector<SymTab*> symtabs_;

 public:
  ModPool(const Path& path) : root_path_(path) {}

  void ReadModulesRecursively(const std::vector<Path>& seed_modules,
                              bool add_builtin);

  inline SymTab* BuiltinSymtab() const { return symtabs_[0]; }

  Node MainEntryFun() const;

  ModInfo AddModInfoSimple(const Path& path, SymTab* symtab);
};

}  // namespace cwerg::fe
