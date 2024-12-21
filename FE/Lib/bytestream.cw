module:

import fmt

-- the input bitstream was corrupted
pub wrapped type OutOfBoundsError = void

pub global OutOfBoundsErrorVal = wrap_as(void, OutOfBoundsError)

--
pub fun SkipUnchecked(buffer ^!span(u8), n uint) void:
    set buffer^ = span_inc(buffer^, n)

--
pub fun Skip(buffer ^!span(u8), n uint) union(void, OutOfBoundsError):
    if len(buffer^) <= n:
        return OutOfBoundsErrorVal
    do SkipUnchecked(buffer, n)

--
pub fun FrontSliceOrDie(buffer ^!span(u8), n uint) span(u8):
    let out = span(front(buffer^), n)
    set buffer^ = span_inc(buffer^, n)
    return out

--
pub fun FrontSliceUnchecked(buffer ^!span(u8), n uint) span(u8):
    let out = span(front(buffer^), n)
    do SkipUnchecked(buffer, n)
    return out

--
pub fun FrontSlice(buffer ^!span(u8), n uint) union(span(u8), OutOfBoundsError):
    if len(buffer^) <= n:
        return OutOfBoundsErrorVal
    let out span(u8) = span(front(buffer^), n)
    do SkipUnchecked(buffer, n)
    return out

--
pub fun FrontU8Unchecked(buffer ^!span(u8)) u8:
    let out u8 = buffer^[{{unchecked}} 0]
    do SkipUnchecked(buffer, 1)
    return out

--
pub fun FrontU8OrDie(buffer ^!span(u8)) u8:
    if len(buffer^) == 0:
        trap
    return FrontU8Unchecked(buffer)

--
pub fun FrontU8(buffer ^!span(u8)) union(u8, OutOfBoundsError):
    if len(buffer^) == 0:
        return OutOfBoundsErrorVal
    return FrontU8Unchecked(buffer)

--
pub fun FrontLeU16Unchecked(buffer ^!span(u8)) u16:
    let out0 = as(buffer^[{{unchecked}} 0], u16)
    let out1 = as(buffer^[{{unchecked}} 1], u16)
    do SkipUnchecked(buffer, 2)
    return out0 + out1 << 8

--
pub fun FrontLeU16OrDie(buffer ^!span(u8)) u16:
    if len(buffer^) <= 1:
        trap
    return FrontLeU16Unchecked(buffer)

--
pub fun FrontLeU16(buffer ^!span(u8)) union(u16, OutOfBoundsError):
    if len(buffer^) <= 1:
        return OutOfBoundsErrorVal
    return FrontLeU16Unchecked(buffer)

--
pub fun FrontBeU16Unchecked(buffer ^!span(u8)) u16:
    let out0 = as(buffer^[{{unchecked}} 0], u16)
    let out1 = as(buffer^[{{unchecked}} 1], u16)
    do SkipUnchecked(buffer, 2)
    return out1 + out0 << 8

--
pub fun FrontBeU16(buffer ^!span(u8)) union(u16, OutOfBoundsError):
    if len(buffer^) <= 1:
        return OutOfBoundsErrorVal
    return FrontBeU16Unchecked(buffer)

--
pub fun FrontLeU32Unchecked(buffer ^!span(u8)) u32:
    let out0 = as(buffer^[{{unchecked}} 0], u32)
    let out1 = as(buffer^[{{unchecked}} 1], u32)
    let out2 = as(buffer^[{{unchecked}} 2], u32)
    let out3 = as(buffer^[{{unchecked}} 3], u32)
    do SkipUnchecked(buffer, 4)
    return out0 + out1 << 8 + out2 << 16 + out3 << 24

--
pub fun FrontLeU32OrDie(buffer ^!span(u8)) u32:
    if len(buffer^) <= 3:
        trap
    return FrontLeU32Unchecked(buffer)

--
pub fun FrontLeU32(buffer ^!span(u8)) union(u32, OutOfBoundsError):
    if len(buffer^) == 3:
        return OutOfBoundsErrorVal
    return FrontLeU32Unchecked(buffer)
