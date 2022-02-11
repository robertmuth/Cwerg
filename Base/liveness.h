#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"
#include "Base/opcode_gen.h"

#include <iostream>
#include <vector>

namespace cwerg::base {

// Pre-requisite for liveness + reaching defs
void FunNumberReg(Fun fun);

// Returns the number iterations the fixed point computation took
extern int FunComputeLivenessInfo(Fun fun);

//
extern int FunRemoveUselessInstructions(Fun fun, std::vector<Ins>* to_delete);

// magic number for LiveRange::pos_def
const constexpr int BEFORE_BBL = -32000;
// magic numbers for LiveRange::pos_last_use
const constexpr int AFTER_BBL = 32000;
const constexpr int NO_USE = AFTER_BBL + 1;

enum class LR_FLAG : uint8_t {
  LAC = 1U << 0U,
  PRE_ALLOC = 1U << 1U,
  IGNORE = 1U << 2U,
};

// Note these two are subtly different
const constexpr CpuReg CPU_REG_SPILL(0);
const constexpr CpuReg CPU_REG_INVALID(HandleInvalid);

const constexpr unsigned MAX_USES_PER_OPCODE = 4;

struct LiveRange {
  int16_t def_pos;
  int16_t last_use_pos;
  Reg reg;
  uint16_t num_uses = 0;
  // contains indices of LiveRanges - not 0 is an invalid values
  uint16_t use_def[MAX_USES_PER_OPCODE];
  uint8_t flags = 0;
  CpuReg cpu_reg = CPU_REG_INVALID;
  // filled in by allocator contains one of:
  // CPU_REG_INVALID ???
  // CPU_REG_SPILL reg must be spilled
  // a CpuReg  cpu_reg the liverange is allocated to.

  bool HasFlag(LR_FLAG flag) const { return (flags & uint8_t(flag)) != 0; }

  void SetFlag(LR_FLAG flag) { flags |= uint8_t(flag); }

  bool is_use_lr() const { return reg.isnull(); }

  bool is_cross_bbl() const {
    return last_use_pos == AFTER_BBL || def_pos == BEFORE_BBL;
  }

  bool operator<(const LiveRange& other) const {
    if (def_pos != other.def_pos) {
      return def_pos < other.def_pos;
    }
    if (last_use_pos != other.last_use_pos) {
      return last_use_pos < other.last_use_pos;
    }
    // This can happen for ranges that cover the entire bbl
    return reg.index() < other.reg.index();
  }
};

std::ostream& operator<<(std::ostream& os, const LiveRange& lr);

// expects that RegLastUse(reg) is 0 for all regs
// it may change the value of RegLastUse during computation
// but return it with all 0 again.
// The first entry of the result vector is always a dummy entry
extern std::vector<LiveRange>
BblGetLiveRanges(Bbl bbl, Fun fun, const std::vector<Reg>& live_out);

}  // namespace cwerg::base
