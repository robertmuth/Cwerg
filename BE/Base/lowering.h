#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "BE/Base/ir.h"

namespace cwerg::base {

extern int FunStrengthReduction(Fun fun);

extern int FunMoveElimination(Fun fun, std::vector<Ins>* inss);

extern void FunRegWidthWidening(Fun fun, DK narrow_kind, DK wide_kind,
                                std::vector<Ins>* inss);

extern void FunEliminateStkLoadStoreWithRegOffset(Fun fun, DK base_kind,
                                                  DK offset_kind,
                                                  std::vector<Ins>* inss);

extern void FunEliminateMemLoadStore(Fun fun, DK base_kind, DK offset_kind,
                                     std::vector<Ins>* inss);

extern void FunEliminateRem(Fun fun, std::vector<Ins>* inss);

extern void FunEliminateCopySign(Fun fun, std::vector<Ins>* inss);

extern void FunEliminateCmp(Fun fun, std::vector<Ins>* inss);

extern void FunEliminateCntPop(Fun fun, std::vector<Ins>* inss);

class RegConstCache {
 public:
  RegConstCache(Unit unit, DK addr_kind, DK offset_kind, uint32_t max_size)
      : unit_(unit),
        addr_kind_(addr_kind),
        offset_kind_(offset_kind),
        max_size_(max_size) {}

  void Reset() { cache_.clear(); }

  Reg Materialize(Fun fun, Const c, bool from_mem, std::vector<Ins>* inss);

 private:
  struct Entry {
    Const num;
    Reg reg;
  };

  void insert(Const c, Reg r) {
    if (max_size_ == 0) return;
    cache_.insert(cache_.begin(), {c, r});
    if (cache_.size() > max_size_) cache_.pop_back();
  }
  const Unit unit_;
  const DK addr_kind_;
  const DK offset_kind_;
  const uint32_t max_size_;

  std::vector<Entry> cache_;
};

extern void FunLimtiShiftAmounts(Fun fun, int width, std::vector<Ins>* inss);

struct PushPopInterface {
  virtual void GetCpuRegsForInSignature(
      unsigned count, const base::DK* kinds,
      std::vector<base::CpuReg>* out) const = 0;
  virtual void GetCpuRegsForOutSignature(
      unsigned count, const base::DK* kinds,
      std::vector<base::CpuReg>* out) const = 0;
};

extern void FunPushargConversion(Fun fun, const PushPopInterface& ppif);
extern void FunPopargConversion(Fun fun, const PushPopInterface& ppif);

extern void FunSetInOutCpuRegs(Fun fun, const PushPopInterface& ppif);

}  // namespace cwerg::base
