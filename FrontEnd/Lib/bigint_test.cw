(module [] :
(import test)

(import fmt)

(import bigint)


(global u64_max auto (- 0_u64 1))


(global u32_max auto (- 0_u32 1))


(global b_u128_zero auto (array_val 2 u64 [0 0]))


(global b_u128_one auto (array_val 2 u64 [1 0]))


(global b_u128_two auto (array_val 2 u64 [2 0]))


(global b_u128_max auto (array_val 2 u64 [u64_max u64_max]))


(fun test_add_b_u128 [] void :
    (test::AssertEq# 0_u64 (at (bigint::add_b_u128 [b_u128_zero b_u128_zero]) 0))
    (test::AssertEq# 1_u64 (at (bigint::add_b_u128 [b_u128_zero b_u128_one]) 0))
    (test::AssertEq# 0_u64 (at (bigint::add_b_u128 [b_u128_max b_u128_one]) 0))
    (test::AssertEq# 1_u64 (at (bigint::add_b_u128 [b_u128_max b_u128_two]) 0)))


(fun test_mul_u64_by_u64_to_b_u128 [] void :
    (test::AssertEq# 0_u64 (at (bigint::mul_u64_by_u64_to_b_u128 [0_u64 0_u64]) 0))
    (test::AssertEq# 1_u64 (at (bigint::mul_u64_by_u64_to_b_u128 [1_u64 1_u64]) 0))
    (test::AssertEq# 4_u64 (at (bigint::mul_u64_by_u64_to_b_u128 [2_u64 2_u64]) 0))
    (test::AssertEq# 1_u64 (at (bigint::mul_u64_by_u64_to_b_u128 [u64_max u64_max]) 0))
    (test::AssertEq# (- u64_max 1) (at (bigint::mul_u64_by_u64_to_b_u128 [u64_max u64_max]) 1)))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (do (test_add_b_u128 []))
    (do (test_mul_u64_by_u64_to_b_u128 []))
    (test::Success#)
    (return 0))
)

