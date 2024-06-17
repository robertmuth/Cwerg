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
