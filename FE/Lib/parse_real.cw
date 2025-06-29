; parse numbers from u8 to int/real
; https://gregstoll.com/~gregstoll/floattohex/
module:

import num_real

import fmt

rec ResultR64:
    value r64
    length uint

pub global ParseError ResultR64

fun is_hex_digit(c u8) bool:
    return c >= '0' && c <= '9' || c >= 'a' && c <= 'f'

fun hex_digit_val(c u8) u8:
    return c <= '9' ? c - '0' : c - 'a' + 10

fun is_dec_digit(c u8) bool:
    return c >= '0' && c <= '9'

fun dec_digit_val(c u8) u8:
    return c - '0'

; this macros capture i,n,s from the environment
macro next_char# STMT_LIST ($c ID, $error_body STMT_LIST) []:
    if i >= n:
        $error_body
    set $c = s[i]
    set i += 1

; if we have too many digits we drop the one after the dot but
; adjust must adjust the exponent for the one before
; this macro captures i,n,s from the environment
macro read_hex_mantissa# STMT_LIST ($c ID, $max_digits EXPR, $val ID, $adjust ID
                                    ) [$digits]:
    block end_of_input:
        let! $digits = $max_digits
        ; ignore leading zeros
        while $c == '0':
            next_char# $c:
                break end_of_input
        while is_hex_digit($c):
            if $digits == 0:
                set $adjust += 1
            else:
                set $val *= 16
                set $val += as(hex_digit_val($c), u64)
                set $digits -= 1
            next_char# $c:
                break end_of_input
        if c == '.':
            next_char# $c:
                break end_of_input
            while is_hex_digit($c):
                if $digits != 0:
                    set $val *= 16
                    set $val += as(hex_digit_val($c), u64)
                    set $adjust -= 1
                    set $digits -= 1
                next_char# $c:
                    break end_of_input

macro read_dec_mantissa# STMT_LIST ($c ID, $max_digits EXPR, $val ID, $adjust ID
                                    , $imprecise ID) [$digits]:
    block end_of_input:
        let! $digits = $max_digits
        ; ignore leading zeros
        while $c == '0':
            next_char# $c:
                break end_of_input
        while is_dec_digit($c):
            if $digits == 0:
                if $c != '0':
                    set $imprecise = true
                set $adjust += 1
            else:
                set $val *= 10
                set $val += as(dec_digit_val($c), u64)
                set $digits -= 1
            next_char# $c:
                break end_of_input
        if c == '.':
            next_char# $c:
                break end_of_input
            while is_dec_digit($c):
                if $digits != 0:
                    set $val *= 10
                    set $val += as(dec_digit_val($c), u64)
                    set $adjust -= 1
                    set $digits -= 1
                else:
                    if $c != '0':
                        set $imprecise = true
                next_char# $c:
                    break end_of_input

; this macro captures i,n,s from the environment
macro read_dec_exponent# STMT_LIST ($c ID, $exp ID) [$negative]:
    let! $negative = false
    if $c == '-' || $c == '+':
        if $c == '-':
            set $negative = true
        next_char# $c:
            return ParseError
    while is_dec_digit($c):
        set $exp *= 10
        set $exp += as(dec_digit_val($c), s32)
        next_char# $c:
            break
    if $negative:
        set $exp = -exp

; expects a string without sign and without '0x' prefix
; note. this code does not perform
; * denormalization - this is not supported by Cwerg
; * rounding - the whole point of hex float is to control the mantissa exactly
fun parse_r64_hex_helper(s span(u8), negative bool, offset uint) ResultR64:
    ; note, thaty besides s we define our own i and n here for next_char#
    let! i uint = offset
    let n = len(s)
    let! c u8
    next_char# c:
        return ParseError
    let! mant = 0_u64
    let! exp_adjustments = 0_s32
    let! exp = 0_s32
    ; allow an extra 2 digits beyond the 52 / 4 = 13 mantissa hex digits
    read_hex_mantissa#(c, num_real::r64_mantissa_bits / 4 + 2, mant,
                       exp_adjustments)
    if c == 'p':
        next_char# c:
            return ParseError
        read_dec_exponent#(c, exp)
    ; TODO: check that we have consumed all chars
    ; early out for simple corner case
    if mant == 0:
        return negative ? {: -0_r64, i} : {: +0_r64, i}
    set exp += exp_adjustments * 4
    set exp += as(num_real::r64_mantissa_bits, s32)
    ; fmt::print# ("BEFORE mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
    ; we want the highest set bit to be at position num_real::r64_mantissa_bits + 1
    ; replace both while loops utilizing "count leading zeros"
    while mant >> as(num_real::r64_mantissa_bits, u64) == 0:
        ; fmt::print# ("@@ shift ", mant, "\n")
        set mant <<= 8
        set exp -= 8
    while mant >> as(num_real::r64_mantissa_bits, u64) != 1:
        set mant >>= 1
        set exp += 1
    if exp > num_real::r64_exponent_max:
        ; maybe return inf
        return ParseError
    if exp < num_real::r64_exponent_min:
        ; we do not support denormalization
        ; maybe return 0.0
        return ParseError
    set exp += num_real::r64_exponent_bias
    ; fmt::print# ("AFTER mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
    ; final touches
    let exp_u64 = as(exp, u64) & num_real::r64_exponent_mask
    set mant &= num_real::r64_mantissa_mask
    return {ResultR64: num_real::make_r64(negative, exp_u64, mant), i}

pub fun parse_r64_hex(s span(u8)) ResultR64:
    if len(s) < 5:
        return ParseError
    let! i uint = 0
    let! c u8 = s[i]
    let! negative = false
    if c == '-' || c == '+':
        set i += 1
        if c == '-':
            set negative = true
    if s[i] != '0' || s[i + 1] != 'x':
        return ParseError
    set i += 2
    return parse_r64_hex_helper(span_inc(s, i), negative, i)

fun r64_dec_fast_helper(mant_orig u64, exp_orig s32, negative bool) r64:
    let! exp = exp_orig
    let! mant = mant_orig
    while mant >= 1 << as(num_real::r64_mantissa_bits + 1, u64):
        set mant /= 10
        set exp += 1
    if exp >= 309:
        return negative ? num_real::inf_neg_r64 : num_real::inf_pos_r64
    if exp <= -309:
        return negative ? num_real::zero_neg_r64 : num_real::zero_pos_r64
    ; on x86-64 there is not conversion instruction from u64->r64
    let! out = as(as(mant, s64), r64)
    if negative:
        set out = -out
    if exp >= 0:
        return out * num_real::powers_of_ten[exp]
    else:
        return out / num_real::powers_of_ten[-exp]

pub fun parse_r64(s span(u8)) ResultR64:
    ; index of next char to read
    let! i uint = 0
    let n = len(s)
    let! c u8
    next_char# c:
        return ParseError
    let! negative = false
    if c == '-' || c == '+':
        if c == '-':
            set negative = true
        next_char# c:
            return ParseError
    if c == 'i':
        if i + 2 > n || s[i] != 'n' || s[i + 1] != 'f':
            return ParseError
        return negative ? {: num_real::inf_neg_r64, i + 2} : {: num_real::inf_pos_r64, i + 2}
    if c == 'n':
        if i + 2 > n || s[i] != 'a' || s[i + 1] != 'n':
            return ParseError
        return negative ? {: num_real::nan_neg_r64, i + 2} : {: num_real::nan_pos_r64, i + 2}
    if c == '0' && i <= n && s[i] == 'x':
        set i += 1
        return parse_r64_hex_helper(s, negative, i)
    let! mant = 0_u64
    let! exp_adjustments = 0_s32
    let! exp = 0_s32
    let! imprecise = false
    ; note, this is macro
    ; log2(10^19) == 63.11
    read_dec_mantissa#(c, 19_s32, mant, exp_adjustments, imprecise)
    if c == 'e':
        next_char# c:
            return ParseError
        read_dec_exponent#(c, exp)
    ; TODO: check that we have consumed all chars
    ; early out for simple corner case
    if mant == 0:
        return negative ? {: num_real::zero_neg_r64, i} : {: num_real::zero_pos_r64, i}
    set exp += exp_adjustments
    ; try making mantissa smaller, this is a common case, e.g.
    ; 555.0000 and helps preserve accuracy
    while mant % 10 == 0:
        set mant /= 10
        set exp += 1
    ; fmt::print# (s, " mant: ", mant, " exp: ", exp, "\n")
    ; quick and dirty. may be not be super precise
    ; for possible improvements see:
    ; https://github.com/ziglang/zig/blob/master/lib/std/fmt/parse_float.zig
    ; https://github.com/c3lang/c3c/blob/master/lib/std/core/string_to_real.c3
    ; https://github.com/oridb/mc/blob/master/lib/std/fltparse.myr
    return {ResultR64: r64_dec_fast_helper(mant, exp, negative), i}
