// (c) Robert Muth - see LICENSE for more info

#include "Base/cfg.h"

#include <set>

#include "Base/opcode_gen.h"
#include "Base/sanity.h"
#include "Base/serialize.h"
#include "Util/parse.h"

namespace cwerg::base {
namespace {

void BblRemoveUnreachableIns(Bbl bbl) {
  Ins last = Ins(0);
  for (Ins ins : BblInsIter(bbl)) {
    OPC_KIND kind = InsOpcodeKind(ins);
    if (kind == OPC_KIND::RET || kind == OPC_KIND::BRA) {
      last = ins;
      break;
    }
  }

  if (last.isnull()) return;
  // drop all Inss after ins
  for (Ins dead = BblInsList::Next(last); !BblInsList::IsSentinel(dead);
       dead = BblInsList::Next(dead)) {
    InsDel(dead);
  }
  BblInsList::Tail(bbl) = last;
  BblInsList::Next(last) = BblInsList::MakeSentinel(bbl);
}

std::vector<Ins> BblFindSubRanges(Bbl bbl) {
  std::vector<Ins> out;
  bool is_start = true;
  for (Ins ins : BblInsIter(bbl)) {
    if (is_start) {
      out.push_back(ins);
      is_start = false;
    }

    if (InsOpcode(ins).IsBblTerminator()) {
      is_start = true;
    }
  }
  return out;
}

void FunReplaceBbls(Fun fun, const std::vector<Bbl>& bbls) {
  ASSERT(!bbls.empty(), "");
  Bbl first = bbls[0];
  FunBblList::Prev(first) = FunBblList::MakeSentinel(fun);
  FunBblList::Head(fun) = first;
  for (size_t i = 1; i < bbls.size(); ++i) {
    FunBblList::Next(bbls[i - 1]) = bbls[i];
    FunBblList::Prev(bbls[i]) = bbls[i - 1];
  }
  Bbl last = bbls.back();
  FunBblList::Next(last) = FunBblList::MakeSentinel(fun);
  FunBblList::Tail(fun) = last;
}

void InsMaybePatchNewSuccessor(Ins last_ins, Bbl old_succ, Bbl new_succ) {
  switch (InsOpcodeKind(last_ins)) {
    case OPC_KIND::BRA:
      if (InsOperand(last_ins, 0) == old_succ) {
        InsOperand(last_ins, 0) = new_succ;
      }
      break;
    case OPC_KIND::COND_BRA:
      if (InsOperand(last_ins, 2) == old_succ) {
        InsOperand(last_ins, 2) = new_succ;
      }
      break;
    case OPC_KIND::SWITCH: {
      Jtb jtb = Jtb(InsOperand(last_ins, 1));
      if (JtbDefBbl(jtb) == old_succ) JtbDefBbl(jtb) = new_succ;
      for (Jen jen : JtbJenIter(jtb)) {
        if (JenBbl(jen) == old_succ) {
          JenBbl(jen) = new_succ;
        }
      }
      break;
    }
    default:
      break;
  }
}

void BblForwardEdgs(Bbl bbl, Bbl old_succ, Bbl new_succ) {
  for (Edg edg : BblSuccEdgIter(bbl)) {
    if (EdgSuccBbl(edg) == old_succ) {
      BblPredEdgUnlink(edg);
      EdgSuccBbl(edg) = new_succ;
      BblPredEdgAppend(new_succ, edg);
    }
  }
}

OPC GetCondBraInv(OPC opc) {
  switch (opc) {
    case OPC::BNE:
      return OPC::BEQ;
    case OPC::BEQ:
      return OPC::BNE;
    case OPC::BLE:
      return OPC::BLT;
    case OPC::BLT:
      return OPC::BLE;
    default:
      ASSERT(false, "");
      return OPC::INVALID;
  }
}

Ins InsNewBra(Bbl target) { return InsNew(OPC::BRA, target); }

}  // namespace

Str NewDerivedBblName(Str orig_name, const char* suffix, Fun fun) {
  char buf[kMaxIdLength];
  strncpy(buf, StrData(orig_name), kMaxIdLength - 1);
  strncat(buf, suffix, kMaxIdLength - 1);
  const size_t len = strlen(buf);
  ASSERT(len < kMaxIdLength - 10, "Bbl name too large");
  for (int i = 1; i < 10000; ++i) {
    ToDecString(i, buf + len);
    Str candidate = StrNew(buf);
    if (FunBblFind(fun, candidate).isnull()) return candidate;
  }
  ASSERT(false, "too many derived Bbls");
  return Str(0);
}

void EdgLink(Edg edg) {
  BblSuccEdgAppend(EdgPredBbl(edg), edg);
  BblPredEdgAppend(EdgSuccBbl(edg), edg);
}

void EdgUnlink(Edg edg) {
  BblSuccEdgUnlink(edg);
  BblPredEdgUnlink(edg);
}

Fun InsCallee(Ins ins) {
  switch (InsOPC(ins)) {
    case OPC::SYSCALL:
      // fallthrough
    case OPC::BSR:
      return Fun(InsOperand(ins, 0));
    case OPC::JSR:
      return Fun(InsOperand(ins, 0));
    default:
      ASSERT(false, "bad ins: " << ins);
      return Fun(0);
  }
}

void InsFlipCondBra(Ins ins, Bbl old_target, Bbl new_target) {
  ASSERT(InsOperand(ins, 2) == old_target, "");
  InsOperand(ins, 2) = new_target;
  InsOPC(ins) = GetCondBraInv(InsOPC(ins));
  if (InsOPC(ins) != OPC::BEQ && InsOPC(ins) != OPC::BNE) {
    InsSwapOps(ins, 0, 1);
  }
}

void BblSplitAfter(Bbl bbl, Ins new_bbl_first_ins, Bbl new_bbl) {
  const Ins new_bbl_last_ins = BblInsList::Tail(bbl);
  const Ins prev_ins = BblInsList::Prev(new_bbl_first_ins);
  BblInsList::Tail(bbl) = prev_ins;
  BblInsList::Next(prev_ins) = BblInsList::MakeSentinel(bbl);

  BblInsList::Head(new_bbl) = new_bbl_first_ins;
  BblInsList::Tail(new_bbl) = new_bbl_last_ins;
  BblInsList::Prev(new_bbl_first_ins) = BblInsList::MakeSentinel(new_bbl);
  BblInsList::Next(new_bbl_last_ins) = BblInsList::MakeSentinel(new_bbl);
}

void BblSplitBeforeFixEdges(Bbl bbl, Ins new_bbl_last_ins, Bbl new_bbl) {
  const Ins new_bbl_first_ins = BblInsList::Head(bbl);
  const Ins next_ins = BblInsList::Next(new_bbl_last_ins);
  BblInsList::Head(bbl) = next_ins;
  if (BblInsList::IsSentinel(next_ins)) {
    BblInsList::Tail(bbl) = next_ins;
  } else {
    BblInsList::Prev(next_ins) = BblInsList::MakeSentinel(bbl);
  }
  BblInsList::Head(new_bbl) = new_bbl_first_ins;
  BblInsList::Tail(new_bbl) = new_bbl_last_ins;
  BblInsList::Prev(new_bbl_first_ins) = BblInsList::MakeSentinel(new_bbl);
  BblInsList::Next(new_bbl_last_ins) = BblInsList::MakeSentinel(new_bbl);

  std::set<Bbl> preds;
  for (Edg edg : BblPredEdgIter(bbl)) preds.insert(EdgPredBbl(edg));
  for (Bbl pred : preds) {
    if (!BblInsList::IsEmpty(pred)) {
      InsMaybePatchNewSuccessor(BblInsList::Tail(pred), bbl, new_bbl);
    }

    BblForwardEdgs(pred, bbl, new_bbl);
  }
  EdgLink(EdgNew(new_bbl, bbl));
}

void FunSplitBbls(Fun fun) {
  std::vector<Bbl> bbls;
  bool dirty = false;
  for (Bbl bbl : FunBblIter(fun)) {
    BblRemoveUnreachableIns(bbl);
    bbls.push_back(bbl);
    std::vector<Ins> ranges = BblFindSubRanges(bbl);
    if (ranges.size() <= 1) continue;
    /*
    std::cout << "splitting " << Name(bbl) << bbl << "\n";
    for (Ins ins : ranges) {
        std::cout << "splitting " << ins << "\n";
    }
     */
    dirty = true;
    for (size_t i = 1; i < ranges.size(); ++i) {
      Ins first_ins = ranges[i];
      const Bbl new_bbl = BblNew(NewDerivedBblName(Name(bbl), "_", fun));

      BblSplitAfter(bbls.back(), first_ins, new_bbl);
      FunBblAddBst(fun, new_bbl);
      bbls.push_back(new_bbl);
    }
  }
  if (dirty) FunReplaceBbls(fun, bbls);
}

void FunInitCFG(Fun fun) {
  Bbl fallthrough = Bbl(0);
  for (Bbl bbl : FunBblIter(fun)) {
    if (!fallthrough.isnull()) {
      EdgLink(EdgNew(fallthrough, bbl));
      fallthrough = Bbl(0);
    }
    if (BblInsList::IsEmpty(bbl)) {
      fallthrough = bbl;
      continue;
    }
    Ins last_ins = BblInsList::Tail(bbl);
    switch (InsOpcodeKind(last_ins)) {
      case OPC_KIND::RET:
        break;
      case OPC_KIND::BRA:
        EdgLink(EdgNew(bbl, Bbl(InsOperand(last_ins, 0))));
        break;
      case OPC_KIND::COND_BRA:
        EdgLink(EdgNew(bbl, Bbl(InsOperand(last_ins, 2))));
        fallthrough = bbl;
        break;
      case OPC_KIND::SWITCH: {
        Jtb jtb = Jtb(InsOperand(last_ins, 1));
        EdgLink(EdgNew(bbl, JtbDefBbl(jtb)));
        for (Jen jen : JtbJenIter(jtb)) {
          EdgLink(EdgNew(bbl, JenBbl(jen)));
        }
      } break;
      default:
        fallthrough = bbl;
        break;
    }
  }
  // TODO: see reference implementation for background info
  if (!fallthrough.isnull()) {
    Bbl last_bbl = FunBblList::Tail(fun);
    ASSERT(BblInsList::IsEmpty(last_bbl), "");
    FunBblDel(fun, last_bbl);
    FunBblUnlink(last_bbl);
    BblDel(last_bbl);
  }
}

void FunRemoveUnconditionalBranches(Fun fun) {
  for (Bbl bbl : FunBblIter(fun)) {
    if (BblInsList::IsEmpty((bbl))) continue;
    Ins last_ins = BblInsList::Tail(bbl);
    OPC_KIND kind = InsOpcodeKind(last_ins);
    if (kind == OPC_KIND::BRA) {
      BblInsUnlink(last_ins);
      InsDel(last_ins);
    }
  }
}

void FunRemoveEmptyBbls(Fun fun) {
  std::vector<Bbl> bbls_keep;
  std::vector<Bbl> bbls_empty;
  for (Bbl bbl : FunBblIter(fun)) {
    if (!BblInsList::IsEmpty(bbl)) {
      bbls_keep.push_back(bbl);
      continue;
    }
    const Edg out_edg = BblSuccEdgList::Head(bbl);
    const Bbl succ = EdgSuccBbl(out_edg);
    if (succ == bbl) {
      bbls_keep.push_back(bbl);
      continue;
    }
    ASSERT(FunBblList::Head(fun) != bbl, "cannot remove entry bbl");
    ASSERT(out_edg == BblSuccEdgList::Tail(bbl) &&
               !BblSuccEdgList::IsSentinel(out_edg),
           "must have one out edge:\n"
               << bbl << "\n"
               << fun);
    bbls_empty.push_back(bbl);
    EdgUnlink(out_edg);
    EdgDel(out_edg);
    // For each incoming edge forward bbl to succ
    // We want to handle each predecessor only once.
    std::set<Bbl> preds;
    for (Edg edg : BblPredEdgIter(bbl)) preds.insert(EdgPredBbl(edg));
    for (Bbl pred : preds) {
      if (!BblInsList::IsEmpty(pred)) {
        InsMaybePatchNewSuccessor(BblInsList::Tail(pred), bbl, succ);
      }

      BblForwardEdgs(pred, bbl, succ);
    }
  }

  if (!bbls_empty.empty()) {
    FunReplaceBbls(fun, bbls_keep);
    for (Bbl bbl : bbls_empty) {
      // no need to unlink
      FunBblDel(fun, bbl);
      BblDel(bbl);
    }
  }
}

void FunRemoveUnreachableBbls(Fun fun) {
  std::set<Bbl> reachable;
  std::vector<Bbl> stack;
  stack.push_back(FunBblList::Head(fun));
  while (!stack.empty()) {
    Bbl bbl = stack.back();
    stack.pop_back();
    if (reachable.find(bbl) != reachable.end()) continue;
    reachable.insert(bbl);
    for (Edg edg : BblSuccEdgIter(bbl)) {
      stack.push_back(EdgSuccBbl(edg));
    }
  }

  Bbl bbl = FunBblList::Head(fun);
  while (!FunBblList::IsSentinel(bbl)) {
    const Bbl next = FunBblList::Next(bbl);  // permit deletions while iterating
    if (reachable.find(bbl) == reachable.end()) {
      Edg edg = BblSuccEdgList::Head(bbl);
      while (!BblSuccEdgList::IsSentinel(edg)) {
        const Edg next = BblSuccEdgList::Next(edg);
        EdgUnlink(edg);
        EdgDel(edg);
        edg = next;
      }

      FunBblUnlink(bbl);
      FunBblDel(fun, bbl);
      BblDel(bbl);
    }

    bbl = next;
  }
}

void FunAddUnconditionalBranches(Fun fun) {
  std::vector<Bbl> bbls;
  bool dirty = false;
  for (Bbl bbl : FunBblIter(fun)) {
    bbls.push_back(bbl);
    const Ins last = BblInsList::Tail(bbl);
    if (!BblInsList::IsSentinel(last) && !InsOpcode(last).HasFallthrough())
      continue;
    const Edg edg1 = BblSuccEdgList::Head(bbl);
    const Edg edg2 = BblSuccEdgList::Tail(bbl);
    // If it has a fall-through there is at least one succ edge
    ASSERT(!BblSuccEdgList::IsSentinel(edg1), "");
    ASSERT(!BblSuccEdgList::IsSentinel(edg2), "");
    const Bbl next = FunBblList::Next(bbl);
    ASSERT(!FunBblList::IsSentinel(next), "");
    // Single Edge case:
    if (edg1 == edg2) {
      if (next != EdgSuccBbl(edg1)) {
        BblInsAdd(bbl, InsNewBra(EdgSuccBbl(edg1)));
      }
    } else {
      ASSERT(InsOpcode(last).kind == OPC_KIND::COND_BRA, "");
      ASSERT(BblSuccEdgList::Next(edg1) == edg2, "");
      const Bbl target = Bbl(InsOperand(last, 2));
      const Bbl other =
          EdgSuccBbl(edg1) == target ? EdgSuccBbl(edg2) : EdgSuccBbl(edg1);
      if (other == next) continue;
      if (target == next) {
        InsFlipCondBra(last, target, other);
        continue;
      }
      dirty = true;
      // Add bbl with bra
      const Bbl bbl_bra = BblNew(NewDerivedBblName(Name(bbl), "bra", fun));
      BblInsAdd(bbl_bra, InsNewBra(other));
      FunBblAddBst(fun, bbl_bra);
      // Note we intentionally do NOT call FunBblAppend(fun, bbl_bra)
      // because it would invalidate the iterator and we call FunReplaceBbls()
      // at the end
      bbls.push_back(bbl_bra);
      // add + patch edges
      InsMaybePatchNewSuccessor(last, other, bbl_bra);

      EdgLink(EdgNew(bbl_bra, other));
      // redirect edg going to other
      const Edg edg = EdgSuccBbl(edg1) == other ? edg1 : edg2;

      // redirect   bbl -> other to bbl -> bbl_bra
      EdgUnlink(edg);
      EdgSuccBbl(edg) = bbl_bra;
      EdgLink(edg);
    }
  }
  if (dirty) {
    FunReplaceBbls(fun, bbls);
  }
}

void UnitRemoveUnreachableCode(Unit unit, const std::vector<Fun>& seeds) {
  for (Fun fun : UnitFunIter(unit)) {
    FunClearFlag(fun, FUN_FLAG::REACHABLE);
  }

  std::vector<Fun> reachable = seeds;
  for (Mem mem : UnitMemIter(unit)) {
    for (Data data : MemDataIter(mem)) {
      if (DataTarget(data).kind() == RefKind::FUN) {
        reachable.push_back(Fun(DataTarget(data)));
      }
    }
  }

  // Fixpoint iteration
  while (!reachable.empty()) {
    Fun fun = reachable.back();
    reachable.pop_back();
    if (FunHasFlag(fun, FUN_FLAG::REACHABLE)) continue;
    FunFlags(fun) |= uint8_t(FUN_FLAG::REACHABLE);
    for (Bbl bbl : FunBblIter(fun)) {
      for (Ins ins : BblInsIter(bbl)) {
        OPC opc = InsOPC(ins);
        if (opc != OPC::LEA_FUN && opc != OPC::BSR && opc != OPC::JSR &&
            opc != OPC::SYSCALL)
          continue;
        for (unsigned i = 0; i < InsOpcode(ins).num_operands; ++i) {
          Fun fun = Fun(InsOperand(ins, i));
          if (fun.kind() == RefKind::FUN &&
              !FunHasFlag(fun, FUN_FLAG::REACHABLE)) {
            reachable.push_back(fun);
          }
        }
      }
    }
  }

  std::vector<Fun> unreachable;
  for (Fun fun : UnitFunIter(unit)) {
    if (!FunHasFlag(fun, FUN_FLAG::REACHABLE)) unreachable.push_back(fun);
  }

  for (Fun fun : unreachable) {
    UnitFunUnlink(fun);
    UnitFunDelBst(unit, fun);
  }
}

}  // namespace cwerg::base
