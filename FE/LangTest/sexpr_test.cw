module:

pub fun foo1(a s32, b s32, c s32) s32:
    do foo1(0, 0, 0)
    do foo2(1, 2, 3)
    return 7

pub global! v1 = 7_u64

pub global v1a = @!v1

fun foo2(a s32, b s32, c s32) s32:
    if a <= b:
        set v1a^ = 666
    if !(a <= b):
        set v1 += 666
    return 7

wrapped type t1 = s32

pub global c1 = 7_s64

pub rec type_rec:
    s1 s32
    s2 s32
    s3 s32
    s4 s32
    b1 bool
    u1 u64
    u2 u64

pub rec one_field_rec:
    the_field r32

pub rec one_one_field_rec:
    the_field one_field_rec

global c2 = offset_of(type_rec, s1)

pub enum type_enum s32:
    s1 7
    s2 auto
    s3 19
    s4 auto

type type_ptr = ^!s32

pub type type_union = union(s32, void, type_ptr)

fun foo3(a bool, b bool, c s32) bool:
    if a and b:
        return a
    else:
        return a xor b
    if a <= b:
    return a == b

fun foo4(a s32, b s32, c s32) ^u8:
    let p1 ^u8 = undef
    let p2 ^u8 = undef
    if p1 == p2:
    let p3 = false ? p1 : p2
    block my_block:
        break
        continue
        break
        continue
    return p1

fun foo5(c s32) bool:
    return c < expr:
            return 6


fun foo6(c s32) s32:
    return 55_s32 * (c + 44)

fun square(c s32) s32:
    return c * c

fun double(c s32) s32:
    return c + c

fun square_or_double(use_square bool, c s32) s32:
    let foo = use_square ? square : double
    return foo(c)

-- just a compilation test
fun main(argc s32, argv ^^u8) s32:
    return 0
