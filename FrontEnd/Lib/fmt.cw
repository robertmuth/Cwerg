(module [] :
(import os)
(import fmt_int)
(import fmt_real)

@pub @extern (fun memcpy [
        (param dst (ptr! u8))
        (param src (ptr u8))
        (param size uint)] (ptr! u8) :)


@pub (global FORMATED_STRING_MAX_LEN uint 4096)


@pub (fun mymemcpy [
        (param dst (ptr! u8))
        (param src (ptr u8))
        (param size uint)] uint :
    (for i 0 size 1 :
        (= (^ (pinc dst i)) (^ (pinc src i))))
    (return size))


@doc "This gets passed to the actual formatters which decide how to interpret the options."
@pub (defrec SysFormatOptions :
    @doc "min width"
    (field witdh u8)
    (field precission u8)
    (field padding u8)
    (field style u8)
    (field show_sign bool)
    (field left_justify bool))


(fun SysRender@ [
        (param v bool)
        (param buffer (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (let s auto (? v (as "true" (slice u8)) (as "false" (slice u8))))
    (let n uint (min (len buffer) (len s)))
    (return (mymemcpy [(front! buffer) (front s) n])))


@pub (fun str_to_u32 [(param s (slice u8))] u32 :
    (let! x auto 0_u32)
    (for i 0 (len s) 1 :
        (*= x 10)
        (let c auto (at s i))
        (+= x (as (- c '0') u32)))
    (return x))


(fun SysRender@ [
        (param v u8)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))


(fun SysRender@ [
        (param v u16)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))


(fun SysRender@ [
        (param v u32)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))


(fun SysRender@ [
        (param v u64)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))

(fun SysRender@ [
        (param v s16)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))

(fun SysRender@ [
        (param v s32)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtDec@ [v out])))


(fun SysRender@ [
        (param v (slice u8))
        (param buffer (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (mymemcpy [(front! buffer) (front v) n])))

(fun SysRender@ [
        (param v (slice! u8))
        (param buffer (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (let n uint (min (len buffer) (len v)))
    (return (mymemcpy [(front! buffer) (front v) n])))

@pub (@wrapped type uint_hex uint)


@pub (@wrapped type u64_hex u64)


@pub (@wrapped type u32_hex u32)


@pub (@wrapped type u16_hex u16)


@pub (@wrapped type u8_hex u8)


(fun SysRender@ [
        (param v uint_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtHex@ [(unwrap v) out])))


(fun SysRender@ [
        (param v u64_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtHex@ [(unwrap v) out])))


(fun SysRender@ [
        (param v u32_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtHex@ [(unwrap v) out])))


(fun SysRender@ [
        (param v u16_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtHex@ [(unwrap v) out])))


(fun SysRender@ [
        (param v u8_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_int::FmtHex@ [(unwrap v) out])))


@pub (@wrapped type rune u8)


(fun SysRender@ [
        (param v rune)
        (param buffer (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (if (== (len buffer) 0) :
        (return 0)
     :
        (= (^ (front! buffer)) (unwrap v))
        (return 1)))


@pub (@wrapped type r64_hex r64)


(fun SysRender@ [
        (param v r64_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_real::FmtHex@ [(unwrap v) out])))

(fun SysRender@ [
        (param v r64)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (return (fmt_real::FmtE@ [v 6 false out])))

@pub (@wrapped type str_hex (slice u8))

(fun to_hex_digit [(param digit u8)] u8 :
    (return (? (<= digit 9) (+ digit '0') (+ digit (- 'a' 10)))))

(fun SysRender@ [
        (param v str_hex)
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (let v_str (slice u8) (unwrap v))
    (let dst_len auto (len v_str))
    (if (<= dst_len (len out)) :
        (for i 0 dst_len 1 :
            (let c u8 (at v_str i))
            (let o1 uint (* i 2))
            (let o2 uint (+ o1 1))
            (= (at out o1) (to_hex_digit [(>> c 4)]))
            (= (at out o2) (to_hex_digit [(and c 15)])))
        (return (* dst_len 2))
     :
        (for i 0 (len out) 1 :
            (= (at out i) '.'))
        (return 0)))


(fun SysRender@ [
        (param v (ptr void))
        (param out (slice! u8))
        (param options (ptr! SysFormatOptions))] uint :
    (let h auto (wrap_as (bitwise_as v uint) uint_hex))
    (return (SysRender@ [h out options])))


@pub (macro print# STMT_LIST [
        @doc "list of items to be printed"
        (mparam $parts EXPR_LIST_REST)] [$buffer $curr $options] :
    (mlet! $buffer auto (vec_val FORMATED_STRING_MAX_LEN u8))
    (mlet! $curr uint 0)
    (@ref mlet! $options auto (rec_val SysFormatOptions []))
    (mfor $i $parts :
        (+= $curr (SysRender@ [$i (slice_val (pinc (front! $buffer) $curr) (- (len $buffer) $curr)) (&! $options)])))
    (do (os::write [(unwrap os::Stdout) (front $buffer) $curr])))


@doc "same as above but takes an EXPR_LIST - should only be used by other macros"
@pub (macro print_list# STMT_LIST [(mparam $parts EXPR_LIST)] [$buffer $curr $options] :
    (mlet! $buffer auto (vec_val FORMATED_STRING_MAX_LEN u8))
    (mlet! $curr uint 0)
    (@ref mlet! $options auto (rec_val SysFormatOptions []))
    (mfor $i $parts :
        (+= $curr (SysRender@ [$i (slice_val (pinc (front! $buffer) $curr) (- (len $buffer) $curr)) (&! $options)])))
    (do (os::write [(unwrap os::Stdout) (front $buffer) $curr])))


@pub (fun strz_to_slice [(param s (ptr u8))] (slice u8) :
    (let! i uint 0)
    (while (!= (^ (pinc s i)) 0) :
        (+= i 1))
    (return (slice_val s i)))


@pub (macro assert# STMT [(mparam $cond EXPR) (mparam $parts EXPR_LIST_REST)] [] :
    (if $cond :
     :
        (print# (stringify $cond))
        (print_list# $parts)
        (trap)))
)
