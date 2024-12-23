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


`(ptr t)` or `(ptr @mut t)`

### vecs

`(vec dim t)`

Note the dimesion is part of the type.

`(len array)` will return the dimension of the array
which is a compile time constant.

`(front vec)`  or  `(front @mut vec)`  will return
a pointer to the first element of the vec.



### spans

`(span t)`
`(span @mut t)`


`(len span)` will return the length of the span.
`(front span)`  or  `(front @mut span)`  will return
a pointer to the first element of the span.

`(front @mut span)`  can only be applied to `(span @mut t)`.

spans are essentially records of the form

`((ptr  t), uint)`
`((ptr  @mut t), uint)`


and will be lowered as such.

### Records


### Untagged Sum Types

`(sum @untagged [t1 t2 t3])`

* untagged sums are like unions in C


### (Tagged) Sum Types

`(sum @untagged [t1 t2 t3])`

### Function Types


### Adhoc Polymorphism