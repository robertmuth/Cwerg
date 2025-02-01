; random
module:

global IM u32 = 139968

global IA u32 = 3877

global IC u32 = 29573

global! LAST u32 = 42

pub fun get_random(n r64) r64:
    set LAST = (LAST * IA + IC) % IM
    return n * as(LAST, r64) / as(IM, r64)

; see https://www.pcg-random.org/download.html
rec Pcg32State:
    state u64
    inc u64

pub global Pcg32StateDefault = {
        Pcg32State: 0x853c49e6748fea9b_u64, 0xda3e39cb94b95bdb_u64}

; Generate a uniformly distributed 32-bit random number
pub fun Pcg32GetRandomU32(state ^!Pcg32State) u32:
    let oldstate u64 = state^.state
    set state^.state = oldstate * 6364136223846793005_u64 + state^.inc
    let xorshifted u32 = as((oldstate >> 18 ~ oldstate) >> 27, u32)
    let rot u32 = as(oldstate >> 59, u32)
    return xorshifted >> rot | xorshifted << ((0 - rot) & 31)

; Generate a r64 number between 0.0 and 1.0
pub fun Pcg32GetRandomR64(state ^!Pcg32State) r64:
    let v = Pcg32GetRandomU32(state)
    return as(v, r64) / 4294967295
