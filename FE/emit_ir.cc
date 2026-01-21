#include "FE/emit_ir.h"

#include <span>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "Util/assert.h"

namespace cwerg::fe {

void FunMachineTypes(CanonType ct, std::vector<std::string>* res_types,
                     std::vector<std::string>* arg_types) {
  ASSERT(CanonType_is_fun(ct), "");

  std::span<CanonType> children = CanonType_children(ct);
  DK rt = CanonType_ir_regs(children[children.size() - 1]);
  if (rt != DK::NONE) {
    res_types->push_back(EnumToString(rt));
  }

  for (CanonType at_ct : children.subspan(0, children.size() - 1)) {
    DK at = CanonType_ir_regs(at_ct);
    ASSERT(at != DK::NONE && at != DK::MEM, "");
    arg_types->push_back(EnumToString(at));
  }
}

std::string MakeFunSigName(CanonType ct) {
  std::vector<std::string> res_types;
  std::vector<std::string> arg_types;
  FunMachineTypes(ct, &res_types, &arg_types);
  if (res_types.empty()) res_types.push_back("void");
  if (arg_types.empty()) arg_types.push_back("void");

  std::string sig_name = "$sig";
  std::string sep = "/";
  for (const std::string& rt : res_types) {
    sig_name += sep;
    sig_name += rt;
    sep = "_";
  }
  for (const std::string& rt : arg_types) {
    sig_name += sep;
    sig_name += rt;
    sep = "_";
  }
  return sig_name;
}

void EmitFunctionHeader(std::string_view sig_name, std::string_view kind,
                        CanonType ct) {
  std::vector<std::string> res_types;
  std::vector<std::string> arg_types;
  FunMachineTypes(ct, &res_types, &arg_types);
  std::cout << "\n\n.fun " << sig_name << " " << kind << " [";
  std::string sep = "";
  for (const std::string& rt : res_types) {
    std::cout << sep << rt;
    sep = " ";
  }
  std::cout << "] = [";
  sep = "";
  for (const std::string& rt : arg_types) {
    std::cout << sep << rt;
    sep = " ";
  }
  std::cout << "]\n";
}

}  // namespace cwerg::fe