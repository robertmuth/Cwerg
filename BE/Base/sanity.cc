#include "BE/Base/sanity.h"

#include <set>

#include "BE/Base/cfg.h"
#include "BE/Base/serialize.h"

namespace cwerg::base {

void BblCheck(Bbl bbl, Fun fun) {
  uint32_t count = 0;
  for (Ins ins : BblInsIter(bbl)) {
    Ins prev = BblInsList::Prev(ins);
    Ins next = BblInsList::Next(ins);

    if (BblInsList::IsSentinel(prev)) {
      CHECK(prev == bbl, "");
      CHECK(BblInsList::Head(bbl) == ins, "");
    } else {
      CHECK(BblInsList::Next(prev) == ins, "");
    }

    if (BblInsList::IsSentinel(next)) {
      CHECK(next == bbl, "");
      if (BblInsList::Tail(bbl) != ins) {
        BblRenderToAsm(bbl, fun, &std::cout);
        CHECK(false, "bbl corruption in " << Name(fun) << " at pos " << count);
      }
    } else {
      if (BblInsList::Prev(next) != ins) {
        BblRenderToAsm(bbl, fun, &std::cout);
        CHECK(false, "bbl corruption in " << Name(fun) << " at pos " << count);
      }
    }

    if (InsOpcode(ins).IsCall()) {
      Fun callee = InsCallee(ins);
      if (FunBblList::IsEmpty(callee)) {
        CHECK(FunKind(callee) == FUN_KIND::BUILTIN ||
                  FunKind(callee) == FUN_KIND::SIGNATURE,
              "undefined function " << Name(callee) << " in " << Name(fun));
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

  const Bbl head = FunBblList::Head(fun);
  const Bbl tail = FunBblList::Tail(fun);

  if (FunBblList::IsSentinel(head)) {
    CHECK(FunBblList::IsSentinel(head), "");
    CHECK(head == tail, "");
  } else {
    CHECK(FunBblList::IsSentinel(FunBblList::Prev(head)), "");
    CHECK(FunBblList::IsSentinel(FunBblList::Next(tail)), "");
  }

  for (Bbl bbl : FunBblIter(fun)) {
    Bbl prev = FunBblList::Prev(bbl);
    Bbl next = FunBblList::Next(bbl);

    if (FunBblList::IsSentinel(prev)) {
      CHECK(prev == fun, "");
      CHECK(FunBblList::Head(fun) == bbl, "");
    } else {
      CHECK(FunBblList::Next(prev) == bbl, "");
    }

    if (FunBblList::IsSentinel(next)) {
      CHECK(next == fun, "");
      CHECK(FunBblList::Tail(fun) == bbl,
            " FUN BBL list corrupted " << Name(fun));
    } else {
      CHECK(FunBblList::Prev(next) == bbl,
            "FUN BBL list corrupted " << Name(fun));
    }

    // cfg checks
    for (Edg edg : BblPredEdgIter(bbl)) {
      Bbl pred = EdgPredBbl(edg);
      Bbl succ = EdgSuccBbl(edg);
      CHECK(bbls.find(pred) != bbls.end(),
            "[" << Name(fun) << "] bad " << Name(pred) << " -> " << Name(succ));
      CHECK(bbls.find(succ) != bbls.end(),
            "bad " << Name(pred) << " -> " << Name(succ));
      CHECK(succ == bbl,
            "bad " << Name(bbl) << ": " << Name(pred) << " -> " << Name(succ));
    }

    for (Edg edg : BblSuccEdgIter(bbl)) {
      Bbl pred = EdgPredBbl(edg);
      Bbl succ = EdgSuccBbl(edg);
      CHECK(bbls.find(pred) != bbls.end(),
            "bad " << Name(pred) << " -> " << Name(succ));
      CHECK(bbls.find(succ) != bbls.end(),
            "bad " << Name(pred) << " -> " << Name(succ));
      CHECK(pred == bbl,
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
      CHECK(prev == unit, "");
      CHECK(UnitFunList::Head(unit) == fun, "");
    } else {
      CHECK(UnitFunList::Next(prev) == fun, "");
    }

    if (UnitFunList::IsSentinel(next)) {
      CHECK(next == unit, "");
      CHECK(UnitFunList::Tail(unit) == fun, "");
    } else {
      CHECK(UnitFunList::Prev(next) == fun, "");
    }

    FunCheck(fun);
  }
}

}  // namespace cwerg::base
