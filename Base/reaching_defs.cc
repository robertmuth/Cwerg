// (c) Robert Muth - see LICENSE for more info

#include "Base/reaching_defs.h"
#include "Base/opcode_gen.h"
#include "Base/cfg.h"
#include "Base/serialize.h"
#include "Util/handlevec.h"

#include <set>

namespace cwerg::base {
namespace {

const Handle HandleBottom(0, RefKind::BBL);
const Handle HandleTop(0, RefKind::INS);

void BblInitReachingDefs(Bbl bbl, unsigned num_regs) {
  for (unsigned i = 1; i < num_regs; ++i) {
    BblReachingDefsIn(bbl).Set(i, HandleBottom);
    BblReachingDefsOut(bbl).Set(i, HandleBottom);
    BblReachingDefsDef(bbl).Set(i, HandleBottom);
  }

  for (Ins ins : BblInsIter(bbl)) {
    for (unsigned i = 1; i < num_regs; ++i) {
      unsigned num_defs = InsOpcode(ins).num_defs;
      for (unsigned pos = 0; pos < num_defs; ++pos) {
        const Reg reg = Reg(InsOperand(ins, pos));
        ASSERT(reg.kind() == RefKind::REG, "");
        BblReachingDefsDef(bbl).Set(RegNo(reg), ins);
      }
    }
  }
}

// Propagation to `self` from an incoming `other`
// Simple lattice with top, bot, and all other elements in-between.
bool HandleVecCombineWith(HandleVec self,
                          HandleVec other,
                          unsigned num_regs,
                          Handle top) {
  ASSERT(self.raw_width() == other.raw_width(), "");
  Handle* data1 = self.BackingStorage();
  Handle* data2 = other.BackingStorage();
  bool change = false;
  for (unsigned i = 1; i < num_regs; ++i) {
    Handle h1 = data1[i];
    if (h1 == top) continue;
    Handle h2 = data2[i];
    if (h2 == HandleBottom || h1 == h2) continue;
    if (h1 == HandleBottom) {
      change = true;
      data1[i] = h2;
      continue;
    }
    change = true;
    data1[i] = top;
  }
  return change;
}

// Propagation to `out` from `in` applying `def`
bool HandleVecUpdateWith(HandleVec out,
                         HandleVec in,
                         HandleVec def,
                         unsigned num_regs) {
  ASSERT(
      out.raw_width() == in.raw_width() && out.raw_width() == def.raw_width(),
      "");
  bool change = false;
  Handle* data_out = out.BackingStorage();
  Handle* data_in = in.BackingStorage();
  Handle* data_def = def.BackingStorage();

  for (unsigned i = 1; i < num_regs; ++i) {
    Handle h = data_def[i];
    if (h == HandleBottom) {
      h = data_in[i];
    }
    if (h != data_out[i]) {
      data_out[i] = h;
      change = true;
    }
  }
  return change;
}

}  // namespace

void FunComputeReachingDefs(Fun fun) {
  const unsigned num_regs = FunNumRegs(fun);

  // Step 1: Initialization
  // By setting the reaching_defs_in of first Bbl to bottom (=undefined),
  // and undefined value combined with some other value x will become x.
  // The other option is to initialize all reaching_defs_in of first Bbl
  // to that bbl.

  for (Bbl bbl : FunBblIter(fun)) HandleVec::Del(BblReachingDefsIn(bbl));
  for (Bbl bbl : FunBblIter(fun)) {
    HandleVec::Del(BblReachingDefsOut(bbl));
    HandleVec::Del(BblReachingDefsDef(bbl));
  }

  // We want all the BblLiveOuts to be adjacent
  for (Bbl bbl : FunBblIter(fun)) {
    BblReachingDefsIn(bbl) = HandleVec::New(num_regs);
  }

  for (Bbl bbl : FunBblIter(fun)) {
    BblReachingDefsOut(bbl) = HandleVec::New(num_regs);
    BblReachingDefsDef(bbl) = HandleVec::New(num_regs);
  }

  for (Bbl bbl : FunBblIter(fun)) {
    BblInitReachingDefs(bbl, num_regs);
  }

  // Step 2: Fixpoint computation
  // Note, we look at the first bbl first
  int count = 0;
  std::set<Bbl> active_set;
  std::vector<Bbl> active_stk;
  for (Bbl bbl : FunBblIterReverse(fun)) {  // stack inverts order
    active_stk.push_back(bbl);
    active_set.insert(bbl);
  }

  while (!active_stk.empty()) {
    ++count;
    const Bbl bbl = active_stk.back();
    active_stk.pop_back();
    active_set.erase(bbl);
    HandleVec out = BblReachingDefsOut(bbl);
    if (!HandleVecUpdateWith(out, BblReachingDefsIn(bbl),
                             BblReachingDefsDef(bbl), num_regs)) {
      continue;
    }

    for (Edg edg : BblSuccEdgIter(bbl)) {
      Bbl succ = EdgSuccBbl(edg);
      if (HandleVecCombineWith(BblReachingDefsIn(succ), out, num_regs, succ)) {
        // NOTE: would it be better to go DFS and move the succ up the stack?
        if (active_set.find(succ) == active_set.end())
          active_stk.push_back(succ);
      }
    }
  }

  // Step 3: Make analysis results accessible
  // All entries should be be Ins or Bbl, except for cases of undefined
  for (Bbl bbl : FunBblIter(fun)) {
    Handle* data = BblReachingDefsIn(bbl).BackingStorage();
    for (unsigned i = 1; i < num_regs; ++i) {
      if (data[i] == HandleBottom) data[i] = bbl;
    }
  }
  HandleVec hv = HandleVec::New(num_regs);
  Handle* data = hv.BackingStorage();
  for (Bbl bbl : FunBblIter(fun)) {
    hv.CopyFrom(BblReachingDefsIn(bbl));
    for (Ins ins : BblInsIter(bbl)) {
      // TODO: when have machine regs we also need to account for
      // clobbered regs after calls
      const unsigned num_defs = InsOpcode(ins).num_defs;
      const unsigned num_ops = InsOpcode(ins).num_operands;
      for (unsigned i = 0; i < num_ops; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        if (i < num_defs || reg.kind() != RefKind::REG) {
          InsDef(ins, i) = HandleTop;
        } else {
          InsDef(ins, i) = data[RegNo(reg)];
        }
      }
      for (unsigned i = 0; i < num_defs; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        ASSERT(reg.kind() == RefKind::REG, "unexpect non reg in " << ins);
        data[RegNo(reg)] = ins;
      }
    }
  }
  HandleVec::Del(hv);
}

static void InsPropagateConsts(Ins ins) {
  const unsigned num_ops = InsOpcode(ins).num_operands;
  for (unsigned i = 0; i < num_ops; ++i) {
    Ins d = Ins(InsDef(ins, i));
    if (d.isnull() || d.kind() != RefKind::INS || InsOPC(d) != OPC::MOV)
      continue;
    Const v = Const(InsOperand(d, 1));
    if (v.kind() != RefKind::CONST) continue;
    InsOperand(ins, i) = v;
    InsDef(ins, i) = HandleTop;
    // std::cout << "@@@in propagate " << Name() << " " << ins << "\n";
  }
}

void FunPropagateConsts(Fun fun) {
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      InsPropagateConsts(ins);
    }
  }
}

namespace {

template <typename VAL>
bool eval_cond(OPC opc, VAL a, VAL b) {
  switch (opc) {
    case OPC::BEQ:
      return a == b;
    case OPC::BNE:
      return a != b;
    case OPC::BLE:
      return a <= b;
    case OPC::BLT:
      return a < b;
    default:
      ASSERT(false, "");
      return false;
  }
}

bool EvalCondBra(OPC opc, Const a, Const b) {
  switch (DKFlavor(ConstKind(a))) {
    case DK_FLAVOR_A:
    case DK_FLAVOR_C:
    case DK_FLAVOR_S: {
      return eval_cond<int64_t>(opc, ConstValueACS(a), ConstValueACS(b));
    }
    case DK_FLAVOR_U: {
      return eval_cond<uint64_t>(opc, ConstValueU(a), ConstValueU(b));
    }
    default:
      ASSERT(false, "not supported");
      return false;
  }
}

Const EvalAlu(OPC opc, Const a, Const b) {
  ASSERT(a.kind() == b.kind(), "");
  if (DKFlavor(ConstKind(a)) == DK_FLAVOR_U) {
    uint64_t va = ConstValueU(a);
    uint64_t vb = ConstValueU(b);
    switch (opc) {
      case OPC::ADD:
        return ConstNewU(ConstKind(a), va + vb);
      case OPC::SUB:
        return ConstNewU(ConstKind(a), va - vb);
      case OPC::MUL:
        return ConstNewU(ConstKind(a), va * vb);
      case OPC::DIV:
        return ConstNewU(ConstKind(a), vb == 0 ? 0 : va / vb);
      case OPC::SHL:
        return ConstNewU(ConstKind(a), va << vb);  // TODO: needs more thought
      default:
        ASSERT(false, "");
        return Const();  // invalid
    }
  } else if (DKFlavor(ConstKind(a)) == DK_FLAVOR_F) {
    double va = ConstValueF(a);
    double vb = ConstValueF(b);
    switch (opc) {
      case OPC::ADD:
        return ConstNewF(ConstKind(a), va + vb);
      case OPC::SUB:
        return ConstNewF(ConstKind(a), va - vb);
      case OPC::MUL:
        return ConstNewF(ConstKind(a), va * vb);
      case OPC::DIV:
        return ConstNewF(ConstKind(a), vb == 0.0 ? 0.0 : va / vb);
      default:
        ASSERT(false, "");
        return Const();  // invalid
    }
  } else {
    int64_t va = ConstValueACS(a);
    int64_t vb = ConstValueACS(b);
    switch (opc) {
      case OPC::ADD:
        return ConstNewACS(ConstKind(a), va + vb);
      case OPC::SUB:
        return ConstNewACS(ConstKind(a), va - vb);
      case OPC::MUL:
        return ConstNewACS(ConstKind(a), va * vb);
      case OPC::DIV:
        return ConstNewACS(ConstKind(a), vb == 0 ? 0 : va / vb);
      case OPC::OR:
        return ConstNewACS(ConstKind(a), va | vb);
      case OPC::AND:
        return ConstNewACS(ConstKind(a), va & vb);
      case OPC::SHR:
        return ConstNewACS(ConstKind(a), va >> vb);  // TODO: needs more thought
      case OPC::SHL:
        return ConstNewACS(ConstKind(a), va << vb);  // TODO: needs more thought
      default:
        ASSERT(false, "unsupported folding of " << int(opc));
        return Const();  // invalid
    }
  }
}

void InsConstantFold(Ins ins, Bbl bbl, bool allow_conv_conversion,
                     std::vector<Ins>* to_delete) {
  const OPC opc = InsOPC(ins);
  const OPC_KIND kind = InsOpcodeKind(ins);
  switch (kind) {
    case OPC_KIND::COND_BRA: {
      const Const op1 = Const(InsOperand(ins, 0));
      const Const op2 = Const(InsOperand(ins, 1));
      if (op1.kind() != RefKind::CONST || op2.kind() != RefKind::CONST) break;
      const Bbl target = Bbl(InsOperand(ins, 2));
      const bool branch_taken = EvalCondBra(opc, op1, op2);
      Edg edg = BblSuccEdgList::Head(bbl);
      // if the branch is taken we want to remove the other Edg
      if ((EdgSuccBbl(edg) == target) == branch_taken) {
        edg = BblSuccEdgList::Next(edg);
      }
      EdgUnlink(edg);
      EdgDel(edg);
      to_delete->push_back(ins);
      break;
    }
    case OPC_KIND::ALU: {
      Const op1 = Const(InsOperand(ins, 1));
      Const op2 = Const(InsOperand(ins, 2));
      if (op1.kind() != RefKind::CONST || op2.kind() != RefKind::CONST) break;
      // std::cout << "@@@@@ " << ins << "\n";
      Const val = EvalAlu(opc, op1, op2);
      InsOPC(ins) = OPC::MOV;
      InsOperand(ins, 1) = val;
      InsDef(ins, 1) = HandleTop;
      InsOperand(ins, 2) = HandleInvalid;
      InsDef(ins, 1) = HandleTop;
      break;
    }
    case OPC_KIND::ALU1: {
      Const op = Const(InsOperand(ins, 1));
      if (op.kind() != RefKind::CONST) break;
      ASSERT(false, "Evaluator NYI for ALU1: " << ins);
      break;
    }
    case OPC_KIND::MOV: {
      Const op = Const(InsOperand(ins, 1));
      if (!allow_conv_conversion || opc != OPC::CONV ||
          op.kind() != RefKind::CONST)
        break;
      ASSERT(false, "Evaluator NYI for MOV: " << ins);
      break;
    }
    default:
      break;
  }
}

}  // namespace

int FunConstantFold(Fun fun, bool allow_conv_conversion,
                     std::vector<Ins>* to_delete) {
  to_delete->clear();
  for (Bbl bbl : FunBblIter(fun)) {
    for (Ins ins : BblInsIter(bbl)) {
      InsConstantFold(ins, bbl, allow_conv_conversion, to_delete);
    }
  }
    for (Ins ins : *to_delete) {
    BblInsUnlink(ins);
    InsDel(ins);
  }
  return to_delete->size();
}

namespace {

struct OpInfo {
  Handle op;
  Handle def;
  DK dk;
};

// TODO: Hackish
Const ConstSumOffsets(Const a, Const b) {
  int64_t va =
      DKFlavor(ConstKind(a)) == DK_FLAVOR_U ? ConstValueU(a) : ConstValueACS(a);
  int64_t vb =
      DKFlavor(ConstKind(b)) == DK_FLAVOR_U ? ConstValueU(b) : ConstValueACS(b);
  // TODO: overflow and signs need to be checked
  return ConstNewOffset(va + vb);
}

OpInfo CombinedOffset(Ins ins, Ins base_ins) {
  const OPC_KIND of = InsOpcodeKind(ins);
  const unsigned off_pos = of == OPC_KIND::ST ? 1 : 2;
  const Const offset1 = Const(InsOperand(ins, off_pos));
  if (InsOPC(base_ins) == OPC::MOV) {
    return OpInfo{offset1, InsDef(ins, off_pos), DK::INVALID};
  }
  if (InsOpcodeKind(base_ins) != OPC_KIND::LEA) {
    return OpInfo{HandleInvalid, HandleInvalid, DK::INVALID};
  }
  const Const offset2 = Const(InsOperand(base_ins, 2));
  if (offset2.kind() == RefKind::CONST && ConstIsZero(offset2)) {
    return OpInfo{offset1, InsDef(ins, off_pos), DK::INVALID};
  }
  if (offset1.kind() == RefKind::CONST && ConstIsZero(offset1)) {
    return OpInfo{offset2, InsDef(base_ins, 2), DK::INVALID};
  }
  if (offset1.kind() == RefKind::CONST && offset2.kind() == RefKind::CONST) {
    return OpInfo{ConstSumOffsets(offset1, offset2), HandleInvalid,
                  DK::INVALID};
  }
  return OpInfo{HandleInvalid, HandleInvalid, DK::INVALID};
}

bool DefAvailable(const OpInfo& op_info, Handle* data) {
  const RefKind kind = op_info.op.kind();
  if (kind == RefKind::CONST || kind == RefKind::MEM || kind == RefKind::STK) {
    return true;
  }
  ASSERT(kind == RefKind::REG, "unexpected Refkind " << int(kind));
  if (op_info.def == HandleTop) return false;
  return op_info.def == data[RegNo(Reg(op_info.op))];
}

#if 0
std::ostream& operator<<(std::ostream& os, const Handle& h) {
  os << h.index() << "::" << int(h.kind());
  return os;
}
#endif

OPC NewOPC(OPC ins_opc, OPC base_opc) {
  if (ins_opc == OPC::LD) {
    switch (base_opc) {
      case OPC::LEA_MEM:
        return OPC::LD_MEM;
      case OPC::LEA_STK:
        return OPC::LD_STK;
      case OPC::MOV:
      case OPC::LEA:
        return OPC::LD;
      default:
        break;
    }
  } else if (ins_opc == OPC::ST) {
    switch (base_opc) {
      case OPC::LEA_MEM:
        return OPC::ST_MEM;
      case OPC::LEA_STK:
        return OPC::ST_STK;
      case OPC::MOV:
      case OPC::LEA:
        return OPC::ST;
      default:
        break;
    }
  } else if (ins_opc == OPC::LEA) {
    switch (base_opc) {
      case OPC::LEA_MEM:
        return OPC::LEA_MEM;
      case OPC::LEA_STK:
        return OPC::LEA_STK;
      case OPC::MOV:
      case OPC::LEA:
        return OPC::LEA;
      default:
        break;
    }
  }
  return OPC::INVALID;
}

void InsTryLoadStoreSimplify(Ins ins, Handle* data) {
  const OPC opc = InsOPC(ins);
  if (opc != OPC::LD && opc != OPC::ST && opc != OPC::LEA) return;
  unsigned base_pos = opc == OPC::ST ? 0 : 1;
  Ins ins_base = Ins(InsDef(ins, base_pos));
  if (ins_base.kind() != RefKind::INS) return;
  const OPC new_opc = NewOPC(opc, InsOPC(ins_base));
  if (new_opc == OPC::INVALID) return;
  const OpInfo base_info{InsOperand(ins_base, 1),  //
                         InsDef(ins_base, 1),      //
                         DK::INVALID};
  if (!DefAvailable(base_info, data)) return;
  OpInfo offset_info = CombinedOffset(ins, ins_base);
  if (offset_info.op.isnull()) return;
  if (!DefAvailable(offset_info, data)) return;
  InsOPC(ins) = new_opc;
  if (opc == OPC::ST) {
    InsOperand(ins, 0) = base_info.op;
    InsDef(ins, 0) = base_info.def;
    InsOperand(ins, 1) = offset_info.op;
    InsDef(ins, 1) = offset_info.def;
  } else {
    InsOperand(ins, 1) = base_info.op;
    InsDef(ins, 1) = base_info.def;
    InsOperand(ins, 2) = offset_info.op;
    InsDef(ins, 2) = offset_info.def;
  }
}

}  // namespace

void FunLoadStoreSimplify(Fun fun) {
  const unsigned num_regs = FunNumRegs(fun);
  HandleVec hv = HandleVec::New(num_regs);
  Handle* data = hv.BackingStorage();
  for (Bbl bbl : FunBblIter(fun)) {
    hv.CopyFrom(BblReachingDefsIn(bbl));
    for (Ins ins : BblInsIter(bbl)) {
      InsTryLoadStoreSimplify(ins, data);
      unsigned num_defs = InsOpcode(ins).num_defs;
      for (unsigned i = 0; i < num_defs; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        ASSERT(reg.kind() == RefKind::REG, "");
        data[RegNo(reg)] = ins;
      }
    }
  }
  HandleVec::Del(hv);
}

void InsTryPropagateRegs(Ins ins, Handle* data) {
  unsigned num_ops = InsOpcode(ins).num_operands;
  for (unsigned i = 0; i < num_ops; ++i) {
    Ins mov = Ins(InsDef(ins, i));
    if (mov.isnull() || mov.kind() != RefKind::INS || InsOPC(mov) != OPC::MOV) {
      continue;
    }
    Reg src_reg = Reg(InsOperand(mov, 1));
    if (src_reg.kind() != RefKind::REG || !RegCpuReg(src_reg).isnull()) {
      continue;
    }
    Ins src_def = Ins(InsDef(mov, 1));
    if (data[RegNo(src_reg)] != src_def) continue;
    InsOperand(ins, i) = src_reg;
    InsDef(ins, i) = src_def;
  }
}

void FunPropagateRegs(Fun fun) {
  const unsigned num_regs = FunNumRegs(fun);
  HandleVec hv = HandleVec::New(num_regs);
  Handle* data = hv.BackingStorage();
  for (Bbl bbl : FunBblIter(fun)) {
    hv.CopyFrom(BblReachingDefsIn(bbl));
    for (Ins ins : BblInsIter(bbl)) {
      InsTryPropagateRegs(ins, data);
      unsigned num_defs = InsOpcode(ins).num_defs;
      for (unsigned i = 0; i < num_defs; ++i) {
        Reg reg = Reg(InsOperand(ins, i));
        ASSERT(reg.kind() == RefKind::REG, "");
        data[RegNo(reg)] = ins;
      }
    }
  }
  HandleVec::Del(hv);
}

}  // namespace cwerg::base
