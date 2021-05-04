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

extern void FunMoveImmediatesToMemory(Fun fun,
                                      Unit unit,
                                      DK imm_kind,
                                      DK offset_kind,
                                      std::vector<Ins>* inss);

extern void BblReplaceInss(Bbl bbl, const std::vector<Ins>& inss);

extern Ins InsEliminateImmediate(Ins ins, unsigned pos, Fun fun);

}  // namespace cwerg::base
