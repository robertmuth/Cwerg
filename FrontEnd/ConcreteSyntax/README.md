# Cwerg Syntax and Semantics (Work In Progress)

Cwerg's syntax is inspired by Python. Indentation levels are significant.

Cwerg is statically type with limited type inference at the statement level.
In declarations and defintions the type immediately follows the identifier as in go-lang.

Semantically, Cwerg is closer to C but with many foot guns removed and features added.
The guiding principle is to make things that are unsafe, hard to reason about,
hard to optimize, etc. possible but not the default.

In a somewhat random order the changes are:

### Constants, Variables and Assignment

All variables, pointer expression and pointer types are readonly by default.
(For pointers that means the data pointed to cannot be modified via the pointer.)

Appending a `!` will result in the corresponding writable flavor:

| Readonly  |  Read/Write | Description |
| --------- | --------- | -------- |
| global    | global!   | Define a global constant/variable |
| let       | let!      | Define a local constant/variable
| &         |  &!       | Get Address of constant/variable |
| front     | front!    | Get Address if first element in array or slice |
| ptr       |  ptr!     | Pointer Type |
| slice     | slice!    | Slice Type |


Converting a readonly pointer to a read/write pointer or
obtaining a read/write pointer to non-mutable causes type errors.
(An unsafe cast is available to override this.)

Assignments are preceeded by the `set` keyword.

```
let! x s32 = 6
set x = 5
set x += 1
```

Note:

```
let x s32 = 6
set x = 5  -- compiler error x is not mutable
```



### Statements vs Expressions

All statements have introductory keywords.
Statements and expressions are strictly separated.

```
set x += foo()  -- assignment expresssion

bar() -- compiler error function calls are expressions and cannot be used as statement
drop bar() -- OK, drop ignores result of expression which makes it into a statement.
```

`--` and `++` are not part of the language as they blur the distinction between expressions
and statements.

### optionally named blocks with optionally named continue and break

```
block outer:
    block:
        if condition:
            break  -- breaks from the inner loop
        if other_condition:
            break outer
        ...
        continue  -- go to the beginning of inner loop
    continue  -- go to the beginning of outer loop
```



### defer

Statements in a defer block are executed when the enclosing scope is exited.
The code inside the defer block must not jump out of it. So a defer block must either reach its end or trap.

```
fun foo () void:
    print# ("enter foo\n")
    defer:
        print# ("exit foo\n")
    ...
    block:
        print# ("enter block\n")
        defer:
            print# ("exit block\n")
        ...
    ...
    return

```


### no null pointers

`null` does not exist as a language concept but there are tagged unions that can be used to emulate nullable types:

```
type nullable_u8_pointer = union(ptr(u8), void)
```

The plan is to special case this kind of union in the compiler and avoid the tag, so there should be no performance penalty.



### tagged unions

unions are tagged by default and are essentially sum types.
The member types are not named, so all of them must be different.
This limitation can (and should) be worked around via wrapped types.

Among other things, tagged unions can be used for
* optional or maybe types (nullable pointer fall in this category)
* result types



More info here:  [Unions](../../FrontEndDocs/union_types.md)

### default zero initialization

All variables/constants are zero initialized by default.
This can be prevented with the `undef` initializer.


### global defininitions (variable, functions, types, macros, ..,) are private by default

An explicit `@pub` annotation is required to make symbols visible for export.
This will also apply to record fields.

### modules/namespaces

Everything lives in a module. Modules may NOT be nested. Import chains may not have cycles.

### arrays and slices

The dimension of an array is part of the type:

`array(100, u8)` is incompatible with `array(99, u8)`

slices are available to model arrays with unknown dimension at compile time.

Taking the address of an array results in a pointer to an array
not the element type. To get a pointer to the first element use
`front`.

Indexing of arrays and slices employs bounds-checking unless explicitly disabled via
an annotation.


### Implicit conversions

Only the following conversions are implicit:

* read/write pointers/slices to readonly pointer/slices
* arrays to the corresponding slice type
* instance of a member type of union to an instance of that union

There are no implicit conversions for numeric type.
However it is often possible to use untyped numerical constants
because of the limited type inference:
```
-- all these are equivalent
let x u64 = 66
let x = 66_u64
let x u64 = 66_u64

-- because x is of type u64, 77 is type infered to be u64 as well
let y = x + 77
```

### pointer arithmetic

Pointer arithmetic is supported but is syntactically more involved.

```

let i u32 = ...
let! p ptr(u16) = ...
let! q ptr(u16) = ...
set p = pinc(s, i)  -- equivalent of C `p + i`
set p = pinc(s, i, 1000)  -- same as above but trap if i >= 1000


let d = p &-& q  -- set d to `p - q``


```

### Macros


There is basic macro support for more information see

[Macros](../../FrontEndDocs/macros.md)
