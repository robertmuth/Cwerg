(module fmt [] :
(import os)
(fun @pub @extern memcpy [
        (param dst (ptr @mut u8))
        (param src (ptr u8))
        (param size uint)] (ptr @mut u8) :)


(global @pub FORMATED_STRING_MAX_LEN uint 4096)


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
    (return (mymemcpy [
            (front @mut buffer)
            (front s)
            n])))


(macro unsigned_to_str! EXPR [
        (mparam $val EXPR)
        (mparam $base EXPR)
        (mparam $max_width EXPR)
        @doc "a slice for the output string"
        (mparam $out EXPR)] [$v $out_eval $tmp $pos] :
    (expr :
        @doc "unsigned to str with given base"
        ($let @mut $v auto $val)
        ($let @mut $tmp auto (array_val $max_width u8))
        ($let @mut $pos uint $max_width)
        ($let $out_eval auto $out)
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
        (return (mymemcpy [
                (front @mut $out_eval)
                (incp (front $tmp) $pos)
                n]))))


(fun slice_incp [(param s (slice @mut u8)) (param inc uint)] (slice @mut u8) :
    (let n uint (min inc (len s)))
    (return (slice_val (incp (front @mut s) n) (- (len s) n))))


(fun u8_to_str [(param v u8) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 10 32_uint out)))


(fun u16_to_str [(param v u16) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 10 32_uint out)))


(fun u32_to_str [(param v u32) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 10 32_uint out)))


(fun u64_to_str [(param v u64) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 10 32_uint out)))


(fun s32_to_str [(param v s32) (param out (slice @mut u8))] uint :
    (if (== (len out) 0) :
        (return 0)
        :)
    (if (< v 0) :
        (let v_unsigned auto (- 0_s32 v))
        (= (at out 0) '-')
        (return (+ 1 (unsigned_to_str! v_unsigned 10 32_uint (slice_incp [out 1]))))
        :
        (return (unsigned_to_str! (as v u32) 10 32_uint out))))


(fun @pub str_to_u32 [(param s (slice u8))] u32 :
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
    (return (u8_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u16)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u16_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u32)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u32_to_str [v out])))


(fun @polymorphic SysRender [
        (param v u64)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u64_to_str [v out])))


(fun @polymorphic SysRender [
        (param v s32)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (s32_to_str [v out])))


(fun @polymorphic SysRender [
        (param v (slice u8))
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (mymemcpy [
            (front @mut buffer)
            (front v)
            n])))


(type @pub @wrapped u64_hex u64)
(type @pub @wrapped u32_hex u32)
(type @pub @wrapped u16_hex u16)
(type @pub @wrapped u8_hex u8)

(fun u64_to_hex_str [(param v u64) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 16 64_uint out)))

(fun u32_to_hex_str [(param v u32) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 16 32_uint out)))

(fun u16_to_hex_str [(param v u16) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 16 32_uint out)))

(fun u8_to_hex_str [(param v u8) (param out (slice @mut u8))] uint :
    (return (unsigned_to_str! v 16 32_uint out)))

(fun @polymorphic SysRender [
        (param v u64_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u64_to_hex_str [(unwrap v) out])))

(fun @polymorphic SysRender [
        (param v u32_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u32_to_hex_str [(unwrap v) out])))

(fun @polymorphic SysRender [
        (param v u16_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u16_to_hex_str [(unwrap v) out])))

(fun @polymorphic SysRender [
        (param v u8_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (u8_to_hex_str [(unwrap v) out])))


(type @pub @wrapped rune u8)


(fun @polymorphic SysRender [
        (param v rune)
        (param buffer (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (if (== (len buffer) 0) :
        (return 0)
        :
        (= (^ (front @mut buffer)) (unwrap v))
        (return 1)))


(global INF_POS auto "inf")


(global INF_NEG auto "-inf")


(global NAN_POS auto "nan")


(global NAN_NEG auto "-nan")


(fun slice_copy [(param src (slice u8)) (param dst (slice @mut u8))] uint :
    (let n uint (min (len src) (len dst)))
    (return (mymemcpy [
            (front @mut dst)
            (front src)
            n])))


(fun nan_to_str [
        (param is_non_neg bool)
        (param frac_is_zero bool)
        (param out (slice @mut u8))] uint :
    (if frac_is_zero :
        (if is_non_neg :
            (return (slice_copy [INF_POS out]))
            :
            (return (slice_copy [INF_NEG out])))
        :
        (if is_non_neg :
            (return (slice_copy [NAN_POS out]))
            :
            (return (slice_copy [NAN_NEG out])))))

(fun to_hex_digit [(param digit u8)] u8 :
  (return (? (<= digit 9) (+ digit '0') (+ digit (- 'a' 10))))
)

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
        (return (nan_to_str [
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
        (= (^ (incp buf i)) (to_hex_digit [(as (>> frac_bits 48) u8)]))
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
    (+= i (u64_to_str [(as exp u64) rest]))
    (return i))


(type @pub @wrapped r64_hex r64)


(fun @polymorphic SysRender [
        (param v r64_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (return (r64_to_hex_str [(unwrap v) out])))

(type @pub @wrapped str_hex (slice u8))

(fun @polymorphic SysRender [
        (param v str_hex)
        (param out (slice @mut u8))
        (param options (ptr @mut SysFormatOptions))] uint :
    (let v_str (slice u8) (unwrap v))
    (let dst_len auto (len v_str))
    (if (<= dst_len (len out))
    : (for i 0 dst_len 1 :
        (let c u8 (at v_str i))
        (let o1 uint (* i 2))
        (let o2 uint (+ o1 1))
        (= (at out o1) (to_hex_digit [(>> c 4)]))
        (= (at out o2) (to_hex_digit [(and c 15)]))
      )
      (return (* dst_len 2))
    :
    (for i 0 (len out) 1 :   (= (at out i) '.'))
    (return 0))
)

(macro @pub print! STMT_LIST [
        @doc "list of items to be printed"
        (mparam $parts EXPR_LIST)] [$buffer $curr $options] :
    ($let @mut $buffer auto (array_val FORMATED_STRING_MAX_LEN u8))
    ($let @mut $curr uint 0)
    ($let @mut @ref $options auto (rec_val SysFormatOptions []))
    ($for $i $parts :
        (+= $curr (@polymorphic SysRender [
                $i
                (slice_val (incp (front @mut $buffer) $curr) (- (len $buffer) $curr))
                (& @mut $options)])))
    (shed (os::write [(unwrap os::Stdout) (front $buffer) $curr])))


(fun @pub strz_to_slice [(param s (ptr u8))] (slice u8) :
    (let @mut i uint 0)
    (while (!= (^ (incp s i)) 0) :
        (+= i 1))
    (return (slice_val s i)))


(macro @pub assert! STMT [(mparam $cond EXPR) (mparam $parts EXPR_LIST)] [] :
    (if $cond :
        :
        (print! [(stringify $cond) $parts])
        (trap)))

)
