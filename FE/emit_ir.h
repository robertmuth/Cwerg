#pragma once
// (c) Robert Muth - see LICENSE for more info
//

#include <string>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"
#include "FE/identifier.h"

namespace cwerg::fe {

extern std::string MakeFunSigName(CanonType ct);

extern void EmitFunctionHeader(std::string_view sig_name, std::string_view kind,
                               CanonType ct, std::ostream* fout);

extern uint32_t EmitDefGlobal(Node node, const TargetArchConfig& ta, std::ostream* fout);

extern void EmitDefFun(Node node, const TargetArchConfig& ta,
                       IdGenIR* id_gen, std::ostream* fout);
}  // namespace cwerg::fe