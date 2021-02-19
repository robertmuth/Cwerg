#include "Util/assert.h"
#include "Util/bst.h"
#include "Util/list.h"
#include "Util/parse.h"
#include "Util/stripe.h"

#include <iostream>
#include <vector>

namespace cwerg {

struct Bbl : public Handle {
  Bbl(uint32_t index = 0) : Handle(index, RefKind::BBL) {}
  explicit Bbl(Handle ref) : Handle(ref.value) {}
};

struct Fun : public Handle {
  Fun(uint32_t index = 0) : Handle(index, RefKind::FUN) {}
  explicit Fun(Handle ref) : Handle(ref.value) {}
};

struct BblList {
  Bbl prev;
  Bbl next;
};

struct BblBst {
  int name;
  Bbl left;
  Bbl right;
  Bbl parent;
  // uint32_t size;
};

struct FunCore {
  Bbl bbl_head;
  Bbl bbl_tail;
  Bbl bbl_syms;
};

struct Stripe<BblList, Bbl> gBblList("BblList");
struct Stripe<BblBst, Bbl> gBblBst("BblBst");
StripeBase* const gAllStripesBbl[] = {&gBblList, &gBblBst, nullptr};
struct StripeGroup gStripeGroupBbl("BBL", gAllStripesBbl, 16 * 1024);

struct Stripe<FunCore, Fun> gFunCore("FunCore");
StripeBase* const gAllStripesFun[] = {&gFunCore, nullptr};
struct StripeGroup gStripeGroupFun("FUN", gAllStripesFun, 16 * 1024);

Bbl BblNew() { return Bbl(gStripeGroupBbl.New().index()); }

Fun FunNew() { return Fun(gStripeGroupFun.New().index()); }

int& Name(Bbl bbl) { return gBblBst[bbl].name; }

struct FunBblList {
  using ITEM = Bbl;
  using CONT = Fun;
  static bool IsSentinel(Bbl bbl) { return bbl.kind() == RefKind::FUN; }
  static Bbl MakeSentinel(Fun fun) { return Bbl(fun); }
  static Bbl& Next(Bbl bbl) { return gBblList[bbl].next; }
  static Bbl& Prev(Bbl bbl) { return gBblList[bbl].prev; }
  static Bbl& Tail(Fun fun) { return gFunCore[fun].bbl_tail; }
  static Bbl& Head(Fun fun) { return gFunCore[fun].bbl_head; }
};

struct FunBblBst {
  using ITEM = Bbl;
  using CONT = Fun;
  using KEY = int;

  static KEY& Key(Bbl bbl) { return gBblBst[bbl].name; }
  static Bbl& Left(Bbl bbl) { return gBblBst[bbl].left; }
  static Bbl& Right(Bbl bbl) { return gBblBst[bbl].right; }
  static Bbl& Parent(Bbl bbl) { return gBblBst[bbl].parent; }
  static int Cmp(unsigned a, unsigned b) { return a - b; }
  static Bbl& Root(Fun fun) { return gFunCore[fun].bbl_syms; }
};

std::ostream& operator<<(std::ostream& os, const Bbl& bbl) {
  os << Name(bbl) << " [" << bbl.index() << "] {" << gBblBst[bbl].parent.index()
     << "}";
  return os;
}

template <typename BST>
void BstDump(typename BST::ITEM item, int level = 0) {
  if (item.isnull()) return;
  const typename BST::ITEM left = BST::Left(item);
  const typename BST::ITEM right = BST::Right(item);
  if (!left.isnull()) {
    if (BST::Parent(left) != item) {
      std::cout << "bad parent  for: " << left << " got: " << item << "\n";
    }
    ASSERT(BST::Parent(left) == item, "");
    BstDump(left, level + 1);
  }
  std::cout << item << " " << level << "\n";
  if (!right.isnull()) {
    ASSERT(BST::Parent(right) == item, "");
    BstDump(right, level + 1);
  }
}

void LinkedListTest(const std::vector<int>& names) {
  Fun fun = FunNew();
  gFunCore[fun].bbl_head = Bbl(fun);
  gFunCore[fun].bbl_tail = Bbl(fun);
  for (unsigned i = 0; i < names.size(); ++i) {
    Bbl bbl = BblNew();
    Name(bbl) = names[i];
    ListAppend<FunBblList>(fun, bbl);
  }

  unsigned count = 0;
  for (Bbl bbl : ListIter<FunBblList>(fun)) {
    ASSERT(names[count] == Name(bbl), "name mismatch " << count);
    count++;
  }
  ASSERT(count == names.size(), "");

  count = 0;
  for (Bbl bbl : ListIterReverse<FunBblList>(fun)) {
    unsigned index = names.size() - 1 - count++;
    ASSERT(names[index] == Name(bbl), "name mismatch " << count);
  }

  const Bbl first = gFunCore[fun].bbl_head;
  const Bbl next = gBblList[first].next;
  const Bbl last = gFunCore[fun].bbl_tail;
  const Bbl prev = gBblList[last].prev;

  ListUnlink<FunBblList>(first);
  ASSERT(gFunCore[fun].bbl_head == next, "");
  ListUnlink<FunBblList>(last);
  ASSERT(gFunCore[fun].bbl_tail == prev, "");
}

void SingleTableTest(const std::vector<int>& names) {
  Fun fun = FunNew();

  // cout << "Fun " << fun.index() << "\n";
  FunBblBst::Root(fun) = Bbl(0);
  Bbl bbl;

  bbl = FunBblBst::Root(fun);
  ASSERT(bbl.isnull(), "");

  bbl = BstFind<FunBblBst>(fun, -1);
  ASSERT(bbl.isnull(), "");
  for (unsigned i = 0; i < names.size(); ++i) {
    bbl = BblNew();
    Name(bbl) = names[i];
    //  cout << "inserting " << bbl << "\n";
    BstAdd<FunBblBst>(fun, bbl);
  }

  // cout << "Tree after insertion\n";
  // BstDump(BstRoot<Fun, Bbl>(fun));
  Bbl last(0);
  for (const Bbl bbl : BstIter<FunBblBst>(fun)) {
    if (!last.isnull()) {
      ASSERT(Name(last) < Name(bbl), "");
    }
    last = bbl;
  }

  bbl = FunBblBst::Root(fun);
  ASSERT(!bbl.isnull(), "");

  for (unsigned i = 0; i < names.size(); ++i) {
    bbl = BstFind<FunBblBst>(fun, names[i]);
    ASSERT(Name(bbl) == names[i], "");
  }

  bbl = BstFind<FunBblBst>(fun, -1);
  ASSERT(bbl.isnull(), "");

  for (unsigned i = 0; i < names.size(); ++i) {
    bbl = BstFind<FunBblBst>(fun, names[i]);
    ASSERT(Name(bbl) == names[i], "");
    BstDel<FunBblBst>(fun, bbl);
    // BstDump<Bbl>(BstRoot<Fun, Bbl>(fun));
  }

  bbl = FunBblBst::Root(fun);
  ASSERT(bbl.isnull(), "");
}

std::vector<int> Flip(const std::vector<int>& names) {
  std::vector<int> out;
  for (int i = names.size() - 1; i >= 0; --i) out.push_back(names[i]);
  return out;
}

std::vector<int> Shuffle(const std::vector<int>& names, uint32_t prime) {
  std::vector<int> out;
  uint32_t index = prime;
  for (unsigned i = 0; i < names.size(); ++i) {
    index = (index + prime) % names.size();
    out.push_back(names[index]);
  }
  return out;
}

void TestToHexStr() {
  char buffer[20];
  ASSERT("#U0" == PosToHexString(0, buffer), "unexpected " << buffer);
  ASSERT("#Uff00ff00" == PosToHexString(0xff00ff00, buffer),
         "unexpected " << buffer);
  ASSERT("#Nc" == NegToHexString(12, buffer), "unexpected " << buffer);
  ASSERT("#F0" == FltToHexString(0.0, buffer), "unexpected " << buffer);
  ASSERT("#F4059000000000000" == FltToHexString(100.0, buffer),
         "unexpected " << buffer);
}

}  // namespace cwerg

int main() {
  cwerg::InitStripes(1);
  std::vector<int> names;
  for (int i = 0; i < 1000; i++) {
    names.push_back(i);
  }

  cwerg::LinkedListTest(names);

  cwerg::SingleTableTest(names);
  cwerg::SingleTableTest(cwerg::Flip(names));
  cwerg::SingleTableTest(cwerg::Shuffle(names, 65521));
  cwerg::SingleTableTest(cwerg::Shuffle(names, 65537));

  cwerg::TestToHexStr();

  return 0;
}
