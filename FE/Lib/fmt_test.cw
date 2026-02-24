module:

import test

import fmt

pub enum color s32:
    black 0
    white 1
    blue 2
    green 3
    red 4

poly fun fmt\SysRender(v color, out span!(u8), options ^!fmt\SysFormatOptions)
  uint:
    return fmt\SysRender(unwrap(v), out, options)

pub rec ic32:
    real s32
    imag s32

poly fun fmt\SysRender(v ic32, s span!(u8), opt ^!fmt\SysFormatOptions) uint:
    let! n uint = 0
    set n = fmt\SysRender(v.real, s, opt)
    set n += fmt\SysRender("+", span_inc(s, n), opt)
    set n += fmt\SysRender(v.imag, span_inc(s, n), opt)
    set n += fmt\SysRender("i", span_inc(s, n), opt)
    return n

global test_string span(u8) = "qwerty_1234"

fun test_custom() void:
    ref let! opt = {fmt\SysFormatOptions:}
    let! buffer = {[fmt\FORMATED_STRING_MAX_LEN]u8:}
    ref let! s span!(u8) = buffer
    let! n uint = 0
    ; complex
    set n = fmt\SysRender({ic32: 111, 222}, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "111+222i")
    ; enum
    set n = fmt\SysRender(color.blue, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "2")

fun test_int() void:
    ref let! opt = {fmt\SysFormatOptions:}
    let! buffer = {[fmt\FORMATED_STRING_MAX_LEN]u8:}
    ref let! s span!(u8) = buffer
    let! n uint = 0
    set n = fmt\SysRender(666_uint, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "666")
    set n = fmt\SysRender(69_u16, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "69")
    set n = fmt\SysRender(-69_s32, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "-69")

fun test_real() void:
    ref let! opt = {fmt\SysFormatOptions:}
    let! buffer = {[fmt\FORMATED_STRING_MAX_LEN]u8:}
    ref let! s span!(u8) = buffer
    let! n uint = 0
    set n = fmt\SysRender(wrap_as(2, fmt\r64_hex), s, @!opt)
    ; (fmt\print# s " \n")
    test\AssertSliceEq#(make_span(front(s), n), "0x1.p+1")
    set n = fmt\SysRender(666e+20_r64, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "6.660000e+22")

fun test_misc() void:
    ref let! opt = {fmt\SysFormatOptions:}
    let! buffer = {[fmt\FORMATED_STRING_MAX_LEN]u8:}
    ref let! s span!(u8) = buffer
    let! n uint = 0
    set n = fmt\SysRender(true, s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "true")
    set n = fmt\SysRender(wrap_as(120, fmt\rune), s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "x")
    set n = fmt\SysRender(wrap_as(test_string, fmt\str_hex), s, @!opt)
    test\AssertSliceEq#(make_span(front(s), n), "7177657274795f31323334")

fun main(argc s32, argv ^^u8) s32:
    do test_int()
    do test_misc()
    do test_custom()
    do test_real()
    ; test end
    test\Success#()
    return 0
