-- union
module main:

import test

@wrapped type t1 = s32

@wrapped type t2 = void

@wrapped type t3 = void

type type_ptr = ^!s32

type UntaggedUnion1 = @untagged union(s32, void, type_ptr)

static_assert sizeof(UntaggedUnion1) == 8

type UntaggedUnion2 = @untagged union(
        s32, void, @untagged union(UntaggedUnion1, u8))

static_assert sizeof(UntaggedUnion2) == 8

type UntaggedUnion3 = @untagged union(bool, s32, s64)

static_assert sizeof(UntaggedUnion2) == 8

type UntaggedUnion4 = @untagged union(bool, s32)

static_assert sizeof(UntaggedUnion4) == 4

@pub type UntaggedUnion5 = @untagged union(t2, t3, s8)

static_assert sizeof(UntaggedUnion5) == 1

type UntaggedUnion6 = @untagged union(bool, u16)

static_assert sizeof(UntaggedUnion6) == 2

type UntaggedUnion = @untagged union(bool, u64, u32, r32, r64, [32]u8)

type TaggedUnion = union(bool, u64, u32, r32, r64, [32]u8)

static_assert sizeof(UntaggedUnion) == 32

rec RecordWithUntaggedUnion:
    t1 bool
    t2 u32
    t3 UntaggedUnion
    t4 bool

fun with_union_result(a bool, b u32, c r32) UntaggedUnion:
    let! out UntaggedUnion = undef
    if a:
        set out = b
    else:
        set out = c
    return out

fun test_untagged_union() void:
    -- straight up union
    let! u1 UntaggedUnion
    let! u2 UntaggedUnion = undef
    let! u3 UntaggedUnion = 2.0_r32
    let! u4 UntaggedUnion = 777_u32
    let s1 u32 = narrowto(u3, u32)
    test::AssertEq#(s1, 0x40000000_u32)
    test::AssertEq#(narrowto(u3, [32]u8)[0], 0_u8)
    test::AssertEq#(narrowto(u3, [32]u8)[1], 0_u8)
    test::AssertEq#(narrowto(u3, [32]u8)[2], 0_u8)
    test::AssertEq#(narrowto(u3, [32]u8)[3], 0x40_u8)
    set narrowto(u3, [32]u8)[2] = 0x28_u8
    set narrowto(u3, [32]u8)[3] = 0x42_u8
    test::AssertEq#(narrowto(u3, u32), 0x42280000_u32)
    test::AssertEq#(narrowto(u3, r32), 42_r32)
    set u3 = 2.0_r64
    test::AssertEq#(narrowto(u3, u64), 0x4000000000000000_u64)
    test::AssertEq#(narrowto(u3, [32]u8)[3], 0_u8)
    test::AssertEq#(narrowto(u3, [32]u8)[7], 0x40_u8)
    -- union embedded in record
    let! rec1 RecordWithUntaggedUnion = undef
    set rec1.t3 = 2.0_r32
    test::AssertEq#(narrowto(rec1.t3, u32), 0x40000000_u32)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[0], 0_u8)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[1], 0_u8)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[2], 0_u8)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[3], 0x40_u8)
    -- union embedded in record 2
    let! rec2 = RecordWithUntaggedUnion{false, 0x12344321, 2.0_r32, true}
    test::AssertEq#(rec2.t1, false)
    test::AssertEq#(rec2.t2, 0x12344321_u32)
    test::AssertEq#(narrowto(rec2.t3, u32), 0x40000000_u32)
    test::AssertEq#(rec2.t4, true)
    -- 
    set narrowto(rec1.t3, [32]u8)[2] = 0x28_u8
    set narrowto(rec1.t3, [32]u8)[3] = 0x42_u8
    test::AssertEq#(narrowto(rec1.t3, u32), 0x42280000_u32)
    test::AssertEq#(narrowto(rec1.t3, r32), 42_r32)
    set rec1.t3 = 2.0_r64
    test::AssertEq#(narrowto(rec1.t3, u64), 0x4000000000000000_u64)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[3], 0_u8)
    test::AssertEq#(narrowto(rec1.t3, [32]u8)[7], 0x40_u8)
    -- array of union
    let! array1 [16]UntaggedUnion = undef
    set array1[13] = 2.0_r32
    test::AssertEq#(narrowto(array1[13], u32), 0x40000000_u32)
    test::AssertEq#(narrowto(array1[13], [32]u8)[0], 0_u8)
    test::AssertEq#(narrowto(array1[13], [32]u8)[1], 0_u8)
    test::AssertEq#(narrowto(array1[13], [32]u8)[2], 0_u8)
    test::AssertEq#(narrowto(array1[13], [32]u8)[3], 0x40_u8)
    set narrowto(array1[13], [32]u8)[2] = 0x28_u8
    set narrowto(array1[13], [32]u8)[3] = 0x42_u8
    test::AssertEq#(narrowto(array1[13], u32), 0x42280000_u32)
    test::AssertEq#(narrowto(array1[13], r32), 42_r32)
    set u1 = with_union_result(true, 10, 2.0)
    test::AssertEq#(narrowto(u1, u32), 10_u32)
    set u1 = with_union_result(false, 10, 2.0)
    test::AssertEq#(narrowto(u1, u32), 0x40000000_u32)
    set array1[13] = 2.0_r64
    test::AssertEq#(narrowto(array1[13], u64), 0x4000000000000000_u64)
    test::AssertEq#(narrowto(array1[13], [32]u8)[3], 0_u8)
    test::AssertEq#(narrowto(array1[13], [32]u8)[7], 0x40_u8)

@cdecl fun main(argc s32, argv ^^u8) s32:
    shed test_untagged_union()
    -- test end
    test::Success#()
    return 0
