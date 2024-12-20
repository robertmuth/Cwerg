-- Lots of literature referencves :
-- https://stackoverflow.com/questions/7153979/algorithm-to-convert-an-ieee-754-double-to-a-string
-- https://www.ryanjuckett.com/printing-floating-point-numbers/
module:

import num_real

import fmt_int

global log2_10 r64 = 3.3219280948873623478703194294

global log10_2_to_52 r64 = 15.653559774527022151114422525

global target_range_hi = as(1_u64 << 53, r64)

global target_range_lo = as(1_u64 << 53, r64) / 10.0

pub fun mymemcpy(dst ^!u8, src ^u8, size uint) uint:
    for i = 0, size, 1:
        set ptr_inc(dst, i)^ = ptr_inc(src, i)^
    return size

fun div_by_power_of_10(val r64, pow10 s32) r64:
    if pow10 >= 0:
        return val / num_real::powers_of_ten[pow10]
    else:
        return val * num_real::powers_of_ten[-pow10]

-- find power of 10 to divide val by so that ideally the result
-- is an integer between target_range_lo and target_range_hi
-- val must be positive
fun find_t(val r64) s32:
    let biased_exp = num_real::r64_raw_exponent(val) - num_real::r64_raw_exponent_bias
    let! t s32 = -as(log10_2_to_52 - as(biased_exp, r64) / log2_10, s32)
    while true:
        let x = div_by_power_of_10(val, t)
        cond:
            case x <= target_range_lo:
                set t -= 1
            case x > target_range_hi:
                set t += 1
            case true:
                return t

-- assumptions:
-- * raw_exp is nan
-- * len(out) >= 5
fun FmtNan(val r64, out span!(u8)) uint:
    let! mantissa = num_real::r64_raw_mantissa(val)
    let is_negative = num_real::r64_is_negative(val)
    set out[0] = is_negative ? '-' : '+'
    cond:
        case mantissa == num_real::r64_mantissa_infinity:
            return 1 + span_append_or_die#("inf", span_inc(out, 1))
        case mantissa == num_real::r64_mantissa_qnan:
            return 1 + span_append_or_die#("nan", span_inc(out, 1))
        case mantissa == num_real::r64_mantissa_snan:
            return 1 + span_append_or_die#("snan", span_inc(out, 1))
    return 0

-- for a given float val we want to find a decomposition
-- val = x * 10^t so that   2^53 / 10 < x <= 2^53
-- because this way we can compute the base ten digits easily.
-- From the standard for %e:
-- The double argument shall be converted in the style "[-]d.ddde±dd",
-- where there is one digit before the radix character (which is non-zero if the argument
-- is non-zero) and the number of digits after it is equal to the precision; if the precision
-- is missing, it shall be taken as 6; if the precision is zero and no '#' flag is present, no
-- radix character shall appear. The low-order digit shall be rounded in an implementation-defined
-- manner. The E conversion specifier shall produce a number with 'E' instead of 'e' introducing
-- the exponent. The exponent shall always contain at least two digits. If the value is zero,
-- the exponent shall be zero.
pub fun FmtExponentE(exp s32, out span!(u8)) uint:
    if len(out) < 4:
        return 0
    -- account for e±
    let! i = 2_uint
    set out[0] = 'e'
    if exp < 0:
        set out[1] = '-'
        if exp >= -9:
            set out[2] = '0'
            set i += 1
        return i + fmt_int::FmtDec(-exp, span_inc(out, i))
    else:
        set out[1] = '+'
        if exp <= 9:
            set out[2] = '0'
            set i += 1
        return i + fmt_int::FmtDec(exp, span_inc(out, i))

fun FmtSign(is_negative bool, force_sign bool, out span!(u8)) uint:
    cond:
        case is_negative:
            set out[0] = '-'
            return 1
        case force_sign:
            set out[0] = '+'
            return 1
        case true:
            return 0

fun FmtMantissaE(digits span(u8), precision uint, out span!(u8)) uint:
    let num_digits = len(digits)
    set out[0] = digits[0]
    set out[1] = '.'
    for j = 1, precision + 1, 1:
        if j < num_digits:
            set out[j + 1] = digits[j]
        else:
            set out[j + 1] = '0'
    return precision + 2

-- return a potential "carry"
fun RoundDigitsUp(digits span!(u8)) s32:
    for pos = 0, len(digits), 1:
        let i = len(digits) - pos - 1
        if digits[i] == '9':
            set digits[i] = '0'
        else:
            set digits[i] += 1
            return 0
    for pos = 0, len(digits) - 1, 1:
        let i = len(digits) - pos - 1
        set digits[i] = digits[i - 1]
    set digits[0] = '1'
    return 1

pub poly fun FmtE(val r64, precision uint, force_sign bool, out span!(u8)) uint:
    -- worst case -x.[precision]e-xxx
    let is_negative = num_real::r64_is_negative(val)
    let! buffer [32]u8 = undef
    if len(out) < precision + 8:
        return 0
    if precision + 1 > len(buffer):
        return 0
    if num_real::r64_raw_exponent(val) == num_real::r64_raw_exponent_subnormal:
        if num_real::r64_raw_mantissa(val) == 0:
            set buffer[0] = '0'
            let! i = 0_uint
            set i += FmtSign(is_negative, force_sign, out)
            set i += FmtMantissaE(
                    span(front(buffer), 1), precision, span_inc(out, i))
            set i += FmtExponentE(0, span_inc(out, i))
            return i
        return 0
    if num_real::r64_raw_exponent(val) == num_real::r64_raw_exponent_nan:
        return FmtNan(val, out)
    -- find power of 10 to divide val by so that ideally the result
    -- is an integer between target_range_lo and target_range_hi
    let! t s32 = find_t(abs(val))
    -- fmt::print#("@@@ ", t, "\n")
    let x = div_by_power_of_10(val, t)
    let! mantissa = num_real::r64_raw_mantissa(x) + 1 << 52
    let exponent = num_real::r64_raw_exponent(x) - num_real::r64_raw_exponent_bias
    assert#(exponent >= 49 && exponent <= 52, "out of bounds\n")
    if exponent != 52:
        set t -= 1
        set mantissa *= 10
        set mantissa >>= as(52_s32 - exponent, u64)
    let num_digits uint = fmt_int::FmtDec(
            mantissa, span(front!(buffer), len(buffer)))
    -- decimal rounding if we drop digits
    if num_digits > precision + 1 && buffer[precision + 2] >= '5':
        set t += RoundDigitsUp(span(front!(buffer), precision + 1))
    set t += as(num_digits - 1, s32)
    let! i = 0_uint
    set i += FmtSign(is_negative, force_sign, out)
    set i += FmtMantissaE(
            span(front(buffer), num_digits), precision, span_inc(out, i))
    set i += FmtExponentE(t, span_inc(out, i))
    -- fmt::print#("@@@ ", t, " ",  exponent, " ",  buffer, " out:", out, "\n")
    return i

fun to_hex_digit(digit u8) u8:
    return digit <= 9 ? digit + '0' : digit + ('a' - 10)

fun FmtMantissaHex(frac_bits u64, is_denorm bool, out span!(u8)) uint:
    set out[0] = '0'
    set out[1] = 'x'
    set out[2] = is_denorm ? '0' : '1'
    set out[3] = '.'
    let! bits = frac_bits
    let! i = 4_uint
    while bits != 0:
        set out[i] = to_hex_digit(as(bits >> 48, u8))
        set i += 1
        set bits and= 0xffff_ffff_ffff
        set bits <<= 4
    return i

fun FmtExponentHex(raw_exponent s32, is_potential_zero bool, out span!(u8)) uint:
    let! exp s32 = raw_exponent
    if raw_exponent == num_real::r64_raw_exponent_subnormal:
        set exp = is_potential_zero ? 0 : -1022
    else:
        set exp -= num_real::r64_raw_exponent_bias
    set out[0] = 'p'
    if exp < 0:
        set out[1] = '-'
        set exp = -exp
    else:
        set out[1] = '+'
    return 2 + fmt_int::FmtDec(as(exp, u32), span_inc(out, 2))

-- r64 format (IEEE 754):  sign (1 bit) exponent (11 bits) fraction (52 bits)
--         exponentiation bias is 1023
--         https://en.wikipedia.org/wiki/Double-precision_floating-point_format
--         https://observablehq.com/@jrus/hexfloat
pub poly fun FmtHex(val r64, out span!(u8)) uint:
    let! frac_bits = num_real::r64_raw_mantissa(val)
    let is_negative = num_real::r64_is_negative(val)
    let raw_exponent = num_real::r64_raw_exponent(val)
    if raw_exponent == num_real::r64_raw_exponent_nan:
        return FmtNan(val, out)
    let! i uint = 0
    if is_negative:
        set out[i] = '-'
        set i += 1
    set i += FmtMantissaHex(
            frac_bits, raw_exponent == num_real::r64_raw_exponent_subnormal, span_inc(
                out, i))
    set i += FmtExponentHex(raw_exponent, frac_bits == 0, span_inc(out, i))
    return i
