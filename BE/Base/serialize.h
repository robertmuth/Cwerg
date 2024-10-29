// (c) Robert Muth - see LICENSE for more info
#pragma once

#include <iostream>

#include "BE/Base/ir.h"

namespace cwerg::base {

extern bool UnitAppendFromAsm(Unit unit, std::string_view input,
                             const std::vector<CpuReg>& cpu_regs);

inline Unit UnitParseFromAsm(const char* name, std::string_view input,
                             const std::vector<CpuReg>& cpu_regs) {
    Unit unit = UnitNew(StrNew(name));       
    if (UnitAppendFromAsm(unit, input, cpu_regs)) return unit;
    return Unit(0);  // unit leaks
}
                             
extern void InsRenderToAsm(Ins ins, std::ostream* output);
extern void BblRenderToAsm(Bbl bbl, Fun fun, std::ostream* output,
                           bool number = false);
extern void FunRenderToAsm(Fun fun, std::ostream* output, bool number = false);
extern void MemRenderToAsm(Mem mem, std::ostream* output);
extern void UnitRenderToAsm(Unit unit, std::ostream* output);

extern void RenderRegBitVec(Fun fun, BitVec bv, std::ostream* output);

extern void EmitParamList(unsigned num_types, DK* types, std::ostream* output);

inline std::ostream& operator<<(std::ostream& os, Mem mem) {
  MemRenderToAsm(mem, &os);
  return os;
}

inline std::ostream& operator<<(std::ostream& os, Ins ins) {
  InsRenderToAsm(ins, &os);
  return os;
}

inline std::ostream& operator<<(std::ostream& os, Bbl bbl) {
  BblRenderToAsm(bbl, Fun(0), &os);
  return os;
}

inline std::ostream& operator<<(std::ostream& os, Fun fun) {
  FunRenderToAsm(fun, &os);
  return os;
}

inline std::ostream& operator<<(std::ostream& os, Unit unit) {
  UnitRenderToAsm(unit, &os);
  return os;
}

}  // namespace cwerg::base
