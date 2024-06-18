# Cwerg Language Tutorial

## Hello World

```module main:

import fmt

@cdecl fun main(argc s32, argv ^^u8) s32:
    fmt::print#("hello world\n")
    return 0

```

Cwerg use a Python inspired syntax where the indentation level
is significant. Adjacent lines of statements with the same indentation
level belong to the same code block.

Every file starts with a module stanza. The `name` of the module, "main",
is largely ignored and may be dropped in the future.

The type information in the function declaration follows the Go model of
identifier followed by type.
Functions can only return one value.

Annotations are identifiers that start with "@ and can preceed certain
syntactical constructs. Here `@cdecl` disables the name mangiling of function main
so it can be linked against the startup code.

`fmt::print#` is a macro call. All macros names must end in "#".

# Lexical Elements

## Base Types

* `u8`, `u16`, `u32`, `u64`  unsigned int in various widths
* `uint`  unsigned int big enough to hold a pointer
* `s8`, `s16`, `s32`, `s64`  signed int in various widths
* `sint`  signed int big enough to hold a pointer
* `r32`, `r64`  floating points  in various widths
* `typeid` unsigned int big enough to hold a type tag
* `bool`
* `void`

## Booleam Literals

`true`, `false`

There is no concept of truthiness

## String Literals

Regular string literals are enclosed in double-quotes. e.g. "escaped string\n" and may contain back-slash escapes. Most single character escapes are supported
('\n', '\t',  '\\', etc).
Also supported are hexadecimal escape ('\xff') but **not** octal escapes.

Unescaped (aka raw) strings are prefixed with "r", e.g. (r"string").

Hex strings are prefixed with x, e.g. (x"de ad be ef") and ignore all white space
characters.

Multi-line strings are enclosed in tripple quotes, e.g. """multi-line string:"""",
and also come in unescaped (prefix "r") and hex (prefix "x") flavors.

## Number Literals

Number literals may contain underscores ("_") which are ignored. Since Cwerg does not implicitly convert numbers it is often necessary use typed number by adding one of the following suffices: u8, u16, u32, u64, s8, s16, s32, s64, r32, r64, e.g. "0x1234_s16".




## Module Level Declations

By default all top level desclations are module private.
The `@pub` annotation will export the annotated symbol.

Note, the declarations listed here can only appear at the module
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


### Type Definitions

Type abbreviations can be declared like so:
```
type t1 = s32
```
This is strictly and abbreviation, so `t1` and `s32` can be used interchangably in the code.

To force by name type equivalence in this case, use the `@wrapped` annotation like so
```
@wrapped type t1 = s32
```
The type `t1` is said to be a wrapped type.

### Enums

Enums can be declared like so:

```
enum Color u8:
    blue 1
    green auto
    red 19
```

This declares an enum `Color` with 3 members (`red`, `green`, `blue`)
with an underlying type of `u8`.
`auto` used the previously asigned value incremented by 1.

Enums are C-like in that they are essentially named integer constants.


#### Records

Records can be declared like so:

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

### If-else Statements

### Cond Statements

### Defer Statements


### Return Statements

### Continue Statements

### Break Statements

### Trap Statements

### Do Statements

## Type Expressions

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
