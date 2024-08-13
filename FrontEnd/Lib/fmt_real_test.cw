(module [] :
(import fmt)

(import test)

(import fmt_real)
(import num_real)


(fun test_nan [] void :
    @doc "sanity checks for NANs"
    (test::AssertNe# +inf_r64 -inf_r64)
)

(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc """
    (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    """


    (do (test_nan []))

    (test::Success#)
    (return 0))
)