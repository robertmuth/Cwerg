// (c) Robert Muth - see LICENSE for more info
#include "Base/lowering.h"
#include "Base/cfg.h"

#include <algorithm>

namespace cwerg::base {
namespace {

bool OPCNopIfSrc2Zero(OPC opc) {
  switch (opc) {
    case OPC::ADD:
    case OPC::SUB:
    case OPC::SHL:
    case OPC::SHR:
    case OPC::OR:
    case OPC::XOR:
    case OPC::LEA:
      // case OPC::ROTL_I:
      return true;
    default:
      return false;
  }
}

bool OPCNopIfSrc1Zero(OPC opc) {
  switch (opc) {
    case OPC::ADD:
    case OPC::OR:
    case OPC::XOR:
      return true;
    default:
      return false;
  }
}

bool OPCNopIfSrc2One(OPC opc) {
  switch (opc) {
    case OPC::MUL:
    case OPC::DIV:
      return true;
    default:
      return false;
  }
}

bool OPCNopIfSrc1One(OPC opc) {
  switch (opc) {
    case OPC::MUL:
      return true;
    default:
      return false;
  }
}

bool InsIsNop1(Ins ins) {
  Handle src2 = InsOperand(ins, 2);
  OPC opc = InsOPC(ins);
  if (src2.kind() != RefKind::CONST) return false;
  return (OPCNopIfSrc2Zero(opc) && ConstIsZero(Const(src2))) ||
         (OPCNopIfSrc2One(opc) && ConstIsOne(Const(src2)));
}

bool InsIsNop2(Ins ins) {
  Const src1 = Const(InsOperand(ins, 1));
  OPC opc = InsOPC(ins);
  if (src1.kind() != RefKind::CONST) return false;
  return (OPCNopIfSrc1Zero(opc) && ConstIsZero(src1)) ||
         (OPCNopIfSrc1One(opc) && ConstIsOne(src1));
}

bool OPCZeroIfOpsSame(OPC opc) {
  switch (opc) {
    case OPC::XOR:
    case OPC::SUB:
      return true;
    default:
      return false;
  }
}

bool OPCZeroIfSrc1Zero(OPC opc) {
  switch (opc) {
    case OPC::SHL:
    case OPC::SHR:
    case OPC::MUL:
      return true;
    default:
      return false;
  }
}

bool OPCZeroIfSrc2Zero(OPC opc) {
  switch (opc) {
    case OPC::MUL:
      return true;
    default:
      return false;
  }
}

Const ConstTryApplyingBinaryLog(Const num) {
  if (DKFlavor(ConstKind(num)) == DK_FLAVOR_S) {
    int64_t v = ConstValueACS(num);
    if (v < 0) return Const(HandleInvalid);
    if ((v & (v - 1)) != 0) return Const(HandleInvalid);
    for (unsigned i = 0; i < 64; ++i) {
      if (v == (1U << i)) {
        return ConstNewACS(ConstKind(num), i);
      }
    }
    ASSERT(false, "");
  } else if (DKFlavor(ConstKind(num)) == DK_FLAVOR_U) {
    uint64_t v = ConstValueU(num);
    if ((v & (v - 1)) != 0) return Const(HandleInvalid);
    for (unsigned i = 0; i < 64; ++i) {
      if (v == (1U << i)) {
        return ConstNewU(ConstKind(num), i);
      }
    }
  }
  return Const(HandleInvalid);
}

bool InsIsZero(Ins ins) {
  OPC opc = InsOPC(ins);
  Const src1 = Const(InsOperand(ins, 1));
  Const src2 = Const(InsOperand(ins, 2));
  return (OPCZeroIfOpsSame(opc) && src1 == src2) ||
         (OPCZeroIfSrc1Zero(opc) && src1.kind() == RefKind::CONST &&
          ConstIsZero(src1)) ||
         (OPCZeroIfSrc2Zero(opc) && src2.kind() == RefKind::CONST &&
          ConstIsZero(src2));
}

bool InsStrengthReduction(Ins ins) {
  if (InsIsNop1(ins)) {
    InsOPC(ins) = OPC::MOV;
    InsOperand(ins, 2) = HandleInvalid;
    return true;
  } else if (InsIsNop2(ins)) {
    InsOPC(ins) = OPC::MOV;
    InsOperand(ins, 1) = InsOperand(ins, 2);
    InsOperand(ins, 2) = HandleInvalid;
    return true;
  } else if (InsIsZero(ins)) {
    InsOPC(ins) = OPC::MOV;
    DK kind = RegKind(Reg(InsOperand(ins, 0)));
    InsOperand(ins, 1) = ConstNew(kind, {"0"});
    InsOperand(ins, 2) = HandleInvalid;
    return true;
  } else if (InsOPC(ins) == OPC::MUL) {
    // MUL -> SHIFT
    const Const num1 = Const(InsOperand(ins, 1));
    if (num1.kind() == RefKind::CONST) {
      const Const bin_log = ConstTryApplyingBinaryLog(num1);
      if (!bin_log.isnull()) {
        InsOPC(ins) = OPC::SHL;
        InsOperand(ins, 1) = InsOperand(ins, 2);
        InsOperand(ins, 2) = bin_log;
        return true;
      }
    }

    const Const num2 = Const(InsOperand(ins, 2));
    if (num2.kind() == RefKind::CONST) {
      const Const bin_log = ConstTryApplyingBinaryLog(num2);
      if (!bin_log.isnull()) {
        InsOPC(ins) = OPC::SHL;
        InsOperand(ins, 2) = bin_log;
        return true;
      }
    }
  }
  return false;
}

}  // namespace

int FunStrengthReduction(Fun fun) {
  int count = 0;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      OPC_KIND of = InsOpcodeKind(ins);
      if (of != OPC_KIND::LEA && of != OPC_KIND::ALU) continue;
      if (InsStrengthReduction(ins)) count += 1;
    }
  }
  return count;
}

int FunMoveElimination(Fun fun, std::vector<Ins>* to_delete) {
  to_delete->clear();
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      OPC opc = InsOPC(ins);
      if ((opc == OPC::MOV || opc == OPC::CONV) &&
          InsOperand(ins, 0) == InsOperand(ins, 1)) {
        to_delete->push_back(ins);
      }
    }
  }

  for (Ins ins : *to_delete) {
    BblInsUnlink(ins);
    InsDel(ins);
  }
  return to_delete->size();
}

// This is tricky and probably quite buggy at this point.
void FunRegWidthWidening(Fun fun,
                         DK narrow_kind,
                         DK wide_kind,
                         std::vector<Ins>* inss) {
  ASSERT(DKFlavor(narrow_kind) == DKFlavor(wide_kind),
         "flavor mismatch " << EnumToString(narrow_kind) << " "
                            << EnumToString(wide_kind));
  ASSERT(DKBitWidth(wide_kind) > DKBitWidth(narrow_kind), "");
  for (unsigned i = 0; i < FunNumInputTypes(fun); ++i) {
    if (FunInputTypes(fun)[i] == narrow_kind) FunInputTypes(fun)[i] = wide_kind;
  }
  for (unsigned i = 0; i < FunNumOutputTypes(fun); ++i) {
    if (FunOutputTypes(fun)[i] == narrow_kind)
      FunOutputTypes(fun)[i] = wide_kind;
  }

  for (Reg reg : FunRegIter(fun)) {
    RegFlags(reg) &= ~uint8_t(REG_FLAG::MARKED);
  }

  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      const unsigned num_ops = InsOpcode(ins).num_operands;
      const OPC_KIND kind = InsOpcodeKind(ins);
      bool change = false;
      for (int i = 0; i < num_ops; ++i) {
        Handle op = InsOperand(ins, i);
        switch (op.kind()) {
          default:  // we only care about REG and CONST operands
            break;
          case RefKind::REG:
            if (RegKind(Reg(op)) == narrow_kind) change = true;
            break;
          case RefKind::CONST: {
            const Const val = Const(op);
            if (ConstKind(val) == narrow_kind) {
              if (i == 2 && kind == OPC_KIND::ST) continue;
              change = true;
              if (DKFlavor(ConstKind(val)) == DK_FLAVOR_U) {
                InsOperand(ins, i) = ConstNewU(wide_kind, ConstValueU(val));
              } else {
                ASSERT(DKFlavor(ConstKind(val)) == DK_FLAVOR_S, "");
                InsOperand(ins, i) = ConstNewACS(wide_kind, ConstValueACS(val));
              }
            }
            break;
          }
        }
      }

      if (!change) {
        inss->push_back(ins);
        continue;
      }

      if (InsOPC(ins) == OPC::SHL || InsOPC(ins) == OPC::SHR) {
        Reg tmp_reg = FunGetScratchReg(fun, wide_kind, "tricky", false);
        Const mask;
        if (DKFlavor(wide_kind) == DK_FLAVOR_U) {
          mask = ConstNewU(wide_kind, DKBitWidth(narrow_kind) - 1);
        } else {
          ASSERT(DKFlavor(wide_kind) == DK_FLAVOR_S, "");
          mask = ConstNewACS(wide_kind, DKBitWidth(narrow_kind) - 1);
        }
        Ins and_ins = InsNew(OPC::AND, tmp_reg, InsOperand(ins, 2), mask);
        inss->push_back(and_ins);
        InsOperand(ins, 2) = tmp_reg;
        if (InsOPC(ins) == OPC::SHR &&
            InsOperand(ins, 1).kind() == RefKind::REG) {
          Reg tmp_reg = FunGetScratchReg(fun, narrow_kind, "narrowed", true);
          RegFlags(tmp_reg) |= uint8_t(REG_FLAG::MARKED);  // do not widen
          inss->push_back(InsNew(OPC::CONV, tmp_reg, InsOperand(ins, 1)));
          inss->push_back(InsNew(OPC::CONV, InsOperand(ins, 1), tmp_reg));
        }
        inss->push_back(ins);
        dirty = true;
      } else if (InsOPC(ins) == OPC::CNTLZ) {
        inss->push_back(ins);
        Const excess = ConstNewACS(
            wide_kind, DKBitWidth(wide_kind) - DKBitWidth(narrow_kind));
        inss->push_back(
            InsNew(OPC::SUB, InsOperand(ins, 0), InsOperand(ins, 0), excess));
        dirty = true;
      } else if (InsOPC(ins) == OPC::CNTTZ) {
        inss->push_back(ins);
        Const max = ConstNewACS(wide_kind, DKBitWidth(narrow_kind));
        inss->push_back(InsNew(OPC::CMPLT, InsOperand(ins, 0),
                               InsOperand(ins, 0), max, InsOperand(ins, 0),
                               max));
        dirty = true;
      } else if (kind == OPC_KIND::LD) {
        inss->push_back(ins);
        const Reg reg = Reg(InsOperand(ins, 0));
        if (RegKind(reg) == narrow_kind) {
          Reg tmp_reg = FunGetScratchReg(fun, narrow_kind, "narrowed", true);
          RegFlags(tmp_reg) |= uint8_t(REG_FLAG::MARKED);  // do not widen
          Ins conv = InsNew(OPC::CONV, reg, tmp_reg);
          InsOperand(ins, 0) = tmp_reg;
          inss->push_back(conv);
          dirty = true;
        }
      } else if (kind == OPC_KIND::ST) {
        const Reg reg = Reg(InsOperand(ins, 2));
        if (reg.kind() == RefKind::REG && RegKind(reg) == narrow_kind) {
          Reg tmp_reg = FunGetScratchReg(fun, narrow_kind, "narrowed", true);
          RegFlags(tmp_reg) |= uint8_t(REG_FLAG::MARKED);  // do not widen
          Ins conv = InsNew(OPC::CONV, tmp_reg, reg);
          inss->push_back(conv);
          dirty = true;
          InsOperand(ins, 2) = tmp_reg;
        }
        inss->push_back(ins);
      } else if (InsOPC(ins) == OPC::CONV) {
        Reg tmp_reg = FunGetScratchReg(fun, narrow_kind, "narrowed", true);
        RegFlags(tmp_reg) |= uint8_t(REG_FLAG::MARKED);  // do not widen
        inss->push_back(InsNew(OPC::CONV, tmp_reg, InsOperand(ins, 1)));
        inss->push_back(InsNew(OPC::CONV, InsOperand(ins, 0), tmp_reg));
        dirty = true;
      } else {
        inss->push_back(ins);
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }

  for (Reg reg : FunRegIter(fun)) {
    if (RegKind(reg) == narrow_kind && !RegHasFlag(reg, REG_FLAG::MARKED)) {
      RegKind(reg) = wide_kind;
    }
  }
}

void FunEliminateStkLoadStoreWithRegOffset(Fun fun,
                                           DK base_kind,
                                           DK offset_kind,
                                           std::vector<Ins>* inss) {
  auto add_lea_stk = [&](Handle stk) -> Reg {
    Reg tmp = FunGetScratchReg(fun, base_kind, "base", false);
    inss->push_back(InsNew(OPC::LEA_STK, tmp, stk, ConstNewU(offset_kind, 0)));
    return tmp;
  };

  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      const OPC opc = InsOPC(ins);
      if (opc == OPC::ST_STK && InsOperand(ins, 1).kind() == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_stk(InsOperand(ins, 0));
        inss->push_back(
            InsInit(ins, OPC::ST, tmp, InsOperand(ins, 1), InsOperand(ins, 2)));
      } else if (opc == OPC::LD_STK &&
                 InsOperand(ins, 2).kind() == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_stk(InsOperand(ins, 1));
        inss->push_back(
            InsInit(ins, OPC::LD, InsOperand(ins, 0), tmp, InsOperand(ins, 2)));
      } else if (opc == OPC::LEA_STK &&
                 InsOperand(ins, 2).kind() == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_stk(InsOperand(ins, 1));
        inss->push_back(InsInit(ins, OPC::LEA, InsOperand(ins, 0), tmp,
                                InsOperand(ins, 2)));
      } else {
        inss->push_back(ins);
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

void FunEliminateMemLoadStore(Fun fun,
                              DK base_kind,
                              DK offset_kind,
                              std::vector<Ins>* inss) {
  auto add_lea_mem = [&](Handle mem, Handle offset) -> Reg {
    Reg tmp = FunGetScratchReg(fun, base_kind, "base", false);
    inss->push_back(InsNew(OPC::LEA_MEM, tmp, mem, offset));
    return tmp;
  };

  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      const OPC opc = InsOPC(ins);
      if (opc == OPC::ST_MEM) {
        Handle st_offset = InsOperand(ins, 1);
        Handle lea_offset = ConstNewU(offset_kind, 0);
        // TODO: small st_offset/ld_offset should probably stay with the `st`
        if (st_offset.kind() == RefKind::CONST)
          std::swap(st_offset, lea_offset);
        Reg tmp = add_lea_mem(InsOperand(ins, 0), lea_offset);
        inss->push_back(
            InsInit(ins, OPC::ST, tmp, st_offset, InsOperand(ins, 2)));
        dirty = true;
      } else if (opc == OPC::LD_MEM) {
        Handle ld_offset = InsOperand(ins, 2);
        Handle lea_offset = ConstNewU(offset_kind, 0);
        if (ld_offset.kind() == RefKind::CONST)
          std::swap(ld_offset, lea_offset);
        Reg tmp = add_lea_mem(InsOperand(ins, 1), lea_offset);
        inss->push_back(
            InsInit(ins, OPC::LD, InsOperand(ins, 0), tmp, ld_offset));
        dirty = true;
      } else if (opc == OPC::LEA_MEM &&
                 InsOperand(ins, 2).kind() == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_mem(InsOperand(ins, 1), ConstNewU(offset_kind, 0));
        inss->push_back(InsInit(ins, OPC::LEA, InsOperand(ins, 0), tmp,
                                InsOperand(ins, 2)));
      } else {
        inss->push_back(ins);
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

void FunEliminateRem(Fun fun, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::REM) {
        DK kind = RegKind(Reg(InsOperand(ins, 0)));
        Reg tmp1 = FunGetScratchReg(fun, kind, "elim_rem1", true);

        inss->push_back(
            InsNew(OPC::DIV, tmp1, InsOperand(ins, 1), InsOperand(ins, 2)));
        if (DKFlavor(kind) == DK_FLAVOR_F) {
          ASSERT(false, "");
          //          Reg tmp3 = FunGetScratchReg(fun, kind, "elim_rem3",
          //          true); inss.push_back(InsNew(OPC::TRUNC, tmp3, tmp1));
          //          tmp1 = tmp3
        }
        Reg tmp2 = FunGetScratchReg(fun, kind, "elim_rem2", true);
        inss->push_back(InsNew(OPC::MUL, tmp2, tmp1, InsOperand(ins, 2)));
        inss->push_back(
            InsNew(OPC::SUB, InsOperand(ins, 0), InsOperand(ins, 1), tmp2));
        dirty = true;

      } else {
        inss->push_back(ins);
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

void InsEliminateImmediateViaMov(Ins ins,
                                 unsigned pos,
                                 Fun fun,
                                 std::vector<Ins>* inss) {
  Const num = Const(InsOperand(ins, pos));
  ASSERT(num.kind() == RefKind::CONST, "");
  Reg tmp = FunGetScratchReg(fun, ConstKind(num), "imm", true);
  InsOperand(ins, pos) = tmp;
  inss->push_back(InsNew(OPC::MOV, tmp, num));
}

void InsEliminateImmediateViaMem(Ins ins,
                                 unsigned pos,
                                 Fun fun,
                                 Unit unit,
                                 DK addr_kind,
                                 DK offset_kind,
                                 std::vector<Ins>* inss) {
  Const num = Const(InsOperand(ins, pos));
  ASSERT(num.kind() == RefKind::CONST, "");
  Mem mem = UnitFindOrAddConstMem(unit, num);
  Reg tmp_addr = FunGetScratchReg(fun, addr_kind, "mem_const_addr", true);
  inss->push_back(
      InsNew(OPC::LEA_MEM, tmp_addr, mem, ConstNewU(offset_kind, 0)));
  Reg tmp = FunGetScratchReg(fun, ConstKind(num), "mem_const", true);
  inss->push_back(InsNew(OPC::LD, tmp, tmp_addr, ConstNewU(offset_kind, 0)));
  InsOperand(ins, pos) = tmp;
}

bool InsLimtiShiftAmounts(Ins ins, Fun fun, int width, std::vector<Ins>* inss) {
  const DK dk = RegKind(Reg(InsOperand(ins, 0)));
  Handle amount = InsOperand(ins, 2);
  if (amount.kind() == RefKind::CONST) {
    inss->push_back(ins);
    if (DKFlavor(dk) == DK_FLAVOR_U) {
      uint64_t a = ConstValueU(Const(amount));
      if (0 <= a && a < width) {
        InsOperand(ins, 2) = ConstNewU(dk, a & (width - 1));
      }
    } else {
      int64_t a = ConstValueACS(Const(amount));
      if (0 <= a && a < width) {
        InsOperand(ins, 2) = ConstNewACS(dk, a & (width - 1));
      }
    }
    return false;
  } else {
    // reg
    Const mask = DKFlavor(dk) == DK_FLAVOR_U ? ConstNewU(dk, width - 1)
                                             : ConstNewACS(dk, width - 1);
    Reg tmp = FunGetScratchReg(fun, dk, "shift", false);
    inss->push_back(InsNew(OPC::AND, tmp, amount, mask));
    InsInit(ins, InsOPC(ins), InsOperand(ins, 0), InsOperand(ins, 1), tmp);
    inss->push_back(ins);
    return true;
  }
}

void FunLimtiShiftAmounts(Fun fun, int width, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      const OPC opc = InsOPC(ins);
      if ((opc != OPC::SHL && opc != OPC::SHR) ||
          width != DKBitWidth(RegKind(Reg(InsOperand(ins, 0))))) {
        inss->push_back(ins);
        continue;
      }
      if (InsLimtiShiftAmounts(ins, fun, width, inss)) dirty = true;
    }
    if (dirty) {
      BblReplaceInss(bbl, *inss);
    }
  }
}

void FunPushargConversion(Fun fun, const PushPopInterface& ppif) {
  std::vector<CpuReg> parameter;
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIterReverse(bbl)) {
      if (InsOPC(ins) == OPC::PUSHARG) {
        ASSERT(!parameter.empty(),
               "possible undefined fun call in " << Name(fun));
        Handle src = InsOperand(ins, 0);
        CpuReg cpu_reg = parameter.back();
        parameter.pop_back();
        Reg reg = FunFindOrAddCpuReg(fun, cpu_reg, RegOrConstKind(src));
        InsInit(ins, OPC::MOV, reg, src);
        continue;
      }

      if (InsOpcode(ins).IsCall()) {
        Fun callee = InsCallee(ins);
        ppif.GetCpuRegsForInSignature(FunNumInputTypes(callee),
                                      FunInputTypes(callee), &parameter);
        std::reverse(parameter.begin(), parameter.end());
      } else if (InsOPC(ins) == OPC::RET) {
        ppif.GetCpuRegsForOutSignature(FunNumOutputTypes(fun),
                                       FunOutputTypes(fun), &parameter);
        std::reverse(parameter.begin(), parameter.end());
      }
    }
  }
}

void FunPopargConversion(Fun fun, const PushPopInterface& ppif) {
  std::vector<CpuReg> parameter;
  ppif.GetCpuRegsForInSignature(FunNumInputTypes(fun), FunInputTypes(fun),
                                &parameter);
  std::reverse(parameter.begin(), parameter.end());
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::POPARG) {
        ASSERT(!parameter.empty(), "");
        Reg dst = Reg(InsOperand(ins, 0));
        CpuReg cpu_reg = parameter.back();
        parameter.pop_back();
        Reg reg = FunFindOrAddCpuReg(fun, cpu_reg, RegKind(dst));
        InsInit(ins, OPC::MOV, dst, reg);
        continue;
      }

      if (InsOpcode(ins).IsCall()) {
        Fun callee = InsCallee(ins);
        ppif.GetCpuRegsForOutSignature(FunNumOutputTypes(callee),
                                       FunOutputTypes(callee), &parameter);
        std::reverse(parameter.begin(), parameter.end());
      }
    }
  }
}

}  // namespace cwerg::base
