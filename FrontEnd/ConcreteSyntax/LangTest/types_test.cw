module:

@wrapped type t1 = s32

@wrapped type t2 = void

@wrapped type t3 = void

pub rec type_rec:
    -- this is a comment with \" with quotes \t
    s1 s32
    s2 s32
    s3 s32
    s4 s32
    b1 bool
    u1 u64
    u2 u64

pub rec linked_list:
    -- this is a comment with \" with quotes \t
    s1 union(void, ^linked_list)

pub enum type_enum s32:
    -- this is a comment with \" with quotes \t
    s1 auto
    s2 auto
    s3 auto
    s4 auto

type type_array = [3]bool

type type_slice = slice(type_rec)

type type_ptr = ^!s32

pub type type_union = union(s32, void, type_ptr)

pub type type_union2 = union(s32, void, union(type_union, u8))

type type_fun = funtype(a bool, b bool, c s32) s32

fun funx(a type_union) s32:
    return narrow_as(a, union_delta(type_union, union(void, type_ptr)))

-- just a compilation test
fun main(argc s32, argv ^^u8) s32:
    return 0
