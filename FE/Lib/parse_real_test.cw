module:

import cmp

import fmt

import test

import parse_real

import num_real

global u64_max = 0_u64 - 1

global u32_max = 0_u32 - 1

; This asumes that there will be no error during the parse
fun parse_r64(s span(u8)) r64:
    let x = parse_real::parse_r64(s)
    assert#(x.length == len(s), "s was not completely consumed")
    return x.value

fun test_nan() void:
    ; sanity checks for NANs
    test::AssertEqR64#(num_real::inf_pos_r64, parse_r64("+inf"))
    test::AssertEqR64#(num_real::inf_neg_r64, parse_r64("-inf"))
    test::AssertNeR64#(num_real::inf_neg_r64, num_real::inf_pos_r64)

    test::AssertEqR64#(num_real::nan_pos_r64, parse_r64("+nan"))
    test::AssertEqR64#(num_real::nan_neg_r64, parse_r64("-nan"))
    test::AssertNeR64#(num_real::nan_neg_r64, num_real::nan_pos_r64)


global REL_ERR1 r64 = 0.5e-15

fun test_dec() void:
    ; zero tests
    test::AssertNeR64#(+0.0_r64, -0.0_r64)
    test::AssertEqR64#(0.0_r64, parse_r64("0"))
    test::AssertEqR64#(0.0_r64, parse_r64("+0"))
    test::AssertEq#(-0.0_r64, parse_r64("-0"))
    test::AssertEqR64#(0.0_r64, parse_r64("000000"))
    test::AssertEqR64#(0.0_r64, parse_r64("+000000"))
    test::AssertEqR64#(-0.0_r64, parse_r64("-000000"))
    test::AssertEqR64#(0.0_r64, parse_r64(".0"))
    test::AssertEqR64#(0.0_r64, parse_r64(".00000"))
    test::AssertEqR64#(0.0_r64, parse_r64("000000.00000"))
    test::AssertEqR64#(0.0_r64, parse_r64("000000.00000"))
    ; largest value (2^53 -1) * 2^(1023 - 52)
    ;     (test::AssertGenericEq# 0x1.fffffffffffffp1023_r64
    ;                             (parse_r64 ["1.79769313486231570814e308"]) REL_ERR1)
    ;
    test::AssertEqR64#(1.0_r64, parse_r64("1"))
    test::AssertEqR64#(1.0_r64, parse_r64(".1e1"))
    test::AssertEqR64#(1.0_r64, parse_r64(".0000000001e10"))
    test::AssertEqR64#(666_r64, parse_r64("666"))
    test::AssertEqR64#(666_r64, parse_r64("666.00000"))
    test::AssertEqR64#(0_r64, parse_r64("1e-500"))
    test::AssertEqR64#(-0_r64, parse_r64("-1e-500"))
    test::AssertEqR64#(+.inf_r64, parse_r64("1e+500"))
    test::AssertEqR64#(-.inf_r64, parse_r64("-1e+500"))
    ; this are slightly less accurate on x86-64 than on arm
    test::AssertGenericEq#({cmp::r64r: 3.141592653589793238462643, REL_ERR1},
                           {cmp::r64r: parse_r64("3.141592653589793238462643")})
    test::AssertGenericEq#({cmp::r64r: 2.718281828459045235360287, REL_ERR1},
                           {cmp::r64r: parse_r64("2.718281828459045235360287")})

fun test_hex() void:
    ;
    ;     try testing.expectEqual(try parseFloat(f64, "0x1.fffffffffffffp+1023"), math.floatMax(f64))&&
    ;     try testing.expectEqual(try parseFloat(f64, "-0x1.fffffffffffffp1023"), -math.floatMax(f64))&&
    ;
    test::AssertEqR64#(0.0, parse_r64("0x0"))
    test::AssertEqR64#(0.0, parse_r64("0x.0"))
    test::AssertEqR64#(1.0, parse_r64("0x1p0"))
    test::AssertEqR64#(0.5, parse_r64("0x1p-1"))
    test::AssertEqR64#(0.25, parse_r64("0x1p-2"))
    test::AssertEqR64#(0.125, parse_r64("0x1p-3"))
    test::AssertEqR64#(16384.0, parse_r64("0x1p14"))
    test::AssertEqR64#(16384.0, parse_r64("0x10p+10"))
    test::AssertEqR64#(-num_real::r64_min, parse_r64("0x1p-1022"))
    test::AssertEqR64#(0.015625, parse_r64("0x10p-10"))
    ; negative
    test::AssertEqR64#(-0.0, parse_r64("-0x0"))
    test::AssertEqR64#(-0.0, parse_r64("-0x.0"))
    test::AssertEqR64#(-0x0p0, parse_r64("-0x0p0"))
    test::AssertEqR64#(-1.0, parse_r64("-0x1p0"))
    test::AssertEqR64#(-0.5, parse_r64("-0x1p-1"))
    test::AssertEqR64#(-0.25, parse_r64("-0x1p-2"))
    test::AssertEqR64#(-0.125, parse_r64("-0x1p-3"))
    test::AssertEqR64#(-16384.0, parse_r64("-0x1p14"))
    test::AssertEqR64#(-16384.0, parse_r64("-0x10p+10"))
    test::AssertEqR64#(num_real::r64_min, parse_r64("-0x1p-1022"))
    test::AssertEqR64#(-0.015625, parse_r64("-0x10p-10"))
    ; variations
    test::AssertEqR64#(0, parse_r64("0x0000p0"))
    test::AssertEqR64#(0, parse_r64("0x0.00000p0"))
    test::AssertEqR64#(1, parse_r64("0x1.0p0"))
    test::AssertEqR64#(16.0, parse_r64("0x10p0"))
    test::AssertEqR64#(16.0, parse_r64("0x10.0p0"))
    test::AssertEqR64#(1.0, parse_r64("0x10p-4"))
    test::AssertEqR64#(1.0, parse_r64("0x100p-8"))
    test::AssertEqR64#(1.0, parse_r64("0x100.00p-8"))
    test::AssertEqR64#(1.0, parse_r64("0x0.01p8"))
    ; after the point
    test::AssertEqR64#(0x1.fffep-1, parse_r64("0x0.ffffp0"))
    test::AssertEqR64#(0x1.fffffffep-1, parse_r64("0x0.ffffffffp0"))
    test::AssertEqR64#(0x1.fffffffffffep-1, parse_r64("0x0.ffffffffffffp0"))
    test::AssertEqR64#(0x1.fffffffffffffp-1, parse_r64("0x0.fffffffffffff8p0"))
    ; extra digits have no effect
    test::AssertEqR64#(0x1.fffffffffffffp-1,
                       parse_r64("0x0.fffffffffffffffffffffp0"))
    test::AssertEqR64#(0x1fffffffffffffp0, parse_r64("0x1fffffffffffffp0"))
    test::AssertEqR64#(0x1fffffffffffffp32,
                       parse_r64("0x1fffffffffffffffffffffp0"))

fun main(argc s32, argv ^^u8) s32:
    ;
    ;     (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    ;     (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    ;
    ; fmt::print#(
    ;         wrap_as(parse_r64("1.79769313486231570814e308"), fmt::r64_hex), "\n")
    do test_nan()
    do test_dec()
    do test_hex()
    test::Success#()
    return 0
