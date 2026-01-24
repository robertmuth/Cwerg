#pragma once
// (c) Robert Muth - see LICENSE for more info
//

#include <string>

#include "FE/cwast_gen.h"
#include "FE/type_corpus.h"


namespace cwerg::fe {

extern std::string MakeFunSigName(CanonType ct);

extern void EmitFunctionHeader(std::string_view sig_name, std::string_view kind,
                               CanonType ct);

extern uint32_t EmitIRDefGlobal(Node node, const TargetArchConfig& ta);

// extern void EmitIRDefFun(Node node, const TargetArchConfig& ta);

}  // namespace cwerg::fe