-- BigInts: fixed with and eventually variable widths
module:

pub global CLEAR_ALL = "\x1b[2J"

type b_u128 = [2]u64

type b_u256 = [4]u64

pub fun add_b_u128(x b_u128, y b_u128) b_u128:
    let z0 = x[0] + y[0]
    let z1 = x[1] + y[1]
    let carry = z0 < x[0] ? 1_u64 : 0_u64
    return {: z0, z1 + carry}

pub fun mul_u64_by_u64_to_b_u128(x u64, y u64) b_u128:
    let x0 = as(as(x, u32), u64)
    let x1 = x >> 32
    let y0 = as(as(y, u32), u64)
    let y1 = y >> 32
    let p00 = x0 * y0
    let p01 = x0 * y1
    let p10 = x1 * y0
    let p11 = x1 * y1
    -- we would like to use
    -- middle =  p10 + p00 >> 32 +  p10
    -- but this might cause an overflow in the high bits
    let middle0 = p10 + p00 >> 32 + as(as(p01, u32), u64)
    -- add missing component after shifting to right
    let middle1 = middle0 >> 32 + p01 >> 32
    return {: as(as(p00, u32), u64) or middle0 << 32, p11 + middle1}
