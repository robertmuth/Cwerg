(module [] :
(import fmt)

(import test)

(import fmt_real)

(import num_real)


(fun test_nan [] void :
    @doc "sanity checks for NANs"
    (test::AssertNe# +inf_r64 -inf_r64))


(fun test_normal [(param multiplier s32) (param precision uint)] void :
    (let! expected (array 64 u8) undef)
    (let! expected2 (array 64 u8) undef)
    (let! buf (array 1024 u8) undef)
    @doc "sanity checks for NANs"
    (for i 0 -294_sint -1 :
        (let! val r64 (as multiplier r64))
        (/= val (at num_real::powers_of_ten (~ i)))
        (do (fmt_real::FmtE@ [val 8 true buf]))

    )
)


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc """
    (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    """
    (do (test_nan []))
    (do (test_normal [1 8]))
    (test::Success#)
    (return 0))
)
