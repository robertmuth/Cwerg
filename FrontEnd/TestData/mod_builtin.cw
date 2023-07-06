(module $builtin [] :
(fun pub extern memcpy [
        (param dst (ptr mut u8))
        (param src (ptr u8))
        (param size uint)] (ptr mut u8) :)


(fun pub extern write [
        (param fd s32)
        (param s (ptr u8))
        (param size uint)] sint :)


(defrec pub TimeSpec :
    (field sec uint)
    (field nano_sec uint)
)

(fun pub extern nanosleep [(param req (ptr TimeSpec)) 
                           (param rem (ptr mut TimeSpec))] s32 :)

(fun pub extern SysErrorPrint [(param buffer (slice u8))] void :)


(fun pub SysPrint [(param buffer (slice u8))] void :
    (stmt (call write [
            1_s32
            (front buffer)
            (len buffer)])))


(global pub FORMATED_STRING_MAX_LEN uint 4096)


(# "macro for while-loop")
(macro pub while STMT [(mparam $cond EXPR) (mparam $body STMT_LIST)] [] :
    (block _ :
        (if (macro_id $cond) :
            :
            break)
        (macro_id $body)
        continue))


(# "macro for number range for-loop")
(macro pub for STMT_LIST [
        (mparam $index ID)
        (mparam $type TYPE)
        (mparam $start EXPR)
        (mparam $end EXPR)
        (mparam $step EXPR)
        (mparam $body STMT_LIST)] [$end_eval $step_eval $it] :
    (macro_let $end_eval (macro_id $type) (macro_id $end))
    (macro_let $step_eval (macro_id $type) (macro_id $step))
    (macro_let mut $it (macro_id $type) (macro_id $start))
    (block _ :
        (if (>= (macro_id $it) (macro_id $end_eval)) :
            break
            :)
        (macro_let $index auto (macro_id $it))
        (= (macro_id $it) (+ (macro_id $it) (macro_id $step_eval)))
        (macro_id $body)
        continue))


(fun pub mymemcpy [
        (param dst (ptr mut u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i uint 0 size 1 :
        (= (^ (incp dst i undef)) 
        (^ (incp src i undef))))
    (return size))


(# "This gets passed to the actual formatters which decide how to interpret the options.")
(defrec pub SysFormatOptions :
    (# "min width")
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool))


(fun polymorphic SysRender [
        (param v bool)
        (param buffer (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))
    (let n uint (min (len buffer) (len s)))
    (return (call mymemcpy [
            (front mut buffer)
            (front s)
            n])))


(macro unsigned_to_str EXPR [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        (# "a slice for the output string")
        (mparam $out ID)] [$v $tmp $pos] :
    (expr :
        (# "unsigned to str with given base")
        (macro_let mut $v auto (macro_id $val))
        (macro_let mut $tmp auto (array_val (macro_id $max_width) u8 []))
        (macro_let mut $pos uint (macro_id $max_width))
        (block _ :
            (-= (macro_id $pos) 1)
            (let c auto (% (macro_id $v) (macro_id $base)))
            (let mut c8 auto (as c u8))
            (+= c8 (? (<= c8 9) '0' (- 'a' 10)))
            (= (at (macro_id $tmp) (macro_id $pos)) c8)
            (/= (macro_id $v) (macro_id $base))
            (if (!= (macro_id $v) 0) :
                continue
                :))
        (let n uint (min (- (macro_id $max_width) (macro_id $pos)) (len (macro_id $out))))
        (return (call mymemcpy [
                (front mut (macro_id $out))
                (incp (front (macro_id $tmp)) (macro_id $pos) undef)
                n]))))


(fun u8_to_str [(param v u8) (param out (slice mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u16_to_str [(param v u16) (param out (slice mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u32_to_str [(param v u32) (param out (slice mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun u64_to_str [(param v u64) (param out (slice mut u8))] uint :
    (return (unsigned_to_str v 10 32_uint out)))


(fun str_to_u32 [(param s (slice u8))] u32 :
    (let mut x auto 0_u32)
    (for i uint 0 (len s) 1 :
        (*= x 10)
        (let c auto (at s i))

        (+= x (as (- c '0') u32))
    )
    (return x)
)


(fun polymorphic SysRender [
        (param v u8)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (return (call u8_to_str [v out])))


(fun polymorphic SysRender [
        (param v u16)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (return (call u16_to_str [v out])))


(fun polymorphic SysRender [
        (param v u32)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (return (call u32_to_str [v out])))


(fun polymorphic SysRender [
        (param v u64)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (return (call u64_to_str [v out])))


(fun polymorphic SysRender [
        (param v (slice u8))
        (param buffer (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (call mymemcpy [
            (front mut buffer)
            (front v)
            n])))


(type pub wrapped rune u8)

(fun polymorphic SysRender [
        (param v rune)
        (param buffer (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (if (== (len buffer) 0) :
        (return 0)
    :
        (= (^ (front mut buffer)) (as v u8))
        (return 1)
    )
)


(global INF_POS auto "inf")


(global INF_NEG auto "-inf")


(global NAN_POS auto "nan")


(global NAN_NEG auto "-nan")


(fun slice_copy [(param src (slice u8)) (param dst (slice mut u8))] uint :
    (let n uint (min (len src) (len dst)))
    (return (call mymemcpy [
            (front mut dst)
            (front src)
            n])))


(fun nan_to_str [
        (param is_non_neg bool)
        (param frac_is_zero bool)
        (param out (slice mut u8))] uint :
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


(# "r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)")
(# "exponentiation bias is 1023")
(# "https://en.wikipedia.org/wiki/Double-precision_floating-point_format")
(# "https://observablehq.com/@jrus/hexfloat")
(fun r64_to_hex_str [(param val r64) (param out (slice mut u8))] uint :
    (let val_bits auto (bitcast val s64))
    (let mut frac_bits auto (and val_bits 0xf_ffff_ffff_ffff))
    (let exp_bits auto (and (>> val_bits 52) 0x7ff))
    (let sign_bit auto (and (>> val_bits 63) 1))
    (if (== exp_bits 0x7ff) :
        (return (call nan_to_str [
                (== sign_bit 0)
                (== frac_bits 0)
                out]))
        :)
    (let mut buf auto (front mut out))
    (let mut exp auto (- exp_bits 1023))
    (let mut i uint 0)
    (if (!= sign_bit 0) :
        (= (^ (incp buf i undef)) '-')
        (+= i 1)
        :)
    (= (^ (incp buf i undef)) '0')
    (+= i 1)
    (= (^ (incp buf i undef)) 'x')
    (+= i 1)
    (= (^ (incp buf i undef)) (? (== exp_bits 0) '0' '1'))
    (+= i 1)
    (= (^ (incp buf i undef)) '.')
    (+= i 1)
    (while (!= frac_bits 0) :
            (let c auto (as (>> frac_bits 48) u8))
            (= (^ (incp buf i undef)) (? (<= c 9) (+ c '0') (+ c (- 'a' 10))))
            (+= i 1)
            (and= frac_bits 0xffff_ffff_ffff)
            (<<= frac_bits 4))
    (= (^ (incp buf i undef)) 'p')
    (+= i 1)
    (if (< exp 0) :
        (= (^ (incp buf i undef)) '-')
        (+= i 1)
        (= exp (- 0_s64 exp))
        :)
    (let rest auto (slice_val (incp buf i undef) (- (len out) i)))
    (+= i (call u64_to_str [(as exp u64) rest]))
    (return i))


(type pub wrapped r64_hex r64)


(fun polymorphic SysRender [
        (param v r64_hex)
        (param out (slice mut u8))
        (param options (ptr mut SysFormatOptions))] uint :
    (return (call r64_to_hex_str [(as v r64) out])))


(macro pub print STMT_LIST [
        (# "list of items to be printed")
        (mparam $parts EXPR_LIST)] [$buffer $curr $options] :
    (macro_let mut $buffer auto (array_val FORMATED_STRING_MAX_LEN u8 []))
    (macro_let mut $curr uint 0)
    (macro_let mut ref $options auto (rec_val SysFormatOptions []))
    (macro_for $i $parts :
        (+= (macro_id $curr) (call polymorphic SysRender [
                (macro_id $i)
                (slice_val (incp (front mut (macro_id $buffer)) (macro_id $curr) undef) (- (len (macro_id $buffer)) (macro_id $curr)))
                (& mut (macro_id $options))])))
    (stmt (call SysPrint [(slice_val (front (macro_id $buffer)) (macro_id $curr))])))


(fun strz_to_slice [(param s (ptr u8))] (slice u8) :
    (let mut i uint 0)
    (while (!= (^ (incp s i undef)) 0) : 
        (+= i 1))
    (return (slice_val s i)))



(macro pub assert STMT [(mparam $cond EXPR) (mparam $parts EXPR_LIST)] [] :
    (if $cond :
        :
        (print [(stringify $cond) $parts])
        (trap)))






)
