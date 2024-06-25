module:

import test

@pub rec type_rec1:
    -- this is a comment with \" with quotes \t 
    i1 s64
    i2 u64
    i3 s32
    i4 u32
    i5 s16
    i6 u16
    i7 s8
    i8 u8
    f1 r64
    f2 r32
    b1 bool
    a1 [7]u8
    a2 [7]u16
    a3 [7]u32
    a4 [7]u64
    a5 [7]r32
    a6 [7]r64

@pub rec type_rec2:
    t1 bool
    t2 u32
    t3 type_rec1
    t4 bool

@pub rec type_rec3:
    u2 u16
    u3 u64
    u4 type_rec2
    u5 [13]u16
    u6 u64

global! ga1 [5]s64 = undef

global! gr1 type_rec1 = undef

global! gar1 [5]type_rec1 = undef

global! gr2 type_rec2 = undef

global! gar2 [5]type_rec2 = undef

fun get_addr() ^!type_rec1:
    return &!gr1

@cdecl fun main(argc s32, argv ^^u8) s32:
    -- a1 u32
    set ga1[3] = 0x8765432187654321
    test::AssertEq#(ga1[3], 0x8765432187654321_s64)
    set ga1[3] += 0x1
    test::AssertEq#(ga1[3], 0x8765432187654322_s64)
    -- gr1 s64
    set gr1.i1 = 0x8765432187654321
    test::AssertEq#(gr1.i1, 0x8765432187654321_s64)
    set gr1.i1 += 0x1
    test::AssertEq#(gr1.i1, 0x8765432187654322_s64)
    -- gr1 u64
    set gr1.i2 = 0x1234567812345678
    test::AssertEq#(gr1.i2, 0x1234567812345678_u64)
    set gr1.i2 -= 0x1
    test::AssertEq#(gr1.i2, 0x1234567812345677_u64)
    -- gr1 u64 via pointer
    set get_addr()^.i2 = 0x1234567812345678
    test::AssertEq#(get_addr()^.i2, 0x1234567812345678_u64)
    set get_addr()^.i2 -= 0x1
    test::AssertEq#(get_addr()^.i2, 0x1234567812345677_u64)
    -- gar1 s64
    set gar1[3].i1 = 0x8765432187654321
    test::AssertEq#(gar1[3].i1, 0x8765432187654321_s64)
    -- gr2 s64
    set gr2.t3.i1 = 0x8765432187654321
    test::AssertEq#(gr2.t3.i1, 0x8765432187654321_s64)
    set gr2.t3.i1 += 0x1
    test::AssertEq#(gr2.t3.i1, 0x8765432187654322_s64)
    -- gr2 u64
    set gr2.t3.i2 = 0x1234567812345678
    test::AssertEq#(gr2.t3.i2, 0x1234567812345678_u64)
    -- test end
    test::Success#()
    return 0
