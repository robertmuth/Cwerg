module:

import test

type type_array = [3]bool

type type_slice = span(s32)

global c1 = [10]s32{1, 2, 3}

global! c2 = [10]s32{1, 2, 3}

--  (let c20 auto (len c1)")
--          "(let c21 auto (at c1 2))") 
global dim = 5_u16

fun foo(a [10]u8, b [dim]u64) u8:
    let v2 = c1[0]
    let v3 = &c1[0]
    let v4 = &!c2[0]
    set c2[0] = 666
    return 66

fun update_array(s span!(u8), pos uint, new u8) u8:
    let old = s[pos]
    set s[pos] = new
    return old

-- ERROR: (let f4 (span mut s32) e1)
fun baz() void:
    -- ERROR: (= (at c1 5) 0)
    let pc1 ^s32 = front(c1)
    set c2[5] = 0

pub rec type_rec3:
    u2 u16
    u3 u64
    u5 [10]u8
    u6 u64

global! r1 = type_rec3{u5 : [10]u8{77, 88, 99}}

global! c4 = [10]u8{41, 51, 61}

fun test_mixed_array() void:
    -- 
    @ref let! a = [10]u8{1, 2, 3}
    let pa = &a
    let pa_mut = &!a
    test::AssertEq#(c4[2], 61_u8)
    set c4 = a
    test::AssertEq#(c4[2], 3_u8)
    set c4[2] = 4_u8
    set a = c4
    test::AssertEq#(a[2], 4_u8)
    test::AssertEq#(r1.u5[1], 88_u8)
    set r1.u5 = a
    test::AssertEq#(r1.u5[1], 2_u8)
    set r1.u5[1] = 111
    set a = r1.u5
    test::AssertEq#(a[1], 111_u8)

fun test_local_array() void:
    -- 
    @ref let! a = [10]u8{1, 2, 3}
    @ref let b = [10]u8{4, 5, 6}
    let pa = &a
    let pa_mut = &!a
    let pb = &b
    test::AssertEq#(a[0], 1_u8)
    test::AssertEq#(b[2], 6_u8)
    set a[0] = 6
    test::AssertEq#(a[0], 6_u8)
    set pa_mut^[2] = 77_u8
    test::AssertEq#(pa^[2], 77_u8)
    test::AssertEq#(pa_mut^[2], 77_u8)
    test::AssertEq#(pb^[0], 4_u8)
    set pa_mut^[0] = 66
    test::AssertEq#(a[0], 66_u8)
    set a = b
    test::AssertEq#(a[0], 4_u8)
    test::AssertEq#(update_array(a, 0, 2), 4_u8)
    test::AssertEq#(update_array(a, 0, 3), 2_u8)
    test::AssertEq#(update_array(pa_mut^, 0, 2), 3_u8)

global d1 = [10]s32{11, 22, 33}

global! d2 = [10]s32{111, 222, 333}

global! c3 = [10]u8{4, 5, 6}

global e1 span(s32) = d1

global e2 span!(s32) = d2

global e3 = [5]s32{0, 1, 2, 3, 4}

global e4 = [2]span(s32){e1, e1}

-- ERROR
--        (global e5 (span (span s32)) e4)
--        (global e3 (span mut s32) d2)
global f1 span(s32) = e1

global f3 span(s32) = e2

global f2 span!(s32) = e2

fun test_global_array() void:
    -- basic
    test::AssertEq#(c1[1], 2_s32)
    test::AssertEq#(c2[2], 3_s32)
    test::AssertEq#(e1[1], 22_s32)
    test::AssertEq#(e2[2], 333_s32)
    test::AssertEq#(f1[1], 22_s32)
    test::AssertEq#(f2[2], 333_s32)
    test::AssertEq#(f3[0], 111_s32)
    -- basic
    test::AssertEq#(c3[0], 4_u8)
    test::AssertEq#(update_array(c3, 0, 77), 4_u8)
    test::AssertEq#(update_array(c3, 0, 5), 77_u8)
    test::AssertEq#(len(e1), 10_uint)

fun main(argc s32, argv ^^u8) s32:
    do test_global_array()
    do test_local_array()
    do test_mixed_array()
    -- test end
    test::Success#()
    return 0
