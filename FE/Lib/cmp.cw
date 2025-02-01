module:

pub poly fun eq(a bool, b bool) bool:
    return a == b

pub poly fun eq(a u8, b u8) bool:
    return a == b

pub poly fun eq(a u16, b u16) bool:
    return a == b

pub poly fun eq(a u32, b u32) bool:
    return a == b

pub poly fun eq(a u64, b u64) bool:
    return a == b

pub poly fun eq(a s8, b s8) bool:
    return a == b

pub poly fun eq(a s16, b s16) bool:
    return a == b

pub poly fun eq(a s32, b s32) bool:
    return a == b

pub poly fun eq(a s64, b s64) bool:
    return a == b

poly fun eq(a r32, b r32) bool:
    return a == b

pub poly fun eq(a r64, b r64) bool:
    return a == b

; r32 range, represents [val - err, val + err]
pub rec r32r:
    val r32
    ; must be >= 0
    err r32

; r64 range, represents [val - err, val + err]
pub rec r64r:
    val r64
    ; must be >= 0
    err r64

pub poly fun eq(a r64r, b r64r) bool:
    return a.val + a.err >= b.val - b.err && a.val - a.err <= b.val + b.err

pub poly fun eq(a r32r, b r32r) bool:
    return a.val + a.err >= b.val - b.err && a.val - a.err <= b.val + b.err
