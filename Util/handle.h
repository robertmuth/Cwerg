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

const int kKindFree = 0xff;
const int kKindInvalid = 0x00;

// Reference mimic 32 bit tagged pointers where the lowest 8 bits are the tag
struct Handle {
  constexpr Handle(uint32_t index, uint8_t kind)
      : value(index << 8 | uint8_t(kind)) {}

  explicit constexpr Handle(int32_t a_value) : value(a_value) {}
  constexpr Handle() : Handle(0, 0) {}

  uint32_t index() const { return value >> 8; }
  uint8_t raw_kind() const { return value & 0xff; }


  bool operator==(const Handle& other) const { return value == other.value; }

  bool operator!=(const Handle& other) const { return value != other.value; }

  bool operator<(const Handle& other) const { return value < other.value; }

  bool isnull() const { return index() == 0; }

  uint32_t value;
};

constexpr const Handle kHandleInvalid(0, kKindInvalid);


}  // namespace cwerg
