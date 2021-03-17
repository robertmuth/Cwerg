
#include "CpuA32/disassembler.h"
#include "CpuA32/opcode_gen.h"
#include "Util/assert.h"

#include <sys/mman.h>
#include <iostream>

using namespace cwerg::a32;

template <typename X>
uint16_t u(X x) {
  return uint16_t(x);
}

using FunPtr = uint32_t (*)(uint32_t);

void DumpA32Ins(uint32_t data) {
  Ins ins;
  DecodeIns(&ins, data);
  std::cout << "0x" << std::hex << data << " " << ins.opcode->enum_name;
  std::string_view sep = " ";
  for (unsigned i = 0; i < ins.opcode->num_fields; ++i) {
    char buf[128];
    RenderOperandStd(buf, *ins.opcode, ins.operands[i], ins.opcode->fields[i]);
    std::cout << sep << buf;
    sep = ", ";
  }
  std::cout << "\n";
}

Ins Fibonacci[] = {
    //
    {&OpcodeTable[u(OPC::stmdb_update)], {u(PRED::al), u(REG::sp), 0x4030}},
    {&OpcodeTable[u(OPC::cmp_imm)], {u(PRED::al), u(REG::r0), 1}},
    {&OpcodeTable[u(OPC::b)], {u(PRED::le), 7}},
    //
    {&OpcodeTable[u(OPC::mov_imm)], {u(PRED::al), u(REG::r4), 0}},
    {&OpcodeTable[u(OPC::mov_regimm)],
     {u(PRED::al), u(REG::r5), u(REG::r0), u(SHIFT::lsl), 0}},
    //
    {&OpcodeTable[u(OPC::sub_imm)], {u(PRED::al), u(REG::r0), u(REG::r5), 1}},
    {&OpcodeTable[u(OPC::bl)], {u(PRED::al), u(REG::lr), -8}},
    {&OpcodeTable[u(OPC::add_regimm)],
     {u(PRED::al), u(REG::r4), u(REG::r4), u(REG::r0), u(SHIFT::lsl), 0}},
    //
    {&OpcodeTable[u(OPC::sub_imm)], {u(PRED::al), u(REG::r0), u(REG::r5), 2}},
    {&OpcodeTable[u(OPC::bl)], {u(PRED::al), u(REG::lr), -11}},
    {&OpcodeTable[u(OPC::add_regimm)],
     {u(PRED::al), u(REG::r0), u(REG::r4), u(REG::r0), u(SHIFT::lsl), 0}},
    //
    {&OpcodeTable[u(OPC::ldmia_update)], {u(PRED::al), 0x8030, u(REG::sp)}}

};

int main(int argc, char* argv[]) {
  uint32_t* memory =
      (uint32_t*)mmap(nullptr, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  ASSERT(memory != nullptr, "");
  unsigned i = 0;
  for (const auto& ins : Fibonacci) {
    memory[i] = EncodeIns(ins);
    DumpA32Ins(memory[i]);
    ++i;
  }

  FunPtr f = reinterpret_cast<FunPtr>(memory);
  for (unsigned i = 0; i < 10; ++i) {
    std::cout << std::dec << i << " " << f(i) << "\n";
  }
  return 0;
}
