#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
#include "FE/lexer.h"

namespace cwerg::fe {

extern Node ParseDefMod(Lexer* lexer);
extern void InitParser();

} // amespace cwerg::fe