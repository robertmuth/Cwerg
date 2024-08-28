@doc """Lots of literature referencves :
https://stackoverflow.com/questions/7153979/algorithm-to-convert-an-ieee-754-double-to-a-string
https://www.ryanjuckett.com/printing-floating-point-numbers/"""
(module [] :
(import fmt)

(import num_real)

(import fmt_int)


(global log2_10 r64 3.3219280948873623478703194294)


(global log10_2_to_52 r64 15.653559774527022151114422525)


(global target_range_hi auto (as (<< 1_u64 53) r64))


(global target_range_lo auto (/ (as (<< 1_u64 53) r64) 10.0))


@pub (fun mymemcpy [
        (param dst (ptr! u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i 0 size 1 :
        (= (^ (pinc dst i)) (^ (pinc src i))))
    (return size))


(fun div_by_power_of_10 [(param val r64) (param pow10 s32)] r64 :
    (if (>= pow10 0) :
        (return (/ val (at num_real::powers_of_ten pow10)))
     :
        (return (* val (at num_real::powers_of_ten (~ pow10))))))


(fun find_t [(param val r64)] s32 :
    (let biased_exp auto (- (num_real::r64_raw_exponent [val]) num_real::r64_raw_exponent_bias))
    (let! t s32 (~ (as (- log10_2_to_52 (/ (as biased_exp r64) log2_10)) s32)))
    (while true :
        (let x auto (div_by_power_of_10 [val t]))
        (cond :
            (case (<= x target_range_lo) :
                (-= t 1))
            (case (> x target_range_hi) :
                (+= t 1))
            (case true :
                (return t)))))


@doc """assumptions:
* raw_exp is nan
* len(out) >= 5"""
(fun FmtNan [(param val r64) (param out (slice! u8))] uint :
    (let! mantissa auto (num_real::r64_raw_mantissa [val]))
    (let is_negative auto (num_real::r64_is_negative [val]))
    (= (at out 0) (? is_negative '-' '+'))
    (cond :
        (case (== mantissa num_real::r64_mantissa_infinity) :
            (return (+ 1 (slice_append_or_die# "inf" (slice_inc_or_die# out 1)))))
        (case (== mantissa num_real::r64_mantissa_qnan) :
            (return (+ 1 (slice_append_or_die# "nan" (slice_inc_or_die# out 1)))))
        (case (== mantissa num_real::r64_mantissa_snan) :
            (return (+ 1 (slice_append_or_die# "snan" (slice_inc_or_die# out 1))))))
    (return 0))


@doc """for a given float val we want to find a decomposition
val = x * 10^t so that   2^53 / 10 < x <= 2^53
because this way we can compute the base ten digits easily.
From the standard for %e:
The double argument shall be converted in the style "[-]d.ddde±dd",
where there is one digit before the radix character (which is non-zero if the argument
is non-zero) and the number of digits after it is equal to the precision; if the precision
is missing, it shall be taken as 6; if the precision is zero and no '#' flag is present, no
radix character shall appear. The low-order digit shall be rounded in an implementation-defined
manner. The E conversion specifier shall produce a number with 'E' instead of 'e' introducing
the exponent. The exponent shall always contain at least two digits. If the value is zero,
the exponent shall be zero."""
@pub (fun FmtExponentE [(param exp s32) (param out (slice! u8))] uint :
    (if (< (len out) 4) :
        (return 0)
     :)
    @doc "account for e±"
    (let! i auto 2_uint)
    (= (at out 0) 'e')
    (if (< exp 0) :
        (= (at out 1) '-')
        (if (>= exp -9) :
            (= (at out 2) '0')
            (+= i 1)
         :)
        (return (+ i (fmt_int::FmtDec@ [(~ exp) (slice_inc_or_die# out i)])))
     :
        (= (at out 1) '+')
        (if (<= exp 9) :
            (= (at out 2) '0')
            (+= i 1)
         :)
        (return (+ i (fmt_int::FmtDec@ [exp (slice_inc_or_die# out i)])))))


(fun FmtSign [
        (param is_negative bool)
        (param force_sign bool)
        (param out (slice! u8))] uint :
    (cond :
        (case is_negative :
            (= (at out 0) '-')
            (return 1))
        (case force_sign :
            (= (at out 0) '+')
            (return 1))
        (case true :
            (return 0))))


(fun FmtMantissaE [
        (param digits (slice u8))
        (param precision uint)
        (param out (slice! u8))] uint :
    (let num_digits auto (len digits))
    (= (at out 0) (at digits 0))
    (= (at out 1) '.')
    (for j 1 (+ precision 1) 1 :
        (if (< j num_digits) :
            (= (at out (+ j 1)) (at digits j))
         :
            (= (at out (+ j 1)) '0')))
    (return (+ precision 2)))


@doc """return a potential "carry""""
(fun RoundDigitsUp [(param digits (slice! u8))] s32 :
    (for pos 0 (len digits) 1 :
        (let i auto (- (- (len digits) pos) 1))
        (if (== (at digits i) '9') :
            (= (at digits i) '0')
         :
            (+= (at digits i) 1)
            (return 0)))
    (for pos 0 (- (len digits) 1) 1 :
        (let i auto (- (- (len digits) pos) 1))
        (= (at digits i) (at digits (- i 1))))
    (= (at digits 0) '1')
    (return 1))


@pub (fun FmtE@ [
        (param val r64)
        (param precision uint)
        (param force_sign bool)
        (param out (slice! u8))] uint :
    @doc "worst case -x.[precision]e-xxx"
    (let is_negative auto (num_real::r64_is_negative [val]))
    (let! buffer (array 32 u8) undef)
    (if (< (len out) (+ precision 8)) :
        (return 0)
     :)
    (if (> (+ precision 1) (len buffer)) :
        (return 0)
     :)
    (if (== (num_real::r64_raw_exponent [val]) num_real::r64_raw_exponent_subnormal) :
        (if (== (num_real::r64_raw_mantissa [val]) 0) :
            (= (at buffer 0) '0')
            (let! i auto 0_uint)
            (+= i (FmtSign [is_negative force_sign out]))
            (+= i (FmtMantissaE [(slice_val (front buffer) 1) precision (slice_inc_or_die# out i)]))
            (+= i (FmtExponentE [0 (slice_inc_or_die# out i)]))
            (return i)
         :)
        (return 0)
     :)
    (if (== (num_real::r64_raw_exponent [val]) num_real::r64_raw_exponent_nan) :
        (return (FmtNan [val out]))
     :)
    (let! t s32 (find_t [val]))
    @doc """fmt::print#("@@@ ", t, "\n")"""
    (let x auto (div_by_power_of_10 [val t]))
    (let! mantissa auto (+ (num_real::r64_raw_mantissa [x]) (<< 1 52)))
    (let exponent auto (- (num_real::r64_raw_exponent [x]) num_real::r64_raw_exponent_bias))
    (fmt::assert# (&& (>= exponent 49) (<= exponent 52)) ["out of bounds\n"])
    (if (!= exponent 52) :
        (-= t 1)
        (*= mantissa 10)
        (>>= mantissa (as (- 52_s32 exponent) u64))
     :)
    (let num_digits uint (fmt_int::FmtDec@ [mantissa (as buffer (slice! u8))]))
    @doc "decimal rounding if we drop digits"
    (if (&& (> num_digits (+ precision 1)) (>= (at buffer (+ precision 2)) '5')) :
        (+= t (RoundDigitsUp [(slice_val (front! buffer) (+ precision 1))]))
     :)
    (+= t (as (- num_digits 1) s32))
    (let! i auto 0_uint)
    (+= i (FmtSign [is_negative force_sign out]))
    (+= i (FmtMantissaE [(slice_val (front buffer) num_digits) precision (slice_inc_or_die# out i)]))
    (+= i (FmtExponentE [t (slice_inc_or_die# out i)]))
    @doc """fmt::print#("@@@ ", t, " ",  exponent, " ",  buffer, " out:", out, "\n")"""
    (return i))
)

