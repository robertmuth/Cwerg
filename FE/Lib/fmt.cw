module:

import os

import fmt_int

import fmt_real

pub @extern fun memcpy(dst ^!u8, src ^u8, size uint) ^!u8:

pub global FORMATED_STRING_MAX_LEN uint = 4096

pub fun mymemcpy(dst ^!u8, src ^u8, size uint) uint:
    for i = 0, size, 1:
        set pinc(dst, i)^ = pinc(src, i)^
    return size

-- This gets passed to the actual formatters which decide how to interpret the options.
pub rec SysFormatOptions:
    -- min width
    witdh u8
    precission u8
    padding u8
    style u8
    show_sign bool
    left_justify bool

fun SysRender@(v bool, buffer span!(u8), options ^!SysFormatOptions) uint:
    let s = v ? as("true", span(u8)) : as("false", span(u8))
    let n uint = len(buffer) min len(s)
    return mymemcpy(front!(buffer), front(s), n)

pub fun str_to_u32(s span(u8)) u32:
    let! x = 0_u32
    for i = 0, len(s), 1:
        set x *= 10
        let c = s[i]
        set x += as(c - '0', u32)
    return x

fun SysRender@(v u8, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v u16, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v u32, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v u64, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v s16, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v s32, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtDec@(v, out)

fun SysRender@(v span(u8), buffer span!(u8), options ^!SysFormatOptions) uint:
    let n uint = len(buffer) min len(v)
    return mymemcpy(front!(buffer), front(v), n)

fun SysRender@(v span!(u8), buffer span!(u8), options ^!SysFormatOptions) uint:
    let n uint = len(buffer) min len(v)
    return mymemcpy(front!(buffer), front(v), n)

pub wrapped type uint_hex = uint

pub wrapped type u64_hex = u64

pub wrapped type u32_hex = u32

pub wrapped type u16_hex = u16

pub wrapped type u8_hex = u8

fun SysRender@(v uint_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtHex@(unwrap(v), out)

fun SysRender@(v u64_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtHex@(unwrap(v), out)

fun SysRender@(v u32_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtHex@(unwrap(v), out)

fun SysRender@(v u16_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtHex@(unwrap(v), out)

fun SysRender@(v u8_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int::FmtHex@(unwrap(v), out)

pub wrapped type rune = u8

fun SysRender@(v rune, buffer span!(u8), options ^!SysFormatOptions) uint:
    if len(buffer) == 0:
        return 0
    else:
        set front!(buffer)^ = unwrap(v)
        return 1

pub wrapped type r64_hex = r64

fun SysRender@(v r64_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_real::FmtHex@(unwrap(v), out)

fun SysRender@(v r64, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_real::FmtE@(v, 6, false, out)

pub wrapped type str_hex = span(u8)

fun to_hex_digit(digit u8) u8:
    return digit <= 9 ? digit + '0' : digit + ('a' - 10)

fun SysRender@(v str_hex, out span!(u8), options ^!SysFormatOptions) uint:
    let v_str span(u8) = unwrap(v)
    let dst_len = len(v_str)
    if dst_len <= len(out):
        for i = 0, dst_len, 1:
            let c u8 = v_str[i]
            let o1 uint = i * 2
            let o2 uint = o1 + 1
            set out[o1] = to_hex_digit(c >> 4)
            set out[o2] = to_hex_digit(c and 15)
        return dst_len * 2
    else:
        for i = 0, len(out), 1:
            set out[i] = '.'
        return 0

fun SysRender@(v ^void, out span!(u8), options ^!SysFormatOptions) uint:
    let h = wrap_as(bitwise_as(v, uint), uint_hex)
    return SysRender@(h, out, options)

pub macro print# STMT_LIST(
    -- list of items to be printed
    $parts EXPR_LIST_REST)[$buffer, $curr, $options]:
    mlet! $buffer = [FORMATED_STRING_MAX_LEN]u8{}
    mlet! $curr uint = 0
    ref mlet! $options = SysFormatOptions{}
    mfor $i $parts:
        set $curr += SysRender@(
                $i, span(pinc(front!($buffer), $curr), len($buffer) - $curr), &!$options)
    do os::write(unwrap(os::Stdout), front($buffer), $curr)

-- same as above but takes an EXPR_LIST - should only be used by other macros
pub macro print_list# STMT_LIST($parts EXPR_LIST)[$buffer, $curr, $options]:
    mlet! $buffer = [FORMATED_STRING_MAX_LEN]u8{}
    mlet! $curr uint = 0
    ref mlet! $options = SysFormatOptions{}
    mfor $i $parts:
        set $curr += SysRender@(
                $i, span(pinc(front!($buffer), $curr), len($buffer) - $curr), &!$options)
    do os::write(unwrap(os::Stdout), front($buffer), $curr)

pub fun strz_to_slice(s ^u8) span(u8):
    let! i uint = 0
    while pinc(s, i)^ != 0:
        set i += 1
    return span(s, i)

pub macro assert# STMT($cond EXPR, $parts EXPR_LIST_REST)[]:
    if $cond:
    else:
        print#(stringify($cond))
        print_list#($parts)
        trap