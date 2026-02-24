module:

import os

import fmt_int

import fmt_real

pub global FORMATED_STRING_MAX_LEN uint = 4096

pub fun mymemcpy(dst ^!u8, src ^u8, size uint) uint:
    for i = 0, size, 1:
        set ptr_inc(dst, i)^ = ptr_inc(src, i)^
    return size

; This gets passed to the actual formatters which decide how to interpret the options.
pub rec SysFormatOptions:
    ; min width
    witdh u8
    precision u8
    padding u8
    show_sign bool
    right_justify bool


; Fake formatters for manipulating the SysFormatOptions
pub wrapped type SetWidth = u8
poly pub fun SysRender(v SetWidth, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^.witdh = unwrap(v)
    return 0

pub wrapped type SetPrecision = u8
poly pub fun SysRender(v SetPrecision, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^.precision = unwrap(v)
    return 0

pub wrapped type SetPadding = u8
poly pub fun SysRender(v SetPadding, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^.padding = unwrap(v)
    return 0

pub wrapped type ShowSign = bool
poly pub fun SysRender(v ShowSign, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^.show_sign = unwrap(v)
    return 0

pub wrapped type RightJustify = bool
poly pub fun SysRender(v RightJustify, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^.right_justify = unwrap(v)
    return 0

pub wrapped type SaveOptions = ^!SysFormatOptions
poly pub fun SysRender(v SaveOptions, buffer span!(u8), options ^!SysFormatOptions) uint:
    set unwrap(v)^ = options^
    return 0

pub wrapped type RestoreOptions = ^!SysFormatOptions
poly pub fun SysRender(v RestoreOptions, buffer span!(u8), options ^!SysFormatOptions) uint:
    set options^ = unwrap(v)^
    return 0


global TRUE_STR span(u8) = "true"

global FALSE_STR span(u8) = "false"


; only need to mark the first poly as pub
poly pub fun SysRender(v bool, buffer span!(u8), options ^!SysFormatOptions)
  uint:
    let s = v ? TRUE_STR : FALSE_STR
    let n uint = min(len(buffer), len(s))
    return mymemcpy(front!(buffer), front(s), n)

pub fun str_to_u32(s span(u8)) u32:
    let! x = 0_u32
    for i = 0, len(s), 1:
        set x *= 10
        let c = s[i]
        set x += as(c - '0', u32)
    return x

poly fun SysRender(v u8, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v u16, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v u32, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v u64, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v s16, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v s32, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtDec(v, out)

poly fun SysRender(v span(u8), buffer span!(u8), options ^!SysFormatOptions)
  uint:
    let n uint = min(len(buffer), len(v))
    return mymemcpy(front!(buffer), front(v), n)

poly fun SysRender(v span!(u8), buffer span!(u8), options ^!SysFormatOptions)
  uint:
    let n uint = min(len(buffer), len(v))
    return mymemcpy(front!(buffer), front(v), n)

pub wrapped type uint_hex = uint

pub wrapped type u64_hex = u64

pub wrapped type u32_hex = u32

pub wrapped type u16_hex = u16

pub wrapped type u8_hex = u8

poly fun SysRender(v uint_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtHex(unwrap(v), out)

poly fun SysRender(v u64_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtHex(unwrap(v), out)

poly fun SysRender(v u32_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtHex(unwrap(v), out)

poly fun SysRender(v u16_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtHex(unwrap(v), out)

poly fun SysRender(v u8_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_int\FmtHex(unwrap(v), out)

pub wrapped type rune = u8

pub wrapped type uft8 = u32

poly fun SysRender(v rune, buffer span!(u8), options ^!SysFormatOptions) uint:
    if len(buffer) == 0:
        return 0
    else:
        set front!(buffer)^ = unwrap(v)
        return 1


; �
pub global REPLACEMMENT_CHAR_UNICODE u32 = 0xfffd;
pub global REPLACEMMENT_CHAR_ASCII u8 = '?';


pub fun UnicodeToUtf8(unicode u32, out span!(u8)) uint:
    let n = len(out)
    cond:
        ; 7 bits
        case unicode <= 0x7f:
            if n < 1:
                return 0
            set out[0] = as(unicode, u8)
            return 1
        ; 11 bits
        case unicode <= 0x7ff:
            if n < 2:
                return 0
            set out[0] = as((unicode >> 6) | 0xc0, u8)
            set out[1] = as((unicode  & 0x3f) | 0x80, u8)
            return 2
        ; 16 bits
        case unicode <= 0xffff :
            if n < 3:
                return 0
            set out[0] = as((unicode >> 12) | 0xe0, u8)
            set out[1] = as(((unicode >> 6) & 0x3f) | 0x80, u8)
            set out[2] = as((unicode  & 0x3f) | 0x80, u8)
            return 3
        ; 21 bits
        case unicode <= 0x10ffff:
            if n < 4:
                return 0
            set out[0] = as((unicode >> 18) | 0xf0, u8)
            set out[1] = as(((unicode >> 12) & 0x3f) | 0x80, u8)
            set out[2] = as(((unicode >> 6) & 0x3f) | 0x80, u8)
            set out[3] = as((unicode  & 0x3f) | 0x80, u8)
            return 4
        case true:
            return 0


pub wrapped type rune_utf8 = u32

poly fun SysRender(v rune_utf8, buffer span!(u8), options ^!SysFormatOptions) uint:
    return UnicodeToUtf8(unwrap(v), buffer)

pub wrapped type r64_hex = r64

poly fun SysRender(v r64_hex, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_real\FmtHex(unwrap(v), out)

poly fun SysRender(v r64, out span!(u8), options ^!SysFormatOptions) uint:
    return fmt_real\FmtE(v, 6, false, out)

pub wrapped type str_hex = span(u8)

fun to_hex_digit(digit u8) u8:
    return digit <= 9 ? digit + '0' : digit + ('a' - 10)

poly fun SysRender(v str_hex, out span!(u8), options ^!SysFormatOptions) uint:
    let v_str span(u8) = unwrap(v)
    let dst_len = len(v_str)
    if dst_len <= len(out):
        for i = 0, dst_len, 1:
            let c u8 = v_str[i]
            let o1 uint = i * 2
            let o2 uint = o1 + 1
            set out[o1] = to_hex_digit(c >> 4)
            set out[o2] = to_hex_digit(c & 15)
        return dst_len * 2
    else:
        for i = 0, len(out), 1:
            set out[i] = '.'
        return 0

poly fun SysRender(v ^void, out span!(u8), options ^!SysFormatOptions) uint:
    let h = wrap_as(bitwise_as(v, uint), uint_hex)
    return SysRender(h, out, options)

pub macro print# STMT_LIST (
                            ; list of items to be printed
                            $parts EXPR_LIST_REST) [$buffer, $curr, $options]:
    let! $buffer = {[FORMATED_STRING_MAX_LEN]u8: undef}
    let! $curr span!(u8) = $buffer
    ref let! $options = {SysFormatOptions:}
    mfor $i $parts:
        set $curr = span_inc($curr, SysRender($i, $curr, @!$options))
    do os\write(unwrap(os\Stdout), front($buffer), len($buffer) - len($curr))

pub fun strz_to_slice(s ^u8) span(u8):
    let! i uint = 0
    while ptr_inc(s, i)^ != 0:
        set i += 1
    return make_span(s, i)

pub macro assert# STMT ($cond EXPR, $parts EXPR_LIST_REST) []:
    if $cond:
    else:
        print#(stringify($cond))
        print#($parts)
        trap
