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


(fun div_by_power_of_10 [(param val r64) (param pow10 s32)] r64 :
    (if (>= pow10 0) :
        (return (/ val (at num_real::powers_of_ten pow10)))
     :
        (return (* val (at num_real::powers_of_ten (~ pow10))))))


(fun find_t [(param val r64)] s32 :
    (let biased_exp auto (- (num_real::r64_raw_exponent [val]) num_real::r64_exponent_bias))
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
    (if (< (len out) 3) :
        (return 0)
     :)
    (let! i auto 1_uint)
    (if (< exp 0) :
        (= (at out 0) '-')
        (if (>= exp -9) :
            (= (at out 1) '0')
            (+= i 1)
         :)
        (return (+ i (fmt_int::FmtDec@ [(~ exp) (slice_inc# out i)])))
     :
        (= (at out 0) '+')
        (if (<= exp 9) :
            (= (at out 1) '0')
            (+= i 1)
         :)
        (return (+ i (fmt_int::FmtDec@ [exp (slice_inc# out i)])))))


@pub (fun FmtE@ [
        (param val r64)
        (param precision u32)
        (param force_sign bool)
        (param out (slice! u8))] uint :
    @doc "worst case -x.[precision]e-xxx"
    (if (< (len out) (+ (as precision uint) 8)) :
        (return 0)
     :)
    (if (num_real::r64_is_subnormal [val]) :
        (return 0)
     :)
    (let! t s32 (find_t [val]))
    @doc """fmt::print#("@@@ ", t, "\n")"""
    (let x auto (div_by_power_of_10 [val t]))
    (let! mantissa auto (+ (num_real::r64_raw_mantissa [x]) (<< 1 52)))
    (let exponent auto (- (num_real::r64_raw_exponent [x]) num_real::r64_exponent_bias))
    (let is_negative auto (num_real::r64_is_negative [x]))
    (fmt::assert# (&& (>= exponent 49) (<= exponent 52)) ["out of bounds\n"])
    (if (!= exponent 52) :
        (-= t 1)
        (*= mantissa 10)
        (>>= mantissa (as (- 52_s32 exponent) u64))
     :)
    (let! buffer (array 32 u8) undef)
    (let num_digits uint (fmt_int::FmtDec@ [mantissa (as buffer (slice! u8))]))
    @doc "decimal rounding if we drop digits"
    (if (> num_digits (as (+ precision 1) uint)) :
        (let! pos auto (+ precision 2))
        (let! carry bool (>= (at buffer pos) '5'))
        (while carry :
            (if (== pos 0) :
                (+= t 1)
                (for j (as (+ precision 2) s32) 1_s32 -1 :
                    (= (at buffer j) (at buffer (- j 1))))
                (= (at buffer 0) '1')
                (break)
             :)
            (-= pos 1)
            (if (== (at buffer pos) '9') :
                (= (at buffer pos) '0')
             :
                (= carry false)
                (+= (at buffer pos) 1)))
     :)
    (+= t (as (- num_digits 1) s32))
    (let! i auto 0_uint)
    (cond :
        (case is_negative :
            (= (at out i) '-')
            (+= i 1))
        (case force_sign :
            (= (at out i) '+')
            (+= i 1)))
    (= (at out i) (at buffer 0))
    (+= i 1)
    (= (at out i) '.')
    (+= i 1)
    (for j 1 (as (+ precision 1) uint) 1 :
        (if (< j num_digits) :
            (= (at out i) (at buffer j))
         :
            (= (at out i) '0'))
        (+= i 1))
    (= (at out i) 'e')
    (+= i 1)
    (let num_exp_digits auto (FmtExponentE [t (as buffer (slice! u8))]))
    (for j 0 num_exp_digits 1 :
        (= (at out i) (at buffer j))
        (+= i 1))
    @doc """fmt::print#("@@@ ", t, " ",  exponent, " ",  buffer, " out:", out, "\n")"""
    (return i))
)

