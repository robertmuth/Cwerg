-- expr
module:

fun assoc1(a u32, b u32, c u32, d u32) u32:
    return a + b - c + d

fun assoc2(a u32, b u32, c u32, d u32) u32:
    return (a + b) * (c + d)

fun assoc3(a u32, b u32, c u32, d u32) u32:
    return a min b max (c min d)

@cdecl fun main(argc s32, argv ^^u8) s32:
    return 0
