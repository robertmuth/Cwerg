#include "Base/sanity.h"
#include "Base/serialize.h"

#include <set>

namespace cwerg::base {

void BblCheck(Bbl bbl, Fun fun) {
  uint32_t count = 0;
  for (Ins ins : BblInsIter(bbl)) {
    Ins prev = BblInsList::Prev(ins);
    Ins next = BblInsList::Next(ins);

    if (BblInsList::IsSentinel(prev)) {
      ASSERT(prev == bbl, "");
      ASSERT(BblInsList::Head(bbl) == ins, "");
    } else {
      ASSERT(BblInsList::Next(prev) == ins, "");
    }

    if (BblInsList::IsSentinel(next)) {
      ASSERT(next == bbl, "");
      if (BblInsList::Tail(bbl) != ins) {
        BblRenderToAsm(bbl, fun, &std::cout);
        ASSERT(false, "bbl corruption in " << Name(fun) << " at pos " << count);
      }
    } else {
      if (BblInsList::Prev(next) != ins) {
        BblRenderToAsm(bbl, fun, &std::cout);
        ASSERT(false, "bbl corruption in " << Name(fun) << " at pos " << count);
      }
    }
    ++count;
  }
}

void FunCheck(Fun fun) {
  std::set<Bbl> bbls;
  for (Bbl bbl : FunBblIter(fun)) {
    bbls.insert(bbl);
  }

  for (Bbl bbl : FunBblIter(fun)) {
    Bbl prev = FunBblList::Prev(bbl);
    Bbl next = FunBblList::Next(bbl);

    if (FunBblList::IsSentinel(prev)) {
      ASSERT(prev == fun, "");
      ASSERT(FunBblList::Head(fun) == bbl, "");
    } else {
      ASSERT(FunBblList::Next(prev) == bbl, "");
    }

    if (FunBblList::IsSentinel(next)) {
      ASSERT(next == fun, "");
      ASSERT(FunBblList::Tail(fun) == bbl, "");
    } else {
      ASSERT(FunBblList::Prev(next) == bbl, "");
    }

    // cfg checks
    for (Edg edg : BblPredEdgIter(bbl)) {
      Bbl pred = EdgPredBbl(edg);
      Bbl succ = EdgSuccBbl(edg);
      ASSERT(bbls.find(pred) != bbls.end(),
             "[" << Name(fun) << "] bad " << Name(pred) << " -> " << Name(succ));
      ASSERT(bbls.find(succ) != bbls.end(),
             "bad " << Name(pred) << " -> " << Name(succ));
      ASSERT(succ == bbl,
             "bad " << Name(bbl) << ": " << Name(pred) << " -> " << Name(succ));
    }

    for (Edg edg : BblSuccEdgIter(bbl)) {
      Bbl pred = EdgPredBbl(edg);
      Bbl succ = EdgSuccBbl(edg);
      ASSERT(bbls.find(pred) != bbls.end(),
             "bad " << Name(pred) << " -> " << Name(succ));
      ASSERT(bbls.find(succ) != bbls.end(),
             "bad " << Name(pred) << " -> " << Name(succ));
      ASSERT(pred == bbl,
             "bad " << Name(bbl) << ": " << Name(pred) << " -> " << Name(succ));
    }

    BblCheck(bbl, fun);
  }
}

void UnitCheck(Unit unit) {
  for (Fun fun : UnitFunIter(unit)) {
    Fun prev = UnitFunList::Prev(fun);
    Fun next = UnitFunList::Next(fun);

    if (UnitFunList::IsSentinel(prev)) {
      ASSERT(prev == unit, "");
      ASSERT(UnitFunList::Head(unit) == fun, "");
    } else {
      ASSERT(UnitFunList::Next(prev) == fun, "");
    }

    if (UnitFunList::IsSentinel(next)) {
      ASSERT(next == unit, "");
      ASSERT(UnitFunList::Tail(unit) == fun, "");
    } else {
      ASSERT(UnitFunList::Prev(next) == fun, "");
    }

    FunCheck(fun);
  }
}

}  // namespace cwerg::base
