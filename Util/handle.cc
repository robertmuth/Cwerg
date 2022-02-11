#include "Util/handle.h"

namespace cwerg {

namespace {

constexpr const char* kRefKindNames[] = {
    "INVALID",  //
    "FREE",     //
    "INS",      //
    "EDG",      //
    "BBL",      //
    "FUN",      //
    "UNIT",     //
    "STR",      //
    "CONST"     //
    "REG",      //
    "STK",      //
    "MEM",      //
    "DATA",     //
    "JTB",      //
    "JEN",      //
    "CPU_REG",  //
    "STACK_SLOT",
};

}  // namespace

const char* EnumToString(RefKind x) { return kRefKindNames[unsigned(x)]; }

}  // namespace cwerg
