# Design Choices


## Syntax

Intially the syntax for Cwerg was essetially s-expressions.
The plan was to also use this as the on-disc format and to just concert
back and forth to a concrete syntax on the fly - say in the IDE.

However, currently we used the newer concrete syntax as the on-disc
format. though all tools can read both representations.

Comments are explicit in the AST and cannot occur in arbitrary places.
Similarly, parenthesis used to group expression will be modelled in the AST.

* [List of S-Expression Nodes](ast.md)



## Features Relative to C

### Added

* modules (optionally with parameters i.e. generics, not nestable)
* enum namespaces
* sum types (tagged unions, supporting nullable types and result types (error code + payload))
* visibility control (default private)
* mutability control (default not mutable)
* referencability control (default address cannot be taken)
* slices (fat pointers)
* structural and by-name type equality
* defer
* named blocks/continue/break
* (optionally) checked array accesses
* strict distinction between expressions and statements
* expression blocks
* simple macro system (optionally hygienic, operating on syntax tree)
* limited polymorphism (good enough to have generic and extensible print/log)
* default iniitialization of all variable/datastructure (can manually overriden)

### Removed

* arrays decay to pointers
* bitfields
* separate compilation
* pre-processor
* varargs
* implcit type conversions
* ++/--
* comma operator
* implicitly nullable pointers
* goto


## Macros

The initial plan was to not support macros because of the problems
they cause in C.

But macros have proven quite useful for two requirements:

1. an efficient version `assert` / `logging`
2. an extensible print(f) facility



For `assert`s and `logging` macros provide a form of lazy evaluation.
Example:
```
     LogInfo(["The value of expr is ", complicated_expression])
```
We only want to evaluate complicated_expression if the logging at the info level is enabled.

TODO

## Discussion of Features

### Operations and Basic Syntax

####  Increment/decrement operators (`++`/`--`): NO

Pro: Helpful for writing very succint code.

Con: Expressions with side-effects requiring the concept of [Sequence Point](https://en.wikipedia.org/wiki/Sequence_point) which adds complexity.


#### Compound Assignments (`+=`, `-=`, etc.): YES

Pro: Convenient shorthand, especially if increment/decrement is not availabe. Helps with code generation in the absence of CSE optimzation pass.

Con: `a += b` is *mostly* syntactic sugar for `a = a + b` so not much expressive power is gained.


#### Multi-assignment: NO

Pro: Nice for swaps: `a, b = b, a` and when Functions return multiple values.

Con: Needs tuples, makes syntax more complicated.


#### Multi-definition of Variables and Parameters: NO

Pro: `x,y,z: int` is very succint

Con: Makes syntax more complicated.


#### Short-circuit operators (`&&`, `||`): YES

Pro: Very common and useful

Con: Adds implementation complexity


#### Select operators (`? :`): YES

Pro: Very common and useful.

Con: Does not add a lot of expressiveness.

(maybe implement as a macro)

#### Symbol visbility control: YES

Decision: included for toplevel Types, Modules, Functions, Constants and Variables. Not for struct fields. Default is not-public

#### Built-in Unicode/Utf-8 support: NO

Pro: Unicode and Utf-8 is widespread.

Con: System programs rarely need internationalization.
      Unicode handling is complex and can be moved into libraries.

Decision: omitted (strings are uninterpreted arrays of bytes). Needs to be implemented in libraries.

#### Checked Array/Slice indexing: YES

Pro: Avoids common bugs.

Decision: included via `[]` operator. But unchecked pointer arithmetic is also available

#### Pointer Arithmetic: YES

Decision: included but see section on Arrays, Slices, etc. below.

#### Default function arguments: NO

Con: Complicate/obscure Function dispatch in combination with overloaded Functions.

#### All variables are initialized: YES

Decision: included. Variables and Struct can explicitly marked as `undef`

#### Allow the const/enum/struct definitions inside Function: NO

Pro: Allow better information hiding by scope narrowing

Con: Makes parsing more complex. Modules help with scope narrowing


#### Allow Function definitions inside Function: NO

Con: Closures have tricky semantics, even simple [gcc style nested functions](https://gcc.gnu.org/onlinedocs/gcc/Nested-Functions.html)


#### Bitfields: NO

Con: Not portable, cannot be set atomically

### Typing

#### Vararg (...): NO

Pro: Handy for printf style function

Con: High implementation complexity


#### Mutability (aka `const`) control:  YES

Pro: Enables more safety checking. Makes Function Prototype more informative.
     Helps with optimizations.

Con: Adds clutter to code. Adds implementation complexity.

Decision: Supported for Variables, Pointees and Slices. `mut` Pointers/Slices can be assigned to non-`mut` Pointers/Slices. Default is non-mutable

#### Built-in Map and List datatypes: NO

Pro: Maps (and List) are almost all you need (see Lua)

Con: They require built-in dynamic memory management.
     They can be implemented in libraries.


#### Structural Type equivalence vs name equivalence: BOTH

Default is structural equivalence (except for enums and recs) but all types
can be wrapped (similar to `distinct` in Nim/Odin) which forces name equivalence.


#### NULL pointers (aka nullptr, nil, None, etc.): NO

Con: Cause a lot of bugs.

Decision: omitted - use optional pointers of sum type  (*A | void) to model nullable Pointers safely.

#### Sum Types (aka tagged union): YES

Pro: Very useful for implementing Result and Optional types

Decision: included with special optimization for optional pointers so that
          nullable pointer can be implemented efficiently

#### Member functions for structs: NO

Pro: makes name resolution of member functions easier


#### Embedded structs: NO

Pro: Suppports primitive implementation inheritance


#### Classes/Interfaces: NO

TBD

#### Tuples: NO

Pro: Needed for multi-assignment (`a, b = 1, 2`) and mutiple return values

#### Multiple return values: NO

Instead makes sure the small structs, slices and sums/unions are passed in registers

#### Passing and returning of (small) Arrays YES

Pro: Provides a path to promote `[4]f32` into SIMD operands

#### Modules YES

Pro: Modules will provide namespaces.

#### Parameterized Modules: YES

Pro: Parameterized Modules will provide template style generics (similar to later versions of Oberon). Modules can be parameterized by Constants, Types or other Modules.

#### Implicit conversion of Numbers (ints/floats) NO

Use explicit casts

### Type Inference: YES BUT LIMITED

Pro: `i := 666_u32` or `i: u32 := 666` reduces clutter

#### Iterators PROBABLY NO


Use macros to define custom for loop syntaxes as needed.

#### Runtime lookup of typeid: YES


#### Overloaded Functions (adhoc polymorphism) UNDECIDED

Likely only supported for a fixed feature set, e.g. iterators and stringification

### Control Flow


#### Goto: PROBABLY NO

The label blocks and defer seem to be adequate.

Gotos in C are convenient when you transpile to C but Cwerg is not meant to be a
compilation target.

#### Named Blocks and Continue/Break statements with labels: YES

Pro: Simplfy inlining in the absence of `goto`


#### Defer: YES

Pro: Avoids `goto cleanup`. Provides limited replacement for RAII.

#### Switch/Match statements: YES

see node type cond

#### Init/Fini Functions for (almost) static initialization and cleanup YES

Decision: included. Will be guided by acyclic Module dependency graph to avoid the [static initialization problem](https://en.cppreference.com/w/cpp/language/siof)


### Misc

#### When-style support for conditional compilation UNDECIDED

Pro: Useful for code re-use and portability

Con: Can make code hard to understand. Tricky to implement unless limited to be
     used inside functions. Must disable some semantic checking in the non-included code portions or run very early.
     Competes with simpler approaches of selecting from a set of API compatible modules at link-time.

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

## Interesting References:

  * [Readable Lisp S-expressions](https://readable.sourceforge.io/)
  * https://github.com/robertmuth/awesome-low-level-programming-languages
  * https://c3.handmade.network/
  * http://c2lang.org/site/
  * https://www.c3-lang.org/
  * https://odin-lang.org/docs/overview/
  * https://github.com/vlang/v/blob/master/doc/docs.md
  * https://nim-lang.org/documentation.html
  * https://github.com/oberon-lang/specification/blob/master/The_Programming_Language_Oberon%2B.adoc
  *
