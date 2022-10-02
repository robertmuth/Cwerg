# Experimental Frontend For The Cwerg Language

Cwerg tries to trade-off language expressiveness with compiler
implementation complexity. We hope to reach a sweet spot *above* what
C goves us today.

Complexity budget: about 10kLOC for a compiler frontend with basic optimization

Warning: This is completely unfinished and experimental

## Syntax
  
  Source code will be stored as serialized S-Exprression with tooling to
  convert back and forth to a yet to be defined concrete syntax.

  The tooling will also do most of the semantic checking.
  Comments wil be explicit in the AST and cannot occur in arbitrary places.
  Similarly, parenthesis used to group expression will be modelled in the AST.


## Discussion of Features


###  Increment/decrement operators (`++`/`--`) NO

Pro: Helpful for writing very succint code. 

Con: Expressions with side-effects requiring the concept of [Sequence Point](https://en.wikipedia.org/wiki/Sequence_point) which adds complexity.

Decision: omitted 

### Enhahanced Assignments (`+=`, `-=`, etc.) YES

Pro: Convenient shorthand, especially if increment/decrement is not availabe. Helps with code generation in the absence of CSE optimzation pass.

Con: `a += b` is *mostly* syntactic sugar for `a = a + b` so not much expressive power is gained.

Decision: included

### Multi-assignment PROBABLY NO

Pro: Nice for swaps: `a, b = b, a`
Con: Needs tuples, makes syntax more complicated

Decision: probably omitted

### Multi-definition of Variables and Parameters NO

Pro: `x,y,z: int` is very succint

Con: Makes syntax more complicated. Likely requires notion of Tuple.

Decision: omitted

### Short-circuit operators (`&&`, `||`) YES

Pro: Very common and useful

Con: Adds implementation complexity

Decision: included

### Select operators (`? :`) YES

Pro: Very common and useful

Con: Does not add a lot of expressiveness

Decision: included


### Vararg (...) NO

Pro: Handy for printf style function

Con: High implementation complexity

Decision: omitted 

#### Mutability (aka `const`) control  YES

Pro: Enables more safety checking

Con: Adds clutter to code. Adds implementation complexity

Decision: Supported for variable, pointees and slices. `mut` pointers/slices can be assigned to non-`mut` pointers/slices. Default is non-mutable

#### Symbol visbility control [YES]

Decision: included for toplevel types, modules, functions, constants and variables. Not for struct fields. Default is not-public

### Built-in Map and List datatypes NO

Pro: Map (and List) are almost all you need (see Lua)

Con: They require built-in memory management

Decision: omitted. Can be implemented in libraries.

### Built-in Unicode/Utf-8 support NO

Pro: The world runs on Unicode and Utf-8

Con: System programs rarely need internationalization. 
      Unicode handling is complex and can be moved into the library.

Decision: omitted (strings are uninterpreted arrays of bytes). Needs to be implemented in libraries.


### Structural Type equivalence vs name equvalence BOTH

Default is structural equivalence but all types can be wrapped (= distinct Nim/Odin) which forces name equivalence.

### Checked Array/Slice indexing YES

Pro: Avoids common bugs

Decision: included via `[]` operator. Can be worked around if necessary.

### NULL pointers (aka nullptr, nil, None, etc.) NO

Con: cause a lot of bugs

Decision: omitted - use optional pointers of sum type  (*A | void)

### Sum Types YES

Pro: Very useful for implementing Result and Optional types

Decision: included with special optimization for optional pointers so that 
          nullable pointer can be implemented efficiently 


### Structs with member functions PROBABLY NOT

Pro: makes name resolution of member functions easier


### Embedded structs PROBABLY NO

Pro: Suppports primitive implementation inheritance


### Classes/Interfaces PROBABLY NO


### Modules YES

Pro: Templated Modules will provide namespaces and generics (similar to later versions of Oberon)

Decision: included

### Metaprogramming GENERIC MODULES

Modules can be parameterized by Constants, Types or other Modules

### Switch/Match statements UNDECIDED

### Tuples UNDECIDED

Pro: Needed for multi-assignment (`a, b = 1, 2`) and mutiple return values

### Multiple return values UNDECIDED

Con: Optional and Result types cover a lot of use cases for multiple return values. If small structs can be passed in and out of functions in registers.

### Passing and returning of (small) Arrays YES

Pro: Provides a path to promote `[4]f32` into SIMD operands

### Init/Fini Functions for (almost) static initialization and cleanup YES

Decision: included. Will be guided by acyclic Module dependency graph.


### Implicit conversion of Numbers (ints/floats) UNDECIDED

### Type Inference PROBABLY YES BUT LIMITED

Pro: `i := 666_u32` or `i: u32 := 666` reduces clutter

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


