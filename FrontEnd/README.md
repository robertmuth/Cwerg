# Experimental Frontend For The Cwerg Language

Cwerg tries to trade-off language expressiveness with compiler implementation complexity. 
The hope os to reach a sweet spot *above* what C gives us today.

Complexity budget: about 10kLOC for a compiler frontend with basic optimization

Warning: This is completely unfinished and experimental. We expexct to gain some
more insights about the design-space by bootstrapping the front- and backend.

## Syntax
  
  Source code will be stored as serialized S-Exprression with tooling to
  convert back and forth to a yet to be defined concrete syntax.

  The tooling will do most of the syntax and semantic checking.
  Comments wil be explicit in the AST and cannot occur in arbitrary places.
  Similarly, parenthesis used to group expression will be modelled in the AST.


## Discussion of Features

### Operations and Basic Syntax

####  Increment/decrement operators (`++`/`--`) NO

Pro: Helpful for writing very succint code. 

Con: Expressions with side-effects requiring the concept of [Sequence Point](https://en.wikipedia.org/wiki/Sequence_point) which adds complexity.

Decision: omitted 

#### Enhanced Assignments (`+=`, `-=`, etc.) YES

Pro: Convenient shorthand, especially if increment/decrement is not availabe. Helps with code generation in the absence of CSE optimzation pass.

Con: `a += b` is *mostly* syntactic sugar for `a = a + b` so not much expressive power is gained.

Decision: included

#### Multi-assignment PROBABLY NO

Pro: Nice for swaps: `a, b = b, a` and when Functions return multiple values.

Con: Needs tuples, makes syntax more complicated.

Decision: probably omitted

#### Multi-definition of Variables and Parameters NO

Pro: `x,y,z: int` is very succint

Con: Makes syntax more complicated.

Decision: omitted

#### Short-circuit operators (`&&`, `||`) YES

Pro: Very common and useful

Con: Adds implementation complexity

Decision: included

#### Select operators (`? :`) YES

Pro: Very common and useful.

Con: Does not add a lot of expressiveness.

Decision: included

#### Symbol visbility control YES

Decision: included for toplevel Types, Modules, Functions, Constants and Variables. Not for struct fields. Default is not-public

#### Built-in Unicode/Utf-8 support NO

Pro: Unicode and Utf-8 is widespread.

Con: System programs rarely need internationalization. 
      Unicode handling is complex and can be moved into libraries.

Decision: omitted (strings are uninterpreted arrays of bytes). Needs to be implemented in libraries.

#### Checked Array/Slice indexing YES

Pro: Avoids common bugs.

Decision: included via `[]` operator. But unchecked pointer arithmetic is also available

#### Pointer Arithmetic YES

Decision: included but see section on Arrays, Slices, etc. below.

### Typing

#### Vararg (...) NO

Pro: Handy for printf style function

Con: High implementation complexity

Decision: omitted 

#### Mutability (aka `const`) control  YES

Pro: Enables more safety checking. Makes Function Prototype more informative.
     Helps with optimizations.

Con: Adds clutter to code. Adds implementation complexity.

Decision: Supported for Variables, Pointees and Slices. `mut` Pointers/Slices can be assigned to non-`mut` Pointers/Slices. Default is non-mutable

#### Built-in Map and List datatypes NO

Pro: Maps (and List) are almost all you need (see Lua)

Con: They require built-in dynamic memory management.

Decision: omitted. Can be implemented in libraries.


#### Structural Type equivalence vs name equivalence BOTH

Default is structural equivalence but all types can be wrapped (similar to `distinct` in Nim/Odin) which forces name equivalence.


#### NULL pointers (aka nullptr, nil, None, etc.) NO

Con: Cause a lot of bugs.

Decision: omitted - use optional pointers of sum type  (*A | void) to model nullable Pointers safely.

#### Sum Types YES

Pro: Very useful for implementing Result and Optional types

Decision: included with special optimization for optional pointers so that 
          nullable pointer can be implemented efficiently 


#### Member functions for structs PROBABLY NO

Pro: makes name resolution of member functions easier


#### Embedded structs PROBABLY NO

Pro: Suppports primitive implementation inheritance


#### Classes/Interfaces PROBABLY NO

TBD

#### Tuples UNDECIDED

Pro: Needed for multi-assignment (`a, b = 1, 2`) and mutiple return values

#### Multiple return values UNDECIDED

Con: Optional and Result types cover a lot of use cases for multiple return values. If small structs can be passed in and out of functions in registers.

#### Passing and returning of (small) Arrays YES

Pro: Provides a path to promote `[4]f32` into SIMD operands

#### Modules YES

Pro: Modules will provide namespaces.

Decision: included

#### Parameterized Modules YES

Pro: Parameterized Modules will provide template style generics (similar to later versions of Oberon). Modules can be parameterized by Constants, Types or other Modules.

Decision: included

#### Implicit conversion of Numbers (ints/floats) UNDECIDED

Must not permit information loss.

### Type Inference PROBABLY YES BUT LIMITED

Pro: `i := 666_u32` or `i: u32 := 666` reduces clutter

#### Iterators UNDECIDED

At a minimum should allow iteration over linked lists in one line of code.

#### Runtime lookup of typeid UNDECIDED

TBD

#### Overloaded Functions (adhoc polymorphism) UNDECIDED 

TBD

### Control Flow


#### Goto PROBABLY NO

Decision:  probably omitted

#### Named Blocks and Continue/Break statements with labels YES

Pro: Simplfy inlining in the absence of `goto`


#### Defer YES

Pro: Avoids `goto cleanup`. Provides limited replacement for RAII.

#### Switch/Match statements UNDECIDED

TBD

#### Init/Fini Functions for (almost) static initialization and cleanup YES

Decision: included. Will be guided by acyclic Module dependency graph to avoid the [static initialization problem](https://en.cppreference.com/w/cpp/language/siof)


### Misc


##### Support for printing/stringification of custom data structure

TBD

#### Support for minimal overhead logging

TBD

## Pointers, Arrays, Slices, Strings

Pointers, Arrays, Slices are not mutable by default but come in mutable
flavors. Casting preserves mutabiity. Mutable entity can be passed
as non-mutable function arguments.

Pointers

* can point to anything including Scalars. Arrays and Slices
* syntactic indexing is not available but 
* pointer arithmetic is allowed and unchecked:
 `^(ptr + 8)`  is equivalent to C's `ptr[8]` or `*(ptr + 8)` 
* pointers can be cast to arrays

Arrays

* have a fixed length known at compile-time
* indexing (`a_array[i]`) is available AND run-time checked
* taking the address of an array does not decay into an ordinary pointer
* ordinary pointers can be obtained via `ptr = &a_array[0]`
* arrays can be cast to arrays of smaller length
* arrays can be converted to slices by applying the slicing operator
  `a_slice = a_array[:]`
* arrays are implicitly converted to slices if passed to a slice    function argument

Slices
* are fat pointer - starting address + length 
* are intended to be the main work horse
* indexing (`a_slice[i]`) is available AND run-time checked
* slicing `b_slice = a_slice[start:length]` can be used for checked "arithmetic"


Strings 
* are just Arrays of unsigned bytes
* they are not null terminated


