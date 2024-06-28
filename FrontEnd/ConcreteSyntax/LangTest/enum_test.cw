module:

import test

pub enum enum8 u8:
    e1 7
    e2 auto
    e3 19
    e4 auto

pub enum enum16 u16:
    e1 70
    e2 auto
    e3 190
    e4 auto

pub enum enum32 u32:
    e1 700
    e2 auto
    e3 1900
    e4 auto

-- GLOBAL
global! g1 = enum8:e1

global! g2 = enum16:e2

global! g3 = enum32:e3

pub rec rec1:
    -- this is a comment with \" with quotes \t 
    f1 s32
    f2 s32
    f3 s32
    f4 bool
    f5 enum8
    f6 enum16
    f7 enum32
    f8 u64
    f9 u64

global! gr1 rec1 = undef

@cdecl fun main(argc s32, argv ^^u8) s32:
    -- LOCAL
    let! v1 = enum8:e2
    let! v2 = enum16:e3
    let! v3 = enum32:e4
    test::AssertEq#(g1, enum8:e1)
    test::AssertEq#(g2, enum16:e2)
    test::AssertEq#(g3, enum32:e3)
    set g1 = v1
    set g2 = v2
    set g3 = v3
    test::AssertEq#(g1, enum8:e2)
    test::AssertEq#(g2, enum16:e3)
    test::AssertEq#(g3, enum32:e4)
    set v1 = enum8:e3
    set v2 = enum16:e4
    set v3 = enum32:e1
    test::AssertEq#(v1, enum8:e3)
    test::AssertEq#(v2, enum16:e4)
    test::AssertEq#(v3, enum32:e1)
    set gr1.f5 = enum8:e3
    set gr1.f6 = enum16:e4
    set gr1.f7 = enum32:e1
    test::AssertEq#(gr1.f5, enum8:e3)
    test::AssertEq#(gr1.f6, enum16:e4)
    test::AssertEq#(gr1.f7, enum32:e1)
    -- test end
    test::Success#()
    return 0
