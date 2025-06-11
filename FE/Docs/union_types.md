# Union Types

## Basics

An `untagged union` mimics C style unions except that there are no field names only types.
Hence each field (member of the union) must have a distinct type.
This limitation can be worked around using wrapped types
which create new types from existing ones.
Unions must have at least two members.

Example:

```
type Union1 = union!(s32, void, ^s32)
```
This represents a union of 3 members: s32, void and ^s32.
Note that void is valid member for unions.
The exclamation mark at the end of the 'union' keyword changes default of a
tagged union to an untagged one.

A `tagged union` can be thought of as a pair of
* a `tag` (a small interger of type `typeid`) and
* an `untagged union`.

Given a tagged union `u` the two components can be retrieved using
`uniontag(u)` and `unionuntagged(u)`.


Example:

```
-- working around the distinct type requirement
wrapped type t1 = s32
type Union1 = union(s32, t1)

-- one or more wrapped void types can be used as error code
wrapped type error1 = void
wrapped type error2 = void

type Union2 = union(void, error1, error2)

-- nullable pointers can be modelled like so
type Union3 = union(void, ^u8)
```

Union types are order independent:
```
type Union1 = union(s32, void, ^u8)
type Union2 = union(void, s32, ^u8)

static_assert typeidof(Union1) ==  typeidof(Union2)
```

Union types are duplicate eliminating

```
type Union1 = union(void, ^u8)

type Union2 = union(void, void, ^u8)

static_assert typeidof(Union1) ==  typeidof(Union2)
```

Unions are "auto flattening", e.g.:

```
type Union1 = union(s32, void, ^u8)

type Union2 = union(s32, void, union(Union1, u8))

type Union3 = union(s32, void, u8, ^u8)

static_assert typeid_of(Union2) ==  typeid_of(Union3)

```

One can create a new union that is the set difference
of two unions or a union and an individual type:

```
type Union1 = union(s32, void, s64, u8)
type Union2 = union(s32, void)

type Delta1 = union_delta(Union1, Union2)
static_assert typeid_of(Delta1) == typeid_of(union(u8, s64))

type Delta2 = union_delta(Union2, void))
static_assert typeid_of(Delta2) == typeid_of(s32)

```

## Initialization and Implicit Widening

A variable declartion, call argument, field-element, return value, etc. of type union `u` can be initialized using an expression whose type is

* any of the underlying types of `u`
* another union `v` where
  * `v` and `u` are either both tagged or both untagged
  * the member types of `v` are a subset of the member types of `u`

This amounts to an explicit type widening which can also be made explicit using the `widen_as` operator. No run-time type check is necessary here.

## Equality Testing

Only tagged unions support equality testing.
One can compare a tagged union against a value of one of its member types.
Internally this works by first checking if the types match and then narrowing
the tagged union and compare the resulting value;

**Not supported**: comparison of two tagged unions (even of the same type).

Assuming
```
type Union1 = union(s16, void, u32)

let! u  Union1 = ...
let! v  Union1 = ...

let! x  u32 = ...

```

The following expressions are valid

```
... != u != 222_s16 ...

... u == 222_s32 ...
... u != 222_s32 ...

... u == void_val ...
... u != void_val ...

... u == x ...
... u != x ...

-- not supported:
... u == v ...
... u != v ...

```

## Runtime type queries

The `is` operator can be used to test if the run-time type of a tagged union belongs to one or more of the member types.


Examples
```
type Union1 = union(s16, void, u32)

let! u  Union = ...

.. is(u, s16) ...
.. is(u, union(s16, void)) ...


```

## Narrowing

Narrowing of values of a union type is possible with the `narrow_as` operator.

For `tagged unions` the narrowing can be explicitly marked as unchecked by using
 `narrow_as!` (note the extra exclamation mark).


For `untagged unions` there is nothing to check.

Assuming `u` is of type `tu`  and `v`, `z` are of type `tv`,
we need to consider the following cases:

### case: tu is untagged union

#### tv is not a union but tv ∈ member-types(tu)

```
   set z = narrow_as(u,  tv)
```

This is always valid:


`z` is set to the bits of `u` truncated to `size_of(tv)`

####  tv is untagged union where member-types(tv) ⊆ member-types(tu)

```
   set z = narrow_as(u,  tv)
```

This is always valid:

The value of `z` are the bits of `u` truncated to `size_of(tv)`.


### case: tu is tagged union - unchecked narrowing

####  tv is not a union but tv ∈ member-types(tu)

```
   set z = narrow_as!(u, tv)
```

This is only valid if  `union_tag(u) == typeid_of(tv)`:
But the assumption is not checked.

The value of `z` are the bits of `union_untagged(u)` truncated to `size_of(tv)`.

####  tv is tagged union where member-types(tv) ⊆ member-types(tu)

```
   set z = narrow_as!(u, tv)
```

This is onlt valid if `union_tag(u) ∈  member-type-ids(tv)`:
But the assumption is not checked.

The value of `z` is a tagged union where

`union_tag(z)` is set to  `union_tag(u)`

`union_untagged(z)` is set to `union_untagged(u)` truncated to
`size_of(union_untagged(tv))`


### case: ut is tagged union - checked narrowing


#### tv is not a union but tv ∈ member-types(tu)

```
    set z = narrowto(u, tv)
```

This will check if  `union_tag(u) == typeid of(tv)` and trap if it is not.
Otherwise, the value of `z` are the bits of `union_untagged(u)` truncated to `size_of(tv)`.

#### tv is tagged union where member-types(tv) ⊆ member-types(tu)

```
    set z = narrowto(u, tv)
```

This will check if `union_tag(u) ∈  member-type-ids(tv)`
and trap if it is not.

Otherwise, the value of `z` is a tagged union where

`union_tag(z)`:  is set to `union_tag(u)`

`union_untagged(z)` is set to `union_untagged(u)` truncated to
`size_of(union_untagged(tv))`


Note, that checking `union_tag(u) ∈  member-type-ids(tv)` is equivalent
to `union_tag(u) ∉  member-type-ids((union_delta(tu, tv))` which may be faster to check.

## Lowering / CodeGen


* EliminateImplicitConversions()
  This introduces explicit `widen_as` operators for
  * FieldVal (value_or_undef)
  * DefVar (initial_or_undef)
  * DefGlobal (initial_or_undef)
  * ExprCall (args)
  * StmtReturn (expr)
  * StmtAssignment (expr_rhs)

* EliminateComparisonConversionsForTaggedUnion()
  This introduces unchecked `narrow_as` nodes - see function comment.


* SimplifyTaggedExprNarrow()
  This replaces all checked narrowto expressions and simplifies
  narrowto expressions that narrow to a non-union

* ReplaceSums
  Replaces all tagged unions with structs representing underlying the tag and the untagged union