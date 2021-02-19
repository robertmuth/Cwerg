#pragma once

// =================================================================================
// Double Link List Templates
// Note we are using the container reference as sentinel for the end/beginning
// of the list
// =================================================================================

namespace cwerg {

template <typename LIST>
void ListInsertBetween(typename LIST::CONT container,
                       typename LIST::ITEM prev,
                       typename LIST::ITEM item,
                       typename LIST::ITEM next) {
  LIST::Next(item) = next;
  LIST::Prev(item) = prev;

  if (LIST::IsSentinel(next)) {
    LIST::Tail(container) = item;
  } else {
    LIST::Prev(next) = item;
  }

  if (LIST::IsSentinel(prev)) {
    LIST::Head(container) = item;
  } else {
    LIST::Next(prev) = item;
  }
}

template <typename LIST>
void ListInsertBefore(typename LIST::CONT container,
                      typename LIST::ITEM before,
                      typename LIST::ITEM item) {
  ListInsertBetween<LIST>(
      container,
      before == container ? LIST::Tail(container) : LIST::Prev(before), item,
      before);
}

template <typename LIST>
void ListAppend(typename LIST::CONT container, typename LIST::ITEM item) {
  ListInsertBetween<LIST>(container, LIST::Tail(container), item,
                          LIST::MakeSentinel(container));
}

template <typename LIST>
void ListInsertAfter(typename LIST::CONT container,
                     typename LIST::ITEM after,
                     typename LIST::ITEM item) {
  ListInsertBetween<LIST>(
      container, after, item,
      after == container ? LIST::Head(container) : LIST::Next(after));
}

template <typename LIST>
void ListPrepend(typename LIST::CONT container, typename LIST::ITEM item) {
  ListInsertBetween<LIST>(container, LIST::MakeSentinel(container), item,
                          LIST::Head(container));
}

template <typename LIST>
void ListUnlink(typename LIST::ITEM item) {
  const typename LIST::ITEM before = LIST::Prev(item);
  const typename LIST::ITEM after = LIST::Next(item);
  if (LIST::IsSentinel(before)) {
    LIST::Head(typename  LIST::CONT(before)) = after;
  } else {
    LIST::Next(before) = after;
  }
  if (LIST::IsSentinel(after)) {
    LIST::Tail(typename LIST::CONT(after)) = before;
  } else {
    LIST::Prev(after) = before;
  }
  LIST::Prev(item) =  typename  LIST::ITEM(0);
  LIST::Next(item) =  typename  LIST::ITEM(0);
}

// List Iterator (compatible with range loops)
template <typename LIST>
class ListIter {
 public:
  ListIter(typename LIST::ITEM begin, typename LIST::ITEM end)
      : begin_(begin), end_(end) {}

  ListIter(typename LIST::CONT cont)
      : ListIter(LIST::Head(cont), LIST::MakeSentinel(cont)) {}

  class it {
   public:
    explicit it(typename LIST::ITEM obj) : obj_(obj) {}
    it operator++() {
      obj_ = LIST::Next(obj_);
      return *this;
    }
    bool operator!=(const it& other) const { return obj_ != other.obj_; }
    typename LIST::ITEM operator*() const { return obj_; }

   private:
    typename LIST::ITEM obj_;
  };
  it begin() const { return it(begin_); }
  it end() const { return it(end_); }

 private:
  const typename LIST::ITEM begin_;
  const typename LIST::ITEM end_;
};

// List Iterator (compatible with range loops)
template <typename LIST>
class ListIterReverse {
 public:
  ListIterReverse(typename LIST::ITEM begin, typename LIST::ITEM end)
      : begin_(begin), end_(end) {}

  ListIterReverse(typename LIST::CONT cont)
      : ListIterReverse(LIST::Tail(cont), LIST::MakeSentinel(cont)) {}

  class it {
   public:
    explicit it(typename LIST::ITEM obj) : obj_(obj) {}
    it operator++() {
      obj_ = LIST::Prev(obj_);
      return *this;
    }
    bool operator!=(const it& other) const { return obj_ != other.obj_; }
    typename LIST::ITEM operator*() const { return obj_; }

   private:
    typename LIST::ITEM obj_;
  };
  it begin() const { return it(begin_); }
  it end() const { return it(end_); }

 private:
  const typename LIST::ITEM begin_;
  const typename LIST::ITEM end_;
};

}  // namespace cwerg
