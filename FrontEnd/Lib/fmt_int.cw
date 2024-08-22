(module [] :
(import os)

(fun mymemcpy [
        (param dst (ptr! u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i 0 size 1 :
        (= (^ (pinc dst i)) (^ (pinc src i))))
    (return size))

@pub (macro unsigned_to_str# EXPR [
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
)