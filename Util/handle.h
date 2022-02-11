#pragma once
// (c) Robert Muth - see LICENSE for more info

/*
 * The Handle abstraction serves several purposes:
 * * a common base class for the most common abstractions
 * * a 32 bit replacement for pointers which will save storage on 64 bit systems
 * * an enabler for the data structure striping mechanism
 */
#include <cstdint>

namespace cwerg {

enum class RefKind : uint8_t {
  INVALID,
  FREE,  // In Free List
  //
  INS,   // Instruction
  EDG,   // CFG Edge
  BBL,   // Basic block
  FUN,   // Function
  UNIT,  // Compilation Unit
  //
  STR,  // Interned string or Bytes
  CONST,
  REG,   // Register
  STK,   // Stack region
  MEM,   // Global memory region
  DATA,  // Data (section within a MEM)
  JTB,   // Jump table
  JEN,   // Jump entry
  CPU_REG,  // Machine Register
  STACK_SLOT, // StackSlot for Register (only used by x86-64)
};

// Reference mimic 32 bit tagged pointers where the lowest 8 bits are the tag
struct Handle {
  constexpr Handle(uint32_t index, RefKind kind)
      : value(index << 8 | uint8_t(kind)) {}
  constexpr Handle() : Handle(0, RefKind::INVALID) {}

  explicit constexpr Handle(int32_t a_value) : value(a_value) {}

  uint32_t index() const { return value >> 8; }
  RefKind kind() const { return RefKind(value & 0xff); }

  bool operator==(const Handle& other) const { return value == other.value; }

  bool operator!=(const Handle& other) const { return value != other.value; }

  bool operator<(const Handle& other) const { return value < other.value; }

  bool isnull() const { return index() == 0; }

  uint32_t value;
};

extern const char* EnumToString(RefKind x);

}  // namespace cwerg
