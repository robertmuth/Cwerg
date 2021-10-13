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

using FunPtr = uint32_t (*)(uint32_t);

int main(int argc, char* argv[]) {
  // Set-up internal memory pools.
  InitStripes(1);
  code_gen_a64::InitCodeGenA64();

  // Generate IR and translate to A64
  base::Unit unit = MakeFibonacci();
  code_gen_a64::LegalizeAll(unit, false, nullptr);
  code_gen_a64::RegAllocGlobal(unit, false, nullptr);
  code_gen_a64::RegAllocLocal(unit, false, nullptr);
  a64::A64Unit a64unit = code_gen_a64::EmitUnitAsBinary(unit, false);
  std::cerr << std::hex;
  std::cerr
            << "RODATA SIZE: 0x" << a64unit.sec_rodata->data->size() << "\n"
            << "TEXT SIZE:   0x" << a64unit.sec_text->data->size() << "\n"
            << "DATA SIZE:   0x" << a64unit.sec_data->data->size() << "\n"
            << "BSS SIZE:    0x" << a64unit.sec_bss->data->size() << "\n";

  // Allocate space for Section data
  uint32_t* text_memory =
      (uint32_t*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

  ASSERT(text_memory != nullptr, "");
  a64unit.sec_text->shdr.sh_addr = (uint64_t)text_memory;
  std::cerr << "text addr: " << text_memory << "\n";

  // Compute Symbol Addresses and Relocate
  for (auto& sym : a64unit.symbols) {
    ASSERT(sym->sym.st_value != ~0U, "undefined symbol " << sym->name);
    if (sym->section != nullptr) {
      ASSERT(sym->section->shdr.sh_addr != ~0U,
             sym->name << "has bad sec " << *sym->section);
      sym->sym.st_value += sym->section->shdr.sh_addr;
      std::cerr << "sym [" << sym->name << "]: 0x" <<   sym->sym.st_value << "\n";
    }
  }

  for (auto& rel : a64unit.relocations) {
    a64::ApplyRelocation(rel);
  }

  // Copy Section dats to their final destination
  memcpy(text_memory, a64unit.sec_text->data->data(), a64unit.sec_text->data->size());

  // Invoke JITed code
  FunPtr f = reinterpret_cast<FunPtr>(text_memory);
  for (unsigned i = 0; i < 10; ++i) {
    std::cout << std::dec << i << " " << f(i) << "\n";
  }
  return 0;
}
