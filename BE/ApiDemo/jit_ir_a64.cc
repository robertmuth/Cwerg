// This examples shows how to jit cwerg ir to a64 assembly

#include "BE/Base/ir.h"
#include "BE/CodeGenA64/codegen.h"
#include "BE/CodeGenA64/legalize.h"
#include "BE/CpuA64/symbolic.h"
#include "Util/assert.h"

#include <sys/mman.h>
#include <iostream>

using namespace cwerg;

#include "BE/ApiDemo/fib_ir.h"

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
  a64::A64Unit a64unit = code_gen_a64::EmitUnitAsBinary(unit);
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

  // Copy Section data to their final destination
  // Note we only have a text section
  memcpy(text_memory, a64unit.sec_text->data->data(), a64unit.sec_text->data->size());

  // Invoke JITed code. This assumes that the calling convention of the
  // JITed code matches the platform ABI. This is only true for simple cases.
  FunPtr f = reinterpret_cast<FunPtr>(text_memory);
  for (unsigned i = 0; i < 10; ++i) {
    std::cout << std::dec << i << " " << f(i) << "\n";
  }
  return 0;
}
