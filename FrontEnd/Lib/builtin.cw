(module $builtin [] :

(fun @pub @extern memcpy [
        (param dst (ptr @mut u8))
        (param src (ptr u8))
        (param size uint)] (ptr @mut u8) :)


(fun @pub @cdecl @extern write [
        (param fd s32)
        (param s (ptr u8))
        (param size uint)] sint :)


(defrec @pub TimeSpec :
    (field sec uint)
    (field nano_sec uint))


(fun @pub @cdecl  @extern nanosleep [(param req (ptr TimeSpec)) (param rem (ptr @mut TimeSpec))] s32 :)


(fun @pub @extern SysErrorPrint [(param buffer (slice u8))] void :)


(fun @pub SysPrint [(param buffer (slice u8))] void :
    (stmt (call write [
            1_s32
            (front buffer)
            (len buffer)])))


(global @pub FORMATED_STRING_MAX_LEN uint 4096)


@doc "macro for while-loop"
(macro @pub while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if $cond :
            :
            (break))
        $body
        (continue)))

@doc """macro for number range for-loop, 

The type of the loop variable is determined by $end"""
(macro @pub for STMT_LIST [
        (mparam $index ID)

        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (macro_let $end_eval (typeof $end) $end)
    (macro_let $step_eval (typeof $end) $step)
    (macro_let @mut $it (typeof $end) $start)
    (block _ :
        (if (>= $it $end_eval) :
            (break)
            :)
        (macro_let $index auto $it)
        (= $it (+ $it $step_eval))
        $body
        (continue)))


(fun @pub mymemcpy [
        (param dst (ptr @mut u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i 0 size 1 :
        (= (^ (incp dst i)) (^ (incp src i))))
    (return size))


@doc "This gets passed to the actual formatters which decide how to interpret the options."
(defrec @pub SysFormatOptions :
    @doc "min width"
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool))


(fun @polymorphic SysRender [
        (param v bool)
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))
    (let n uint (min (len buffer) (len s)))
    (return (call mymemcpy [
            (front @mut buffer)
            (front s)
            n])))


(macro unsigned_to_str EXPR [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        @doc "a slice for the output string"
        (mparam $out EXPR)] [$v $out_eval $tmp $pos] :
    (expr :
        @doc "unsigned to str with given base"
        (macro_let @mut $v auto $val)
        (macro_let @mut $tmp auto (array_val $max_width u8))
        (macro_let @mut $pos uint $max_width)
        (macro_let $out_eval auto $out)
        (block _ :
            (-= $pos 1)
            (let c auto (% $v $base))
            (let @mut c8 auto (as c u8))
            (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
            (= (at $tmp $pos) c8)
            (/= $v $base)
            (if (!= $v 0) :
                (continue)
                :))
        (let n uint (min (- $max_width $pos) (len $out_eval)))
        (return (call mymemcpy [
                (front @mut $out_eval)
                (incp (front $tmp) $pos)
                n]))))


(fun slice_incp [(param s (slice @mut u8)) (param inc uint)] (slice @mut u8) :
    (let n uint (min inc (len s)))
    (return (slice_val (incp (front @mut s) n) (- (len s) n))))


(fun u8_to_str [(param v u8) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u16_to_str [(param v u16) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u32_to_str [(param v u32) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u64_to_str [(param v u64) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun s32_to_str [(param v s32) (param out (slice @mut u8))] uint :
    (if (== (len out) 0) :
        (return 0)
        :)
    (if (< v 0) :
        (let v_unsigned auto (- 0_s32 v))
        (= (at out 0) '-')
        (return (+ 1 (unsigned_to_str v_unsigned 10 32_uint (call slice_incp [out 1]))))
        :
        (return (unsigned_to_str (as v u32) 10 32_uint out))))


(fun str_to_u32 [(param s (slice u8))] u32 :
    (let @mut x auto 0_u32)
    (for i 0 (len s) 1 :
        (*= x 10)
        (let c auto (at s i))
        (+= x (as (- c '0') u32)))
    (return x))


(fun @polymorphic SysRender [
        (param v u8)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u8_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u16)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u16_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u32)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u32_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u64)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u64_to_str [v out])))


(fun @polymorphic SysRender [
        (param v s32)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call s32_to_str [v out])))


(fun @polymorphic SysRender [
        (param v (slice u8))
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (call mymemcpy [
            (front @mut buffer)
            (front v)
            n])))


(type @pub @wrapped u32_hex u32)
(type @pub @wrapped u16_hex u16)
(type @pub @wrapped u8_hex u8)

(fun u32_to_hex_str [(param v u32) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 16 32_uint out)))

(fun u16_to_hex_str [(param v u16) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 16 32_uint out)))

(fun u8_to_hex_str [(param v u8) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str v 16 32_uint out)))

(fun @polymorphic SysRender [
        (param v u32_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u32_to_hex_str [(as v u32) out])))

(fun @polymorphic SysRender [
        (param v u16_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u16_to_hex_str [(as v u16) out])))

(fun @polymorphic SysRender [
        (param v u8_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call u8_to_hex_str [(as v u8) out])))


(type @pub @wrapped rune u8)


(fun @polymorphic SysRender [
        (param v rune)
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (if (== (len buffer) 0) :
        (return 0)
        :
        (= (^ (front @mut buffer)) (as v u8))
        (return 1)))


(global INF_POS auto "inf")


(global INF_NEG auto "-inf")


(global NAN_POS auto "nan")


(global NAN_NEG auto "-nan")


(fun slice_copy [(param src (slice u8)) (param dst (slice @mut u8))] uint :
    (let n uint (min (len src) (len dst)))
    (return (call mymemcpy [
            (front @mut dst)
            (front src)
            n])))


(fun nan_to_str [
        (param is_non_neg bool)
        (param frac_is_zero bool)
        (param out (slice @mut u8))] uint :
    (if frac_is_zero :
        (if is_non_neg :
            (return (call slice_copy [INF_POS out]))
            :
            (return (call slice_copy [INF_NEG out])))
        :
        (if is_non_neg :
            (return (call slice_copy [NAN_POS out]))
            :
            (return (call slice_copy [NAN_NEG out])))))


@doc """r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)
        exponentiation bias is 1023
        https://en.wikipedia.org/wiki/Double-precision_floating-point_format
        https://observablehq.com/@jrus/hexfloat"""
(fun r64_to_hex_str [(param val r64) (param out (slice @mut u8))] uint :
    (let val_bits auto (bitcast val s64))
    (let @mut frac_bits auto (and val_bits 0xf_ffff_ffff_ffff))
    (let exp_bits auto (and (>> val_bits 52) 0x7ff))
    (let sign_bit auto (and (>> val_bits 63) 1))
    (if (== exp_bits 0x7ff) :
        (return (call nan_to_str [
                (== sign_bit 0)
                (== frac_bits 0)
                out]))
        :)
    (let @mut buf auto (front @mut out))
    (let @mut exp auto (- exp_bits 1023))
    (let @mut i uint 0)
    (if (!= sign_bit 0) :
        (= (^ (incp buf i)) '-')
        (+= i 1)
        :)
    (= (^ (incp buf i)) '0')
    (+= i 1)
    (= (^ (incp buf i)) 'x')
    (+= i 1)
    (= (^ (incp buf i)) (? (== exp_bits 0) '0' '1'))
    (+= i 1)
    (= (^ (incp buf i)) '.')
    (+= i 1)
    (while (!= frac_bits 0) :
        (let c auto (as (>> frac_bits 48) u8))
        (= (^ (incp buf i)) (? (<= c 9) (+ c '0') (+ c (- 'a' 10))))
        (+= i 1)
        (and= frac_bits 0xffff_ffff_ffff)
        (<<= frac_bits 4))
    (= (^ (incp buf i)) 'p')
    (+= i 1)
    (if (< exp 0) :
        (= (^ (incp buf i)) '-')
        (+= i 1)
        (= exp (- 0_s64 exp))
        :)
    (let rest auto (slice_val (incp buf i) (- (len out) i)))
    (+= i (call u64_to_str [(as exp u64) rest]))
    (return i))


(type @pub @wrapped r64_hex r64)


(fun @polymorphic SysRender [
        (param v r64_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (call r64_to_hex_str [(as v r64) out])))


(macro @pub print STMT_LIST [
        @doc "list of items to be printed"
        (mparam $parts EXPR_LIST)] [$buffer $curr $options] :
    (macro_let @mut $buffer auto (array_val FORMATED_STRING_MAX_LEN u8))
    (macro_let @mut $curr uint 0)
    (macro_let @mut @ref $options auto (rec_val SysFormatOptions []))
    (macro_for $i $parts :
        (+= $curr (call @polymorphic SysRender [
                $i
                (slice_val (incp (front @mut $buffer) $curr) (- (len $buffer) $curr))
                (& @mut $options)])))
    (stmt (call SysPrint [(slice_val (front $buffer) $curr)])))


(fun strz_to_slice [(param s (ptr u8))] (slice u8) :
    (let @mut i uint 0)
    (while (!= (^ (incp s i)) 0) :
        (+= i 1))
    (return (slice_val s i)))


(macro @pub assert STMT [(mparam $cond EXPR) (mparam $parts EXPR_LIST)] [] :
    (if $cond :
        :
        (print [(stringify $cond) $parts])
        (trap)))


@doc "macro for c-style -> operator"
(macro @pub -> EXPR [(mparam $pointer EXPR) (mparam $field FIELD)] [] :
    (. (^ $pointer) $field))
)

