#pragma once
// (c) Robert Muth - see LICENSE for more info

// =================================================================================
// BST Templates (which ia really a Treap)
// cf.: https://medium.com/carpanese/a-visual-introduction-to-treap-data-structure-part-1-6196d6cc12ee
// FAQ:
// Q: Why re-invent the wheel and not use STL?
// A: STL does not work for our data structures. We also try to not use STL for performance critical code.
// Q: Why a treap and not a tree?
// A: We use the priority of the heap to add randomization and avoid degenerate trees. 
// =================================================================================

#include "Util/assert.h"
#include <iostream>
#include <cstdint>

namespace cwerg {
extern uint32_t bst_stats_num_finds;
extern uint32_t bst_stats_num_find_steps;

extern uint32_t bst_stats_num_adds;
extern uint32_t bst_stats_num_add_steps;

extern uint32_t bst_stats_left_rotations;
extern uint32_t bst_stats_right_rotations;

void DumpBstStates(std::ostream& os);


template <typename BST>
typename BST::ITEM BstFind(typename BST::CONT container,
                           typename BST::KEY the_key) {
  ++bst_stats_num_finds;
  typename BST::ITEM root = BST::Root(container);
  while (true) {
    ++bst_stats_num_find_steps;
    if (root.isnull()) return typename BST::ITEM(0);
    const int cmp = BST::Cmp(the_key, BST::Key(root));
    if (cmp == 0) return root;
    if (cmp < 0) {
      root = BST::Left(root);
    } else {
      root = BST::Right(root);
    }
  }
}

template <typename BST>
void RotateLeft(typename BST::CONT container, typename BST::ITEM root) {
  ++bst_stats_left_rotations;
  typename BST::ITEM p = BST::Parent(root);
  typename BST::ITEM r = BST::Right(root);  // must exist
  typename BST::ITEM x = BST::Left(r);      // may be null
  BST::Left(r) = root;
  BST::Parent(root) = r;

  BST::Right(root) = x;
  if (!x.isnull()) BST::Parent(x) = root;

  BST::Parent(r) = p;
  if (p.isnull()) {
    BST::Root(container) = r;
  } else if (BST::Left(p) == root) {
    BST::Left(p) = r;
  } else {
    BST::Right(p) = r;
  }
}

template <typename BST>
void RotateRight(typename BST::CONT container, typename BST::ITEM root) {
  ++bst_stats_right_rotations;
  typename BST::ITEM p = BST::Parent(root);
  typename BST::ITEM l = BST::Left(root);  // must exist
  typename BST::ITEM x = BST::Right(l);    // may be null
  BST::Right(l) = root;
  BST::Parent(root) = l;

  BST::Left(root) = x;
  if (!x.isnull()) BST::Parent(x) = root;

  BST::Parent(l) = p;
  if (p.isnull()) {
    BST::Root(container) = l;
  } else if (BST::Left(p) == root) {
    BST::Left(p) = l;
  } else {
    BST::Right(p) = l;
  }
}

template<typename Handle>
int priority(Handle h) {
  return h.value % 997;
}


template <typename BST>
bool BstAdd(typename BST::CONT container, typename BST::ITEM item) {
  ++bst_stats_num_adds;
  typename BST::ITEM node = BST::Root(container);

  BST::Left(item) = typename BST::ITEM(0);
  BST::Right(item) = typename BST::ITEM(0);
  // BstSize(item) = 1;

  if (node.isnull()) {
    BST::Root(container) = item;
    BST::Parent(item) = typename BST::ITEM(0);
    return true;
  }

  while (true) {
    ++bst_stats_num_add_steps;
    const int cmp = BST::Cmp(BST::Key(item), BST::Key(node));
    if (cmp == 0) {
      return false;  // duplicate key
    } else if (cmp < 0) {
      if (BST::Left(node).isnull()) {
        BST::Left(node) = item;
        BST::Parent(item) = node;
        break;
      }
      node = BST::Left(node);
    } else {
      if (BST::Right(node).isnull()) {
        BST::Right(node) = item;
        BST::Parent(item) = node;
        break;
      }
      node = BST::Right(node);
    }
  }
#if 1
  node = item;
  while (!node.isnull()) {
    typename BST::ITEM p = BST::Parent(node);
    if (p.isnull()) break;
    if (BST::Left(p) == node) {
      // if (rand() & 1) {
      if (priority(p) < priority(node)) {
        RotateRight<BST>(container, p);  // node  and p were swapped
        node = BST::Parent(node);
        continue;
      }
    } else {
      //if (rand() & 1) {
      if (priority(p) < priority(node)) {
        RotateLeft<BST>(container, p);  // node  and p were swapped
        node = BST::Parent(node);
        continue;
      }
    }
    node = p;
  }
#endif
  return true;
}

template <typename BST>
typename BST::ITEM BstSmallest(typename BST::ITEM root) {
  ASSERT(!root.isnull(), "cannot call with null node");
  while (!BST::Left(root).isnull()) root = BST::Left(root);
  return root;
}

template <typename BST>
void BstDel(typename BST::CONT container, typename BST::ITEM item) {
  const typename BST::ITEM parent = BST::Parent(item);
  const typename BST::ITEM left = BST::Left(item);
  typename BST::ITEM right = BST::Right(item);
  typename BST::ITEM new_child;
  if (right.isnull() || left.isnull()) {
    new_child = left.isnull() ? right : left;
    if (!new_child.isnull()) BST::Parent(new_child) = parent;
  } else {
    // Replace item with next_smallest in the tree
    new_child = BstSmallest<BST>(right);
    ASSERT(BST::Left(new_child).isnull(), "expected left most node");

    // unlink it (which is easy since it does not have a left branch)
    BstDel<BST>(container, new_child);
    right = BST::Right(item);  // the removal may change `right`
    ASSERT(BST::Left(item) == left, "unexpected left");
    ASSERT(BST::Parent(item) == parent, "unexpected right");

    BST::Right(new_child) = right;
    BST::Left(new_child) = left;
    BST::Parent(new_child) = parent;
    BST::Parent(right) = new_child;
    BST::Parent(left) = new_child;
  }

  ASSERT(BST::Parent(item) == parent, "unexpected parent");
  if (parent.isnull()) {
    // cout << "fixup root\n";
    BST::Root(container) = new_child;
  } else {
    // cout << "fixup parent\n";
    if (BST::Left(parent) == item) {
      BST::Left(parent) = new_child;
    } else {
      ASSERT(BST::Right(parent) == item, "unexpected parent");
      BST::Right(parent) = new_child;
    }
  }
}

// Tree Iterator (compatible with range loops)
template <typename BST>
class BstIter {
 public:
  explicit BstIter(typename BST::ITEM root) : root_(root) {}
  explicit BstIter(typename BST::CONT cont) : root_(BST::Root(cont)) {}

  class it {
   public:
    explicit it(typename BST::ITEM obj) : obj_(obj) {}
    it operator++() {
      const typename BST::ITEM right = BST::Right(obj_);
      if (!right.isnull()) {
        obj_ = BstSmallest<BST>(right);
      } else {
        while (true) {
          const typename BST::ITEM last = obj_;
          obj_ = BST::Parent(last);
          if (obj_.isnull() || BST::Left(obj_) == last) {
            break;
          }
        }
      }
      return *this;
    }

    bool operator!=(const it& other) const { return obj_ != other.obj_; }
    typename BST::ITEM operator*() const { return obj_; }

   private:
    typename BST::ITEM obj_;
  };

  it begin() const {
    if (root_.isnull()) return it(typename BST::ITEM(0));
    return it(BstSmallest<BST>(root_));
  }

  it end() const { return it(typename BST::ITEM(0)); }

 private:
  const typename BST::ITEM root_;
};

}  // namespace cwerg
