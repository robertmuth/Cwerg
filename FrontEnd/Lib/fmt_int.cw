(module [] :

(fun mymemcpy [
        (param dst (ptr! u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i 0 size 1 :
        (= (^ (pinc dst i)) (^ (pinc src i))))
    (return size))


(macro unsigned_to_str# EXPR [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        @doc "a slice for the output string"
        (mparam $out EXPR)] [$v $out_eval $tmp $pos] :
    (expr :
        @doc "unsigned to str with given base"
        (mlet! $v auto $val)
        (mlet! $tmp auto (array_val 1024 u8))
        (mlet! $pos uint $max_width)
        (mlet $out_eval auto $out)
        (block _ :
            (-= $pos 1)
            (let c auto (% $v $base))
            (let! c8 auto (as c u8))
            (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
            (= (at $tmp $pos) c8)
            (/= $v $base)
            (if (!= $v 0) :
                (continue)
             :))
        (let n uint (min (- $max_width $pos) (len $out_eval)))
        (return (mymemcpy [(front! $out_eval) (pinc (front $tmp) $pos) n]))))


@doc """Why the polymorphism?
        It makes shorter names and avoids the need for separate
        uint and sint handling"""
@pub (fun FmtDec@ [(param v u8) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 10 32_uint out)))


@pub (fun FmtDec@ [(param v u16) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 10 32_uint out)))


@pub (fun FmtDec@ [(param v u32) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 10 32_uint out)))


@pub (fun FmtDec@ [(param v u64) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 10 32_uint out)))


@pub (fun FmtDec@ [(param v s16) (param out (slice! u8))] uint :
    (if (== (len out) 0) :
        (return 0)
     :)
    (if (< v 0) :
        (let v_unsigned auto (- 0_s16 v))
        (= (at out 0) '-')
        (return (+ 1 (FmtDec@ [v_unsigned (slice_inc_or_die# out 1)])))
     :
        (return (FmtDec@ [(as v u16) out]))))


@pub (fun FmtDec@ [(param v s32) (param out (slice! u8))] uint :
    (if (== (len out) 0) :
        (return 0)
     :)
    (if (< v 0) :
        (= (at out 0) '-')
        (let v_unsigned auto (as (- 0_s32 v) u32))
        (return (+ 1 (FmtDec@ [v_unsigned (slice_inc_or_die# out 1)])))
     :
        (return (FmtDec@ [(as v u32) out]))))


@doc """Why the polymorphism?
        It makes shorter names and avoids the need for separate
        uint and sint handling"""
@pub (fun FmtHex@ [(param v u64) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 16 64_uint out)))


@pub (fun FmtHex@ [(param v u32) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 16 32_uint out)))


@pub (fun FmtHex@ [(param v u16) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 16 32_uint out)))


@pub (fun FmtHex@ [(param v u8) (param out (slice! u8))] uint :
    (return (unsigned_to_str# v 16 32_uint out)))
)
