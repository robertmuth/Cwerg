@doc """parse numbers from u8 to int/real
https://gregstoll.com/~gregstoll/floattohex/"""
(module [] :
(import num_real)

(import fmt)


@pub (@wrapped type ParseError void)


@pub (global ParseErrorVal auto (wrap_as void_val ParseError))


(fun is_hex_digit [(param c u8)] bool :
    (return (|| (&& (>= c '0') (<= c '9')) (&& (>= c 'a') (<= c 'f')))))


(fun hex_digit_val [(param c u8)] u8 :
    (return (? (<= c '9') (- c '0') (+ (- c 'a') 10))))


(fun is_dec_digit [(param c u8)] bool :
    (return (&& (>= c '0') (<= c '9'))))


(fun dec_digit_val [(param c u8)] u8 :
    (return (- c '0')))


@doc "this macros capture i,n,s from the environment"
(macro next_char# STMT_LIST [(mparam $c ID) (mparam $body STMT_LIST)] [] :
    (if (>= i n) :
        $body
     :)
    (= $c (at s i))
    (+= i 1))


@doc """if we have too many digits we drop the one after the dot but
adjust must adjust the exponent for the one before
this macro captures i,n,s from the environment"""
(macro read_hex_mantissa# STMT_LIST [
        (mparam $c ID)
        (mparam $max_digits EXPR)
        (mparam $val ID)
        (mparam $adjust ID)] [$digits] :
    (block end_of_input :
        (mlet! $digits auto $max_digits)
        @doc "ignore leading zeros"
        (while (== $c '0') :
            (next_char# $c :
                (break end_of_input)))
        (while (is_hex_digit [$c]) :
            (if (== $digits 0) :
                (+= $adjust 1)
             :
                (*= $val 16)
                (+= $val (as (hex_digit_val [$c]) u64))
                (-= $digits 1))
            (next_char# $c :
                (break end_of_input)))
        (if (== c '.') :
            (next_char# $c :
                (break end_of_input))
            (while (is_hex_digit [$c]) :
                (if (!= $digits 0) :
                    (*= $val 16)
                    (+= $val (as (hex_digit_val [$c]) u64))
                    (-= $adjust 1)
                    (-= $digits 1)
                 :)
                (next_char# $c :
                    (break end_of_input)))
         :)))


(macro read_dec_mantissa# STMT_LIST [
        (mparam $c ID)
        (mparam $max_digits EXPR)
        (mparam $val ID)
        (mparam $adjust ID)
        (mparam $imprecise ID)] [$digits] :
    (block end_of_input :
        (mlet! $digits auto $max_digits)
        @doc "ignore leading zeros"
        (while (== $c '0') :
            (next_char# $c :)
            (break end_of_input))
        (while (is_dec_digit [$c]) :
            (if (== $digits 0) :
                (if (!= $c '0') :
                    (= $imprecise true)
                 :)
                (+= $adjust 1)
             :
                (*= $val 10)
                (+= $val (as (dec_digit_val [$c]) u64))
                (-= $digits 1))
            (next_char# $c :
                (break end_of_input)))
        (if (== c '.') :
            (next_char# $c :
                (break end_of_input))
            (while (is_dec_digit [$c]) :
                (if (!= $digits 0) :
                    (*= $val 10)
                    (+= $val (as (dec_digit_val [$c]) u64))
                    (-= $adjust 1)
                    (-= $digits 1)
                 :
                    (if (!= $c '0') :
                        (= $imprecise true)
                     :))
                (next_char# $c :
                    (break end_of_input)))
         :)))


@doc "this macro captures i,n,s from the environment"
(macro read_dec_exponent# STMT_LIST [(mparam $c ID) (mparam $exp ID)] [$negative] :
    (mlet! $negative auto false)
    (if (|| (== $c '-') (== $c '+')) :
        (if (== $c '-') :
            (= $negative true)
         :)
        (next_char# $c :
            (return ParseErrorVal))
     :)
    (while (is_dec_digit [$c]) :
        (*= $exp 10)
        (+= $exp (as (dec_digit_val [$c]) s32))
        (next_char# $c :
            (break)))
    (if $negative :
        (= $exp (~ exp))
     :))


@doc """expects a string without sign and without '0x' prefix
note. this code does not perform
* denormalization - this is not supported by Cwerg
* rounding - the whole point of hex float is to control the mantissa exactly"""
(fun parse_r64_hex_helper [(param s (span u8)) (param negative bool)] (union [ParseError r64]) :
    (let! i uint 0)
    (let n auto (len s))
    (let! c u8)
    (next_char# c :
        (return ParseErrorVal))
    (let! mant auto 0_u64)
    (let! exp_adjustments auto 0_s32)
    (let! exp auto 0_s32)
    @doc "allow an extra 2 digits beyond the 52 / 4 = 13 mantissa hex digits"
    (read_hex_mantissa# c (+ (/ num_real::r64_mantissa_bits 4) 2) mant exp_adjustments)
    (if (== c 'p') :
        (next_char# c :
            (return ParseErrorVal))
        (read_dec_exponent# c exp)
     :)
    @doc """TODO: check that we have consumed all chars
early out for simple corner case"""
    (if (== mant 0) :
        (return (? negative -0_r64 +0_r64))
     :)
    (+= exp (* exp_adjustments 4))
    (+= exp (as num_real::r64_mantissa_bits s32))
    @doc """gitfmt::print# ("BEFORE mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
we want the highest set bit to be at position num_real::r64_mantissa_bits + 1
replace both while loops utilizing "count leading zeros""""
    (while (== (>> mant (as num_real::r64_mantissa_bits u64)) 0) :
        @doc """fmt::print# ("@@ shift ", mant, "\n")"""
        (<<= mant 8)
        (-= exp 8))
    (while (!= (>> mant (as num_real::r64_mantissa_bits u64)) 1) :
        (>>= mant 1)
        (+= exp 1))
    (if (> exp num_real::r64_exponent_max) :
        @doc "maybe return inf"
        (return ParseErrorVal)
     :)
    (if (< exp num_real::r64_exponent_min) :
        @doc """we do not support denormalization
maybe return 0.0"""
        (return ParseErrorVal)
     :)
    (+= exp num_real::r64_raw_exponent_bias)
    @doc """fmt::print# ("AFTER mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
final touches"""
    (let exp_u64 auto (and (as exp u64) num_real::r64_exponent_mask))
    (and= mant num_real::r64_mantissa_mask)
    (return (num_real::make_r64 [negative exp_u64 mant])))


@pub (fun parse_r64_hex [(param s (span u8))] (union [ParseError r64]) :
    (let! n auto (len s))
    (if (< n 5) :
        (return ParseErrorVal)
     :)
    (let! i uint 0)
    (let! c u8 (at s i))
    (let! negative auto false)
    (if (|| (== c '-') (== c '+')) :
        (+= i 1)
        (if (== c '-') :
            (= negative true)
         :)
     :)
    (if (|| (!= (at s i) '0') (!= (at s (+ i 1)) 'x')) :
        (return ParseErrorVal)
     :)
    (+= i 2)
    (return (parse_r64_hex_helper [(span_val (pinc (front s) i) (- n i)) negative])))


(fun r64_dec_fast_helper [
        (param mant_orig u64)
        (param exp_orig s32)
        (param negative bool)] r64 :
    (let! exp auto exp_orig)
    (let! mant auto mant_orig)
    (while (>= mant (<< 1 (as (+ num_real::r64_mantissa_bits 1) u64))) :
        (/= mant 10)
        (+= exp 1))
    (if (>= exp 309) :
        (return (? negative -inf_r64 +inf_r64))
     :)
    (if (<= exp -309) :
        (return (? negative -0_r64 +0_r64))
     :)
    @doc "on x86-64 there is not conversion instruction from u64->r64"
    (let! out auto (as (as mant s64) r64))
    (if negative :
        (= out (~ out))
     :)
    (if (>= exp 0) :
        (return (* out (at num_real::powers_of_ten exp)))
     :
        (return (/ out (at num_real::powers_of_ten (~ exp))))))


@pub (fun parse_r64 [(param s (span u8))] (union [ParseError r64]) :
    @doc "index of next char to read"
    (let! i uint 0)
    (let! n auto (len s))
    (let! c u8)
    (next_char# c :
        (return ParseErrorVal))
    (let! negative auto false)
    (if (|| (== c '-') (== c '+')) :
        (if (== c '-') :
            (= negative true)
         :)
        (next_char# c :
            (return ParseErrorVal))
     :)
    (if (== c 'i') :
        (if (|| (|| (!= (+ i 2) n) (!= (at s 1) 'n')) (!= (at s 2) 'f')) :
            (return (? negative -inf_r64 +inf_r64))
         :)
        (return ParseErrorVal)
     :)
    (if (== c 'n') :
        (if (|| (|| (!= (+ i 2) n) (!= (at s 1) 'a')) (!= (at s 2) 'n')) :
            (return (? negative -nan_r64 +nan_r64))
         :)
        (return ParseErrorVal)
     :)
    (if (&& (&& (== c '0') (<= i n)) (== (at s i) 'x')) :
        (+= i 1)
        (return (parse_r64_hex_helper [(span_val (pinc (front s) i) (- n i)) negative]))
     :)
    (let! mant auto 0_u64)
    (let! exp_adjustments auto 0_s32)
    (let! exp auto 0_s32)
    (let! imprecise auto false)
    @doc "log2(10^19) == 63.11"
    (read_dec_mantissa# c 19_s32 mant exp_adjustments imprecise)
    (if (== c 'e') :
        (next_char# c :
            (return ParseErrorVal))
        (read_dec_exponent# c exp)
     :)
    @doc """TODO: check that we have consumed all chars
early out for simple corner case"""
    (if (== mant 0) :
        (return (? negative -0_r64 +0_r64))
     :)
    (+= exp exp_adjustments)
    @doc """try making mantissa smaller, this is a common case, e.g.
555.0000 and helps preserve accuracy"""
    (while (== (% mant 10) 0) :
        (/= mant 10)
        (+= exp 1))
    @doc """fmt::print# (s, " mant: ", mant, " exp: ", exp, "\n")
quick and dirty. may be not be super precise
for possible improvements see:
https://github.com/ziglang/zig/blob/master/lib/std/fmt/parse_float.zig
https://github.com/c3lang/c3c/blob/master/lib/std/core/string_to_real.c3
https://github.com/oridb/mc/blob/master/lib/std/fltparse.myr"""
    (return (r64_dec_fast_helper [mant exp negative])))
)
