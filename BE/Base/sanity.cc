#include "BE/Base/sanity.h"

#include <set>
#include <vector>

#include "BE/Base/cfg.h"
#include "BE/Base/ir.h"
#include "BE/Base/serialize.h"

namespace cwerg::base {

class FunArgState {
 public:
  FunArgState() = default;

  void HandleProlog(Fun fun) {
    FillPopArgs(FunNumInputTypes(fun), FunInputTypes(fun));
  }

  void HandleIns(Ins ins, Bbl bbl, Fun fun) {
    switch (InsOPC(ins)) {
      case OPC::POPARG: {
        if (num_pop_args_ == 0) {
          CHECK(false, "too many pop args in " << Name(fun));
        }
        DK expected = pop_args_[num_pop_args_ - 1];
        --num_pop_args_;
        DK actual = RegOrConstKind(InsOperand(ins, 0));
        CHECK(expected == actual, "unexpected pop arg type in "
                                      << Name(fun) << ": expected "
                                      << EnumToString(expected) << " got "
                                      << EnumToString(actual));
        break;
      }
      case OPC::PUSHARG: {
        CHECK(num_pop_args_ == 0, "orphan pop args in " << Name(fun));
        DK dk = RegOrConstKind(InsOperand(ins, 0));
        CHECK(num_push_args_ < MAX_PARAMETERS,
              "too many push args in " << Name(fun));
        push_args_[num_push_args_] = dk;
        ++num_push_args_;
        break;
      }
      case OPC::RET:
        CHECK(num_pop_args_ == 0, "orphan pop args " << Name(fun));
        ConsumePushArgs(FunNumOutputTypes(fun), FunOutputTypes(fun),
                        Fun(HandleInvalid), fun);
        break;
      case OPC::JSR:
      case OPC::BSR:
      case OPC::SYSCALL: {
        Fun callee = InsCallee(ins);
        CHECK(num_pop_args_ == 0, "orphan pop args in " << Name(fun));
        ConsumePushArgs(FunNumInputTypes(callee), FunInputTypes(callee), callee,
                        fun);
        FillPopArgs(FunNumOutputTypes(callee), FunOutputTypes(callee));
        if (FunBblList::IsEmpty(callee)) {
          CHECK(FunKind(callee) == FUN_KIND::BUILTIN ||
                    FunKind(callee) == FUN_KIND::SIGNATURE,
                "undefined function " << Name(callee) << " in " << Name(fun));
        }
        break;
      }
      default:
        CHECK(num_pop_args_ == 0, "orphan pop args " << Name(fun));
        CHECK(num_push_args_ == 0, "orphan push args " << Name(fun));
        break;
    }
  }

 private:
  void ConsumePushArgs(int n, DK* dks, Fun callee, Fun caller) {
    if (num_push_args_ != n) {
      if (callee == HandleInvalid) {
        CHECK(false, "In " << Name(caller) << "epilog: expected " << n
                           << " push args, got " << num_push_args_);
      } else {
        CHECK(false, "In " << Name(caller) << " calling " << Name(callee)
                           << ": expected " << n << " push args, got "
                           << num_push_args_);
      }
    }
    for (int i = 0; i < n; i++) {
      if (push_args_[i] != dks[n - 1 - i]) {
        if (callee == HandleInvalid) {
          CHECK(false, "In caller " << Name(caller) << " epilog: expected push arg "
                                    << i << " to be "
                                    << EnumToString(dks[n - 1 - i]) << " got "
                                    << EnumToString(push_args_[i]));
        } else {
          CHECK(false, "In caller " << Name(caller) << " calling "
                                    << Name(callee) << ": expected push arg "
                                    << i << " to be "
                                    << EnumToString(dks[n - 1 - i]) << " got "
                                    << EnumToString(push_args_[i]));
        }
      }
    }
    num_push_args_ = 0;
  }

  void FillPopArgs(int n, DK* dks) {
    for (int i = 0; i < n; i++) {
      DK dk = dks[n - i - 1];
      pop_args_[i] = dk;
    }
    num_pop_args_ = n;
  }

  void FillPushArgs(int n, DK* dks) {
    for (int i = 0; i < n; i++) {
      DK dk = dks[n - i - 1];
      push_args_[i] = dk;
    }
    num_push_args_ = n;
  }

  DK pop_args_[MAX_PARAMETERS];
  DK push_args_[MAX_PARAMETERS];
  int num_pop_args_ = 0;
  int num_push_args_ = 0;
};

void BblCheck(Bbl bbl, Fun fun, FunArgState* state, bool check_push_pop) {
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
    if (check_push_pop) {
      state->HandleIns(ins, bbl, fun);
    }
    ++count;
  }
}

void FunCheck(Fun fun, bool check_cfg, bool check_push_pop,
              bool check_fallthroughs) {
  FunArgState state;
  state.HandleProlog(fun);

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
            "bad 1 " << Name(pred) << " -> " << Name(succ) << " " << Name(fun));
      CHECK(bbls.find(succ) != bbls.end(),
            "bad 2 " << Name(pred) << " -> " << Name(succ) << " " << Name(fun));
      CHECK(pred == bbl, "bad 3 " << Name(bbl) << ": " << Name(pred) << " -> "
                                  << Name(succ) << " " << Name(fun));
    }

    BblCheck(bbl, fun, &state, check_push_pop);
  }
}

}  // namespace cwerg::base
