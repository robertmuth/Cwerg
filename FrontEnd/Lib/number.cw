(module [] :

@doc "https://en.wikipedia.org/wiki/IEEE_754"
@pub (global r64_exponent_bits u32 11)


@pub (global r64_mantissa_bits u32 52)
@pub (global r64_mantissa_mask u64 (- (<< 1 52) 1))

@pub (global r64_exponent_bias u32 1023)

@pub (global r64_exponent_max s32 1023)
@pub (global r64_exponent_min s32 -1022)

@pub (fun make_r64 [(param negative bool)
                    (param exp u64)
                    (param mantissa u64) ] r64 :
    (let! out u64 (as negative u64))
    (<<= out (as r64_exponent_bits u64))
    (or= out exp)
    (<<= out (as r64_mantissa_bits u64))
    (or= out mantissa)
    (return (bitwise_as out r64))
)

@pub (global r32_exponent_bits u32 8)


@pub (global r32_mantissa_bits u32 23)


@pub (global r32_exponent_max s32 127)


@pub (global r32_exponent_min s32 -126)


@pub (fun make_r32 [(param negative bool)
                    (param exp u32)
                    (param mantissa u32) ] r32 :
    (let! out u32 (as negative u32))
    (<<= out r32_exponent_bits)
    (or= out exp)
    (<<= out r32_mantissa_bits)
    (or= out mantissa)
    (return (bitwise_as out r32))
)
)