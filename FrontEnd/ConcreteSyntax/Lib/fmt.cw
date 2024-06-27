module:

import os

@pub @extern fun memcpy(dst ^!u8, src ^u8, size uint) ^!u8:

@pub global FORMATED_STRING_MAX_LEN uint = 4096

@pub fun mymemcpy(dst ^!u8, src ^u8, size uint) uint:
    for i = 0, size, 1:
        set pinc(dst, i)^ = pinc(src, i)^
    return size

-- This gets passed to the actual formatters which decide how to interpret the options.
@pub rec SysFormatOptions:
    -- min width
    witdh u8
    precission u8
    padding u8
    style u8
    show_sign bool
    left_justify bool

fun SysRender@(v bool, buffer slice!(u8), options ^!SysFormatOptions) uint:
    let s = v ? as("true", slice(u8)) : as("false", slice(u8))
    let n uint = len(buffer) min len(s)
    return mymemcpy(front!(buffer), front(s), n)

macro unsigned_to_str# EXPR(
        $val EXPR, $base EXPR, $max_width EXPR, 
        -- a slice for the output string
        $out EXPR)[$v, $out_eval, $tmp, $pos]:
    expr:
        -- unsigned to str with given base
        mlet! $v = $val
        mlet! $tmp = [1024]u8{}
        mlet! $pos uint = $max_width
        mlet $out_eval = $out
        block _:
            set $pos -= 1
            let c = $v % $base
            let! c8 = as(c, u8)
            set c8 += c8 <= 9 ? '0' : 'a' - 10
            set $tmp[$pos] = c8
            set $v /= $base
            if $v != 0:
                continue
        let n uint = $max_width - $pos min len($out_eval)
        return mymemcpy(front!($out_eval), pinc(front($tmp), $pos), n)


fun slice_incp(s slice!(u8), inc uint) slice!(u8):
    let n uint = inc min len(s)
    return slice(pinc(front!(s), n), len(s) - n)

fun DecToStr@(v u8, out slice!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

fun DecToStr@(v u16, out slice!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

fun DecToStr@(v u32, out slice!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

fun DecToStr@(v u64, out slice!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

fun DecToStr@(v s32, out slice!(u8)) uint:
    if len(out) == 0:
        return 0
    if v < 0:
        let v_unsigned = 0_s32 - v
        set out[0] = '-'
        return 1 + unsigned_to_str#(v_unsigned, 10, 32_uint, slice_incp(out, 1))
    else:
        return DecToStr@(as(v, u32), out)

@pub fun str_to_u32(s slice(u8)) u32:
    let! x = 0_u32
    for i = 0, len(s), 1:
        set x *= 10
        let c = s[i]
        set x += as(c - '0', u32)
    return x

fun SysRender@(v u8, out slice!(u8), options ^!SysFormatOptions) uint:
    return DecToStr@(v, out)

fun SysRender@(v u16, out slice!(u8), options ^!SysFormatOptions) uint:
    return DecToStr@(v, out)

fun SysRender@(v u32, out slice!(u8), options ^!SysFormatOptions) uint:
    return DecToStr@(v, out)

fun SysRender@(v u64, out slice!(u8), options ^!SysFormatOptions) uint:
    return DecToStr@(v, out)

fun SysRender@(v s32, out slice!(u8), options ^!SysFormatOptions) uint:
    return DecToStr@(v, out)

fun SysRender@(v slice(u8), buffer slice!(u8), options ^!SysFormatOptions) uint:
    let n uint = len(buffer) min len(v)
    return mymemcpy(front!(buffer), front(v), n)

@pub @wrapped type uint_hex = uint

@pub @wrapped type u64_hex = u64

@pub @wrapped type u32_hex = u32

@pub @wrapped type u16_hex = u16

@pub @wrapped type u8_hex = u8

fun ToHexStr@(v u64, out slice!(u8)) uint:
    return unsigned_to_str#(v, 16, 64_uint, out)

fun ToHexStr@(v u32, out slice!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)

fun ToHexStr@(v u16, out slice!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)

fun ToHexStr@(v u8, out slice!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)

fun SysRender@(v uint_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

fun SysRender@(v u64_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

fun SysRender@(v u32_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

fun SysRender@(v u16_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

fun SysRender@(v u8_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

@pub @wrapped type rune = u8

fun SysRender@(v rune, buffer slice!(u8), options ^!SysFormatOptions) uint:
    if len(buffer) == 0:
        return 0
    else:
        set front!(buffer)^ = unwrap(v)
        return 1

global INF_POS = "inf"

global INF_NEG = "-inf"

global NAN_POS = "nan"

global NAN_NEG = "-nan"

fun slice_copy(src slice(u8), dst slice!(u8)) uint:
    let n uint = len(src) min len(dst)
    return mymemcpy(front!(dst), front(src), n)

fun nan_to_str(is_non_neg bool, frac_is_zero bool, out slice!(u8)) uint:
    if frac_is_zero:
        if is_non_neg:
            return slice_copy(INF_POS, out)
        else:
            return slice_copy(INF_NEG, out)
    else:
        if is_non_neg:
            return slice_copy(NAN_POS, out)
        else:
            return slice_copy(NAN_NEG, out)

fun to_hex_digit(digit u8) u8:
    return digit <= 9 ? digit + '0' : digit + ('a' - 10)

-- r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)
--         exponentiation bias is 1023
--         https://en.wikipedia.org/wiki/Double-precision_floating-point_format
--         https://observablehq.com/@jrus/hexfloat
fun ToHexStr@(val r64, out slice!(u8)) uint:
    let val_bits = bitwise_as(val, s64)
    let! frac_bits = val_bits and 0xf_ffff_ffff_ffff
    let exp_bits = val_bits >> 52 and 0x7ff
    let sign_bit = val_bits >> 63 and 1
    if exp_bits == 0x7ff:
        return nan_to_str(sign_bit == 0, frac_bits == 0, out)
    let! buf = front!(out)
    let! exp = exp_bits - 1023
    let! i uint = 0
    if sign_bit != 0:
        set pinc(buf, i)^ = '-'
        set i += 1
    set pinc(buf, i)^ = '0'
    set i += 1
    set pinc(buf, i)^ = 'x'
    set i += 1
    set pinc(buf, i)^ = exp_bits == 0 ? '0' : '1'
    set i += 1
    set pinc(buf, i)^ = '.'
    set i += 1
    while frac_bits != 0:
        set pinc(buf, i)^ = to_hex_digit(as(frac_bits >> 48, u8))
        set i += 1
        set frac_bits and= 0xffff_ffff_ffff
        set frac_bits <<= 4
    set pinc(buf, i)^ = 'p'
    set i += 1
    if exp < 0:
        set pinc(buf, i)^ = '-'
        set i += 1
        set exp = 0_s64 - exp
    let rest = slice(pinc(buf, i), len(out) - i)
    set i += DecToStr@(as(exp, u64), rest)
    return i

@pub @wrapped type r64_hex = r64

fun SysRender@(v r64_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    return ToHexStr@(unwrap(v), out)

@pub @wrapped type str_hex = slice(u8)

fun SysRender@(v str_hex, out slice!(u8), options ^!SysFormatOptions) uint:
    let v_str slice(u8) = unwrap(v)
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

fun SysRender@(v ^void, out slice!(u8), options ^!SysFormatOptions) uint:
    let h = wrap_as(bitwise_as(v, uint), uint_hex)
    return SysRender@(h, out, options)

@pub macro print# STMT_LIST(
    -- list of items to be printed
    $parts EXPR_LIST_REST)[$buffer, $curr, $options]:
    mlet! $buffer = [FORMATED_STRING_MAX_LEN]u8{}
    mlet! $curr uint = 0
    @ref mlet! $options = SysFormatOptions{}
    mfor $i $parts:
        set $curr += SysRender@(
                $i, slice(pinc(front!($buffer), $curr), len($buffer) - $curr), &!
                $options)
    do os::write(unwrap(os::Stdout), front($buffer), $curr)

-- same as above but takes an EXPR_LIST - should only be used by other macros
@pub macro print_list# STMT_LIST($parts EXPR_LIST)[$buffer, $curr, $options]:
    mlet! $buffer = [FORMATED_STRING_MAX_LEN]u8{}
    mlet! $curr uint = 0
    @ref mlet! $options = SysFormatOptions{}
    mfor $i $parts:
        set $curr += SysRender@(
                $i, slice(pinc(front!($buffer), $curr), len($buffer) - $curr), &!
                $options)
    do os::write(unwrap(os::Stdout), front($buffer), $curr)

@pub fun strz_to_slice(s ^u8) slice(u8):
    let! i uint = 0
    while pinc(s, i)^ != 0:
        set i += 1
    return slice(s, i)

@pub macro assert# STMT($cond EXPR, $parts EXPR_LIST_REST)[]:
    if $cond:
    else:
        print#(stringify($cond))
        print_list#($parts)
        trap
