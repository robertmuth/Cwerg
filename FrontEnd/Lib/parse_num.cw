@doc """parse numbers from u8 to int/real
https://gregstoll.com/~gregstoll/floattohex/"""
(module [] :
(import number)

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
        (mparam $adjust ID)] [$digits] :
    (block end_of_input :
        (mlet! $digits auto $max_digits)
        @doc "ignore leading zeros"
        (while (== $c '0') :
            (next_char# $c :)
            (break end_of_input))
        (while (is_dec_digit [$c]) :
            (if (== $digits 0) :
                (+= $adjust 1)
             :
                (*= $val 10)
                (+= $val (as (dec_digit_val [$c]) u64))
                (-= $digits 1))
            (next_char# $c :
                (break end_of_input)))
        (if (== c '.') :
            (next_char# $c :
                (return ParseErrorVal))
            (while (is_dec_digit [$c]) :
                (if (!= $digits 0) :
                    (*= $val 10)
                    (+= $val (as (dec_digit_val [$c]) u64))
                    (-= $adjust 1)
                    (-= $digits 1)
                 :)
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
(fun parse_r64_hex_helper [(param s (slice u8)) (param negative bool)] (union [ParseError r64]) :
    (let! i uint 0)
    (let n auto (len s))
    (let! c u8)
    (next_char# c :
        (return ParseErrorVal))
    (let! mant auto 0_u64)
    (let! exp_adjustments auto 0_s32)
    (let! exp auto 0_s32)
    @doc "allow an extra 2 digits beyond the 52 / 4 = 13 mantissa hex digits"
    (read_hex_mantissa# c (+ (/ number::r64_mantissa_bits 4) 2) mant exp_adjustments)
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
    (+= exp (as number::r64_mantissa_bits s32))
    @doc """gitfmt::print# ("BEFORE mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
we want the highest set bit to be at position number::r64_mantissa_bits + 1
replace both while loops utilizing "count leading zeros""""
    (while (== (>> mant (as number::r64_mantissa_bits u64)) 0) :
        @doc """fmt::print# ("@@ shift ", mant, "\n")"""
        (<<= mant 8)
        (-= exp 8))
    (while (!= (>> mant (as number::r64_mantissa_bits u64)) 1) :
        (>>= mant 1)
        (+= exp 1))
    (if (> exp number::r64_exponent_max) :
        @doc "maybe return inf"
        (return ParseErrorVal)
     :)
    (if (< exp number::r64_exponent_min) :
        @doc """we do not support denormalization
maybe return 0.0"""
        (return ParseErrorVal)
     :)
    (+= exp number::r64_exponent_bias)
    @doc """fmt::print# ("AFTER mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")
final touches"""
    (let exp_u64 auto (and (as exp u64) number::r64_exponent_mask))
    (and= mant number::r64_mantissa_mask)
    (return (number::make_r64 [negative exp_u64 mant])))


@pub (fun parse_r64_hex [(param s (slice u8))] (union [ParseError r64]) :
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
    (return (parse_r64_hex_helper [(slice_val (pinc (front s) i) (- n i)) negative])))


@pub (fun parse_r64 [(param s (slice u8))] (union [ParseError r64]) :
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
        (return (parse_r64_hex_helper [(slice_val (pinc (front s) i) (- n i)) negative]))
     :)
    (let! mant auto 0_u64)
    (let! exp_adjustments auto 0_s32)
    (let! exp auto 0_s32)
    @doc "log2(10^19) == 63.11"
    (read_dec_mantissa# c 19_s32 mant exp_adjustments)
    (if (== c 'e') :
        (next_char# c :
            (return ParseErrorVal))
        (read_dec_exponent# c exp)
     :)
    @doc """TODO: check that we have consumed all chars
early out for simple corner case
fmt::print# ("AFTER mant: ", wrap_as(mant, fmt::u64_hex), " exp: ", exp, "\n")"""
    (if (== mant 0) :
        (return (? negative -0_r64 +0_r64))
     :)
    (return ParseErrorVal))
)

