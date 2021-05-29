// This examples shows how to jit a32 assembly directly (not cwerg IR)
#include "CpuA64/opcode_gen.h"
#include "CpuA64/symbolic.h"
#include "Util/assert.h"

#include <sys/mman.h>
#include <iostream>

using namespace cwerg::a64;

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
  std::cout << "0x" << std::hex << data << " " << enum_name;
  std::string_view sep = " ";
  for (const std::string& op : ops) {
    std::cout << sep << op;
    sep = ", ";
  }
  std::cout << "\n";
}

// encode a OK.SIMM_0_23
constexpr uint32_t encode_bl_offset(int32_t offset) {
  return offset & 0x3ffffff;
}

#define OPCODE(o) &OpcodeTable[+OPC::o]

uint32_t offset8(int32_t x) {
  return (x >> 3) & 0x7f;
}

#define SP 31
#define XZR 31
#define LSL 0

int main(int argc, char* argv[]) {
  // TODO: create enums so we do not have to use unintuitve numbers
  const Ins Fibonacci[] = {
      // prolog
      {OPCODE(stp_x_imm_pre), {SP, offset8(-16), 29, 30}},
      {OPCODE(stp_x_imm_pre), {SP, offset8(-16), 27, 28}},
      //
      {OPCODE(subs_x_imm), {XZR, 0, 1}},
      {OPCODE(b_ls), {8}},
      // difficult part:
      {OPCODE(orr_x_reg), {29, XZR, 0, LSL, 0}},
      {OPCODE(subs_x_imm), {0, 29, 1}},
      {OPCODE(bl), {encode_bl_offset(-6)}},
      {OPCODE(orr_x_reg), {28, XZR, 0, LSL, 0}},
      {OPCODE(subs_x_imm), {0, 29, 2}},
      {OPCODE(bl), {encode_bl_offset(-9)}},
      {OPCODE(add_x_reg), {0, 0, 28, LSL, 0}},
      // epilog
      {OPCODE(ldp_x_imm_post), {27, 28, SP, offset8(16)}},
      {OPCODE(ldp_x_imm_post), {29, 30, SP, offset8(16)}},
      {OPCODE(ret), {30}}
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
