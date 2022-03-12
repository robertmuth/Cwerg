// This examples shows how to jit x64 assembly directly (not cwerg IR)
#include <sys/mman.h>

#include <iostream>

#include "CpuX64/opcode_gen.h"
#include "CpuX64/symbolic.h"
#include "Util/assert.h"

using namespace cwerg::x64;

// +-prefix converts an enum the underlying type
template <typename T>
constexpr auto operator+(T e) noexcept
    -> std::enable_if_t<std::is_enum<T>::value, std::underlying_type_t<T>> {
  return static_cast<std::underlying_type_t<T>>(e);
}

using FunPtr = uint32_t (*)(uint32_t);

void DumpIns(char* data, uint32_t offset) {
  Ins ins;
  Disassemble(&ins, std::string_view(data, 16));
  std::vector<std::string> ops;
  std::string_view enum_name = InsSymbolize(ins, true, false, &ops);
  std::cerr << "0x" << std::hex << offset << std::dec << " " << enum_name;
  std::string_view sep = " ";
  for (const std::string& op : ops) {
    std::cerr << sep << op;
    sep = ", ";
  }
  std::cerr << "\n";
}

#define OPCODE(o) &OpcodeTableEncodings[+OPC::o]

#define RAX 0
#define RBX 3
#define RDI 7
#define R14 14

int32_t pcoffset(const unsigned* ins_length, unsigned src, unsigned dst) {
  int32_t out = 0;
  for (unsigned i = src; i < dst; ++i) {
    out += ins_length[i];
  }
  return out;
}

int main(int argc, char* argv[]) {
  // TODO: create enums so we do not have to use unintuitve numbers
  Ins Fibonacci[] = {
    // prolog
    {OPCODE(push_64_r), {R14}},
    {OPCODE(push_64_r), {RBX}},
    {OPCODE(push_64_r), {RBX}},  // dummy to force 16byte aligned stack
    //
    {OPCODE(cmp_64_mr_imm8), {RDI, 2}},
    {OPCODE(jb_8), {0}},  // to be updated later
    //
    {OPCODE(mov_64_mr_r), {RBX, RDI}},
    {OPCODE(xor_32_mr_r), {R14, R14}},
    {OPCODE(sub_64_mr_imm8), {RDI, 1}},
    {OPCODE(call_32), {0}},  // to be updated later
    {OPCODE(add_64_mr_r), {R14, RAX}},
    //
    {OPCODE(mov_64_mr_r), {RDI, RBX}},
    {OPCODE(sub_64_mr_imm8), {RDI, 2}},
    {OPCODE(call_32), {0}},  // to be updated later
    {OPCODE(add_64_mr_r), {R14, RAX}},
    {OPCODE(mov_64_mr_r), {RDI, R14}},
    // epilog
    {OPCODE(mov_64_mr_r), {RAX, RDI}},
    {OPCODE(pop_64_r), {RBX}},
    {OPCODE(pop_64_r), {RBX}},
    {OPCODE(pop_64_r), {R14}},
    {OPCODE(ret), {}}
  };

  // hack to get instruction lengths
  unsigned ins_length[100];
  int i = 0;
  for (const auto& ins : Fibonacci) {
    ins_length[i++] = UsesRex(ins) + ins.opcode->num_bytes;
  }

  ASSERT(Fibonacci[4].opcode->fields[0] == OK::OFFPCREL8, "");
  Fibonacci[4].operands[0] = pcoffset(ins_length, 5, 15);
  ASSERT(Fibonacci[8].opcode->fields[0] == OK::OFFPCREL32, "");
  Fibonacci[8].operands[0] = -pcoffset(ins_length, 0, 9);
  ASSERT(Fibonacci[12].opcode->fields[0] == OK::OFFPCREL32, "");
  Fibonacci[12].operands[0] = -pcoffset(ins_length, 0, 13);

  char* const memory =
      (char*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  ASSERT(memory != nullptr, "");
  char* data = memory;
  for (const auto& ins : Fibonacci) {
    uint32_t length = Assemble(ins, data);
    DumpIns(data, data - memory);
    data += length;
  }

  FunPtr f = reinterpret_cast<FunPtr>(memory);
  for (unsigned i = 0; i < 10; ++i) {
    std::cout << std::dec << i << " " << f(i) << "\n";
  }
  return 0;
}
