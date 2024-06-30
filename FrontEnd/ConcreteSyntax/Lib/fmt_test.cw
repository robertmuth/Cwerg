module:

import test

import fmt

pub enum color s32:
    black 0
    white 1
    blue 2
    green 3
    red 4

fun fmt::SysRender@(v color, out slice!(u8), options ^!fmt::SysFormatOptions) uint:
    return fmt::SysRender@(unwrap(v), out, options)

pub rec ic32:
    real s32
    imag s32

fun fmt::SysRender@(v ic32, s slice!(u8), opt ^!fmt::SysFormatOptions) uint:
    let f = front!(s)
    let l = len(s)
    let! n uint = 0
    set n = fmt::SysRender@(v.real, s, opt)
    set n += fmt::SysRender@("+", slice(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@(v.imag, slice(pinc(f, n), l - n), opt)
    set n += fmt::SysRender@("i", slice(pinc(f, n), l - n), opt)
    return n

global test_string slice(u8) = "qwerty_1234"

fun main(argc s32, argv ^^u8) s32:
    @ref let! opt = fmt::SysFormatOptions{}
    let! buffer = [fmt::FORMATED_STRING_MAX_LEN]u8{}
    @ref let! s slice!(u8) = buffer
    let! n uint = 0
    set n = fmt::SysRender@(666_uint, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "666")
    set n = fmt::SysRender@(true, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "true")
    set n = fmt::SysRender@(69_u16, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "69")
    set n = fmt::SysRender@(-69_s32, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "-69")
    set n = fmt::SysRender@(wrap_as(120, fmt::rune), s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "x")
    set n = fmt::SysRender@(wrap_as(2, fmt::r64_hex), s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "0x1.p1")
    set n = fmt::SysRender@(color:blue, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "2")
    set n = fmt::SysRender@(ic32{111, 222}, s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "111+222i")
    set n = fmt::SysRender@(wrap_as(test_string, fmt::str_hex), s, &!opt)
    test::AssertSliceEq#(slice(front(s), n), "7177657274795f31323334")
    -- test end
    test::Success#()
    return 0
