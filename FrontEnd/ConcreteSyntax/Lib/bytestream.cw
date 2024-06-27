module:

import fmt

-- the input bitstream was corrupted
@pub @wrapped type OutOfBoundsError = void

@pub global OutOfBoundsErrorVal = wrap_as(void, OutOfBoundsError)

-- 
fun IncSliceUnchecked(buffer ^!slice(u8), n uint) void:
    let length uint = len(buffer^)
    set buffer^ = slice(pinc(front(buffer^), n), length - n)

-- 
fun IncSliceOrDie(buffer ^!slice(u8), n uint) void:
    let length uint = len(buffer^)
    set buffer^ = slice(pinc(front(buffer^), n, length), length - n)

-- 
@pub fun FrontSliceOrDie(buffer ^!slice(u8), n uint) slice(u8):
    let out = slice(front(buffer^), n)
    do IncSliceOrDie(buffer, n)
    return out

-- 
@pub fun FrontSliceUnchecked(buffer ^!slice(u8), n uint) slice(u8):
    let out = slice(front(buffer^), n)
    do IncSliceUnchecked(buffer, n)
    return out

-- 
@pub fun FrontSlice(buffer ^!slice(u8), n uint) union(
        slice(u8), OutOfBoundsError):
    if len(buffer^) <= n:
        return OutOfBoundsErrorVal
    let out slice(u8) = slice(front(buffer^), n)
    do IncSliceUnchecked(buffer, n)
    return out

-- 
@pub fun FrontLeU8Unchecked(buffer ^!slice(u8)) u8:
    let out u8 = buffer^[@unchecked 0]
    do IncSliceUnchecked(buffer, 1)
    return out

-- 
@pub fun FrontLeU8OrDie(buffer ^!slice(u8)) u8:
    if len(buffer^) == 0:
        trap
    return FrontLeU8Unchecked(buffer)

-- 
@pub fun FrontLeU8(buffer ^!slice(u8)) union(u8, OutOfBoundsError):
    if len(buffer^) == 0:
        return OutOfBoundsErrorVal
    return FrontLeU8Unchecked(buffer)

-- 
@pub fun FrontLeU16Unchecked(buffer ^!slice(u8)) u16:
    let out0 = as(buffer^[@unchecked 0], u16)
    let out1 = as(buffer^[@unchecked 1], u16)
    do IncSliceUnchecked(buffer, 2)
    return out0 + out1 << 8

-- 
@pub fun FrontLeU16OrDie(buffer ^!slice(u8)) u16:
    if len(buffer^) <= 1:
        trap
    return FrontLeU16Unchecked(buffer)

-- 
@pub fun FrontLeU16(buffer ^!slice(u8)) union(u16, OutOfBoundsError):
    if len(buffer^) == 1:
        return OutOfBoundsErrorVal
    return FrontLeU16Unchecked(buffer)

-- 
@pub fun FrontLeU32Unchecked(buffer ^!slice(u8)) u32:
    let out0 = as(buffer^[@unchecked 0], u32)
    let out1 = as(buffer^[@unchecked 1], u32)
    let out2 = as(buffer^[@unchecked 2], u32)
    let out3 = as(buffer^[@unchecked 3], u32)
    do IncSliceUnchecked(buffer, 4)
    return out0 + out1 << 8 + out2 << 16 + out3 << 24

-- 
@pub fun FrontLeU32OrDie(buffer ^!slice(u8)) u32:
    if len(buffer^) <= 3:
        trap
    return FrontLeU32Unchecked(buffer)

-- 
@pub fun FrontLeU32(buffer ^!slice(u8)) union(u32, OutOfBoundsError):
    if len(buffer^) == 3:
        return OutOfBoundsErrorVal
    return FrontLeU32Unchecked(buffer)
