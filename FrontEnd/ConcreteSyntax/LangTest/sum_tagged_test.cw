module main:

import test

@wrapped type t1 = s32

@wrapped type t2 = void

@wrapped type t3 = void

type type_ptr = ^!s32

type Union1 = union(s32, void, type_ptr)

static_assert sizeof(Union1) == 16

type Union2 = union(s32, void, union(Union1, u8))

static_assert sizeof(Union2) == 16

type Union2Simplified = union(s32, void, u8, type_ptr)

static_assert typeid(Union2) == typeid(Union2Simplified)

type Union3 = union(bool, u8, s32, s64)

static_assert sizeof(Union3) == 16

type Delta1 = uniondelta(Union3, union(bool, u8, s32))

static_assert sizeof(Delta1) == 8

static_assert typeid(Delta1) == typeid(s64)

type Delta2 = uniondelta(Union3, union(bool, u8))

static_assert typeid(Delta2) == typeid(union(s32, s64))

type Delta3 = uniondelta(Union3, union(bool, u8, s64))

static_assert typeid(Delta3) == typeid(s32)

@pub type Union5 = union(t2, t3, s8)

static_assert sizeof(Union5) == 3

type Union6 = union(bool, u16)

static_assert sizeof(Union6) == 4

type Union = union(bool, u64, u32, r32, r64, [32]u8)

static_assert sizeof(Union) == 40

rec rec1:
    s1 Union5
    s2 Union5

@pub rec rec2:
    s1 Union1
    s2 Union2

global global_rec1 = rec1{1_s8, 2_s8}

-- 
-- @pub (type sum11_t (union [bool u16]))
-- @pub (type sum12_t (union [type_ptr u16])) 
fun test_tagged_union_basic() void:
    let! x Union3 = true
    let! y Union3 = undef
    let! z s32 = 777
    set y = x
    test::AssertTrue#(is(x, bool))
    test::AssertFalse#(is(x, s32))
    test::AssertTrue#(is(y, bool))
    test::AssertFalse#(is(y, s32))
    set x = 777_s32
    set x = z
    set y = x
    test::AssertFalse#(is(x, bool))
    test::AssertTrue#(is(x, s32))
    test::AssertFalse#(is(y, bool))
    test::AssertTrue#(is(y, s32))
    test::AssertTrue#(y == 777_s32)
    test::AssertTrue#(777_s32 == y)

@pub type UnionVoid = union(void, t2, t3)

fun test_tagged_union_void() void:
    let! x UnionVoid = void

fun fun_param(a bool, b bool, c s32, x Union3) void:
    if a:
        test::AssertTrue#(is(x, bool))
    else:
        test::AssertTrue#(is(x, s32))

fun test_tagged_union_parameter() void:
    let! x Union3 = true
    do fun_param(true, true, 0, x)
    set x = 666_s32
    do fun_param(false, true, 666, x)

fun fun_result(a bool, b bool, c s32) Union3:
    let! out Union3 = undef
    if a:
        set out = b
    else:
        set out = c
    return out

fun test_tagged_union_result() void:
    let! x = fun_result(true, false, 2)
    test::AssertTrue#(is(x, bool))
    test::AssertFalse#(is(x, s32))
    set x = fun_result(false, false, 2)
    test::AssertFalse#(is(x, bool))
    test::AssertTrue#(is(x, s32))

fun test_tagged_union_narrowto() void:
    let! x Union3 = true
    let! y = narrowto(x, bool)
    test::AssertTrue#(y)
    test::AssertTrue#(narrowto(x, bool))
    let! z = narrowto(x, union(u8, bool))

@cdecl fun main(argc s32, argv ^^u8) s32:
    do test_tagged_union_basic()
    do test_tagged_union_void()
    do test_tagged_union_result()
    do test_tagged_union_parameter()
    do test_tagged_union_narrowto()
    -- test end
    test::Success#()
    return 0
