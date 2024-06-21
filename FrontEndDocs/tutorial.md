# Cwerg Language Tutorial


## Highlights

* Low level, C-like language: no GC, no unexpected control flow
* Python inspired syntax
* Optional sexpr syntax
* defer statement (scheduling code to run code at scope exit)
* tagged unions (sum types)
* optionally wrapped types (by-name type equivalence)
* modules (not nested)
* simple hygienic macro system
* limited polymorphism
* slices (array views)
* (almost) no implicit conversions

## Examples

Cwerg use a Python inspired syntax where the indentation level
is significant. Adjacent lines of statements with the same indentation
level belong to the same code block.

### Hello World (full example)

```
module main:

import fmt

@cdecl fun main(argc s32, argv ^^u8) s32:
    fmt::print#("hello world\n")
    return 0

```

Every file starts with a module stanza. The `name` of the module, "main",
is largely ignored and may be dropped in the future.

The type information in the function declaration follows the Go model of
identifier followed by type.
Functions can only return one value.

Annotations are identifiers that start with "@" and can preceed certain
syntactical constructs. Here `@cdecl` disables the name mangiling of function main
so it can be linked against the startup code.

`fmt::print#` is a macro call. All macros names must end in "#".


### Fibonacci (excerpt)

```
@pub fun fib(x uint) uint:
    if x <= 1:
        return x
    return fib(x - 1) + fib(x - 2)
```

The `@pub` annotation makes `fib` visible outside of the module.

### Sieve of Eratosthenes (excerpt)

```
-- a global constant
global N uint = 1000 * 1000 * 1000;

-- a mutable global array of bool initialized to `true`
-- index i reprents number 3 + 2 * i
global! is_prime = [N]bool{true}

-- Count the number of primes below n
fun sieve() uint:
    let! count uint = 1
    for i = 0, N, 1:
        if is_prime[i]:
            set count += 1
            let p uint = i + i + 3
            for k = i + p, N, p:
                set is_prime[k] = false
    return count
```

Exclamtion marks at the end of keywords indicate mutability.

## Type System

Cwerg's type system is similar to C's with the following differences

* there are very few implicit conversions
* pointers cannot be null
* there is a stronger emphasis on "const/mutability correctness"
* arrays do not decay to to pointers and arrays of different sizes
  are different types
* slices can be used where arrays like objects with variable length are required
* (tagged) unions are supported to simplifying error handling and emulate nullable
 pointers

### Base Types

* `u8`, `u16`, `u32`, `u64`  unsigned int in various widths
* `uint`  unsigned int big enough to hold a pointer
* `s8`, `s16`, `s32`, `s64`  signed int in various widths
* `sint`  signed int big enough to hold a pointer
* `r32`, `r64`  floating points  in various widths
* `typeid` unsigned int big enough to hold a type tag
* `bool`
* `void`

### Pointer Types

The pointer type notation is similar to Pascal.

```
-- pointer to a u32
^u32

-- pointer to a mutable u32
^!u32
```

### Arrays

Array of different length are not compatible

```
-- 10 element array of element type u32
[10]u32

```

### Slices

Slices are essentially fat pointers consisting of pointer to the first element of an array
and a length.

```
-- regular slice
slice(u32)
-- mutable slice
slice!(u32)
```

### Function types


Function type can be described like so:
```
funtype(param1 type1, param2 type2, ...) return-type
```
### Records


Records, essentially C-structs, can be declared like so:

```
rec Date:
    year u16
    month u8
    day   u8
    hour u8
    minute u8
    second u8
```


There are plans to have per field private/public access control but for now if the `rec` is annotated with `@pub` all fields are externally visible.

### Enums

Enums can be declared like so:

```
enum Color u8:
    blue auto
    green 10
    red auto

```

This declares an enum `Color` with 3 members (`red`, `green`, `blue`)
with an underlying type of `u8`.
`auto` is used the previously asigned value incremented by 1 or zero if it is the first member.  So in the above example we get:
```
Color:blue has value 0
Color:green has value 10
Color:red has value 11
```

Enums are C-like in that they are essentially named integer constants.
Unlike C, enums members are always used "fully qualified" using a single colon.

### Type shortcuts and wrapped types

Abbreviations for length types can be declared like so:

```
type t1 = funtype(x u8, y u8) u1
```


This is strictly and abbreviation, the lhs and the rhs can be used interchangably in the code.

To force by name type equivalence in this case, use the `@wrapped` annotation like so
```
@wrapped type t1 = funtype(x u8, y u8) u1
```
The type `t1` is said to be a wrapped type.



### (Tagged) Unions


Tagged unions can be declared liek so:

```
union(s32, void, u8, ^sint, [32]u8))
```

Note, that there are no names only types. In case that the same type is
needed twice in a single union, wrapped types can be  used.

The annotation `@untagged` changes a union to untagged.

Unions are a order independent, duplicate eliminating, and auto-flattening.
In the example below `u1` and `u2` are the same type:
```
type u1  = union (u8, s64, union(u8, s32), union(u8, void))
type u2  = union (s64, s32, void, u8))
```

More info in [Unions](union_types.md)


## Literals


### Booleam Literals

`true`, `false`

There is no concept of truthiness

### String Literals

Regular string literals are enclosed in double-quotes. e.g. "escaped string\n" and may contain back-slash escapes. Most single character escapes are supported
('\n', '\t',  '\\', etc).
Also supported are hexadecimal escape ('\xff') but **not** octal escapes.

Unescaped (aka raw) strings are prefixed with "r", e.g. (r"string").

Hex strings are prefixed with x, e.g. (x"de ad be ef") and ignore all white space
characters.

Multi-line strings are enclosed in tripple quotes, e.g. """multi-line string:"""",
and also come in unescaped (prefix "r") and hex (prefix "x") flavors.

### Number Literals

Number literals may contain underscores ("_") which are ignored. Since Cwerg does not implicitly convert numbers it is often necessary use typed number by adding one of the following suffices: u8, u16, u32, u64, s8, s16, s32, s64, r32, r64, e.g. "0x1234_s16".

### Array Literals

Array literals are declared like so:
```
[5]s32{1, 2, 3}
```
If there are fewer initializers than the array size, the last value will
repeated. So this is equivalent to:
```
[5]s32{1, 2, 3, 3, 3}
```

If no initializer is provided, zero will be used.
initializers for specific indices can declared like so:
```
[5]s32{1:6, 3:9}
```
This is  equivalent to:
```
[5]s32{0, 6, 6, 9, 9}
```

### Record Literals
Assuming this record:
```
rec Date:
    year u16
    month u8
    day   u8
    hour u8
    minute u8
    second u8
```

record literals are declared like so:

```
    Date{2000, 1, 12}
```

If no initializer is provided, zero will be used.

Initializers for specific fields can declared like so:


```
    Date{year:2000, month:1, day:12}
```

## Module Definitions

Every file starts with module definition. A simple version looks like:

```
module optional-name:
    <TOP-LEVEL-DECLARATIOND>+]
```

A more complex definition for the generic case looks like:

```
module optional-name(param-name1 param-kind1, param-name2 param-kind2, ...):
    <TOP-LEVEL-DECLARATIOND>+]
```

## Top Level Declations

By default all top level desclations are module private.
The `@pub` annotation will export the declaration and thereby make it visible to the
importing module.

Note, the declarations listed here can only appear at the top
level, not inside function bodies.

### Global Constants

Global constants are declared like so

```
global a_global_const u64 = 7_u64
```

Cwerg has limit type inference so this could be simplified to either:
`global a_global_const u64 = 7` or `global a_global_const = 7_u64`.


### Global Variables

Variables use the same syntax as global except that the keyword is suffixed by `!`, e.g.;

```
global! a_global_var u64 = 7_u64
```

If an initializer expression is omitted, the global is initialized to zero.











#### Macros

TBD

### Static Asserts

TBD

### Functions

Functions are declared like so:

```
 fun foo(param1 typ1, param2 type2, ...) returntype:
    <STATEMENTS>+]
```


## Statements

Note: all statments start with an introductory keyword.

### Local Constants

Local constants have the same syntax as global constants except
they are introduce with the `let` keyword. All these statements are equivalent:

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
set a_local_const = 666;
set a_local_const += 666;
```

### Block Statements

A block introduces an optionally labelled new scope.
Controlflow will resume at the next statement after block if
the control flow falls throuh the last statement of the block.
```
block <NAME>?:
    <STAREMENTS>+
```

A `continue` statement inside the block will set controlflow to the beginning
of the block and a `break` statement will exit the block.
Both  `continue` and `break` statements can have an optional label indicating
which enclosing `block` they refer to.

### While Loops

```
while <CONDITION>:
    <STAREMENTS>+
```


### For Loops

```
for var-name = initial-expr, limit-expr, step-expr:
    <STAREMENTS>+
```

For loops differ from their C counterparts in the following way:
* they are mostly meant for ranging over a sequence of integers
* initial-expr, limit-expr, step-expr are evaluated once at the beginning
* the type of var-name is determined by the type of limit-expr

If you need a for loop to iterated over a custom data-structure, define
a macro.

### If-else Statements

```
if condition:
    <STAREMENTS>+
else:
    <STAREMENTS>+
```

### Cond Statements

```
cond:
    case condition1:
        <STAREMENTS>+
    case condition2:
        <STAREMENTS>+
    ...
```

### Defer Statements

```
defer:
    <STAREMENTS>+
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
If no expression is provide `void` is assumed.

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

### Trap Statements

```
trap
```

Stop execution of the program.

### Do Statements

```
do expression
```

Runs the expression and discards the result






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
| AND    | and      | bitwise and               |
| OR     | or       | bitwise or                |
| XOR    | xor      | bitwise xor               |
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
| PDELTA | &-&      | pointer difference        |

Note, operator precendence has yet to be finalized

### Function Style Operators


| Notation               | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| len(E) -> uint         | length of an array or slice                                 |
| front(E) -> P          | pointer to first element of array or slice                  |
| front!(E) -> P         | mutable pointer to first element of array or slice          |
| slice(P, E) -> S       | make a slice from a pointer and length                      |
| slice!(P, E) -> S      | make a mutable slice from a mutable pointer and length      |
| offsetof(R, F) -> uint | offset of field in record                                   |
| sizeof(T) -> uint      | size of a type                                              |
| pinc(P, E [, E]) -> P  | increment pointer with optional bounds check                |
| pdec(P, E [, E]) -> P  | decrement pointer with optional bounds check                |
| unwrap(E) -> E         | convert expression of a wrapped type to the underlying type |
| type(E) -> T           | type of expression                                          |
| typeidof(E) -> typeid  | typeid of an expression of union type                       |
| uniondelta(T, T) -> T  | type delta of two union type expressions                    |
| stringify(E) -> []u8   | convert an expression to a textual representation           |


Casts


TBD  - see [Casting](casting.md)


| Notation          | Description                                |
| ----------------- | ------------------------------------------ |
| as(E, T) -> E     | casts with run-time checks                 |
| wrapas(E, T) -> E | convert expression to a wrapped type       |
| bitas(E, T) -> E  | convert expression to a type of same width |

## Macros

TBD  - see [Macros](macros.md)
