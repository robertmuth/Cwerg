# Cwerg Language Overview

Cwerg tries to find the right balance between language expressiveness and compiler implementation complexity. The hope is to reach a sweet spot above what C gives us today. A language that makes it convenient to write system software like operating systems and compilers.


## Philosophy

Above all Cwerg is meant to be a small language that can be maintained by a single person. Since small is subjective we have set a complexity budget for about 10kLOC for a compiler frontend with basic optimizations.

## Highlights

* Low level, C-like language: no GC, no unexpected control flow
* defer statement (scheduling code to run code at scope exit)
* tagged unions (sum types)
* optionally wrapped types (by-name type equivalence)
* modules (not nested)
* generics via generic modules
* simple hygienic macro system
* limited polymorphism
* slices (array views)
* named blocks + multi-level break/continue
* expression statements - cleaned up version of the C's comma operator
* (almost) no implicit conversions and no truthinesss
* all value are zero initialized by default
* visibility is private by default
* array indexing is checked by default
* variables are immutable by default
* no goto, no va-args, no bitfields,


## Syntax

Cwerg currently has two syntaxes:

1. Sexpr syntax that is close to the AST
2. Python inspired concrete syntax

The two syntaxes are intended to be equivalent
and one can be translated to the other without
loss of information.


## Concrete Syntax Examples

Cwerg use a Python inspired syntax where the indentation level
is significant.

We give some examples below to convey a general feeling for the language.
The details should become clear after reading through the tutorial.

More examples can be found here: https://github.com/robertmuth/Cwerg/tree/master/FrontEnd/ConcreteSyntax/TestData


### Hello World (full example)

```
module:

import fmt

@cdecl fun main(argc s32, argv ^^u8) s32:
    fmt::print#("hello world\n")
    return 0

```

Every file starts with a module stanza.

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

-- a mutable global array of bools initialized to `true`
-- index i reprents number 3 + 2 * i
global! is_prime = [N]bool{true}

-- Count the number of primes below n
fun sieve() uint:
    let! count uint = 1
    -- the type of `i`  is determined by `N`
    for i = 0, N, 1:
        if is_prime[i]:
            set count += 1
            let p uint = i + i + 3
            for k = i + p, N, p:
                set is_prime[k] = false
    return count
```

Exclamtion marks at the end of keywords indicate mutability.

## Binary Tree (parameterized/generic module)

```
module(
        -- the payload type
        $type TYPE,
        -- the less-than function ($type x $type) -> bool
        $lt CONST_EXPR):

@pub global Leaf = void

@pub rec Node:
    left union(void, ^!Node)
    right union(void, ^!Node)
    payload $type

-- same as above for left and right
@pub type MaybeNode = union(void, ^!Node)

type Visitor = funtype(node ^$type) void

@pub fun InorderTraversal(root MaybeNode, visitor Visitor) void:
    trylet node ^!Node = root, _:
        return
    do InorderTraversal(node^.left, visitor)
    do visitor(&node^.payload)
    do InorderTraversal(node^.right, visitor)

-- returns the new root
@pub fun Insert(root MaybeNode, node ^!Node) ^!Node:
    set node^.left = Leaf
    set node^.right = Leaf
    trylet curr ^!Node = root, _:
        return node
    if $lt(&node^.payload, &curr^.payload):
        set curr^.left = Insert(curr^.left, node)
    else:
        set curr^.right = Insert(curr^.right, node)
    return curr

```

## Type System

Cwerg's type system is similar to C's with the following differences

* there are very few implicit conversions
* pointers cannot be null
* there is a stronger emphasis on "const/mutability correctness"
* arrays do not decay to to pointers and arrays of different sizes
  are different types
* slices can be used where array-like objects with variable length are required
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
The caret goes in front of type.

```
-- pointer to a u32
^u32

-- pointer to a mutable u32
^!u32
```

### Arrays

Array dimension go in front of the element type:

```
-- 10 element array of element type u32
    [10]u32

```

Array of different length are not compatible and
are different from pointers to the element type.
```
static_assert typeidof([10]u32) != typeidof([2]u32)
static_assert typeidof([10]u32) != typeidof(^u32)
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
`auto` is using the previously asigned value incremented by 1 or zero if it is the first member.  So in the above example we get:
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


This is strictly an abbreviation, the lhs and the rhs can be used interchangably in the code.

To force by name type equivalence in this case, use the `@wrapped` annotation like so
```
@wrapped type t1 = funtype(x u8, y u8) u1
```
The type `t1` is said to be a wrapped type.



### (Tagged) Unions


Tagged unions can be declared like so:

```
union(s32, void, u8, ^sint, [32]u8))
```

Note, that there are no names - only types. In case that the same type is
needed twice in a single union, wrapped types can be used.

The annotation `@untagged` changes a union to untagged.

Unions are: order independent, duplicate eliminating, and auto-flattening.
In the example below `u1` and `u2` are the same type:
```
type u1  = union (u8, s64, union(u8, s32), union(u8, void))
type u2  = union (s64, s32, void, u8))
static_assert typeidof)u1)  ==  typeidof)u2)
```

More info in [Unions](union_types.md)


## Literals


### Booleam Literals

`true`, `false`

There is no concept of truthiness.


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
module:
    <TOP-LEVEL-DECLARATIOND>+
```

A more complex definition for the generic case looks like:

```
module optional-name(param-name1 param-kind1, param-name2 param-kind2, ...):
    <TOP-LEVEL-DECLARATIOND>+
```

All module parameters must start with a '$' (similar to macro parameters)
and must be have one of the following kinds:
* CONST_EXPR: a constant expression including a function
* TYPE: a type expression


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


### Functions

Functions are declared like so:

```
 fun foo(param1 typ1, param2 type2, ...) returntype:
    <STATEMENTS>*
```

### Enums, Types (Typedefs) and Recs (Structs)

These were covered in the Type Section above


#### Macros

TBD  - see [Macros](macros.md)


### Static Asserts

TBD


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


### Let Statements (Local Variables)


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
...
set a_local_const += 666;
set a_local_const and= 666;

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
Controlflow will resume at the next statement after block if
the control flow falls throuh the last statement of the block.
```
block <NAME>?:
    <STAREMENTS>*
```

A `continue` statement inside the block will set controlflow to the beginning
of the block and a `break` statement will exit the block.
Both  `continue` and `break` statements can have an optional label indicating
which enclosing `block` they refer to.


### While Loops

```
while <CONDITION>:
    <STAREMENTS>*
```


### For Loops

```
for var-name = initial-expr, limit-expr, step-expr:
    <STAREMENTS>*
```

For loops differ from their C counterparts in the following way:
* they are mostly meant for ranging over a sequence of integers
* initial-expr, limit-expr, step-expr are evaluated once at the beginning
* the type of var-name is determined by the type of limit-expr

If you need a for loop to iterated over a custom data-structure, define
a macro.


### If-else Statements

Simple
```
if condition:
    <STAREMENTS>*
```

With else clause

```
if condition:
    <STAREMENTS>*
else:
    <STAREMENTS>*
```


### Cond Statements

```
cond:
    case condition1:
        <STAREMENTS>*
    case condition2:
        <STAREMENTS>*
    ...
```

Note, there is no fallthrough.
Case are checked in order.
A `default` case  be expressed as `case true`
and must go last.


### Defer Statements

```
defer:
    <STAREMENTS>*
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
```
    block label1;

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


### Expression Statements

Expression Statements are code blocks that evalute to a value. Examples

```
let x s8 = foo()
let sign s8 = expr:
                  cond:
                    case x == 0:
                        return 0_s8
                    case x < 0
                        return -1_s8
                    case true:
                        return 1_s8

```


### Casts


TBD  - see [Casting](casting.md)


| Notation          | Description                                |
| ----------------- | ------------------------------------------ |
| as(E, T) -> E     | casts with run-time checks                 |
| wrapas(E, T) -> E | convert expression to a wrapped type       |
| bitas(E, T) -> E  | convert expression to a type of same width |
