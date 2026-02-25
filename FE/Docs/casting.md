# Cwerg Casting and Implicit Conversion

## Overview

| Notation              | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| wrap_as(E, T) -> E    | convert value to enum or wrapped type                                |
| unwrap(E) -> E        | convert  enum or wrapped type to underlying type                     |
| narrow_as(E, T) -> E  | convert union value to actual type (may involve a check)             |
| widen_as(E, T) -> E   | convert value to union                                               |
| as(E, T) -> E         | converts between  numerical types                                    |
| bitwise_as(E, T) -> E | convert expression to a type of same width, including int to pointer |
| unsafe_as(E, T) -> E  | convert between pointers                                             |

## `wrap_as` / `unwrap`

`unwrap` converts a value of a wrapped type or enum type to the underlying type.

```
enum color u8:
    red 1
    green 2
    blue 3

static_assert unwrap(color.green) == 2_u8

```

`wrap_as` is the inverse operation:

```
static_assert wrap(2, color) == color.green
```

Another example using wrapped type (`type!` indicates a wrapped type)
```
type! temperature_celsius = u16

global freezing_point auto = wrap_as(100, temperature_celsius)
```

## narrowing / widening (`narrow_as` / `widen_as`)

Narrowing describes the conversion from a union value to an individual
type of that union or a subset of that union.

If the union is tagged, this will include a typeid check which can be disabled with
the `@unchecked` attribute.

Explicit widening, i.e. the conversion for a value to a union the includes that value,
is rarely needed since Cwerg does this implicitly.

## Regular/numerical cast (`as`)

Conversation between these numerical types attempting
to preserve the value as much as possible

* u8, u16, u32, u64
* s8, s16, s32, s64
* r32, r64

## Bitcasts (`bitwise_as`)

* s32/u32 <-> r32
* s64/u64 <-> r64
* sint/uint <-> ptr T
* ptr a <-> ptr b
* ptr a <-> mut ptr a
* span a <-> mut span a


## No cast required (implicit conversion)

### drop mutability

mut ptr T -> ptr T
mut slice T -> slice T

### convert to a wider union


sum A|B|C -> sum A|B|C|D|E
A -> sum A|B|C|D|E

This can be made explcit with the `widen_as` operation
but is rarely needed.

### array to slice conversion

mut array T size -> mut slice T
mut array T size -> slice T
array T size -> slice T

For array constants `array T size -> slice T`
will materialized the array constant in
readonly memory.
