-- math module
module:

-- e
pub global E r64 = 2.718281828459045235360287471352662498

-- log_2 e
pub global LOG2_E r64 = 1.442695040888963407359924681001892137

-- log_10(e)
pub global LOG10_E r64 = 0.434294481903251827651128918916605082

-- log_e(2)
pub global LN_2 r64 = 0.693147180559945309417232121458176568

-- log_e(10)
pub global LN_10 r64 = 2.302585092994045684017991454684364208

-- pi
pub global PI r64 = 3.141592653589793238462643383279502884

-- pi / 2
pub global PI_2 r64 = 1.570796326794896619231321691639751442

-- pi / 4
pub global PI_4 r64 = 0.785398163397448309615660845819875721

-- 1 / pi
pub global ONE_PI r64 = 0.318309886183790671537767526745028724

-- 2 / pi
pub global TWO_PI r64 = 0.636619772367581343075535053490057448

-- 2 / sqrt(pi)
pub global TWO__SQRT_PI r64 = 1.128379167095512573896158903121545172

-- sqrt(2)
pub global SQRT_2 r64 = 1.414213562373095048801688724209698079

-- 1 / sqrt(2)
pub global ONE_SQRT_2 r64 = 0.707106781186547524400844362104849039

-- sqrt(3)
pub global SQRT_3 r64 = 1.7320508075688772935274463415058723669428

-- 1 / sqrt(3)
pub global ONE_SQRT_3 r64 = 0.5773502691896257645091487805019574556476

-- Kahan's doubly compensated summation. Less accurate but fast
fun sum_kahan_compensated(summands slice(r64)) r64:
    let! s r64 = 0.0
    let! c r64 = 0.0
    for i = 0, len(summands), 1:
        let x = summands[i]
        let y = x - c
        let t = s + y
        set c = t - s - y
        set s = t
    return s

pub rec SumCompensation:
    sum r64
    compensation r64

-- Priest's doubly compensated summation. Accurate but slow
fun sum_priest_compensated(summands slice(r64)) SumCompensation:
    let! s r64 = 0.0
    let! c r64 = 0.0
    for i = 0, len(summands), 1:
        let x = summands[i]
        let y = c + x
        let u = x - (y - c)
        let t = y + s
        let v = y - (t - s)
        let z = u + v
        set s = t + z
        set c = z - (s - t)
    return SumCompensation{s, c}

fun horner_sum(x r64, coeffs slice(r64)) r64:
    let! s r64 = 0.0
    for i = 0, len(coeffs), 1:
        let c = coeffs[i]
        set s = s * x + c
    return s
