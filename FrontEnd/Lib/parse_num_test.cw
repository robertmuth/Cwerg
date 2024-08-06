(module [] :
(import fmt)
(import test)

(import parse_num)

(global u64_max auto (- 0_u64 1))
(global u32_max auto (- 0_u32 1))




(fun test_simple  [] void :
    (test::AssertEq# 0.0_r64 (parse_num::parse_r64 ["0"]))
    (test::AssertEq# 0.0_r64 (parse_num::parse_r64 ["+0"]))
    (test::AssertEq# 0.0_r64 (parse_num::parse_r64 ["000000"]))
    (test::AssertEq# 0.0_r64 (parse_num::parse_r64 ["+000000"]))
    (test::AssertEq# -0.0_r64 (parse_num::parse_r64 ["-0"]))
    (test::AssertEq# 0.0_r64 (parse_num::parse_r64 ["-000000"]))
 )

(fun test_mul_u64_by_u64_to_b_u128  [] void :
 )

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (test_simple []))
    (do (test_mul_u64_by_u64_to_b_u128 []))
    (test::Success#)
    (return 0))
)