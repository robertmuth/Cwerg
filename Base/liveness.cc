// (c) Robert Muth - see LICENSE for more info

#include "Base/liveness.h"
#include "Base/cfg.h"
#include "Base/ir.h"
#include "Base/serialize.h"

#include <algorithm>
#include <iomanip>
#include <set>

namespace cwerg::base {
namespace {

#if 0
void DumpLiveness(BitVec bv, Fun fun, std::ostream* output) {
  const unsigned num_regs = FunNumRegs(fun);
  const HandleVec reg_names = FunRegNames(fun);
  for (unsigned i = 0; i < num_regs; ++i) {
    if (!bv.BitGet(i)) continue;
    *output << " " <<  Str(reg_names.Get(i));
  }
}
#endif

int FunLivenessFixpoint(Fun fun, BitVec live, BitVec old) {
  // Note we look at the last bbl first
  int count = 0;
  std::set<Bbl> active_set;
  std::vector<Bbl> active_stk;
  for (Bbl bbl : FunBblIter(fun)) {
    active_stk.push_back(bbl);
    active_set.insert(bbl);
  }

  while (!active_stk.empty()) {
    ++count;
    const Bbl bbl = active_stk.back();
    active_stk.pop_back();
    active_set.erase(bbl);
#if 0
    std::cout << "fixpoint BBL " << Name(bbl) << " out: ";
    DumpLiveness(BblLiveOut(bbl), fun, &std::cout);
    std::cout << "\n";
#endif
    live.CopyFrom(BblLiveOut(bbl));
    live.AndNotWith(BblLiveDef(bbl));
    live.OrWith(BblLiveUse(bbl));
    if (live.Equal(BblLiveIn(bbl))) continue;
    /*
    std::cout << Name(bbl) << ": ";
    RenderRegBitVec(fun, BblLiveOut(bbl), &std::cout);
    std::cout <<  " -> ";
    RenderRegBitVec(fun, live, &std::cout);
    std::cout <<  "\n";
  */
    for (Edg edg : BblPredEdgIter(bbl)) {
      Bbl pred = EdgPredBbl(edg);
      old.CopyFrom(BblLiveOut(pred));
      BblLiveOut(pred).OrWith(live);
      if (old.Equal(BblLiveOut(pred))) continue;
      // NOTE: would it be better to go DFS and move the succ up the stack?
      if (active_set.find(pred) == active_set.end()) active_stk.push_back(pred);
    }
  }
  return count;
}

void InsUpdateDefUse(Ins ins,
                     BitVec defs,
                     BitVec uses,
                     unsigned num_regs,
                     const Reg reg_map[]) {
  if (InsOpcode(ins).IsCall()) {
    Fun callee = InsCallee(ins);
    for (unsigned j = 0; j < FunNumCpuLiveOut(callee); ++j) {
      const CpuReg cpu_reg = FunCpuLiveOut(callee)[j];
      // terminate live ranges for callee result regs
      for (unsigned i = 0; i < num_regs; ++i) {
        const Reg reg = reg_map[i];
        if (RegCpuReg(reg) == cpu_reg) {
          defs.BitSet(RegNo(reg));
          uses.BitClear(RegNo(reg));
        }
      }
    }
  }

  // for function calls deal with clobbering machine regs
  const unsigned num_ops = InsOpcode(ins).num_operands;
  const unsigned num_defs = InsOpcode(ins).num_defs;
  for (unsigned i = 0; i < num_defs; ++i) {
    Reg reg = Reg(InsOperand(ins, i));
    defs.BitSet(RegNo(reg));
    uses.BitClear(RegNo(reg));
  }
  for (unsigned i = num_defs; i < num_ops; ++i) {
    const Reg reg = Reg(InsOperand(ins, i));
    if (reg.kind() != RefKind::REG) continue;
    uses.BitSet(RegNo(reg));
  }
}

}  // namespace

bool InsWritesRegInList(Ins ins, BitVec regs) {
  const unsigned num_defs = InsOpcode(ins).num_defs;
  for (unsigned i = 0; i < num_defs; ++i) {
    Reg reg = Reg(InsOperand(ins, i));
    if (regs.BitGet(RegNo(reg))) return true;
  }
  return false;
}

void InsUpdateLiveness(Ins ins,
                       unsigned num_regs,
                       const Reg reg_map[],
                       BitVec live) {
  if (InsOpcode(ins).IsCall()) {
    Fun callee = InsCallee(ins);
    for (unsigned j = 0; j < FunNumCpuLiveOut(callee); ++j) {
      const CpuReg cpu_reg = FunCpuLiveOut(callee)[j];
      // terminate live ranges for callee result regs
      for (unsigned i = 0; i < num_regs; ++i) {
        const Reg reg = reg_map[i];
        if (RegCpuReg(reg) == cpu_reg) {
          live.BitClear(RegNo(reg));
        }
      }
    }
  }
  // TODO: this needs to take FunCpuLiveIn into account
  // for function calls deal with clobbering machine regs
  const unsigned num_defs = InsOpcode(ins).num_defs;
  const unsigned num_ops = InsOpcode(ins).num_operands;
  for (unsigned i = 0; i < num_defs; ++i) {
    const Reg reg = Reg(InsOperand(ins, i));
    live.BitClear(RegNo(reg));
  }
  for (unsigned i = num_defs; i < num_ops; ++i) {
    const Reg reg = Reg(InsOperand(ins, i));
    if (reg.kind() != RefKind::REG) continue;
    live.BitSet(RegNo(reg));
  }
}

int FunRemoveUselessInstructions(Fun fun, std::vector<Ins>* to_delete) {
  to_delete->clear();
  const uint16_t num_regs = FunNumRegs(fun);
  const Reg* const reg_map = (Reg*)FunRegMap(fun).BackingStorage();
  BitVec live = BitVec::New(num_regs);
  std::vector<Ins> useless;

  for (Bbl bbl : FunBblIter(fun)) {
    live.CopyFrom(BblLiveOut(bbl));
    for (Ins ins : BblInsIterReverse(bbl)) {
      // InsRenderToAsm(ins, &std::cout);
      // std::cout << "\n";
      if (!InsOpcode(ins).HasSideEffect() && !InsWritesRegInList(ins, live)) {
        to_delete->push_back(ins);
        continue;
      }
      InsUpdateLiveness(ins, num_regs, reg_map, live);
    }
  }
  for (Ins ins : *to_delete) {
    BblInsUnlink(ins);
    InsDel(ins);
  }
  BitVec::Del(live);
  return to_delete->size();
}

void FunNumberReg(Fun fun) {
  unsigned num_regs = 1;  // do not use zero
  for (Reg reg : FunRegIter(fun)) {
    RegNo(reg) = num_regs++;
  }
  FunNumRegs(fun) = num_regs;
  HandleVec::Del(FunRegMap(fun));
  FunRegMap(fun) = HandleVec::New(num_regs);

  num_regs = 1;
  for (Reg reg : FunRegIter(fun)) {
    FunRegMap(fun).Set(num_regs++, reg);
  }
}

// Returns the number iterations the fixed point computation took
// (Re)Initializes the following fields:
// * RegLiveness
// * FunLiveXXX
// * BblLiveXXX
int FunComputeLivenessInfo(Fun fun) {
  const unsigned num_regs = FunNumRegs(fun);
  const Reg* const reg_map = (Reg*)FunRegMap(fun).BackingStorage();
#if 0
  BitVec::Realloc(&FunLiveOut(fun), num_regs);
#endif

  // Mimic what we do for allocation
  for (Bbl bbl : FunBblIter(fun)) {
    BitVec::Del(BblLiveOut(bbl));
  }
  for (Bbl bbl : FunBblIter(fun)) {
    BitVec::Del(BblLiveIn(bbl));
    BitVec::Del(BblLiveUse(bbl));
    BitVec::Del(BblLiveDef(bbl));
  }

  // We want all the BblLiveOuts to be adjacent
  for (Bbl bbl : FunBblIter(fun)) {
    BblLiveOut(bbl) = BitVec::New(num_regs);
  }
  for (Bbl bbl : FunBblIter(fun)) {
    BblLiveIn(bbl) = BitVec::New(num_regs);
    BblLiveUse(bbl) = BitVec::New(num_regs);
    BblLiveDef(bbl) = BitVec::New(num_regs);
  }

  for (Bbl bbl : FunBblIter(fun)) {
    // std::cout  << "BBL " << Name(bbl) << "\n";
    for (Ins ins : BblInsIterReverse(bbl)) {
      InsUpdateDefUse(ins, BblLiveDef(bbl), BblLiveUse(bbl), num_regs, reg_map);
    }
/*
    std::cout  << "BBL " << Name(bbl) << "  use";
    RenderRegBitVec(fun, BblLiveUse(bbl), &std::cout);
    std::cout  << "  def";
    RenderRegBitVec(fun, BblLiveDef(bbl), &std::cout);
    std::cout  << "\n";
*/
#if 0
    std::cout << "def:";
    DumpLiveness(BblLiveDef(bbl), fun, &std::cout);
    std::cout << "\n";

    std::cout << "use:";
    DumpLiveness(BblLiveUse(bbl), fun, &std::cout);
    std::cout << "\n";
#endif
#if 0
    Ins tail = BblInsList::Tail(bbl);
    if (!tail.isnull() && InsOpcodeKind(tail) == OF::RET) {
      // This is only relevant once we have CPU regs
      // otherwise the push instructions will take care of this
       BblLiveOut(bbl).CopyFrom(FunLiveOut(fun));
    }
#endif
  }

  BitVec use = BitVec::New(num_regs);
  BitVec def = BitVec::New(num_regs);
  int count = FunLivenessFixpoint(fun, use, def);
  BitVec::Del(use);
  BitVec::Del(def);
  return count;
}

bool ListContainsCpuReg(const CpuReg* list, unsigned num_regs, CpuReg cpu_reg) {
  for (unsigned i = 0; i < num_regs; ++i) {
    if (list[i] == cpu_reg) return true;
  }
  return false;
}

std::vector<LiveRange> BblGetLiveRanges(Bbl bbl,
                                        Fun fun,
                                        const std::vector<Reg>& live_out,
                                        bool emit_use_def) {
  unsigned bbl_size = 0;
  for (Ins ins : BblInsIter(bbl)) {
    std::ignore = ins;
    ++bbl_size;
  }

  int16_t last_call_pos = -1;
  const CpuReg* last_call_cpu_live_in = nullptr;
  unsigned last_call_num_cpu_live_in = 0;

  std::vector<LiveRange> out;
  // Add dummy entry at index 0 - so we can treat this as invalid
  out.emplace_back(LiveRange{BEFORE_BBL, BEFORE_BBL, Reg(0), 0, {0, 0, 0, 0}});

  auto initialize_lr = [&](int16_t pos, Reg reg) -> uint16_t {
    uint16_t lr_index = out.size();
    RegLastUse(reg) = lr_index;
    out.emplace_back(LiveRange{-1, pos, reg, 1, {0, 0, 0, 0}});
    return lr_index;
  };

  auto finalize_lr = [&](int16_t lr_no, int16_t def_pos) {
    LiveRange& lr = out[lr_no];
    // BblRenderToAsm(bbl, fun, &std::cout);
    ASSERT(lr.def_pos == -1, "in " << Name(fun) << "unexpected def_pos " << lr);
    lr.def_pos = def_pos;
    if (last_call_pos != -1 && last_call_pos != AFTER_BBL &&
        last_call_pos < lr.last_use_pos) {
      lr.SetFlag(LR_FLAG::LAC);
    }
    RegLastUse(lr.reg) = 0;  // invalid
  };

  for (Reg reg : live_out) {
    initialize_lr(AFTER_BBL, reg);
  }

  int16_t pos = bbl_size;
  for (Ins ins : BblInsIterReverse(bbl)) {
    --pos;
    if (InsOPC(ins) == OPC::RET) {
      if (FunNumCpuLiveOut(fun) > 0) {
        last_call_num_cpu_live_in = FunNumCpuLiveOut(fun);
        last_call_cpu_live_in = FunCpuLiveOut(fun);
        last_call_pos = AFTER_BBL;
      }
    } else if (InsOpcode(ins).IsCall()) {
      Fun callee = InsCallee(ins);
      // This complication only applies after we have (partial) reg allocation
      if (FunNumCpuLiveOut(callee) > 0) {
        // terminate live ranges for callee result regs
        for (unsigned i = 0; i < out.size(); ++i) {
          if (out[i].def_pos == -1) {
            const CpuReg cpu_reg(RegCpuReg(out[i].reg));
            if (cpu_reg.kind() != RefKind::CPU_REG) continue;
            if (ListContainsCpuReg(FunCpuLiveOut(callee),
                                   FunNumCpuLiveOut(callee), cpu_reg)) {
              finalize_lr(i, pos);
            }
          }
        }
      }
      last_call_pos = pos;
      last_call_cpu_live_in = FunCpuLiveIn(callee);
      last_call_num_cpu_live_in = FunNumCpuLiveIn(callee);
    }
    const unsigned num_defs = InsOpcode(ins).num_defs;
    const unsigned num_ops = InsOpcode(ins).num_operands;
    // process definitions
    for (unsigned i = 0; i < num_defs; ++i) {
      const Reg reg(InsOperand(ins, i));
       const CpuReg cpu_reg(RegCpuReg(reg));
      // skip spilled regs
      if (cpu_reg.kind() == RefKind::STACK_SLOT) continue;
      if (i == 0 && RegHasFlag(reg, REG_FLAG::TWO_ADDRESS) && reg == InsOperand(ins, 1)) continue;
      if (RegLastUse(reg) != 0) {
        finalize_lr(RegLastUse(reg), pos);
      } else {
        int16_t last_use_pos = NO_USE;
        if (cpu_reg.kind() == RefKind::CPU_REG &&
            ListContainsCpuReg(last_call_cpu_live_in, last_call_num_cpu_live_in,
                               cpu_reg)) {
          last_use_pos = last_call_pos;
        }
        out.emplace_back(LiveRange{pos, last_use_pos, reg, 0, {0, 0, 0, 0}});
      }
    }

    // process uses
    uint16_t ud[4] = {0, 0, 0, 0}; // use-def links
    unsigned num_ud = 0;
    for (unsigned i = num_defs; i < num_ops; ++i) {
      const Reg reg = Reg(InsOperand(ins, i));
      if (reg.kind() != RefKind::REG) continue;
      const CpuReg cpu_reg(RegCpuReg(reg));
      // skip spilled regs
      if (cpu_reg.kind() == RefKind::STACK_SLOT) continue;
      uint16_t lr_index = RegLastUse(reg);
      if (lr_index == 0) {
        // this is the end of a live range
        lr_index = initialize_lr(pos, reg);
      } else {
        ++out[lr_index].num_uses;
      }
      // record uses but avoid dups
      unsigned pos;
      for (pos = 0; pos < num_ud; ++pos) {
        if (ud[pos] == lr_index) break;
      }
      if (pos == num_ud) {
        ud[num_ud] = lr_index;
        ++num_ud;
      }
    }
    if (emit_use_def && num_ud > 0) {
      out.emplace_back(
          LiveRange{pos, pos, Reg(0), 0, {ud[0], ud[1], ud[2], ud[3]}});
    }
  }

  for (unsigned i = 0; i < out.size(); ++i) {
    if (out[i].def_pos == -1) {
      finalize_lr(i, BEFORE_BBL);
      RegLastUse(out[i].reg) = 0;
    }
  }
  return out;
}

std::ostream& operator<<(std::ostream& os, const LiveRange& lr) {
  auto render_pos = [&os](int16_t pos) {
    if (pos == BEFORE_BBL)
      os << "BB";
    else if (pos == AFTER_BBL)
      os << "AB";
    else if (pos == NO_USE)
      os << "NU";
    else
      os << std::setw(2) << pos;
  };
  os << "LR ";
  render_pos(lr.def_pos);
  os << " - ";
  render_pos(lr.last_use_pos);

  if (lr.HasFlag(LR_FLAG::PRE_ALLOC)) os << " PRE_ALLOC";
  if (lr.HasFlag(LR_FLAG::LAC)) os << " LAC";
  if (lr.HasFlag(LR_FLAG::IGNORE)) os << " IGNORE";
  if (lr.is_use_lr()) {
    unsigned int n = 0;
    for (unsigned i = 0; i < MAX_USES_PER_OPCODE; ++i) {
      if (lr.use_def[i] != 0) ++n;
    }
    std::cout << " uses:" << n;

  } else {
    if (lr.cpu_reg == CPU_REG_SPILL) std::cout << " SPILLED";
    os << " def:" << Name(lr.reg) << ":" << EnumToString(RegKind(lr.reg));
    if (!lr.cpu_reg.isnull()) {
      os << "@" << Name(lr.cpu_reg);
    }
  }
  return os;
}

}  // namespace cwerg::base
