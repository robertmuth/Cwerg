# Union/Sum Types

## Basics

An `untagged union` mimics C style unions except that each member must have a distinct type
because there are no field names. This limitation can be worked around using wrapped types
which create new types from existing ones.

Example:

```
(type UntaggedUnion1 (union @untagged [ s32 void (ptr @mut s32)]))
```
This represents a union of 3 fields/types: s32, void and (ptr @mut s32).
Note that void is valid field/type for unions.


A `tagged union` can be thought of as a pair of
* a `tag` (a small interger of type `typeid`) and
* an `untagged union`.

Given a tagged union the two components can be retrieved using
`sumtypetag` and `sumuntagged`.


Example:

```
(type @wrapped t1 s32)
(type type_ptr (ptr @mut s32))

(type TaggedUnion (union [ s32 void type_ptr ]))

(type @wrapped t2 void)
(type @wrapped t3 void)

(type @pub TaggedUnionVoid (union [ void t2 t3 ]))
```

Union types are auto flattening, duplicate eliminating and order independent:

```
(type TaggedUnion1 (union [ s32 void type_ptr ]))

(type TaggedUnion2 (union [ s32 void (union [TaggedUnion1 u8])]))

(type TaggedUnion2Simplified (union [s32 void u8 type_ptr]))

(static_assert (== (typeid TaggedUnion2) (typeid TaggedUnion2Simplified)))
```

## Initialization and Implicit Widening

A typed variable, parameter, field-element, return, etc. of type union u can be initialized using
an expression whose type is
* any of the underlying types of u
* another union v where
  * v and u are either both tagged or both untagged
  * the underlying types of v are a subset of the underlying types of u

This amounts to an explicit type widening which can also be made explicit using
`ExprWide`. No run-time type check is necessary here.

## Equality Testing

Only tagged unions support equality testing only against values of the underlying types.

Assuming
```
(type TaggedUnion1 (union [ s16 void u32 ]))

(let @mut u  TaggedUnion1 ...)
```

The following expressions are valid:
```
... (== u 222_s16) ...
... (!= u 222_s16) ...

... (== u 222_s32) ...
... (!= u 222_s32) ...

... (== u void_val) ...
... (!= u void_val) ...

```

## Narrowing

Narrowing of values of a union type is possible with `ExprNarrow`.
For `tagged unions` the narrowing can be explicitly marked as `@unchecked`.
For `untagged unions` there is nothing to check anyway.

In order to avoid runtime type inspection narrowing is subject to restriction show below,
assuming the underlying types of v are a subset of the underlying types of u:

### case: u, v are untagged unions

This is always valid:
```
... (narrowto u (typeof v)) ...
```
The value of the expression are the bits of u truncated to `(sizeof (typeof v))`

### case: u, v are tagged unions, unchecked

TBD

###case: u, v are tagged unions, (checked)

TBD

