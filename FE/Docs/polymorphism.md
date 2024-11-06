# Polymorphism

Besides parameterized modules, Cwerg supports a limited form of (ad-hoc) polymorphism for functions.
There is no dynamic dispatch as everything is resolved at compile-time.

Example:
```
fun SysRender@(v u8, out span!(u8)) uint:
    return FmtDecU8(v, out)
```

**Note the trailing "@" which indicates that a function is polymorphic.**

This example has two effects:

1. It defines a function that render an `u8` value in decimal into the buffer `out` and returns the number of characters written.
2. It registers a family of functions named `SysRender@` that only differ in their first argument.



Functions can be added to this family by re-using the name  like so
```
fun SysRender@(v u32, out span!(u8)) uint:
    return FmtDecU32(v, out)
```

Note, this function has a different first parameter type for the first argument while the other stay the same.
**Cwerg's polymorphism applieds to the first argument only!**

Printing in hex instead of decimal could be accomplished like so:

```
pub wrapped type u32_hex = u32

fun SysRender@(v u32_hex, out span!(u8)) uint:
    return FmtHexU32(unwrap(v), out)
```

Assuming the functions above are defined in a module named `fmt` they can be called like so:
```
    ...
    ref let! buf_raw = [1024]u8{}
    let! buf span!(u8) = buf_raw
    set buf = IncSpan(buf, fmt::SysRender@(666_u32, buf))
    set buf = IncSpan(buf, fmt::SysRender@(66_u8, buf))
    set buf = IncSpan(buf, fmt::SysRender@(
        wrap_as(666,  fmt:: u32_hex), buf))
    ...
```

Defining SysRender@ for a data type in another module can be accomplished like so:
```
rec Point:
    x u32
    y u32

fun fmt::SysRender@(v Point, out span!(u8)) uint:
    let! buf = out
    set buf = IncSpan(buf, fmt::SysRender@(v.x, buf))
    set buf = IncSpan(buf, fmt::SysRender@(", ", buf))
    set buf = IncSpan(buf, fmt::SysRender@(v.y, buf))
    return len(out) - len(buf)

```

Note, that the definition uses a `qualified` name referencing the family of
polymorphic function we want to add to.
