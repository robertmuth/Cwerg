// (c) Robert Muth - see LICENSE for more info
#include "BE/Base/lowering.h"

#include <algorithm>

#include "BE/Base/cfg.h"
#include "BE/Base/eval.h"
#include "BE/Base/ir.h"

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
  if (Kind(src2) != RefKind::CONST) return false;
  return (OPCNopIfSrc2Zero(opc) && ConstIsZero(Const(src2))) ||
         (OPCNopIfSrc2One(opc) && ConstIsOne(Const(src2)));
}

bool InsIsNop2(Ins ins) {
  Const src1 = Const(InsOperand(ins, 1));
  OPC opc = InsOPC(ins);
  if (Kind(src1) != RefKind::CONST) return false;
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
         (OPCZeroIfSrc1Zero(opc) && Kind(src1) == RefKind::CONST &&
          ConstIsZero(src1)) ||
         (OPCZeroIfSrc2Zero(opc) && Kind(src2) == RefKind::CONST &&
          ConstIsZero(src2));
}

bool InsStrengthReduction(Ins ins) {
  // limit shifts to [0, bitwidth -1]
  if (InsOPC(ins) == OPC::SHL || InsOPC(ins) == OPC::SHR) {
    const Const num2 = Const(InsOperand(ins, 2));
    if (Kind(num2) == RefKind::CONST) {
      const DK dk = ConstKind(num2);
      uint64_t mask = DKBitWidth(dk) - 1;
      if (DKFlavor(dk) == DK_FLAVOR_U) {
        InsOperand(ins, 2) = ConstNewU(dk, mask & ConstValueU(num2));
      } else {
        InsOperand(ins, 2) = ConstNewACS(dk, mask & ConstValueACS(num2));
      }
    }
  }

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
    if (Kind(num1) == RefKind::CONST) {
      const Const bin_log = ConstTryApplyingBinaryLog(num1);
      if (!bin_log.isnull()) {
        InsOPC(ins) = OPC::SHL;
        InsOperand(ins, 1) = InsOperand(ins, 2);
        InsOperand(ins, 2) = bin_log;
        return true;
      }
    }

    const Const num2 = Const(InsOperand(ins, 2));
    if (Kind(num2) == RefKind::CONST) {
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

Handle NarrowOperand(Handle op, Fun fun, DK narrow_kind,
                     std::vector<Ins>* inss) {
  if (Kind(op) == RefKind::CONST) {
    Const c(op);
    if (DKFlavor(narrow_kind) == DK_FLAVOR_U) {
      uint64_t mask = (1 << DKBitWidth(narrow_kind)) - 1;
      uint64_t v = ConstValueU(c) & mask;
      return ConstNewU(ConstKind(c), v);
    } else {
      ASSERT(DKFlavor(narrow_kind) == DK_FLAVOR_S, "");
      int64_t v = ConstValueACS(c);
      return ConstNewACS(ConstKind(c),
                         SignedIntFromBits(v, DKBitWidth(narrow_kind)));
    }
  } else {
    ASSERT(Kind(op) == RefKind::REG, "");
    Reg reg(op);
    Reg tmp_reg = FunGetScratchReg(fun, narrow_kind, "narrowed", true);
    RegFlags(tmp_reg) |= uint8_t(REG_FLAG::MARKED);  // do not widen
    inss->push_back(InsNew(OPC::CONV, tmp_reg, reg));
    inss->push_back(InsNew(OPC::CONV, reg, tmp_reg));
    return op;
  }
}

// This is tricky and probably quite buggy at this point.
void FunRegWidthWidening(Fun fun, DK narrow_kind, DK wide_kind,
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
        switch (Kind(op)) {
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
        if (InsOPC(ins) == OPC::SHR) {
          InsOperand(ins, 1) =
              NarrowOperand(InsOperand(ins, 1), fun, narrow_kind, inss);
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
        if (Kind(reg) == RefKind::REG && RegKind(reg) == narrow_kind) {
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
      } else if (InsOpcodeKind(ins) == OPC_KIND::COND_BRA) {
        InsOperand(ins, 0) =
            NarrowOperand(InsOperand(ins, 0), fun, narrow_kind, inss);
        InsOperand(ins, 1) =
            NarrowOperand(InsOperand(ins, 1), fun, narrow_kind, inss);
        inss->push_back(ins);
        dirty = true;
      } else if (InsOpcodeKind(ins) == OPC_KIND::CMP) {
        InsOperand(ins, 1) =
            NarrowOperand(InsOperand(ins, 1), fun, narrow_kind, inss);
        InsOperand(ins, 2) =
            NarrowOperand(InsOperand(ins, 2), fun, narrow_kind, inss);
        inss->push_back(ins);
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

void FunEliminateStkLoadStoreWithRegOffset(Fun fun, DK base_kind,
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
      if (opc == OPC::ST_STK && Kind(InsOperand(ins, 1)) == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_stk(InsOperand(ins, 0));
        inss->push_back(
            InsInit(ins, OPC::ST, tmp, InsOperand(ins, 1), InsOperand(ins, 2)));
      } else if (opc == OPC::LD_STK &&
                 Kind(InsOperand(ins, 2)) == RefKind::REG) {
        dirty = true;
        Reg tmp = add_lea_stk(InsOperand(ins, 1));
        inss->push_back(
            InsInit(ins, OPC::LD, InsOperand(ins, 0), tmp, InsOperand(ins, 2)));
      } else if (opc == OPC::LEA_STK &&
                 Kind(InsOperand(ins, 2)) == RefKind::REG) {
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

void FunEliminateMemLoadStore(Fun fun, DK base_kind, DK offset_kind,
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
        // TODO: small st_offset/ld_offset should probably stay with the
        // `st`
        if (Kind(st_offset) == RefKind::CONST) std::swap(st_offset, lea_offset);
        Reg tmp = add_lea_mem(InsOperand(ins, 0), lea_offset);
        inss->push_back(
            InsInit(ins, OPC::ST, tmp, st_offset, InsOperand(ins, 2)));
        dirty = true;
      } else if (opc == OPC::LD_MEM) {
        Handle ld_offset = InsOperand(ins, 2);
        Handle lea_offset = ConstNewU(offset_kind, 0);
        if (Kind(ld_offset) == RefKind::CONST) std::swap(ld_offset, lea_offset);
        Reg tmp = add_lea_mem(InsOperand(ins, 1), lea_offset);
        inss->push_back(
            InsInit(ins, OPC::LD, InsOperand(ins, 0), tmp, ld_offset));
        dirty = true;
      } else if (opc == OPC::CAS_MEM) {
        Handle cas_offset = InsOperand(ins, 4);
        Handle lea_offset = ConstNewU(offset_kind, 0);
        if (Kind(cas_offset) == RefKind::CONST)
          std::swap(cas_offset, lea_offset);
        Reg tmp = add_lea_mem(InsOperand(ins, 3), lea_offset);
        inss->push_back(InsInit(ins, OPC::CAS, InsOperand(ins, 0),
                                InsOperand(ins, 1), InsOperand(ins, 2), tmp,
                                cas_offset));
        dirty = true;
      } else if (opc == OPC::LEA_MEM &&
                 Kind(InsOperand(ins, 2)) == RefKind::REG) {
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

void FunEliminateCntPop(Fun fun, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::CNTPOP) {
        ASSERT(DKBitWidth(RegKind(Reg(InsOperand(ins, 0)))) == 32,
               "only 32 bit supported");
        DK kind = DK::U32;
        Reg m1 = FunGetScratchReg(fun, kind, "popcnt_m1", false);
        Reg m2 = FunGetScratchReg(fun, kind, "popcnt_m2", false);
        Reg x = FunGetScratchReg(fun, kind, "popcnt_x", false);
        Reg t1 = FunGetScratchReg(fun, kind, "popcnt_t1", false);
        Reg t2 = FunGetScratchReg(fun, kind, "popcnt_t2", false);

        inss->push_back(InsNew(OPC::CONV, x, InsOperand(ins, 1)));
        inss->push_back(InsNew(OPC::MOV, m1, ConstNewU(kind, 0x55555555)));
        inss->push_back(InsNew(OPC::MOV, m2, ConstNewU(kind, 0x03030303)));
        inss->push_back(InsNew(OPC::SHR, t1, x, ConstNewU(kind, 1)));
        inss->push_back(InsNew(OPC::AND, t1, t1, m1));
        inss->push_back(InsNew(OPC::SUB, x, x, t1));
        //
        inss->push_back(InsNew(OPC::AND, t2, x, m2));
        inss->push_back(InsNew(OPC::SHR, t1, x, ConstNewU(kind, 2)));
        inss->push_back(InsNew(OPC::AND, t1, t1, m2));
        inss->push_back(InsNew(OPC::ADD, t2, t2, t1));
        inss->push_back(InsNew(OPC::SHR, t1, x, ConstNewU(kind, 4)));
        inss->push_back(InsNew(OPC::AND, t1, t1, m2));
        inss->push_back(InsNew(OPC::ADD, t2, t2, t1));
        inss->push_back(InsNew(OPC::SHR, t1, x, ConstNewU(kind, 6)));
        inss->push_back(InsNew(OPC::AND, t1, t1, m2));
        inss->push_back(InsNew(OPC::ADD, t2, t2, t1));
        //
        inss->push_back(InsNew(OPC::SHR, t1, t2, ConstNewU(kind, 8)));
        inss->push_back(InsNew(OPC::ADD, t2, t2, t1));
        inss->push_back(InsNew(OPC::SHR, t1, t2, ConstNewU(kind, 16)));
        inss->push_back(InsNew(OPC::ADD, t2, t2, t1));
        inss->push_back(InsNew(OPC::AND, t2, t2, ConstNewU(kind, 0x3f)));
        inss->push_back(InsNew(OPC::CONV, InsOperand(ins, 0), t2));
        //
        dirty = true;
      } else {
        inss->push_back(ins);
      }
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

void InsEliminateCmp(Ins cmp_ins, Bbl bbl, Fun fun) {
  const Bbl bbl_skip = BblNew(NewDerivedBblName(Name(bbl), "_split", fun));
  FunBblAddBst(fun, bbl_skip);
  FunBblInsertBefore(fun, bbl, bbl_skip);
  BblSplitBeforeFixEdges(bbl, cmp_ins, bbl_skip);

  const Bbl bbl_prev = BblNew(NewDerivedBblName(Name(bbl), "_split", fun));
  FunBblAddBst(fun, bbl_prev);
  FunBblInsertBefore(fun, bbl_skip, bbl_prev);
  BblSplitBeforeFixEdges(bbl_skip, cmp_ins, bbl_prev);

  const DK dk = RegKind(Reg(InsOperand(cmp_ins, 0)));
  const Reg reg = FunGetScratchReg(fun, dk, "cmp", false);
  BblInsUnlink(cmp_ins);
  BblInsAppendList(bbl_prev, InsNew(OPC::MOV, reg, InsOperand(cmp_ins, 1)));
  BblInsAppendList(bbl_prev,
                   InsNew(InsOPC(cmp_ins) == OPC::CMPEQ ? OPC::BEQ : OPC::BLT,
                          InsOperand(cmp_ins, 3), InsOperand(cmp_ins, 4), bbl));

  BblInsAppendList(bbl_skip, InsNew(OPC::MOV, reg, InsOperand(cmp_ins, 2)));

  BblInsPrepend(bbl, InsNew(OPC::MOV, InsOperand(cmp_ins, 0), reg));
  EdgLink(EdgNew(bbl_prev, bbl));

  InsDel(cmp_ins);  // must delay deletion as we are still reading operands
}

void FunEliminateCmp(Fun fun, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    Ins ins = BblInsList::Head(bbl);
    while (!BblInsList::IsSentinel(ins)) {
      const Ins next = BblInsList::Next(ins);
      if (InsOpcode(ins).kind == OPC_KIND::CMP) {
        // deletes ins
        InsEliminateCmp(ins, bbl, fun);
      }
      ins = next;
    }
  }
}

void FunEliminateCopySign(Fun fun, std::vector<Ins>* inss) {
  for (Bbl bbl : FunBblIter(fun)) {
    inss->clear();
    bool dirty = false;
    for (Ins ins : BblInsIter(bbl)) {
      if (InsOPC(ins) == OPC::COPYSIGN) {
        const DK dk = RegKind(Reg(InsOperand(ins, 0)));
        ASSERT(DKFlavor(dk) == DK_FLAVOR_F, "");
        const DK int_dk = (dk == DK::R32) ? DK::U32 : DK::U64;
        const uint64_t sign = (dk == DK::R32) ? 1ULL << 31 : 1ULL << 63;
        const Const sign_mask = ConstNewU(int_dk, sign);
        const Const rest_mask = ConstNewU(int_dk, sign - 1);
        const Reg tmp_src1 =
            FunGetScratchReg(fun, int_dk, "elim_copysign1", false);
        const Reg tmp_src2 =
            FunGetScratchReg(fun, int_dk, "elim_copysign2", false);
        inss->push_back(InsNew(OPC::BITCAST, tmp_src1, InsOperand(ins, 1)));
        inss->push_back(InsNew(OPC::AND, tmp_src1, tmp_src1, rest_mask));
        inss->push_back(InsNew(OPC::BITCAST, tmp_src2, InsOperand(ins, 2)));
        inss->push_back(InsNew(OPC::AND, tmp_src2, tmp_src2, sign_mask));
        inss->push_back(InsNew(OPC::OR, tmp_src1, tmp_src1, tmp_src2));
        InsInit(ins, OPC::BITCAST, InsOperand(ins, 0), tmp_src1);
        dirty = true;
      }
      inss->push_back(ins);
    }
    if (dirty) BblReplaceInss(bbl, *inss);
  }
}

Reg RegConstCache::Materialize(Fun fun, Const num, bool from_mem,
                               std::vector<Ins>* inss) {
  for (uint32_t i = 0; i < cache_.size(); ++i) {
    if (cache_[i].num == num) {
      Reg out = cache_[i].reg;
      if (i != 0) {
        cache_.erase(cache_.begin() + i);
        insert(num, out);
      }
      return out;
    }
  }
  // not in cache
  Reg out;
  if (from_mem) {
    Mem mem = UnitFindOrAddConstMem(unit_, num);
    Reg tmp_addr = FunGetScratchReg(fun, addr_kind_, "mem_const_addr", true);
    inss->push_back(
        InsNew(OPC::LEA_MEM, tmp_addr, mem, ConstNewU(offset_kind_, 0)));
    out = FunGetScratchReg(fun, ConstKind(num), "mem_const", true);
    inss->push_back(InsNew(OPC::LD, out, tmp_addr, ConstNewU(offset_kind_, 0)));
  } else {
    out = FunGetScratchReg(fun, ConstKind(num), "imm", true);
    inss->push_back(InsNew(OPC::MOV, out, num));
  }
  insert(num, out);
  return out;
}

bool InsLimtiShiftAmounts(Ins ins, Fun fun, int width, std::vector<Ins>* inss) {
  const DK dk = RegKind(Reg(InsOperand(ins, 0)));
  Handle amount = InsOperand(ins, 2);
  if (Kind(amount) == RefKind::CONST) {
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
        // everytime we see a PUSHARG we must have seen a call or return
        // before with parameters that still needs to be processed.
        // Note: that we are going backwards inside the BBL.
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

void FunSetInOutCpuRegs(Fun fun, const PushPopInterface& ppif) {
  std::vector<CpuReg> cpu_regs;
  ppif.GetCpuRegsForInSignature(FunNumInputTypes(fun), FunInputTypes(fun),
                                &cpu_regs);
  FunNumCpuLiveIn(fun) = cpu_regs.size();
  memcpy(FunCpuLiveIn(fun), cpu_regs.data(), cpu_regs.size() * sizeof(CpuReg));

  ppif.GetCpuRegsForOutSignature(FunNumOutputTypes(fun), FunOutputTypes(fun),
                                 &cpu_regs);
  FunNumCpuLiveOut(fun) = cpu_regs.size();
  memcpy(FunCpuLiveOut(fun), cpu_regs.data(), cpu_regs.size() * sizeof(CpuReg));
}

}  // namespace cwerg::base
