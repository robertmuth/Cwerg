@doc """Lots of literature referencves :
https://stackoverflow.com/questions/7153979/algorithm-to-convert-an-ieee-754-double-to-a-string
https://www.ryanjuckett.com/printing-floating-point-numbers/"""
(module [] :
(import fmt)

(import parse_num)

(import number)


(global NAN_EXP auto 1024_s32)


(global DENORM_EXP auto -1023_s32)


(global log2_10 r64 3.3219280948873623478703194294)


(global log10_2_to_52 r64 15.653559774527022151114422525)


(global target_range_hi auto (as (<< 1_u64 53) r64))


(global target_range_lo auto (as (<< 1_u64 53) r64))


@doc """compute n so that:
target_range_lo <= x * 10^n < target_range_hi"""
(fun exp10_multiplier [(param x r64)] s32 :
    (let biased_exp auto (- (as (>> (paren (<< (bitwise_as x u64) 1)) 53) s32) number::r64_exponent_bias))
    (if (|| (== biased_exp DENORM_EXP) (== biased_exp NAN_EXP)) :
        (return biased_exp)
     :)
    @doc "first approximation of a power of 10"
    (let! exp10 s32 (as (- log10_2_to_52 (/ (as biased_exp r64) log2_10)) s32))
    (return 0))


@pub (fun fmt_r64 [(param x r64) (param out (slice! u8))] void :)
)

