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


@doc "8 * 308 = 2.5KB table. log10(2^1023) == 307.95"
(global powers_of_ten auto (array_val 309 r64 [
        1e0 1e1 1e2 1e3 1e4 1e5 1e6 1e7 1e8 1e9 1e10 1e11 1e12 1e13 1e14 1e15 1e16
        1e17 1e18 1e19 1e20 1e21 1e22 1e23 1e24 1e25 1e26 1e27 1e28 1e29 1e30 1e31
        1e32 1e33 1e34 1e35 1e36 1e37 1e38 1e39 1e40 1e41 1e42 1e43 1e44 1e45 1e46
        1e47 1e48 1e49 1e50 1e51 1e52 1e53 1e54 1e55 1e56 1e57 1e58 1e59 1e60 1e61
        1e62 1e63 1e64 1e65 1e66 1e67 1e68 1e69 1e70 1e71 1e72 1e73 1e74 1e75 1e76
        1e77 1e78 1e79 1e80 1e81 1e82 1e83 1e84 1e85 1e86 1e87 1e88 1e89 1e90 1e91
        1e92 1e93 1e94 1e95 1e96 1e97 1e98 1e99 1e100 1e101 1e102 1e103 1e104 1e105
        1e106 1e107 1e108 1e109 1e110 1e111 1e112 1e113 1e114 1e115 1e116 1e117 1e118
        1e119 1e120 1e121 1e122 1e123 1e124 1e125 1e126 1e127 1e128 1e129 1e130 1e131
        1e132 1e133 1e134 1e135 1e136 1e137 1e138 1e139 1e140 1e141 1e142 1e143 1e144
        1e145 1e146 1e147 1e148 1e149 1e150 1e151 1e152 1e153 1e154 1e155 1e156 1e157
        1e158 1e159 1e160 1e161 1e162 1e163 1e164 1e165 1e166 1e167 1e168 1e169 1e170
        1e171 1e172 1e173 1e174 1e175 1e176 1e177 1e178 1e179 1e180 1e181 1e182 1e183
        1e184 1e185 1e186 1e187 1e188 1e189 1e190 1e191 1e192 1e193 1e194 1e195 1e196
        1e197 1e198 1e199 1e200 1e201 1e202 1e203 1e204 1e205 1e206 1e207 1e208 1e209
        1e210 1e211 1e212 1e213 1e214 1e215 1e216 1e217 1e218 1e219 1e220 1e221 1e222
        1e223 1e224 1e225 1e226 1e227 1e228 1e229 1e230 1e231 1e232 1e233 1e234 1e235
        1e236 1e237 1e238 1e239 1e240 1e241 1e242 1e243 1e244 1e245 1e246 1e247 1e248
        1e249 1e250 1e251 1e252 1e253 1e254 1e255 1e256 1e257 1e258 1e259 1e260 1e261
        1e262 1e263 1e264 1e265 1e266 1e267 1e268 1e269 1e270 1e271 1e272 1e273 1e274
        1e275 1e276 1e277 1e278 1e279 1e280 1e281 1e282 1e283 1e284 1e285 1e286 1e287
        1e288 1e289 1e290 1e291 1e292 1e293 1e294 1e295 1e296 1e297 1e298 1e299 1e300
        1e301 1e302 1e303 1e304 1e305 1e306 1e307 1e308]))


(fun r64_dec_fast_helper [
        (param mant_orig u64)
        (param exp_orig s32)
        (param negative bool)] r64 :
    (let! exp auto exp_orig)
    (let! mant auto mant_orig)
    (while (>= mant (<< 1 (as (+ number::r64_mantissa_bits 1) u64))) :
        (/= mant 10)
        (+= exp 1))
    (if (>= exp 309) :
        (return (? negative -inf_r64 +inf_r64))
     :)
    (if (<= exp (~ 309)) :
        (return (? negative -0_r64 +0_r64))
     :)
    (let! out auto (as mant r64))
    (if negative :
        (= out (~ out))
     :)
    (if (>= exp 0) :
        (return (* out (at powers_of_ten exp)))
     :
        (return (/ out (at powers_of_ten (~ exp))))))


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

