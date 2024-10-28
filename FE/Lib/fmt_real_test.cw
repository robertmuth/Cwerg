module:

import fmt

import test

import fmt_real

import num_real

fun test_special() void:
    -- sanity checks for NANs
    let! actual [1024]u8 = undef
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_zero_pos, 1, true, actual)
        test::AssertSliceEq#("+0.0e+00", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_zero_neg, 1, true, actual)
        test::AssertSliceEq#("-0.0e+00", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_inf_pos, 1, true, actual)
        test::AssertSliceEq#("+inf", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_inf_neg, 1, true, actual)
        test::AssertSliceEq#("-inf", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_nan_pos, 1, true, actual)
        test::AssertSliceEq#("+nan", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtE@(num_real::r64_nan_neg, 1, true, actual)
        test::AssertSliceEq#("-nan", span(front(actual), len_a))

-- python3 -c 'print(0.0).hex())'
fun test_hex() void:
    let! actual [1024]u8 = undef
    block _:
        let len_a = fmt_real::FmtHex@(+0.5_r64, actual)
        test::AssertSliceEq#("0x1.p-1", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtHex@(+2.0_r64, actual)
        test::AssertSliceEq#("0x1.p+1", span(front(actual), len_a))
    block _:
        let len_a = fmt_real::FmtHex@(+0.0_r64, actual)
        -- (fmt::print# actual " BBBB\n")
        test::AssertSliceEq#("0x0.p+0", span(front(actual), len_a))

global PRECISION uint = 8

fun make_expected(is_neg bool, integer u32, exp10 s32, precision uint, out span!(
        u8)) uint:
    set out[0] = is_neg ? '-' : '+'
    set out[1] = '0' + as(integer, u8)
    set out[2] = '.'
    for j = 0, precision, 1:
        set out[j + 3] = '0'
    let! n uint = fmt_real::FmtExponentE(
            exp10, span_inc_or_die#(out, precision + 3))
    set n += precision
    set n += 3
    return n

fun test_normal(is_neg bool, multiplier u32, exp10 s32, precision uint) void:
    let! expected [1024]u8 = undef
    let! actual [1024]u8 = undef
    let! val r64 = as(multiplier, r64)
    if exp10 < 0:
        set val /= num_real::powers_of_ten[-exp10]
    else:
        set val *= num_real::powers_of_ten[exp10]
    if is_neg:
        set val *= -1.0
    let len_a uint = fmt_real::FmtE@(val, PRECISION, true, actual)
    let len_e uint = make_expected(is_neg, multiplier, exp10, precision, expected)
    test::AssertSliceEq#(span(front(expected), len_e), span(
            front(actual), len_a))

fun main(argc s32, argv ^^u8) s32:
    -- 
    --     (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    --     (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    --     
    do test_special()
    do test_hex()
    -- null:
    do test_normal(false, 0, 0, PRECISION)
    do test_normal(true, 0, 0, PRECISION)
    for i = 0, 294_s32, 1:
        for m = 1, 10_u32, 2:
            do test_normal(false, m, i, PRECISION)
            do test_normal(false, m, -i, PRECISION)
    test::Success#()
    return 0
