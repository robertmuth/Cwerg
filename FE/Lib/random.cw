; random
module:


pub rec SimpleLCGState:
    last u32

pub global SimpleLCGStateDefault = {SimpleLCGState: 42}

global LCG_IM u32 = 139968
global LCG_IA u32 = 3877
global LCG_IC u32 = 29573


; Generate a r64 number between 0.0 and 1.0
poly pub fun NextR64(s ^!SimpleLCGState) r64:
    set s^.last = (s^.last * LCG_IA + LCG_IC) % LCG_IM
    return as(s^.last, r64) / as(LCG_IM, r64)


; Generate a 32-bit random number BUT only in the range of [0:LCG_IM[
poly pub fun NextU32(s ^!SimpleLCGState) u32:
    set s^.last = (s^.last * LCG_IA + LCG_IC) % LCG_IM
    return s^.last

; see https://www.pcg-random.org/download.html
pub rec Pcg32State:
    state u64
    inc u64

pub global Pcg32StateDefault = {Pcg32State: 0x853c49e6748fea9b_u64,
                                0xda3e39cb94b95bdb_u64}

; Generate a uniformly distributed 32-bit random number
poly pub fun NextU32(state ^!Pcg32State) u32:
    let oldstate u64 = state^.state
    set state^.state = oldstate * 6364136223846793005_u64 + state^.inc
    let xorshifted u32 = as((oldstate >> 18 ~ oldstate) >> 27, u32)
    let rot u32 = as(oldstate >> 59, u32)
    return xorshifted >> rot | xorshifted << ((0 - rot) & 31)

; Generate a r64 number between 0.0 and 1.0
poly pub fun NextR64(state ^!Pcg32State) r64:
    let v = NextU32(state)
    return as(v, r64) / 4294967295
