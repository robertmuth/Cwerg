module:

import test

pub rec type_rec1:
    ; this is a comment with \" with quotes \t
    s1 s32
    ; s2 comment
    s2 s32
    ; s3 is ...
    s3 s32
    s4 bool
    s5 u64
    s6 u64

pub rec type_rec2:
    t1 bool
    t2 u32
    t3 type_rec1
    t4 bool

pub rec type_rec3:
    u2 u16
    u3 u64
    u4 type_rec2
    u5 [13]u16
    u6 u64

pub rec type_rec4:
    t1 u64
    t2 u8
    t3 u16
    t4 u32
    t5 bool

global u0 u32 = 0x12345678

; g0 is i mportant
global g0 type_rec1 = undef

global g1 [5]type_rec1 = undef

global g2 = {type_rec2: true, u0}

global! g3 = {type_rec3: 0x1234, 0x4321, g2, {[13]u16: 0x11, undef, 0x12}}

global! g3_alt = {type_rec3: 0x1234, 0x4321, g2, {[13]u16: 0x11, undef, 0x12}}

; BROKEN init
global g4 = {[4]type_rec2: undef, g2}

pub rec type_rec5:
    t1 u64
    t2 span!(u8)
    t5 bool

global! buffer = {[3]u8: 0, 0, 0}

global g5 type_rec5 = undef

global g6 type_rec5 = {type_rec5: 0, buffer, false}

global g7 = {[1]type_rec5:
             {type_rec5: 0, buffer, false}}

; single element rec
pub rec rec_type8:
    t1 u32



fun test_rec_basic() void:
    let! g8 = {rec_type8: 66}
    set g8.t1 = 123
    test::AssertEq#(g8.t1, 123_u32)

fun main(argc s32, argv ^^u8) s32:
    ; LOCAL
    let! v1 = {type_rec3:}
    set v1.u2 = 102
    set v1.u3 = 103
    set v1.u6 = 106
    test::AssertEq#(v1.u2, 102_u16)
    test::AssertEq#(v1.u3, 103_u64)
    test::AssertEq#(v1.u6, 106_u64)
    set v1.u4.t1 = false
    set v1.u4.t2 = 402
    test::AssertEq#(v1.u4.t2, 402_u32)
    test::AssertEq#(v1.u4.t1, false)
    set v1.u5[2] = 502
    set v1.u5[3] = 503
    set v1.u5[10] = 510
    test::AssertEq#(v1.u5[2], 502_u16)
    test::AssertEq#(v1.u5[3], 503_u16)
    test::AssertEq#(v1.u5[10], 510_u16)
    ; GLOBAL ALT
    test::AssertEq#(g3_alt.u2, 0x1234_u16)
    test::AssertEq#(g3_alt.u3, 0x4321_u64)
    test::AssertEq#(g3_alt.u4.t1, true)
    test::AssertEq#(g3_alt.u4.t2, 0x12345678_u32)
    test::AssertEq#(g3_alt.u5[0], 0x11_u16)
    test::AssertEq#(g3_alt.u5[2], 0x12_u16)
    ; GLOBAL
    test::AssertEq#(g3.u2, 0x1234_u16)
    test::AssertEq#(g3.u3, 0x4321_u64)
    test::AssertEq#(g3.u4.t1, true)
    test::AssertEq#(g3.u4.t2, 0x12345678_u32)
    test::AssertEq#(g3.u5[0], 0x11_u16)
    test::AssertEq#(g3.u5[2], 0x12_u16)
    set g3.u2 = 102
    set g3.u3 = 103
    set g3.u6 = 106
    test::AssertEq#(g3.u2, 102_u16)
    test::AssertEq#(g3.u3, 103_u64)
    test::AssertEq#(g3.u6, 106_u64)
    set g3.u4.t1 = false
    set g3.u4.t2 = 402
    test::AssertEq#(g3.u4.t2, 402_u32)
    test::AssertEq#(g3.u4.t1, false)
    set g3.u5[2] = 502
    set g3.u5[3] = 503
    set g3.u5[10] = 510
    test::AssertEq#(g3.u5[2], 502_u16)
    test::AssertEq#(g3.u5[3], 503_u16)
    test::AssertEq#(g3.u5[10], 510_u16)

    do test_rec_basic()

    ; test end
    test::Success#()
    ; return
    return 0
