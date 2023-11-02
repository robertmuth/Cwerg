#pragma once
// (c) Robert Muth - see LICENSE for more info

#include "Util/handle.h"
#include <iostream>

/*
We employs a number of unconventional mechanism to improve translation
performance. These mechanism are not hidden behind an API and need some time to
getting used to.

Information pertaining to a specific entity, say a Basic Block (Bbl),
is not stored in one massive struct but is broken up into several smaller
entities say one for core information and one for liveness information, etc.
Each of these are stored in an array called a Stripe.

The collection of all `Stripes` pertaining to an entity is called
a `StripeGroup`.
This resembles a `array of structs` approach
(https://en.wikipedia.org/wiki/AoS_and_SoA) which greatly improves
locality.

Since the information belonging to an entity is spread (`striped`) across
multiple memory regions entities are not identified by pointers but
`Handles` which are essentially indices into the `Stripes`.

Since `Handles` are 32 bit they also save memory on 64 bit systems
where ordinary pointers would consume twice the space.

The first stripe in a stripe group is used to manage the free list and
must have the size of two handles (2 * 4 bytes).

To make accessing `Stripes` less syntactically obtrusive all `Stripes`
are global objects.

STL containers are still used in places where performance does not matter
much but we generally try to avoid them.

*/

namespace cwerg {

// A Stripe is an array indexed by a matching Handle
struct StripeBase {
  StripeBase(uint32_t a_element_size, const char* a_name)
      : element_size(a_element_size), name(a_name) {}

  char* base = nullptr;
  const uint32_t element_size;
  const char* const name;

  void* element(int index) const { return base + index * element_size; }
};

// A StripeGroup is a container for all the Stripes of the same Handle type
// It is responsible for the New'ing/Del'ing of the Handles and the
// allocation of the backing store in the stripes.
struct StripeGroup {
  StripeGroup(const char* name, StripeBase* const* stripes,
              uint32_t max_allocated)
      : max_instances_(max_allocated), name_(name),
        stripes_(stripes), next(root) {
    root = this;
  }
  // Get next free index for this group.
  // Will call Reserve if necessary.
  Handle New();

  void Del(Handle ref);


  uint32_t NumFree() const;  // slow: iterates through the entire free-list
  uint32_t MaxInstances() const { return max_instances_; }

  static void AllocateAllStripes(uint32_t multiplier);

  // vec must have >=  MaxInstances() bits. A bit will be set if
  // the instance with the corresponding number is on the free list.
  void SetBitVecOfFreeInstances(uint8_t* vec) const;
  
  static void DumpAllGroups(std::ostream& os);

 private:
  uint32_t max_instances_;
  Handle first_free_ = Handle(0, RefKind::FREE);
  uint32_t num_dels_ = 0;
  uint32_t num_news_ = 0;
  const char* const name_;

  // Increase the size of all stripes to n elements
  void Reserve(int32_t n);

  // nullptr terminated arrays of StripeBase pointers
  StripeBase* const* stripes_;

  // Singly linked list of StripeGroups
  StripeGroup* const next;
  static StripeGroup* root;

};


// Wrapper around StripeBase to enforce some type checking
// STRUCT is the data structure stored in the stripe
// REG is the handle type used to index into it (for type enforcement)
template <typename STRUCT, typename REF>
struct Stripe : public StripeBase {
  Stripe(const char* name) : StripeBase(sizeof(STRUCT), name) {
    static_assert(sizeof(STRUCT) % 4 == 0, "stripe sizes must be multiples of 4");
    static_assert(std::alignment_of<STRUCT>::value <= 4, "stripe alignment must be at most 4");

  }

  STRUCT& operator[](REF ref) {
    return *(static_cast<STRUCT*>(element(ref.index())));
  }
};

void InitStripes(uint32_t multiplier);

}  // namespace cwerg
