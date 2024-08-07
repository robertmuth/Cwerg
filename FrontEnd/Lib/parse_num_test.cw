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


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc """
    (fmt::print# (bitwise_as (parse_r64 ["-nan"]) u64) "\n")
    (fmt::print# (bitwise_as -nan_r64 u64) "\n")
    """
    (do (test_simple []))
    (test::Success#)
    (return 0))
)
