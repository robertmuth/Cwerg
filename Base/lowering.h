#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Base/ir.h"

namespace cwerg::base {

extern int FunStrengthReduction(Fun fun);

extern int FunMoveElimination(Fun fun, std::vector<Ins>* inss);

extern void FunRegWidthWidening(Fun fun,
                                DK narrow_kind,
                                DK wide_kind,
                                std::vector<Ins>* inss);

extern void FunEliminateStkLoadStoreWithRegOffset(Fun fun,
                                                  DK base_kind,
                                                  DK offset_kind,
                                                  std::vector<Ins>* inss);

extern void FunEliminateMemLoadStore(Fun fun,
                                     DK base_kind,
                                     DK offset_kind,
                                     std::vector<Ins>* inss);

extern void FunEliminateRem(Fun fun, std::vector<Ins>* inss);

// add new instructions to inss to replace the immediate at pos with
// a reg, also rewrites ins
// The caller usually will followup with a inss->push_back(ins)
extern void InsEliminateImmediateViaMov(Ins ins,
                                        unsigned pos,
                                        Fun fun,
                                        std::vector<Ins>* inss);

// Same as above but the new instructions will load the immediate from memory
extern void InsEliminateImmediateViaMem(Ins ins,
                                        unsigned pos,
                                        Fun fun,
                                        Unit unit,
                                        DK addr_kind,
                                        DK offset_kind,
                                        std::vector<Ins>* inss);
extern void FunLimtiShiftAmounts(Fun fun, int width, std::vector<Ins>* inss);


struct PushPopInterface {
  virtual void GetCpuRegsForInSignature(
      unsigned count,
      const base::DK* kinds,  std::vector<base::CpuReg>* out) const = 0;
  virtual void GetCpuRegsForOutSignature(
      unsigned count,
      const base::DK* kinds,  std::vector<base::CpuReg>* out) const = 0;
};

extern void FunPushargConversion(Fun fun, const PushPopInterface& ppif);
extern void FunPopargConversion(Fun fun, const PushPopInterface& ppif);

}  // namespace cwerg::base
