// This examples shows how to jit a32 assembly directly (not cwerg IR)
#include "CpuA32/opcode_gen.h"
#include "CpuA32/symbolic.h"
#include "Util/assert.h"

#include <sys/mman.h>
#include <iostream>

using namespace cwerg::a32;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

using FunPtr = uint32_t (*)(uint32_t);

void DumpIns(uint32_t data) {
  Ins ins;
  Disassemble(&ins, data);
  std::vector<std::string> ops;
  std::string_view enum_name = InsSymbolize(ins, &ops);
  std::cerr << "0x" << std::hex << data << " " << enum_name;
  std::string_view sep = " ";
  for (const std::string& op : ops) {
    std::cerr << sep << op;
    sep = ", ";
  }
  std::cerr << "\n";
}

// encode a OK.SIMM_0_23
constexpr uint32_t encode_branch_offset(int32_t offset) {
  return offset & 0xffffff;
}

#define OPCODE(o) &OpcodeTable[+OPC::o]

int main(int argc, char* argv[]) {
  const Ins Fibonacci[] = {
      //
      {OPCODE(stmdb_update), {+PRED::al, +REG::sp, 0x4030}},
      {OPCODE(cmp_imm), {+PRED::al, +REG::r0, 1}},
      {OPCODE(b), {+PRED::le, encode_branch_offset(7)}},
      //
      {OPCODE(mov_imm), {+PRED::al, +REG::r4, 0}},
      {OPCODE(mov_regimm), {+PRED::al, +REG::r5, +REG::r0, +SHIFT::lsl, 0}},
      //
      {OPCODE(sub_imm), {+PRED::al, +REG::r0, +REG::r5, 1}},
      {OPCODE(bl), {+PRED::al, encode_branch_offset(-8)}},
      {OPCODE(add_regimm),
       {+PRED::al, +REG::r4, +REG::r4, +REG::r0, +SHIFT::lsl, 0}},
      //
      {OPCODE(sub_imm), {+PRED::al, +REG::r0, +REG::r5, 2}},
      {OPCODE(bl), {+PRED::al,encode_branch_offset(-11)}},
      {OPCODE(add_regimm),
       {+PRED::al, +REG::r0, +REG::r4, +REG::r0, +SHIFT::lsl, 0}},
      //
      {OPCODE(ldmia_update), {+PRED::al, 0x8030, +REG::sp}}

  };

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
  return 0;
}
