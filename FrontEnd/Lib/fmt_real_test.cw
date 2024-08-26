(module [] :
(import fmt)

(import test)

(import fmt_real)

(import num_real)

(fun slice_incp [(param s (slice! u8)) (param inc uint)] (slice! u8) :
      (let n uint (min inc (len s)))
      (return (slice_val (pinc (front! s) n) (- (len s) n))))


(fun test_nan [] void :
    @doc "sanity checks for NANs"
    (test::AssertNe# +inf_r64 -inf_r64))


(fun test_normal [(param multiplier s32)
                  (param exp10 s32)
                  (param precision uint)] void :
    (let! expected (array 64 u8) undef)
    (let! actual (array 1024 u8) undef)
    (let! val r64 (as multiplier r64))
    (if (< exp10 0) :
        (/= val (at num_real::powers_of_ten (~ exp10)))
    :
        (*= val (at num_real::powers_of_ten exp10))

    )
    (let len_a uint (fmt_real::FmtE@ [val 8 true actual]))
    (= (at expected 0) (? (< multiplier 0) '-' '+'))
    (= (at expected 1) (+ '0' (as multiplier u8)))
    (= (at expected 2) '.')
    (for j 0 precision 1 :
        (= (at expected (+ j 3)) '0')
    )
    (= (at expected (+ precision 3)) 'e')
    (let! len_e uint (fmt_real::FmtExponentE [exp10
                                    (slice_incp [expected (+ precision 4)])]))
    (+= len_e precision)
    (+= len_e 4)
    (test::AssertSliceEq# (slice_val (front expected) len_e)
                          (slice_val (front actual) len_a))
)


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc """
    (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    """
    (do (test_nan []))
    (for i 0 294_s32 1 :
        (do (test_normal [1 i 8]))
        (do (test_normal [3 i 8]))
        (do (test_normal [5 i 8]))
        (do (test_normal [9 i 8]))

        (do (test_normal [1 (~ i) 8]))
        (do (test_normal [3 (~ i) 8]))
        (do (test_normal [5 (~ i) 8]))
        (do (test_normal [9 (~ i) 8]))
    )
    (test::Success#)
    (return 0))
)
