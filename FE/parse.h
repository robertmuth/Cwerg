#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "FE/cwast_gen.h"
#include "FE/lexer.h"

namespace cwerg::fe {

// Must be called once at start-up
extern void InitParser();

extern Node ParseDefMod(Lexer* lexer, Name name);

} // namespace cwerg::fe