module:

fun mymemcpy(dst ^!u8, src ^u8, size uint) uint:
    for i = 0, size, 1:
        set ptr_inc(dst, i)^ = ptr_inc(src, i)^
    return size

macro unsigned_to_str# EXPR ($val EXPR, $base EXPR, $max_width EXPR,
                             ; a slice for the output string
                             $out EXPR) [$v, $out_eval, $tmp, $pos]:
    expr:
        ; unsigned to str with given base
        let! $v = $val
        let! $tmp = {[1024]u8: undef}
        let! $pos uint = $max_width
        let $out_eval = $out
        block:
            set $pos -= 1
            let c = $v % $base
            let! c8 = as(c, u8)
            set c8 += c8 <= 9 ? '0' : 'a' - 10
            set $tmp[$pos] = c8
            set $v /= $base
            if $v != 0:
                continue
        let n uint = $max_width - min($pos, len($out_eval))
        return mymemcpy(front!($out_eval), ptr_inc(front($tmp), $pos), n)

; Why the polymorphism?
;         It makes shorter names and avoids the need for separate
;         uint and sint handling
poly pub fun FmtDec(v u8, out span!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

poly pub fun FmtDec(v u16, out span!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

poly pub fun FmtDec(v u32, out span!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

poly pub fun FmtDec(v u64, out span!(u8)) uint:
    return unsigned_to_str#(v, 10, 32_uint, out)

poly pub fun FmtDec(v s16, out span!(u8)) uint:
    if len(out) == 0:
        return 0
    if v < 0:
        let v_unsigned = 0_s16 - v
        set out[0] = '-'
        return 1 + FmtDec(v_unsigned, span_inc(out, 1))
    else:
        return FmtDec(as(v, u16), out)

poly pub fun FmtDec(v s32, out span!(u8)) uint:
    if len(out) == 0:
        return 0
    if v < 0:
        set out[0] = '-'
        let v_unsigned = as(0_s32 - v, u32)
        return 1 + FmtDec(v_unsigned, span_inc(out, 1))
    else:
        return FmtDec(as(v, u32), out)

; Why the polymorphism?
;         It makes shorter names and avoids the need for separate
;         uint and sint handling
poly pub fun FmtHex(v u64, out span!(u8)) uint:
    return unsigned_to_str#(v, 16, 64_uint, out)

poly pub fun FmtHex(v u32, out span!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)

poly pub fun FmtHex(v u16, out span!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)

poly pub fun FmtHex(v u8, out span!(u8)) uint:
    return unsigned_to_str#(v, 16, 32_uint, out)
