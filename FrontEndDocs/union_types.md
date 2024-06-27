# Union Types

## Basics

An `untagged union` mimics C style unions except that there are no field names only types.
Hence each field (member of the union) must have a distinct type.
This limitation can be worked around using wrapped types
which create new types from existing ones.
Unions must have at least two members.

Example:

```
type Union1 @untagged union(s32 void ^!s32)
```
This represents a union of 3 members: s32, void and ^!s32.
Note that void is valid member for unions.


A `tagged union` can be thought of as a pair of
* a `tag` (a small interger of type `typeid`) and
* an `untagged union`.

Given a tagged union `u` the two components can be retrieved using
`uniontag(u)` and `unionuntagged(u)`.


Example:

```
-- working around the distinct type requirement
@wrapped type t1 s32
type Union1 union(s32, t1)

-- one or more wrapped void types can be used as error code
@wrapped type error1 void
@wrapped type error2 void

type Union2 union(void, error1, error2)

-- nullable pointers can be modelled like so
type Union3 union(void, ^!u8)
```

Union types are order independent:
```
type Union1 union(s32. void, type_ptr)
type Union2 union(void. s32. type_ptr)

static_assert typeidof(Union1) ==  typeidof(Union2)
```

Union types are duplicate eliminating

```
type Union1 union(void, type_ptr)

type Union2 union(void, void, type_ptr)

static_assert typeidof(Union1) ==  typeidof(Union2)
```

Unions are "auto flattening", e.g.:

```
type Union1 union(s32, void, type_ptr)

type Union2 union(s32, void, union(Union1, u8))

type Union3 union(s32, void, u8, type_ptr)

static_assert typeidof(Union2) ==  typeidof(Union3)

```

One can create a new union that is the set difference
of two unions or a union and an individual type:

```
type Union1 union(s32, void, s64, u8)
type Union2 union(s32, void)

type Delta1 uniondelta(Union1, Union2)
static_assert typeid(Delta1) == typeid(union(u8, s64))

type Delta2 uniondelta(Union2, void))
static_assert typeid(Delta2) == typeid(s32)

```

## Initialization and Implicit Widening

A typed variable, parameter, field-element, return value, etc. of type union `u` can be initialized using an expression whose type is

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
(type Union1 (union [ s16 void u32 ]))

(let! u  Union1 ...)
(let! v  Union1 ...)

(let! x  u32 ...)

```

The following expressions are valid:

```
... (!= u 222_s16) ...

... (== u 222_s32) ...
... (!= u 222_s32) ...

... (== u void_val) ...
... (!= u void_val) ...

... (== u v) ...
... (!= u v) ...

... (== u x) ...
... (!= u x) ...

@doc "not supported:"
... (== u v) ...
... (!= u v) ...

```

## Runtime type queries

The `is` operator can be used to test if the run-time type of a tagged union belongs to one or more of the member types.


Examples
```
(type Union1 (union [ s16 void u32 ]))

(let! u  Union1 ...)

.. (is u s16) ..
.. (is u (union  [ s16 void ])) ..


```

## Narrowing

Narrowing of values of a union type is possible with the `narrowto` operator.

For `tagged unions` the narrowing can be explicitly marked as `@unchecked`.

For `untagged unions` there is nothing to check.

Assuming `u` is of type `tu`  and `v`, `z` are of type `tv`,
we need to consider the following cases:

### case: ut is untagged union

```
(= z (narrowto u tv))
```

#### tv ∈ member-types(tu)

This is always valid:


`z` is set to the bits of `u` truncated to `(sizeof tv)`

####  tv is untagged union where member-types(tv) ⊆ member-types(tu)

This is always valid:

The value of `z` are the bits of `u` truncated to `(sizeof tv)`.


### case: ut is tagged union unchecked

```
(= z (narrowto @unchecked u tv))
```

#### tv ∈ member-types(tu)

This is only valid if  `(uniontypetag u) == (typeid tv)`:
But the assumption is not checked.

The value of `z` are the bits of `(unionuntagged u)` truncated to `(sizeof tv)`.

####  tv is tagged union where member-types(tv) ⊆ member-types(tu)


This is onlt valid if `(uniontypetag u) ∈  member-type-ids(tv)`:
But the assumption is not checked.

The value of `z` is a tagged union where

`(uniontypetag z)`:  `(uniontypetag u)`

`(unionuntagged z)`:   `(unionuntagged u)` truncated to
`(sizeof (unionuntagged tv))`


### case: ut is tagged union checked

```
(= z (narrowto u tv))
```

#### tv ∈ member-types(tu)

This will check if  `(uniontypetag u) == (typeid tv)` and trap if it is not.
Otherwise, the value of `z` are the bits of `(unionuntagged u)` truncated to `(sizeof tv)`.

#### tv is tagged union where member-types(tv) ⊆ member-types(tu)

This will check if `(uniontypetag u) ∈  member-type-ids(tv)`
and trap if it is not.

Otherwise, the value of `z` is a tagged union where

`(uniontypetag z)`:  `(uniontypetag u)`

`(unionuntagged z)`:   `(unionuntagged u)` truncated to
`(sizeof (unionuntagged tv))`


Note, that checking `(uniontypetag u) ∈  member-type-ids(tv)` is equivalent
to `(uniontypetag u) ∉  member-type-ids((uniondelta tu tv))` which may be faster to check.

## Lowering / CodeGen


* EliminateImplicitConversions()
  This introduces explicit `widento` operators for
  * FieldVal (value_or_undef)
  * DefVar (initial_or_undef)
  * DefGlobal (initial_or_undef)
  * ExprCall (args)
  * ExprWrap (expr)
  * StmtReturn (expr)
  * StmtAssignment (expr_rhs)

* EliminateComparisonConversionsForTaggedUnion()
  This introduces unchecked `narrowto`nodes - see function comment.


* SimplifyTaggedExprNarrow()
  This replaces all checked narrowto expressions and simplifies
  narrowto expressions that narrow to a non-union

* ReplaceSums
  Replaces all tagged unions with structs representing underlying the tag and the untagged union