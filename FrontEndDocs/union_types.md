# Union  Types

## Basics

An `untagged union` mimics C style unions except that there are no field names only types.
Hence each field (member of the union) must have a distinct type.
This limitation can be worked around using wrapped types
which create new types from existing ones.
Unions must have at least two members.

Example:

```
(type UntaggedUnion1 (union @untagged [ s32 void (ptr @mut s32)]))
```
This represents a union of 3 members: s32, void and (ptr @mut s32).
Note that void is valid member for unions.


A `tagged union` can be thought of as a pair of
* a `tag` (a small interger of type `typeid`) and
* an `untagged union`.

Given a tagged union `u` the two components can be retrieved using
`(uniontypetag u)` and `(unionuntagged u)`.


Example:

```
(type @wrapped t1 s32)
(type type_ptr (ptr @mut s32))

(type TaggedUnion (union [ s32 void type_ptr ]))

(type @wrapped t2 void)
(type @wrapped t3 void)

(type @pub TaggedUnionVoid (union [ void t2 t3 ]))
```


A union with only one member is equivalent to that member:
```
(type Union1 (union [ s32 ]))

(static_assert (== (typeid Union1) (typeid s32)))
```

Union types are order independent:
```
(type Union1 (union [ s32 void type_ptr ]))
(type Union2 (union [ void s32 type_ptr ]))

(static_assert (== (typeid Union1) (typeid Union2)))
```

Union types are duplicate eliminating

```
(type Union1 (union [ void type_ptr ]))

(type Union2 (union [ void void type_ptr ]))

(static_assert (== (typeid Union1) (typeid Union2)))
```

Unions are "auto flattening", e.g.:

(type Union1 (union [ s32 void type_ptr ]))

(type Union2 (union [ s32 void (union [Union1 u8])]))

(type Union3 (union [ s32 void u8 type_ptr]))

(static_assert (== (typeid Union2) (typeid Union3)))
```

One can create a new union that is the set difference
of two unions or a union and an individual type:

```
(type Union1 (union [ s32 void s64 u8]))
(type Union2 (union [ s32 void]))

(type Union3 (uniondelta Union1 Union2))
(static_assert (== (typeid Union3) (typeid (union [ u8 s64 ]))))

(type Union3 (uniondelta Union1 Union2))
```


## Initialization and Implicit Widening

A typed variable, parameter, field-element, return value, etc. of type union `u` can be initialized using
an expression whose type is
* any of the underlying types of u
* another union v where
  * v and u are either both tagged or both untagged
  * the underlying types of v are a subset of the underlying types of u

This amounts to an explicit type widening which can also be made explicit using `widento`. No run-time type check is necessary here.

## Equality Testing

Only tagged unions support equality testing.
One can compare two tagged unions of the same type or
a tagged union against a value of one of its member types.
In the latter case implicit widening is used.

Assuming
```
(type Union1 (union [ s16 void u32 ]))

(let @mut u  Union1 ...)
(let @mut v  Union1 ...)

(let @mut x  u32 ...)

```

The following expressions are valid:
```
... (== u 222_s16) ...
... (!= u 222_s16) ...

... (== u 222_s32) ...
... (!= u 222_s32) ...

... (== u void_val) ...
... (!= u void_val) ...

... (== u v) ...
... (!= u v) ...

... (== u x) ...
... (!= u x) ...

```

## Narrowing

Narrowing of values of a union type is possible with `narrowto`.
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
