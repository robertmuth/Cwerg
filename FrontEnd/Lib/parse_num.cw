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


(macro next_char# STMT_LIST [
        (mparam $str ID)
        (mparam $c ID)
        (mparam $i ID)
        (mparam $n ID)
        (mparam $body STMT_LIST)] [] :
    (if (>= $i $n) :
        $body
     :)
    (= $c (at $str $i))
    (+= $i 1))


(macro read_hex_digits# STMT_LIST [
        (mparam $str ID)
        (mparam $c ID)
        (mparam $i ID)
        (mparam $n ID)
        (mparam $val ID)
        (mparam $count ID)] [] :
    (while (is_hex_digit [c]) :
        (<<= $val 4)
        (or= $val (as (hex_digit_val [$c]) u64))
        (+= $count 1)
        (next_char# $str $c $i $n :
            (return ParseErrorVal))))


@doc "expects a string without sign and without '0x' prefix"
(fun parse_r64_hex_helper [(param s (slice u8)) (param negative bool)] (union [ParseError r64]) :
    (let! i uint 0)
    (let n auto (len s))
    (let! c u8)
    (next_char# s c i n :
        (return ParseErrorVal))
    (while (== c '0') :
        (next_char# s c i n :
            (return ParseErrorVal)))
    (let! digits_before_dot auto 0_u32)
    (let! mant auto 0_u64)
    (read_hex_digits# s c i n mant digits_before_dot)
    (let! digits_after_dot auto 0_u32)
    (if (== c '.') :
        (if (>= i n) :
            (return ParseErrorVal)
         :)
        (+= i 1)
        (read_hex_digits# s c i n mant digits_after_dot)
     :)
    (let! negative_exp auto false)
    (let! exp auto 0_u32)
    (if (== c 'p') :
        (next_char# s c i n :
            (return ParseErrorVal))
        (if (|| (== c '-') (== c '+')) :
            (if (== c '-') :
                (= negative_exp true)
             :)
            (next_char# s c i n :
                (return ParseErrorVal))
         :)
        (while (&& (>= c '0') (<= c '9')) :
            (*= exp 10)
            (+= exp (as (- c '0') u32))
            (next_char# s c i n :
                (break)))
     :)
    (if negative_exp :
        (= exp (! exp))
        (+= exp 1)
     :)
    (-= exp (* digits_after_dot 4))
    (+= exp number::r64_mantissa_bits)
    @doc "early out for simple corner case"
    (if (== mant 0) :
        (return (? negative -0_r64 +0_r64))
     :)
    (fmt::print# "BEFORE mantissa: " mant " exponent: " exp " digits-bef: " digits_before_dot " digits-aft: " digits_after_dot "\n")
    (while (== (>> mant (as number::r64_mantissa_bits u64)) 0) :
        @doc """fmt::print# ("@@ shift ", mant, "\n")"""
        (<<= mant 1)
        (-= exp 1))
    (and= mant number::r64_mantissa_mask)
    (+= exp number::r64_exponent_bias)
    (fmt::print# number::r64_mantissa_mask " mantissa: " mant " exponent: " exp "\n")
    (return (number::make_r64 [negative (as exp u64) mant])))


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
    (next_char# s c i n :
        (return ParseErrorVal))
    (let! negative auto false)
    (if (|| (== c '-') (== c '+')) :
        (if (== c '-') :
            (= negative true)
         :)
        (next_char# s c i n :
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
    (while (== c '0') :
        (next_char# s c i n :
            (return (? negative -0.0_r64 +0.0_r64))))
    (return 1.0_r64))
)

