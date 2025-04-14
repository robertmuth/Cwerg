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
    // return std::filesystem::canonical(path);
    return path;
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
  Node mod = kNodeInvalid;
  SymTab* symtab = nullptr;

  bool IsValid() { return mod.raw_kind() != kKindInvalid; }
};

struct ModPool {
   SymTab* builtin_symtab = nullptr;
   Node main_entry_fun;
};

ModPool ReadModulesRecursively(Path root_path,
                               const std::vector<Path>& seed_modules,
                               bool add_builtin);


}  // namespace cwerg::fe
