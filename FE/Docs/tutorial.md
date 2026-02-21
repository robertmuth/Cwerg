# Cwerg Language Overview

Cwerg tries to find the right balance between language expressiveness and compiler
implementation complexity.
The hope is to reach a sweet spot above what C gives us today:
A small language that can be maintained by a single person and which is
convenient for writing system software like operating systems and compilers.

As with C, all control flow and all memory allocation is explicit.

Discouraged/unsafe practices are possible but require explicit overrides, e.g.:
uninitialized variables, global visibility, mutability, unchecked array accesses, untagged unions, ...

Since small is subjective we have set a complexity budget of about 10kLOC
for a compiler frontend with basic optimizations
(there is a comparable complexity budget for the backend).

 Cwerg is also meant to be a fast language focussing on whole program compilation. We target a compilation speed
 of at least a million LOC per second and programs of up to 10 million LOC.

## Highlights

* Low level, C-like language: no GC, no unexpected control flow
* defer statement (scheduling code to run at scope exit)
* tagged unions (sum types)
* optionally wrapped types (by-name type equivalence)
* modules (not nested)
* generics via generic modules
* simple hygienic macro system
* limited polymorphism
* printf like functionality with custom formatters (enabled by polymorphism and generics)
* vecs (arrays) do not decay to pointers when passes as arguments
* vec indexing is checked by default
* spans (views on vecs)
* named blocks + multi-level break/continue
* expression statements - cleaned up version of the C's comma operator
* (almost) no implicit conversions and no truthinesss
* all values are zero initialized by default (can be overriden with undef)
* visibility is private by default
* variables are immutable by default
* no goto, no va-args, no bitfields
* no cyclic dependencies between modules
* limited type inference
* order of function definitions and globals does not matter
* all comments are on separate lines (no end of line comments)
* blocks are the elementary loop construct
* break and continue have optional label argument. 
* for loops are only for iterating over numeric ranges. Use macros
  to create custom for loops for specific data structures

## Syntax

Cwerg uses a Python inspired syntax where the indentation level
is significant. Operators are C style except for pointers, address taking and dereferncing
which are Pascal style.mostly 

We give some examples below to convey a general feeling for the language.
The details should become clear after reading the rest of the tutorial.

More examples can be found in
*  [FE/TestData/](../TestData)
*  [FE/Lib/](../Lib)
*  [FE/LangTest/](../LangTest)


### Hello World (full example)

```
module:

import fmt

; the program entry point
fun main(argc s32, argv ^^u8) s32:
    fmt::print#("hello world\n")
    return 0

```

Every file starts with a module stanza which only becomes interesting for generic modules.

The type information in the function declaration follows the Pacal model
of identifier followed by type.
Functions can only return one value.

`fmt::print#` is a macro invocation. All macros names must end in "#".


### Sieve of Eratosthenes (excerpt)

```
; a global constant
global N uint = 1000 * 1000 * 1000

; a mutable global vec of bools initialized to `true`
; index i represents number 3 + 2 * i
global! is_prime = [N]bool{true}

; Count the number of primes below n
fun sieve() uint:
    ; mutable local varible
    let! count uint = 1
    ; the type of loop variable `i`  is determined by `N`
    for i = 0, N, 1:
        if is_prime[i]:
            set count += 1
            let p uint = i + i + 3
            for k = i + p, N, p:
                set is_prime[k] = false
    return count
```

Exclamation marks at the end of keywords indicate mutability
or potentially unsafe behavior.

## Binary Tree (parameterized/generic module)

```
module(
        ; the payload type
        $type TYPE,
        ; the less-than function ($type x $type) -> bool
        $lt CONST_EXPR):

pub global Leaf = void_val

pub rec Node:
    left union(void, ^!Node)
    right union(void, ^!Node)
    payload $type

; shorthand for optional Node pointer
; currently, we cannot use inside the Node definiton
; because of type cycles. 
pub type MaybeNode = union(void, ^!Node)

type Visitor = funtype(node ^$type) void

pub fun InorderTraversal(root MaybeNode, visitor Visitor) void:
    ; return if the union root is a Leaf
    trylet node ^!Node = root, _:
        return
    do InorderTraversal(node^.left, visitor)
    do visitor(@node^.payload)
    do InorderTraversal(node^.right, visitor)

; returns the new root
pub fun Insert(root MaybeNode, node ^!Node) ^!Node:
    set node^.left = Leaf
    set node^.right = Leaf
    trylet curr ^!Node = root, _:
        return node
    if $lt(@node^.payload, @curr^.payload):
        set curr^.left = Insert(curr^.left, node)
    else:
        set curr^.right = Insert(curr^.right, node)
    return curr

```

## Word Count

```
module:

import os

import fmt

fun is_white_space(c u8) bool:
    return c == ' ' || c == '\n' || c == '\t' || c == '\r'

; word, line and character count statistics
rec TextStats:
    num_lines uint
    num_words uint
    num_chars uint

; Returns either a TextStat or an Error
fun WordCount(fd os::FD) union(TextStats, os::Error):
    ; note limited type inference in next two stmts
    let! stats = TextStats{}
    let! in_word = false
    ; do not initialize buf with zeros
    let! buf [1024]u8 = undef
    while true:
        ; if FileRead returns an uint, assign it to n else return it
        trylet n uint = os::FileRead(fd, buf), err:
            return err
        if n == 0:
            break
        set stats.num_chars += n
        ; index variable has the same type as n.
        for i = 0, n, 1:
            let c = buf[i]
            cond:
                case c == '\n':
                    set stats.num_lines += 1
                case is_white_space(c):
                    set in_word = false
                case !in_word:
                    set in_word = true
                    set stats.num_words += 1
        if n != len(buf):
            break
    return stats

fun main(argc s32, argv ^^u8) s32:
    trylet stats TextStats = WordCount(os::Stdin), err:
        return 1
    ; print# is a stmt macro for printing arbitrary values.
    ; (It is possible to define formatters for custom types.)
    fmt::print#(stats.num_lines, " ", stats.num_words, " ", stats.num_chars, "\n")
    return 0
```
## Type System

Cwerg's type system is similar to C's with the following differences

* there are almost no implicit conversions
* pointers cannot be null
* there is a stronger emphasis on "const/mutability correctness"
* vecs (arrays) do not decay to to pointers, you have explicitly take the address
* vecs of different sizes are different types
* spans can be used where vec-like objects with variable length
  are required
* (tagged) unions are supported to simplifying error handling and
  emulate nullable pointers

### Base Types

* `u8`, `u16`, `u32`, `u64`  unsigned int in various widths
* `uint`  unsigned int big enough to hold a pointer
* `s8`, `s16`, `s32`, `s64`  signed int in various widths
* `sint`  signed int big enough to hold a pointer
* `r32`, `r64`  floating points in various widths
* `typeid` unsigned int big enough to hold a type tag
* `bool`
* `void`

### Pointer Types

The pointer type notation is similar to Pascal.
The caret goes in front of type.

```
; pointer to a u32
let p_normal ^u32 = ...

; pointer to a mutable u32
let p_mutable ^!u32 = ...


; address of operator
let p = @...

```


### Vecs (Arrays)

Vec dimension go in front of the element type:

```
    ; 10 element vec of element type u32, initialized with 1
    global! one_dim_vec [10]u32 = {: 1}
    ; while types have the square brackets on the left,
    ; indexing puts the on the right
    let element5 = one_dim_vec[1]

    static_assert type_of(front!(one_dim_vec)) == typeid_of(^!u32)
    static_assert type_of(@!one_dim_vec[0]) == typeid_of(^!u32)
    static_assert type_of(front(one_dim_vec)) == typeid_of(^u32)
    static_assert type_of(@one_dim_vec[0]) == typeid_of(^!u32)

    ; 2 element vec of 10 element vec of element type u32
    global! two_dim_vec [2][10]u32 = {: {: 2 }}

    static_assert type_of(two_dim_vec[1]) == typeid_of(one_dim_vec)
     
```

Vecs of different length are not compatible and
are different from pointers to the element type.
```
static_assert typeid_of([10]u32) != typeid_of([2]u32)
static_assert typeid_of([10]u32) != typeid_of(^u32)
```

Accessing the length of a vec:
```
    -- returns a `uint` with the length of the vec
    ... = len(a_vec)
```
Accessing the address of the first element of a vec:

```
    ; returns a readonly pointer to the first element of the vec

    ... = front(readonly_or_mutable_vec)

    ; returns a mutable pointer to the first element of the mutable vec

    ... = front!(mutable_vec)
```


Note: vec literals are immutable but you can use them to initialize
a mutable variable like so:
```
let! buffer = {[10]u16: 0 = 666, 1 = 66, 3 = 6}


```

### Spans

Spans are essentially fat pointers consisting of a pointer to the first element
of a vec and a length.

Type declations:
```
    ; regular span with elements of type `u32`
    let s_normal span(u32) = ...

    ; mutable span with elements of type `u32`
    let s_mutable span!(u32) = ...
```

The length and address of the first element of a span can be accessed
with the same syntax as for vec:
```
    ; returns a readonly pointer to the first element of the span

    ... = front(readomly_or_mutable_span)

    ; returns a mutable pointer to the first element of the mutable span

    ... = front!(mutable_span)

    ; returns a `uint` with the length of the span.

    ... = len(a_span)

```

Creation:
```
    ; create a span from a pointer and length.
    ; the mutability of the span is determined by the pointer.
    let a = {[1024]u8: 0, 1, 2, 3}
    let s_mutable = make_span(front!(a), len(a))

    ; conversion from vecs to non-mutable span is one of the few
    ; implicit conversions supported by Cwerg:
    let s_normal span(u8) = a
```



### Function types


Function types can be described like so:
```
    funtype(param1 type1, param2 type2, ...) return-type
```
### Recs (Structs)


Rec types can be declared like so:

```
rec Date:
    year u16
    month u8
    day u8
    hour u8
    minute u8
    second u8
```

Some usage examples:
```
; rec literals use a similar syntax to array literals
let! mydate = {Date: 2011, 11, 11, 11, 11, 11}

; field access 
... =  mydate.year
```

There are plans to have per field private/public access control but for now if the `rec` is annotated with `pub` all fields are externally visible.

### Enums

Enum types can be declared like so:

```
enum Color u8:
    blue auto
    green 10
    red auto

```

This declares an enum `Color` with 3 members (`red`, `green`, `blue`)
with an underlying type of `u8`.
`auto` is using the previously assigned value incremented by 1 or zero if it is the first member.  So in the above example we get:

```
static_assert unwrap(Color:blue) == 0_u8
static_assert unwrap(Color:green) == 10_u8
static_assert unwrap(Color:red) == 11_u8
```

Enums are C-like in that they are essentially named integer constants.
Unlike C, enums members are always used "fully qualified" using a **single** colon.

### Type shortcuts and wrapped types

Abbreviations for lengthy types can be declared like so:

```
type t1 = funtype(x u8, y u8) u1
assert_static typeid_of(t1) == typeid_of(funtype(x u8, y u8) u1) 
```


This is strictly an abbreviation, the lhs and the rhs can be used interchangeably in the code.

To force by name type equivalence use an exclamation mark like so
```
type! t1 = funtype(x u8, y u8) u1
assert_static typeid_of(t1) != typeid_of(funtype(x u8, y u8) u1) 
```
The type `t1` is said to be a wrapped type.



### (Tagged) Unions


Tagged unions can be declared like so:

```
    union(s32, void, u8, ^sint, [32]u8))
```

Note, that there are no names - only types. In case that the same type is
needed twice in a single union, wrapped types can be used.

Using the exclamation mark suffix as in `union!` changes the union to be untagged.

Unions are:
*  order independent
*  duplicate eliminating
*  auto-flattening

In the example below `u1` and `u2` are the same type:
```
type u1  = union(u8, s64, union(u8, s32), union(u8, void))
type u2  = union(s64, s32, void, u8))
static_assert typeid_of(u1)  ==  typeid_of(u2)
```

Sometimes it is useful to define the type of a union which is the delta of two unions
A and B where B's member types are a subset of A's. This can be done like so:
```
type u1  = union(u8, s64, void, r64)
type u2  = union(s64, void))
static_assert typeid_of(union_delta(u1, u2)  ==  typeid_of(union(u8, r64))
```

Note having names for union elements changes the usage patterns
compared with C, especially for tagged unions.
The usual patterns is to copy the entire member into or our of the union.

More info in [Unions](union_types.md)

## Literals


### Boolean Literals

`true`, `false`

There is no concept of truthiness.


### String Literals

Regular string literals are enclosed in double-quotes. e.g. "escaped string\n" and may contain back-slash escapes. Most single character escapes are supported
('\n', '\t',  '\\', etc).
Also supported are hexadecimal escape ('\xff') but **not** octal escapes.

Unescaped (aka raw) strings are prefixed with "r", e.g. (r"string").

Hex strings are prefixed with x, e.g. (x"de ad be ef") and ignore all
white space characters.

Multi-line strings are enclosed in triple quotes, e.g. """multi-line string:"""",
and also come in unescaped (prefix "r") and hex (prefix "x") flavors.


### Number Literals

Number literals may contain underscores ("_") which are ignored. Since Cwerg does not implicitly convert numbers it is often necessary to use typed number by adding one of the following suffices: u8, u16, u32, u64, s8, s16, s32, s64, r32, r64, e.g. "0x1234_s16".

Both hexadecimal (0x) and binary (0b) basis are supported but **not octal**.
For hexadecimal numbers only the lower case letters (a-f) are valid.

### Vec (Array) Literals


Vec literals are declared like so:
```
    {[5]s32: 1, 2, 3}
```
If there are fewer initializers than the vec size, the previous value will
repeated. So this is equivalent to:
```
    {[5]s32: 1, 2, 3, 3, 3}
```

If no initializer is provided, zero will be used.

initializers for specific indices can declared like so:
```
   {[5]s32: 1 = 6, 3 = 9}
```
This is equivalent to:
```
{[5]s32: 0, 6, 6, 9, 9}
```

### Rec (Struct) Literals


Literals:

Assuming this rec:
```
rec Date:
    year u16
    month u8
    day   u8
    hour u8
    minute u8
    second u8
```

Rec literals are declared like so:

```
    {Date: 2000, 1, 12}
```

If no initializer is provided, zero will be used.

Initializers for specific fields can be declared like so:


```
    {Date: year =2000, month = 1, day = 12}
```

The initializer may skip fields but must be in rec order.

## Module Definitions

Every file starts with module stanza. A simple version looks like:

```
module:
    <TOP-LEVEL-DECLARATION>+
```

A more complex definition for the generic case looks like:

```
module optional-name(param-name1 param-kind1, param-name2 param-kind2, ...):
    <TOP-LEVEL-DECLARATION>+
```

All module parameters must start with a '$' (similar to macro parameters)
and must be have one of the following kinds:
* CONST_EXPR: a constant expression including a function
* TYPE: a type expression


## Top Level Declarations

By default all top level declarations are module private.
The `pub` modifier will export the declaration and thereby make it
visible to the importing module.

Note, the declarations listed here can only appear at the top
level, not inside function bodies.


### Global Constants

Global constants are declared like so

```
global a_global_const u64 = 7_u64
```

Cwerg has limit type inference so this could be simplified to either:
```
global a_global_const u64 = 7
```
or
```
global a_global_const = 7_u64
```


### Global Variables

Variables use the same syntax as global except that the keyword is suffixed by `!`, e.g.:

```
global! a_global_var u64 = 7_u64
```

If an initializer expression is omitted, the global is initialized to zero.


### Functions

Functions are declared like so:

```
 fun foo(param1 typ1, param2 type2, ...) returntype:
    <STATEMENT>*
```

Functions can only have one result.

Function parameters are not mutable.

Polymorphism is described [here](polymorphism.md)

### Enums, Types (Typedefs) and Recs (Structs)

These were covered in the Type Section above



### Static Asserts

Static asserts are checked at compile time. Example:
```
-- this ensures that we are on a 64bit system
static_assert sizeof(^u8) == 8
```

#### Macros

TBD  - see [Macros](macros.md)


## Statements

Note: all statements start with an introductory keyword.


### Local Constants

Local constants have the same syntax as global constants except
they are introduced with the `let` keyword. All these statements are equivalent:

```
let a_local_const u64 = 7_u64
let a_local_const u64 = 7
let a_local_const = 7_u64
```


### Local Variables

Local variable have the same syntax as local constants except that introductory
keyword is suffixed with "!". All these statements are equivalent:

```
let! a_local_const u64 = 7_u64
let! a_local_const u64 = 7
let! a_local_const = 7_u64
```
If an initializer expression is omitted, the global is initialized to zero.
The special initializer `undef` will leave the initial value undefined.


### (Compound) Assignment Statements

```
set a_local_const = 666
...
set a_local_const += 666
set a_local_const and= 666

```


### Trylet Statements

A trylet statement is most useful for processing unions that represent two states. e.g.
* a valid pointer or null
* a result or an error

Example error processing:
```
    trylet n uint = os::FileRead(fd, buf), err:
        return err
```

The call to `os::FileRead` returns either a `uint` or one of several error types.
If the call returns `uint`, it will be assigned to `n`. Otherwise the error type will
be assigned `err` and then subsequently returned.


### Tryset Statements

`tryset` is to `trylet` what `set` is to `let`.
Example:
```
    let! u uint = ...
    ...
    tryset n = os::FileRead(fd, buf), err:
        return err
```

### Block Statements

A block introduces an optionally labelled new scope.
Control-flow will resume at the next statement after block if
the control flow falls through the last statement of the block.
```
block <NAME>?:
    <STATEMENT>*
```

A `continue` statement inside the block will set control-flow to the beginning
of the block and a `break` statement will exit the block.
Both  `continue` and `break` statements can have an optional label indicating
which enclosing `block` they refer to.


### While Loops

```
while <CONDITION>:
    <STATEMENT>*
```


### For Loops

```
for var-name = initial-expr, limit-expr, step-expr:
    <STATEMENT>*
```

For loops differ from their C counterparts in the following way:
* they are mostly meant for ranging over a sequence of integers
* initial-expr, limit-expr, step-expr are evaluated once at the beginning
* the type of var-name is determined by the type of limit-expr
* var-name is not mutable

If you need a for loop to iterate over a custom data-structure, define
a macro.


### If-else Statements

Simple
```
if condition:
    <STATEMENT>*
```

With else clause

```
if condition:
    <STATEMENT>*
else:
    <STATEMENT>*
```


### Cond Statements

```
cond:
    case condition1:
        <STATEMENT>*
    case condition2:
        <STATEMENT>*
    ...
```

Note, there is no fallthrough.
Case are checked in order.z
A `default` case  be expressed as `case true`
and must go last.


### Defer Statements

```
defer:
    <STATEMENT>*
```

The code in the defer body will be run when the enclosing scope is exited.
The code in the defer body **must not** branch out of the body.
Multiple defer statements in the same scope are run in the reverse order they
are defined.


### Return Statements

```
return optional-expression
```

Return a value from the enclosing function or expression statement.
If no expression is provided, `void` is assumed.


### Continue Statements

```
continue optional-label
```

Jump to the beginning of a  `block`, `while` or `for` statement.
The optional label can be used to name the block to exit.


### Break Statements

```
break optional-label
```

Exit the enclosing `block`, `while` or `for` statement.
The optional label can be used to name the block to exit.
```
    block label1:
        ...
        block label2:
            ...
            -- exits the block, label2
            break label2
            ...
            -- also exits the block, label2
            break
            ...
            -- exits the block, label1
            break label1
            ...
```

### Trap Statements

```
trap
```

Stop execution of the program.


### Do Statements

```
do expression
```

Runs the expression and discards the result.
The expression will usually be a function call with a side-effect.


## Expressions

### Prefix Operators

| Name  | Symbol | Description            |
| ----- | ------ | ---------------------- |
| NOT   | !      | bitwise or logical not |
| MINUS | -      | unary minus            |


### Infix Operators

| Name   | Notation | Description               |
| ------ | -------- | ------------------------- |
| ADD    | +        |                           |
| SUB    | -        |                           |
| DIV    | /        |                           |
| MUL    | *        |                           |
| MOD    | %        |                           |
| MIN    | min      |                           |
| MAX    | max      |                           |
| AND    | &        | bitwise and               |
| OR     | \|       | bitwise or                |
| XOR    | ~        | bitwise xor               |
| EQ     | ==       |                           |
| NE     | !=       |                           |
| LT     | <        |                           |
| LE     | <=       |                           |
| GT     | >        |                           |
| GE     | >=       |                           |
| ANDSC  | &&       | short-circuit logical and |
| ORSC   | \|\|     | short-circuit logical or  |
| SHR    | >>       |                           |
| SHL    | <<       |                           |
| ROTR   | >>>      | bitwise rotate right      |
| ROTL   | <<<      | bitwise rotate left       |


+, -, *, /. % for signed and unsigned integers have wrap-around
sematics and do not trap on overflow.

The main additions to C are: MIN, MAX, ROTL, ROTR which are directly
supported by the backend.

Note, operator precedence has yet to be finalized

### Function Style Operators

#### Expression centric

| Notation                 | Description                                       |
| ------------------------ | ------------------------------------------------- |
| len(E) -> uint           | length of an vec or span                          |
| front(E) -> P            | pointer to first element of vec or span           |
| front!(E) -> P           | mutable pointer to first element of vec or span   |
| make_span(P, E) -> S     | make a span from a pointer and a length           |
| ptr_inc(P, E [, E]) -> P | increment pointer with optional bounds check      |
| ptr_dec(P, E [, E]) -> P | decrement pointer with optional bounds check      |
| ptr_diff(P, P) -> sint   | pointer difference (C semantics)                  |
| stringify(E) -> []u8     | convert an expression to a textual representation |


#### Type centric

| Notation                | Description                                |
| ----------------------- | ------------------------------------------ |
| is(E, T) -> bool        | check if union expression is of given type |
| type(E) -> T            | type of expression                         |
| typeid_of(T) -> typeid  | typeid of a type                           |
| type_of(E) -> T         | type of an expression                      |
| union_delta(T, T) -> T  | type delta of two union type expressions   |
| offset_of(R, F) -> uint | offset of field in record                  |
| size_of(T) -> uint      | size of a type                             |


#### Casts

| Notation              | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| wrap_as(E, T) -> E    | convert value to enum or wrapped type                                |
| unwrap(E) -> E        | convert  enum or wrapped type to underlying type                     |
| narrow_as(E, T) -> E  | convert union value to actual type                                   |
| narrow_as!(E, T) -> E | same as above but unchecked                                          |
| widen_as(E, T) -> E   | convert value to union                                               |
| as(E, T) -> E         | converts between  numerical types                                    |
| bitwise_as(E, T) -> E | convert expression to a type of same width, including int to pointer |
| unsafe_as(E, T) -> E  | convert between pointers                                             |

Also see [Casting](casting.md)

##### Legend

* E: expression
* T: type expression
* T: record type
* P: pointer value
* F: record field name
* S: span

### Expression Statements

Expression Statements are code blocks that evaluate to a value. Examples

```
let x s8 = foo()
let sign s8 = expr:
                  cond:
                    case x == 0:
                        return 0_s8
                    case x < 0
                        return -1_s8
                    -- default case
                    case true:
                        return 1_s8

```
