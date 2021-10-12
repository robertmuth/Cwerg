// This examples shows how to jit cwerg ir to a64 assembly

#include "Base/ir.h"
#include "CodeGenA64/codegen.h"
#include "CodeGenA64/legalize.h"
#include "CpuA64/symbolic.h"
#include "Util/assert.h"

#include <sys/mman.h>
#include <iostream>

using namespace cwerg;

base::Unit MakeFibonacci() {
  using namespace cwerg::base;

  Unit unit = UnitNew(StrNew("fibonacci"));
  Fun fun = UnitFunAdd(unit, FunNew(StrNew("fib"), FUN_KIND::NORMAL));
  FunOutputTypes(fun)[0] = DK::U32;
  FunNumOutputTypes(fun) = 1;
  FunInputTypes(fun)[0] = DK::U32;
  FunNumInputTypes(fun) = 1;
  Bbl bbl_start = FunBblAdd(fun, BblNew(StrNew("start")));
  Bbl bbl_difficult = FunBblAdd(fun, BblNew(StrNew("difficult")));
  Reg reg_in = FunRegAdd(fun, RegNew(DK::U32, StrNew("in")));
  Reg reg_out = FunRegAdd(fun, RegNew(DK::U32, StrNew("out")));
  Reg reg_x = FunRegAdd(fun, RegNew(DK::U32, StrNew("x")));
  Const zero = ConstNewU(DK::U32, 0);
  Const one = ConstNewU(DK::U32, 1);
  Const two = ConstNewU(DK::U32, 2);
  // start
  BblInsAdd(bbl_start, InsNew(OPC::POPARG, reg_in));
  BblInsAdd(bbl_start, InsNew(OPC::BLT, one, reg_in, bbl_difficult));
  BblInsAdd(bbl_start, InsNew(OPC::PUSHARG, reg_in));
  BblInsAdd(bbl_start, InsNew(OPC::RET));
  // difficult
  BblInsAdd(bbl_difficult, InsNew(OPC::MOV, reg_out, zero));
  BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, one));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
  BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::SUB, reg_x, reg_in, two));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::BSR, fun));
  BblInsAdd(bbl_difficult, InsNew(OPC::POPARG, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::ADD, reg_out, reg_out, reg_x));
  BblInsAdd(bbl_difficult, InsNew(OPC::PUSHARG, reg_out));
  BblInsAdd(bbl_difficult, InsNew(OPC::RET));

  return unit;
}

int main(int argc, char* argv[]) {
  // Set-up internal memory pools.
  InitStripes(1);
  code_gen_a64::InitCodeGenA64();

  base::Unit unit = MakeFibonacci();
  code_gen_a64::LegalizeAll(unit, false, nullptr);
  code_gen_a64::RegAllocGlobal(unit, false, nullptr);
  code_gen_a64::RegAllocLocal(unit, false, nullptr);
  a64::A64Unit a64unit = code_gen_a64::EmitUnitAsBinary(unit, false);
  std::cout << std::hex  //
            << "RODATA SIZE: 0x" << a64unit.sec_rodata->data->size() << "\n"
            << "TEXT SIZE:   0x" << a64unit.sec_text->data->size() << "\n"
            << "DATA SIZE:   0x" << a64unit.sec_data->data->size() << "\n"
            << "BSS SIZE:    0x" << a64unit.sec_bss->data->size() << "\n"
            << std::dec;

#if 0



  uint32_t* memory =
      (uint32_t*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  ASSERT(memory != nullptr, "");
  unsigned i = 0;
  for (const auto& ins : Fibonacci) {
    memory[i] = Assemble(ins);
    DumpIns(memory[i]);
    ++i;
  }

  FunPtr f = reinterpret_cast<FunPtr>(memory);
  for (unsigned i = 0; i < 10; ++i) {
    std::cout << std::dec << i << " " << f(i) << "\n";
  }
#endif
  return 0;
}
