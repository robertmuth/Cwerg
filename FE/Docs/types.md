## Cwerg Language Typesystem

### Basic Types



| Name     | Byte Width | Alignment | Description                                |
| -------- | ---------- | --------- | ------------------------------------------ |
| `s8`     | 1          | 1         | signed 8 bit int (two's complement)        |
| `s16`    | 2          | 2         | signed 16 bit int (two's complement)       |
| `s32`    | 4          | 4         | signed 32 bit int (two's complement)       |
| `s64`    | 8          | 8         | signed 64 bit int( two's complement)       |
| `sint`   | platform   | dependent | signed similar to ssize_t                  |
| `u8`     | 1          | 1         | unsigned 8 bit int                         |
| `u16`    | 2          | 2         | unsigned 16 bit int                        |
| `u32`    | 4          | 4         | unsigned 32 bit int                        |
| `u64`    | 8          | 8         | unsigned 64 bit int                        |
| `uint`   | platform   | dependent | unsigned int similar to size_t             |
| `typeid` | project   | dependent | unsigned int large enough to hold a typeid |
| `r32`    | 4          | 4         | 32 bit floating point (ieee)               |
| `r64`    | 8          | 8         | 64 bit floating point (ieee)               |
| `bool`   | 1          | 1         | bool                                       |
| `void`   | n/a        | n/a       |                                            |

Note:
* not all sizes are available on all systems, e.g. s64 and u64 are usually not available on 32 bit
  systems.
* `sint`` and `uint`` are large enough to hold a native pointer
* `typeid` must be larger than the total count of all types in a program 16 bit should be
  sufficient for most projects.

### Enums



### Wrapped Types

### Pointer Types

* `^u32` pointer to a readonly `u32`
*`^!u32` pointer to a writable `u32`


### vecs

* `[dim]u32`  vector of length `dim` of elements of type `u32`
   `dim` must be evaluable at compile-time

Note the dimesion is part of the type.

`len(v)` will return the dimension of the vetor `v`
which is a compile time constant.

`front(v)`  or  `(front!(v)`  will return
a pointer to the first element of the vec.



### spans

`span(t)`
`span!(t)`


`len(span)` will return the length of the span.
`front(span)`  or  `front!(span)`  will return
a pointer to the first element of the span.

`front!(span)`  can only be applied to `span!(t)`.

spans are essentially records of the form

`(^t, uint)`
`(^!t), uint)`


and will be lowered as such.

### Records


### Untagged Sum Types

`union!(t1, t2, t3)`

* untagged sums are like unions in C


### (Tagged) Sum Types

`union!(t1, t2, t3)`

### Function Types

`type type_fun = funtype(a bool, b bool, c s32) s32`


### Adhoc Polymorphism