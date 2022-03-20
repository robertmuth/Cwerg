// (c) Robert Muth - see LICENSE for more info

#include "Util/stripe.h"
#include "Util/assert.h"

#include <iomanip>
namespace cwerg {

StripeGroup* StripeGroup::root = nullptr;

Handle StripeGroup::New() {
  ASSERT(!first_free_.isnull(),
         "out of item in " << name_ << ". Rerun with larger multiplier");
  ++num_news_;
  Handle out = first_free_;
  StripeBase* sb = stripes_[0];
  first_free_ = *static_cast<Handle*>(sb->element(out.index()));
  return out;
}

void StripeGroup::Del(Handle ref) {
  ++num_dels_;
  StripeBase* sb = stripes_[0];
  *static_cast<Handle*>(sb->element(ref.index())) = first_free_;
  first_free_ = ref;
}

uint32_t StripeGroup::NumFree() const {
  StripeBase* sb = stripes_[0];
  int n = 0;
  for (Handle r = first_free_; !r.isnull();
       r = *static_cast<Handle*>(sb->element(r.index()))) {
    ++n;
  }
  return n;
}

uintptr_t Align(uintptr_t x, uint32_t alignment) {
  return (x + alignment - 1) / alignment * alignment;
}

char* Align(char* x, uint32_t alignment) {
  return (char*)Align(uintptr_t(x), alignment);
}

void StripeGroup::DumpAllGroups(std::ostream& os) {
  for (StripeGroup* sg = StripeGroup::root; sg != nullptr; sg = sg->next) {
    uint32_t sum_element_sizes = 0;
    for (int i = 0; sg->stripes_[i] != nullptr; ++i) {
      sum_element_sizes += sg->stripes_[i]->element_size;
    }
    uint32_t allocated = sg->max_instances_ - 1;
    uint32_t used = allocated - sg->NumFree();
    uint32_t percent = used * 100 / (sg->max_instances_ - 1);
    size_t size_mb = sum_element_sizes * sg->max_instances_ / (1024 * 1024);
    os << std::setw(12) << std::left << sg->name_ << std::right
       << "  mem: " << std::setw(5) << size_mb << " MiB "
       << "in-use: " << std::setw(5) << used << "/" << std::setw(5) << allocated
       << " " << percent << "%\n";

    for (int i = 0; sg->stripes_[i] != nullptr; ++i) {
      const StripeBase& base = *sg->stripes_[i];
      size_t mem_size = base.element_size * sg->max_instances_;
      os << std::setw(12) << std::left << base.name << std::right << " "
         << " mem: " << std::setw(5) << mem_size / (1024 * 1024) << " MiB "
         << "item-size: " << std::setw(2) << base.element_size << " "
         << std::hex << (void*)base.base << std::dec << "\n";
    }
    os << "\n";
   }
}

void StripeGroup::AllocateAllStripes(uint32_t multiplier) {
  const size_t kStripeAlignment = 64 * 1024;
  for (StripeGroup* sg = StripeGroup::root; sg != nullptr; sg = sg->next) {
    sg->max_instances_ *= multiplier;
  }

  size_t mem_size = 0;
  for (StripeGroup* sg = StripeGroup::root; sg != nullptr; sg = sg->next) {
    for (int i = 0; sg->stripes_[i] != nullptr; ++i) {
      const StripeBase& base = *sg->stripes_[i];
      mem_size += base.element_size * sg->max_instances_;
      mem_size = Align(mem_size, kStripeAlignment);
    }
  }

  char* data = Align(new char[mem_size + kStripeAlignment], kStripeAlignment);

  for (StripeGroup* sg = StripeGroup::root; sg != nullptr; sg = sg->next) {
    for (int i = 0; sg->stripes_[i] != nullptr; ++i) {
      StripeBase& base = *sg->stripes_[i];
      ASSERT(base.base == nullptr, "");
      base.base = data;
      data += base.element_size * sg->max_instances_;
      data = Align(data, kStripeAlignment);
    }
  }

  // Put everything except the first element into the free list in order.
  for (StripeGroup* sg = StripeGroup::root; sg != nullptr; sg = sg->next) {
    StripeBase* sb = sg->stripes_[0];
    // we do not use the zeroest element!
    sg->first_free_ = Handle(1, RefKind::FREE);
    for (unsigned i = 1; i < sg->max_instances_ - 1; i++) {
      *static_cast<Handle*>(sb->element(i)) = Handle(i + 1, RefKind::FREE);
    }
    *static_cast<Handle*>(sb->element(sg->max_instances_ - 1)) =
        Handle(0, RefKind::FREE);
  }
}

void InitStripes(uint32_t multiplier) {
  StripeGroup::AllocateAllStripes(multiplier);
  // StripeGroup::DumpAllGroups(std::cout);
}

}  // namespace cwerg
