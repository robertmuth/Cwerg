
(module [] :
(import fmt)

(import test)

(import parse_num)


(global u64_max auto (- 0_u64 1))


(global u32_max auto (- 0_u32 1))


(fun parse_r64 [(param s (slice u8))] r64 :
    (return (narrow_as (parse_num::parse_r64 [s]) r64)))


(fun test_simple [] void :
    @doc "zero tests"
    (test::AssertNeR64# +0.0_r64 -0.0_r64)
    (test::AssertEqR64# 0.0_r64 (parse_r64 ["0"]))
    (test::AssertEqR64# 0.0_r64 (parse_r64 ["+0"]))
    (test::AssertEqR64# 0.0_r64 (parse_r64 ["000000"]))
    (test::AssertEqR64# 0.0_r64 (parse_r64 ["+000000"]))
    (test::AssertEq# -0.0_r64 (parse_r64 ["-0"]))
    (test::AssertEqR64# 0.0_r64 (parse_r64 ["000000"]))
    @doc "sanity checks for NANs"
    (test::AssertNeR64# +inf_r64 -inf_r64)
    (test::AssertNeR64# +nan_r64 -nan_r64)

    (test::AssertEqR64# -nan_r64 (parse_r64 ["-nan"]))
    (test::AssertEqR64# +nan_r64 (parse_r64 ["+nan"]))
    (test::AssertEqR64# +inf_r64 (parse_r64 ["+inf"]))
    (test::AssertEqR64# -inf_r64 (parse_r64 ["-inf"])))

(fun test_hex [] void :
    @doc """
    try testing.expectEqual(try parseFloat(f64, "-0x1p-1"), -0.5);
    try testing.expectEqual(try parseFloat(f64, "0x10p+10"), 16384.0);
    try testing.expectEqual(try parseFloat(f64, "0x10p-10"), 0.015625);
    // Max normalized value.
    try testing.expectEqual(try parseFloat(f64, "0x1.fffffffffffffp+1023"), math.floatMax(f64));
    try testing.expectEqual(try parseFloat(f64, "-0x1.fffffffffffffp1023"), -math.floatMax(f64));
    // Min normalized value.
    try testing.expectEqual(try parseFloat(f64, "0x1p-1022"), math.floatMin(f64));
    try testing.expectEqual(try parseFloat(f64, "-0x1p-1022"), -math.floatMin(f64));
    // Min denormalized value.
    try testing.expectEqual(try parseFloat(f64, "0x1p-1074"), math.floatTrueMin(f64));
    try testing.expectEqual(try parseFloat(f64, "-0x1p-1074"), -math.floatTrueMin(f64));
    """
    (test::AssertEqR64# 0.125 (parse_r64 ["0x1p-3"]))
    (test::AssertEqR64# 0.25 (parse_r64 ["0x1p-2"]))
    (test::AssertEqR64# 0.5 (parse_r64 ["0x1p-1"]))

    (test::AssertEqR64# 0x0p0 (parse_r64 ["0x0p0"]))
    (test::AssertEqR64# 1.0 (parse_r64 ["0x1p0"]))

)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (fmt::print# (bitwise_as (parse_r64 ["0x0p0"]) u64) "\n")
    (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    (do (test_simple []))
    (do (test_hex []))

    (test::Success#)
    (return 0))
)
