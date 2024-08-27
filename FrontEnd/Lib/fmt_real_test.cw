(module [] :
(import fmt)

(import test)

(import fmt_real)

(import num_real)


(fun test_nans [] void :
    @doc "sanity checks for NANs"
    (return)
)

(global PRECISION uint 8)

(fun make_expected [(param is_neg bool) (param integer u32) (param exp10 s32) (param precision uint) (param out (slice! u8))] uint :
    (= (at out 0) (? is_neg '-' '+'))
    (= (at out 1) (+ '0' (as integer u8)))
    (= (at out 2) '.')
    (for j 0 precision 1 : (= (at out (+ j 3)) '0'))
    (let! n uint (fmt_real::FmtExponentE [exp10 (slice_inc# out (+ precision 3))]))
    (+= n precision)
    (+= n 3)
    (return n)
)


(fun test_normal [
        (param is_neg bool)
        (param multiplier u32)
        (param exp10 s32)
        (param precision uint)] void :
    (let! expected (array 1024 u8) undef)
    (let! actual (array 1024 u8) undef)
    (let! val r64 (as multiplier r64))
    (if (< exp10 0) :
        (/= val (at num_real::powers_of_ten (~ exp10)))
     :
        (*= val (at num_real::powers_of_ten exp10)))
    (if is_neg :
        (*= val -1.0)
    :)
    (let len_a uint (fmt_real::FmtE@ [val PRECISION true actual]))
    (let len_e uint (make_expected [is_neg multiplier exp10 precision expected]))
    (test::AssertSliceEq# (slice_val (front expected) len_e) (slice_val (front actual) len_a)))


(fun main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    @doc """
    (fmt::print# (wrap_as (parse_r64 ["1.79769313486231570814e308"]) fmt::r64_hex) "\n")
    (fmt::print# (bitwise_as 0x0p0_r64 u64) "\n")
    """
    (do (test_nans []))
    @doc "null:
    (do (test_normal [false 0 0 PRECISION]))
    (do (test_normal [true 0 0 PRECISION]))

    (for i 0 294_s32 1 :
        (for m 1 10_u32 2 :
            (do (test_normal [false m i PRECISION]))
            (do (test_normal [false m (~ i) PRECISION]))
        )
    )
    (test::Success#)
    (return 0))
)
